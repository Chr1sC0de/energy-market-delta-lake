import polars.testing
from dagster import InMemoryIOManager, asset, materialize
from polars import DataFrame, LazyFrame, read_delta
from types_boto3_s3 import S3Client

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.parameter_specification import (
    PolarsDataFrameReadScanDeltaParamSpec,
    PolarsDataFrameWriteDeltaParamSpec,
    PolarsDeltaLakeMergeParamSpec,
)
from aemo_etl.resource import S3PolarsDeltaLakeIOManager

# pyright: reportUnusedParameter=false


class Test__S3PolarsDeltaLakeIOManager:
    s3_target_table = f"s3://{BRONZE_BUCKET}/aemo/gas/test_table"
    scan_delta_options = PolarsDataFrameReadScanDeltaParamSpec(source=s3_target_table)

    def test__handle_input_overwrite(
        self, create_buckets: None, create_delta_log: None, s3: S3Client
    ):
        test_df = LazyFrame({"col_a": [1, 2, 3], "col_b": [1, 2, 3]})

        @asset(
            io_manager_key="s3_polars_deltalake_io_manager",
            metadata={
                "s3_polars_deltalake_io_manager_options": {
                    "write_delta_options": PolarsDataFrameWriteDeltaParamSpec(
                        target=self.s3_target_table, mode="overwrite"
                    ),
                    "scan_delta_options": self.scan_delta_options,
                }
            },
        )
        def table_asset() -> LazyFrame:
            return test_df

        _ = materialize(
            assets=[table_asset],
            resources={"s3_polars_deltalake_io_manager": S3PolarsDeltaLakeIOManager()},
        )

        polars.testing.assert_frame_equal(
            read_delta(f"{self.s3_target_table}/"), test_df.collect()
        )

    def test__handle_input_merge(
        self, create_buckets: None, create_delta_log: None, s3: S3Client
    ):
        io_manager_key = "s3_polars_deltalake_io_manager"
        df_1 = LazyFrame({"col_a": [1, 2, 3], "col_b": [1, 2, 3]})
        df_2 = LazyFrame({"col_a": [1, 4, 5], "col_b": [2, 4, 5]})

        metadata = {
            "s3_polars_deltalake_io_manager_options": {
                "write_delta_options": PolarsDataFrameWriteDeltaParamSpec(
                    target=self.s3_target_table,
                    mode="merge",
                    delta_merge_options=PolarsDeltaLakeMergeParamSpec(
                        source_alias="s",
                        target_alias="t",
                        predicate="s.col_a = t.col_a",
                        merge_schema=True,
                    ),
                ),
                "scan_delta_options": self.scan_delta_options,
            }
        }

        @asset(io_manager_key=io_manager_key, metadata=metadata)
        def asset_1() -> LazyFrame:
            return df_1

        _ = materialize(
            assets=[asset_1],
            resources={io_manager_key: S3PolarsDeltaLakeIOManager()},
        )

        polars.testing.assert_frame_equal(
            read_delta(self.s3_target_table), df_1.collect()
        )

        @asset(io_manager_key=io_manager_key, metadata=metadata)
        def asset_2() -> LazyFrame:
            return df_2

        _ = materialize(
            assets=[asset_2],
            resources={io_manager_key: S3PolarsDeltaLakeIOManager()},
        )

        polars.testing.assert_frame_equal(
            read_delta(self.s3_target_table).sort("col_a"),
            DataFrame({"col_a": [1, 2, 3, 4, 5], "col_b": [2, 2, 3, 4, 5]}),
        )

    def test__handle_output(
        self, create_buckets: None, create_delta_log: None, s3: S3Client
    ):
        test_df = LazyFrame({"col_a": [1, 2, 3], "col_b": [1, 2, 3]})

        @asset(
            io_manager_key="s3_polars_deltalake_io_manager",
            metadata={
                "s3_polars_deltalake_io_manager_options": {
                    "write_delta_options": PolarsDataFrameWriteDeltaParamSpec(
                        target=self.s3_target_table
                    ),
                    "scan_delta_options": self.scan_delta_options,
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
                "s3_polars_deltalake_io_manager": S3PolarsDeltaLakeIOManager(),
                "in_memory_io_manager": InMemoryIOManager(),
            },
        )

        value_for_output_node = result.output_for_node("dependant_asset")
        polars.testing.assert_frame_equal(value_for_output_node, test_df)
