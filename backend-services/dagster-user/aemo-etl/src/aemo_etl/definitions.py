from pathlib import Path

from dagster import Definitions, definitions, load_from_defs_folder
from dagster_aws.s3 import S3Resource, s3_pickle_io_manager

from aemo_etl.configs import DEFAULT_SCHEDULE_STATUS, IO_MANAGER_BUCKET
from aemo_etl.maintenance.delta_tables import (
    delta_table_maintenance_definitions_factory,
)


@definitions
def defs() -> Definitions:
    loaded_definitions = load_from_defs_folder(
        path_within_project=Path(__file__).parent
    )

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
        ),
        loaded_definitions,
        delta_table_maintenance_definitions_factory(
            loaded_definitions,
            default_status=DEFAULT_SCHEDULE_STATUS,
        ),
    )
