"""Table discovery helpers for the Marimo table explorer."""

from collections.abc import Hashable, Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from html import escape
from io import BytesIO
import os
import posixpath
from typing import Protocol, runtime_checkable
from urllib.parse import urlparse

import boto3
import polars as pl

from marimoserver.dagster_graphql import (
    DEFAULT_DAGSTER_GRAPHQL_URL,
    DagsterAssetCatalogue,
    DagsterTableAsset,
    GraphQLExecutorProtocol,
    fetch_dagster_asset_catalogue,
)
from marimoserver.gas_model_loader import (
    bounded_row_limit,
    compact_error,
)

DEFAULT_LOCAL_BUCKETS: tuple[str, ...] = (
    "dev-energy-market-aemo",
    "dev-energy-market-landing",
    "dev-energy-market-archive",
    "dev-energy-market-io-manager",
)
DEFAULT_BUCKET_PREFIX = "dev-energy-market-"
DEFAULT_AWS_ENDPOINT_URL = "http://localstack:4566"
DEFAULT_AWS_REGION = "ap-southeast-4"
DEFAULT_AWS_ACCESS_KEY_ID = "test"
DEFAULT_AWS_SECRET_ACCESS_KEY = "test"
DEFAULT_AWS_ALLOW_HTTP = "true"
DEFAULT_DISCOVERY_OBJECT_LIMIT = 10_000
DEFAULT_AWS_PREVIEW_ROWS = 100
DEFAULT_LOCAL_PREVIEW_ROWS = 10_000
DEFAULT_PREVIEW_ROWS = 25
DEFAULT_ROW_LIMIT = 25
AWS_DEVELOPMENT_LOCATION = "aws"


@runtime_checkable
class S3Body(Protocol):
    """Readable body returned by the subset of boto3 S3 used here."""

    def read(self) -> bytes:
        """Read object bytes."""
        ...


class S3Paginator(Protocol):
    """Paginator protocol for S3 list_objects_v2."""

    def paginate(self, *, Bucket: str) -> Iterable[Mapping[str, object]]:
        """Yield S3 list pages for a bucket."""
        ...


class S3Client(Protocol):
    """Small boto3 S3 client surface used by the local explorer."""

    def list_buckets(self) -> Mapping[str, object]:
        """Return S3 bucket metadata."""
        ...

    def get_paginator(self, operation_name: str) -> S3Paginator:
        """Return a paginator for an S3 operation."""
        ...

    def get_object(self, *, Bucket: str, Key: str) -> Mapping[str, object]:
        """Return an S3 object body."""
        ...


class TableFormat(StrEnum):
    """Supported table-like storage formats."""

    DELTA = "Delta"
    PARQUET = "Parquet"


class TableAvailability(StrEnum):
    """Joined catalogue and local storage state for one table row."""

    LIVE = "Live"
    UNMATERIALIZED = "Unmaterialized"
    MISSING = "Missing"
    GRAPHQL_UNAVAILABLE = "GraphQL unavailable"


class BucketHealthState(StrEnum):
    """Operator-facing S3-compatible bucket health state."""

    REACHABLE = "Reachable"
    EMPTY = "Empty"
    TRUNCATED = "Truncated"
    MISSING = "Missing"
    UNAVAILABLE = "Unavailable"


class AssetCatalogueState(StrEnum):
    """Operator-facing Dagster asset catalogue dashboard state."""

    READY = "Ready"
    ATTENTION = "Needs attention"
    EMPTY = "Empty"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True)
class TableExplorerConfig:
    """Environment-derived settings for table exploration."""

    runtime_location: str
    default_buckets: tuple[str, ...]
    bucket_prefix: str
    aws_endpoint_url: str | None
    aws_region: str
    aws_access_key_id: str | None
    aws_secret_access_key: str | None
    aws_allow_http: str
    dagster_graphql_url: str
    max_preview_rows: int
    full_table_scan_enabled: bool

    @property
    def aws_runtime(self) -> bool:
        """Return whether the explorer is running in AWS deployment mode."""
        return self.runtime_location == AWS_DEVELOPMENT_LOCATION

    def s3_client_kwargs(self) -> dict[str, str]:
        """Return boto3 S3 client keyword arguments."""
        kwargs = {"region_name": self.aws_region}
        if self.aws_endpoint_url is not None:
            kwargs["endpoint_url"] = self.aws_endpoint_url
        if self.aws_access_key_id is not None:
            kwargs["aws_access_key_id"] = self.aws_access_key_id
        if self.aws_secret_access_key is not None:
            kwargs["aws_secret_access_key"] = self.aws_secret_access_key
        return kwargs

    def delta_storage_options(self) -> dict[str, str]:
        """Return Delta Lake storage options for the configured S3 endpoint."""
        options = {
            "AWS_REGION": self.aws_region,
            "AWS_ALLOW_HTTP": self.aws_allow_http,
            "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
        }
        if self.aws_endpoint_url is not None:
            options["AWS_ENDPOINT_URL"] = self.aws_endpoint_url
        if self.aws_access_key_id is not None:
            options["AWS_ACCESS_KEY_ID"] = self.aws_access_key_id
        if self.aws_secret_access_key is not None:
            options["AWS_SECRET_ACCESS_KEY"] = self.aws_secret_access_key
        return options


@dataclass(frozen=True)
class TableExplorerDeepLink:
    """Table explorer query-parameter defaults from dashboard links."""

    search: str
    table_entry_id: str | None
    asset_entry_id: str | None

    @property
    def requested_entry_id(self) -> str | None:
        """Return the exact table catalogue entry requested by the URL."""
        if self.table_entry_id is not None:
            return self.table_entry_id
        return self.asset_entry_id


@dataclass(frozen=True)
class BucketStatus:
    """Local bucket health and table-discovery summary."""

    name: str
    is_default: bool
    discovered: bool
    reachable: bool
    object_count: int
    table_count: int
    truncated: bool
    error: str | None


@dataclass(frozen=True)
class BucketHealthSummary:
    """Aggregate storage-health summary for the S3 bucket health dashboard."""

    runtime_location: str
    configured_bucket_count: int
    checked_bucket_count: int
    reachable_bucket_count: int
    populated_bucket_count: int
    empty_bucket_count: int
    truncated_bucket_count: int
    missing_bucket_count: int
    unavailable_bucket_count: int
    object_count: int
    table_prefix_count: int
    delta_table_prefix_count: int
    parquet_table_prefix_count: int
    discovery_object_limit: int
    bucket_listing_error: str | None

    @property
    def degraded_bucket_count(self) -> int:
        """Return the number of bucket rows needing operator attention."""
        return (
            self.empty_bucket_count
            + self.truncated_bucket_count
            + self.missing_bucket_count
            + self.unavailable_bucket_count
        )

    @property
    def aws_runtime(self) -> bool:
        """Return whether the summary came from AWS deployment mode."""
        return self.runtime_location == AWS_DEVELOPMENT_LOCATION


@dataclass(frozen=True)
class AssetCatalogueSummary:
    """Aggregate Dagster GraphQL and table asset coverage for a dashboard."""

    url: str
    graphql_available: bool
    graphql_error: str | None
    table_asset_count: int
    overlaid_table_count: int
    local_table_prefix_count: int
    live_count: int
    unmaterialized_count: int
    missing_count: int
    graphql_unavailable_count: int
    materialized_asset_count: int
    materializable_asset_count: int
    executable_asset_count: int
    uri_asset_count: int
    schema_asset_count: int
    latest_materialization_timestamp: float | None

    @property
    def degraded_table_count(self) -> int:
        """Return overlaid table rows needing operator attention."""
        return (
            self.unmaterialized_count
            + self.missing_count
            + self.graphql_unavailable_count
        )

    @property
    def latest_materialization_label(self) -> str:
        """Return a readable latest materialization timestamp."""
        return format_materialization_timestamp(self.latest_materialization_timestamp)


@dataclass(frozen=True)
class AssetCatalogueStatusCard:
    """One first-viewport status card for the asset catalogue dashboard."""

    area: str
    state: AssetCatalogueState
    value: str
    detail: str
    action: str


