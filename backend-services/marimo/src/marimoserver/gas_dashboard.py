"""Helpers for the gas market overview marimo dashboard."""

from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from html import escape
from math import isnan
import os
from time import perf_counter
from urllib.parse import quote

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
DEFAULT_RELATED_CONTEXT_LIMIT = 9
GAS_DAY_CONTEXT_ID = "gas-day-context"
DEFAULT_GAS_DAY_EXAMPLES_PER_FIELD = 3
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
MARKET_PRICE_TABLE_NAME = "silver_gas_fact_market_price"
MARKET_PRICE_PRICE_TYPE_FILTER_ALL = "All price types"
MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
MARKET_PRICE_SOURCE_TABLE_FILTER_ALL = "All source tables"
DEFAULT_MARKET_PRICE_PREVIEW_ROWS = 50
MARKET_PRICE_MEASURE_COLUMNS = (
    "price_value_gst_ex",
    "weighted_average_price_gst_ex",
    "cumulative_price",
    "administered_price",
)
SCHEDULE_RUN_TABLE_NAME = "silver_gas_fact_schedule_run"
SCHEDULE_RUN_GAS_DATE_FILTER_ALL = "All gas dates"
SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL = "All schedule types"
DEFAULT_SCHEDULE_RUN_PREVIEW_ROWS = 50
SETTLEMENT_ACTIVITY_TABLE_NAME = "silver_gas_fact_settlement_activity"
SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL = "All gas dates"
SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL = "All activity types"
DEFAULT_SETTLEMENT_ACTIVITY_PREVIEW_ROWS = 50
CUSTOMER_TRANSFER_TABLE_NAME = "silver_gas_fact_customer_transfer"
CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL = "All gas dates"
CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL = "All market codes"
CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
DEFAULT_CUSTOMER_TRANSFER_PREVIEW_ROWS = 50
BID_STACK_TABLE_NAME = "silver_gas_fact_bid_stack"
BID_STACK_PARTICIPANT_FILTER_ALL = "All participants"
BID_STACK_FACILITY_FILTER_ALL = "All facilities"
BID_STACK_ZONE_FILTER_ALL = "All zones"
BID_STACK_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
DEFAULT_BID_STACK_PREVIEW_ROWS = 50
GAS_QUALITY_TABLE_NAME = "silver_gas_fact_gas_quality"
GAS_QUALITY_QUALITY_TYPE_FILTER_ALL = "All quality types"
GAS_QUALITY_SOURCE_POINT_FILTER_ALL = "All source points"
DEFAULT_GAS_QUALITY_PREVIEW_ROWS = 50
SOURCE_COVERAGE_TABLE_EXPLORER_ROUTE = "/marimo/table_explorer/"
SOURCE_COVERAGE_STATE_COVERED = "Covered"
SOURCE_COVERAGE_STATE_GAP = "Coverage gap"
SOURCE_COVERAGE_STATE_EMPTY = "Empty"
SOURCE_COVERAGE_STATE_UNAVAILABLE = "Unavailable"
FACILITY_CONTEXT_ID = "facility-context"
FACILITY_DIM_TABLE_NAME = "silver_gas_dim_facility"
FACILITY_FLOW_STORAGE_TABLE_NAME = "silver_gas_fact_facility_flow_storage"
FACILITY_CAPACITY_OUTLOOK_TABLE_NAME = "silver_gas_fact_capacity_outlook"
DEFAULT_FACILITY_PREVIEW_ROWS = 50
_FACILITY_CAPACITY_METADATA_COLUMNS = (
    "default_capacity",
    "maximum_capacity",
    "high_capacity_threshold",
    "low_capacity_threshold",
)
_FACILITY_FLOW_MEASURE_COLUMNS = (
    "demand_tj",
    "supply_tj",
    "transfer_in_tj",
    "transfer_out_tj",
)
_FACILITY_STORAGE_MEASURE_COLUMNS = (
    "held_in_storage_tj",
    "cushion_gas_storage_tj",
)

_SOURCE_COVERAGE_MISSING_SOURCE_SYSTEM_COLUMN = "(missing source_system column)"
_SOURCE_COVERAGE_EMPTY_SOURCE_SYSTEM_VALUE = "(empty source_system value)"
_SOURCE_COVERAGE_MISSING_SOURCE_TABLE_COLUMN = (
    "(missing source_table/source_tables column)"
)
_SOURCE_COVERAGE_EMPTY_SOURCE_TABLE_VALUE = "(empty source_table/source_tables value)"


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


@dataclass(frozen=True)
class _SourceCoverageContext:
    table_explorer_link: str
    asset_metadata_link: str
    uri: str


MARKET_PRICE_TABLE_SPEC = GasTableSpec(
    section="Prices",
    label="Market prices",
    table_name=MARKET_PRICE_TABLE_NAME,
    date_columns=("gas_date",),
    preview_columns=(
        "gas_date",
        "source_system",
        "source_table",
        "price_type",
        "schedule_type_id",
        "schedule_interval",
        "transmission_id",
        "source_location_id",
        "price_value_gst_ex",
        "weighted_average_price_gst_ex",
        "cumulative_price",
        "administered_price",
    ),
)

