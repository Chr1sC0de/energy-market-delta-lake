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

KEY_PREFIXES = ["bronze", "gbb"]

LOCAL_DATA_PATH = Path(f"{environ.get('HOME')}/localstack-landing-download")

GBB_ASSET_SELECTION = AssetSelection.key_prefixes(
    KEY_PREFIXES
) & AssetSelection.key_substring("bronze_gasbb")


S3_PREFIX = "/".join(KEY_PREFIXES)

root_definitions = defs()

repository_def = root_definitions.get_repository_def()

asset_keys = sorted(
    GBB_ASSET_SELECTION.resolve(repository_def.assets_defs_by_key.values())
)


def get_local_files(glob_pattern: str) -> list[Path]:
    return list(LOCAL_DATA_PATH.rglob(glob_pattern))


@pytest.mark.parametrize(
    ("key"), asset_keys, ids=[list(key.path)[-1] for key in asset_keys]
)
def test_gbb_assets_definitions(key: AssetKey, s3: S3Client) -> None:

    asset_defs = repository_def.assets_defs_by_key.get(key)

    assert hasattr(asset_defs, "metadata_by_key")

    glob_pattern = asset_defs.metadata_by_key[key]["glob_pattern"]

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

    result = root_definitions.get_implicit_global_asset_job_def().execute_in_process(
        run_config=RunConfig(
            ops={
                key.to_python_identifier(): DFFromS3KeysConfiguration(s3_keys=s3_keys),
            }
        ),
        asset_selection=[key],
    )

    assert result.success

    result.get_asset_check_evaluations()

    for check in result.get_asset_check_evaluations():
        assert check.passed, check.metadata
