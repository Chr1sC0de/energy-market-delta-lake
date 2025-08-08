from dagster import AssetIn, AutomationCondition, MetadataValue
from dagster import asset as dagster_asset
from polars import LazyFrame, col

from aemo_etl.configuration import (
    SILVER_BUCKET,
)
from aemo_etl.configuration.mibb.bronze_int041_v4_market_and_reference_prices_1 import (
    schema_descriptions,
    primary_keys,
    group_name,
)
from aemo_etl.factory.asset import (
    compact_and_vacuum_dataframe_asset_factory,
)
from aemo_etl.factory.check import (
    check_primary_keys_are_unique_factory,
)
from aemo_etl.parameter_specification import (
    PolarsDataFrameReadScanDeltaParamSpec,
    PolarsDataFrameWriteDeltaParamSpec,
)

key_prefix = ["silver", "aemo", "mibb"]
table_name = "silver_int041_market_and_reference_prices"
s3_prefix = "aemo/mibb"
s3_table_location = f"s3://{SILVER_BUCKET}/{s3_prefix}/{table_name}"
s3_polars_deltalake_io_manager_options = {
    "write_delta_options": PolarsDataFrameWriteDeltaParamSpec(
        target=s3_table_location,
        mode="overwrite",
    ),
    "scan_delta_options": PolarsDataFrameReadScanDeltaParamSpec(
        source=s3_table_location
    ),
}


@dagster_asset(
    name=table_name,
    key_prefix=key_prefix,
    io_manager_key="s3_polars_deltalake_io_manager",
    ins={
        "bronze_int041_v4_market_and_reference_prices_1": AssetIn(
            key_prefix=["bronze", "aemo", "vicgas"]
        ),
    },
    group_name=group_name,
    metadata={
        "dagster/primary_keys": MetadataValue.json(primary_keys),
        "dagster/column_description": schema_descriptions,
        "s3_polars_deltalake_io_manager_options": s3_polars_deltalake_io_manager_options,
    },
    automation_condition=AutomationCondition.eager()
    .without(~AutomationCondition.any_deps_missing())
    .with_label("eager_allow_missing"),
)
def table_asset(
    bronze_int041_v4_market_and_reference_prices_1: LazyFrame,
) -> LazyFrame:
    return bronze_int041_v4_market_and_reference_prices_1.with_columns(
        col("gas_date")
        .str.to_datetime("%d %b %Y", time_zone="Australia/Melbourne", time_unit="ms")
        .dt.convert_time_zone("UTC"),
        col("current_date")
        .str.to_datetime(
            "%d %b %Y %H:%M:%S", time_zone="Australia/Melbourne", time_unit="ms"
        )
        .dt.convert_time_zone("UTC"),
    )


compact_and_vacuum_asset = compact_and_vacuum_dataframe_asset_factory(
    group_name="aemo__optimize",
    key_prefix=["optimize"] + key_prefix,
    s3_target_bucket=SILVER_BUCKET,
    s3_target_prefix=s3_prefix,
    s3_target_table_name=table_name,
    retention_hours=0,
    dependant_definitions=[table_asset],
    storage_options=None,
    automation_condition=AutomationCondition.on_cron("@daily"),
)

asset_check = check_primary_keys_are_unique_factory(
    table_asset, primary_keys=primary_keys
)
