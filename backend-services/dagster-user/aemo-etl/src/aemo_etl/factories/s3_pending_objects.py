"""Helpers for planning sensor-triggered runs from pending S3 objects."""

from collections.abc import Mapping, Sequence
from typing import cast

from dagster import (
    AssetKey,
    DagsterRun,
    DagsterRunStatus,
    RunRequest,
    SensorEvaluationContext,
)

from aemo_etl.utils import (
    S3ObjectHead,
    get_s3_object_keys_from_prefix_and_name_glob,
)

ACTIVE_RUN_STATUSES = (
    DagsterRunStatus.QUEUED,
    DagsterRunStatus.NOT_STARTED,
    DagsterRunStatus.STARTING,
    DagsterRunStatus.STARTED,
)


def is_asset_running(runs: Sequence[DagsterRun], asset_key: AssetKey) -> bool:
    """Return whether an active run already targets the asset."""
    for run in runs:
        if run.asset_selection and asset_key in run.asset_selection:
            return True
    return False


def has_asset_failed(runs: Sequence[DagsterRun], asset_key: AssetKey) -> bool:
    """Return True if the most recent completed run containing this asset failed."""
    for run in runs:
        if run.asset_selection and asset_key in run.asset_selection:
            return run.status == DagsterRunStatus.FAILURE
    return False


def get_asset_glob_pattern(
    context: SensorEvaluationContext,
    *,
    sensor_name: str,
    asset_key: AssetKey,
) -> str:
    """Read the S3 glob pattern from Dagster asset metadata."""
    assert hasattr(context.repository_def, "assets_defs_by_key")

    asset_defs = context.repository_def.assets_defs_by_key.get(asset_key)
    assert hasattr(asset_defs, "metadata_by_key")
    asset_meta = cast(
        Mapping[str, object] | None,
        asset_defs.metadata_by_key.get(asset_key),
    )
    assert asset_meta is not None and "glob_pattern" in asset_meta, (
        f"{sensor_name} sensor unable to process {asset_key}: missing 'glob_pattern' metadata"
    )
    glob_pattern = asset_meta["glob_pattern"]
    assert isinstance(glob_pattern, str), (
        f"{sensor_name} sensor unable to process {asset_key}: 'glob_pattern' metadata must be a string"
    )
    return glob_pattern


def select_s3_pending_object_keys(
    *,
    s3_source_prefix: str,
    s3_file_glob: str,
    object_head_mapping: Mapping[str, S3ObjectHead],
    bytes_cap: float,
    files_cap: int | None,
) -> list[str]:
    """Select matching S3 object keys while respecting byte and file caps."""
    s3_object_keys = get_s3_object_keys_from_prefix_and_name_glob(
        s3_prefix=s3_source_prefix,
        s3_file_glob=s3_file_glob,
        original_keys=list(object_head_mapping.keys()),
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

    return objects_to_process


def build_s3_keys_run_config(
    *,
    asset_key: AssetKey,
    s3_keys: Sequence[str],
) -> dict[str, object]:
    """Build Dagster run config for selected S3 keys."""
    return {
        "ops": {
            asset_key.to_python_identifier(): {
                "config": {
                    "s3_keys": list(s3_keys),
                },
            },
        },
    }


def build_s3_pending_objects_run_request(
    *,
    asset_key: AssetKey,
    s3_keys: Sequence[str],
) -> RunRequest | None:
    """Build a run request for pending S3 keys when any keys are selected."""
    if not s3_keys:
        return None
    return RunRequest(
        asset_selection=[asset_key],
        run_config=build_s3_keys_run_config(asset_key=asset_key, s3_keys=s3_keys),
    )


def plan_s3_pending_objects_run_request(
    context: SensorEvaluationContext,
    *,
    sensor_name: str,
    asset_key: AssetKey,
    active_runs: Sequence[DagsterRun],
    completed_runs: Sequence[DagsterRun],
    s3_source_prefix: str,
    object_head_mapping: Mapping[str, S3ObjectHead],
    bytes_cap: float,
    files_cap: int | None,
) -> RunRequest | None:
    """Plan a run request for an asset by scanning pending S3 objects."""
    s3_file_glob = get_asset_glob_pattern(
        context,
        sensor_name=sensor_name,
        asset_key=asset_key,
    )

    if is_asset_running(active_runs, asset_key) or has_asset_failed(
        completed_runs, asset_key
    ):
        return None

    objects_to_process = select_s3_pending_object_keys(
        s3_source_prefix=s3_source_prefix,
        s3_file_glob=s3_file_glob,
        object_head_mapping=object_head_mapping,
        bytes_cap=bytes_cap,
        files_cap=files_cap,
    )
    return build_s3_pending_objects_run_request(
        asset_key=asset_key,
        s3_keys=objects_to_process,
    )
