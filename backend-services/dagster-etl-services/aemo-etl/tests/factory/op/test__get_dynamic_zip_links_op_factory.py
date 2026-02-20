import pathlib as pt
from io import BytesIO

import pytest
from dagster import build_op_context
from dagster_aws.s3 import S3Resource
from types_boto3_s3 import S3Client

from aemo_etl.configuration import LANDING_BUCKET
from aemo_etl.factory.op._get_dynamic_zip_links_op_factory import (
    get_dyanmic_zip_links_op_factory,
)

cwd = pt.Path(__file__).parent
mock_data_folder = cwd / "@mockdata"

mock_files = [
    file for file in mock_data_folder.glob("*") if not file.name.endswith(".py")
]


@pytest.fixture(scope="function", autouse=True)
def upload_files(create_buckets: None, s3: S3Client) -> None:
    for file in mock_files:
        s3.upload_fileobj(
            Fileobj=BytesIO(file.read_bytes()),
            Bucket=LANDING_BUCKET,
            Key=f"prefix/{file.name}",
        )


def test__get_dyanmic_zip_links_op_factory() -> None:
    dynamic = list(
        get_dyanmic_zip_links_op_factory(
            s3_source_bucket=LANDING_BUCKET, s3_source_prefix="prefix"
        )(build_op_context(), S3Resource())
    )
    assert set([item.value for item in dynamic]) == set(
        [f"prefix/{f.name}" for f in mock_files if f.name.lower().endswith(".zip")]
    )
