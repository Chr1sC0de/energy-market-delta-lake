from dagster import build_asset_context
from dagster_aws.s3 import S3Resource
from pytest import mark
from io import BytesIO
from pathlib import Path
from types_boto3_s3 import S3Client
from aemo_etl.definitions import bronze_vicgas_mibb_reports
from aemo_etl.util import get_lazyframe_num_rows


# pyright: reportUnusedParameter=false

CWD = Path(__file__).parent
MOCK_DATA_FOLDER = CWD / "@mockdata"

PARQUET_FILES = list(MOCK_DATA_FOLDER.glob("*.parquet"))

mibb_report_sub_modules = [
    module for module in dir(bronze_vicgas_mibb_reports) if not module.startswith("_")
]

testable_submmodules = []

for sub_module in mibb_report_sub_modules:
    if "definition_builder" in dir(getattr(bronze_vicgas_mibb_reports, sub_module)):
        testable_submmodules.append(sub_module)


@mark.parametrize("submodule_name", testable_submmodules)
def test__mibb_report_module(
    create_delta_log: None, create_buckets: None, s3: S3Client, submodule_name: str
):
    module = getattr(bronze_vicgas_mibb_reports, submodule_name)
    definition_builder = module.definition_builder

    for file in MOCK_DATA_FOLDER.glob(definition_builder.s3_file_glob):
        s3.upload_fileobj(
            Fileobj=BytesIO(file.read_bytes()),
            Bucket=definition_builder.s3_source_bucket,
            Key=f"{definition_builder.s3_source_prefix}/{file.name}",
        )

    table_asset = next(
        iter(module.definition_builder.table_asset(build_asset_context(), S3Resource()))
    ).value

    assert get_lazyframe_num_rows(table_asset) > 0
