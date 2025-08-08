from dagster import (
    AssetSelection,
    AutomationConditionSensorDefinition,
    DefaultSensorStatus,
    Definitions,
)
from dagster_aws.s3 import S3Resource, s3_pickle_io_manager

import aemo_etl
from aemo_etl.configuration import IO_MANAGER_BUCKET
from aemo_etl.definitions import (
    bronze_download_public_nemweb_files_to_s3,
    bronze_vicgas_mibb_reports,
    bronze_gasbb_reports,
)
from aemo_etl.register import definitions_list
from aemo_etl.resource import (
    S3PolarsDeltaLakeIOManager,
    S3PolarsParquetIOManager,
)
from aemo_etl.configuration import DEVELOPMENT_LOCATION
from aemo_etl.definitions.sensors import sensor_aemo_vicgas_jobs, sensor_aemo_gasbb_jobs

definitions = Definitions.merge(
    Definitions(
        assets=aemo_etl.asset.asset_list,
        asset_checks=aemo_etl.asset.asset_check_list,
        resources={
            "s3": S3Resource(),
            "s3_polars_parquet_io_manager": S3PolarsParquetIOManager(),
            "s3_polars_deltalake_io_manager": S3PolarsDeltaLakeIOManager(),
            "io_manager": s3_pickle_io_manager.configured(
                {
                    "s3_bucket": IO_MANAGER_BUCKET,
                    "s3_prefix": "dagster/storage",
                }
            ),
        },
        sensors=[
            sensor_aemo_vicgas_jobs,
            sensor_aemo_gasbb_jobs,
            AutomationConditionSensorDefinition(
                name="sensor_automation_condition",
                target=AssetSelection.all(),
                default_status=DefaultSensorStatus.STOPPED
                if DEVELOPMENT_LOCATION == "local"
                else DefaultSensorStatus.RUNNING,
            ),
        ],
    ),
    *definitions_list,
)

__all__ = [
    "bronze_vicgas_mibb_reports",
    "bronze_gasbb_reports",
    "bronze_download_public_nemweb_files_to_s3",
]
