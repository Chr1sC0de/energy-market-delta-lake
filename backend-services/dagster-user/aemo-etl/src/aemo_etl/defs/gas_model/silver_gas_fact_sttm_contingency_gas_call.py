"""Dagster definitions for the silver STTM contingency gas call fact asset."""

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
TABLE_NAME = "silver_gas_fact_sttm_contingency_gas_call"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one STTM contingency gas quantity measure at its accepted source grain"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "source_report_id",
    "gas_date",
    "contingency_grain",
    "quantity_type",
    "source_hub_id",
    "source_facility_id",
    "flow_direction",
    "bid_offer_type",
    "contingency_call_id",
    "contingency_bid_offer_id",
    "bid_step",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.sttm.silver_int661_v1_contingency_gas_called_scheduled_bid_offer_rpt_1",
    "silver.sttm.silver_int673_v1_total_contingency_bid_offer_rpt_1",
    "silver.sttm.silver_int674_v1_total_contingency_gas_schedules_rpt_1",
]
SOURCE_SYSTEM = "STTM"
INT661_KEY = AssetKey(
    [
        "silver",
        "sttm",
        "silver_int661_v1_contingency_gas_called_scheduled_bid_offer_rpt_1",
    ]
)
INT673_KEY = AssetKey(
    ["silver", "sttm", "silver_int673_v1_total_contingency_bid_offer_rpt_1"]
)
INT674_KEY = AssetKey(
    ["silver", "sttm", "silver_int674_v1_total_contingency_gas_schedules_rpt_1"]
)
PARTICIPANTS_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_participant"])
FACILITIES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_facility"])
ZONES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_zone"])

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT661_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT673_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT674_KEY, column_name="surrogate_key"),
]

_SOURCE_HUB_ID_DEPS = [
    TableColumnDep(asset_key=INT661_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT673_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT674_KEY, column_name="hub_identifier"),
]

_SOURCE_FACILITY_ID_DEPS = [
    TableColumnDep(asset_key=INT661_KEY, column_name="facility_identifier"),
    TableColumnDep(asset_key=INT674_KEY, column_name="facility_identifier"),
]

_QUANTITY_DEPS = [
    TableColumnDep(
        asset_key=INT661_KEY,
        column_name="contingency_gas_bid_offer_confirmed_step_quantity",
    ),
    TableColumnDep(
        asset_key=INT661_KEY,
        column_name="contingency_gas_bid_offer_called_step_quantity",
    ),
    TableColumnDep(asset_key=INT673_KEY, column_name="total_contingency_gas_bid_qty"),
    TableColumnDep(asset_key=INT673_KEY, column_name="total_contingency_gas_offer_qty"),
    TableColumnDep(
        asset_key=INT674_KEY,
        column_name="contingency_gas_bid_offer_called_quantity",
    ),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "participant_key": [
            TableColumnDep(asset_key=INT661_KEY, column_name="company_identifier"),
            TableColumnDep(asset_key=PARTICIPANTS_KEY, column_name="surrogate_key"),
        ],
        "facility_key": [
            *_SOURCE_HUB_ID_DEPS,
            *_SOURCE_FACILITY_ID_DEPS,
            TableColumnDep(asset_key=FACILITIES_KEY, column_name="surrogate_key"),
        ],
        "zone_key": [
            *_SOURCE_HUB_ID_DEPS,
            TableColumnDep(asset_key=ZONES_KEY, column_name="surrogate_key"),
        ],
        "source_hub_id": _SOURCE_HUB_ID_DEPS,
        "source_facility_id": _SOURCE_FACILITY_ID_DEPS,
        "quantity_gj": _QUANTITY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "participant_key": pl.String,
    "facility_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "source_report_id": pl.String,
    "gas_date": pl.Date,
    "contingency_grain": pl.String,
    "quantity_type": pl.String,
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "flow_direction": pl.String,
    "bid_offer_type": pl.String,
    "participant_id": pl.String,
    "participant_name": pl.String,
    "contingency_call_id": pl.String,
    "contingency_bid_offer_id": pl.String,
    "bid_step": pl.Int64,
    "bid_price": pl.Float64,
    "bid_qty_gj": pl.Float64,
    "quantity_gj": pl.Float64,
    "approval_timestamp": pl.Datetime("us"),
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver fact primary key generated by surrogate_key_sources.",
    "date_key": "Deterministic silver_gas_dim_date surrogate_key for gas_date.",
    "participant_key": "Parent silver_gas_dim_participant surrogate_key when resolvable.",
    "facility_key": "Parent silver_gas_dim_facility surrogate_key when resolvable.",
    "zone_key": "Parent silver_gas_dim_zone surrogate_key for STTM hub when resolvable.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the row.",
    "source_table": "Specific silver source table for this row.",
    "source_report_id": "STTM report identifier.",
    "gas_date": "Gas day date.",
    "contingency_grain": "Accepted source grain for the contingency quantity row.",
    "quantity_type": "Normalized contingency gas quantity measure type.",
    "source_hub_id": "Source-system hub identifier.",
    "source_hub_name": "Source-system hub name.",
    "source_facility_id": "Source-system facility identifier where present.",
    "facility_name": "Source-system facility name where present.",
    "flow_direction": "STTM source flow-direction flag where present.",
    "bid_offer_type": "Source bid or offer type flag where present.",
    "participant_id": "Source participant company identifier where present.",
    "participant_name": "Source participant company name where present.",
    "contingency_call_id": "Source contingency gas called schedule identifier.",
    "contingency_bid_offer_id": "Source contingency bid or offer identifier.",
    "bid_step": "Source contingency bid or offer step number.",
    "bid_price": "Source contingency bid or offer step price.",
    "bid_qty_gj": "Source contingency bid or offer cumulative step quantity.",
    "quantity_gj": "Contingency gas quantity value for quantity_type.",
    "approval_timestamp": "Parsed source approval timestamp where reported.",
    "source_last_updated": "Raw source update value.",
    "source_last_updated_timestamp": "Parsed source update timestamp.",
    "source_surrogate_key": "Source row surrogate key for lineage.",
    "source_file": "Archived source file for the source row.",
    "ingested_timestamp": "Timestamp when the source row was ingested.",
}

