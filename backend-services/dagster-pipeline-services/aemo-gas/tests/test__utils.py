import pathlib as pt
from dagster_aws.s3 import S3Resource
import pytest
from aemo_gas.configurations import LANDING_BUCKET
from aemo_gas import utils
from types_boto3_s3.client import S3Client

cwd = pt.Path(__file__).parent
mock_data_folder = cwd / "@mockdata"


@pytest.fixture(scope="function")
def upload_get_s3_object_keys_from_prefix_files(
    create_buckets: None, s3: S3Client
) -> list[str]:
    keys: list[str] = []
    for filepath in (
        mock_data_folder / "mock_get_s3_object_keys_from_prefix_data"
    ).glob("*"):
        key = f"aemo/gas/vichub/{filepath.name}"
        s3.upload_file(
            Filename=filepath.as_posix(),
            Bucket=LANDING_BUCKET,
            Key=key,
        )
        keys.append(key)
    return keys


def test__get_s3_object_keys_from_prefix(
    upload_get_s3_object_keys_from_prefix_files: list[str],
):
    s3_object_keys = utils.get_s3_object_keys_from_prefix_and_name_glob(
        S3Resource(), LANDING_BUCKET, "aemo/gas/vichub", "int128*"
    )

    assert s3_object_keys == [
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401123603.csv",
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401123630.csv",
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401133609.csv",
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401143605.csv",
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401143632.csv",
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401153607.CSV",
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401153636.CSV",
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401163600.csv",
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401163630.csv",
        "aemo/gas/vichub/int128_v4_actual_linepack_1~20250401173608.csv",
    ]
