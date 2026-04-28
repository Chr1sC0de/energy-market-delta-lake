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
from aemo_etl.defs.gas_model._parsing import parse_gas_datetime, parse_yes_no_bool
from aemo_etl.factories.checks import (
    duplicate_row_check_factory,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.utils import get_metadata_schema, get_surrogate_key

DOMAIN = "gas_model"
TABLE_NAME = "silver_gas_fact_system_notice"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific system notice"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "source_notice_id",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int029a_v4_system_notices_1",
    "silver.vicgas.silver_int929a_v4_system_notices_1",
]
SOURCE_SYSTEM = "VICGAS"
INT029A_KEY = AssetKey(["silver", "vicgas", "silver_int029a_v4_system_notices_1"])
INT929A_KEY = AssetKey(["silver", "vicgas", "silver_int929a_v4_system_notices_1"])
_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT029A_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT929A_KEY, column_name="surrogate_key"),
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
    "source_notice_id": pl.String,
    "critical_notice": pl.Boolean,
    "notice_start_timestamp": pl.Datetime("us"),
    "notice_end_timestamp": pl.Datetime("us"),
    "system_message": pl.String,
    "system_email_message": pl.String,
    "url_path": pl.String,
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
    "source_notice_id",
]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _notice_rows(df: LazyFrame, source_table: str) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([source_table]).cast(pl.List(pl.String)),
        source_table=pl.lit(source_table),
        source_notice_id=pl.col("system_wide_notice_id").cast(pl.String),
        critical_notice=parse_yes_no_bool("critical_notice_flag"),
        notice_start_timestamp=_parse_datetime("notice_start_date"),
        notice_end_timestamp=_parse_datetime("notice_end_date"),
        system_message=pl.col("system_message").cast(pl.String),
        system_email_message=pl.col("system_email_message").cast(pl.String),
        url_path=pl.col("url_path").cast(pl.String),
        source_last_updated=pl.col("current_date").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("current_date"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _select_system_notices(int029a: LazyFrame, int929a: LazyFrame) -> LazyFrame:
    return (
        pl.concat(
            [
                _notice_rows(int029a, SOURCE_TABLES[0]),
                _notice_rows(int929a, SOURCE_TABLES[1]),
            ],
            how="diagonal_relaxed",
        )
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
    description="Silver gas system notice fact.",
    ins={"int029a": AssetIn(key=INT029A_KEY), "int929a": AssetIn(key=INT929A_KEY)},
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
def silver_gas_fact_system_notice(
    int029a: LazyFrame, int929a: LazyFrame
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(_select_system_notices(int029a, int929a))


@asset_check(asset=silver_gas_fact_system_notice, name="check_required_fields")
def silver_gas_fact_system_notice_required_fields(
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


silver_gas_fact_system_notice_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_system_notice,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_system_notice_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_system_notice, check_name="check_schema_matches"
)
silver_gas_fact_system_notice_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_system_notice, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_system_notice],
        asset_checks=[
            silver_gas_fact_system_notice_duplicate_row_check,
            silver_gas_fact_system_notice_schema_check,
            silver_gas_fact_system_notice_schema_drift_check,
            silver_gas_fact_system_notice_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_system_notice_sensor",
                target=[silver_gas_fact_system_notice.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
