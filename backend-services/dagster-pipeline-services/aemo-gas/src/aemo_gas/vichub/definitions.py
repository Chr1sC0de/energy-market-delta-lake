from aemo_gas.vichub.resources import (
    bronze_aemo_gas_upsert_io_manager,
    s3_pickle_io_manager,
)
from dagster_aws.s3 import S3Resource
from dagster import Definitions
from aemo_gas import vichub


all = Definitions(
    assets=[*vichub.assets.all],
    jobs=[*vichub.jobs.all],
    schedules=[*vichub.schedules.all],
    asset_checks=[*vichub.assets.checks],
    resources={
        "bronze_aemo_gas_upsert_io_manager": bronze_aemo_gas_upsert_io_manager,
        "s3_resource": S3Resource(region_name="ap-southeast-2"),
        "s3_pickle_io_manager": s3_pickle_io_manager,
    },
)