@dataclass(frozen=True)
class TablePrefix:
    """A discovered table-like S3 prefix."""

    bucket: str
    prefix: str
    table_format: TableFormat
    parquet_files: tuple[str, ...]

    @property
    def table_id(self) -> str:
        """Return a stable selector id for this table prefix."""
        return f"{self.bucket}/{self.prefix}"

    @property
    def uri(self) -> str:
        """Return an S3 URI for this table prefix."""
        if self.prefix == "":
            return f"s3://{self.bucket}"
        return f"s3://{self.bucket}/{self.prefix}"

    @property
    def display_name(self) -> str:
        """Return a readable table label."""
        if self.prefix == "":
            return f"{self.bucket}/"
        return self.table_id


@dataclass(frozen=True)
class StorageDiscovery:
    """Bucket health and discovered table prefixes."""

    buckets: tuple[BucketStatus, ...]
    tables: tuple[TablePrefix, ...]
    bucket_listing_error: str | None


@dataclass(frozen=True)
class CataloguedTable:
    """One table row after overlaying Dagster GraphQL and local storage."""

    entry_id: str
    status: TableAvailability
    asset: DagsterTableAsset | None
    table: TablePrefix | None

    @property
    def display_name(self) -> str:
        """Return the best readable label for this table row."""
        if self.asset is not None:
            return self.asset.asset_id
        if self.table is not None:
            return self.table.display_name
        return self.entry_id

    @property
    def uri(self) -> str | None:
        """Return the Dagster URI or local storage URI for this row."""
        if self.asset is not None and self.asset.uri is not None:
            return self.asset.uri
        if self.table is not None:
            return self.table.uri
        return None


@dataclass(frozen=True)
class ColumnSchema:
    """One loaded table column and its dtype."""

    name: str
    dtype: str


@dataclass(frozen=True)
class TableInspection:
    """Loaded schema, row count, and preview for one table."""

    table: TablePrefix
    schema: tuple[ColumnSchema, ...]
    row_count: int
    preview: pl.DataFrame
    is_limited: bool
    error: str | None

    @property
    def available(self) -> bool:
        """Return whether the inspection loaded successfully."""
        return self.error is None


@dataclass(frozen=True)
class TableScan:
    """A loaded table scan cached for a notebook session."""

    table: TablePrefix
    dataframe: pl.DataFrame
    is_limited: bool
    row_limit: int | None
    error: str | None

    @property
    def available(self) -> bool:
        """Return whether the table loaded successfully."""
        return self.error is None


@dataclass(frozen=True)
class TableQuery:
    """In-memory exploration controls for a loaded table."""

    row_limit: int = DEFAULT_ROW_LIMIT
    columns: tuple[str, ...] = ()
    sort_column: str | None = None
    sort_descending: bool = False
    text_search: str = ""


@dataclass(frozen=True)
class ColumnStatistic:
    """Selected-column statistics computed from an exact table scan."""

    column: str
    null_count: int
    distinct_count: int


@dataclass(frozen=True)
class TableExploration:
    """Preview and selected-column statistics for a loaded table."""

    table: TablePrefix
    schema: tuple[ColumnSchema, ...]
    row_count: int
    filtered_row_count: int
    preview: pl.DataFrame
    column_statistics: tuple[ColumnStatistic, ...]
    is_limited: bool
    error: str | None

    @property
    def available(self) -> bool:
        """Return whether the exploration loaded successfully."""
        return self.error is None


@dataclass
class _TableFacts:
    parquet_files: list[str]
    has_delta_log: bool = False


TableScanCacheKey = tuple[
    str,
    str,
    str,
    tuple[str, ...],
    tuple[tuple[str, str], ...],
    Hashable,
]


def discover_table_explorer_config(
    environ: Mapping[str, str] | None = None,
) -> TableExplorerConfig:
    """Discover table explorer settings from the Marimo service environment."""
    settings = os.environ if environ is None else environ
    runtime_location = _setting(settings, "DEVELOPMENT_LOCATION", "local").lower()
    aws_runtime = runtime_location == AWS_DEVELOPMENT_LOCATION
    default_buckets = (
        _configured_bucket_names(settings, "MARIMO_TABLE_BUCKETS")
        if aws_runtime
        else DEFAULT_LOCAL_BUCKETS
    )
    if aws_runtime and not default_buckets:
        default_buckets = _aws_curated_bucket_names(settings)

    return TableExplorerConfig(
        runtime_location=runtime_location,
        default_buckets=default_buckets,
        bucket_prefix=DEFAULT_BUCKET_PREFIX,
        aws_endpoint_url=_optional_setting(
            settings,
            "AWS_ENDPOINT_URL",
            None if aws_runtime else DEFAULT_AWS_ENDPOINT_URL,
        ),
        aws_region=_setting(settings, "AWS_DEFAULT_REGION", DEFAULT_AWS_REGION),
        aws_access_key_id=_optional_setting(
            settings,
            "AWS_ACCESS_KEY_ID",
            None if aws_runtime else DEFAULT_AWS_ACCESS_KEY_ID,
        ),
        aws_secret_access_key=_optional_setting(
            settings,
            "AWS_SECRET_ACCESS_KEY",
            None if aws_runtime else DEFAULT_AWS_SECRET_ACCESS_KEY,
        ),
        aws_allow_http=_setting(
            settings,
            "AWS_ALLOW_HTTP",
            "false" if aws_runtime else DEFAULT_AWS_ALLOW_HTTP,
        ),
        dagster_graphql_url=_setting(
            settings,
            "DAGSTER_GRAPHQL_URL",
            DEFAULT_DAGSTER_GRAPHQL_URL,
        ),
        max_preview_rows=_positive_int_setting(
            settings,
            "MARIMO_MAX_PREVIEW_ROWS",
            DEFAULT_AWS_PREVIEW_ROWS if aws_runtime else DEFAULT_LOCAL_PREVIEW_ROWS,
        ),
        full_table_scan_enabled=_bool_setting(
            settings,
            "MARIMO_FULL_TABLE_SCAN_ENABLED",
            not aws_runtime,
        ),
    )


def create_s3_client(config: TableExplorerConfig) -> S3Client:
    """Create a boto3 S3 client using compose-local AWS settings."""
    client: S3Client = boto3.client(  # type: ignore[no-untyped-call]
        "s3",
        **config.s3_client_kwargs(),
    )
    return client


def discover_storage(
    config: TableExplorerConfig,
    s3_client: S3Client | None = None,
    object_limit_per_bucket: int = DEFAULT_DISCOVERY_OBJECT_LIMIT,
) -> StorageDiscovery:
    """Discover default and local dev buckets plus table-like prefixes."""
    client = create_s3_client(config) if s3_client is None else s3_client
    if config.aws_runtime:
        discovered_bucket_names: set[str] = set()
        bucket_listing_error = None
    else:
        discovered_bucket_names, bucket_listing_error = _discover_bucket_names(
            client,
            config.bucket_prefix,
        )
    bucket_names = _ordered_bucket_names(
        config.default_buckets, discovered_bucket_names
    )
    buckets: list[BucketStatus] = []
    tables: list[TablePrefix] = []

    for bucket_name in bucket_names:
        keys, truncated, error = _list_bucket_keys(
            client,
            bucket_name,
            object_limit_per_bucket,
        )
        bucket_tables = classify_table_prefixes(bucket_name, keys)
        tables.extend(bucket_tables)
        buckets.append(
            BucketStatus(
                name=bucket_name,
                is_default=bucket_name in config.default_buckets,
                discovered=bucket_name in discovered_bucket_names,
                reachable=error is None,
                object_count=len(keys),
                table_count=len(bucket_tables),
                truncated=truncated,
                error=error,
            )
        )

    return StorageDiscovery(
        buckets=tuple(buckets),
        tables=tuple(sorted(tables, key=lambda table: table.table_id)),
        bucket_listing_error=bucket_listing_error,
    )


