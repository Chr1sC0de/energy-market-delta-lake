from io import BytesIO
from pathlib import Path
from typing import Generator, cast

from dagster import AssetExecutionContext, Output, build_asset_context
from dagster_aws.s3 import S3Resource
from polars import LazyFrame, col
from pytest import fixture
from types_boto3_s3 import S3Client

from aemo_etl.configuration import LANDING_BUCKET
from aemo_etl.factory.asset import get_df_from_s3_files_asset_factory

cwd = Path(__file__).parent
mock_data_folder = cwd / "@mockdata/upload_sample_1"
mock_data_files = list(mock_data_folder.glob("*"))

# pyright: reportUnusedParameter=false


@fixture(scope="function", autouse=True)
def upload_mock_files(
    create_buckets: None, create_delta_log: None, s3: S3Client
) -> None:
    for file_ in mock_data_files:
        s3.upload_fileobj(
            Fileobj=BytesIO(file_.read_bytes()),
            Bucket=LANDING_BUCKET,
            Key=f"aemo_vicgas/{file_.name}",
        )


def test__get_mibb_report_from_s3_files_asset_factory(s3: S3Client) -> None:
    def post_process_hook(context: AssetExecutionContext, df: LazyFrame) -> LazyFrame:
        df_out = df.filter(
            (col("current_date") == col("current_date").max()).over(
                "demand_type_name",
                "schedule_type_id",
                "transmission_group_id",
                "transmission_id",
            )
        ).sort("transmission_id")
        return df_out

    table_name = "bronze_int029_indicative_market_price"

    asset = get_df_from_s3_files_asset_factory(
        s3_source_bucket=LANDING_BUCKET,
        s3_source_prefix="aemo_vicgas",
        s3_source_file_glob="int037b*",
        key_prefix=["bronze", "aemo", "gas"],
        name=table_name,
        post_process_hook=post_process_hook,
        io_manager_key="bronze_aemo_gas_deltalake_upsert_io_manager",
    )

    results = cast(
        Generator[Output[LazyFrame]], asset(build_asset_context(), S3Resource())
    )

    df = next(iter(results)).value

    assert df.collect().shape == (45, 9)
