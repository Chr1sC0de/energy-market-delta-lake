import dagster as dg
from dagster_aws.s3 import S3Resource
from aemo_gas.vichub import assets


def test__get_s3_object_keys_op():
    _ = assets.bronze.int029a_system_wide_notices.get_s3_object_keys_op(S3Resource())


def test__combine_to_dataframe_op():
    _ = assets.bronze.int029a_system_wide_notices.combine_to_dataframe_op(
        dg.build_op_context(),
        S3Resource(),
        [
            "aemo/gas/vichub/int029a_v4_system_notices_1~20250309090043.parquet",
            "aemo/gas/vichub/int029a_v4_system_notices_1~20250314090026.parquet",
        ],
    )
