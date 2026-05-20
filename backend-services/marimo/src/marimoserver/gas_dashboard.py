"""Helpers for the gas market overview marimo dashboard."""

from collections.abc import Hashable, Mapping, Sequence
from dataclasses import dataclass, field as dataclass_field, replace
from datetime import UTC, date, datetime, timedelta
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
PARTICIPANT_CONTEXT_ID = "participant-context"
PARTICIPANT_DIM_TABLE_NAME = "silver_gas_dim_participant"
PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME = "silver_gas_participant_market_membership"
DEFAULT_PARTICIPANT_PREVIEW_ROWS = 50
SOURCE_COVERAGE_TABLE_EXPLORER_ROUTE = "/marimo/table_explorer/"
SOURCE_COVERAGE_STATE_COVERED = "Covered"
SOURCE_COVERAGE_STATE_GAP = "Coverage gap"
SOURCE_COVERAGE_STATE_EMPTY = "Empty"
SOURCE_COVERAGE_STATE_UNAVAILABLE = "Unavailable"
FACILITY_CONTEXT_ID = "facility-context"
HUB_ZONE_CONTEXT_ID = "hub-zone-context"
CONNECTION_POINT_CONTEXT_ID = "connection-point-context"
FACILITY_DIM_TABLE_NAME = "silver_gas_dim_facility"
LOCATION_DIM_TABLE_NAME = "silver_gas_dim_location"
HUB_ZONE_DIM_TABLE_NAME = "silver_gas_dim_zone"
CONNECTION_POINT_DIM_TABLE_NAME = "silver_gas_dim_connection_point"
CONNECTION_POINT_FLOW_TABLE_NAME = "silver_gas_fact_connection_point_flow"
FACILITY_FLOW_STORAGE_TABLE_NAME = "silver_gas_fact_facility_flow_storage"
FACILITY_CAPACITY_OUTLOOK_TABLE_NAME = "silver_gas_fact_capacity_outlook"
CAPACITY_CONTEXT_ID = "capacity-context"
CAPACITY_OUTLOOK_TABLE_NAME = FACILITY_CAPACITY_OUTLOOK_TABLE_NAME
CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL = "All date ranges"
CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL = "All capacity types"
CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL = "All directions"
CAPACITY_OUTLOOK_FACILITY_FILTER_ALL = "All facilities"
CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL = "All capacity source coverage"
CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
DEFAULT_CAPACITY_OUTLOOK_PREVIEW_ROWS = 50
DEFAULT_FACILITY_PREVIEW_ROWS = 50
DEFAULT_HUB_ZONE_PREVIEW_ROWS = 50
DEFAULT_CONNECTION_POINT_PREVIEW_ROWS = 50
FLOW_CONTEXT_ID = "flow-context"
NOMINATION_FORECAST_TABLE_NAME = "silver_gas_fact_nomination_forecast"
NOMINATION_FORECAST_CONTEXT_ID = "nomination-demand-forecast"
NOMINATION_FORECAST_GAS_DATE_FILTER_ALL = "All gas dates"
NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
NOMINATION_FORECAST_FACILITY_FILTER_ALL = "All facilities"
NOMINATION_FORECAST_LOCATION_FILTER_ALL = "All locations"
OPERATIONAL_METER_FLOW_TABLE_NAME = "silver_gas_fact_operational_meter_flow"
DEFAULT_FLOW_PREVIEW_ROWS = 50
DEFAULT_NOMINATION_FORECAST_PREVIEW_ROWS = 50
FACILITY_FLOW_STORAGE_CONTEXT_ID = "facility-flow-storage"
FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL = "All gas dates"
FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL = "All facilities"
FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
DEFAULT_FACILITY_FLOW_STORAGE_PREVIEW_ROWS = 50
FORECAST_ACTUAL_CONTEXT_ID = "forecast-vs-actual"
FORECAST_ACTUAL_GAS_DATE_FILTER_ALL = "All gas dates"
FORECAST_ACTUAL_FACILITY_FILTER_ALL = "All facilities"
FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
DEFAULT_FORECAST_ACTUAL_PREVIEW_ROWS = 50
LINEPACK_TABLE_NAME = "silver_gas_fact_linepack"
LINEPACK_CONTEXT_ID = "linepack-context"
LINEPACK_GAS_DATE_FILTER_ALL = "All gas dates"
LINEPACK_FACILITY_FILTER_ALL = "All facilities"
LINEPACK_ZONE_FILTER_ALL = "All zones"
LINEPACK_ADEQUACY_FLAG_FILTER_ALL = "All adequacy flags"
LINEPACK_SOURCE_SYSTEM_FILTER_ALL = "All source systems"
DEFAULT_LINEPACK_PREVIEW_ROWS = 50
_FACILITY_CAPACITY_METADATA_COLUMNS = (
    "default_capacity",
    "maximum_capacity",
    "high_capacity_threshold",
    "low_capacity_threshold",
)
_CONNECTION_POINT_RELATIONSHIP_KEY_COLUMNS = (
    "facility_key",
    "location_key",
    "zone_key",
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
_FACILITY_FLOW_STORAGE_MEASURES = (
    *_FACILITY_FLOW_MEASURE_COLUMNS,
    *_FACILITY_STORAGE_MEASURE_COLUMNS,
)
_NOMINATION_FORECAST_MEASURE_COLUMNS = (
    "demand_forecast_gj",
    "supply_forecast_gj",
    "transfer_in_forecast_gj",
    "transfer_out_forecast_gj",
    "override_quantity_gj",
)
_OPERATIONAL_METER_FLOW_MEASURE_COLUMNS = ("quantity_gj",)
_FLOW_MEASURE_COLUMNS_BY_TABLE = {
    CONNECTION_POINT_FLOW_TABLE_NAME: ("actual_quantity_tj",),
    FACILITY_FLOW_STORAGE_TABLE_NAME: _FACILITY_FLOW_STORAGE_MEASURES,
    NOMINATION_FORECAST_TABLE_NAME: _NOMINATION_FORECAST_MEASURE_COLUMNS,
    OPERATIONAL_METER_FLOW_TABLE_NAME: _OPERATIONAL_METER_FLOW_MEASURE_COLUMNS,
}
_FLOW_MEASURE_UNITS_BY_TABLE = {
    CONNECTION_POINT_FLOW_TABLE_NAME: "TJ",
    FACILITY_FLOW_STORAGE_TABLE_NAME: "TJ",
    NOMINATION_FORECAST_TABLE_NAME: "GJ",
    OPERATIONAL_METER_FLOW_TABLE_NAME: "GJ",
}

_SOURCE_COVERAGE_MISSING_SOURCE_SYSTEM_COLUMN = "(missing source_system column)"
_SOURCE_COVERAGE_EMPTY_SOURCE_SYSTEM_VALUE = "(empty source_system value)"
_SOURCE_COVERAGE_MISSING_SOURCE_TABLE_COLUMN = (
    "(missing source_table/source_tables column)"
)
_SOURCE_COVERAGE_EMPTY_SOURCE_TABLE_VALUE = "(empty source_table/source_tables value)"
_CAPACITY_OUTLOOK_UNDATED_DATE_RANGE = "(undated outlook period)"
_CAPACITY_OUTLOOK_OTHER_SOURCE_COVERAGE = "Other capacity outlook"
_CAPACITY_OUTLOOK_SOURCE_TABLE_COVERAGE_LABELS = {
    "silver.gbb.silver_gasbb_short_term_capacity_outlook": (
        "Short-term capacity outlook"
    ),
    "silver.gbb.silver_gasbb_medium_term_capacity_outlook": (
        "Medium-term capacity outlook"
    ),
    "silver.gbb.silver_gasbb_uncontracted_capacity": "Uncontracted capacity",
    "silver.gbb.silver_gasbb_nameplate_rating": "Nameplate rating",
    "silver.gbb.silver_gasbb_connection_point_nameplate": (
        "Connection-point nameplate"
    ),
}


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


@dataclass
class _FlowSourceSummary:
    fact: str
    source_system: str
    source_table: str
    row_limit: str
    detail: str
    rows: int = 0
    gas_dates: set[date] = dataclass_field(default_factory=set)
    measure_rows: int = 0
    latest_gas_date: date | None = None
    latest_source_update: datetime | None = None
    latest_ingest: datetime | None = None


@dataclass
class _ForecastActualAggregate:
    rows: int = 0
    source_systems: set[str] = dataclass_field(default_factory=set)
    source_tables: set[str] = dataclass_field(default_factory=set)
    forecast_type_versions: set[tuple[str | None, str | None]] = dataclass_field(
        default_factory=set
    )
    measure_totals: dict[str, float] = dataclass_field(default_factory=dict)
    measure_counts: dict[str, int] = dataclass_field(default_factory=dict)
    latest_source_update: datetime | None = None
    latest_ingest: datetime | None = None


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

LINEPACK_TABLE_SPEC = GasTableSpec(
    section="Flow and capacity",
    label="Linepack",
    table_name=LINEPACK_TABLE_NAME,
    date_columns=(
        "gas_date",
        "observation_timestamp",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
    preview_columns=(
        "gas_date",
        "observation_timestamp",
        "source_system",
        "source_tables",
        "source_table",
        "facility_key",
        "zone_key",
        "source_facility_id",
        "actual_linepack_gj",
        "adequacy_flag",
        "adequacy_description",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
)

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
    LINEPACK_TABLE_SPEC,
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

FACILITY_FLOW_STORAGE_TABLE_SPEC = GasTableSpec(
    section="Flow and capacity",
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
        "source_tables",
        "facility_key",
        "location_key",
        "source_facility_id",
        "source_location_id",
        "demand_tj",
        "supply_tj",
        "transfer_in_tj",
        "transfer_out_tj",
        "held_in_storage_tj",
        "cushion_gas_storage_tj",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
)

CAPACITY_OUTLOOK_TABLE_SPEC = GasTableSpec(
    section="Flow and capacity",
    label="Capacity outlook",
    table_name=CAPACITY_OUTLOOK_TABLE_NAME,
    date_columns=(
        "from_gas_date",
        "to_gas_date",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
    preview_columns=(
        "from_gas_date",
        "to_gas_date",
        "outlook_month",
        "outlook_year",
        "source_system",
        "source_table",
        "source_facility_id",
        "facility_name",
        "capacity_type",
        "flow_direction",
        "receipt_location_id",
        "delivery_location_id",
        "capacity_quantity_tj",
        "capacity_description",
    ),
)
CAPACITY_OUTLOOK_TABLE_SPECS = (CAPACITY_OUTLOOK_TABLE_SPEC,)

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
    FACILITY_FLOW_STORAGE_TABLE_SPEC,
    CAPACITY_OUTLOOK_TABLE_SPEC,
)
CONNECTION_POINT_TABLE_SPECS = (
    GasTableSpec(
        section="Dimensions",
        label="Connection point standing data",
        table_name=CONNECTION_POINT_DIM_TABLE_NAME,
        date_columns=(
            "effective_date",
            "effective_to_date",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ),
        preview_columns=(
            "source_system",
            "source_tables",
            "source_hub_id",
            "source_hub_name",
            "source_facility_id",
            "source_connection_point_id",
            "connection_point_name",
            "flow_direction",
            "facility_name",
            "source_location_id",
            "location_name",
            "state",
            "exempt",
            "effective_date",
            "effective_to_date",
        ),
    ),
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
            "facility_type",
            "participant_key",
            "zone_key",
        ),
    ),
    GasTableSpec(
        section="Dimensions",
        label="Location standing data",
        table_name=LOCATION_DIM_TABLE_NAME,
        date_columns=("ingested_timestamp",),
        preview_columns=(
            "source_system",
            "source_location_id",
            "location_name",
            "state",
            "location_type",
        ),
    ),
    GasTableSpec(
        section="Dimensions",
        label="Hub and zone standing data",
        table_name=HUB_ZONE_DIM_TABLE_NAME,
        date_columns=("ingested_timestamp",),
        preview_columns=(
            "source_system",
            "source_tables",
            "zone_type",
            "source_zone_id",
            "zone_name",
            "zone_description",
        ),
    ),
    GasTableSpec(
        section="Facts",
        label="Connection point flow",
        table_name=CONNECTION_POINT_FLOW_TABLE_NAME,
        date_columns=(
            "gas_date",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ),
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
        ),
    ),
)
NOMINATION_FORECAST_TABLE_SPEC = GasTableSpec(
    section="Flow facts",
    label="Nomination forecast",
    table_name=NOMINATION_FORECAST_TABLE_NAME,
    date_columns=(
        "gas_date",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
    preview_columns=(
        "gas_date",
        "source_system",
        "source_table",
        "forecast_type",
        "forecast_version",
        "source_facility_id",
        "source_location_id",
        "gas_interval",
        "demand_forecast_gj",
        "supply_forecast_gj",
        "transfer_in_forecast_gj",
        "transfer_out_forecast_gj",
        "override_quantity_gj",
        "source_last_updated_timestamp",
        "ingested_timestamp",
    ),
)
NOMINATION_FORECAST_TABLE_SPECS = (NOMINATION_FORECAST_TABLE_SPEC,)
FORECAST_ACTUAL_TABLE_SPECS = (
    NOMINATION_FORECAST_TABLE_SPEC,
    FACILITY_FLOW_STORAGE_TABLE_SPEC,
)
FLOW_TABLE_SPECS = (
    GasTableSpec(
        section="Flow facts",
        label="Connection point flow",
        table_name=CONNECTION_POINT_FLOW_TABLE_NAME,
        date_columns=(
            "gas_date",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_tables",
            "source_facility_id",
            "source_connection_point_id",
            "flow_direction",
            "actual_quantity_tj",
            "quality",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ),
    ),
    GasTableSpec(
        section="Flow facts",
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
            "source_tables",
            "source_facility_id",
            "source_location_id",
            "demand_tj",
            "supply_tj",
            "transfer_in_tj",
            "transfer_out_tj",
            "held_in_storage_tj",
            "cushion_gas_storage_tj",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ),
    ),
    NOMINATION_FORECAST_TABLE_SPEC,
    GasTableSpec(
        section="Flow facts",
        label="Operational meter flow",
        table_name=OPERATIONAL_METER_FLOW_TABLE_NAME,
        date_columns=(
            "gas_date",
            "commencement_timestamp",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_table",
            "gas_interval",
            "point_type",
            "source_point_id",
            "flow_direction",
            "quantity_gj",
            "commencement_timestamp",
            "termination_timestamp",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ),
    ),
)
HUB_ZONE_TABLE_SPECS = (
    GasTableSpec(
        section="Dimensions",
        label="Hub and zone standing data",
        table_name=HUB_ZONE_DIM_TABLE_NAME,
        date_columns=("ingested_timestamp",),
        preview_columns=(
            "source_system",
            "source_tables",
            "zone_type",
            "source_zone_id",
            "zone_name",
            "zone_description",
            "source_files",
            "ingested_timestamp",
        ),
    ),
)
PARTICIPANT_DIM_TABLE_SPEC = GasTableSpec(
    section="Dimensions",
    label="Participant standing data",
    table_name=PARTICIPANT_DIM_TABLE_NAME,
    date_columns=("ingested_timestamp",),
    preview_columns=(
        "participant_identity_source",
        "participant_identity_value",
        "canonical_participant_name",
        "registered_name",
        "abn",
        "acn",
        "participant_type",
        "participant_status",
        "source_systems",
        "source_tables",
        "ingested_timestamp",
    ),
)
PARTICIPANT_MARKET_MEMBERSHIP_TABLE_SPEC = GasTableSpec(
    section="Associations",
    label="Participant market membership",
    table_name=PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME,
    date_columns=("ingested_timestamp",),
    preview_columns=(
        "participant_key",
        "source_system",
        "source_tables",
        "market_code",
        "source_company_id",
        "source_company_code",
        "source_hub_id",
        "source_hub_name",
        "registration_type",
        "registered_capacity",
        "membership_status",
        "participant_identity_source",
        "participant_identity_value",
        "source_file",
        "ingested_timestamp",
    ),
)
PARTICIPANT_TABLE_SPECS = (
    PARTICIPANT_DIM_TABLE_SPEC,
    PARTICIPANT_MARKET_MEMBERSHIP_TABLE_SPEC,
    FACILITY_TABLE_SPECS[0],
    BID_STACK_TABLE_SPEC,
    SETTLEMENT_ACTIVITY_TABLE_SPEC,
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
_PARTICIPANT_DIM_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "participant_identity_source": pl.String,
    "participant_identity_value": pl.String,
    "canonical_participant_name": pl.String,
    "registered_name": pl.String,
    "abn": pl.String,
    "acn": pl.String,
    "participant_type": pl.String,
    "participant_status": pl.String,
    "source_systems": pl.List(pl.String),
    "source_tables": pl.List(pl.String),
    "source_company_ids": pl.List(pl.String),
    "source_surrogate_keys": pl.List(pl.String),
    "source_files": pl.List(pl.String),
    "ingested_timestamp": pl.Datetime("us"),
}
_PARTICIPANT_MARKET_MEMBERSHIP_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "participant_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "market_code": pl.String,
    "source_company_id": pl.String,
    "source_company_code": pl.String,
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "registration_type": pl.String,
    "registered_capacity": pl.String,
    "membership_status": pl.String,
    "participant_identity_source": pl.String,
    "participant_identity_value": pl.String,
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_PARTICIPANT_COVERAGE_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_PARTICIPANT_MEMBERSHIP_COVERAGE_SCHEMA = {
    "source system": pl.String,
    "market code": pl.String,
    "registration type": pl.String,
    "membership status": pl.String,
    "rows": pl.UInt32,
    "participant keys": pl.UInt32,
    "source company ids": pl.UInt32,
    "source company codes": pl.UInt32,
    "hub ids": pl.UInt32,
    "source tables": pl.UInt32,
    "latest ingest": pl.Datetime("us"),
}
_PARTICIPANT_MARKET_FACT_SCHEMA = {
    "related surface": pl.String,
    "source table": pl.String,
    "available rows": pl.UInt32,
    "participant references": pl.UInt32,
    "matched participants": pl.UInt32,
    "detail": pl.String,
}
_PARTICIPANT_PREVIEW_SCHEMA = {
    "identity source": pl.String,
    "identity value": pl.String,
    "participant": pl.String,
    "registered name": pl.String,
    "participant type": pl.String,
    "participant status": pl.String,
    "source systems": pl.String,
    "source tables": pl.String,
    "source company ids": pl.String,
    "latest ingest": pl.Datetime("us"),
}
_PARTICIPANT_MEMBERSHIP_PREVIEW_SCHEMA = {
    "source system": pl.String,
    "market code": pl.String,
    "participant key": pl.String,
    "company id": pl.String,
    "company code": pl.String,
    "hub": pl.String,
    "registration type": pl.String,
    "registered capacity": pl.String,
    "membership status": pl.String,
    "identity source": pl.String,
    "identity value": pl.String,
    "source tables": pl.String,
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
_FACILITY_FLOW_STORAGE_DASHBOARD_ROW_SCHEMA = {
    **_FACILITY_FLOW_STORAGE_RAW_SCHEMA,
    "source_table": pl.String,
}
_FACILITY_FLOW_STORAGE_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_FACILITY_FLOW_STORAGE_SUMMARY_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "facility key": pl.String,
    "source facility id": pl.String,
    "source location id": pl.String,
    "rows": pl.UInt32,
    "gas days": pl.UInt32,
    "demand rows": pl.UInt32,
    "total demand tj": pl.Float64,
    "supply rows": pl.UInt32,
    "total supply tj": pl.Float64,
    "transfer in rows": pl.UInt32,
    "total transfer in tj": pl.Float64,
    "transfer out rows": pl.UInt32,
    "total transfer out tj": pl.Float64,
    "held storage rows": pl.UInt32,
    "latest held storage tj": pl.Float64,
    "cushion gas rows": pl.UInt32,
    "latest cushion gas storage tj": pl.Float64,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_FACILITY_FLOW_STORAGE_DAILY_SCHEMA = {
    "gas date": pl.Date,
    "rows": pl.UInt32,
    "facilities": pl.UInt32,
    "source systems": pl.UInt32,
    "demand rows": pl.UInt32,
    "total demand tj": pl.Float64,
    "supply rows": pl.UInt32,
    "total supply tj": pl.Float64,
    "transfer in rows": pl.UInt32,
    "total transfer in tj": pl.Float64,
    "transfer out rows": pl.UInt32,
    "total transfer out tj": pl.Float64,
    "held storage rows": pl.UInt32,
    "total held storage tj": pl.Float64,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_FACILITY_FLOW_STORAGE_SOURCE_COVERAGE_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "rows": pl.UInt32,
    "facility keys": pl.UInt32,
    "source facilities": pl.UInt32,
    "source locations": pl.UInt32,
    "gas days": pl.UInt32,
    "measure rows": pl.UInt32,
    "source files": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_FACILITY_FLOW_STORAGE_OBSERVATION_SCHEMA = {
    "gas date": pl.Date,
    "source system": pl.String,
    "source table": pl.String,
    "facility key": pl.String,
    "location key": pl.String,
    "source facility id": pl.String,
    "source location id": pl.String,
    "demand_tj": pl.Float64,
    "supply_tj": pl.Float64,
    "transfer_in_tj": pl.Float64,
    "transfer_out_tj": pl.Float64,
    "held_in_storage_tj": pl.Float64,
    "cushion_gas_storage_tj": pl.Float64,
    "source file": pl.String,
    "source updated": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_FORECAST_ACTUAL_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_FORECAST_ACTUAL_COMPARISON_SCHEMA = {
    "gas date": pl.Date,
    "source facility id": pl.String,
    "source location id": pl.String,
    "match status": pl.String,
    "forecast rows": pl.UInt32,
    "actual rows": pl.UInt32,
    "forecast source systems": pl.String,
    "actual source systems": pl.String,
    "forecast source tables": pl.String,
    "actual source tables": pl.String,
    "forecast type/version pairs": pl.UInt32,
    "forecast demand gj": pl.Float64,
    "actual demand gj": pl.Float64,
    "demand delta gj": pl.Float64,
    "demand delta pct": pl.Float64,
    "forecast supply gj": pl.Float64,
    "actual supply gj": pl.Float64,
    "supply delta gj": pl.Float64,
    "supply delta pct": pl.Float64,
    "forecast transfer in gj": pl.Float64,
    "actual transfer in gj": pl.Float64,
    "transfer in delta gj": pl.Float64,
    "transfer in delta pct": pl.Float64,
    "forecast transfer out gj": pl.Float64,
    "actual transfer out gj": pl.Float64,
    "transfer out delta gj": pl.Float64,
    "transfer out delta pct": pl.Float64,
    "latest forecast update": pl.Datetime("us"),
    "latest actual update": pl.Datetime("us"),
    "latest forecast ingest": pl.Datetime("us"),
    "latest actual ingest": pl.Datetime("us"),
}
_FORECAST_ACTUAL_STORAGE_SCHEMA = {
    "gas date": pl.Date,
    "source facility id": pl.String,
    "source location id": pl.String,
    "forecast coverage": pl.String,
    "actual rows": pl.UInt32,
    "actual source systems": pl.String,
    "actual source tables": pl.String,
    "held storage rows": pl.UInt32,
    "held in storage tj": pl.Float64,
    "cushion gas rows": pl.UInt32,
    "cushion gas storage tj": pl.Float64,
    "latest actual update": pl.Datetime("us"),
    "latest actual ingest": pl.Datetime("us"),
}
_LINEPACK_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "facility_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "gas_date": pl.Date,
    "observation_timestamp": pl.Datetime("us"),
    "source_facility_id": pl.String,
    "actual_linepack_gj": pl.Float64,
    "adequacy_flag": pl.String,
    "adequacy_description": pl.String,
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "ingested_timestamp": pl.Datetime("us"),
}
_LINEPACK_DASHBOARD_ROW_SCHEMA = {
    **_LINEPACK_RAW_SCHEMA,
    "source_table": pl.String,
}
_LINEPACK_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_LINEPACK_SUMMARY_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "facility key": pl.String,
    "zone key": pl.String,
    "source facility id": pl.String,
    "adequacy flag": pl.String,
    "adequacy description": pl.String,
    "rows": pl.UInt32,
    "gas days": pl.UInt32,
    "linepack rows": pl.UInt32,
    "avg linepack gj": pl.Float64,
    "latest linepack gj": pl.Float64,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest observation": pl.Datetime("us"),
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_LINEPACK_SOURCE_COVERAGE_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "rows": pl.UInt32,
    "facility keys": pl.UInt32,
    "zone keys": pl.UInt32,
    "source facilities": pl.UInt32,
    "gas days": pl.UInt32,
    "linepack rows": pl.UInt32,
    "adequacy flags": pl.UInt32,
    "adequacy descriptions": pl.UInt32,
    "source files": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest observation": pl.Datetime("us"),
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_LINEPACK_OBSERVATION_SCHEMA = {
    "gas date": pl.Date,
    "observation timestamp": pl.Datetime("us"),
    "source system": pl.String,
    "source table": pl.String,
    "facility key": pl.String,
    "zone key": pl.String,
    "source facility id": pl.String,
    "actual_linepack_gj": pl.Float64,
    "adequacy flag": pl.String,
    "adequacy description": pl.String,
    "source file": pl.String,
    "source updated": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
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
    "outlook_month": pl.Int64,
    "outlook_year": pl.Int64,
    "receipt_location_id": pl.String,
    "delivery_location_id": pl.String,
    "capacity_quantity_tj": pl.Float64,
    "capacity_description": pl.String,
    "source_last_updated": pl.String,
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "ingested_timestamp": pl.Datetime("us"),
}
_CAPACITY_OUTLOOK_DASHBOARD_ROW_SCHEMA = {
    **_FACILITY_CAPACITY_RAW_SCHEMA,
    "source_table": pl.String,
    "date_range": pl.String,
    "capacity_source_coverage": pl.String,
}
_CAPACITY_OUTLOOK_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_CAPACITY_OUTLOOK_SUMMARY_SCHEMA = {
    "capacity source coverage": pl.String,
    "source system": pl.String,
    "source table": pl.String,
    "source facility id": pl.String,
    "facility": pl.String,
    "capacity type": pl.String,
    "direction": pl.String,
    "date range": pl.String,
    "rows": pl.UInt32,
    "capacity rows": pl.UInt32,
    "total capacity tj": pl.Float64,
    "avg capacity tj": pl.Float64,
    "max capacity tj": pl.Float64,
    "first from gas date": pl.Date,
    "latest to gas date": pl.Date,
    "outlook months": pl.UInt32,
    "source files": pl.UInt32,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_CAPACITY_OUTLOOK_SOURCE_COVERAGE_SCHEMA = {
    "capacity source coverage": pl.String,
    "source system": pl.String,
    "source table": pl.String,
    "rows": pl.UInt32,
    "facilities": pl.UInt32,
    "capacity types": pl.UInt32,
    "directions": pl.UInt32,
    "date ranges": pl.UInt32,
    "capacity rows": pl.UInt32,
    "total capacity tj": pl.Float64,
    "first from gas date": pl.Date,
    "latest to gas date": pl.Date,
    "source files": pl.UInt32,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_CAPACITY_OUTLOOK_OBSERVATION_SCHEMA = {
    "capacity source coverage": pl.String,
    "from gas date": pl.Date,
    "to gas date": pl.Date,
    "outlook month": pl.Int64,
    "outlook year": pl.Int64,
    "source system": pl.String,
    "source table": pl.String,
    "source facility id": pl.String,
    "facility": pl.String,
    "capacity type": pl.String,
    "direction": pl.String,
    "receipt location": pl.String,
    "delivery location": pl.String,
    "capacity_quantity_tj": pl.Float64,
    "capacity description": pl.String,
    "source identifier": pl.String,
    "source file": pl.String,
    "source updated": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
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
_LOCATION_DIM_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_location_id": pl.String,
    "location_name": pl.String,
    "state": pl.String,
    "location_type": pl.String,
    "location_description": pl.String,
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_CONNECTION_POINT_DIM_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "facility_key": pl.String,
    "location_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "source_facility_id": pl.String,
    "source_connection_point_id": pl.String,
    "source_node_id": pl.String,
    "source_location_id": pl.String,
    "connection_point_name": pl.String,
    "flow_direction": pl.String,
    "facility_name": pl.String,
    "location_name": pl.String,
    "state": pl.String,
    "exempt": pl.Boolean,
    "exemption_description": pl.String,
    "effective_date": pl.Date,
    "effective_to_date": pl.Date,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_CONNECTION_POINT_FLOW_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "facility_key": pl.String,
    "location_key": pl.String,
    "connection_point_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "gas_date": pl.Date,
    "source_facility_id": pl.String,
    "source_connection_point_id": pl.String,
    "flow_direction": pl.String,
    "actual_quantity_tj": pl.Float64,
    "quality": pl.String,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_CONNECTION_POINT_COVERAGE_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_CONNECTION_POINT_SOURCE_SYSTEM_SCHEMA = {
    "source system": pl.String,
    "rows": pl.UInt32,
    "connection points": pl.UInt32,
    "facilities": pl.UInt32,
    "locations": pl.UInt32,
    "flow directions": pl.UInt32,
    "source tables": pl.UInt32,
    "latest ingest": pl.Datetime("us"),
}
_CONNECTION_POINT_RELATIONSHIP_SCHEMA = {
    "relationship": pl.String,
    "source table": pl.String,
    "available rows": pl.UInt32,
    "connection points": pl.UInt32,
    "matched connection points": pl.UInt32,
    "detail": pl.String,
}
_CONNECTION_POINT_PREVIEW_SCHEMA = {
    "source-qualified identifier": pl.String,
    "source system": pl.String,
    "source facility id": pl.String,
    "source connection point id": pl.String,
    "connection point": pl.String,
    "flow direction": pl.String,
    "facility": pl.String,
    "location": pl.String,
    "state": pl.String,
    "hub": pl.String,
    "facility key": pl.String,
    "location key": pl.String,
    "zone key": pl.String,
    "source tables": pl.String,
    "latest ingest": pl.Datetime("us"),
}
_NOMINATION_FORECAST_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "facility_key": pl.String,
    "location_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "gas_date": pl.Date,
    "forecast_type": pl.String,
    "forecast_version": pl.String,
    "gas_interval": pl.Int64,
    "source_facility_id": pl.String,
    "source_location_id": pl.String,
    "demand_forecast_gj": pl.Float64,
    "supply_forecast_gj": pl.Float64,
    "transfer_in_forecast_gj": pl.Float64,
    "transfer_out_forecast_gj": pl.Float64,
    "override_quantity_gj": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_NOMINATION_FORECAST_DASHBOARD_ROW_SCHEMA = {
    **_NOMINATION_FORECAST_RAW_SCHEMA,
    "forecast_horizon": pl.String,
}
_NOMINATION_FORECAST_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_NOMINATION_FORECAST_TYPE_VERSION_SCHEMA = {
    "forecast type": pl.String,
    "forecast version": pl.String,
    "forecast horizon": pl.String,
    "rows": pl.UInt32,
    "gas days": pl.UInt32,
    "facilities": pl.UInt32,
    "locations": pl.UInt32,
    "demand rows": pl.UInt32,
    "total demand forecast gj": pl.Float64,
    "supply rows": pl.UInt32,
    "total supply forecast gj": pl.Float64,
    "transfer in rows": pl.UInt32,
    "total transfer in forecast gj": pl.Float64,
    "transfer out rows": pl.UInt32,
    "total transfer out forecast gj": pl.Float64,
    "override rows": pl.UInt32,
    "total override quantity gj": pl.Float64,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_NOMINATION_FORECAST_DAILY_SCHEMA = {
    "gas date": pl.Date,
    "forecast horizon": pl.String,
    "rows": pl.UInt32,
    "forecast type/version pairs": pl.UInt32,
    "source systems": pl.UInt32,
    "facilities": pl.UInt32,
    "locations": pl.UInt32,
    "demand rows": pl.UInt32,
    "total demand forecast gj": pl.Float64,
    "supply rows": pl.UInt32,
    "total supply forecast gj": pl.Float64,
    "transfer in rows": pl.UInt32,
    "total transfer in forecast gj": pl.Float64,
    "transfer out rows": pl.UInt32,
    "total transfer out forecast gj": pl.Float64,
    "override rows": pl.UInt32,
    "total override quantity gj": pl.Float64,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_NOMINATION_FORECAST_SOURCE_COVERAGE_SCHEMA = {
    "source system": pl.String,
    "source table": pl.String,
    "rows": pl.UInt32,
    "forecast types": pl.UInt32,
    "forecast versions": pl.UInt32,
    "gas days": pl.UInt32,
    "facilities": pl.UInt32,
    "locations": pl.UInt32,
    "measure rows": pl.UInt32,
    "source files": pl.UInt32,
    "first gas date": pl.Date,
    "latest gas date": pl.Date,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_NOMINATION_FORECAST_OBSERVATION_SCHEMA = {
    "gas date": pl.Date,
    "forecast horizon": pl.String,
    "source system": pl.String,
    "source table": pl.String,
    "forecast type": pl.String,
    "forecast version": pl.String,
    "gas interval": pl.Int64,
    "facility key": pl.String,
    "location key": pl.String,
    "source facility id": pl.String,
    "source location id": pl.String,
    "demand_forecast_gj": pl.Float64,
    "supply_forecast_gj": pl.Float64,
    "transfer_in_forecast_gj": pl.Float64,
    "transfer_out_forecast_gj": pl.Float64,
    "override_quantity_gj": pl.Float64,
    "source file": pl.String,
    "source updated": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_OPERATIONAL_METER_FLOW_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "operational_point_key": pl.String,
    "zone_key": pl.String,
    "pipeline_segment_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "gas_date": pl.Date,
    "gas_interval": pl.String,
    "point_type": pl.String,
    "source_point_id": pl.String,
    "flow_direction": pl.String,
    "quantity_gj": pl.Float64,
    "commencement_timestamp": pl.Datetime("us"),
    "termination_timestamp": pl.Datetime("us"),
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us"),
}
_FLOW_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_FLOW_SOURCE_SUMMARY_SCHEMA = {
    "fact": pl.String,
    "source system": pl.String,
    "source table": pl.String,
    "rows": pl.UInt32,
    "gas days": pl.UInt32,
    "measure rows": pl.UInt32,
    "latest gas date": pl.Date,
    "latest source update": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
    "row limit": pl.String,
    "detail": pl.String,
}
_FLOW_RECENT_OBSERVATION_SCHEMA = {
    "fact": pl.String,
    "gas date": pl.Date,
    "source system": pl.String,
    "source table": pl.String,
    "flow context": pl.String,
    "measure": pl.String,
    "quantity": pl.Float64,
    "unit": pl.String,
    "source updated": pl.Datetime("us"),
    "latest ingest": pl.Datetime("us"),
}
_HUB_ZONE_DIM_RAW_SCHEMA = {
    "surrogate_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "zone_type": pl.String,
    "source_zone_id": pl.String,
    "zone_name": pl.String,
    "zone_description": pl.String,
    "source_surrogate_keys": pl.List(pl.String),
    "source_files": pl.List(pl.String),
    "ingested_timestamp": pl.Datetime("us"),
}
_HUB_ZONE_COVERAGE_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}
_HUB_ZONE_SOURCE_SYSTEM_SCHEMA = {
    "source system": pl.String,
    "rows": pl.UInt32,
    "zone types": pl.UInt32,
    "source zone ids": pl.UInt32,
    "source tables": pl.UInt32,
    "source files": pl.UInt32,
    "latest ingest": pl.Datetime("us"),
}
_HUB_ZONE_IDENTIFIER_SCHEMA = {
    "source-qualified identifier": pl.String,
    "source system": pl.String,
    "zone type": pl.String,
    "source zone id": pl.String,
    "zone name": pl.String,
    "zone description": pl.String,
    "source tables": pl.String,
    "source files": pl.String,
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


def load_nomination_forecast_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the nomination forecast fact through the shared bounded loader."""
    return load_gas_model_tables(
        config,
        specs=NOMINATION_FORECAST_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_nomination_forecast_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached nomination forecast rows for explicit refreshes."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=NOMINATION_FORECAST_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )[0]


def load_facility_flow_storage_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the facility flow/storage fact through the shared bounded loader."""
    return load_gas_model_tables(
        config,
        specs=(FACILITY_FLOW_STORAGE_TABLE_SPEC,),
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_facility_flow_storage_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached facility flow/storage rows for explicit refreshes."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=(FACILITY_FLOW_STORAGE_TABLE_SPEC,),
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )[0]


def load_forecast_actual_tables(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Load forecast and actual flow/storage facts through the bounded loader."""
    return load_gas_model_tables(
        config,
        specs=FORECAST_ACTUAL_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )


def cached_load_forecast_actual_tables(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Return session-cached forecast-vs-actual rows for explicit refreshes."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=FORECAST_ACTUAL_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )


def load_linepack_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the linepack fact through the shared bounded loader."""
    return load_gas_model_tables(
        config,
        specs=(LINEPACK_TABLE_SPEC,),
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_linepack_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached linepack rows for explicit refreshes."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=(LINEPACK_TABLE_SPEC,),
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )[0]


def load_capacity_outlook_table(
    config: GasDashboardConfig,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Load the capacity outlook fact through the shared bounded loader."""
    return load_gas_model_tables(
        config,
        specs=CAPACITY_OUTLOOK_TABLE_SPECS,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )[0]


def cached_load_capacity_outlook_table(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> GasTableLoad:
    """Return session-cached capacity outlook rows for explicit refreshes."""
    return cached_load_gas_model_tables(
        config,
        cache,
        specs=CAPACITY_OUTLOOK_TABLE_SPECS,
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


def participant_table_specs() -> tuple[GasTableSpec, ...]:
    """Return Participant-oriented tables used by the explainer."""
    return PARTICIPANT_TABLE_SPECS


def load_participant_context_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Load Participant explainer tables through the shared bounded loader."""
    requested_specs = PARTICIPANT_TABLE_SPECS if specs is None else specs
    return load_gas_model_tables(
        _source_coverage_bounded_config(config),
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        clock=clock,
    )


def cached_load_participant_context_tables(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Return cached Participant explainer table reads for explicit refreshes."""
    requested_specs = PARTICIPANT_TABLE_SPECS if specs is None else specs
    return cached_load_gas_model_tables(
        _source_coverage_bounded_config(config),
        cache,
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        refresh_token=refresh_token,
        clock=clock,
    )


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


def connection_point_table_specs() -> tuple[GasTableSpec, ...]:
    """Return the tables used by the Connection Point explainer."""
    return CONNECTION_POINT_TABLE_SPECS


def load_connection_point_context_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Load Connection Point explainer tables through the bounded loader."""
    requested_specs = CONNECTION_POINT_TABLE_SPECS if specs is None else specs
    return load_gas_model_tables(
        _source_coverage_bounded_config(config),
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        clock=clock,
    )


def cached_load_connection_point_context_tables(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Return cached Connection Point explainer reads for explicit refreshes."""
    requested_specs = CONNECTION_POINT_TABLE_SPECS if specs is None else specs
    return cached_load_gas_model_tables(
        _source_coverage_bounded_config(config),
        cache,
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        refresh_token=refresh_token,
        clock=clock,
    )


def flow_table_specs() -> tuple[GasTableSpec, ...]:
    """Return Flow-oriented fact tables used by the operations dashboard."""
    return FLOW_TABLE_SPECS


def load_flow_context_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Load Flow operations tables through the shared bounded loader."""
    requested_specs = FLOW_TABLE_SPECS if specs is None else specs
    return load_gas_model_tables(
        _source_coverage_bounded_config(config),
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.RECENT,
        clock=clock,
    )


def cached_load_flow_context_tables(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Return cached Flow operations table reads for explicit refreshes."""
    requested_specs = FLOW_TABLE_SPECS if specs is None else specs
    return cached_load_gas_model_tables(
        _source_coverage_bounded_config(config),
        cache,
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.RECENT,
        refresh_token=refresh_token,
        clock=clock,
    )


def hub_zone_table_specs() -> tuple[GasTableSpec, ...]:
    """Return the Hub / Zone dimension tables used by the explainer."""
    return HUB_ZONE_TABLE_SPECS


def load_hub_zone_context_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Load Hub / Zone explainer tables through the shared bounded loader."""
    requested_specs = HUB_ZONE_TABLE_SPECS if specs is None else specs
    return load_gas_model_tables(
        _source_coverage_bounded_config(config),
        specs=requested_specs,
        reader=reader,
        view=GasModelTableView.SAMPLE,
        clock=clock,
    )


def cached_load_hub_zone_context_tables(
    config: GasDashboardConfig,
    cache: GasModelSessionCache,
    specs: Sequence[GasTableSpec] | None = None,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasTableLoad]:
    """Return cached Hub / Zone explainer table reads for explicit refreshes."""
    requested_specs = HUB_ZONE_TABLE_SPECS if specs is None else specs
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


def participant_dimension_coverage_frame(load: GasTableLoad | None) -> pl.DataFrame:
    """Return Participant dimension coverage metrics from bounded rows."""
    dataframe = _normalised_participant_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_PARTICIPANT_COVERAGE_SCHEMA)

    source_system_count = _participant_list_value_count(dataframe, "source_systems")
    source_table_count = _participant_list_value_count(dataframe, "source_tables")
    source_company_count = _participant_list_value_count(
        dataframe,
        "source_company_ids",
    )

    return pl.DataFrame(
        [
            {
                "metric": "Participant dimension rows",
                "value": f"{dataframe.height:,}",
                "detail": "Loaded bounded rows from silver_gas_dim_participant",
            },
            {
                "metric": "Identity sources",
                "value": (
                    f"{_distinct_non_empty_count(dataframe, 'participant_identity_source'):,}"
                ),
                "detail": "Distinct participant_identity_source values represented",
            },
            {
                "metric": "Canonical participants",
                "value": (
                    f"{_distinct_non_empty_count(dataframe, 'canonical_participant_name'):,}"
                ),
                "detail": "Distinct canonical_participant_name values represented",
            },
            {
                "metric": "Registered names",
                "value": f"{_distinct_non_empty_count(dataframe, 'registered_name'):,}",
                "detail": "Distinct registered_name values where source data provides them",
            },
            {
                "metric": "Participant types",
                "value": f"{_distinct_non_empty_count(dataframe, 'participant_type'):,}",
                "detail": "Distinct participant_type values in the dimension preview",
            },
            {
                "metric": "Participant statuses",
                "value": (
                    f"{_distinct_non_empty_count(dataframe, 'participant_status'):,}"
                ),
                "detail": "Distinct participant_status values in the dimension preview",
            },
            {
                "metric": "Source systems",
                "value": f"{source_system_count:,}",
                "detail": "Distinct lineage values carried in source_systems",
            },
            {
                "metric": "Source tables",
                "value": f"{source_table_count:,}",
                "detail": "Distinct lineage values carried in source_tables",
            },
            {
                "metric": "Source company ids",
                "value": f"{source_company_count:,}",
                "detail": "Distinct source_company_ids carried by participant rows",
            },
        ],
        schema=_PARTICIPANT_COVERAGE_SCHEMA,
    )


def participant_membership_coverage_frame(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    """Return participant market membership coverage grouped by market metadata."""
    dataframe = _normalised_participant_membership_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_PARTICIPANT_MEMBERSHIP_COVERAGE_SCHEMA)

    rows: list[dict[str, object]] = []
    groups = (
        dataframe.select(
            "source_system",
            "market_code",
            "registration_type",
            "membership_status",
        )
        .unique()
        .sort(
            ["source_system", "market_code", "registration_type"],
            nulls_last=True,
        )
        .to_dicts()
    )
    for group in groups:
        subset = dataframe.filter(
            _participant_group_expression("source_system", group["source_system"])
            & _participant_group_expression("market_code", group["market_code"])
            & _participant_group_expression(
                "registration_type",
                group["registration_type"],
            )
            & _participant_group_expression(
                "membership_status",
                group["membership_status"],
            )
        )
        rows.append(
            {
                "source system": group["source_system"],
                "market code": group["market_code"],
                "registration type": group["registration_type"],
                "membership status": group["membership_status"],
                "rows": subset.height,
                "participant keys": _distinct_non_empty_count(
                    subset,
                    "participant_key",
                ),
                "source company ids": _distinct_non_empty_count(
                    subset,
                    "source_company_id",
                ),
                "source company codes": _distinct_non_empty_count(
                    subset,
                    "source_company_code",
                ),
                "hub ids": _distinct_non_empty_count(subset, "source_hub_id"),
                "source tables": _participant_list_value_count(
                    subset,
                    "source_tables",
                ),
                "latest ingest": _latest_ingest_timestamp(subset),
            }
        )

    return pl.DataFrame(rows, schema=_PARTICIPANT_MEMBERSHIP_COVERAGE_SCHEMA)


def participant_related_market_fact_frame(
    loads: Sequence[GasTableLoad],
) -> pl.DataFrame:
    """Return participant-facing relationships to related market tables."""
    participant_load = table_load_by_name(loads, PARTICIPANT_DIM_TABLE_NAME)
    membership_load = table_load_by_name(
        loads,
        PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME,
    )
    facility_load = table_load_by_name(loads, FACILITY_DIM_TABLE_NAME)
    bid_stack_load = table_load_by_name(loads, BID_STACK_TABLE_NAME)
    settlement_load = table_load_by_name(loads, SETTLEMENT_ACTIVITY_TABLE_NAME)

    participants = _normalised_participant_dimension_dataframe(participant_load)
    memberships = _normalised_participant_membership_dataframe(membership_load)
    facilities = _normalised_facility_dimension_dataframe(facility_load)
    bid_stack = _normalised_bid_stack_dataframe(bid_stack_load)
    settlements = _normalised_settlement_activity_dataframe(settlement_load)

    if (
        participants.is_empty()
        and memberships.is_empty()
        and facilities.is_empty()
        and bid_stack.is_empty()
        and settlements.is_empty()
    ):
        return pl.DataFrame(schema=_PARTICIPANT_MARKET_FACT_SCHEMA)

    participant_keys = _participant_reference_set(participants, "surrogate_key")
    participant_identity_values = _participant_reference_set(
        participants,
        "participant_identity_value",
    )
    participant_names = _participant_name_set(participants)

    rows = [
        {
            "related surface": "Market membership",
            "source table": PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME,
            "available rows": memberships.height,
            "participant references": _distinct_non_empty_count(
                memberships,
                "participant_key",
            ),
            "matched participants": _matched_reference_count(
                memberships,
                "participant_key",
                participant_keys,
            ),
            "detail": (
                "Bridge rows connecting participant_key to market_code, source "
                "system, STTM hub, registration type, and membership status."
            ),
        },
        {
            "related surface": "Facility",
            "source table": FACILITY_DIM_TABLE_NAME,
            "available rows": _non_empty_string_count(facilities, "participant_key"),
            "participant references": _distinct_non_empty_count(
                facilities,
                "participant_key",
            ),
            "matched participants": _matched_reference_count(
                facilities,
                "participant_key",
                participant_keys,
            ),
            "detail": (
                "Facility dimension rows with participant_key populated where "
                "operator participant lineage is resolvable."
            ),
        },
        {
            "related surface": "Bid / Offer",
            "source table": BID_STACK_TABLE_NAME,
            "available rows": bid_stack.height,
            "participant references": _bid_stack_participant_reference_count(
                bid_stack,
            ),
            "matched participants": _matched_bid_stack_participant_count(
                bid_stack,
                participant_identity_values,
                participant_names,
            ),
            "detail": (
                "Bid / Offer stack rows carrying source participant ids and "
                "participant names alongside facility, zone, price, and "
                "quantity fields."
            ),
        },
        {
            "related surface": "Settlement",
            "source table": SETTLEMENT_ACTIVITY_TABLE_NAME,
            "available rows": settlements.height,
            "participant references": _distinct_non_empty_count(
                settlements,
                "participant_name",
            ),
            "matched participants": _matched_reference_count(
                settlements,
                "participant_name",
                participant_names,
            ),
            "detail": (
                "Settlement activity rows carrying participant_name with "
                "amount, quantity, percentage, schedule, and network context."
            ),
        },
    ]
    return pl.DataFrame(rows, schema=_PARTICIPANT_MARKET_FACT_SCHEMA)


def participant_dimension_preview_frame(
    load: GasTableLoad | None,
    *,
    preview_rows: int = DEFAULT_PARTICIPANT_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return a table-friendly preview of participant standing data."""
    dataframe = _normalised_participant_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_PARTICIPANT_PREVIEW_SCHEMA)

    rows: list[dict[str, object]] = []
    for row in (
        dataframe.sort(
            [
                "participant_identity_source",
                "participant_identity_value",
                "canonical_participant_name",
            ],
            nulls_last=True,
        )
        .head(max(1, preview_rows))
        .to_dicts()
    ):
        rows.append(
            {
                "identity source": row.get("participant_identity_source"),
                "identity value": row.get("participant_identity_value"),
                "participant": row.get("canonical_participant_name"),
                "registered name": row.get("registered_name"),
                "participant type": row.get("participant_type"),
                "participant status": row.get("participant_status"),
                "source systems": ", ".join(
                    _source_coverage_value_strings(row.get("source_systems"))
                ),
                "source tables": ", ".join(
                    _source_coverage_value_strings(row.get("source_tables"))
                ),
                "source company ids": ", ".join(
                    _source_coverage_value_strings(row.get("source_company_ids"))
                ),
                "latest ingest": row.get("ingested_timestamp"),
            }
        )
    return pl.DataFrame(rows, schema=_PARTICIPANT_PREVIEW_SCHEMA)


def participant_membership_preview_frame(
    load: GasTableLoad | None,
    *,
    preview_rows: int = DEFAULT_PARTICIPANT_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return a table-friendly preview of participant market memberships."""
    dataframe = _normalised_participant_membership_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_PARTICIPANT_MEMBERSHIP_PREVIEW_SCHEMA)

    rows: list[dict[str, object]] = []
    for row in (
        dataframe.sort(
            ["source_system", "market_code", "source_company_id"],
            nulls_last=True,
        )
        .head(max(1, preview_rows))
        .to_dicts()
    ):
        rows.append(
            {
                "source system": row.get("source_system"),
                "market code": row.get("market_code"),
                "participant key": row.get("participant_key"),
                "company id": row.get("source_company_id"),
                "company code": row.get("source_company_code"),
                "hub": row.get("source_hub_name") or row.get("source_hub_id"),
                "registration type": row.get("registration_type"),
                "registered capacity": row.get("registered_capacity"),
                "membership status": row.get("membership_status"),
                "identity source": row.get("participant_identity_source"),
                "identity value": row.get("participant_identity_value"),
                "source tables": ", ".join(
                    _source_coverage_value_strings(row.get("source_tables"))
                ),
                "latest ingest": row.get("ingested_timestamp"),
            }
        )
    return pl.DataFrame(rows, schema=_PARTICIPANT_MEMBERSHIP_PREVIEW_SCHEMA)


def participant_context_empty_state_markdown(loads: Sequence[GasTableLoad]) -> str:
    """Return empty-state copy for the Participant explainer dashboard."""
    if len(loads) == 0:
        return """
        **No Participant context tables were requested.**

        The dashboard expected Participant-oriented `silver.gas_model` table
        specs but received none. Check the Marimo dashboard registry and
        Participant explainer configuration.
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
    **No Participant metadata, membership, or related fact rows are available.**

    The dashboard checked `{len(loads)}` Participant-oriented
    `silver.gas_model` assets, including `silver_gas_dim_participant`,
    `silver_gas_participant_market_membership`, `silver_gas_dim_facility`,
    `silver_gas_fact_bid_stack`, and `silver_gas_fact_settlement_activity`.
    {read_detail}

    {read_policy}

    Materialize or seed the curated gas model outputs, then use
    **Refresh data**.
    """


def render_participant_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Participant links to related dashboards and concept panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        PARTICIPANT_CONTEXT_ID,
        "source-coverage-matrix",
        "gas-model-table-explorer",
        "bid-offer-context",
        "settlement-context",
        "facility-context",
        "gas-customer-transfer-activity",
    )
    rows = "\n".join(
        _render_participant_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="participant-links__empty">'
            "No Participant, bid, settlement, facility, or table explorer "
            "entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_participant_context_links_css()}
</style>
<section class="participant-links" aria-label="Participant context links">
    <div>
        <p class="participant-links__eyebrow">Context links</p>
        <h2>Participant, membership, bid, settlement, and facility context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


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


def connection_point_dimension_coverage_frame(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    """Return Connection Point dimension coverage metrics from bounded rows."""
    dataframe = _normalised_connection_point_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CONNECTION_POINT_COVERAGE_SCHEMA)

    source_table_count = _connection_point_list_value_count(
        dataframe,
        "source_tables",
    )
    relationship_counts = {
        column: _non_empty_string_count(dataframe, column)
        for column in _CONNECTION_POINT_RELATIONSHIP_KEY_COLUMNS
    }

    return pl.DataFrame(
        [
            {
                "metric": "Connection point dimension rows",
                "value": f"{dataframe.height:,}",
                "detail": "Loaded bounded rows from silver_gas_dim_connection_point",
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
                "metric": "Connection point IDs",
                "value": (
                    f"{_distinct_non_empty_count(dataframe, 'source_connection_point_id'):,}"
                ),
                "detail": "Distinct source_connection_point_id values represented",
            },
            {
                "metric": "Facility links",
                "value": f"{relationship_counts['facility_key']:,}",
                "detail": "Rows with facility_key populated",
            },
            {
                "metric": "Location links",
                "value": f"{relationship_counts['location_key']:,}",
                "detail": "Rows with location_key populated",
            },
            {
                "metric": "Zone links",
                "value": f"{relationship_counts['zone_key']:,}",
                "detail": "Rows with zone_key populated",
            },
            {
                "metric": "Flow directions",
                "value": f"{_distinct_non_empty_count(dataframe, 'flow_direction'):,}",
                "detail": "Distinct flow_direction values in the dimension preview",
            },
            {
                "metric": "Data exemption rows",
                "value": f"{_connection_point_exempt_row_count(dataframe):,}",
                "detail": "Rows where source data marks the connection point exempt",
            },
        ],
        schema=_CONNECTION_POINT_COVERAGE_SCHEMA,
    )


def connection_point_source_system_frame(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    """Return Connection Point coverage grouped by source_system."""
    dataframe = _normalised_connection_point_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CONNECTION_POINT_SOURCE_SYSTEM_SCHEMA)

    rows: list[dict[str, object]] = []
    for source_system in _connection_point_source_systems(dataframe):
        subset = dataframe.filter(pl.col("source_system") == source_system)
        rows.append(
            {
                "source system": source_system,
                "rows": subset.height,
                "connection points": _distinct_non_empty_count(
                    subset,
                    "source_connection_point_id",
                ),
                "facilities": _distinct_non_empty_count(subset, "source_facility_id"),
                "locations": _distinct_non_empty_count(subset, "source_location_id"),
                "flow directions": _distinct_non_empty_count(
                    subset,
                    "flow_direction",
                ),
                "source tables": _connection_point_list_value_count(
                    subset,
                    "source_tables",
                ),
                "latest ingest": _latest_ingest_timestamp(subset),
            }
        )

    return pl.DataFrame(rows, schema=_CONNECTION_POINT_SOURCE_SYSTEM_SCHEMA)


def connection_point_relationship_frame(
    loads: Sequence[GasTableLoad],
) -> pl.DataFrame:
    """Return Connection Point relationships to dimensions and related facts."""
    connection_point_load = table_load_by_name(loads, CONNECTION_POINT_DIM_TABLE_NAME)
    facility_load = table_load_by_name(loads, FACILITY_DIM_TABLE_NAME)
    location_load = table_load_by_name(loads, LOCATION_DIM_TABLE_NAME)
    hub_zone_load = table_load_by_name(loads, HUB_ZONE_DIM_TABLE_NAME)
    flow_load = table_load_by_name(loads, CONNECTION_POINT_FLOW_TABLE_NAME)
    capacity_load = table_load_by_name(loads, FACILITY_CAPACITY_OUTLOOK_TABLE_NAME)

    connection_points = _normalised_connection_point_dimension_dataframe(
        connection_point_load
    )
    facilities = _normalised_facility_dimension_dataframe(facility_load)
    locations = _normalised_location_dimension_dataframe(location_load)
    zones = _normalised_hub_zone_dimension_dataframe(hub_zone_load)
    flows = _normalised_connection_point_flow_dataframe(flow_load)
    capacity = _normalised_facility_capacity_dataframe(capacity_load)

    if (
        connection_points.is_empty()
        and facilities.is_empty()
        and locations.is_empty()
        and zones.is_empty()
        and flows.is_empty()
        and capacity.is_empty()
    ):
        return pl.DataFrame(schema=_CONNECTION_POINT_RELATIONSHIP_SCHEMA)

    connection_point_keys = _connection_point_identifier_set(
        connection_points,
        "surrogate_key",
    )
    connection_point_tuples = _connection_point_tuple_set(connection_points)
    facility_rows = connection_points.filter(
        _non_empty_string_expression("facility_key")
    )
    location_rows = connection_points.filter(
        _non_empty_string_expression("location_key")
    )
    zone_rows = connection_points.filter(_non_empty_string_expression("zone_key"))
    flow_direction_rows = connection_points.filter(
        _non_empty_string_expression("flow_direction")
    )
    quantity_rows = flows.filter(pl.col("actual_quantity_tj").is_not_null())
    capacity_rows = capacity.filter(pl.col("capacity_quantity_tj").is_not_null())

    rows = [
        {
            "relationship": "Facility",
            "source table": CONNECTION_POINT_DIM_TABLE_NAME,
            "available rows": facility_rows.height,
            "connection points": _distinct_non_empty_count(
                connection_points,
                "source_connection_point_id",
            ),
            "matched connection points": _matched_connection_dimension_count(
                facility_rows,
                facilities,
                "facility_key",
                "source_facility_id",
            ),
            "detail": (
                "facility_key and source_facility_id connect connection points "
                "to Facility context when the Facility dimension is available."
            ),
        },
        {
            "relationship": "Location",
            "source table": CONNECTION_POINT_DIM_TABLE_NAME,
            "available rows": location_rows.height,
            "connection points": _distinct_non_empty_count(
                connection_points,
                "source_connection_point_id",
            ),
            "matched connection points": _matched_connection_dimension_count(
                location_rows,
                locations,
                "location_key",
                "source_location_id",
            ),
            "detail": (
                "location_key and source_location_id connect connection points "
                "to GBB location standing data where available."
            ),
        },
        {
            "relationship": "Zone",
            "source table": CONNECTION_POINT_DIM_TABLE_NAME,
            "available rows": zone_rows.height,
            "connection points": _distinct_non_empty_count(
                connection_points,
                "source_connection_point_id",
            ),
            "matched connection points": _matched_connection_dimension_count(
                zone_rows,
                zones,
                "zone_key",
                "source_hub_id",
            ),
            "detail": (
                "zone_key and hub identifiers connect hub-scoped connection "
                "points to Hub / Zone context where the source can resolve them."
            ),
        },
        {
            "relationship": "Flow direction",
            "source table": CONNECTION_POINT_DIM_TABLE_NAME,
            "available rows": flow_direction_rows.height,
            "connection points": _distinct_non_empty_count(
                flow_direction_rows,
                "source_connection_point_id",
            ),
            "matched connection points": _distinct_non_empty_count(
                flow_direction_rows,
                "flow_direction",
            ),
            "detail": (
                "flow_direction separates receipt, delivery, and not-applicable "
                "connection point identifiers before downstream flow and capacity use."
            ),
        },
        {
            "relationship": "Actual flow",
            "source table": CONNECTION_POINT_FLOW_TABLE_NAME,
            "available rows": quantity_rows.height,
            "connection points": _distinct_non_empty_count(
                quantity_rows,
                "source_connection_point_id",
            ),
            "matched connection points": _matched_connection_flow_count(
                quantity_rows,
                connection_point_keys,
                connection_point_tuples,
            ),
            "detail": (
                "Connection point flow rows match the dimension by "
                "connection_point_key or source facility, connection point, "
                "and flow direction."
            ),
        },
        {
            "relationship": "Capacity",
            "source table": FACILITY_CAPACITY_OUTLOOK_TABLE_NAME,
            "available rows": capacity_rows.height,
            "connection points": _distinct_non_empty_count(
                capacity_rows,
                "source_facility_id",
            ),
            "matched connection points": _matched_capacity_flow_direction_count(
                capacity_rows,
                connection_point_tuples,
            ),
            "detail": (
                "Capacity outlook rows can be read beside connection points by "
                "source facility and flow_direction; they do not carry a direct "
                "connection_point_key."
            ),
        },
    ]
    return pl.DataFrame(rows, schema=_CONNECTION_POINT_RELATIONSHIP_SCHEMA)


def connection_point_dimension_preview_frame(
    load: GasTableLoad | None,
    *,
    preview_rows: int = DEFAULT_CONNECTION_POINT_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return source-qualified connection point identifiers for display."""
    dataframe = _normalised_connection_point_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CONNECTION_POINT_PREVIEW_SCHEMA)

    rows: list[dict[str, object]] = []
    for row in (
        dataframe.sort(
            [
                "source_system",
                "source_facility_id",
                "source_connection_point_id",
                "flow_direction",
            ],
            nulls_last=True,
        )
        .head(max(1, preview_rows))
        .to_dicts()
    ):
        rows.append(
            {
                "source-qualified identifier": (
                    _connection_point_source_qualified_identifier(row)
                ),
                "source system": row.get("source_system"),
                "source facility id": row.get("source_facility_id"),
                "source connection point id": row.get("source_connection_point_id"),
                "connection point": row.get("connection_point_name"),
                "flow direction": row.get("flow_direction"),
                "facility": row.get("facility_name"),
                "location": row.get("location_name"),
                "state": row.get("state"),
                "hub": _connection_point_hub_label(row),
                "facility key": row.get("facility_key"),
                "location key": row.get("location_key"),
                "zone key": row.get("zone_key"),
                "source tables": ", ".join(
                    _source_coverage_value_strings(row.get("source_tables"))
                ),
                "latest ingest": row.get("ingested_timestamp"),
            }
        )
    return pl.DataFrame(rows, schema=_CONNECTION_POINT_PREVIEW_SCHEMA)


def connection_point_context_empty_state_markdown(
    loads: Sequence[GasTableLoad],
) -> str:
    """Return empty-state copy for the Connection Point explainer dashboard."""
    if len(loads) == 0:
        return """
        **No Connection Point context tables were requested.**

        The dashboard expected Connection Point-oriented `silver.gas_model`
        table specs but received none. Check the Marimo dashboard registry and
        Connection Point explainer configuration.
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
    **No Connection Point metadata or relationship rows are available.**

    The dashboard checked `{len(loads)}` Connection Point-oriented
    `silver.gas_model` assets: `silver_gas_dim_connection_point`,
    `silver_gas_dim_facility`, `silver_gas_dim_location`,
    `silver_gas_dim_zone`, `silver_gas_fact_connection_point_flow`, and
    `silver_gas_fact_capacity_outlook`. {read_detail}

    {read_policy}

    Materialize or seed the curated gas model outputs, then use
    **Refresh data**.
    """


def hub_zone_dimension_coverage_frame(load: GasTableLoad | None) -> pl.DataFrame:
    """Return Hub / Zone dimension coverage metrics from bounded rows."""
    dataframe = _normalised_hub_zone_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_HUB_ZONE_COVERAGE_SCHEMA)

    sttm_hub_rows = _hub_zone_type_row_count(dataframe, "sttm_hub")
    source_table_count = _hub_zone_list_value_count(dataframe, "source_tables")
    source_file_count = _hub_zone_list_value_count(dataframe, "source_files")

    return pl.DataFrame(
        [
            {
                "metric": "Zone dimension rows",
                "value": f"{dataframe.height:,}",
                "detail": "Loaded bounded rows from silver_gas_dim_zone",
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
                "metric": "Zone types",
                "value": f"{_distinct_non_empty_count(dataframe, 'zone_type'):,}",
                "detail": "Distinct zone_type values in the dimension preview",
            },
            {
                "metric": "STTM hubs",
                "value": f"{sttm_hub_rows:,}",
                "detail": "Rows where zone_type is sttm_hub",
            },
            {
                "metric": "DWGM/GBB zone rows",
                "value": f"{dataframe.height - sttm_hub_rows:,}",
                "detail": "Non-STTM rows such as demand, linepack, HV, and TUOS zones",
            },
            {
                "metric": "Source-qualified identifiers",
                "value": f"{_hub_zone_source_qualified_count(dataframe):,}",
                "detail": "Distinct source_system + zone_type + source_zone_id keys",
            },
            {
                "metric": "Source files",
                "value": f"{source_file_count:,}",
                "detail": "Distinct lineage files carried in source_files",
            },
        ],
        schema=_HUB_ZONE_COVERAGE_SCHEMA,
    )


def hub_zone_source_system_frame(load: GasTableLoad | None) -> pl.DataFrame:
    """Return Hub / Zone coverage grouped by source_system."""
    dataframe = _normalised_hub_zone_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_HUB_ZONE_SOURCE_SYSTEM_SCHEMA)

    rows: list[dict[str, object]] = []
    for source_system in _hub_zone_source_systems(dataframe):
        subset = dataframe.filter(pl.col("source_system") == source_system)
        rows.append(
            {
                "source system": source_system,
                "rows": subset.height,
                "zone types": _distinct_non_empty_count(subset, "zone_type"),
                "source zone ids": _distinct_non_empty_count(
                    subset,
                    "source_zone_id",
                ),
                "source tables": _hub_zone_list_value_count(subset, "source_tables"),
                "source files": _hub_zone_list_value_count(subset, "source_files"),
                "latest ingest": _hub_zone_latest_ingest(subset),
            }
        )

    return pl.DataFrame(rows, schema=_HUB_ZONE_SOURCE_SYSTEM_SCHEMA)


def hub_zone_identifier_preview_frame(
    load: GasTableLoad | None,
    *,
    preview_rows: int = DEFAULT_HUB_ZONE_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return source-qualified Hub / Zone identifiers for table display."""
    dataframe = _normalised_hub_zone_dimension_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_HUB_ZONE_IDENTIFIER_SCHEMA)

    rows: list[dict[str, object]] = []
    for row in (
        dataframe.sort(
            ["source_system", "zone_type", "source_zone_id"],
            nulls_last=True,
        )
        .head(max(1, preview_rows))
        .to_dicts()
    ):
        rows.append(
            {
                "source-qualified identifier": _hub_zone_source_qualified_identifier(
                    row
                ),
                "source system": row.get("source_system"),
                "zone type": row.get("zone_type"),
                "source zone id": row.get("source_zone_id"),
                "zone name": row.get("zone_name"),
                "zone description": row.get("zone_description"),
                "source tables": ", ".join(
                    _source_coverage_value_strings(row.get("source_tables"))
                ),
                "source files": ", ".join(
                    _source_coverage_value_strings(row.get("source_files"))
                ),
                "latest ingest": row.get("ingested_timestamp"),
            }
        )

    return pl.DataFrame(rows, schema=_HUB_ZONE_IDENTIFIER_SCHEMA)


def hub_zone_context_empty_state_markdown(loads: Sequence[GasTableLoad]) -> str:
    """Return empty-state copy for the Hub / Zone explainer dashboard."""
    if len(loads) == 0:
        return """
        **No Hub / Zone context tables were requested.**

        The dashboard expected the `silver_gas_dim_zone` table spec but
        received none. Check the Marimo dashboard registry and Hub / Zone
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
    **No Hub / Zone metadata rows are available.**

    The dashboard checked `silver.gas_model.silver_gas_dim_zone` for current
    source-qualified hub and zone rows. {read_detail}

    {read_policy}

    Materialize or seed the curated gas model outputs, then use
    **Refresh data**.
    """


def render_hub_zone_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Hub / Zone links to related dashboards and concept panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        HUB_ZONE_CONTEXT_ID,
        "source-coverage-matrix",
        "gas-model-table-explorer",
        "facility-context",
        "connection-point-context",
        "flow-context",
        "capacity-context",
        "schedule-context",
        "bid-offer-context",
        "gbb-interactive-map",
    )
    rows = "\n".join(
        _render_hub_zone_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="hub-zone-links__empty">'
            "No Hub / Zone, Facility, flow, capacity, schedule, bid, or table "
            "explorer entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_hub_zone_context_links_css()}
</style>
<section class="hub-zone-links" aria-label="Hub and Zone context links">
    <div>
        <p class="hub-zone-links__eyebrow">Context links</p>
        <h2>Hub / Zone, source coverage, and downstream dashboards</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def render_facility_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Facility links to related dashboards and concept panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        FACILITY_CONTEXT_ID,
        FACILITY_FLOW_STORAGE_CONTEXT_ID,
        NOMINATION_FORECAST_CONTEXT_ID,
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


def render_connection_point_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Connection Point links to related dashboards and concept panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        CONNECTION_POINT_CONTEXT_ID,
        "gbb-interactive-map",
        "source-coverage-matrix",
        "gas-model-table-explorer",
        "facility-context",
        "hub-zone-context",
        "flow-context",
        "capacity-context",
    )
    rows = "\n".join(
        _render_connection_point_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="connection-point-links__empty">'
            "No Connection Point, Facility, Hub / Zone, flow, capacity, map, or "
            "table explorer entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_connection_point_context_links_css()}
</style>
<section
    class="connection-point-links"
    aria-label="Connection Point context links"
>
    <div>
        <p class="connection-point-links__eyebrow">Context links</p>
        <h2>Connection Point, Facility, flow, capacity, and map context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def flow_source_summary_frame(loads: Sequence[GasTableLoad]) -> pl.DataFrame:
    """Return source-system coverage for loaded Flow fact rows."""
    summaries: dict[tuple[str, str, str], _FlowSourceSummary] = {}

    for load in loads:
        dataframe = _normalised_flow_dataframe(load)
        if dataframe.is_empty():
            continue

        for row in dataframe.to_dicts():
            _update_flow_source_summaries(summaries, load, row)

    if len(summaries) == 0:
        return pl.DataFrame(schema=_FLOW_SOURCE_SUMMARY_SCHEMA)

    return pl.DataFrame(
        [_flow_source_summary_row(summary) for summary in summaries.values()],
        schema=_FLOW_SOURCE_SUMMARY_SCHEMA,
    ).sort(
        ["fact", "source system", "source table"],
        nulls_last=True,
    )


def flow_recent_observation_frame(
    loads: Sequence[GasTableLoad],
    *,
    preview_rows: int = DEFAULT_FLOW_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return recent/sample Flow observations from already bounded reads."""
    rows: list[dict[str, object]] = []

    for load in loads:
        dataframe = _normalised_flow_dataframe(load)
        if dataframe.is_empty():
            continue
        for row in dataframe.to_dicts():
            rows.extend(_flow_observation_rows(load, row))

    if len(rows) == 0:
        return pl.DataFrame(schema=_FLOW_RECENT_OBSERVATION_SCHEMA)

    return (
        pl.DataFrame(rows, schema=_FLOW_RECENT_OBSERVATION_SCHEMA)
        .sort(
            ["gas date", "source updated", "latest ingest", "fact", "measure"],
            descending=[True, True, True, False, False],
            nulls_last=True,
        )
        .head(max(1, preview_rows))
    )


def flow_kpi_frame(loads: Sequence[GasTableLoad]) -> pl.DataFrame:
    """Return first-viewport Flow operations KPIs."""
    source_summary = flow_source_summary_frame(loads)
    recent_observations = flow_recent_observation_frame(loads)
    unavailable_count = sum(load.error is not None for load in loads)
    empty_count = sum(
        load.error is None and (load.dataframe is None or load.dataframe.is_empty())
        for load in loads
    )
    row_limit = _common_row_limit(loads) if len(loads) > 0 else None

    source_rows = source_summary.to_dicts() if not source_summary.is_empty() else []
    source_system_count = len(
        {
            row["source system"]
            for row in source_rows
            if row["source system"] != "(empty source_system value)"
        }
    )
    source_table_count = len(
        {
            row["source table"]
            for row in source_rows
            if row["source table"] != "(empty source_table/source_tables value)"
        }
    )
    latest_gas_date = _flow_latest_gas_date(loads)
    measure_rows = sum(_flow_measure_row_count(load) for load in loads)

    return pl.DataFrame(
        [
            {
                "metric": "Flow facts checked",
                "value": f"{len(loads):,}",
                "detail": "Flow-oriented silver.gas_model table reads requested",
            },
            {
                "metric": "Loaded facts",
                "value": f"{sum(load.available for load in loads):,}",
                "detail": "Tables with at least one loaded bounded row",
            },
            {
                "metric": "Source systems",
                "value": f"{source_system_count:,}",
                "detail": "Distinct populated source_system values in loaded facts",
            },
            {
                "metric": "Source tables",
                "value": f"{source_table_count:,}",
                "detail": "Distinct populated source_table/source_tables values",
            },
            {
                "metric": "Flow measure rows",
                "value": f"{measure_rows:,}",
                "detail": "Rows with at least one populated flow, storage, or forecast measure",
            },
            {
                "metric": "Latest Gas Day",
                "value": _format_optional_value(latest_gas_date),
                "detail": "Maximum gas_date across the loaded bounded Flow rows",
            },
            {
                "metric": "Recent/sample observations",
                "value": f"{recent_observations.height:,}",
                "detail": "Rendered measure observations after bounded reads",
            },
            {
                "metric": "Unavailable or empty facts",
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
        schema=_FLOW_KPI_SCHEMA,
    )


def flow_context_empty_state_markdown(loads: Sequence[GasTableLoad]) -> str:
    """Return empty-state copy for the Flow operations dashboard."""
    if len(loads) == 0:
        return """
        **No Flow operations tables were requested.**

        The dashboard expected Flow-oriented `silver.gas_model` fact table
        specs but received none. Check the Marimo dashboard registry and Flow
        operations configuration.
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
    **No Flow source summaries or recent measure rows are available.**

    The dashboard checked `{len(loads)}` Flow-oriented `silver.gas_model`
    facts: `silver_gas_fact_connection_point_flow`,
    `silver_gas_fact_facility_flow_storage`,
    `silver_gas_fact_nomination_forecast`, and
    `silver_gas_fact_operational_meter_flow`. {read_detail}

    {read_policy}

    Materialize or seed the curated gas model outputs, then use
    **Refresh data**.
    """


def render_flow_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render Flow links to related dashboards and concept panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        FLOW_CONTEXT_ID,
        NOMINATION_FORECAST_CONTEXT_ID,
        FACILITY_FLOW_STORAGE_CONTEXT_ID,
        "gbb-interactive-map",
        "source-coverage-matrix",
        "gas-model-table-explorer",
        "facility-context",
        "connection-point-context",
        "gas-day-context",
        "schedule-context",
        "capacity-context",
    )
    rows = "\n".join(
        _render_flow_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="flow-links__empty">'
            "No Flow, Facility, Connection Point, Gas Day, schedule, capacity, "
            "map, or table explorer entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_flow_context_links_css()}
</style>
<section class="flow-links" aria-label="Flow context links">
    <div>
        <p class="flow-links__eyebrow">Context links</p>
        <h2>Flow, Facility, Connection Point, and Gas Day context</h2>
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


def nomination_forecast_gas_date_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return gas-date filter options for loaded nomination forecast rows."""
    dataframe = _normalised_nomination_forecast_dashboard_dataframe(load)
    if dataframe.is_empty():
        return (NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,)

    values = sorted(
        str(value)
        for value in dataframe.get_column("gas_date").drop_nulls().unique().to_list()
        if value is not None
    )
    return (NOMINATION_FORECAST_GAS_DATE_FILTER_ALL, *reversed(values))


def nomination_forecast_source_system_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-system filter options for nomination forecast rows."""
    return _nomination_forecast_string_filter_options(
        load,
        "source_system",
        NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
    )


def nomination_forecast_facility_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-facility filter options for nomination forecast rows."""
    return _nomination_forecast_string_filter_options(
        load,
        "source_facility_id",
        NOMINATION_FORECAST_FACILITY_FILTER_ALL,
    )


def nomination_forecast_location_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-location filter options for nomination forecast rows."""
    return _nomination_forecast_string_filter_options(
        load,
        "source_location_id",
        NOMINATION_FORECAST_LOCATION_FILTER_ALL,
    )


def nomination_forecast_kpi_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
    source_system_filter: str = NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
    facility_filter: str = NOMINATION_FORECAST_FACILITY_FILTER_ALL,
    location_filter: str = NOMINATION_FORECAST_LOCATION_FILTER_ALL,
    *,
    as_of_date: date | None = None,
) -> pl.DataFrame:
    """Return first-viewport KPIs for nomination and demand forecast rows."""
    dataframe = _filtered_nomination_forecast_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        facility_filter,
        location_filter,
        as_of_date=as_of_date,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_NOMINATION_FORECAST_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_rows"),
        pl.col("forecast_type").drop_nulls().n_unique().alias("forecast_types"),
        pl.col("forecast_version").drop_nulls().n_unique().alias("forecast_versions"),
        pl.col("source_system").drop_nulls().n_unique().alias("source_systems"),
        pl.col("source_facility_id").drop_nulls().n_unique().alias("facilities"),
        pl.col("source_location_id").drop_nulls().n_unique().alias("locations"),
        pl.col("gas_date").drop_nulls().n_unique().alias("gas_days"),
        pl.col("gas_date").max().alias("latest_gas_date"),
        pl.col("demand_forecast_gj").is_not_null().sum().alias("demand_rows"),
        pl.col("demand_forecast_gj").sum().alias("demand_forecast_gj"),
        pl.col("supply_forecast_gj").is_not_null().sum().alias("supply_rows"),
        pl.col("supply_forecast_gj").sum().alias("supply_forecast_gj"),
        pl.col("transfer_in_forecast_gj").is_not_null().sum().alias("transfer_in_rows"),
        pl.col("transfer_in_forecast_gj").sum().alias("transfer_in_forecast_gj"),
        pl.col("transfer_out_forecast_gj")
        .is_not_null()
        .sum()
        .alias("transfer_out_rows"),
        pl.col("transfer_out_forecast_gj").sum().alias("transfer_out_forecast_gj"),
        pl.col("override_quantity_gj").is_not_null().sum().alias("override_rows"),
        pl.col("override_quantity_gj").sum().alias("override_quantity_gj"),
    ).row(0, named=True)
    source_table_count = _nomination_forecast_source_table_count(dataframe)
    type_version_count = _nomination_forecast_type_version_count(dataframe)
    reference_date = _nomination_forecast_reference_date(as_of_date)
    current_future_rows = dataframe.filter(
        pl.col("forecast_horizon") == "Current/future forecast"
    ).height
    historical_rows = dataframe.filter(
        pl.col("forecast_horizon") == "Historical forecast"
    ).height
    row_limit = None if load is None else load.row_limit

    return pl.DataFrame(
        [
            {
                "metric": "Loaded forecast rows",
                "value": f"{counts['loaded_rows']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Forecast type/version pairs",
                "value": f"{type_version_count:,}",
                "detail": (
                    "Distinct forecast_type and forecast_version combinations "
                    "represented"
                ),
            },
            {
                "metric": "Forecast types",
                "value": f"{counts['forecast_types']:,}",
                "detail": "Distinct populated forecast_type values in the view",
            },
            {
                "metric": "Forecast versions",
                "value": f"{counts['forecast_versions']:,}",
                "detail": "Distinct populated forecast_version values in the view",
            },
            {
                "metric": "Current/future forecasts",
                "value": f"{current_future_rows:,}",
                "detail": f"Forecast rows with gas_date on or after {reference_date}",
            },
            {
                "metric": "Historical forecasts",
                "value": f"{historical_rows:,}",
                "detail": (
                    "Forecast rows before the reference date; historical actuals "
                    "are not loaded by this dashboard"
                ),
            },
            {
                "metric": "Source systems",
                "value": f"{counts['source_systems']:,}",
                "detail": "Distinct source_system values in the current view",
            },
            {
                "metric": "Source tables",
                "value": f"{source_table_count:,}",
                "detail": "Distinct source_table/source_tables values represented",
            },
            {
                "metric": "Facilities",
                "value": f"{counts['facilities']:,}",
                "detail": "Distinct source_facility_id values in the current view",
            },
            {
                "metric": "Locations",
                "value": f"{counts['locations']:,}",
                "detail": "Distinct source_location_id values in the current view",
            },
            {
                "metric": "Latest gas date",
                "value": _format_optional_value(counts["latest_gas_date"]),
                "detail": "Maximum gas_date in the loaded bounded rows",
            },
            {
                "metric": "Demand forecast",
                "value": _format_measure_total(
                    counts["demand_forecast_gj"],
                    counts["demand_rows"],
                    suffix=" GJ",
                ),
                "detail": (
                    f"{counts['demand_rows']:,} populated demand_forecast_gj rows"
                ),
            },
            {
                "metric": "Supply forecast",
                "value": _format_measure_total(
                    counts["supply_forecast_gj"],
                    counts["supply_rows"],
                    suffix=" GJ",
                ),
                "detail": (
                    f"{counts['supply_rows']:,} populated supply_forecast_gj rows"
                ),
            },
            {
                "metric": "Transfer in forecast",
                "value": _format_measure_total(
                    counts["transfer_in_forecast_gj"],
                    counts["transfer_in_rows"],
                    suffix=" GJ",
                ),
                "detail": (
                    f"{counts['transfer_in_rows']:,} populated "
                    "transfer_in_forecast_gj rows"
                ),
            },
            {
                "metric": "Transfer out forecast",
                "value": _format_measure_total(
                    counts["transfer_out_forecast_gj"],
                    counts["transfer_out_rows"],
                    suffix=" GJ",
                ),
                "detail": (
                    f"{counts['transfer_out_rows']:,} populated "
                    "transfer_out_forecast_gj rows"
                ),
            },
            {
                "metric": "Override quantity",
                "value": _format_measure_total(
                    counts["override_quantity_gj"],
                    counts["override_rows"],
                    suffix=" GJ",
                ),
                "detail": (
                    f"{counts['override_rows']:,} populated override_quantity_gj rows"
                ),
            },
        ],
        schema=_NOMINATION_FORECAST_KPI_SCHEMA,
    )


def nomination_forecast_summary_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
    source_system_filter: str = NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
    facility_filter: str = NOMINATION_FORECAST_FACILITY_FILTER_ALL,
    location_filter: str = NOMINATION_FORECAST_LOCATION_FILTER_ALL,
    *,
    as_of_date: date | None = None,
) -> pl.DataFrame:
    """Return forecast type/version summaries for the bounded current view."""
    dataframe = _filtered_nomination_forecast_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        facility_filter,
        location_filter,
        as_of_date=as_of_date,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_NOMINATION_FORECAST_TYPE_VERSION_SCHEMA)

    sorted_frame = dataframe.sort(
        ["gas_date", "source_last_updated_timestamp", "ingested_timestamp"],
        nulls_last=True,
    )
    summary = (
        sorted_frame.group_by("forecast_type", "forecast_version", "forecast_horizon")
        .agg(
            pl.len().alias("rows"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("source_facility_id").drop_nulls().n_unique().alias("facilities"),
            pl.col("source_location_id").drop_nulls().n_unique().alias("locations"),
            pl.col("demand_forecast_gj").is_not_null().sum().alias("demand rows"),
            pl.col("demand_forecast_gj").sum().alias("total demand forecast gj"),
            pl.col("supply_forecast_gj").is_not_null().sum().alias("supply rows"),
            pl.col("supply_forecast_gj").sum().alias("total supply forecast gj"),
            pl.col("transfer_in_forecast_gj")
            .is_not_null()
            .sum()
            .alias("transfer in rows"),
            pl.col("transfer_in_forecast_gj")
            .sum()
            .alias("total transfer in forecast gj"),
            pl.col("transfer_out_forecast_gj")
            .is_not_null()
            .sum()
            .alias("transfer out rows"),
            pl.col("transfer_out_forecast_gj")
            .sum()
            .alias("total transfer out forecast gj"),
            pl.col("override_quantity_gj").is_not_null().sum().alias("override rows"),
            pl.col("override_quantity_gj").sum().alias("total override quantity gj"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(
            ["latest gas date", "forecast_type", "forecast_version"],
            descending=[True, False, False],
            nulls_last=True,
        )
        .rename(
            {
                "forecast_type": "forecast type",
                "forecast_version": "forecast version",
                "forecast_horizon": "forecast horizon",
            }
        )
    )
    return summary.select([*list(_NOMINATION_FORECAST_TYPE_VERSION_SCHEMA)])


def nomination_forecast_daily_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
    source_system_filter: str = NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
    facility_filter: str = NOMINATION_FORECAST_FACILITY_FILTER_ALL,
    location_filter: str = NOMINATION_FORECAST_LOCATION_FILTER_ALL,
    *,
    as_of_date: date | None = None,
    preview_rows: int = DEFAULT_NOMINATION_FORECAST_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return recent Gas Day nomination forecast totals."""
    dataframe = _filtered_nomination_forecast_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        facility_filter,
        location_filter,
        as_of_date=as_of_date,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_NOMINATION_FORECAST_DAILY_SCHEMA)

    daily = (
        dataframe.group_by("gas_date", "forecast_horizon")
        .agg(
            pl.len().alias("rows"),
            pl.struct("forecast_type", "forecast_version")
            .n_unique()
            .alias("forecast type/version pairs"),
            pl.col("source_system").drop_nulls().n_unique().alias("source systems"),
            pl.col("source_facility_id").drop_nulls().n_unique().alias("facilities"),
            pl.col("source_location_id").drop_nulls().n_unique().alias("locations"),
            pl.col("demand_forecast_gj").is_not_null().sum().alias("demand rows"),
            pl.col("demand_forecast_gj").sum().alias("total demand forecast gj"),
            pl.col("supply_forecast_gj").is_not_null().sum().alias("supply rows"),
            pl.col("supply_forecast_gj").sum().alias("total supply forecast gj"),
            pl.col("transfer_in_forecast_gj")
            .is_not_null()
            .sum()
            .alias("transfer in rows"),
            pl.col("transfer_in_forecast_gj")
            .sum()
            .alias("total transfer in forecast gj"),
            pl.col("transfer_out_forecast_gj")
            .is_not_null()
            .sum()
            .alias("transfer out rows"),
            pl.col("transfer_out_forecast_gj")
            .sum()
            .alias("total transfer out forecast gj"),
            pl.col("override_quantity_gj").is_not_null().sum().alias("override rows"),
            pl.col("override_quantity_gj").sum().alias("total override quantity gj"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort("gas_date", descending=True, nulls_last=True)
        .rename(
            {
                "gas_date": "gas date",
                "forecast_horizon": "forecast horizon",
            }
        )
        .head(max(1, preview_rows))
    )
    return daily.select([*list(_NOMINATION_FORECAST_DAILY_SCHEMA)])


def nomination_forecast_source_coverage_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
    source_system_filter: str = NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
    facility_filter: str = NOMINATION_FORECAST_FACILITY_FILTER_ALL,
    location_filter: str = NOMINATION_FORECAST_LOCATION_FILTER_ALL,
    *,
    as_of_date: date | None = None,
) -> pl.DataFrame:
    """Return source-system and source-table coverage for loaded forecasts."""
    dataframe = _filtered_nomination_forecast_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        facility_filter,
        location_filter,
        as_of_date=as_of_date,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_NOMINATION_FORECAST_SOURCE_COVERAGE_SCHEMA)

    has_measure = pl.any_horizontal(
        *(
            pl.col(column).is_not_null()
            for column in _NOMINATION_FORECAST_MEASURE_COLUMNS
        )
    )
    coverage = (
        dataframe.group_by("source_system", "source_table")
        .agg(
            pl.len().alias("rows"),
            pl.col("forecast_type").drop_nulls().n_unique().alias("forecast types"),
            pl.col("forecast_version")
            .drop_nulls()
            .n_unique()
            .alias("forecast versions"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("source_facility_id").drop_nulls().n_unique().alias("facilities"),
            pl.col("source_location_id").drop_nulls().n_unique().alias("locations"),
            has_measure.sum().alias("measure rows"),
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
    return coverage.select([*list(_NOMINATION_FORECAST_SOURCE_COVERAGE_SCHEMA)])


def nomination_forecast_observation_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
    source_system_filter: str = NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
    facility_filter: str = NOMINATION_FORECAST_FACILITY_FILTER_ALL,
    location_filter: str = NOMINATION_FORECAST_LOCATION_FILTER_ALL,
    *,
    as_of_date: date | None = None,
    preview_rows: int = DEFAULT_NOMINATION_FORECAST_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return bounded recent/sample nomination forecast observations."""
    dataframe = _filtered_nomination_forecast_dataframe(
        load,
        gas_date_filter,
        source_system_filter,
        facility_filter,
        location_filter,
        as_of_date=as_of_date,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_NOMINATION_FORECAST_OBSERVATION_SCHEMA)

    return (
        dataframe.sort(
            [
                "gas_date",
                "source_last_updated_timestamp",
                "ingested_timestamp",
                "source_system",
                "forecast_type",
                "forecast_version",
                "source_facility_id",
            ],
            descending=[True, True, True, False, False, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("gas_date").alias("gas date"),
            pl.col("forecast_horizon").alias("forecast horizon"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("forecast_type").alias("forecast type"),
            pl.col("forecast_version").alias("forecast version"),
            pl.col("gas_interval").alias("gas interval"),
            pl.col("facility_key").alias("facility key"),
            pl.col("location_key").alias("location key"),
            pl.col("source_facility_id").alias("source facility id"),
            pl.col("source_location_id").alias("source location id"),
            pl.col("demand_forecast_gj"),
            pl.col("supply_forecast_gj"),
            pl.col("transfer_in_forecast_gj"),
            pl.col("transfer_out_forecast_gj"),
            pl.col("override_quantity_gj"),
            pl.col("source_file").alias("source file"),
            pl.col("source_last_updated_timestamp").alias("source updated"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def nomination_forecast_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched forecast rows."""
    table_label = _markdown_breakable_text(
        "silver.gas_model.silver_gas_fact_nomination_forecast"
    )
    if load is None:
        status_detail = "The dashboard did not receive a nomination forecast load."
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = (
                "The current filters do not match any loaded nomination forecast rows."
            )
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No nomination or demand forecast data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    `gas_date`, source system, facility/location fields, `forecast_type`,
    `forecast_version`, demand, supply, transfer, and override forecast measures.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` nomination forecast asset, then
    use **Refresh data**.
    """


def render_nomination_forecast_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render nomination forecast links to related Market context panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        NOMINATION_FORECAST_CONTEXT_ID,
        FLOW_CONTEXT_ID,
        FACILITY_CONTEXT_ID,
        GAS_DAY_CONTEXT_ID,
        FACILITY_FLOW_STORAGE_CONTEXT_ID,
        "gbb-interactive-map",
        "source-coverage-matrix",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_flow_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="flow-links__empty">'
            "No Nomination forecast, Flow, Facility, Gas Day, map, source "
            "coverage, or table explorer entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_flow_context_links_css()}
</style>
<section class="flow-links" aria-label="Nomination forecast context links">
    <div>
        <p class="flow-links__eyebrow">Context links</p>
        <h2>Nomination forecast, Flow, Facility, and Gas Day context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def facility_flow_storage_gas_date_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return gas-date filter options for loaded facility flow/storage rows."""
    dataframe = _normalised_facility_flow_storage_dashboard_dataframe(load)
    if dataframe.is_empty():
        return (FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,)

    values = sorted(
        str(value)
        for value in dataframe.get_column("gas_date").drop_nulls().unique().to_list()
        if value is not None
    )
    return (FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL, *reversed(values))


def facility_flow_storage_facility_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-facility filter options for facility flow/storage rows."""
    return _facility_flow_storage_string_filter_options(
        load,
        "source_facility_id",
        FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
    )


def facility_flow_storage_source_system_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-system filter options for facility flow/storage rows."""
    return _facility_flow_storage_string_filter_options(
        load,
        "source_system",
        FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
    )


def facility_flow_storage_kpi_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
    facility_filter: str = FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
    source_system_filter: str = FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return first-viewport KPIs for loaded facility flow/storage rows."""
    dataframe = _filtered_facility_flow_storage_dataframe(
        load,
        gas_date_filter,
        facility_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_FLOW_STORAGE_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_rows"),
        pl.col("facility_key").drop_nulls().n_unique().alias("facility_keys"),
        pl.col("source_facility_id").drop_nulls().n_unique().alias("source_facilities"),
        pl.col("source_location_id").drop_nulls().n_unique().alias("source_locations"),
        pl.col("source_system").drop_nulls().n_unique().alias("source_systems"),
        pl.col("gas_date").drop_nulls().n_unique().alias("gas_days"),
        pl.col("gas_date").max().alias("latest_gas_date"),
        pl.col("demand_tj").is_not_null().sum().alias("demand_rows"),
        pl.col("demand_tj").sum().alias("demand_tj"),
        pl.col("supply_tj").is_not_null().sum().alias("supply_rows"),
        pl.col("supply_tj").sum().alias("supply_tj"),
        pl.col("transfer_in_tj").is_not_null().sum().alias("transfer_in_rows"),
        pl.col("transfer_in_tj").sum().alias("transfer_in_tj"),
        pl.col("transfer_out_tj").is_not_null().sum().alias("transfer_out_rows"),
        pl.col("transfer_out_tj").sum().alias("transfer_out_tj"),
        pl.col("held_in_storage_tj").is_not_null().sum().alias("held_storage_rows"),
        pl.col("held_in_storage_tj").sum().alias("held_in_storage_tj"),
        pl.col("cushion_gas_storage_tj").is_not_null().sum().alias("cushion_gas_rows"),
        pl.col("cushion_gas_storage_tj").sum().alias("cushion_gas_storage_tj"),
    ).row(0, named=True)
    source_table_count = _facility_flow_storage_source_table_count(dataframe)
    row_limit = None if load is None else load.row_limit

    return pl.DataFrame(
        [
            {
                "metric": "Loaded facility rows",
                "value": f"{counts['loaded_rows']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Facility keys",
                "value": f"{counts['facility_keys']:,}",
                "detail": "Distinct facility_key values in the current view",
            },
            {
                "metric": "Source facilities",
                "value": f"{counts['source_facilities']:,}",
                "detail": "Distinct source_facility_id values in the current view",
            },
            {
                "metric": "Source locations",
                "value": f"{counts['source_locations']:,}",
                "detail": "Distinct source_location_id values in the current view",
            },
            {
                "metric": "Source systems",
                "value": f"{counts['source_systems']:,}",
                "detail": "Distinct source_system values in the current view",
            },
            {
                "metric": "Source tables",
                "value": f"{source_table_count:,}",
                "detail": "Distinct source_table/source_tables values represented",
            },
            {
                "metric": "Gas days",
                "value": f"{counts['gas_days']:,}",
                "detail": "Distinct gas_date values in the current view",
            },
            {
                "metric": "Latest gas date",
                "value": _format_optional_value(counts["latest_gas_date"]),
                "detail": "Maximum gas_date in the loaded bounded rows",
            },
            {
                "metric": "Demand",
                "value": _format_measure_total(
                    counts["demand_tj"],
                    counts["demand_rows"],
                    suffix=" TJ",
                ),
                "detail": f"{counts['demand_rows']:,} populated demand_tj rows",
            },
            {
                "metric": "Supply",
                "value": _format_measure_total(
                    counts["supply_tj"],
                    counts["supply_rows"],
                    suffix=" TJ",
                ),
                "detail": f"{counts['supply_rows']:,} populated supply_tj rows",
            },
            {
                "metric": "Transfer in",
                "value": _format_measure_total(
                    counts["transfer_in_tj"],
                    counts["transfer_in_rows"],
                    suffix=" TJ",
                ),
                "detail": (
                    f"{counts['transfer_in_rows']:,} populated transfer_in_tj rows"
                ),
            },
            {
                "metric": "Transfer out",
                "value": _format_measure_total(
                    counts["transfer_out_tj"],
                    counts["transfer_out_rows"],
                    suffix=" TJ",
                ),
                "detail": (
                    f"{counts['transfer_out_rows']:,} populated transfer_out_tj rows"
                ),
            },
            {
                "metric": "Held in storage",
                "value": _format_measure_total(
                    counts["held_in_storage_tj"],
                    counts["held_storage_rows"],
                    suffix=" TJ",
                ),
                "detail": (
                    f"{counts['held_storage_rows']:,} populated held_in_storage_tj rows"
                ),
            },
            {
                "metric": "Cushion gas storage",
                "value": _format_measure_total(
                    counts["cushion_gas_storage_tj"],
                    counts["cushion_gas_rows"],
                    suffix=" TJ",
                ),
                "detail": (
                    f"{counts['cushion_gas_rows']:,} populated "
                    "cushion_gas_storage_tj rows"
                ),
            },
        ],
        schema=_FACILITY_FLOW_STORAGE_KPI_SCHEMA,
    )


def facility_flow_storage_summary_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
    facility_filter: str = FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
    source_system_filter: str = FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return facility-level flow, transfer, and storage summaries."""
    dataframe = _filtered_facility_flow_storage_dataframe(
        load,
        gas_date_filter,
        facility_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_FLOW_STORAGE_SUMMARY_SCHEMA)

    sorted_frame = dataframe.sort(
        ["gas_date", "source_last_updated_timestamp", "ingested_timestamp"],
        nulls_last=True,
    )
    summary = (
        sorted_frame.group_by(
            "source_system",
            "source_table",
            "facility_key",
            "source_facility_id",
            "source_location_id",
        )
        .agg(
            pl.len().alias("rows"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("demand_tj").is_not_null().sum().alias("demand rows"),
            pl.col("demand_tj").sum().alias("total demand tj"),
            pl.col("supply_tj").is_not_null().sum().alias("supply rows"),
            pl.col("supply_tj").sum().alias("total supply tj"),
            pl.col("transfer_in_tj").is_not_null().sum().alias("transfer in rows"),
            pl.col("transfer_in_tj").sum().alias("total transfer in tj"),
            pl.col("transfer_out_tj").is_not_null().sum().alias("transfer out rows"),
            pl.col("transfer_out_tj").sum().alias("total transfer out tj"),
            pl.col("held_in_storage_tj").is_not_null().sum().alias("held storage rows"),
            pl.col("held_in_storage_tj")
            .drop_nulls()
            .last()
            .alias("latest held storage tj"),
            pl.col("cushion_gas_storage_tj")
            .is_not_null()
            .sum()
            .alias("cushion gas rows"),
            pl.col("cushion_gas_storage_tj")
            .drop_nulls()
            .last()
            .alias("latest cushion gas storage tj"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(
            ["latest gas date", "source_system", "source_facility_id"],
            descending=[True, False, False],
            nulls_last=True,
        )
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
                "facility_key": "facility key",
                "source_facility_id": "source facility id",
                "source_location_id": "source location id",
            }
        )
    )
    return summary.select([*list(_FACILITY_FLOW_STORAGE_SUMMARY_SCHEMA)])


def facility_flow_storage_daily_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
    facility_filter: str = FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
    source_system_filter: str = FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_FACILITY_FLOW_STORAGE_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return recent Gas Day facility flow/storage totals."""
    dataframe = _filtered_facility_flow_storage_dataframe(
        load,
        gas_date_filter,
        facility_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_FLOW_STORAGE_DAILY_SCHEMA)

    daily = (
        dataframe.group_by("gas_date")
        .agg(
            pl.len().alias("rows"),
            pl.col("facility_key").drop_nulls().n_unique().alias("facilities"),
            pl.col("source_system").drop_nulls().n_unique().alias("source systems"),
            pl.col("demand_tj").is_not_null().sum().alias("demand rows"),
            pl.col("demand_tj").sum().alias("total demand tj"),
            pl.col("supply_tj").is_not_null().sum().alias("supply rows"),
            pl.col("supply_tj").sum().alias("total supply tj"),
            pl.col("transfer_in_tj").is_not_null().sum().alias("transfer in rows"),
            pl.col("transfer_in_tj").sum().alias("total transfer in tj"),
            pl.col("transfer_out_tj").is_not_null().sum().alias("transfer out rows"),
            pl.col("transfer_out_tj").sum().alias("total transfer out tj"),
            pl.col("held_in_storage_tj").is_not_null().sum().alias("held storage rows"),
            pl.col("held_in_storage_tj").sum().alias("total held storage tj"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort("gas_date", descending=True, nulls_last=True)
        .rename({"gas_date": "gas date"})
        .head(max(1, preview_rows))
    )
    return daily.select([*list(_FACILITY_FLOW_STORAGE_DAILY_SCHEMA)])


def facility_flow_storage_source_coverage_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
    facility_filter: str = FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
    source_system_filter: str = FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return source-system and source-table coverage for loaded rows."""
    dataframe = _filtered_facility_flow_storage_dataframe(
        load,
        gas_date_filter,
        facility_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_FLOW_STORAGE_SOURCE_COVERAGE_SCHEMA)

    has_measure = pl.any_horizontal(
        *(pl.col(column).is_not_null() for column in _FACILITY_FLOW_STORAGE_MEASURES)
    )
    coverage = (
        dataframe.group_by("source_system", "source_table")
        .agg(
            pl.len().alias("rows"),
            pl.col("facility_key").drop_nulls().n_unique().alias("facility keys"),
            pl.col("source_facility_id")
            .drop_nulls()
            .n_unique()
            .alias("source facilities"),
            pl.col("source_location_id")
            .drop_nulls()
            .n_unique()
            .alias("source locations"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            has_measure.sum().alias("measure rows"),
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
    return coverage.select([*list(_FACILITY_FLOW_STORAGE_SOURCE_COVERAGE_SCHEMA)])


def facility_flow_storage_observation_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
    facility_filter: str = FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
    source_system_filter: str = FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_FACILITY_FLOW_STORAGE_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return bounded recent/sample facility flow/storage observations."""
    dataframe = _filtered_facility_flow_storage_dataframe(
        load,
        gas_date_filter,
        facility_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_FLOW_STORAGE_OBSERVATION_SCHEMA)

    return (
        dataframe.sort(
            [
                "gas_date",
                "source_last_updated_timestamp",
                "ingested_timestamp",
                "source_system",
                "source_facility_id",
            ],
            descending=[True, True, True, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("gas_date").alias("gas date"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("facility_key").alias("facility key"),
            pl.col("location_key").alias("location key"),
            pl.col("source_facility_id").alias("source facility id"),
            pl.col("source_location_id").alias("source location id"),
            pl.col("demand_tj"),
            pl.col("supply_tj"),
            pl.col("transfer_in_tj"),
            pl.col("transfer_out_tj"),
            pl.col("held_in_storage_tj"),
            pl.col("cushion_gas_storage_tj"),
            pl.col("source_file").alias("source file"),
            pl.col("source_last_updated_timestamp").alias("source updated"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def facility_flow_storage_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched facility rows."""
    table_label = _markdown_breakable_text(
        "silver.gas_model.silver_gas_fact_facility_flow_storage"
    )
    if load is None:
        status_detail = "The dashboard did not receive a facility flow/storage load."
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = (
                "The current filters do not match any loaded facility "
                "flow/storage rows."
            )
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No facility flow or storage data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    `facility_key`, `gas_date`, demand, supply, transfer-in, transfer-out,
    `held_in_storage_tj`, cushion-gas storage, source-system, and source-table
    fields.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` facility flow/storage asset,
    then use **Refresh data**.
    """


def render_facility_flow_storage_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render facility flow/storage links to related Market context panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        FACILITY_FLOW_STORAGE_CONTEXT_ID,
        FACILITY_CONTEXT_ID,
        FLOW_CONTEXT_ID,
        "capacity-context",
        "gbb-interactive-map",
        "source-coverage-matrix",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_facility_flow_storage_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="facility-flow-storage-links__empty">'
            "No Facility flow/storage, Facility, Flow, Capacity, map, source "
            "coverage, or table explorer entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_facility_flow_storage_context_links_css()}
</style>
<section
    class="facility-flow-storage-links"
    aria-label="Facility flow and storage context links"
>
    <div>
        <p class="facility-flow-storage-links__eyebrow">Context links</p>
        <h2>Facility, Flow, Capacity, map, and source coverage context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def forecast_actual_gas_date_options(
    loads: Sequence[GasTableLoad],
) -> tuple[str, ...]:
    """Return Gas Day filter options across forecast and actual inputs."""
    forecast, actual = _forecast_actual_input_frames(loads)
    values = {
        str(value)
        for dataframe in (forecast, actual)
        if not dataframe.is_empty()
        for value in dataframe.get_column("gas_date").drop_nulls().unique().to_list()
        if value is not None
    }
    return (FORECAST_ACTUAL_GAS_DATE_FILTER_ALL, *reversed(sorted(values)))


def forecast_actual_facility_options(
    loads: Sequence[GasTableLoad],
) -> tuple[str, ...]:
    """Return source-facility options across forecast and actual inputs."""
    return _forecast_actual_string_filter_options(
        loads,
        "source_facility_id",
        FORECAST_ACTUAL_FACILITY_FILTER_ALL,
    )


def forecast_actual_source_system_options(
    loads: Sequence[GasTableLoad],
) -> tuple[str, ...]:
    """Return source-system options across forecast and actual inputs."""
    return _forecast_actual_string_filter_options(
        loads,
        "source_system",
        FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
    )


def forecast_actual_bounded_scope_markdown(
    config: GasDashboardConfig,
    loads: Sequence[GasTableLoad],
) -> str:
    """Return explicit bounded-scope copy for the comparison dashboard."""
    row_limit = _common_row_limit(loads) if loads else None
    if config.aws_runtime:
        behavior = (
            "AWS mode uses sampled/recent-only bounded reads: each forecast and "
            "actual source table is capped before this dashboard joins the loaded "
            "preview rows."
        )
    else:
        behavior = (
            "Local mode uses the configured gas dashboard read policy; when full "
            "table scans are disabled, the same bounded preview cap applies."
        )

    return f"""
    **Bounded forecast-vs-actual scope.**

    {behavior}

    The comparison joins only the loaded rows sharing `gas_date`,
    `source_facility_id`, and `source_location_id`. Rows outside the bounded
    read window can appear as forecast-only or actual-only until the source
    tables are materialized into a fuller local view.

    {row_limit_message(row_limit)}
    """


def forecast_actual_kpi_frame(
    loads: Sequence[GasTableLoad],
    gas_date_filter: str = FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
    facility_filter: str = FORECAST_ACTUAL_FACILITY_FILTER_ALL,
    source_system_filter: str = FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
    *,
    as_of_date: date | None = None,
) -> pl.DataFrame:
    """Return first-viewport KPIs for forecast-vs-actual bounded rows."""
    forecast_aggs, actual_aggs = _forecast_actual_aggregates(
        loads,
        gas_date_filter,
        facility_filter,
        source_system_filter,
        as_of_date=as_of_date,
    )
    if len(forecast_aggs) == 0 and len(actual_aggs) == 0:
        return pl.DataFrame(schema=_FORECAST_ACTUAL_KPI_SCHEMA)

    keys = set(forecast_aggs) | set(actual_aggs)
    matched_count = sum(key in forecast_aggs and key in actual_aggs for key in keys)
    forecast_only_count = sum(
        key in forecast_aggs and key not in actual_aggs for key in keys
    )
    actual_only_count = sum(
        key in actual_aggs and key not in forecast_aggs for key in keys
    )
    comparable_measure_count = sum(
        _forecast_actual_comparable_measure_count(
            forecast_aggs.get(key),
            actual_aggs.get(key),
        )
        for key in keys
    )
    latest_gas_date = _forecast_actual_latest_gas_date(keys)
    row_limit = _common_row_limit(loads) if loads else None

    return pl.DataFrame(
        [
            {
                "metric": "Forecast rows",
                "value": f"{sum(agg.rows for agg in forecast_aggs.values()):,}",
                "detail": f"{NOMINATION_FORECAST_TABLE_NAME} rows in scope",
            },
            {
                "metric": "Actual rows",
                "value": f"{sum(agg.rows for agg in actual_aggs.values()):,}",
                "detail": f"{FACILITY_FLOW_STORAGE_TABLE_NAME} rows in scope",
            },
            {
                "metric": "Matched facility days",
                "value": f"{matched_count:,}",
                "detail": (
                    "Gas Day plus source facility/location groups present in "
                    "both bounded inputs"
                ),
            },
            {
                "metric": "Forecast-only groups",
                "value": f"{forecast_only_count:,}",
                "detail": "Loaded forecast groups without a matching actual row",
            },
            {
                "metric": "Actual-only groups",
                "value": f"{actual_only_count:,}",
                "detail": "Loaded actual groups without a matching forecast row",
            },
            {
                "metric": "Comparable flow measures",
                "value": f"{comparable_measure_count:,}",
                "detail": "Demand, supply, transfer-in, and transfer-out pairs",
            },
            {
                "metric": "Latest Gas Day",
                "value": _format_optional_value(latest_gas_date),
                "detail": "Maximum gas_date in the loaded bounded comparison",
            },
            {
                "metric": "Read policy",
                "value": format_row_limit(row_limit),
                "detail": "Forecast-vs-actual uses the shared bounded loader",
            },
        ],
        schema=_FORECAST_ACTUAL_KPI_SCHEMA,
    )


def forecast_actual_comparison_frame(
    loads: Sequence[GasTableLoad],
    gas_date_filter: str = FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
    facility_filter: str = FORECAST_ACTUAL_FACILITY_FILTER_ALL,
    source_system_filter: str = FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
    *,
    as_of_date: date | None = None,
    preview_rows: int = DEFAULT_FORECAST_ACTUAL_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return joined forecast-vs-actual flow comparison rows."""
    forecast_aggs, actual_aggs = _forecast_actual_aggregates(
        loads,
        gas_date_filter,
        facility_filter,
        source_system_filter,
        as_of_date=as_of_date,
    )
    keys = sorted(
        set(forecast_aggs) | set(actual_aggs),
        key=_forecast_actual_sort_key,
    )
    if len(keys) == 0:
        return pl.DataFrame(schema=_FORECAST_ACTUAL_COMPARISON_SCHEMA)

    rows = [
        _forecast_actual_comparison_row(
            key,
            forecast_aggs.get(key),
            actual_aggs.get(key),
        )
        for key in keys[: max(1, preview_rows)]
    ]
    return pl.DataFrame(rows, schema=_FORECAST_ACTUAL_COMPARISON_SCHEMA)


def forecast_actual_storage_frame(
    loads: Sequence[GasTableLoad],
    gas_date_filter: str = FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
    facility_filter: str = FORECAST_ACTUAL_FACILITY_FILTER_ALL,
    source_system_filter: str = FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
    *,
    as_of_date: date | None = None,
    preview_rows: int = DEFAULT_FORECAST_ACTUAL_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return actual storage rows with forecast coverage status."""
    forecast_aggs, actual_aggs = _forecast_actual_aggregates(
        loads,
        gas_date_filter,
        facility_filter,
        source_system_filter,
        as_of_date=as_of_date,
    )
    keys = sorted(actual_aggs, key=_forecast_actual_sort_key)
    if len(keys) == 0:
        return pl.DataFrame(schema=_FORECAST_ACTUAL_STORAGE_SCHEMA)

    rows = [
        _forecast_actual_storage_row(
            key,
            actual_aggs[key],
            forecast_available=key in forecast_aggs,
        )
        for key in keys[: max(1, preview_rows)]
    ]
    return pl.DataFrame(rows, schema=_FORECAST_ACTUAL_STORAGE_SCHEMA)


def forecast_actual_empty_state_markdown(loads: Sequence[GasTableLoad]) -> str:
    """Return useful empty-state copy for missing comparison inputs."""
    forecast_load, actual_load = _forecast_actual_load_pair(loads)
    row_limit = _common_row_limit(loads) if loads else None

    return f"""
    **No forecast-vs-actual comparison rows are available for this view.**

    The dashboard compares
    `silver.gas_model.silver_gas_fact_nomination_forecast` with
    `silver.gas_model.silver_gas_fact_facility_flow_storage` where loaded rows
    share `gas_date`, `source_facility_id`, and `source_location_id`.

    Forecast input: {_forecast_actual_load_detail(forecast_load)}

    Actual input: {_forecast_actual_load_detail(actual_load)}

    {row_limit_message(row_limit)}

    Materialize or seed the missing `silver.gas_model` assets, then use
    **Refresh data**. If only one side is available, the dashboard shows
    forecast-only or actual-only rows instead of raising a notebook traceback.
    """


def render_forecast_actual_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render forecast-vs-actual links to related Market context panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        FORECAST_ACTUAL_CONTEXT_ID,
        NOMINATION_FORECAST_CONTEXT_ID,
        FACILITY_FLOW_STORAGE_CONTEXT_ID,
        FLOW_CONTEXT_ID,
        FACILITY_CONTEXT_ID,
        GAS_DAY_CONTEXT_ID,
        "gbb-interactive-map",
        "source-coverage-matrix",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_flow_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="flow-links__empty">'
            "No forecast-vs-actual, Nomination forecast, Facility flow/storage, "
            "Flow, Facility, Gas Day, map, source coverage, or table explorer "
            "entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_flow_context_links_css()}
</style>
<section class="flow-links" aria-label="Forecast-vs-actual context links">
    <div>
        <p class="flow-links__eyebrow">Context links</p>
        <h2>Forecast-vs-actual, Flow, Facility, and Gas Day context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def linepack_gas_date_options(load: GasTableLoad | None) -> tuple[str, ...]:
    """Return gas-date filter options for loaded linepack rows."""
    dataframe = _normalised_linepack_dashboard_dataframe(load)
    if dataframe.is_empty():
        return (LINEPACK_GAS_DATE_FILTER_ALL,)

    values = sorted(
        str(value)
        for value in dataframe.get_column("gas_date").drop_nulls().unique().to_list()
        if value is not None
    )
    return (LINEPACK_GAS_DATE_FILTER_ALL, *reversed(values))


def linepack_facility_options(load: GasTableLoad | None) -> tuple[str, ...]:
    """Return facility filter options for loaded linepack rows."""
    return _linepack_string_filter_options(
        load,
        "source_facility_id",
        LINEPACK_FACILITY_FILTER_ALL,
    )


def linepack_zone_options(load: GasTableLoad | None) -> tuple[str, ...]:
    """Return zone filter options for loaded linepack rows."""
    return _linepack_string_filter_options(
        load,
        "zone_key",
        LINEPACK_ZONE_FILTER_ALL,
    )


def linepack_adequacy_flag_options(load: GasTableLoad | None) -> tuple[str, ...]:
    """Return adequacy-flag filter options for loaded linepack rows."""
    return _linepack_string_filter_options(
        load,
        "adequacy_flag",
        LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
    )


def linepack_source_system_options(load: GasTableLoad | None) -> tuple[str, ...]:
    """Return source-system filter options for loaded linepack rows."""
    return _linepack_string_filter_options(
        load,
        "source_system",
        LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
    )


def linepack_kpi_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = LINEPACK_GAS_DATE_FILTER_ALL,
    facility_filter: str = LINEPACK_FACILITY_FILTER_ALL,
    zone_filter: str = LINEPACK_ZONE_FILTER_ALL,
    adequacy_flag_filter: str = LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
    source_system_filter: str = LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return first-viewport KPIs for loaded linepack rows."""
    dataframe = _filtered_linepack_dataframe(
        load,
        gas_date_filter,
        facility_filter,
        zone_filter,
        adequacy_flag_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_LINEPACK_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_rows"),
        pl.col("facility_key").drop_nulls().n_unique().alias("facility_keys"),
        pl.col("zone_key").drop_nulls().n_unique().alias("zone_keys"),
        pl.col("source_facility_id").drop_nulls().n_unique().alias("source_facilities"),
        pl.col("source_system").drop_nulls().n_unique().alias("source_systems"),
        pl.col("gas_date").drop_nulls().n_unique().alias("gas_days"),
        pl.col("gas_date").max().alias("latest_gas_date"),
        pl.col("observation_timestamp").max().alias("latest_observation"),
        pl.col("actual_linepack_gj").is_not_null().sum().alias("linepack_rows"),
        pl.col("actual_linepack_gj").sum().alias("total_linepack_gj"),
        pl.col("adequacy_flag").drop_nulls().n_unique().alias("adequacy_flags"),
        pl.col("adequacy_description")
        .drop_nulls()
        .n_unique()
        .alias("adequacy_descriptions"),
    ).row(0, named=True)
    source_table_count = _linepack_source_table_count(dataframe)
    row_limit = None if load is None else load.row_limit

    return pl.DataFrame(
        [
            {
                "metric": "Loaded linepack rows",
                "value": f"{counts['loaded_rows']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Facility keys",
                "value": f"{counts['facility_keys']:,}",
                "detail": "Distinct facility_key values in the current view",
            },
            {
                "metric": "Zone keys",
                "value": f"{counts['zone_keys']:,}",
                "detail": "Distinct zone_key values in the current view",
            },
            {
                "metric": "Source facilities",
                "value": f"{counts['source_facilities']:,}",
                "detail": "Distinct source_facility_id values in the current view",
            },
            {
                "metric": "Source systems",
                "value": f"{counts['source_systems']:,}",
                "detail": "Distinct source_system values in the current view",
            },
            {
                "metric": "Source tables",
                "value": f"{source_table_count:,}",
                "detail": "Distinct source_table/source_tables values represented",
            },
            {
                "metric": "Gas days",
                "value": f"{counts['gas_days']:,}",
                "detail": "Distinct gas_date values in the current view",
            },
            {
                "metric": "Latest gas date",
                "value": _format_optional_value(counts["latest_gas_date"]),
                "detail": "Maximum gas_date in the loaded bounded rows",
            },
            {
                "metric": "Latest observation",
                "value": _format_optional_value(counts["latest_observation"]),
                "detail": "Maximum observation_timestamp in the current view",
            },
            {
                "metric": "Linepack quantity",
                "value": _format_measure_total(
                    counts["total_linepack_gj"],
                    counts["linepack_rows"],
                    suffix=" GJ",
                ),
                "detail": (
                    f"{counts['linepack_rows']:,} populated actual_linepack_gj rows"
                ),
            },
            {
                "metric": "Adequacy flags",
                "value": f"{counts['adequacy_flags']:,}",
                "detail": "Distinct adequacy_flag values in the current view",
            },
            {
                "metric": "Adequacy descriptions",
                "value": f"{counts['adequacy_descriptions']:,}",
                "detail": ("Distinct adequacy_description values in the current view"),
            },
        ],
        schema=_LINEPACK_KPI_SCHEMA,
    )


def linepack_summary_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = LINEPACK_GAS_DATE_FILTER_ALL,
    facility_filter: str = LINEPACK_FACILITY_FILTER_ALL,
    zone_filter: str = LINEPACK_ZONE_FILTER_ALL,
    adequacy_flag_filter: str = LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
    source_system_filter: str = LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return facility, zone, and adequacy summaries for loaded linepack rows."""
    dataframe = _filtered_linepack_dataframe(
        load,
        gas_date_filter,
        facility_filter,
        zone_filter,
        adequacy_flag_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_LINEPACK_SUMMARY_SCHEMA)

    sorted_frame = dataframe.sort(
        [
            "gas_date",
            "observation_timestamp",
            "source_last_updated_timestamp",
            "ingested_timestamp",
        ],
        nulls_last=True,
    )
    summary = (
        sorted_frame.group_by(
            "source_system",
            "source_table",
            "facility_key",
            "zone_key",
            "source_facility_id",
            "adequacy_flag",
            "adequacy_description",
        )
        .agg(
            pl.len().alias("rows"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("actual_linepack_gj").is_not_null().sum().alias("linepack rows"),
            pl.col("actual_linepack_gj").mean().alias("avg linepack gj"),
            pl.col("actual_linepack_gj")
            .drop_nulls()
            .last()
            .alias("latest linepack gj"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("observation_timestamp").max().alias("latest observation"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(
            ["latest gas date", "latest observation", "source_system", "source_table"],
            descending=[True, True, False, False],
            nulls_last=True,
        )
        .rename(
            {
                "source_system": "source system",
                "source_table": "source table",
                "facility_key": "facility key",
                "zone_key": "zone key",
                "source_facility_id": "source facility id",
                "adequacy_flag": "adequacy flag",
                "adequacy_description": "adequacy description",
            }
        )
    )
    return summary.select([*list(_LINEPACK_SUMMARY_SCHEMA)])


def linepack_source_coverage_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = LINEPACK_GAS_DATE_FILTER_ALL,
    facility_filter: str = LINEPACK_FACILITY_FILTER_ALL,
    zone_filter: str = LINEPACK_ZONE_FILTER_ALL,
    adequacy_flag_filter: str = LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
    source_system_filter: str = LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return source-system and source-table coverage for loaded linepack rows."""
    dataframe = _filtered_linepack_dataframe(
        load,
        gas_date_filter,
        facility_filter,
        zone_filter,
        adequacy_flag_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_LINEPACK_SOURCE_COVERAGE_SCHEMA)

    coverage = (
        dataframe.group_by("source_system", "source_table")
        .agg(
            pl.len().alias("rows"),
            pl.col("facility_key").drop_nulls().n_unique().alias("facility keys"),
            pl.col("zone_key").drop_nulls().n_unique().alias("zone keys"),
            pl.col("source_facility_id")
            .drop_nulls()
            .n_unique()
            .alias("source facilities"),
            pl.col("gas_date").drop_nulls().n_unique().alias("gas days"),
            pl.col("actual_linepack_gj").is_not_null().sum().alias("linepack rows"),
            pl.col("adequacy_flag").drop_nulls().n_unique().alias("adequacy flags"),
            pl.col("adequacy_description")
            .drop_nulls()
            .n_unique()
            .alias("adequacy descriptions"),
            pl.col("source_file").drop_nulls().n_unique().alias("source files"),
            pl.col("gas_date").min().alias("first gas date"),
            pl.col("gas_date").max().alias("latest gas date"),
            pl.col("observation_timestamp").max().alias("latest observation"),
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
    return coverage.select([*list(_LINEPACK_SOURCE_COVERAGE_SCHEMA)])


def linepack_observation_frame(
    load: GasTableLoad | None,
    gas_date_filter: str = LINEPACK_GAS_DATE_FILTER_ALL,
    facility_filter: str = LINEPACK_FACILITY_FILTER_ALL,
    zone_filter: str = LINEPACK_ZONE_FILTER_ALL,
    adequacy_flag_filter: str = LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
    source_system_filter: str = LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_LINEPACK_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return bounded recent/sample linepack observations."""
    dataframe = _filtered_linepack_dataframe(
        load,
        gas_date_filter,
        facility_filter,
        zone_filter,
        adequacy_flag_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_LINEPACK_OBSERVATION_SCHEMA)

    return (
        dataframe.sort(
            [
                "gas_date",
                "observation_timestamp",
                "source_last_updated_timestamp",
                "ingested_timestamp",
                "source_system",
                "source_facility_id",
            ],
            descending=[True, True, True, True, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("gas_date").alias("gas date"),
            pl.col("observation_timestamp").alias("observation timestamp"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("facility_key").alias("facility key"),
            pl.col("zone_key").alias("zone key"),
            pl.col("source_facility_id").alias("source facility id"),
            pl.col("actual_linepack_gj"),
            pl.col("adequacy_flag").alias("adequacy flag"),
            pl.col("adequacy_description").alias("adequacy description"),
            pl.col("source_file").alias("source file"),
            pl.col("source_last_updated_timestamp").alias("source updated"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def linepack_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched linepack rows."""
    table_label = _markdown_breakable_text("silver.gas_model.silver_gas_fact_linepack")
    if load is None:
        status_detail = "The dashboard did not receive a linepack load result."
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = "The current filters do not match any loaded linepack rows."
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No linepack data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    `actual_linepack_gj`, `adequacy_flag`, `adequacy_description`,
    `facility_key`, `zone_key`, source-system, and source-table fields.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` linepack asset, then use
    **Refresh data**.
    """


def render_linepack_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render linepack links to related Market context panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        LINEPACK_CONTEXT_ID,
        FLOW_CONTEXT_ID,
        "capacity-context",
        "mos-context",
        FACILITY_CONTEXT_ID,
        HUB_ZONE_CONTEXT_ID,
        "source-coverage-matrix",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_linepack_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="linepack-links__empty">'
            "No Linepack, Flow, Capacity, MOS, Facility, Hub / Zone, source "
            "coverage, or table explorer entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_linepack_context_links_css()}
</style>
<section class="linepack-links" aria-label="Linepack context links">
    <div>
        <p class="linepack-links__eyebrow">Context links</p>
        <h2>Linepack, Flow, Capacity, MOS, and source coverage context</h2>
    </div>
    <ul>
{rows}
    </ul>
</section>"""


def capacity_outlook_date_range_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return date-range filter options for loaded capacity outlook rows."""
    return _capacity_outlook_string_filter_options(
        load,
        "date_range",
        CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL,
    )


def capacity_outlook_capacity_type_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return capacity-type filter options for loaded capacity outlook rows."""
    return _capacity_outlook_string_filter_options(
        load,
        "capacity_type",
        CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL,
    )


def capacity_outlook_direction_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return direction filter options for loaded capacity outlook rows."""
    return _capacity_outlook_string_filter_options(
        load,
        "flow_direction",
        CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL,
    )


def capacity_outlook_facility_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return facility filter options for loaded capacity outlook rows."""
    return _capacity_outlook_string_filter_options(
        load,
        "source_facility_id",
        CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
    )


def capacity_outlook_source_coverage_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return capacity-source-coverage filter options for loaded rows."""
    return _capacity_outlook_string_filter_options(
        load,
        "capacity_source_coverage",
        CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL,
    )


def capacity_outlook_source_system_options(
    load: GasTableLoad | None,
) -> tuple[str, ...]:
    """Return source-system filter options for loaded capacity outlook rows."""
    return _capacity_outlook_string_filter_options(
        load,
        "source_system",
        CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
    )


def capacity_outlook_kpi_frame(
    load: GasTableLoad | None,
    date_range_filter: str = CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL,
    capacity_type_filter: str = CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL,
    direction_filter: str = CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL,
    facility_filter: str = CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
    source_coverage_filter: str = CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL,
    source_system_filter: str = CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return first-viewport KPIs for loaded capacity outlook rows."""
    dataframe = _filtered_capacity_outlook_dataframe(
        load,
        date_range_filter,
        capacity_type_filter,
        direction_filter,
        facility_filter,
        source_coverage_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CAPACITY_OUTLOOK_KPI_SCHEMA)

    counts = dataframe.select(
        pl.len().alias("loaded_rows"),
        pl.col("capacity_source_coverage")
        .drop_nulls()
        .n_unique()
        .alias("source_coverage"),
        pl.col("source_facility_id").drop_nulls().n_unique().alias("facilities"),
        pl.col("capacity_type").drop_nulls().n_unique().alias("capacity_types"),
        pl.col("flow_direction").drop_nulls().n_unique().alias("directions"),
        pl.col("date_range").drop_nulls().n_unique().alias("date_ranges"),
        pl.col("from_gas_date").min().alias("first_from_gas_date"),
        pl.col("from_gas_date").max().alias("latest_from_gas_date"),
        pl.col("to_gas_date").max().alias("latest_to_gas_date"),
        pl.col("capacity_quantity_tj").is_not_null().sum().alias("capacity_rows"),
        pl.col("capacity_quantity_tj").sum().alias("total_capacity_tj"),
        pl.col("capacity_quantity_tj").max().alias("max_capacity_tj"),
        pl.col("source_system").drop_nulls().n_unique().alias("source_systems"),
        pl.col("source_last_updated_timestamp").max().alias("latest_source_update"),
        pl.col("ingested_timestamp").max().alias("latest_ingest"),
    ).row(0, named=True)
    source_table_count = _capacity_outlook_source_table_count(dataframe)
    row_limit = None if load is None else load.row_limit

    return pl.DataFrame(
        [
            {
                "metric": "Loaded capacity rows",
                "value": f"{counts['loaded_rows']:,}",
                "detail": format_row_limit(row_limit),
            },
            {
                "metric": "Capacity source coverage",
                "value": f"{counts['source_coverage']:,}",
                "detail": (
                    "Distinct short-term, medium-term, nameplate, uncontracted, "
                    "connection-point, or other source coverage labels"
                ),
            },
            {
                "metric": "Facilities",
                "value": f"{counts['facilities']:,}",
                "detail": "Distinct source_facility_id values in the current view",
            },
            {
                "metric": "Capacity types",
                "value": f"{counts['capacity_types']:,}",
                "detail": "Distinct capacity_type values in the current view",
            },
            {
                "metric": "Directions",
                "value": f"{counts['directions']:,}",
                "detail": "Distinct flow_direction values in the current view",
            },
            {
                "metric": "Date ranges",
                "value": f"{counts['date_ranges']:,}",
                "detail": (
                    "Distinct from_gas_date, to_gas_date, or outlook month ranges"
                ),
            },
            {
                "metric": "Source systems",
                "value": f"{counts['source_systems']:,}",
                "detail": "Distinct source_system values in the current view",
            },
            {
                "metric": "Source tables",
                "value": f"{source_table_count:,}",
                "detail": "Distinct source_table/source_tables values represented",
            },
            {
                "metric": "From Gas Day range",
                "value": (
                    f"{_format_optional_value(counts['first_from_gas_date'])} to "
                    f"{_format_optional_value(counts['latest_from_gas_date'])}"
                ),
                "detail": "Minimum and maximum from_gas_date in the current view",
            },
            {
                "metric": "Latest To Gas Day",
                "value": _format_optional_value(counts["latest_to_gas_date"]),
                "detail": "Maximum to_gas_date in the current view",
            },
            {
                "metric": "Capacity quantity",
                "value": _format_measure_total(
                    counts["total_capacity_tj"],
                    counts["capacity_rows"],
                    suffix=" TJ",
                ),
                "detail": (
                    f"{counts['capacity_rows']:,} populated capacity_quantity_tj rows"
                ),
            },
            {
                "metric": "Max capacity quantity",
                "value": _format_measure_total(
                    counts["max_capacity_tj"],
                    counts["capacity_rows"],
                    suffix=" TJ",
                ),
                "detail": "Maximum capacity_quantity_tj in the current view",
            },
            {
                "metric": "Latest source update",
                "value": _format_optional_value(counts["latest_source_update"]),
                "detail": "Maximum source_last_updated_timestamp in the current view",
            },
            {
                "metric": "Latest ingest",
                "value": _format_optional_value(counts["latest_ingest"]),
                "detail": "Maximum ingested_timestamp in the current view",
            },
        ],
        schema=_CAPACITY_OUTLOOK_KPI_SCHEMA,
    )


def capacity_outlook_source_coverage_frame(
    load: GasTableLoad | None,
    date_range_filter: str = CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL,
    capacity_type_filter: str = CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL,
    direction_filter: str = CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL,
    facility_filter: str = CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
    source_coverage_filter: str = CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL,
    source_system_filter: str = CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return source coverage by capacity outlook source family."""
    dataframe = _filtered_capacity_outlook_dataframe(
        load,
        date_range_filter,
        capacity_type_filter,
        direction_filter,
        facility_filter,
        source_coverage_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CAPACITY_OUTLOOK_SOURCE_COVERAGE_SCHEMA)

    coverage = (
        dataframe.group_by(
            "capacity_source_coverage",
            "source_system",
            "source_table",
        )
        .agg(
            pl.len().alias("rows"),
            pl.col("source_facility_id").drop_nulls().n_unique().alias("facilities"),
            pl.col("capacity_type").drop_nulls().n_unique().alias("capacity types"),
            pl.col("flow_direction").drop_nulls().n_unique().alias("directions"),
            pl.col("date_range").drop_nulls().n_unique().alias("date ranges"),
            pl.col("capacity_quantity_tj").is_not_null().sum().alias("capacity rows"),
            pl.col("capacity_quantity_tj").sum().alias("total capacity tj"),
            pl.col("from_gas_date").min().alias("first from gas date"),
            pl.col("to_gas_date").max().alias("latest to gas date"),
            pl.col("source_file").drop_nulls().n_unique().alias("source files"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(
            ["rows", "capacity_source_coverage", "source_table"],
            descending=[True, False, False],
        )
        .rename(
            {
                "capacity_source_coverage": "capacity source coverage",
                "source_system": "source system",
                "source_table": "source table",
            }
        )
    )
    return coverage.select([*list(_CAPACITY_OUTLOOK_SOURCE_COVERAGE_SCHEMA)])


def capacity_outlook_summary_frame(
    load: GasTableLoad | None,
    date_range_filter: str = CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL,
    capacity_type_filter: str = CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL,
    direction_filter: str = CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL,
    facility_filter: str = CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
    source_coverage_filter: str = CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL,
    source_system_filter: str = CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
) -> pl.DataFrame:
    """Return facility, direction, type, and date-range capacity summaries."""
    dataframe = _filtered_capacity_outlook_dataframe(
        load,
        date_range_filter,
        capacity_type_filter,
        direction_filter,
        facility_filter,
        source_coverage_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CAPACITY_OUTLOOK_SUMMARY_SCHEMA)

    summary = (
        dataframe.group_by(
            "capacity_source_coverage",
            "source_system",
            "source_table",
            "source_facility_id",
            "facility_name",
            "capacity_type",
            "flow_direction",
            "date_range",
        )
        .agg(
            pl.len().alias("rows"),
            pl.col("capacity_quantity_tj").is_not_null().sum().alias("capacity rows"),
            pl.col("capacity_quantity_tj").sum().alias("total capacity tj"),
            pl.col("capacity_quantity_tj").mean().alias("avg capacity tj"),
            pl.col("capacity_quantity_tj").max().alias("max capacity tj"),
            pl.col("from_gas_date").min().alias("first from gas date"),
            pl.col("to_gas_date").max().alias("latest to gas date"),
            pl.col("outlook_month").drop_nulls().n_unique().alias("outlook months"),
            pl.col("source_file").drop_nulls().n_unique().alias("source files"),
            pl.col("source_last_updated_timestamp").max().alias("latest source update"),
            pl.col("ingested_timestamp").max().alias("latest ingest"),
        )
        .sort(
            [
                "first from gas date",
                "latest to gas date",
                "capacity_source_coverage",
                "source_facility_id",
            ],
            descending=[True, True, False, False],
            nulls_last=True,
        )
        .rename(
            {
                "capacity_source_coverage": "capacity source coverage",
                "source_system": "source system",
                "source_table": "source table",
                "source_facility_id": "source facility id",
                "facility_name": "facility",
                "capacity_type": "capacity type",
                "flow_direction": "direction",
                "date_range": "date range",
            }
        )
    )
    return summary.select([*list(_CAPACITY_OUTLOOK_SUMMARY_SCHEMA)])


def capacity_outlook_observation_frame(
    load: GasTableLoad | None,
    date_range_filter: str = CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL,
    capacity_type_filter: str = CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL,
    direction_filter: str = CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL,
    facility_filter: str = CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
    source_coverage_filter: str = CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL,
    source_system_filter: str = CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
    *,
    preview_rows: int = DEFAULT_CAPACITY_OUTLOOK_PREVIEW_ROWS,
) -> pl.DataFrame:
    """Return bounded recent/sample capacity outlook observations."""
    dataframe = _filtered_capacity_outlook_dataframe(
        load,
        date_range_filter,
        capacity_type_filter,
        direction_filter,
        facility_filter,
        source_coverage_filter,
        source_system_filter,
    )
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CAPACITY_OUTLOOK_OBSERVATION_SCHEMA)

    return (
        dataframe.sort(
            [
                "from_gas_date",
                "to_gas_date",
                "outlook_year",
                "outlook_month",
                "source_last_updated_timestamp",
                "ingested_timestamp",
                "source_system",
                "source_facility_id",
            ],
            descending=[True, True, True, True, True, True, False, False],
            nulls_last=True,
        )
        .select(
            pl.col("capacity_source_coverage").alias("capacity source coverage"),
            pl.col("from_gas_date").alias("from gas date"),
            pl.col("to_gas_date").alias("to gas date"),
            pl.col("outlook_month").alias("outlook month"),
            pl.col("outlook_year").alias("outlook year"),
            pl.col("source_system").alias("source system"),
            pl.col("source_table").alias("source table"),
            pl.col("source_facility_id").alias("source facility id"),
            pl.col("facility_name").alias("facility"),
            pl.col("capacity_type").alias("capacity type"),
            pl.col("flow_direction").alias("direction"),
            pl.col("receipt_location_id").alias("receipt location"),
            pl.col("delivery_location_id").alias("delivery location"),
            pl.col("capacity_quantity_tj"),
            pl.col("capacity_description").alias("capacity description"),
            pl.col("source_surrogate_key").alias("source identifier"),
            pl.col("source_file").alias("source file"),
            pl.col("source_last_updated_timestamp").alias("source updated"),
            pl.col("ingested_timestamp").alias("latest ingest"),
        )
        .head(max(1, preview_rows))
    )


def capacity_outlook_empty_state_markdown(load: GasTableLoad | None) -> str:
    """Return useful empty-state copy for missing or unmatched capacity rows."""
    table_label = _markdown_breakable_text(
        "silver.gas_model.silver_gas_fact_capacity_outlook"
    )
    if load is None:
        status_detail = "The dashboard did not receive a capacity outlook load result."
        uri = table_label
        read_policy = "No read policy was reported."
    else:
        if load.error is not None:
            status_detail = f"Read detail: {_markdown_breakable_text(load.error)}"
        elif load.dataframe is None or load.dataframe.is_empty():
            status_detail = "The table loaded successfully but returned no rows."
        else:
            status_detail = (
                "The current filters do not match any loaded capacity outlook rows."
            )
        uri = _markdown_breakable_text(load.uri)
        read_policy = row_limit_message(load.row_limit)

    return f"""
    **No capacity outlook data is available for this view.**

    The dashboard checked {uri}, which should contain {table_label} rows with
    `capacity_type`, `flow_direction`, `from_gas_date`, `to_gas_date`,
    `capacity_quantity_tj`, Facility identifiers, source-system, and
    source-table fields.

    {status_detail}

    {read_policy}

    Materialize or seed the `silver.gas_model` capacity outlook asset, then use
    **Refresh data**.
    """


def render_capacity_outlook_context_links(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> str:
    """Render capacity outlook links to related Market context panels."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concept_ids = (
        CAPACITY_CONTEXT_ID,
        FACILITY_CONTEXT_ID,
        FLOW_CONTEXT_ID,
        CONNECTION_POINT_CONTEXT_ID,
        GAS_DAY_CONTEXT_ID,
        "gbb-interactive-map",
        "source-coverage-matrix",
        "gas-model-table-explorer",
    )
    rows = "\n".join(
        _render_capacity_outlook_context_link(entry)
        for entry in (
            registry_entry_by_concept_id(concept_id, candidate_entries)
            for concept_id in concept_ids
        )
        if entry is not None
    )
    if rows == "":
        rows = (
            '<li class="capacity-outlook-links__empty">'
            "No Capacity, Facility, Flow, Connection Point, Gas Day, map, "
            "source coverage, or table explorer entries are registered."
            "</li>"
        )

    return f"""\
<style>
{_capacity_outlook_context_links_css()}
</style>
<section class="capacity-outlook-links" aria-label="Capacity outlook context links">
    <div>
        <p class="capacity-outlook-links__eyebrow">Context links</p>
        <h2>Capacity, Facility, Flow, Connection Point, and Gas Day context</h2>
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


def _normalised_participant_dimension_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_PARTICIPANT_DIM_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _PARTICIPANT_DIM_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("participant_identity_source").cast(pl.String, strict=False),
        pl.col("participant_identity_value").cast(pl.String, strict=False),
        pl.col("canonical_participant_name").cast(pl.String, strict=False),
        pl.col("registered_name").cast(pl.String, strict=False),
        pl.col("abn").cast(pl.String, strict=False),
        pl.col("acn").cast(pl.String, strict=False),
        pl.col("participant_type").cast(pl.String, strict=False),
        pl.col("participant_status").cast(pl.String, strict=False),
        pl.col("source_systems").cast(pl.List(pl.String), strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_company_ids").cast(pl.List(pl.String), strict=False),
        pl.col("source_surrogate_keys").cast(pl.List(pl.String), strict=False),
        pl.col("source_files").cast(pl.List(pl.String), strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_participant_membership_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_PARTICIPANT_MARKET_MEMBERSHIP_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _PARTICIPANT_MARKET_MEMBERSHIP_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("participant_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("market_code").cast(pl.String, strict=False),
        pl.col("source_company_id").cast(pl.String, strict=False),
        pl.col("source_company_code").cast(pl.String, strict=False),
        pl.col("source_hub_id").cast(pl.String, strict=False),
        pl.col("source_hub_name").cast(pl.String, strict=False),
        pl.col("registration_type").cast(pl.String, strict=False),
        pl.col("registered_capacity").cast(pl.String, strict=False),
        pl.col("membership_status").cast(pl.String, strict=False),
        pl.col("participant_identity_source").cast(pl.String, strict=False),
        pl.col("participant_identity_value").cast(pl.String, strict=False),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_location_dimension_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_LOCATION_DIM_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _LOCATION_DIM_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_location_id").cast(pl.String, strict=False),
        pl.col("location_name").cast(pl.String, strict=False),
        pl.col("state").cast(pl.String, strict=False),
        pl.col("location_type").cast(pl.String, strict=False),
        pl.col("location_description").cast(pl.String, strict=False),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_hub_zone_dimension_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_HUB_ZONE_DIM_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _HUB_ZONE_DIM_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("zone_type").cast(pl.String, strict=False),
        pl.col("source_zone_id").cast(pl.String, strict=False),
        pl.col("zone_name").cast(pl.String, strict=False),
        pl.col("zone_description").cast(pl.String, strict=False),
        pl.col("source_surrogate_keys").cast(pl.List(pl.String), strict=False),
        pl.col("source_files").cast(pl.List(pl.String), strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


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


def _normalised_linepack_dataframe(load: GasTableLoad | None) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_LINEPACK_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _LINEPACK_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("date_key").cast(pl.String, strict=False),
        pl.col("facility_key").cast(pl.String, strict=False),
        pl.col("zone_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        _normalise_timestamp_column(dataframe, "observation_timestamp"),
        pl.col("source_facility_id").cast(pl.String, strict=False),
        pl.col("actual_linepack_gj").cast(pl.Float64, strict=False),
        pl.col("adequacy_flag").cast(pl.String, strict=False),
        pl.col("adequacy_description").cast(pl.String, strict=False),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
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
        pl.col("outlook_month").cast(pl.Int64, strict=False),
        pl.col("outlook_year").cast(pl.Int64, strict=False),
        pl.col("receipt_location_id").cast(pl.String, strict=False),
        pl.col("delivery_location_id").cast(pl.String, strict=False),
        pl.col("capacity_quantity_tj").cast(pl.Float64, strict=False),
        pl.col("capacity_description").cast(pl.String, strict=False),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_connection_point_dimension_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_CONNECTION_POINT_DIM_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _CONNECTION_POINT_DIM_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("facility_key").cast(pl.String, strict=False),
        pl.col("location_key").cast(pl.String, strict=False),
        pl.col("zone_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_hub_id").cast(pl.String, strict=False),
        pl.col("source_hub_name").cast(pl.String, strict=False),
        pl.col("source_facility_id").cast(pl.String, strict=False),
        pl.col("source_connection_point_id").cast(pl.String, strict=False),
        pl.col("source_node_id").cast(pl.String, strict=False),
        pl.col("source_location_id").cast(pl.String, strict=False),
        pl.col("connection_point_name").cast(pl.String, strict=False),
        pl.col("flow_direction").cast(pl.String, strict=False),
        pl.col("facility_name").cast(pl.String, strict=False),
        pl.col("location_name").cast(pl.String, strict=False),
        pl.col("state").cast(pl.String, strict=False),
        pl.col("exempt").cast(pl.Boolean, strict=False),
        pl.col("exemption_description").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "effective_date"),
        _normalise_date_column(dataframe, "effective_to_date"),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_connection_point_flow_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_CONNECTION_POINT_FLOW_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _CONNECTION_POINT_FLOW_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("date_key").cast(pl.String, strict=False),
        pl.col("facility_key").cast(pl.String, strict=False),
        pl.col("location_key").cast(pl.String, strict=False),
        pl.col("connection_point_key").cast(pl.String, strict=False),
        pl.col("zone_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("source_facility_id").cast(pl.String, strict=False),
        pl.col("source_connection_point_id").cast(pl.String, strict=False),
        pl.col("flow_direction").cast(pl.String, strict=False),
        pl.col("actual_quantity_tj").cast(pl.Float64, strict=False),
        pl.col("quality").cast(pl.String, strict=False),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_nomination_forecast_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_NOMINATION_FORECAST_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _NOMINATION_FORECAST_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("date_key").cast(pl.String, strict=False),
        pl.col("facility_key").cast(pl.String, strict=False),
        pl.col("location_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("forecast_type").cast(pl.String, strict=False),
        pl.col("forecast_version").cast(pl.String, strict=False),
        pl.col("gas_interval").cast(pl.Int64, strict=False),
        pl.col("source_facility_id").cast(pl.String, strict=False),
        pl.col("source_location_id").cast(pl.String, strict=False),
        pl.col("demand_forecast_gj").cast(pl.Float64, strict=False),
        pl.col("supply_forecast_gj").cast(pl.Float64, strict=False),
        pl.col("transfer_in_forecast_gj").cast(pl.Float64, strict=False),
        pl.col("transfer_out_forecast_gj").cast(pl.Float64, strict=False),
        pl.col("override_quantity_gj").cast(pl.Float64, strict=False),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_nomination_forecast_dashboard_dataframe(
    load: GasTableLoad | None,
    *,
    as_of_date: date | None = None,
) -> pl.DataFrame:
    dataframe = _normalised_nomination_forecast_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_NOMINATION_FORECAST_DASHBOARD_ROW_SCHEMA)

    reference_date = _nomination_forecast_reference_date(as_of_date)
    rows = [
        _nomination_forecast_dashboard_row(row, reference_date)
        for row in dataframe.to_dicts()
    ]
    return pl.DataFrame(rows, schema=_NOMINATION_FORECAST_DASHBOARD_ROW_SCHEMA)


def _nomination_forecast_dashboard_row(
    row: Mapping[str, object],
    reference_date: date,
) -> dict[str, object]:
    return {
        **row,
        "source_table": _nomination_forecast_source_table_label(row),
        "forecast_horizon": _nomination_forecast_horizon_label(
            row.get("gas_date"),
            reference_date,
        ),
    }


def _nomination_forecast_source_table_label(row: Mapping[str, object]) -> str:
    values = list(_source_coverage_value_strings(row.get("source_table")))
    values.extend(_source_coverage_value_strings(row.get("source_tables")))
    deduplicated_values = tuple(dict.fromkeys(values))
    if len(deduplicated_values) == 0:
        return _SOURCE_COVERAGE_EMPTY_SOURCE_TABLE_VALUE
    return ", ".join(deduplicated_values)


def _nomination_forecast_horizon_label(
    gas_date_value: object | None,
    reference_date: date,
) -> str:
    gas_date = _flow_date_value(gas_date_value)
    if gas_date is None:
        return "Unknown Gas Day forecast"
    if gas_date < reference_date:
        return "Historical forecast"
    return "Current/future forecast"


def _nomination_forecast_reference_date(as_of_date: date | None) -> date:
    return date.today() if as_of_date is None else as_of_date


def _normalised_operational_meter_flow_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    if load is None or load.dataframe is None or load.dataframe.is_empty():
        return pl.DataFrame(schema=_OPERATIONAL_METER_FLOW_RAW_SCHEMA)

    dataframe = load.dataframe
    missing_columns = [
        pl.lit(None, dtype=dtype).alias(column)
        for column, dtype in _OPERATIONAL_METER_FLOW_RAW_SCHEMA.items()
        if column not in dataframe.columns
    ]
    if missing_columns:
        dataframe = dataframe.with_columns(missing_columns)

    return dataframe.with_columns(
        pl.col("surrogate_key").cast(pl.String, strict=False),
        pl.col("date_key").cast(pl.String, strict=False),
        pl.col("operational_point_key").cast(pl.String, strict=False),
        pl.col("zone_key").cast(pl.String, strict=False),
        pl.col("pipeline_segment_key").cast(pl.String, strict=False),
        pl.col("source_system").cast(pl.String, strict=False),
        pl.col("source_tables").cast(pl.List(pl.String), strict=False),
        pl.col("source_table").cast(pl.String, strict=False),
        _normalise_date_column(dataframe, "gas_date"),
        pl.col("gas_interval").cast(pl.String, strict=False),
        pl.col("point_type").cast(pl.String, strict=False),
        pl.col("source_point_id").cast(pl.String, strict=False),
        pl.col("flow_direction").cast(pl.String, strict=False),
        pl.col("quantity_gj").cast(pl.Float64, strict=False),
        _normalise_timestamp_column(dataframe, "commencement_timestamp"),
        _normalise_timestamp_column(dataframe, "termination_timestamp"),
        pl.col("source_last_updated").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "source_last_updated_timestamp"),
        pl.col("source_surrogate_key").cast(pl.String, strict=False),
        pl.col("source_file").cast(pl.String, strict=False),
        _normalise_timestamp_column(dataframe, "ingested_timestamp"),
    )


def _normalised_flow_dataframe(load: GasTableLoad) -> pl.DataFrame:
    if load.spec.table_name == CONNECTION_POINT_FLOW_TABLE_NAME:
        return _normalised_connection_point_flow_dataframe(load)
    if load.spec.table_name == FACILITY_FLOW_STORAGE_TABLE_NAME:
        return _normalised_facility_flow_storage_dataframe(load)
    if load.spec.table_name == NOMINATION_FORECAST_TABLE_NAME:
        return _normalised_nomination_forecast_dataframe(load)
    if load.spec.table_name == OPERATIONAL_METER_FLOW_TABLE_NAME:
        return _normalised_operational_meter_flow_dataframe(load)
    if load.dataframe is None:
        return pl.DataFrame()
    return load.dataframe


def _update_flow_source_summaries(
    summaries: dict[tuple[str, str, str], _FlowSourceSummary],
    load: GasTableLoad,
    row: Mapping[str, object],
) -> None:
    source_system = _flow_source_system_value(row)
    for source_table in _flow_source_table_labels(row):
        key = (load.spec.label, source_system, source_table)
        summary = summaries.setdefault(
            key,
            _FlowSourceSummary(
                fact=load.spec.label,
                source_system=source_system,
                source_table=source_table,
                row_limit=format_row_limit(load.row_limit),
                detail=_flow_fact_detail(load),
            ),
        )
        _update_flow_source_summary(summary, load.spec.table_name, row)


def _update_flow_source_summary(
    summary: _FlowSourceSummary,
    table_name: str,
    row: Mapping[str, object],
) -> None:
    summary.rows += 1
    gas_date = _flow_date_value(row.get("gas_date"))
    if gas_date is not None:
        summary.gas_dates.add(gas_date)
        summary.latest_gas_date = _latest_date(summary.latest_gas_date, gas_date)
    if _flow_row_has_measure(table_name, row):
        summary.measure_rows += 1
    summary.latest_source_update = _latest_datetime(
        summary.latest_source_update,
        _flow_datetime_value(row.get("source_last_updated_timestamp")),
    )
    summary.latest_ingest = _latest_datetime(
        summary.latest_ingest,
        _flow_datetime_value(row.get("ingested_timestamp")),
    )


def _flow_source_summary_row(summary: _FlowSourceSummary) -> dict[str, object]:
    return {
        "fact": summary.fact,
        "source system": summary.source_system,
        "source table": summary.source_table,
        "rows": summary.rows,
        "gas days": len(summary.gas_dates),
        "measure rows": summary.measure_rows,
        "latest gas date": summary.latest_gas_date,
        "latest source update": summary.latest_source_update,
        "latest ingest": summary.latest_ingest,
        "row limit": summary.row_limit,
        "detail": summary.detail,
    }


def _flow_source_system_value(row: Mapping[str, object]) -> str:
    values = _source_coverage_value_strings(row.get("source_system"))
    if len(values) == 0:
        return "(empty source_system value)"
    return values[0]


def _flow_source_table_labels(row: Mapping[str, object]) -> tuple[str, ...]:
    values = _flow_source_table_values(row)
    if len(values) == 0:
        return ("(empty source_table/source_tables value)",)
    return values


def _flow_source_table_values(row: Mapping[str, object]) -> tuple[str, ...]:
    values: list[str] = []
    values.extend(_source_coverage_value_strings(row.get("source_table")))
    values.extend(_source_coverage_value_strings(row.get("source_tables")))
    return tuple(dict.fromkeys(values))


def _flow_fact_detail(load: GasTableLoad) -> str:
    measure_names = ", ".join(_flow_measure_columns(load.spec.table_name))
    if measure_names == "":
        return f"{load.spec.table_name} has no configured Flow measure columns"
    return f"{load.spec.table_name} measures: {measure_names}"


def _flow_row_has_measure(table_name: str, row: Mapping[str, object]) -> bool:
    return any(
        row.get(column) is not None for column in _flow_measure_columns(table_name)
    )


def _flow_measure_columns(table_name: str) -> tuple[str, ...]:
    return _FLOW_MEASURE_COLUMNS_BY_TABLE.get(table_name, ())


def _flow_measure_unit(table_name: str) -> str:
    return _FLOW_MEASURE_UNITS_BY_TABLE.get(table_name, "")


def _latest_date(current: date | None, value: date | None) -> date | None:
    if value is None:
        return current
    if current is None or value > current:
        return value
    return current


def _latest_datetime(
    current: datetime | None,
    value: datetime | None,
) -> datetime | None:
    if value is None:
        return current
    if current is None or value > current:
        return value
    return current


def _flow_date_value(value: object | None) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return None


def _flow_datetime_value(value: object | None) -> datetime | None:
    return value if isinstance(value, datetime) else None


def _flow_observation_rows(
    load: GasTableLoad,
    row: Mapping[str, object],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    source_table = ", ".join(_flow_source_table_values(row))
    for measure in _flow_measure_columns(load.spec.table_name):
        value = row.get(measure)
        if value is None:
            continue
        rows.append(
            {
                "fact": load.spec.label,
                "gas date": row.get("gas_date"),
                "source system": _flow_source_system_value(row),
                "source table": source_table,
                "flow context": _flow_context_label(load.spec.table_name, row),
                "measure": measure,
                "quantity": value,
                "unit": _flow_measure_unit(load.spec.table_name),
                "source updated": row.get("source_last_updated_timestamp"),
                "latest ingest": row.get("ingested_timestamp"),
            }
        )
    return rows


def _flow_context_label(table_name: str, row: Mapping[str, object]) -> str:
    context_parts = {
        CONNECTION_POINT_FLOW_TABLE_NAME: (
            row.get("source_facility_id"),
            row.get("source_connection_point_id"),
            row.get("flow_direction"),
        ),
        FACILITY_FLOW_STORAGE_TABLE_NAME: (
            row.get("source_facility_id"),
            row.get("source_location_id"),
        ),
        NOMINATION_FORECAST_TABLE_NAME: (
            row.get("forecast_type"),
            row.get("forecast_version"),
            row.get("source_facility_id"),
            row.get("source_location_id"),
            row.get("gas_interval"),
        ),
        OPERATIONAL_METER_FLOW_TABLE_NAME: (
            row.get("point_type"),
            row.get("source_point_id"),
            row.get("flow_direction"),
            row.get("gas_interval"),
        ),
    }
    return _join_flow_context_parts(context_parts.get(table_name, ()))


def _join_flow_context_parts(values: Sequence[object | None]) -> str:
    parts = [
        str(value).strip()
        for value in values
        if value is not None and str(value).strip() != ""
    ]
    return " / ".join(parts)


def _flow_latest_gas_date(loads: Sequence[GasTableLoad]) -> date | None:
    latest: date | None = None
    for load in loads:
        dataframe = _normalised_flow_dataframe(load)
        if dataframe.is_empty() or "gas_date" not in dataframe.columns:
            continue
        value = _flow_date_value(dataframe.get_column("gas_date").drop_nulls().max())
        latest = _latest_date(latest, value)
    return latest


def _flow_measure_row_count(load: GasTableLoad) -> int:
    dataframe = _normalised_flow_dataframe(load)
    measure_columns = _flow_measure_columns(load.spec.table_name)
    if dataframe.is_empty() or len(measure_columns) == 0:
        return 0

    return dataframe.filter(
        pl.any_horizontal(*(pl.col(column).is_not_null() for column in measure_columns))
    ).height


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


def _hub_zone_list_value_count(dataframe: pl.DataFrame, column: str) -> int:
    values: set[str] = set()
    for row in dataframe.select(column).to_dicts():
        values.update(_source_coverage_value_strings(row.get(column)))
    return len(values)


def _hub_zone_type_row_count(dataframe: pl.DataFrame, zone_type: str) -> int:
    return dataframe.filter(pl.col("zone_type") == zone_type).height


def _hub_zone_source_qualified_count(dataframe: pl.DataFrame) -> int:
    identifiers = {
        _hub_zone_source_qualified_identifier(row)
        for row in dataframe.select(
            "source_system",
            "zone_type",
            "source_zone_id",
        ).to_dicts()
    }
    identifiers.discard("")
    return len(identifiers)


def _hub_zone_source_qualified_identifier(row: Mapping[str, object]) -> str:
    source_system = str(row.get("source_system") or "").strip()
    zone_type = str(row.get("zone_type") or "").strip()
    source_zone_id = str(row.get("source_zone_id") or "").strip()
    if source_system == "" or zone_type == "" or source_zone_id == "":
        return ""
    return f"{source_system}:{zone_type}:{source_zone_id}"


def _hub_zone_source_systems(dataframe: pl.DataFrame) -> tuple[str, ...]:
    values = (
        dataframe.filter(_non_empty_string_expression("source_system"))
        .get_column("source_system")
        .cast(pl.String, strict=False)
        .unique()
        .sort()
        .to_list()
    )
    return tuple(str(value) for value in values if value is not None)


def _hub_zone_latest_ingest(dataframe: pl.DataFrame) -> datetime | None:
    values = dataframe.get_column("ingested_timestamp").drop_nulls()
    if values.is_empty():
        return None
    latest = values.max()
    return latest if isinstance(latest, datetime) else None


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


def _connection_point_list_value_count(dataframe: pl.DataFrame, column: str) -> int:
    values: set[str] = set()
    for row in dataframe.select(column).to_dicts():
        values.update(_source_coverage_value_strings(row.get(column)))
    return len(values)


def _connection_point_exempt_row_count(dataframe: pl.DataFrame) -> int:
    return dataframe.filter(pl.col("exempt").fill_null(False)).height


def _connection_point_source_systems(dataframe: pl.DataFrame) -> tuple[str, ...]:
    values = (
        dataframe.filter(_non_empty_string_expression("source_system"))
        .get_column("source_system")
        .cast(pl.String, strict=False)
        .unique()
        .sort()
        .to_list()
    )
    return tuple(str(value) for value in values if value is not None)


def _connection_point_identifier_set(dataframe: pl.DataFrame, column: str) -> set[str]:
    if dataframe.is_empty() or column not in dataframe.columns:
        return set()
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


def _connection_point_tuple_set(dataframe: pl.DataFrame) -> set[tuple[str, str, str]]:
    if dataframe.is_empty():
        return set()

    tuples: set[tuple[str, str, str]] = set()
    for row in dataframe.select(
        "source_facility_id",
        "source_connection_point_id",
        "flow_direction",
    ).to_dicts():
        tuple_key = _connection_point_tuple_from_row(row)
        if all(value != "" for value in tuple_key):
            tuples.add(tuple_key)
    return tuples


def _matched_connection_dimension_count(
    rows: pl.DataFrame,
    dimension: pl.DataFrame,
    key_column: str,
    source_column: str,
) -> int:
    dimension_keys = _connection_point_identifier_set(dimension, "surrogate_key")
    dimension_source_ids = _connection_point_identifier_set(dimension, source_column)
    selected_columns = list(
        dict.fromkeys(
            column
            for column in (
                "surrogate_key",
                "source_system",
                "source_facility_id",
                "source_connection_point_id",
                "flow_direction",
                key_column,
                source_column,
            )
            if column in rows.columns
        )
    )
    matched: set[str] = set()

    for row in rows.select(selected_columns).to_dicts():
        key_value = str(row.get(key_column) or "").strip()
        source_value = str(row.get(source_column) or "").strip()
        if key_value in dimension_keys or source_value in dimension_source_ids:
            matched.add(_connection_point_row_identity(row))
    return len(matched)


def _matched_connection_flow_count(
    rows: pl.DataFrame,
    connection_point_keys: set[str],
    connection_point_tuples: set[tuple[str, str, str]],
) -> int:
    matched: set[str] = set()
    for row in rows.select(
        "connection_point_key",
        "source_system",
        "source_facility_id",
        "source_connection_point_id",
        "flow_direction",
    ).to_dicts():
        connection_point_key = str(row.get("connection_point_key") or "").strip()
        tuple_key = _connection_point_tuple_from_row(row)
        if (
            connection_point_key in connection_point_keys
            or tuple_key in connection_point_tuples
        ):
            matched.add(_connection_point_row_identity(row))
    return len(matched)


def _matched_capacity_flow_direction_count(
    rows: pl.DataFrame,
    connection_point_tuples: set[tuple[str, str, str]],
) -> int:
    connection_point_pairs = {
        (source_facility_id, flow_direction)
        for source_facility_id, _, flow_direction in connection_point_tuples
    }
    matched_pairs: set[tuple[str, str]] = set()

    for row in rows.select("source_facility_id", "flow_direction").to_dicts():
        source_facility_id = str(row.get("source_facility_id") or "").strip()
        flow_direction = str(row.get("flow_direction") or "").strip()
        pair = (source_facility_id, flow_direction)
        if (
            source_facility_id != ""
            and flow_direction != ""
            and pair in connection_point_pairs
        ):
            matched_pairs.add(pair)
    return len(matched_pairs)


def _connection_point_tuple_from_row(
    row: Mapping[str, object],
) -> tuple[str, str, str]:
    return (
        str(row.get("source_facility_id") or "").strip(),
        str(row.get("source_connection_point_id") or "").strip(),
        str(row.get("flow_direction") or "").strip(),
    )


def _connection_point_row_identity(row: Mapping[str, object]) -> str:
    source_qualified = _connection_point_source_qualified_identifier(row)
    if source_qualified != "":
        return source_qualified
    return str(row.get("surrogate_key") or "").strip()


def _connection_point_source_qualified_identifier(
    row: Mapping[str, object],
) -> str:
    source_system = str(row.get("source_system") or "").strip()
    source_facility_id = str(row.get("source_facility_id") or "").strip()
    source_connection_point_id = str(
        row.get("source_connection_point_id") or ""
    ).strip()
    flow_direction = str(row.get("flow_direction") or "").strip()
    if (
        source_system == ""
        or source_facility_id == ""
        or source_connection_point_id == ""
        or flow_direction == ""
    ):
        return ""
    return (
        f"{source_system}:{source_facility_id}:"
        f"{source_connection_point_id}:{flow_direction}"
    )


def _connection_point_hub_label(row: Mapping[str, object]) -> str | None:
    source_hub_name = str(row.get("source_hub_name") or "").strip()
    source_hub_id = str(row.get("source_hub_id") or "").strip()
    if source_hub_name != "" and source_hub_id != "":
        return f"{source_hub_name} ({source_hub_id})"
    if source_hub_name != "":
        return source_hub_name
    if source_hub_id != "":
        return source_hub_id
    return None


def _participant_list_value_count(dataframe: pl.DataFrame, column: str) -> int:
    values: set[str] = set()
    for row in dataframe.select(column).to_dicts():
        values.update(_source_coverage_value_strings(row.get(column)))
    return len(values)


def _participant_group_expression(column: str, value: object | None) -> pl.Expr:
    if value is None:
        return pl.col(column).is_null()
    return pl.col(column) == value


def _latest_ingest_timestamp(dataframe: pl.DataFrame) -> datetime | None:
    values = dataframe.get_column("ingested_timestamp").drop_nulls()
    if values.is_empty():
        return None
    latest = values.max()
    return latest if isinstance(latest, datetime) else None


def _participant_reference_set(dataframe: pl.DataFrame, column: str) -> set[str]:
    if dataframe.is_empty() or column not in dataframe.columns:
        return set()

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


def _participant_name_set(dataframe: pl.DataFrame) -> set[str]:
    names: set[str] = set()
    for column in ("canonical_participant_name", "registered_name"):
        names.update(_participant_reference_set(dataframe, column))
    return names


def _matched_reference_count(
    dataframe: pl.DataFrame,
    column: str,
    reference_values: set[str],
) -> int:
    if not reference_values:
        return 0
    return len(_participant_reference_set(dataframe, column) & reference_values)


def _bid_stack_participant_reference_count(dataframe: pl.DataFrame) -> int:
    references = _participant_reference_set(dataframe, "participant_id")
    references.update(_participant_reference_set(dataframe, "participant_name"))
    return len(references)


def _matched_bid_stack_participant_count(
    dataframe: pl.DataFrame,
    participant_identity_values: set[str],
    participant_names: set[str],
) -> int:
    matched_ids = _participant_reference_set(dataframe, "participant_id") & (
        participant_identity_values
    )
    matched_names = _participant_reference_set(dataframe, "participant_name") & (
        participant_names
    )
    return len(matched_ids | matched_names)


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


def _nomination_forecast_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_nomination_forecast_dashboard_dataframe(load)
    if dataframe.is_empty() or column not in dataframe.columns:
        return (all_label,)

    values = sorted(
        str(value)
        for value in dataframe.get_column(column)
        .drop_nulls()
        .cast(pl.String, strict=False)
        .unique()
        .to_list()
        if value is not None and str(value).strip() != ""
    )
    return (all_label, *values)


def _filtered_nomination_forecast_dataframe(
    load: GasTableLoad | None,
    gas_date_filter: str,
    source_system_filter: str,
    facility_filter: str,
    location_filter: str,
    *,
    as_of_date: date | None = None,
) -> pl.DataFrame:
    dataframe = _normalised_nomination_forecast_dashboard_dataframe(
        load,
        as_of_date=as_of_date,
    )
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if gas_date_filter != NOMINATION_FORECAST_GAS_DATE_FILTER_ALL:
        filtered = filtered.filter(
            pl.col("gas_date").cast(pl.String) == gas_date_filter
        )
    if source_system_filter != NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_system") == source_system_filter)
    if facility_filter != NOMINATION_FORECAST_FACILITY_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_facility_id") == facility_filter)
    if location_filter != NOMINATION_FORECAST_LOCATION_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_location_id") == location_filter)
    return filtered


def _nomination_forecast_source_table_count(dataframe: pl.DataFrame) -> int:
    return _distinct_non_empty_count(dataframe, "source_table")


def _nomination_forecast_type_version_count(dataframe: pl.DataFrame) -> int:
    values: set[tuple[str | None, str | None]] = set()
    for row in dataframe.select("forecast_type", "forecast_version").to_dicts():
        forecast_type = _optional_non_empty_string(row.get("forecast_type"))
        forecast_version = _optional_non_empty_string(row.get("forecast_version"))
        if forecast_type is not None or forecast_version is not None:
            values.add((forecast_type, forecast_version))
    return len(values)


def _optional_non_empty_string(value: object | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text != "" else None


def _facility_flow_storage_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_facility_flow_storage_dashboard_dataframe(load)
    if dataframe.is_empty() or column not in dataframe.columns:
        return (all_label,)

    values = sorted(
        str(value)
        for value in dataframe.get_column(column)
        .drop_nulls()
        .cast(pl.String, strict=False)
        .unique()
        .to_list()
        if value is not None and str(value).strip() != ""
    )
    return (all_label, *values)


def _filtered_facility_flow_storage_dataframe(
    load: GasTableLoad | None,
    gas_date_filter: str,
    facility_filter: str,
    source_system_filter: str,
) -> pl.DataFrame:
    dataframe = _normalised_facility_flow_storage_dashboard_dataframe(load)
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if gas_date_filter != FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL:
        filtered = filtered.filter(
            pl.col("gas_date").cast(pl.String) == gas_date_filter
        )
    if facility_filter != FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_facility_id") == facility_filter)
    if source_system_filter != FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_system") == source_system_filter)
    return filtered


def _forecast_actual_load_pair(
    loads: Sequence[GasTableLoad],
) -> tuple[GasTableLoad | None, GasTableLoad | None]:
    return (
        table_load_by_name(loads, NOMINATION_FORECAST_TABLE_NAME),
        table_load_by_name(loads, FACILITY_FLOW_STORAGE_TABLE_NAME),
    )


def _forecast_actual_input_frames(
    loads: Sequence[GasTableLoad],
    gas_date_filter: str = FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
    facility_filter: str = FORECAST_ACTUAL_FACILITY_FILTER_ALL,
    source_system_filter: str = FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
    *,
    as_of_date: date | None = None,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    forecast_load, actual_load = _forecast_actual_load_pair(loads)
    forecast_gas_date_filter = (
        NOMINATION_FORECAST_GAS_DATE_FILTER_ALL
        if gas_date_filter == FORECAST_ACTUAL_GAS_DATE_FILTER_ALL
        else gas_date_filter
    )
    forecast_facility_filter = (
        NOMINATION_FORECAST_FACILITY_FILTER_ALL
        if facility_filter == FORECAST_ACTUAL_FACILITY_FILTER_ALL
        else facility_filter
    )
    forecast_source_system_filter = (
        NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL
        if source_system_filter == FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL
        else source_system_filter
    )
    actual_gas_date_filter = (
        FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL
        if gas_date_filter == FORECAST_ACTUAL_GAS_DATE_FILTER_ALL
        else gas_date_filter
    )
    actual_facility_filter = (
        FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL
        if facility_filter == FORECAST_ACTUAL_FACILITY_FILTER_ALL
        else facility_filter
    )
    actual_source_system_filter = (
        FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL
        if source_system_filter == FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL
        else source_system_filter
    )

    return (
        _filtered_nomination_forecast_dataframe(
            forecast_load,
            forecast_gas_date_filter,
            forecast_source_system_filter,
            forecast_facility_filter,
            NOMINATION_FORECAST_LOCATION_FILTER_ALL,
            as_of_date=as_of_date,
        ),
        _filtered_facility_flow_storage_dataframe(
            actual_load,
            actual_gas_date_filter,
            actual_facility_filter,
            actual_source_system_filter,
        ),
    )


def _forecast_actual_string_filter_options(
    loads: Sequence[GasTableLoad],
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    forecast, actual = _forecast_actual_input_frames(loads)
    values: set[str] = set()
    for dataframe in (forecast, actual):
        if dataframe.is_empty() or column not in dataframe.columns:
            continue
        values.update(
            str(value)
            for value in dataframe.get_column(column)
            .drop_nulls()
            .cast(pl.String, strict=False)
            .unique()
            .to_list()
            if value is not None and str(value).strip() != ""
        )
    return (all_label, *sorted(values))


def _forecast_actual_aggregates(
    loads: Sequence[GasTableLoad],
    gas_date_filter: str,
    facility_filter: str,
    source_system_filter: str,
    *,
    as_of_date: date | None = None,
) -> tuple[
    dict[tuple[date | None, str | None, str | None], _ForecastActualAggregate],
    dict[tuple[date | None, str | None, str | None], _ForecastActualAggregate],
]:
    forecast, actual = _forecast_actual_input_frames(
        loads,
        gas_date_filter,
        facility_filter,
        source_system_filter,
        as_of_date=as_of_date,
    )
    return (
        _forecast_actual_forecast_aggregates(forecast),
        _forecast_actual_actual_aggregates(actual),
    )


def _forecast_actual_forecast_aggregates(
    dataframe: pl.DataFrame,
) -> dict[tuple[date | None, str | None, str | None], _ForecastActualAggregate]:
    aggregates: dict[
        tuple[date | None, str | None, str | None],
        _ForecastActualAggregate,
    ] = {}
    if dataframe.is_empty():
        return aggregates

    for row in dataframe.to_dicts():
        aggregate = aggregates.setdefault(
            _forecast_actual_key(row),
            _ForecastActualAggregate(),
        )
        _forecast_actual_update_common_aggregate(aggregate, row)
        forecast_type = _optional_non_empty_string(row.get("forecast_type"))
        forecast_version = _optional_non_empty_string(row.get("forecast_version"))
        if forecast_type is not None or forecast_version is not None:
            aggregate.forecast_type_versions.add((forecast_type, forecast_version))
        _forecast_actual_add_measure(
            aggregate,
            "demand",
            row.get("demand_forecast_gj"),
        )
        _forecast_actual_add_measure(
            aggregate,
            "supply",
            row.get("supply_forecast_gj"),
        )
        _forecast_actual_add_measure(
            aggregate,
            "transfer_in",
            row.get("transfer_in_forecast_gj"),
        )
        _forecast_actual_add_measure(
            aggregate,
            "transfer_out",
            row.get("transfer_out_forecast_gj"),
        )
    return aggregates


def _forecast_actual_actual_aggregates(
    dataframe: pl.DataFrame,
) -> dict[tuple[date | None, str | None, str | None], _ForecastActualAggregate]:
    aggregates: dict[
        tuple[date | None, str | None, str | None],
        _ForecastActualAggregate,
    ] = {}
    if dataframe.is_empty():
        return aggregates

    for row in dataframe.to_dicts():
        aggregate = aggregates.setdefault(
            _forecast_actual_key(row),
            _ForecastActualAggregate(),
        )
        _forecast_actual_update_common_aggregate(aggregate, row)
        _forecast_actual_add_measure(aggregate, "demand", row.get("demand_tj"), 1000.0)
        _forecast_actual_add_measure(aggregate, "supply", row.get("supply_tj"), 1000.0)
        _forecast_actual_add_measure(
            aggregate,
            "transfer_in",
            row.get("transfer_in_tj"),
            1000.0,
        )
        _forecast_actual_add_measure(
            aggregate,
            "transfer_out",
            row.get("transfer_out_tj"),
            1000.0,
        )
        _forecast_actual_add_measure(
            aggregate,
            "held_storage_tj",
            row.get("held_in_storage_tj"),
        )
        _forecast_actual_add_measure(
            aggregate,
            "cushion_gas_storage_tj",
            row.get("cushion_gas_storage_tj"),
        )
    return aggregates


def _forecast_actual_update_common_aggregate(
    aggregate: _ForecastActualAggregate,
    row: Mapping[str, object],
) -> None:
    aggregate.rows += 1
    source_system = _optional_non_empty_string(row.get("source_system"))
    if source_system is not None:
        aggregate.source_systems.add(source_system)
    source_table = _optional_non_empty_string(row.get("source_table"))
    if source_table is not None:
        aggregate.source_tables.add(source_table)
    aggregate.latest_source_update = _latest_datetime(
        aggregate.latest_source_update,
        _flow_datetime_value(row.get("source_last_updated_timestamp")),
    )
    aggregate.latest_ingest = _latest_datetime(
        aggregate.latest_ingest,
        _flow_datetime_value(row.get("ingested_timestamp")),
    )


def _forecast_actual_add_measure(
    aggregate: _ForecastActualAggregate,
    key: str,
    value: object | None,
    scale: float = 1.0,
) -> None:
    number = _optional_float(value)
    if number is None:
        return
    aggregate.measure_totals[key] = aggregate.measure_totals.get(key, 0.0) + (
        number * scale
    )
    aggregate.measure_counts[key] = aggregate.measure_counts.get(key, 0) + 1


def _forecast_actual_key(
    row: Mapping[str, object],
) -> tuple[date | None, str | None, str | None]:
    return (
        _flow_date_value(row.get("gas_date")),
        _optional_non_empty_string(row.get("source_facility_id")),
        _optional_non_empty_string(row.get("source_location_id")),
    )


def _forecast_actual_sort_key(
    key: tuple[date | None, str | None, str | None],
) -> tuple[int, str, str]:
    gas_date, source_facility_id, source_location_id = key
    gas_date_rank = -gas_date.toordinal() if gas_date is not None else 1
    return gas_date_rank, source_facility_id or "", source_location_id or ""


def _forecast_actual_comparison_row(
    key: tuple[date | None, str | None, str | None],
    forecast: _ForecastActualAggregate | None,
    actual: _ForecastActualAggregate | None,
) -> dict[str, object]:
    gas_date, source_facility_id, source_location_id = key
    forecast_demand = _forecast_actual_measure_total(forecast, "demand")
    actual_demand = _forecast_actual_measure_total(actual, "demand")
    forecast_supply = _forecast_actual_measure_total(forecast, "supply")
    actual_supply = _forecast_actual_measure_total(actual, "supply")
    forecast_transfer_in = _forecast_actual_measure_total(forecast, "transfer_in")
    actual_transfer_in = _forecast_actual_measure_total(actual, "transfer_in")
    forecast_transfer_out = _forecast_actual_measure_total(forecast, "transfer_out")
    actual_transfer_out = _forecast_actual_measure_total(actual, "transfer_out")

    return {
        "gas date": gas_date,
        "source facility id": source_facility_id,
        "source location id": source_location_id,
        "match status": _forecast_actual_match_status(forecast, actual),
        "forecast rows": 0 if forecast is None else forecast.rows,
        "actual rows": 0 if actual is None else actual.rows,
        "forecast source systems": _forecast_actual_join_values(
            None if forecast is None else forecast.source_systems
        ),
        "actual source systems": _forecast_actual_join_values(
            None if actual is None else actual.source_systems
        ),
        "forecast source tables": _forecast_actual_join_values(
            None if forecast is None else forecast.source_tables
        ),
        "actual source tables": _forecast_actual_join_values(
            None if actual is None else actual.source_tables
        ),
        "forecast type/version pairs": (
            0 if forecast is None else len(forecast.forecast_type_versions)
        ),
        "forecast demand gj": forecast_demand,
        "actual demand gj": actual_demand,
        "demand delta gj": _forecast_actual_delta(forecast_demand, actual_demand),
        "demand delta pct": _forecast_actual_delta_pct(forecast_demand, actual_demand),
        "forecast supply gj": forecast_supply,
        "actual supply gj": actual_supply,
        "supply delta gj": _forecast_actual_delta(forecast_supply, actual_supply),
        "supply delta pct": _forecast_actual_delta_pct(forecast_supply, actual_supply),
        "forecast transfer in gj": forecast_transfer_in,
        "actual transfer in gj": actual_transfer_in,
        "transfer in delta gj": _forecast_actual_delta(
            forecast_transfer_in,
            actual_transfer_in,
        ),
        "transfer in delta pct": _forecast_actual_delta_pct(
            forecast_transfer_in,
            actual_transfer_in,
        ),
        "forecast transfer out gj": forecast_transfer_out,
        "actual transfer out gj": actual_transfer_out,
        "transfer out delta gj": _forecast_actual_delta(
            forecast_transfer_out,
            actual_transfer_out,
        ),
        "transfer out delta pct": _forecast_actual_delta_pct(
            forecast_transfer_out,
            actual_transfer_out,
        ),
        "latest forecast update": (
            None if forecast is None else forecast.latest_source_update
        ),
        "latest actual update": None if actual is None else actual.latest_source_update,
        "latest forecast ingest": None if forecast is None else forecast.latest_ingest,
        "latest actual ingest": None if actual is None else actual.latest_ingest,
    }


def _forecast_actual_storage_row(
    key: tuple[date | None, str | None, str | None],
    actual: _ForecastActualAggregate,
    *,
    forecast_available: bool,
) -> dict[str, object]:
    gas_date, source_facility_id, source_location_id = key
    return {
        "gas date": gas_date,
        "source facility id": source_facility_id,
        "source location id": source_location_id,
        "forecast coverage": (
            "Matched forecast row in bounded view"
            if forecast_available
            else "No matching forecast row in bounded view"
        ),
        "actual rows": actual.rows,
        "actual source systems": _forecast_actual_join_values(actual.source_systems),
        "actual source tables": _forecast_actual_join_values(actual.source_tables),
        "held storage rows": actual.measure_counts.get("held_storage_tj", 0),
        "held in storage tj": _forecast_actual_measure_total(
            actual,
            "held_storage_tj",
        ),
        "cushion gas rows": actual.measure_counts.get("cushion_gas_storage_tj", 0),
        "cushion gas storage tj": _forecast_actual_measure_total(
            actual,
            "cushion_gas_storage_tj",
        ),
        "latest actual update": actual.latest_source_update,
        "latest actual ingest": actual.latest_ingest,
    }


def _forecast_actual_match_status(
    forecast: _ForecastActualAggregate | None,
    actual: _ForecastActualAggregate | None,
) -> str:
    if forecast is not None and actual is not None:
        return "Matched forecast and actual"
    if forecast is not None:
        return "Forecast only"
    return "Actual only"


def _forecast_actual_measure_total(
    aggregate: _ForecastActualAggregate | None,
    key: str,
) -> float | None:
    if aggregate is None or aggregate.measure_counts.get(key, 0) == 0:
        return None
    return aggregate.measure_totals.get(key, 0.0)


def _forecast_actual_delta(
    forecast_value: float | None,
    actual_value: float | None,
) -> float | None:
    if forecast_value is None or actual_value is None:
        return None
    return actual_value - forecast_value


def _forecast_actual_delta_pct(
    forecast_value: float | None,
    actual_value: float | None,
) -> float | None:
    if forecast_value is None or actual_value is None or forecast_value == 0:
        return None
    return ((actual_value - forecast_value) / forecast_value) * 100


def _forecast_actual_comparable_measure_count(
    forecast: _ForecastActualAggregate | None,
    actual: _ForecastActualAggregate | None,
) -> int:
    return sum(
        _forecast_actual_measure_total(forecast, measure) is not None
        and _forecast_actual_measure_total(actual, measure) is not None
        for measure in ("demand", "supply", "transfer_in", "transfer_out")
    )


def _forecast_actual_latest_gas_date(
    keys: set[tuple[date | None, str | None, str | None]],
) -> date | None:
    dates = [gas_date for gas_date, _, _ in keys if gas_date is not None]
    if len(dates) == 0:
        return None
    return max(dates)


def _forecast_actual_join_values(values: set[str] | None) -> str:
    if values is None or len(values) == 0:
        return ""
    return ", ".join(sorted(values))


def _forecast_actual_load_detail(load: GasTableLoad | None) -> str:
    if load is None:
        return "not requested by this dashboard run."
    if load.error is not None:
        return f"unavailable: {_markdown_breakable_text(load.error)}."
    if load.dataframe is None or load.dataframe.is_empty():
        return f"loaded from {_markdown_breakable_text(load.uri)} but returned no rows."
    return (
        f"loaded `{load.dataframe.height:,}` bounded rows from "
        f"{_markdown_breakable_text(load.uri)}."
    )


def _optional_float(value: object | None) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, int | float | str | bytes):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if isnan(number):
        return None
    return number


def _normalised_facility_flow_storage_dashboard_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    dataframe = _normalised_facility_flow_storage_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_FACILITY_FLOW_STORAGE_DASHBOARD_ROW_SCHEMA)

    rows = [_facility_flow_storage_dashboard_row(row) for row in dataframe.to_dicts()]
    return pl.DataFrame(rows, schema=_FACILITY_FLOW_STORAGE_DASHBOARD_ROW_SCHEMA)


def _facility_flow_storage_dashboard_row(
    row: Mapping[str, object],
) -> dict[str, object]:
    return {
        **row,
        "source_table": _facility_flow_storage_source_table_label(row),
    }


def _facility_flow_storage_source_table_label(
    row: Mapping[str, object],
) -> str:
    values = _source_coverage_value_strings(row.get("source_tables"))
    if len(values) == 0:
        return _SOURCE_COVERAGE_EMPTY_SOURCE_TABLE_VALUE
    return ", ".join(values)


def _facility_flow_storage_source_table_count(dataframe: pl.DataFrame) -> int:
    values: set[str] = set()
    for row in dataframe.select("source_tables").to_dicts():
        values.update(_source_coverage_value_strings(row.get("source_tables")))
    return len(values)


def _linepack_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_linepack_dashboard_dataframe(load)
    if dataframe.is_empty() or column not in dataframe.columns:
        return (all_label,)

    values = sorted(
        str(value)
        for value in dataframe.get_column(column)
        .drop_nulls()
        .cast(pl.String, strict=False)
        .unique()
        .to_list()
        if value is not None and str(value).strip() != ""
    )
    return (all_label, *values)


def _filtered_linepack_dataframe(
    load: GasTableLoad | None,
    gas_date_filter: str,
    facility_filter: str,
    zone_filter: str,
    adequacy_flag_filter: str,
    source_system_filter: str,
) -> pl.DataFrame:
    dataframe = _normalised_linepack_dashboard_dataframe(load)
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if gas_date_filter != LINEPACK_GAS_DATE_FILTER_ALL:
        filtered = filtered.filter(
            pl.col("gas_date").cast(pl.String) == gas_date_filter
        )
    if facility_filter != LINEPACK_FACILITY_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_facility_id") == facility_filter)
    if zone_filter != LINEPACK_ZONE_FILTER_ALL:
        filtered = filtered.filter(pl.col("zone_key") == zone_filter)
    if adequacy_flag_filter != LINEPACK_ADEQUACY_FLAG_FILTER_ALL:
        filtered = filtered.filter(pl.col("adequacy_flag") == adequacy_flag_filter)
    if source_system_filter != LINEPACK_SOURCE_SYSTEM_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_system") == source_system_filter)
    return filtered


def _normalised_linepack_dashboard_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    dataframe = _normalised_linepack_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_LINEPACK_DASHBOARD_ROW_SCHEMA)

    rows = [_linepack_dashboard_row(row) for row in dataframe.to_dicts()]
    return pl.DataFrame(rows, schema=_LINEPACK_DASHBOARD_ROW_SCHEMA)


def _linepack_dashboard_row(row: Mapping[str, object]) -> dict[str, object]:
    return {
        **row,
        "source_table": _linepack_source_table_label(row),
    }


def _linepack_source_table_label(row: Mapping[str, object]) -> str:
    values = [
        *_source_coverage_value_strings(row.get("source_table")),
        *_source_coverage_value_strings(row.get("source_tables")),
    ]
    unique_values = tuple(dict.fromkeys(values))
    if len(unique_values) == 0:
        return _SOURCE_COVERAGE_EMPTY_SOURCE_TABLE_VALUE
    return ", ".join(unique_values)


def _linepack_source_table_count(dataframe: pl.DataFrame) -> int:
    values: set[str] = set()
    for row in dataframe.select("source_table").to_dicts():
        values.update(_source_coverage_value_strings(row.get("source_table")))
    values.discard(_SOURCE_COVERAGE_EMPTY_SOURCE_TABLE_VALUE)
    return len(values)


def _capacity_outlook_string_filter_options(
    load: GasTableLoad | None,
    column: str,
    all_label: str,
) -> tuple[str, ...]:
    dataframe = _normalised_capacity_outlook_dashboard_dataframe(load)
    if dataframe.is_empty() or column not in dataframe.columns:
        return (all_label,)

    values = sorted(
        str(value)
        for value in dataframe.get_column(column)
        .drop_nulls()
        .cast(pl.String, strict=False)
        .unique()
        .to_list()
        if value is not None and str(value).strip() != ""
    )
    return (all_label, *values)


def _filtered_capacity_outlook_dataframe(
    load: GasTableLoad | None,
    date_range_filter: str,
    capacity_type_filter: str,
    direction_filter: str,
    facility_filter: str,
    source_coverage_filter: str,
    source_system_filter: str,
) -> pl.DataFrame:
    dataframe = _normalised_capacity_outlook_dashboard_dataframe(load)
    if dataframe.is_empty():
        return dataframe

    filtered = dataframe
    if date_range_filter != CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL:
        filtered = filtered.filter(pl.col("date_range") == date_range_filter)
    if capacity_type_filter != CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL:
        filtered = filtered.filter(pl.col("capacity_type") == capacity_type_filter)
    if direction_filter != CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL:
        filtered = filtered.filter(pl.col("flow_direction") == direction_filter)
    if facility_filter != CAPACITY_OUTLOOK_FACILITY_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_facility_id") == facility_filter)
    if source_coverage_filter != CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL:
        filtered = filtered.filter(
            pl.col("capacity_source_coverage") == source_coverage_filter
        )
    if source_system_filter != CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL:
        filtered = filtered.filter(pl.col("source_system") == source_system_filter)
    return filtered


def _normalised_capacity_outlook_dashboard_dataframe(
    load: GasTableLoad | None,
) -> pl.DataFrame:
    dataframe = _normalised_facility_capacity_dataframe(load)
    if dataframe.is_empty():
        return pl.DataFrame(schema=_CAPACITY_OUTLOOK_DASHBOARD_ROW_SCHEMA)

    rows = [_capacity_outlook_dashboard_row(row) for row in dataframe.to_dicts()]
    return pl.DataFrame(rows, schema=_CAPACITY_OUTLOOK_DASHBOARD_ROW_SCHEMA)


def _capacity_outlook_dashboard_row(row: Mapping[str, object]) -> dict[str, object]:
    return {
        **row,
        "source_table": _capacity_outlook_source_table_label(row),
        "date_range": _capacity_outlook_date_range_label(row),
        "capacity_source_coverage": _capacity_outlook_source_coverage_label(row),
    }


def _capacity_outlook_source_table_label(row: Mapping[str, object]) -> str:
    values = [
        *_source_coverage_value_strings(row.get("source_table")),
        *_source_coverage_value_strings(row.get("source_tables")),
    ]
    unique_values = tuple(dict.fromkeys(values))
    if len(unique_values) == 0:
        return _SOURCE_COVERAGE_EMPTY_SOURCE_TABLE_VALUE
    return ", ".join(unique_values)


def _capacity_outlook_source_table_count(dataframe: pl.DataFrame) -> int:
    values: set[str] = set()
    for row in dataframe.select("source_table").to_dicts():
        values.update(_source_coverage_value_strings(row.get("source_table")))
    values.discard(_SOURCE_COVERAGE_EMPTY_SOURCE_TABLE_VALUE)
    return len(values)


def _capacity_outlook_date_range_label(row: Mapping[str, object]) -> str:
    from_gas_date = _optional_non_empty_string(row.get("from_gas_date"))
    to_gas_date = _optional_non_empty_string(row.get("to_gas_date"))
    outlook_month = _int_from_value(row.get("outlook_month"))
    outlook_year = _int_from_value(row.get("outlook_year"))

    if from_gas_date is not None and to_gas_date is not None:
        return f"{from_gas_date} to {to_gas_date}"
    if from_gas_date is not None:
        return f"from {from_gas_date}"
    if to_gas_date is not None:
        return f"to {to_gas_date}"
    if outlook_month is not None and outlook_year is not None:
        return f"{outlook_year:04d}-{outlook_month:02d}"
    if outlook_year is not None:
        return str(outlook_year)
    return _CAPACITY_OUTLOOK_UNDATED_DATE_RANGE


def _capacity_outlook_source_coverage_label(row: Mapping[str, object]) -> str:
    source_tables = [
        *_source_coverage_value_strings(row.get("source_table")),
        *_source_coverage_value_strings(row.get("source_tables")),
    ]
    for source_table in source_tables:
        if source_table in _CAPACITY_OUTLOOK_SOURCE_TABLE_COVERAGE_LABELS:
            return _CAPACITY_OUTLOOK_SOURCE_TABLE_COVERAGE_LABELS[source_table]

    search_text = " ".join(
        value
        for value in (
            _optional_non_empty_string(row.get("capacity_type")),
            _optional_non_empty_string(row.get("capacity_description")),
            " ".join(source_tables),
        )
        if value is not None
    ).lower()
    normalised = search_text.replace("_", " ").replace("-", " ")
    if "connection point" in normalised:
        return "Connection-point nameplate"
    if "uncontracted" in normalised:
        return "Uncontracted capacity"
    if "nameplate" in normalised:
        return "Nameplate rating"
    if "medium term" in normalised:
        return "Medium-term capacity outlook"
    if "short term" in normalised:
        return "Short-term capacity outlook"
    return _CAPACITY_OUTLOOK_OTHER_SOURCE_COVERAGE


def _int_from_value(value: object | None) -> int | None:
    if isinstance(value, int):
        return value
    return None


def _render_capacity_outlook_context_link(entry: DashboardRegistryEntry) -> str:
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


def _capacity_outlook_context_links_css() -> str:
    return """\
.capacity-outlook-links {
    display: grid;
    gap: 12px;
    padding: 16px;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.capacity-outlook-links__eyebrow {
    margin: 0 0 4px;
    color: var(--emdl-green, #3e7a54);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0;
    text-transform: uppercase;
}

.capacity-outlook-links h2 {
    margin: 0;
    font-size: 1.1rem;
}

.capacity-outlook-links ul {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
    gap: 8px;
    padding: 0;
    margin: 0;
    list-style: none;
}

.capacity-outlook-links li {
    display: grid;
    gap: 4px;
    min-height: 84px;
    padding: 10px 12px;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: rgb(var(--emdl-panel-rgb, 255 255 255) / 0.76);
}

.capacity-outlook-links li:first-child {
    border-color: var(--emdl-green, #3e7a54);
}

.capacity-outlook-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 700;
    text-decoration: none;
}

.capacity-outlook-links span {
    color: var(--emdl-muted, #566365);
    overflow-wrap: anywhere;
}

.capacity-outlook-links li > span:nth-child(2) {
    font-size: 0.82rem;
    font-weight: 650;
}

.capacity-outlook-links code {
    overflow-wrap: anywhere;
    white-space: normal;
}

@media (max-width: 640px) {
    .capacity-outlook-links li {
        min-height: 0;
    }
}
"""


def _render_linepack_context_link(entry: DashboardRegistryEntry) -> str:
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


def _linepack_context_links_css() -> str:
    return """\
.linepack-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.linepack-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.linepack-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.linepack-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.linepack-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.linepack-links li:first-child {
    border-top: 0;
}

.linepack-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.linepack-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.linepack-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.linepack-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .linepack-links li {
        grid-template-columns: 1fr;
    }
}
"""


def _render_facility_flow_storage_context_link(
    entry: DashboardRegistryEntry,
) -> str:
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


def _facility_flow_storage_context_links_css() -> str:
    return """\
.facility-flow-storage-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.facility-flow-storage-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.facility-flow-storage-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.facility-flow-storage-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.facility-flow-storage-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.facility-flow-storage-links li:first-child {
    border-top: 0;
}

.facility-flow-storage-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.facility-flow-storage-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.facility-flow-storage-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.facility-flow-storage-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .facility-flow-storage-links li {
        grid-template-columns: 1fr;
    }
}
"""


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


def _render_participant_context_link(entry: DashboardRegistryEntry) -> str:
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


def _participant_context_links_css() -> str:
    return """\
.participant-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.participant-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.participant-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.participant-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.participant-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.participant-links li:first-child {
    border-top: 0;
}

.participant-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.participant-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.participant-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.participant-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .participant-links li {
        grid-template-columns: 1fr;
    }
}
"""


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


def _render_hub_zone_context_link(entry: DashboardRegistryEntry) -> str:
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


def _render_connection_point_context_link(entry: DashboardRegistryEntry) -> str:
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


def _render_flow_context_link(entry: DashboardRegistryEntry) -> str:
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


def _hub_zone_context_links_css() -> str:
    return """\
.hub-zone-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.hub-zone-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.hub-zone-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.hub-zone-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.hub-zone-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.hub-zone-links li:first-child {
    border-top: 0;
}

.hub-zone-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.hub-zone-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.hub-zone-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.hub-zone-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .hub-zone-links li {
        grid-template-columns: 1fr;
    }
}
"""


def _flow_context_links_css() -> str:
    return """\
.flow-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.flow-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.flow-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.flow-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.flow-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.flow-links li:first-child {
    border-top: 0;
}

.flow-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.flow-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.flow-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.flow-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .flow-links li {
        grid-template-columns: 1fr;
    }
}
"""


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


def _connection_point_context_links_css() -> str:
    return """\
.connection-point-links {
    display: grid;
    gap: 0.75rem;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.connection-point-links__eyebrow {
    margin: 0;
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.connection-point-links h2 {
    margin: 0.15rem 0 0;
    font-size: 1.05rem;
}

.connection-point-links ul {
    display: grid;
    gap: 0.5rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.connection-point-links li {
    display: grid;
    grid-template-columns: minmax(10rem, 1fr) auto auto;
    gap: 0.65rem;
    align-items: center;
    min-width: 0;
    padding: 0.55rem 0;
    border-top: 1px solid var(--emdl-line, #cfdbd6);
}

.connection-point-links li:first-child {
    border-top: 0;
}

.connection-point-links a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    overflow-wrap: anywhere;
    text-decoration: none;
}

.connection-point-links span {
    min-width: 0;
    overflow-wrap: anywhere;
}

.connection-point-links li > span:nth-child(2) {
    color: var(--emdl-muted, #566365);
    font-size: 0.84rem;
    font-weight: 700;
}

.connection-point-links code {
    overflow-wrap: anywhere;
}

@media (max-width: 760px) {
    .connection-point-links li {
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
        {_render_context_list("silver chunk paths", entry.silver_chunk_paths)}
        {_render_context_list("source hashes", entry.source_hashes)}
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
