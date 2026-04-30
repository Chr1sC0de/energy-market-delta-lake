"""Dagster definitions for the silver gas gas quality fact asset."""

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
TABLE_NAME = "silver_gas_fact_gas_quality"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific gas quality or composition measurement"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "gas_date",
    "source_point_id",
    "quality_type",
    "gas_interval",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int140_v5_gas_quality_data_1",
    "silver.vicgas.silver_int176_v4_gas_composition_data_1",
]
SOURCE_SYSTEM = "VICGAS"
INT140_KEY = AssetKey(["silver", "vicgas", "silver_int140_v5_gas_quality_data_1"])
INT176_KEY = AssetKey(["silver", "vicgas", "silver_int176_v4_gas_composition_data_1"])

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT140_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT176_KEY, column_name="surrogate_key"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
        "quantity": [
            TableColumnDep(asset_key=INT140_KEY, column_name="quantity"),
            TableColumnDep(asset_key=INT176_KEY, column_name="methane"),
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
    "gas_interval": pl.String,
    "source_point_id": pl.String,
    "point_name": pl.String,
    "quality_type": pl.String,
    "unit": pl.String,
    "quantity": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {column: column.replace("_", " ") for column in SCHEMA}
REQUIRED_COLUMNS = ["surrogate_key", "source_system", "source_table", "quality_type"]
COMPOSITION_COLUMNS = [
    "methane",
    "ethane",
    "propane",
    "butane_i",
    "butane_n",
    "pentane_i",
    "pentane_n",
    "pentane_neo",
    "hexane",
    "nitrogen",
    "carbon_dioxide",
    "hydrogen",
    "spec_gravity",
]


def _parse_datetime(column: str) -> pl.Expr:
    source = pl.col(column).cast(pl.String)
    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%d %b %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %b %Y", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y", strict=False),
    )


def _quality_rows(int140: LazyFrame) -> LazyFrame:
    return int140.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[0]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[0]),
        gas_date=_parse_datetime("gas_date").dt.date(),
        gas_interval=pl.col("ti").cast(pl.String),
        source_point_id=pl.col("mirn").cast(pl.String),
        point_name=pl.col("site_company").cast(pl.String),
        quality_type=pl.col("quality_type").cast(pl.String),
        unit=pl.col("unit").cast(pl.String),
        quantity=pl.col("quantity").cast(pl.Float64),
        source_last_updated=pl.col("current_date").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("current_date"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _composition_rows(int176: LazyFrame) -> LazyFrame:
    return (
        int176.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[1]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[1]),
            gas_date=_parse_datetime("gas_date").dt.date(),
            gas_interval=pl.lit(None).cast(pl.String),
            source_point_id=pl.col("hv_zone").cast(pl.String),
            point_name=pl.col("hv_zone_desc").cast(pl.String),
            source_last_updated=pl.col("current_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("current_date"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
            *[pl.col(column).cast(pl.Float64) for column in COMPOSITION_COLUMNS],
        )
        .unpivot(
            index=[
                "source_system",
                "source_tables",
                "source_table",
                "gas_date",
                "gas_interval",
                "source_point_id",
                "point_name",
                "source_last_updated",
                "source_last_updated_timestamp",
                "source_surrogate_key",
                "source_file",
                "ingested_timestamp",
            ],
            on=COMPOSITION_COLUMNS,
            variable_name="quality_type",
            value_name="quantity",
        )
        .with_columns(unit=pl.lit("composition"))
    )


def _select_gas_quality(int140: LazyFrame, int176: LazyFrame) -> LazyFrame:
    return (
        pl.concat(
            [_quality_rows(int140), _composition_rows(int176)], how="diagonal_relaxed"
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
    description="Silver gas quality and composition fact.",
    ins={"int140": AssetIn(key=INT140_KEY), "int176": AssetIn(key=INT176_KEY)},
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
def silver_gas_fact_gas_quality(
    int140: LazyFrame, int176: LazyFrame
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver gas gas quality fact asset."""
    return _materialize_result(_select_gas_quality(int140, int176))


@asset_check(asset=silver_gas_fact_gas_quality, name="check_required_fields")
def silver_gas_fact_gas_quality_required_fields(
    input_df: LazyFrame,
) -> AssetCheckResult:
    """Validate required fields for the silver gas gas quality fact asset."""
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


silver_gas_fact_gas_quality_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_gas_quality,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_gas_quality_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_gas_quality, check_name="check_schema_matches"
)
silver_gas_fact_gas_quality_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_gas_quality, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver gas gas quality fact asset."""
    return Definitions(
        assets=[silver_gas_fact_gas_quality],
        asset_checks=[
            silver_gas_fact_gas_quality_duplicate_row_check,
            silver_gas_fact_gas_quality_schema_check,
            silver_gas_fact_gas_quality_schema_drift_check,
            silver_gas_fact_gas_quality_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_gas_quality_sensor",
                target=[silver_gas_fact_gas_quality.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
