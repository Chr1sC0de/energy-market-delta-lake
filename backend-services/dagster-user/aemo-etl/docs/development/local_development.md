# Local Development

This guide covers the local workflow for running `aemo-etl` against LocalStack-backed storage and for executing the repository's tests and Dagster UI.

## Table of contents

- [LocalStack workflow](#localstack-workflow)
- [Environment variables](#environment-variables)
- [Install dependencies](#install-dependencies)
- [Local Dagster workflow](#local-dagster-workflow)
- [Cached Archive seed runbook](#cached-archive-seed-runbook)
- [Bronze archive rebuild runbook](#bronze-archive-rebuild-runbook)
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

## Cached Archive seed runbook

Use `aemo-e2e-archive-seed` to prepare local **End-to-end test** inputs for the
full `gas_model` target without requiring every later local stack run to have
live AWS archive access.

Run commands from this Subproject:

```bash
cd backend-services/dagster-user/aemo-etl
```

Inspect the derived seed spec:

```bash
uv run aemo-e2e-archive-seed spec
```

The CLI imports `aemo_etl.definitions.defs()`, selects the full `gas_model`
target and upstream assets, and emits JSON containing the required source-table
archive glob patterns plus zip seed domains.

Refresh is opt-in. It defaults to `dev-energy-market-archive`, 3 latest raw
objects per required source table, and 3 latest zip objects per required domain:

```bash
uv run aemo-e2e-archive-seed refresh
```

Override the slice deliberately when a smaller local **End-to-end test** cache is
needed:

```bash
uv run aemo-e2e-archive-seed refresh --raw-latest-count 2 --zip-latest-count 1
```

The cache and `seed-run-manifest.json` are written under
`backend-services/.e2e/aemo-etl` by default. If any required source table or zip
domain has fewer live archive objects than requested, refresh exits non-zero and
records the shortfall in that manifest.

To require the cached seed before the local compose `aemo-etl` service starts:

```bash
cd backend-services
AEMO_ETL_E2E_SEED_ENABLED=1 podman-compose up --build -d
```

`aemo-etl-seed-localstack` validates the cache, uploads the selected cached
objects into LocalStack landing storage, and completes before Dagster starts.
This load path only needs LocalStack credentials and does not read the live
archive bucket.

For the isolated AEMO ETL **End-to-end test** stack, run the backend-services
command instead of the broader fixed developer compose stack:

```bash
backend-services/scripts/aemo-etl-e2e run
```

That command starts Postgres, LocalStack, the cached Archive seed loader, the
AEMO ETL gRPC service, one Dagster webserver, and the Dagster daemon with
generated e2e Dagster config. It builds missing local images by default, supports
`--rebuild`, derives the Podman socket from `XDG_RUNTIME_DIR`, and validates the
cached seed under `backend-services/.e2e/aemo-etl`, or the explicit
`--seed-root` path, using the selected scenario's seed horizon.
Successful non-reuse runs attempt to clean containers, Dagster run-worker
containers, named volumes, and the e2e network; pre-run cleanup treats
already-absent e2e resources as benign. Post-success cleanup also treats an
already-absent e2e network as benign when compose has already removed the stack,
while other post-run cleanup warnings or failures stay visible in the run
manifest as cleanup status and `cleanup_issues` without changing a successful
dataflow result. Failures preserve the stack plus run manifests unless
`--always-clean` is used. The run manifest records total gate, stack startup,
Dagster dataflow monitor, and cleanup durations plus cleanup phase status, final
Dagster run, target progress, target materialization timestamp, and asset-check
telemetry. For the `promotion-gas-model` direct launch path, the dataflow
manifest also records scenario evidence: selected scenario, launch mode, target
group, target asset count, selected upstream closure count, skipped live source
asset keys, dependency-wave count, run-batch count, and asset batch size.
After startup, it uses Dagster GraphQL to drive the selected scenario. The
default `full-gas-model` scenario starts only the intended unzipper,
event-driven raw, and gas model automation sensors. NEMWeb discovery schedules,
the failed-run alert sensor, the date-dimension schedule, and maintenance
schedules remain stopped. The command bootstraps non-sensor prerequisites,
including date dimension and table metadata materialization, then monitors until
the full `gas_model` target succeeds, fails, or the timeout is reached. The
`full-gas-model` scenario uses host webserver port `3001`, a 90 minute timeout,
3 raw objects per required source table, 3 zip objects per required domain, and
Dagster `max_concurrent_runs` `6`. The `promotion-gas-model` scenario keeps
automation stopped and launches one explicit Dagster asset run for every
materializable `gas_model` asset plus its materializable upstream closure,
while skipping live `bronze_nemweb_public_files_*` discovery/listing assets and
narrowing the seed horizon to 1 raw object and 1 zip object. Promotion asset
batches use Dagster's in-process executor inside Podman run-worker containers,
with a 20 minute timeout and `max_concurrent_runs` `6`; Ralph **Promotion** uses
that scenario from the isolated source worktree. Direct Promotion launches pace
asset-run batch submission against `max_concurrent_runs` before starting more
batches in a dependency wave so the queued-run guard remains bounded. Override
these values with
`--webserver-port`, `--timeout-seconds`, `--max-concurrent-runs`,
`--raw-latest-count`, and `--zip-latest-count`.

The required e2e coverage remains every materializable Dagster asset in group
`gas_model`, plus final asset-check status for that target. Current
`dg list defs --assets "group:gas_model" --json` discovery evidence is 29
assets and 112 asset checks, including
`silver/metadata/silver_table_metadata`. The `promotion-gas-model` scenario
enforces Promotion guard regression budgets from the #78 targeted baseline:
total gate duration at or below 20 minutes, peak active runs at or below `6`,
peak queued runs at or below `6`, total Dagster runs at or below `48`, target
progress exactly `29/29`, and missing or failed target assets and asset checks
at `0`. Budget failures print observed values, thresholds, and the
`run-manifest.json` path. These are Promotion guard budgets, not generic local
development performance claims; the full scenario prints the same telemetry
without enforcing them.

The generated compose stack uses fixed service IPs for Postgres, LocalStack,
and the AEMO ETL code server so Podman run-worker containers do not depend on
container DNS during high-concurrency **Promotion** gates.

## Bronze archive rebuild runbook

Use `aemo-replay-bronze-archive` when an operator needs to rebuild
source-table bronze Delta tables from archived source files. This runbook is for
source-table bronze assets generated by `df_from_s3_keys`; it is not for
`bronze_nemweb_public_files_*` discovery/listing assets or for `unzipper_*`
assets.

Run commands from this Subproject:

```bash
cd backend-services/dagster-user/aemo-etl
```

Point the command at the intended S3-compatible environment before planning.
For LocalStack, source `.localstack.env` and use local test credentials. For
AWS, leave `AWS_ENDPOINT_URL` unset and use the intended AWS credentials.

Choose exactly one target scope:

- `--all` rebuilds every registered source-table bronze asset
- `--domain gbb`, `--domain sttm`, or `--domain vicgas` rebuilds one
  source-table domain
- `--table gbb.bronze_gasbb_contacts` rebuilds one source table

Dry-run is the default. Use it first and keep the output as rebuild evidence:

```bash
uv run aemo-replay-bronze-archive --domain gbb
uv run aemo-replay-bronze-archive --domain sttm
uv run aemo-replay-bronze-archive --table gbb.bronze_gasbb_contacts --json
```

Review the dry-run output before writing. It reports the archive prefix, glob
pattern, matching archive files, planned batch count, total bytes, and target
Delta table URI. The default replay bounds are 134,217,728 bytes and 25 files
per batch; override them with `--batch-bytes` or `--batch-files` only when the
operator deliberately wants a different bound.

Run replace only after the dry-run confirms the intended scope:

```bash
uv run aemo-replay-bronze-archive --table gbb.bronze_gasbb_contacts --replace
```

Replace mode writes the selected source-table bronze Delta table in the AEMO
bucket from archive storage. The first non-empty replay batch overwrites the
target table. Later non-empty batches use the same current-state merge predicate
as normal bronze ingestion: merge on `surrogate_key`, update matched rows only
when `source_content_hash` changes, insert new keys, and retain target rows that
are absent from the later batch.

Treat `--replace` as explicit operator intent to rebuild the selected table from
the selected archive scope. If the dry-run archive file list or target Delta URI
does not match the intended rebuild, stop and correct the target selection,
bucket options, or credentials before writing.

For STTM, the current source-table replay surface covers complete v19.1
spec-backed public reports: `INT651` through `INT684` and `INT687` through
`INT691`. Valid replay targets run from
`sttm.bronze_int651_v1_ex_ante_market_price_rpt_1` through
`sttm.bronze_int691_v1_sttm_ctp_register_rpt_1`, excluding `INT685` and
`INT685B` because those live root CSV reports are landing-only gaps absent from
the v19.1 STTM report specification manifest.

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

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/configs.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/alerts.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/jobs/download_vicgas_public_report_zip_files.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/testing.py`
  - `backend-services/dagster-user/aemo-etl/Makefile`
  - `backend-services/dagster-user/aemo-etl/.pre-commit-config.yaml`
  - `backend-services/dagster-user/aemo-etl/pyproject.toml`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/replay_bronze_archive.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/archive_replay.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/e2e_archive_seed.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/e2e_archive_seed.py`
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
- `sync.scope`: `operations, tooling`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
