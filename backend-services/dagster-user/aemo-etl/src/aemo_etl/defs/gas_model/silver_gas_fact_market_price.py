import polars as pl
from dagster import (
    AssetCheckResult,
    AssetIn,
    AssetKey,
    AutomationCondition,
    AutomationConditionSensorDefinition,
    Backoff,
    Definitions,
    Jitter,
    MaterializeResult,
    RetryPolicy,
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
TABLE_NAME = "silver_gas_fact_market_price"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific market price observation"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "gas_date",
    "price_type",
    "schedule_interval",
    "transmission_id",
    "source_location_id",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int037b_v4_indicative_mkt_price_1",
    "silver.vicgas.silver_int037c_v4_indicative_price_1",
    "silver.vicgas.silver_int039b_v4_indicative_locational_price_1",
    "silver.vicgas.silver_int041_v4_market_and_reference_prices_1",
    "silver.vicgas.silver_int042_v4_weighted_average_daily_prices_1",
    "silver.vicgas.silver_int199_v4_cumulative_price_1",
    "silver.vicgas.silver_int310_v1_price_and_withdrawals_rpt_1",
    "silver.vicgas.silver_int310_v4_price_and_withdrawals_1",
    "silver.vicgas.silver_int235_v4_sched_system_total_1",
]
SOURCE_SYSTEM = "VICGAS"

INT037B_KEY = AssetKey(["silver", "vicgas", "silver_int037b_v4_indicative_mkt_price_1"])
INT037C_KEY = AssetKey(["silver", "vicgas", "silver_int037c_v4_indicative_price_1"])
INT039B_KEY = AssetKey(
    ["silver", "vicgas", "silver_int039b_v4_indicative_locational_price_1"]
)
INT041_KEY = AssetKey(
    ["silver", "vicgas", "silver_int041_v4_market_and_reference_prices_1"]
)
INT042_KEY = AssetKey(
    ["silver", "vicgas", "silver_int042_v4_weighted_average_daily_prices_1"]
)
INT199_KEY = AssetKey(["silver", "vicgas", "silver_int199_v4_cumulative_price_1"])
INT310_V1_KEY = AssetKey(
    ["silver", "vicgas", "silver_int310_v1_price_and_withdrawals_rpt_1"]
)
INT310_V4_KEY = AssetKey(
    ["silver", "vicgas", "silver_int310_v4_price_and_withdrawals_1"]
)
INT235_KEY = AssetKey(["silver", "vicgas", "silver_int235_v4_sched_system_total_1"])

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT037B_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT037C_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT039B_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT041_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT042_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT199_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT310_V1_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT310_V4_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT235_KEY, column_name="surrogate_key"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
        "gas_date": [
            TableColumnDep(asset_key=INT037B_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT037C_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT039B_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT041_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT042_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT199_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT310_V1_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT310_V4_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT235_KEY, column_name="gas_date"),
        ],
        "price_value_gst_ex": [
            TableColumnDep(asset_key=INT037B_KEY, column_name="price_value_gst_ex"),
            TableColumnDep(asset_key=INT037C_KEY, column_name="price_value_gst_ex"),
            TableColumnDep(
                asset_key=INT039B_KEY, column_name="nodal_price_value_gst_ex"
            ),
            TableColumnDep(asset_key=INT310_V1_KEY, column_name="price_value"),
            TableColumnDep(asset_key=INT310_V4_KEY, column_name="price_value"),
            TableColumnDep(asset_key=INT235_KEY, column_name="value"),
        ],
        "weighted_average_price_gst_ex": [
            TableColumnDep(
                asset_key=INT041_KEY, column_name="imb_wtd_ave_price_gst_ex"
            ),
            TableColumnDep(
                asset_key=INT042_KEY, column_name="imb_dev_wa_dly_price_gst_ex"
            ),
        ],
        "cumulative_price": [
            TableColumnDep(asset_key=INT199_KEY, column_name="cumulative_price")
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
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver fact primary key generated by surrogate_key_sources.",
    "date_key": "Deterministic silver_gas_dim_date surrogate_key for gas_date.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the row.",
    "source_table": "Specific silver source table for this row.",
    "gas_date": "Gas day date.",
    "price_type": "Normalized price measure type.",
    "schedule_type_id": "Source schedule type identifier where present.",
    "schedule_interval": "Source schedule interval or gas hour where present.",
    "transmission_id": "Source transmission or schedule identifier.",
    "transmission_doc_id": "Source transmission document identifier where present.",
    "source_location_id": "Source node, location, or market id where present.",
    "price_value_gst_ex": "Market or nodal price value, GST exclusive.",
    "weighted_average_price_gst_ex": "Weighted average price, GST exclusive.",
    "cumulative_price": "Cumulative price value where reported.",
    "administered_price": "Administered price value where reported.",
    "source_last_updated": "Raw source update value.",
    "source_last_updated_timestamp": "Parsed source update timestamp.",
    "source_surrogate_key": "Source row surrogate key for lineage.",
    "source_file": "Archived source file for the source row.",
    "ingested_timestamp": "Timestamp when the source row was ingested.",
}

