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
TABLE_NAME = "silver_gas_fact_settlement_activity"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific settlement activity observation"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "gas_date",
    "settlement_version_id",
    "activity_type",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int117a_v4_est_ancillary_payments_1",
    "silver.vicgas.silver_int117b_v4_ancillary_payments_1",
    "silver.vicgas.silver_int138_v4_settlement_version_1",
    "silver.vicgas.silver_int312_v4_settlements_activity_1",
    "silver.vicgas.silver_int322a_v4_uplift_breakdown_sett_1",
    "silver.vicgas.silver_int322b_v4_uplift_breakdown_prud_1",
    "silver.vicgas.silver_int538_v4_settlement_versions_1",
    "silver.vicgas.silver_int583_v4_monthly_cumulative_imb_pos_1",
]
SOURCE_SYSTEM = "VICGAS"
KEYS = [
    AssetKey(["silver", "vicgas", table.removeprefix("silver.vicgas.")])
    for table in SOURCE_TABLES
]
(
    INT117A_KEY,
    INT117B_KEY,
    INT138_KEY,
    INT312_KEY,
    INT322A_KEY,
    INT322B_KEY,
    INT538_KEY,
    INT583_KEY,
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
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}
DESCRIPTIONS = {column: column.replace("_", " ") for column in SCHEMA}
REQUIRED_COLUMNS = ["surrogate_key", "source_system", "source_table", "activity_type"]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _simple_payment(
    df: LazyFrame,
    source_table: str,
    amount_column: str,
    activity_type: str,
    schedule_column: str,
    version_column: str | None = None,
) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([source_table]).cast(pl.List(pl.String)),
        source_table=pl.lit(source_table),
        gas_date=_parse_datetime("gas_date").dt.date(),
        settlement_version_id=pl.col(version_column).cast(pl.String)
        if version_column is not None
        else pl.lit(None).cast(pl.String),
        activity_type=pl.lit(activity_type),
        schedule_no=pl.col(schedule_column).cast(pl.String),
        network_name=pl.lit(None).cast(pl.String),
        participant_name=pl.lit(None).cast(pl.String),
        amount_gst_ex=pl.col(amount_column).cast(pl.Float64),
        quantity_gj=pl.lit(None).cast(pl.Float64),
        percentage=pl.lit(None).cast(pl.Float64),
        source_last_updated=pl.col("current_date").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("current_date"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _select_settlement_activity(
    int117a: LazyFrame,
    int117b: LazyFrame,
    int138: LazyFrame,
    int312: LazyFrame,
    int322a: LazyFrame,
    int322b: LazyFrame,
    int538: LazyFrame,
    int583: LazyFrame,
) -> LazyFrame:
    rows = [
        _simple_payment(
            int117a,
            SOURCE_TABLES[0],
            "est_ancillary_amt_gst_ex",
            "estimated_ancillary_payment",
            "schedule_no",
        ),
        _simple_payment(
            int117b,
            SOURCE_TABLES[1],
            "ancillary_amt_gst_ex",
            "ancillary_payment",
            "schedule_no",
            "ap_run_id",
        ),
        int138.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[2]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[2]),
            gas_date=_parse_datetime("version_from_date").dt.date(),
            settlement_version_id=pl.col("statement_version_id").cast(pl.String),
            activity_type=pl.col("settlement_cat_type").cast(pl.String),
            schedule_no=pl.lit(None).cast(pl.String),
            network_name=pl.lit(None).cast(pl.String),
            participant_name=pl.lit(None).cast(pl.String),
            amount_gst_ex=pl.lit(None).cast(pl.Float64),
            quantity_gj=pl.lit(None).cast(pl.Float64),
            percentage=pl.col("interest_rate").cast(pl.Float64),
            source_last_updated=pl.col("current_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("current_date"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
        ),
        int312.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[3]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[3]),
            gas_date=_parse_datetime("gas_date").dt.date(),
            settlement_version_id=pl.lit(None).cast(pl.String),
            activity_type=pl.lit("settlements_activity"),
            schedule_no=pl.lit(None).cast(pl.String),
            network_name=pl.lit(None).cast(pl.String),
            participant_name=pl.lit(None).cast(pl.String),
            amount_gst_ex=pl.col("total_uplift_amt").cast(pl.Float64),
            quantity_gj=pl.col("total_actual_wdl_gj").cast(pl.Float64),
            percentage=pl.col("uafg_28_days_pct").cast(pl.Float64),
            source_last_updated=pl.col("gas_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("gas_date"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
        ),
        _simple_payment(
            int322a,
            SOURCE_TABLES[4],
            "total_uplift_amt",
            "uplift_breakdown_settlement",
            "sched_no",
            "statement_version_id",
        ),
        _simple_payment(
            int322b,
            SOURCE_TABLES[5],
            "total_uplift_amt",
            "uplift_breakdown_prudential",
            "sched_no",
        ),
        int538.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[6]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[6]),
            gas_date=_parse_datetime("version_from_date").dt.date(),
            settlement_version_id=pl.col("version_id").cast(pl.String),
            activity_type=pl.col("extract_type").cast(pl.String),
            schedule_no=pl.lit(None).cast(pl.String),
            network_name=pl.col("network_name").cast(pl.String),
            participant_name=pl.lit(None).cast(pl.String),
            amount_gst_ex=pl.lit(None).cast(pl.Float64),
            quantity_gj=pl.lit(None).cast(pl.Float64),
            percentage=pl.lit(None).cast(pl.Float64),
            source_last_updated=pl.col("current_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("current_date"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
        ),
        int583.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[7]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[7]),
            gas_date=_parse_datetime("curr_cum_date").dt.date(),
            settlement_version_id=pl.col("version_id").cast(pl.String),
            activity_type=pl.concat_str(
                [
                    pl.lit("monthly_cumulative_imbalance_position_"),
                    pl.col("curr_cum_imb_position")
                    .cast(pl.String)
                    .str.to_lowercase()
                    .str.replace_all(r"\s+", "_"),
                ]
            ),
            schedule_no=pl.lit(None).cast(pl.String),
            network_name=pl.col("network_name").cast(pl.String),
            participant_name=pl.col("fro_name").cast(pl.String),
            amount_gst_ex=pl.lit(None).cast(pl.Float64),
            quantity_gj=pl.lit(None).cast(pl.Float64),
            percentage=pl.lit(None).cast(pl.Float64),
            source_last_updated=pl.col("current_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("current_date"),
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
    description="Silver gas settlement activity fact.",
    ins={
        "int117a": AssetIn(key=INT117A_KEY),
        "int117b": AssetIn(key=INT117B_KEY),
        "int138": AssetIn(key=INT138_KEY),
        "int312": AssetIn(key=INT312_KEY),
        "int322a": AssetIn(key=INT322A_KEY),
        "int322b": AssetIn(key=INT322B_KEY),
        "int538": AssetIn(key=INT538_KEY),
        "int583": AssetIn(key=INT583_KEY),
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
def silver_gas_fact_settlement_activity(
    int117a: LazyFrame,
    int117b: LazyFrame,
    int138: LazyFrame,
    int312: LazyFrame,
    int322a: LazyFrame,
    int322b: LazyFrame,
    int538: LazyFrame,
    int583: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_settlement_activity(
            int117a, int117b, int138, int312, int322a, int322b, int538, int583
        )
    )


@asset_check(asset=silver_gas_fact_settlement_activity, name="check_required_fields")
def silver_gas_fact_settlement_activity_required_fields(
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


silver_gas_fact_settlement_activity_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_settlement_activity,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_settlement_activity_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_settlement_activity, check_name="check_schema_matches"
)
silver_gas_fact_settlement_activity_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_settlement_activity, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_settlement_activity],
        asset_checks=[
            silver_gas_fact_settlement_activity_duplicate_row_check,
            silver_gas_fact_settlement_activity_schema_check,
            silver_gas_fact_settlement_activity_schema_drift_check,
            silver_gas_fact_settlement_activity_required_fields,
        ],
    )
