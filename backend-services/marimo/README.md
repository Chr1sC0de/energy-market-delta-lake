# Marimo Notebook Services

Local Marimo Subproject used in the backend-services compose stack. It provides
a curated dashboard image and a separate local-only Marimo-Codex research
workspace image against the same LocalStack-backed data flows used by the rest
of the repo.

## Table of contents

- [What it does](#what-it-does)
- [Image split](#image-split)
- [Local table explorer](#local-table-explorer)
- [Gas market dashboard](#gas-market-dashboard)
- [Local usage](#local-usage)
- [Validation](#validation)
- [Related docs](#related-docs)

## What it does

The dashboard app in [src/marimoserver/main.py](src/marimoserver/main.py):

- exposes `/health` for container health checks
- discovers `*.py` notebooks from `notebooks/`
- mounts each notebook as a marimo sub-app under `/marimo/<notebook-name>`
- serves a simple index page at `/marimo`
- links the Caddy-served shared theme at `/theme.css` for the index and sample
  notebook head
- applies a MIME-type fix middleware for `woff` and `woff2` assets

In the local compose stack, Caddy proxies `/marimo*` traffic to
`marimo-dashboard`. Most notebook routes are protected by the authentication
service, while static asset and websocket paths are proxied through directly.
Caddy still serves `/theme.css` from its static root, so notebook pages can use
the same palette as the root portfolio page.

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

## Local table explorer

[notebooks/local_table_explorer.py](notebooks/local_table_explorer.py) discovers
the compose-local `dev-energy-market-*` LocalStack buckets and shows bucket
health, table-like prefixes, and on-demand inspection for selected tables.

The explorer reads the same AWS settings passed to the Marimo service by
compose: `AWS_ENDPOINT_URL`, `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, and `AWS_ALLOW_HTTP`. It always checks the default
local buckets:

- `dev-energy-market-aemo`
- `dev-energy-market-landing`
- `dev-energy-market-archive`
- `dev-energy-market-io-manager`

Prefixes with `_delta_log/` are classified as Delta tables. Prefixes with one or
more parquet files are classified as parquet tables. Empty buckets render bucket
health and an empty state instead of raising notebook exceptions. Selecting a
live table and running inspection loads schema, exact row count, and a small
preview.

## Gas market dashboard

The default notebook,
[notebooks/sample_energy_market.py](notebooks/sample_energy_market.py), is a
local gas market overview dashboard over curated `silver.gas_model` outputs. It
reads Delta tables from:

```text
s3://<AEMO_BUCKET>/silver/gas_model/<table>
```

The dashboard discovers its bucket and storage settings from environment
variables available to the Marimo service:

- `AEMO_BUCKET`, when explicitly set
- `DEVELOPMENT_ENVIRONMENT` and `NAME_PREFIX`, used to derive the default
  `<environment>-<name-prefix>-aemo` bucket
- `AWS_ENDPOINT_URL`, `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`,
  `AWS_SECRET_ACCESS_KEY`, and `AWS_ALLOW_HTTP`, passed through to Delta Lake
  storage options

It gives first-look sections for:

- prices from `silver_gas_fact_market_price`
- schedules from `silver_gas_fact_schedule_run` and
  `silver_gas_fact_scheduled_quantity`
- flow and capacity from connection-point flow, facility flow/storage,
  linepack, capacity outlook, and capacity auction facts
- source coverage from the `source_system`, `source_table`, and
  `source_tables` columns on loaded `gas_model` outputs

When LocalStack has no seeded or materialized gas_model tables yet, the notebook
renders section empty states instead of surfacing Delta read tracebacks.

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

With the local backend stack running, open the Marimo index through Caddy and
choose `local_table_explorer` or `sample_energy_market`:

```text
http://localhost/marimo
```

For direct notebook development from this Subproject, point the notebook at the
host-exposed LocalStack endpoint:

```bash
cd backend-services/marimo
AWS_ENDPOINT_URL=http://localhost:4566 uv run marimo edit notebooks/sample_energy_market.py
```

Use the same pattern for the local table explorer:

```bash
cd backend-services/marimo
AWS_ENDPOINT_URL=http://localhost:4566 uv run marimo edit notebooks/local_table_explorer.py
```

Materialize the `gas_model` assets in Dagster, or seed LocalStack with curated
outputs, then refresh the dashboard to see populated sections.

## Validation

From this Subproject, run the Marimo **Component test** lane:

```bash
uv run pytest tests/component
```

Run the Marimo **Commit check** surface before handing changes to Ralph:

```bash
prek run -a
```

## Related docs

- [Local backend-services stack](../README.md)
- [Authentication service](../authentication/README.md)
- [Gas-model ERDs](../dagster-user/aemo-etl/docs/gas_model/README.md)
- [Repository workflow](../../docs/repository/workflow.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/marimo/src/marimoserver/main.py`
  - `backend-services/marimo/Dockerfile`
  - `backend-services/marimo/research-workspace/AGENTS.md`
  - `backend-services/marimo/src/marimoserver/gas_dashboard.py`
  - `backend-services/marimo/src/marimoserver/table_explorer.py`
  - `backend-services/marimo/notebooks/head.html`
  - `backend-services/marimo/notebooks/sample_energy_market.py`
  - `backend-services/marimo/notebooks/local_table_explorer.py`
  - `backend-services/compose.yaml`
  - `backend-services/caddy/Caddyfile`
  - `backend-services/caddy/theme.css`
- `sync.scope`: `interface`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
