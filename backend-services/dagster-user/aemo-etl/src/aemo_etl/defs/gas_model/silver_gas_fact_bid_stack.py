"""Dagster definitions for the silver gas bid stack fact asset."""

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
TABLE_NAME = "silver_gas_fact_bid_stack"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific bid stack step"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "gas_date",
    "participant_id",
    "source_hub_id",
    "source_point_id",
    "schedule_identifier",
    "bid_id",
    "bid_step",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.vicgas.silver_int131_v4_bids_at_bid_cutoff_times_prev_2_1",
    "silver.vicgas.silver_int314_v4_bid_stack_1",
    "silver.sttm.silver_int659_v1_bid_offer_rpt_1",
    "silver.sttm.silver_int660_v1_contingency_gas_bids_and_offers_rpt_1",
]
SOURCE_SYSTEM = "VICGAS"
STTM_SOURCE_SYSTEM = "STTM"
INT131_KEY = AssetKey(
    ["silver", "vicgas", "silver_int131_v4_bids_at_bid_cutoff_times_prev_2_1"]
)
INT314_KEY = AssetKey(["silver", "vicgas", "silver_int314_v4_bid_stack_1"])
INT659_KEY = AssetKey(["silver", "sttm", "silver_int659_v1_bid_offer_rpt_1"])
INT660_KEY = AssetKey(
    ["silver", "sttm", "silver_int660_v1_contingency_gas_bids_and_offers_rpt_1"]
)
PARTICIPANTS_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_participant"])
FACILITIES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_facility"])
ZONES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_zone"])

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT131_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT314_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT659_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT660_KEY, column_name="surrogate_key"),
]

_PARTICIPANT_ID_DEPS = [
    TableColumnDep(asset_key=INT131_KEY, column_name="participant_id"),
    TableColumnDep(asset_key=INT314_KEY, column_name="market_participant_id"),
    TableColumnDep(asset_key=INT659_KEY, column_name="company_identifier"),
    TableColumnDep(asset_key=INT660_KEY, column_name="company_identifier"),
]

_SOURCE_HUB_ID_DEPS = [
    TableColumnDep(asset_key=INT659_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT660_KEY, column_name="hub_identifier"),
]

