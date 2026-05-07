"""Dagster definitions for the silver STTM market settlement fact asset."""

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
TABLE_NAME = "silver_gas_fact_sttm_market_settlement"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per STTM settlement or NMB component at its accepted source grain"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "settlement_run_id",
    "gas_date",
    "period_start_date",
    "period_end_date",
    "source_hub_id",
    "source_facility_id",
    "settlement_stage",
    "settlement_component",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    source_table("int662_v1_provisional_deviation_rpt_1"),
    source_table("int663_v1_provisional_variation_rpt_1"),
    source_table("int678_v1_net_market_balance_daily_amounts_rpt_1"),
    source_table("int679_v1_net_market_balance_settlement_amounts_rpt_1"),
]
INT662_KEY = source_asset_key("int662_v1_provisional_deviation_rpt_1")
INT663_KEY = source_asset_key("int663_v1_provisional_variation_rpt_1")
INT678_KEY = source_asset_key("int678_v1_net_market_balance_daily_amounts_rpt_1")
INT679_KEY = source_asset_key("int679_v1_net_market_balance_settlement_amounts_rpt_1")

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=INT662_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT663_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT678_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=INT679_KEY, column_name="surrogate_key"),
]
_SOURCE_HUB_ID_DEPS = [
    TableColumnDep(asset_key=INT662_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT663_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT678_KEY, column_name="hub_identifier"),
    TableColumnDep(asset_key=INT679_KEY, column_name="hub_identifier"),
]

COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "date_key": [
            TableColumnDep(asset_key=INT662_KEY, column_name="gas_date"),
            TableColumnDep(asset_key=INT663_KEY, column_name="gas_date"),
        ],
        "period_start_date_key": [
            TableColumnDep(asset_key=INT678_KEY, column_name="period_start_date"),
            TableColumnDep(asset_key=INT679_KEY, column_name="period_start_date"),
        ],
        "period_end_date_key": [
            TableColumnDep(asset_key=INT678_KEY, column_name="period_end_date"),
            TableColumnDep(asset_key=INT679_KEY, column_name="period_end_date"),
        ],
        "facility_key": [
            TableColumnDep(asset_key=INT662_KEY, column_name="facility_identifier"),
            TableColumnDep(asset_key=FACILITIES_KEY, column_name="surrogate_key"),
        ],
        "zone_key": [
            *_SOURCE_HUB_ID_DEPS,
            TableColumnDep(asset_key=ZONES_KEY, column_name="surrogate_key"),
        ],
        "source_hub_id": _SOURCE_HUB_ID_DEPS,
        "source_facility_id": [
            TableColumnDep(asset_key=INT662_KEY, column_name="facility_identifier")
        ],
        "quantity_gj": [
            TableColumnDep(asset_key=INT662_KEY, column_name="total_deviation_qty"),
            TableColumnDep(asset_key=INT662_KEY, column_name="net_deviation_qty"),
            TableColumnDep(asset_key=INT663_KEY, column_name="variation_qty"),
            TableColumnDep(asset_key=INT678_KEY, column_name="total_deviation_qty"),
            TableColumnDep(asset_key=INT678_KEY, column_name="total_withdrawals"),
            TableColumnDep(asset_key=INT679_KEY, column_name="total_deviation_qty"),
            TableColumnDep(asset_key=INT679_KEY, column_name="total_withdrawals"),
        ],
        "amount": [
            TableColumnDep(asset_key=INT662_KEY, column_name="deviation_charge"),
            TableColumnDep(asset_key=INT662_KEY, column_name="deviation_payment"),
            TableColumnDep(asset_key=INT663_KEY, column_name="variation_charge"),
            TableColumnDep(asset_key=INT663_KEY, column_name="mos_capacity_payment"),
            TableColumnDep(asset_key=INT663_KEY, column_name="mos_cashout_payment"),
            TableColumnDep(asset_key=INT663_KEY, column_name="mos_cashout_charge"),
            TableColumnDep(asset_key=INT678_KEY, column_name="net_market_balance"),
            TableColumnDep(asset_key=INT678_KEY, column_name="total_variation_charges"),
            TableColumnDep(asset_key=INT679_KEY, column_name="net_market_balance"),
            TableColumnDep(asset_key=INT679_KEY, column_name="total_variation_charges"),
        ],
        "source_surrogate_key": _SOURCE_KEY_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "date_key": pl.String,
    "period_start_date_key": pl.String,
    "period_end_date_key": pl.String,
    "facility_key": pl.String,
    "zone_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "source_report_id": pl.String,
    "gas_date": pl.Date,
    "period_start_date": pl.Date,
    "period_end_date": pl.Date,
    "settlement_run_id": pl.String,
    "settlement_stage": pl.String,
    "settlement_component": pl.String,
    "source_hub_id": pl.String,
    "source_hub_name": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "quantity_gj": pl.Float64,
    "amount": pl.Float64,
    "source_last_updated": pl.String,
    "source_last_updated_timestamp": pl.Datetime("us"),
    "source_surrogate_key": pl.String,
    "source_file": pl.String,
    "ingested_timestamp": pl.Datetime("us", time_zone="UTC"),
}

