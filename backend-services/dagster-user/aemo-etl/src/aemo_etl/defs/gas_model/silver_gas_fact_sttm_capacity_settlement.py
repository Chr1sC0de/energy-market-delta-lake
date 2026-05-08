"""Dagster definitions for the silver STTM capacity settlement fact asset."""

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
    ZONES_KEY,
    parse_datetime,
    source_asset_key,
    source_metadata,
    source_table,
    with_facility_zone_keys,
)
from aemo_etl.factories.checks import (
    duplicate_row_check_factory,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.utils import get_metadata_schema, get_surrogate_key

DOMAIN = "gas_model"
TABLE_NAME = "silver_gas_fact_sttm_capacity_settlement"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per STTM gas date, facility, and MOS or capacity settlement component"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "settlement_run_id",
    "gas_date",
    "source_hub_id",
    "source_facility_id",
    "settlement_stage",
    "capacity_settlement_component",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    source_table("int664_v1_daily_provisional_mos_allocation_rpt_1"),
    source_table("int681_v1_daily_provisional_capacity_data_rpt_1"),
    source_table("int682_v1_settlement_mos_and_capacity_data_rpt_1"),
]
INT664_KEY = source_asset_key("int664_v1_daily_provisional_mos_allocation_rpt_1")
INT681_KEY = source_asset_key("int681_v1_daily_provisional_capacity_data_rpt_1")
INT682_KEY = source_asset_key("int682_v1_settlement_mos_and_capacity_data_rpt_1")

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT664_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT681_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT682_KEY, column_name="surrogate_key"),
]
_SOURCE_HUB_ID_DEPS = [
    TableColumnDep(asset_key=INT664_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT681_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT682_KEY, column_name="hub_identifier"),
]
_SOURCE_FACILITY_ID_DEPS = [
    TableColumnDep(asset_key=INT664_KEY, column_name="facility_identifier"),
    TableColumnDep(asset_key=INT681_KEY, column_name="facility_identifier"),
    TableColumnDep(asset_key=INT682_KEY, column_name="facility_identifier"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "date_key": [
            TableColumnDep(asset_key=INT664_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT681_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT682_KEY, column_name="gas_date"),
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
        "quantity_gj": [
            TableColumnDep(asset_key=INT664_KEY, column_name="mos_allocated_qty"),
            TableColumnDep(asset_key=INT664_KEY, column_name="mos_overrun_qty"),
            TableColumnDep(asset_key=INT681_KEY, column_name="firm_not_flowed"),
            TableColumnDep(asset_key=INT681_KEY, column_name="as_available_flowed"),
            TableColumnDep(asset_key=INT682_KEY, column_name="mos_allocated_qty"),
            TableColumnDep(asset_key=INT682_KEY, column_name="mos_overrun_qty"),
            TableColumnDep(asset_key=INT682_KEY, column_name="firm_not_flowed"),
            TableColumnDep(asset_key=INT682_KEY, column_name="as_available_flowed"),
        ],
        "source_surrogate_key": _SOURCE_KEY_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "facility_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "source_report_id": pl.String,
    "gas_date": pl.Date,
    "settlement_run_id": pl.String,
    "settlement_stage": pl.String,
    "capacity_settlement_component": pl.String,
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "quantity_gj": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver fact primary key generated by surrogate_key_sources.",
    "date_key": "Deterministic silver_gas_dim_date surrogate_key for gas_date.",
    "facility_key": "Parent silver_gas_dim_facility surrogate_key when resolvable.",
    "zone_key": "Parent silver_gas_dim_zone surrogate_key for STTM hub when resolvable.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the row.",
    "source_table": "Specific silver source table for this row.",
    "source_report_id": "STTM report identifier.",
    "gas_date": "Gas day date.",
    "settlement_run_id": "Source settlement run identifier where present.",
    "settlement_stage": "Source-specific capacity settlement stage represented by the row.",
    "capacity_settlement_component": "Source MOS or capacity component represented by the row.",
    "source_hub_id": "Source-system hub identifier.",
    "source_hub_name": "Source-system hub name.",
    "source_facility_id": "Source-system facility identifier.",
    "facility_name": "Source-system facility name.",
    "quantity_gj": "Component quantity value.",
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
    "settlement_stage",
    "capacity_settlement_component",
    "source_hub_id",
    "source_facility_id",
    "quantity_gj",
    "source_surrogate_key",
]

_COMMON_INDEX = [
    "source_system",
    "source_tables",
    "source_table",
    "source_report_id",
    "gas_date",
    "settlement_run_id",
    "settlement_stage",
    "source_hub_id",
    "source_hub_name",
    "source_facility_id",
    "facility_name",
    "source_last_updated",
    "source_last_updated_timestamp",
    "source_surrogate_key",
    "source_file",
    "ingested_timestamp",
]

_COMPONENTS = {
    "mos_allocated_qty": "mos_allocated_qty",
    "mos_overrun_qty": "mos_overrun_qty",
    "firm_not_flowed": "firm_not_flowed",
    "as_available_flowed": "as_available_flowed",
}


def _component_rows(
    df: LazyFrame,
    *,
    table_name: str,
    report_id: str,
    settlement_stage: str,
    component_columns: list[str],
    has_settlement_run_id: bool,
) -> LazyFrame:
    selected = df.select(
        *source_metadata(table_name=table_name, report_id=report_id),
        gas_date=parse_datetime("gas_date").dt.date(),
        settlement_run_id=(
            pl.col("settlement_run_identifier").cast(pl.String)
            if has_settlement_run_id
            else pl.lit(None).cast(pl.String)
        ),
        settlement_stage=pl.lit(settlement_stage),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        source_facility_id=pl.col("facility_identifier").cast(pl.String),
        facility_name=pl.col("facility_name").cast(pl.String),
        *[pl.col(column).cast(pl.Float64) for column in component_columns],
    )
    return (
        selected.unpivot(
            index=_COMMON_INDEX,
            on=component_columns,
            variable_name="capacity_settlement_component",
            value_name="quantity_gj",
        )
        .with_columns(
            capacity_settlement_component=pl.col(
                "capacity_settlement_component"
            ).replace(_COMPONENTS)
        )
        .filter(pl.col("quantity_gj").is_not_null())
    )


def _select_sttm_capacity_settlements(
    int664: LazyFrame,
    int681: LazyFrame,
    int682: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> LazyFrame:
    combined = pl.concat(
        [
            _component_rows(
                int664,
                table_name=SOURCE_TABLES[0],
                report_id="INT664",
                settlement_stage="provisional_mos_allocation",
                component_columns=["mos_allocated_qty", "mos_overrun_qty"],
                has_settlement_run_id=False,
            ),
            _component_rows(
                int681,
                table_name=SOURCE_TABLES[1],
                report_id="INT681",
                settlement_stage="provisional_capacity",
                component_columns=["firm_not_flowed", "as_available_flowed"],
                has_settlement_run_id=False,
            ),
            _component_rows(
                int682,
                table_name=SOURCE_TABLES[2],
                report_id="INT682",
                settlement_stage="settlement_mos_capacity",
                component_columns=[
                    "mos_allocated_qty",
                    "mos_overrun_qty",
                    "firm_not_flowed",
                    "as_available_flowed",
                ],
                has_settlement_run_id=True,
            ),
        ],
        how="diagonal_relaxed",
    ).with_columns(
        date_key=get_surrogate_key(["gas_date"]),
        surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES),
    )
    return with_facility_zone_keys(combined, facilities, zones).select(list(SCHEMA))


def _materialize_result(value: LazyFrame) -> MaterializeResult[LazyFrame]:
    return MaterializeResult(
        value=value,
        metadata={"dagster/column_lineage": COLUMN_LINEAGE},
    )


@asset(
    key_prefix=KEY_PREFIX,
    group_name=GROUP_NAME,
    description="Silver STTM capacity settlement fact.",
    ins={
        "int664": AssetIn(key=INT664_KEY),
        "int681": AssetIn(key=INT681_KEY),
        "int682": AssetIn(key=INT682_KEY),
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
def silver_gas_fact_sttm_capacity_settlement(
    int664: LazyFrame,
    int681: LazyFrame,
    int682: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver STTM capacity settlement fact asset."""
    return _materialize_result(
        _select_sttm_capacity_settlements(int664, int681, int682, facilities, zones)
    )


@asset_check(
    asset=silver_gas_fact_sttm_capacity_settlement,
    name="check_required_fields",
    description="Check required STTM capacity settlement fields are not null.",
)
def silver_gas_fact_sttm_capacity_settlement_required_fields(
    input_df: LazyFrame,
) -> AssetCheckResult:
    """Validate required fields for the silver STTM capacity settlement fact."""
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


silver_gas_fact_sttm_capacity_settlement_duplicate_row_check = (
    duplicate_row_check_factory(
        assets_definition=silver_gas_fact_sttm_capacity_settlement,
        check_name="check_for_duplicate_rows",
        primary_key="surrogate_key",
        description="Check that surrogate_key is unique.",
    )
)
silver_gas_fact_sttm_capacity_settlement_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_fact_sttm_capacity_settlement,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)
silver_gas_fact_sttm_capacity_settlement_schema_drift_check = (
    schema_drift_check_factory(
        schema=SCHEMA,
        assets_definition=silver_gas_fact_sttm_capacity_settlement,
        check_name="check_schema_drift",
        description="Check for schema drift against the declared asset schema.",
    )
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver STTM capacity settlement fact."""
    return Definitions(
        assets=[silver_gas_fact_sttm_capacity_settlement],
        asset_checks=[
            silver_gas_fact_sttm_capacity_settlement_duplicate_row_check,
            silver_gas_fact_sttm_capacity_settlement_schema_check,
            silver_gas_fact_sttm_capacity_settlement_schema_drift_check,
            silver_gas_fact_sttm_capacity_settlement_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_sttm_capacity_settlement_sensor",
                target=[silver_gas_fact_sttm_capacity_settlement.key],
                default_status=DEFAULT_SENSOR_STATUS,
                run_tags={"ecs/cpu": "512", "ecs/memory": "4096"},
            )
        ],
    )
