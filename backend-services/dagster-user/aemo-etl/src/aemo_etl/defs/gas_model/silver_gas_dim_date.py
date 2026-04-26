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
TABLE_NAME = "silver_gas_dim_date"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per gas date observed in operations mart source tables"
SURROGATE_KEY_SOURCES = ["gas_date"]
SOURCE_TABLES = [
    "silver.gbb.silver_gasbb_pipeline_connection_flow_v2",
    "silver.gbb.silver_gasbb_actual_flow_storage",
    "silver.gbb.silver_gasbb_nomination_and_forecast",
    "silver.gbb.silver_gasbb_linepack_capacity_adequacy",
    "silver.vicgas.silver_int126_v4_dfs_data_1",
    "silver.vicgas.silver_int153_v4_demand_forecast_rpt_1",
    "silver.vicgas.silver_int128_v4_actual_linepack_1",
    "silver.vicgas.silver_int236_v4_operational_meter_readings_1",
    "silver.vicgas.silver_int313_v4_allocated_injections_withdrawals_1",
]

GBB_CONNECTION_FLOW_KEY = AssetKey(
    ["silver", "gbb", "silver_gasbb_pipeline_connection_flow_v2"]
)
GBB_FLOW_STORAGE_KEY = AssetKey(["silver", "gbb", "silver_gasbb_actual_flow_storage"])
GBB_NOMINATION_FORECAST_KEY = AssetKey(
    ["silver", "gbb", "silver_gasbb_nomination_and_forecast"]
)
GBB_LINEPACK_KEY = AssetKey(
    ["silver", "gbb", "silver_gasbb_linepack_capacity_adequacy"]
)
VICGAS_DFS_KEY = AssetKey(["silver", "vicgas", "silver_int126_v4_dfs_data_1"])
VICGAS_DEMAND_FORECAST_KEY = AssetKey(
    ["silver", "vicgas", "silver_int153_v4_demand_forecast_rpt_1"]
)
VICGAS_LINEPACK_KEY = AssetKey(
    ["silver", "vicgas", "silver_int128_v4_actual_linepack_1"]
)
VICGAS_METER_READINGS_KEY = AssetKey(
    ["silver", "vicgas", "silver_int236_v4_operational_meter_readings_1"]
)
VICGAS_ALLOCATIONS_KEY = AssetKey(
    ["silver", "vicgas", "silver_int313_v4_allocated_injections_withdrawals_1"]
)

_GAS_DATE_DEPS = [
    TableColumnDep(asset_key=GBB_CONNECTION_FLOW_KEY, column_name="GasDate"),
    TableColumnDep(asset_key=GBB_FLOW_STORAGE_KEY, column_name="GasDate"),
    TableColumnDep(asset_key=GBB_NOMINATION_FORECAST_KEY, column_name="Gasdate"),
    TableColumnDep(asset_key=GBB_LINEPACK_KEY, column_name="GasDate"),
    TableColumnDep(asset_key=VICGAS_DFS_KEY, column_name="gas_date"),
    TableColumnDep(asset_key=VICGAS_DEMAND_FORECAST_KEY, column_name="forecast_date"),
    TableColumnDep(asset_key=VICGAS_LINEPACK_KEY, column_name="commencement_datetime"),
    TableColumnDep(asset_key=VICGAS_METER_READINGS_KEY, column_name="gas_date"),
    TableColumnDep(asset_key=VICGAS_ALLOCATIONS_KEY, column_name="gas_date"),
]

_SOURCE_SURROGATE_KEY_DEPS = [
    TableColumnDep(asset_key=GBB_CONNECTION_FLOW_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=GBB_FLOW_STORAGE_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=GBB_NOMINATION_FORECAST_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=GBB_LINEPACK_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=VICGAS_DFS_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=VICGAS_DEMAND_FORECAST_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=VICGAS_LINEPACK_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=VICGAS_METER_READINGS_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=VICGAS_ALLOCATIONS_KEY, column_name="surrogate_key"),
]