DESCRIPTIONS = {
    "surrogate_key": "Silver fact primary key generated by surrogate_key_sources.",
    "date_key": "Deterministic silver_gas_dim_date surrogate_key for gas_date.",
    "period_start_date_key": "Deterministic silver_gas_dim_date surrogate_key for period_start_date.",
    "period_end_date_key": "Deterministic silver_gas_dim_date surrogate_key for period_end_date.",
    "facility_key": "Parent silver_gas_dim_facility surrogate_key when resolvable.",
    "zone_key": "Parent silver_gas_dim_zone surrogate_key for STTM hub when resolvable.",
    "source_system": "Source system identifier.",
    "source_tables": "Silver source tables used to construct the row.",
    "source_table": "Specific silver source table for this row.",
    "source_report_id": "STTM report identifier.",
    "gas_date": "Gas day date where the source grain is daily.",
    "period_start_date": "Start date for NMB calculation or settlement period rows.",
    "period_end_date": "End date for NMB calculation or settlement period rows.",
    "settlement_run_id": "Source settlement run identifier where present.",
    "settlement_stage": "Source-specific settlement stage represented by the row.",
    "settlement_component": "Source settlement or NMB component represented by the row.",
    "source_hub_id": "Source-system hub identifier.",
    "source_hub_name": "Source-system hub name.",
    "source_facility_id": "Source-system facility identifier where present.",
    "facility_name": "Source-system facility name where present.",
    "quantity_gj": "Component quantity value where the source component is a quantity.",
    "amount": "Component monetary amount where the source component is an amount.",
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
    "settlement_stage",
    "settlement_component",
    "source_hub_id",
    "source_surrogate_key",
]

