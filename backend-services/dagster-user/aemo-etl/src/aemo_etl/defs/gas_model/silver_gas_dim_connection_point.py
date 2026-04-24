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
TABLE_NAME = "silver_gas_dim_connection_point"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one current row per source-qualified facility, connection point, and flow direction"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_facility_id",
    "source_connection_point_id",
    "flow_direction",
]
SOURCE_TABLES = [
    "silver.gbb.silver_gasbb_nodes_connection_points",
    "silver.gbb.silver_gasbb_demand_zones_and_pipeline_connectionpoint_mapping",
]
SOURCE_SYSTEM = "GBB"
GBB_NODES_CONNECTION_POINTS_KEY = AssetKey(
    ["silver", "gbb", "silver_gasbb_nodes_connection_points"]
)
GBB_DEMAND_ZONE_MAPPING_KEY = AssetKey(
    ["silver", "gbb", "silver_gasbb_demand_zones_and_pipeline_connectionpoint_mapping"]
)
FACILITIES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_facility"])
LOCATIONS_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_location"])
ZONES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_zone"])

_SURROGATE_KEY_DEPS = [
    TableColumnDep(asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="FacilityId"),
    TableColumnDep(
        asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="ConnectionPointId"
    ),
    TableColumnDep(
        asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="FlowDirection"
    ),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SURROGATE_KEY_DEPS,
        "facility_key": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="FacilityId"
            ),
            TableColumnDep(asset_key=FACILITIES_KEY, column_name="surrogate_key"),
        ],
        "location_key": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="LocationId"
            ),
            TableColumnDep(asset_key=LOCATIONS_KEY, column_name="surrogate_key"),
        ],
        "zone_key": [
            TableColumnDep(
                asset_key=GBB_DEMAND_ZONE_MAPPING_KEY, column_name="DemandZone"
            ),
            TableColumnDep(asset_key=ZONES_KEY, column_name="surrogate_key"),
        ],
        "source_facility_id": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="FacilityId"
            )
        ],
        "source_connection_point_id": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY,
                column_name="ConnectionPointId",
            )
        ],
        "source_node_id": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="NodeId"
            )
        ],
        "source_location_id": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="LocationId"
            )
        ],
        "connection_point_name": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY,
                column_name="ConnectionPointName",
            )
        ],
        "flow_direction": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY,
                column_name="FlowDirection",
            )
        ],
        "facility_name": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="FacilityName"
            )
        ],
        "location_name": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="LocationName"
            )
        ],
        "state": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="StateName"
            )
        ],
        "exempt": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="Exempt"
            )
        ],
        "exemption_description": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY,
                column_name="ExemptionDescription",
            )
        ],
        "effective_date": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="EffectiveDate"
            )
        ],
        "source_last_updated": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="LastUpdated"
            )
        ],
        "source_last_updated_timestamp": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="LastUpdated"
            )
        ],
        "source_surrogate_key": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="surrogate_key"
            )
        ],
        "source_file": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY, column_name="source_file"
            )
        ],
        "ingested_timestamp": [
            TableColumnDep(
                asset_key=GBB_NODES_CONNECTION_POINTS_KEY,
                column_name="ingested_timestamp",
            )
        ],
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "facility_key": pl.String,
    "location_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_facility_id": pl.String,
    "source_connection_point_id": pl.String,
    "source_node_id": pl.String,
    "source_location_id": pl.String,
    "connection_point_name": pl.String,
    "flow_direction": pl.String,
    "facility_name": pl.String,
    "location_name": pl.String,
    "state": pl.String,
    "exempt": pl.Boolean,
    "exemption_description": pl.String,
    "effective_date": pl.Date,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver dimension primary key generated by surrogate_key_sources.",
    "facility_key": "Parent silver_gas_dim_facility surrogate_key.",
    "location_key": "Parent silver_gas_dim_location surrogate_key.",
    "zone_key": "Parent silver_gas_dim_zone surrogate_key when mapped.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the gas model row.",
    "source_facility_id": "Source-system facility identifier.",
    "source_connection_point_id": "Source-system connection point identifier.",
    "source_node_id": "Source-system node identifier.",
    "source_location_id": "Source-system location identifier.",
    "connection_point_name": "Connection point name.",
    "flow_direction": "Gas flow direction.",
    "facility_name": "Source facility name.",
    "location_name": "Source location name.",
    "state": "Source state.",
    "exempt": "Flag indicating whether the connection point has a data exemption.",
    "exemption_description": "Source exemption description.",
    "effective_date": "Parsed effective date.",
    "source_last_updated": "Raw source update value.",
    "source_last_updated_timestamp": "Parsed source update timestamp.",
    "source_surrogate_key": "Source row surrogate key for lineage.",
    "source_file": "Archived source file for the bronze row.",
    "ingested_timestamp": "Timestamp when the bronze row was ingested.",
}

REQUIRED_COLUMNS = [
    "surrogate_key",
    "source_system",
    "source_facility_id",
    "source_connection_point_id",
    "flow_direction",
]


def _parse_datetime(column: str) -> pl.Expr:
    source = pl.col(column).cast(pl.String)
    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %b %Y %H:%M:%S", strict=False),
    )


def _parse_date(column: str) -> pl.Expr:
    return _parse_datetime(column).dt.date()


