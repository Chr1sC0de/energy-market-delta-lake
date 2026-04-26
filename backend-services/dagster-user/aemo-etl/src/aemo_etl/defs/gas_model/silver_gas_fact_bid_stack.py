import polars as pl
from dagster import (
    AssetCheckResult,
    AssetIn,
    AssetKey,
    AutomationCondition,
    AutomationConditionSensorDefinition,
    Definitions,
    MaterializeResult,
    TableColumnDep,
    TableColumnLineage,
    asset,
    asset_check,
    definitions,
)
from polars import LazyFrame

from aemo_etl.configs import AEMO_BUCKET, DEFAULT_SENSOR_STATUS
from aemo_etl.defs.gas_model._parsing import parse_gas_datetime
from aemo_etl.factories.checks import (
    duplicate_row_check_factory,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.utils import get_metadata_schema, get_surrogate_key

DOMAIN = "gas_model"
TABLE_NAME = "silver_gas_fact_bid_stack"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific bid stack step"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "gas_date",
    "participant_id",
    "source_point_id",
    "bid_id",
    "bid_step",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int131_v4_bids_at_bid_cutoff_times_prev_2_1",
    "silver.vicgas.silver_int314_v4_bid_stack_1",
]
SOURCE_SYSTEM = "VICGAS"
INT131_KEY = AssetKey(
    ["silver", "vicgas", "silver_int131_v4_bids_at_bid_cutoff_times_prev_2_1"]
)
INT314_KEY = AssetKey(["silver", "vicgas", "silver_int314_v4_bid_stack_1"])

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT131_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT314_KEY, column_name="surrogate_key"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
        "bid_price": [TableColumnDep(asset_key=INT314_KEY, column_name="bid_price")],
        "bid_qty_gj": [TableColumnDep(asset_key=INT314_KEY, column_name="bid_qty_gj")],
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "gas_date": pl.Date,
    "participant_key": pl.String,
    "participant_id": pl.String,
    "participant_name": pl.String,
    "source_point_id": pl.String,
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
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {column: column.replace("_", " ") for column in SCHEMA}
REQUIRED_COLUMNS = ["surrogate_key", "source_system", "source_table", "bid_id"]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _cutoff_bid_rows(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[0]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[0]),
        gas_date=_parse_datetime("gas_date").dt.date(),
        participant_key=pl.lit(None).cast(pl.String),
        participant_id=pl.col("participant_id").cast(pl.String),
        participant_name=pl.col("participant_name").cast(pl.String),
        source_point_id=pl.col("code").cast(pl.String),
        bid_id=pl.col("bid_id").cast(pl.String),
        bid_step=pl.lit(None).cast(pl.Int64),
        bid_price=pl.lit(None).cast(pl.Float64),
        bid_qty_gj=pl.col("min_daily_qty").cast(pl.Float64),
        step_qty_gj=pl.lit(None).cast(pl.Float64),
        offer_type=pl.col("offer_type").cast(pl.String),
        inject_withdraw=pl.col("type_1").cast(pl.String),
        schedule_type=pl.col("schedule_type").cast(pl.String),
        schedule_time=pl.col("schedule_time").cast(pl.String),
        bid_cutoff_timestamp=_parse_datetime("bid_cutoff_time"),
        source_last_updated=pl.col("current_date").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("current_date"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _public_bid_stack_rows(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[1]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[1]),
        gas_date=_parse_datetime("gas_date").dt.date(),
        participant_key=pl.lit(None).cast(pl.String),
        participant_id=pl.col("market_participant_id").cast(pl.String),
        participant_name=pl.col("company_name").cast(pl.String),
        source_point_id=pl.col("mirn").cast(pl.String),
        bid_id=pl.col("bid_id").cast(pl.String),
        bid_step=pl.col("bid_step").cast(pl.Int64),
        bid_price=pl.col("bid_price").cast(pl.Float64),
        bid_qty_gj=pl.col("bid_qty_gj").cast(pl.Float64),
        step_qty_gj=pl.col("step_qty_gj").cast(pl.Float64),
        offer_type=pl.lit(None).cast(pl.String),
        inject_withdraw=pl.col("inject_withdraw").cast(pl.String),
        schedule_type=pl.lit(None).cast(pl.String),
        schedule_time=pl.lit(None).cast(pl.String),
        bid_cutoff_timestamp=pl.lit(None).cast(pl.Datetime("us")),
        source_last_updated=pl.col("current_date").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("current_date"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _select_bid_stack(int131: LazyFrame, int314: LazyFrame) -> LazyFrame:
    return (
        pl.concat(
            [_cutoff_bid_rows(int131), _public_bid_stack_rows(int314)],
            how="diagonal_relaxed",
        )
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
    description="Silver gas bid stack fact.",
    ins={"int131": AssetIn(key=INT131_KEY), "int314": AssetIn(key=INT314_KEY)},
    io_manager_key="aemo_parquet_overwrite_io_manager",
    metadata={
        "dagster/table_name": f"silver.{DOMAIN}.{TABLE_NAME}",
        "dagster/uri": f"s3://{AEMO_BUCKET}/{'/'.join(KEY_PREFIX)}/{TABLE_NAME}",
        "dagster/column_schema": get_metadata_schema(SCHEMA, DESCRIPTIONS),
        "grain": GRAIN,
        "surrogate_key_sources": SURROGATE_KEY_SOURCES,
        "source_tables": SOURCE_TABLES,
    },
    tags={"ecs/cpu": "512", "ecs/memory": "4096"},
    kinds={"table", "parquet"},
    automation_condition=AutomationCondition.any_deps_updated()
    & ~AutomationCondition.in_progress()
    & ~AutomationCondition.any_deps_missing(),
)
def silver_gas_fact_bid_stack(
    int131: LazyFrame, int314: LazyFrame
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(_select_bid_stack(int131, int314))


@asset_check(asset=silver_gas_fact_bid_stack, name="check_required_fields")
def silver_gas_fact_bid_stack_required_fields(input_df: LazyFrame) -> AssetCheckResult:
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


silver_gas_fact_bid_stack_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_bid_stack,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_bid_stack_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_bid_stack, check_name="check_schema_matches"
)
silver_gas_fact_bid_stack_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_bid_stack, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_bid_stack],
        asset_checks=[
            silver_gas_fact_bid_stack_duplicate_row_check,
            silver_gas_fact_bid_stack_schema_check,
            silver_gas_fact_bid_stack_schema_drift_check,
            silver_gas_fact_bid_stack_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_bid_stack_sensor",
                target=[silver_gas_fact_bid_stack.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
