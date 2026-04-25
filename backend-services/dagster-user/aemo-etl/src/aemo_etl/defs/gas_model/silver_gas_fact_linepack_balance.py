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
TABLE_NAME = "silver_gas_fact_linepack_balance"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific linepack balance observation"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "gas_date",
    "linepack_type",
    "source_linepack_id",
    "gas_interval",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int089_v4_linepack_balance_1",
    "silver.vicgas.silver_int152_v4_sched_min_qty_linepack_1",
    "silver.vicgas.silver_int257_v4_linepack_with_zones_1",
]
SOURCE_SYSTEM = "VICGAS"
INT089_KEY = AssetKey(["silver", "vicgas", "silver_int089_v4_linepack_balance_1"])
INT152_KEY = AssetKey(["silver", "vicgas", "silver_int152_v4_sched_min_qty_linepack_1"])
INT257_KEY = AssetKey(["silver", "vicgas", "silver_int257_v4_linepack_with_zones_1"])

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT089_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT152_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT257_KEY, column_name="surrogate_key"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
        "quantity": [TableColumnDep(asset_key=INT152_KEY, column_name="quantity")],
        "amount_gst_ex": [
            TableColumnDep(asset_key=INT089_KEY, column_name="linepack_acct_bal_gst_ex")
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
    "linepack_type": pl.String,
    "source_linepack_id": pl.String,
    "source_zone_id": pl.String,
    "zone_name": pl.String,
    "gas_interval": pl.String,
    "quantity": pl.Float64,
    "amount_gst_ex": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {column: column.replace("_", " ") for column in SCHEMA}
REQUIRED_COLUMNS = ["surrogate_key", "source_system", "source_table"]


def _parse_datetime(column: str) -> pl.Expr:
    source = pl.col(column).cast(pl.String)
    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%d %b %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %b %Y", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y", strict=False),
    )


def _select_linepack_balance(
    int089: LazyFrame, int152: LazyFrame, int257: LazyFrame
) -> LazyFrame:
    rows = [
        int089.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[0]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[0]),
            gas_date=_parse_datetime("gas_date").dt.date(),
            linepack_type=pl.lit("account_balance"),
            source_linepack_id=pl.lit(None).cast(pl.String),
            source_zone_id=pl.lit(None).cast(pl.String),
            zone_name=pl.lit(None).cast(pl.String),
            gas_interval=pl.lit(None).cast(pl.String),
            quantity=pl.lit(None).cast(pl.Float64),
            amount_gst_ex=pl.col("linepack_acct_bal_gst_ex").cast(pl.Float64),
            source_last_updated=pl.col("current_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("current_date"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
        ),
        int152.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[1]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[1]),
            gas_date=_parse_datetime("gas_date").dt.date(),
            linepack_type=pl.col("type").cast(pl.String),
            source_linepack_id=pl.col("linepack_id").cast(pl.String),
            source_zone_id=pl.col("linepack_zone_id").cast(pl.String),
            zone_name=pl.col("linepack_zone_name").cast(pl.String),
            gas_interval=pl.col("ti").cast(pl.String),
            quantity=pl.col("quantity").cast(pl.Float64),
            amount_gst_ex=pl.lit(None).cast(pl.Float64),
            source_last_updated=pl.col("current_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("current_date"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
        ),
        int257.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[2]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[2]),
            gas_date=_parse_datetime("last_mod_date").dt.date(),
            linepack_type=pl.lit("zone_reference"),
            source_linepack_id=pl.col("linepack_zone_id").cast(pl.String),
            source_zone_id=pl.col("linepack_zone_id").cast(pl.String),
            zone_name=pl.col("linepack_zone_name").cast(pl.String),
            gas_interval=pl.lit(None).cast(pl.String),
            quantity=pl.lit(None).cast(pl.Float64),
            amount_gst_ex=pl.lit(None).cast(pl.Float64),
            source_last_updated=pl.col("last_mod_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("last_mod_date"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
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
    description="Silver gas linepack balance fact.",
    ins={
        "int089": AssetIn(key=INT089_KEY),
        "int152": AssetIn(key=INT152_KEY),
        "int257": AssetIn(key=INT257_KEY),
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
def silver_gas_fact_linepack_balance(
    int089: LazyFrame, int152: LazyFrame, int257: LazyFrame
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(_select_linepack_balance(int089, int152, int257))


@asset_check(asset=silver_gas_fact_linepack_balance, name="check_required_fields")
def silver_gas_fact_linepack_balance_required_fields(
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


silver_gas_fact_linepack_balance_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_linepack_balance,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_linepack_balance_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_linepack_balance, check_name="check_schema_matches"
)
silver_gas_fact_linepack_balance_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_linepack_balance, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_linepack_balance],
        asset_checks=[
            silver_gas_fact_linepack_balance_duplicate_row_check,
            silver_gas_fact_linepack_balance_schema_check,
            silver_gas_fact_linepack_balance_schema_drift_check,
            silver_gas_fact_linepack_balance_required_fields,
        ],
    )
