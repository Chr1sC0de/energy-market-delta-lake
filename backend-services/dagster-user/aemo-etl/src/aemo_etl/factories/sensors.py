"""Sensor factories for S3-key driven raw ingestion assets."""

from typing import Sequence

from dagster import (
    AssetSelection,
    DagsterRun,
    DagsterRunStatus,
    DefaultSensorStatus,
    RunsFilter,
    SensorDefinition,
    SensorEvaluationContext,
    SensorReturnTypesUnion,
    sensor,
)
from dagster._core.definitions.target import ExecutableDefinition
from dagster_aws.s3 import S3Resource

from aemo_etl.factories.s3_pending_objects import (
    ACTIVE_RUN_STATUSES,
    has_job_failed as _has_job_failed,
    is_job_running,
    plan_s3_pending_objects_job_run_request,
)
from aemo_etl.utils import (
    get_object_head_from_pages,
    get_s3_pagination,
)

ACTIVE_STATUSES = list(ACTIVE_RUN_STATUSES)


def is_running(runs: Sequence[DagsterRun], job_name: str) -> bool:
    """Return whether an active run already uses the job name."""
    return is_job_running(runs, job_name)


def has_job_failed(runs: Sequence[DagsterRun], job_name: str) -> bool:
    """Return True if the most recent completed run for this job failed.

    Scans ``runs`` in order (expected newest-first) and returns the status of
    the first run whose ``job_name`` matches ``job_name``.  If no matching run
    is found the function returns False.
    """
    return _has_job_failed(runs, job_name)


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
    """Create a sensor that launches raw ingestion jobs for matching S3 keys."""

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
            name_suffix = list(bronze_key.parts)[-1].replace("bronze_", "")
            job_name = f"{name_suffix}_job"

            run_request = plan_s3_pending_objects_job_run_request(
                context,
                sensor_name=name,
                asset_key=bronze_key,
                job_name=job_name,
                active_runs=active_runs,
                completed_runs=completed_runs,
                s3_source_prefix=s3_source_prefix,
                object_head_mapping=object_head_mapping,
                bytes_cap=bytes_cap,
                files_cap=files_cap,
            )
            if run_request is not None:
                yield run_request

    return sensor_