def bucket_health_state(bucket: BucketStatus) -> BucketHealthState:
    """Return the operator-facing health state for one configured bucket."""
    if bucket.error is not None:
        if _bucket_error_is_missing(bucket.error):
            return BucketHealthState.MISSING
        return BucketHealthState.UNAVAILABLE
    if bucket.truncated:
        return BucketHealthState.TRUNCATED
    if bucket.object_count == 0:
        return BucketHealthState.EMPTY
    return BucketHealthState.REACHABLE


def build_bucket_health_summary(
    config: TableExplorerConfig,
    discovery: StorageDiscovery,
    object_limit_per_bucket: int = DEFAULT_DISCOVERY_OBJECT_LIMIT,
) -> BucketHealthSummary:
    """Build aggregate storage-health metrics for the dashboard first viewport."""
    states = [bucket_health_state(bucket) for bucket in discovery.buckets]
    table_format_counts = _table_format_counts(discovery.tables)

    return BucketHealthSummary(
        runtime_location=config.runtime_location,
        configured_bucket_count=len(config.default_buckets),
        checked_bucket_count=len(discovery.buckets),
        reachable_bucket_count=sum(
            1 for bucket in discovery.buckets if bucket.reachable
        ),
        populated_bucket_count=sum(
            1
            for bucket in discovery.buckets
            if bucket.reachable and bucket.object_count > 0
        ),
        empty_bucket_count=states.count(BucketHealthState.EMPTY),
        truncated_bucket_count=states.count(BucketHealthState.TRUNCATED),
        missing_bucket_count=states.count(BucketHealthState.MISSING),
        unavailable_bucket_count=states.count(BucketHealthState.UNAVAILABLE),
        object_count=sum(bucket.object_count for bucket in discovery.buckets),
        table_prefix_count=len(discovery.tables),
        delta_table_prefix_count=table_format_counts[TableFormat.DELTA],
        parquet_table_prefix_count=table_format_counts[TableFormat.PARQUET],
        discovery_object_limit=object_limit_per_bucket,
        bucket_listing_error=discovery.bucket_listing_error,
    )


def s3_bucket_health_frame(discovery: StorageDiscovery) -> pl.DataFrame:
    """Return bucket health rows for configured bucket operations."""
    format_counts_by_bucket = _table_format_counts_by_bucket(discovery.tables)
    rows: list[dict[str, object]] = []

    for bucket in discovery.buckets:
        state = bucket_health_state(bucket)
        format_counts = format_counts_by_bucket.get(bucket.name, {})
        rows.append(
            {
                "bucket": bucket.name,
                "configured": bucket.is_default,
                "discovered locally": bucket.discovered,
                "status": state.value,
                "objects scanned": bucket.object_count,
                "table prefixes": bucket.table_count,
                "Delta prefixes": format_counts.get(TableFormat.DELTA, 0),
                "Parquet prefixes": format_counts.get(TableFormat.PARQUET, 0),
                "truncated": bucket.truncated,
                "detail": bucket.error or _bucket_detail(bucket),
                "action": _bucket_health_action(state),
            }
        )

    if rows:
        return pl.DataFrame(rows)

    return pl.DataFrame(
        [
            {
                "bucket": "No configured buckets",
                "configured": False,
                "discovered locally": False,
                "status": BucketHealthState.EMPTY.value,
                "objects scanned": 0,
                "table prefixes": 0,
                "Delta prefixes": 0,
                "Parquet prefixes": 0,
                "truncated": False,
                "detail": discovery.bucket_listing_error or "",
                "action": (
                    "Configure MARIMO_TABLE_BUCKETS or the default bucket "
                    "environment, then refresh storage health."
                ),
            }
        ]
    )


def table_prefix_discovery_frame(
    tables: Sequence[TablePrefix],
) -> pl.DataFrame:
    """Return discovered Delta and Parquet table-like prefixes."""
    rows = [
        {
            "bucket": table.bucket,
            "prefix": table.prefix or "(bucket root)",
            "format": table.table_format.value,
            "parquet files": len(table.parquet_files),
            "uri": table.uri,
        }
        for table in tables
    ]
    if rows:
        return pl.DataFrame(rows)

    return pl.DataFrame(
        [
            {
                "bucket": "No table prefixes discovered",
                "prefix": "",
                "format": "",
                "parquet files": 0,
                "uri": "",
            }
        ]
    )


def filter_table_prefixes(
    tables: Sequence[TablePrefix],
    *,
    buckets: Sequence[str] = (),
    formats: Sequence[str | TableFormat] = (),
    search: str = "",
) -> tuple[TablePrefix, ...]:
    """Filter discovered table prefixes for notebook controls."""
    bucket_filters = {bucket.strip().lower() for bucket in buckets if bucket.strip()}
    format_filters = {
        _table_format_filter_value(table_format).lower()
        for table_format in formats
        if _table_format_filter_value(table_format) != ""
    }
    search_term = search.strip().lower()
    filtered: list[TablePrefix] = []

    for table in tables:
        if bucket_filters and table.bucket.lower() not in bucket_filters:
            continue
        if format_filters and table.table_format.value.lower() not in format_filters:
            continue
        if search_term and search_term not in _table_prefix_search_text(table):
            continue
        filtered.append(table)

    return tuple(filtered)


def storage_health_action_markdown(summary: BucketHealthSummary) -> str:
    """Return Markdown action guidance for degraded storage-health states."""
    actions: list[str] = []

    if summary.bucket_listing_error is not None:
        actions.append(
            "Bucket listing: local bucket enumeration failed; configured "
            "bucket checks still ran where possible."
        )
    if summary.missing_bucket_count > 0:
        actions.append(
            "Missing buckets: provision the configured bucket or correct the "
            "bucket environment value."
        )
    if summary.unavailable_bucket_count > 0:
        actions.append(
            "Unavailable buckets: check S3 endpoint reachability, credentials, "
            "IAM permission, and bucket policy."
        )
    if summary.truncated_bucket_count > 0:
        actions.append(
            "Truncated buckets: object and table-prefix counts are capped by "
            f"the `{summary.discovery_object_limit}` object discovery limit."
        )
    if summary.empty_bucket_count > 0:
        actions.append(
            "Empty buckets: seed LocalStack or materialize data before expecting "
            "table prefixes."
        )
    if not actions and summary.table_prefix_count == 0:
        actions.append(
            "No table prefixes were discovered. Confirm data has been "
            "materialized under Delta or Parquet table-like paths."
        )

    if not actions:
        return "All checked buckets are reachable under the current configuration."
    return "\n".join(f"- {action}" for action in actions)


def render_storage_health_cards(summary: BucketHealthSummary) -> str:
    """Render first-viewport storage-health KPI cards using repo theme tokens."""
    listing_policy = (
        "AWS mode checks configured buckets only; it does not list the account."
        if summary.aws_runtime
        else "Local mode checks configured buckets and discovers matching local buckets."
    )
    error_count = summary.missing_bucket_count + summary.unavailable_bucket_count
    cards = (
        _render_storage_health_card(
            "Bucket reachability",
            _summary_reachability_state(summary),
            f"{summary.reachable_bucket_count}/{summary.checked_bucket_count}",
            (f"{summary.configured_bucket_count} configured buckets. {listing_policy}"),
        ),
        _render_storage_health_card(
            "Objects scanned",
            _summary_object_state(summary),
            _format_int(summary.object_count),
            (
                f"{summary.populated_bucket_count} populated, "
                f"{summary.empty_bucket_count} empty, "
                f"{summary.truncated_bucket_count} truncated."
            ),
        ),
        _render_storage_health_card(
            "Table prefixes",
            _summary_table_state(summary),
            _format_int(summary.table_prefix_count),
            (
                f"{summary.delta_table_prefix_count} Delta and "
                f"{summary.parquet_table_prefix_count} Parquet prefixes."
            ),
        ),
        _render_storage_health_card(
            "Bucket errors",
            _summary_error_state(summary),
            _format_int(error_count),
            (
                f"{summary.missing_bucket_count} missing, "
                f"{summary.unavailable_bucket_count} unavailable."
            ),
        ),
    )
    rendered_cards = "\n".join(cards)
    return f"""\
<style>
{_storage_health_cards_css()}
</style>
<section class="storage-health-card-grid" aria-label="S3 bucket health summary">
{rendered_cards}
</section>"""


