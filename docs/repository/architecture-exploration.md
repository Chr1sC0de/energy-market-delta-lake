# Architecture Exploration

This temporary repository page captures issue-scoped architecture research.
It is not durable architecture guidance. Issue #87 must consume any accepted
findings into durable repo docs before deleting this file.

## Table of contents

- [#82: Explore deeper gas-model asset shell Module](#82-explore-deeper-gas-model-asset-shell-module)
- [Issue #83: Explore deeper NEMWeb discovery Module](#issue-83-explore-deeper-nemweb-discovery-module)
- [Issue #84: Explore archive-source planning consolidation](#issue-84-explore-archive-source-planning-consolidation)
- [Issue #85: Explore Ralph workflow and state separation](#issue-85-explore-ralph-workflow-and-state-separation)
- [Issue #86: Explore Dagster ECS runtime task-definition consolidation](#issue-86-explore-dagster-ecs-runtime-task-definition-consolidation)
- [Issue #81: Final architecture decision matrix](#issue-81-final-architecture-decision-matrix)

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
That definition module merges three scheduled discovery/listing assets:
`bronze_nemweb_public_files_vicgas` for `REPORTS/CURRENT/VicGas` and
`bronze_nemweb_public_files_gbb` for `REPORTS/CURRENT/GBB`, plus
`bronze_nemweb_public_files_sttm` for root CSV reports under
`REPORTS/CURRENT/STTM`. All three pass
`cron_schedule="*/30 * * * *"`, `n_executors=10`, `group_name="integration"`,
the configured default schedule status, and ECS CPU and memory tags into
`nemweb_public_files_definitions_factory`.

The definition module owns the domain-specific filters. `vicgas_file_filter`
excludes `CurrentDay.zip` and `PublicRptsNN.zip` bundles so the ad hoc
`download_vicgas_public_report_zip_files_job` remains the bootstrap/backfill
path for VicGas public report bundles. STTM uses a root-only folder filter and
a CSV-only file filter that excludes `CURRENTDAY.*`, `DAYNN.ZIP`, subfolders,
and helper file formats; the ad hoc `download_sttm_day_zip_files_job` owns
STTM DAYNN.ZIP bootstrap/backfill outside scheduled discovery.
`gbb_folder_filter` excludes `[To Parent Directory]` and `DUPLICATE`, while
otherwise using the default file filter.

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

## Issue #84: Explore archive-source planning consolidation

Issue #84 asks whether archive replay and local **End-to-end test** seed logic
should share a bounded archive-source planning Module. This section records
docs-only research. It does not change runtime behavior. Issue `#87` must
consume any accepted findings into durable repo docs before deleting this
temporary file.

### Evidence

Both paths already depend on the same source-table registry. Source-table
definition modules call
`backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/definitions.py`
to register a `DFFromS3KeysSourceTableSpec` containing `domain`,
`name_suffix`, `glob_pattern`, schema, surrogate-key columns, and object/frame
postprocess hooks. The registry in
`backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/source_tables.py`
imports the GBB, STTM, and VICGAS raw definition packages, returns stable ordered
specs, derives `archive_prefix` as `bronze/{domain}`, derives the target bronze
Delta URI, and supports explicit all/domain/table selection for the replay CLI.

Archive replay starts from operator-selected source-table specs. The CLI in
`backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/replay_bronze_archive.py`
requires exactly one of `--all`, `--domain`, or `--table`, defaults to dry-run,
and only writes when `--replace` is present. The maintenance code in
`backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/archive_replay.py`
lists S3 objects under each spec's `archive_prefix`, applies the spec
`glob_pattern`, returns `ArchiveObject` records, groups them into
`ArchiveReplayBatch` values bounded by bytes and file count, and reports an
`ArchiveReplayPlan` with matching files, batch count, total bytes, and target
Delta table URI. Replace mode remains outside object planning: it downloads
archive bytes, parses each source object with the source-table schema and
hooks, stages batches, collapses current state, and calls the same
current-state Delta writer used by normal source-table bronze ingestion.

The local **End-to-end test** seed path starts from the Dagster asset graph and
then falls back to the same source-table registry. In
`backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/e2e_archive_seed.py`,
`build_gas_model_archive_seed_spec` resolves the upstream assets for the
`gas_model` group, keeps only source-table bronze assets needed by that target,
and adds zip-domain seed specs for the selected source-table domains when the
matching unzipper asset exists. `refresh_archive_seed` builds coverage from the
live archive bucket, downloads the de-duplicated selected objects into the
ignored local cache, and writes a seed spec plus seed-run manifest. The
`load_cached_seed_to_localstack` path validates the cached coverage and uploads
the selected objects to the LocalStack landing bucket without reading live S3.
The CLI in
`backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/e2e_archive_seed.py`
keeps `spec`, `refresh`, and `load-localstack` as separate operator commands
and exposes the raw and zip latest-count knobs.

The prefix/glob S3 matching is already partly shared. Both archive replay and
seed refresh call `get_s3_pagination`, `get_object_head_from_pages`, and
`get_s3_object_keys_from_prefix_and_name_glob` from
`backend-services/dagster-user/aemo-etl/src/aemo_etl/utils.py`. The seed cache
path has a parallel filesystem implementation in `e2e_archive_seed.py` that
walks cached objects under the archive prefix and uses `fnmatch` against
`{archive_prefix}/{glob_pattern}`. The shared S3 helper does case-insensitive
matching by default, while the cached seed path lowers both relative keys and
normalized patterns before matching, so the matching semantics are
intentionally similar but duplicated.

The tests show the current behavioral contracts.
`backend-services/dagster-user/aemo-etl/tests/unit/test_maintenance_archive_replay.py`
checks source-table selector validation, archive-prefix and target-URI
derivation, byte/file batch planning, dry-run plan reporting without object
downloads, invalid/empty file skipping, and replace-mode current-state writes.
`backend-services/dagster-user/aemo-etl/tests/unit/test_maintenance_e2e_archive_seed.py`
checks default seed counts, seed-root discovery, live refresh shortfalls,
latest-object selection, cache reload into LocalStack, and cache shortfall
manifests.
`backend-services/dagster-user/aemo-etl/tests/component/test_maintenance_e2e_archive_seed.py`
verifies that the seed spec really comes from the Dagster definitions graph and
includes both GBB and VICGAS zip domains.

### Comparison

| Behavior | Archive replay | Local **End-to-end test** seed | Consolidation signal |
| --- | --- | --- | --- |
| Source-table spec loading | Loads all registered source-table specs, then uses explicit all/domain/table operator selection. | Resolves the `gas_model` upstream Dagster asset graph, then keeps matching registered source-table specs. | Shared source-table requirement shape is useful, but the selector inputs should stay caller-owned. |
| Prefix/glob matching | Lists S3 pages from the archive bucket and filters keys by source-table `archive_prefix` and `glob_pattern`. | Uses the same S3 list/filter path for refresh and a duplicated filesystem list/filter path for cached seed loading. | A small Module can own prefix/glob matching over supplied object heads for both S3 and cached heads. |
| Object planning | Plans the full matching archive scope into byte/file-bounded batches for dry-run evidence and replace execution. | Selects the latest N raw objects per required source table and latest N zip objects per required domain, then de-duplicates selected objects for download or upload. | Shared object DTOs and matching are valuable; selection policy differs and should be explicit. |
| Coverage selection | Coverage is the complete selected archive scope and reports file count, batch count, total bytes, and target table URI. | Coverage is requirement-based, reports requested count, available count, shortfall, selected objects, and manifest status. | Coverage reporting can share a common requirement/result model with replay-specific and seed-specific views. |
| Execution boundary | Dry-run stops at planning. Replace downloads bytes, parses source rows, stages Delta batches, and writes bounded current-state bronze. | Refresh downloads live archive objects to cache. LocalStack load uploads cached objects to landing before Dagster starts. | Execution side effects should stay outside the planning Module. |

### Proposed Module Interface

Create a Python Module for archive-source planning, not a Dagster Component and
not a current-state ingestion abstraction. The Interface should be bounded to
archive object requirements, matching, selection, and batch planning:

```python
ArchiveSourceRequirement(
    kind: Literal["source-table", "zip-domain"],
    name: str,
    archive_prefix: str,
    glob_pattern: str,
    target_table_uri: str | None = None,
)

ArchiveSourceObject(key: str, size: int)

ArchiveSourceSelectionPolicy(
    mode: Literal["all-batched", "latest-count"],
    max_batch_bytes: int = DEFAULT_MAX_BATCH_BYTES,
    max_batch_files: int = DEFAULT_MAX_BATCH_FILES,
    latest_count: int | None = None,
)

ArchiveSourceCoverage(
    requirement: ArchiveSourceRequirement,
    requested_count: int | None,
    available_count: int,
    selected_objects: tuple[ArchiveSourceObject, ...],
    shortfall: int = 0,
)

ArchiveSourceBatch(objects: tuple[ArchiveSourceObject, ...])

ArchiveSourcePlan(
    requirement: ArchiveSourceRequirement,
    coverage: ArchiveSourceCoverage,
    batches: tuple[ArchiveSourceBatch, ...] = (),
)

match_archive_source_objects(
    requirement: ArchiveSourceRequirement,
    object_heads: Mapping[str, S3ObjectHead],
) -> tuple[ArchiveSourceObject, ...]

plan_archive_sources(
    requirements: Sequence[ArchiveSourceRequirement],
    object_heads_by_requirement: Mapping[str, Mapping[str, S3ObjectHead]],
    policy: ArchiveSourceSelectionPolicy,
) -> tuple[ArchiveSourcePlan, ...]
```

The Module should own deterministic Implementation detail only:

- turning source-table and zip-domain requirements into archive prefix/glob
  matches
- normalizing S3-listed and cached-file object heads into one object shape
- applying case-insensitive prefix/glob matching consistently
- selecting either the full matching scope or the latest N objects
- producing byte/file batches only when the caller chooses the `all-batched`
  policy
- computing requested count, available count, selected object count, shortfall,
  total bytes, and stable selected-key ordering

The Interface should not absorb ADR 0003 current-state behavior. The existing
current-state write helper, archive replay replace mode, source-table bronze
asset ingestion, zero-byte handling, skipped-key warning, no-delete-on-absence
semantics, and Delta target replacement/merge policy must remain owned by
`factories/df_from_s3_keys` and `maintenance/archive_replay.py`. The planning
Module may carry `target_table_uri` as replay evidence, but it must not decide
when to overwrite or merge a Delta table.

### Explicit Integration Edges

Keep these edges explicit at the call sites:

- S3 client construction, `AWS_ENDPOINT_URL`, bucket names, and live S3 listing.
  The replay and seed CLIs decide whether they point at AWS or LocalStack.
- Archive refresh downloads and LocalStack seed uploads. The LocalStack load
  path is a concrete side effect into the landing bucket, not planning logic.
- LocalStack service wiring. `backend-services/compose.yaml` keeps
  `aemo-etl-seed-localstack` as a one-shot service gated by LocalStack health,
  and `backend-services/localstack/init-s3.sh` owns local bucket and DynamoDB
  lock-table creation.
- Dagster graph selection. The seed path should continue resolving
  `AssetSelection.groups("gas_model").upstream()` in the End-to-end test seed
  module and pass explicit archive requirements to the planning Module.
- Operator intent. The replay CLI's all/domain/table selection and `--replace`
  switch should stay outside the Module.
- Current-state writes. ADR 0003 limits current-state semantics to
  source-table bronze assets and archive replay; zip-domain seed objects and
  LocalStack landing uploads are not source-table bronze rebuilds.

### Recommendation

The smallest implementation slice is to extract a pure
`maintenance/archive_source_planning.py` Module and migrate only the duplicated
archive object matching, latest-object selection, coverage accounting, and
byte/file batch planning from archive replay and the End-to-end test seed
maintenance code. Keep `DFFromS3KeysSourceTableSpec`, Dagster asset selection,
CLI parsing, S3 download/upload, LocalStack cache loading, and current-state
Delta writes in their current modules for the first slice.

Use the AEMO ETL **Unit test** lane for that slice because the extracted Module
should be pure Python over object-head mappings and cached-file metadata. Useful
narrowed debugging targets are:

```bash
uv run pytest tests/unit/test_maintenance_archive_replay.py \
  tests/unit/test_maintenance_e2e_archive_seed.py \
  tests/unit/test_utils.py
```

Before treating the slice as validated, run `make unit-test` from
`backend-services/dagster-user/aemo-etl`, then the Subproject **Commit check**
with `make run-prek`. Add the AEMO ETL **Component test** lane only if the
slice changes `build_gas_model_archive_seed_spec` or any Dagster definition
graph behavior. Do not run **Integration tests** by default unless the slice
changes LocalStack service wiring, S3-compatible behavior, cached seed uploads,
or the landing/Delta write contract.

## Issue #85: Explore Ralph workflow and state separation

Issue #85 asks how Ralph's workflow and state handling can be separated without
changing runtime behavior. This section records docs-only research. It does not
change runtime behavior, git operations, GitHub issue metadata, or Ralph
labels. Issue `#87` must consume any accepted findings into durable repo docs
before deleting this temporary file.

### Current Responsibility Map

- Queue selection and issue eligibility currently mix pure policy and GitHub
  reads. `RalphLoop.run`, `_next_ready_issue`, `_next_triage_issue`,
  `_issue_pool`, and `_has_open_blockers` decide whether Ralph implements,
  triages, or stops. The pure predicates `is_ready_candidate`,
  `is_basic_triage_candidate`, `parse_blockers`, and
  `missing_required_sections` hold the reusable workflow rules. Tests cover
  label blocking, triage candidacy, drain budgets, and dirty-root preflight in
  `tests/test_ralph.py`; `docs/agents/ralph-loop.md` documents the same drain
  flow and implementation stop labels.
- **Delivery mode** and **Integration target** resolution are already mostly
  pure. Constants such as `GITFLOW_MODE`, `TRUNK_MODE`, `EXPLORATORY_MODE`,
  `DEFAULT_GITFLOW_BRANCH`, `DEFAULT_TRUNK_BRANCH`,
  `DEFAULT_EXPLORATORY_BRANCH_PREFIX`, and the delivery labels define the
  vocabulary. `resolve_delivery_plan`,
  `delivery_label_for_mode`, and `default_target_branch_for_mode` decide the
  mode, target, labels to add, and conflicting labels to remove. `build_config`
  adds CLI defaults and the deprecated `--base` compatibility path. Tests
  assert Gitflow defaults, exploratory review-branch defaults, conflict
  normalization to Exploratory or Gitflow, and trunk compatibility.
  `docs/adr/0002-ralph-delivery-modes.md` records why Gitflow is the default,
  why `delivery-exploratory` wins conflicting delivery labels, and why
  Gitflow wins trunk-only conflicts.
- Run state is centralized in `RunManifest`, but the manifest writes are
  called directly from workflow steps. Implementation manifests record issue,
  **Delivery mode**, **Integration target**, branch paths, changed files, QA,
  sandboxed issue access, published implementation commit, pushes, GitHub
  metadata, events, and failure details. **Promotion** manifests additionally
  record source branch, source tree, promoted issues, the promoted source
  commit inventory, Promotion commit, source-branch sync, and
  **Post-promotion review** plus validated follow-up issue creation state. The
  promoted source commit inventory records each promoted commit SHA and subject,
  then classifies commits that match verified issue `integrated_commit` values
  as verified **Local integration** commits while leaving other entries visible
  as unverified **Promotion** commits.
  Inspection and recovery helpers (`load_run_manifest`, `inspect_run`,
  `recommended_run_action`, and `RalphRunRecovery`) read the same JSON
  contract. Tests assert manifest content for successful implementation,
  failed QA, Promotion, inspection, and recovery.
- QA selection is pure policy plus command execution. `select_qa_commands`
  maps changed files to the AEMO ETL **Test lane** commands, root
  **Commit check**, and Ralph unit tests. `select_promotion_gate_commands`
  adds the AEMO ETL **End-to-end test** gate for non-doc runtime AEMO ETL
  changes during **Promotion**. `_run_qa_command_sequence` owns execution,
  logs, run-scoped QA runtime environment, failure classification, and manifest
  mutation. Tests cover runtime AEMO ETL changes, docs-only AEMO ETL changes,
  mixed changes, root docs plus Ralph script changes, Promotion gates, and
  manifest-recorded QA runtime variables. `docs/agents/ralph-loop.md` mirrors
  this policy in the QA policy section.
- Codex implementation and sandbox setup are workflow-adjacent side effects.
  `_implement_with_retry` decides the two-attempt behavior and when to rerun QA
  after a retry. `_run_codex`, `prepare_sandbox_issue_access`,
  `write_sandbox_gh_wrapper`, and `codex_env_for_sandbox_issue_access` set up
  **Sandboxed issue access** and writable QA runtime paths before command
  execution. Tests assert that the sandbox receives `GH_TOKEN`, `GH_REPO`, and
  runtime paths without recording the token in the manifest.
  `docs/adr/0004-ralph-sandboxed-issue-access.md` records the boundary:
  sandboxed Codex may update GitHub issue metadata, but **Local integration**,
  Git push, and **Promotion** stay in Ralph's outer loop.
- Git operations are concentrated in `GitClient`, but workflow ordering still
  lives in `_handle_implementation`, `_ensure_integration_target`,
  `_sync_default_gitflow_target_with_trunk`, `_promote`, and
  `_sync_source_branch_after_promotion`. `GitClient` performs fetch, branch
  creation, worktree creation, diff detection, commit, rebase, squash merge,
  no-ff merge, push, ancestor checks, and cleanup. Tests assert trunk squash
  merge and push, Gitflow `dev` creation, Gitflow `main` to `dev` sync before
  issue branch creation, target-drift rebase plus QA rerun, Promotion merge,
  and `dev` fast-forward after Promotion. `docs/adr/0001-ralph-local-integration.md`
  records why Ralph uses **Local integration** instead of GitHub PRs.
- GitHub issue metadata is concentrated in `GitHubClient`, but metadata policy
  is spread through `_handle_implementation`, `_mark_issue_failed`,
  `_close_promoted_issues`, `RalphRunRecovery`, `build_completion_comment`,
  and `build_promotion_comment`. The current semantics are: claim by adding
  `agent-running`, add or normalize the delivery label, remove stale terminal
  labels, remove `ready-for-agent`, comment completion evidence after a
  successful push, mark trunk work `agent-merged` and close it, mark Gitflow
  work `agent-integrated` and leave it open, mark exploratory work
  `agent-reviewing` and leave it open for review, mark failures
  `agent-failed`, and close only verified `agent-integrated` issues during
  **Promotion**. Tests cover completion comments, failure comments, trunk
  closure, Gitflow non-closure, exploratory review-branch state, Promotion
  comments, recovery metadata, and post-push metadata failure.
- Recovery and fail-stop behavior are state-driven but adapter-backed.
  `inspect_run` is read-only. `RalphRunRecovery.recover` fetches the expected
  **Integration target** and refuses metadata recovery unless the recorded
  **Local integration** commit is reachable from `origin/<target>`. After a
  post-push metadata failure, Ralph raises `PostPushFailure`, records the
  failure in the manifest, and does not clean up successful worktrees. Tests
  assert that recovery refuses unreachable commits, reconciles trunk metadata
  with closure, reconciles Gitflow metadata without closure, and stops after
  post-push metadata failure.
- **Promotion** is currently a method-level workflow inside `RalphLoop`.
  `_promote` fetches source and target, records the source revision, computes
  changed files, records the promoted source commit inventory, creates a
  source worktree, runs the aggregate **Push check** and any Promotion gate
  from that exact source revision, verifies `agent-integrated` issues by
  parsing recorded Gitflow integration commits, classifies inventory commits
  as verified **Local integration** or unverified **Promotion** commits, creates
  the target Promotion worktree, merges, pushes `main`, fast-forwards `dev`,
  updates issue metadata, and then runs **Post-promotion review** when enabled
  and changed files exist. Successful review artifacts may then feed Ralph's
  validated create-only helper for follow-up issues. Unverified **Promotion**
  commits are review context only, not **Promotion** blockers or automatic
  issue-association work. Tests assert ordering so failed **Push check** or
  AEMO ETL **End-to-end test** gate
  cannot reach merge, push, branch sync, issue metadata, or closure.

### Proposed Module Structure

Keep `scripts/ralph.py` as the CLI entrypoint and controller, but move policy
and state into Modules that can be tested without git or GitHub:

```text
scripts/ralph.py
  CLI parsing, command wiring, and high-level controller.

scripts/ralph_workflow.py
  Pure workflow policy: label sets, Issue snapshot, issue eligibility,
  required-section validation, blocker parsing, DeliveryPlan resolution,
  Integration target defaults, branch/worktree naming, QA command selection,
  recovery action recommendation, and comment body builders.

scripts/ralph_state.py
  RunManifest and manifest readers/writers. This Module owns the JSON schema,
  state transitions, event names, status values, QA result serialization,
  push metadata, GitHub metadata status, and recovery preconditions that can be
  checked without calling git or gh.

scripts/ralph_adapters.py
  Side-effect Adapters: CommandRunner, GitAdapter, GitHubIssueAdapter, and
  CodexAdapter or sandbox preparation helpers. These classes translate method
  calls into shell commands, file writes, gh calls, and command logs. They do
  not choose **Delivery mode**, decide issue terminal state, or mutate
  manifests except through explicit controller calls.
```

The controller can then read as: compute a workflow decision, record the state
transition, call the relevant Adapter, record the Adapter result, and continue.
That shape keeps the behavior observable in the same `ralph-run.json` files
while making decision code testable without fake git or fake gh command
fixtures.

The useful boundaries are:

- Workflow policy owns "what should happen next": issue eligibility, **Delivery
  mode**, **Integration target**, selected QA commands, failure classifications,
  expected metadata transition, and recovery recommendation.
- Run state owns "what has happened": manifest schema, status/stage/events,
  changed files, QA results, sandbox and runtime environment evidence, commits,
  pushes, GitHub metadata state, and failure details.
- Git Adapter owns "how refs are changed": fetch, branch creation, worktree
  creation, commit, rebase, squash merge, no-ff merge, push, ancestor checks,
  worktree removal, and branch deletion.
- GitHub Issue Adapter owns "how issue metadata is changed": list/view issue,
  issue state, comments, label edits, closure, reopen, auth status, and label
  bootstrap.
- Codex/command Adapter owns "how commands run": command logs, heartbeat,
  stdin prompt handling, sandbox wrapper creation, environment injection, and
  environment-failure detection.

### Semantics To Preserve

- **Local integration** must remain after implementation QA and before issue
  completion metadata for Gitflow and Trunk delivery. It must still fetch the
  current **Integration target**, rebase and rerun selected QA if the target
  moved, create a detached integration worktree from the target, squash-merge
  the issue branch, create one integration commit, and push that commit to the
  target. Exploratory delivery must instead push a durable handoff branch from
  `origin/main` without opening a GitHub PR.
- **Delivery mode** semantics must stay identical. Missing delivery labels use
  the CLI default, default CLI behavior is Gitflow, Gitflow defaults to `dev`,
  Trunk defaults to `main`, Exploratory defaults to
  `agent/exploratory/issue-N-slug`, `--target-branch` overrides the target, and
  conflicting delivery labels normalize to `delivery-exploratory` when present
  or `delivery-gitflow` for Gitflow/trunk conflicts. Gitflow must still create
  `dev` from `main` when missing and keep default `dev` current with `main`
  before issue work begins. Exploratory must still fail clearly if the remote
  handoff branch already exists.
- GitHub issue metadata must remain ordered behind git pushes. Trunk completion
  still comments evidence, marks `agent-merged`, and closes the issue. Gitflow
  completion still comments evidence, marks `agent-integrated`, and leaves the
  issue open for **Promotion**. Exploratory completion still comments evidence,
  marks `agent-reviewing`, and leaves the issue open for human review. Failure
  still records `agent-failed` with run evidence. Post-push metadata failures
  must still stop loudly and keep enough state for recovery.
- **Promotion** must still run the aggregate **Push check** from an isolated
  source worktree at the fetched source revision before creating the target
  Promotion worktree. The AEMO ETL **End-to-end test** gate must still run for
  non-doc runtime AEMO ETL changes before any Promotion merge, push,
  source-branch sync, GitHub metadata update, or issue closure. **Promotion**
  must close only `agent-integrated` issues whose recorded Gitflow integration
  commit is verified in the promoted range. Unverified **Promotion** commits
  must remain **Post-promotion review** context, without blocking **Promotion**
  or automatically creating GitHub Issues by themselves. Follow-up issue
  creation must come only from structured review drafts and Ralph's validated
  create-only helper.
- Recovery must remain manifest-gated. `--inspect-run` stays read-only, and
  `--recover-run` must refuse to mutate GitHub issue metadata until the
  recorded **Local integration** or Exploratory handoff commit is reachable
  from the expected **Integration target**.
- **Sandboxed issue access** must remain limited to GitHub issue metadata for
  spawned Codex subprocesses. Git fetch, **Local integration**, Exploratory
  handoff pushes, and **Promotion** stay outside the sandbox.

### Smallest Implementation Slice

Start with a no-behavior-change extraction of pure workflow and state objects,
not a full controller rewrite:

1. Create `scripts/ralph_workflow.py` and move label constants, issue
   eligibility helpers, blocker parsing, required-section validation,
   `DeliveryPlan`, delivery resolution, target defaults, QA command selection,
   recovery action recommendation, and completion/promotion comment builders
   into it.
2. Create `scripts/ralph_state.py` and move `RunManifest`, manifest loading,
   manifest summary helpers, and recovery precondition readers into it.
3. Leave `GitClient`, `GitHubClient`, `CommandRunner`, Codex sandbox setup,
   `RalphLoop`, and `RalphRunRecovery` in `scripts/ralph.py` for the first
   slice, importing the extracted policy/state code. This keeps the git and
   GitHub Adapter behavior stable while making the workflow/state boundary
   explicit.
4. Move or add focused unit tests for the extracted Modules, but keep the
   existing end-to-end fake-runner tests in `tests/test_ralph.py` as regression
   coverage for current **Local integration**, **Promotion**, recovery, and
   issue metadata semantics.

That slice should run Ralph's script-level **Test lane** plus the root
**Commit check** because it changes `scripts/`, `tests/`, and maintained docs:

```bash
python3 -m unittest discover -s tests
prek run -a
```

No AEMO ETL **Unit test**, **Component test**, **Integration test**, or
**End-to-end test** lane is needed unless a later slice changes the AEMO ETL
**Subproject** or the Promotion gate command surface.

## Issue #86: Explore Dagster ECS runtime task-definition consolidation

Issue #86 asks whether the repeated Pulumi Dagster ECS runtime
task-definition logic should become a shared runtime Module. This section
records docs-only research. It does not change runtime behavior. Issue `#87`
must consume any accepted findings into durable repo docs before deleting this
temporary file.

### Evidence

The repeated behavior is concentrated in
`infrastructure/aws-pulumi/components/ecs_services.py`. There are four deployed
services but three runtime roles to compare: one `aemo-etl` user-code gRPC
service, two webserver variants created by `DagsterWebserverServiceComponentResource`,
and one daemon service. The existing `_task_definition` helper already owns the
AWS task-definition shell: `requires_compatibilities=["FARGATE"]`,
`network_mode="awsvpc"`, task CPU, task memory, execution role ARN, task role
ARN, and JSON container definitions. The existing `_fargate_service` helper
already owns service-level Fargate behavior: one desired task,
`FARGATE_SPOT`, private subnet placement, no public IP, deployment circuit
breaker with rollback, forced deployments, propagated service tags, and
optional Cloud Map registration.

The remaining duplication is inside each role's `container_defs =
pulumi.Output.all(...).apply(lambda a: json.dumps([...]))` block. Every role
builds a single essential container, injects PostgreSQL environment values from
Pulumi resource outputs, attaches CloudWatch `awslogs` configuration, and
defines a health-check object with the same timing settings.

| Runtime concern | Shared behavior | Role-specific Inputs |
| --- | --- | --- |
| Pulumi dependency inputs | Each role combines an image URI, Postgres hostname/password, CloudWatch log group name, and AWS region before serializing container definitions. | The image URI differs by ECR repository. User code also passes failure-alert config values. |
| Environment | All roles set `DAGSTER_POSTGRES_DB`, `DAGSTER_POSTGRES_HOSTNAME`, `DAGSTER_POSTGRES_USER`, `DAGSTER_POSTGRES_PASSWORD`, `DEVELOPMENT_ENVIRONMENT`, and `DEVELOPMENT_LOCATION`. | User code and daemon also set `AWS_S3_LOCKING_PROVIDER` and `DAGSTER_GRPC_TIMEOUT_SECONDS`. User code adds `AWS_DEFAULT_REGION`, `DAGSTER_CURRENT_IMAGE`, `DAGSTER_FAILURE_ALERT_TOPIC_ARN`, and `DAGSTER_FAILURE_ALERT_BASE_URL`. Webservers intentionally keep a smaller environment. |
| Logging | All roles use `logDriver="awslogs"` with the shared cluster log group and region. | Stream prefixes are role-specific: `dagster-aemo-etl-user-code`, the supplied webserver stream prefix, and `dagster-daemon`. |
| Health | All roles use interval `15`, timeout `5`, retries `4`, and start period `60`. | User code performs a socket check against localhost port `4000`. Webserver and daemon currently use `true`. |
| Container task shape | Every role defines one essential container and serializes the container list to the ECS task definition. | Container name, entry point, and ports differ: `dagster-grpc` exposes `4000`, webserver exposes `3000` and may insert `--read-only`, and daemon has no port mapping. |
| Task settings | Code currently gives all four deployed task definitions CPU `256` and memory `1024` through `_task_definition`. | Families and IAM role ARNs differ. User code and daemon currently use daemon execution/task roles, while webservers use webserver execution/task roles. The runtime doc currently lists webservers as CPU `512`; `#87` should reconcile that durable-doc drift while consuming this temporary section. |
| Service Fargate settings | `_fargate_service` already centralizes `FARGATE_SPOT`, private subnet, no public IP, circuit breaker, desired count, and tag propagation. | Security group, Cloud Map namespace/name, service tags, and absence of daemon Cloud Map registration remain role-owned service Inputs rather than task-definition Inputs. |

This is enough repetition to justify a shared runtime task Module, but not a
new high-level Pulumi `ComponentResource` that receives whole ECR, Postgres,
cluster, IAM, service-discovery, security-group, or VPC components. Passing
whole components would hide the Pulumi resource dependencies that currently
make task definitions readable.

### Proposed Module Interface

Create a small Python Module for Dagster ECS runtime task definitions inside
the AWS Pulumi **Subproject**. Keep it code-level, not a Dagster Component and
not a new service-level Pulumi component. The Interface should accept explicit
Pulumi Inputs and return the same task-definition resource shape used today:

```python
DagsterRuntimeTaskSharedInputs(
    postgres_host: pulumi.Input[str],
    postgres_password: pulumi.Input[str],
    log_group_name: pulumi.Input[str],
    region: pulumi.Input[str],
    environment: str,
    development_location: str = "aws",
)

DagsterRuntimeTaskSpec(
    resource_name: str,
    family: str,
    container_name: str,
    image: pulumi.Input[str],
    entry_point: Sequence[str],
    log_stream_prefix: str,
    execution_role_arn: pulumi.Input[str] | None,
    task_role_arn: pulumi.Input[str],
    cpu: str = "256",
    memory: str = "1024",
    port: int | None = None,
    extra_environment: Mapping[str, pulumi.Input[str]] | None = None,
    health_check_command: Sequence[str] = ("CMD-SHELL", "true"),
    child_opts: pulumi.ResourceOptions | None = None,
)

build_dagster_runtime_task_definition(
    shared: DagsterRuntimeTaskSharedInputs,
    spec: DagsterRuntimeTaskSpec,
) -> aws.ecs.TaskDefinition
```

The Module should own these shared defaults:

- common PostgreSQL and deployment environment variables
- one-container ECS JSON serialization
- CloudWatch log configuration shape
- default health-check timing
- optional port mapping construction
- Fargate task-definition defaults already used by `_task_definition`
- default CPU and memory values, with explicit overrides

The role components should keep these Inputs explicit at the call site:

- ECR image URI outputs, because they name the deployed image dependency
- Postgres hostname/password, log group name, and region, because they are
  Pulumi resource/provider values
- execution role and task role ARNs, because user code and daemon currently
  share daemon roles while webservers use separate webserver roles
- user-code gRPC entry point, current-image env, failure-alert env, port `4000`,
  and socket health command
- webserver path prefix, read-only flag, Cloud Map-derived family, stream
  prefix, port `3000`, and smaller environment
- daemon `dagster-daemon run` entry point, no port mapping, no Cloud Map service
  registration, and daemon tags

Keep `_fargate_service` separate for the first implementation slice. Its
service-level defaults are already consolidated, and folding service discovery,
security groups, subnet placement, and tags into the task-definition Module
would blur the boundary between task runtime and ECS service wiring.

### Test Strategy

The current
`infrastructure/aws-pulumi/tests/component/test_ecs_services.py` suite already
uses Pulumi mocks and inspects resolved task definitions and services. A shared
Module should let tests validate common behavior once and role differences
separately:

- Add one shared-runtime test that builds a minimal spec and asserts the common
  container JSON: one essential container, common Postgres and deployment env,
  `awslogs` log configuration, default health-check timing, optional port
  behavior, and digest-pinned image pass-through.
- Add one task-definition test for Fargate defaults: compatibility
  `FARGATE`, network mode `awsvpc`, CPU, memory, execution role ARN, task role
  ARN, and parent options.
- Keep role-specific tests for user code, webserver admin, webserver guest, and
  daemon. Those should assert entry points, ports, extra env, stream prefixes,
  task-definition families, read-only webserver behavior, user-code alert env,
  current-image env, and daemon no-port behavior.
- Keep service-level tests around `_fargate_service`: `FARGATE_SPOT`, private
  subnet, no public IP, circuit breaker, Cloud Map registration for inbound
  services, and no Cloud Map registration for the daemon.
- Keep `test_deprecation_warnings.py` as a cross-component regression guard so
  the extraction does not reintroduce deprecated Pulumi AWS provider usage.

The relevant infrastructure **Test lane** for the implementation slice is the
AWS Pulumi **Component test** lane because Pulumi mocks validate in-process
resource wiring without deployed cloud resources. A narrowed debug run can
target:

```bash
uv run pytest tests/component/test_ecs_services.py \
  tests/component/test_deprecation_warnings.py -q
```

Before treating the slice as validated, run the AWS Pulumi **Commit check** from
`infrastructure/aws-pulumi`:

```bash
prek run -a
```

No **Deployed test** or **Push check** should be required for the no-behavior
extraction unless the slice changes live service settings rather than only
centralizing equivalent task-definition construction. If the slice also updates
durable root docs, run the root documentation QA described in
`docs/repository/documentation-sync.md`.

### Recommendation

Use the smallest no-behavior-change implementation slice: extract only the
runtime task-definition and container-definition assembly behind a
`DagsterRuntimeTaskSpec`, then migrate user code, both webserver variants, and
daemon to that helper in one pass. Leave ECR image publishing, IAM policy
definitions, `_fargate_service`, Cloud Map service registration, security-group
selection, subnet placement, and Dagster run-worker configuration unchanged.

That slice is small enough to prove the shared runtime defaults once while
still preserving role-specific Inputs at the current component call sites. It
also avoids a half-migrated state where some roles use a shared task shell and
others keep the old inline JSON shape.

## Issue #81: Final architecture decision matrix

This is the aggregate decision matrix for issues #82, #83, #84, #85, and #86.
It is still temporary architecture exploration, not durable architecture
guidance. Issue #87 must consume the accepted decisions, doc-sync targets, and
known doc drift into maintained repo docs before deleting this file.

| Candidate | Evidence consumed | Depth gain | Coupling removed | Affected **Subproject** | Likely Interface shape | Risk | **Test lane** or **Commit check** | Maintained doc sync impact | Smallest implementation slice |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gas-model asset shell | #82 found 28 `silver_*.py` gas-model assets under `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model` with repeated Dagster asset metadata, retry policy, checks, sensors, and `Definitions` assembly. The same section cites `silver_gas_dim_date.py` as the schedule-shaped exception and tests such as `test_defs_sensors.py` and gas-model component tests as current behavior evidence. | High. The current asset files mostly repeat shell code around domain transforms, so a Module would deepen the gas-model asset boundary while keeping transform logic local. | Removes repeated Dagster decoration, metadata, standard checks, retry policy, `MaterializeResult` wrapping, and default sensor assembly from each asset file. | `backend-services/dagster-user/aemo-etl` AEMO ETL **Subproject**. | Python Module with `GasModelAssetSpec` plus `build_gas_model_asset_definitions(spec) -> Definitions`. Keep `AssetIn`, `AssetKey`, lineage, schedules, and Polars transforms explicit at each asset. | Medium. Over-generalizing scheduled assets such as `silver_gas_dim_date` would hide real graph variation; asset metadata and sensor names are regression-prone. | AEMO ETL **Component test** lane with narrowed asset tests and `test_defs_sensors.py`; finish with `make component-test` and the Subproject **Commit check** `make run-prek`. Add **Unit tests** only for pure helper extraction. | Likely `backend-services/dagster-user/aemo-etl/README.md`, `backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md`, and `backend-services/dagster-user/aemo-etl/docs/gas_model/README.md`; individual gas-model ERD docs only if public table contracts or column metadata change. | Add a private gas-model shell Module and migrate one ordinary dependency-updated asset such as `silver_gas_dim_location` or `silver_gas_fact_scada_pressure`; leave `silver_gas_dim_date` explicit. |
| NEMWeb discovery | #83 traced `defs/raw/nemweb_public_files.py`, `nemweb_public_files_definitions_factory`, the four op-builder seams, `HTTPNEMWebLinkFetcher`, `FilteredDynamicNEMWebLinksFetcher`, `S3NemwebLinkProcessor`, `S3ProcessedLinkCombiner`, and tests such as `test_factories_nemweb.py`, `test_defs_raw_modules.py`, and `test_download_vicgas_public_report_zip_files.py`. It also cites ADR 0003 as evidence that current-state semantics belong to source-table bronze assets, not discovery/listing assets. | High. The discovery/listing asset is one cohesive fetch-filter-process-combine Module with too much caller-visible orchestration. | Removes one-Adapter strategy classes, op-builder pass-throughs, cached-link filter assembly, fixed output schema wiring, surrogate-key construction, duplicate-row check wiring, job naming, and schedule assembly from caller-owned configuration. | `backend-services/dagster-user/aemo-etl` AEMO ETL **Subproject**. | Compatibility wrapper around `NEMWebPublicFilesSpec` plus `build_nemweb_public_files_definitions(spec) -> Definitions`. Keep domain identity, filters, schedule/status, concurrency, retry knobs, buckets, and IO manager explicit. | Medium. Dynamic mapping, landing object writes, schedule names, and duplicate suppression must remain byte-for-byte equivalent from the caller perspective. | AEMO ETL **Component test** lane; narrowed debug targets are `test_factories_nemweb.py`, `test_defs_raw_modules.py`, and `test_download_vicgas_public_report_zip_files.py`; finish with `make component-test` and `make run-prek`. Run **Integration tests** only if LocalStack, S3-compatible behavior, or landing/Delta contracts change. | Likely `backend-services/dagster-user/aemo-etl/README.md`, `backend-services/dagster-user/aemo-etl/docs/architecture/ingestion_flows.md`, and `backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md`; ADR 0003 only if current-state boundary language changes. | Introduce the spec-shaped builder, keep `nemweb_public_files_definitions_factory` as a thin wrapper, and migrate only the NEMWeb discovery factory. Do not fold in manual ZIP bootstrap downloads, unzipper assets, or source-table bronze ingestion. |
| Archive-source planning | #84 compared archive replay and local **End-to-end test** seed logic. Evidence came from source-table registry files, `maintenance/archive_replay.py`, `maintenance/e2e_archive_seed.py`, both CLIs, shared S3 helpers in `utils.py`, LocalStack/compose wiring, ADR 0003, and unit/component tests for archive replay and seed refresh/load behavior. | Medium-high. The repeated archive object matching and coverage planning are deep enough for a pure planning Module, but execution side effects should stay outside it. | Removes duplicated prefix/glob matching, object-head normalization, latest-object selection, coverage accounting, and byte/file batch planning from replay and seed paths. | `backend-services/dagster-user/aemo-etl` AEMO ETL **Subproject** plus local development wiring in `backend-services` when seed behavior is documented. | Pure Python Module such as `maintenance/archive_source_planning.py` with `ArchiveSourceRequirement`, `ArchiveSourceObject`, `ArchiveSourceSelectionPolicy`, `ArchiveSourceCoverage`, `ArchiveSourcePlan`, `match_archive_source_objects`, and `plan_archive_sources`. | Medium. Mixing planning with ADR 0003 current-state writes, LocalStack upload side effects, or Dagster graph selection would create the wrong abstraction. | AEMO ETL **Unit test** lane; finish with `make unit-test` and `make run-prek`. Add AEMO ETL **Component test** lane only if `build_gas_model_archive_seed_spec` or Dagster definition graph behavior changes. Run **Integration tests** only if LocalStack, S3-compatible behavior, cache uploads, or landing/Delta contracts change. | Likely `backend-services/dagster-user/aemo-etl/README.md`, `backend-services/dagster-user/aemo-etl/docs/development/local_development.md`, `backend-services/dagster-user/aemo-etl/docs/architecture/ingestion_flows.md`, `backend-services/README.md`, and ADR 0003 if current-state scope wording changes. | Extract pure archive-source planning and migrate only duplicated matching, latest-object selection, coverage accounting, and batch planning. Keep source-table specs, DAG selection, CLI parsing, S3 download/upload, LocalStack loading, and current-state Delta writes in their current modules. |
| Ralph workflow/state separation | #85 mapped `scripts/ralph.py`, `tests/test_ralph.py`, `docs/agents/ralph-loop.md`, ADR 0001, ADR 0002, and ADR 0004. Evidence covered issue eligibility, **Delivery mode** resolution, **Integration target** defaults, `RunManifest`, QA selection, **Local integration**, GitHub metadata ordering, recovery, and **Promotion** gates. #88 adds Exploratory delivery labels, review-branch defaults, and `agent-reviewing` blocking; #89 moves Exploratory delivery to a durable `agent/exploratory/issue-N-slug` handoff branch from `origin/main` without **Local integration**; #90 requires `## Review focus` before Exploratory handoff. | High. Pure workflow and state rules can become testable Modules while the CLI controller keeps side effects in one place. | Removes pure label policy, blocker parsing, required-section validation, delivery planning, QA command selection, manifest schema, comment builders, and recovery recommendation from the side-effect-heavy controller. | Repository root scripts/docs **Subproject** surface: `scripts/`, `tests/`, `docs/agents`, and ADRs. | `scripts/ralph_workflow.py` for pure policy and `scripts/ralph_state.py` for manifest/state. Keep Git, GitHub, command, and Codex adapters in `scripts/ralph.py` for the first slice. | High. Ordering is critical: QA must precede **Local integration** or Exploratory handoff, git pushes must precede issue metadata, Gitflow work must remain open until **Promotion**, trunk work must close after integration to `main`, Exploratory work must fail if the Review focus is missing or the remote handoff branch already exists and otherwise remain open with `agent-reviewing`, and recovery must stay manifest-gated by reachability from the expected **Integration target**. | Ralph script-level **Test lane** with `python3 -m unittest discover -s tests`; finish with root **Commit check** `prek run -a`. No AEMO ETL lane is needed unless Promotion gate command selection changes. | Likely `docs/agents/ralph-loop.md`; ADR 0001, ADR 0002, and ADR 0004 if **Local integration**, **Delivery mode**, **Integration target**, sandboxed issue access, or **Promotion** semantics are touched. `docs/repository/documentation-sync.md` only if root doc QA policy changes. | Extract pure workflow helpers to `scripts/ralph_workflow.py` and manifest/state helpers to `scripts/ralph_state.py`, then import them from `scripts/ralph.py` while keeping `GitClient`, `GitHubClient`, `CommandRunner`, `RalphLoop`, and `RalphRunRecovery` in place. |
| Dagster ECS runtime task definitions | #86 found repeated container JSON assembly in `infrastructure/aws-pulumi/components/ecs_services.py` across the AEMO ETL user-code service, two webserver variants, and the daemon. Evidence also came from `_task_definition`, `_fargate_service`, `test_ecs_services.py`, `test_deprecation_warnings.py`, and `infrastructure/aws-pulumi/docs/runtime.md`, including the noted CPU documentation drift for webservers. | Medium-high. Task-definition and container-definition defaults can become one runtime Module without hiding service-level Pulumi wiring. | Removes repeated PostgreSQL/deployment environment variables, one-container ECS JSON serialization, CloudWatch log config, health-check timing, optional port mapping, and Fargate task-definition defaults from role components. | `infrastructure/aws-pulumi` AWS Pulumi **Subproject**. | Python Module with `DagsterRuntimeTaskSharedInputs`, `DagsterRuntimeTaskSpec`, and `build_dagster_runtime_task_definition(shared, spec) -> aws.ecs.TaskDefinition`. Keep ECR image outputs, roles, entry points, ports, role-specific env, Cloud Map, security groups, and `_fargate_service` explicit. | Medium. Pulumi `Input`/`Output` ordering, role-specific IAM ARNs, read-only webserver flags, daemon no-port behavior, and runtime doc drift make equivalence testing important. | AWS Pulumi **Component test** lane with `tests/component/test_ecs_services.py` and `tests/component/test_deprecation_warnings.py`; finish with the AWS Pulumi **Commit check** `prek run -a` from `infrastructure/aws-pulumi`. No **Push check** or deployed validation unless live service settings change. | Likely `infrastructure/aws-pulumi/README.md` and `infrastructure/aws-pulumi/docs/runtime.md`; root `docs/repository/architecture.md` only if repository-level AWS runtime structure changes. #87 should reconcile the webserver CPU doc drift while making durable updates. | Extract only runtime task-definition and container-definition assembly behind `DagsterRuntimeTaskSpec`, then migrate user code, both webservers, and daemon together. Leave ECR publishing, IAM policy definitions, `_fargate_service`, Cloud Map, security groups, subnet placement, and Dagster run-worker configuration unchanged. |

The matrix points to no runtime behavior change by itself. Later implementation
issues should treat these as independent slices, run the listed local **Test
lane** and **Commit check** surfaces, treat those **Commit check** commands as
the relevant local **Fast check** path for their **Subproject**, and let Ralph
perform the configured **Local integration** or Exploratory handoff for the
selected **Delivery mode** and **Integration target**. Gitflow slices remain
open after integration to `dev` until **Promotion** moves them to `main`; trunk
slices can close after integration to `main`; exploratory slices stay open with
`agent-reviewing` after publishing their durable review branch.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `CONTEXT.md`
  - `backend-services/compose.yaml`
  - `backend-services/localstack/init-s3.sh`
  - `backend-services/scripts/aemo-etl-e2e`
  - `docs/repository/documentation-sync.md`
  - `docs/adr/0003-bounded-current-state-bronze-source-tables.md`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/utils.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/e2e_archive_seed.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/replay_bronze_archive.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/nemweb_public_files.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/_manifest.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/source_tables.json`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int651_v1_ex_ante_market_price_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int652_v1_ex_ante_schedule_quantity_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int653_v3_ex_ante_pipeline_price_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int654_v1_provisional_market_price_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int655_v1_provisional_schedule_quantity_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int656_v2_provisional_pipeline_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int657_v2_ex_post_market_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int658_v1_latest_allocation_quantity_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int659_v1_bid_offer_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int660_v1_contingency_gas_bids_and_offers_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int661_v1_contingency_gas_called_scheduled_bid_offer_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int662_v1_provisional_deviation_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int663_v1_provisional_variation_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int664_v1_daily_provisional_mos_allocation_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int665_v1_mos_stack_data_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int666_v1_market_notice_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int667_v1_market_parameters_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int668_v1_schedule_log_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/sttm/int669_v1_settlement_version_rpt_1.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/jobs/download_vicgas_public_report_zip_files.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/assets.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/current_state.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/df_from_s3_keys/source_tables.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/assets.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/models.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/ops/dynamic_nemweb_links_fetcher.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/ops/nemweb_link_fetcher.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/ops/nemweb_link_processor.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/nemweb_public_files/ops/processed_link_combiner.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/archive_replay.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/e2e_archive_seed.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_factories_nemweb.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_raw_modules.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_download_vicgas_public_report_zip_files.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_maintenance_e2e_archive_seed.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_dim_location.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_fact_scada_pressure.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/gas_model/silver_gas_dim_date.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/checks.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_sensors.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_gas_model_silver_gas_dim_location.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_gas_model_silver_gas_future_facts.py`
  - `backend-services/dagster-user/aemo-etl/tests/component/test_defs_gas_model_silver_gas_operations_facts.py`
  - `backend-services/dagster-user/aemo-etl/tests/unit/test_cli_e2e_archive_seed.py`
  - `backend-services/dagster-user/aemo-etl/tests/unit/test_cli_replay_bronze_archive.py`
  - `backend-services/dagster-user/aemo-etl/tests/unit/test_maintenance_archive_replay.py`
  - `backend-services/dagster-user/aemo-etl/tests/unit/test_maintenance_e2e_archive_seed.py`
  - `backend-services/dagster-user/aemo-etl/tests/unit/test_utils.py`
  - `docs/agents/ralph-loop.md`
  - `docs/adr/0001-ralph-local-integration.md`
  - `docs/adr/0002-ralph-delivery-modes.md`
  - `docs/adr/0004-ralph-sandboxed-issue-access.md`
  - `infrastructure/aws-pulumi/README.md`
  - `infrastructure/aws-pulumi/__main__.py`
  - `infrastructure/aws-pulumi/components/ecs_services.py`
  - `infrastructure/aws-pulumi/components/iam_roles.py`
  - `infrastructure/aws-pulumi/docs/runtime.md`
  - `infrastructure/aws-pulumi/tests/component/test_deprecation_warnings.py`
  - `infrastructure/aws-pulumi/tests/component/test_ecs_services.py`
  - `scripts/ralph.py`
  - `tests/test_ralph.py`
- `sync.scope`: `temporary architecture exploration`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `prek run -a`
  - `verify #87 consumption and deletion note remains visible`
