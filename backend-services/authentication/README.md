# Authentication Service

FastAPI service used behind Caddy to protect the admin Dagster UI and the
local `marimo-dashboard` notebook routes with an OIDC-backed browser session.

## Table of contents

- [What it does](#what-it-does)
- [Protected route flows](#protected-route-flows)
- [Required environment](#required-environment)
- [Local usage](#local-usage)
- [Related docs](#related-docs)

## What it does

- starts a FastAPI app from [main.py](main.py)
- stores browser session state with Starlette `SessionMiddleware`
- redirects users to the configured OIDC provider for login
- validates the returned access token against the configured JWKS endpoint
- returns auth decisions to Caddy `forward_auth` checks for protected routes

## Protected route flows

Current route groups implemented in [main.py](main.py):

- Dagster admin:
  - `/dagster-webserver/admin/login`
  - `/oauth2/dagster-webserver/admin/authorize`
  - `/oauth2/dagster-webserver/admin/validate`
- Marimo dashboard:
  - `/marimo/login`
  - `/oauth2/marimo/authorize`
  - `/oauth2/marimo/validate`

In the local compose stack, Caddy forwards these auth routes to the
`authentication` container and uses the `*/validate` endpoints for
`forward_auth` checks before proxying to the protected upstream.

The local-only `marimo-codex-workspace` service is not routed through this auth
service. It binds to `127.0.0.1:2719` for local research and remains outside
deployed Codex execution scope.

## Required environment

The service reads these environment variables:

- `WEBSITE_ROOT_URL`
- `COGNITO_DAGSTER_AUTH_CLIENT_ID`
- `COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL`
- `COGNITO_TOKEN_SIGNING_KEY_URL`
- `COGNITO_DAGSTER_AUTH_CLIENT_SECRET`

`WEBSITE_ROOT_URL` is normalized to an HTTPS, slash-free base URL before the
service redirects the browser back to `/dagster-webserver/admin` or `/marimo`.

## Local usage

This service is started by [../compose.yaml](../compose.yaml) as part of the
local backend stack. It is normally reached through Caddy at `https://localhost`
rather than directly.

## Related docs

- [Local backend-services stack](../README.md)
- [Marimo notebook services](../marimo/README.md)
- [Repository architecture](../../docs/repository/architecture.md)
- [AWS Pulumi infrastructure](../../infrastructure/aws-pulumi/README.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/authentication/main.py`
  - `backend-services/compose.yaml`
  - `backend-services/caddy/Caddyfile`
- `sync.scope`: `interface`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
