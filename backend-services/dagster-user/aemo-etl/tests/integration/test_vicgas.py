from os import environ
from pathlib import Path

import pytest
from dagster import AssetKey, AssetSelection, RunConfig
from types_boto3_s3 import S3Client

from aemo_etl.configs import (
    LANDING_BUCKET,
)
from aemo_etl.definitions import defs
from aemo_etl.factories.df_from_s3_keys.assets import DFFromS3KeysConfiguration

BRONZE_KEY_PREFIXES = ["bronze", "vicgas"]
SILVER_KEY_PREFIXES = ["silver", "vicgas"]

LOCAL_DATA_PATH = Path(f"{environ.get('HOME')}/localstack-landing-download")

BRONZE_VICGAS_ASSET_SELECTION = AssetSelection.key_prefixes(
    BRONZE_KEY_PREFIXES
) & AssetSelection.key_substring("bronze_int")

SILVER_VICGAS_ASSET_SELECTION = AssetSelection.key_prefixes(
    SILVER_KEY_PREFIXES
) & AssetSelection.key_substring("silver")


S3_PREFIX = "/".join(BRONZE_KEY_PREFIXES)

root_definitions = defs()

repository_def = root_definitions.get_repository_def()

bronze_asset_keys = sorted(
    BRONZE_VICGAS_ASSET_SELECTION.resolve(repository_def.assets_defs_by_key.values()),
    key=lambda key: tuple(key.path),
)
silver_asset_keys = sorted(
    SILVER_VICGAS_ASSET_SELECTION.resolve(repository_def.assets_defs_by_key.values()),
    key=lambda key: tuple(key.path),
)


def get_local_files(glob_pattern: str) -> list[Path]:
    return list(LOCAL_DATA_PATH.rglob(glob_pattern))


@pytest.mark.parametrize(
    ("bronze_key", "silver_key"),
    zip(bronze_asset_keys, silver_asset_keys),
    ids=[list(key.path)[-1].replace("bronze", "") for key in bronze_asset_keys],
)
def test_vicgas_assets_definitions(
    bronze_key: AssetKey, silver_key: AssetKey, s3: S3Client
) -> None:

    asset_defs = repository_def.assets_defs_by_key.get(bronze_key)

    assert hasattr(asset_defs, "metadata_by_key")

    glob_pattern = asset_defs.metadata_by_key[bronze_key]["glob_pattern"]

    local_file_paths = get_local_files(glob_pattern)

    s3_keys = []

    assert len(local_file_paths) > 0, "nothing to test"

    for file_path in local_file_paths:
        s3_key = f"{S3_PREFIX}/{file_path.name}"

        s3.upload_file(
            file_path.as_posix(),
            LANDING_BUCKET,
            s3_key,
        )

        s3_keys.append(s3_key)

    bronze_result = (
        root_definitions.get_implicit_global_asset_job_def().execute_in_process(
            run_config=RunConfig(
                ops={
                    bronze_key.to_python_identifier(): DFFromS3KeysConfiguration(
                        s3_keys=s3_keys
                    ),
                }
            ),
            asset_selection=[bronze_key],
        )
    )

    assert bronze_result.success

    silver_result = (
        root_definitions.get_implicit_global_asset_job_def().execute_in_process(
            asset_selection=[silver_key],
        )
    )

    for check in silver_result.get_asset_check_evaluations():
        assert check.passed, check.metadata
