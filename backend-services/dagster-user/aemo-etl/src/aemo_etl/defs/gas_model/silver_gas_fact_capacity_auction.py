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
from aemo_etl.factories.checks import (
    duplicate_row_check_factory,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.utils import get_metadata_schema, get_surrogate_key

DOMAIN = "gas_model"
TABLE_NAME = "silver_gas_fact_capacity_auction"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific capacity auction observation"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "auction_id",
    "source_zone_id",
    "capacity_period",
    "auction_metric",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int339_v4_ccauction_bid_stack_1",
    "silver.vicgas.silver_int342_v4_ccauction_sys_capability_1",
    "silver.vicgas.silver_int343_v4_ccauction_auction_qty_1",
    "silver.vicgas.silver_int345_v4_ccauction_zone_1",
    "silver.vicgas.silver_int348_v4_cctransfer_1",
    "silver.vicgas.silver_int351_v4_ccregistry_summary_1",
    "silver.vicgas.silver_int353_v4_ccauction_qty_won_1",
    "silver.vicgas.silver_int353_v4_ccauction_qty_won_all_1",
    "silver.vicgas.silver_int381_v4_tie_breaking_event_1",
]
SOURCE_SYSTEM = "VICGAS"
KEYS = [
    AssetKey(["silver", "vicgas", table.removeprefix("silver.vicgas.")])
    for table in SOURCE_TABLES
]
(
    INT339_KEY,
    INT342_KEY,
    INT343_KEY,
    INT345_KEY,
    INT348_KEY,
    INT351_KEY,
    INT353_KEY,
    INT353_ALL_KEY,
    INT381_KEY,
) = KEYS
_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=key, column_name="surrogate_key") for key in KEYS
]
COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "auction_id": pl.String,
    "auction_date": pl.Date,
    "source_zone_id": pl.String,
    "zone_name": pl.String,
    "zone_type": pl.String,
    "capacity_period": pl.String,
    "start_date": pl.Date,
    "end_date": pl.Date,
    "auction_metric": pl.String,
    "quantity_gj": pl.Float64,
    "price": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}
DESCRIPTIONS = {column: column.replace("_", " ") for column in SCHEMA}
REQUIRED_COLUMNS = ["surrogate_key", "source_system", "source_table", "auction_metric"]


def _parse_datetime(column: str) -> pl.Expr:
    source = pl.col(column).cast(pl.String)
    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%d %b %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %b %Y", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y", strict=False),
    )


def _base(source_table: str, updated_column: str = "current_date") -> list[pl.Expr]:
    return [
        pl.lit(SOURCE_SYSTEM).alias("source_system"),
        pl.lit([source_table]).cast(pl.List(pl.String)).alias("source_tables"),
        pl.lit(source_table).alias("source_table"),
        pl.col(updated_column).cast(pl.String).alias("source_last_updated"),
        _parse_datetime(updated_column).alias("source_last_updated_timestamp"),
        pl.col("surrogate_key").cast(pl.String).alias("source_surrogate_key"),
        pl.col("source_file").cast(pl.String).alias("source_file"),
        pl.col("ingested_timestamp").alias("ingested_timestamp"),
    ]


