from io import BytesIO
from pathlib import Path
from typing import Callable, Generator, cast

from dagster import AssetExecutionContext, Output, build_asset_context
from dagster_aws.s3 import S3Resource
from polars import LazyFrame
from pytest import mark
from types_boto3_s3 import S3Client

from aemo_etl.definitions import bronze_vicgas_mibb_reports
from aemo_etl.factory.definition._get_mibb_report_from_s3_files_definition import (
    GetMibbReportFromS3FilesDefinitionBuilder,
)
from aemo_etl.util import get_lazyframe_num_rows

# pyright: reportUnusedParameter=false

CWD = Path(__file__).parent
MOCK_DATA_FOLDER = CWD / "@mockdata/bronze-vicgas"


mibb_report_sub_modules = [
    module for module in dir(bronze_vicgas_mibb_reports) if not module.startswith("_")
]

testable_submmodules = []

for sub_module in mibb_report_sub_modules:
    if "definition_builder" in dir(getattr(bronze_vicgas_mibb_reports, sub_module)):
        testable_submmodules.append(sub_module)

skip = [
    "int135_v4_uplift_cap_1",
    "int112c_v4_ssc_1",
    "int112d_v4_zftc_1",
    "int039b_v4_indicative_locational_price_1",
    "int261_v4_agg_amdq_transferred_1",
    "int310_v1_price_and_withdrawals_rpt_1",
]


@mark.parametrize("submodule_name", testable_submmodules)
def test__asset(
    create_delta_log: None, create_buckets: None, s3: S3Client, submodule_name: str
):
    module = getattr(bronze_vicgas_mibb_reports, submodule_name)
    definition_builder = module.definition_builder

    definition_builder = cast(
        GetMibbReportFromS3FilesDefinitionBuilder, module.definition_builder
    )

    # upload files to our mocked s3
    for file in MOCK_DATA_FOLDER.glob(
        definition_builder.s3_file_glob, case_sensitive=False
    ):
        s3.upload_fileobj(
            Fileobj=BytesIO(file.read_bytes()),
            Bucket=definition_builder.s3_source_bucket,
            Key=f"{definition_builder.s3_source_prefix}/{file.name}",
        )

    table_asset = cast(
        Callable[[AssetExecutionContext, S3Resource], Generator[Output[LazyFrame]]],
        definition_builder.table_asset,
    )

    table_asset = next(iter(table_asset(build_asset_context(), S3Resource()))).value

    table_asset.head().collect()

    if not any([check in submodule_name for check in skip]):
        assert get_lazyframe_num_rows(table_asset) > 0

    for asset_check in definition_builder.asset_checks:
        assert asset_check(table_asset)[0]
