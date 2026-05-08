"""Dagster definitions for the silver STTM MOS stack fact asset."""

import polars as pl
from dagster import (
    AssetCheckResult,
    AssetIn,
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
from aemo_etl.defs.gas_model._sttm_common import (
    FACILITIES_KEY,
    PARTICIPANTS_KEY,
    ZONES_KEY,
    parse_datetime,
    source_asset_key,
    source_metadata,
    source_table,
    with_facility_zone_keys,
    with_participant_key,
)
from aemo_etl.factories.checks import (
    duplicate_row_check_factory,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.utils import get_metadata_schema, get_surrogate_key

DOMAIN = "gas_model"
TABLE_NAME = "silver_gas_fact_sttm_mos_stack"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per STTM MOS stack step and effective or used-step context"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "mos_stack_context",
    "settlement_run_id",
    "gas_date",
    "effective_from_date",
    "effective_to_date",
    "source_hub_id",
    "source_facility_id",
    "stack_id",
    "stack_step_id",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    source_table("int665_v1_mos_stack_data_rpt_1"),
    source_table("int683_v1_provisional_used_mos_steps_rpt_1"),
    source_table("int684_v1_settlement_used_mos_steps_rpt_1"),
]
INT665_KEY = source_asset_key("int665_v1_mos_stack_data_rpt_1")
INT683_KEY = source_asset_key("int683_v1_provisional_used_mos_steps_rpt_1")
INT684_KEY = source_asset_key("int684_v1_settlement_used_mos_steps_rpt_1")

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT665_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT683_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT684_KEY, column_name="surrogate_key"),
]
_SOURCE_HUB_ID_DEPS = [
    TableColumnDep(asset_key=INT665_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT683_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT684_KEY, column_name="hub_identifier"),
]
_SOURCE_FACILITY_ID_DEPS = [
    TableColumnDep(asset_key=INT665_KEY, column_name="facility_identifier"),
    TableColumnDep(asset_key=INT683_KEY, column_name="facility_identifier"),
    TableColumnDep(asset_key=INT684_KEY, column_name="facility_identifier"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "date_key": [
            TableColumnDep(asset_key=INT683_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT684_KEY, column_name="gas_date"),
        ],
        "effective_from_date_key": [
            TableColumnDep(asset_key=INT665_KEY, column_name="effective_from_date")
        ],
        "effective_to_date_key": [
            TableColumnDep(asset_key=INT665_KEY, column_name="effective_to_date")
        ],
        "participant_key": [
            TableColumnDep(
                asset_key=INT665_KEY, column_name="trading_participant_identifier"
            ),
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
        "estimated_maximum_quantity_gj": [
            TableColumnDep(
                asset_key=INT665_KEY, column_name="estimated_maximum_quantity"
            )
        ],
        "step_quantity_gj": [
            TableColumnDep(asset_key=INT665_KEY, column_name="step_quantity")
        ],
        "step_price": [TableColumnDep(asset_key=INT665_KEY, column_name="step_price")],
        "source_surrogate_key": _SOURCE_KEY_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "effective_from_date_key": pl.String,
    "effective_to_date_key": pl.String,
    "participant_key": pl.String,
    "facility_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "source_report_id": pl.String,
    "mos_stack_context": pl.String,
    "settlement_run_id": pl.String,
    "gas_date": pl.Date,
    "effective_from_date": pl.Date,
    "effective_to_date": pl.Date,
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "stack_id": pl.String,
    "stack_type": pl.String,
    "stack_step_id": pl.String,
    "participant_id": pl.String,
    "participant_name": pl.String,
    "estimated_maximum_quantity_gj": pl.Float64,
    "step_quantity_gj": pl.Float64,
    "step_price": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver fact primary key generated by surrogate_key_sources.",
    "date_key": "Deterministic silver_gas_dim_date surrogate_key for gas_date.",
    "effective_from_date_key": "Deterministic silver_gas_dim_date surrogate_key for effective_from_date.",
    "effective_to_date_key": "Deterministic silver_gas_dim_date surrogate_key for effective_to_date.",
    "participant_key": "Parent silver_gas_dim_participant surrogate_key when resolvable.",
    "facility_key": "Parent silver_gas_dim_facility surrogate_key when resolvable.",
    "zone_key": "Parent silver_gas_dim_zone surrogate_key for STTM hub when resolvable.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the row.",
    "source_table": "Specific silver source table for this row.",
    "source_report_id": "STTM report identifier.",
    "mos_stack_context": "Source MOS stack context represented by the row.",
    "settlement_run_id": "Source settlement run identifier where present.",
    "gas_date": "Gas day date for used MOS step rows.",
    "effective_from_date": "First gas date for which the MOS stack applies.",
    "effective_to_date": "Last gas date for which the MOS stack applies.",
    "source_hub_id": "Source-system hub identifier.",
    "source_hub_name": "Source-system hub name.",
    "source_facility_id": "Source-system facility identifier.",
    "facility_name": "Source-system facility name.",
    "stack_id": "Source MOS stack identifier.",
    "stack_type": "Source MOS stack type flag.",
    "stack_step_id": "Source MOS stack step identifier.",
    "participant_id": "Source MOS trading participant identifier where present.",
    "participant_name": "Source MOS trading participant name where present.",
    "estimated_maximum_quantity_gj": "Source estimated maximum MOS quantity where present.",
    "step_quantity_gj": "Source MOS stack step quantity where present.",
    "step_price": "Source MOS stack step price where present.",
    "source_last_updated": "Raw source update value.",
    "source_last_updated_timestamp": "Parsed source update timestamp.",
    "source_surrogate_key": "Source row surrogate key for lineage.",
    "source_file": "Archived source file for the source row.",
    "ingested_timestamp": "Timestamp when the source row was ingested.",
}

REQUIRED_COLUMNS = [
    "surrogate_key",
    "source_system",
    "source_table",
    "source_report_id",
    "mos_stack_context",
    "source_hub_id",
    "source_facility_id",
    "stack_id",
    "stack_step_id",
    "source_surrogate_key",
]


def _mos_stack_rows(df: LazyFrame) -> LazyFrame:
    return df.select(
        *source_metadata(table_name=SOURCE_TABLES[0], report_id="INT665"),
        mos_stack_context=pl.lit("registered_stack"),
        settlement_run_id=pl.lit(None).cast(pl.String),
        gas_date=pl.lit(None).cast(pl.Date),
        effective_from_date=parse_datetime("effective_from_date").dt.date(),
        effective_to_date=parse_datetime("effective_to_date").dt.date(),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        source_facility_id=pl.col("facility_identifier").cast(pl.String),
        facility_name=pl.col("facility_name").cast(pl.String),
        stack_id=pl.col("stack_identifier").cast(pl.String),
        stack_type=pl.col("stack_type").cast(pl.String),
        stack_step_id=pl.col("stack_step_identifier").cast(pl.String),
        participant_id=pl.col("trading_participant_identifier").cast(pl.String),
        participant_name=pl.col("trading_participant_name").cast(pl.String),
        estimated_maximum_quantity_gj=pl.col("estimated_maximum_quantity").cast(
            pl.Float64
        ),
        step_quantity_gj=pl.col("step_quantity").cast(pl.Float64),
        step_price=pl.col("step_price").cast(pl.Float64),
    )


def _used_mos_rows(
    df: LazyFrame,
    *,
    table_name: str,
    report_id: str,
    mos_stack_context: str,
    has_settlement_run_id: bool,
) -> LazyFrame:
    return df.select(
        *source_metadata(table_name=table_name, report_id=report_id),
        mos_stack_context=pl.lit(mos_stack_context),
        settlement_run_id=(
            pl.col("settlement_run_identifier").cast(pl.String)
            if has_settlement_run_id
            else pl.lit(None).cast(pl.String)
        ),
        gas_date=parse_datetime("gas_date").dt.date(),
        effective_from_date=pl.lit(None).cast(pl.Date),
        effective_to_date=pl.lit(None).cast(pl.Date),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        source_facility_id=pl.col("facility_identifier").cast(pl.String),
        facility_name=pl.col("facility_name").cast(pl.String),
        stack_id=pl.col("stack_identifier").cast(pl.String),
        stack_type=pl.col("stack_type").cast(pl.String),
        stack_step_id=pl.col("stack_step_identifier").cast(pl.String),
        participant_id=pl.lit(None).cast(pl.String),
        participant_name=pl.lit(None).cast(pl.String),
        estimated_maximum_quantity_gj=pl.lit(None).cast(pl.Float64),
        step_quantity_gj=pl.lit(None).cast(pl.Float64),
        step_price=pl.lit(None).cast(pl.Float64),
    )


def _nullable_date_key(column: str) -> pl.Expr:
    return (
        pl.when(pl.col(column).is_not_null())
        .then(get_surrogate_key([column]))
        .otherwise(pl.lit(None).cast(pl.String))
    )


def _select_sttm_mos_stack(
    int665: LazyFrame,
    int683: LazyFrame,
    int684: LazyFrame,
    participants: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> LazyFrame:
    combined = pl.concat(
        [
            _mos_stack_rows(int665),
            _used_mos_rows(
                int683,
                table_name=SOURCE_TABLES[1],
                report_id="INT683",
                mos_stack_context="provisional_used_step",
                has_settlement_run_id=False,
            ),
            _used_mos_rows(
                int684,
                table_name=SOURCE_TABLES[2],
                report_id="INT684",
                mos_stack_context="settlement_used_step",
                has_settlement_run_id=True,
            ),
        ],
        how="diagonal_relaxed",
    ).with_columns(
        date_key=_nullable_date_key("gas_date"),
        effective_from_date_key=_nullable_date_key("effective_from_date"),
        effective_to_date_key=_nullable_date_key("effective_to_date"),
        surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES),
    )
    with_participants = with_participant_key(combined, participants)
    return with_facility_zone_keys(with_participants, facilities, zones).select(
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
    description="Silver STTM MOS stack fact.",
    ins={
        "int665": AssetIn(key=INT665_KEY),
        "int683": AssetIn(key=INT683_KEY),
        "int684": AssetIn(key=INT684_KEY),
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
def silver_gas_fact_sttm_mos_stack(
    int665: LazyFrame,
    int683: LazyFrame,
    int684: LazyFrame,
    participants: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver STTM MOS stack fact asset."""
    return _materialize_result(
        _select_sttm_mos_stack(int665, int683, int684, participants, facilities, zones)
    )


@asset_check(
    asset=silver_gas_fact_sttm_mos_stack,
    name="check_required_fields",
    description="Check required STTM MOS stack fields are not null.",
)
def silver_gas_fact_sttm_mos_stack_required_fields(
    input_df: LazyFrame,
) -> AssetCheckResult:
    """Validate required fields for the silver STTM MOS stack fact."""
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


silver_gas_fact_sttm_mos_stack_duplicate_row_check = duplicate_row_check_factory(
    assets_definition=silver_gas_fact_sttm_mos_stack,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
    description="Check that surrogate_key is unique.",
)
silver_gas_fact_sttm_mos_stack_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_fact_sttm_mos_stack,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)
silver_gas_fact_sttm_mos_stack_schema_drift_check = schema_drift_check_factory(
    schema=SCHEMA,
    assets_definition=silver_gas_fact_sttm_mos_stack,
    check_name="check_schema_drift",
    description="Check for schema drift against the declared asset schema.",
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver STTM MOS stack fact."""
    return Definitions(
        assets=[silver_gas_fact_sttm_mos_stack],
        asset_checks=[
            silver_gas_fact_sttm_mos_stack_duplicate_row_check,
            silver_gas_fact_sttm_mos_stack_schema_check,
            silver_gas_fact_sttm_mos_stack_schema_drift_check,
            silver_gas_fact_sttm_mos_stack_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_sttm_mos_stack_sensor",
                target=[silver_gas_fact_sttm_mos_stack.key],
                default_status=DEFAULT_SENSOR_STATUS,
                run_tags={"ecs/cpu": "512", "ecs/memory": "4096"},
            )
        ],
    )