_SOURCE_FACILITY_ID_DEPS = [
    TableColumnDep(asset_key=INT659_KEY, column_name="facility_identifier"),
    TableColumnDep(asset_key=INT660_KEY, column_name="facility_identifier"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "participant_key": [
            *_PARTICIPANT_ID_DEPS,
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
        "source_surrogate_key": _SOURCE_KEY_DEPS,
        "participant_id": _PARTICIPANT_ID_DEPS,
        "source_hub_id": _SOURCE_HUB_ID_DEPS,
        "source_facility_id": _SOURCE_FACILITY_ID_DEPS,
        "bid_price": [TableColumnDep(asset_key=INT314_KEY, column_name="bid_price")],
        "bid_qty_gj": [
            TableColumnDep(asset_key=INT314_KEY, column_name="bid_qty_gj"),
            TableColumnDep(
                asset_key=INT659_KEY, column_name="step_capped_cumulative_qty"
            ),
            TableColumnDep(
                asset_key=INT660_KEY,
                column_name="contingency_gas_bid_offer_step_quantity",
            ),
        ],
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
    "participant_id": pl.String,
    "participant_name": pl.String,
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "source_point_id": pl.String,
    "schedule_identifier": pl.String,
    "bid_id": pl.String,
    "bid_step": pl.Int64,
    "bid_price": pl.Float64,
    "bid_qty_gj": pl.Float64,
    "step_qty_gj": pl.Float64,
    "offer_type": pl.String,
    "inject_withdraw": pl.String,
    "schedule_type": pl.String,
    "schedule_time": pl.String,
    "bid_cutoff_timestamp": pl.Datetime("us"),
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
    "source_report_id",
    "gas_date",
    "participant_id",
    "source_point_id",
    "bid_id",
]


def _parse_datetime(column: str) -> pl.Expr:
    return parse_gas_datetime(column)


def _cutoff_bid_rows(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[0]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[0]),
        source_report_id=pl.lit("INT131"),
        gas_date=_parse_datetime("gas_date").dt.date(),
        participant_id=pl.col("participant_id").cast(pl.String),
        participant_name=pl.col("participant_name").cast(pl.String),
        source_hub_id=pl.lit(None).cast(pl.String),
        source_hub_name=pl.lit(None).cast(pl.String),
        source_facility_id=pl.lit(None).cast(pl.String),
        facility_name=pl.lit(None).cast(pl.String),
        source_point_id=pl.col("code").cast(pl.String),
        schedule_identifier=pl.lit(None).cast(pl.String),
        bid_id=pl.col("bid_id").cast(pl.String),
        bid_step=pl.lit(None).cast(pl.Int64),
        bid_price=pl.lit(None).cast(pl.Float64),
        bid_qty_gj=pl.col("min_daily_qty").cast(pl.Float64),
        step_qty_gj=pl.lit(None).cast(pl.Float64),
        offer_type=pl.col("offer_type").cast(pl.String),
        inject_withdraw=pl.col("type_1").cast(pl.String),
        schedule_type=pl.col("schedule_type").cast(pl.String),
        schedule_time=pl.col("schedule_time").cast(pl.String),
        bid_cutoff_timestamp=_parse_datetime("bid_cutoff_time"),
        source_last_updated=pl.col("current_date").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("current_date"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _public_bid_stack_rows(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[1]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[1]),
        source_report_id=pl.lit("INT314"),
        gas_date=_parse_datetime("gas_date").dt.date(),
        participant_id=pl.col("market_participant_id").cast(pl.String),
        participant_name=pl.col("company_name").cast(pl.String),
        source_hub_id=pl.lit(None).cast(pl.String),
        source_hub_name=pl.lit(None).cast(pl.String),
        source_facility_id=pl.lit(None).cast(pl.String),
        facility_name=pl.lit(None).cast(pl.String),
        source_point_id=pl.col("mirn").cast(pl.String),
        schedule_identifier=pl.lit(None).cast(pl.String),
        bid_id=pl.col("bid_id").cast(pl.String),
        bid_step=pl.col("bid_step").cast(pl.Int64),
        bid_price=pl.col("bid_price").cast(pl.Float64),
        bid_qty_gj=pl.col("bid_qty_gj").cast(pl.Float64),
        step_qty_gj=pl.col("step_qty_gj").cast(pl.Float64),
        offer_type=pl.lit(None).cast(pl.String),
        inject_withdraw=pl.col("inject_withdraw").cast(pl.String),
        schedule_type=pl.lit(None).cast(pl.String),
        schedule_time=pl.lit(None).cast(pl.String),
        bid_cutoff_timestamp=pl.lit(None).cast(pl.Datetime("us")),
        source_last_updated=pl.col("current_date").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("current_date"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _sttm_bid_offer_rows(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(STTM_SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[2]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[2]),
        source_report_id=pl.lit("INT659"),
        gas_date=_parse_datetime("gas_date").dt.date(),
        participant_id=pl.col("company_identifier").cast(pl.String),
        participant_name=pl.col("company_name").cast(pl.String),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        source_facility_id=pl.col("facility_identifier").cast(pl.String),
        facility_name=pl.col("facility_name").cast(pl.String),
        source_point_id=pl.col("facility_identifier").cast(pl.String),
        schedule_identifier=pl.col("schedule_identifier").cast(pl.String),
        bid_id=pl.col("bid_offer_identifier").cast(pl.String),
        bid_step=pl.col("bid_offer_step_number").cast(pl.Int64),
        bid_price=pl.col("step_price").cast(pl.Float64),
        bid_qty_gj=pl.col("step_capped_cumulative_qty").cast(pl.Float64),
        step_qty_gj=pl.lit(None).cast(pl.Float64),
        offer_type=pl.col("bid_offer_type").cast(pl.String),
        inject_withdraw=pl.lit(None).cast(pl.String),
        schedule_type=pl.lit(None).cast(pl.String),
        schedule_time=pl.lit(None).cast(pl.String),
        bid_cutoff_timestamp=pl.lit(None).cast(pl.Datetime("us")),
        source_last_updated=pl.col("report_datetime").cast(pl.String),
        source_last_updated_timestamp=_parse_datetime("report_datetime"),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _sttm_contingency_bid_offer_rows(df: LazyFrame) -> LazyFrame:
    return df.select(
        source_system=pl.lit(STTM_SOURCE_SYSTEM),
        source_tables=pl.lit([SOURCE_TABLES[3]]).cast(pl.List(pl.String)),
        source_table=pl.lit(SOURCE_TABLES[3]),
        source_report_id=pl.lit("INT660"),
        gas_date=_parse_datetime("gas_date").dt.date(),
        participant_id=pl.col("company_identifier").cast(pl.String),
        participant_name=pl.col("company_name").cast(pl.String),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        source_facility_id=pl.col("facility_identifier").cast(pl.String),
        facility_name=pl.col("facility_name").cast(pl.String),
        source_point_id=pl.col("facility_identifier").cast(pl.String),
        schedule_identifier=pl.lit(None).cast(pl.String),
        bid_id=pl.col("contingency_gas_bid_offer_identifier").cast(pl.String),
        bid_step=pl.col("contingency_gas_bid_offer_step_number").cast(pl.Int64),
        bid_price=pl.col("contingency_gas_bid_offer_step_price").cast(pl.Float64),
        bid_qty_gj=pl.col("contingency_gas_bid_offer_step_quantity").cast(pl.Float64),
        step_qty_gj=pl.lit(None).cast(pl.Float64),
        offer_type=pl.col("contingency_gas_bid_offer_type").cast(pl.String),
        inject_withdraw=pl.col("flow_direction").cast(pl.String),
        schedule_type=pl.lit(None).cast(pl.String),
        schedule_time=pl.lit(None).cast(pl.String),
        bid_cutoff_timestamp=pl.lit(None).cast(pl.Datetime("us")),
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
    facility_keys = facilities.filter(
        pl.col("source_system") == STTM_SOURCE_SYSTEM
    ).select(
        facility_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        source_hub_id=pl.col("source_hub_id"),
        source_facility_id=pl.col("source_facility_id"),
    )
    zone_keys = zones.filter(
        (pl.col("source_system") == STTM_SOURCE_SYSTEM)
        & (pl.col("zone_type") == "sttm_hub")
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


def _select_bid_stack(
    int131: LazyFrame,
    int314: LazyFrame,
    int659: LazyFrame,
    int660: LazyFrame,
    participants: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> LazyFrame:
    combined = pl.concat(
        [
            _cutoff_bid_rows(int131),
            _public_bid_stack_rows(int314),
            _sttm_bid_offer_rows(int659),
            _sttm_contingency_bid_offer_rows(int660),
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
        value=value, metadata={"dagster/column_lineage": COLUMN_LINEAGE}
    )


@asset(
    key_prefix=KEY_PREFIX,
    group_name=GROUP_NAME,
    description="Silver gas bid stack fact.",
    ins={
        "int131": AssetIn(key=INT131_KEY),
        "int314": AssetIn(key=INT314_KEY),
        "int659": AssetIn(key=INT659_KEY),
        "int660": AssetIn(key=INT660_KEY),
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
def silver_gas_fact_bid_stack(
    int131: LazyFrame,
    int314: LazyFrame,
    int659: LazyFrame,
    int660: LazyFrame,
    participants: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver gas bid stack fact asset."""
    return _materialize_result(
        _select_bid_stack(
            int131,
            int314,
            int659,
            int660,
            participants,
            facilities,
            zones,
        )
    )


@asset_check(asset=silver_gas_fact_bid_stack, name="check_required_fields")
def silver_gas_fact_bid_stack_required_fields(input_df: LazyFrame) -> AssetCheckResult:
    """Validate required fields for the silver gas bid stack fact asset."""
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


silver_gas_fact_bid_stack_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_bid_stack,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_bid_stack_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_bid_stack, check_name="check_schema_matches"
)
silver_gas_fact_bid_stack_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_bid_stack, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver gas bid stack fact asset."""
    return Definitions(
        assets=[silver_gas_fact_bid_stack],
        asset_checks=[
            silver_gas_fact_bid_stack_duplicate_row_check,
            silver_gas_fact_bid_stack_schema_check,
            silver_gas_fact_bid_stack_schema_drift_check,
            silver_gas_fact_bid_stack_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_bid_stack_sensor",
                target=[silver_gas_fact_bid_stack.key],
                default_status=DEFAULT_SENSOR_STATUS,
                run_tags={"ecs/cpu": "512", "ecs/memory": "4096"},
            )
        ],
    )
