# Gas-Model ERDs

Index for the implemented `silver.gas_model` documentation in `aemo-etl`.

## Table of contents

- [STTM modeling policy](#sttm-modeling-policy)
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
  - `docs/repository/architecture-exploration.md`
  - `docs/adr/0006-sttm-gas-model-uses-fit-plus-extend-modeling.md`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/source_tables.json`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/__init__.py`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
