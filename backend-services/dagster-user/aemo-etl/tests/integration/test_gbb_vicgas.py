from itertools import repeat
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

ROOT_DEFINITIONS = defs()

REPOSITORY_DEF = ROOT_DEFINITIONS.get_repository_def()

LOCAL_DATA_PATH = Path(f"{environ.get('HOME')}/localstack-landing-download")


def get_key_name(asset_key: AssetKey) -> str:
    return list(asset_key.path)[-1]


def get_asset_keys(key_prefixes: list[str], key_substring: str) -> list[AssetKey]:
    asset_selection = AssetSelection.key_prefixes(
        key_prefixes
    ) & AssetSelection.key_substring(key_substring)
    return sorted(
        asset_selection.resolve(REPOSITORY_DEF.assets_defs_by_key.values()),
        key=lambda key: tuple(key.path),
    )


def get_local_files(glob_pattern: str) -> list[Path]:
    return list(LOCAL_DATA_PATH.rglob(glob_pattern))


gbb_asset_set = zip(
    get_asset_keys(["bronze", "gbb"], "bronze_gasbb"),
    get_asset_keys(["silver", "gbb"], "silver_gasbb"),
    repeat("bronze/gbb"),
    repeat(10),
)

vicgas_asset_set = zip(
    get_asset_keys(["bronze", "vicgas"], "bronze_int"),
    get_asset_keys(["silver", "vicgas"], "silver_int"),
    repeat("bronze/vicgas"),
    repeat(1000),
)

all_asset_key_sets = [*gbb_asset_set, *vicgas_asset_set]


@pytest.mark.parametrize(
    ("bronze_key", "silver_key", "s3_prefix", "n_files"),
    all_asset_key_sets,
    ids=[
        get_key_name(asset_key_set[0]).replace("bronze", "")
        for asset_key_set in all_asset_key_sets
    ],
)
def test_gbb_assets_definitions(
    bronze_key: AssetKey,
    silver_key: AssetKey,
    s3_prefix: str,
    n_files: int,
    s3: S3Client,
) -> None:

    asset_defs = REPOSITORY_DEF.assets_defs_by_key.get(bronze_key)

    assert hasattr(asset_defs, "metadata_by_key")

    glob_pattern = asset_defs.metadata_by_key[bronze_key]["glob_pattern"]

    local_file_paths = get_local_files(glob_pattern)

    s3_keys = []

    assert len(local_file_paths) > 0, "nothing to test"

    for i, file_path in enumerate(local_file_paths):
        if i > n_files:
            break
        s3_key = f"{s3_prefix}/{file_path.name}"

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
