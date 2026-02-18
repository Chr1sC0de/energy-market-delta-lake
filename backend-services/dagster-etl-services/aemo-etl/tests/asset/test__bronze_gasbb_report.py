from io import BytesIO
from pathlib import Path
from typing import Callable, Generator, cast

import polars as pl
from dagster import AssetExecutionContext, Output, build_asset_context
from dagster_aws.s3 import S3Resource
from polars import LazyFrame
from pytest import mark
from types_boto3_s3 import S3Client

from aemo_etl.configuration.gasbb import GASBB_CONFIGS
from aemo_etl.configuration.gasbb.hooks import get_hooks_for_report
from aemo_etl.definitions.bronze_gasbb_reports.utils import (
    definition_builder_factory,
)
from aemo_etl.factory.definition._get_mibb_report_from_s3_files_definition import (
    GetMibbReportFromS3FilesDefinitionBuilder,
)
from aemo_etl.util import get_lazyframe_num_rows

# pyright: reportUnusedParameter=false

CWD = Path(__file__).parent
MOCK_DATA_FOLDER = CWD / "@mockdata/bronze-gasbb"

# Get all testable configs from registry
testable_configs = list(GASBB_CONFIGS.keys())

skip = []


@mark.parametrize("table_name", testable_configs)
def test__asset(
    create_delta_log: None, create_buckets: None, s3: S3Client, table_name: str
):
    # Get config from registry
    config = GASBB_CONFIGS[table_name]

    # Get hooks for this report
    hooks = get_hooks_for_report(table_name)

    # Build definition
    definition_builder = cast(
        GetMibbReportFromS3FilesDefinitionBuilder,
        definition_builder_factory(
            config=config,
            process_object_hook=hooks.get("process_object_hook"),
            preprocess_hook=hooks.get("preprocess_hook"),
            post_process_hook=hooks.get("post_process_hook"),
            datetime_pattern=hooks.get("datetime_pattern"),
            datetime_column_name=hooks.get("datetime_column_name"),
        ),
    )

    mock_s3_data_files = list(
        MOCK_DATA_FOLDER.glob(definition_builder.s3_file_glob, case_sensitive=False)
    )

    # upload files to our mocked s3
    for file in mock_s3_data_files:
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

    if not any([check in table_name for check in skip]):
        assert get_lazyframe_num_rows(table_asset) > 0

    assert len(table_asset.filter(pl.col.surrogate_key.is_null()).collect()) == 0

    for asset_check in definition_builder.asset_checks:
        assert asset_check(table_asset)[0]
