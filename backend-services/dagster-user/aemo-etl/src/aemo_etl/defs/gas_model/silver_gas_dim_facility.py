"""Dagster definitions for the silver gas facility dimension asset."""

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
TABLE_NAME = "silver_gas_dim_facility"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one current row per source-qualified gas facility and optional hub"
SURROGATE_KEY_SOURCES = ["source_system", "source_facility_id", "source_hub_id"]
SOURCE_TABLES = [
    "silver.gbb.silver_gasbb_facilities",
    "silver.sttm.silver_int671_v1_hub_facility_definition_rpt_1",
    "silver.sttm.silver_int687_v1_facility_hub_capacity_data_rpt_1",
]
SOURCE_SYSTEM = "GBB"
GBB_FACILITIES_KEY = AssetKey(["silver", "gbb", "silver_gasbb_facilities"])
STTM_HUB_FACILITY_DEFINITION_KEY = AssetKey(
    ["silver", "sttm", "silver_int671_v1_hub_facility_definition_rpt_1"]
)
STTM_FACILITY_HUB_CAPACITY_KEY = AssetKey(
    ["silver", "sttm", "silver_int687_v1_facility_hub_capacity_data_rpt_1"]
)
PARTICIPANTS_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_participant"])
ZONES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_zone"])

_SOURCE_FACILITY_ID_DEPS = [
    TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="FacilityId"),
    TableColumnDep(
        asset_key=STTM_HUB_FACILITY_DEFINITION_KEY, column_name="facility_identifier"
    ),
    TableColumnDep(
        asset_key=STTM_FACILITY_HUB_CAPACITY_KEY, column_name="facility_identifier"
    ),
]

_SOURCE_HUB_ID_DEPS = [
    TableColumnDep(
        asset_key=STTM_HUB_FACILITY_DEFINITION_KEY, column_name="hub_identifier"
    ),
    TableColumnDep(
        asset_key=STTM_FACILITY_HUB_CAPACITY_KEY, column_name="hub_identifier"
    ),
]

_FACILITY_NAME_DEPS = [
    TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="FacilityName"),
    TableColumnDep(
        asset_key=STTM_HUB_FACILITY_DEFINITION_KEY, column_name="facility_name"
    ),
    TableColumnDep(
        asset_key=STTM_FACILITY_HUB_CAPACITY_KEY, column_name="facility_name"
    ),
]

_FACILITY_TYPE_DEPS = [
    TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="FacilityType"),
    TableColumnDep(
        asset_key=STTM_HUB_FACILITY_DEFINITION_KEY, column_name="facility_type"
    ),
]

_LAST_UPDATED_DEPS = [
    TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="LastUpdated"),
    TableColumnDep(
        asset_key=STTM_HUB_FACILITY_DEFINITION_KEY,
        column_name="last_update_datetime",
    ),
    TableColumnDep(
        asset_key=STTM_FACILITY_HUB_CAPACITY_KEY,
        column_name="last_update_datetime",
    ),
]

_SOURCE_SURROGATE_KEY_DEPS = [
    TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="surrogate_key"),
    TableColumnDep(
        asset_key=STTM_HUB_FACILITY_DEFINITION_KEY, column_name="surrogate_key"
    ),
    TableColumnDep(
        asset_key=STTM_FACILITY_HUB_CAPACITY_KEY, column_name="surrogate_key"
    ),
]

_SOURCE_FILE_DEPS = [
    TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="source_file"),
    TableColumnDep(
        asset_key=STTM_HUB_FACILITY_DEFINITION_KEY, column_name="source_file"
    ),
    TableColumnDep(asset_key=STTM_FACILITY_HUB_CAPACITY_KEY, column_name="source_file"),
]

