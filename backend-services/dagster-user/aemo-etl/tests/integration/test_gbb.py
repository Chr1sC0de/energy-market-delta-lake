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

BRONZE_KEY_PREFIXES = ["bronze", "gbb"]
SILVER_KEY_PREFIXES = ["silver", "gbb"]

LOCAL_DATA_PATH = Path(f"{environ.get('HOME')}/localstack-landing-download")

BRONZE_GBB_ASSET_SELECTION = AssetSelection.key_prefixes(
    BRONZE_KEY_PREFIXES
) & AssetSelection.key_substring("bronze_gasbb")

SILVER_GBB_ASSET_SELECTION = AssetSelection.key_prefixes(
    SILVER_KEY_PREFIXES
) & AssetSelection.key_substring("silver_gasbb")


S3_PREFIX = "/".join(BRONZE_KEY_PREFIXES)

ROOT_DEFINITIONS = defs()

REPOSITORY_DEF = ROOT_DEFINITIONS.get_repository_def()

BRONZE_ASSET_KEYS = sorted(
    BRONZE_GBB_ASSET_SELECTION.resolve(REPOSITORY_DEF.assets_defs_by_key.values()),
    key=lambda key: tuple(key.path),
)

SILVER_ASSET_KEYS = sorted(
    SILVER_GBB_ASSET_SELECTION.resolve(REPOSITORY_DEF.assets_defs_by_key.values()),
    key=lambda key: tuple(key.path),
)


def get_local_files(glob_pattern: str) -> list[Path]:
    return list(LOCAL_DATA_PATH.rglob(glob_pattern))


@pytest.mark.parametrize(
    ("bronze_key", "silver_key"),
    zip(BRONZE_ASSET_KEYS, SILVER_ASSET_KEYS),
    ids=[list(key.path)[-1].replace("bronze", "") for key in BRONZE_ASSET_KEYS],
)
def test_gbb_assets_definitions(
    bronze_key: AssetKey, silver_key: AssetKey, s3: S3Client
) -> None:

    asset_defs = REPOSITORY_DEF.assets_defs_by_key.get(bronze_key)

    assert hasattr(asset_defs, "metadata_by_key")

    glob_pattern = asset_defs.metadata_by_key[bronze_key]["glob_pattern"]

    local_file_paths = get_local_files(glob_pattern)

    s3_keys = []

    assert len(local_file_paths) > 0, "nothing to test"

    for i, file_path in enumerate(local_file_paths):
        if i > 10:
            break
        s3_key = f"{S3_PREFIX}/{file_path.name}"

        s3.upload_file(
            file_path.as_posix(),
            LANDING_BUCKET,
            s3_key,
        )

        s3_keys.append(s3_key)

    bronze_result = (
        ROOT_DEFINITIONS.get_implicit_global_asset_job_def().execute_in_process(
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
        ROOT_DEFINITIONS.get_implicit_global_asset_job_def().execute_in_process(
            asset_selection=[silver_key],
        )
    )

    for check in silver_result.get_asset_check_evaluations():
        assert check.passed, check.metadata
