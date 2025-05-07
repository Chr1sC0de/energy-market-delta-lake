from configurations.parameters import DEVELOPMENT_LOCATION
from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions import (
    bronze_download_public_nemweb_files_to_s3,
    bronze_vicgas_mibb_reports,
)
from aemo_etl.register import definitions_list
from aemo_etl.resource import bronze_delta_polars_io_manager
from aemo_etl.resource._polars_parquet_io_manager import PolarsParquetIOManager

__all__ = ["bronze_vicgas_mibb_reports", "bronze_download_public_nemweb_files_to_s3"]

from dagster import (
    AssetSelection,
    AutomationConditionSensorDefinition,
    DefaultSensorStatus,
    Definitions,
    load_asset_checks_from_modules,
    load_assets_from_modules,
)
from dagster_aws.s3 import S3Resource


import aemo_etl


definitions = Definitions.merge(
    Definitions(
        assets=load_assets_from_modules([aemo_etl.asset]),
        asset_checks=load_asset_checks_from_modules([aemo_etl.asset]),
        resources={
            "s3_resource": S3Resource(),
            "bronze_delta_polars_io_manager": bronze_delta_polars_io_manager,
            "bronze_aemo_gas_simple_polars_parquet_io_manager": PolarsParquetIOManager(
                root_uri=f"s3://{BRONZE_BUCKET}", schema="aemo_vicgas"
            ),
        },
        sensors=[
            AutomationConditionSensorDefinition(
                name="automation_condition_sensor",
                target=AssetSelection.all(),
                default_status=DefaultSensorStatus.STOPPED
                if DEVELOPMENT_LOCATION == "local"
                else DefaultSensorStatus.RUNNING,
            ),
        ],
    ),
    *definitions_list,
)
