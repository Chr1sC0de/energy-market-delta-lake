# Gas-Model ERDs

Index for the implemented `silver.gas_model` documentation in `aemo-etl`.

## Table of contents

- [ERD pages](#erd-pages)
- [Related docs](#related-docs)

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

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/__init__.py`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