REQUIRED_COLUMNS = ["surrogate_key", "source_system", "source_table"]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _base_columns(
    source_table: str, gas_date_column: str, last_updated_column: str
) -> list[pl.Expr]:
    return [
        pl.lit(SOURCE_SYSTEM).alias("source_system"),
        pl.lit([source_table]).cast(pl.List(pl.String)).alias("source_tables"),
        pl.lit(source_table).alias("source_table"),
        _parse_datetime(gas_date_column).dt.date().alias("gas_date"),
        pl.col(last_updated_column).cast(pl.String).alias("source_last_updated"),
        _parse_datetime(last_updated_column).alias("source_last_updated_timestamp"),
        pl.col("surrogate_key").cast(pl.String).alias("source_surrogate_key"),
        pl.col("source_file").cast(pl.String).alias("source_file"),
        pl.col("ingested_timestamp").alias("ingested_timestamp"),
    ]


def _indicative_price_rows(
    df: LazyFrame, source_table: str, price_type: str
) -> LazyFrame:
    return df.select(
        *_base_columns(source_table, "gas_date", "current_date"),
        price_type=pl.lit(price_type),
        schedule_type_id=pl.col("schedule_type_id").cast(pl.String),
        schedule_interval=pl.lit(None).cast(pl.String),
        transmission_id=pl.col("transmission_id").cast(pl.String),
        transmission_doc_id=pl.lit(None).cast(pl.String),
        source_location_id=pl.col("transmission_group_id").cast(pl.String),
        price_value_gst_ex=pl.col("price_value_gst_ex").cast(pl.Float64),
        weighted_average_price_gst_ex=pl.lit(None).cast(pl.Float64),
        cumulative_price=pl.lit(None).cast(pl.Float64),
        administered_price=pl.lit(None).cast(pl.Float64),
    )


def _market_reference_prices(df: LazyFrame) -> LazyFrame:
    return df.select(
        *_base_columns(SOURCE_TABLES[3], "gas_date", "current_date"),
        price_type=pl.lit("market_reference_daily"),
        schedule_type_id=pl.lit(None).cast(pl.String),
        schedule_interval=pl.lit(None).cast(pl.String),
        transmission_id=pl.lit(None).cast(pl.String),
        transmission_doc_id=pl.lit(None).cast(pl.String),
        source_location_id=pl.lit(None).cast(pl.String),
        price_value_gst_ex=pl.col("price_bod_gst_ex").cast(pl.Float64),
        weighted_average_price_gst_ex=pl.col("imb_wtd_ave_price_gst_ex").cast(
            pl.Float64
        ),
        cumulative_price=pl.lit(None).cast(pl.Float64),
        administered_price=pl.lit(None).cast(pl.Float64),
    )