SCHEDULE_RUN_TABLE_SPEC = GasTableSpec(
    section="Schedules",
    label="Schedule runs",
    table_name=SCHEDULE_RUN_TABLE_NAME,
    date_columns=(
        "gas_date",
        "gas_start_timestamp",
        "bid_cutoff_timestamp",
        "creation_timestamp",
        "approval_timestamp",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
    preview_columns=(
        "gas_date",
        "source_system",
        "source_table",
        "schedule_type_id",
        "forecast_demand_version",
        "transmission_id",
        "transmission_document_id",
        "transmission_group_id",
        "gas_start_timestamp",
        "bid_cutoff_timestamp",
        "creation_timestamp",
        "approval_timestamp",
    ),
)
SETTLEMENT_ACTIVITY_TABLE_SPEC = GasTableSpec(
    section="Settlement",
    label="Settlement activity",
    table_name=SETTLEMENT_ACTIVITY_TABLE_NAME,
    date_columns=(
        "gas_date",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
    preview_columns=(
        "gas_date",
        "source_system",
        "source_table",
        "settlement_version_id",
        "activity_type",
        "schedule_no",
        "network_name",
        "participant_name",
        "amount_gst_ex",
        "quantity_gj",
        "percentage",
        "source_last_updated_timestamp",
        "source_file",
        "source_surrogate_key",
    ),
)
SETTLEMENT_ACTIVITY_TABLE_SPECS = (SETTLEMENT_ACTIVITY_TABLE_SPEC,)

CUSTOMER_TRANSFER_TABLE_SPEC = GasTableSpec(
    section="Retail activity",
    label="Customer transfers",
    table_name=CUSTOMER_TRANSFER_TABLE_NAME,
    date_columns=(
        "gas_date",
        "ingested_timestamp",
    ),
    preview_columns=(
        "gas_date",
        "market_code",
        "source_system",
        "source_table",
        "transfers_lodged",
        "transfers_completed",
        "transfers_cancelled",
        "int_transfers_lodged",
        "int_transfers_completed",
        "int_transfers_cancelled",
        "greenfields_received",
        "source_file",
        "source_surrogate_key",
    ),
)
CUSTOMER_TRANSFER_TABLE_SPECS = (CUSTOMER_TRANSFER_TABLE_SPEC,)

BID_STACK_TABLE_SPEC = GasTableSpec(
    section="Bid / Offer",
    label="Bid / Offer stack",
    table_name=BID_STACK_TABLE_NAME,
    date_columns=(
        "gas_date",
        "bid_cutoff_timestamp",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
    preview_columns=(
        "gas_date",
        "source_system",
        "source_table",
        "source_report_id",
        "participant_id",
        "participant_name",
        "source_hub_id",
        "source_hub_name",
        "source_facility_id",
        "facility_name",
        "source_point_id",
        "schedule_identifier",
        "bid_id",
        "bid_step",
        "bid_price",
        "bid_qty_gj",
        "step_qty_gj",
        "offer_type",
        "inject_withdraw",
        "source_surrogate_key",
    ),
)
BID_STACK_TABLE_SPECS = (BID_STACK_TABLE_SPEC,)

GAS_MODEL_TABLES: tuple[GasTableSpec, ...] = (
    MARKET_PRICE_TABLE_SPEC,
    SCHEDULE_RUN_TABLE_SPEC,
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

FACILITY_TABLE_SPECS = (
    GasTableSpec(
        section="Dimensions",
        label="Facility standing data",
        table_name=FACILITY_DIM_TABLE_NAME,
        date_columns=(
            "operating_state_date",
            "operator_change_date",
            "capacity_effective_from_date",
            "capacity_effective_to_date",
            "ingested_timestamp",
        ),
        preview_columns=(
            "source_system",
            "source_facility_id",
            "facility_name",
            "facility_short_name",
            "facility_type",
            "facility_type_description",
            "operator_name",
            "participant_key",
            "zone_key",
            "default_capacity",
            "maximum_capacity",
        ),
    ),
    GasTableSpec(
        section="Facts",
        label="Facility flow and storage",
        table_name=FACILITY_FLOW_STORAGE_TABLE_NAME,
        date_columns=(
            "gas_date",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_facility_id",
            "source_location_id",
            "demand_tj",
            "supply_tj",
            "transfer_in_tj",
            "transfer_out_tj",
            "held_in_storage_tj",
            "cushion_gas_storage_tj",
        ),
    ),
    GasTableSpec(
        section="Facts",
        label="Capacity outlook",
        table_name=FACILITY_CAPACITY_OUTLOOK_TABLE_NAME,
        date_columns=(
            "from_gas_date",
            "to_gas_date",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ),
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
            "capacity_description",
        ),
    ),
)

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
_MARKET_PRICE_RAW_SCHEMA = {
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "gas_date": pl.Date,
    "price_type": pl.String,
    "schedule_type_id": pl.String,
    "schedule_interval": pl.String,
    "transmission_id": pl.String,
    "transmission_doc_id": pl.String,
    "source_location_id": pl.String,
    "price_value_gst_ex": pl.Float64,
    "weighted_average_price_gst_ex": pl.Float64,
    "cumulative_price": pl.Float64,
    "administered_price": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "ingested_timestamp": pl.Datetime("us"),
}
_MARKET_PRICE_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_MARKET_PRICE_TYPE_SUMMARY_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "price type": pl.String,
    "observations": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "available price measures": pl.String,
    "avg price_value_gst_ex": pl.Float64,
    "avg weighted_average_price_gst_ex": pl.Float64,
    "latest cumulative_price": pl.Float64,
    "latest administered_price": pl.Float64,
}
_MARKET_PRICE_TREND_SCHEMA = {
    "gas date": pl.Date,
    "source system": pl.String,
    "price type": pl.String,
    "observations": pl.UInt32,
    "source tables": pl.UInt32,
    "available price measures": pl.String,
    "avg price_value_gst_ex": pl.Float64,
    "avg weighted_average_price_gst_ex": pl.Float64,
    "avg cumulative_price": pl.Float64,
    "avg administered_price": pl.Float64,
}
_MARKET_PRICE_OBSERVATION_SCHEMA = {
    "gas date": pl.Date,
    "source system": pl.String,
    "source table": pl.String,
    "price type": pl.String,
    "schedule type": pl.String,
    "schedule interval": pl.String,
    "transmission": pl.String,
    "source location": pl.String,
    "available price measures": pl.String,
    "price_value_gst_ex": pl.Float64,
    "weighted_average_price_gst_ex": pl.Float64,
    "cumulative_price": pl.Float64,
    "administered_price": pl.Float64,
    "source updated": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_SCHEDULE_RUN_RAW_SCHEMA = {
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "gas_date": pl.Date,
    "transmission_id": pl.String,
    "transmission_document_id": pl.String,
    "transmission_group_id": pl.String,
    "schedule_type_id": pl.String,
    "forecast_demand_version": pl.String,
    "demand_type_id": pl.String,
    "objective_function_value": pl.Float64,
    "gas_start_timestamp": pl.Datetime("us"),
    "bid_cutoff_timestamp": pl.Datetime("us"),
    "creation_timestamp": pl.Datetime("us"),
    "approval_timestamp": pl.Datetime("us"),
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_SCHEDULE_RUN_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_SCHEDULE_RUN_TYPE_SUMMARY_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "schedule type": pl.String,
    "forecast demand version": pl.String,
    "runs": pl.UInt32,
    "gas days": pl.UInt32,
    "transmissions": pl.UInt32,
    "transmission documents": pl.UInt32,
    "transmission groups": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest creation": pl.Datetime("us"),
    "latest approval": pl.Datetime("us"),
}
_SCHEDULE_RUN_TIMESTAMP_SUMMARY_SCHEMA = {
    "gas date": pl.Date,
    "source system": pl.String,
    "schedule type": pl.String,
    "runs": pl.UInt32,
    "first gas start": pl.Datetime("us"),
    "latest gas start": pl.Datetime("us"),
    "latest bid cutoff": pl.Datetime("us"),
    "latest creation": pl.Datetime("us"),
    "latest approval": pl.Datetime("us"),
}
_SCHEDULE_RUN_SOURCE_COVERAGE_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "schedule runs": pl.UInt32,
    "schedule types": pl.UInt32,
    "forecast demand versions": pl.UInt32,
    "gas days": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_SCHEDULE_RUN_OBSERVATION_SCHEMA = {
    "gas date": pl.Date,
    "source system": pl.String,
    "source table": pl.String,
    "schedule type": pl.String,
    "forecast demand version": pl.String,
    "demand type": pl.String,
    "transmission": pl.String,
    "transmission document": pl.String,
    "transmission group": pl.String,
    "objective function value": pl.Float64,
    "gas start": pl.Datetime("us"),
    "bid cutoff": pl.Datetime("us"),
    "created": pl.Datetime("us"),
    "approved": pl.Datetime("us"),
    "source updated": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_SETTLEMENT_ACTIVITY_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "gas_date": pl.Date,
    "settlement_version_id": pl.String,
    "activity_type": pl.String,
    "schedule_no": pl.String,
    "network_name": pl.String,
    "participant_name": pl.String,
    "amount_gst_ex": pl.Float64,
    "quantity_gj": pl.Float64,
    "percentage": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_SETTLEMENT_ACTIVITY_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_SETTLEMENT_ACTIVITY_SUMMARY_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "activity type": pl.String,
    "settlement version": pl.String,
    "rows": pl.UInt32,
    "gas days": pl.UInt32,
    "schedules": pl.UInt32,
    "networks": pl.UInt32,
    "participants": pl.UInt32,
    "amount rows": pl.UInt32,
    "total amount gst ex": pl.Float64,
    "quantity rows": pl.UInt32,
    "total quantity gj": pl.Float64,
    "percentage rows": pl.UInt32,
    "avg percentage": pl.Float64,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
}
_SETTLEMENT_ACTIVITY_SOURCE_COVERAGE_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "rows": pl.UInt32,
    "activity types": pl.UInt32,
    "settlement versions": pl.UInt32,
    "schedules": pl.UInt32,
    "networks": pl.UInt32,
    "participants": pl.UInt32,
    "amount rows": pl.UInt32,
    "quantity rows": pl.UInt32,
    "percentage rows": pl.UInt32,
    "source files": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_SETTLEMENT_ACTIVITY_OBSERVATION_SCHEMA = {
    "gas date": pl.Date,
    "source system": pl.String,
    "source table": pl.String,
    "settlement version": pl.String,
    "activity type": pl.String,
    "schedule": pl.String,
    "network": pl.String,
    "participant": pl.String,
    "amount_gst_ex": pl.Float64,
    "quantity_gj": pl.Float64,
    "percentage": pl.Float64,
    "source updated": pl.Datetime("us"),
    "source file": pl.String,
    "source identifier": pl.String,
    "latest ingest": pl.Datetime("us"),
}
_CUSTOMER_TRANSFER_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "gas_date": pl.Date,
    "market_code": pl.String,
    "transfers_lodged": pl.Int64,
    "transfers_completed": pl.Int64,
    "transfers_cancelled": pl.Int64,
    "int_transfers_lodged": pl.Int64,
    "int_transfers_completed": pl.Int64,
    "int_transfers_cancelled": pl.Int64,
    "greenfields_received": pl.Int64,
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_CUSTOMER_TRANSFER_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_CUSTOMER_TRANSFER_SUMMARY_SCHEMA = {
    "market code": pl.String,
    "source system": pl.String,
    "source table": pl.String,
    "rows": pl.UInt32,
    "gas days": pl.UInt32,
    "transfers lodged": pl.Int64,
    "transfers completed": pl.Int64,
    "transfers cancelled": pl.Int64,
    "internal transfers lodged": pl.Int64,
    "internal transfers completed": pl.Int64,
    "internal transfers cancelled": pl.Int64,
    "greenfields received": pl.Int64,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest ingest": pl.Datetime("us"),
}
_CUSTOMER_TRANSFER_DAILY_SCHEMA = {
    "gas date": pl.Date,
    "market code": pl.String,
    "rows": pl.UInt32,
    "transfers lodged": pl.Int64,
    "transfers completed": pl.Int64,
    "transfers cancelled": pl.Int64,
    "internal transfers lodged": pl.Int64,
    "internal transfers completed": pl.Int64,
    "internal transfers cancelled": pl.Int64,
    "greenfields received": pl.Int64,
}
_CUSTOMER_TRANSFER_SOURCE_COVERAGE_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "rows": pl.UInt32,
    "market codes": pl.UInt32,
    "gas days": pl.UInt32,
    "source files": pl.UInt32,
    "source identifiers": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest ingest": pl.Datetime("us"),
}
_CUSTOMER_TRANSFER_OBSERVATION_SCHEMA = {
    "gas date": pl.Date,
    "market code": pl.String,
    "source system": pl.String,
    "source table": pl.String,
    "transfers_lodged": pl.Int64,
    "transfers_completed": pl.Int64,
    "transfers_cancelled": pl.Int64,
    "int_transfers_lodged": pl.Int64,
    "int_transfers_completed": pl.Int64,
    "int_transfers_cancelled": pl.Int64,
    "greenfields_received": pl.Int64,
    "source file": pl.String,
    "source identifier": pl.String,
    "latest ingest": pl.Datetime("us"),
}
_BID_STACK_RAW_SCHEMA = {
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "source_report_id": pl.String,
    "gas_date": pl.Date,
    "participant_id": pl.String,
    "participant_name": pl.String,
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "source_point_id": pl.String,
    "schedule_identifier": pl.String,
    "bid_id": pl.String,
    "bid_step": pl.Int64,
    "bid_price": pl.Float64,
    "bid_qty_gj": pl.Float64,
    "step_qty_gj": pl.Float64,
    "offer_type": pl.String,
    "inject_withdraw": pl.String,
    "schedule_type": pl.String,
    "schedule_time": pl.String,
    "bid_cutoff_timestamp": pl.Datetime("us"),
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_BID_STACK_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_BID_STACK_STEP_SUMMARY_SCHEMA = {
    "source system": pl.String,
    "zone": pl.String,
    "facility": pl.String,
    "bid step": pl.Int64,
    "rows": pl.UInt32,
    "participants": pl.UInt32,
    "bid ids": pl.UInt32,
    "min bid price": pl.Float64,
    "avg bid price": pl.Float64,
    "max bid price": pl.Float64,
    "total bid quantity gj": pl.Float64,
    "total step quantity gj": pl.Float64,
    "latest gas date": pl.Date,
}
_BID_STACK_SOURCE_SUMMARY_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "source report": pl.String,
    "rows": pl.UInt32,
    "participants": pl.UInt32,
    "facilities": pl.UInt32,
    "zones": pl.UInt32,
    "bid ids": pl.UInt32,
    "bid steps": pl.UInt32,
    "accepted source identifiers": pl.UInt32,
    "source files": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_BID_STACK_OBSERVATION_SCHEMA = {
    "gas date": pl.Date,
    "source system": pl.String,
    "source table": pl.String,
    "source report": pl.String,
    "participant": pl.String,
    "participant name": pl.String,
    "zone": pl.String,
    "zone name": pl.String,
    "facility": pl.String,
    "facility name": pl.String,
    "source point": pl.String,
    "schedule identifier": pl.String,
    "bid id": pl.String,
    "bid step": pl.Int64,
    "bid price": pl.Float64,
    "bid quantity gj": pl.Float64,
    "step quantity gj": pl.Float64,
    "offer type": pl.String,
    "inject withdraw": pl.String,
    "schedule type": pl.String,
    "schedule time": pl.String,
    "bid cutoff": pl.Datetime("us"),
    "accepted source identifier": pl.String,
    "source file": pl.String,
    "source updated": pl.Datetime("us"),
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
_FACILITY_DIM_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "participant_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "facility_short_name": pl.String,
    "facility_type": pl.String,
    "facility_type_description": pl.String,
    "operating_state": pl.String,
    "operating_state_date": pl.Date,
    "operator_name": pl.String,
    "source_operator_id": pl.String,
    "operator_change_date": pl.Date,
    "capacity_effective_from_date": pl.Date,
    "capacity_effective_to_date": pl.Date,
    "default_capacity": pl.Float64,
    "maximum_capacity": pl.Float64,
    "high_capacity_threshold": pl.Float64,
    "low_capacity_threshold": pl.Float64,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_FACILITY_FLOW_STORAGE_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "facility_key": pl.String,
    "location_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "gas_date": pl.Date,
    "source_facility_id": pl.String,
    "source_location_id": pl.String,
    "demand_tj": pl.Float64,
    "supply_tj": pl.Float64,
    "transfer_in_tj": pl.Float64,
    "transfer_out_tj": pl.Float64,
    "held_in_storage_tj": pl.Float64,
    "cushion_gas_storage_tj": pl.Float64,
    "source_file": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "ingested_timestamp": pl.Datetime("us"),
}
_FACILITY_CAPACITY_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "capacity_type": pl.String,
    "flow_direction": pl.String,
    "from_gas_date": pl.Date,
    "to_gas_date": pl.Date,
    "capacity_quantity_tj": pl.Float64,
    "capacity_description": pl.String,
    "source_file": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "ingested_timestamp": pl.Datetime("us"),
}
_FACILITY_COVERAGE_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_FACILITY_RELATIONSHIP_SCHEMA = {
    "relationship": pl.String,
    "source table": pl.String,
    "available rows": pl.UInt32,
    "facilities": pl.UInt32,
    "matched facilities": pl.UInt32,
    "detail": pl.String,
}
_FACILITY_PREVIEW_SCHEMA = {
    "source system": pl.String,
    "source facility id": pl.String,
    "facility": pl.String,
    "short name": pl.String,
    "facility type": pl.String,
    "operator": pl.String,
    "participant key": pl.String,
    "zone key": pl.String,
    "default capacity": pl.Float64,
    "maximum capacity": pl.Float64,
    "capacity effective from": pl.Date,
    "capacity effective to": pl.Date,
    "source tables": pl.String,
    "latest ingest": pl.Datetime("us"),
}
_SOURCE_COVERAGE_MATRIX_SCHEMA = {
    "asset": pl.String,
    "section": pl.String,
    "table": pl.String,
    "source system": pl.String,
    "source table": pl.String,
    "coverage state": pl.String,
    "rows loaded": pl.UInt32,
    "row limit": pl.String,
    "source fields": pl.String,
    "table explorer": pl.String,
    "asset metadata": pl.String,
    "uri": pl.String,
    "detail": pl.String,
}
_SOURCE_COVERAGE_MATRIX_HTML_COLUMNS = (
    "asset",
    "section",
    "source system",
    "source table",
    "coverage state",
    "rows loaded",
    "row limit",
    "source fields",
    "table explorer",
    "asset metadata",
    "uri",
    "detail",
)
_SOURCE_COVERAGE_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_GAS_DAY_FIELD_DISCOVERY_SCHEMA = {
    "asset": pl.String,
    "section": pl.String,
    "table": pl.String,
    "field": pl.String,
    "field role": pl.String,
    "dtype": pl.String,
    "status": pl.String,
    "rows loaded": pl.UInt32,
    "populated values": pl.UInt32,
    "first value": pl.String,
    "latest value": pl.String,
    "row limit": pl.String,
    "table explorer": pl.String,
    "uri": pl.String,
    "detail": pl.String,
}
_GAS_DAY_EXAMPLE_SCHEMA = {
    "asset": pl.String,
    "section": pl.String,
    "table": pl.String,
    "field": pl.String,
    "field role": pl.String,
    "value": pl.String,
    "source system": pl.String,
    "source table": pl.String,
    "context": pl.String,
    "row limit": pl.String,
    "uri": pl.String,
}
_GAS_DAY_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_GAS_DAY_EXAMPLE_CONTEXT_COLUMNS = (
    "price_type",
    "schedule_type_id",
    "forecast_demand_version",
    "transmission_id",
    "activity_type",
    "market_code",
    "source_facility_id",
    "facility_name",
    "source_connection_point_id",
    "source_point_id",
    "quality_type",
    "gas_interval",
    "ingested_timestamp",
)
_GAS_DAY_KNOWN_TABLE_SPECS = (
    *GAS_MODEL_TABLES,
    SYSTEM_NOTICE_TABLE_SPEC,
    MARKET_PRICE_TABLE_SPEC,
    SCHEDULE_RUN_TABLE_SPEC,
    SETTLEMENT_ACTIVITY_TABLE_SPEC,
    CUSTOMER_TRANSFER_TABLE_SPEC,
    BID_STACK_TABLE_SPEC,
    GAS_QUALITY_TABLE_SPEC,
)
_GAS_DAY_KNOWN_DATE_COLUMNS_BY_TABLE = {
    spec.table_name: spec.date_columns
    for spec in _GAS_DAY_KNOWN_TABLE_SPECS
    if len(spec.date_columns) > 0
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


def load_market_price_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the market price fact through the shared bounded table loader."""
    return load_gas_model_tables(
        config,
        specs=(MARKET_PRICE_TABLE_SPEC,),
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_market_price_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached market price data for explicit-refresh dashboards."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=(MARKET_PRICE_TABLE_SPEC,),
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )[0]


def load_schedule_run_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the schedule run fact through the shared bounded table loader."""
    return load_gas_model_tables(
        config,
        specs=(SCHEDULE_RUN_TABLE_SPEC,),
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_schedule_run_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached schedule run data for explicit-refresh dashboards."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=(SCHEDULE_RUN_TABLE_SPEC,),
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )[0]


def load_settlement_activity_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the settlement activity fact through the shared bounded table loader."""
    return load_gas_model_tables(
        config,
        specs=SETTLEMENT_ACTIVITY_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_settlement_activity_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached settlement activity data for explicit refreshes."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=SETTLEMENT_ACTIVITY_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )[0]


def load_customer_transfer_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the customer transfer fact through the shared bounded table loader."""
    return load_gas_model_tables(
        config,
        specs=CUSTOMER_TRANSFER_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_customer_transfer_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached customer transfer data for explicit refreshes."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=CUSTOMER_TRANSFER_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )[0]


def load_bid_stack_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the Bid / Offer stack fact through the shared bounded table loader."""
    return load_gas_model_tables(
        config,
        specs=BID_STACK_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_bid_stack_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached Bid / Offer stack data for explicit refreshes."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=BID_STACK_TABLE_SPECS,
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


def facility_table_specs() -> tuple[GasTableSpec, ...]:
    """Return the facility-oriented tables used by the Facility explainer."""
    return FACILITY_TABLE_SPECS


def load_facility_context_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Load Facility explainer tables through the shared bounded loader."""
    requested_specs = FACILITY_TABLE_SPECS if specs is None else specs
    return load_gas_model_tables(
        _source_coverage_bounded_config(config),
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        clock=clock,
    )


def cached_load_facility_context_tables(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Return cached Facility explainer table reads for explicit refreshes."""
    requested_specs = FACILITY_TABLE_SPECS if specs is None else specs
    return cached_load_gas_model_tables(
        _source_coverage_bounded_config(config),
        cache,
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        refresh_token=refresh_token,
        clock=clock,
    )


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


def source_coverage_table_specs(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> tuple[GasTableSpec, ...]:
    """Return unique gas_model table specs from the Marimo dashboard registry."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    seen_table_names: set[str] = set()
    specs: list[GasTableSpec] = []

    for entry in candidate_entries:
        for asset in entry.backing_assets:
            table_name = _source_coverage_table_name_from_registry_asset(asset)
            if table_name is None or table_name in seen_table_names:
                continue
            seen_table_names.add(table_name)
            specs.append(
                GasTableSpec(
                    section=_source_coverage_section(table_name),
                    label=_source_coverage_label(table_name),
                    table_name=table_name,
                )
            )

    return tuple(specs)


def source_coverage_table_specs_from_catalogue(
    table_catalogue: Sequence[object],
) -> tuple[GasTableSpec, ...]:
    """Return unique gas_model table specs from discovered catalogue rows."""
    seen_table_names: set[str] = set()
    specs: list[GasTableSpec] = []

    for entry in table_catalogue:
        table_name = _source_coverage_table_name_from_catalogue_entry(entry)
        if table_name is None or table_name in seen_table_names:
            continue
        seen_table_names.add(table_name)
        specs.append(
            GasTableSpec(
                section=_source_coverage_section(table_name),
                label=_source_coverage_label(table_name),
                table_name=table_name,
            )
        )

    return tuple(specs)


def load_source_coverage_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Load registry-backed gas_model tables for source coverage inspection."""
    requested_specs = source_coverage_table_specs() if specs is None else specs
    return load_gas_model_tables(
        _source_coverage_bounded_config(config),
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        clock=clock,
    )


def cached_load_source_coverage_tables(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Return cached registry-backed gas_model source coverage reads."""
    requested_specs = source_coverage_table_specs() if specs is None else specs
    return cached_load_gas_model_tables(
        _source_coverage_bounded_config(config),
        cache,
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        refresh_token=refresh_token,
        clock=clock,
    )


def _source_coverage_bounded_config(config: GasDashboardConfig) -> GasDashboardConfig:
    if not config.full_table_scan_enabled:
        return config
    return replace(config, full_table_scan_enabled=False)


def source_coverage_matrix_frame(
    loads: Sequence[GasTableLoad],
    table_catalogue: Sequence[object] = (),
) -> pl.DataFrame:
    """Return source-system and source-table coverage by gas_model asset."""
    context_by_table_name = _source_coverage_context_by_table_name(table_catalogue)
    rows: list[dict[str, object]] = []

    for load in loads:
        context = context_by_table_name.get(load.spec.table_name)
        rows.extend(_source_coverage_rows(load, context))

    if rows:
        return pl.DataFrame(rows, schema=_SOURCE_COVERAGE_MATRIX_SCHEMA)
    return pl.DataFrame(schema=_SOURCE_COVERAGE_MATRIX_SCHEMA)


def render_source_coverage_matrix_html(
    matrix: pl.DataFrame,
    *,
    max_rows: int = 200,
) -> str:
    """Return source coverage rows as an HTML table with real deep-link anchors."""
    row_limit = max(1, max_rows)
    visible_rows = matrix.head(row_limit).to_dicts()
    hidden_rows = max(0, matrix.height - len(visible_rows))
    body_html = "\n".join(
        _render_source_coverage_matrix_row(row) for row in visible_rows
    )
    if body_html == "":
        body_html = (
            '<tr><td colspan="12" class="source-coverage-matrix__empty">'
            "No source coverage rows match the current filters."
            "</td></tr>"
        )

    overflow_note = ""
    if hidden_rows > 0:
        overflow_note = (
            '<p class="source-coverage-matrix__overflow">'
            f"{hidden_rows:,} additional rows are hidden by the dashboard "
            "display limit. Narrow the filters to inspect them."
            "</p>"
        )

    return f"""\
<style>
{_source_coverage_matrix_css()}
</style>
<div
    class="source-coverage-matrix"
    data-row-count="{matrix.height}"
    data-rendered-row-count="{len(visible_rows)}"
>
    <div class="source-coverage-matrix__scroller">
        <table>
            <thead>
                <tr>
                    {_render_source_coverage_matrix_headings()}
                </tr>
            </thead>
            <tbody>
                {body_html}
            </tbody>
        </table>
    </div>
    {overflow_note}
</div>"""


def source_coverage_kpi_frame(
    loads: Sequence[GasTableLoad],
    matrix: pl.DataFrame,
) -> pl.DataFrame:
    """Return first-viewport source coverage KPIs for loaded gas_model assets."""
    covered_assets = _source_coverage_distinct_count(
        matrix,
        "asset",
        coverage_state=SOURCE_COVERAGE_STATE_COVERED,
    )
    gap_assets = _source_coverage_distinct_count(
        matrix,
        "asset",
        coverage_state=SOURCE_COVERAGE_STATE_GAP,
    )
    source_systems = _source_coverage_distinct_count(
        matrix,
        "source system",
        coverage_state=SOURCE_COVERAGE_STATE_COVERED,
        exclude_missing=True,
    )
    source_tables = _source_coverage_distinct_count(
        matrix,
        "source table",
        coverage_state=SOURCE_COVERAGE_STATE_COVERED,
        exclude_missing=True,
    )
    unavailable_assets = sum(load.error is not None for load in loads)
    empty_assets = sum(
        load.error is None and (load.dataframe is None or load.dataframe.is_empty())
        for load in loads
    )

    return pl.DataFrame(
        [
            {
                "metric": "Requested assets",
                "value": f"{len(loads):,}",
                "detail": "Unique silver.gas_model table reads requested",
            },
            {
                "metric": "Loaded assets",
                "value": f"{sum(load.available for load in loads):,}",
                "detail": "Tables with at least one loaded bounded row",
            },
            {
                "metric": "Assets with source coverage",
                "value": f"{covered_assets:,}",
                "detail": "Assets with populated source-system and source-table values",
            },
            {
                "metric": "Assets with coverage gaps",
                "value": f"{gap_assets:,}",
                "detail": "Assets missing source metadata columns or values",
            },
            {
                "metric": "Source systems",
                "value": f"{source_systems:,}",
                "detail": "Distinct covered source_system values in loaded rows",
            },
            {
                "metric": "Source tables",
                "value": f"{source_tables:,}",
                "detail": "Distinct covered source_table/source_tables values",
            },
            {
                "metric": "Unavailable or empty assets",
                "value": f"{unavailable_assets + empty_assets:,}",
                "detail": (
                    f"{unavailable_assets:,} unavailable reads and "
                    f"{empty_assets:,} empty reads"
                ),
            },
        ],
        schema=_SOURCE_COVERAGE_KPI_SCHEMA,
    )


def source_coverage_empty_state_markdown(loads: Sequence[GasTableLoad]) -> str:
    """Return empty-state copy for source coverage dashboards."""
    if len(loads) == 0:
        return """
        **No source coverage tables were requested.**

        The dashboard expected registry-backed `silver.gas_model` assets but
        received no table specs. Check the Marimo dashboard registry.
        """

    failed_count = sum(load.error is not None for load in loads)
    empty_count = sum(
        load.error is None and (load.dataframe is None or load.dataframe.is_empty())
        for load in loads
    )
    return f"""
    **No source coverage rows are available.**

    The dashboard checked `{len(loads)}` registry-backed `silver.gas_model`
    assets. `{failed_count}` reads were unavailable and `{empty_count}` reads
    returned no rows.

    Materialize or seed the curated gas model outputs, then use
    **Refresh data**.
    """


def facility_dimension_coverage_frame(load: GasTableLoad | None) -> pl.DataFrame:
    """Return Facility dimension coverage metrics from bounded rows."""
    dataframe = _normalised_facility_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_COVERAGE_SCHEMA)

    participant_rows = _non_empty_string_count(dataframe, "participant_key")
    zone_rows = _non_empty_string_count(dataframe, "zone_key")
    capacity_rows = _capacity_metadata_row_count(dataframe)
    source_table_count = _facility_source_table_count(dataframe)

    return pl.DataFrame(
        [
            {
                "metric": "Facility dimension rows",
                "value": f"{dataframe.height:,}",
                "detail": "Loaded bounded rows from silver_gas_dim_facility",
            },
            {
                "metric": "Source systems",
                "value": f"{_distinct_non_empty_count(dataframe, 'source_system'):,}",
                "detail": "Distinct source_system values represented",
            },
            {
                "metric": "Source tables",
                "value": f"{source_table_count:,}",
                "detail": "Distinct source table values carried in source_tables",
            },
            {
                "metric": "Facility types",
                "value": (f"{_distinct_non_empty_count(dataframe, 'facility_type'):,}"),
                "detail": "Distinct facility_type values in the dimension preview",
            },
            {
                "metric": "Operators",
                "value": f"{_distinct_non_empty_count(dataframe, 'operator_name'):,}",
                "detail": "Distinct operator_name values where source data provides them",
            },
            {
                "metric": "Participant links",
                "value": f"{participant_rows:,}",
                "detail": "Rows with participant_key populated",
            },
            {
                "metric": "Zone links",
                "value": f"{zone_rows:,}",
                "detail": "Rows with zone_key populated",
            },
            {
                "metric": "Capacity metadata rows",
                "value": f"{capacity_rows:,}",
                "detail": (
                    "Rows with default, maximum, high-threshold, or "
                    "low-threshold capacity populated"
                ),
            },
        ],
        schema=_FACILITY_COVERAGE_SCHEMA,
    )


def facility_relationship_frame(loads: Sequence[GasTableLoad]) -> pl.DataFrame:
    """Return Facility relationships to dimensions and related facts."""
    facility_load = table_load_by_name(loads, FACILITY_DIM_TABLE_NAME)
    flow_load = table_load_by_name(loads, FACILITY_FLOW_STORAGE_TABLE_NAME)
    capacity_load = table_load_by_name(loads, FACILITY_CAPACITY_OUTLOOK_TABLE_NAME)
    facilities = _normalised_facility_dimension_dataframe(facility_load)
    flow_storage = _normalised_facility_flow_storage_dataframe(flow_load)
    capacity = _normalised_facility_capacity_dataframe(capacity_load)

    if facilities.is_empty() and flow_storage.is_empty() and capacity.is_empty():
        return pl.DataFrame(schema=_FACILITY_RELATIONSHIP_SCHEMA)

    facility_ids = _facility_identifier_set(facilities, "source_facility_id")
    facility_keys = _facility_identifier_set(facilities, "surrogate_key")
    participant_rows = _non_empty_string_count(facilities, "participant_key")
    zone_rows = _non_empty_string_count(facilities, "zone_key")
    flow_rows = _facility_flow_rows(flow_storage)
    storage_rows = _facility_storage_rows(flow_storage)
    capacity_rows = capacity.filter(pl.col("capacity_quantity_tj").is_not_null())
    capacity_metadata_rows = _capacity_metadata_row_count(facilities)

    rows = [
        {
            "relationship": "Participant",
            "source table": FACILITY_DIM_TABLE_NAME,
            "available rows": participant_rows,
            "facilities": _distinct_non_empty_count(facilities, "source_facility_id"),
            "matched facilities": participant_rows,
            "detail": (
                "participant_key is populated on facility dimension rows where "
                "operator participant lineage is resolvable."
            ),
        },
        {
            "relationship": "Zone",
            "source table": FACILITY_DIM_TABLE_NAME,
            "available rows": zone_rows,
            "facilities": _distinct_non_empty_count(facilities, "source_facility_id"),
            "matched facilities": zone_rows,
            "detail": (
                "zone_key is populated for hub-scoped facility rows where the "
                "source can resolve a gas_model zone."
            ),
        },
        {
            "relationship": "Flow",
            "source table": FACILITY_FLOW_STORAGE_TABLE_NAME,
            "available rows": flow_rows.height,
            "facilities": _distinct_non_empty_count(flow_rows, "source_facility_id"),
            "matched facilities": _matched_facility_count(
                flow_rows,
                facility_ids,
                facility_keys,
            ),
            "detail": (
                "Rows with demand, supply, transfer-in, or transfer-out measures "
                "from the facility flow/storage fact."
            ),
        },
        {
            "relationship": "Storage",
            "source table": FACILITY_FLOW_STORAGE_TABLE_NAME,
            "available rows": storage_rows.height,
            "facilities": _distinct_non_empty_count(storage_rows, "source_facility_id"),
            "matched facilities": _matched_facility_count(
                storage_rows,
                facility_ids,
                facility_keys,
            ),
            "detail": (
                "Rows with held-in-storage or cushion-gas storage measures from "
                "the facility flow/storage fact."
            ),
        },
        {
            "relationship": "Capacity",
            "source table": FACILITY_CAPACITY_OUTLOOK_TABLE_NAME,
            "available rows": capacity_rows.height,
            "facilities": _distinct_non_empty_count(
                capacity_rows, "source_facility_id"
            ),
            "matched facilities": _matched_facility_count(
                capacity_rows,
                facility_ids,
                facility_keys,
            ),
            "detail": (
                "Capacity outlook rows with capacity_quantity_tj populated; "
                f"{capacity_metadata_rows:,} facility dimension rows also carry "
                "standing capacity metadata."
            ),
        },
    ]
    return pl.DataFrame(rows, schema=_FACILITY_RELATIONSHIP_SCHEMA)


def facility_dimension_preview_frame(
    load: GasTableLoad | None,
    *,
    preview_rows: int = DEFAULT_FACILITY_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return a table-friendly preview of facility standing data."""
    dataframe = _normalised_facility_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_PREVIEW_SCHEMA)

    rows: list[dict[str, object]] = []
    for row in (
        dataframe.sort(
            ["source_system", "facility_type", "source_facility_id"],
            nulls_last=True,
        )
        .head(max(1, preview_rows))
        .to_dicts()
    ):
        rows.append(
            {
                "source system": row.get("source_system"),
                "source facility id": row.get("source_facility_id"),
                "facility": row.get("facility_name"),
                "short name": row.get("facility_short_name"),
                "facility type": row.get("facility_type"),
                "operator": row.get("operator_name"),
                "participant key": row.get("participant_key"),
                "zone key": row.get("zone_key"),
                "default capacity": row.get("default_capacity"),
                "maximum capacity": row.get("maximum_capacity"),
                "capacity effective from": row.get("capacity_effective_from_date"),
                "capacity effective to": row.get("capacity_effective_to_date"),
                "source tables": ", ".join(
                    _source_coverage_value_strings(row.get("source_tables"))
                ),
                "latest ingest": row.get("ingested_timestamp"),
            }
        )
    return pl.DataFrame(rows, schema=_FACILITY_PREVIEW_SCHEMA)


def facility_context_empty_state_markdown(loads: Sequence[GasTableLoad]) -> str:
    """Return empty-state copy for the Facility explainer dashboard."""
    if len(loads) == 0:
        return """
        **No Facility context tables were requested.**

        The dashboard expected Facility-oriented `silver.gas_model` table specs
        but received none. Check the Marimo dashboard registry and Facility
        explainer configuration.
        """

    failed_count = sum(load.error is not None for load in loads)
    empty_count = sum(
        load.error is None and (load.dataframe is None or load.dataframe.is_empty())
        for load in loads
    )
    read_policy = row_limit_message(_common_row_limit(loads))
    read_detail = (
        f"`{failed_count}` reads were unavailable and `{empty_count}` reads "
        "returned no rows."
    )
    return f"""
    **No Facility metadata or relationship rows are available.**

    The dashboard checked `{len(loads)}` Facility-oriented `silver.gas_model`
    assets: `silver_gas_dim_facility`,
    `silver_gas_fact_facility_flow_storage`, and
    `silver_gas_fact_capacity_outlook`. {read_detail}

    {read_policy}

    Materialize or seed the curated gas model outputs, then use
    **Refresh data**.
    """


def render_facility_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Facility links to related dashboards and concept panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        FACILITY_CONTEXT_ID,
        "gbb-interactive-map",
        "source-coverage-matrix",
        "gas-model-table-explorer",
        "participant-context",
        "hub-zone-context",
        "flow-context",
        "capacity-context",
        "connection-point-context",
        "bid-offer-context",
    )
    rows = "\n".join(
        _render_facility_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="facility-links__empty">'
            "No Facility, flow, capacity, participant, zone, or table explorer "
            "entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_facility_context_links_css()}
</style>
<section class="facility-links" aria-label="Facility context links">
    <div>
        <p class="facility-links__eyebrow">Context links</p>
        <h2>Facility, flow, capacity, participant, and zone context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def gas_day_table_specs(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> tuple[GasTableSpec, ...]:
    """Return current registry-backed gas_model specs for Gas Day inspection."""
    specs = source_coverage_table_specs(entries)
    return tuple(
        replace(
            spec,
            date_columns=_GAS_DAY_KNOWN_DATE_COLUMNS_BY_TABLE.get(
                spec.table_name,
                (),
            ),
        )
        for spec in specs
    )


def load_gas_day_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Load bounded registry-backed gas_model tables for Gas Day examples."""
    requested_specs = gas_day_table_specs() if specs is None else specs
    return load_gas_model_tables(
        _source_coverage_bounded_config(config),
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        clock=clock,
    )


def cached_load_gas_day_tables(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Return cached bounded gas_model table reads for Gas Day examples."""
    requested_specs = gas_day_table_specs() if specs is None else specs
    return cached_load_gas_model_tables(
        _source_coverage_bounded_config(config),
        cache,
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        refresh_token=refresh_token,
        clock=clock,
    )


def gas_day_field_discovery_frame(loads: Sequence[GasTableLoad]) -> pl.DataFrame:
    """Return date and gas-date field coverage across loaded gas_model assets."""
    rows: list[dict[str, object]] = []
    for load in loads:
        fields = _gas_day_candidate_fields(load)
        if len(fields) == 0:
            rows.append(_gas_day_missing_field_row(load))
            continue
        rows.extend(_gas_day_field_row(load, field) for field in fields)

    if rows:
        return pl.DataFrame(rows, schema=_GAS_DAY_FIELD_DISCOVERY_SCHEMA)
    return pl.DataFrame(schema=_GAS_DAY_FIELD_DISCOVERY_SCHEMA)


def gas_day_kpi_frame(
    loads: Sequence[GasTableLoad],
    field_discovery: pl.DataFrame,
    examples: pl.DataFrame,
) -> pl.DataFrame:
    """Return first-viewport Gas Day coverage KPIs."""
    field_rows = field_discovery.to_dicts() if not field_discovery.is_empty() else []
    gas_day_fields = [
        row
        for row in field_rows
        if row["field role"] == "Gas Day field" and row["field"] != ""
    ]
    fields_with_values = [
        row for row in field_rows if _is_positive_count(row["populated values"])
    ]
    latest_gas_day = _latest_gas_day_value(gas_day_fields)
    unavailable_count = sum(load.error is not None for load in loads)
    empty_count = sum(
        load.error is None and (load.dataframe is None or load.dataframe.is_empty())
        for load in loads
    )
    row_limit = _common_row_limit(loads) if len(loads) > 0 else None

    return pl.DataFrame(
        [
            {
                "metric": "Curated assets checked",
                "value": f"{len(loads):,}",
                "detail": "Registry-backed silver.gas_model table reads requested",
            },
            {
                "metric": "Loaded assets",
                "value": f"{sum(load.available for load in loads):,}",
                "detail": "Tables with at least one loaded bounded row",
            },
            {
                "metric": "Gas Day fields",
                "value": f"{len(gas_day_fields):,}",
                "detail": "Fields named gas_date, from_gas_date, or to_gas_date",
            },
            {
                "metric": "Date fields with values",
                "value": f"{len(fields_with_values):,}",
                "detail": "Date, timestamp, or date-key fields populated in the read",
            },
            {
                "metric": "Bounded examples",
                "value": f"{examples.height:,}",
                "detail": "Example rows rendered from already bounded table reads",
            },
            {
                "metric": "Latest Gas Day",
                "value": latest_gas_day or "unknown",
                "detail": "Maximum loaded value across populated Gas Day fields",
            },
            {
                "metric": "Unavailable or empty assets",
                "value": f"{unavailable_count + empty_count:,}",
                "detail": (
                    f"{unavailable_count:,} unavailable reads and "
                    f"{empty_count:,} empty reads"
                ),
            },
            {
                "metric": "Read policy",
                "value": format_row_limit(row_limit),
                "detail": row_limit_message(row_limit),
            },
        ],
        schema=_GAS_DAY_KPI_SCHEMA,
    )


def gas_day_bounded_examples_frame(
    loads: Sequence[GasTableLoad],
    *,
    examples_per_field: int = DEFAULT_GAS_DAY_EXAMPLES_PER_FIELD,
) -> pl.DataFrame:
    """Return bounded example values for discovered date and gas-date fields."""
    row_limit = max(1, examples_per_field)
    rows: list[dict[str, object]] = []

    for load in loads:
        dataframe = load.dataframe
        if load.error is not None or dataframe is None or dataframe.is_empty():
            continue

        for field in _gas_day_example_fields(load):
            if field not in dataframe.columns:
                continue
            examples = _gas_day_field_examples(dataframe, field, row_limit)
            rows.extend(_gas_day_example_row(load, field, row) for row in examples)

    if rows:
        return pl.DataFrame(rows, schema=_GAS_DAY_EXAMPLE_SCHEMA)
    return pl.DataFrame(schema=_GAS_DAY_EXAMPLE_SCHEMA)


def gas_day_examples_empty_state_markdown(loads: Sequence[GasTableLoad]) -> str:
    """Return empty-state copy for absent Gas Day bounded examples."""
    if len(loads) == 0:
        return """
        **No Gas Day tables were requested.**

        The dashboard expected registry-backed `silver.gas_model` assets but
        received no table specs. Check the Marimo dashboard registry.
        """

    failed_count = sum(load.error is not None for load in loads)
    empty_count = sum(
        load.error is None and (load.dataframe is None or load.dataframe.is_empty())
        for load in loads
    )
    row_limit = _common_row_limit(loads)

    return f"""
    **No bounded Gas Day examples are available.**

    The dashboard checked `{len(loads)}` registry-backed `silver.gas_model`
    assets. `{failed_count}` reads were unavailable and `{empty_count}` reads returned
    no rows or no populated date fields.

    {row_limit_message(row_limit)}

    Materialize or seed the curated gas model outputs, then use
    **Refresh data**.
    """


def market_price_price_type_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return price-type filter options for the loaded market price preview."""
    return _market_price_string_filter_options(
        load,
        "price_type",
        MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    )


def market_price_source_system_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-system filter options for the loaded market price preview."""
    return _market_price_string_filter_options(
        load,
        "source_system",
        MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
    )


def market_price_source_table_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-table filter options for the loaded market price preview."""
    return _market_price_string_filter_options(
        load,
        "source_table",
        MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
    )


def market_price_kpi_frame(
    load: GasTableLoad | None,
    price_type_filter: str = MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    source_system_filter: str = MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
    source_table_filter: str = MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
) -> pl.DataFrame:
    """Return first-viewport KPIs for loaded market price observations."""
    dataframe = _filtered_market_price_dataframe(
        load,
        price_type_filter,
        source_system_filter,
        source_table_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_MARKET_PRICE_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_observations"),
        pl.col("price_type").drop_nulls().n_unique().alias("price_types"),
        pl.col("source_system").drop_nulls().n_unique().alias("source_systems"),
        pl.col("source_table").drop_nulls().n_unique().alias("source_tables"),
        pl.col("gas_date").max().alias("latest_gas_date"),
    ).row(0, named=True)
    available_measures = _available_market_price_measures(dataframe)
    row_limit = None if load is None else load.row_limit

    return pl.DataFrame(
        [
            {
                "metric": "Loaded price rows",
                "value": f"{counts['loaded_observations']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Price types",
                "value": f"{counts['price_types']:,}",
                "detail": "Distinct price_type values in the current view",
            },
            {
                "metric": "Source systems",
                "value": f"{counts['source_systems']:,}",
                "detail": "Distinct source_system values in the current view",
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
            {
                "metric": "Available price measures",
                "value": str(len(available_measures)),
                "detail": _format_market_price_measure_names(available_measures),
            },
        ],
        schema=_MARKET_PRICE_KPI_SCHEMA,
    )


def market_price_type_summary_frame(
    load: GasTableLoad | None,
    price_type_filter: str = MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    source_system_filter: str = MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
    source_table_filter: str = MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
) -> pl.DataFrame:
    """Return source and price-type summaries for loaded market price rows."""
    dataframe = _filtered_market_price_dataframe(
        load,
        price_type_filter,
        source_system_filter,
        source_table_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_MARKET_PRICE_TYPE_SUMMARY_SCHEMA)

    summary = (
        dataframe.group_by("source_system", "source_table", "price_type")
        .agg(
            pl.len().alias("observations"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("price_value_gst_ex")
            .mean()
            .round(4)
            .alias("avg price_value_gst_ex"),
            pl.col("weighted_average_price_gst_ex")
            .mean()
            .round(4)
            .alias("avg weighted_average_price_gst_ex"),
            pl.col("cumulative_price")
            .drop_nulls()
            .last()
            .alias("latest cumulative_price"),
            pl.col("administered_price")
            .drop_nulls()
            .last()
            .alias("latest administered_price"),
            *_market_price_measure_count_expressions(),
        )
        .with_columns(_market_price_measure_count_label_expression())
        .sort(
            ["observations", "source_system", "source_table", "price_type"],
            descending=[True, False, False, False],
        )
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
                "price_type": "price type",
            }
        )
    )
    return summary.select([*list(_MARKET_PRICE_TYPE_SUMMARY_SCHEMA)])


def market_price_trend_frame(
    load: GasTableLoad | None,
    price_type_filter: str = MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    source_system_filter: str = MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
    source_table_filter: str = MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_MARKET_PRICE_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return a bounded recent trend table by gas date, source, and price type."""
    dataframe = _filtered_market_price_dataframe(
        load,
        price_type_filter,
        source_system_filter,
        source_table_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_MARKET_PRICE_TREND_SCHEMA)

    trend = (
        dataframe.group_by("gas_date", "source_system", "price_type")
        .agg(
            pl.len().alias("observations"),
            pl.col("source_table").drop_nulls().n_unique().alias("source tables"),
            pl.col("price_value_gst_ex")
            .mean()
            .round(4)
            .alias("avg price_value_gst_ex"),
            pl.col("weighted_average_price_gst_ex")
            .mean()
            .round(4)
            .alias("avg weighted_average_price_gst_ex"),
            pl.col("cumulative_price").mean().round(4).alias("avg cumulative_price"),
            pl.col("administered_price")
            .mean()
            .round(4)
            .alias("avg administered_price"),
            *_market_price_measure_count_expressions(),
        )
        .with_columns(_market_price_measure_count_label_expression())
        .sort(
            ["gas_date", "source_system", "price_type"],
            descending=[True, False, False],
            nulls_last=True,
        )
        .rename(
            {
                "gas_date": "gas date",
                "source_system": "source system",
                "price_type": "price type",
            }
        )
        .head(max(1, preview_rows))
    )
    return trend.select([*list(_MARKET_PRICE_TREND_SCHEMA)])


def market_price_observation_frame(
    load: GasTableLoad | None,
    price_type_filter: str = MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    source_system_filter: str = MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
    source_table_filter: str = MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_MARKET_PRICE_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return filtered market price observations for bounded detail preview."""
    dataframe = _filtered_market_price_dataframe(
        load,
        price_type_filter,
        source_system_filter,
        source_table_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_MARKET_PRICE_OBSERVATION_SCHEMA)

    return (
        dataframe.with_columns(_market_price_measure_value_label_expression())
        .sort(
            [
                "gas_date",
                "source_last_updated_timestamp",
                "price_type",
                "source_system",
                "source_table",
            ],
            descending=[True, True, False, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("gas_date").alias("gas date"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("price_type").alias("price type"),
            pl.col("schedule_type_id").alias("schedule type"),
            pl.col("schedule_interval").alias("schedule interval"),
            pl.col("transmission_id").alias("transmission"),
            pl.col("source_location_id").alias("source location"),
            pl.col("available price measures"),
            pl.col("price_value_gst_ex"),
            pl.col("weighted_average_price_gst_ex"),
            pl.col("cumulative_price"),
            pl.col("administered_price"),
            pl.col("source_last_updated_timestamp").alias("source updated"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def market_price_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched market prices."""
    table_label = _markdown_breakable_text(
        "silver.gas_model.silver_gas_fact_market_price"
    )
    if load is None:
        status_detail = "The dashboard did not receive a market price load result."
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = (
                "The current filters do not match any loaded market price rows."
            )
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No market price data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    price type, source system, source table, gas date, schedule context fields,
    and available price measures.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` market price asset, then use
    **Refresh data**.
    """


def render_market_price_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Market price dashboard links and related Schedule context state."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        "gas-market-prices",
        "gas-market-overview",
        "schedule-context",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_market_price_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="market-price-links__empty">'
            "No Market price or Schedule context entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_market_price_context_links_css()}
</style>
<section class="market-price-links" aria-label="Market price context links">
    <div>
        <p class="market-price-links__eyebrow">Context links</p>
        <h2>Market price and Schedule context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def schedule_run_gas_date_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return gas-date filter options for the loaded schedule run preview."""
    dataframe = _normalised_schedule_run_dataframe(load)
    if dataframe.is_empty():
        return (SCHEDULE_RUN_GAS_DATE_FILTER_ALL,)

    values = sorted(
        str(value)
        for value in dataframe.get_column("gas_date").drop_nulls().unique().to_list()
        if value is not None
    )
    return (SCHEDULE_RUN_GAS_DATE_FILTER_ALL, *reversed(values))


def schedule_run_source_system_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-system filter options for the loaded schedule run preview."""
    return _schedule_run_string_filter_options(
        load,
        "source_system",
        SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    )


def schedule_run_schedule_type_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return schedule-type filter options for the loaded schedule run preview."""
    return _schedule_run_string_filter_options(
        load,
        "schedule_type_id",
        SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
    )


def schedule_run_kpi_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
    source_system_filter: str = SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    schedule_type_filter: str = SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
) -> pl.DataFrame:
    """Return first-viewport KPIs for loaded schedule run rows."""
    dataframe = _filtered_schedule_run_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        schedule_type_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SCHEDULE_RUN_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_runs"),
        pl.col("schedule_type_id").drop_nulls().n_unique().alias("schedule_types"),
        pl.col("source_system").drop_nulls().n_unique().alias("source_systems"),
        pl.col("transmission_id").drop_nulls().n_unique().alias("transmissions"),
        pl.col("forecast_demand_version")
        .drop_nulls()
        .n_unique()
        .alias("forecast_demand_versions"),
        pl.col("gas_date").max().alias("latest_gas_date"),
        pl.col("approval_timestamp").max().alias("latest_approval"),
    ).row(0, named=True)
    row_limit = None if load is None else load.row_limit

    return pl.DataFrame(
        [
            {
                "metric": "Loaded schedule runs",
                "value": f"{counts['loaded_runs']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Schedule types",
                "value": f"{counts['schedule_types']:,}",
                "detail": "Distinct schedule_type_id values in the current view",
            },
            {
                "metric": "Source systems",
                "value": f"{counts['source_systems']:,}",
                "detail": "Distinct source_system values in the current view",
            },
            {
                "metric": "Transmissions",
                "value": f"{counts['transmissions']:,}",
                "detail": "Distinct transmission_id values in the current view",
            },
            {
                "metric": "Forecast demand versions",
                "value": f"{counts['forecast_demand_versions']:,}",
                "detail": "Distinct forecast_demand_version values represented",
            },
            {
                "metric": "Latest gas date",
                "value": _format_optional_value(counts["latest_gas_date"]),
                "detail": "Maximum gas_date in the loaded bounded rows",
            },
            {
                "metric": "Latest approval",
                "value": _format_optional_value(counts["latest_approval"]),
                "detail": "Maximum approval_timestamp in the current view",
            },
        ],
        schema=_SCHEDULE_RUN_KPI_SCHEMA,
    )


def schedule_run_type_summary_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
    source_system_filter: str = SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    schedule_type_filter: str = SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
) -> pl.DataFrame:
    """Return schedule type, transmission, and forecast-version summaries."""
    dataframe = _filtered_schedule_run_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        schedule_type_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SCHEDULE_RUN_TYPE_SUMMARY_SCHEMA)

    summary = (
        dataframe.group_by(
            "source_system",
            "source_table",
            "schedule_type_id",
            "forecast_demand_version",
        )
        .agg(
            pl.len().alias("runs"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("transmission_id").drop_nulls().n_unique().alias("transmissions"),
            pl.col("transmission_document_id")
            .drop_nulls()
            .n_unique()
            .alias("transmission documents"),
            pl.col("transmission_group_id")
            .drop_nulls()
            .n_unique()
            .alias("transmission groups"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("creation_timestamp").max().alias("latest creation"),
            pl.col("approval_timestamp").max().alias("latest approval"),
        )
        .sort(
            [
                "runs",
                "latest gas date",
                "source_system",
                "schedule_type_id",
                "forecast_demand_version",
            ],
            descending=[True, True, False, False, False],
            nulls_last=True,
        )
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
                "schedule_type_id": "schedule type",
                "forecast_demand_version": "forecast demand version",
            }
        )
    )
    return summary.select([*list(_SCHEDULE_RUN_TYPE_SUMMARY_SCHEMA)])


def schedule_run_timestamp_summary_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
    source_system_filter: str = SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    schedule_type_filter: str = SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_SCHEDULE_RUN_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return bounded timestamp coverage by Gas Day, source, and schedule type."""
    dataframe = _filtered_schedule_run_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        schedule_type_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SCHEDULE_RUN_TIMESTAMP_SUMMARY_SCHEMA)

    summary = (
        dataframe.group_by("gas_date", "source_system", "schedule_type_id")
        .agg(
            pl.len().alias("runs"),
            pl.col("gas_start_timestamp").min().alias("first gas start"),
            pl.col("gas_start_timestamp").max().alias("latest gas start"),
            pl.col("bid_cutoff_timestamp").max().alias("latest bid cutoff"),
            pl.col("creation_timestamp").max().alias("latest creation"),
            pl.col("approval_timestamp").max().alias("latest approval"),
        )
        .sort(
            ["gas_date", "source_system", "schedule_type_id"],
            descending=[True, False, False],
            nulls_last=True,
        )
        .rename(
            {
                "gas_date": "gas date",
                "source_system": "source system",
                "schedule_type_id": "schedule type",
            }
        )
        .head(max(1, preview_rows))
    )
    return summary.select([*list(_SCHEDULE_RUN_TIMESTAMP_SUMMARY_SCHEMA)])


def schedule_run_source_coverage_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
    source_system_filter: str = SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    schedule_type_filter: str = SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
) -> pl.DataFrame:
    """Return source coverage for loaded schedule run rows."""
    dataframe = _filtered_schedule_run_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        schedule_type_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SCHEDULE_RUN_SOURCE_COVERAGE_SCHEMA)

    return (
        dataframe.group_by("source_system", "source_table")
        .agg(
            pl.len().alias("schedule runs"),
            pl.col("schedule_type_id").drop_nulls().n_unique().alias("schedule types"),
            pl.col("forecast_demand_version")
            .drop_nulls()
            .n_unique()
            .alias("forecast demand versions"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(["schedule runs", "source_table"], descending=[True, False])
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
            }
        )
    )


def schedule_run_observation_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
    source_system_filter: str = SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    schedule_type_filter: str = SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_SCHEDULE_RUN_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return filtered schedule run observations for bounded detail preview."""
    dataframe = _filtered_schedule_run_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        schedule_type_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SCHEDULE_RUN_OBSERVATION_SCHEMA)

    return (
        dataframe.sort(
            [
                "gas_date",
                "approval_timestamp",
                "creation_timestamp",
                "source_system",
                "schedule_type_id",
                "transmission_id",
            ],
            descending=[True, True, True, False, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("gas_date").alias("gas date"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("schedule_type_id").alias("schedule type"),
            pl.col("forecast_demand_version").alias("forecast demand version"),
            pl.col("demand_type_id").alias("demand type"),
            pl.col("transmission_id").alias("transmission"),
            pl.col("transmission_document_id").alias("transmission document"),
            pl.col("transmission_group_id").alias("transmission group"),
            pl.col("objective_function_value").alias("objective function value"),
            pl.col("gas_start_timestamp").alias("gas start"),
            pl.col("bid_cutoff_timestamp").alias("bid cutoff"),
            pl.col("creation_timestamp").alias("created"),
            pl.col("approval_timestamp").alias("approved"),
            pl.col("source_last_updated_timestamp").alias("source updated"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def schedule_run_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched schedule runs."""
    table_label = _markdown_breakable_text(
        "silver.gas_model.silver_gas_fact_schedule_run"
    )
    if load is None:
        status_detail = "The dashboard did not receive a schedule run load result."
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = (
                "The current filters do not match any loaded schedule run rows."
            )
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No schedule run data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    Gas Day, source system, schedule type, forecast demand version,
    transmission identifiers, schedule timestamps, and source coverage fields.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` schedule run asset, then use
    **Refresh data**.
    """


def render_schedule_run_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Schedule run dashboard links to Schedule and Settlement context."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        "gas-schedule-runs",
        "gas-market-overview",
        "schedule-context",
        "gas-day-context",
        "settlement-context",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_schedule_run_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="schedule-run-links__empty">'
            "No Schedule, Gas Day, or Settlement context entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_schedule_run_context_links_css()}
</style>
<section class="schedule-run-links" aria-label="Schedule run context links">
    <div>
        <p class="schedule-run-links__eyebrow">Context links</p>
        <h2>Schedule run, Gas Day, and Settlement context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def settlement_activity_gas_date_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return gas-date filter options for loaded settlement activity rows."""
    dataframe = _normalised_settlement_activity_dataframe(load)
    if dataframe.is_empty():
        return (SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,)

    values = sorted(
        str(value)
        for value in dataframe.get_column("gas_date").drop_nulls().unique().to_list()
        if value is not None
    )
    return (SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL, *reversed(values))


def settlement_activity_source_system_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-system filter options for loaded settlement activity rows."""
    return _settlement_activity_string_filter_options(
        load,
        "source_system",
        SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
    )


def settlement_activity_activity_type_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return activity-type filter options for loaded settlement activity rows."""
    return _settlement_activity_string_filter_options(
        load,
        "activity_type",
        SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
    )


def settlement_activity_kpi_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
    source_system_filter: str = SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
    activity_type_filter: str = SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
) -> pl.DataFrame:
    """Return first-viewport KPIs for loaded settlement activity rows."""
    dataframe = _filtered_settlement_activity_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        activity_type_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SETTLEMENT_ACTIVITY_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_rows"),
        pl.col("activity_type").drop_nulls().n_unique().alias("activity_types"),
        pl.col("source_system").drop_nulls().n_unique().alias("source_systems"),
        pl.col("settlement_version_id")
        .drop_nulls()
        .n_unique()
        .alias("settlement_versions"),
        pl.col("schedule_no").drop_nulls().n_unique().alias("schedules"),
        pl.col("network_name").drop_nulls().n_unique().alias("networks"),
        pl.col("participant_name").drop_nulls().n_unique().alias("participants"),
        pl.col("amount_gst_ex").is_not_null().sum().alias("amount_rows"),
        pl.col("amount_gst_ex").sum().round(4).alias("total_amount"),
        pl.col("quantity_gj").is_not_null().sum().alias("quantity_rows"),
        pl.col("quantity_gj").sum().round(4).alias("total_quantity"),
        pl.col("percentage").is_not_null().sum().alias("percentage_rows"),
        pl.col("percentage").min().alias("min_percentage"),
        pl.col("percentage").max().alias("max_percentage"),
        pl.col("gas_date").max().alias("latest_gas_date"),
    ).row(0, named=True)
    row_limit = None if load is None else load.row_limit

    return pl.DataFrame(
        [
            {
                "metric": "Loaded settlement activity rows",
                "value": f"{counts['loaded_rows']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Activity types",
                "value": f"{counts['activity_types']:,}",
                "detail": "Distinct activity_type values in the current view",
            },
            {
                "metric": "Source systems",
                "value": f"{counts['source_systems']:,}",
                "detail": "Distinct source_system values in the current view",
            },
            {
                "metric": "Settlement versions",
                "value": f"{counts['settlement_versions']:,}",
                "detail": "Distinct settlement_version_id values represented",
            },
            {
                "metric": "Schedules",
                "value": f"{counts['schedules']:,}",
                "detail": "Distinct schedule_no values represented",
            },
            {
                "metric": "Networks",
                "value": f"{counts['networks']:,}",
                "detail": "Distinct network_name values represented",
            },
            {
                "metric": "Participants",
                "value": f"{counts['participants']:,}",
                "detail": "Distinct participant_name values represented",
            },
            {
                "metric": "Amount GST ex",
                "value": _format_measure_total(
                    counts["total_amount"],
                    counts["amount_rows"],
                ),
                "detail": (f"{counts['amount_rows']:,} populated amount_gst_ex rows"),
            },
            {
                "metric": "Quantity",
                "value": _format_measure_total(
                    counts["total_quantity"],
                    counts["quantity_rows"],
                    suffix=" GJ",
                ),
                "detail": f"{counts['quantity_rows']:,} populated quantity_gj rows",
            },
            {
                "metric": "Percentage range",
                "value": _format_measure_range(
                    counts["min_percentage"],
                    counts["max_percentage"],
                    counts["percentage_rows"],
                ),
                "detail": f"{counts['percentage_rows']:,} populated percentage rows",
            },
            {
                "metric": "Latest gas date",
                "value": _format_optional_value(counts["latest_gas_date"]),
                "detail": "Maximum gas_date in the loaded bounded rows",
            },
        ],
        schema=_SETTLEMENT_ACTIVITY_KPI_SCHEMA,
    )


def settlement_activity_summary_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
    source_system_filter: str = SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
    activity_type_filter: str = SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
) -> pl.DataFrame:
    """Return activity, settlement-version, and populated-measure summaries."""
    dataframe = _filtered_settlement_activity_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        activity_type_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SETTLEMENT_ACTIVITY_SUMMARY_SCHEMA)

    summary = (
        dataframe.group_by(
            "source_system",
            "source_table",
            "activity_type",
            "settlement_version_id",
        )
        .agg(
            pl.len().alias("rows"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("schedule_no").drop_nulls().n_unique().alias("schedules"),
            pl.col("network_name").drop_nulls().n_unique().alias("networks"),
            pl.col("participant_name").drop_nulls().n_unique().alias("participants"),
            pl.col("amount_gst_ex").is_not_null().sum().alias("amount rows"),
            pl.col("amount_gst_ex").sum().round(4).alias("total amount gst ex"),
            pl.col("quantity_gj").is_not_null().sum().alias("quantity rows"),
            pl.col("quantity_gj").sum().round(4).alias("total quantity gj"),
            pl.col("percentage").is_not_null().sum().alias("percentage rows"),
            pl.col("percentage").mean().round(4).alias("avg percentage"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
        )
        .sort(
            [
                "rows",
                "latest gas date",
                "source_system",
                "activity_type",
                "settlement_version_id",
            ],
            descending=[True, True, False, False, False],
            nulls_last=True,
        )
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
                "activity_type": "activity type",
                "settlement_version_id": "settlement version",
            }
        )
    )
    return summary.select([*list(_SETTLEMENT_ACTIVITY_SUMMARY_SCHEMA)])


def settlement_activity_source_coverage_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
    source_system_filter: str = SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
    activity_type_filter: str = SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
) -> pl.DataFrame:
    """Return source coverage for loaded settlement activity rows."""
    dataframe = _filtered_settlement_activity_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        activity_type_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SETTLEMENT_ACTIVITY_SOURCE_COVERAGE_SCHEMA)

    return (
        dataframe.group_by("source_system", "source_table")
        .agg(
            pl.len().alias("rows"),
            pl.col("activity_type").drop_nulls().n_unique().alias("activity types"),
            pl.col("settlement_version_id")
            .drop_nulls()
            .n_unique()
            .alias("settlement versions"),
            pl.col("schedule_no").drop_nulls().n_unique().alias("schedules"),
            pl.col("network_name").drop_nulls().n_unique().alias("networks"),
            pl.col("participant_name").drop_nulls().n_unique().alias("participants"),
            pl.col("amount_gst_ex").is_not_null().sum().alias("amount rows"),
            pl.col("quantity_gj").is_not_null().sum().alias("quantity rows"),
            pl.col("percentage").is_not_null().sum().alias("percentage rows"),
            pl.col("source_file").drop_nulls().n_unique().alias("source files"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(["rows", "source_table"], descending=[True, False])
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
            }
        )
    )


def settlement_activity_observation_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
    source_system_filter: str = SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
    activity_type_filter: str = SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_SETTLEMENT_ACTIVITY_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return filtered settlement activity observations for bounded preview."""
    dataframe = _filtered_settlement_activity_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        activity_type_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_SETTLEMENT_ACTIVITY_OBSERVATION_SCHEMA)

    return (
        dataframe.sort(
            [
                "gas_date",
                "source_last_updated_timestamp",
                "source_system",
                "activity_type",
                "settlement_version_id",
                "schedule_no",
            ],
            descending=[True, True, False, False, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("gas_date").alias("gas date"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("settlement_version_id").alias("settlement version"),
            pl.col("activity_type").alias("activity type"),
            pl.col("schedule_no").alias("schedule"),
            pl.col("network_name").alias("network"),
            pl.col("participant_name").alias("participant"),
            pl.col("amount_gst_ex"),
            pl.col("quantity_gj"),
            pl.col("percentage"),
            pl.col("source_last_updated_timestamp").alias("source updated"),
            pl.col("source_file").alias("source file"),
            pl.col("source_surrogate_key").alias("source identifier"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def settlement_activity_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched settlement rows."""
    table_label = _markdown_breakable_text(
        "silver.gas_model.silver_gas_fact_settlement_activity"
    )
    if load is None:
        status_detail = (
            "The dashboard did not receive a settlement activity load result."
        )
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = (
                "The current filters do not match any loaded settlement activity rows."
            )
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No settlement activity data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    settlement version, activity type, schedule, network, participant, amount,
    quantity, percentage, Gas Day, source-system, and source-table fields.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` settlement activity asset, then
    use **Refresh data**.
    """


def render_settlement_activity_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Settlement activity links to related Market context panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        "settlement-context",
        "allocation-context",
        "participant-context",
        "gas-day-context",
        "schedule-context",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_settlement_activity_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="settlement-activity-links__empty">'
            "No Settlement, Allocation, Participant, Gas Day, or Schedule "
            "context entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_settlement_activity_context_links_css()}
</style>
<section
    class="settlement-activity-links"
    aria-label="Settlement activity context links"
>
    <div>
        <p class="settlement-activity-links__eyebrow">Context links</p>
        <h2>Settlement, Allocation, Participant, Gas Day, and Schedule context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def customer_transfer_gas_date_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return gas-date filter options for loaded customer transfer rows."""
    dataframe = _normalised_customer_transfer_dataframe(load)
    if dataframe.is_empty():
        return (CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,)

    values = sorted(
        str(value)
        for value in dataframe.get_column("gas_date").drop_nulls().unique().to_list()
        if value is not None
    )
    return (CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL, *reversed(values))


def customer_transfer_market_code_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return market-code filter options for loaded customer transfer rows."""
    return _customer_transfer_string_filter_options(
        load,
        "market_code",
        CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    )


def customer_transfer_source_system_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-system filter options for loaded customer transfer rows."""
    return _customer_transfer_string_filter_options(
        load,
        "source_system",
        CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
    )


def customer_transfer_kpi_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
    market_code_filter: str = CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    source_system_filter: str = CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return first-viewport KPIs for loaded customer transfer rows."""
    dataframe = _filtered_customer_transfer_dataframe(
        load,
        gas_date_filter,
        market_code_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CUSTOMER_TRANSFER_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_rows"),
        pl.col("market_code").drop_nulls().n_unique().alias("market_codes"),
        pl.col("source_system").drop_nulls().n_unique().alias("source_systems"),
        pl.col("transfers_lodged").is_not_null().sum().alias("lodged_rows"),
        pl.col("transfers_lodged").sum().alias("transfers_lodged"),
        pl.col("transfers_completed").is_not_null().sum().alias("completed_rows"),
        pl.col("transfers_completed").sum().alias("transfers_completed"),
        pl.col("transfers_cancelled").is_not_null().sum().alias("cancelled_rows"),
        pl.col("transfers_cancelled").sum().alias("transfers_cancelled"),
        pl.col("int_transfers_lodged")
        .is_not_null()
        .sum()
        .alias("internal_lodged_rows"),
        pl.col("int_transfers_lodged").sum().alias("internal_transfers_lodged"),
        pl.col("int_transfers_completed")
        .is_not_null()
        .sum()
        .alias("internal_completed_rows"),
        pl.col("int_transfers_completed").sum().alias("internal_transfers_completed"),
        pl.col("int_transfers_cancelled")
        .is_not_null()
        .sum()
        .alias("internal_cancelled_rows"),
        pl.col("int_transfers_cancelled").sum().alias("internal_transfers_cancelled"),
        pl.col("greenfields_received").is_not_null().sum().alias("greenfield_rows"),
        pl.col("greenfields_received").sum().alias("greenfields_received"),
        pl.col("gas_date").max().alias("latest_gas_date"),
    ).row(0, named=True)
    row_limit = None if load is None else load.row_limit

    return pl.DataFrame(
        [
            {
                "metric": "Loaded customer transfer rows",
                "value": f"{counts['loaded_rows']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Market codes",
                "value": f"{counts['market_codes']:,}",
                "detail": "Distinct market_code values in the current view",
            },
            {
                "metric": "Source systems",
                "value": f"{counts['source_systems']:,}",
                "detail": "Distinct source_system values in the current view",
            },
            {
                "metric": "Transfers lodged",
                "value": _format_measure_total(
                    counts["transfers_lodged"],
                    counts["lodged_rows"],
                ),
                "detail": f"{counts['lodged_rows']:,} populated transfers_lodged rows",
            },
            {
                "metric": "Transfers completed",
                "value": _format_measure_total(
                    counts["transfers_completed"],
                    counts["completed_rows"],
                ),
                "detail": (
                    f"{counts['completed_rows']:,} populated transfers_completed rows"
                ),
            },
            {
                "metric": "Transfers cancelled",
                "value": _format_measure_total(
                    counts["transfers_cancelled"],
                    counts["cancelled_rows"],
                ),
                "detail": (
                    f"{counts['cancelled_rows']:,} populated transfers_cancelled rows"
                ),
            },
            {
                "metric": "Internal transfers lodged",
                "value": _format_measure_total(
                    counts["internal_transfers_lodged"],
                    counts["internal_lodged_rows"],
                ),
                "detail": (
                    f"{counts['internal_lodged_rows']:,} populated "
                    "int_transfers_lodged rows"
                ),
            },
            {
                "metric": "Internal transfers completed",
                "value": _format_measure_total(
                    counts["internal_transfers_completed"],
                    counts["internal_completed_rows"],
                ),
                "detail": (
                    f"{counts['internal_completed_rows']:,} populated "
                    "int_transfers_completed rows"
                ),
            },
            {
                "metric": "Internal transfers cancelled",
                "value": _format_measure_total(
                    counts["internal_transfers_cancelled"],
                    counts["internal_cancelled_rows"],
                ),
                "detail": (
                    f"{counts['internal_cancelled_rows']:,} populated "
                    "int_transfers_cancelled rows"
                ),
            },
            {
                "metric": "Greenfields received",
                "value": _format_measure_total(
                    counts["greenfields_received"],
                    counts["greenfield_rows"],
                ),
                "detail": (
                    f"{counts['greenfield_rows']:,} populated greenfields_received rows"
                ),
            },
            {
                "metric": "Latest gas date",
                "value": _format_optional_value(counts["latest_gas_date"]),
                "detail": "Maximum gas_date in the loaded bounded rows",
            },
        ],
        schema=_CUSTOMER_TRANSFER_KPI_SCHEMA,
    )


def customer_transfer_summary_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
    market_code_filter: str = CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    source_system_filter: str = CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return market-code customer transfer summaries."""
    dataframe = _filtered_customer_transfer_dataframe(
        load,
        gas_date_filter,
        market_code_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CUSTOMER_TRANSFER_SUMMARY_SCHEMA)

    summary = (
        dataframe.group_by("market_code", "source_system", "source_table")
        .agg(
            pl.len().alias("rows"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("transfers_lodged").sum().alias("transfers lodged"),
            pl.col("transfers_completed").sum().alias("transfers completed"),
            pl.col("transfers_cancelled").sum().alias("transfers cancelled"),
            pl.col("int_transfers_lodged").sum().alias("internal transfers lodged"),
            pl.col("int_transfers_completed")
            .sum()
            .alias("internal transfers completed"),
            pl.col("int_transfers_cancelled")
            .sum()
            .alias("internal transfers cancelled"),
            pl.col("greenfields_received").sum().alias("greenfields received"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(
            ["transfers lodged", "latest gas date", "market_code"],
            descending=[True, True, False],
            nulls_last=True,
        )
        .rename(
            {
                "market_code": "market code",
                "source_system": "source system",
                "source_table": "source table",
            }
        )
    )
    return summary.select([*list(_CUSTOMER_TRANSFER_SUMMARY_SCHEMA)])


def customer_transfer_daily_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
    market_code_filter: str = CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    source_system_filter: str = CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_CUSTOMER_TRANSFER_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return bounded daily transfer totals by Gas Day and market code."""
    dataframe = _filtered_customer_transfer_dataframe(
        load,
        gas_date_filter,
        market_code_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CUSTOMER_TRANSFER_DAILY_SCHEMA)

    daily = (
        dataframe.group_by("gas_date", "market_code")
        .agg(
            pl.len().alias("rows"),
            pl.col("transfers_lodged").sum().alias("transfers lodged"),
            pl.col("transfers_completed").sum().alias("transfers completed"),
            pl.col("transfers_cancelled").sum().alias("transfers cancelled"),
            pl.col("int_transfers_lodged").sum().alias("internal transfers lodged"),
            pl.col("int_transfers_completed")
            .sum()
            .alias("internal transfers completed"),
            pl.col("int_transfers_cancelled")
            .sum()
            .alias("internal transfers cancelled"),
            pl.col("greenfields_received").sum().alias("greenfields received"),
        )
        .sort(
            ["gas_date", "market_code"],
            descending=[True, False],
            nulls_last=True,
        )
        .rename(
            {
                "gas_date": "gas date",
                "market_code": "market code",
            }
        )
        .head(max(1, preview_rows))
    )
    return daily.select([*list(_CUSTOMER_TRANSFER_DAILY_SCHEMA)])


def customer_transfer_source_coverage_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
    market_code_filter: str = CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    source_system_filter: str = CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return source coverage for loaded customer transfer rows."""
    dataframe = _filtered_customer_transfer_dataframe(
        load,
        gas_date_filter,
        market_code_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CUSTOMER_TRANSFER_SOURCE_COVERAGE_SCHEMA)

    return (
        dataframe.group_by("source_system", "source_table")
        .agg(
            pl.len().alias("rows"),
            pl.col("market_code").drop_nulls().n_unique().alias("market codes"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("source_file").drop_nulls().n_unique().alias("source files"),
            pl.col("source_surrogate_key")
            .drop_nulls()
            .n_unique()
            .alias("source identifiers"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(["rows", "source_table"], descending=[True, False])
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
            }
        )
    )


def customer_transfer_observation_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
    market_code_filter: str = CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    source_system_filter: str = CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_CUSTOMER_TRANSFER_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return filtered customer transfer observations for bounded preview."""
    dataframe = _filtered_customer_transfer_dataframe(
        load,
        gas_date_filter,
        market_code_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CUSTOMER_TRANSFER_OBSERVATION_SCHEMA)

    return (
        dataframe.sort(
            [
                "gas_date",
                "market_code",
                "ingested_timestamp",
                "source_system",
                "source_table",
            ],
            descending=[True, False, True, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("gas_date").alias("gas date"),
            pl.col("market_code").alias("market code"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("transfers_lodged"),
            pl.col("transfers_completed"),
            pl.col("transfers_cancelled"),
            pl.col("int_transfers_lodged"),
            pl.col("int_transfers_completed"),
            pl.col("int_transfers_cancelled"),
            pl.col("greenfields_received"),
            pl.col("source_file").alias("source file"),
            pl.col("source_surrogate_key").alias("source identifier"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def customer_transfer_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched transfer rows."""
    table_label = _markdown_breakable_text(
        "silver.gas_model.silver_gas_fact_customer_transfer"
    )
    if load is None:
        status_detail = "The dashboard did not receive a customer transfer load result."
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = (
                "The current filters do not match any loaded customer transfer rows."
            )
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No customer transfer data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    Gas Day, market code, transfers lodged, completed and cancelled, internal
    transfer counts, greenfields received, source-system, and source-table
    fields.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` customer transfer asset, then
    use **Refresh data**.
    """


def render_customer_transfer_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render customer transfer links to related Market context panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        "gas-customer-transfer-activity",
        "gas-market-overview",
        "participant-context",
        "gas-day-context",
        "settlement-context",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_customer_transfer_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="customer-transfer-links__empty">'
            "No Customer transfer, Participant, Gas Day, or Settlement context "
            "entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_customer_transfer_context_links_css()}
</style>
<section
    class="customer-transfer-links"
    aria-label="Customer transfer context links"
>
    <div>
        <p class="customer-transfer-links__eyebrow">Context links</p>
        <h2>Customer transfer, Participant, Gas Day, and Settlement context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def bid_stack_participant_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return participant filter options for the loaded Bid / Offer stack."""
    return _bid_stack_string_filter_options(
        load,
        "participant_id",
        BID_STACK_PARTICIPANT_FILTER_ALL,
    )


def bid_stack_facility_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return facility filter options for the loaded Bid / Offer stack."""
    return _bid_stack_string_filter_options(
        load,
        "source_facility_id",
        BID_STACK_FACILITY_FILTER_ALL,
    )


def bid_stack_zone_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return zone or hub filter options for the loaded Bid / Offer stack."""
    return _bid_stack_string_filter_options(
        load,
        "source_hub_id",
        BID_STACK_ZONE_FILTER_ALL,
    )


def bid_stack_source_system_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-system filter options for the loaded Bid / Offer stack."""
    return _bid_stack_string_filter_options(
        load,
        "source_system",
        BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
    )


def bid_stack_kpi_frame(
    load: GasTableLoad | None,
    participant_filter: str = BID_STACK_PARTICIPANT_FILTER_ALL,
    facility_filter: str = BID_STACK_FACILITY_FILTER_ALL,
    zone_filter: str = BID_STACK_ZONE_FILTER_ALL,
    source_system_filter: str = BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return first-viewport KPIs for loaded Bid / Offer stack rows."""
    dataframe = _filtered_bid_stack_dataframe(
        load,
        participant_filter,
        facility_filter,
        zone_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_BID_STACK_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_rows"),
        pl.col("source_system").drop_nulls().n_unique().alias("source_systems"),
        pl.col("participant_id").drop_nulls().n_unique().alias("participants"),
        pl.col("source_facility_id").drop_nulls().n_unique().alias("facilities"),
        pl.col("source_hub_id").drop_nulls().n_unique().alias("zones"),
        pl.col("bid_step").drop_nulls().n_unique().alias("bid_steps"),
        pl.col("bid_price").min().alias("min_bid_price"),
        pl.col("bid_price").max().alias("max_bid_price"),
        pl.col("bid_qty_gj").sum().alias("total_bid_qty_gj"),
        pl.col("source_surrogate_key")
        .drop_nulls()
        .n_unique()
        .alias("source_identifiers"),
        pl.col("gas_date").max().alias("latest_gas_date"),
    ).row(0, named=True)
    row_limit = None if load is None else load.row_limit

    return pl.DataFrame(
        [
            {
                "metric": "Loaded bid stack rows",
                "value": f"{counts['loaded_rows']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Source systems",
                "value": f"{counts['source_systems']:,}",
                "detail": "Distinct source_system values in the current view",
            },
            {
                "metric": "Participants",
                "value": f"{counts['participants']:,}",
                "detail": "Distinct participant_id values represented",
            },
            {
                "metric": "Facilities",
                "value": f"{counts['facilities']:,}",
                "detail": "Distinct source_facility_id values represented",
            },
            {
                "metric": "Zones",
                "value": f"{counts['zones']:,}",
                "detail": "Distinct source_hub_id values represented",
            },
            {
                "metric": "Bid steps",
                "value": f"{counts['bid_steps']:,}",
                "detail": "Distinct bid_step values represented",
            },
            {
                "metric": "Bid price range",
                "value": _format_numeric_range(
                    counts["min_bid_price"],
                    counts["max_bid_price"],
                ),
                "detail": "Minimum and maximum bid_price in the current view",
            },
            {
                "metric": "Loaded bid quantity",
                "value": _format_quantity(counts["total_bid_qty_gj"]),
                "detail": "Sum of bid_qty_gj in loaded bounded rows",
            },
            {
                "metric": "Accepted source identifiers",
                "value": f"{counts['source_identifiers']:,}",
                "detail": "Distinct source_surrogate_key values represented",
            },
            {
                "metric": "Latest gas date",
                "value": _format_optional_value(counts["latest_gas_date"]),
                "detail": "Maximum gas_date in the loaded bounded rows",
            },
        ],
        schema=_BID_STACK_KPI_SCHEMA,
    )


def bid_stack_step_summary_frame(
    load: GasTableLoad | None,
    participant_filter: str = BID_STACK_PARTICIPANT_FILTER_ALL,
    facility_filter: str = BID_STACK_FACILITY_FILTER_ALL,
    zone_filter: str = BID_STACK_ZONE_FILTER_ALL,
    source_system_filter: str = BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_BID_STACK_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return bid step, price, and quantity summaries for loaded rows."""
    dataframe = _filtered_bid_stack_dataframe(
        load,
        participant_filter,
        facility_filter,
        zone_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_BID_STACK_STEP_SUMMARY_SCHEMA)

    summary = (
        dataframe.group_by(
            "source_system",
            "source_hub_id",
            "source_facility_id",
            "bid_step",
        )
        .agg(
            pl.len().alias("rows"),
            pl.col("participant_id").drop_nulls().n_unique().alias("participants"),
            pl.col("bid_id").drop_nulls().n_unique().alias("bid ids"),
            pl.col("bid_price").min().alias("min bid price"),
            pl.col("bid_price").mean().round(4).alias("avg bid price"),
            pl.col("bid_price").max().alias("max bid price"),
            pl.col("bid_qty_gj").sum().round(4).alias("total bid quantity gj"),
            pl.col("step_qty_gj").sum().round(4).alias("total step quantity gj"),
            pl.col("gas_date").max().alias("latest gas date"),
        )
        .sort(
            ["latest gas date", "source_system", "source_hub_id", "bid_step"],
            descending=[True, False, False, False],
            nulls_last=True,
        )
        .rename(
            {
                "source_system": "source system",
                "source_hub_id": "zone",
                "source_facility_id": "facility",
                "bid_step": "bid step",
            }
        )
        .head(max(1, preview_rows))
    )
    return summary.select([*list(_BID_STACK_STEP_SUMMARY_SCHEMA)])


def bid_stack_source_summary_frame(
    load: GasTableLoad | None,
    participant_filter: str = BID_STACK_PARTICIPANT_FILTER_ALL,
    facility_filter: str = BID_STACK_FACILITY_FILTER_ALL,
    zone_filter: str = BID_STACK_ZONE_FILTER_ALL,
    source_system_filter: str = BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return source-system and accepted source identifier coverage."""
    dataframe = _filtered_bid_stack_dataframe(
        load,
        participant_filter,
        facility_filter,
        zone_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_BID_STACK_SOURCE_SUMMARY_SCHEMA)

    summary = (
        dataframe.group_by("source_system", "source_table", "source_report_id")
        .agg(
            pl.len().alias("rows"),
            pl.col("participant_id").drop_nulls().n_unique().alias("participants"),
            pl.col("source_facility_id").drop_nulls().n_unique().alias("facilities"),
            pl.col("source_hub_id").drop_nulls().n_unique().alias("zones"),
            pl.col("bid_id").drop_nulls().n_unique().alias("bid ids"),
            pl.col("bid_step").drop_nulls().n_unique().alias("bid steps"),
            pl.col("source_surrogate_key")
            .drop_nulls()
            .n_unique()
            .alias("accepted source identifiers"),
            pl.col("source_file").drop_nulls().n_unique().alias("source files"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(
            ["rows", "source_system", "source_table"], descending=[True, False, False]
        )
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
                "source_report_id": "source report",
            }
        )
    )
    return summary.select([*list(_BID_STACK_SOURCE_SUMMARY_SCHEMA)])


def bid_stack_observation_frame(
    load: GasTableLoad | None,
    participant_filter: str = BID_STACK_PARTICIPANT_FILTER_ALL,
    facility_filter: str = BID_STACK_FACILITY_FILTER_ALL,
    zone_filter: str = BID_STACK_ZONE_FILTER_ALL,
    source_system_filter: str = BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_BID_STACK_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return filtered Bid / Offer stack observations for bounded preview."""
    dataframe = _filtered_bid_stack_dataframe(
        load,
        participant_filter,
        facility_filter,
        zone_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_BID_STACK_OBSERVATION_SCHEMA)

    return (
        dataframe.sort(
            [
                "gas_date",
                "source_last_updated_timestamp",
                "source_system",
                "source_table",
                "participant_id",
                "source_facility_id",
                "bid_step",
            ],
            descending=[True, True, False, False, False, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("gas_date").alias("gas date"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("source_report_id").alias("source report"),
            pl.col("participant_id").alias("participant"),
            pl.col("participant_name").alias("participant name"),
            pl.col("source_hub_id").alias("zone"),
            pl.col("source_hub_name").alias("zone name"),
            pl.col("source_facility_id").alias("facility"),
            pl.col("facility_name").alias("facility name"),
            pl.col("source_point_id").alias("source point"),
            pl.col("schedule_identifier").alias("schedule identifier"),
            pl.col("bid_id").alias("bid id"),
            pl.col("bid_step").alias("bid step"),
            pl.col("bid_price").alias("bid price"),
            pl.col("bid_qty_gj").alias("bid quantity gj"),
            pl.col("step_qty_gj").alias("step quantity gj"),
            pl.col("offer_type").alias("offer type"),
            pl.col("inject_withdraw").alias("inject withdraw"),
            pl.col("schedule_type").alias("schedule type"),
            pl.col("schedule_time").alias("schedule time"),
            pl.col("bid_cutoff_timestamp").alias("bid cutoff"),
            pl.col("source_surrogate_key").alias("accepted source identifier"),
            pl.col("source_file").alias("source file"),
            pl.col("source_last_updated_timestamp").alias("source updated"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def bid_stack_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched bid stack data."""
    table_label = _markdown_breakable_text("silver.gas_model.silver_gas_fact_bid_stack")
    if load is None:
        status_detail = "The dashboard did not receive a Bid / Offer stack load result."
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = (
                "The current filters do not match any loaded Bid / Offer stack rows."
            )
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No Bid / Offer stack data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    participant, facility, zone, price, quantity, bid step, source system, and
    accepted source identifier fields.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` Bid / Offer stack asset, then
    use **Refresh data**.
    """


def render_bid_stack_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Bid / Offer stack links to related market context panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        "bid-offer-context",
        "participant-context",
        "facility-context",
        "schedule-context",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_bid_stack_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="bid-stack-links__empty">'
            "No Bid / Offer, Participant, Facility, or Schedule context entries "
            "are registered."
            "</li>"
        )

    return f"""\
<style>
{_bid_stack_context_links_css()}
</style>
<section class="bid-stack-links" aria-label="Bid / Offer stack context links">
    <div>
        <p class="bid-stack-links__eyebrow">Context links</p>
        <h2>Bid / Offer, Participant, Facility, and Schedule context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


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


def _source_coverage_table_name_from_registry_asset(asset: str) -> str | None:
    prefix = "silver.gas_model."
    if asset.startswith(prefix):
        return asset.removeprefix(prefix)
    return None


def _source_coverage_section(table_name: str) -> str:
    if table_name.startswith("silver_gas_dim_"):
        return "Dimensions"
    if table_name.startswith("silver_gas_fact_"):
        return "Facts"
    return "Associations"


def _source_coverage_label(table_name: str) -> str:
    label = table_name.removeprefix("silver_gas_")
    return label.replace("_", " ").title()


def _source_coverage_context_by_table_name(
    table_catalogue: Sequence[object],
) -> dict[str, _SourceCoverageContext]:
    contexts: dict[str, _SourceCoverageContext] = {}
    for entry in table_catalogue:
        table_name = _source_coverage_table_name_from_catalogue_entry(entry)
        if table_name is None or table_name in contexts:
            continue
        contexts[table_name] = _source_coverage_context_from_catalogue_entry(entry)
    return contexts


def _source_coverage_context_from_catalogue_entry(
    entry: object,
) -> _SourceCoverageContext:
    entry_id = _source_coverage_entry_id(entry)
    has_asset = getattr(entry, "asset", None) is not None
    uri = getattr(entry, "uri", None)
    uri_text = uri if isinstance(uri, str) else ""

    if entry_id == "":
        table_link = SOURCE_COVERAGE_TABLE_EXPLORER_ROUTE
        asset_link = ""
    else:
        encoded_entry_id = quote(entry_id, safe="")
        table_link = f"{SOURCE_COVERAGE_TABLE_EXPLORER_ROUTE}?table={encoded_entry_id}"
        asset_link = (
            f"{SOURCE_COVERAGE_TABLE_EXPLORER_ROUTE}?asset={encoded_entry_id}"
            if has_asset
            else ""
        )

    return _SourceCoverageContext(
        table_explorer_link=table_link,
        asset_metadata_link=asset_link,
        uri=uri_text,
    )


def _source_coverage_entry_id(entry: object) -> str:
    entry_id = getattr(entry, "entry_id", "")
    return entry_id if isinstance(entry_id, str) else ""


def _source_coverage_table_name_from_catalogue_entry(
    entry: object,
) -> str | None:
    for reference in _source_coverage_catalogue_references(entry):
        table_name = _source_coverage_table_name_from_reference(reference)
        if table_name is not None:
            return table_name
    return None


def _source_coverage_catalogue_references(entry: object) -> tuple[str, ...]:
    references: list[str] = []
    asset = getattr(entry, "asset", None)
    if asset is not None:
        _append_source_coverage_reference(references, asset, "asset_id")
        _append_source_coverage_reference(references, asset, "uri")

    table = getattr(entry, "table", None)
    if table is not None:
        _append_source_coverage_reference(references, table, "prefix")
        _append_source_coverage_reference(references, table, "uri")

    _append_source_coverage_reference(references, entry, "uri")
    return tuple(references)


def _append_source_coverage_reference(
    references: list[str],
    source: object,
    attribute: str,
) -> None:
    value = getattr(source, attribute, "")
    if isinstance(value, str):
        references.append(value)


def _source_coverage_table_name_from_reference(reference: str) -> str | None:
    dotted_prefix = "silver.gas_model."
    if reference.startswith(dotted_prefix):
        return reference.removeprefix(dotted_prefix).split(".", maxsplit=1)[0]

    path_marker = "silver/gas_model/"
    if path_marker not in reference:
        return None

    suffix = reference.split(path_marker, maxsplit=1)[1].strip("/")
    if suffix == "":
        return None
    return suffix.split("/", maxsplit=1)[0]


def _source_coverage_rows(
    load: GasTableLoad,
    context: _SourceCoverageContext | None,
) -> list[dict[str, object]]:
    dataframe = load.dataframe
    if load.error is not None:
        return [
            _source_coverage_row(
                load,
                context,
                source_system="",
                source_table="",
                coverage_state=SOURCE_COVERAGE_STATE_UNAVAILABLE,
                rows_loaded=0,
                source_fields="",
                detail=f"Read detail: {load.error}",
            )
        ]

    if dataframe is None or dataframe.is_empty():
        return [
            _source_coverage_row(
                load,
                context,
                source_system="",
                source_table="",
                coverage_state=SOURCE_COVERAGE_STATE_EMPTY,
                rows_loaded=0,
                source_fields="",
                detail="The table read succeeded but returned no rows.",
            )
        ]

    source_fields = _source_coverage_field_label(dataframe)
    counts, gap_details = _source_coverage_counts(dataframe)
    rows = [
        _source_coverage_row(
            load,
            context,
            source_system=source_system,
            source_table=source_table,
            coverage_state=_source_coverage_state(source_system),
            rows_loaded=count,
            source_fields=source_fields,
            detail=_source_coverage_detail(source_system),
        )
        for (source_system, source_table), count in sorted(
            counts.items(),
            key=_source_coverage_count_sort_key,
        )
    ]
    rows.extend(
        _source_coverage_row(
            load,
            context,
            source_system=source_system,
            source_table=source_table,
            coverage_state=SOURCE_COVERAGE_STATE_GAP,
            rows_loaded=count,
            source_fields=source_fields,
            detail=detail,
        )
        for (source_system, source_table, detail), count in sorted(
            gap_details.items(),
            key=_source_coverage_gap_sort_key,
        )
    )

    return rows


def _source_coverage_counts(
    dataframe: pl.DataFrame,
) -> tuple[dict[tuple[str, str], int], dict[tuple[str, str, str], int]]:
    source_system_column_available = "source_system" in dataframe.columns
    source_table_columns = tuple(
        column
        for column in ("source_table", "source_tables")
        if column in dataframe.columns
    )
    counts: dict[tuple[str, str], int] = {}
    gap_details: dict[tuple[str, str, str], int] = {}

    for row in dataframe.to_dicts():
        source_systems = _source_coverage_row_values(
            row,
            "source_system",
            missing_label=_SOURCE_COVERAGE_MISSING_SOURCE_SYSTEM_COLUMN,
            empty_label=_SOURCE_COVERAGE_EMPTY_SOURCE_SYSTEM_VALUE,
            column_available=source_system_column_available,
        )
        source_tables = _source_coverage_source_table_values(row, source_table_columns)
        for source_system in source_systems:
            if source_tables:
                for source_table in source_tables:
                    key = (source_system, source_table)
                    counts[key] = counts.get(key, 0) + 1
                continue

            source_table_label = (
                _SOURCE_COVERAGE_MISSING_SOURCE_TABLE_COLUMN
                if len(source_table_columns) == 0
                else _SOURCE_COVERAGE_EMPTY_SOURCE_TABLE_VALUE
            )
            gap_key = (
                source_system,
                source_table_label,
                _source_coverage_gap_detail(source_table_columns),
            )
            gap_details[gap_key] = gap_details.get(gap_key, 0) + 1

    return counts, gap_details


def _source_coverage_row_values(
    row: Mapping[str, object],
    column: str,
    *,
    missing_label: str,
    empty_label: str,
    column_available: bool,
) -> tuple[str, ...]:
    if not column_available:
        return (missing_label,)

    values = _source_coverage_value_strings(row.get(column))
    if values:
        return values
    return (empty_label,)


def _source_coverage_source_table_values(
    row: Mapping[str, object],
    source_table_columns: Sequence[str],
) -> tuple[str, ...]:
    values: list[str] = []
    for column in source_table_columns:
        values.extend(_source_coverage_value_strings(row.get(column)))
    return tuple(dict.fromkeys(values))


def _source_coverage_value_strings(value: object | None) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, float) and isnan(value):
        return ()
    if isinstance(value, str):
        stripped = value.strip()
        return (stripped,) if stripped else ()
    if isinstance(value, Sequence) and not isinstance(value, bytes):
        values: list[str] = []
        for item in value:
            values.extend(_source_coverage_value_strings(item))
        return tuple(dict.fromkeys(values))

    text = str(value).strip()
    return (text,) if text else ()


def _source_coverage_gap_detail(source_table_columns: Sequence[str]) -> str:
    if len(source_table_columns) == 0:
        return (
            "Missing source_table/source_tables columns; cannot identify source "
            "tables for these loaded rows."
        )
    return (
        "source_table/source_tables columns are present but empty for these "
        "loaded rows."
    )


def _source_coverage_state(source_system: str) -> str:
    if source_system in {
        _SOURCE_COVERAGE_MISSING_SOURCE_SYSTEM_COLUMN,
        _SOURCE_COVERAGE_EMPTY_SOURCE_SYSTEM_VALUE,
    }:
        return SOURCE_COVERAGE_STATE_GAP
    return SOURCE_COVERAGE_STATE_COVERED


def _source_coverage_detail(source_system: str) -> str:
    if source_system == _SOURCE_COVERAGE_MISSING_SOURCE_SYSTEM_COLUMN:
        return "Missing source_system column; source table values were present."
    if source_system == _SOURCE_COVERAGE_EMPTY_SOURCE_SYSTEM_VALUE:
        return "source_system column is present but empty for these loaded rows."
    return "source_system and source table metadata are populated in loaded rows."


def _source_coverage_row(
    load: GasTableLoad,
    context: _SourceCoverageContext | None,
    *,
    source_system: str,
    source_table: str,
    coverage_state: str,
    rows_loaded: int,
    source_fields: str,
    detail: str,
) -> dict[str, object]:
    return {
        "asset": f"silver.gas_model.{load.spec.table_name}",
        "section": load.spec.section,
        "table": load.spec.table_name,
        "source system": source_system,
        "source table": source_table,
        "coverage state": coverage_state,
        "rows loaded": rows_loaded,
        "row limit": format_row_limit(load.row_limit),
        "source fields": source_fields,
        "table explorer": _source_coverage_table_explorer_link(load, context),
        "asset metadata": "" if context is None else context.asset_metadata_link,
        "uri": load.uri if context is None or context.uri == "" else context.uri,
        "detail": detail,
    }


def _source_coverage_table_explorer_link(
    load: GasTableLoad,
    context: _SourceCoverageContext | None,
) -> str:
    if context is not None and context.table_explorer_link != "":
        return context.table_explorer_link
    table_name = quote(load.spec.table_name, safe="")
    return f"{SOURCE_COVERAGE_TABLE_EXPLORER_ROUTE}?search={table_name}"


def _source_coverage_field_label(dataframe: pl.DataFrame) -> str:
    fields = [
        column
        for column in ("source_system", "source_table", "source_tables")
        if column in dataframe.columns
    ]
    if fields:
        return ", ".join(fields)
    return "(none)"


def _source_coverage_count_sort_key(
    item: tuple[tuple[str, str], int],
) -> tuple[int, str, str]:
    (source_system, source_table), count = item
    return (-count, source_system, source_table)


def _source_coverage_gap_sort_key(
    item: tuple[tuple[str, str, str], int],
) -> tuple[int, str, str, str]:
    (source_system, source_table, detail), count = item
    return (-count, source_system, source_table, detail)


def _render_source_coverage_matrix_headings() -> str:
    return "\n".join(
        f'<th scope="col">{escape(column)}</th>'
        for column in _SOURCE_COVERAGE_MATRIX_HTML_COLUMNS
    )


def _render_source_coverage_matrix_row(row: Mapping[str, object]) -> str:
    cells = "\n".join(
        _render_source_coverage_matrix_cell(row, column)
        for column in _SOURCE_COVERAGE_MATRIX_HTML_COLUMNS
    )
    coverage_state = _source_coverage_matrix_text(row.get("coverage state"))
    return f"""\
<tr data-coverage-state="{escape(coverage_state, quote=True)}">
    {cells}
</tr>"""


def _render_source_coverage_matrix_cell(
    row: Mapping[str, object],
    column: str,
) -> str:
    if column == "table explorer":
        cell_html = _source_coverage_matrix_link(
            row.get(column),
            label="Open table",
            target="table-explorer",
            asset=row.get("asset"),
        )
        return f'<td class="source-coverage-matrix__link-cell">{cell_html}</td>'

    if column == "asset metadata":
        cell_html = _source_coverage_matrix_link(
            row.get(column),
            label="Open asset",
            target="asset-metadata",
            asset=row.get("asset"),
        )
        return f'<td class="source-coverage-matrix__link-cell">{cell_html}</td>'

    text = _source_coverage_matrix_text(row.get(column))
    return f"<td>{escape(text)}</td>"


def _source_coverage_matrix_link(
    value: object,
    *,
    label: str,
    target: str,
    asset: object,
) -> str:
    href = _source_coverage_matrix_href(value)
    if href == "":
        return '<span class="source-coverage-matrix__missing-link">Unavailable</span>'

    asset_label = _source_coverage_matrix_text(asset)
    aria_label = f"{label} for {asset_label}"
    return (
        '<a class="source-coverage-matrix__link" '
        f'data-link-target="{escape(target, quote=True)}" '
        f'href="{escape(href, quote=True)}" '
        f'aria-label="{escape(aria_label, quote=True)}">'
        f"{escape(label)}</a>"
    )


def _source_coverage_matrix_href(value: object | None) -> str:
    if not isinstance(value, str):
        return ""

    href = value.strip()
    if href.startswith(SOURCE_COVERAGE_TABLE_EXPLORER_ROUTE):
        return href
    return ""


def _source_coverage_matrix_text(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value:,}"
    return str(value)


def _source_coverage_matrix_css() -> str:
    return """\
.source-coverage-matrix {
    border: 1px solid var(--emdl-line);
    border-radius: 8px;
    background: var(--emdl-panel);
    overflow: hidden;
}

.source-coverage-matrix__scroller {
    overflow-x: auto;
}

.source-coverage-matrix table {
    width: 100%;
    min-width: 72rem;
    border-collapse: collapse;
    font-size: 0.9rem;
}

.source-coverage-matrix th,
.source-coverage-matrix td {
    border-bottom: 1px solid var(--emdl-line);
    padding: 0.55rem 0.65rem;
    text-align: left;
    vertical-align: top;
}

.source-coverage-matrix th {
    color: var(--emdl-muted);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
}

.source-coverage-matrix td {
    color: var(--emdl-ink);
    max-width: 20rem;
    overflow-wrap: anywhere;
}

.source-coverage-matrix tbody tr:last-child td {
    border-bottom: 0;
}

.source-coverage-matrix__link {
    color: var(--emdl-blue);
    font-weight: 700;
    text-decoration: none;
    white-space: nowrap;
}

.source-coverage-matrix__link:hover {
    text-decoration: underline;
}

.source-coverage-matrix__missing-link,
.source-coverage-matrix__overflow,
.source-coverage-matrix__empty {
    color: var(--emdl-muted);
}

.source-coverage-matrix__overflow {
    margin: 0;
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--emdl-line);
    font-size: 0.85rem;
}
"""


def _source_coverage_distinct_count(
    matrix: pl.DataFrame,
    column: str,
    *,
    coverage_state: str,
    exclude_missing: bool = False,
) -> int:
    if matrix.is_empty() or column not in matrix.columns:
        return 0

    values = (
        matrix.filter(pl.col("coverage state") == coverage_state)
        .get_column(column)
        .drop_nulls()
        .cast(pl.String, strict=False)
        .unique()
        .to_list()
    )
    if exclude_missing:
        values = [
            value
            for value in values
            if isinstance(value, str) and not value.startswith("(")
        ]
    return len(values)


def _normalised_facility_dimension_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_DIM_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _FACILITY_DIM_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("participant_key").cast(pl.String, strict=False),
        pl.col("zone_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_hub_id").cast(pl.String, strict=False),
        pl.col("source_hub_name").cast(pl.String, strict=False),
        pl.col("source_facility_id").cast(pl.String, strict=False),
        pl.col("facility_name").cast(pl.String, strict=False),
        pl.col("facility_short_name").cast(pl.String, strict=False),
        pl.col("facility_type").cast(pl.String, strict=False),
        pl.col("facility_type_description").cast(pl.String, strict=False),
        pl.col("operating_state").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "operating_state_date"),
        pl.col("operator_name").cast(pl.String, strict=False),
        pl.col("source_operator_id").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "operator_change_date"),
        _normalise_date_column(dataframe, "capacity_effective_from_date"),
        _normalise_date_column(dataframe, "capacity_effective_to_date"),
        pl.col("default_capacity").cast(pl.Float64, strict=False),
        pl.col("maximum_capacity").cast(pl.Float64, strict=False),
        pl.col("high_capacity_threshold").cast(pl.Float64, strict=False),
        pl.col("low_capacity_threshold").cast(pl.Float64, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_facility_flow_storage_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_FLOW_STORAGE_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _FACILITY_FLOW_STORAGE_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("facility_key").cast(pl.String, strict=False),
        pl.col("location_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("source_facility_id").cast(pl.String, strict=False),
        pl.col("source_location_id").cast(pl.String, strict=False),
        pl.col("demand_tj").cast(pl.Float64, strict=False),
        pl.col("supply_tj").cast(pl.Float64, strict=False),
        pl.col("transfer_in_tj").cast(pl.Float64, strict=False),
        pl.col("transfer_out_tj").cast(pl.Float64, strict=False),
        pl.col("held_in_storage_tj").cast(pl.Float64, strict=False),
        pl.col("cushion_gas_storage_tj").cast(pl.Float64, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_facility_capacity_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_CAPACITY_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _FACILITY_CAPACITY_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        pl.col("source_facility_id").cast(pl.String, strict=False),
        pl.col("facility_name").cast(pl.String, strict=False),
        pl.col("capacity_type").cast(pl.String, strict=False),
        pl.col("flow_direction").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "from_gas_date"),
        _normalise_date_column(dataframe, "to_gas_date"),
        pl.col("capacity_quantity_tj").cast(pl.Float64, strict=False),
        pl.col("capacity_description").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _non_empty_string_count(dataframe: pl.DataFrame, column: str) -> int:
    return dataframe.filter(_non_empty_string_expression(column)).height


def _distinct_non_empty_count(dataframe: pl.DataFrame, column: str) -> int:
    return (
        dataframe.filter(_non_empty_string_expression(column))
        .get_column(column)
        .n_unique()
    )


def _non_empty_string_expression(column: str) -> pl.Expr:
    value = pl.col(column).cast(pl.String, strict=False)
    return value.is_not_null() & (value.str.strip_chars() != "")


def _capacity_metadata_row_count(dataframe: pl.DataFrame) -> int:
    return dataframe.filter(
        pl.any_horizontal(
            *(
                pl.col(column).is_not_null()
                for column in _FACILITY_CAPACITY_METADATA_COLUMNS
            )
        )
    ).height


def _facility_source_table_count(dataframe: pl.DataFrame) -> int:
    values: set[str] = set()
    for row in dataframe.select("source_tables").to_dicts():
        values.update(_source_coverage_value_strings(row.get("source_tables")))
    return len(values)


def _facility_identifier_set(dataframe: pl.DataFrame, column: str) -> set[str]:
    return {
        value
        for value in (
            dataframe.filter(_non_empty_string_expression(column))
            .get_column(column)
            .cast(pl.String, strict=False)
            .to_list()
        )
        if isinstance(value, str) and value != ""
    }


def _facility_flow_rows(dataframe: pl.DataFrame) -> pl.DataFrame:
    return dataframe.filter(
        pl.any_horizontal(
            *(pl.col(column).is_not_null() for column in _FACILITY_FLOW_MEASURE_COLUMNS)
        )
    )


def _facility_storage_rows(dataframe: pl.DataFrame) -> pl.DataFrame:
    return dataframe.filter(
        pl.any_horizontal(
            *(
                pl.col(column).is_not_null()
                for column in _FACILITY_STORAGE_MEASURE_COLUMNS
            )
        )
    )


def _matched_facility_count(
    rows: pl.DataFrame,
    facility_ids: set[str],
    facility_keys: set[str],
) -> int:
    columns = [
        column
        for column in ("source_facility_id", "facility_key")
        if column in rows.columns
    ]
    matched: set[str] = set()
    for row in rows.select(columns).to_dicts():
        source_facility_id = str(row.get("source_facility_id") or "").strip()
        facility_key = str(row.get("facility_key") or "").strip()
        if source_facility_id in facility_ids:
            matched.add(f"source:{source_facility_id}")
        elif facility_key in facility_keys:
            matched.add(f"key:{facility_key}")
    return len(matched)


def _gas_day_candidate_fields(load: GasTableLoad) -> tuple[str, ...]:
    fields: list[str] = list(load.spec.date_columns)
    dataframe = load.dataframe
    if dataframe is not None:
        fields.extend(
            column
            for column in dataframe.columns
            if _is_gas_day_candidate_column(column)
        )
    return tuple(dict.fromkeys(fields))


def _gas_day_example_fields(load: GasTableLoad) -> tuple[str, ...]:
    fields = _gas_day_candidate_fields(load)
    gas_day_fields = tuple(
        field for field in fields if _gas_day_field_role(field) == "Gas Day field"
    )
    return gas_day_fields if gas_day_fields else fields


def _is_gas_day_candidate_column(column: str) -> bool:
    normalised = column.lower()
    return "date" in normalised or "timestamp" in normalised


def _gas_day_missing_field_row(load: GasTableLoad) -> dict[str, object]:
    rows_loaded = 0 if load.dataframe is None else load.dataframe.height
    detail = load.error or "No date, timestamp, or date-key fields were discovered."
    return {
        "asset": f"silver.gas_model.{load.spec.table_name}",
        "section": load.spec.section,
        "table": load.spec.table_name,
        "field": "",
        "field role": "No date field found",
        "dtype": "",
        "status": _gas_day_load_status(load),
        "rows loaded": rows_loaded,
        "populated values": 0,
        "first value": "",
        "latest value": "",
        "row limit": format_row_limit(load.row_limit),
        "table explorer": _gas_day_table_explorer_link(load),
        "uri": load.uri,
        "detail": detail,
    }


def _gas_day_field_row(load: GasTableLoad, field: str) -> dict[str, object]:
    dataframe = load.dataframe
    rows_loaded = 0 if dataframe is None else dataframe.height
    field_present = dataframe is not None and field in dataframe.columns
    dtype = (
        "" if not field_present or dataframe is None else str(dataframe.schema[field])
    )
    populated_values = (
        _field_populated_count(dataframe, field)
        if field_present and dataframe is not None
        else 0
    )
    first_value, latest_value = (
        _field_value_bounds(dataframe, field)
        if field_present and dataframe is not None
        else ("", "")
    )

    return {
        "asset": f"silver.gas_model.{load.spec.table_name}",
        "section": load.spec.section,
        "table": load.spec.table_name,
        "field": field,
        "field role": _gas_day_field_role(field),
        "dtype": dtype,
        "status": _gas_day_field_status(load, field_present),
        "rows loaded": rows_loaded,
        "populated values": populated_values,
        "first value": first_value,
        "latest value": latest_value,
        "row limit": format_row_limit(load.row_limit),
        "table explorer": _gas_day_table_explorer_link(load),
        "uri": load.uri,
        "detail": _gas_day_field_detail(load, field, field_present),
    }


def _gas_day_field_role(field: str) -> str:
    normalised = field.lower()
    if normalised in {"gas_date", "from_gas_date", "to_gas_date"}:
        return "Gas Day field"
    if normalised.endswith("_gas_date"):
        return "Gas Day field"
    if normalised == "date_key" or normalised.endswith("_date_key"):
        return "Date key"
    if "timestamp" in normalised:
        return "Timestamp field"
    return "Date field"


def _gas_day_load_status(load: GasTableLoad) -> str:
    if load.error is not None:
        return "Unavailable"
    if load.dataframe is None or load.dataframe.is_empty():
        return "Empty"
    return "Loaded"


def _gas_day_field_status(load: GasTableLoad, field_present: bool) -> str:
    if load.error is not None:
        return "Unavailable"
    if load.dataframe is None or load.dataframe.is_empty():
        return "Empty"
    if field_present:
        return "Discovered"
    return "Declared only"


def _gas_day_field_detail(
    load: GasTableLoad,
    field: str,
    field_present: bool,
) -> str:
    if load.error is not None:
        return load.error
    if load.dataframe is None or load.dataframe.is_empty():
        return "The table read returned no rows; field presence came from metadata."
    if not field_present:
        return f"{field} is declared for this dashboard but absent from loaded rows."
    return "Field is present in the bounded table read."


def _field_populated_count(dataframe: pl.DataFrame, field: str) -> int:
    return dataframe.get_column(field).drop_nulls().len()


def _field_value_bounds(
    dataframe: pl.DataFrame,
    field: str,
) -> tuple[str, str]:
    values = dataframe.get_column(field).drop_nulls()
    if values.is_empty():
        return "", ""

    return _format_cell_value(values.min()), _format_cell_value(values.max())


def _gas_day_field_examples(
    dataframe: pl.DataFrame,
    field: str,
    row_limit: int,
) -> list[dict[str, object]]:
    selected_columns = _gas_day_example_columns(dataframe, field)
    examples = (
        dataframe.select(selected_columns)
        .filter(pl.col(field).is_not_null())
        .sort(field, descending=True, nulls_last=True)
        .head(row_limit)
    )
    return examples.to_dicts()


def _gas_day_example_columns(dataframe: pl.DataFrame, field: str) -> list[str]:
    columns = [field]
    for column in (
        "source_system",
        "source_table",
        "source_tables",
        *_GAS_DAY_EXAMPLE_CONTEXT_COLUMNS,
    ):
        if column in dataframe.columns and column not in columns:
            columns.append(column)
    return columns


def _gas_day_example_row(
    load: GasTableLoad,
    field: str,
    row: Mapping[str, object],
) -> dict[str, object]:
    return {
        "asset": f"silver.gas_model.{load.spec.table_name}",
        "section": load.spec.section,
        "table": load.spec.table_name,
        "field": field,
        "field role": _gas_day_field_role(field),
        "value": _format_cell_value(row.get(field)),
        "source system": _format_cell_value(row.get("source_system")),
        "source table": _gas_day_source_table_value(row),
        "context": _gas_day_example_context(row, field),
        "row limit": format_row_limit(load.row_limit),
        "uri": load.uri,
    }


def _gas_day_source_table_value(row: Mapping[str, object]) -> str:
    if "source_table" in row:
        return _format_cell_value(row["source_table"])
    return _format_cell_value(row.get("source_tables"))


def _gas_day_example_context(row: Mapping[str, object], field: str) -> str:
    labels: list[str] = []
    excluded_columns = {field, "source_system", "source_table", "source_tables"}
    for column in _GAS_DAY_EXAMPLE_CONTEXT_COLUMNS:
        if column in excluded_columns:
            continue
        value = _format_cell_value(row.get(column))
        if value:
            labels.append(f"{column}={value}")
    return "; ".join(labels)


def _format_cell_value(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return str(value)
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return ", ".join(_format_cell_value(item) for item in value if item is not None)
    return str(value)


def _latest_gas_day_value(rows: Sequence[Mapping[str, object]]) -> str:
    values = sorted(
        str(value)
        for row in rows
        if (value := row.get("latest value")) not in {"", None}
    )
    if len(values) == 0:
        return ""
    return values[-1]


def _gas_day_table_explorer_link(load: GasTableLoad) -> str:
    table_name = quote(load.spec.table_name, safe="")
    return f"{SOURCE_COVERAGE_TABLE_EXPLORER_ROUTE}?search={table_name}"


def _market_price_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_market_price_dataframe(load)
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


def _filtered_market_price_dataframe(
    load: GasTableLoad | None,
    price_type_filter: str,
    source_system_filter: str,
    source_table_filter: str,
) -> pl.DataFrame:
    dataframe = _normalised_market_price_dataframe(load)
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if price_type_filter != MARKET_PRICE_PRICE_TYPE_FILTER_ALL:
        filtered = filtered.filter(pl.col("price_type") == price_type_filter)
    if source_system_filter != MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_system") == source_system_filter)
    if source_table_filter != MARKET_PRICE_SOURCE_TABLE_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_table") == source_table_filter)
    return filtered


def _normalised_market_price_dataframe(load: GasTableLoad | None) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_MARKET_PRICE_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _MARKET_PRICE_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("price_type").cast(pl.String, strict=False),
        pl.col("schedule_type_id").cast(pl.String, strict=False),
        pl.col("schedule_interval").cast(pl.String, strict=False),
        pl.col("transmission_id").cast(pl.String, strict=False),
        pl.col("transmission_doc_id").cast(pl.String, strict=False),
        pl.col("source_location_id").cast(pl.String, strict=False),
        pl.col("price_value_gst_ex").cast(pl.Float64, strict=False),
        pl.col("weighted_average_price_gst_ex").cast(pl.Float64, strict=False),
        pl.col("cumulative_price").cast(pl.Float64, strict=False),
        pl.col("administered_price").cast(pl.Float64, strict=False),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _available_market_price_measures(dataframe: pl.DataFrame) -> tuple[str, ...]:
    return tuple(
        column
        for column in MARKET_PRICE_MEASURE_COLUMNS
        if column in dataframe.columns
        and not dataframe.get_column(column).drop_nulls().is_empty()
    )


def _market_price_measure_count_expressions() -> tuple[pl.Expr, ...]:
    return tuple(
        pl.col(column).is_not_null().sum().alias(f"_{column}_rows")
        for column in MARKET_PRICE_MEASURE_COLUMNS
    )


def _market_price_measure_count_label_expression() -> pl.Expr:
    return (
        pl.struct(
            [pl.col(f"_{column}_rows") for column in MARKET_PRICE_MEASURE_COLUMNS]
        )
        .map_elements(
            _format_market_price_measure_counts,
            return_dtype=pl.String,
        )
        .alias("available price measures")
    )


def _market_price_measure_value_label_expression() -> pl.Expr:
    return (
        pl.struct([pl.col(column) for column in MARKET_PRICE_MEASURE_COLUMNS])
        .map_elements(
            _format_market_price_measure_values,
            return_dtype=pl.String,
        )
        .alias("available price measures")
    )


def _format_market_price_measure_counts(values: Mapping[str, object]) -> str:
    measures = tuple(
        column
        for column in MARKET_PRICE_MEASURE_COLUMNS
        if _is_positive_count(values.get(f"_{column}_rows"))
    )
    return _format_market_price_measure_names(measures)


def _format_market_price_measure_values(values: Mapping[str, object]) -> str:
    measures = tuple(
        column
        for column in MARKET_PRICE_MEASURE_COLUMNS
        if values.get(column) is not None
    )
    return _format_market_price_measure_names(measures)


def _format_market_price_measure_names(measures: Sequence[str]) -> str:
    if len(measures) == 0:
        return "none"
    return ", ".join(measures)


def _is_positive_count(value: object) -> bool:
    return isinstance(value, int | float) and value > 0


def _render_market_price_context_link(entry: DashboardRegistryEntry) -> str:
    status_label = _dashboard_entry_status_label(entry)
    title = escape(entry.title)
    route = entry.notebook_route
    if entry.status.value == "available" and route is not None:
        title_html = f'<a href="{escape(route, quote=True)}">{title}</a>'
    else:
        title_html = f"<span>{title}</span>"

    return f"""\
        <li data-dashboard-status="{escape(entry.status.value, quote=True)}">
            {title_html}
            <span>{escape(status_label)}</span>
            <code>{escape(entry.concept_id)}</code>
        </li>"""


def _dashboard_entry_status_label(entry: DashboardRegistryEntry) -> str:
    if entry.status.value == "available" and entry.notebook_route is not None:
        return "Available dashboard"
    if entry.status.value == "planned":
        return "Planned dashboard"
    return "Unavailable dashboard"


def _market_price_context_links_css() -> str:
    return """\
.market-price-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.market-price-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.market-price-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.market-price-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.market-price-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.market-price-links li:first-child {
    border-top: 0;
}

.market-price-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.market-price-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.market-price-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.market-price-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .market-price-links li {
        grid-template-columns: 1fr;
    }
}
"""


def _schedule_run_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_schedule_run_dataframe(load)
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


def _filtered_schedule_run_dataframe(
    load: GasTableLoad | None,
    gas_date_filter: str,
    source_system_filter: str,
    schedule_type_filter: str,
) -> pl.DataFrame:
    dataframe = _normalised_schedule_run_dataframe(load)
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if gas_date_filter != SCHEDULE_RUN_GAS_DATE_FILTER_ALL:
        filtered = filtered.filter(
            pl.col("gas_date").cast(pl.String) == gas_date_filter
        )
    if source_system_filter != SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_system") == source_system_filter)
    if schedule_type_filter != SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL:
        filtered = filtered.filter(pl.col("schedule_type_id") == schedule_type_filter)
    return filtered


def _normalised_schedule_run_dataframe(load: GasTableLoad | None) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_SCHEDULE_RUN_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _SCHEDULE_RUN_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("transmission_id").cast(pl.String, strict=False),
        pl.col("transmission_document_id").cast(pl.String, strict=False),
        pl.col("transmission_group_id").cast(pl.String, strict=False),
        pl.col("schedule_type_id").cast(pl.String, strict=False),
        pl.col("forecast_demand_version").cast(pl.String, strict=False),
        pl.col("demand_type_id").cast(pl.String, strict=False),
        pl.col("objective_function_value").cast(pl.Float64, strict=False),
        _normalise_timestamp_column(dataframe, "gas_start_timestamp"),
        _normalise_timestamp_column(dataframe, "bid_cutoff_timestamp"),
        _normalise_timestamp_column(dataframe, "creation_timestamp"),
        _normalise_timestamp_column(dataframe, "approval_timestamp"),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _render_schedule_run_context_link(entry: DashboardRegistryEntry) -> str:
    status_label = _dashboard_entry_status_label(entry)
    title = escape(entry.title)
    route = entry.notebook_route
    if entry.status.value == "available" and route is not None:
        title_html = f'<a href="{escape(route, quote=True)}">{title}</a>'
    else:
        title_html = f"<span>{title}</span>"

    return f"""\
        <li data-dashboard-status="{escape(entry.status.value, quote=True)}">
            {title_html}
            <span>{escape(status_label)}</span>
            <code>{escape(entry.concept_id)}</code>
        </li>"""


def _schedule_run_context_links_css() -> str:
    return """\
.schedule-run-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.schedule-run-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.schedule-run-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.schedule-run-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.schedule-run-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.schedule-run-links li:first-child {
    border-top: 0;
}

.schedule-run-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.schedule-run-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.schedule-run-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.schedule-run-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .schedule-run-links li {
        grid-template-columns: 1fr;
    }
}
"""


def _settlement_activity_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_settlement_activity_dataframe(load)
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


def _filtered_settlement_activity_dataframe(
    load: GasTableLoad | None,
    gas_date_filter: str,
    source_system_filter: str,
    activity_type_filter: str,
) -> pl.DataFrame:
    dataframe = _normalised_settlement_activity_dataframe(load)
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if gas_date_filter != SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL:
        filtered = filtered.filter(
            pl.col("gas_date").cast(pl.String) == gas_date_filter
        )
    if source_system_filter != SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_system") == source_system_filter)
    if activity_type_filter != SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL:
        filtered = filtered.filter(pl.col("activity_type") == activity_type_filter)
    return filtered


def _normalised_settlement_activity_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_SETTLEMENT_ACTIVITY_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _SETTLEMENT_ACTIVITY_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("date_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("settlement_version_id").cast(pl.String, strict=False),
        pl.col("activity_type").cast(pl.String, strict=False),
        pl.col("schedule_no").cast(pl.String, strict=False),
        pl.col("network_name").cast(pl.String, strict=False),
        pl.col("participant_name").cast(pl.String, strict=False),
        pl.col("amount_gst_ex").cast(pl.Float64, strict=False),
        pl.col("quantity_gj").cast(pl.Float64, strict=False),
        pl.col("percentage").cast(pl.Float64, strict=False),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _render_settlement_activity_context_link(entry: DashboardRegistryEntry) -> str:
    status_label = _dashboard_entry_status_label(entry)
    title = escape(entry.title)
    route = entry.notebook_route
    if entry.status.value == "available" and route is not None:
        title_html = f'<a href="{escape(route, quote=True)}">{title}</a>'
    else:
        title_html = f"<span>{title}</span>"

    return f"""\
        <li data-dashboard-status="{escape(entry.status.value, quote=True)}">
            {title_html}
            <span>{escape(status_label)}</span>
            <code>{escape(entry.concept_id)}</code>
        </li>"""


def _settlement_activity_context_links_css() -> str:
    return """\
.settlement-activity-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.settlement-activity-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.settlement-activity-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.settlement-activity-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.settlement-activity-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.settlement-activity-links li:first-child {
    border-top: 0;
}

.settlement-activity-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.settlement-activity-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.settlement-activity-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.settlement-activity-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .settlement-activity-links li {
        grid-template-columns: 1fr;
    }
}
"""


def _customer_transfer_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_customer_transfer_dataframe(load)
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


def _filtered_customer_transfer_dataframe(
    load: GasTableLoad | None,
    gas_date_filter: str,
    market_code_filter: str,
    source_system_filter: str,
) -> pl.DataFrame:
    dataframe = _normalised_customer_transfer_dataframe(load)
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if gas_date_filter != CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL:
        filtered = filtered.filter(
            pl.col("gas_date").cast(pl.String) == gas_date_filter
        )
    if market_code_filter != CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL:
        filtered = filtered.filter(pl.col("market_code") == market_code_filter)
    if source_system_filter != CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_system") == source_system_filter)
    return filtered


def _normalised_customer_transfer_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_CUSTOMER_TRANSFER_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _CUSTOMER_TRANSFER_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("date_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("market_code").cast(pl.String, strict=False),
        pl.col("transfers_lodged").cast(pl.Int64, strict=False),
        pl.col("transfers_completed").cast(pl.Int64, strict=False),
        pl.col("transfers_cancelled").cast(pl.Int64, strict=False),
        pl.col("int_transfers_lodged").cast(pl.Int64, strict=False),
        pl.col("int_transfers_completed").cast(pl.Int64, strict=False),
        pl.col("int_transfers_cancelled").cast(pl.Int64, strict=False),
        pl.col("greenfields_received").cast(pl.Int64, strict=False),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _render_customer_transfer_context_link(entry: DashboardRegistryEntry) -> str:
    status_label = _dashboard_entry_status_label(entry)
    title = escape(entry.title)
    route = entry.notebook_route
    if entry.status.value == "available" and route is not None:
        title_html = f'<a href="{escape(route, quote=True)}">{title}</a>'
    else:
        title_html = f"<span>{title}</span>"

    return f"""\
        <li data-dashboard-status="{escape(entry.status.value, quote=True)}">
            {title_html}
            <span>{escape(status_label)}</span>
            <code>{escape(entry.concept_id)}</code>
        </li>"""


def _customer_transfer_context_links_css() -> str:
    return """\
.customer-transfer-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.customer-transfer-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.customer-transfer-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.customer-transfer-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.customer-transfer-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.customer-transfer-links li:first-child {
    border-top: 0;
}

.customer-transfer-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.customer-transfer-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.customer-transfer-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.customer-transfer-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .customer-transfer-links li {
        grid-template-columns: 1fr;
    }
}
"""


def _bid_stack_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_bid_stack_dataframe(load)
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


def _filtered_bid_stack_dataframe(
    load: GasTableLoad | None,
    participant_filter: str,
    facility_filter: str,
    zone_filter: str,
    source_system_filter: str,
) -> pl.DataFrame:
    dataframe = _normalised_bid_stack_dataframe(load)
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if participant_filter != BID_STACK_PARTICIPANT_FILTER_ALL:
        filtered = filtered.filter(pl.col("participant_id") == participant_filter)
    if facility_filter != BID_STACK_FACILITY_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_facility_id") == facility_filter)
    if zone_filter != BID_STACK_ZONE_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_hub_id") == zone_filter)
    if source_system_filter != BID_STACK_SOURCE_SYSTEM_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_system") == source_system_filter)
    return filtered


def _render_facility_context_link(entry: DashboardRegistryEntry) -> str:
    status_label = _dashboard_entry_status_label(entry)
    title = escape(entry.title)
    route = entry.notebook_route
    if entry.status.value == "available" and route is not None:
        title_html = f'<a href="{escape(route, quote=True)}">{title}</a>'
    else:
        title_html = f"<span>{title}</span>"

    return f"""\
        <li data-dashboard-status="{escape(entry.status.value, quote=True)}">
            {title_html}
            <span>{escape(status_label)}</span>
            <code>{escape(entry.concept_id)}</code>
        </li>"""


def _facility_context_links_css() -> str:
    return """\
.facility-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.facility-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.facility-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.facility-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.facility-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.facility-links li:first-child {
    border-top: 0;
}

.facility-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.facility-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.facility-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.facility-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .facility-links li {
        grid-template-columns: 1fr;
    }
}
"""


def _normalised_bid_stack_dataframe(load: GasTableLoad | None) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_BID_STACK_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _BID_STACK_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        pl.col("source_report_id").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("participant_id").cast(pl.String, strict=False),
        pl.col("participant_name").cast(pl.String, strict=False),
        pl.col("source_hub_id").cast(pl.String, strict=False),
        pl.col("source_hub_name").cast(pl.String, strict=False),
        pl.col("source_facility_id").cast(pl.String, strict=False),
        pl.col("facility_name").cast(pl.String, strict=False),
        pl.col("source_point_id").cast(pl.String, strict=False),
        pl.col("schedule_identifier").cast(pl.String, strict=False),
        pl.col("bid_id").cast(pl.String, strict=False),
        pl.col("bid_step").cast(pl.Int64, strict=False),
        pl.col("bid_price").cast(pl.Float64, strict=False),
        pl.col("bid_qty_gj").cast(pl.Float64, strict=False),
        pl.col("step_qty_gj").cast(pl.Float64, strict=False),
        pl.col("offer_type").cast(pl.String, strict=False),
        pl.col("inject_withdraw").cast(pl.String, strict=False),
        pl.col("schedule_type").cast(pl.String, strict=False),
        pl.col("schedule_time").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "bid_cutoff_timestamp"),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _render_bid_stack_context_link(entry: DashboardRegistryEntry) -> str:
    status_label = _dashboard_entry_status_label(entry)
    title = escape(entry.title)
    route = entry.notebook_route
    if entry.status.value == "available" and route is not None:
        title_html = f'<a href="{escape(route, quote=True)}">{title}</a>'
    else:
        title_html = f"<span>{title}</span>"

    return f"""\
        <li data-dashboard-status="{escape(entry.status.value, quote=True)}">
            {title_html}
            <span>{escape(status_label)}</span>
            <code>{escape(entry.concept_id)}</code>
        </li>"""


def _bid_stack_context_links_css() -> str:
    return """\
.bid-stack-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.bid-stack-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.bid-stack-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.bid-stack-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.bid-stack-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.bid-stack-links li:first-child {
    border-top: 0;
}

.bid-stack-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.bid-stack-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.bid-stack-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.bid-stack-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .bid-stack-links li {
        grid-template-columns: 1fr;
    }
}
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


def _format_numeric_range(minimum: object | None, maximum: object | None) -> str:
    return (
        "unknown"
        if minimum is None and maximum is None
        else f"{_format_number(minimum)} to {_format_number(maximum)}"
    )


def _format_measure_range(
    minimum: object | None,
    maximum: object | None,
    populated_count: object | None,
) -> str:
    if not _is_positive_count(populated_count):
        return "unknown"
    return _format_numeric_range(minimum, maximum)


def _format_measure_total(
    value: object | None,
    populated_count: object | None,
    *,
    suffix: str = "",
) -> str:
    if not _is_positive_count(populated_count):
        return "unknown"
    return f"{_format_number(value)}{suffix}"


def _format_quantity(value: object | None) -> str:
    return "unknown" if value is None else f"{_format_number(value)} GJ"


def _format_number(value: object | None) -> str:
    return "unknown" if not isinstance(value, int | float) else f"{value:,.4g}"


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