_SOURCE_FILE_DEPS = [
    TableColumnDep(asset_key=GBB_CONNECTION_FLOW_KEY, column_name="source_file"),
    TableColumnDep(asset_key=GBB_FLOW_STORAGE_KEY, column_name="source_file"),
    TableColumnDep(asset_key=GBB_NOMINATION_FORECAST_KEY, column_name="source_file"),
    TableColumnDep(asset_key=GBB_LINEPACK_KEY, column_name="source_file"),
    TableColumnDep(asset_key=VICGAS_DFS_KEY, column_name="source_file"),
    TableColumnDep(asset_key=VICGAS_DEMAND_FORECAST_KEY, column_name="source_file"),
    TableColumnDep(asset_key=VICGAS_LINEPACK_KEY, column_name="source_file"),
    TableColumnDep(asset_key=VICGAS_METER_READINGS_KEY, column_name="source_file"),
    TableColumnDep(asset_key=VICGAS_ALLOCATIONS_KEY, column_name="source_file"),
]

_INGESTED_TIMESTAMP_DEPS = [
    TableColumnDep(asset_key=GBB_CONNECTION_FLOW_KEY, column_name="ingested_timestamp"),
    TableColumnDep(asset_key=GBB_FLOW_STORAGE_KEY, column_name="ingested_timestamp"),
    TableColumnDep(
        asset_key=GBB_NOMINATION_FORECAST_KEY, column_name="ingested_timestamp"
    ),
    TableColumnDep(asset_key=GBB_LINEPACK_KEY, column_name="ingested_timestamp"),
    TableColumnDep(asset_key=VICGAS_DFS_KEY, column_name="ingested_timestamp"),
    TableColumnDep(
        asset_key=VICGAS_DEMAND_FORECAST_KEY, column_name="ingested_timestamp"
    ),
    TableColumnDep(asset_key=VICGAS_LINEPACK_KEY, column_name="ingested_timestamp"),
    TableColumnDep(
        asset_key=VICGAS_METER_READINGS_KEY, column_name="ingested_timestamp"
    ),
    TableColumnDep(asset_key=VICGAS_ALLOCATIONS_KEY, column_name="ingested_timestamp"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _GAS_DATE_DEPS,
        "gas_date": _GAS_DATE_DEPS,
        "source_surrogate_keys": _SOURCE_SURROGATE_KEY_DEPS,
        "source_files": _SOURCE_FILE_DEPS,
        "ingested_timestamp": _INGESTED_TIMESTAMP_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "source_tables": pl.List(pl.String),
    "gas_date": pl.Date,
    "gas_year": pl.Int32,
    "gas_quarter": pl.Int8,
    "gas_month": pl.Int8,
    "gas_day": pl.Int8,
    "day_name": pl.String,
    "source_surrogate_keys": pl.List(pl.String),
    "source_files": pl.List(pl.String),
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver date dimension primary key generated by gas_date.",
    "source_tables": "Silver source tables where the gas date was observed.",
    "gas_date": "Gas day date.",
    "gas_year": "Gas date calendar year.",
    "gas_quarter": "Gas date calendar quarter.",
    "gas_month": "Gas date calendar month.",
    "gas_day": "Gas date calendar day.",
    "day_name": "Gas date weekday name.",
    "source_surrogate_keys": "Source row surrogate keys where the gas date was observed.",
    "source_files": "Archived source files where the gas date was observed.",
    "ingested_timestamp": "Latest contributing source ingestion timestamp.",
}

REQUIRED_COLUMNS = ["surrogate_key", "gas_date"]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _date_rows(df: LazyFrame, source_table: str, date_column: str) -> LazyFrame:
    return df.select(
        source_table=pl.lit(source_table),
        gas_date=_parse_datetime(date_column).dt.date(),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _select_dates(
    gbb_connection_flow: LazyFrame,
    gbb_flow_storage: LazyFrame,
    gbb_nomination_forecast: LazyFrame,
    gbb_linepack: LazyFrame,
    vicgas_dfs: LazyFrame,
    vicgas_demand_forecast: LazyFrame,
    vicgas_linepack: LazyFrame,
    vicgas_meter_readings: LazyFrame,
    vicgas_allocations: LazyFrame,
) -> LazyFrame:
    combined = pl.concat(
        [
            _date_rows(gbb_connection_flow, SOURCE_TABLES[0], "GasDate"),
            _date_rows(gbb_flow_storage, SOURCE_TABLES[1], "GasDate"),
            _date_rows(gbb_nomination_forecast, SOURCE_TABLES[2], "Gasdate"),
            _date_rows(gbb_linepack, SOURCE_TABLES[3], "GasDate"),
            _date_rows(vicgas_dfs, SOURCE_TABLES[4], "gas_date"),
            _date_rows(vicgas_demand_forecast, SOURCE_TABLES[5], "forecast_date"),
            _date_rows(vicgas_linepack, SOURCE_TABLES[6], "commencement_datetime"),
            _date_rows(vicgas_meter_readings, SOURCE_TABLES[7], "gas_date"),
            _date_rows(vicgas_allocations, SOURCE_TABLES[8], "gas_date"),
        ],
        how="diagonal_relaxed",
    ).filter(pl.col("gas_date").is_not_null())

    return (
        combined.group_by("gas_date")
        .agg(
            source_tables=pl.col("source_table").drop_nulls().unique().sort(),
            source_surrogate_keys=pl.col("source_surrogate_key")
            .drop_nulls()
            .unique()
            .sort(),
            source_files=pl.col("source_file").drop_nulls().unique().sort(),
            ingested_timestamp=pl.col("ingested_timestamp").max(),
        )
        .with_columns(
            surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES),
            gas_year=pl.col("gas_date").dt.year().cast(pl.Int32),
            gas_quarter=pl.col("gas_date").dt.quarter().cast(pl.Int8),
            gas_month=pl.col("gas_date").dt.month().cast(pl.Int8),
            gas_day=pl.col("gas_date").dt.day().cast(pl.Int8),
            day_name=pl.col("gas_date").dt.strftime("%A"),
        )
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
    description="Silver gas date dimension for operations mart facts.",
    ins={
        "gbb_connection_flow": AssetIn(key=GBB_CONNECTION_FLOW_KEY),
        "gbb_flow_storage": AssetIn(key=GBB_FLOW_STORAGE_KEY),
        "gbb_nomination_forecast": AssetIn(key=GBB_NOMINATION_FORECAST_KEY),
        "gbb_linepack": AssetIn(key=GBB_LINEPACK_KEY),
        "vicgas_dfs": AssetIn(key=VICGAS_DFS_KEY),
        "vicgas_demand_forecast": AssetIn(key=VICGAS_DEMAND_FORECAST_KEY),
        "vicgas_linepack": AssetIn(key=VICGAS_LINEPACK_KEY),
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
    automation_condition=AutomationCondition.any_deps_updated()
    & ~AutomationCondition.in_progress()
    & ~AutomationCondition.any_deps_missing(),
)
def silver_gas_dim_date(
    gbb_connection_flow: LazyFrame,
    gbb_flow_storage: LazyFrame,
    gbb_nomination_forecast: LazyFrame,
    gbb_linepack: LazyFrame,
    vicgas_dfs: LazyFrame,
    vicgas_demand_forecast: LazyFrame,
    vicgas_linepack: LazyFrame,
    vicgas_meter_readings: LazyFrame,
    vicgas_allocations: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_dates(
            gbb_connection_flow,
            gbb_flow_storage,
            gbb_nomination_forecast,
            gbb_linepack,
            vicgas_dfs,
            vicgas_demand_forecast,
            vicgas_linepack,
            vicgas_meter_readings,
            vicgas_allocations,
        )
    )


@asset_check(
    asset=silver_gas_dim_date,
    name="check_required_fields",
    description="Check required dimension fields are not null.",
)
def silver_gas_dim_date_required_fields(input_df: LazyFrame) -> AssetCheckResult:
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


silver_gas_dim_date_duplicate_row_check = duplicate_row_check_factory(
    assets_definition=silver_gas_dim_date,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
    description="Check that surrogate_key is unique.",
)

silver_gas_dim_date_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_date,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)

silver_gas_dim_date_schema_drift_check = schema_drift_check_factory(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_date,
    check_name="check_schema_drift",
    description="Check for schema drift against the declared asset schema.",
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_dim_date],
        asset_checks=[
            silver_gas_dim_date_duplicate_row_check,
            silver_gas_dim_date_schema_check,
            silver_gas_dim_date_schema_drift_check,
            silver_gas_dim_date_required_fields,
        ],
    )
