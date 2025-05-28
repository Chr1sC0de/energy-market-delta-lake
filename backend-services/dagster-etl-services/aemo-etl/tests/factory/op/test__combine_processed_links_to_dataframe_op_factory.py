from pytest import fixture
from datetime import datetime
from dagster import OpExecutionContext, build_op_context
from polars import Datetime, LazyFrame, String, col
import polars.testing
from aemo_etl.configuration import ProcessedLink
from aemo_etl.factory.op._combine_processed_links_to_dataframe_op_factory import (
    combine_processed_links_to_dataframe_op_factory,
)


now = datetime.now()

schema = {
    "source_absolute_href": String,
    "source_upload_datetime": Datetime("ms", time_zone="Australia/Melbourne"),
    "target_s3_href": String,
    "target_s3_bucket": String,
    "target_s3_prefix": String,
    "target_s3_name": String,
    "target_ingested_datetime": Datetime("ms", time_zone="Australia/Melbourne"),
}


@fixture(scope="module")
def processed_links() -> list[ProcessedLink]:
    return [
        ProcessedLink(
            source_absolute_href=f"mock{i}",
            target_s3_href=f"mock{i}",
            target_s3_bucket=f"mock{i}",
            target_s3_prefix=f"mock{i}",
            target_s3_name=f"mock{i}",
            target_ingested_datetime=now,
            source_upload_datetime=now,
        )
        for i in range(0, 20)
    ]


class Test__combine_processed_links_to_dataframe_op_factory:
    def test__no_hook(self, processed_links: list[ProcessedLink]):
        df = combine_processed_links_to_dataframe_op_factory(schema=schema)(
            build_op_context(),
            processed_links,
        )

        polars.testing.assert_frame_equal(
            df,
            LazyFrame(
                dict(
                    source_absolute_href=[f"mock{i}" for i in range(20)],
                    source_upload_datetime=[now] * 20,
                    target_s3_href=[f"mock{i}" for i in range(20)],
                    target_s3_bucket=[f"mock{i}" for i in range(20)],
                    target_s3_prefix=[f"mock{i}" for i in range(20)],
                    target_s3_name=[f"mock{i}" for i in range(20)],
                    target_ingested_datetime=[now] * 20,
                ),
                schema=schema,
            ).with_columns(
                col("source_upload_datetime").dt.convert_time_zone("UTC"),
                col("target_ingested_datetime").dt.convert_time_zone("UTC"),
            ),
        )

    def test__with_hook(self, processed_links: list[ProcessedLink]):
        def mock_hook(_: OpExecutionContext, df: LazyFrame) -> LazyFrame:
            return df

        df = combine_processed_links_to_dataframe_op_factory(
            schema=schema, post_process_dataframe_hook=mock_hook
        )(
            build_op_context(),
            processed_links,
        )

        polars.testing.assert_frame_equal(
            df,
            LazyFrame(
                dict(
                    source_absolute_href=[f"mock{i}" for i in range(20)],
                    source_upload_datetime=[now] * 20,
                    target_s3_href=[f"mock{i}" for i in range(20)],
                    target_s3_bucket=[f"mock{i}" for i in range(20)],
                    target_s3_prefix=[f"mock{i}" for i in range(20)],
                    target_s3_name=[f"mock{i}" for i in range(20)],
                    target_ingested_datetime=[now] * 20,
                ),
                schema=schema,
            ).with_columns(
                col("source_upload_datetime").dt.convert_time_zone("UTC"),
                col("target_ingested_datetime").dt.convert_time_zone("UTC"),
            ),
        )
