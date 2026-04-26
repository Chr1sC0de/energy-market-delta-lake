import polars as pl
from dagster import (
    AssetCheckResult,
    AssetIn,
    AssetKey,
    AutomationCondition,
    AutomationConditionSensorDefinition,
    Definitions,
    MaterializeResult,
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
TABLE_NAME = "silver_gas_dim_pipeline_segment"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one current row per source-qualified gas pipeline segment"
SURROGATE_KEY_SOURCES = ["source_system", "source_pipe_segment_id"]
SOURCE_TABLES = [
    "silver.vicgas.silver_int259_v4_pipe_segment_1",
    "silver.vicgas.silver_int258_v4_mce_nodes_1",
]
SOURCE_SYSTEM = "VICGAS"
VICGAS_PIPE_SEGMENTS_KEY = AssetKey(
    ["silver", "vicgas", "silver_int259_v4_pipe_segment_1"]
)
VICGAS_MCE_NODES_KEY = AssetKey(["silver", "vicgas", "silver_int258_v4_mce_nodes_1"])
ZONES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_zone"])

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="pipe_segment_id"
            )
        ],
        "zone_key": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="linepack_zone_id"
            ),
            TableColumnDep(asset_key=ZONES_KEY, column_name="surrogate_key"),
        ],
        "source_pipe_segment_id": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="pipe_segment_id"
            )
        ],
        "pipe_segment_name": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="pipe_segment_name"
            )
        ],
        "source_linepack_zone_id": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="linepack_zone_id"
            )
        ],
        "source_origin_node_id": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="node_origin_id"
            )
        ],
        "source_origin_node_name": [
            TableColumnDep(
                asset_key=VICGAS_MCE_NODES_KEY,
                column_name="point_group_identifier_name",
            )
        ],
        "source_destination_node_id": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="node_destination_id"
            )
        ],
        "source_destination_node_name": [
            TableColumnDep(
                asset_key=VICGAS_MCE_NODES_KEY,
                column_name="point_group_identifier_name",
            )
        ],
        "diameter": [
            TableColumnDep(asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="diameter")
        ],
        "length": [
            TableColumnDep(asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="length")
        ],
        "max_pressure": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="max_pressure"
            )
        ],
        "min_pressure": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="min_pressure"
            )
        ],
        "reverse_flow": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="reverse_flow"
            )
        ],
        "compressor": [
            TableColumnDep(asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="compressor")
        ],
        "commencement_date": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="commencement_date"
            )
        ],
        "termination_date": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="termination_date"
            )
        ],
        "source_last_updated": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="last_mod_date"
            )
        ],
        "source_last_updated_timestamp": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="last_mod_date"
            )
        ],
        "source_surrogate_key": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="surrogate_key"
            )
        ],
        "source_file": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="source_file"
            )
        ],
        "ingested_timestamp": [
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="ingested_timestamp"
            )
        ],
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_pipeline_id": pl.String,
    "source_pipe_segment_id": pl.String,
    "pipe_segment_name": pl.String,
    "source_linepack_zone_id": pl.String,
    "source_origin_node_id": pl.String,
    "source_origin_node_name": pl.String,
    "source_destination_node_id": pl.String,
    "source_destination_node_name": pl.String,
    "diameter": pl.Float64,
    "length": pl.Float64,
    "max_pressure": pl.Float64,
    "min_pressure": pl.Float64,
    "reverse_flow": pl.String,
    "compressor": pl.String,
    "commencement_date": pl.Date,
    "termination_date": pl.Date,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver dimension primary key generated by surrogate_key_sources.",
    "zone_key": "Parent silver_gas_dim_zone surrogate_key for linepack zone when resolvable.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the gas model row.",
    "source_pipeline_id": "Source-system pipeline identifier.",
    "source_pipe_segment_id": "Source-system pipe segment identifier.",
    "pipe_segment_name": "Pipe segment name.",
    "source_linepack_zone_id": "Source-system linepack zone identifier.",
    "source_origin_node_id": "Source-system origin node identifier.",
    "source_origin_node_name": "Source-system origin node name.",
    "source_destination_node_id": "Source-system destination node identifier.",
    "source_destination_node_name": "Source-system destination node name.",
    "diameter": "Pipe diameter.",
    "length": "Pipe segment length.",
    "max_pressure": "Maximum pressure.",
    "min_pressure": "Minimum pressure.",
    "reverse_flow": "Source reverse-flow flag.",
    "compressor": "Source compressor flag.",
    "commencement_date": "Parsed pipe segment commencement date.",
    "termination_date": "Parsed pipe segment termination date.",
    "source_last_updated": "Raw source update value.",
    "source_last_updated_timestamp": "Parsed source update timestamp.",
    "source_surrogate_key": "Source row surrogate key for lineage.",
    "source_file": "Archived source file for the bronze row.",
    "ingested_timestamp": "Timestamp when the bronze row was ingested.",
}