def _select_market_prices(
    int037b: LazyFrame,
    int037c: LazyFrame,
    int039b: LazyFrame,
    int041: LazyFrame,
    int042: LazyFrame,
    int199: LazyFrame,
    int310_v1: LazyFrame,
    int310_v4: LazyFrame,
    int235: LazyFrame,
) -> LazyFrame:
    rows = [
        _indicative_price_rows(int037b, SOURCE_TABLES[0], "indicative_market"),
        _indicative_price_rows(int037c, SOURCE_TABLES[1], "indicative_operating"),
        int039b.select(
            *_base_columns(SOURCE_TABLES[2], "gas_date", "current_date"),
            price_type=pl.lit("indicative_locational"),
            schedule_type_id=pl.lit(None).cast(pl.String),
            schedule_interval=pl.col("ti").cast(pl.String),
            transmission_id=pl.col("transmission_id").cast(pl.String),
            transmission_doc_id=pl.lit(None).cast(pl.String),
            source_location_id=pl.col("node_name").cast(pl.String),
            price_value_gst_ex=pl.col("nodal_price_value_gst_ex").cast(pl.Float64),
            weighted_average_price_gst_ex=pl.lit(None).cast(pl.Float64),
            cumulative_price=pl.lit(None).cast(pl.Float64),
            administered_price=pl.lit(None).cast(pl.Float64),
        ),
        _market_reference_prices(int041),
        int042.select(
            *_base_columns(SOURCE_TABLES[4], "gas_date", "current_date"),
            price_type=pl.lit("weighted_average_daily"),
            schedule_type_id=pl.lit(None).cast(pl.String),
            schedule_interval=pl.lit(None).cast(pl.String),
            transmission_id=pl.lit(None).cast(pl.String),
            transmission_doc_id=pl.lit(None).cast(pl.String),
            source_location_id=pl.lit(None).cast(pl.String),
            price_value_gst_ex=pl.lit(None).cast(pl.Float64),
            weighted_average_price_gst_ex=pl.col("imb_dev_wa_dly_price_gst_ex").cast(
                pl.Float64
            ),
            cumulative_price=pl.lit(None).cast(pl.Float64),
            administered_price=pl.lit(None).cast(pl.Float64),
        ),
        int199.select(
            *_base_columns(SOURCE_TABLES[5], "gas_date", "current_date"),
            price_type=pl.lit("cumulative_price"),
            schedule_type_id=pl.col("schedule_type_id").cast(pl.String),
            schedule_interval=pl.col("schedule_interval").cast(pl.String),
            transmission_id=pl.col("transmission_id").cast(pl.String),
            transmission_doc_id=pl.col("transmission_doc_id").cast(pl.String),
            source_location_id=pl.lit(None).cast(pl.String),
            price_value_gst_ex=pl.lit(None).cast(pl.Float64),
            weighted_average_price_gst_ex=pl.lit(None).cast(pl.Float64),
            cumulative_price=pl.col("cumulative_price").cast(pl.Float64),
            administered_price=pl.lit(None).cast(pl.Float64),
        ),
        int310_v1.select(
            *_base_columns(SOURCE_TABLES[6], "gas_date", "gas_date"),
            price_type=pl.lit("price_and_withdrawals"),
            schedule_type_id=pl.lit(None).cast(pl.String),
            schedule_interval=pl.col("gas_hour").cast(pl.String),
            transmission_id=pl.col("transmission_id").cast(pl.String),
            transmission_doc_id=pl.lit(None).cast(pl.String),
            source_location_id=pl.lit(None).cast(pl.String),
            price_value_gst_ex=pl.col("price_value").cast(pl.Float64),
            weighted_average_price_gst_ex=pl.lit(None).cast(pl.Float64),
            cumulative_price=pl.lit(None).cast(pl.Float64),
            administered_price=pl.col("administered_price").cast(pl.Float64),
        ),
        int310_v4.select(
            *_base_columns(SOURCE_TABLES[7], "gas_date", "gas_date"),
            price_type=pl.lit("price_and_withdrawals"),
            schedule_type_id=pl.lit(None).cast(pl.String),
            schedule_interval=pl.col("schedule_interval").cast(pl.String),
            transmission_id=pl.col("transmission_id").cast(pl.String),
            transmission_doc_id=pl.lit(None).cast(pl.String),
            source_location_id=pl.lit(None).cast(pl.String),
            price_value_gst_ex=pl.col("price_value").cast(pl.Float64),
            weighted_average_price_gst_ex=pl.lit(None).cast(pl.Float64),
            cumulative_price=pl.lit(None).cast(pl.Float64),
            administered_price=pl.col("administered_price").cast(pl.Float64),
        ),
        int235.filter(pl.col("data_type").cast(pl.String).str.contains("PRICE")).select(
            *_base_columns(SOURCE_TABLES[8], "gas_date", "current_date"),
            price_type=pl.col("data_type").cast(pl.String),
            schedule_type_id=pl.col("flag").cast(pl.String),
            schedule_interval=pl.col("detail").cast(pl.String),
            transmission_id=pl.col("transmission_id").cast(pl.String),
            transmission_doc_id=pl.col("transmission_doc_id").cast(pl.String),
            source_location_id=pl.col("id").cast(pl.String),
            price_value_gst_ex=pl.col("value").cast(pl.Float64),
            weighted_average_price_gst_ex=pl.lit(None).cast(pl.Float64),
            cumulative_price=pl.lit(None).cast(pl.Float64),
            administered_price=pl.lit(None).cast(pl.Float64),
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
        value=value,
        metadata={"dagster/column_lineage": COLUMN_LINEAGE},
    )


@asset(
    key_prefix=KEY_PREFIX,
    group_name=GROUP_NAME,
    description="Silver gas market price fact.",
    ins={
        "int037b": AssetIn(key=INT037B_KEY),
        "int037c": AssetIn(key=INT037C_KEY),
        "int039b": AssetIn(key=INT039B_KEY),
        "int041": AssetIn(key=INT041_KEY),
        "int042": AssetIn(key=INT042_KEY),
        "int199": AssetIn(key=INT199_KEY),
        "int310_v1": AssetIn(key=INT310_V1_KEY),
        "int310_v4": AssetIn(key=INT310_V4_KEY),
        "int235": AssetIn(key=INT235_KEY),
    },
    io_manager_key="aemo_parquet_overwrite_io_manager",
    metadata={
        "dagster/table_name": f"silver.{DOMAIN}.{TABLE_NAME}",
        "dagster/uri": f"s3://{AEMO_BUCKET}/{'/'.join(KEY_PREFIX)}/{TABLE_NAME}",
        "dagster/column_schema": get_metadata_schema(SCHEMA, DESCRIPTIONS),
        "grain": GRAIN,
        "surrogate_key_sources": SURROGATE_KEY_SOURCES,
        "source_tables": SOURCE_TABLES,
    },
    kinds={"table", "parquet"},
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=60,
        backoff=Backoff.EXPONENTIAL,
        jitter=Jitter.PLUS_MINUS,
    ),
    automation_condition=AutomationCondition.any_deps_updated()
    & ~AutomationCondition.in_progress()
    & ~AutomationCondition.any_deps_missing(),
)
def silver_gas_fact_market_price(
    int037b: LazyFrame,
    int037c: LazyFrame,
    int039b: LazyFrame,
    int041: LazyFrame,
    int042: LazyFrame,
    int199: LazyFrame,
    int310_v1: LazyFrame,
    int310_v4: LazyFrame,
    int235: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_market_prices(
            int037b,
            int037c,
            int039b,
            int041,
            int042,
            int199,
            int310_v1,
            int310_v4,
            int235,
        )
    )


@asset_check(
    asset=silver_gas_fact_market_price,
    name="check_required_fields",
    description="Check required fact fields are not null.",
)
def silver_gas_fact_market_price_required_fields(
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


silver_gas_fact_market_price_duplicate_row_check = duplicate_row_check_factory(
    assets_definition=silver_gas_fact_market_price,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
    description="Check that surrogate_key is unique.",
)

silver_gas_fact_market_price_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_fact_market_price,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)

silver_gas_fact_market_price_schema_drift_check = schema_drift_check_factory(
    schema=SCHEMA,
    assets_definition=silver_gas_fact_market_price,
    check_name="check_schema_drift",
    description="Check for schema drift against the declared asset schema.",
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_market_price],
        asset_checks=[
            silver_gas_fact_market_price_duplicate_row_check,
            silver_gas_fact_market_price_schema_check,
            silver_gas_fact_market_price_schema_drift_check,
            silver_gas_fact_market_price_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_market_price_sensor",
                target=[silver_gas_fact_market_price.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
