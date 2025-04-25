import pathlib as pt
from typing import Callable

import dagster as dg
import polars as pl
import pytest
from dagster_aws.s3 import S3Resource
from types_boto3_s3.client import S3Client

from aemo_gas import factory, utils
from aemo_gas.configurations import BRONZE_BUCKET, LANDING_BUCKET

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                       variables                                        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

cwd = pt.Path(__file__).parent
mock_data_folder = cwd / "@mockdata"

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                        fixtures                                        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@pytest.fixture(scope="function")
def upload_get_s3_object_keys_from_prefix_files(
    create_buckets: None, s3: S3Client
) -> list[str]:
    keys: list[str] = []
    for filepath in (
        mock_data_folder / "mock_get_s3_object_keys_from_prefix_data"
    ).glob("*"):
        key: str = f"aemo/gas/vichub/{filepath.name}"
        s3.upload_file(
            Filename=filepath.as_posix(),
            Bucket=LANDING_BUCKET,
            Key=key,
        )
        keys.append(key)
    return keys


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                         tests                                          │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


def test__get_s3_object_keys_from_prefix_factory(
    upload_get_s3_object_keys_from_prefix_files: list[str],
):
    op_function: Callable[[dg.OpExecutionContext, S3Resource], list[str]] = (
        factory.ops.get_s3_object_keys_from_prefix_factory(
            LANDING_BUCKET, "aemo/gas/vichub", "int128*"
        )
    )
    s3_object_keys: list[str] = op_function(dg.build_op_context(), S3Resource())

    assert set(s3_object_keys) == set(
        [
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
    )


def test__get_dataframe_from_source_files(
    upload_get_s3_object_keys_from_prefix_files: list[str],
):
    s3_resource = S3Resource()
    s3_object_keys = utils.get_s3_object_keys_from_prefix_and_name_glob(
        s3_resource=s3_resource,
        bucket=LANDING_BUCKET,
        prefix="aemo/gas/vichub",
        file_glob="int128*",
    )
    op_function = factory.ops.get_dataframe_from_source_files(
        source_bucket=LANDING_BUCKET,
        target_bucket=BRONZE_BUCKET,
        target_s3_prefix="aemo/gas/vichub",
        target_name="int128_actual_linepack",
        io_manager_key="dummy",
        df_schema={
            "commencement_datetime": pl.String,
            "actual_linepack": pl.Float64,
            "current_date": pl.String,
        },
    )
    output = next(
        iter(op_function(dg.build_op_context(), s3_resource, s3_object_keys))
    ).value

    assert output.collect().shape == (554, 4)
