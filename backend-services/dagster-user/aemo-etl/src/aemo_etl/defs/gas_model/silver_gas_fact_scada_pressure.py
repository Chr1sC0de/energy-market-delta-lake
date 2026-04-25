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
TABLE_NAME = "silver_gas_fact_scada_pressure"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per MCE node pressure measurement offset"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_node_id",
    "measurement_timestamp",
    "pressure_offset_hour",
    "source_surrogate_key",
]
SOURCE_TABLES = ["silver.vicgas.silver_int276_v4_hourly_scada_pressures_at_mce_nodes_1"]
SOURCE_SYSTEM = "VICGAS"
INT276_KEY = AssetKey(
    ["silver", "vicgas", "silver_int276_v4_hourly_scada_pressures_at_mce_nodes_1"]
)
PRESSURE_COLUMNS = ["current_hour", *[f"hour_{i:02d}_ago" for i in range(1, 25)]]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": [
            TableColumnDep(asset_key=INT276_KEY, column_name="surrogate_key")
        ],
        "source_surrogate_key": [
            TableColumnDep(asset_key=INT276_KEY, column_name="surrogate_key")
        ],
        "pressure_kpa": [
            TableColumnDep(asset_key=INT276_KEY, column_name="current_hour")
        ],
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "source_node_id": pl.String,
    "node_name": pl.String,
    "measurement_timestamp": pl.Datetime("us"),
    "pressure_offset_hour": pl.Int64,
    "pressure_kpa": pl.Float64,
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
    "source_node_id",
    "measurement_timestamp",
]


def _parse_datetime(column: str) -> pl.Expr:
    source = pl.col(column).cast(pl.String)
    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%d %b %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y %H:%M:%S", strict=False),
    )


def _select_scada_pressure(int276: LazyFrame) -> LazyFrame:
    return (
        int276.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit(SOURCE_TABLES).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[0]),
            source_node_id=pl.col("node_id").cast(pl.String),
            node_name=pl.col("node_name").cast(pl.String),
            measurement_timestamp=_parse_datetime("measurement_datetime"),
            source_last_updated=pl.col("current_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("current_date"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
            *[pl.col(column).cast(pl.Float64) for column in PRESSURE_COLUMNS],
        )
        .unpivot(
            index=[
                "source_system",
                "source_tables",
                "source_table",
                "source_node_id",
                "node_name",
                "measurement_timestamp",
                "source_last_updated",
                "source_last_updated_timestamp",
                "source_surrogate_key",
                "source_file",
                "ingested_timestamp",
            ],
            on=PRESSURE_COLUMNS,
            variable_name="pressure_offset",
            value_name="pressure_kpa",
        )
        .with_columns(
            pressure_offset_hour=pl.when(pl.col("pressure_offset") == "current_hour")
            .then(0)
            .otherwise(
                pl.col("pressure_offset").str.extract(r"hour_(\d+)_ago").cast(pl.Int64)
            )
        )
        .with_columns(
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
    description="Silver gas SCADA pressure fact.",
    ins={"int276": AssetIn(key=INT276_KEY)},
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
def silver_gas_fact_scada_pressure(int276: LazyFrame) -> MaterializeResult[LazyFrame]:
    return _materialize_result(_select_scada_pressure(int276))


@asset_check(asset=silver_gas_fact_scada_pressure, name="check_required_fields")
def silver_gas_fact_scada_pressure_required_fields(
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


silver_gas_fact_scada_pressure_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_scada_pressure,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_scada_pressure_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_scada_pressure, check_name="check_schema_matches"
)
silver_gas_fact_scada_pressure_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_scada_pressure, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_fact_scada_pressure],
        asset_checks=[
            silver_gas_fact_scada_pressure_duplicate_row_check,
            silver_gas_fact_scada_pressure_schema_check,
            silver_gas_fact_scada_pressure_schema_drift_check,
            silver_gas_fact_scada_pressure_required_fields,
        ],
    )
