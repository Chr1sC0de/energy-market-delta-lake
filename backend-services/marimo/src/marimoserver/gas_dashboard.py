"""Helpers for the local gas market overview marimo dashboard."""

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
SILVER_GAS_MODEL_PREFIX = "silver/gas_model"


@dataclass(frozen=True)
class GasDashboardConfig:
    """Environment-derived settings used to read local gas model Delta tables."""

    development_environment: str
    name_prefix: str
    aemo_bucket: str
    aws_endpoint_url: str
    aws_region: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_allow_http: str

    def table_uri(self, table_name: str) -> str:
        """Return the Delta table URI for a silver gas_model table."""
        return f"s3://{self.aemo_bucket}/{SILVER_GAS_MODEL_PREFIX}/{table_name}"

    def storage_options(self) -> dict[str, str]:
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
class GasTableSpec:
    """A gas_model output table included in the local dashboard."""

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


DeltaReader = Callable[[str, Mapping[str, str]], pl.DataFrame]

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
        development_environment=development_environment,
        name_prefix=name_prefix,
        aemo_bucket=aemo_bucket,
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


def read_delta_table(uri: str, storage_options: Mapping[str, str]) -> pl.DataFrame:
    """Read one Delta table using Polars and delta-rs storage options."""
    return pl.read_delta(uri, storage_options=dict(storage_options))


def load_gas_model_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] = GAS_MODEL_TABLES,
    reader: DeltaReader = read_delta_table,
) -> list[GasTableLoad]:
    """Load configured gas_model tables, returning unavailable entries on errors."""
    storage_options = config.storage_options()
    loads: list[GasTableLoad] = []

    for spec in specs:
        uri = config.table_uri(spec.table_name)
        try:
            dataframe = reader(uri, storage_options)
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


def _compact_error(error: Exception) -> str:
    message = str(error).strip().splitlines()
    if not message:
        return error.__class__.__name__
    return f"{error.__class__.__name__}: {message[0]}"
