# Architecture Exploration

This temporary repository page captures issue-scoped architecture research.
It is not durable architecture guidance. Issue #87 must consume any accepted
findings into durable repo docs before deleting this file.

## Table of contents

- [#82: Explore deeper gas-model asset shell Module](#82-explore-deeper-gas-model-asset-shell-module)
- [Issue #83: Explore deeper NEMWeb discovery Module](#issue-83-explore-deeper-nemweb-discovery-module)

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

## Issue #83: Explore deeper NEMWeb discovery Module

Issue #83 asks which current NEMWeb public-file discovery seams should remain
external Adapters and which should become internal Implementation detail. This
section records docs-only research. It does not change runtime behavior.
Issue `#87` must consume any accepted findings into durable repo docs before
deleting this temporary file.

### Current Flow

The runtime entrypoint is
`backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/nemweb_public_files.py`.
That definition module merges two scheduled discovery/listing assets:
`bronze_nemweb_public_files_vicgas` for `REPORTS/CURRENT/VicGas` and
`bronze_nemweb_public_files_gbb` for `REPORTS/CURRENT/GBB`. Both pass
`cron_schedule="*/30 * * * *"`, `n_executors=10`, `group_name="integration"`,
the configured default schedule status, and ECS CPU and memory tags into
`nemweb_public_files_definitions_factory`.

The definition module owns the domain-specific filters. `vicgas_file_filter`
excludes `CurrentDay.zip` and `PublicRptsNN.zip` bundles so the ad hoc
`download_vicgas_public_report_zip_files_job` remains the bootstrap/backfill
path for public report bundles. `gbb_folder_filter` excludes
`[To Parent Directory]` and `DUPLICATE`, while otherwise using the default file
filter.

`nemweb_public_files_definitions_factory` builds the Dagster shell and concrete
runtime Adapters. It creates the bronze key prefix, AEMO Delta table path,
asset metadata, retrying HTTP getter, graph asset, duplicate-row check,
asset job, and schedule. It also wires the concrete discovery pieces:

- `HTTPNEMWebLinkFetcher` for recursive NEMWeb folder discovery.
- `FilteredDynamicNEMWebLinksFetcher` with `InMemoryCachedLinkFilter` for
  skipping links already present in the discovery/listing Delta table.
- `S3NemwebLinkProcessor` with `ParquetProcessor` for download, best-effort
  CSV-to-Parquet conversion, and landing upload.
- `S3ProcessedLinkCombiner` for producing the typed metadata `LazyFrame`.

`nemweb_public_files_asset_factory` turns those pieces into one Dagster
`graph_asset`. The graph runs in this order:

1. `build_nemweb_link_fetcher_op` calls `fetcher.fetch(context, href)`.
   `HTTPNEMWebLinkFetcher` walks folder pages breadth-first from
   `https://www.nemweb.com.au/{relative_href}`, parses `<a>` tags with
   BeautifulSoup, applies the folder and file filters, derives upload datetime
   from the preceding NEMWeb text, and returns `Link` records.
2. `build_dynamic_nemweb_links_fetcher_op` filters and batches discovered
   links. `InMemoryCachedLinkFilter` scans the existing output Delta table and
   rejects links with the same `source_absolute_href` and
   `source_upload_datetime`; missing tables accept every link. The dynamic
   fetcher then emits Dagster `DynamicOutput` batches for parallel mapping.
3. `build_nemweb_link_processor_op` maps each batch. `ParquetProcessor`
   downloads each source URL, lowercases the source filename, adds a timestamp
   suffix, converts CSV responses to Parquet when parsing succeeds, and falls
   back to the original bytes and extension when conversion fails.
   `S3NemwebLinkProcessor` uploads the resulting buffer to
   `LANDING_BUCKET/{bronze/<domain>}` and returns `ProcessedLink` records with
   source, target S3, and ingestion timestamps.
4. `build_process_link_combiner_op` collects mapped batch outputs.
   `S3ProcessedLinkCombiner` drops `None` batches, flattens processed records,
   casts timestamps to UTC, and creates the `surrogate_key` from
   `source_absolute_href`, `source_upload_datetime`, `target_s3_name`, and
   `target_ingested_datetime`.
5. The graph asset returns that `LazyFrame` through
   `aemo_deltalake_append_io_manager`, appending the discovery/listing table
   under the AEMO bucket. The factory adds one duplicate-row asset check over
   `surrogate_key`.

The resulting discovery/listing assets are distinct from downstream ingestion.
They record observed NEMWeb files and write landing objects. The unzipper
assets expand zip payloads from landing storage, and source-table bronze assets
consume selected landing objects into bounded current-state Delta tables.
ADR 0003 deliberately scopes current-state semantics to source-table bronze
assets, not to `bronze_nemweb_public_files_*` discovery/listing assets.

### Seam Assessment

The current package has useful external variation, but exposes more seams than
the callers need.

Keep these as explicit external Adapters or caller-visible configuration:

- Domain identity: `domain`, `table_name`, `nemweb_relative_href`, and the
  derived bronze key prefix and table path.
- Domain filters: `folder_filter` and `file_filter` are real variation between
  GBB and VICGAS, and tests are clearer when those rules stay visible.
- Schedule and operator knobs: cron schedule, default schedule status,
  `group_name`, run tags, `n_executors`, and retry timing belong at the Module
  Interface because operators and Dagster deployment policy can vary them.
- Dagster storage seams: the S3 resource, landing bucket, AEMO bucket URI, and
  Delta IO manager are real external integration points. The Interface can keep
  defaults, but should not hide the fact that discovery writes landing objects
  and appends a discovery/listing Delta table.

Move these toward internal Implementation detail:

- The four public op-builder seams:
  `build_nemweb_link_fetcher_op`,
  `build_dynamic_nemweb_links_fetcher_op`,
  `build_nemweb_link_processor_op`, and
  `build_process_link_combiner_op`. They mostly wrap one injected object's
  method and force tests to inspect decorated closures instead of testing the
  full discovery Module Interface.
- Link DTOs: `Link` and `ProcessedLink` are useful data contracts because they
  name the facts crossing discovery, processing, and combining. They should stay
  inside the Module rather than appear in caller-owned configuration.
- One-Adapter ABCs:
  `NEMWebLinkFetcher`, `DynamicNEMWebLinksFetcher`, `NEMWebLinkProcessor`,
  `BufferProcessor`, and `ProcessedLinkedCombiner`. Each currently has one
  production Adapter in this package. The deletion test suggests that deleting
  the public seam would not scatter domain complexity across callers; the
  existing behavior would stay concentrated inside the NEMWeb discovery Module.
- `InMemoryCachedLinkFilter` as public configuration. Skipping already-seen
  links is core discovery behavior because the output table is the discovery
  memory. The cache TTL may stay configurable, but callers should not need to
  assemble the filter Adapter.
- `ParquetProcessor` as public configuration. Best-effort CSV conversion,
  original-byte fallback, target filename stamping, and download retries are
  part of the landing policy for this Module, not caller-specific orchestration.
- `S3ProcessedLinkCombiner` as a public Adapter. Combining processed records
  into the fixed output schema and surrogate key is the discovery table write
  contract, so tests should exercise it through the Module Interface.

The shallowest seams reduce Locality in tests. `test_factories_nemweb.py`
currently tests many pass-through op builders with mocks, then reaches into
Dagster closure cells to confirm factory wiring. Those tests prove the seams are
wired, but they do not make the fetch-filter-process-combine behavior easier to
understand as one Module.

### Proposed Module Interface

Keep the existing top-level factory callable as the public compatibility layer,
but make it delegate to one spec-shaped Module Interface:

```python
NEMWebPublicFilesSpec(
    domain: str,
    table_name: str,
    nemweb_relative_href: str,
    cron_schedule: str,
    folder_filter: TagFilter = default_folder_filter,
    file_filter: TagFilter = default_file_filter,
    n_executors: int = 1,
    cache_ttl_seconds: int = 900,
    process_retry: int = 3,
    initial: int = 10,
    exp_base: int = 3,
    max_retry_time: int = 100,
    group_name: str = "gas_raw",
    tags: Mapping[str, str] | None = None,
    default_status: DefaultScheduleStatus = DefaultScheduleStatus.STOPPED,
    landing_bucket: str = LANDING_BUCKET,
    aemo_bucket: str = AEMO_BUCKET,
    io_manager_key: str = "aemo_deltalake_append_io_manager",
)

build_nemweb_public_files_definitions(spec: NEMWebPublicFilesSpec) -> Definitions
```

That Interface keeps real variation explicit: domain, path, filters,
schedule/status, concurrency, retry policy, resource tags, bucket defaults, and
IO-manager choice. It hides incidental orchestration: op-builder objects,
concrete fetcher/processor/combiner classes, the cached link filter assembly,
fixed output schema, surrogate-key sources, duplicate-row check wiring, asset
job naming, and schedule assembly.

Internally, the Module can still use private seams for focused tests. For
example, pure HTML link extraction, cached-link filtering, filename generation,
CSV conversion fallback, S3 upload record creation, and processed-link
combining can remain small Implementation helpers. They do not need to be
caller-owned Adapters unless a second production Adapter appears.

### Recommendation

The smallest implementation slice is to introduce the spec and
`build_nemweb_public_files_definitions`, then keep
`nemweb_public_files_definitions_factory` as a thin compatibility wrapper. Move
the one-Adapter strategy classes and op builders behind the new Module
Interface without changing `defs/raw/nemweb_public_files.py`, asset keys, graph
node names, output metadata, duplicate-row check, job names, schedules, or
landing paths.

The proof slice should migrate only the NEMWeb discovery factory. Do not fold in
the ad hoc VicGas public report job, unzipper assets, source-table bronze
assets, or ADR 0003 current-state ingestion behavior. Those are separate
ingestion roles.

Use the AEMO ETL **Component test** lane for the implementation slice because
the change composes Dagster `Definitions`, graph assets, dynamic mapping,
schedules, IO-manager metadata, and asset checks in process. Add focused
**Unit tests** only for pure helpers extracted inside the Module. Useful
narrowed debugging targets are:

```bash
uv run pytest tests/component/test_factories_nemweb.py \
  tests/component/test_defs_raw_modules.py \
  tests/component/test_download_vicgas_public_report_zip_files.py
```

Before treating the slice as validated, run `make component-test` from
`backend-services/dagster-user/aemo-etl`. Because this is an isolated AEMO ETL
Subproject change, finish with the Subproject **Commit check**:
`make run-prek`. Do not run **Integration tests** by default unless the slice
changes LocalStack, S3-compatible behavior, or the landing/Delta write
contract.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `CONTEXT.md`
  - `docs/repository/documentation-sync.md`
  - `docs/adr/0003-bounded-current-state-bronze-source-tables.md`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/nemweb_public_files.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/jobs/download_vicgas_public_report_zip_files.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/assets.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/models.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/ops/dynamic_nemweb_links_fetcher.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/ops/nemweb_link_fetcher.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/ops/nemweb_link_processor.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/ops/processed_link_combiner.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_factories_nemweb.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_raw_modules.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_download_vicgas_public_report_zip_files.py`
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
