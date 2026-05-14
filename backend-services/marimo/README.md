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
- [GBB interactive map](#gbb-interactive-map)
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
the compose-local `dev-energy-market-*` LocalStack buckets, overlays the local
Dagster GraphQL table asset catalogue, and shows bucket health, table assets,
storage status, catalogue controls, and cached inspection for selected live
tables.

The explorer reads the same AWS settings passed to the Marimo service by
compose: `AWS_ENDPOINT_URL`, `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, and `AWS_ALLOW_HTTP`. It also reads
`DAGSTER_GRAPHQL_URL`, defaulting inside compose to
`http://dagster-webserver-guest:3000/graphql`. The compose services pass the
same default with a shell override so local operators can point Marimo at a
different reachable Dagster GraphQL endpoint without editing the notebook.

It always checks the default local buckets:

- `dev-energy-market-aemo`
- `dev-energy-market-landing`
- `dev-energy-market-archive`
- `dev-energy-market-io-manager`

Prefixes with `_delta_log/` are classified as Delta tables. Prefixes with one or
more parquet files are classified as parquet tables. When GraphQL is reachable,
the catalogue includes table assets even when their `dagster/uri` prefix has not
been materialized in LocalStack yet. The table view distinguishes live,
unmaterialized, missing, and GraphQL-unavailable rows. Selected GraphQL assets
show asset key, group, kinds, description, `dagster/uri`, materializable and
executable flags, latest materialization timestamp, and column metadata when
Dagster provides it. If GraphQL is unavailable, the notebook warns clearly and
continues in storage-only mode. Empty buckets render bucket health and an empty
state instead of raising notebook exceptions.

The catalogue controls filter by asset group, layer or domain, live status, and
free-text asset search. For a selected live LocalStack table, the preview
controls support row limit, column picker, sort column and direction, text
search, exact row count, selected-column null counts, selected-column distinct
counts, and preview rows. The notebook caches the selected table scan for the
Marimo session, so changing preview controls does not repeatedly read the same
table from LocalStack. Use **Refresh table scan** after materializing or
re-seeding data.

Unmaterialized assets and empty local tables show materialization guidance
instead of a traceback. In a fresh compose stack, LocalStack may contain empty
or schema-only table prefixes before any Dagster run has produced rows; those
tables are not previewable until the asset is materialized or curated outputs
are seeded.

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

## GBB interactive map

[notebooks/gbb_interactive_map.py](notebooks/gbb_interactive_map.py) provides a
local Marimo replica of the AEMO GBB interactive map over curated
`silver.gas_model` outputs. The supporting helper in
[src/marimoserver/gbb_interactive_map.py](src/marimoserver/gbb_interactive_map.py)
loads facility, location, connection-point, actual-flow, nomination-forecast,
and capacity-outlook tables from:

```text
s3://<AEMO_BUCKET>/silver/gas_model/<table>
```

The notebook renders a Plotly `Scattergeo` map using Plotly's built-in
geographic base, approximate pipeline routes, and overlays for summary,
pipeline, production, and storage views. The coordinate catalogue is display
metadata in the Marimo helper, not authoritative GIS standing data. Pipeline
flow direction follows AEMO's documented GBB map rule shape: past gas days use
`silver_gas_fact_facility_flow_storage`, while the current gas day and future
gas days use `silver_gas_fact_nomination_forecast`. Capacity comes from
`silver_gas_fact_capacity_outlook`. The map still renders if LocalStack has no
materialized inputs; the notebook shows a compact input warning, keeps the
table-level diagnostics in an accordion, and falls back to standing pipeline
metadata. Direct notebook runs preflight the local S3 endpoint so an offline
LocalStack instance becomes a fast degraded state instead of six slow table read
attempts.

During development, keep the notebook pointed at LocalStack and hydrate the
required `silver/gas_model` table prefixes there instead of reading live S3 from
the notebook process. Use
[scripts/sync-gbb-map-s3-to-localstack.sh](scripts/sync-gbb-map-s3-to-localstack.sh)
to mirror the six GBB map input table prefixes from live S3 into a local cache,
then upload that cache into the LocalStack AEMO bucket. The helper reads Delta
tables first and falls back to parquet-prefix snapshots, matching the current
`gas_model` outputs. Subsequent development runs can reload from the cache
without live S3 access.

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
choose `local_table_explorer`, `sample_energy_market`, or `gbb_interactive_map`:

```text
http://localhost/marimo
```

The table explorer is compose-first. Start the stack from
[../compose.yaml](../compose.yaml), wait for `localstack`, `aemo-etl`, both
Dagster webservers, and `marimo-dashboard` to be healthy, then open
`/marimo` and choose `local_table_explorer`. The explorer can list Dagster table
assets before local data exists, but previews require materialized LocalStack
tables. Materialize the target assets from the Dagster UI or a local Dagster
launch, then refresh the table scan in the notebook.

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

Use the same pattern for the GBB interactive map:

```bash
cd backend-services/marimo
AWS_ENDPOINT_URL=http://localhost:4566 uv run marimo edit notebooks/gbb_interactive_map.py
```

If the GBB map inputs are missing from LocalStack, refresh or load the local
GBB map cache before opening the notebook:

```bash
cd backend-services/marimo
scripts/sync-gbb-map-s3-to-localstack.sh --from live
```

Use cached data for repeat offline development:

```bash
cd backend-services/marimo
scripts/sync-gbb-map-s3-to-localstack.sh --from cache
```

`--from live` requires normal AWS credentials for the source bucket and writes
the mirrored table prefixes under
`backend-services/.e2e/marimo-gbb-map/aemo`. Both modes upload only the table
prefixes used by `gbb_interactive_map.py` into
`s3://dev-energy-market-aemo/silver/gas_model/...` on LocalStack by default.

When running the table explorer outside compose, set `DAGSTER_GRAPHQL_URL` to a
reachable Dagster GraphQL endpoint if you want the catalogue overlay. Leaving it
unset is still usable: the notebook shows a GraphQL warning and keeps
storage-only discovery and preview behavior. Outside compose, previews still
require `AWS_ENDPOINT_URL` to point at the LocalStack endpoint that holds the
materialized table data.

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
  - `backend-services/marimo/pyproject.toml`
  - `backend-services/marimo/Dockerfile`
  - `backend-services/marimo/scripts/sync-gbb-map-s3-to-localstack.sh`
  - `backend-services/marimo/research-workspace/AGENTS.md`
  - `backend-services/marimo/src/marimoserver/gas_dashboard.py`
  - `backend-services/marimo/src/marimoserver/gbb_interactive_map.py`
  - `backend-services/marimo/src/marimoserver/dagster_graphql.py`
  - `backend-services/marimo/src/marimoserver/table_explorer.py`
  - `backend-services/marimo/notebooks/head.html`
  - `backend-services/marimo/notebooks/sample_energy_market.py`
  - `backend-services/marimo/notebooks/gbb_interactive_map.py`
  - `backend-services/marimo/notebooks/local_table_explorer.py`
  - `backend-services/compose.yaml`
  - `backend-services/caddy/Caddyfile`
  - `backend-services/caddy/theme.css`
- `sync.scope`: `interface`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `uv run pytest tests/component`
  - `prek run -a`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
