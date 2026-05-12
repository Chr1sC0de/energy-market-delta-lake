"""LocalStack-backed table discovery helpers for the Marimo table explorer."""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from io import BytesIO
import os
import posixpath
from typing import Protocol, runtime_checkable

import boto3
import polars as pl

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


@dataclass
class _TableFacts:
    parquet_files: list[str]
    has_delta_log: bool = False


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
    try:
        if table.table_format is TableFormat.DELTA:
            dataframe = read_delta_table(table, config)
        else:
            client = create_s3_client(config) if s3_client is None else s3_client
            dataframe = read_parquet_table(table, client)
    except Exception as error:
        return TableInspection(
            table=table,
            schema=(),
            row_count=0,
            preview=pl.DataFrame(),
            error=_compact_error(error),
        )

    return TableInspection(
        table=table,
        schema=_schema_from_dataframe(dataframe),
        row_count=dataframe.height,
        preview=dataframe.head(preview_rows),
        error=None,
    )


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


def _schema_from_dataframe(dataframe: pl.DataFrame) -> tuple[ColumnSchema, ...]:
    return tuple(
        ColumnSchema(name=name, dtype=str(dtype))
        for name, dtype in dataframe.schema.items()
    )


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
