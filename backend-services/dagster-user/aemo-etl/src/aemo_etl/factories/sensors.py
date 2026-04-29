from typing import Sequence, cast

from dagster import (
    AssetSelection,
    DagsterRun,
    DagsterRunStatus,
    DefaultSensorStatus,
    RunRequest,
    RunsFilter,
    SensorDefinition,
    SensorEvaluationContext,
    SensorReturnTypesUnion,
    sensor,
)
from dagster._core.definitions.target import ExecutableDefinition
from dagster_aws.s3 import S3Resource

from aemo_etl.utils import (
    get_object_head_from_pages,
    get_s3_object_keys_from_prefix_and_name_glob,
    get_s3_pagination,
)

ACTIVE_STATUSES = [
    DagsterRunStatus.QUEUED,
    DagsterRunStatus.NOT_STARTED,
    DagsterRunStatus.STARTING,
    DagsterRunStatus.STARTED,
]


def is_running(runs: Sequence[DagsterRun], job_name: str) -> bool:
    for run in runs:
        if run.job_name == job_name:
            return True
    return False


def has_job_failed(runs: Sequence[DagsterRun], job_name: str) -> bool:
    """Return True if the most recent completed run for this job failed.

    Scans ``runs`` in order (expected newest-first) and returns the status of
    the first run whose ``job_name`` matches ``job_name``.  If no matching run
    is found the function returns False.
    """
    for run in runs:
        if run.job_name == job_name:
            return run.status == DagsterRunStatus.FAILURE
    return False


def df_from_s3_keys_sensor(
    name: str,
    asset_selection: AssetSelection,
    s3_source_bucket: str,
    s3_source_prefix: str,
    bytes_cap: float = 200e6,
    files_cap: int | None = None,
    default_status: DefaultSensorStatus = DefaultSensorStatus.STOPPED,
    jobs: Sequence[ExecutableDefinition] | None = None,
) -> SensorDefinition:

    @sensor(
        name=name,
        default_status=default_status,
        jobs=jobs,
    )
    def sensor_(
        context: SensorEvaluationContext, s3: S3Resource
    ) -> SensorReturnTypesUnion:
        s3_client = s3.get_client()
        pages = get_s3_pagination(s3_client, s3_source_bucket, s3_source_prefix)

        assert hasattr(context.repository_def, "assets_defs_by_key")

        bronze_keys = asset_selection.resolve(
            context.repository_def.assets_defs_by_key.values()
        )

        active_runs = context.instance.get_runs(
            filters=RunsFilter(statuses=list(ACTIVE_STATUSES))
        )
        completed_runs = context.instance.get_runs(
            filters=RunsFilter(
                statuses=[DagsterRunStatus.SUCCESS, DagsterRunStatus.FAILURE]
            ),
            limit=100,
        )
        object_head_mapping = get_object_head_from_pages(pages, logger=context.log)

        for bronze_key in bronze_keys:
            asset_defs = context.repository_def.assets_defs_by_key.get(bronze_key)
            assert hasattr(asset_defs, "metadata_by_key")
            asset_meta = cast(
                dict[str, str], asset_defs.metadata_by_key.get(bronze_key)
            )
            assert "glob_pattern" in asset_meta, (
                f"{name} sensor unable to process {bronze_key}"
            )
            s3_file_glob = asset_meta["glob_pattern"]
            name_suffix = list(bronze_key.parts)[-1].replace("bronze_", "")
            job_name = f"{name_suffix}_job"

            if not is_running(active_runs, job_name) and not has_job_failed(
                completed_runs, job_name
            ):
                s3_object_keys = get_s3_object_keys_from_prefix_and_name_glob(
                    s3_prefix=s3_source_prefix,
                    s3_file_glob=s3_file_glob,
                    original_keys=cast(list[str], object_head_mapping.keys()),
                )
                current_bytes = 0
                objects_to_process: list[str] = []

                for s3_object_key in s3_object_keys:
                    object_head = object_head_mapping[s3_object_key]

                    size_in_bytes = object_head["Size"]
                    if current_bytes + size_in_bytes > bytes_cap:
                        break
                    if files_cap is not None:
                        if len(objects_to_process) >= files_cap:
                            break
                    objects_to_process.append(s3_object_key)
                    current_bytes += size_in_bytes

                if s3_object_keys:
                    yield RunRequest(
                        job_name=job_name,
                        run_config={
                            "ops": {
                                bronze_key.to_python_identifier(): {
                                    "config": {
                                        "s3_keys": objects_to_process,
                                    },
                                }
                            }
                        },
                    )

    return sensor_
