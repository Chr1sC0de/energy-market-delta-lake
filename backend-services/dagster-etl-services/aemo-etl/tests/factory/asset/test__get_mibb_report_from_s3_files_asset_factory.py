from io import BytesIO
from pathlib import Path
from dagster import AssetExecutionContext, materialize
from dagster_aws.s3 import S3Resource
from dagster_delta import (
    DeltaLakePolarsIOManager,
    MergeConfig,
    MergeType,
    S3Config,
    SchemaMode,
    WriteMode,
)
from polars import LazyFrame, col, read_delta
from pytest import fixture
from types_boto3_s3 import S3Client

from aemo_etl.configuration import BRONZE_BUCKET, LANDING_BUCKET
from aemo_etl.factory.asset import get_mibb_report_from_s3_files_asset_factory
from aemo_etl.util import newline_join


cwd = Path(__file__).parent
mock_data_folder = cwd / "@mockdata/upload_sample_1"
mock_data_files = list(mock_data_folder.glob("*"))

# pyright: reportUnusedParameter=false


@fixture(scope="function", autouse=True)
def upload_mock_files(create_buckets: None, create_delta_log: None, s3: S3Client):
    for file_ in mock_data_files:
        s3.upload_fileobj(
            Fileobj=BytesIO(file_.read_bytes()),
            Bucket=LANDING_BUCKET,
            Key=f"aemo_vicgas/{file_.name}",
        )


def test__get_mibb_report_from_s3_files_asset_factory(s3: S3Client):
    root_uri = f"s3://{BRONZE_BUCKET}"

    bronze_aemo_gas_deltalake_upsert_io_manager = DeltaLakePolarsIOManager(
        root_uri=root_uri,
        storage_options=S3Config(),
        mode=WriteMode.merge,
        schema_mode=SchemaMode.overwrite,
        merge_config=MergeConfig(
            merge_type=MergeType.upsert,
            source_alias="s",
            target_alias="t",
        ),
    )

    def post_process_hook(context: AssetExecutionContext, df: LazyFrame):
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

    schema_name = "aemo_vicgas"

    asset = get_mibb_report_from_s3_files_asset_factory(
        s3_source_bucket=LANDING_BUCKET,
        s3_source_prefix="aemo_vicgas",
        s3_source_file_glob="int037b*",
        key_prefix=["aemo", "gas"],
        name=table_name,
        table_schema=None,
        metadata={
            "merge_predicate": newline_join(
                "s.transmission_group_id=t.transmission_group_id",
                "and s.schedule_type_id=t.schedule_type_id",
                "and s.transmission_id=t.transmission_id",
                "and s.demand_type_name=t.demand_type_name",
            ),
            "schema": schema_name,
        },
        post_process_hook=post_process_hook,
        io_manager_key="bronze_aemo_gas_deltalake_upsert_io_manager",
    )

    _ = materialize(
        assets=[asset],
        resources={
            "s3_resource": S3Resource(),
            "bronze_aemo_gas_deltalake_upsert_io_manager": bronze_aemo_gas_deltalake_upsert_io_manager,
        },
    )

    assert read_delta(f"{root_uri}/{schema_name}/{table_name}").shape == (45, 9)
