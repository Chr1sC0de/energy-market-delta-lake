from datetime import datetime
from typing import Callable
from unittest.mock import Mock

import bs4
import pytest
from dagster import OpExecutionContext, build_op_context
from requests.models import Response

from aemo_etl.factories.nemweb_public_files.data_models import Link
from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_fetcher import (
    HTTPNEMWebLinkFetcher,
    NEMWebLinkFetcher,
    build_nemweb_link_fetcher_op,
    default_file_filter,
    default_folder_filter,
    soup_getter,
)


@pytest.fixture
def mock_html_with_folders_and_files() -> str:
    return """
    <html>
        <body>
            Monday, January 06, 2025  6:05 AM Dispatch_SCADA/
                <a href="/Reports/Current/Dispatch_SCADA/">Dispatch_SCADA/</a>
            Tuesday, January 07, 2025  7:30 PM [To Parent Directory]
                <a href="/Reports/Archive/">[To Parent Directory]</a>
            Wednesday, January 01, 2025  11:59 PM PUBLIC_PRICES_20250101.CSV
                <a href="/Reports/Current/PUBLIC_PRICES_20250101.CSV">PUBLIC_PRICES_20250101.CSV</a>
            Thursday, January 02, 2025  12:00 AM CURRENTDAY.ZIP
                <a href="/Reports/Current/CURRENTDAY.ZIP">CURRENTDAY.ZIP</a>
            Friday, January 03, 2025  9:15 AM DATA_20250102.CSV
                <a href="/Reports/Current/DATA_20250102.CSV">DATA_20250102.CSV</a>
        </body>
    </html>
    """


@pytest.fixture
def mock_html_files_only() -> str:
    return """
    <html>
        <body>
            Monday, January 06, 2025  6:05 AM FILE1.CSV<a href="/Reports/Current/FILE1.CSV">FILE1.CSV</a>
            Tuesday, January 07, 2025  7:30 PM FILE2.CSV<a href="/Reports/Current/FILE2.CSV">FILE2.CSV</a>
        </body>
    </html>
    """


MockResponseFactory = Callable[[str], Response]


@pytest.fixture
def mock_response_factory() -> MockResponseFactory:
    def _factory(html: str) -> Response:
        response = Mock(spec=Response)
        response.text = html
        response.status_code = 200
        return response

    return _factory


def test_nemweb_link_fetcher_abstract_method_raises() -> None:
    class TestFetcher(NEMWebLinkFetcher):
        def fetch(
            self, context: OpExecutionContext, relative_root_href: str
        ) -> list[Link]:
            return super().fetch(context, relative_root_href)  # type: ignore[safe-super]

    fetcher = TestFetcher()
    with pytest.raises(NotImplementedError):
        fetcher.fetch(build_op_context(), "test")


def test_build_nemweb_link_fetcher_op() -> None:
    class MockNEMWebLinkFetcher(NEMWebLinkFetcher):
        def fetch(
            self, context: OpExecutionContext, relative_root_href: str
        ) -> list[Link]:
            return [
                Link(
                    source_absolute_href="https://example.com.au/mock.csv",
                    source_upload_datetime=datetime(year=2025, month=1, day=1),
                )
            ]

    nemweb_link_fetcher_op = build_nemweb_link_fetcher_op(
        "mock", "Reports/Current", MockNEMWebLinkFetcher()
    )

    results = nemweb_link_fetcher_op(build_op_context())

    assert len(results) == 1
    assert results[0].source_absolute_href == "https://example.com.au/mock.csv"
    assert results[0].source_upload_datetime == datetime(year=2025, month=1, day=1)


def test_default_folder_filter() -> None:
    context = build_op_context()

    tag_parent = bs4.BeautifulSoup(
        '<a href="/parent/">[To Parent Directory]</a>', features="html.parser"
    ).find("a")
    tag_folder = bs4.BeautifulSoup(
        '<a href="/folder/">Folder/</a>', features="html.parser"
    ).find("a")

    assert tag_parent is not None
    assert tag_folder is not None

    assert default_folder_filter(context, tag_parent) is False
    assert default_folder_filter(context, tag_folder) is True


def test_default_file_filter() -> None:
    context = build_op_context()

    tag_currentday = bs4.BeautifulSoup(
        '<a href="/CURRENTDAY.ZIP">CURRENTDAY.ZIP</a>', features="html.parser"
    ).find("a")
    tag_regular = bs4.BeautifulSoup(
        '<a href="/data.csv">data.csv</a>', features="html.parser"
    ).find("a")

    assert tag_currentday is not None
    assert tag_regular is not None

    assert default_file_filter(context, tag_currentday) is False
    assert default_file_filter(context, tag_regular) is True


