# pyright: reportUnusedParameter=false

import shutil

from dagster import RunConfig, materialize
from polars import DataFrame, read_delta
from polars import testing as polars_testing

from aemo_etl.asset.admin import deduplicate_rows
from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.resource._s3_polars_parquet_io_manager import S3PolarsParquetIOManager

testable_submmodules = []


def test__deduplicate_asset(create_delta_log: None, create_buckets: None) -> None:
    test_df = DataFrame({"a": [1, 1, 3], "b": [1, 1, 7], "c": [1, 2, 3]})
    target_df = DataFrame({"a": [1, 3], "b": [1, 7], "c": [1, 3]})

    s3_uri = f".tmp/{BRONZE_BUCKET}/test-df"
    config = deduplicate_rows.DeduplicateConfig(s3_uri=s3_uri, primary_keys=["a", "b"])

    test_df.write_delta(s3_uri, mode="overwrite")

    _ = materialize(
        assets=[deduplicate_rows.asset],
        run_config=RunConfig({"admin__deduplicate_lazyframe_rows": config}),
        resources={"s3_polars_parquet_io_manager": S3PolarsParquetIOManager()},
    )

    read_df = read_delta(s3_uri)

    shutil.rmtree(s3_uri)

    polars_testing.assert_frame_equal(read_df, target_df)
