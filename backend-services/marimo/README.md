# Marimo Notebook Services

Marimo Subproject used by the backend-services compose stack and the deployed
AWS dashboard. It provides a curated dashboard image and a separate local-only
Marimo-Codex research workspace image.

## Table of contents

- [What it does](#what-it-does)
- [Image split](#image-split)
- [Table explorer](#table-explorer)
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

In local compose and AWS, Caddy proxies `/marimo*` traffic to
`marimo-dashboard`. Most notebook routes are protected by the authentication
service, while `/marimo/health`, static asset paths, and websocket paths are
proxied through directly. Caddy still serves `/theme.css` from its static root,
so notebook pages can use the same palette as the root portfolio page.

## Image split

[Dockerfile](Dockerfile) exposes two image targets:

- `dashboard`: used by the `marimo-dashboard` compose service. It runs the
  FastAPI wrapper, mounts [notebooks/](notebooks/) read-only, and keeps Codex
  tooling out of the curated dashboard image.
- `codex-workspace`: used by the `marimo-codex-workspace` compose service. It
  runs `marimo edit` against the writable
  [research-workspace/](research-workspace/) mount on `127.0.0.1:2719` and
  includes [research-workspace/AGENTS.md](research-workspace/AGENTS.md) for
  local notebook research, data access boundaries, and issue-draft generation.

The curated dashboard image is deployed to AWS on a private EC2 instance behind
Caddy. The research workspace is for human-operated local Marimo-Codex research
only; compose does not launch unattended Codex, and deployed Codex execution is
deferred until a security review approves identity, network, filesystem, secret,
audit, and rollback controls.

## Table explorer

[notebooks/table_explorer.py](notebooks/table_explorer.py) discovers configured
S3-compatible buckets, overlays the Dagster GraphQL table asset catalogue, and
shows bucket health, table assets, storage status, catalogue controls, and
cached inspection for selected live tables.

The explorer reads the same AWS settings passed to the Marimo service by
compose: `AWS_ENDPOINT_URL`, `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`,
`AWS_SECRET_ACCESS_KEY`, and `AWS_ALLOW_HTTP`. It also reads
`DAGSTER_GRAPHQL_URL`, defaulting inside compose to
`http://dagster-webserver-guest:3000/dagster-webserver/guest/graphql`. The
compose services pass the same path-prefixed default with a shell override so
local operators can point Marimo at a different reachable Dagster GraphQL
endpoint without editing the notebook.

In local compose, it checks the default local buckets:

- `dev-energy-market-aemo`
- `dev-energy-market-landing`
- `dev-energy-market-archive`
- `dev-energy-market-io-manager`

In AWS, Pulumi sets `DEVELOPMENT_LOCATION=aws`, `MARIMO_TABLE_BUCKETS`, and
`MARIMO_FULL_TABLE_SCAN_ENABLED=false`. The deployed dashboard uses instance
profile credentials, checks only the AEMO and IO-manager buckets, caps discovery
at 10,000 objects per bucket, and loads at most 100 preview rows per selected
table. It does not request account-wide S3 bucket listing permission in AWS.
Global text search, sort, and selected-column statistics are disabled in that
bounded mode because they require a full table scan.

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
free-text asset search. For a selected live table, the preview
controls support row limit, column picker, sort column and direction, text
search, exact row count, selected-column null counts, selected-column distinct
counts, and preview rows when full table scans are enabled. In AWS, the preview
is deliberately bounded and reports preview rows loaded instead of an exact row
count. The notebook caches the selected table scan for the Marimo session, so
changing preview controls does not repeatedly read the same table. Use
**Refresh table scan** after materializing or reloading data.

Unmaterialized assets and empty local tables show materialization guidance
instead of a traceback. In a fresh compose stack, LocalStack may contain empty
or schema-only table prefixes before any Dagster run has produced rows; those
tables are not previewable until the asset is materialized or curated outputs
are seeded.

## Gas market dashboard

The default notebook,
[notebooks/sample_energy_market.py](notebooks/sample_energy_market.py), is a
gas market overview dashboard over curated `silver.gas_model` outputs. It
reads Parquet datasets from:

```text
s3://<AEMO_BUCKET>/silver/gas_model/<table>
```

The dashboard discovers its bucket and storage settings from environment
variables available to the Marimo service:

- `AEMO_BUCKET`, when explicitly set
- `DEVELOPMENT_ENVIRONMENT` and `NAME_PREFIX`, used to derive the default
  `<environment>-<name-prefix>-aemo` bucket
- `AWS_ENDPOINT_URL`, `AWS_DEFAULT_REGION`, `AWS_ACCESS_KEY_ID`,
  `AWS_SECRET_ACCESS_KEY`, and `AWS_ALLOW_HTTP`, passed through to Polars S3
  storage options when set

In AWS mode, the dashboard omits LocalStack endpoint and static credential
options, uses the EC2 instance profile, and limits each loaded table to the
preview row cap.

It gives first-look sections for:

- prices from `silver_gas_fact_market_price`
- schedules from `silver_gas_fact_schedule_run` and
  `silver_gas_fact_scheduled_quantity`
- flow and capacity from connection-point flow, facility flow/storage,
  linepack, capacity outlook, and capacity auction facts
- source coverage from the `source_system`, `source_table`, and
  `source_tables` columns on loaded `gas_model` outputs

When storage has no seeded or materialized `gas_model` tables yet, the notebook
renders section empty states instead of surfacing Parquet read tracebacks.

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
choose `table_explorer` or `sample_energy_market`:

```text
http://localhost/marimo
```

The table explorer is compose-first for local development. Start the stack from
[../compose.yaml](../compose.yaml), wait for `localstack`, `aemo-etl`, both
Dagster webservers, and `marimo-dashboard` to be healthy, then open
`/marimo` and choose `table_explorer`. The explorer can list Dagster table
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
AWS_ENDPOINT_URL=http://localhost:4566 uv run marimo edit notebooks/table_explorer.py
```

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
  - `backend-services/marimo/Dockerfile`
  - `backend-services/marimo/research-workspace/AGENTS.md`
  - `backend-services/marimo/src/marimoserver/gas_dashboard.py`
  - `backend-services/marimo/src/marimoserver/dagster_graphql.py`
  - `backend-services/marimo/src/marimoserver/table_explorer.py`
  - `backend-services/marimo/notebooks/head.html`
  - `backend-services/marimo/notebooks/sample_energy_market.py`
  - `backend-services/marimo/notebooks/table_explorer.py`
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
