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
TABLE_NAME = "silver_gas_dim_zone"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one current row per source-qualified gas zone"
SURROGATE_KEY_SOURCES = ["source_system", "zone_type", "source_zone_id"]
SOURCE_TABLES = [
    "silver.gbb.silver_gasbb_demand_zones_and_pipeline_connectionpoint_mapping",
    "silver.gbb.silver_gasbb_linepack_zones",
    "silver.vicgas.silver_int188_v4_ctm_to_hv_zone_mapping_1",
    "silver.vicgas.silver_int284_v4_tuos_zone_postcode_map_1",
    "silver.vicgas.silver_int259_v4_pipe_segment_1",
]
GBB_DEMAND_ZONE_MAPPING_KEY = AssetKey(
    ["silver", "gbb", "silver_gasbb_demand_zones_and_pipeline_connectionpoint_mapping"]
)
GBB_LINEPACK_ZONES_KEY = AssetKey(["silver", "gbb", "silver_gasbb_linepack_zones"])
VICGAS_HV_ZONE_MAPPING_KEY = AssetKey(
    ["silver", "vicgas", "silver_int188_v4_ctm_to_hv_zone_mapping_1"]
)
VICGAS_TUOS_ZONE_MAPPING_KEY = AssetKey(
    ["silver", "vicgas", "silver_int284_v4_tuos_zone_postcode_map_1"]
)
VICGAS_PIPE_SEGMENTS_KEY = AssetKey(
    ["silver", "vicgas", "silver_int259_v4_pipe_segment_1"]
)

_SOURCE_ZONE_ID_DEPS = [
    TableColumnDep(asset_key=GBB_DEMAND_ZONE_MAPPING_KEY, column_name="DemandZone"),
    TableColumnDep(asset_key=GBB_LINEPACK_ZONES_KEY, column_name="LinepackZone"),
    TableColumnDep(asset_key=VICGAS_HV_ZONE_MAPPING_KEY, column_name="hv_zone"),
    TableColumnDep(asset_key=VICGAS_TUOS_ZONE_MAPPING_KEY, column_name="tuos_zone"),
    TableColumnDep(asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="linepack_zone_id"),
]

_SOURCE_SURROGATE_KEY_DEPS = [
    TableColumnDep(asset_key=GBB_DEMAND_ZONE_MAPPING_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=GBB_LINEPACK_ZONES_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=VICGAS_HV_ZONE_MAPPING_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=VICGAS_TUOS_ZONE_MAPPING_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="surrogate_key"),
]

_SOURCE_FILE_DEPS = [
    TableColumnDep(asset_key=GBB_DEMAND_ZONE_MAPPING_KEY, column_name="source_file"),
    TableColumnDep(asset_key=GBB_LINEPACK_ZONES_KEY, column_name="source_file"),
    TableColumnDep(asset_key=VICGAS_HV_ZONE_MAPPING_KEY, column_name="source_file"),
    TableColumnDep(asset_key=VICGAS_TUOS_ZONE_MAPPING_KEY, column_name="source_file"),
    TableColumnDep(asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="source_file"),
]