def build_asset_catalogue_summary(
    catalogue: DagsterAssetCatalogue,
    table_catalogue: Sequence[CataloguedTable],
) -> AssetCatalogueSummary:
    """Build aggregate GraphQL and table-coverage metrics for the dashboard."""
    status_counts = _catalogued_status_counts(table_catalogue)
    timestamps = [
        asset.latest_materialization_timestamp
        for asset in catalogue.assets
        if asset.latest_materialization_timestamp is not None
    ]

    return AssetCatalogueSummary(
        url=catalogue.url,
        graphql_available=catalogue.available,
        graphql_error=catalogue.error,
        table_asset_count=len(catalogue.assets),
        overlaid_table_count=len(table_catalogue),
        local_table_prefix_count=sum(
            table.table is not None for table in table_catalogue
        ),
        live_count=status_counts[TableAvailability.LIVE],
        unmaterialized_count=status_counts[TableAvailability.UNMATERIALIZED],
        missing_count=status_counts[TableAvailability.MISSING],
        graphql_unavailable_count=status_counts[TableAvailability.GRAPHQL_UNAVAILABLE],
        materialized_asset_count=sum(
            asset.latest_materialization_timestamp is not None
            for asset in catalogue.assets
        ),
        materializable_asset_count=sum(
            asset.is_materializable for asset in catalogue.assets
        ),
        executable_asset_count=sum(asset.is_executable for asset in catalogue.assets),
        uri_asset_count=sum(asset.uri is not None for asset in catalogue.assets),
        schema_asset_count=sum(bool(asset.columns) for asset in catalogue.assets),
        latest_materialization_timestamp=max(timestamps) if timestamps else None,
    )


def asset_catalogue_status_cards(
    summary: AssetCatalogueSummary,
) -> tuple[AssetCatalogueStatusCard, ...]:
    """Return first-viewport Dagster catalogue status cards."""
    return (
        _graphql_status_card(summary),
        _table_coverage_card(summary),
        _asset_metadata_card(summary),
        _latest_materialization_card(summary),
    )


def asset_catalogue_action_markdown(summary: AssetCatalogueSummary) -> str:
    """Return Markdown action guidance for catalogue dashboard degraded states."""
    actions: list[str] = []

    if not summary.graphql_available:
        actions.append(
            "Dagster GraphQL: confirm `DAGSTER_GRAPHQL_URL`, Dagster webserver "
            "health, and reverse-proxy path. Storage-only table rows remain usable."
        )
    elif summary.table_asset_count == 0:
        actions.append(
            "Dagster GraphQL: no table assets were returned. Confirm Dagster "
            "definitions expose table metadata."
        )

    if summary.missing_count > 0:
        actions.append(
            "Missing tables: check `dagster/uri` values and expected S3 table prefixes."
        )
    if summary.unmaterialized_count > 0:
        actions.append(
            "Unmaterialized assets: materialize or backfill the listed assets "
            "before treating their storage as ready."
        )
    if (
        summary.graphql_available
        and summary.table_asset_count > 0
        and summary.schema_asset_count < summary.table_asset_count
    ):
        actions.append(
            "Schema metadata: review assets without column schema metadata if "
            "operators need table-level lineage or validation detail."
        )

    if not actions:
        return "Dagster GraphQL and table asset coverage are usable under the current configuration."
    return "\n".join(f"- {action}" for action in actions)


def render_asset_catalogue_status_cards(
    summary: AssetCatalogueSummary,
) -> str:
    """Render first-viewport Dagster catalogue status cards."""
    cards = asset_catalogue_status_cards(summary)
    rendered_cards = "\n".join(_render_asset_catalogue_card(card) for card in cards)
    return f"""\
<style>
{_asset_catalogue_cards_css()}
</style>
<section class="asset-catalogue-card-grid" aria-label="Dagster asset catalogue summary">
{rendered_cards}
</section>"""


def table_asset_catalogue_frame(
    table_catalogue: Sequence[CataloguedTable],
) -> pl.DataFrame:
    """Return overlaid Dagster asset and storage status rows."""
    rows: list[dict[str, object]] = []
    for entry in table_catalogue:
        asset = entry.asset
        table = entry.table
        rows.append(
            {
                "asset key": "" if asset is None else asset.asset_id,
                "group": catalogued_table_group(entry),
                "kinds": "" if asset is None else ", ".join(asset.kinds),
                "status": entry.status.value,
                "materializable": ""
                if asset is None
                else _yes_no(asset.is_materializable),
                "executable": "" if asset is None else _yes_no(asset.is_executable),
                "latest materialization": ""
                if asset is None
                else format_materialization_timestamp(
                    asset.latest_materialization_timestamp
                ),
                "uri": entry.uri or "",
                "schema available": ""
                if asset is None
                else _yes_no(bool(asset.columns)),
                "schema columns": 0 if asset is None else len(asset.columns),
                "local storage": "" if table is None else "Available",
                "bucket": "" if table is None else table.bucket,
                "prefix": "" if table is None else table.prefix or "(bucket root)",
                "format": "" if table is None else table.table_format.value,
            }
        )

    if rows:
        return pl.DataFrame(rows)

    return pl.DataFrame(
        [
            {
                "asset key": "No table assets or storage prefixes discovered",
                "group": "",
                "kinds": "",
                "status": AssetCatalogueState.EMPTY.value,
                "materializable": "",
                "executable": "",
                "latest materialization": "",
                "uri": "",
                "schema available": "",
                "schema columns": 0,
                "local storage": "",
                "bucket": "",
                "prefix": "",
                "format": "",
            }
        ]
    )


def asset_schema_metadata_frame(
    table_catalogue: Sequence[CataloguedTable],
) -> pl.DataFrame:
    """Return parsed Dagster table asset schema metadata rows."""
    rows: list[dict[str, object]] = []
    for entry in table_catalogue:
        asset = entry.asset
        if asset is None:
            continue
        for column in asset.columns:
            rows.append(
                {
                    "asset key": asset.asset_id,
                    "group": catalogued_table_group(entry),
                    "column": column.name,
                    "type": column.dtype,
                    "description": column.description or "",
                }
            )

    if rows:
        return pl.DataFrame(rows)

    return pl.DataFrame(
        [
            {
                "asset key": "No schema metadata available",
                "group": "",
                "column": "",
                "type": "",
                "description": (
                    "Dagster GraphQL returned no parsed column schema metadata "
                    "for the current table asset filter."
                ),
            }
        ]
    )


def discover_table_catalogue(
    config: TableExplorerConfig,
    client: GraphQLExecutorProtocol | None = None,
) -> DagsterAssetCatalogue:
    """Discover table assets from the configured Dagster GraphQL endpoint."""
    return fetch_dagster_asset_catalogue(
        config.dagster_graphql_url,
        client=client,
    )


def overlay_table_catalogue(
    discovery: StorageDiscovery,
    catalogue: DagsterAssetCatalogue,
) -> tuple[CataloguedTable, ...]:
    """Overlay Dagster catalogue assets with local storage table status."""
    local_tables_by_location = {
        location: table
        for table in discovery.tables
        if (location := _s3_table_location(table.uri)) is not None
    }
    matched_table_ids: set[str] = set()
    entries: list[CataloguedTable] = []

    if not catalogue.available:
        entries.extend(
            CataloguedTable(
                entry_id=f"storage:{table.table_id}",
                status=TableAvailability.GRAPHQL_UNAVAILABLE,
                asset=None,
                table=table,
            )
            for table in discovery.tables
        )
        return tuple(sorted(entries, key=lambda entry: entry.display_name))

    for asset in catalogue.assets:
        table = None
        if asset.uri is not None:
            location = _s3_table_location(asset.uri)
            if location is not None:
                table = local_tables_by_location.get(location)
        if table is not None:
            matched_table_ids.add(table.table_id)
        entries.append(
            CataloguedTable(
                entry_id=f"asset:{asset.asset_id}",
                status=_catalogue_asset_status(asset, table),
                asset=asset,
                table=table,
            )
        )

    entries.extend(
        CataloguedTable(
            entry_id=f"storage:{table.table_id}",
            status=TableAvailability.LIVE,
            asset=None,
            table=table,
        )
        for table in discovery.tables
        if table.table_id not in matched_table_ids
    )
    return tuple(sorted(entries, key=lambda entry: entry.display_name))