def test_soup_getter() -> None:
    html = "<html><body><a href='/test'>Test</a></body></html>"
    soup = soup_getter(html)

    assert isinstance(soup, bs4.BeautifulSoup)
    assert soup.find("a") is not None


class TestHTTPNEMWebLinkFetcher:
    def test_fetch_with_files_only(
        self, mock_html_files_only: str, mock_response_factory: MockResponseFactory
    ) -> None:
        mock_request_getter = Mock(
            return_value=mock_response_factory(mock_html_files_only)
        )

        fetcher = HTTPNEMWebLinkFetcher(request_getter=mock_request_getter)

        results = fetcher.fetch(build_op_context(), "Reports/Current")

        assert len(results) == 2
        assert (
            results[0].source_absolute_href
            == "https://www.nemweb.com.au/Reports/Current/FILE1.CSV"
        )
        assert results[0].source_upload_datetime == datetime(2025, 1, 6, 6, 5)
        assert (
            results[1].source_absolute_href
            == "https://www.nemweb.com.au/Reports/Current/FILE2.CSV"
        )
        assert results[1].source_upload_datetime == datetime(2025, 1, 7, 19, 30)

    def test_fetch_with_folders_and_files(
        self,
        mock_html_with_folders_and_files: str,
        mock_html_files_only: str,
        mock_response_factory: MockResponseFactory,
    ) -> None:
        call_count = 0

        def mock_request_getter(path: str) -> Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_response_factory(mock_html_with_folders_and_files)
            else:
                return mock_response_factory(mock_html_files_only)

        fetcher = HTTPNEMWebLinkFetcher(request_getter=mock_request_getter)

        results = fetcher.fetch(build_op_context(), "Reports/Current")

        assert len(results) == 4
        assert (
            results[0].source_absolute_href
            == "https://www.nemweb.com.au/Reports/Current/PUBLIC_PRICES_20250101.CSV"
        )
        assert results[0].source_upload_datetime == datetime(2025, 1, 1, 23, 59)
        assert (
            results[1].source_absolute_href
            == "https://www.nemweb.com.au/Reports/Current/DATA_20250102.CSV"
        )
        assert results[1].source_upload_datetime == datetime(2025, 1, 3, 9, 15)

    def test_fetch_filters_parent_directory(
        self,
        mock_html_with_folders_and_files: str,
        mock_html_files_only: str,
        mock_response_factory: MockResponseFactory,
    ) -> None:
        call_count = 0

        def mock_request_getter(path: str) -> Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_response_factory(mock_html_with_folders_and_files)
            else:
                return mock_response_factory(mock_html_files_only)

        fetcher = HTTPNEMWebLinkFetcher(request_getter=mock_request_getter)

        results = fetcher.fetch(build_op_context(), "Reports/Current")

        parent_directory_links = [
            link
            for link in results
            if "[To Parent Directory]" in link.source_absolute_href
        ]
        assert len(parent_directory_links) == 0

    def test_fetch_filters_currentday_zip(
        self,
        mock_html_with_folders_and_files: str,
        mock_html_files_only: str,
        mock_response_factory: MockResponseFactory,
    ) -> None:
        call_count = 0

        def mock_request_getter(path: str) -> Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return mock_response_factory(mock_html_with_folders_and_files)
            else:
                return mock_response_factory(mock_html_files_only)

        fetcher = HTTPNEMWebLinkFetcher(request_getter=mock_request_getter)

        results = fetcher.fetch(build_op_context(), "Reports/Current")

        currentday_links = [
            link for link in results if "CURRENTDAY.ZIP" in link.source_absolute_href
        ]
        assert len(currentday_links) == 0

    def test_fetch_with_custom_filters(
        self, mock_html_files_only: str, mock_response_factory: MockResponseFactory
    ) -> None:
        def custom_file_filter(context: OpExecutionContext, tag: bs4.Tag) -> bool:
            return "FILE1" in tag.text

        mock_request_getter = Mock(
            return_value=mock_response_factory(mock_html_files_only)
        )

        fetcher = HTTPNEMWebLinkFetcher(
            file_filter=custom_file_filter, request_getter=mock_request_getter
        )

        results = fetcher.fetch(build_op_context(), "Reports/Current")

        assert len(results) == 1
        assert (
            results[0].source_absolute_href
            == "https://www.nemweb.com.au/Reports/Current/FILE1.CSV"
        )
