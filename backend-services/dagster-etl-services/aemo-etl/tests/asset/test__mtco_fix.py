# pyright: reportUnusedParameter=false
from io import BytesIO
from pathlib import Path
from typing import Callable, Generator, cast

from dagster import AssetExecutionContext, Output, build_asset_context
from dagster_aws.s3 import S3Resource
from polars import LazyFrame, scan_delta
from types_boto3_s3 import S3Client

from aemo_etl.definitions import bronze_gasbb_reports
from aemo_etl.util import get_lazyframe_num_rows

CWD = Path(__file__).parent
MOCK_DATA_FOLDER = CWD / "@mockdata/mtco-fix"


testable_submmodules = []


def test__asset(create_delta_log: None, create_buckets: None, s3: S3Client):
    definition_builder = bronze_gasbb_reports.bronze_gasbb_medium_term_capacity_outlook.definition_builder

    for file in MOCK_DATA_FOLDER.glob(
        definition_builder.s3_file_glob, case_sensitive=False
    ):
        s3.upload_fileobj(
            Fileobj=BytesIO(file.read_bytes()),
            Bucket=definition_builder.s3_source_bucket,
            Key=f"{definition_builder.s3_source_prefix}/{file.name}",
        )

    target_s3_table = f"s3://{definition_builder.s3_target_bucket}/{definition_builder.s3_target_prefix}/bronze_gasbb_medium_term_capacity_outlook"

    table_folder = MOCK_DATA_FOLDER / "bronze_gasbb_medium_term_capacity_outlook"

    for file in table_folder.rglob("*", case_sensitive=False):
        if file.is_file():
            s3.upload_fileobj(
                Fileobj=BytesIO(file.read_bytes()),
                Bucket=definition_builder.s3_target_bucket,
                Key=f"{definition_builder.s3_target_prefix}/bronze_gasbb_medium_term_capacity_outlook/{str(file.relative_to(table_folder))}",
            )

    table_asset = cast(
        Callable[[AssetExecutionContext, S3Resource], Generator[Output[LazyFrame]]],
        definition_builder.table_asset,
    )

    table_asset = next(iter(table_asset(build_asset_context(), S3Resource()))).value

    df = scan_delta(target_s3_table)

    assert get_lazyframe_num_rows(df) > 0

    for asset_check in definition_builder.asset_checks:
        assert asset_check(df)[0]
