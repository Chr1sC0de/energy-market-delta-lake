# Creating a Marimo analytics layer

For analytics we would like to use [marimo](https://marimo.io/).

To deploy marimo we would require a fast api server to server muliple notebooks.

Create for me a fastapi marimoserver which will server multiple notebooks, create for me a sample notebook and add this to the compose file.

This fastapi server should be added to caddy and protected like the dagster admin server

______________________________________________________________________

## Implementation Plan

### Overview

Add a marimo notebook server behind a FastAPI proxy, integrated into the existing Caddy reverse proxy with the same OIDC auth protection as the Dagster admin server. The local compose setup is the first target; the service will be deployed to AWS in future.

______________________________________________________________________

### 1. New `backend-services/marimo/` service directory

- **`pyproject.toml`** — Python package with deps: `marimo`, `fastapi[standard]`, `uvicorn`, `polars`, `deltalake`, `boto3`
- **`Dockerfile`** — Multi-stage build matching the existing pattern (`uv` builder + `python:3.13-slim` deploy stage)
- **`src/marimoserver/main.py`** — FastAPI app that:
  - Iterates over `notebooks/` and mounts each `.py` file via `marimo.create_asgi_app().with_app(path="/<name>", root=...)` (note: `with_dynamic_directory` does not support `path="/"`, so a static loop is used instead — a server restart is needed to pick up new notebooks)
  - Serves an HTML index page at `/` listing all discovered notebooks
  - Exposes a `/health` endpoint for container healthchecks
  - The marimo ASGI app is mounted at the root inside the container; Caddy handles the `/marimo` prefix stripping externally (see section 5)
- **`notebooks/sample_energy_market.py`** — A sample marimo notebook reading from the Delta Lake S3 data (using polars + deltalake), showing a basic chart

______________________________________________________________________

### 2. `compose.yaml` changes

- Add a new `marimo` service:
  - `build: { context: ./marimo, target: deploy }`
  - `container_name: marimo`
  - `networks: [dagster_network]`
  - `ports: ["2718:2718"]`
  - `environment`: AWS creds (same as aemo-etl), `MARIMO_SERVER_PORT=2718`
  - `depends_on: { localstack: service_healthy }`
  - `volumes`: mount `./marimo/notebooks` to the container's `notebooks/` directory for local dev (edit notebooks without rebuilding)
  - `healthcheck`: curl against the `/health` endpoint
- Add `MARIMO_SERVER: ${MARIMO_SERVER}` to the `caddy` service environment
- Add `marimo` to the caddy service `depends_on` list (startup ordering)

______________________________________________________________________

### 3. `.envrc` changes

- Add `MARIMO_SERVER=marimo:2718`

______________________________________________________________________

### 4. `authentication/main.py` changes

Add three new route handlers mirroring the three dagster-admin routes, but scoped to `/marimo`:

- `GET /oauth2/marimo/validate` — JWT validation (reuses existing `verify_jwt` / session logic)
- `GET /marimo/login` — OIDC redirect to Cognito
- `GET /oauth2/marimo/authorize` — OIDC callback, set session cookie, redirect to `{WEBSITE_ROOT_URL}/marimo`

> **Note:** The redirect in the authorize callback must go through the Caddy root URL (e.g. `https://localhost:8443/marimo`), not directly to the marimo service port. `WEBSITE_ROOT_URL` should be set to the Caddy-facing URL. This applies to the existing dagster routes too and should be verified.

______________________________________________________________________

### 5. `caddy/Caddyfile` changes

Add new routes under the existing site block:

**5a. Update `@static` matcher** — add `/marimo*` to the exclusion list so the static file server does not intercept marimo requests:

```caddyfile
@static {
    not path /dagster-webserver* /oauth2* /_next* /graphql* /favicon.* /manifest.json /marimo*
}
```

**5b. Add marimo auth and proxy routes:**

```caddyfile
# Marimo login + OAuth callback (unprotected, handled by auth server)
reverse_proxy /marimo/login*        {$DAGSTER_AUTHSERVER}
reverse_proxy /oauth2/marimo*       {$DAGSTER_AUTHSERVER}

# Protected Marimo routes
@protectedMarimo {
    path /marimo*
    not path /marimo/login*
}

handle @protectedMarimo {
    forward_auth {$DAGSTER_AUTHSERVER} {
        uri /oauth2/marimo/validate
        header_up Host {upstream_hostport}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_up X-Forwarded-Host {host}

        @error status 401
        handle_response @error {
            redir * /marimo/login
        }
    }

    # Strip /marimo prefix before proxying — the marimo FastAPI app serves
    # from root inside the container. This also ensures marimo's static
    # assets (JS/CSS) resolve correctly.
    uri strip_prefix /marimo
    reverse_proxy {$MARIMO_SERVER}
}
```

> **WebSocket note:** Marimo uses WebSocket for real-time kernel communication. Caddy transparently proxies WebSocket upgrade requests, so no extra config is needed, but this must be verified during testing.

______________________________________________________________________

### 6. `caddy/index.html` changes

Add a marimo link to the landing page:

```html
<li><a href="/marimo">Marimo Notebooks</a></li>
```

______________________________________________________________________

### Key design decisions

| Decision | Rationale |
|---|---|
| FastAPI wraps marimo ASGI | Allows future extension (health endpoint, notebook management API) while marimo itself is mounted as a sub-app |
| `with_app` loop for notebook discovery | `with_dynamic_directory` does not support `path="/"` — notebooks are discovered at startup via a loop over the `notebooks/` directory. Restart the server to pick up new notebooks |
| Caddy `uri strip_prefix /marimo` | Marimo serves from root inside the container; Caddy owns the `/marimo` prefix. Keeps the marimo app unaware of deployment path and ensures asset URLs resolve correctly |
| Volume-mount notebooks in compose | Dev ergonomics — edit notebooks without rebuilding the image. In production (AWS), notebooks are baked into the image via `COPY` |
| Port `2718` | Convention — Euler's number, commonly used for marimo |
| Same auth pattern as Dagster admin | Spec explicitly says "protected like the dagster admin server" |
| `WEBSITE_ROOT_URL` for auth redirects | Auth callback must redirect through Caddy, not directly to the service |
| Sample notebook uses polars + deltalake | Consistent with existing aemo-etl toolchain |

______________________________________________________________________

### AWS deployment considerations

- The Dockerfile `deploy` stage bakes notebooks into the image (`COPY notebooks/ ./notebooks/`), removing the need for volume mounts
- The service can sit behind an ALB or API Gateway with the same `/marimo` prefix stripping
- Auth will use the same Cognito OIDC flow; `WEBSITE_ROOT_URL` will point to the production domain
- Marimo kernels are stateful (WebSocket + in-process threads) — sticky sessions are required if load balancing across multiple instances. Scale vertically first (increase container CPU/memory) before adding instances
- Consider an ECS Fargate task definition mirroring the dagster-webserver pattern
