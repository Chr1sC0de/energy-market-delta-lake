from datetime import datetime
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from dagster import build_op_context
from dagster_aws.s3 import S3Resource
from polars import read_parquet
from types_boto3_s3 import S3Client

from aemo_etl.configuration import LANDING_BUCKET, Link
from aemo_etl.factory.op import download_link_and_upload_to_s3_op_factory

# pyright: reportUnusedParameter=false, reportAny=false, reportMissingTypeStubs=false

cwd = Path(__file__).parent

mock_data_folder = cwd / "@mockdata"

mock_files = {f.name: f for f in mock_data_folder.glob("*")}


class Test__download_link_and_upload_to_s3_op_factory:
    def test__upload_csv_link(self, s3: S3Client, create_buckets: None):
        with patch("requests.get") as mocked_requests_get:
            target_file = "INT891_V1_EDDACT_1.CSV"

            mocked_requests_get.return_value.raise_for_status = lambda: None
            mocked_requests_get.return_value.content = mock_files[
                target_file
            ].read_bytes()

            processed_link = download_link_and_upload_to_s3_op_factory(
                s3_landing_bucket=LANDING_BUCKET,
                s3_landing_prefix="mock/prefix",
            )(
                build_op_context(),
                S3Resource(),
                Link(
                    source_absolute_href=f"fs://@mockdata/{target_file}",
                    source_upload_datetime=datetime.now(),
                ),
            )

            buffer = BytesIO()

            s3.download_fileobj(
                Bucket=processed_link.target_s3_bucket,
                Key=f"{processed_link.target_s3_prefix}/{processed_link.target_s3_name}",
                Fileobj=buffer,
            )

            assert read_parquet(buffer).shape == (118, 5)

    def test__upload_zip_link(self, s3: S3Client, create_buckets: None):
        with patch("requests.get") as mocked_requests_get:
            target_file = "PUBLICRPTS01.zip"

            mocked_requests_get.return_value.raise_for_status = lambda: None
            mocked_requests_get.return_value.content = mock_files[
                target_file
            ].read_bytes()

            processed_link = download_link_and_upload_to_s3_op_factory(
                LANDING_BUCKET,
                "mock/prefix",
            )(
                build_op_context(),
                S3Resource(),
                Link(
                    source_absolute_href=f"fs://@mockdata/{target_file}",
                    source_upload_datetime=datetime.now(),
                ),
            )

            buffer = BytesIO()

            s3.download_fileobj(
                Bucket=processed_link.target_s3_bucket,
                Key=f"{processed_link.target_s3_prefix}/{processed_link.target_s3_name}",
                Fileobj=buffer,
            )

            _ = buffer.seek(0)

            assert buffer.read() == mock_files[target_file].read_bytes()