_INGESTED_TIMESTAMP_DEPS = [
    TableColumnDep(
        asset_key=GBB_DEMAND_ZONE_MAPPING_KEY, column_name="ingested_timestamp"
    ),
    TableColumnDep(asset_key=GBB_LINEPACK_ZONES_KEY, column_name="ingested_timestamp"),
    TableColumnDep(
        asset_key=VICGAS_HV_ZONE_MAPPING_KEY, column_name="ingested_timestamp"
    ),
    TableColumnDep(
        asset_key=VICGAS_TUOS_ZONE_MAPPING_KEY, column_name="ingested_timestamp"
    ),
    TableColumnDep(
        asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="ingested_timestamp"
    ),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_ZONE_ID_DEPS,
        "source_zone_id": _SOURCE_ZONE_ID_DEPS,
        "zone_name": [
            TableColumnDep(
                asset_key=GBB_DEMAND_ZONE_MAPPING_KEY, column_name="DemandZone"
            ),
            TableColumnDep(
                asset_key=GBB_LINEPACK_ZONES_KEY, column_name="LinepackZone"
            ),
            TableColumnDep(
                asset_key=VICGAS_HV_ZONE_MAPPING_KEY, column_name="hv_zone_desc"
            ),
            TableColumnDep(
                asset_key=VICGAS_TUOS_ZONE_MAPPING_KEY, column_name="tuos_zone_desc"
            ),
            TableColumnDep(
                asset_key=VICGAS_PIPE_SEGMENTS_KEY, column_name="linepack_zone_id"
            ),
        ],
        "zone_description": [
            TableColumnDep(
                asset_key=GBB_LINEPACK_ZONES_KEY,
                column_name="LinepackZoneDescription",
            ),
            TableColumnDep(
                asset_key=VICGAS_HV_ZONE_MAPPING_KEY, column_name="hv_zone_desc"
            ),
            TableColumnDep(
                asset_key=VICGAS_TUOS_ZONE_MAPPING_KEY, column_name="tuos_zone_desc"
            ),
        ],
        "source_surrogate_keys": _SOURCE_SURROGATE_KEY_DEPS,
        "source_files": _SOURCE_FILE_DEPS,
        "ingested_timestamp": _INGESTED_TIMESTAMP_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "zone_type": pl.String,
    "source_zone_id": pl.String,
    "zone_name": pl.String,
    "zone_description": pl.String,
    "source_surrogate_keys": pl.List(pl.String),
    "source_files": pl.List(pl.String),
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver dimension primary key generated by surrogate_key_sources.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the gas model row.",
    "zone_type": "Canonical zone type.",
    "source_zone_id": "Source-system zone identifier.",
    "zone_name": "Zone name.",
    "zone_description": "Zone description.",
    "source_surrogate_keys": "Source row surrogate keys for lineage.",
    "source_files": "Archived source files contributing to the row.",
    "ingested_timestamp": "Latest contributing bronze row ingestion timestamp.",
}

REQUIRED_COLUMNS = ["surrogate_key", "source_system", "zone_type", "source_zone_id"]


