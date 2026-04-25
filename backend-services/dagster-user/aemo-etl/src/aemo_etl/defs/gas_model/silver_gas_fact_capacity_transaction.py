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
TABLE_NAME = "silver_gas_fact_capacity_transaction"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific capacity or LNG transaction"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "transaction_type",
    "transaction_date",
    "source_location_id",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.gbb.silver_gasbb_short_term_transactions",
    "silver.gbb.silver_gasbb_short_term_swap_transactions",
    "silver.gbb.silver_gasbb_gsh_gas_trades",
    "silver.gbb.silver_gasbb_lng_transactions",
    "silver.gbb.silver_gasbb_lng_shipments",
]
SOURCE_SYSTEM = "GBB"
SHORT_KEY = AssetKey(["silver", "gbb", "silver_gasbb_short_term_transactions"])
SWAP_KEY = AssetKey(["silver", "gbb", "silver_gasbb_short_term_swap_transactions"])
GSH_KEY = AssetKey(["silver", "gbb", "silver_gasbb_gsh_gas_trades"])
LNG_TX_KEY = AssetKey(["silver", "gbb", "silver_gasbb_lng_transactions"])
LNG_SHIP_KEY = AssetKey(["silver", "gbb", "silver_gasbb_lng_shipments"])
_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=key, column_name="surrogate_key")
    for key in [SHORT_KEY, SWAP_KEY, GSH_KEY, LNG_TX_KEY, LNG_SHIP_KEY]
]
COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "transaction_type": pl.String,
    "transaction_date": pl.Date,
    "supply_start_date": pl.Date,
    "supply_end_date": pl.Date,
    "source_location_id": pl.String,
    "source_facility_id": pl.String,
    "quantity_tj": pl.Float64,
    "quantity_gj": pl.Float64,
    "volume_pj": pl.Float64,
    "price": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}
