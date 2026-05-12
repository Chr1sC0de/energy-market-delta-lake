# Marimo Notebook Service

FastAPI wrapper around `marimo` used in the local development stack for
notebook-oriented exploration against the same S3-compatible data flows used by
the rest of the repo.

## Table of contents

- [What it does](#what-it-does)
- [Local usage](#local-usage)
- [Related docs](#related-docs)

## What it does

The app in [src/marimoserver/main.py](src/marimoserver/main.py):

- exposes `/health` for container health checks
- discovers `*.py` notebooks from `notebooks/`
- mounts each notebook as a marimo sub-app under `/marimo/<notebook-name>`
- serves a simple index page at `/marimo`
- links the Caddy-served shared theme at `/theme.css` for the index and sample
  notebook head
- applies a MIME-type fix middleware for `woff` and `woff2` assets

In the local compose stack, Caddy proxies `/marimo*` traffic to this service.
Most notebook routes are protected by the authentication service, while static
asset and websocket paths are proxied through directly. Caddy still serves
`/theme.css` from its static root, so notebook pages can use the same palette as
the root portfolio page.

## Local usage

The service is started by [../compose.yaml](../compose.yaml). Notebook files are
mounted from [notebooks/](notebooks/) into the container, so adding a notebook
there makes it available through the `/marimo` index.

The implementation also accepts `MARIMO_NOTEBOOKS_DIR` if you need to point the
server at a different notebook directory.

## Related docs

- [Local backend-services stack](../README.md)
- [Authentication service](../authentication/README.md)
- [Repository workflow](../../docs/repository/workflow.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/marimo/src/marimoserver/main.py`
  - `backend-services/marimo/notebooks/head.html`
  - `backend-services/marimo/notebooks/sample_energy_market.py`
  - `backend-services/compose.yaml`
  - `backend-services/caddy/Caddyfile`
  - `backend-services/caddy/theme.css`
- `sync.scope`: `interface`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
