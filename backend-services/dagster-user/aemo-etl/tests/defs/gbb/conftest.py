import fnmatch
from typing import Callable

import pytest
from types_boto3_s3 import S3Client

from aemo_etl.configs import AEMO_BUCKET, ARCHIVE_BUCKET, LANDING_BUCKET
from tests.utils import GBB_DATA_DIR, MakeBucketProtocol

GBB_S3_PREFIX = "bronze/gbb"


@pytest.fixture
def gbb_buckets(
    make_bucket: MakeBucketProtocol,
    create_delta_log: None,
) -> None:
    make_bucket(LANDING_BUCKET, random_suffix=False)
    make_bucket(ARCHIVE_BUCKET, random_suffix=False)
    make_bucket(AEMO_BUCKET, random_suffix=False)


@pytest.fixture
def upload_gbb_files(
    s3: S3Client,
    gbb_buckets: None,
) -> Callable[[str], list[str]]:

    def _upload(glob_pattern: str, max_files: int = 4) -> list[str]:
        matching = sorted(
            f
            for f in GBB_DATA_DIR.iterdir()
            if fnmatch.fnmatch(f.name.lower(), glob_pattern.lower())
        )[:max_files]
        s3_keys: list[str] = []
        for f in matching:
            key = f"{GBB_S3_PREFIX}/{f.name}"
            s3.put_object(Bucket=LANDING_BUCKET, Key=key, Body=f.read_bytes())
            s3_keys.append(key)
        return s3_keys

    return _upload
