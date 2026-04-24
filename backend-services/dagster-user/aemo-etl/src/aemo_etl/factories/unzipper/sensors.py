from typing import Sequence, cast

from dagster import (
    AssetKey,
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


def _is_running(runs: Sequence[DagsterRun], asset_key: AssetKey) -> bool:
    for run in runs:
        if run.asset_selection and asset_key in run.asset_selection:
            return True
    return False


def _has_asset_failed(runs: Sequence[DagsterRun], asset_key: AssetKey) -> bool:
    """Return True if the most recent completed run containing this asset failed."""
    for run in runs:
        if run.asset_selection and asset_key in run.asset_selection:
            return run.status == DagsterRunStatus.FAILURE
    return False


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
            filters=RunsFilter(statuses=list(ACTIVE_STATUSES))
        )
        completed_runs = context.instance.get_runs(
            filters=RunsFilter(
                statuses=[DagsterRunStatus.SUCCESS, DagsterRunStatus.FAILURE]
            ),
            limit=100,
        )
        object_head_mapping = get_object_head_from_pages(pages, logger=context.log)

        for asset_key in asset_keys:
            asset_defs = context.repository_def.assets_defs_by_key.get(asset_key)
            assert hasattr(asset_defs, "metadata_by_key")
            asset_meta = cast(dict[str, str], asset_defs.metadata_by_key.get(asset_key))
            assert "glob_pattern" in asset_meta, (
                f"{name} sensor unable to process {asset_key}: missing 'glob_pattern' metadata"
            )
            s3_file_glob = asset_meta["glob_pattern"]

            if _is_running(active_runs, asset_key) or _has_asset_failed(
                completed_runs, asset_key
            ):
                continue

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
                if files_cap is not None and len(objects_to_process) >= files_cap:
                    break
                objects_to_process.append(s3_object_key)
                current_bytes += size_in_bytes

            if objects_to_process:
                yield RunRequest(
                    asset_selection=[asset_key],
                    run_config={
                        "ops": {
                            asset_key.to_python_identifier(): {
                                "config": {
                                    "s3_keys": objects_to_process,
                                },
                            }
                        }
                    },
                )

    return sensor_
