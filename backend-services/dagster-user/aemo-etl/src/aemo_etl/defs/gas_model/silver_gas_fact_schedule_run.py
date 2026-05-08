"""Dagster definitions for the silver gas schedule run fact asset."""

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
from aemo_etl.factories.checks import (
    duplicate_row_check_factory,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.utils import get_metadata_schema, get_surrogate_key

DOMAIN = "gas_model"
TABLE_NAME = "silver_gas_fact_schedule_run"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source schedule run"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "transmission_document_id",
    "transmission_id",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int108_v4_scheduled_run_log_7_1",
    "silver.sttm.silver_int668_v1_schedule_log_rpt_1",
]
SOURCE_SYSTEM = "VICGAS"
STTM_SOURCE_SYSTEM = "STTM"
INT108_KEY = AssetKey(["silver", "vicgas", "silver_int108_v4_scheduled_run_log_7_1"])
INT668_KEY = AssetKey(["silver", "sttm", "silver_int668_v1_schedule_log_rpt_1"])

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": [
            TableColumnDep(asset_key=INT108_KEY, column_name="surrogate_key"),
            TableColumnDep(asset_key=INT668_KEY, column_name="surrogate_key"),
        ],
        "source_surrogate_key": [
            TableColumnDep(asset_key=INT108_KEY, column_name="surrogate_key"),
            TableColumnDep(asset_key=INT668_KEY, column_name="surrogate_key"),
        ],
        "transmission_id": [
            TableColumnDep(asset_key=INT108_KEY, column_name="transmission_id"),
            TableColumnDep(asset_key=INT668_KEY, column_name="schedule_identifier"),
        ],
        "transmission_document_id": [
            TableColumnDep(
                asset_key=INT108_KEY, column_name="transmission_document_id"
            ),
            TableColumnDep(asset_key=INT668_KEY, column_name="schedule_identifier"),
        ],
        "objective_function_value": [
            TableColumnDep(asset_key=INT108_KEY, column_name="objective_function_value")
        ],
        "gas_start_timestamp": [
            TableColumnDep(asset_key=INT108_KEY, column_name="gas_start_datetime"),
            TableColumnDep(asset_key=INT668_KEY, column_name="gas_date"),
        ],
        "bid_cutoff_timestamp": [
            TableColumnDep(asset_key=INT108_KEY, column_name="bid_cutoff_datetime"),
            TableColumnDep(
                asset_key=INT668_KEY, column_name="bid_offer_cut_off_datetime"
            ),
        ],
        "creation_timestamp": [
            TableColumnDep(asset_key=INT108_KEY, column_name="creation_datetime"),
            TableColumnDep(asset_key=INT668_KEY, column_name="creation_datetime"),
        ],
        "approval_timestamp": [
            TableColumnDep(asset_key=INT108_KEY, column_name="approval_datetime"),
            TableColumnDep(asset_key=INT668_KEY, column_name="approval_datetime"),
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
    "transmission_id": pl.String,
    "transmission_document_id": pl.String,
    "transmission_group_id": pl.String,
    "schedule_type_id": pl.String,
    "forecast_demand_version": pl.String,
    "demand_type_id": pl.String,
    "objective_function_value": pl.Float64,
    "gas_start_timestamp": pl.Datetime("us"),
    "bid_cutoff_timestamp": pl.Datetime("us"),
    "creation_timestamp": pl.Datetime("us"),
    "approval_timestamp": pl.Datetime("us"),
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
    "transmission_document_id",
]


def _parse_datetime(column: str) -> pl.Expr:
    source = pl.col(column).cast(pl.String)
    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%d %b %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %b %Y", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y", strict=False),
    )


def _vicgas_schedule_runs(int108: LazyFrame) -> LazyFrame:
    return int108.with_columns(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[0]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[0]),
        gas_date=_parse_datetime("gas_start_datetime").dt.date(),
        transmission_id=pl.col("transmission_id").cast(pl.String),
        transmission_document_id=pl.col("transmission_document_id").cast(pl.String),
        transmission_group_id=pl.col("transmission_group_id").cast(pl.String),
        schedule_type_id=pl.col("schedule_type_id").cast(pl.String),
        forecast_demand_version=pl.col("forecast_demand_version").cast(pl.String),
        demand_type_id=pl.col("demand_type_id").cast(pl.String),
        objective_function_value=pl.col("objective_function_value").cast(pl.Float64),
        gas_start_timestamp=_parse_datetime("gas_start_datetime"),
        bid_cutoff_timestamp=_parse_datetime("bid_cutoff_datetime"),
        creation_timestamp=_parse_datetime("creation_datetime"),
        approval_timestamp=_parse_datetime("approval_datetime"),
        source_last_updated=pl.col("current_date").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("current_date"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
    )


def _sttm_schedule_runs(int668: LazyFrame) -> LazyFrame:
    return int668.with_columns(
        source_system=pl.lit(STTM_SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[1]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[1]),
        gas_date=_parse_datetime("gas_date").dt.date(),
        transmission_id=pl.col("schedule_identifier").cast(pl.String),
        transmission_document_id=pl.col("schedule_identifier").cast(pl.String),
        transmission_group_id=pl.col("hub_identifier").cast(pl.String),
        schedule_type_id=pl.col("schedule_type").cast(pl.String),
        forecast_demand_version=pl.col("schedule_day").cast(pl.String),
        demand_type_id=pl.lit(None).cast(pl.String),
        objective_function_value=pl.lit(None).cast(pl.Float64),
        gas_start_timestamp=_parse_datetime("gas_date"),
        bid_cutoff_timestamp=_parse_datetime("bid_offer_cut_off_datetime"),
        creation_timestamp=_parse_datetime("creation_datetime"),
        approval_timestamp=_parse_datetime("approval_datetime"),
        source_last_updated=pl.col("report_datetime").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("report_datetime"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
    )


def _select_schedule_runs(int108: LazyFrame, int668: LazyFrame) -> LazyFrame:
    return (
        pl.concat(
            [_vicgas_schedule_runs(int108), _sttm_schedule_runs(int668)],
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
    description="Silver gas schedule run fact.",
    ins={"int108": AssetIn(key=INT108_KEY), "int668": AssetIn(key=INT668_KEY)},
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
def silver_gas_fact_schedule_run(
    int108: LazyFrame, int668: LazyFrame
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver gas schedule run fact asset."""
    return _materialize_result(_select_schedule_runs(int108, int668))


@asset_check(asset=silver_gas_fact_schedule_run, name="check_required_fields")
def silver_gas_fact_schedule_run_required_fields(
    input_df: LazyFrame,
) -> AssetCheckResult:
    """Validate required fields for the silver gas schedule run fact asset."""
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


silver_gas_fact_schedule_run_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_schedule_run,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_schedule_run_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_schedule_run, check_name="check_schema_matches"
)
silver_gas_fact_schedule_run_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_schedule_run, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver gas schedule run fact asset."""
    return Definitions(
        assets=[silver_gas_fact_schedule_run],
        asset_checks=[
            silver_gas_fact_schedule_run_duplicate_row_check,
            silver_gas_fact_schedule_run_schema_check,
            silver_gas_fact_schedule_run_schema_drift_check,
            silver_gas_fact_schedule_run_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_schedule_run_sensor",
                target=[silver_gas_fact_schedule_run.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