_INGESTED_TIMESTAMP_DEPS = [
    TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="ingested_timestamp"),
    TableColumnDep(
        asset_key=STTM_HUB_FACILITY_DEFINITION_KEY,
        column_name="ingested_timestamp",
    ),
    TableColumnDep(
        asset_key=STTM_FACILITY_HUB_CAPACITY_KEY,
        column_name="ingested_timestamp",
    ),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": [*_SOURCE_FACILITY_ID_DEPS, *_SOURCE_HUB_ID_DEPS],
        "participant_key": [
            TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="OperatorId"),
            TableColumnDep(asset_key=PARTICIPANTS_KEY, column_name="surrogate_key"),
        ],
        "zone_key": [
            *_SOURCE_HUB_ID_DEPS,
            TableColumnDep(asset_key=ZONES_KEY, column_name="surrogate_key"),
        ],
        "source_hub_id": _SOURCE_HUB_ID_DEPS,
        "source_hub_name": [
            TableColumnDep(
                asset_key=STTM_HUB_FACILITY_DEFINITION_KEY, column_name="hub_name"
            ),
            TableColumnDep(
                asset_key=STTM_FACILITY_HUB_CAPACITY_KEY, column_name="hub_name"
            ),
        ],
        "source_facility_id": _SOURCE_FACILITY_ID_DEPS,
        "facility_name": _FACILITY_NAME_DEPS,
        "facility_short_name": [
            TableColumnDep(
                asset_key=GBB_FACILITIES_KEY, column_name="FacilityShortName"
            )
        ],
        "facility_type": _FACILITY_TYPE_DEPS,
        "facility_type_description": [
            TableColumnDep(
                asset_key=GBB_FACILITIES_KEY, column_name="FacilityTypeDescription"
            )
        ],
        "operating_state": [
            TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="OperatingState")
        ],
        "operating_state_date": [
            TableColumnDep(
                asset_key=GBB_FACILITIES_KEY, column_name="OperatingStateDate"
            )
        ],
        "operator_name": [
            TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="OperatorName")
        ],
        "source_operator_id": [
            TableColumnDep(asset_key=GBB_FACILITIES_KEY, column_name="OperatorId")
        ],
        "operator_change_date": [
            TableColumnDep(
                asset_key=GBB_FACILITIES_KEY, column_name="OperatorChangeDate"
            )
        ],
        "capacity_effective_from_date": [
            TableColumnDep(
                asset_key=STTM_FACILITY_HUB_CAPACITY_KEY,
                column_name="effective_from_date",
            )
        ],
        "capacity_effective_to_date": [
            TableColumnDep(
                asset_key=STTM_FACILITY_HUB_CAPACITY_KEY,
                column_name="effective_to_date",
            )
        ],
        "default_capacity": [
            TableColumnDep(
                asset_key=STTM_FACILITY_HUB_CAPACITY_KEY,
                column_name="default_capacity",
            )
        ],
        "maximum_capacity": [
            TableColumnDep(
                asset_key=STTM_FACILITY_HUB_CAPACITY_KEY,
                column_name="maximum_capacity",
            )
        ],
        "high_capacity_threshold": [
            TableColumnDep(
                asset_key=STTM_FACILITY_HUB_CAPACITY_KEY,
                column_name="high_capacity_threshold",
            )
        ],
        "low_capacity_threshold": [
            TableColumnDep(
                asset_key=STTM_FACILITY_HUB_CAPACITY_KEY,
                column_name="low_capacity_threshold",
            )
        ],
        "source_last_updated": _LAST_UPDATED_DEPS,
        "source_last_updated_timestamp": _LAST_UPDATED_DEPS,
        "source_surrogate_key": _SOURCE_SURROGATE_KEY_DEPS,
        "source_surrogate_keys": _SOURCE_SURROGATE_KEY_DEPS,
        "source_file": _SOURCE_FILE_DEPS,
        "source_files": _SOURCE_FILE_DEPS,
        "ingested_timestamp": _INGESTED_TIMESTAMP_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "participant_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "facility_short_name": pl.String,
    "facility_type": pl.String,
    "facility_type_description": pl.String,
    "operating_state": pl.String,
    "operating_state_date": pl.Date,
    "operator_name": pl.String,
    "source_operator_id": pl.String,
    "operator_change_date": pl.Date,
    "capacity_effective_from_date": pl.Date,
    "capacity_effective_to_date": pl.Date,
    "default_capacity": pl.Float64,
    "maximum_capacity": pl.Float64,
    "high_capacity_threshold": pl.Float64,
    "low_capacity_threshold": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_surrogate_keys": pl.List(pl.String),
    "source_file": pl.String,
    "source_files": pl.List(pl.String),
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver dimension primary key generated by surrogate_key_sources.",
    "participant_key": "Operator participant surrogate key when resolvable.",
    "zone_key": "Parent silver_gas_dim_zone surrogate_key for hub when resolvable.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the gas model row.",
    "source_hub_id": "Source-system hub identifier where the facility is hub-scoped.",
    "source_hub_name": "Source-system hub name where the facility is hub-scoped.",
    "source_facility_id": "Source-system facility identifier.",
    "facility_name": "Facility name.",
    "facility_short_name": "Facility short name.",
    "facility_type": "Facility type.",
    "facility_type_description": "Facility type description.",
    "operating_state": "Facility operating state.",
    "operating_state_date": "Parsed date the current operating state was set.",
    "operator_name": "Facility operator name.",
    "source_operator_id": "Source-system operator company identifier.",
    "operator_change_date": "Parsed date the operator changed.",
    "capacity_effective_from_date": "Parsed first gas date for the current STTM capacity context.",
    "capacity_effective_to_date": "Parsed last gas date for the current STTM capacity context.",
    "default_capacity": "Current STTM default registered facility capacity.",
    "maximum_capacity": "Current STTM maximum registered facility capacity.",
    "high_capacity_threshold": "Current STTM registered high capacity threshold.",
    "low_capacity_threshold": "Current STTM registered low capacity threshold.",
    "source_last_updated": "Raw source update value.",
    "source_last_updated_timestamp": "Parsed source update timestamp.",
    "source_surrogate_key": "Source row surrogate key for lineage.",
    "source_surrogate_keys": "Source row surrogate keys contributing to the row.",
    "source_file": "Archived source file for the source row.",
    "source_files": "Archived source files contributing to the row.",
    "ingested_timestamp": "Timestamp when the source row was ingested.",
}

