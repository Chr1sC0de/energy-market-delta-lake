import polars as pl
from dagster import (
    AssetCheckResult,
    AssetIn,
    AssetKey,
    AutomationCondition,
    Definitions,
    MaterializeResult,
    TableColumnDep,
    TableColumnLineage,
    asset,
    asset_check,
    definitions,
)
from polars import LazyFrame

from aemo_etl.configs import AEMO_BUCKET
from aemo_etl.defs.gas_model._parsing import parse_gas_datetime
from aemo_etl.factories.checks import (
    duplicate_row_check_factory,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.utils import get_metadata_schema, get_surrogate_key

DOMAIN = "gas_model"
TABLE_NAME = "silver_gas_fact_heating_value"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific heating value observation"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "gas_date",
    "source_zone_id",
    "gas_interval",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int047_v4_heating_values_1",
    "silver.vicgas.silver_int139_v4_declared_daily_state_heating_value_1",
    "silver.vicgas.silver_int139a_v4_daily_zonal_heating_1",
    "silver.vicgas.silver_int439_v4_published_daily_heating_value_non_pts_1",
    "silver.vicgas.silver_int539_v4_daily_zonal_hv_1",
    "silver.vicgas.silver_int839a_v1_daily_zonal_hv_1",
]
SOURCE_SYSTEM = "VICGAS"
INT047_KEY = AssetKey(["silver", "vicgas", "silver_int047_v4_heating_values_1"])
INT139_KEY = AssetKey(
    ["silver", "vicgas", "silver_int139_v4_declared_daily_state_heating_value_1"]
)
INT139A_KEY = AssetKey(["silver", "vicgas", "silver_int139a_v4_daily_zonal_heating_1"])
INT439_KEY = AssetKey(
    ["silver", "vicgas", "silver_int439_v4_published_daily_heating_value_non_pts_1"]
)
INT539_KEY = AssetKey(["silver", "vicgas", "silver_int539_v4_daily_zonal_hv_1"])
INT839A_KEY = AssetKey(["silver", "vicgas", "silver_int839a_v1_daily_zonal_hv_1"])

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT047_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT139_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT139A_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT439_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT539_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT839A_KEY, column_name="surrogate_key"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
        "heating_value": [
            TableColumnDep(asset_key=INT047_KEY, column_name="current_heating_value"),
            TableColumnDep(asset_key=INT139_KEY, column_name="declared_heating_value"),
            TableColumnDep(asset_key=INT139A_KEY, column_name="heating_value"),
            TableColumnDep(asset_key=INT439_KEY, column_name="heating_value"),
            TableColumnDep(asset_key=INT539_KEY, column_name="heating_value_mj"),
            TableColumnDep(asset_key=INT839A_KEY, column_name="heating_value_mj"),
        ],
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "gas_date": pl.Date,
    "gas_interval": pl.String,
    "source_zone_id": pl.String,
    "zone_name": pl.String,
    "heating_value": pl.Float64,
    "initial_heating_value": pl.Float64,
    "heating_value_unit": pl.String,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {column: column.replace("_", " ") for column in SCHEMA}
REQUIRED_COLUMNS = ["surrogate_key", "source_system", "source_table"]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _base(
    source_table: str, gas_date_column: str, updated_column: str
) -> list[pl.Expr]:
    return [
        pl.lit(SOURCE_SYSTEM).alias("source_system"),
        pl.lit([source_table]).cast(pl.List(pl.String)).alias("source_tables"),
        pl.lit(source_table).alias("source_table"),
        _parse_datetime(gas_date_column).dt.date().alias("gas_date"),
        pl.col(updated_column).cast(pl.String).alias("source_last_updated"),
        _parse_datetime(updated_column).alias("source_last_updated_timestamp"),
        pl.col("surrogate_key").cast(pl.String).alias("source_surrogate_key"),
        pl.col("source_file").cast(pl.String).alias("source_file"),
        pl.col("ingested_timestamp").alias("ingested_timestamp"),
    ]


