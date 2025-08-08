#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                create the asset sensor                                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


from dagster import (
    DagsterInstance,
    DagsterRunStatus,
    DefaultSensorStatus,
    RunRequest,
    RunsFilter,
    SensorEvaluationContext,
    sensor,
)
from dagster_aws.s3 import S3Resource

from aemo_etl.configuration import LANDING_BUCKET, mibb
from aemo_etl.definitions import bronze_vicgas_mibb_reports
from aemo_etl.util import (
    get_s3_object_keys_from_prefix_and_name_glob,
    get_s3_pagination,
)
from aemo_etl.configuration import DEVELOPMENT_LOCATION

configurations = [getattr(mibb, name) for name in dir(mibb) if not name.startswith("_")]


jobs = [
    getattr(bronze_vicgas_mibb_reports, name).definition_builder.table_asset_job
    for name in dir(bronze_vicgas_mibb_reports)
    if name.startswith("bronze_int")
]


def has_job_failed(instance: DagsterInstance, job_name: str) -> bool:
    runs = instance.get_runs(limit=1, filters=RunsFilter(job_name=job_name))
    if runs:
        return runs[0].status.value == "FAILURE"
    return False


@sensor(
    name="sensor_aemo_vicgas_jobs",
    minimum_interval_seconds=30,
    jobs=jobs,
    default_status=(
        DefaultSensorStatus.STOPPED
        if DEVELOPMENT_LOCATION == "local"
        else DefaultSensorStatus.RUNNING
    ),  # Sensor is turned on by default
)
def sensor_aemo_vicgas_jobs(context: SensorEvaluationContext, s3: S3Resource):
    s3_client = s3.get_client()
    s3_source_bucket = LANDING_BUCKET
    s3_source_prefix = "aemo/vicgas"
    pages = get_s3_pagination(s3_client, s3_source_bucket, s3_source_prefix)
    for configuration in configurations:
        name = configuration.table_name
        s3_file_glob = configuration.s3_file_glob

        asset_job_name = f"asset_{name}_job"

        core_job_run_records = context.instance.get_run_records(
            RunsFilter(
                job_name=asset_job_name,
                statuses=[
                    DagsterRunStatus.QUEUED,
                    DagsterRunStatus.NOT_STARTED,
                    DagsterRunStatus.STARTING,
                    DagsterRunStatus.STARTED,
                ],
            )
        )

        # kill the sensor if the job has failed

        if len(core_job_run_records) == 0 and not has_job_failed(
            context.instance, asset_job_name
        ):
            s3_object_keys = get_s3_object_keys_from_prefix_and_name_glob(
                s3_client=s3_client,
                s3_bucket=s3_source_bucket,
                s3_prefix=s3_source_prefix,
                s3_file_glob=s3_file_glob,
                case_insensitive=True,
                pages=pages,
            )

            s3_object_keys = [
                key
                for key in s3_object_keys
                if not any([key.lower().endswith(ignore) for ignore in [".zip"]])
            ]

            if len(s3_object_keys) > 0:
                yield RunRequest(job_name=asset_job_name)