DESCRIPTIONS = {column: column.replace("_", " ") for column in SCHEMA}
REQUIRED_COLUMNS = [
    "surrogate_key",
    "source_system",
    "source_table",
    "transaction_type",
]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _short_rows(df: LazyFrame, source_table: str) -> LazyFrame:
    return df.filter(pl.col("TransactionType").is_not_null()).select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([source_table]).cast(pl.List(pl.String)),
        source_table=pl.lit(source_table),
        transaction_type=pl.col("TransactionType").cast(pl.String),
        transaction_date=_parse_datetime("SupplyPeriodStart").dt.date(),
        supply_start_date=_parse_datetime("SupplyPeriodStart").dt.date(),
        supply_end_date=_parse_datetime("SupplyPeriodEnd").dt.date(),
        source_location_id=pl.col("State").cast(pl.String),
        source_facility_id=pl.lit(None).cast(pl.String),
        quantity_tj=pl.col("Quantity (TJ)").cast(pl.Float64),
        quantity_gj=pl.col("Quantity (TJ)").cast(pl.Float64) * 1000,
        volume_pj=pl.lit(None).cast(pl.Float64),
        price=pl.col("VolumeWeightedPrice ($)").cast(pl.Float64),
        source_last_updated=pl.col("SupplyPeriodEnd").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("SupplyPeriodEnd"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _select_capacity_transactions(
    short: LazyFrame,
    swap: LazyFrame,
    gsh: LazyFrame,
    lng_transactions: LazyFrame,
    lng_shipments: LazyFrame,
) -> LazyFrame:
    rows = [
        _short_rows(short, SOURCE_TABLES[0]),
        _short_rows(swap, SOURCE_TABLES[1]),
        gsh.filter(pl.col("TYPE").is_not_null()).select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[2]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[2]),
            transaction_type=pl.col("TYPE").cast(pl.String),
            transaction_date=_parse_datetime("TRADE_DATE").dt.date(),
            supply_start_date=_parse_datetime("START_DATE").dt.date(),
            supply_end_date=_parse_datetime("END_DATE").dt.date(),
            source_location_id=pl.col("LOCATION").cast(pl.String),
            source_facility_id=pl.lit(None).cast(pl.String),
            quantity_tj=pl.col("DAILY_QTY_GJ").cast(pl.Float64) / 1000,
            quantity_gj=pl.col("DAILY_QTY_GJ").cast(pl.Float64),
            volume_pj=pl.lit(None).cast(pl.Float64),
            price=pl.col("TRADE_PRICE").cast(pl.Float64),
            source_last_updated=pl.col("END_DATE").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("END_DATE"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
        ),
        lng_transactions.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[3]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[3]),
            transaction_type=pl.lit("lng_transaction"),
            transaction_date=_parse_datetime("TransactionMonth").dt.date(),
            supply_start_date=_parse_datetime("SupplyStartDate").dt.date(),
            supply_end_date=_parse_datetime("SupplyEndDate").dt.date(),
            source_location_id=pl.lit(None).cast(pl.String),
            source_facility_id=pl.lit(None).cast(pl.String),
            quantity_tj=pl.lit(None).cast(pl.Float64),
            quantity_gj=pl.lit(None).cast(pl.Float64),
            volume_pj=pl.col("VolumePJ").cast(pl.Float64),
            price=pl.col("VolWeightPrice").cast(pl.Float64),
            source_last_updated=pl.col("SupplyEndDate").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("SupplyEndDate"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
        ),
        lng_shipments.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[4]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[4]),
            transaction_type=pl.lit("lng_shipment"),
            transaction_date=_parse_datetime("ShipmentDate").dt.date(),
            supply_start_date=_parse_datetime("ShipmentDate").dt.date(),
            supply_end_date=_parse_datetime("ShipmentDate").dt.date(),
            source_location_id=pl.lit(None).cast(pl.String),
            source_facility_id=pl.col("FacilityId").cast(pl.String),
            quantity_tj=pl.lit(None).cast(pl.Float64),
            quantity_gj=pl.lit(None).cast(pl.Float64),
            volume_pj=pl.col("VolumePJ").cast(pl.Float64),
            price=pl.lit(None).cast(pl.Float64),
            source_last_updated=pl.col("VersionDateTime").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("VersionDateTime"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
        ),
    ]
    return (
        pl.concat(rows, how="diagonal_relaxed")
        .with_columns(surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES))
        .select(list(SCHEMA))
    )


def _materialize_result(value: LazyFrame) -> MaterializeResult[LazyFrame]:
    return MaterializeResult(
        value=value, metadata={"dagster/column_lineage": COLUMN_LINEAGE}
    )


@asset(
    key_prefix=KEY_PREFIX,
    group_name=GROUP_NAME,
    description="Silver gas capacity transaction fact.",
    ins={
        "short": AssetIn(key=SHORT_KEY),
        "swap": AssetIn(key=SWAP_KEY),
        "gsh": AssetIn(key=GSH_KEY),
        "lng_transactions": AssetIn(key=LNG_TX_KEY),
        "lng_shipments": AssetIn(key=LNG_SHIP_KEY),
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
def silver_gas_fact_capacity_transaction(
    short: LazyFrame,
    swap: LazyFrame,
    gsh: LazyFrame,
    lng_transactions: LazyFrame,
    lng_shipments: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_capacity_transactions(short, swap, gsh, lng_transactions, lng_shipments)
    )


@asset_check(asset=silver_gas_fact_capacity_transaction, name="check_required_fields")
def silver_gas_fact_capacity_transaction_required_fields(
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


silver_gas_fact_capacity_transaction_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_capacity_transaction,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_capacity_transaction_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_capacity_transaction, check_name="check_schema_matches"
)
silver_gas_fact_capacity_transaction_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_capacity_transaction, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_capacity_transaction],
        asset_checks=[
            silver_gas_fact_capacity_transaction_duplicate_row_check,
            silver_gas_fact_capacity_transaction_schema_check,
            silver_gas_fact_capacity_transaction_schema_drift_check,
            silver_gas_fact_capacity_transaction_required_fields,
        ],
    )
