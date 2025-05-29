from dagster import (
    AssetSelection,
    AutomationConditionSensorDefinition,
    DefaultSensorStatus,
    Definitions,
)
from dagster_aws.s3 import S3Resource

import aemo_etl
from aemo_etl.definitions import (
    bronze_download_public_nemweb_files_to_s3,
    bronze_vicgas_mibb_reports,
)
from aemo_etl.register import definitions_list
from aemo_etl.resource import (
    S3PolarsDeltaLakeIOManager,
    S3PolarsParquetIOManager,
)
from configurations.parameters import DEVELOPMENT_LOCATION

definitions = Definitions.merge(
    Definitions(
        assets=aemo_etl.asset.asset_list,
        asset_checks=aemo_etl.asset.asset_check_list,
        resources={
            "s3_resource": S3Resource(),
            "s3_polars_parquet_io_manager": S3PolarsParquetIOManager(),
            "s3_polars_deltalake_io_manager": S3PolarsDeltaLakeIOManager(),
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

__all__ = ["bronze_vicgas_mibb_reports", "bronze_download_public_nemweb_files_to_s3"]
