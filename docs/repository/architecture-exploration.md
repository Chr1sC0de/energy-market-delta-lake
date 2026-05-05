# Architecture Exploration

This temporary repository page captures issue-scoped architecture research.
It is not durable architecture guidance. Issue #87 must consume any accepted
findings into durable repo docs before deleting this file.

## Table of contents

- [#82: Explore deeper gas-model asset shell Module](#82-explore-deeper-gas-model-asset-shell-module)

## #82: Explore deeper gas-model asset shell Module

Issue #82 asks whether the repeated Dagster shell around `gas_model` assets
should become a deeper Module. This section records the exploration only. It
does not change runtime behavior.

### Evidence

The `aemo-etl` Subproject currently has 28 `silver_*.py` gas-model asset files
under `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model`.
Each file defines a single Dagster asset with the same shell shape: `KEY_PREFIX`
is `["silver", "gas_model"]`, `GROUP_NAME` is `gas_model`, the IO manager is
`aemo_parquet_overwrite_io_manager`, metadata includes `dagster/table_name`,
`dagster/uri`, `dagster/column_schema`, `grain`, and
`surrogate_key_sources`, and the asset uses `RetryPolicy(max_retries=3,
delay=60, backoff=Backoff.EXPONENTIAL, jitter=Jitter.PLUS_MINUS)`.

Most files also share `SOURCE_TABLES` metadata, `MaterializeResult` wrapping,
`dagster/column_lineage`, `AutomationCondition.any_deps_updated() &
~AutomationCondition.in_progress() &
~AutomationCondition.any_deps_missing()`, three factory-built checks
(`check_for_duplicate_rows`, `check_schema_matches`, `check_schema_drift`), one
custom `check_required_fields`, and a `Definitions` object containing one
asset, four checks, and one asset-targeted `AutomationConditionSensorDefinition`.
Observed examples include `silver_gas_dim_location.py` and
`silver_gas_fact_scada_pressure.py`.

`silver_gas_dim_date.py` is the main exception that proves the Module should
not over-generalize. It still shares the asset metadata, retry policy,
schema checks, duplicate-row check, and required-field check, but it has no
source tables, uses `AutomationCondition.missing()`, and returns a
`ScheduleDefinition` built from `define_asset_job` instead of an
asset-targeted automation sensor.

The tests repeat the same shell assumptions. The gas-model component tests
call each decorated asset's compute function directly for transform behavior,
call the required-field check directly for null validation, and call each
module's `defs()` to assert the resulting `Definitions` contain one asset and
four checks. `test_defs_sensors.py` scans all `silver_*.py` gas-model modules
and asserts that every module except `silver_gas_dim_date` defines exactly one
asset-targeted automation sensor named `{module_name}_sensor`; the date
dimension must instead expose `silver_gas_dim_date_schedule`. Grouped fact
tests such as `test_defs_gas_model_silver_gas_future_facts.py` and
`test_defs_gas_model_silver_gas_operations_facts.py` also assert that
`source_tables` metadata stays aligned with the per-module `SOURCE_TABLES`
constant.

### Proposed Module Interface

Use a Python Module, not a Dagster YAML Component, as the first step. The
smallest useful Interface is a code-level factory that accepts per-asset
Implementation details and returns Dagster definitions:

```python
GasModelAssetSpec(
    table_name: str,
    description: str,
    schema: Mapping[str, PolarsDataType],
    descriptions: Mapping[str, str],
    grain: str,
    required_columns: Sequence[str],
    surrogate_key_sources: Sequence[str],
    transform: Callable[..., LazyFrame],
    ins: Mapping[str, AssetIn] = {},
    source_tables: Sequence[str] = (),
    column_lineage: TableColumnLineage | None = None,
    automation_condition: AutomationCondition | None = DEFAULT_DEP_UPDATE_CONDITION,
    primary_key: str | Sequence[str] = "surrogate_key",
)

build_gas_model_asset_definitions(spec: GasModelAssetSpec) -> Definitions
```

The Module should own only the repeated shell:

- asset decorator defaults: key prefix, group name, IO-manager key, kinds,
  table name, URI, column schema metadata, source-table metadata when present,
  and the standard retry policy
- `MaterializeResult` wrapping, including optional column lineage metadata
- the required-field asset check implementation
- duplicate-row, schema-match, and schema-drift check factory wiring
- the default `AutomationConditionSensorDefinition` for dependency-updated
  assets
- the `Definitions` assembly for one asset plus checks and the default sensor

The per-asset Implementation should remain in each asset file:

- Polars transform logic and helper functions
- schema, column descriptions, required columns, grain, source tables, and
  surrogate-key sources
- raw and dimension input keys through explicit `AssetIn` mappings
- column lineage through explicit `TableColumnLineage`
- asset docstring and domain-specific description text

### Explicit Adapters And Dagster Constructs

Keep these constructs explicit at the call site or in a visible adapter object:

- `AssetIn` mappings and `AssetKey` constants, because they define Dagster
  asset graph lineage and the transform function signature.
- `TableColumnLineage`, because each asset maps different source columns and
  some assets have partial lineage rather than a full column-by-column map.
- Automation shape. The default dependency-updated sensor can be built by the
  Module, but scheduled assets such as `silver_gas_dim_date` should keep
  `define_asset_job` and `ScheduleDefinition` explicit until a second asset
  proves that scheduling belongs in the shared Interface.
- IO-manager selection. The current default can be `aemo_parquet_overwrite_io_manager`,
  but the Interface should keep an override field so future Delta, append, or
  metadata-only assets do not need a second shell.
- Check semantics. The existing check factories are already shared Adapters;
  the gas-model Module should compose them, not absorb their internals.
- Polars transform call adapters. The factory can normalize Dagster wrapping,
  but it should not hide asset-specific input names, joins, pivots, parsing,
  deduplication, or surrogate-key logic.

### Recommendation

Create the smallest implementation slice around one ordinary dependency-updated
asset, preferably `silver_gas_fact_scada_pressure` or
`silver_gas_dim_location`. That slice should add a private gas-model shell
Module and migrate one asset to prove the factory preserves asset key, group,
metadata, retry policy, checks, sensor name, column lineage metadata, and
transform output. Leave `silver_gas_dim_date` explicit in the first slice.

The relevant AEMO ETL **Test lane** for that slice is the **Component test**
lane because the change composes Dagster `Definitions`, checks, sensors, and
asset metadata in process. A narrowed debug run can target the migrated asset
test plus `test_defs_sensors.py`, but validation should finish with
`make component-test` from `backend-services/dagster-user/aemo-etl`. If the
slice extracts pure required-field or metadata helpers, add focused
**Unit tests**, then run the Subproject **Commit check** with `make run-prek`.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `CONTEXT.md`
  - `docs/repository/documentation-sync.md`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_dim_location.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_fact_scada_pressure.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_dim_date.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/checks.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_sensors.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_gas_model_silver_gas_dim_location.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_gas_model_silver_gas_future_facts.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_gas_model_silver_gas_operations_facts.py`
- `sync.scope`: `temporary architecture exploration`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `prek run -a`
  - `verify #87 consumption and deletion note remains visible`