REQUIRED_COLUMNS = [
    "surrogate_key",
    "date_key",
    "source_system",
    "source_table",
    "source_report_id",
    "gas_date",
    "contingency_grain",
    "quantity_type",
    "source_hub_id",
    "quantity_gj",
    "source_surrogate_key",
]

_INT661_INDEX = [
    "source_system",
    "source_tables",
    "source_table",
    "source_report_id",
    "gas_date",
    "contingency_grain",
    "source_hub_id",
    "source_hub_name",
    "source_facility_id",
    "facility_name",
    "flow_direction",
    "bid_offer_type",
    "participant_id",
    "participant_name",
    "contingency_call_id",
    "contingency_bid_offer_id",
    "bid_step",
    "bid_price",
    "bid_qty_gj",
    "approval_timestamp",
    "source_last_updated",
    "source_last_updated_timestamp",
    "source_surrogate_key",
    "source_file",
    "ingested_timestamp",
]

_INT673_INDEX = [
    "source_system",
    "source_tables",
    "source_table",
    "source_report_id",
    "gas_date",
    "contingency_grain",
    "source_hub_id",
    "source_hub_name",
    "source_facility_id",
    "facility_name",
    "flow_direction",
    "participant_id",
    "participant_name",
    "contingency_call_id",
    "contingency_bid_offer_id",
    "bid_step",
    "bid_price",
    "bid_qty_gj",
    "approval_timestamp",
    "source_last_updated",
    "source_last_updated_timestamp",
    "source_surrogate_key",
    "source_file",
    "ingested_timestamp",
]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _called_scheduled_bid_offer_rows(df: LazyFrame) -> LazyFrame:
    return (
        df.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[0]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[0]),
            source_report_id=pl.lit("INT661"),
            gas_date=_parse_datetime("gas_date").dt.date(),
            contingency_grain=pl.lit("bid_offer_step"),
            source_hub_id=pl.col("hub_identifier").cast(pl.String),
            source_hub_name=pl.col("hub_name").cast(pl.String),
            source_facility_id=pl.col("facility_identifier").cast(pl.String),
            facility_name=pl.col("facility_name").cast(pl.String),
            flow_direction=pl.col("flow_direction").cast(pl.String),
            bid_offer_type=pl.col("contingency_gas_bid_offer_type").cast(pl.String),
            participant_id=pl.col("company_identifier").cast(pl.String),
            participant_name=pl.col("company_name").cast(pl.String),
            contingency_call_id=pl.col("contingency_gas_called_identifier").cast(
                pl.String
            ),
            contingency_bid_offer_id=pl.col(
                "contingency_gas_bid_offer_identifier"
            ).cast(pl.String),
            bid_step=pl.col("contingency_gas_bid_offer_step_number").cast(pl.Int64),
            bid_price=pl.col("contingency_gas_bid_offer_step_price").cast(pl.Float64),
            bid_qty_gj=pl.col("contingency_gas_bid_offer_step_quantity").cast(
                pl.Float64
            ),
            approval_timestamp=_parse_datetime("approval_datetime"),
            source_last_updated=pl.col("report_datetime").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("report_datetime"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
            confirmed_step_quantity=pl.col(
                "contingency_gas_bid_offer_confirmed_step_quantity"
            ).cast(pl.Float64),
            called_step_quantity=pl.col(
                "contingency_gas_bid_offer_called_step_quantity"
            ).cast(pl.Float64),
        )
        .unpivot(
            index=_INT661_INDEX,
            on=["confirmed_step_quantity", "called_step_quantity"],
            variable_name="quantity_type",
            value_name="quantity_gj",
        )
        .with_columns(
            quantity_type=pl.col("quantity_type").replace(
                {
                    "confirmed_step_quantity": "confirmed_step_quantity",
                    "called_step_quantity": "called_step_quantity",
                }
            )
        )
        .filter(pl.col("quantity_gj").is_not_null())
    )


