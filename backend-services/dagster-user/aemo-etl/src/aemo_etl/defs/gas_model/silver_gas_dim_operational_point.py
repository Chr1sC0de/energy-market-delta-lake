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
TABLE_NAME = "silver_gas_dim_operational_point"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one current row per source-qualified VICGAS operational point"
SURROGATE_KEY_SOURCES = ["source_system", "point_type", "source_point_id"]
SOURCE_TABLES = [
    "silver.vicgas.silver_int236_v4_operational_meter_readings_1",
    "silver.vicgas.silver_int313_v4_allocated_injections_withdrawals_1",
]
SOURCE_SYSTEM = "VICGAS"

VICGAS_METER_READINGS_KEY = AssetKey(
    ["silver", "vicgas", "silver_int236_v4_operational_meter_readings_1"]
)
VICGAS_ALLOCATIONS_KEY = AssetKey(
    ["silver", "vicgas", "silver_int313_v4_allocated_injections_withdrawals_1"]
)
ZONES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_zone"])
PIPELINE_SEGMENTS_KEY = AssetKey(
    ["silver", "gas_model", "silver_gas_dim_pipeline_segment"]
)

_SOURCE_POINT_ID_DEPS = [
    TableColumnDep(
        asset_key=VICGAS_METER_READINGS_KEY, column_name="direction_code_name"
    ),
    TableColumnDep(asset_key=VICGAS_ALLOCATIONS_KEY, column_name="phy_mirn"),
]

_POINT_NAME_DEPS = [
    TableColumnDep(
        asset_key=VICGAS_METER_READINGS_KEY, column_name="direction_code_name"
    ),
    TableColumnDep(asset_key=VICGAS_ALLOCATIONS_KEY, column_name="site_company"),
]

_SOURCE_SURROGATE_KEY_DEPS = [
    TableColumnDep(asset_key=VICGAS_METER_READINGS_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=VICGAS_ALLOCATIONS_KEY, column_name="surrogate_key"),
]

_SOURCE_FILE_DEPS = [
    TableColumnDep(asset_key=VICGAS_METER_READINGS_KEY, column_name="source_file"),
    TableColumnDep(asset_key=VICGAS_ALLOCATIONS_KEY, column_name="source_file"),
]

