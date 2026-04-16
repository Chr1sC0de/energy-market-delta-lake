from typing import Sequence, cast

from dagster import (
    AssetKey,
    AssetSelection,
    DagsterRun,
    DagsterRunStatus,
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


def is_running(runs: Sequence[DagsterRun], asset_key: AssetKey) -> bool:
    for run in runs:
        if run.asset_selection:
            if asset_key in run.asset_selection:
                return True
    return False


def factory(
    name: str,
    asset_selection: AssetSelection,
    s3_source_bucket: str,
    s3_source_prefix: str,
    # 200mb for a 1024 ram ecs instance
    bytes_cap: float = 200e6,
) -> SensorDefinition:

    @sensor(asset_selection=asset_selection, name=name)
    def sensor_(
        context: SensorEvaluationContext, s3: S3Resource
    ) -> SensorReturnTypesUnion:
        s3_client = s3.get_client()
        pages = get_s3_pagination(s3_client, s3_source_bucket, s3_source_prefix)

        assert hasattr(context.repository_def, "assets_defs_by_key")

        asset_keys = asset_selection.resolve(
            context.repository_def.assets_defs_by_key.values()
        )

        runs = context.instance.get_runs(
            filters=RunsFilter(statuses=list(ACTIVE_STATUSES))
        )
        object_head_mapping = get_object_head_from_pages(pages, logger=context.log)

        for asset_key in asset_keys:
            asset_defs = context.repository_def.assets_defs_by_key.get(asset_key)
            assert hasattr(asset_defs, "metadata_by_key")
            asset_meta = cast(dict[str, str], asset_defs.metadata_by_key.get(asset_key))
            assert "glob_pattern" in asset_meta, (
                f"{name} sensor unable to process {asset_key}"
            )
            s3_file_glob = asset_meta["glob_pattern"]

            if not is_running(runs, asset_key):
                s3_object_keys = get_s3_object_keys_from_prefix_and_name_glob(
                    s3_prefix=s3_source_prefix,
                    s3_file_glob=s3_file_glob,
                    original_keys=cast(list[str], object_head_mapping.keys()),
                )
                current_bytes = 0
                objects_to_process = []

                for s3_object_key in s3_object_keys:
                    object_head = object_head_mapping[s3_object_key]

                    size_in_bytes = object_head["Size"]
                    if current_bytes + size_in_bytes > bytes_cap:
                        break
                    objects_to_process.append(s3_object_key)
                    current_bytes += size_in_bytes

                if s3_object_keys:
                    # ensure
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