REQUIRED_COLUMNS = [
    "surrogate_key",
    "source_system",
    "source_pipe_segment_id",
    "pipe_segment_name",
]


def _parse_datetime(column: str) -> pl.Expr:
    source = pl.col(column).cast(pl.String)
    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%d %b %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d", strict=False),
    )


def _parse_date(column: str) -> pl.Expr:
    return _parse_datetime(column).dt.date()


def _node_names(nodes: LazyFrame, id_column: str, name_column: str) -> LazyFrame:
    return nodes.select(
        **{
            id_column: pl.col("point_group_identifier_id").cast(pl.String),
            name_column: pl.col("point_group_identifier_name").cast(pl.String),
        }
    ).unique(subset=[id_column], keep="first")


def _select_current_pipeline_segments(
    vicgas_pipe_segments: LazyFrame,
    vicgas_mce_nodes: LazyFrame,
    zones: LazyFrame,
) -> LazyFrame:
    zone_keys = zones.filter(
        (pl.col("source_system") == SOURCE_SYSTEM)
        & (pl.col("zone_type") == "linepack_zone")
    ).select(
        zone_key=pl.col("surrogate_key"),
        source_linepack_zone_id=pl.col("source_zone_id"),
    )
    origin_nodes = _node_names(
        vicgas_mce_nodes, "source_origin_node_id", "source_origin_node_name"
    )
    destination_nodes = _node_names(
        vicgas_mce_nodes,
        "source_destination_node_id",
        "source_destination_node_name",
    )
    return (
        vicgas_pipe_segments.with_columns(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit(SOURCE_TABLES).cast(pl.List(pl.String)),
            source_pipeline_id=pl.lit(None).cast(pl.String),
            source_pipe_segment_id=pl.col("pipe_segment_id").cast(pl.String),
            pipe_segment_name=pl.col("pipe_segment_name").cast(pl.String),
            source_linepack_zone_id=pl.col("linepack_zone_id").cast(pl.String),
            source_origin_node_id=pl.col("node_origin_id").cast(pl.String),
            source_destination_node_id=pl.col("node_destination_id").cast(pl.String),
            diameter=pl.col("diameter").cast(pl.Float64),
            length=pl.col("length").cast(pl.Float64),
            max_pressure=pl.col("max_pressure").cast(pl.Float64),
            min_pressure=pl.col("min_pressure").cast(pl.Float64),
            reverse_flow=pl.col("reverse_flow").cast(pl.String),
            compressor=pl.col("compressor").cast(pl.String),
            commencement_date=_parse_date("commencement_date"),
            termination_date=_parse_date("termination_date"),
            source_last_updated=pl.col("last_mod_date").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("last_mod_date"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        )
        .with_columns(surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES))
        .sort(
            [
                "source_system",
                "source_pipe_segment_id",
                "source_last_updated_timestamp",
                "commencement_date",
                "ingested_timestamp",
            ],
            descending=[False, False, True, True, True],
            nulls_last=True,
        )
        .unique(subset=SURROGATE_KEY_SOURCES, keep="first", maintain_order=True)
        .join(zone_keys, on="source_linepack_zone_id", how="left")
        .join(origin_nodes, on="source_origin_node_id", how="left")
        .join(destination_nodes, on="source_destination_node_id", how="left")
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
    description="Silver current-snapshot gas pipeline segment dimension.",
    ins={
        "vicgas_pipe_segments": AssetIn(key=VICGAS_PIPE_SEGMENTS_KEY),
        "vicgas_mce_nodes": AssetIn(key=VICGAS_MCE_NODES_KEY),
        "zones": AssetIn(key=ZONES_KEY),
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
def silver_gas_dim_pipeline_segment(
    vicgas_pipe_segments: LazyFrame,
    vicgas_mce_nodes: LazyFrame,
    zones: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_current_pipeline_segments(vicgas_pipe_segments, vicgas_mce_nodes, zones)
    )


@asset_check(
    asset=silver_gas_dim_pipeline_segment,
    name="check_required_fields",
    description="Check required dimension fields are not null.",
)
def silver_gas_dim_pipeline_segment_required_fields(
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


silver_gas_dim_pipeline_segment_duplicate_row_check = duplicate_row_check_factory(
    assets_definition=silver_gas_dim_pipeline_segment,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
    description="Check that surrogate_key is unique.",
)

silver_gas_dim_pipeline_segment_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_pipeline_segment,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)

silver_gas_dim_pipeline_segment_schema_drift_check = schema_drift_check_factory(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_pipeline_segment,
    check_name="check_schema_drift",
    description="Check for schema drift against the declared asset schema.",
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_dim_pipeline_segment],
        asset_checks=[
            silver_gas_dim_pipeline_segment_duplicate_row_check,
            silver_gas_dim_pipeline_segment_schema_check,
            silver_gas_dim_pipeline_segment_schema_drift_check,
            silver_gas_dim_pipeline_segment_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_dim_pipeline_segment_sensor",
                target=[silver_gas_dim_pipeline_segment.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
