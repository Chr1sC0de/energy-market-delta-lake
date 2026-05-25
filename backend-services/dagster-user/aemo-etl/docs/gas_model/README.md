# Gas-Model ERDs

Index for the implemented `silver.gas_model` documentation in `aemo-etl`.

## Table of contents

- [STTM modeling policy](#sttm-modeling-policy)
- [Lineage and selection contract](#lineage-and-selection-contract)
- [ERD pages](#erd-pages)
- [Related docs](#related-docs)

## STTM modeling policy

The ERD pages describe the implemented `silver.gas_model` assets. Manifest-backed
STTM coverage follows the fit-plus-extend policy in ADR
[0006](../../../../../docs/adr/0006-sttm-gas-model-uses-fit-plus-extend-modeling.md):
existing `gas_model` facts and dimensions receive STTM rows where report grains
match, and new `gas_model` facts are added where a report has a real grain that
does not fit current assets.

`INT685` and `INT685B` remain **Source-spec gaps** until AEMO document discovery
provides usable source definitions.

## Lineage and selection contract

Curated `silver/gas_model/*` assets are visually grouped by mart:
`gas_model_dimensions`, `gas_model_operations`, `gas_model_market`,
`gas_model_capacity_settlement`, or `gas_model_quality_status`. Durable
automation does not target those visual groups directly. Local **End-to-end
test** seed generation and Promotion evidence use
`tag:aemo_etl_layer=gas_model`, and each curated asset also carries
`aemo_etl_mart` for mart-level inspection.

`silver/metadata/silver_table_metadata` is metadata, not a curated gas-model
mart asset, so it stays outside the `tag:aemo_etl_layer=gas_model` target.

## ERD pages

- [Shared dimensions ERD](gas_dim_erd.md)
- [Operations mart ERD](gas_operations_mart_erd.md)
- [Market mart ERD](gas_market_mart_erd.md)
- [Capacity and settlement mart ERD](gas_capacity_settlement_mart_erd.md)
- [Quality and status mart ERD](gas_quality_status_mart_erd.md)

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
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