_COMMON_INDEX = [
    "source_system",
    "source_tables",
    "source_table",
    "source_report_id",
    "gas_date",
    "period_start_date",
    "period_end_date",
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

_QUANTITY_COMPONENTS = {
    "total_deviation_qty": "total_deviation_qty",
    "net_deviation_qty": "net_deviation_qty",
    "variation_qty": "variation_qty",
    "total_withdrawals": "total_withdrawals",
}
_AMOUNT_COMPONENTS = {
    "deviation_charge": "deviation_charge",
    "deviation_payment": "deviation_payment",
    "variation_charge": "variation_charge",
    "mos_capacity_payment": "mos_capacity_payment",
    "mos_cashout_payment": "mos_cashout_payment",
    "mos_cashout_charge": "mos_cashout_charge",
    "net_market_balance": "net_market_balance",
    "total_variation_charges": "total_variation_charges",
}


def _unpivot_components(
    df: LazyFrame,
    *,
    quantity_columns: list[str],
    amount_columns: list[str],
) -> LazyFrame:
    quantity_rows = (
        df.unpivot(
            index=_COMMON_INDEX,
            on=quantity_columns,
            variable_name="settlement_component",
            value_name="quantity_gj",
        )
        .with_columns(
            settlement_component=pl.col("settlement_component").replace(
                _QUANTITY_COMPONENTS
            ),
            amount=pl.lit(None).cast(pl.Float64),
        )
        .filter(pl.col("quantity_gj").is_not_null())
    )
    amount_rows = (
        df.unpivot(
            index=_COMMON_INDEX,
            on=amount_columns,
            variable_name="settlement_component",
            value_name="amount",
        )
        .with_columns(
            settlement_component=pl.col("settlement_component").replace(
                _AMOUNT_COMPONENTS
            ),
            quantity_gj=pl.lit(None).cast(pl.Float64),
        )
        .filter(pl.col("amount").is_not_null())
    )
    return pl.concat([quantity_rows, amount_rows], how="diagonal_relaxed")


def _provisional_deviation_rows(df: LazyFrame) -> LazyFrame:
    selected = df.select(
        *source_metadata(table_name=SOURCE_TABLES[0], report_id="INT662"),
        gas_date=parse_datetime("gas_date").dt.date(),
        period_start_date=pl.lit(None).cast(pl.Date),
        period_end_date=pl.lit(None).cast(pl.Date),
        settlement_run_id=pl.lit(None).cast(pl.String),
        settlement_stage=pl.lit("provisional_deviation"),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        source_facility_id=pl.col("facility_identifier").cast(pl.String),
        facility_name=pl.col("facility_name").cast(pl.String),
        total_deviation_qty=pl.col("total_deviation_qty").cast(pl.Float64),
        net_deviation_qty=pl.col("net_deviation_qty").cast(pl.Float64),
        deviation_charge=pl.col("deviation_charge").cast(pl.Float64),
        deviation_payment=pl.col("deviation_payment").cast(pl.Float64),
    )
    return _unpivot_components(
        selected,
        quantity_columns=["total_deviation_qty", "net_deviation_qty"],
        amount_columns=["deviation_charge", "deviation_payment"],
    )


def _provisional_variation_rows(df: LazyFrame) -> LazyFrame:
    selected = df.select(
        *source_metadata(table_name=SOURCE_TABLES[1], report_id="INT663"),
        gas_date=parse_datetime("gas_date").dt.date(),
        period_start_date=pl.lit(None).cast(pl.Date),
        period_end_date=pl.lit(None).cast(pl.Date),
        settlement_run_id=pl.lit(None).cast(pl.String),
        settlement_stage=pl.lit("provisional_variation_mos"),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        source_facility_id=pl.lit(None).cast(pl.String),
        facility_name=pl.lit(None).cast(pl.String),
        variation_qty=pl.col("variation_qty").cast(pl.Float64),
        variation_charge=pl.col("variation_charge").cast(pl.Float64),
        mos_capacity_payment=pl.col("mos_capacity_payment").cast(pl.Float64),
        mos_cashout_payment=pl.col("mos_cashout_payment").cast(pl.Float64),
        mos_cashout_charge=pl.col("mos_cashout_charge").cast(pl.Float64),
    )
    return _unpivot_components(
        selected,
        quantity_columns=["variation_qty"],
        amount_columns=[
            "variation_charge",
            "mos_capacity_payment",
            "mos_cashout_payment",
            "mos_cashout_charge",
        ],
    )


def _nmb_rows(
    df: LazyFrame,
    *,
    table_name: str,
    report_id: str,
    settlement_stage: str,
    has_settlement_run_id: bool,
) -> LazyFrame:
    selected = df.select(
        *source_metadata(table_name=table_name, report_id=report_id),
        gas_date=pl.lit(None).cast(pl.Date),
        period_start_date=parse_datetime("period_start_date").dt.date(),
        period_end_date=parse_datetime("period_end_date").dt.date(),
        settlement_run_id=(
            pl.col("settlement_run_identifier").cast(pl.String)
            if has_settlement_run_id
            else pl.lit(None).cast(pl.String)
        ),
        settlement_stage=pl.lit(settlement_stage),
        source_hub_id=pl.col("hub_identifier").cast(pl.String),
        source_hub_name=pl.col("hub_name").cast(pl.String),
        source_facility_id=pl.lit(None).cast(pl.String),
        facility_name=pl.lit(None).cast(pl.String),
        net_market_balance=pl.col("net_market_balance").cast(pl.Float64),
        total_deviation_qty=pl.col("total_deviation_qty").cast(pl.Float64),
        total_withdrawals=pl.col("total_withdrawals").cast(pl.Float64),
        total_variation_charges=pl.col("total_variation_charges").cast(pl.Float64),
    )
    return _unpivot_components(
        selected,
        quantity_columns=["total_deviation_qty", "total_withdrawals"],
        amount_columns=["net_market_balance", "total_variation_charges"],
    )


def _nullable_date_key(column: str) -> pl.Expr:
    return (
        pl.when(pl.col(column).is_not_null())
        .then(get_surrogate_key([column]))
        .otherwise(pl.lit(None).cast(pl.String))
    )


def _select_sttm_market_settlements(
    int662: LazyFrame,
    int663: LazyFrame,
    int678: LazyFrame,
    int679: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> LazyFrame:
    combined = pl.concat(
        [
            _provisional_deviation_rows(int662),
            _provisional_variation_rows(int663),
            _nmb_rows(
                int678,
                table_name=SOURCE_TABLES[2],
                report_id="INT678",
                settlement_stage="nmb_daily_amounts",
                has_settlement_run_id=False,
            ),
            _nmb_rows(
                int679,
                table_name=SOURCE_TABLES[3],
                report_id="INT679",
                settlement_stage="nmb_settlement_amounts",
                has_settlement_run_id=True,
            ),
        ],
        how="diagonal_relaxed",
    ).with_columns(
        date_key=_nullable_date_key("gas_date"),
        period_start_date_key=_nullable_date_key("period_start_date"),
        period_end_date_key=_nullable_date_key("period_end_date"),
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
    description="Silver STTM market settlement fact.",
    ins={
        "int662": AssetIn(key=INT662_KEY),
        "int663": AssetIn(key=INT663_KEY),
        "int678": AssetIn(key=INT678_KEY),
        "int679": AssetIn(key=INT679_KEY),
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
def silver_gas_fact_sttm_market_settlement(
    int662: LazyFrame,
    int663: LazyFrame,
    int678: LazyFrame,
    int679: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver STTM market settlement fact asset."""
    return _materialize_result(
        _select_sttm_market_settlements(
            int662,
            int663,
            int678,
            int679,
            facilities,
            zones,
        )
    )


@asset_check(
    asset=silver_gas_fact_sttm_market_settlement,
    name="check_required_fields",
    description="Check required STTM market settlement fields are not null.",
)
def silver_gas_fact_sttm_market_settlement_required_fields(
    input_df: LazyFrame,
) -> AssetCheckResult:
    """Validate required fields for the silver STTM market settlement fact."""
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


silver_gas_fact_sttm_market_settlement_duplicate_row_check = (
    duplicate_row_check_factory(
        assets_definition=silver_gas_fact_sttm_market_settlement,
        check_name="check_for_duplicate_rows",
        primary_key="surrogate_key",
        description="Check that surrogate_key is unique.",
    )
)
silver_gas_fact_sttm_market_settlement_schema_check = schema_matches_check_factor(
    schema=SCHEMA,
    assets_definition=silver_gas_fact_sttm_market_settlement,
    check_name="check_schema_matches",
    description="Check observed schema matches target schema.",
)
silver_gas_fact_sttm_market_settlement_schema_drift_check = schema_drift_check_factory(
    schema=SCHEMA,
    assets_definition=silver_gas_fact_sttm_market_settlement,
    check_name="check_schema_drift",
    description="Check for schema drift against the declared asset schema.",
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver STTM market settlement fact."""
    return Definitions(
        assets=[silver_gas_fact_sttm_market_settlement],
        asset_checks=[
            silver_gas_fact_sttm_market_settlement_duplicate_row_check,
            silver_gas_fact_sttm_market_settlement_schema_check,
            silver_gas_fact_sttm_market_settlement_schema_drift_check,
            silver_gas_fact_sttm_market_settlement_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_sttm_market_settlement_sensor",
                target=[silver_gas_fact_sttm_market_settlement.key],
                default_status=DEFAULT_SENSOR_STATUS,
                run_tags={"ecs/cpu": "512", "ecs/memory": "4096"},
            )
        ],
    )