def _total_contingency_bid_offer_rows(df: LazyFrame) -> LazyFrame:
    return (
        df.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[1]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[1]),
            source_report_id=pl.lit("INT673"),
            gas_date=_parse_datetime("gas_date").dt.date(),
            contingency_grain=pl.lit("hub_total"),
            source_hub_id=pl.col("hub_identifier").cast(pl.String),
            source_hub_name=pl.col("hub_name").cast(pl.String),
            source_facility_id=pl.lit(None).cast(pl.String),
            facility_name=pl.lit(None).cast(pl.String),
            flow_direction=pl.lit(None).cast(pl.String),
            participant_id=pl.lit(None).cast(pl.String),
            participant_name=pl.lit(None).cast(pl.String),
            contingency_call_id=pl.lit(None).cast(pl.String),
            contingency_bid_offer_id=pl.lit(None).cast(pl.String),
            bid_step=pl.lit(None).cast(pl.Int64),
            bid_price=pl.lit(None).cast(pl.Float64),
            bid_qty_gj=pl.lit(None).cast(pl.Float64),
            approval_timestamp=pl.lit(None).cast(pl.Datetime("us")),
            source_last_updated=pl.col("report_datetime").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("report_datetime"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
            total_bid_quantity=pl.col("total_contingency_gas_bid_qty").cast(pl.Float64),
            total_offer_quantity=pl.col("total_contingency_gas_offer_qty").cast(
                pl.Float64
            ),
        )
        .unpivot(
            index=_INT673_INDEX,
            on=["total_bid_quantity", "total_offer_quantity"],
            variable_name="quantity_type",
            value_name="quantity_gj",
        )
        .with_columns(
            bid_offer_type=(
                pl.when(pl.col("quantity_type") == "total_bid_quantity")
                .then(pl.lit("B"))
                .otherwise(pl.lit("O"))
            )
        )
        .filter(pl.col("quantity_gj").is_not_null())
    )


