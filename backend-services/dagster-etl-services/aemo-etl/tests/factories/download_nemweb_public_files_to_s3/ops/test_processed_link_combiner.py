from datetime import datetime

import pytest
from dagster import OpExecutionContext, build_op_context
from polars import LazyFrame, Schema
from polars.datatypes import Datetime, String

from aemo_etl.factories.download_nemweb_public_files_to_s3.data_models import (
    ProcessedLink,
)
from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.processed_link_combiner import (
    ProcessedLinkedCombiner,
    S3ProcessedLinkCombiner,
    build_process_link_combiner_op,
)


class ConcreteS3ProcessedLinkCombiner(S3ProcessedLinkCombiner):
    def combine(
        self,
        context: OpExecutionContext,
        processed_links: list[ProcessedLink | None],
        schema: Schema,
    ) -> LazyFrame:
        return super().combine(context, processed_links, schema)


@pytest.fixture
def mock_schema() -> Schema:
    return Schema(
        {
            "source_absolute_href": String,
            "source_upload_datetime": Datetime(time_zone="UTC"),
            "target_s3_href": String,
            "target_s3_bucket": String,
            "target_s3_prefix": String,
            "target_s3_name": String,
            "target_ingested_datetime": Datetime(time_zone="UTC"),
        }
    )


@pytest.fixture
def mock_processed_links() -> list[ProcessedLink | None]:
    return [
        ProcessedLink(
            source_absolute_href="https://example.com.au/reports/file1.csv",
            source_upload_datetime=datetime(2025, 1, 1, 10, 0, 0),
            target_s3_href="s3://test-bucket/prefix/file1.csv",
            target_s3_bucket="test-bucket",
            target_s3_prefix="prefix",
            target_s3_name="file1.csv",
            target_ingested_datetime=datetime(2025, 1, 1, 10, 5, 0),
        ),
        ProcessedLink(
            source_absolute_href="https://example.com.au/reports/file2.csv",
            source_upload_datetime=datetime(2025, 1, 2, 11, 0, 0),
            target_s3_href="s3://test-bucket/prefix/file2.csv",
            target_s3_bucket="test-bucket",
            target_s3_prefix="prefix",
            target_s3_name="file2.csv",
            target_ingested_datetime=datetime(2025, 1, 2, 11, 5, 0),
        ),
        ProcessedLink(
            source_absolute_href="https://example.com.au/reports/file3.csv",
            source_upload_datetime=datetime(2025, 1, 3, 12, 0, 0),
            target_s3_href="s3://test-bucket/prefix/file3.csv",
            target_s3_bucket="test-bucket",
            target_s3_prefix="prefix",
            target_s3_name="file3.csv",
            target_ingested_datetime=datetime(2025, 1, 3, 12, 5, 0),
        ),
    ]


def test_build_process_link_combiner_op(
    mock_schema: Schema, mock_processed_links: list[ProcessedLink]
) -> None:
    class MockProcessedLinkCombiner(ProcessedLinkedCombiner):
        def combine(
            self,
            context: OpExecutionContext,
            processed_links: list[ProcessedLink | None],
            schema: Schema,
        ) -> LazyFrame:
            return LazyFrame(
                {
                    "source_absolute_href": ["https://example.com.au/test.csv"],
                    "source_upload_datetime": [datetime(2025, 1, 1, 10, 0, 0)],
                    "target_s3_href": ["s3://test-bucket/prefix/test.csv"],
                    "target_s3_bucket": ["test-bucket"],
                    "target_s3_prefix": ["prefix"],
                    "target_s3_name": ["test.csv"],
                    "target_ingested_datetime": [datetime(2025, 1, 1, 10, 5, 0)],
                },
                schema=schema,
            )

    combiner_op = build_process_link_combiner_op(
        "mock",
        mock_schema,
        None,
        None,
        MockProcessedLinkCombiner(),
    )

    result = combiner_op(build_op_context(), mock_processed_links)

    assert isinstance(result, LazyFrame)
    collected = result.collect()
    assert len(collected) == 1
    assert collected["source_absolute_href"][0] == "https://example.com.au/test.csv"