def classify_table_prefixes(
    bucket: str, keys: Sequence[str]
) -> tuple[TablePrefix, ...]:
    """Classify table-like S3 prefixes from object keys."""
    delta_roots = {
        delta_root for key in keys if (delta_root := _delta_root(key)) is not None
    }
    facts: dict[str, _TableFacts] = {
        delta_root: _TableFacts(parquet_files=[], has_delta_log=True)
        for delta_root in delta_roots
    }

    for key in keys:
        if not key.lower().endswith(".parquet"):
            continue

        delta_root = _matching_delta_root(key, delta_roots)
        if delta_root is not None:
            facts[delta_root].parquet_files.append(key)
            continue

        parquet_root = _parquet_root(key)
        if parquet_root not in facts:
            facts[parquet_root] = _TableFacts(parquet_files=[])
        facts[parquet_root].parquet_files.append(key)

    tables = [
        TablePrefix(
            bucket=bucket,
            prefix=prefix,
            table_format=TableFormat.DELTA
            if table_facts.has_delta_log
            else TableFormat.PARQUET,
            parquet_files=tuple(sorted(table_facts.parquet_files)),
        )
        for prefix, table_facts in facts.items()
        if table_facts.has_delta_log or table_facts.parquet_files
    ]
    return tuple(sorted(tables, key=lambda table: table.table_id))


def read_delta_table(
    table: TablePrefix,
    config: TableExplorerConfig,
    row_limit: int | None = None,
) -> pl.DataFrame:
    """Read a Delta table into a Polars DataFrame."""
    storage_options = config.delta_storage_options()
    if row_limit is None:
        return pl.read_delta(table.uri, storage_options=storage_options)
    return (
        pl.scan_delta(table.uri, storage_options=storage_options)
        .head(row_limit)
        .collect()
    )


def read_parquet_table(
    table: TablePrefix,
    s3_client: S3Client,
    row_limit: int | None = None,
) -> pl.DataFrame:
    """Read discovered parquet files into a Polars DataFrame."""
    dataframes: list[pl.DataFrame] = []
    remaining_rows = row_limit
    for key in table.parquet_files:
        response = s3_client.get_object(Bucket=table.bucket, Key=key)
        body = response["Body"]
        if not isinstance(body, S3Body):
            raise TypeError("S3 response Body must provide read()")
        dataframe = pl.read_parquet(BytesIO(body.read()), n_rows=remaining_rows)
        dataframes.append(dataframe)
        if remaining_rows is not None:
            remaining_rows -= dataframe.height
            if remaining_rows <= 0:
                break

    if not dataframes:
        return pl.DataFrame()
    return pl.concat(dataframes, how="diagonal_relaxed")


def inspect_table(
    table: TablePrefix,
    config: TableExplorerConfig,
    s3_client: S3Client | None = None,
    preview_rows: int = DEFAULT_PREVIEW_ROWS,
) -> TableInspection:
    """Load schema, exact row count, and preview rows for a discovered table."""
    scan = load_table_dataframe(table, config, s3_client=s3_client)
    if scan.error is not None:
        return TableInspection(
            table=table,
            schema=(),
            row_count=0,
            preview=pl.DataFrame(),
            is_limited=False,
            error=scan.error,
        )

    dataframe = scan.dataframe
    return TableInspection(
        table=table,
        schema=_schema_from_dataframe(dataframe),
        row_count=dataframe.height,
        preview=dataframe.head(preview_rows),
        is_limited=scan.is_limited,
        error=None,
    )


def load_table_dataframe(
    table: TablePrefix,
    config: TableExplorerConfig,
    s3_client: S3Client | None = None,
) -> TableScan:
    """Load a table DataFrame for notebook-session caching."""
    row_limit = bounded_row_limit(config)
    try:
        if table.table_format is TableFormat.DELTA:
            dataframe = read_delta_table(table, config, row_limit=row_limit)
        else:
            client = create_s3_client(config) if s3_client is None else s3_client
            dataframe = read_parquet_table(table, client, row_limit=row_limit)
    except Exception as error:
        return TableScan(
            table=table,
            dataframe=pl.DataFrame(),
            is_limited=False,
            row_limit=None,
            error=_compact_error(error),
        )

    return TableScan(
        table=table,
        dataframe=dataframe,
        is_limited=row_limit is not None,
        row_limit=row_limit,
        error=None,
    )


def cached_table_scan(
    table: TablePrefix,
    config: TableExplorerConfig,
    cache: MutableMapping[TableScanCacheKey, TableScan],
    *,
    s3_client: S3Client | None = None,
    refresh_token: Hashable = 0,
) -> TableScan:
    """Return a cached full table scan for one notebook session."""
    cache_key = _table_scan_cache_key(table, config, refresh_token)
    if cache_key not in cache:
        cache[cache_key] = load_table_dataframe(table, config, s3_client=s3_client)
    return cache[cache_key]


def explore_table_scan(scan: TableScan, query: TableQuery) -> TableExploration:
    """Apply row, column, sort, and text-search controls to a cached table scan."""
    if scan.error is not None:
        return TableExploration(
            table=scan.table,
            schema=(),
            row_count=0,
            filtered_row_count=0,
            preview=pl.DataFrame(),
            column_statistics=(),
            is_limited=scan.is_limited,
            error=scan.error,
        )

    dataframe = scan.dataframe
    selected_columns = _selected_columns(dataframe, query.columns)
    filtered = (
        dataframe
        if scan.is_limited
        else _filter_text(dataframe, selected_columns, query.text_search)
    )
    if not scan.is_limited and query.sort_column in dataframe.columns:
        filtered = filtered.sort(
            query.sort_column,
            descending=query.sort_descending,
            nulls_last=True,
        )

    preview_columns = selected_columns or tuple(dataframe.columns)
    return TableExploration(
        table=scan.table,
        schema=_schema_from_dataframe(dataframe),
        row_count=dataframe.height,
        filtered_row_count=filtered.height,
        preview=filtered.select(preview_columns).head(_normalized_row_limit(query)),
        column_statistics=()
        if scan.is_limited
        else _column_statistics(dataframe, preview_columns),
        is_limited=scan.is_limited,
        error=None,
    )


def filter_catalogued_tables(
    tables: Sequence[CataloguedTable],
    *,
    groups: Sequence[str] = (),
    layers_or_domains: Sequence[str] = (),
    statuses: Sequence[str | TableAvailability] = (),
    search: str = "",
) -> tuple[CataloguedTable, ...]:
    """Filter overlaid table catalogue rows for notebook controls."""
    group_filters = {group.strip().lower() for group in groups if group.strip()}
    layer_filters = {
        layer_or_domain.strip().lower()
        for layer_or_domain in layers_or_domains
        if layer_or_domain.strip()
    }
    status_filters = {
        _status_filter_value(status).lower()
        for status in statuses
        if _status_filter_value(status) != ""
    }
    search_term = search.strip().lower()
    filtered: list[CataloguedTable] = []

    for table in tables:
        if group_filters and catalogued_table_group(table).lower() not in group_filters:
            continue
        table_layers = {
            layer_or_domain.lower()
            for layer_or_domain in catalogued_table_layers_or_domains(table)
        }
        if layer_filters and table_layers.isdisjoint(layer_filters):
            continue
        if status_filters and table.status.value.lower() not in status_filters:
            continue
        if search_term and search_term not in _catalogued_table_search_text(table):
            continue
        filtered.append(table)

    return tuple(filtered)


