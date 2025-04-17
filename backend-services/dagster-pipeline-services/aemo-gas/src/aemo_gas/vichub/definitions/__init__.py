# import the definitions
from . import bronze

# construct the core definitions
import dagster as dg
from dagster import Definitions
from dagster_aws.s3 import S3Resource

from aemo_gas import vichub
from aemo_gas.vichub.resources import (
    bronze_aemo_gas_upsert_io_manager,
    s3_pickle_io_manager,
)
from configurations.parameters import DEVELOPMENT_LOCATION

all = Definitions.merge(
    Definitions(
        assets=[*vichub.assets.all],
        jobs=[*vichub.jobs.all],
        schedules=[*vichub.schedules.all],
        asset_checks=[*vichub.assets.checks],
        sensors=[
            dg.AutomationConditionSensorDefinition(
                name="automation_condition_sensor",
                target=dg.AssetSelection.all(),
                default_status=dg.DefaultSensorStatus.STOPPED
                if DEVELOPMENT_LOCATION == "local"
                else dg.DefaultSensorStatus.RUNNING,
            ),
            *vichub.sensors.all,
        ],
        resources={
            "bronze_aemo_gas_upsert_io_manager": bronze_aemo_gas_upsert_io_manager,
            "s3_resource": S3Resource(region_name="ap-southeast-2"),
            "s3_pickle_io_manager": s3_pickle_io_manager,
        },
    ),
    *bronze.all,
)