def _total_contingency_schedule_rows(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[2]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[2]),
        source_report_id=pl.lit("INT674"),
        gas_date=_parse_datetime("gas_date").dt.date(),
        contingency_grain=pl.lit("facility_called_total"),
        quantity_type=pl.lit("called_total_quantity"),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        source_facility_id=pl.col("facility_identifier").cast(pl.String),
        facility_name=pl.col("facility_name").cast(pl.String),
        flow_direction=pl.col("flow_direction").cast(pl.String),
        bid_offer_type=pl.col("contingency_gas_bid_offer_type").cast(pl.String),
        participant_id=pl.lit(None).cast(pl.String),
        participant_name=pl.lit(None).cast(pl.String),
        contingency_call_id=pl.col("contingency_gas_called_identifier").cast(pl.String),
        contingency_bid_offer_id=pl.lit(None).cast(pl.String),
        bid_step=pl.lit(None).cast(pl.Int64),
        bid_price=pl.lit(None).cast(pl.Float64),
        bid_qty_gj=pl.lit(None).cast(pl.Float64),
        quantity_gj=pl.col("contingency_gas_bid_offer_called_quantity").cast(
            pl.Float64
        ),
        approval_timestamp=_parse_datetime("approval_datetime"),
        source_last_updated=pl.col("report_datetime").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("report_datetime"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _with_dimension_keys(
    df: LazyFrame,
    participants: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> LazyFrame:
    participant_keys = participants.filter(
        pl.col("participant_identity_source") == "company_id"
    ).select(
        participant_key=pl.col("surrogate_key"),
        participant_id=pl.col("participant_identity_value"),
    )
    facility_keys = facilities.filter(pl.col("source_system") == SOURCE_SYSTEM).select(
        facility_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        source_hub_id=pl.col("source_hub_id"),
        source_facility_id=pl.col("source_facility_id"),
    )
    zone_keys = zones.filter(
        (pl.col("source_system") == SOURCE_SYSTEM) & (pl.col("zone_type") == "sttm_hub")
    ).select(
        zone_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        source_hub_id=pl.col("source_zone_id"),
    )
    return (
        df.join(participant_keys, on="participant_id", how="left")
        .join(
            facility_keys,
            on=["source_system", "source_hub_id", "source_facility_id"],
            how="left",
        )
        .join(zone_keys, on=["source_system", "source_hub_id"], how="left")
    )


def _select_sttm_contingency_gas_calls(
    int661: LazyFrame,
    int673: LazyFrame,
    int674: LazyFrame,
    participants: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> LazyFrame:
    combined = pl.concat(
        [
            _called_scheduled_bid_offer_rows(int661),
            _total_contingency_bid_offer_rows(int673),
            _total_contingency_schedule_rows(int674),
        ],
        how="diagonal_relaxed",
    ).with_columns(
        date_key=get_surrogate_key(["gas_date"]),
        surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES),
    )
    return _with_dimension_keys(combined, participants, facilities, zones).select(
        list(SCHEMA)
    )


def _materialize_result(value: LazyFrame) -> MaterializeResult[LazyFrame]:
    return MaterializeResult(
        value=value,
        metadata={"dagster/column_lineage": COLUMN_LINEAGE},
    )


@asset(
    key_prefix=KEY_PREFIX,
    group_name=GROUP_NAME,
    description="Silver STTM contingency gas call fact.",
    ins={
        "int661": AssetIn(key=INT661_KEY),
        "int673": AssetIn(key=INT673_KEY),
        "int674": AssetIn(key=INT674_KEY),
        "participants": AssetIn(key=PARTICIPANTS_KEY),
        "facilities": AssetIn(key=FACILITIES_KEY),
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
def silver_gas_fact_sttm_contingency_gas_call(
    int661: LazyFrame,
    int673: LazyFrame,
    int674: LazyFrame,
    participants: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver STTM contingency gas call fact asset."""
    return _materialize_result(
        _select_sttm_contingency_gas_calls(
            int661,
            int673,
            int674,
            participants,
            facilities,
            zones,
        )
    )


@asset_check(
    asset=silver_gas_fact_sttm_contingency_gas_call,
    name="check_required_fields",
    description="Check required STTM contingency gas call fields are not null.",
)
def silver_gas_fact_sttm_contingency_gas_call_required_fields(
    input_df: LazyFrame,
) -> AssetCheckResult:
    """Validate required fields for the silver STTM contingency gas call fact asset."""
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


silver_gas_fact_sttm_contingency_gas_call_duplicate_row_check = (
    duplicate_row_check_factory(
        assets_definition=silver_gas_fact_sttm_contingency_gas_call,
        check_name="check_for_duplicate_rows",
        primary_key="surrogate_key",
        description="Check that surrogate_key is unique.",
    )
)

silver_gas_fact_sttm_contingency_gas_call_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_fact_sttm_contingency_gas_call,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)

silver_gas_fact_sttm_contingency_gas_call_schema_drift_check = (
    schema_drift_check_factory(
        schema=SCHEMA,
        assets_definition=silver_gas_fact_sttm_contingency_gas_call,
        check_name="check_schema_drift",
        description="Check for schema drift against the declared asset schema.",
    )
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver STTM contingency gas call fact."""
    return Definitions(
        assets=[silver_gas_fact_sttm_contingency_gas_call],
        asset_checks=[
            silver_gas_fact_sttm_contingency_gas_call_duplicate_row_check,
            silver_gas_fact_sttm_contingency_gas_call_schema_check,
            silver_gas_fact_sttm_contingency_gas_call_schema_drift_check,
            silver_gas_fact_sttm_contingency_gas_call_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_sttm_contingency_gas_call_sensor",
                target=[silver_gas_fact_sttm_contingency_gas_call.key],
                default_status=DEFAULT_SENSOR_STATUS,
                run_tags={"ecs/cpu": "512", "ecs/memory": "4096"},
            )
        ],
    )
