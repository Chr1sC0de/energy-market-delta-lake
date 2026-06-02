# Gas-Model Maintainer Contract

This is the maintainer entry point for implemented `silver.gas_model` assets in
`aemo-etl`. Read this contract before using the ERD pages. The ERDs remain the
schema and relationship reference, but this page explains the asset shape,
shared helpers, lineage contract, and modeling policy that maintainers preserve
when adding or modifying curated gas-model assets.

## Table of contents

- [Maintainer contract](#maintainer-contract)
- [Adding or modifying assets](#adding-or-modifying-assets)
- [Shared helper roles](#shared-helper-roles)
- [Lineage, groups, and tags](#lineage-groups-and-tags)
- [STTM modeling policy](#sttm-modeling-policy)
- [How to use the ERD pages](#how-to-use-the-erd-pages)
- [Related docs](#related-docs)

## Maintainer contract

Curated gas-model assets are shared gas-market marts under
`src/aemo_etl/defs/gas_model`. Source-backed assets consume source silver assets
and publish current parquet snapshots under `silver/gas_model/<asset_name>`.
The generated `silver_gas_dim_date` calendar is the exception: it has no source
table input and is refreshed by schedule. The layer is not a source-specific
holding area and should not duplicate GBB, STTM, or VICGAS source silver shape
just because the source table is convenient.

Every curated gas-model asset keeps these invariants unless the implementation
and docs are deliberately updated together:

- Asset keys use `["silver", "gas_model", <asset_name>]`, and table metadata
  uses `silver.gas_model.<asset_name>`.
- Assets write through `aemo_parquet_overwrite_io_manager` with
  `kinds={"table", "parquet"}` and a `dagster/uri` under
  `s3://<AEMO_BUCKET>/silver/gas_model/<asset_name>`.
- Asset metadata declares `dagster/column_schema`, `grain`, and
  `surrogate_key_sources`; source-backed assets also declare `source_tables`.
- `surrogate_key` is the primary key and is generated from the declared
  `surrogate_key_sources`.
- Source-backed rows carry lineage fields appropriate to the asset shape, such
  as `source_system`, `source_tables`, row-level `source_table` where one output
  row preserves one contributing source table, `source_report_id` for STTM
  report-specific rows, `source_surrogate_key`, `source_file`, and
  `ingested_timestamp`. Conformed dimensions may also keep list-valued lineage
  such as `source_surrogate_keys` or `source_files`.
- Asset checks cover duplicate `surrogate_key` values, schema matches, schema
  drift, and asset-specific required fields.
- Source-backed dependency-updated assets use
  `AutomationCondition.any_deps_updated()` guarded by not-in-progress and
  no-missing-dependency checks, plus one asset-targeted
  `AutomationConditionSensorDefinition`. `silver_gas_dim_date` uses missing-only
  automation and a daily schedule.

Column lineage is part of the maintained interface where modules declare
`TableColumnLineage`. Preserve it when changing source columns, adding source
tables, or splitting rows into multiple accepted measures.

## Adding or modifying assets

Before changing an asset, decide whether the source coverage fits an existing
shared dimension or fact grain. If the grain and meaning match, extend that
asset with new source rows and source lineage. If the source has a real grain
that does not fit, add a new shared `silver.gas_model` fact with an explicit
grain.

Use this implementation order:

1. Choose the destination asset using the fit-plus-extend policy in ADR
   [0006](../../../../../docs/adr/0006-sttm-gas-model-uses-fit-plus-extend-modeling.md).
2. Keep the module under `src/aemo_etl/defs/gas_model` with the
   `silver_gas_*` naming pattern.
3. Add or update the asset's mart assignment in `GAS_MODEL_MART_BY_ASSET` before
   relying on `gas_model_group_name()` or `gas_model_asset_tags()`.
4. Use the shared asset shell when `GasModelAssetSpec` can describe the asset.
   For custom transforms, keep the same metadata, check, retry, automation, and
   sensor conventions manually.
5. Reuse shared parsers and STTM helpers instead of adding one-off parsing,
   source-lineage, or dimension-join logic in a fact module.
6. Update the relevant ERD page when the grain, schema, source-table inventory,
   relationship notes, or nullable foreign-key behavior changes.

For documentation-only work, keep asset definitions, schemas, ERD diagrams, and
materialization behavior unchanged.

## Shared helper roles

`_asset_shell.py` owns the ordinary dependency-updated asset shell:
`GasModelAssetSpec` describes the asset, and `build_gas_model_asset_definitions`
builds the Dagster asset, standard checks, retry policy, automation condition,
metadata, group name, tags, and asset-targeted sensor.

`_parsing.py` owns source-format parsing that is shared across gas-model
modules. Use `parse_gas_datetime()` for gas source date and timestamp strings
that arrive in mixed numeric or month-name formats. Use `parse_yes_no_bool()`
for source boolean flags such as yes/no, true/false, and one/zero values.

`_sttm_common.py` owns STTM-specific conventions. It provides STTM source table
and asset-key helpers, common STTM source lineage through `source_metadata()`,
and conformed joins for STTM hub zones, facilities, and participants through
`with_zone_key()`, `with_facility_zone_keys()`, and `with_participant_key()`.
Use these helpers for STTM facts that need accepted source lineage or shared
dimension keys.

`asset_organization.py` owns durable grouping and tag organization. The
gas-model functions are the source of truth for mart assignment, Dagster visual
groups, and automation selectors.

## Lineage, groups, and tags

Curated `silver/gas_model/*` assets are visually grouped by mart:
`gas_model_dimensions`, `gas_model_operations`, `gas_model_market`,
`gas_model_capacity_settlement`, or `gas_model_quality_status`.

Durable automation does not target those visual groups directly. Local
**End-to-end test** seed generation, gas-model target checks, and Promotion
evidence use `tag:aemo_etl_layer=gas_model`, exposed as
`GAS_MODEL_TARGET_SELECTOR`. Each curated asset also carries these structured
tags:

| Tag | Value |
| --- | --- |
| `aemo_etl_layer` | `gas_model` |
| `aemo_etl_domain` | `gas` |
| `aemo_etl_role` | `curated_gas_model` |
| `aemo_etl_mart` | the asset's mart from `GAS_MODEL_MART_BY_ASSET` |

`silver/metadata/silver_table_metadata` is metadata, not a curated gas-model
mart asset, so it stays outside the `tag:aemo_etl_layer=gas_model` target.

## STTM modeling policy

Manifest-backed STTM coverage follows the fit-plus-extend policy in ADR
[0006](../../../../../docs/adr/0006-sttm-gas-model-uses-fit-plus-extend-modeling.md):
existing `gas_model` facts and dimensions receive STTM rows where report grains
match, and new `gas_model` facts are added where a report has a real grain that
does not fit current assets.

That policy keeps `silver.gas_model` as the shared gas-market mart rather than a
set of source-specific silos. STTM-specific fact names are acceptable when the
grain is STTM-specific, but those facts still use the same lineage, tag, group,
and asset-check conventions as the rest of the layer.

`INT685` and `INT685B` remain **Source-spec gaps** until AEMO document discovery
provides usable source definitions for their fields, grain, and meaning.

## How to use the ERD pages

Use this README to understand the maintainer contract first. Then use the ERD
pages as topical reference material for the current implemented schema. ERD page
names are not the authoritative mart assignment; use `GAS_MODEL_MART_BY_ASSET`
for `aemo_etl_mart` and group membership.

- [Shared dimensions ERD](gas_dim_erd.md): shared dimensions, bridge assets,
  conformed identifiers, and dimension relationship notes.
- [Operations mart ERD](gas_operations_mart_erd.md): flow, storage, forecast,
  linepack, and operational-meter facts.
- [Market mart ERD](gas_market_mart_erd.md): market price, schedule, scheduled
  quantity, bid-stack, and STTM contingency facts.
- [Capacity and settlement mart ERD](gas_capacity_settlement_mart_erd.md):
  capacity, auction, transfer, settlement, allocation, MOS, and STTM parameter
  facts.
- [Quality and status mart ERD](gas_quality_status_mart_erd.md): heating value,
  gas quality, pressure, linepack-status, and notice facts.

Each ERD page lists the implemented asset grain, relationship columns,
source-table inventory, and notes about nullable or unresolved conformed keys.
The ERDs are not the only entry point and should not be used by themselves to
infer modeling policy, automation selectors, or helper ownership.

## Related docs

- [aemo-etl project README](../../README.md)
- [High-level architecture](../architecture/high_level_architecture.md)
- [Ingestion sequence diagrams](../architecture/ingestion_flows.md)
- [Local development guide](../development/local_development.md)
- [ADR 0006: STTM gas_model fit-plus-extend modeling](../../../../../docs/adr/0006-sttm-gas-model-uses-fit-plus-extend-modeling.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `CONTEXT.md`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/asset_organization.py`
  - `docs/adr/0006-sttm-gas-model-uses-fit-plus-extend-modeling.md`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/source_tables.json`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/__init__.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/_asset_shell.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/_parsing.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/_sttm_common.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_dim_date.py`
  - `backend-services/dagster-user/aemo-etl/docs/gas_model/gas_dim_erd.md`
  - `backend-services/dagster-user/aemo-etl/docs/gas_model/gas_operations_mart_erd.md`
  - `backend-services/dagster-user/aemo-etl/docs/gas_model/gas_market_mart_erd.md`
  - `backend-services/dagster-user/aemo-etl/docs/gas_model/gas_capacity_settlement_mart_erd.md`
  - `backend-services/dagster-user/aemo-etl/docs/gas_model/gas_quality_status_mart_erd.md`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `prek run -a`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
