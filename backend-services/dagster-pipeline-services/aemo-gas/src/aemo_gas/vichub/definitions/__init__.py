# import the definitions
from .. import resources
from . import bronze

# construct the core definitions
import dagster as dg
from dagster_aws.s3 import S3Resource
from configurations.parameters import DEVELOPMENT_LOCATION
from aemo_gas.vichub import assets


all = dg.Definitions.merge(
    dg.Definitions(
        assets=[assets.bronze.mibb.report_list.asset],
        resources={
            "bronze_aemo_gas_deltalake_upsert_io_manager": resources.bronze_aemo_gas_deltalake_upsert_io_manager,
            "bronze_aemo_gas_simple_polars_parquet_io_manager": resources.bronze_aemo_gas_simple_polars_parquet_io_manager,
            "s3_resource": S3Resource(region_name="ap-southeast-2"),
            "s3_pickle_io_manager": resources.s3_pickle_io_manager,
        },
        sensors=[
            dg.AutomationConditionSensorDefinition(
                name="automation_condition_sensor",
                target=dg.AssetSelection.all(),
                default_status=dg.DefaultSensorStatus.STOPPED
                if DEVELOPMENT_LOCATION == "local"
                else dg.DefaultSensorStatus.RUNNING,
            ),
        ],
    ),
    *bronze.definitions,
)
