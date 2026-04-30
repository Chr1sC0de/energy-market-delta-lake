# Local Development

This guide covers the local workflow for running `aemo-etl` against LocalStack-backed storage and for executing the repository's tests and Dagster UI.

## Table of contents

- [LocalStack workflow](#localstack-workflow)
- [Environment variables](#environment-variables)
- [Install dependencies](#install-dependencies)
- [Local Dagster workflow](#local-dagster-workflow)
- [Test assumptions](#test-assumptions)
- [Useful commands](#useful-commands)
- [Related docs](#related-docs)

## LocalStack workflow

The project's local end-to-end flow expects an S3-compatible endpoint and, for integration-style Delta writes, a DynamoDB-backed lock table.

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

To bootstrap or backfill VicGas public report bundles into the landing bucket,
run the manual job:

```bash
uv run dg launch --job download_vicgas_public_report_zip_files_job
```

When `AWS_ENDPOINT_URL` is set, this writes to LocalStack-backed landing
storage. Without that override, the job writes to the configured AWS landing
bucket.

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
```

`make run-prek` is this Subproject's **Commit check**. It includes executable
shell script header documentation alongside the existing shell formatting,
shell linting, Python, pytest, and Dagster validation hooks. Ruff enforces
Google-style docstrings for public production ETL APIs while excluding tests and
generated-like or schema-heavy data definition surfaces.

## Related docs

- [High-level architecture](../architecture/high_level_architecture.md)
- [Ingestion sequence diagrams](../architecture/ingestion_flows.md)

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
  - `backend-services/dagster-user/aemo-etl/tests/integration/conftest.py`
  - `backend-services/dagster-user/aemo-etl/.localstack.env`
  - `backend-services/dagster-user/aemo-etl/scripts/setup-debugging-environment`
  - `backend-services/dagster-user/aemo-etl/dagster.dev.yaml`
  - `backend-services/dagster-user/aemo-etl/workspace.dev.yaml`
- `sync.scope`: `operations, tooling`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
