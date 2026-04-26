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
    RawSensor->>Bronze: Launch matching bronze_gasbb_* asset with s3_keys
    Bronze->>Landing: Read csv/parquet objects
    Bronze->>Archive: Move processed source files from landing
    Bronze->>Silver: Trigger silver_gasbb_* auto-materialization
    Silver->>GasModel: Trigger shared dimensions and marts when relevant
```

Trigger and output notes:

- The first step is schedule-driven from `src/aemo_etl/defs/raw/nemweb_public_files.py`.
- The unzip and bronze steps are sensor-driven from `src/aemo_etl/defs/sensors.py`.
- Outputs land in Delta tables under the AEMO bucket plus archived source files under `ARCHIVE_BUCKET/bronze/gbb`.

## VICGAS ingestion flow

```mermaid
sequenceDiagram
    autonumber
    participant NEMWeb as NEMWeb VicGas folder
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

    Schedule->>Discover: Run every 15 minutes
    Discover->>NEMWeb: List and fetch links from REPORTS/CURRENT/VicGas
    Discover->>Landing: Write discovered zip/csv/parquet files
    Discover->>Bronze: Record file metadata in `bronze_nemweb_public_files_vicgas`

    Landing->>UnzipSensor: Detect *.zip
    UnzipSensor->>UnzipAsset: Launch with selected zip keys
    UnzipAsset->>Landing: Extract members, convert CSV members to parquet when possible
    UnzipAsset->>Archive: Archive successful zip inputs

    Landing->>RawSensor: Detect files matching bronze asset glob_pattern
    RawSensor->>Bronze: Launch matching bronze_int* asset with s3_keys
    Bronze->>Landing: Read source members
    Bronze->>Archive: Copy then delete processed source files
    Bronze->>Silver: Trigger silver_int* current-snapshot assets
    Silver->>GasModel: Feed shared dimensions and fact marts
```

Trigger and output notes:

- This follows the same factory pattern as GBB, but the downstream assets are the `int*` VICGAS report assets under `src/aemo_etl/defs/raw/vicgas`.
- The bronze assets write partitioned Delta tables by `ingested_date`; the silver assets overwrite the deduplicated current snapshot.

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
    participant DeltaSilver as AEMO Delta silver table
    participant GasModel as Downstream gas_model asset

    Operator->>BronzeAsset: Run with s3_keys
    BronzeAsset->>Landing: Download matching objects
    BronzeAsset->>BronzeAsset: Parse bytes to LazyFrame and apply hooks
    BronzeAsset->>DeltaBronze: Append partitioned rows with ingested_date
    BronzeAsset->>Archive: Copy processed files and delete from landing

    DeltaBronze->>SilverAsset: Dependency update observed
    SilverAsset->>DeltaBronze: Read bronze Delta table
    SilverAsset->>SilverAsset: Sort by source recency and deduplicate on surrogate_key
    SilverAsset->>DeltaSilver: Overwrite current snapshot
    DeltaSilver->>GasModel: Trigger shared dimensions or fact assets when selected as input
```

Trigger and output notes:

- The bronze run can come from an event-driven sensor or from a manual asset launch with explicit `s3_keys`.
- Bronze uses `aemo_deltalake_ingest_partitioned_append_io_manager`; silver uses `aemo_deltalake_overwrite_io_manager`.
- A representative downstream example is `silver_gas_fact_operational_meter_flow`, which reads VICGAS silver inputs plus shared dimensions and writes a `silver/gas_model/...` Delta table.

## LocalStack and S3-compatible behavior

When `AWS_ENDPOINT_URL` points at LocalStack, the same flow runs against local S3-compatible storage rather than AWS. Integration tests also create a `delta_log` DynamoDB table so Delta locking works for local end-to-end materializations.

## Related docs

- [High-level architecture](high_level_architecture.md)
- [Local development guide](../development/local_development.md)
- [Gas-model ERDs](../gas_model/)
