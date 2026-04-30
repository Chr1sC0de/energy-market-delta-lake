"""Dagster definitions for the silver gas capacity outlook fact asset."""

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
TABLE_NAME = "silver_gas_fact_capacity_outlook"
KEY_PREFIX = ["silver", DOMAIN]
GROUP_NAME = "gas_model"
GRAIN = "one row per source-specific capacity outlook observation"
SURROGATE_KEY_SOURCES = [
    "source_system",
    "source_table",
    "source_facility_id",
    "capacity_type",
    "flow_direction",
    "from_gas_date",
    "to_gas_date",
    "outlook_month",
    "outlook_year",
    "source_surrogate_key",
]
SOURCE_TABLES = [
    "silver.gbb.silver_gasbb_short_term_capacity_outlook",
    "silver.gbb.silver_gasbb_medium_term_capacity_outlook",
    "silver.gbb.silver_gasbb_uncontracted_capacity",
    "silver.gbb.silver_gasbb_nameplate_rating",
    "silver.gbb.silver_gasbb_connection_point_nameplate",
]
SOURCE_SYSTEM = "GBB"
SHORT_KEY = AssetKey(["silver", "gbb", "silver_gasbb_short_term_capacity_outlook"])
MEDIUM_KEY = AssetKey(["silver", "gbb", "silver_gasbb_medium_term_capacity_outlook"])
UNCONTRACTED_KEY = AssetKey(["silver", "gbb", "silver_gasbb_uncontracted_capacity"])
NAMEPLATE_KEY = AssetKey(["silver", "gbb", "silver_gasbb_nameplate_rating"])
CP_NAMEPLATE_KEY = AssetKey(
    ["silver", "gbb", "silver_gasbb_connection_point_nameplate"]
)

_SOURCE_KEY_DEPS = [
    TableColumnDep(asset_key=SHORT_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=MEDIUM_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=UNCONTRACTED_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=NAMEPLATE_KEY, column_name="surrogate_key"),
    TableColumnDep(asset_key=CP_NAMEPLATE_KEY, column_name="surrogate_key"),
]
COLUMN_LINEAGE = TableColumnLineage(
    deps_by_column={
        "surrogate_key": _SOURCE_KEY_DEPS,
        "source_surrogate_key": _SOURCE_KEY_DEPS,
    }
)

SCHEMA = {
    "surrogate_key": pl.String,
    "source_system": pl.String,
    "source_tables": pl.List(pl.String),
    "source_table": pl.String,
    "source_facility_id": pl.String,
    "facility_name": pl.String,
    "capacity_type": pl.String,
    "flow_direction": pl.String,
    "from_gas_date": pl.Date,
    "to_gas_date": pl.Date,
    "outlook_month": pl.Int64,
    "outlook_year": pl.Int64,
    "receipt_location_id": pl.String,
    "delivery_location_id": pl.String,
    "capacity_quantity_tj": pl.Float64,
    "capacity_description": pl.String,
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
    "source_facility_id",
]


def _parse_datetime(column: str) -> pl.Expr:
    source = pl.col(column).cast(pl.String)
    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%d %b %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %b %Y", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %B %Y", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d", strict=False),
    )


def _rows(
    df: LazyFrame,
    source_table: str,
    facility_id: str,
    facility_name: str,
    quantity: str,
    updated: str,
    capacity_type: str,
    flow_direction: str,
    receipt_location: str,
    delivery_location: str,
    capacity_description: str,
    from_date: str | None = None,
    to_date: str | None = None,
    month: str | None = None,
    year: str | None = None,
) -> LazyFrame:
    return df.select(
        source_system=pl.lit(SOURCE_SYSTEM),
        source_tables=pl.lit([source_table]).cast(pl.List(pl.String)),
        source_table=pl.lit(source_table),
        source_facility_id=pl.col(facility_id).cast(pl.String),
        facility_name=pl.col(facility_name).cast(pl.String),
        capacity_type=pl.col(capacity_type).cast(pl.String),
        flow_direction=pl.col(flow_direction).cast(pl.String),
        from_gas_date=_parse_datetime(from_date).dt.date()
        if from_date is not None
        else pl.lit(None).cast(pl.Date),
        to_gas_date=_parse_datetime(to_date).dt.date()
        if to_date is not None
        else pl.lit(None).cast(pl.Date),
        outlook_month=pl.col(month).cast(pl.Int64)
        if month is not None
        else pl.lit(None).cast(pl.Int64),
        outlook_year=pl.col(year).cast(pl.Int64)
        if year is not None
        else pl.lit(None).cast(pl.Int64),
        receipt_location_id=pl.col(receipt_location).cast(pl.String),
        delivery_location_id=pl.col(delivery_location).cast(pl.String),
        capacity_quantity_tj=pl.col(quantity).cast(pl.Float64),
        capacity_description=pl.col(capacity_description).cast(pl.String),
        source_last_updated=pl.col(updated).cast(pl.String),
        source_last_updated_timestamp=_parse_datetime(updated),
        source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
        source_file=pl.col("source_file").cast(pl.String),
        ingested_timestamp=pl.col("ingested_timestamp"),
    )