def _select_heating_values(
    int047: LazyFrame,
    int139: LazyFrame,
    int139a: LazyFrame,
    int439: LazyFrame,
    int539: LazyFrame,
    int839a: LazyFrame,
) -> LazyFrame:
    rows = [
        int047.select(
            *_base(SOURCE_TABLES[0], "gas_date", "current_date"),
            gas_interval=pl.col("event_interval").cast(pl.String),
            source_zone_id=pl.col("heating_value_zone").cast(pl.String),
            zone_name=pl.col("heating_value_zone_desc").cast(pl.String),
            heating_value=pl.col("current_heating_value").cast(pl.Float64),
            initial_heating_value=pl.col("initial_heating_value").cast(pl.Float64),
            heating_value_unit=pl.lit("GJ/1000m3"),
        ),
        int139.select(
            *_base(SOURCE_TABLES[1], "gas_date", "current_date"),
            gas_interval=pl.lit(None).cast(pl.String),
            source_zone_id=pl.lit("VIC").cast(pl.String),
            zone_name=pl.lit("Victoria"),
            heating_value=pl.col("declared_heating_value").cast(pl.Float64),
            initial_heating_value=pl.lit(None).cast(pl.Float64),
            heating_value_unit=pl.lit("declared"),
        ),
        int139a.select(
            *_base(SOURCE_TABLES[2], "gas_date", "current_date"),
            gas_interval=pl.lit(None).cast(pl.String),
            source_zone_id=pl.col("hv_zone").cast(pl.String),
            zone_name=pl.col("hv_zone_desc").cast(pl.String),
            heating_value=pl.col("heating_value").cast(pl.Float64),
            initial_heating_value=pl.lit(None).cast(pl.Float64),
            heating_value_unit=pl.lit("source"),
        ),
        int439.select(
            *_base(SOURCE_TABLES[3], "gas_day", "current_date"),
            gas_interval=pl.lit(None).cast(pl.String),
            source_zone_id=pl.col("network_name").cast(pl.String),
            zone_name=pl.col("network_name").cast(pl.String),
            heating_value=pl.col("heating_value").cast(pl.Float64),
            initial_heating_value=pl.lit(None).cast(pl.Float64),
            heating_value_unit=pl.lit("source"),
        ),
        int539.select(
            *_base(SOURCE_TABLES[4], "gas_date", "current_date"),
            gas_interval=pl.lit(None).cast(pl.String),
            source_zone_id=pl.col("hv_zone").cast(pl.String),
            zone_name=pl.col("hv_zone_desc").cast(pl.String),
            heating_value=pl.col("heating_value_mj").cast(pl.Float64),
            initial_heating_value=pl.lit(None).cast(pl.Float64),
            heating_value_unit=pl.lit("MJ"),
        ),
        int839a.select(
            *_base(SOURCE_TABLES[5], "gas_date", "current_date"),
            gas_interval=pl.lit(None).cast(pl.String),
            source_zone_id=pl.col("hv_zone").cast(pl.String),
            zone_name=pl.col("hv_zone_description").cast(pl.String),
            heating_value=pl.col("heating_value_mj").cast(pl.Float64),
            initial_heating_value=pl.lit(None).cast(pl.Float64),
            heating_value_unit=pl.lit("MJ"),
        ),
    ]
    return (
        pl.concat(rows, how="diagonal_relaxed")
        .with_columns(
            date_key=get_surrogate_key(["gas_date"]),
            surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES),
        )
        .select(list(SCHEMA))
    )


def _materialize_result(value: LazyFrame) -> MaterializeResult[LazyFrame]:
    return MaterializeResult(
        value=value, metadata={"dagster/column_lineage": COLUMN_LINEAGE}
    )


@asset(
    key_prefix=KEY_PREFIX,
    group_name=GROUP_NAME,
    description="Silver gas heating value fact.",
    ins={
        "int047": AssetIn(key=INT047_KEY),
        "int139": AssetIn(key=INT139_KEY),
        "int139a": AssetIn(key=INT139A_KEY),
        "int439": AssetIn(key=INT439_KEY),
        "int539": AssetIn(key=INT539_KEY),
        "int839a": AssetIn(key=INT839A_KEY),
    },
    io_manager_key="aemo_deltalake_overwrite_io_manager",
    metadata={
        "dagster/table_name": f"silver.{DOMAIN}.{TABLE_NAME}",
        "dagster/uri": f"s3://{AEMO_BUCKET}/{'/'.join(KEY_PREFIX)}/{TABLE_NAME}",
        "dagster/column_schema": get_metadata_schema(SCHEMA, DESCRIPTIONS),
        "grain": GRAIN,
        "surrogate_key_sources": SURROGATE_KEY_SOURCES,
        "source_tables": SOURCE_TABLES,
    },
    kinds={"table", "deltalake"},
    automation_condition=AutomationCondition.any_deps_updated()
    & ~AutomationCondition.in_progress()
    & ~AutomationCondition.any_deps_missing(),
)
def silver_gas_fact_heating_value(
    int047: LazyFrame,
    int139: LazyFrame,
    int139a: LazyFrame,
    int439: LazyFrame,
    int539: LazyFrame,
    int839a: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_heating_values(int047, int139, int139a, int439, int539, int839a)
    )


@asset_check(asset=silver_gas_fact_heating_value, name="check_required_fields")
def silver_gas_fact_heating_value_required_fields(
    input_df: LazyFrame,
) -> AssetCheckResult:
    null_counts = (
        input_df.select(pl.col(column).is_null().sum() for column in REQUIRED_COLUMNS)
        .collect()
        .to_dicts()[0]
    )
    return AssetCheckResult(
        passed=all(count == 0 for count in null_counts.values()),
        check_name="check_required_fields",
        metadata={"null_counts": null_counts},
    )


silver_gas_fact_heating_value_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_heating_value,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_heating_value_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_heating_value, check_name="check_schema_matches"
)
silver_gas_fact_heating_value_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_heating_value, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_heating_value],
        asset_checks=[
            silver_gas_fact_heating_value_duplicate_row_check,
            silver_gas_fact_heating_value_schema_check,
            silver_gas_fact_heating_value_schema_drift_check,
            silver_gas_fact_heating_value_required_fields,
        ],
    )
