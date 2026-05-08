"""Dagster definitions for the silver gas scheduled quantity fact asset."""

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
TABLE_NAME = "silver_gas_fact_scheduled_quantity"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific scheduled quantity observation"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "gas_date",
    "quantity_type",
    "transmission_id",
    "source_point_id",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int050_v4_sched_withdrawals_1",
    "silver.vicgas.silver_int235_v4_sched_system_total_1",
    "silver.vicgas.silver_int291_v4_out_of_merit_order_gas_1",
    "silver.vicgas.silver_int316_v4_operational_gas_1",
    "silver.sttm.silver_int652_v1_ex_ante_schedule_quantity_rpt_1",
    "silver.sttm.silver_int655_v1_provisional_schedule_quantity_rpt_1",
]
SOURCE_SYSTEM = "VICGAS"
STTM_SOURCE_SYSTEM = "STTM"
INT050_KEY = AssetKey(["silver", "vicgas", "silver_int050_v4_sched_withdrawals_1"])
INT235_KEY = AssetKey(["silver", "vicgas", "silver_int235_v4_sched_system_total_1"])
INT291_KEY = AssetKey(["silver", "vicgas", "silver_int291_v4_out_of_merit_order_gas_1"])
INT316_KEY = AssetKey(["silver", "vicgas", "silver_int316_v4_operational_gas_1"])
INT652_KEY = AssetKey(
    ["silver", "sttm", "silver_int652_v1_ex_ante_schedule_quantity_rpt_1"]
)
INT655_KEY = AssetKey(
    ["silver", "sttm", "silver_int655_v1_provisional_schedule_quantity_rpt_1"]
)

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT050_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT235_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT291_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT316_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT652_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT655_KEY, column_name="surrogate_key"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
        "quantity_gj": [
            TableColumnDep(asset_key=INT050_KEY, column_name="scheduled_qty"),
            TableColumnDep(asset_key=INT235_KEY, column_name="value"),
            TableColumnDep(
                asset_key=INT291_KEY, column_name="scheduled_out_of_merit_gj"
            ),
            TableColumnDep(asset_key=INT316_KEY, column_name="energy_gj"),
            TableColumnDep(asset_key=INT652_KEY, column_name="scheduled_qty"),
            TableColumnDep(asset_key=INT652_KEY, column_name="firm_gas_scheduled_qty"),
            TableColumnDep(
                asset_key=INT652_KEY, column_name="as_available_scheduled_qty"
            ),
            TableColumnDep(asset_key=INT652_KEY, column_name="price_taker_bid_qty"),
            TableColumnDep(
                asset_key=INT652_KEY, column_name="price_taker_bid_not_sched_qty"
            ),
            TableColumnDep(asset_key=INT655_KEY, column_name="provisional_qty"),
            TableColumnDep(
                asset_key=INT655_KEY, column_name="provisional_firm_gas_scheduled"
            ),
            TableColumnDep(
                asset_key=INT655_KEY, column_name="provisional_as_available_scheduled"
            ),
            TableColumnDep(
                asset_key=INT655_KEY,
                column_name="price_taker_bid_provisional_not_sched_qty",
            ),
            TableColumnDep(
                asset_key=INT655_KEY, column_name="price_taker_bid_provisional_qty"
            ),
        ],
        "amount_gst_ex": [
            TableColumnDep(asset_key=INT291_KEY, column_name="ancillary_amt_gst_ex")
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
    "quantity_type": pl.String,
    "schedule_type_id": pl.String,
    "transmission_id": pl.String,
    "transmission_doc_id": pl.String,
    "source_point_id": pl.String,
    "quantity_gj": pl.Float64,
    "volume_kscm": pl.Float64,
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
    return parse_gas_datetime(column)


def _base(
    source_table: str,
    gas_date_column: str,
    updated_column: str,
    source_system: str = SOURCE_SYSTEM,
) -> list[pl.Expr]:
    return [
        pl.lit(source_system).alias("source_system"),
        pl.lit([source_table]).cast(pl.List(pl.String)).alias("source_tables"),
        pl.lit(source_table).alias("source_table"),
        _parse_datetime(gas_date_column).dt.date().alias("gas_date"),
        pl.col(updated_column).cast(pl.String).alias("source_last_updated"),
        _parse_datetime(updated_column).alias("source_last_updated_timestamp"),
        pl.col("surrogate_key").cast(pl.String).alias("source_surrogate_key"),
        pl.col("source_file").cast(pl.String).alias("source_file"),
        pl.col("ingested_timestamp").alias("ingested_timestamp"),
    ]


def _sttm_base(source_table: str) -> list[pl.Expr]:
    return _base(
        source_table,
        "gas_date",
        "report_datetime",
        source_system=STTM_SOURCE_SYSTEM,
    )


def _sttm_quantity_rows(
    df: LazyFrame,
    source_table: str,
    quantity_columns: dict[str, str],
    *,
    schedule_type: pl.Expr,
) -> LazyFrame:
    quantity_column_names = list(quantity_columns)
    return (
        df.select(
            *_sttm_base(source_table),
            schedule_type_id=schedule_type,
            transmission_id=pl.col("schedule_identifier").cast(pl.String),
            transmission_doc_id=pl.lit(None).cast(pl.String),
            source_point_id=pl.col("facility_identifier").cast(pl.String),
            volume_kscm=pl.lit(None).cast(pl.Float64),
            amount_gst_ex=pl.lit(None).cast(pl.Float64),
            *[pl.col(column).cast(pl.Float64) for column in quantity_column_names],
        )
        .unpivot(
            index=[
                "source_system",
                "source_tables",
                "source_table",
                "gas_date",
                "source_last_updated",
                "source_last_updated_timestamp",
                "source_surrogate_key",
                "source_file",
                "ingested_timestamp",
                "schedule_type_id",
                "transmission_id",
                "transmission_doc_id",
                "source_point_id",
                "volume_kscm",
                "amount_gst_ex",
            ],
            on=quantity_column_names,
            variable_name="quantity_type",
            value_name="quantity_gj",
        )
        .with_columns(quantity_type=pl.col("quantity_type").replace(quantity_columns))
        .filter(pl.col("quantity_gj").is_not_null())
    )


def _select_scheduled_quantities(
    int050: LazyFrame,
    int235: LazyFrame,
    int291: LazyFrame,
    int316: LazyFrame,
    int652: LazyFrame,
    int655: LazyFrame,
) -> LazyFrame:
    rows = [
        int050.select(
            *_base(SOURCE_TABLES[0], "gas_date", "current_date"),
            quantity_type=pl.lit("scheduled_withdrawal"),
            schedule_type_id=pl.lit(None).cast(pl.String),
            transmission_id=pl.col("transmission_id").cast(pl.String),
            transmission_doc_id=pl.lit(None).cast(pl.String),
            source_point_id=pl.col("withdrawal_zone_name").cast(pl.String),
            quantity_gj=pl.col("scheduled_qty").cast(pl.Float64),
            volume_kscm=pl.lit(None).cast(pl.Float64),
            amount_gst_ex=pl.lit(None).cast(pl.Float64),
        ),
        int235.filter(
            ~pl.col("data_type").cast(pl.String).str.contains("PRICE")
        ).select(
            *_base(SOURCE_TABLES[1], "gas_date", "current_date"),
            quantity_type=pl.col("data_type").cast(pl.String),
            schedule_type_id=pl.col("flag").cast(pl.String),
            transmission_id=pl.col("transmission_id").cast(pl.String),
            transmission_doc_id=pl.col("transmission_doc_id").cast(pl.String),
            source_point_id=pl.col("id").cast(pl.String),
            quantity_gj=pl.col("value").cast(pl.Float64),
            volume_kscm=pl.lit(None).cast(pl.Float64),
            amount_gst_ex=pl.lit(None).cast(pl.Float64),
        ),
        int291.select(
            *_base(SOURCE_TABLES[2], "gas_date", "current_date"),
            quantity_type=pl.lit("out_of_merit_gas"),
            schedule_type_id=pl.lit(None).cast(pl.String),
            transmission_id=pl.col("statement_version_id").cast(pl.String),
            transmission_doc_id=pl.lit(None).cast(pl.String),
            source_point_id=pl.lit(None).cast(pl.String),
            quantity_gj=pl.col("scheduled_out_of_merit_gj").cast(pl.Float64),
            volume_kscm=pl.lit(None).cast(pl.Float64),
            amount_gst_ex=pl.col("ancillary_amt_gst_ex").cast(pl.Float64),
        ),
        int316.select(
            *_base(SOURCE_TABLES[3], "gas_date", "current_date"),
            quantity_type=pl.lit("operational_gas"),
            schedule_type_id=pl.lit(None).cast(pl.String),
            transmission_id=pl.lit(None).cast(pl.String),
            transmission_doc_id=pl.lit(None).cast(pl.String),
            source_point_id=pl.col("hv_zone").cast(pl.String),
            quantity_gj=pl.col("energy_gj").cast(pl.Float64),
            volume_kscm=pl.col("volume_kscm").cast(pl.Float64),
            amount_gst_ex=pl.lit(None).cast(pl.Float64),
        ),
        _sttm_quantity_rows(
            int652,
            SOURCE_TABLES[4],
            {
                "scheduled_qty": "sttm_ex_ante_scheduled_qty",
                "firm_gas_scheduled_qty": "sttm_ex_ante_firm_gas_scheduled_qty",
                "as_available_scheduled_qty": (
                    "sttm_ex_ante_as_available_scheduled_qty"
                ),
                "price_taker_bid_qty": "sttm_ex_ante_price_taker_bid_qty",
                "price_taker_bid_not_sched_qty": (
                    "sttm_ex_ante_price_taker_bid_not_scheduled_qty"
                ),
            },
            schedule_type=pl.lit("ex_ante"),
        ),
        _sttm_quantity_rows(
            int655,
            SOURCE_TABLES[5],
            {
                "provisional_qty": "sttm_provisional_scheduled_qty",
                "provisional_firm_gas_scheduled": (
                    "sttm_provisional_firm_gas_scheduled_qty"
                ),
                "provisional_as_available_scheduled": (
                    "sttm_provisional_as_available_scheduled_qty"
                ),
                "price_taker_bid_provisional_not_sched_qty": (
                    "sttm_provisional_price_taker_bid_not_scheduled_qty"
                ),
                "price_taker_bid_provisional_qty": (
                    "sttm_provisional_price_taker_bid_qty"
                ),
            },
            schedule_type=pl.col("provisional_schedule_type").cast(pl.String),
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
    description="Silver gas scheduled quantity fact.",
    ins={
        "int050": AssetIn(key=INT050_KEY),
        "int235": AssetIn(key=INT235_KEY),
        "int291": AssetIn(key=INT291_KEY),
        "int316": AssetIn(key=INT316_KEY),
        "int652": AssetIn(key=INT652_KEY),
        "int655": AssetIn(key=INT655_KEY),
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
def silver_gas_fact_scheduled_quantity(
    int050: LazyFrame,
    int235: LazyFrame,
    int291: LazyFrame,
    int316: LazyFrame,
    int652: LazyFrame,
    int655: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver gas scheduled quantity fact asset."""
    return _materialize_result(
        _select_scheduled_quantities(int050, int235, int291, int316, int652, int655)
    )


@asset_check(asset=silver_gas_fact_scheduled_quantity, name="check_required_fields")
def silver_gas_fact_scheduled_quantity_required_fields(
    input_df: LazyFrame,
) -> AssetCheckResult:
    """Validate required fields for the silver gas scheduled quantity fact asset."""
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


silver_gas_fact_scheduled_quantity_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_scheduled_quantity,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_scheduled_quantity_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_scheduled_quantity, check_name="check_schema_matches"
)
silver_gas_fact_scheduled_quantity_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_scheduled_quantity, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver gas scheduled quantity fact asset."""
    return Definitions(
        assets=[silver_gas_fact_scheduled_quantity],
        asset_checks=[
            silver_gas_fact_scheduled_quantity_duplicate_row_check,
            silver_gas_fact_scheduled_quantity_schema_check,
            silver_gas_fact_scheduled_quantity_schema_drift_check,
            silver_gas_fact_scheduled_quantity_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_scheduled_quantity_sensor",
                target=[silver_gas_fact_scheduled_quantity.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