def table_explorer_deep_link_from_query(
    query_params: Mapping[str, object],
) -> TableExplorerDeepLink:
    """Return table explorer defaults from URL query parameters."""
    return TableExplorerDeepLink(
        search=_query_param_text(query_params.get("search")),
        table_entry_id=_query_param_entry_id(query_params.get("table")),
        asset_entry_id=_query_param_entry_id(query_params.get("asset")),
    )


def include_deep_linked_catalogued_table(
    tables: Sequence[CataloguedTable],
    filtered_tables: Sequence[CataloguedTable],
    requested_entry_id: str | None,
) -> tuple[CataloguedTable, ...]:
    """Include an exact deep-linked catalogue row in the filtered table list."""
    filtered = tuple(filtered_tables)
    if requested_entry_id is None:
        return filtered
    if catalogued_table_by_id(filtered, requested_entry_id) is not None:
        return filtered

    requested_table = catalogued_table_by_id(tables, requested_entry_id)
    if requested_table is None:
        return filtered
    return (requested_table, *filtered)


def default_catalogued_table_entry_id(
    tables: Sequence[CataloguedTable],
    requested_entry_id: str | None,
) -> str | None:
    """Return the table picker default entry ID for filtered catalogue rows."""
    if not tables:
        return None
    if (
        requested_entry_id is not None
        and catalogued_table_by_id(tables, requested_entry_id) is not None
    ):
        return requested_entry_id
    return tables[0].entry_id


def catalogued_table_group(table: CataloguedTable) -> str:
    """Return the asset group filter value for an overlaid table row."""
    if table.asset is None:
        return "Storage only"
    return table.asset.group_name or "(no group)"


def catalogued_table_layers_or_domains(table: CataloguedTable) -> tuple[str, ...]:
    """Return layer and domain filter values for an overlaid table row."""
    if table.table is not None:
        parts = _path_parts(table.table.prefix)
    elif table.uri is not None and (location := _s3_table_location(table.uri)):
        parts = _path_parts(location[1])
    elif table.asset is not None:
        parts = table.asset.asset_key
    else:
        parts = ()

    values = list(parts[:2])
    if not values and table.table is not None:
        values.append(table.table.bucket)
    return tuple(dict.fromkeys(value for value in values if value))


def table_by_id(
    tables: Sequence[TablePrefix],
    table_id: str | None,
) -> TablePrefix | None:
    """Return a discovered table by selector id."""
    if table_id is None:
        return None
    for table in tables:
        if table.table_id == table_id:
            return table
    return None


def catalogued_table_by_id(
    tables: Sequence[CataloguedTable],
    entry_id: str | None,
) -> CataloguedTable | None:
    """Return an overlaid table row by selector id."""
    if entry_id is None:
        return None
    for table in tables:
        if table.entry_id == entry_id:
            return table
    return None


def format_materialization_timestamp(timestamp: float | None) -> str:
    """Return a readable UTC timestamp for Dagster materialization time."""
    if timestamp is None:
        return ""
    return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()


def _bucket_error_is_missing(error: str) -> bool:
    normalized = error.casefold()
    return (
        "nosuchbucket" in normalized
        or "not found" in normalized
        or "notfound" in normalized
        or "404" in normalized
    )


def _bucket_detail(bucket: BucketStatus) -> str:
    if bucket.truncated:
        return "Object listing reached the per-bucket discovery cap."
    if bucket.reachable and bucket.object_count == 0:
        return "Bucket is reachable but contains no listed objects."
    if bucket.reachable:
        return "Bucket is reachable."
    return ""


def _bucket_health_action(state: BucketHealthState) -> str:
    if state is BucketHealthState.REACHABLE:
        return "No action."
    if state is BucketHealthState.EMPTY:
        return "Seed LocalStack or materialize data before expecting table prefixes."
    if state is BucketHealthState.TRUNCATED:
        return "Review with the discovery cap in mind before trusting counts."
    if state is BucketHealthState.MISSING:
        return "Provision the bucket or correct the configured bucket name."
    return "Check endpoint reachability, credentials, IAM permission, and policy."


def _table_format_counts(
    tables: Sequence[TablePrefix],
) -> dict[TableFormat, int]:
    counts = {table_format: 0 for table_format in TableFormat}
    for table in tables:
        counts[table.table_format] += 1
    return counts


def _table_format_counts_by_bucket(
    tables: Sequence[TablePrefix],
) -> dict[str, dict[TableFormat, int]]:
    counts_by_bucket: dict[str, dict[TableFormat, int]] = {}
    for table in tables:
        if table.bucket not in counts_by_bucket:
            counts_by_bucket[table.bucket] = {
                table_format: 0 for table_format in TableFormat
            }
        counts_by_bucket[table.bucket][table.table_format] += 1
    return counts_by_bucket


def _table_format_filter_value(table_format: str | TableFormat) -> str:
    if isinstance(table_format, TableFormat):
        return table_format.value
    return table_format.strip()


def _table_prefix_search_text(table: TablePrefix) -> str:
    return " ".join(
        [
            table.bucket,
            table.prefix,
            table.table_format.value,
            table.uri,
            " ".join(table.parquet_files),
        ]
    ).lower()


def _summary_reachability_state(
    summary: BucketHealthSummary,
) -> BucketHealthState:
    if summary.checked_bucket_count == 0:
        return BucketHealthState.EMPTY
    if summary.reachable_bucket_count == 0:
        return BucketHealthState.UNAVAILABLE
    if summary.truncated_bucket_count > 0:
        return BucketHealthState.TRUNCATED
    if summary.missing_bucket_count > 0 or summary.unavailable_bucket_count > 0:
        return BucketHealthState.UNAVAILABLE
    if summary.empty_bucket_count == summary.checked_bucket_count:
        return BucketHealthState.EMPTY
    return BucketHealthState.REACHABLE


def _summary_object_state(summary: BucketHealthSummary) -> BucketHealthState:
    if summary.truncated_bucket_count > 0:
        return BucketHealthState.TRUNCATED
    if summary.object_count == 0:
        return BucketHealthState.EMPTY
    return BucketHealthState.REACHABLE


def _summary_table_state(summary: BucketHealthSummary) -> BucketHealthState:
    if summary.truncated_bucket_count > 0:
        return BucketHealthState.TRUNCATED
    if summary.table_prefix_count == 0:
        return BucketHealthState.EMPTY
    return BucketHealthState.REACHABLE


def _summary_error_state(summary: BucketHealthSummary) -> BucketHealthState:
    if summary.missing_bucket_count > 0:
        return BucketHealthState.MISSING
    if summary.unavailable_bucket_count > 0 or summary.bucket_listing_error:
        return BucketHealthState.UNAVAILABLE
    return BucketHealthState.REACHABLE


def _render_storage_health_card(
    label: str,
    state: BucketHealthState,
    value: str,
    detail: str,
) -> str:
    state_class = _bucket_state_css_class(state)
    return f"""\
    <article class="storage-health-card storage-health-card--{state_class}">
        <div class="storage-health-card__topline">
            <span>{escape(label)}</span>
            <strong>{escape(state.value)}</strong>
        </div>
        <p class="storage-health-card__value">{escape(value)}</p>
        <p>{escape(detail)}</p>
    </article>"""


def _bucket_state_css_class(state: BucketHealthState) -> str:
    return state.value.lower().replace(" ", "-")


def _format_int(value: int) -> str:
    return f"{value:,}"


def _storage_health_cards_css() -> str:
    return """\
.storage-health-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr));
    gap: 0.9rem;
}

.storage-health-card {
    display: grid;
    gap: 0.55rem;
    min-width: 0;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-left-width: 5px;
    border-radius: 8px;
    padding: 0.9rem;
    background: var(--emdl-panel, #ffffff);
    color: var(--emdl-ink, #1b2324);
}

.storage-health-card--reachable {
    border-left-color: var(--emdl-green, #3e7a54);
}

.storage-health-card--empty,
.storage-health-card--truncated {
    border-left-color: var(--emdl-amber, #b2682a);
}

.storage-health-card--missing,
.storage-health-card--unavailable {
    border-left-color: var(--emdl-red, #9e4839);
}

.storage-health-card__topline {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.45rem;
    color: var(--emdl-muted, #566365);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
}

.storage-health-card__topline strong {
    color: var(--emdl-slate, #354348);
}

.storage-health-card__value {
    margin: 0;
    color: var(--emdl-slate, #354348);
    font-size: 1.45rem;
    font-weight: 760;
    line-height: 1.1;
}

.storage-health-card p {
    margin: 0;
}"""


