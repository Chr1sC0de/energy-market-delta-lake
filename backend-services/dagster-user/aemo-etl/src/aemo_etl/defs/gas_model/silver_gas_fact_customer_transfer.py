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
TABLE_NAME = "silver_gas_fact_customer_transfer"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per gas date and market code customer transfer summary"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "gas_date",
    "market_code",
    "source_surrogate_key",
]
SOURCE_TABLES = ["silver.vicgas.silver_int311_v5_customer_transfers_1"]
SOURCE_SYSTEM = "VICGAS"
INT311_KEY = AssetKey(["silver", "vicgas", "silver_int311_v5_customer_transfers_1"])
COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": [
            TableColumnDep(asset_key=INT311_KEY, column_name="surrogate_key")
        ]
    }
)

SCHEMA = {
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
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}
DESCRIPTIONS = {column: column.replace("_", " ") for column in SCHEMA}
REQUIRED_COLUMNS = [
    "surrogate_key",
    "source_system",
    "source_table",
    "gas_date",
    "market_code",
]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _select_customer_transfers(int311: LazyFrame) -> LazyFrame:
    return (
        int311.with_columns(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit(SOURCE_TABLES).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[0]),
            gas_date=_parse_datetime("gas_date").dt.date(),
            market_code=pl.col("market_code").cast(pl.String),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
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
    description="Silver gas customer transfer fact.",
    ins={"int311": AssetIn(key=INT311_KEY)},
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
def silver_gas_fact_customer_transfer(
    int311: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(_select_customer_transfers(int311))


@asset_check(asset=silver_gas_fact_customer_transfer, name="check_required_fields")
def silver_gas_fact_customer_transfer_required_fields(
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


silver_gas_fact_customer_transfer_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_customer_transfer,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_customer_transfer_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_customer_transfer, check_name="check_schema_matches"
)
silver_gas_fact_customer_transfer_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_customer_transfer, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_customer_transfer],
        asset_checks=[
            silver_gas_fact_customer_transfer_duplicate_row_check,
            silver_gas_fact_customer_transfer_schema_check,
            silver_gas_fact_customer_transfer_schema_drift_check,
            silver_gas_fact_customer_transfer_required_fields,
        ],
    )
