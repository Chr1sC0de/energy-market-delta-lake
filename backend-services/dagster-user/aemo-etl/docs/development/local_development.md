# Local Development

This guide covers the local workflow for running `aemo-etl` against LocalStack-backed storage and for executing the repository's tests and Dagster UI.

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

## Test assumptions

Integration tests in `tests/integration/conftest.py` make these assumptions:

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
make integration-test
make duplicate-check
make run-prek
```

## Related docs

- [High-level architecture](../architecture/high_level_architecture.md)
- [Ingestion sequence diagrams](../architecture/ingestion_flows.md)