_INGESTED_TIMESTAMP_DEPS = [
    TableColumnDep(
        asset_key=VICGAS_METER_READINGS_KEY, column_name="ingested_timestamp"
    ),
    TableColumnDep(asset_key=VICGAS_ALLOCATIONS_KEY, column_name="ingested_timestamp"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_POINT_ID_DEPS,
        "source_point_id": _SOURCE_POINT_ID_DEPS,
        "point_name": _POINT_NAME_DEPS,
        "zone_key": [TableColumnDep(asset_key=ZONES_KEY, column_name="surrogate_key")],
        "pipeline_segment_key": [
            TableColumnDep(asset_key=PIPELINE_SEGMENTS_KEY, column_name="surrogate_key")
        ],
        "source_surrogate_key": _SOURCE_SURROGATE_KEY_DEPS,
        "source_file": _SOURCE_FILE_DEPS,
        "ingested_timestamp": _INGESTED_TIMESTAMP_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "point_type": pl.String,
    "source_point_id": pl.String,
    "point_name": pl.String,
    "source_zone_id": pl.String,
    "zone_key": pl.String,
    "source_pipeline_id": pl.String,
    "source_pipeline_segment_id": pl.String,
    "pipeline_segment_key": pl.String,
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver operational point dimension primary key.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the gas model row.",
    "point_type": "Operational point identifier type.",
    "source_point_id": "Source-system operational point identifier.",
    "point_name": "Operational point display name.",
    "source_zone_id": "Source-system zone identifier when available.",
    "zone_key": "Parent silver_gas_dim_zone surrogate_key when resolvable.",
    "source_pipeline_id": "Source-system pipeline identifier when available.",
    "source_pipeline_segment_id": "Source-system pipeline segment identifier when available.",
    "pipeline_segment_key": "Parent silver_gas_dim_pipeline_segment surrogate_key when resolvable.",
    "source_surrogate_key": "Source row surrogate key for lineage.",
    "source_file": "Archived source file for the source row.",
    "ingested_timestamp": "Timestamp when the source row was ingested.",
}

REQUIRED_COLUMNS = [
    "surrogate_key",
    "source_system",
    "point_type",
    "source_point_id",
]


def _meter_points(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[0]]).cast(pl.List(pl.String)),
        point_type=pl.lit("direction_code_name"),
        source_point_id=pl.col("direction_code_name").cast(pl.String),
        point_name=pl.col("direction_code_name").cast(pl.String),
        source_zone_id=pl.lit(None).cast(pl.String),
        zone_key=pl.lit(None).cast(pl.String),
        source_pipeline_id=pl.lit(None).cast(pl.String),
        source_pipeline_segment_id=pl.lit(None).cast(pl.String),
        pipeline_segment_key=pl.lit(None).cast(pl.String),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _allocation_points(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[1]]).cast(pl.List(pl.String)),
        point_type=pl.lit("phy_mirn"),
        source_point_id=pl.col("phy_mirn").cast(pl.String),
        point_name=pl.col("site_company").cast(pl.String),
        source_zone_id=pl.lit(None).cast(pl.String),
        zone_key=pl.lit(None).cast(pl.String),
        source_pipeline_id=pl.lit(None).cast(pl.String),
        source_pipeline_segment_id=pl.lit(None).cast(pl.String),
        pipeline_segment_key=pl.lit(None).cast(pl.String),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _select_current_operational_points(
    vicgas_meter_readings: LazyFrame,
    vicgas_allocations: LazyFrame,
) -> LazyFrame:
    combined = pl.concat(
        [_meter_points(vicgas_meter_readings), _allocation_points(vicgas_allocations)],
        how="diagonal_relaxed",
    ).filter(pl.col("source_point_id").is_not_null())

    return (
        combined.with_columns(surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES))
        .sort(
            [
                "source_system",
                "point_type",
                "source_point_id",
                "ingested_timestamp",
                "source_file",
            ],
            descending=[False, False, False, True, True],
            nulls_last=True,
        )
        .unique(subset=SURROGATE_KEY_SOURCES, keep="first", maintain_order=True)
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
    description="Silver current-snapshot VICGAS operational point dimension.",
    ins={
        "vicgas_meter_readings": AssetIn(key=VICGAS_METER_READINGS_KEY),
        "vicgas_allocations": AssetIn(key=VICGAS_ALLOCATIONS_KEY),
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
def silver_gas_dim_operational_point(
    vicgas_meter_readings: LazyFrame,
    vicgas_allocations: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_current_operational_points(vicgas_meter_readings, vicgas_allocations)
    )


@asset_check(
    asset=silver_gas_dim_operational_point,
    name="check_required_fields",
    description="Check required dimension fields are not null.",
)
def silver_gas_dim_operational_point_required_fields(
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


silver_gas_dim_operational_point_duplicate_row_check = duplicate_row_check_factory(
    assets_definition=silver_gas_dim_operational_point,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
    description="Check that surrogate_key is unique.",
)

silver_gas_dim_operational_point_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_operational_point,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)

silver_gas_dim_operational_point_schema_drift_check = schema_drift_check_factory(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_operational_point,
    check_name="check_schema_drift",
    description="Check for schema drift against the declared asset schema.",
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_dim_operational_point],
        asset_checks=[
            silver_gas_dim_operational_point_duplicate_row_check,
            silver_gas_dim_operational_point_schema_check,
            silver_gas_dim_operational_point_schema_drift_check,
            silver_gas_dim_operational_point_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_dim_operational_point_sensor",
                target=[silver_gas_dim_operational_point.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