def _graphql_status_card(summary: AssetCatalogueSummary) -> AssetCatalogueStatusCard:
    if not summary.graphql_available:
        return AssetCatalogueStatusCard(
            area="Dagster GraphQL",
            state=AssetCatalogueState.UNAVAILABLE,
            value="Unavailable",
            detail=summary.graphql_error or "Dagster GraphQL returned no detail.",
            action="Restore GraphQL to classify storage prefixes against assets.",
        )

    if summary.table_asset_count == 0:
        return AssetCatalogueStatusCard(
            area="Dagster GraphQL",
            state=AssetCatalogueState.EMPTY,
            value="No table assets",
            detail=f"GraphQL responded at {summary.url}, but no table assets matched.",
            action="Confirm Dagster definitions expose table metadata.",
        )

    return AssetCatalogueStatusCard(
        area="Dagster GraphQL",
        state=AssetCatalogueState.READY,
        value=f"{_format_int(summary.table_asset_count)} assets",
        detail=f"GraphQL responded at {summary.url}.",
        action="No action.",
    )


def _table_coverage_card(summary: AssetCatalogueSummary) -> AssetCatalogueStatusCard:
    detail = (
        f"{summary.live_count} live, "
        f"{summary.unmaterialized_count} unmaterialized, "
        f"{summary.missing_count} missing, "
        f"{summary.graphql_unavailable_count} storage-only while GraphQL is unavailable."
    )

    if summary.overlaid_table_count == 0:
        return AssetCatalogueStatusCard(
            area="Table coverage",
            state=AssetCatalogueState.EMPTY,
            value="No rows",
            detail="No Dagster table assets or local table prefixes were discovered.",
            action="Materialize assets or seed table prefixes, then refresh.",
        )

    if summary.graphql_unavailable_count > 0:
        return AssetCatalogueStatusCard(
            area="Table coverage",
            state=AssetCatalogueState.ATTENTION,
            value=f"{_format_int(summary.local_table_prefix_count)} storage rows",
            detail=detail,
            action="Use storage-only rows, then restore GraphQL for asset classification.",
        )

    if summary.live_count == 0 or summary.degraded_table_count > 0:
        return AssetCatalogueStatusCard(
            area="Table coverage",
            state=AssetCatalogueState.ATTENTION,
            value=f"{summary.live_count}/{summary.overlaid_table_count} live",
            detail=detail,
            action="Review missing or unmaterialized table rows.",
        )

    return AssetCatalogueStatusCard(
        area="Table coverage",
        state=AssetCatalogueState.READY,
        value=f"{summary.live_count}/{summary.overlaid_table_count} live",
        detail=detail,
        action="No action.",
    )


def _asset_metadata_card(summary: AssetCatalogueSummary) -> AssetCatalogueStatusCard:
    if not summary.graphql_available:
        return AssetCatalogueStatusCard(
            area="Asset metadata",
            state=AssetCatalogueState.UNAVAILABLE,
            value="GraphQL unavailable",
            detail="Group, kinds, URI, executable flags, and schema metadata are unavailable.",
            action="Restore GraphQL to inspect Dagster asset metadata.",
        )

    if summary.table_asset_count == 0:
        return AssetCatalogueStatusCard(
            area="Asset metadata",
            state=AssetCatalogueState.EMPTY,
            value="No metadata",
            detail="No table assets were returned for metadata summarization.",
            action="Confirm table assets are present in Dagster.",
        )

    state = (
        AssetCatalogueState.READY
        if summary.schema_asset_count > 0 and summary.uri_asset_count > 0
        else AssetCatalogueState.ATTENTION
    )
    return AssetCatalogueStatusCard(
        area="Asset metadata",
        state=state,
        value=f"{summary.schema_asset_count}/{summary.table_asset_count} schemas",
        detail=(
            f"{summary.uri_asset_count} with URI, "
            f"{summary.materializable_asset_count} materializable, "
            f"{summary.executable_asset_count} executable."
        ),
        action="No action."
        if state is AssetCatalogueState.READY
        else "Review assets missing URI or schema metadata.",
    )


def _latest_materialization_card(
    summary: AssetCatalogueSummary,
) -> AssetCatalogueStatusCard:
    if not summary.graphql_available:
        return AssetCatalogueStatusCard(
            area="Latest materialization",
            state=AssetCatalogueState.UNAVAILABLE,
            value="Unknown",
            detail="GraphQL is unavailable, so materialization metadata cannot be read.",
            action="Restore GraphQL to inspect materialization freshness.",
        )

    if summary.table_asset_count == 0:
        return AssetCatalogueStatusCard(
            area="Latest materialization",
            state=AssetCatalogueState.EMPTY,
            value="No assets",
            detail="No table assets were returned.",
            action="Confirm table assets are present in Dagster.",
        )

    if summary.latest_materialization_timestamp is None:
        return AssetCatalogueStatusCard(
            area="Latest materialization",
            state=AssetCatalogueState.ATTENTION,
            value="No materializations",
            detail="GraphQL returned table assets without materialization timestamps.",
            action="Materialize the expected table assets.",
        )

    return AssetCatalogueStatusCard(
        area="Latest materialization",
        state=AssetCatalogueState.READY,
        value=summary.latest_materialization_label,
        detail=f"{summary.materialized_asset_count}/{summary.table_asset_count} assets have materialization metadata.",
        action="No action.",
    )


def _render_asset_catalogue_card(card: AssetCatalogueStatusCard) -> str:
    state_class = _asset_catalogue_state_css_class(card.state)
    return f"""\
    <article class="asset-catalogue-card asset-catalogue-card--{state_class}">
        <div class="asset-catalogue-card__topline">
            <span>{escape(card.area)}</span>
            <strong>{escape(card.state.value)}</strong>
        </div>
        <p class="asset-catalogue-card__value">{escape(card.value)}</p>
        <p>{escape(card.detail)}</p>
        <p class="asset-catalogue-card__action">{escape(card.action)}</p>
    </article>"""


def _asset_catalogue_state_css_class(state: AssetCatalogueState) -> str:
    return state.value.lower().replace(" ", "-")


def _asset_catalogue_cards_css() -> str:
    return """\
.asset-catalogue-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 14rem), 1fr));
    gap: 0.9rem;
}

.asset-catalogue-card {
    display: grid;
    gap: 0.55rem;
    min-width: 0;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-left-width: 5px;
    border-radius: 8px;
    padding: 0.9rem;
    background: var(--emdl-panel, #ffffff);
    color: var(--emdl-ink, #1b2324);
}

.asset-catalogue-card--ready {
    border-left-color: var(--emdl-green, #3e7a54);
}

.asset-catalogue-card--needs-attention,
.asset-catalogue-card--empty {
    border-left-color: var(--emdl-amber, #b2682a);
}

.asset-catalogue-card--unavailable {
    border-left-color: var(--emdl-red, #9e4839);
}

.asset-catalogue-card__topline {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 0.45rem;
    color: var(--emdl-muted, #566365);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
}

.asset-catalogue-card__topline strong {
    color: var(--emdl-slate, #354348);
}

.asset-catalogue-card__value {
    margin: 0;
    color: var(--emdl-slate, #354348);
    font-size: 1.45rem;
    font-weight: 760;
    line-height: 1.1;
}

.asset-catalogue-card p {
    margin: 0;
}

.asset-catalogue-card__action {
    color: var(--emdl-muted, #566365);
    font-size: 0.9rem;
}"""


