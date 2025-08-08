from io import BytesIO
from pathlib import Path

from dagster import build_op_context
from dagster_aws.s3 import S3Resource
from pytest import fixture, mark
from types_boto3_s3 import S3Client

from aemo_etl.configuration import BRONZE_BUCKET, LANDING_BUCKET
from aemo_etl.factory.op._unzip_s3_file_from_key_op_factory import (
    unzip_s3_file_from_key_op_factory,
)

# pyright: reportUnusedParameter=false, reportArgumentType=false

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                       variables                                        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

cwd = Path(__file__).parent

mock_data_folder = cwd / "@mockdata"

zip_files = list(mock_data_folder.glob("*.zip"))

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                        fixtures                                        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@fixture(scope="function", autouse=True)
def upload_files_to_s3(create_buckets: None, s3: S3Client):
    for file in zip_files:
        s3.upload_fileobj(
            Fileobj=BytesIO(file.read_bytes()),
            Bucket=LANDING_BUCKET,
            Key=f"mockdata/prefix/{file.name}",
        )


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                       functions                                        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


def validate_unzipped_files(s3: S3Client, unzipped_files: dict[str, str]):
    for dict_ in unzipped_files:
        bucket = dict_["Bucket"]
        key = dict_["Key"]
        response = s3.head_object(Bucket=bucket, Key=key)
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                         tests                                          │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


class Test__unzip_s3_file_from_key_op_factory:
    @mark.parametrize("zip_file", zip_files)
    def test__same_target_target_directory_and_prefix(
        self, s3: S3Client, zip_file: Path
    ):
        unzipped_files = unzip_s3_file_from_key_op_factory(
            s3_source_bucket=LANDING_BUCKET,
            s3_target_bucket=LANDING_BUCKET,
            s3_target_prefix="mockdata/prefix",
        )(
            context=build_op_context(),
            s3=S3Resource(),
            s3_source_key=f"mockdata/prefix/{zip_file.name}",
        )
        assert len(unzipped_files) > 2
        validate_unzipped_files(s3, unzipped_files)

    @mark.parametrize("zip_file", zip_files)
    def test__different_bucket(self, s3: S3Client, zip_file: Path):
        unzipped_files = unzip_s3_file_from_key_op_factory(
            s3_source_bucket=LANDING_BUCKET,
            s3_target_bucket=BRONZE_BUCKET,
            s3_target_prefix="mockdata/prefix",
        )(
            context=build_op_context(),
            s3=S3Resource(),
            s3_source_key=f"mockdata/prefix/{zip_file.name}",
        )
        assert len(unzipped_files) > 2
        validate_unzipped_files(s3, unzipped_files)

    @mark.parametrize("zip_file", zip_files)
    def test__different_prefix(self, s3: S3Client, zip_file: Path):
        unzipped_files = unzip_s3_file_from_key_op_factory(
            s3_source_bucket=LANDING_BUCKET,
            s3_target_bucket=LANDING_BUCKET,
            s3_target_prefix="mockdatat/prefix_2",
        )(
            context=build_op_context(),
            s3=S3Resource(),
            s3_source_key=f"mockdata/prefix/{zip_file.name}",
        )
        assert len(unzipped_files) > 2
        validate_unzipped_files(s3, unzipped_files)

    @mark.parametrize("zip_file", zip_files)
    def test__different_prefix_and_bucket(self, s3: S3Client, zip_file: Path):
        unzipped_files = unzip_s3_file_from_key_op_factory(
            s3_source_bucket=LANDING_BUCKET,
            s3_target_bucket=BRONZE_BUCKET,
            s3_target_prefix="mockdatat/prefix_2",
        )(
            context=build_op_context(),
            s3=S3Resource(),
            s3_source_key=f"mockdata/prefix/{zip_file.name}",
        )
        assert len(unzipped_files) > 2
        validate_unzipped_files(s3, unzipped_files)