def _select_capacity_outlook(
    short: LazyFrame,
    medium: LazyFrame,
    uncontracted: LazyFrame,
    nameplate: LazyFrame,
    cp_nameplate: LazyFrame,
) -> LazyFrame:
    rows = [
        _rows(
            short,
            SOURCE_TABLES[0],
            "FacilityId",
            "FacilityName",
            "OutlookQuantity",
            "LastUpdated",
            "CapacityType",
            "FlowDirection",
            "ReceiptLocation",
            "DeliveryLocation",
            "CapacityDescription",
            from_date="GasDate",
        ),
        _rows(
            medium,
            SOURCE_TABLES[1],
            "FacilityId",
            "FacilityName",
            "OutlookQuantity",
            "LastUpdated",
            "CapacityType",
            "FlowDirection",
            "ReceiptLocation",
            "DeliveryLocation",
            "CapacityDescription",
            from_date="FromGasDate",
            to_date="ToGasDate",
        ),
        _rows(
            uncontracted,
            SOURCE_TABLES[2],
            "FacilityId",
            "FacilityName",
            "OutlookQuantity",
            "LastUpdated",
            "CapacityType",
            "FlowDirection",
            "ReceiptLocation",
            "DeliveryLocation",
            "CapacityDescription",
            month="OutlookMonth",
            year="OutlookYear",
        ),
        _rows(
            nameplate,
            SOURCE_TABLES[3],
            "facilityid",
            "facilityname",
            "capacityquantity",
            "lastupdated",
            "capacitytype",
            "flowdirection",
            "receiptlocation",
            "deliverylocation",
            "capacitydescription",
            from_date="effectivedate",
        ),
        cp_nameplate.select(
            source_system=pl.lit(SOURCE_SYSTEM),
            source_tables=pl.lit([SOURCE_TABLES[4]]).cast(pl.List(pl.String)),
            source_table=pl.lit(SOURCE_TABLES[4]),
            source_facility_id=pl.col("FacilityId").cast(pl.String),
            facility_name=pl.col("FacilityName").cast(pl.String),
            capacity_type=pl.lit("connection_point_nameplate"),
            flow_direction=pl.lit(None).cast(pl.String),
            from_gas_date=_parse_datetime("EffectiveDate").dt.date(),
            to_gas_date=pl.lit(None).cast(pl.Date),
            outlook_month=pl.lit(None).cast(pl.Int64),
            outlook_year=pl.lit(None).cast(pl.Int64),
            receipt_location_id=pl.col("ConnectionPointId").cast(pl.String),
            delivery_location_id=pl.lit(None).cast(pl.String),
            capacity_quantity_tj=pl.col("CapacityQuantity").cast(pl.Float64),
            capacity_description=pl.col("Description").cast(pl.String),
            source_last_updated=pl.col("LastUpdated").cast(pl.String),
            source_last_updated_timestamp=_parse_datetime("LastUpdated"),
            source_surrogate_key=pl.col("surrogate_key").cast(pl.String),
            source_file=pl.col("source_file").cast(pl.String),
            ingested_timestamp=pl.col("ingested_timestamp"),
        ),
    ]
    return (
        pl.concat(rows, how="diagonal_relaxed")
        .with_columns(surrogate_key=get_surrogate_key(SURROGATE_KEY_SOURCES))
        .select(list(SCHEMA))
    )


def _materialize_result(value: LazyFrame) -> MaterializeResult[LazyFrame]:
    return MaterializeResult(
        value=value, metadata={"dagster/column_lineage": COLUMN_LINEAGE}
    )


@asset(
    key_prefix=KEY_PREFIX,
    group_name=GROUP_NAME,
    description="Silver gas capacity outlook fact.",
    ins={
        "short": AssetIn(key=SHORT_KEY),
        "medium": AssetIn(key=MEDIUM_KEY),
        "uncontracted": AssetIn(key=UNCONTRACTED_KEY),
        "nameplate": AssetIn(key=NAMEPLATE_KEY),
        "cp_nameplate": AssetIn(key=CP_NAMEPLATE_KEY),
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
def silver_gas_fact_capacity_outlook(
    short: LazyFrame,
    medium: LazyFrame,
    uncontracted: LazyFrame,
    nameplate: LazyFrame,
    cp_nameplate: LazyFrame,
) -> MaterializeResult[LazyFrame]:
    """Materialize the silver gas capacity outlook fact asset."""
    return _materialize_result(
        _select_capacity_outlook(short, medium, uncontracted, nameplate, cp_nameplate)
    )


@asset_check(asset=silver_gas_fact_capacity_outlook, name="check_required_fields")
def silver_gas_fact_capacity_outlook_required_fields(
    input_df: LazyFrame,
) -> AssetCheckResult:
    """Validate required fields for the silver gas capacity outlook fact asset."""
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


silver_gas_fact_capacity_outlook_duplicate_row_check = duplicate_row_check_factory(
    silver_gas_fact_capacity_outlook,
    check_name="check_for_duplicate_rows",
    primary_key="surrogate_key",
)
silver_gas_fact_capacity_outlook_schema_check = schema_matches_check_factor(
    SCHEMA, silver_gas_fact_capacity_outlook, check_name="check_schema_matches"
)
silver_gas_fact_capacity_outlook_schema_drift_check = schema_drift_check_factory(
    SCHEMA, silver_gas_fact_capacity_outlook, check_name="check_schema_drift"
)


@definitions
def defs() -> Definitions:
    """Return Dagster definitions for the silver gas capacity outlook fact asset."""
    return Definitions(
        assets=[silver_gas_fact_capacity_outlook],
        asset_checks=[
            silver_gas_fact_capacity_outlook_duplicate_row_check,
            silver_gas_fact_capacity_outlook_schema_check,
            silver_gas_fact_capacity_outlook_schema_drift_check,
            silver_gas_fact_capacity_outlook_required_fields,
        ],
        sensors=[
            AutomationConditionSensorDefinition(
                name="silver_gas_fact_capacity_outlook_sensor",
                target=[silver_gas_fact_capacity_outlook.key],
                default_status=DEFAULT_SENSOR_STATUS,
            )
        ],
    )
