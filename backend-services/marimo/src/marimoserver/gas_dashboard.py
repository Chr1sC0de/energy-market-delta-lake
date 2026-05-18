"""Helpers for the gas market overview marimo dashboard."""

from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from html import escape
import os
from time import perf_counter

import polars as pl

from marimoserver.dashboard_registry import (
    DashboardRegistryEntry,
    DashboardRegistryError,
    dashboard_registry,
    registry_entry_by_concept_id,
)
from marimoserver.gas_model_loader import (
    SILVER_GAS_MODEL_PREFIX as SILVER_GAS_MODEL_PREFIX,
    Clock,
    GasModelReadRequest,
    GasModelSessionCache,
    GasModelTableLoad,
    GasModelTableView,
    TableReader,
    cache_status_label,
    cached_gas_model_read_requests,
    format_load_duration,
    format_row_limit,
    load_gas_model_read_requests,
    read_parquet_table as read_parquet_table,
    row_limit_message,
)

DEFAULT_NAME_PREFIX = "energy-market"
DEFAULT_DEVELOPMENT_ENVIRONMENT = "dev"
DEFAULT_AWS_ENDPOINT_URL = "http://localstack:4566"
DEFAULT_AWS_REGION = "ap-southeast-4"
DEFAULT_AWS_ACCESS_KEY_ID = "test"
DEFAULT_AWS_SECRET_ACCESS_KEY = "test"
DEFAULT_AWS_ALLOW_HTTP = "true"
DEFAULT_AWS_PREVIEW_ROWS = 100
AWS_DEVELOPMENT_LOCATION = "aws"
DEFAULT_RELATED_CONTEXT_LIMIT = 6
SYSTEM_NOTICE_TABLE_NAME = "silver_gas_fact_system_notice"
SYSTEM_NOTICE_CRITICAL_FILTER_ALL = "All notices"
SYSTEM_NOTICE_CRITICAL_FILTER_CRITICAL = "Critical only"
SYSTEM_NOTICE_CRITICAL_FILTER_NON_CRITICAL = "Non-critical only"
SYSTEM_NOTICE_CRITICAL_FILTER_OPTIONS = (
    SYSTEM_NOTICE_CRITICAL_FILTER_ALL,
    SYSTEM_NOTICE_CRITICAL_FILTER_CRITICAL,
    SYSTEM_NOTICE_CRITICAL_FILTER_NON_CRITICAL,
)
SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE_RECENT = "Active or recent"
SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE = "Active now"
SYSTEM_NOTICE_WINDOW_FILTER_RECENT = "Recent starts"
SYSTEM_NOTICE_WINDOW_FILTER_ALL = "All loaded notices"
SYSTEM_NOTICE_WINDOW_FILTER_OPTIONS = (
    SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE_RECENT,
    SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE,
    SYSTEM_NOTICE_WINDOW_FILTER_RECENT,
    SYSTEM_NOTICE_WINDOW_FILTER_ALL,
)
DEFAULT_SYSTEM_NOTICE_RECENT_DAYS = 14
DEFAULT_SYSTEM_NOTICE_PREVIEW_ROWS = 50
GAS_QUALITY_TABLE_NAME = "silver_gas_fact_gas_quality"
GAS_QUALITY_QUALITY_TYPE_FILTER_ALL = "All quality types"
GAS_QUALITY_SOURCE_POINT_FILTER_ALL = "All source points"
DEFAULT_GAS_QUALITY_PREVIEW_ROWS = 50


@dataclass(frozen=True)
class GasDashboardConfig:
    """Environment-derived settings used to read gas model Parquet tables."""

    runtime_location: str
    development_environment: str
    name_prefix: str
    aemo_bucket: str
    aws_endpoint_url: str | None
    aws_region: str
    aws_access_key_id: str | None
    aws_secret_access_key: str | None
    aws_allow_http: str
    max_preview_rows: int
    full_table_scan_enabled: bool

    @property
    def aws_runtime(self) -> bool:
        """Return whether the dashboard is running in AWS deployment mode."""
        return self.runtime_location == AWS_DEVELOPMENT_LOCATION

    def table_uri(self, table_name: str) -> str:
        """Return the Parquet dataset URI for a silver gas_model table."""
        return f"s3://{self.aemo_bucket}/{SILVER_GAS_MODEL_PREFIX}/{table_name}"

    def storage_options(self) -> dict[str, str]:
        """Return Polars S3 storage options for the configured endpoint."""
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
class GasTableSpec:
    """A gas_model output table included in the dashboard."""

    section: str
    label: str
    table_name: str
    date_columns: tuple[str, ...] = ()
    preview_columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class GasTableLoad:
    """Loaded DataFrame or professional unavailable-state detail for one table."""

    spec: GasTableSpec
    uri: str
    dataframe: pl.DataFrame | None
    error: str | None
    row_limit: int | None
    load_duration_seconds: float
    cache_hit: bool

    @property
    def available(self) -> bool:
        """Return whether the table loaded and contains at least one row."""
        return self.dataframe is not None and not self.dataframe.is_empty()

    @property
    def is_limited(self) -> bool:
        """Return whether the runtime applied a bounded preview row limit."""
        return self.row_limit is not None