def _gbb_demand_zones(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit("GBB"),
        source_tables=pl.lit(
            [
                "silver.gbb.silver_gasbb_demand_zones_and_pipeline_connectionpoint_mapping"
            ]
        ).cast(pl.List(pl.String)),
        zone_type=pl.lit("demand_zone"),
        source_zone_id=pl.col("DemandZone").cast(pl.String),
        zone_name=pl.col("DemandZone").cast(pl.String),
        zone_description=pl.lit(None).cast(pl.String),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _gbb_linepack_zones(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit("GBB"),
        source_tables=pl.lit(["silver.gbb.silver_gasbb_linepack_zones"]).cast(
            pl.List(pl.String)
        ),
        zone_type=pl.lit("linepack_zone"),
        source_zone_id=pl.col("LinepackZone").cast(pl.String),
        zone_name=pl.col("LinepackZone").cast(pl.String),
        zone_description=pl.col("LinepackZoneDescription").cast(pl.String),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _vicgas_hv_zones(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit("VICGAS"),
        source_tables=pl.lit(
            ["silver.vicgas.silver_int188_v4_ctm_to_hv_zone_mapping_1"]
        ).cast(pl.List(pl.String)),
        zone_type=pl.lit("heating_value_zone"),
        source_zone_id=pl.col("hv_zone").cast(pl.String),
        zone_name=pl.col("hv_zone_desc").cast(pl.String),
        zone_description=pl.col("hv_zone_desc").cast(pl.String),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _vicgas_tuos_zones(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit("VICGAS"),
        source_tables=pl.lit(
            ["silver.vicgas.silver_int284_v4_tuos_zone_postcode_map_1"]
        ).cast(pl.List(pl.String)),
        zone_type=pl.lit("tuos_zone"),
        source_zone_id=pl.col("tuos_zone").cast(pl.String),
        zone_name=pl.col("tuos_zone_desc").cast(pl.String),
        zone_description=pl.col("tuos_zone_desc").cast(pl.String),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _vicgas_linepack_zones(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit("VICGAS"),
        source_tables=pl.lit(["silver.vicgas.silver_int259_v4_pipe_segment_1"]).cast(
            pl.List(pl.String)
        ),
        zone_type=pl.lit("linepack_zone"),
        source_zone_id=pl.col("linepack_zone_id").cast(pl.String),
        zone_name=pl.col("linepack_zone_id").cast(pl.String),
        zone_description=pl.lit(None).cast(pl.String),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _select_current_zones(
    gbb_demand_zone_mapping: LazyFrame,
    gbb_linepack_zones: LazyFrame,
    vicgas_hv_zone_mapping: LazyFrame,
    vicgas_tuos_zone_mapping: LazyFrame,
    vicgas_pipe_segments: LazyFrame,
) -> LazyFrame:
    combined = pl.concat(
        [
            _gbb_demand_zones(gbb_demand_zone_mapping),
            _gbb_linepack_zones(gbb_linepack_zones),
            _vicgas_hv_zones(vicgas_hv_zone_mapping),
            _vicgas_tuos_zones(vicgas_tuos_zone_mapping),
            _vicgas_linepack_zones(vicgas_pipe_segments),
        ],
        how="diagonal_relaxed",
    )
    return (
        combined.group_by(SURROGATE_KEY_SOURCES)
        .agg(
            source_tables=pl.col("source_tables")
            .explode()
            .drop_nulls()
            .unique()
            .sort(),
            zone_name=pl.col("zone_name").drop_nulls().first(),
            zone_description=pl.col("zone_description").drop_nulls().first(),
            source_surrogate_keys=pl.col("source_surrogate_key")
            .drop_nulls()
            .unique()
            .sort(),
            source_files=pl.col("source_file").drop_nulls().unique().sort(),
            ingested_timestamp=pl.col("ingested_timestamp").max(),
        )
        .with_columns(surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES))
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
    description="Silver current-snapshot gas zone dimension.",
    ins={
        "gbb_demand_zone_mapping": AssetIn(key=GBB_DEMAND_ZONE_MAPPING_KEY),
        "gbb_linepack_zones": AssetIn(key=GBB_LINEPACK_ZONES_KEY),
        "vicgas_hv_zone_mapping": AssetIn(key=VICGAS_HV_ZONE_MAPPING_KEY),
        "vicgas_tuos_zone_mapping": AssetIn(key=VICGAS_TUOS_ZONE_MAPPING_KEY),
        "vicgas_pipe_segments": AssetIn(key=VICGAS_PIPE_SEGMENTS_KEY),
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
def silver_gas_dim_zone(
    gbb_demand_zone_mapping: LazyFrame,
    gbb_linepack_zones: LazyFrame,
    vicgas_hv_zone_mapping: LazyFrame,
    vicgas_tuos_zone_mapping: LazyFrame,
    vicgas_pipe_segments: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_current_zones(
            gbb_demand_zone_mapping,
            gbb_linepack_zones,
            vicgas_hv_zone_mapping,
            vicgas_tuos_zone_mapping,
            vicgas_pipe_segments,
        )
    )


@asset_check(
    asset=silver_gas_dim_zone,
    name="check_required_fields",
    description="Check required dimension fields are not null.",
)
def silver_gas_dim_zone_required_fields(input_df: LazyFrame) -> AssetCheckResult:
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


silver_gas_dim_zone_duplicate_row_check = duplicate_row_check_factory(
    assets_definition=silver_gas_dim_zone,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
    description="Check that surrogate_key is unique.",
)

silver_gas_dim_zone_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_zone,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)

silver_gas_dim_zone_schema_drift_check = schema_drift_check_factory(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_zone,
    check_name="check_schema_drift",
    description="Check for schema drift against the declared asset schema.",
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_dim_zone],
        asset_checks=[
            silver_gas_dim_zone_duplicate_row_check,
            silver_gas_dim_zone_schema_check,
            silver_gas_dim_zone_schema_drift_check,
            silver_gas_dim_zone_required_fields,
        ],
    )
