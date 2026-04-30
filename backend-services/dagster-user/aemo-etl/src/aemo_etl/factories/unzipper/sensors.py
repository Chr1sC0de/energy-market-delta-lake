"""Sensor factory for S3 zip extraction assets."""

from dagster import (
    AssetSelection,
    DagsterRunStatus,
    DefaultSensorStatus,
    RunsFilter,
    SensorDefinition,
    SensorEvaluationContext,
    SensorReturnTypesUnion,
    sensor,
)
from dagster_aws.s3 import S3Resource

from aemo_etl.factories.s3_pending_objects import (
    ACTIVE_RUN_STATUSES,
    plan_s3_pending_objects_run_request,
)
from aemo_etl.utils import (
    get_object_head_from_pages,
    get_s3_pagination,
)


def unzipper_sensor(
    name: str,
    asset_selection: AssetSelection,
    s3_source_bucket: str,
    s3_source_prefix: str,
    bytes_cap: float = 500e6,
    files_cap: int | None = None,
    default_status: DefaultSensorStatus = DefaultSensorStatus.STOPPED,
) -> SensorDefinition:
    """Create a sensor that watches S3 for ``.zip`` files and triggers unzipper assets.

    For each asset in *asset_selection* the sensor reads the asset's
    ``glob_pattern`` metadata (expected to be ``"*.zip"`` or similar), scans
    the S3 prefix for matching files, respects *bytes_cap* / *files_cap* limits,
    and emits a ``RunRequest`` with the matching keys as ``s3_keys`` config.

    The sensor skips assets that are already running or whose last run failed,
    matching the behaviour of ``df_from_s3_keys_sensor``.

    Parameters
    ----------
    name:
        Sensor name registered in Dagster.
    asset_selection:
        The unzipper asset(s) this sensor should target.
    s3_source_bucket:
        S3 bucket to scan for zip files.
    s3_source_prefix:
        S3 prefix within the bucket.
    bytes_cap:
        Maximum total bytes to include in a single run request.  Defaults to
        500 MB (zips are typically large).
    files_cap:
        Optional maximum number of zip files per run request.
    default_status:
        Whether the sensor starts in RUNNING or STOPPED state.
    """

    @sensor(asset_selection=asset_selection, name=name, default_status=default_status)
    def sensor_(
        context: SensorEvaluationContext, s3: S3Resource
    ) -> SensorReturnTypesUnion:
        s3_client = s3.get_client()
        pages = get_s3_pagination(s3_client, s3_source_bucket, s3_source_prefix)

        assert hasattr(context.repository_def, "assets_defs_by_key")

        asset_keys = asset_selection.resolve(
            context.repository_def.assets_defs_by_key.values()
        )

        active_runs = context.instance.get_runs(
            filters=RunsFilter(statuses=list(ACTIVE_RUN_STATUSES))
        )
        completed_runs = context.instance.get_runs(
            filters=RunsFilter(
                statuses=[DagsterRunStatus.SUCCESS, DagsterRunStatus.FAILURE]
            ),
            limit=100,
        )
        object_head_mapping = get_object_head_from_pages(pages, logger=context.log)

        for asset_key in asset_keys:
            run_request = plan_s3_pending_objects_run_request(
                context,
                sensor_name=name,
                asset_key=asset_key,
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
