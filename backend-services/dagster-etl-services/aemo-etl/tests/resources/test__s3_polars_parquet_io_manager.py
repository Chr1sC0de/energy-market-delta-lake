from dagster import InMemoryIOManager, asset, materialize
from polars import LazyFrame, read_parquet
import polars.testing
from types_boto3_s3 import S3Client

from aemo_etl.resource import S3PolarsParquetIOManager
from aemo_etl.parameter_specification import (
    PolarsLazyFrameScanParquetParamSpec,
    PolarsLazyFrameSinkParquetParamSpec,
)
from aemo_etl.configuration import BRONZE_BUCKET


# pyright: reportUnusedParameter=false


class Test__S3PolarsParquetIOManager:
    s3_target_table = f"s3://{BRONZE_BUCKET}/aemo/gas/test_table"
    sink_parquet_options = PolarsLazyFrameSinkParquetParamSpec(
        path=f"{s3_target_table}/result.parquet"
    )
    scan_parquet_options = PolarsLazyFrameScanParquetParamSpec(
        source=f"{s3_target_table}/"
    )

    def test__hand_input(
        self, create_buckets: None, create_delta_log: None, s3: S3Client
    ):
        test_df = LazyFrame({"col_a": [1, 2, 3], "col_b": [1, 2, 3]})

        @asset(
            io_manager_key="s3_polars_parquet_io_manager",
            metadata={
                "s3_polars_parquet_io_manager_options": {
                    "scan_parquet_options": self.scan_parquet_options,
                    "sink_parquet_options": self.sink_parquet_options,
                }
            },
        )
        def table_asset() -> LazyFrame:
            return test_df

        _ = materialize(
            assets=[table_asset],
            resources={"s3_polars_parquet_io_manager": S3PolarsParquetIOManager()},
        )

        polars.testing.assert_frame_equal(
            read_parquet(f"{self.s3_target_table}/"), test_df.collect()
        )

    def test__handle_output(
        self, create_buckets: None, create_delta_log: None, s3: S3Client
    ):
        test_df = LazyFrame({"col_a": [1, 2, 3], "col_b": [1, 2, 3]})

        @asset(
            io_manager_key="s3_polars_parquet_io_manager",
            metadata={
                "s3_polars_parquet_io_manager_options": {
                    "sink_parquet_options": self.sink_parquet_options,
                    "scan_parquet_options": self.scan_parquet_options,
                }
            },
        )
        def table_asset() -> LazyFrame:
            return test_df

        @asset(io_manager_key="in_memory_io_manager")
        def dependant_asset(table_asset: LazyFrame) -> LazyFrame:
            return table_asset

        result = materialize(
            assets=[table_asset, dependant_asset],
            resources={
                "s3_polars_parquet_io_manager": S3PolarsParquetIOManager(),
                "in_memory_io_manager": InMemoryIOManager(),
            },
        )

        value_for_output_node = result.output_for_node("dependant_asset")
        polars.testing.assert_frame_equal(value_for_output_node, test_df)
