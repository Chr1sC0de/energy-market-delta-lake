"""LocalStack-backed table discovery helpers for the Marimo table explorer."""

from collections.abc import Hashable, Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
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
DEFAULT_PREVIEW_ROWS = 25
DEFAULT_ROW_LIMIT = 25


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


@dataclass(frozen=True)
class TableExplorerConfig:
    """Environment-derived settings for compose-local table exploration."""

    default_buckets: tuple[str, ...]
    bucket_prefix: str
    aws_endpoint_url: str
    aws_region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_allow_http: str
    dagster_graphql_url: str

    def s3_client_kwargs(self) -> dict[str, str]:
        """Return boto3 S3 client keyword arguments."""
        return {
            "endpoint_url": self.aws_endpoint_url,
            "region_name": self.aws_region,
            "aws_access_key_id": self.aws_access_key_id,
            "aws_secret_access_key": self.aws_secret_access_key,
        }

    def delta_storage_options(self) -> dict[str, str]:
        """Return Delta Lake storage options for the configured S3 endpoint."""
        return {
            "AWS_ENDPOINT_URL": self.aws_endpoint_url,
            "AWS_REGION": self.aws_region,
            "AWS_ACCESS_KEY_ID": self.aws_access_key_id,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret_access_key,
            "AWS_ALLOW_HTTP": self.aws_allow_http,
            "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
        }


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
    """Loaded schema, exact row count, and preview for one table."""

    table: TablePrefix
    schema: tuple[ColumnSchema, ...]
    row_count: int
    preview: pl.DataFrame
    error: str | None

    @property
    def available(self) -> bool:
        """Return whether the inspection loaded successfully."""
        return self.error is None


@dataclass(frozen=True)
class TableScan:
    """A full table scan cached for a notebook session."""

    table: TablePrefix
    dataframe: pl.DataFrame
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
    return TableExplorerConfig(
        default_buckets=DEFAULT_LOCAL_BUCKETS,
        bucket_prefix=DEFAULT_BUCKET_PREFIX,
        aws_endpoint_url=_setting(
            settings,
            "AWS_ENDPOINT_URL",
            DEFAULT_AWS_ENDPOINT_URL,
        ),
        aws_region=_setting(settings, "AWS_DEFAULT_REGION", DEFAULT_AWS_REGION),
        aws_access_key_id=_setting(
            settings,
            "AWS_ACCESS_KEY_ID",
            DEFAULT_AWS_ACCESS_KEY_ID,
        ),
        aws_secret_access_key=_setting(
            settings,
            "AWS_SECRET_ACCESS_KEY",
            DEFAULT_AWS_SECRET_ACCESS_KEY,
        ),
        aws_allow_http=_setting(settings, "AWS_ALLOW_HTTP", DEFAULT_AWS_ALLOW_HTTP),
        dagster_graphql_url=_setting(
            settings,
            "DAGSTER_GRAPHQL_URL",
            DEFAULT_DAGSTER_GRAPHQL_URL,
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
) -> pl.DataFrame:
    """Read a Delta table into a Polars DataFrame."""
    return pl.read_delta(table.uri, storage_options=config.delta_storage_options())


def read_parquet_table(
    table: TablePrefix,
    s3_client: S3Client,
) -> pl.DataFrame:
    """Read discovered parquet files into a Polars DataFrame."""
    dataframes: list[pl.DataFrame] = []
    for key in table.parquet_files:
        response = s3_client.get_object(Bucket=table.bucket, Key=key)
        body = response["Body"]
        if not isinstance(body, S3Body):
            raise TypeError("S3 response Body must provide read()")
        dataframes.append(pl.read_parquet(BytesIO(body.read())))

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
            error=scan.error,
        )

    dataframe = scan.dataframe
    return TableInspection(
        table=table,
        schema=_schema_from_dataframe(dataframe),
        row_count=dataframe.height,
        preview=dataframe.head(preview_rows),
        error=None,
    )


def load_table_dataframe(
    table: TablePrefix,
    config: TableExplorerConfig,
    s3_client: S3Client | None = None,
) -> TableScan:
    """Load a full table DataFrame for notebook-session caching."""
    try:
        if table.table_format is TableFormat.DELTA:
            dataframe = read_delta_table(table, config)
        else:
            client = create_s3_client(config) if s3_client is None else s3_client
            dataframe = read_parquet_table(table, client)
    except Exception as error:
        return TableScan(
            table=table,
            dataframe=pl.DataFrame(),
            error=_compact_error(error),
        )

    return TableScan(table=table, dataframe=dataframe, error=None)


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
            error=scan.error,
        )

    dataframe = scan.dataframe
    selected_columns = _selected_columns(dataframe, query.columns)
    filtered = _filter_text(dataframe, selected_columns, query.text_search)
    if query.sort_column in dataframe.columns:
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
        column_statistics=_column_statistics(dataframe, preview_columns),
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
    config_fingerprint = tuple(
        sorted(
            {
                "AWS_ENDPOINT_URL": config.aws_endpoint_url,
                "AWS_REGION": config.aws_region,
                "AWS_ACCESS_KEY_ID": config.aws_access_key_id,
                "AWS_SECRET_ACCESS_KEY": config.aws_secret_access_key,
                "AWS_ALLOW_HTTP": config.aws_allow_http,
            }.items()
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


def _compact_error(error: Exception) -> str:
    message = str(error).strip().splitlines()
    if not message:
        return error.__class__.__name__
    return f"{error.__class__.__name__}: {message[0]}"