def _demand_zone_mapping(df: LazyFrame) -> LazyFrame:
    return (
        df.select(
            source_facility_id=pl.col("FacilityId").cast(pl.String),
            source_connection_point_id=pl.col("ConnectionPointId").cast(pl.String),
            flow_direction=pl.col("FlowDirection").cast(pl.String),
            source_zone_id=pl.col("DemandZone").cast(pl.String),
        )
        .unique(
            subset=[
                "source_facility_id",
                "source_connection_point_id",
                "flow_direction",
            ],
            keep="first",
        )
        .with_columns(
            source_system=pl.lit(SOURCE_SYSTEM),
            zone_type=pl.lit("demand_zone"),
        )
    )


def _select_current_connection_points(
    gbb_nodes_connection_points: LazyFrame,
    gbb_demand_zone_mapping: LazyFrame,
    facilities: LazyFrame,
    locations: LazyFrame,
    zones: LazyFrame,
) -> LazyFrame:
    facility_keys = facilities.select(
        facility_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        source_facility_id=pl.col("source_facility_id"),
    )
    location_keys = locations.select(
        location_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        source_location_id=pl.col("source_location_id"),
    )
    zone_keys = zones.filter(pl.col("zone_type") == "demand_zone").select(
        zone_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        zone_type=pl.col("zone_type"),
        source_zone_id=pl.col("source_zone_id"),
    )
    return (
        gbb_nodes_connection_points.with_columns(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit(SOURCE_TABLES).cast(pl.List(pl.String)),
            source_facility_id=pl.col("FacilityId").cast(pl.String),
            source_connection_point_id=pl.col("ConnectionPointId").cast(pl.String),
            source_node_id=pl.col("NodeId").cast(pl.String),
            source_location_id=pl.col("LocationId").cast(pl.String),
            connection_point_name=pl.col("ConnectionPointName").cast(pl.String),
            flow_direction=pl.col("FlowDirection").cast(pl.String),
            facility_name=pl.col("FacilityName").cast(pl.String),
            location_name=pl.col("LocationName").cast(pl.String),
            state=pl.col("StateName").cast(pl.String),
            exempt=pl.col("Exempt").cast(pl.Boolean),
            exemption_description=pl.col("ExemptionDescription").cast(pl.String),
            effective_date=_parse_date("EffectiveDate"),
            source_last_updated=pl.col("LastUpdated").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("LastUpdated"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        )
        .with_columns(surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES))
        .sort(
            [
                "source_system",
                "source_facility_id",
                "source_connection_point_id",
                "flow_direction",
                "source_last_updated_timestamp",
                "effective_date",
                "ingested_timestamp",
            ],
            descending=[False, False, False, False, True, True, True],
            nulls_last=True,
        )
        .unique(subset=SURROGATE_KEY_SOURCES, keep="first", maintain_order=True)
        .join(
            _demand_zone_mapping(gbb_demand_zone_mapping),
            on=[
                "source_system",
                "source_facility_id",
                "source_connection_point_id",
                "flow_direction",
            ],
            how="left",
        )
        .join(facility_keys, on=["source_system", "source_facility_id"], how="left")
        .join(location_keys, on=["source_system", "source_location_id"], how="left")
        .join(
            zone_keys,
            on=["source_system", "zone_type", "source_zone_id"],
            how="left",
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
    description="Silver current-snapshot gas connection point dimension.",
    ins={
        "gbb_nodes_connection_points": AssetIn(key=GBB_NODES_CONNECTION_POINTS_KEY),
        "gbb_demand_zone_mapping": AssetIn(key=GBB_DEMAND_ZONE_MAPPING_KEY),
        "facilities": AssetIn(key=FACILITIES_KEY),
        "locations": AssetIn(key=LOCATIONS_KEY),
        "zones": AssetIn(key=ZONES_KEY),
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
def silver_gas_dim_connection_point(
    gbb_nodes_connection_points: LazyFrame,
    gbb_demand_zone_mapping: LazyFrame,
    facilities: LazyFrame,
    locations: LazyFrame,
    zones: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    return _materialize_result(
        _select_current_connection_points(
            gbb_nodes_connection_points,
            gbb_demand_zone_mapping,
            facilities,
            locations,
            zones,
        )
    )


@asset_check(
    asset=silver_gas_dim_connection_point,
    name="check_required_fields",
    description="Check required dimension fields are not null.",
)
def silver_gas_dim_connection_point_required_fields(
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


silver_gas_dim_connection_point_duplicate_row_check = duplicate_row_check_factory(
    assets_definition=silver_gas_dim_connection_point,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
    description="Check that surrogate_key is unique.",
)

silver_gas_dim_connection_point_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_connection_point,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)

silver_gas_dim_connection_point_schema_drift_check = schema_drift_check_factory(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_connection_point,
    check_name="check_schema_drift",
    description="Check for schema drift against the declared asset schema.",
)


@definitions
def defs() -> Definitions:
    return Definitions(
        assets=[silver_gas_dim_connection_point],
        asset_checks=[
            silver_gas_dim_connection_point_duplicate_row_check,
            silver_gas_dim_connection_point_schema_check,
            silver_gas_dim_connection_point_schema_drift_check,
            silver_gas_dim_connection_point_required_fields,
        ],
    )
