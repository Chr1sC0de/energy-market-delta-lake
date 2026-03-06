from datetime import datetime
from time import sleep
from typing import TypedDict

import pytest
from dagster import DynamicOutput, OpExecutionContext, build_op_context
from polars import LazyFrame

from aemo_etl.configs import LANDING_BUCKET
from aemo_etl.factories.download_nemweb_public_files_to_s3.data_models import Link
from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.dynamic_nemweb_links_fetcher import (
    DynamicNEMWebLinksFetcher,
    FilteredDynamicNEMWebLinksFetcher,
    InMemoryCachedLinkFilter,
    build_dynamic_nemweb_links_fetcher_op,
)
from tests.utils import MakeBucketProtocol


@pytest.fixture
def mock_links() -> list[Link]:
    return [
        Link(
            source_absolute_href="https://example.com.au/mock_0.zip",
            source_upload_datetime=datetime(year=2025, month=1, day=1),
        ),
        Link(
            source_absolute_href="https://example.com.au/mock_1.csv",
            source_upload_datetime=datetime(year=2025, month=1, day=1),
        ),
        Link(
            source_absolute_href="https://example.com.au/mock_2.csv",
            source_upload_datetime=datetime(year=2025, month=1, day=1),
        ),
        Link(
            source_absolute_href="https://example.com.au/mock_3.csv",
            source_upload_datetime=datetime(year=2025, month=1, day=1),
        ),
    ]


@pytest.fixture
def mock_dynamic_links(mock_links: list[Link]) -> list[DynamicOutput[Link]]:
    return [DynamicOutput(link, f"key_{i}") for i, link in enumerate(mock_links)]


def test_build_dynamic_nemweb_links_fetcher_op(
    mock_links: list[Link], mock_dynamic_links: list[DynamicOutput[Link]]
) -> None:

    class MockDynamicNEMWebLinksFetcher(DynamicNEMWebLinksFetcher):
        def fetch(
            self, context: OpExecutionContext, links: list[Link]
        ) -> list[DynamicOutput[Link]]:
            return mock_dynamic_links

    dynamic_nemweb_links_fetcher_op = build_dynamic_nemweb_links_fetcher_op(
        "mock", "mock_href", MockDynamicNEMWebLinksFetcher()
    )

    results = dynamic_nemweb_links_fetcher_op(build_op_context(), mock_links)

    assert results == mock_dynamic_links


def test_filtered_dynamic_nemweb_link_fetcher(
    mock_links: list[Link], mock_dynamic_links: list[DynamicOutput[Link]]
) -> None:
    filtered_dynamic_nemweb_link_fetcher = FilteredDynamicNEMWebLinksFetcher()

    results = filtered_dynamic_nemweb_link_fetcher.fetch(build_op_context(), mock_links)
    assert len(results) == 4


class TestInMemoryCachedLinkFilter:
    def test_table_missing_error(
        self,
        mock_links: list[Link],
        make_bucket: MakeBucketProtocol,
        create_delta_log: None,
    ) -> None:
        bucket_name = make_bucket(LANDING_BUCKET)
        table_path = f"s3://{bucket_name}/test"
        in_memory_cache_filter = InMemoryCachedLinkFilter(table_path, 1)
        assert in_memory_cache_filter(build_op_context(), mock_links[0])

    def test_filter_works(
        self,
        mock_links: list[Link],
        make_bucket: MakeBucketProtocol,
        create_delta_log: None,
    ) -> None:

        bucket_name = make_bucket(LANDING_BUCKET)
        table_path = f"s3://{bucket_name}"
        in_memory_cache_filter = InMemoryCachedLinkFilter(table_path, 1)

        class DataDict(TypedDict):
            source_absolute_href: list[str]
            source_upload_datetime: list[datetime | None]

        data_dict: DataDict = {"source_absolute_href": [], "source_upload_datetime": []}

        for link in mock_links[:-2]:
            data_dict["source_absolute_href"].append(link.source_absolute_href)
            data_dict["source_upload_datetime"].append(link.source_upload_datetime)

        LazyFrame(data_dict).sink_delta(table_path)

        for link in mock_links:
            in_memory_cache_filter(build_op_context(), link)

    def test_reset(
        self,
        mock_links: list[Link],
        make_bucket: MakeBucketProtocol,
        create_delta_log: None,
    ) -> None:
        bucket_name = make_bucket(LANDING_BUCKET)
        table_path = f"s3://{bucket_name}"
        in_memory_cache_filter = InMemoryCachedLinkFilter(table_path, 0.01)

        class DataDict(TypedDict):
            source_absolute_href: list[str]
            source_upload_datetime: list[datetime | None]

        data_dict: DataDict = {"source_absolute_href": [], "source_upload_datetime": []}

        for link in mock_links[:-2]:
            data_dict["source_absolute_href"].append(link.source_absolute_href)
            data_dict["source_upload_datetime"].append(link.source_upload_datetime)

        in_memory_cache_filter.get()

        sleep(0.2)

        in_memory_cache_filter.get()
