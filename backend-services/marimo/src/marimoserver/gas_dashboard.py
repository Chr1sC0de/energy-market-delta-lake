"""Helpers for the gas market overview marimo dashboard."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
import os

import polars as pl

DEFAULT_NAME_PREFIX = "energy-market"
DEFAULT_DEVELOPMENT_ENVIRONMENT = "dev"
DEFAULT_AWS_ENDPOINT_URL = "http://localstack:4566"
DEFAULT_AWS_REGION = "ap-southeast-4"
DEFAULT_AWS_ACCESS_KEY_ID = "test"
DEFAULT_AWS_SECRET_ACCESS_KEY = "test"
DEFAULT_AWS_ALLOW_HTTP = "true"
DEFAULT_AWS_PREVIEW_ROWS = 100
AWS_DEVELOPMENT_LOCATION = "aws"
SILVER_GAS_MODEL_PREFIX = "silver/gas_model"


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

    @property
    def available(self) -> bool:
        """Return whether the table loaded and contains at least one row."""
        return self.dataframe is not None and not self.dataframe.is_empty()


TableReader = Callable[[str, Mapping[str, str], int | None], pl.DataFrame]

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


def read_parquet_table(
    uri: str,
    storage_options: Mapping[str, str],
    row_limit: int | None = None,
) -> pl.DataFrame:
    """Read one gas_model Parquet dataset using Polars storage options."""
    options = dict(storage_options)
    scan = pl.scan_parquet(_parquet_dataset_glob(uri), storage_options=options)
    if row_limit is not None:
        scan = scan.head(row_limit)
    return scan.collect()


def load_gas_model_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] = GAS_MODEL_TABLES,
    reader: TableReader = read_parquet_table,
) -> list[GasTableLoad]:
    """Load configured gas_model tables, returning unavailable entries on errors."""
    storage_options = config.storage_options()
    row_limit = None if config.full_table_scan_enabled else config.max_preview_rows
    loads: list[GasTableLoad] = []

    for spec in specs:
        uri = config.table_uri(spec.table_name)
        try:
            dataframe = reader(uri, storage_options, row_limit)
        except Exception as error:
            loads.append(
                GasTableLoad(
                    spec=spec,
                    uri=uri,
                    dataframe=None,
                    error=_compact_error(error),
                )
            )
            continue

        loads.append(
            GasTableLoad(
                spec=spec,
                uri=uri,
                dataframe=dataframe,
                error=None,
            )
        )

    return loads


def table_load_by_name(
    loads: Sequence[GasTableLoad],
    table_name: str,
) -> GasTableLoad | None:
    """Return a loaded table entry by gas_model table name."""
    for load in loads:
        if load.spec.table_name == table_name:
            return load
    return None


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


def _parquet_dataset_glob(uri: str) -> str:
    return f"{uri.rstrip('/')}/*.parquet"


def _compact_error(error: Exception) -> str:
    message = str(error).strip().splitlines()
    if not message:
        return error.__class__.__name__
    return f"{error.__class__.__name__}: {message[0]}"
