# Marimo Notebook Services

Local Marimo Subproject used in the backend-services compose stack. It provides
a curated dashboard image and a separate local-only Marimo-Codex research
workspace image against the same LocalStack-backed data flows used by the rest
of the repo.

## Table of contents

- [What it does](#what-it-does)
- [Image split](#image-split)
- [Local usage](#local-usage)
- [Related docs](#related-docs)

## What it does

The dashboard app in [src/marimoserver/main.py](src/marimoserver/main.py):

- exposes `/health` for container health checks
- discovers `*.py` notebooks from `notebooks/`
- mounts each notebook as a marimo sub-app under `/marimo/<notebook-name>`
- serves a simple index page at `/marimo`
- applies a MIME-type fix middleware for `woff` and `woff2` assets

In the local compose stack, Caddy proxies `/marimo*` traffic to
`marimo-dashboard`. Most notebook routes are protected by the authentication
service, while static asset and websocket paths are proxied through directly.

## Image split

[Dockerfile](Dockerfile) exposes two local image targets:

- `dashboard`: used by the `marimo-dashboard` compose service. It runs the
  FastAPI wrapper, mounts [notebooks/](notebooks/) read-only, and keeps Codex
  tooling out of the curated dashboard image.
- `codex-workspace`: used by the `marimo-codex-workspace` compose service. It
  runs `marimo edit` against the writable
  [research-workspace/](research-workspace/) mount on `127.0.0.1:2719` and
  includes [research-workspace/AGENTS.md](research-workspace/AGENTS.md) for
  local notebook research, data access boundaries, and issue-draft generation.

Both targets are local-first. The research workspace is for human-operated local
Marimo-Codex research only; compose does not launch unattended Codex, and
deployed Codex execution is deferred until a security review approves identity,
network, filesystem, secret, audit, and rollback controls.

## Local usage

The services are started by [../compose.yaml](../compose.yaml).

Dashboard notebooks are mounted from [notebooks/](notebooks/) into
`marimo-dashboard`, so adding a curated notebook there makes it available
through the `/marimo` index.

Research notebooks and draft issue notes stay under
[research-workspace/](research-workspace/) and are served by
`marimo-codex-workspace` at `http://127.0.0.1:2719`.

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
  - `backend-services/marimo/Dockerfile`
  - `backend-services/marimo/research-workspace/AGENTS.md`
  - `backend-services/compose.yaml`
  - `backend-services/caddy/Caddyfile`
- `sync.scope`: `interface`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