class TestS3ProcessedLinkCombiner:
    def test_combine_creates_lazyframe(
        self, mock_schema: Schema, mock_processed_links: list[ProcessedLink | None]
    ) -> None:
        combiner = ConcreteS3ProcessedLinkCombiner()

        result = combiner.combine(build_op_context(), mock_processed_links, mock_schema)

        assert isinstance(result, LazyFrame)
        collected = result.collect()
        assert len(collected) == 3

    def test_combine_has_correct_columns(
        self, mock_schema: Schema, mock_processed_links: list[ProcessedLink | None]
    ) -> None:
        combiner = ConcreteS3ProcessedLinkCombiner()

        result = combiner.combine(build_op_context(), mock_processed_links, mock_schema)

        collected = result.collect()
        expected_columns = [
            "source_absolute_href",
            "source_upload_datetime",
            "target_s3_href",
            "target_s3_bucket",
            "target_s3_prefix",
            "target_s3_name",
            "target_ingested_datetime",
        ]
        assert list(collected.columns) == expected_columns

    def test_combine_has_correct_data(
        self, mock_schema: Schema, mock_processed_links: list[ProcessedLink | None]
    ) -> None:
        combiner = ConcreteS3ProcessedLinkCombiner()

        result = combiner.combine(build_op_context(), mock_processed_links, mock_schema)

        collected = result.collect()
        assert (
            collected["source_absolute_href"][0]
            == "https://example.com.au/reports/file1.csv"
        )
        assert (
            collected["source_absolute_href"][1]
            == "https://example.com.au/reports/file2.csv"
        )
        assert (
            collected["source_absolute_href"][2]
            == "https://example.com.au/reports/file3.csv"
        )
        assert collected["target_s3_name"][0] == "file1.csv"
        assert collected["target_s3_name"][1] == "file2.csv"
        assert collected["target_s3_name"][2] == "file3.csv"

    def test_combine_filters_none_values(self, mock_schema: Schema) -> None:
        processed_links_with_none: list[ProcessedLink | None] = [
            ProcessedLink(
                source_absolute_href="https://example.com.au/reports/file1.csv",
                source_upload_datetime=datetime(2025, 1, 1, 10, 0, 0),
                target_s3_href="s3://test-bucket/prefix/file1.csv",
                target_s3_bucket="test-bucket",
                target_s3_prefix="prefix",
                target_s3_name="file1.csv",
                target_ingested_datetime=datetime(2025, 1, 1, 10, 5, 0),
            ),
            None,
            ProcessedLink(
                source_absolute_href="https://example.com.au/reports/file2.csv",
                source_upload_datetime=datetime(2025, 1, 2, 11, 0, 0),
                target_s3_href="s3://test-bucket/prefix/file2.csv",
                target_s3_bucket="test-bucket",
                target_s3_prefix="prefix",
                target_s3_name="file2.csv",
                target_ingested_datetime=datetime(2025, 1, 2, 11, 5, 0),
            ),
            None,
        ]

        combiner = ConcreteS3ProcessedLinkCombiner()

        result = combiner.combine(
            build_op_context(), processed_links_with_none, mock_schema
        )

        collected = result.collect()
        assert len(collected) == 2
        assert (
            collected["source_absolute_href"][0]
            == "https://example.com.au/reports/file1.csv"
        )
        assert (
            collected["source_absolute_href"][1]
            == "https://example.com.au/reports/file2.csv"
        )

    def test_combine_converts_timezone_to_utc(
        self, mock_schema: Schema, mock_processed_links: list[ProcessedLink | None]
    ) -> None:
        combiner = ConcreteS3ProcessedLinkCombiner()

        result = combiner.combine(build_op_context(), mock_processed_links, mock_schema)

        collected = result.collect()
        assert collected.schema["source_upload_datetime"] == Datetime(time_zone="UTC")
        assert collected.schema["target_ingested_datetime"] == Datetime(time_zone="UTC")

    def test_combine_empty_list(self, mock_schema: Schema) -> None:
        combiner = ConcreteS3ProcessedLinkCombiner()

        empty_list: list[ProcessedLink | None] = []
        result = combiner.combine(build_op_context(), empty_list, mock_schema)

        collected = result.collect()
        assert len(collected) == 0
        assert list(collected.columns) == [
            "source_absolute_href",
            "source_upload_datetime",
            "target_s3_href",
            "target_s3_bucket",
            "target_s3_prefix",
            "target_s3_name",
            "target_ingested_datetime",
        ]

    def test_combine_all_none_values(self, mock_schema: Schema) -> None:
        processed_links_all_none: list[ProcessedLink | None] = [None, None, None]

        combiner = ConcreteS3ProcessedLinkCombiner()

        result = combiner.combine(
            build_op_context(), processed_links_all_none, mock_schema
        )

        collected = result.collect()
        assert len(collected) == 0
