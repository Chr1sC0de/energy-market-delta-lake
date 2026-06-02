# Local Development

This guide covers the local workflow for running `aemo-etl` against LocalStack-backed storage and for executing the repository's tests and Dagster UI.

## Table of contents

- [LocalStack workflow](#localstack-workflow)
- [Environment variables](#environment-variables)
- [Install dependencies](#install-dependencies)
- [Local Dagster workflow](#local-dagster-workflow)
- [Archive source coverage, cached seed, and bronze replay](#archive-source-coverage-cached-seed-and-bronze-replay)
- [AEMO gas document manifest refresh](#aemo-gas-document-manifest-refresh)
- [Test assumptions](#test-assumptions)
- [Useful commands](#useful-commands)
- [Related docs](#related-docs)

## LocalStack workflow

The project's local **End-to-end test** flow expects an S3-compatible endpoint
and, for integration-style Delta writes, a DynamoDB-backed lock table.

`.localstack.env` currently provides:

```bash
AWS_ENDPOINT_URL=http://localhost:4566
```

Use that environment file when you want Dagster assets to write to LocalStack instead of AWS:

```bash
source .localstack.env
```

Typical local credential expectations mirror the integration test setup:

```bash
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_SESSION_TOKEN=test
export AWS_DEFAULT_REGION=ap-southeast-2
export AWS_ALLOW_HTTP=true
export AWS_S3_LOCKING_PROVIDER=dynamodb
```

These values are not meant to be real AWS credentials. They are placeholders that let boto3, Dagster, and Delta-compatible storage clients run against LocalStack.

## Environment variables

The main project-level environment variables are defined in `src/aemo_etl/configs.py`.

- `DEVELOPMENT_ENVIRONMENT`
  - default: `dev`
  - contributes to all derived bucket names
- `DEVELOPMENT_LOCATION`
  - default: `local`
  - controls whether schedules and sensors default to stopped or running
  - selects the ECS executor only when set to `aws`
- `NAME_PREFIX`
  - default: `energy-market`
  - contributes to all derived bucket names
- `AWS_ENDPOINT_URL`
  - set this for LocalStack
  - omit it when running against AWS-managed services
- `DAGSTER_FAILURE_ALERT_TOPIC_ARN`
  - optional SNS topic ARN for failed-run alert fan-out
  - leave empty locally unless you want the stopped-by-default alert sensor to publish through LocalStack or AWS
- `DAGSTER_FAILURE_ALERT_BASE_URL`
  - optional Dagster UI base URL included in failed-run alert links

Derived bucket behavior:

- landing files go to `{env}-{prefix}-landing`
- archived source files go to `{env}-{prefix}-archive`
- Delta tables go to `{env}-{prefix}-aemo`
- Dagster intermediates go to `{env}-{prefix}-io-manager`

## Install dependencies

The repository targets Python `>=3.13,<3.14`.

Install dependencies with:

```bash
uv sync
```

## Local Dagster workflow

Start the local Dagster UI from the project root:

```bash
dg dev
```

The UI is served at `http://localhost:3000`.

What to expect locally:

- sensors default to stopped
- schedules default to stopped
- assets still materialize correctly when launched manually
- S3 resources use `AWS_ENDPOINT_URL` when you point them at LocalStack

This default-stopped behavior is intentional and comes from `DEFAULT_SENSOR_STATUS` and `DEFAULT_SCHEDULE_STATUS` in `src/aemo_etl/configs.py`.

To validate failed-run alert handling, launch the manual probe asset:

```bash
dg launch --assets "key:ops/testing/failed_run_alert_probe"
```

That asset always raises `Intentional failure for Dagster failed-run alert
testing.`. In a live AWS Dagster deployment, the failed run should trigger
`aemo_etl_failed_run_alert_sensor` and publish to the configured SNS topic. A
local `dg launch` run only validates local Dagster behavior.

To bootstrap or backfill VicGas or STTM public report bundles into the landing
bucket, run the manual jobs:

```bash
uv run dg launch --job download_vicgas_public_report_zip_files_job
uv run dg launch --job download_sttm_day_zip_files_job
```

When `AWS_ENDPOINT_URL` is set, this writes to LocalStack-backed landing
storage. Without that override, the job writes to the configured AWS landing
bucket. Both jobs preserve the source basename in landing keys, and their
`target_files` config can narrow a run to basename-only targets such as
`PublicRpts01.zip` or `DAY01.ZIP`.

For the debugger-driven local stack, use:

```bash
scripts/setup-debugging-environment
```

That script now starts:

- a LocalStack container on `localhost:4566`
- a PostgreSQL container on `localhost:5432`
- `dg dev` with `workspace.dev.yaml`

During that flow, `dagster.dev.yaml` configures Dagster run, schedule, and event-log storage to use the local Postgres container via:

- `DAGSTER_POSTGRES_HOSTNAME=localhost`
- `DAGSTER_POSTGRES_USER=dagster_user`
- `DAGSTER_POSTGRES_PASSWORD=dagster_pass`
- `DAGSTER_POSTGRES_DB=dagster`

## Archive source coverage, cached seed, and bronze replay

Use this runbook when archive-backed local testing or source-table bronze
recovery depends on archived AEMO inputs. It covers two operator paths that
share archive source coverage planning:

- `aemo-e2e-archive-seed` prepares cached Archive inputs for local
  **End-to-end test** runs of the full `gas_model` target.
- `aemo-replay-bronze-archive` rebuilds source-table bronze Delta tables from
  archived source files after an operator has inspected a dry-run plan.

Both paths plan archive coverage from source-table `archive_prefix` and
`glob_pattern` contracts. The planner reports requested, available, selected,
and shortfall counts for each source requirement, then builds bounded object
batches where the caller needs batching. Seed refresh uses a latest-object slice
by sorted archive key. Bronze replay uses all matching source-table objects for
the selected scope.

Run commands from this Subproject:

```bash
cd backend-services/dagster-user/aemo-etl
```

### Choose the archive path

Use the cached Archive seed when you need repeatable local inputs for the
isolated AEMO ETL **End-to-end test** stack or LocalStack-backed developer
compose. The seed path reads from the live Archive bucket only during
`refresh`. Later LocalStack loads read the ignored local cache and write objects
into LocalStack landing storage before Dagster starts.

Use bronze archive replay when current-state source-table bronze data must be
rebuilt from archive storage. Replay reads source-table specs plus Archive
bucket objects, stages parsed rows locally, and writes selected bronze Delta
tables in the AEMO bucket only when `--replace` is present. It does not update
the cached seed, landing storage, source-table specs, or generated artifacts.

The current-state ingestion contract stays in
[Ingestion Flows: Source-table current-state reader journey](../architecture/ingestion_flows.md#source-table-current-state-reader-journey)
and ADR
[0003](../../../../../docs/adr/0003-bounded-current-state-bronze-source-tables.md).
Replay uses the same source-table parser, duplicate-key diagnostics, and
current-state write helper as normal source-table bronze ingestion; this section
only explains the operator path around that contract.

### Inspect archive source coverage for local seed

Inspect the derived seed spec first:

```bash
uv run aemo-e2e-archive-seed spec
```

The CLI imports `aemo_etl.definitions.defs()`, selects the curated
`gas_model` target by `tag:aemo_etl_layer=gas_model`, walks its upstream asset
closure, and writes JSON to stdout. The JSON names the required source-table
archive prefixes and glob patterns plus the zip archive domains needed by
unzipper-backed inputs. The command does not read S3 and does not write a local
cache.

Refresh is opt-in. It defaults to `dev-energy-market-archive`, 3 latest raw
objects per required source table, and 3 latest zip objects per required
domain:

```bash
uv run aemo-e2e-archive-seed refresh
```

Override the slice only when the local **End-to-end test** scenario should use a
different cache horizon:

```bash
uv run aemo-e2e-archive-seed refresh --raw-latest-count 2 --zip-latest-count 1
```

`refresh` reads object listings and selected object bytes from the configured
Archive bucket. It writes cached objects under
`backend-services/.e2e/aemo-etl/archive-seed/objects`, writes
`archive-seed/seed-spec.json`, and writes `seed-run-manifest.json` under
`backend-services/.e2e/aemo-etl`. If any source table or zip domain has fewer
objects than requested, the command exits non-zero after writing a failed
manifest with the shortfall evidence.

For source tables that are validly absent from the live archive slice, add
`--allow-empty-source-table-seed` to write explicit zero-byte placeholders into
the local cache:

```bash
uv run aemo-e2e-archive-seed refresh --allow-empty-source-table-seed
```

Zip-domain shortfalls still fail because the e2e stack needs at least one zip
per required domain to exercise unzipper-backed inputs.

### Load the cached seed into LocalStack

To load the cached seed into LocalStack during local compose startup:

```bash
cd backend-services
AEMO_ETL_E2E_SEED_ENABLED=1 podman-compose up --build -d
```

`aemo-etl-seed-localstack` validates the cache against the selected seed
horizon, uploads the selected cached Archive objects into LocalStack landing
storage, and writes `seed-run-manifest.json`. This load path only needs
LocalStack credentials. It does not read the live Archive bucket.

The broader developer stack keeps its `podman-compose` dependency graph shallow
for Podman startup. Use `backend-services/scripts/aemo-etl-e2e run` when a
strict seed-before-Dagster gate is required:

```bash
backend-services/scripts/aemo-etl-e2e run
```

That command starts Postgres, LocalStack, the cached Archive seed loader, the
AEMO ETL gRPC service, one Dagster webserver, and the Dagster daemon with
generated e2e Dagster config. It builds missing local images by default,
supports `--rebuild`, derives the Podman socket from `XDG_RUNTIME_DIR`, and
validates the cached seed under `backend-services/.e2e/aemo-etl`, or the
explicit `--seed-root` path, using the selected scenario's seed horizon.

The default `full-gas-model` scenario keeps automation stopped and launches
explicit Dagster asset-run batches by dependency wave for every materializable
curated `gas_model` asset selected by `tag:aemo_etl_layer=gas_model` plus its
materializable upstream closure. It uses host webserver port `3001`, a 90
minute timeout, 1 raw object per required source table, 1 zip object per
required domain, and Dagster `max_concurrent_runs` `6`. The
`promotion-gas-model` scenario uses the same one-object seed horizon for Ralph
**Promotion**, uses a 30 minute timeout, and adds the #141
stale-runtime/current-source validation guard. Both direct scenarios skip live
`bronze_nemweb_public_files_*` discovery/listing assets so the stack starts from
seeded LocalStack objects.

Successful non-reuse runs attempt to clean containers, Dagster run-worker
containers, named volumes, and the e2e network. Failures preserve the stack plus
run manifests unless `--always-clean` is used. Each `run-manifest.json` records
total gate, stack startup, Dagster dataflow monitor, and cleanup durations plus
cleanup phase status, final Dagster run, target progress, target materialization
timestamp, and asset-check telemetry. Direct-launch evidence includes the
selected scenario, launch mode, target selector, target asset count, target
asset-check count, target keys, STTM target keys, selected upstream closure
count, skipped live source asset keys, dependency-wave count, run-batch count,
asset batch size, and source-definition evidence when available.

Ralph runs `promotion-gas-model` as a **Promotion** gate after the aggregate
**Push check** for the source revision and before `main` is merged, pushed, or
issue metadata is updated. It protects work that has reached `dev` through
**Local integration** in Gitflow **Delivery mode**. It is not a separate
**Test lane** and it is not a local development benchmark.

### Plan bronze archive replay

Use `aemo-replay-bronze-archive` when an operator needs to rebuild
source-table bronze Delta tables from archived source files. This command
targets source-table bronze assets generated by `df_from_s3_keys`; it does not
target `bronze_nemweb_public_files_*` discovery/listing assets or `unzipper_*`
assets.

Point the command at the intended S3-compatible environment before planning.
For LocalStack, source `.localstack.env` and use local test credentials. For
AWS, leave `AWS_ENDPOINT_URL` unset and use the intended AWS credentials.

Choose exactly one target scope:

- `--all` rebuilds every registered source-table bronze asset.
- `--domain gbb`, `--domain sttm`, or `--domain vicgas` rebuilds one
  source-table domain.
- `--table gbb.bronze_gasbb_contacts` rebuilds one source table by suffix,
  bronze table name, or domain-qualified table ID.

Dry-run is the default. Use it first and keep the output as rebuild evidence:

```bash
uv run aemo-replay-bronze-archive --domain gbb
uv run aemo-replay-bronze-archive --domain sttm
uv run aemo-replay-bronze-archive --table gbb.bronze_gasbb_contacts --json
```

Dry-run lists Archive objects, applies the same target selection and batching
logic that replace mode will use, and writes the plan to stdout. It does not
read object bytes, stage rows, or write Delta tables. The output reports the
source-table ID, Archive bucket and prefix, glob pattern, matching archive file
list, matching file count, planned batch count, total bytes, and target Delta
table URI. The default replay bounds are 134,217,728 bytes and 25 files per
batch; override them with `--batch-bytes` or `--batch-files` only when the
operator deliberately wants a different bound.

This dry-run path protects source-table replay work by proving the scope before
any table replacement happens. It also exposes credential and bucket mistakes:
the target table URI, Archive prefix, file count, and file list must match the
intended environment and source table before `--replace` is safe.

### Replace current-state bronze after operator checks

Run replace only after the dry-run confirms the intended scope:

```bash
uv run aemo-replay-bronze-archive --table gbb.bronze_gasbb_contacts --replace
```

Before replacing current-state bronze data, check:

- the selected environment, credentials, `--archive-bucket`, and `--aemo-bucket`
  point at the intended LocalStack or AWS storage
- the scope selects the intended table, domain, or complete source-table set
- the Archive prefix and glob pattern match the source-table contract
- the matching archive file list contains the expected historical source files
  and excludes unrelated discovery/listing or zip-only inputs
- the planned batch count, total bytes, and default or overridden batch bounds
  are reasonable for the rebuild
- the target Delta table URI names the table that should be replaced
- downstream source silver and `gas_model` rematerialization expectations are
  clear for the affected source table

Replace mode reads selected Archive objects, parses supported non-empty inputs,
stages rows locally, and writes the selected source-table bronze Delta table in
the AEMO bucket. The first non-empty replay batch overwrites the target table.
Later non-empty batches use the same current-state merge predicate as normal
bronze ingestion: merge on `surrogate_key`, update matched rows only when
`source_content_hash` changes, insert new keys, and retain target rows that are
absent from the later batch.

Archive replay also uses the same duplicate-source diagnostics as live bronze
ingestion for each staged replay batch. If latest source rows in a batch contain
distinct records for the same `surrogate_key`, that batch fails so the table key
can be corrected. Earlier batches in the same `--replace` run may already have
overwritten or merged into the target table, so keep the dry-run evidence and
plan remediation before retrying. Headered CSV files use their declared
headers, headerless CSV files use the manifest schema order, and physical CSV
lines containing NUL bytes are dropped before surrogate keys and
`source_content_hash` are calculated.

After replace, review the command output for written batch, written file, and
skipped file counts. Then materialize the paired source silver and affected
`gas_model` assets through the normal Dagster path and inspect asset checks,
especially skipped-key or duplicate-key diagnostics on the affected source
table.

### STTM source-table replay coverage

The current STTM source-table replay surface covers complete v19.1 spec-backed
public reports: `INT651` through `INT684` and `INT687` through `INT691`. Valid
replay targets run from
`sttm.bronze_int651_v1_ex_ante_market_price_rpt_1` through
`sttm.bronze_int691_v1_sttm_ctp_register_rpt_1`, excluding `INT685` and
`INT685B` because those live root CSV reports are landing-only gaps absent from
the v19.1 STTM report specification manifest.

That replay surface feeds the manifest-backed STTM `gas_model` expansion policy
in ADR
[0006](../../../../../docs/adr/0006-sttm-gas-model-uses-fit-plus-extend-modeling.md):
matching STTM grains enrich existing `gas_model` assets, and distinct STTM
grains become new `gas_model` facts.

## AEMO gas document manifest refresh

`bronze_aemo_gas_document_sources` uses a checked-in package manifest for its
daily materialization path. It does not scrape source-page HTML during the
default daily run. The full reader journey lives in the
[AEMO gas document source flow](../architecture/ingestion_flows.md#aemo-gas-document-source-flow).

The manifest refresh command owns source-page discovery for the manifest-backed
document source. It visits configured AEMO gas source pages with Playwright,
extracts direct `https://www.aemo.com.au/-/media/...` media links, validates
those URLs with the same browser-compatible request headers used by the daily
asset, and writes two checked-in JSON files:

- `aemo_gas_document_media_manifest.json`: package input for the daily asset,
  including source-page entries, media-link entries, include decisions,
  document metadata, and `should_download`.
- `aemo_gas_document_media_discovery_report.json`: refresh review evidence,
  including source-page status, candidate and preserved media counts, direct
  media validation status, HTTP status code, content type, content length,
  resolved URL, and validation errors.

Before refreshing or changing document source configuration, inspect:

- `DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES` in
  `src/aemo_etl/factories/aemo_gas_documents/models.py` for the intended source
  pages, `corpus_source` values, include decisions, audit reasons,
  `fetch_links`, and child-page discovery settings.
- The current manifest for `source_page_count`, `media_link_count`,
  `should_download=false` rows, source-page URLs, and document-family changes
  that a refresh would carry into the next daily materialization.
- The current discovery report for failed validation rows, HTTP 403 or other
  repeated status patterns, preserved media counts, and blocked source pages.
- The split between the manifest-backed gas document source and
  `bronze_aemo_major_publications_hub_downloads`. Keep the AEMO
  energy-systems major publications hub observation-only in the manifest-backed
  source unless the source-family ownership changes in code and docs together.
- Downstream corpus references in ADR
  [0010](../../../../../docs/adr/0010-gas-market-knowledge-base.md) and the
  [Gas market knowledge base Subproject](../../../../../tools/gas-market-knowledge-base/README.md)
  when the refresh changes raw document availability for later corpus work.

Failed direct-media validation rows stay in the manifest with
`should_download=false`; the daily asset records those rows without requesting
the failed media URL or landing bytes. If a row marked `should_download=true`
later fails during daily materialization, the asset records a metadata-only row
with the failure reason and reports it through `failed_download_count`. If a
configured source page is blocked or unreadable, refresh preserves existing
media entries for that page instead of replacing them with an empty result.

This workflow is separate from source-table CSV ingestion. It does not declare
source-table schemas, `glob_pattern` values, source silver assets, or archive
replay scope. Included document media bytes land under
`LANDING_BUCKET/bronze/aemo_gas_documents` and move to
`ARCHIVE_BUCKET/bronze/aemo_gas_documents` only after the bronze metadata Delta
write succeeds.

`bronze_aemo_major_publications_hub_downloads` is the approved live-discovery
source family for landing public major-publications, library, GSOO, and WA GSOO
publication bytes under `bronze/aemo_major_publications`. Its materialization
metadata reports target table URI, landing/archive roots, source page count,
included download count, failed count, and review-needed count. Duplicate
normalized source URLs are downloaded once per materialization, and
byte-identical files share one content-addressed archive object while
preserving each metadata row. Validate that source family with
`make component-test` for the AEMO ETL **Component test** lane and
`make run-prek` for the AEMO ETL **Commit check**.

Run commands from this Subproject:

```bash
cd backend-services/dagster-user/aemo-etl
```

Refresh the manifest and discovery report for local review without staging or
committing generated files:

```bash
uv run aemo-refresh-gas-document-media-manifest --no-commit
```

Omit `--no-commit` only when the refreshed generated JSON files are ready to be
staged and committed. The CLI stages and commits only the checked-in AEMO gas
document media manifest and discovery report files. If a configured source page
is blocked or unreadable, the refresh preserves any existing media entries for
that page rather than replacing them with an empty result. If direct-media
validation fails, the refresh records the failure in the discovery report and
sets the manifest row `should_download=false` until a later successful refresh
can make it downloadable again. If the local Playwright Chromium binary is
missing, install it once with
`uv run playwright install chromium`.

## Test assumptions

Integration tests in `tests/integration/conftest.py` make these assumptions:

- `LOCAL_INTEGRATION_TESTS=1` is set; otherwise the lane skips before
  containers are started
- LocalStack is started dynamically for the test session
- `AWS_PROFILE` is removed
- local test credentials are injected
- four buckets are created:
  - landing
  - archive
  - AEMO
  - IO manager
- a DynamoDB table named `delta_log` is created for Delta locking

Representative integration behavior lives in `tests/integration/test_gbb_vicgas.py`, which uploads sample files into landing storage, runs bronze assets with explicit `s3_keys`, then materializes the matching silver assets and asserts that all asset checks pass.

## Useful commands

```bash
make unit-test
make component-test
make fast-test
make integration-test
make integration-test-testmon
make duplicate-check
make run-prek
uv run aemo-e2e-archive-seed spec
uv run aemo-e2e-archive-seed refresh
uv run aemo-refresh-gas-document-media-manifest --no-commit
uv run aemo-replay-bronze-archive --domain gbb
uv run aemo-replay-bronze-archive --domain sttm
uv run aemo-replay-bronze-archive --table gbb.bronze_gasbb_contacts --replace
```

`make run-prek` is this Subproject's **Commit check**. It includes executable
shell script header documentation alongside the existing shell formatting,
shell linting, Python, pytest, and Dagster validation hooks. Ruff enforces
Google-style docstrings for public production ETL APIs while excluding tests and
generated-like raw source-table and TypedDict model definition surfaces from the
docstring ratchet. It also applies the default `C901` complexity threshold
across the Subproject.

## Related docs

- [High-level architecture](../architecture/high_level_architecture.md)
- [Ingestion sequence diagrams](../architecture/ingestion_flows.md)
- [ADR 0003: bounded current-state bronze source tables](../../../../../docs/adr/0003-bounded-current-state-bronze-source-tables.md)
- [ADR 0006: STTM gas_model fit-plus-extend modeling](../../../../../docs/adr/0006-sttm-gas-model-uses-fit-plus-extend-modeling.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/asset_organization.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/configs.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/alerts.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/jobs/download_vicgas_public_report_zip_files.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/testing.py`
  - `backend-services/dagster-user/aemo-etl/Makefile`
  - `backend-services/dagster-user/aemo-etl/.pre-commit-config.yaml`
  - `backend-services/dagster-user/aemo-etl/pyproject.toml`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/archive_source_planning.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/replay_bronze_archive.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/archive_replay.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/e2e_archive_seed.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/refresh_aemo_gas_document_manifest.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/aemo_gas_documents.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/assets.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/manifest.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/models.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/scraper.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/e2e_archive_seed.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/definitions.py`
  - `backend-services/scripts/aemo-etl-e2e`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/current_state.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/assets.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/source_tables.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/_manifest.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/source_tables.json`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int651_v1_ex_ante_market_price_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int652_v1_ex_ante_schedule_quantity_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int653_v3_ex_ante_pipeline_price_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int654_v1_provisional_market_price_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int655_v1_provisional_schedule_quantity_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int656_v2_provisional_pipeline_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int657_v2_ex_post_market_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int658_v1_latest_allocation_quantity_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int659_v1_bid_offer_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int660_v1_contingency_gas_bids_and_offers_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int661_v1_contingency_gas_called_scheduled_bid_offer_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int662_v1_provisional_deviation_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int663_v1_provisional_variation_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int664_v1_daily_provisional_mos_allocation_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int665_v1_mos_stack_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int666_v1_market_notice_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int667_v1_market_parameters_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int668_v1_schedule_log_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int669_v1_settlement_version_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int670_v1_registered_participants_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int671_v1_hub_facility_definition_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int672_v1_cumulative_price_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int673_v1_total_contingency_bid_offer_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int674_v1_total_contingency_gas_schedules_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int675_v1_default_allocation_notice_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int676_v1_rolling_average_price_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int677_v1_contingency_gas_price_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int678_v1_net_market_balance_daily_amounts_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int679_v1_net_market_balance_settlement_amounts_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int680_v1_dp_flag_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int681_v1_daily_provisional_capacity_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int682_v1_settlement_mos_and_capacity_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int683_v1_provisional_used_mos_steps_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int684_v1_settlement_used_mos_steps_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int687_v1_facility_hub_capacity_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int688_v1_allocation_warning_limit_thresholds_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int689_v1_expost_allocation_quantity_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int690_v1_deviation_price_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int691_v1_sttm_ctp_register_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/resources.py`
  - `backend-services/dagster-user/aemo-etl/tests/integration/conftest.py`
  - `backend-services/dagster-user/aemo-etl/.localstack.env`
  - `backend-services/dagster-user/aemo-etl/scripts/setup-debugging-environment`
  - `backend-services/dagster-user/aemo-etl/dagster.dev.yaml`
  - `backend-services/dagster-user/aemo-etl/workspace.dev.yaml`
  - `docs/adr/0003-bounded-current-state-bronze-source-tables.md`
  - `docs/adr/0006-sttm-gas-model-uses-fit-plus-extend-modeling.md`
- `sync.scope`: `operations, tooling`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
