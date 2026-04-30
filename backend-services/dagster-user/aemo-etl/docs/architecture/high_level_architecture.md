# High-Level Architecture

This project packages Dagster definitions for ingesting public AEMO gas files into bronze Delta tables and then transforming those source-specific datasets into parquet-backed source silver and shared `gas_model` layers.

## Table of contents

- [Runtime overview](#runtime-overview)
- [How definitions are loaded](#how-definitions-are-loaded)
- [Component roles](#component-roles)
- [Sensors and automation](#sensors-and-automation)
- [Storage model](#storage-model)
- [S3-backed IO managers](#s3-backed-io-managers)
- [Module map](#module-map)
- [Related docs](#related-docs)

## Runtime overview

```mermaid
flowchart LR
    subgraph Source
        NEMWeb["AEMO / NEMWeb public reports"]
    end

    subgraph Orchestration
        Sched["bronze_nemweb_public_files_* schedules"]
        Discover["Discovery graph assets"]
        UnzipSensors["*_unzipper_sensor"]
        RawSensors["*_event_driven_assets_sensor"]
        Bronze["Bronze assets"]
        Silver["Source silver assets"]
        GasModel["gas_model assets"]
        Maintenance["Delta maintenance job"]
    end

    subgraph Storage
        Landing["Landing bucket"]
        Archive["Archive bucket"]
        Delta["AEMO Delta bucket"]
        DagsterStore["IO manager bucket"]
        Dynamo["DynamoDB Delta lock table in local tests"]
    end

    NEMWeb --> Discover
    Sched --> Discover
    Discover --> Landing
    Landing --> UnzipSensors
    UnzipSensors --> Landing
    UnzipSensors --> Archive
    Landing --> RawSensors
    RawSensors --> Bronze
    Bronze --> Archive
    Bronze --> Delta
    Silver --> Delta
    GasModel --> Delta
    Maintenance --> Delta
    Bronze -. intermediates .-> DagsterStore
    Silver -. intermediates .-> DagsterStore
    GasModel -. intermediates .-> DagsterStore
    Delta -. local locking .-> Dynamo
    Maintenance -. local locking .-> Dynamo
```

## How definitions are loaded

`src/aemo_etl/definitions.py` is the project entrypoint for Dagster. It does three things:

1. Calls `load_from_defs_folder(path_within_project=Path(__file__).parent)` once to discover all definitions under `src/aemo_etl/defs`, including shared resources from `src/aemo_etl/defs/resources.py`.
2. Builds the scheduled Delta maintenance definitions from discovered Delta-backed asset metadata.
3. Wires the event-driven ingestion sensors, unzipper sensors, and failed-run alert sensor.

That means the actual asset topology is assembled from small modules in:

- `src/aemo_etl/defs/raw`
- `src/aemo_etl/defs/resources.py`
- `src/aemo_etl/defs/gas_model`

## Component roles

### Discovery assets

`src/aemo_etl/defs/raw/nemweb_public_files.py` registers the scheduled discovery assets:

- `bronze_nemweb_public_files_vicgas`
- `bronze_nemweb_public_files_gbb`

These are created by `factories/nemweb_public_files/definitions.py`. Each one:

- polls a NEMWeb folder every 15 minutes
- filters links
- downloads or converts discovered source files into landing storage
- records a Delta table of discovered file metadata in the AEMO bucket

### Unzipper assets

`src/aemo_etl/defs/raw/unzipper.py` registers one unzipper asset per domain:

- `unzipper_vicgas`
- `unzipper_gbb`

Those assets are sensor-driven, look for `*.zip` objects in landing storage, expand members in place, convert CSV members to Parquet when possible, and archive the original zip only after all members succeed.

### Bronze and source silver assets

The source-table modules under `src/aemo_etl/defs/raw/gbb` and `src/aemo_etl/defs/raw/vicgas` are generated from `factories/df_from_s3_keys/definitions.py`.

For each source table the factory creates:

- one bronze asset under `bronze/<domain>/...`
- one source-specific silver asset under `silver/<domain>/...`
- schema and duplicate-row checks

The bronze asset:

- receives S3 object keys from a sensor run config
- reads bytes from landing storage
- applies optional preprocessing hooks
- writes a partitioned Delta append table into the AEMO bucket
- archives processed source files by moving them from landing to archive

The corresponding silver asset:

- reads the bronze Delta table
- selects the latest `source_file` per `surrogate_key` and deduplicates the current snapshot
- overwrites the current parquet snapshot in the AEMO bucket
- auto-materializes when its bronze dependency changes

### Gas-model assets

`src/aemo_etl/defs/gas_model` contains curated dimensions and fact tables such as:

- `silver_gas_dim_date`
- `silver_gas_dim_operational_point`
- `silver_gas_fact_operational_meter_flow`

Most of these assets consume the source silver layer and publish shared dimensions and marts back into `silver/gas_model/...` parquet snapshot datasets. `silver_gas_dim_date` is a standalone scheduled calendar generated from `1900-01-01` through the run date.
Gas-model silver assets retry failed materializations up to three times with a 60-second exponential backoff and plus/minus jitter.

### Delta maintenance

`src/aemo_etl/maintenance/delta_tables.py` defines `delta_table_vacuum_job` and `delta_table_vacuum_schedule`. The root definitions inspect loaded assets, select those using Delta IO managers with `dagster/uri` metadata, resolve optional `delta_maintenance/*` metadata, and pass those table paths and settings to one scheduled job.

The schedule runs daily at 02:00 Australia/Melbourne. Each run can compact and vacuum each discovered Delta table. Missing metadata defaults to compact enabled, vacuum enabled, retention `0`, retention enforcement disabled, and `dry_run=False`; this immediately deletes unreferenced Delta files but does not remove files referenced by the current table version.

Per-asset overrides use flat metadata keys: `delta_maintenance/enabled`, `delta_maintenance/compact`, `delta_maintenance/vacuum`, `delta_maintenance/retention_hours`, `delta_maintenance/enforce_retention_duration`, and `delta_maintenance/dry_run`.

## Sensors and automation

`src/aemo_etl/definitions.py` wires three orchestration patterns:

- `vicgas_unzipper_sensor` and `gbb_unzipper_sensor`
  - watch landing storage for `*.zip`
  - launch unzipper assets with matching S3 keys
- `vicgas_event_driven_assets_sensor` and `gbb_event_driven_assets_sensor`
  - watch landing storage for file patterns declared on bronze assets
  - launch matching raw ingestion jobs with S3 keys
- `aemo_etl_failed_run_alert_sensor`
  - watches failed runs in the AEMO ETL code location
  - publishes one alert to an AWS SNS topic when
    `DAGSTER_FAILURE_ALERT_TOPIC_ARN` is configured
- `ops/testing/failed_run_alert_probe`
  - manual asset that always raises an intentional error
  - creates a real failed run for live alert sensor and SNS validation
- `default_automation_condition_sensor`
  - covers everything else
  - lets the non-event-driven silver and dependency-driven `gas_model` assets materialize when dependencies update

`silver_gas_dim_date` is refreshed by its own daily schedule at 06:03 Australia/Melbourne time.

Locally these sensors and schedules default to stopped. On AWS they default to running.
The Delta maintenance schedule follows the same local-stopped and AWS-running default schedule status.

## Storage model

Bucket naming comes from `src/aemo_etl/configs.py`:

- `LANDING_BUCKET`: incoming files ready for unzip or bronze ingestion
- `ARCHIVE_BUCKET`: successfully processed raw source files and zips
- `AEMO_BUCKET`: Delta table storage for bronze assets and parquet snapshot storage for source silver and `gas_model` assets
- `IO_MANAGER_BUCKET`: Dagster IO manager payloads and intermediates

All bucket names are derived from:

- `DEVELOPMENT_ENVIRONMENT`
- `NAME_PREFIX`

Example defaults:

- `dev-energy-market-landing`
- `dev-energy-market-archive`
- `dev-energy-market-aemo`
- `dev-energy-market-io-manager`

## S3-backed IO managers

`src/aemo_etl/defs/resources.py` defines three Delta-oriented IO managers plus one Parquet overwrite IO manager:

- `aemo_deltalake_append_io_manager`
  - append mode with schema merge
- `aemo_deltalake_overwrite_io_manager`
  - overwrite mode with schema merge
- `aemo_deltalake_ingest_partitioned_append_io_manager`
  - append mode partitioned by `ingested_date`
- `aemo_parquet_overwrite_io_manager`
  - overwrites a Parquet dataset directory with the current snapshot

The Delta managers persist `polars.LazyFrame` outputs to Delta tables in the AEMO bucket using the `dagster/uri` asset metadata. The Parquet manager overwrites a Parquet dataset directory at the same metadata URI contract. All managers publish preview, row count, and schema metadata back into Dagster.

## Module map

```mermaid
flowchart TD
    Definitions["src/aemo_etl/definitions.py"] --> Defs["src/aemo_etl/defs"]
    Definitions --> Config["src/aemo_etl/configs.py"]
    Definitions --> Maintenance["src/aemo_etl/maintenance"]

    Defs --> Raw["raw/"]
    Defs --> Sensors["sensors.py"]
    Defs --> Resources["resources.py"]
    Defs --> GasModel["gas_model/"]

    Raw --> NemwebDefs["nemweb_public_files.py"]
    Raw --> UnzipDefs["unzipper.py"]
    Raw --> GBB["gbb/*.py"]
    Raw --> VICGAS["vicgas/*.py"]

    GBB --> DFFactory["factories/df_from_s3_keys"]
    VICGAS --> DFFactory
    NemwebDefs --> NemwebFactory["factories/nemweb_public_files"]
    UnzipDefs --> UnzipFactory["factories/unzipper"]
```

## Related docs

- [Ingestion sequence diagrams](ingestion_flows.md)
- [Local development guide](../development/local_development.md)
- [Gas-model ERDs](../gas_model/)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/alerts.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/delta_tables.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/testing.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/nemweb_public_files.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/resources.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/assets.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/s3_pending_objects.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/unzipper/sensors.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/table_metadata.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_dim_date.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_fact_operational_meter_flow.py`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