REQUIRED_COLUMNS = [
    "surrogate_key",
    "source_system",
    "source_facility_id",
    "facility_name",
]


def _parse_datetime(column: str) -> pl.Expr:
    source = pl.col(column).cast(pl.String)
    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%d %b %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y-%m-%d %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y-%m-%d", strict=False),
    )


def _parse_date(column: str) -> pl.Expr:
    return _parse_datetime(column).dt.date()


def _parse_float(column: str) -> pl.Expr:
    return pl.col(column).cast(pl.Float64, strict=False)


def _first_non_null(column: str) -> pl.Expr:
    return pl.col(column).drop_nulls().first()


def _gbb_facilities(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit(["silver.gbb.silver_gasbb_facilities"]).cast(
            pl.List(pl.String)
        ),
        source_hub_id=pl.lit(None).cast(pl.String),
        source_hub_name=pl.lit(None).cast(pl.String),
        zone_type=pl.lit(None).cast(pl.String),
        source_facility_id=pl.col("FacilityId").cast(pl.String),
        facility_name=pl.col("FacilityName").cast(pl.String),
        facility_short_name=pl.col("FacilityShortName").cast(pl.String),
        facility_type=pl.col("FacilityType").cast(pl.String),
        facility_type_description=pl.col("FacilityTypeDescription").cast(pl.String),
        operating_state=pl.col("OperatingState").cast(pl.String),
        operating_state_date=_parse_date("OperatingStateDate"),
        operator_name=pl.col("OperatorName").cast(pl.String),
        source_operator_id=pl.col("OperatorId").cast(pl.String),
        operator_change_date=_parse_date("OperatorChangeDate"),
        capacity_effective_from_date=pl.lit(None).cast(pl.Date),
        capacity_effective_to_date=pl.lit(None).cast(pl.Date),
        default_capacity=pl.lit(None).cast(pl.Float64),
        maximum_capacity=pl.lit(None).cast(pl.Float64),
        high_capacity_threshold=pl.lit(None).cast(pl.Float64),
        low_capacity_threshold=pl.lit(None).cast(pl.Float64),
        source_last_updated=pl.col("LastUpdated").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("LastUpdated"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _sttm_facility_definitions(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit("STTM"),
        source_tables=pl.lit(
            ["silver.sttm.silver_int671_v1_hub_facility_definition_rpt_1"]
        ).cast(pl.List(pl.String)),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        zone_type=pl.lit("sttm_hub"),
        source_facility_id=pl.col("facility_identifier").cast(pl.String),
        facility_name=pl.col("facility_name").cast(pl.String),
        facility_short_name=pl.lit(None).cast(pl.String),
        facility_type=pl.col("facility_type").cast(pl.String),
        facility_type_description=pl.lit(None).cast(pl.String),
        operating_state=pl.lit(None).cast(pl.String),
        operating_state_date=pl.lit(None).cast(pl.Date),
        operator_name=pl.lit(None).cast(pl.String),
        source_operator_id=pl.lit(None).cast(pl.String),
        operator_change_date=pl.lit(None).cast(pl.Date),
        capacity_effective_from_date=pl.lit(None).cast(pl.Date),
        capacity_effective_to_date=pl.lit(None).cast(pl.Date),
        default_capacity=pl.lit(None).cast(pl.Float64),
        maximum_capacity=pl.lit(None).cast(pl.Float64),
        high_capacity_threshold=pl.lit(None).cast(pl.Float64),
        low_capacity_threshold=pl.lit(None).cast(pl.Float64),
        source_last_updated=pl.col("last_update_datetime").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("last_update_datetime"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _sttm_facility_capacity_context(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit("STTM"),
        source_tables=pl.lit(
            ["silver.sttm.silver_int687_v1_facility_hub_capacity_data_rpt_1"]
        ).cast(pl.List(pl.String)),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        zone_type=pl.lit("sttm_hub"),
        source_facility_id=pl.col("facility_identifier").cast(pl.String),
        facility_name=pl.col("facility_name").cast(pl.String),
        facility_short_name=pl.lit(None).cast(pl.String),
        facility_type=pl.lit(None).cast(pl.String),
        facility_type_description=pl.lit(None).cast(pl.String),
        operating_state=pl.lit(None).cast(pl.String),
        operating_state_date=pl.lit(None).cast(pl.Date),
        operator_name=pl.lit(None).cast(pl.String),
        source_operator_id=pl.lit(None).cast(pl.String),
        operator_change_date=pl.lit(None).cast(pl.Date),
        capacity_effective_from_date=_parse_date("effective_from_date"),
        capacity_effective_to_date=_parse_date("effective_to_date"),
        default_capacity=_parse_float("default_capacity"),
        maximum_capacity=_parse_float("maximum_capacity"),
        high_capacity_threshold=_parse_float("high_capacity_threshold"),
        low_capacity_threshold=_parse_float("low_capacity_threshold"),
        source_last_updated=pl.col("last_update_datetime").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("last_update_datetime"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _select_current_facilities(
    gbb_facilities: LazyFrame,
    participants: LazyFrame,
    zones: LazyFrame,
    sttm_hub_facility_definition: LazyFrame,
    sttm_facility_hub_capacity: LazyFrame,
) -> LazyFrame:
    participant_keys = participants.filter(
        pl.col("participant_identity_source") == "company_id"
    ).select(
        participant_key=pl.col("surrogate_key"),
        source_operator_id=pl.col("participant_identity_value"),
    )
    zone_keys = zones.filter(pl.col("zone_type") == "sttm_hub").select(
        zone_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        source_hub_id=pl.col("source_zone_id"),
    )
    combined = pl.concat(
        [
            _gbb_facilities(gbb_facilities),
            _sttm_facility_definitions(sttm_hub_facility_definition),
            _sttm_facility_capacity_context(sttm_facility_hub_capacity),
        ],
        how="diagonal_relaxed",
    )
    return (
        combined.sort(
            [
                "source_system",
                "source_facility_id",
                "source_hub_id",
                "source_last_updated_timestamp",
                "capacity_effective_from_date",
                "operating_state_date",
                "ingested_timestamp",
            ],
            descending=[False, False, False, True, True, True, True],
            nulls_last=True,
        )
        .group_by(SURROGATE_KEY_SOURCES, maintain_order=True)
        .agg(
            source_tables=pl.col("source_tables")
            .explode()
            .drop_nulls()
            .unique()
            .sort(),
            source_hub_name=_first_non_null("source_hub_name"),
            zone_type=_first_non_null("zone_type"),
            facility_name=_first_non_null("facility_name"),
            facility_short_name=_first_non_null("facility_short_name"),
            facility_type=_first_non_null("facility_type"),
            facility_type_description=_first_non_null("facility_type_description"),
            operating_state=_first_non_null("operating_state"),
            operating_state_date=_first_non_null("operating_state_date"),
            operator_name=_first_non_null("operator_name"),
            source_operator_id=_first_non_null("source_operator_id"),
            operator_change_date=_first_non_null("operator_change_date"),
            capacity_effective_from_date=_first_non_null(
                "capacity_effective_from_date"
            ),
            capacity_effective_to_date=_first_non_null("capacity_effective_to_date"),
            default_capacity=_first_non_null("default_capacity"),
            maximum_capacity=_first_non_null("maximum_capacity"),
            high_capacity_threshold=_first_non_null("high_capacity_threshold"),
            low_capacity_threshold=_first_non_null("low_capacity_threshold"),
            source_last_updated=_first_non_null("source_last_updated"),
            source_last_updated_timestamp=_first_non_null(
                "source_last_updated_timestamp"
            ),
            source_surrogate_key=_first_non_null("source_surrogate_key"),
            source_surrogate_keys=pl.col("source_surrogate_key")
            .drop_nulls()
            .unique()
            .sort(),
            source_file=_first_non_null("source_file"),
            source_files=pl.col("source_file").drop_nulls().unique().sort(),
            ingested_timestamp=pl.col("ingested_timestamp").max(),
        )
        .with_columns(surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES))
        .sort(
            [
                "source_system",
                "source_facility_id",
                "source_hub_id",
            ],
            nulls_last=True,
        )
        .join(participant_keys, on="source_operator_id", how="left")
        .join(zone_keys, on=["source_system", "source_hub_id"], how="left")
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
    description="Silver current-snapshot gas facility dimension.",
    ins={
        "gbb_facilities": AssetIn(key=GBB_FACILITIES_KEY),
        "participants": AssetIn(key=PARTICIPANTS_KEY),
        "zones": AssetIn(key=ZONES_KEY),
        "sttm_hub_facility_definition": AssetIn(key=STTM_HUB_FACILITY_DEFINITION_KEY),
        "sttm_facility_hub_capacity": AssetIn(key=STTM_FACILITY_HUB_CAPACITY_KEY),
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
def silver_gas_dim_facility(
    gbb_facilities: LazyFrame,
    participants: LazyFrame,
    zones: LazyFrame,
    sttm_hub_facility_definition: LazyFrame,
    sttm_facility_hub_capacity: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver gas facility dimension asset."""
    return _materialize_result(
        _select_current_facilities(
            gbb_facilities,
            participants,
            zones,
            sttm_hub_facility_definition,
            sttm_facility_hub_capacity,
        )
    )


@asset_check(
    asset=silver_gas_dim_facility,
    name="check_required_fields",
    description="Check required dimension fields are not null.",
)
def silver_gas_dim_facility_required_fields(input_df: LazyFrame) -> AssetCheckResult:
    """Validate required fields for the silver gas facility dimension asset."""
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


silver_gas_dim_facility_duplicate_row_check = duplicate_row_check_factory(
    assets_definition=silver_gas_dim_facility,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
    description="Check that surrogate_key is unique.",
)

silver_gas_dim_facility_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_facility,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)

silver_gas_dim_facility_schema_drift_check = schema_drift_check_factory(
    schema=SCHEMA,
    assets_definition=silver_gas_dim_facility,
    check_name="check_schema_drift",
    description="Check for schema drift against the declared asset schema.",
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver gas facility dimension asset."""
    return Definitions(
        assets=[silver_gas_dim_facility],
        asset_checks=[
            silver_gas_dim_facility_duplicate_row_check,
            silver_gas_dim_facility_schema_check,
            silver_gas_dim_facility_schema_drift_check,
            silver_gas_dim_facility_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_dim_facility_sensor",
                target=[silver_gas_dim_facility.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