def _select_capacity_auction(
    int339: LazyFrame,
    int342: LazyFrame,
    int343: LazyFrame,
    int345: LazyFrame,
    int348: LazyFrame,
    int351: LazyFrame,
    int353: LazyFrame,
    int353_all: LazyFrame,
    int381: LazyFrame,
) -> LazyFrame:
    rows = [
        int339.select(
            *_base(SOURCE_TABLES[0]),
            auction_id=pl.col("auction_id").cast(pl.String),
            auction_date=_parse_datetime("auction_date").dt.date(),
            source_zone_id=pl.col("zone_id").cast(pl.String),
            zone_name=pl.col("zone_name").cast(pl.String),
            zone_type=pl.lit(None).cast(pl.String),
            capacity_period=pl.col("start_period").cast(pl.String),
            start_date=_parse_datetime("start_period").dt.date(),
            end_date=_parse_datetime("end_period").dt.date(),
            auction_metric=pl.lit("bid_stack"),
            quantity_gj=pl.col("bid_quantity_gj").cast(pl.Float64),
            price=pl.col("bid_price").cast(pl.Float64),
        ),
        int342.select(
            *_base(SOURCE_TABLES[1]),
            auction_id=pl.lit(None).cast(pl.String),
            auction_date=pl.lit(None).cast(pl.Date),
            source_zone_id=pl.col("zone_id").cast(pl.String),
            zone_name=pl.col("zone_name").cast(pl.String),
            zone_type=pl.col("zone_type").cast(pl.String),
            capacity_period=pl.col("capacity_period").cast(pl.String),
            start_date=pl.lit(None).cast(pl.Date),
            end_date=pl.lit(None).cast(pl.Date),
            auction_metric=pl.lit("system_capability"),
            quantity_gj=pl.col("zone_capacity_gj").cast(pl.Float64),
            price=pl.lit(None).cast(pl.Float64),
        ),
        int343.select(
            *_base(SOURCE_TABLES[2]),
            auction_id=pl.col("auction_id").cast(pl.String),
            auction_date=_parse_datetime("auction_date").dt.date(),
            source_zone_id=pl.col("zone_id").cast(pl.String),
            zone_name=pl.col("zone_name").cast(pl.String),
            zone_type=pl.col("zone_type").cast(pl.String),
            capacity_period=pl.col("capacity_period").cast(pl.String),
            start_date=pl.lit(None).cast(pl.Date),
            end_date=pl.lit(None).cast(pl.Date),
            auction_metric=pl.lit("available_capacity"),
            quantity_gj=pl.col("available_capacity_gj").cast(pl.Float64),
            price=pl.lit(None).cast(pl.Float64),
        ),
        int345.select(
            *_base(SOURCE_TABLES[3]),
            auction_id=pl.lit(None).cast(pl.String),
            auction_date=pl.lit(None).cast(pl.Date),
            source_zone_id=pl.col("zone_id").cast(pl.String),
            zone_name=pl.col("zone_name").cast(pl.String),
            zone_type=pl.col("zone_type").cast(pl.String),
            capacity_period=pl.lit(None).cast(pl.String),
            start_date=_parse_datetime("from_date").dt.date(),
            end_date=_parse_datetime("to_date").dt.date(),
            auction_metric=pl.lit("zone_reference"),
            quantity_gj=pl.lit(None).cast(pl.Float64),
            price=pl.lit(None).cast(pl.Float64),
        ),
        int348.select(
            *_base(SOURCE_TABLES[4]),
            auction_id=pl.col("transfer_id").cast(pl.String),
            auction_date=pl.lit(None).cast(pl.Date),
            source_zone_id=pl.col("zone_id").cast(pl.String),
            zone_name=pl.col("zone_name").cast(pl.String),
            zone_type=pl.lit(None).cast(pl.String),
            capacity_period=pl.lit(None).cast(pl.String),
            start_date=_parse_datetime("start_date").dt.date(),
            end_date=_parse_datetime("end_date").dt.date(),
            auction_metric=pl.lit("transfer"),
            quantity_gj=pl.col("transferred_qty_gj").cast(pl.Float64),
            price=pl.lit(None).cast(pl.Float64),
        ),
        int351.select(
            *_base(SOURCE_TABLES[5]),
            auction_id=pl.lit(None).cast(pl.String),
            auction_date=pl.lit(None).cast(pl.Date),
            source_zone_id=pl.col("zone_id").cast(pl.String),
            zone_name=pl.col("zone_name").cast(pl.String),
            zone_type=pl.col("zone_type").cast(pl.String),
            capacity_period=pl.col("source").cast(pl.String),
            start_date=_parse_datetime("start_date").dt.date(),
            end_date=_parse_datetime("end_date").dt.date(),
            auction_metric=pl.lit("registry_holding"),
            quantity_gj=pl.col("total_holding_gj").cast(pl.Float64),
            price=pl.lit(None).cast(pl.Float64),
        ),
        int353.select(
            *_base(SOURCE_TABLES[6]),
            auction_id=pl.col("auction_id").cast(pl.String),
            auction_date=_parse_datetime("auction_date").dt.date(),
            source_zone_id=pl.col("zone_id").cast(pl.String),
            zone_name=pl.col("zone_name").cast(pl.String),
            zone_type=pl.col("zone_type").cast(pl.String),
            capacity_period=pl.col("cc_period").cast(pl.String),
            start_date=_parse_datetime("start_date").dt.date(),
            end_date=_parse_datetime("end_date").dt.date(),
            auction_metric=pl.lit("quantity_won"),
            quantity_gj=pl.col("quantities_won_gj").cast(pl.Float64),
            price=pl.col("clearing_price").cast(pl.Float64),
        ),
        int353_all.select(
            *_base(SOURCE_TABLES[7]),
            auction_id=pl.col("auction_id").cast(pl.String),
            auction_date=_parse_datetime("auction_date").dt.date(),
            source_zone_id=pl.col("zone_id").cast(pl.String),
            zone_name=pl.col("zone_name").cast(pl.String),
            zone_type=pl.col("zone_type").cast(pl.String),
            capacity_period=pl.col("cc_period").cast(pl.String),
            start_date=_parse_datetime("start_date").dt.date(),
            end_date=_parse_datetime("end_date").dt.date(),
            auction_metric=pl.lit("quantity_won_all"),
            quantity_gj=pl.col("quantities_won_gj").cast(pl.Float64),
            price=pl.col("clearing_price").cast(pl.Float64),
        ),
        int381.select(
            *_base(SOURCE_TABLES[8]),
            auction_id=pl.col("transmission_id").cast(pl.String),
            auction_date=_parse_datetime("gas_date").dt.date(),
            source_zone_id=pl.col("mirn").cast(pl.String),
            zone_name=pl.col("mirn").cast(pl.String),
            zone_type=pl.lit(None).cast(pl.String),
            capacity_period=pl.col("schedule_interval").cast(pl.String),
            start_date=_parse_datetime("gas_date").dt.date(),
            end_date=_parse_datetime("gas_date").dt.date(),
            auction_metric=pl.col("tie_breaking_event").cast(pl.String),
            quantity_gj=pl.col("gas_not_scheduled").cast(pl.Float64),
            price=pl.lit(None).cast(pl.Float64),
        ),
    ]
    return (
        pl.concat(rows, how="diagonal_relaxed")
        .with_columns(
            date_key=get_surrogate_key(["auction_date"]),
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
    description="Silver gas capacity auction fact.",
    ins={
        "int339": AssetIn(key=INT339_KEY),
        "int342": AssetIn(key=INT342_KEY),
        "int343": AssetIn(key=INT343_KEY),
        "int345": AssetIn(key=INT345_KEY),
        "int348": AssetIn(key=INT348_KEY),
        "int351": AssetIn(key=INT351_KEY),
        "int353": AssetIn(key=INT353_KEY),
        "int353_all": AssetIn(key=INT353_ALL_KEY),
        "int381": AssetIn(key=INT381_KEY),
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
    automation_condition=AutomationCondition.any_deps_updated()
    & ~AutomationCondition.in_progress()
    & ~AutomationCondition.any_deps_missing(),
)
def silver_gas_fact_capacity_auction(
    int339: LazyFrame,
    int342: LazyFrame,
    int343: LazyFrame,
    int345: LazyFrame,
    int348: LazyFrame,
    int351: LazyFrame,
    int353: LazyFrame,
    int353_all: LazyFrame,
    int381: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_capacity_auction(
            int339, int342, int343, int345, int348, int351, int353, int353_all, int381
        )
    )


@asset_check(asset=silver_gas_fact_capacity_auction, name="check_required_fields")
def silver_gas_fact_capacity_auction_required_fields(
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


silver_gas_fact_capacity_auction_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_capacity_auction,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_capacity_auction_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_capacity_auction, check_name="check_schema_matches"
)
silver_gas_fact_capacity_auction_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_capacity_auction, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_capacity_auction],
        asset_checks=[
            silver_gas_fact_capacity_auction_duplicate_row_check,
            silver_gas_fact_capacity_auction_schema_check,
            silver_gas_fact_capacity_auction_schema_drift_check,
            silver_gas_fact_capacity_auction_required_fields,
        ],
    )
