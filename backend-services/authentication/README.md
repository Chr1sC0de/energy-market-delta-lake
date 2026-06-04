# Authentication Service

FastAPI service used behind Caddy to protect the admin Dagster UI and
`marimo-dashboard` notebook routes with a Cognito-backed browser session.

## Table of contents

- [What it does](#what-it-does)
- [Protected route flows](#protected-route-flows)
- [Required environment](#required-environment)
- [Local usage](#local-usage)
- [Related docs](#related-docs)

## What it does

- starts a FastAPI app from [main.py](main.py)
- stores only an opaque auth session id in the Starlette
  `SessionMiddleware` browser cookie
- keeps Cognito user and access-token state server-side behind that session id
- accepts same-origin custom login posts at `/auth/login`, authenticates
  username/password credentials with Cognito password auth, and returns a safe
  local redirect target
- clears the opaque auth session through `POST /logout`
- validates the returned Cognito access token against the configured JWKS
  endpoint, user-pool issuer, expiry, access-token use, and app client id
- returns auth decisions to Caddy `forward_auth` checks for protected routes

## Protected route flows

Current route groups implemented in [main.py](main.py):

- Dagster admin:
  - `/oauth2/dagster-webserver/admin/validate`
- Marimo dashboard:
  - `/oauth2/marimo/validate`
- Custom browser auth:
  - `POST /auth/login`
  - `POST /logout`

In local compose and AWS, Caddy forwards these auth routes to the
`authentication` service and uses the `*/validate` endpoints for `forward_auth`
checks before proxying to the protected upstream.

`POST /auth/login` accepts JSON or form fields named `identifier`, `password`,
and optional `next`. It rejects cross-origin `Origin` or `Referer` headers,
computes Cognito `SECRET_HASH` server-side, and stores only server-side auth
state behind the opaque browser session id. `next` must resolve to `/`,
`/dagster-webserver/admin`, `/dagster-webserver/admin/...`, `/marimo`, or
`/marimo/...`.

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
- `AWS_DEFAULT_REGION`

`WEBSITE_ROOT_URL` is normalized to an HTTPS, slash-free base URL before the
service compares browser origin headers for login requests.
`AWS_DEFAULT_REGION` configures the regional Cognito IDP client used by the
username/password login endpoint.

The configured Cognito app client must allow username/password auth for the
custom login endpoint. The service uses `COGNITO_DAGSTER_AUTH_CLIENT_SECRET` to
compute the Cognito `SECRET_HASH`; the secret hash, password, raw Cognito
response, ID token, and refresh token are not written to browser cookies or
responses.

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
