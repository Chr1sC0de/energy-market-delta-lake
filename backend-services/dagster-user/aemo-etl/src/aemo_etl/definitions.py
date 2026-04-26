from pathlib import Path

from dagster import Definitions, definitions, load_from_defs_folder
from dagster_aws import ecs
from dagster_aws.s3 import S3Resource, s3_pickle_io_manager

from aemo_etl.configs import DEVELOPMENT_LOCATION, IO_MANAGER_BUCKET

AWS_ECS_EXECUTOR_CONFIG = {
    "cpu": 512,
    "memory": 4096,
    "max_concurrent": 3,
}


@definitions
def defs() -> Definitions:
    return Definitions.merge(
        Definitions(
            resources={
                "s3": S3Resource(),
                "io_manager": s3_pickle_io_manager.configured(
                    {
                        "s3_bucket": IO_MANAGER_BUCKET,
                        "s3_prefix": "dagster/storage",
                    }
                ),
            },
            executor=(
                ecs.ecs_executor.configured(AWS_ECS_EXECUTOR_CONFIG)
                if DEVELOPMENT_LOCATION == "aws"
                else None
            ),
        ),
        load_from_defs_folder(path_within_project=Path(__file__).parent),
    )
