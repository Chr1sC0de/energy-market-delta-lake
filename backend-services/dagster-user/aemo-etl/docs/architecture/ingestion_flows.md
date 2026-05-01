# Ingestion Flows

These diagrams show the main ingestion paths implemented by the current factories and definition modules. They stay close to the repo's real layers: scheduled NEMWeb discovery, landing and archive buckets, unzipper assets, bronze ingestion assets, source silver assets, and downstream `gas_model` automation.

## Table of contents

- [GBB ingestion flow](#gbb-ingestion-flow)
- [VICGAS ingestion flow](#vicgas-ingestion-flow)
- [Raw-to-silver transformation flow](#raw-to-silver-transformation-flow)
- [LocalStack and S3-compatible behavior](#localstack-and-s3-compatible-behavior)
- [Related docs](#related-docs)

## GBB ingestion flow

```mermaid
sequenceDiagram
    autonumber
    participant NEMWeb as NEMWeb GBB folder
    participant Schedule as bronze_nemweb_public_files_gbb_job_schedule
    participant Discover as bronze_nemweb_public_files_gbb
    participant Landing as LANDING_BUCKET/bronze/gbb
    participant UnzipSensor as gbb_unzipper_sensor
    participant UnzipAsset as unzipper_gbb
    participant RawSensor as gbb_event_driven_assets_sensor
    participant Bronze as bronze_gasbb_*
    participant Archive as ARCHIVE_BUCKET/bronze/gbb
    participant Silver as silver_gasbb_*
    participant GasModel as silver/gas_model/*

    Schedule->>Discover: Run every 15 minutes
    Discover->>NEMWeb: List and fetch links from REPORTS/CURRENT/GBB
    Discover->>Landing: Write discovered files and converted parquet outputs
    Discover->>Bronze: Record file metadata in `bronze_nemweb_public_files_gbb`

    Landing->>UnzipSensor: Zip objects become visible
    UnzipSensor->>UnzipAsset: Launch with matching s3_keys
    UnzipAsset->>Landing: Expand members in place under `bronze/gbb`
    UnzipAsset->>Archive: Copy successful zip inputs, then delete from landing

    Landing->>RawSensor: Matching source files become visible
    RawSensor->>Bronze: Launch matching gasbb_*_job with s3_keys
    Bronze->>Landing: Read csv/parquet objects
    Bronze->>Archive: Move processed source files from landing
    Bronze->>Silver: Trigger silver_gasbb_* auto-materialization
    Silver->>GasModel: Trigger shared dimensions and marts when relevant
```

Trigger and output notes:

- The first step is schedule-driven from `src/aemo_etl/defs/raw/nemweb_public_files.py`.
- The unzip and bronze steps are sensor-driven from `src/aemo_etl/definitions.py`; that module also registers the failed-run alert sensor, which is not part of the ingestion data path shown here. Source-table bronze raw sensors select at most 128 MB (128,000,000 bytes) and 25 landing files per run request by default. Those caps are source-table batching defaults, not the full repo **Fast check** or **Push check** configuration.
- Outputs land in Delta tables under the AEMO bucket plus archived source files under `ARCHIVE_BUCKET/bronze/gbb`.

## VICGAS ingestion flow

```mermaid
sequenceDiagram
    autonumber
    participant NEMWeb as NEMWeb VicGas folder
    participant Operator as Manual launch
    participant ManualJob as download_vicgas_public_report_zip_files_job
    participant Schedule as bronze_nemweb_public_files_vicgas_job_schedule
    participant Discover as bronze_nemweb_public_files_vicgas
    participant Landing as LANDING_BUCKET/bronze/vicgas
    participant UnzipSensor as vicgas_unzipper_sensor
    participant UnzipAsset as unzipper_vicgas
    participant RawSensor as vicgas_event_driven_assets_sensor
    participant Bronze as bronze_int*
    participant Archive as ARCHIVE_BUCKET/bronze/vicgas
    participant Silver as silver_int*
    participant GasModel as silver/gas_model/*

    Operator->>ManualJob: Optional bootstrap/backfill launch
    ManualJob->>NEMWeb: List and fetch PublicRptsNN.zip bundles
    ManualJob->>Landing: Write zip objects for unzipper processing

    Schedule->>Discover: Run every 15 minutes
    Discover->>NEMWeb: List and fetch links from REPORTS/CURRENT/VicGas
    Discover->>Landing: Write discovered zip/csv/parquet files
    Discover->>Bronze: Record file metadata in `bronze_nemweb_public_files_vicgas`

    Landing->>UnzipSensor: Detect *.zip
    UnzipSensor->>UnzipAsset: Launch with selected zip keys
    UnzipAsset->>Landing: Extract members, convert CSV members to parquet when possible
    UnzipAsset->>Archive: Archive successful zip inputs

    Landing->>RawSensor: Detect files matching bronze asset glob_pattern
    RawSensor->>Bronze: Launch matching int*_job with s3_keys
    Bronze->>Landing: Read source members
    Bronze->>Archive: Copy then delete processed source files
    Bronze->>Silver: Trigger silver_int* current-snapshot assets
    Silver->>GasModel: Feed shared dimensions and fact marts
```

Trigger and output notes:

- This follows the same factory pattern as GBB, but the downstream assets are the `int*` VICGAS report assets under `src/aemo_etl/defs/raw/vicgas`.
- `download_vicgas_public_report_zip_files_job` is ad hoc only. It is used for bootstrap or backfill of `PublicRptsNN.zip` bundles into `LANDING_BUCKET/bronze/vicgas`; the existing unzipper and raw sensors handle downstream processing.
- The bronze assets merge current-state Delta rows by `surrogate_key` after collapsing each micro-batch to the maximum `source_file` per key; the silver assets overwrite the current parquet snapshot.

## Raw-to-silver transformation flow

```mermaid
sequenceDiagram
    autonumber
    participant Operator as Sensor or manual launch
    participant BronzeAsset as bronze table asset
    participant Landing as Landing bucket object(s)
    participant Archive as Archive bucket object(s)
    participant DeltaBronze as AEMO Delta bronze table
    participant SilverAsset as silver table asset
    participant ParquetSilver as AEMO Parquet silver dataset
    participant GasModel as Downstream gas_model asset
    participant Maintenance as delta_table_vacuum_job

    Operator->>BronzeAsset: Run with s3_keys
    BronzeAsset->>Landing: Download matching objects
    BronzeAsset->>BronzeAsset: Parse bytes to LazyFrame and apply hooks
    BronzeAsset->>BronzeAsset: Add source_content_hash and keep max source_file per surrogate_key
    BronzeAsset->>DeltaBronze: Merge rows by surrogate_key when source_content_hash changed
    BronzeAsset->>Archive: Copy staged source files and delete from landing

    DeltaBronze->>SilverAsset: Dependency update observed
    SilverAsset->>DeltaBronze: Read bronze Delta table
    SilverAsset->>SilverAsset: Select latest source_file and deduplicate on surrogate_key
    SilverAsset->>ParquetSilver: Overwrite current Parquet snapshot dataset
    ParquetSilver->>GasModel: Trigger shared dimensions or fact assets when selected as input
    Maintenance->>DeltaBronze: Daily compact and full vacuum
```

Trigger and output notes:

- The bronze run can come from an event-driven sensor or from a manual asset launch with explicit `s3_keys`.
- Bronze uses `aemo_deltalake_current_state_merge_io_manager`; `df_from_s3_keys` silver uses `aemo_parquet_overwrite_io_manager`.
- `aemo-replay-bronze-archive` rebuilds source-table bronze Delta tables from
  archive storage. It can target all source-table bronze assets, one domain, or
  one table; dry-run is the default and reports matching archive files, planned
  batch count, total bytes, and target table URI. `--replace` is required before
  it overwrites the first non-empty replay batch and then merges later batches
  with the same current-state predicate.
- `delta_table_vacuum_schedule` runs daily at 02:00 Australia/Melbourne and uses each Delta asset's `delta_maintenance/*` metadata, defaulting to compact plus full vacuum retention `0`.
- A representative downstream example is `silver_gas_fact_operational_meter_flow`, which reads VICGAS silver inputs plus shared dimensions and writes a `silver/gas_model/...` parquet snapshot dataset.
- Downstream `gas_model` silver assets retry failed materializations up to three times with a 60-second exponential backoff and plus/minus jitter.

## LocalStack and S3-compatible behavior

When `AWS_ENDPOINT_URL` points at LocalStack, the same flow runs against local S3-compatible storage rather than AWS. Integration tests also create a `delta_log` DynamoDB table so Delta locking works for local end-to-end materializations.

## Related docs

- [High-level architecture](high_level_architecture.md)
- [Local development guide](../development/local_development.md)
- [Gas-model ERDs](../gas_model/)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/nemweb_public_files.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/jobs/download_vicgas_public_report_zip_files.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/alerts.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/assets.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/source_tables.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/s3_pending_objects.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/delta_tables.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/archive_replay.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/replay_bronze_archive.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/resources.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_fact_operational_meter_flow.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/unzipper/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/unzipper/sensors.py`
- `sync.scope`: `behavior`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