def _catalogued_status_counts(
    table_catalogue: Sequence[CataloguedTable],
) -> dict[TableAvailability, int]:
    counts = {status: 0 for status in TableAvailability}
    for table in table_catalogue:
        counts[table.status] += 1
    return counts


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def _discover_bucket_names(
    s3_client: S3Client,
    bucket_prefix: str,
) -> tuple[set[str], str | None]:
    try:
        response = s3_client.list_buckets()
    except Exception as error:
        return set(), _compact_error(error)

    bucket_values = response.get("Buckets", ())
    buckets = bucket_values if isinstance(bucket_values, Sequence) else ()
    discovered = {
        name
        for bucket in buckets
        if isinstance(bucket, Mapping)
        and isinstance(name := bucket.get("Name"), str)
        and name.startswith(bucket_prefix)
    }
    return discovered, None


def _catalogue_asset_status(
    asset: DagsterTableAsset,
    table: TablePrefix | None,
) -> TableAvailability:
    if table is not None:
        return TableAvailability.LIVE
    if asset.latest_materialization_timestamp is None:
        return TableAvailability.UNMATERIALIZED
    return TableAvailability.MISSING


def _s3_table_location(uri: str) -> tuple[str, str] | None:
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or parsed.netloc == "":
        return None
    return parsed.netloc, parsed.path.removeprefix("/").rstrip("/")


def _ordered_bucket_names(
    default_buckets: Sequence[str],
    discovered_bucket_names: set[str],
) -> tuple[str, ...]:
    ordered = list(default_buckets)
    ordered.extend(
        bucket
        for bucket in sorted(discovered_bucket_names)
        if bucket not in default_buckets
    )
    return tuple(ordered)


def _list_bucket_keys(
    s3_client: S3Client,
    bucket: str,
    object_limit: int,
) -> tuple[tuple[str, ...], bool, str | None]:
    keys: list[str] = []
    truncated = False
    try:
        paginator = s3_client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket):
            contents = page.get("Contents", [])
            if not isinstance(contents, Sequence):
                continue
            for item in contents:
                if not isinstance(item, Mapping):
                    continue
                key = item.get("Key")
                if not isinstance(key, str):
                    continue
                if len(keys) >= object_limit:
                    truncated = True
                    break
                keys.append(key)
            if truncated:
                break
    except Exception as error:
        return tuple(keys), truncated, _compact_error(error)

    return tuple(keys), truncated, None


def _delta_root(key: str) -> str | None:
    parts = key.split("/")
    if "_delta_log" not in parts:
        return None
    return "/".join(parts[: parts.index("_delta_log")])


def _matching_delta_root(key: str, delta_roots: set[str]) -> str | None:
    matches = [
        delta_root
        for delta_root in delta_roots
        if delta_root == "" or key.startswith(f"{delta_root}/")
    ]
    if not matches:
        return None
    return max(matches, key=len)


def _parquet_root(key: str) -> str:
    root = posixpath.dirname(key)
    while _last_path_part(root).find("=") > 0:
        root = posixpath.dirname(root)
    return root


def _last_path_part(path: str) -> str:
    if path == "":
        return ""
    return path.rsplit("/", maxsplit=1)[-1]


def _path_parts(path: str) -> tuple[str, ...]:
    return tuple(part for part in path.split("/") if part)


def _schema_from_dataframe(dataframe: pl.DataFrame) -> tuple[ColumnSchema, ...]:
    return tuple(
        ColumnSchema(name=name, dtype=str(dtype))
        for name, dtype in dataframe.schema.items()
    )


def _table_scan_cache_key(
    table: TablePrefix,
    config: TableExplorerConfig,
    refresh_token: Hashable,
) -> TableScanCacheKey:
    config_values = {
        "DEVELOPMENT_LOCATION": config.runtime_location,
        "AWS_ENDPOINT_URL": config.aws_endpoint_url,
        "AWS_REGION": config.aws_region,
        "AWS_ACCESS_KEY_ID": config.aws_access_key_id,
        "AWS_SECRET_ACCESS_KEY": config.aws_secret_access_key,
        "AWS_ALLOW_HTTP": config.aws_allow_http,
        "MARIMO_MAX_PREVIEW_ROWS": str(config.max_preview_rows),
        "MARIMO_FULL_TABLE_SCAN_ENABLED": str(config.full_table_scan_enabled),
    }
    config_fingerprint = tuple(
        sorted(
            (key, "" if value is None else str(value))
            for key, value in config_values.items()
        )
    )
    return (
        table.table_id,
        table.uri,
        table.table_format.value,
        table.parquet_files,
        config_fingerprint,
        refresh_token,
    )


def _selected_columns(
    dataframe: pl.DataFrame,
    columns: Sequence[str],
) -> tuple[str, ...]:
    available_columns = set(dataframe.columns)
    return tuple(column for column in columns if column in available_columns)


def _filter_text(
    dataframe: pl.DataFrame,
    selected_columns: Sequence[str],
    text_search: str,
) -> pl.DataFrame:
    search_term = text_search.strip().lower()
    if search_term == "" or not dataframe.columns:
        return dataframe

    search_columns = tuple(selected_columns) or tuple(dataframe.columns)
    search_expression = pl.any_horizontal(
        [
            pl.col(column)
            .cast(pl.String)
            .str.to_lowercase()
            .str.contains(search_term, literal=True)
            for column in search_columns
        ]
    ).fill_null(False)
    return dataframe.filter(search_expression)


def _normalized_row_limit(query: TableQuery) -> int:
    return max(1, int(query.row_limit))


def _column_statistics(
    dataframe: pl.DataFrame,
    columns: Sequence[str],
) -> tuple[ColumnStatistic, ...]:
    statistics: list[ColumnStatistic] = []
    for column in columns:
        statistics.append(
            ColumnStatistic(
                column=column,
                null_count=int(dataframe.select(pl.col(column).null_count()).item()),
                distinct_count=int(
                    dataframe.select(pl.col(column).drop_nulls().n_unique()).item()
                ),
            )
        )
    return tuple(statistics)


def _query_param_entry_id(value: object) -> str | None:
    text = _query_param_text(value)
    if text == "":
        return None
    return text


def _query_param_text(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, Sequence) and not isinstance(value, bytes | bytearray):
        for item in value:
            if isinstance(item, str) and item.strip():
                return item.strip()
    return ""


def _status_filter_value(status: str | TableAvailability) -> str:
    if isinstance(status, TableAvailability):
        return status.value
    return status.strip()


def _catalogued_table_search_text(table: CataloguedTable) -> str:
    values = [
        table.display_name,
        table.status.value,
        table.uri or "",
        catalogued_table_group(table),
        " ".join(catalogued_table_layers_or_domains(table)),
    ]
    if table.asset is not None:
        values.extend(
            [
                table.asset.asset_id,
                table.asset.description or "",
                " ".join(table.asset.kinds),
            ]
        )
    if table.table is not None:
        values.extend([table.table.table_id, table.table.uri])
    return " ".join(values).lower()


def _setting(environ: Mapping[str, str], name: str, default: str) -> str:
    value = environ.get(name, default).strip()
    if value == "":
        return default
    return value


def _optional_setting(
    environ: Mapping[str, str],
    name: str,
    default: str | None,
) -> str | None:
    value = environ.get(name)
    if value is None:
        return default
    stripped = value.strip()
    if stripped == "":
        return default
    return stripped


def _configured_bucket_names(
    environ: Mapping[str, str],
    name: str,
) -> tuple[str, ...]:
    raw_value = environ.get(name, "")
    return tuple(
        dict.fromkeys(
            bucket.strip() for bucket in raw_value.split(",") if bucket.strip()
        )
    )


def _aws_curated_bucket_names(environ: Mapping[str, str]) -> tuple[str, ...]:
    buckets = [
        _optional_setting(environ, "AEMO_BUCKET", None),
        _optional_setting(environ, "IO_MANAGER_BUCKET", None),
    ]
    return tuple(bucket for bucket in buckets if bucket is not None)


def _positive_int_setting(
    environ: Mapping[str, str],
    name: str,
    default: int,
) -> int:
    value = environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(1, parsed)


def _bool_setting(environ: Mapping[str, str], name: str, default: bool) -> bool:
    value = environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _compact_error(error: Exception) -> str:
    return compact_error(error)