GAS_MODEL_TABLES: tuple[GasTableSpec, ...] = (
    GasTableSpec(
        section="Prices",
        label="Market prices",
        table_name="silver_gas_fact_market_price",
        date_columns=("gas_date",),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_table",
            "price_type",
            "schedule_type_id",
            "source_location_id",
            "price_value_gst_ex",
            "weighted_average_price_gst_ex",
            "cumulative_price",
            "administered_price",
        ),
    ),
    GasTableSpec(
        section="Schedules",
        label="Schedule runs",
        table_name="silver_gas_fact_schedule_run",
        date_columns=("gas_date", "creation_timestamp", "approval_timestamp"),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_table",
            "schedule_type_id",
            "transmission_id",
            "forecast_demand_version",
            "approval_timestamp",
        ),
    ),
    GasTableSpec(
        section="Schedules",
        label="Scheduled quantities",
        table_name="silver_gas_fact_scheduled_quantity",
        date_columns=("gas_date",),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_table",
            "quantity_type",
            "schedule_type_id",
            "source_point_id",
            "quantity_gj",
            "amount_gst_ex",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Connection point flow",
        table_name="silver_gas_fact_connection_point_flow",
        date_columns=("gas_date",),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_facility_id",
            "source_connection_point_id",
            "flow_direction",
            "actual_quantity_tj",
            "quality",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Facility flow and storage",
        table_name="silver_gas_fact_facility_flow_storage",
        date_columns=("gas_date",),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_facility_id",
            "source_location_id",
            "demand_tj",
            "supply_tj",
            "held_in_storage_tj",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Linepack",
        table_name="silver_gas_fact_linepack",
        date_columns=("gas_date", "observation_timestamp"),
        preview_columns=(
            "gas_date",
            "observation_timestamp",
            "source_system",
            "source_table",
            "source_facility_id",
            "actual_linepack_gj",
            "adequacy_flag",
            "adequacy_description",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Capacity outlook",
        table_name="silver_gas_fact_capacity_outlook",
        date_columns=("from_gas_date", "to_gas_date"),
        preview_columns=(
            "from_gas_date",
            "to_gas_date",
            "source_system",
            "source_table",
            "source_facility_id",
            "facility_name",
            "capacity_type",
            "flow_direction",
            "capacity_quantity_tj",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Capacity auction",
        table_name="silver_gas_fact_capacity_auction",
        date_columns=("auction_date", "start_date", "end_date"),
        preview_columns=(
            "auction_date",
            "source_system",
            "source_table",
            "auction_id",
            "zone_name",
            "auction_metric",
            "quantity_gj",
            "price",
        ),
    ),
)

SYSTEM_NOTICE_TABLE_SPEC = GasTableSpec(
    section="System notices",
    label="System notices",
    table_name=SYSTEM_NOTICE_TABLE_NAME,
    date_columns=(
        "notice_start_timestamp",
        "notice_end_timestamp",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
    preview_columns=(
        "source_notice_id",
        "critical_notice",
        "notice_start_timestamp",
        "notice_end_timestamp",
        "system_message",
        "system_email_message",
        "url_path",
        "source_system",
        "source_table",
    ),
)
SYSTEM_NOTICE_TABLE_SPECS = (SYSTEM_NOTICE_TABLE_SPEC,)
GAS_QUALITY_TABLE_SPEC = GasTableSpec(
    section="Quality and composition",
    label="Gas quality and composition",
    table_name=GAS_QUALITY_TABLE_NAME,
    date_columns=(
        "gas_date",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
    preview_columns=(
        "gas_date",
        "gas_interval",
        "source_point_id",
        "point_name",
        "quality_type",
        "unit",
        "quantity",
        "source_system",
        "source_table",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
)
GAS_QUALITY_TABLE_SPECS = (GAS_QUALITY_TABLE_SPEC,)

_SYSTEM_NOTICE_RAW_SCHEMA = {
    "source_notice_id": pl.String,
    "critical_notice": pl.Boolean,
    "notice_start_timestamp": pl.Datetime("us"),
    "notice_end_timestamp": pl.Datetime("us"),
    "system_message": pl.String,
    "system_email_message": pl.String,
    "url_path": pl.String,
    "source_system": pl.String,
    "source_table": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "ingested_timestamp": pl.Datetime("us"),
}
_SYSTEM_NOTICE_SUMMARY_SCHEMA = {
    "notice id": pl.String,
    "critical": pl.Boolean,
    "window": pl.String,
    "start": pl.Datetime("us"),
    "end": pl.Datetime("us"),
    "message": pl.String,
    "email message": pl.String,
    "url": pl.String,
    "source system": pl.String,
    "source table": pl.String,
}
_SYSTEM_NOTICE_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_SYSTEM_NOTICE_SOURCE_COVERAGE_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "notices": pl.UInt32,
    "critical notices": pl.UInt32,
    "active notices": pl.UInt32,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_GAS_QUALITY_RAW_SCHEMA = {
    "source_system": pl.String,
    "source_table": pl.String,
    "gas_date": pl.Date,
    "gas_interval": pl.String,
    "source_point_id": pl.String,
    "point_name": pl.String,
    "quality_type": pl.String,
    "unit": pl.String,
    "quantity": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "ingested_timestamp": pl.Datetime("us"),
}
_GAS_QUALITY_OBSERVATION_SCHEMA = {
    "gas date": pl.Date,
    "gas interval": pl.String,
    "source point": pl.String,
    "point name": pl.String,
    "quality type": pl.String,
    "unit": pl.String,
    "quantity": pl.Float64,
    "source system": pl.String,
    "source table": pl.String,
    "source updated": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_GAS_QUALITY_TYPE_SUMMARY_SCHEMA = {
    "quality type": pl.String,
    "unit": pl.String,
    "observations": pl.UInt32,
    "source points": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "min quantity": pl.Float64,
    "avg quantity": pl.Float64,
    "max quantity": pl.Float64,
}
_GAS_QUALITY_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_GAS_QUALITY_SOURCE_COVERAGE_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "observations": pl.UInt32,
    "quality types": pl.UInt32,
    "units": pl.UInt32,
    "source points": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}


def discover_dashboard_config(
    environ: Mapping[str, str] | None = None,
) -> GasDashboardConfig:
    """Discover dashboard settings from the Marimo service environment."""
    settings = os.environ if environ is None else environ
    runtime_location = _setting(settings, "DEVELOPMENT_LOCATION", "local").lower()
    aws_runtime = runtime_location == AWS_DEVELOPMENT_LOCATION
    name_prefix = _setting(settings, "NAME_PREFIX", DEFAULT_NAME_PREFIX)
    development_environment = _setting(
        settings,
        "DEVELOPMENT_ENVIRONMENT",
        DEFAULT_DEVELOPMENT_ENVIRONMENT,
    ).lower()
    aemo_bucket = _setting(
        settings,
        "AEMO_BUCKET",
        f"{development_environment}-{name_prefix}-aemo",
    )

    return GasDashboardConfig(
        runtime_location=runtime_location,
        development_environment=development_environment,
        name_prefix=name_prefix,
        aemo_bucket=aemo_bucket,
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
        max_preview_rows=_positive_int_setting(
            settings,
            "MARIMO_MAX_PREVIEW_ROWS",
            DEFAULT_AWS_PREVIEW_ROWS,
        ),
        full_table_scan_enabled=_bool_setting(
            settings,
            "MARIMO_FULL_TABLE_SCAN_ENABLED",
            not aws_runtime,
        ),
    )


def load_gas_model_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] = GAS_MODEL_TABLES,
    reader: TableReader = read_parquet_table,
    view: GasModelTableView = GasModelTableView.SAMPLE,
    *,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Load configured gas_model tables, returning unavailable entries on errors."""
    shared_loads = load_gas_model_read_requests(
        config,
        _gas_model_read_requests(specs, view),
        reader=reader,
        clock=clock,
    )
    return _gas_table_loads(specs, shared_loads)


def cached_load_gas_model_tables(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    specs: Sequence[GasTableSpec] = GAS_MODEL_TABLES,
    reader: TableReader = read_parquet_table,
    view: GasModelTableView = GasModelTableView.SAMPLE,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Return session-cached gas_model tables for explicit-refresh dashboards."""
    shared_loads = cached_gas_model_read_requests(
        config,
        _gas_model_read_requests(specs, view),
        cache,
        reader=reader,
        refresh_token=refresh_token,
        clock=clock,
    )
    return _gas_table_loads(specs, shared_loads)


def load_system_notice_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the system notice fact through the shared bounded table loader."""
    return load_gas_model_tables(
        config,
        specs=SYSTEM_NOTICE_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_system_notice_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached system notice data for explicit-refresh dashboards."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=SYSTEM_NOTICE_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )[0]


def load_gas_quality_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the gas quality fact through the shared bounded table loader."""
    return load_gas_model_tables(
        config,
        specs=GAS_QUALITY_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_gas_quality_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached gas quality data for explicit-refresh dashboards."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=GAS_QUALITY_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )[0]


def gas_table_load_status_frame(loads: Sequence[GasTableLoad]) -> pl.DataFrame:
    """Return dashboard table-load status with timing and row-limit detail."""
    return pl.DataFrame(
        [
            {
                "section": load.spec.section,
                "table": load.spec.table_name,
                "label": load.spec.label,
                "status": _table_load_status(load),
                "rows": 0 if load.dataframe is None else load.dataframe.height,
                "row limit": format_row_limit(load.row_limit),
                "load time": format_load_duration(load.load_duration_seconds),
                "cache": cache_status_label(load.cache_hit),
                "detail": load.error or "",
                "uri": load.uri,
            }
            for load in loads
        ]
    )


def gas_table_load_status_message(loads: Sequence[GasTableLoad]) -> str:
    """Return consistent Markdown status copy for dashboard bounded table reads."""
    if len(loads) == 0:
        return "No `silver.gas_model` tables were requested."

    available_count = sum(load.available for load in loads)
    failed_count = sum(load.error is not None for load in loads)
    cache_hit_count = sum(load.cache_hit for load in loads)
    total_duration = sum(load.load_duration_seconds for load in loads)
    row_limit = _common_row_limit(loads)

    return "\n".join(
        (
            f"- Tables available: `{available_count}` of `{len(loads)}`",
            f"- Read policy: {row_limit_message(row_limit)}",
            (
                f"- Load timing: `{format_load_duration(total_duration)}` "
                f"across `{len(loads)}` table reads"
            ),
            (
                f"- Session cache: `{cache_hit_count}` hits; use **Refresh data** "
                "after source tables are materialized or reseeded"
            ),
            f"- Unavailable tables: `{failed_count}`",
        )
    )


def _gas_model_read_requests(
    specs: Sequence[GasTableSpec],
    view: GasModelTableView,
) -> tuple[GasModelReadRequest, ...]:
    return tuple(
        GasModelReadRequest(
            table_name=spec.table_name,
            view=view,
            date_columns=spec.date_columns,
        )
        for spec in specs
    )


def _gas_table_loads(
    specs: Sequence[GasTableSpec],
    shared_loads: Sequence[GasModelTableLoad],
) -> list[GasTableLoad]:
    return [
        GasTableLoad(
            spec=spec,
            uri=shared_load.uri,
            dataframe=shared_load.dataframe,
            error=shared_load.error,
            row_limit=shared_load.row_limit,
            load_duration_seconds=shared_load.load_duration_seconds,
            cache_hit=shared_load.cache_hit,
        )
        for spec, shared_load in zip(specs, shared_loads, strict=True)
    ]


def _table_load_status(load: GasTableLoad) -> str:
    if load.error is not None:
        return "Unavailable"
    if load.available:
        return "Available"
    return "Empty"


def _common_row_limit(loads: Sequence[GasTableLoad]) -> int | None:
    row_limits = {load.row_limit for load in loads}
    if len(row_limits) == 1:
        return next(iter(row_limits))
    return min(row_limit for row_limit in row_limits if row_limit is not None)


def table_load_by_name(
    loads: Sequence[GasTableLoad],
    table_name: str,
) -> GasTableLoad | None:
    """Return a loaded table entry by gas_model table name."""
    for load in loads:
        if load.spec.table_name == table_name:
            return load
    return None


def gas_quality_quality_type_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return quality-type filter options for the loaded gas quality preview."""
    return _gas_quality_string_filter_options(
        load,
        "quality_type",
        GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
    )


def gas_quality_source_point_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-point filter options for the loaded gas quality preview."""
    return _gas_quality_string_filter_options(
        load,
        "source_point_id",
        GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
    )


def gas_quality_observation_frame(
    load: GasTableLoad | None,
    quality_type_filter: str = GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
    source_point_filter: str = GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_GAS_QUALITY_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return filtered gas quality and composition observations for preview."""
    dataframe = _filtered_gas_quality_dataframe(
        load,
        quality_type_filter,
        source_point_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_GAS_QUALITY_OBSERVATION_SCHEMA)

    return (
        dataframe.sort(
            [
                "gas_date",
                "source_last_updated_timestamp",
                "quality_type",
                "source_point_id",
                "gas_interval",
            ],
            descending=[True, True, False, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("gas_date").alias("gas date"),
            pl.col("gas_interval").alias("gas interval"),
            pl.col("source_point_id").alias("source point"),
            pl.col("point_name").alias("point name"),
            pl.col("quality_type").alias("quality type"),
            pl.col("unit"),
            pl.col("quantity"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("source_last_updated_timestamp").alias("source updated"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def gas_quality_type_summary_frame(
    load: GasTableLoad | None,
    quality_type_filter: str = GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
    source_point_filter: str = GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
) -> pl.DataFrame:
    """Return quality-type and unit summary metrics for loaded gas quality rows."""
    dataframe = _filtered_gas_quality_dataframe(
        load,
        quality_type_filter,
        source_point_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_GAS_QUALITY_TYPE_SUMMARY_SCHEMA)

    return (
        dataframe.group_by("quality_type", "unit")
        .agg(
            pl.len().alias("observations"),
            pl.col("source_point_id").drop_nulls().n_unique().alias("source points"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("quantity").min().alias("min quantity"),
            pl.col("quantity").mean().round(4).alias("avg quantity"),
            pl.col("quantity").max().alias("max quantity"),
        )
        .sort(["observations", "quality_type", "unit"], descending=[True, False, False])
        .rename(
            {
                "quality_type": "quality type",
            }
        )
    )


def gas_quality_kpi_frame(
    load: GasTableLoad | None,
    quality_type_filter: str = GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
    source_point_filter: str = GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
) -> pl.DataFrame:
    """Return first-viewport KPIs for loaded gas quality observations."""
    dataframe = _filtered_gas_quality_dataframe(
        load,
        quality_type_filter,
        source_point_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_GAS_QUALITY_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_observations"),
        pl.col("quality_type").drop_nulls().n_unique().alias("quality_types"),
        pl.col("unit").drop_nulls().n_unique().alias("units"),
        pl.col("source_point_id").drop_nulls().n_unique().alias("source_points"),
        pl.col("source_table").drop_nulls().n_unique().alias("source_tables"),
        pl.col("gas_date").max().alias("latest_gas_date"),
    ).row(0, named=True)

    row_limit = None if load is None else load.row_limit
    return pl.DataFrame(
        [
            {
                "metric": "Loaded observations",
                "value": f"{counts['loaded_observations']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Quality types",
                "value": f"{counts['quality_types']:,}",
                "detail": "Distinct quality_type values in the current view",
            },
            {
                "metric": "Units",
                "value": f"{counts['units']:,}",
                "detail": "Distinct unit values in the current view",
            },
            {
                "metric": "Source points",
                "value": f"{counts['source_points']:,}",
                "detail": "Distinct source_point_id values in the current view",
            },
            {
                "metric": "Source tables",
                "value": f"{counts['source_tables']:,}",
                "detail": "Distinct source_table values represented",
            },
            {
                "metric": "Latest gas date",
                "value": _format_optional_value(counts["latest_gas_date"]),
                "detail": "Maximum gas_date in the loaded bounded rows",
            },
        ],
        schema=_GAS_QUALITY_KPI_SCHEMA,
    )


def gas_quality_source_coverage_frame(
    load: GasTableLoad | None,
    quality_type_filter: str = GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
    source_point_filter: str = GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
) -> pl.DataFrame:
    """Return source coverage for loaded gas quality and composition rows."""
    dataframe = _filtered_gas_quality_dataframe(
        load,
        quality_type_filter,
        source_point_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_GAS_QUALITY_SOURCE_COVERAGE_SCHEMA)

    return (
        dataframe.group_by("source_system", "source_table")
        .agg(
            pl.len().alias("observations"),
            pl.col("quality_type").drop_nulls().n_unique().alias("quality types"),
            pl.col("unit").drop_nulls().n_unique().alias("units"),
            pl.col("source_point_id").drop_nulls().n_unique().alias("source points"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(["observations", "source_table"], descending=[True, False])
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
            }
        )
    )


def gas_quality_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched gas quality data."""
    table_label = _markdown_breakable_text(
        "silver.gas_model.silver_gas_fact_gas_quality"
    )
    if load is None:
        status_detail = "The dashboard did not receive a gas quality load result."
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = (
                "The current filters do not match any loaded gas quality rows."
            )
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No gas quality or composition data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    quality type, unit, quantity, gas date, gas interval, source point, and
    source fields.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` gas quality asset, then use
    **Refresh data**.
    """


def system_notice_summary_frame(
    load: GasTableLoad | None,
    critical_filter: str = SYSTEM_NOTICE_CRITICAL_FILTER_ALL,
    window_filter: str = SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE_RECENT,
    *,
    reference_time: datetime | None = None,
    recent_days: int = DEFAULT_SYSTEM_NOTICE_RECENT_DAYS,
    preview_rows: int = DEFAULT_SYSTEM_NOTICE_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return filtered system notice rows for the dashboard detail preview."""
    dataframe = _normalised_system_notice_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SYSTEM_NOTICE_SUMMARY_SCHEMA)

    reference = _system_notice_reference_time(reference_time)
    filtered = _filter_system_notice_dataframe(
        dataframe,
        critical_filter,
        window_filter,
        reference,
        recent_days,
    )
    if filtered.is_empty():
        return pl.DataFrame(schema=_SYSTEM_NOTICE_SUMMARY_SCHEMA)

    return (
        filtered.with_columns(
            _system_notice_window_status_expression(reference).alias("_window_status"),
            pl.col("critical_notice").fill_null(False).alias("_critical_sort"),
            _system_notice_active_expression(reference).alias("_active_sort"),
        )
        .sort(
            [
                "_critical_sort",
                "_active_sort",
                "notice_start_timestamp",
                "notice_end_timestamp",
                "source_notice_id",
            ],
            descending=[True, True, True, True, False],
            nulls_last=True,
        )
        .select(
            pl.col("source_notice_id").alias("notice id"),
            pl.col("critical_notice").fill_null(False).alias("critical"),
            pl.col("_window_status").alias("window"),
            pl.col("notice_start_timestamp").alias("start"),
            pl.col("notice_end_timestamp").alias("end"),
            pl.col("system_message").alias("message"),
            pl.col("system_email_message").alias("email message"),
            pl.col("url_path").alias("url"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
        )
        .head(max(1, preview_rows))
    )


def system_notice_kpi_frame(
    load: GasTableLoad | None,
    *,
    reference_time: datetime | None = None,
    recent_days: int = DEFAULT_SYSTEM_NOTICE_RECENT_DAYS,
) -> pl.DataFrame:
    """Return notice-count KPIs for the first dashboard viewport."""
    dataframe = _normalised_system_notice_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SYSTEM_NOTICE_KPI_SCHEMA)

    reference = _system_notice_reference_time(reference_time)
    recent_threshold = reference - timedelta(days=max(1, recent_days))
    active_expression = _system_notice_active_expression(reference)
    recent_expression = _system_notice_recent_expression(recent_threshold)
    counts = dataframe.select(
        pl.len().alias("loaded_notices"),
        pl.col("critical_notice")
        .fill_null(False)
        .cast(pl.UInt32)
        .sum()
        .alias("critical_notices"),
        active_expression.cast(pl.UInt32).sum().alias("active_notices"),
        recent_expression.cast(pl.UInt32).sum().alias("recent_notices"),
        pl.col("source_table").drop_nulls().n_unique().alias("source_tables"),
    ).row(0, named=True)

    row_limit = None if load is None else load.row_limit
    return pl.DataFrame(
        [
            {
                "metric": "Loaded notices",
                "value": f"{counts['loaded_notices']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Critical notices",
                "value": f"{counts['critical_notices']:,}",
                "detail": "Rows where the critical flag is true",
            },
            {
                "metric": "Active notices",
                "value": f"{counts['active_notices']:,}",
                "detail": f"Active at {_format_reference_time(reference)}",
            },
            {
                "metric": "Recent notices",
                "value": f"{counts['recent_notices']:,}",
                "detail": f"Started or ended in the last {max(1, recent_days)} days",
            },
            {
                "metric": "Source tables",
                "value": f"{counts['source_tables']:,}",
                "detail": "Distinct system notice source tables represented",
            },
        ],
        schema=_SYSTEM_NOTICE_KPI_SCHEMA,
    )


def system_notice_source_coverage_frame(
    load: GasTableLoad | None,
    *,
    reference_time: datetime | None = None,
) -> pl.DataFrame:
    """Return source coverage for loaded system notice rows."""
    dataframe = _normalised_system_notice_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SYSTEM_NOTICE_SOURCE_COVERAGE_SCHEMA)

    reference = _system_notice_reference_time(reference_time)
    return (
        dataframe.with_columns(
            _system_notice_active_expression(reference).alias("_active_notice")
        )
        .group_by("source_system", "source_table")
        .agg(
            pl.len().alias("notices"),
            pl.col("critical_notice")
            .fill_null(False)
            .cast(pl.UInt32)
            .sum()
            .alias("critical notices"),
            pl.col("_active_notice").cast(pl.UInt32).sum().alias("active notices"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(["notices", "source_table"], descending=[True, False])
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
            }
        )
    )


def system_notice_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched notice data."""
    if load is None:
        status_detail = "The dashboard did not receive a system notice load result."
        uri = "`silver.gas_model.silver_gas_fact_system_notice`"
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: `{load.error}`"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = "The current filters do not match any loaded notice rows."
        uri = f"`{load.uri}`"
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No system notice data is available for this view.**

    The dashboard checked {uri}, which should contain
    `silver.gas_model.silver_gas_fact_system_notice` rows with notice IDs,
    critical flags, active windows, messages, and URL paths.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` system notice asset, then use
    **Refresh data**.
    """


def _gas_quality_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_gas_quality_dataframe(load)
    if dataframe.is_empty() or column not in dataframe.columns:
        return (all_label,)

    values = sorted(
        str(value)
        for value in dataframe.get_column(column)
        .drop_nulls()
        .cast(pl.String, strict=False)
        .unique()
        .to_list()
        if value is not None
    )
    return (all_label, *values)


def _filtered_gas_quality_dataframe(
    load: GasTableLoad | None,
    quality_type_filter: str,
    source_point_filter: str,
) -> pl.DataFrame:
    dataframe = _normalised_gas_quality_dataframe(load)
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if quality_type_filter != GAS_QUALITY_QUALITY_TYPE_FILTER_ALL:
        filtered = filtered.filter(pl.col("quality_type") == quality_type_filter)
    if source_point_filter != GAS_QUALITY_SOURCE_POINT_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_point_id") == source_point_filter)
    return filtered


def _normalised_gas_quality_dataframe(load: GasTableLoad | None) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_GAS_QUALITY_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _GAS_QUALITY_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("gas_interval").cast(pl.String, strict=False),
        pl.col("source_point_id").cast(pl.String, strict=False),
        pl.col("point_name").cast(pl.String, strict=False),
        pl.col("quality_type").cast(pl.String, strict=False),
        pl.col("unit").cast(pl.String, strict=False),
        pl.col("quantity").cast(pl.Float64, strict=False),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_system_notice_dataframe(load: GasTableLoad | None) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_SYSTEM_NOTICE_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _SYSTEM_NOTICE_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("source_notice_id").cast(pl.String, strict=False),
        pl.col("critical_notice").cast(pl.Boolean, strict=False),
        _normalise_timestamp_column(dataframe, "notice_start_timestamp"),
        _normalise_timestamp_column(dataframe, "notice_end_timestamp"),
        pl.col("system_message").cast(pl.String, strict=False),
        pl.col("system_email_message").cast(pl.String, strict=False),
        pl.col("url_path").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalise_date_column(dataframe: pl.DataFrame, column: str) -> pl.Expr:
    if dataframe.schema[column] == pl.String:
        return pl.col(column).str.to_date(strict=False).alias(column)
    return pl.col(column).cast(pl.Date, strict=False).alias(column)


def _normalise_timestamp_column(dataframe: pl.DataFrame, column: str) -> pl.Expr:
    if dataframe.schema[column] == pl.String:
        return (
            pl.col(column)
            .str.to_datetime(strict=False)
            .cast(pl.Datetime("us"), strict=False)
            .alias(column)
        )
    return pl.col(column).cast(pl.Datetime("us"), strict=False).alias(column)


def _filter_system_notice_dataframe(
    dataframe: pl.DataFrame,
    critical_filter: str,
    window_filter: str,
    reference_time: datetime,
    recent_days: int,
) -> pl.DataFrame:
    filtered = _filter_system_notice_critical(dataframe, critical_filter)
    recent_threshold = reference_time - timedelta(days=max(1, recent_days))

    if window_filter == SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE:
        return filtered.filter(_system_notice_active_expression(reference_time))
    if window_filter == SYSTEM_NOTICE_WINDOW_FILTER_RECENT:
        return filtered.filter(_system_notice_recent_start_expression(recent_threshold))
    if window_filter == SYSTEM_NOTICE_WINDOW_FILTER_ALL:
        return filtered
    return filtered.filter(
        _system_notice_active_expression(reference_time)
        | _system_notice_recent_expression(recent_threshold)
    )


def _filter_system_notice_critical(
    dataframe: pl.DataFrame,
    critical_filter: str,
) -> pl.DataFrame:
    critical_expression = pl.col("critical_notice").fill_null(False)
    if critical_filter == SYSTEM_NOTICE_CRITICAL_FILTER_CRITICAL:
        return dataframe.filter(critical_expression)
    if critical_filter == SYSTEM_NOTICE_CRITICAL_FILTER_NON_CRITICAL:
        return dataframe.filter(~critical_expression)
    return dataframe


def _system_notice_active_expression(reference_time: datetime) -> pl.Expr:
    reference = pl.lit(reference_time, dtype=pl.Datetime("us"))
    has_window_boundary = (
        pl.col("notice_start_timestamp").is_not_null()
        | pl.col("notice_end_timestamp").is_not_null()
    )
    return (
        has_window_boundary
        & (
            pl.col("notice_start_timestamp").is_null()
            | (pl.col("notice_start_timestamp") <= reference)
        )
        & (
            pl.col("notice_end_timestamp").is_null()
            | (pl.col("notice_end_timestamp") >= reference)
        )
    )


def _system_notice_recent_start_expression(recent_threshold: datetime) -> pl.Expr:
    threshold = pl.lit(recent_threshold, dtype=pl.Datetime("us"))
    return pl.col("notice_start_timestamp").is_not_null() & (
        pl.col("notice_start_timestamp") >= threshold
    )


def _system_notice_recent_expression(recent_threshold: datetime) -> pl.Expr:
    threshold = pl.lit(recent_threshold, dtype=pl.Datetime("us"))
    return (
        pl.col("notice_start_timestamp").is_not_null()
        & (pl.col("notice_start_timestamp") >= threshold)
    ) | (
        pl.col("notice_end_timestamp").is_not_null()
        & (pl.col("notice_end_timestamp") >= threshold)
    )


def _system_notice_window_status_expression(reference_time: datetime) -> pl.Expr:
    reference = pl.lit(reference_time, dtype=pl.Datetime("us"))
    return (
        pl.when(_system_notice_active_expression(reference_time))
        .then(pl.lit("Active"))
        .when(
            pl.col("notice_start_timestamp").is_not_null()
            & (pl.col("notice_start_timestamp") > reference)
        )
        .then(pl.lit("Upcoming"))
        .when(
            pl.col("notice_end_timestamp").is_not_null()
            & (pl.col("notice_end_timestamp") < reference)
        )
        .then(pl.lit("Ended"))
        .otherwise(pl.lit("Window unknown"))
    )


def _system_notice_reference_time(reference_time: datetime | None) -> datetime:
    if reference_time is not None:
        return reference_time.replace(tzinfo=None)
    return datetime.now(UTC).replace(tzinfo=None)


def _format_reference_time(reference_time: datetime) -> str:
    return reference_time.isoformat(sep=" ", timespec="minutes")


def _format_optional_value(value: object | None) -> str:
    if value is None:
        return "unknown"
    return str(value)


def _markdown_breakable_text(value: str) -> str:
    escaped_value = escape(value)
    return f'<span style="overflow-wrap:anywhere;">{escaped_value}</span>'


def render_dashboard_context_panel(
    concept_id: str,
    entries: Sequence[DashboardRegistryEntry] | None = None,
    related_limit: int = DEFAULT_RELATED_CONTEXT_LIMIT,
) -> str:
    """Render a cited Market context panel from the Marimo dashboard registry."""
    candidate_entries = dashboard_registry() if entries is None else entries
    entry = registry_entry_by_concept_id(concept_id, candidate_entries)
    if entry is None:
        raise DashboardRegistryError(
            f"dashboard context panel concept not found: {concept_id}"
        )

    related_entries = _related_context_entries(
        entry,
        candidate_entries,
        related_limit,
    )
    notebook_name = entry.notebook_name or ""
    notebook_route = entry.notebook_route or ""

    return f"""\
<style>
{_dashboard_context_panel_css()}
</style>
<section
    class="dashboard-context-panel"
    aria-labelledby="dashboard-context-title-{escape(entry.concept_id, quote=True)}"
    data-concept-id="{escape(entry.concept_id, quote=True)}"
    data-status="{escape(entry.status.value, quote=True)}"
    data-notebook-name="{escape(notebook_name, quote=True)}"
    data-notebook-route="{escape(notebook_route, quote=True)}"
>
    <div class="context-panel__header">
        <p class="context-panel__eyebrow">Market context</p>
        <h2 id="dashboard-context-title-{escape(entry.concept_id, quote=True)}">
            {escape(entry.title)}
        </h2>
        <p>{escape(entry.description)}</p>
    </div>
    <dl class="context-panel__metadata" aria-label="Dashboard usage metadata">
        {_definition_item("Concept ID", entry.concept_id)}
        {_definition_item("Status", entry.status.value)}
        {_definition_item("Audiences", ", ".join(audience.value for audience in entry.audiences))}
        {_definition_item("Notebook", notebook_name or "No notebook recorded")}
        {_definition_item("Route", notebook_route or "No notebook route recorded")}
    </dl>
    <div class="context-panel__grid">
        {_render_context_list("generated-gold paths", entry.generated_gold_paths)}
        {_render_context_list("source chunk IDs", entry.source_chunk_ids)}
        {_render_context_list("backing assets", entry.backing_assets)}
        {_render_related_context_list(related_entries)}
    </div>
</section>"""


def _related_context_entries(
    entry: DashboardRegistryEntry,
    entries: Sequence[DashboardRegistryEntry],
    limit: int,
) -> tuple[DashboardRegistryEntry, ...]:
    if limit <= 0:
        return ()

    scored_entries: list[tuple[int, str, DashboardRegistryEntry]] = []
    entry_gold_paths = set(entry.generated_gold_paths)
    entry_source_chunks = set(entry.source_chunk_ids)
    entry_assets = set(entry.backing_assets)

    for candidate in entries:
        if candidate.concept_id == entry.concept_id:
            continue

        score = (
            len(entry_gold_paths & set(candidate.generated_gold_paths)) * 3
            + len(entry_assets & set(candidate.backing_assets)) * 2
            + len(entry_source_chunks & set(candidate.source_chunk_ids))
        )
        if score == 0:
            continue
        scored_entries.append((score, candidate.title, candidate))

    return tuple(
        candidate
        for _, _, candidate in sorted(
            scored_entries,
            key=lambda scored_entry: (-scored_entry[0], scored_entry[1]),
        )[:limit]
    )


def _definition_item(label: str, value: str) -> str:
    return f"""\
        <div>
            <dt>{escape(label)}</dt>
            <dd>{escape(value)}</dd>
        </div>"""


def _render_context_list(title: str, values: Sequence[str]) -> str:
    if len(values) == 0:
        body = (
            '<p class="context-panel__empty">'
            f"No {escape(title)} recorded in the Marimo registry."
            "</p>"
        )
    else:
        body = "\n".join(
            f"                <li><code>{escape(value)}</code></li>" for value in values
        )
        body = f"<ul>\n{body}\n            </ul>"

    return f"""\
        <section class="context-panel__section">
            <h3>{escape(title)}</h3>
            {body}
        </section>"""


def _render_related_context_list(
    related_entries: Sequence[DashboardRegistryEntry],
) -> str:
    if len(related_entries) == 0:
        body = (
            '<p class="context-panel__empty">'
            "No related concepts share generated-gold paths, source chunk IDs, "
            "or backing assets in the Marimo registry."
            "</p>"
        )
    else:
        rows = "\n".join(
            f"""\
                <li>
                    <span>{escape(entry.title)}</span>
                    <code>{escape(entry.concept_id)}</code>
                </li>"""
            for entry in related_entries
        )
        body = f"<ul>\n{rows}\n            </ul>"

    return f"""\
        <section class="context-panel__section">
            <h3>related concepts</h3>
            {body}
        </section>"""


def _dashboard_context_panel_css() -> str:
    return """\
.dashboard-context-panel {
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    padding: 1rem;
    background: var(--emdl-panel, #ffffff);
    color: var(--emdl-ink, #1b2324);
}

.context-panel__header {
    display: grid;
    gap: 0.35rem;
    margin-bottom: 0.9rem;
}

.context-panel__eyebrow {
    margin: 0;
    color: var(--emdl-green, #3e7a54);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0;
    text-transform: uppercase;
}

.context-panel__header h2,
.context-panel__section h3 {
    margin: 0;
    color: var(--emdl-slate, #354348);
}

.context-panel__header h2 {
    font-size: 1.25rem;
}

.context-panel__header p,
.context-panel__empty {
    margin: 0;
    color: var(--emdl-muted, #566365);
}

.context-panel__metadata {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
    gap: 0.7rem;
    margin-bottom: 1rem;
}

.context-panel__metadata div {
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 6px;
    padding: 0.55rem 0.65rem;
    background: var(--emdl-service-band, #eef4f1);
}

.context-panel__metadata dt {
    color: var(--emdl-muted, #566365);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
}

.context-panel__metadata dd {
    margin: 0.2rem 0 0;
    overflow-wrap: anywhere;
}

.context-panel__grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
    gap: 0.85rem;
}

.context-panel__section {
    min-width: 0;
}

.context-panel__section h3 {
    margin-bottom: 0.4rem;
    font-size: 0.95rem;
    text-transform: capitalize;
}

.context-panel__section ul {
    display: grid;
    gap: 0.35rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.context-panel__section li {
    display: grid;
    gap: 0.2rem;
    min-width: 0;
    border-left: 3px solid var(--emdl-blue, #166791);
    padding: 0.35rem 0 0.35rem 0.55rem;
    background: rgb(var(--emdl-line-rgb, 207 219 214) / 0.24);
}

.context-panel__section code {
    white-space: normal;
    overflow-wrap: anywhere;
}"""


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
