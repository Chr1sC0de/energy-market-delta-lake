from io import BytesIO
from typing import cast

import polars as pl
import pytest
from dagster import build_asset_context
from dagster_aws.s3 import S3Resource
from polars import Datetime, Int64, LazyFrame, String, col
from types_boto3_s3 import S3Client

from aemo_etl.configs import ARCHIVE_BUCKET, LANDING_BUCKET
from aemo_etl.factories.df_from_s3_keys.assets import (
    DFFromS3KeysConfiguration,
    bronze_df_from_s3_keys_asset_factory,
)
from aemo_etl.factories.df_from_s3_keys.hooks import Deduplicate, Hook
from tests.utils import MakeBucketProtocol

MOCK_DATA_CSV = LazyFrame({"a": [1, 2, 3], "b": [3, 4, 5], "c": [6, 7, 8]})
MOCK_DATA_PARQUET = LazyFrame({"a": [9, 10, 11], "b": [12, 13, 14], "c": [15, 16, 17]})
MOCK_SCHEMA = {
    "a": Int64,
    "b": Int64,
    "c": Int64,
    "source_file": String,
    "surrogate_key": String,
    "ingested_timestamp": Datetime("ms", "UTC"),
}
MOCK_DESCRIPTIONS = {"a": "a column", "b": "b column", "c": "c column"}


@pytest.fixture(autouse=True)
def s3_archive_bucket(
    make_bucket: MakeBucketProtocol,
) -> str:
    bucket = make_bucket(ARCHIVE_BUCKET)
    return bucket


@pytest.fixture(autouse=True)
def s3_landing_bucket(
    s3: S3Client,
    make_bucket: MakeBucketProtocol,
    create_delta_log: None,
) -> str:
    bucket = make_bucket(LANDING_BUCKET)
    MOCK_DATA_CSV.sink_csv(f"s3://{bucket}/mock_data.csv")
    MOCK_DATA_PARQUET.sink_parquet(f"s3://{bucket}/mock_data.parquet")
    MOCK_DATA_PARQUET.sink_parquet(f"s3://{bucket}/mock_data.invalid_extenstion")
    s3.upload_fileobj(
        Fileobj=BytesIO(b""),
        Bucket=bucket,
        Key="empty_file.csv",
    )

    return bucket


class PassthroughBytesHook(Hook[bytes]):
    def process(self, s3_bucket: str, s3_key: str, object_: bytes) -> bytes:
        return object_


def test_df_from_s3_keys_factory(
    s3_landing_bucket: str, s3_archive_bucket: str, caplog: pytest.LogCaptureFixture
) -> None:
    captured: list[str] = []

    mock_context = build_asset_context()

    asset = bronze_df_from_s3_keys_asset_factory(
        MOCK_SCHEMA,
        ["a"],
        postprocess_object_hooks=[PassthroughBytesHook()],
        postprocess_lazyframe_hooks=[Deduplicate()],
        s3_archive_bucket=s3_archive_bucket,
        s3_landing_bucket=s3_landing_bucket,
    )

    def mock_info(msg: str) -> None:
        captured.append(msg)

    mock_context.log.info = mock_info  # ty:ignore[invalid-assignment]

    df = cast(
        LazyFrame,
        asset(
            mock_context,
            S3Resource(),
            DFFromS3KeysConfiguration(
                s3_keys=[
                    "mock_data.csv",
                    "mock_data.parquet",
                    "mock_data.invalid_extension",
                    "empty_file.csv",
                    "no_such_key.csv",
                ],
            ),
        ),
    )

    assert len(captured) == 3
    assert df.select(pl.len()).collect().item() == 6  # ty:ignore[unresolved-attribute]
    assert df.filter(col.surrogate_key.is_null()).collect().is_empty()  # ty:ignore[unresolved-attribute]
    assert df.filter(col.ingested_timestamp.is_null()).collect().is_empty()  # ty:ignore[unresolved-attribute]


def test_df_from_s3_keys_factory_no_valid_files(
    s3_landing_bucket: str, s3_archive_bucket: str
) -> None:
    mock_context = build_asset_context()
    asset = bronze_df_from_s3_keys_asset_factory(
        MOCK_SCHEMA,
        ["a"],
        s3_archive_bucket=s3_archive_bucket,
        s3_landing_bucket=s3_landing_bucket,
    )
    df = cast(
        LazyFrame,
        asset(
            mock_context,
            S3Resource(),
            DFFromS3KeysConfiguration(s3_keys=["empty_file.csv"]),
        ),
    )
    assert df.select(pl.len()).collect().item() == 0  # ty:ignore[unresolved-attribute]
