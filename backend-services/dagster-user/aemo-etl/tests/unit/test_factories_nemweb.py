"""Unit tests for all factories/nemweb_public_files/ modules."""

import datetime as dt
from datetime import timezone
from io import BytesIO
from unittest.mock import MagicMock

import bs4
import polars as pl
import pytest
from dagster import Definitions
from dagster_aws.s3 import S3Resource
from pytest_mock import MockerFixture
from types_boto3_s3 import S3Client

from aemo_etl.factories.nemweb_public_files.assets import (
    SURROGATE_KEY_SOURCES,
    nemweb_public_files_asset_factory,
)
from aemo_etl.factories.nemweb_public_files.definitions import (
    nemweb_public_files_definitions_factory,
)
from aemo_etl.factories.nemweb_public_files.models import Link, ProcessedLink
from aemo_etl.factories.nemweb_public_files.ops.dynamic_nemweb_links_fetcher import (
    FilteredDynamicNEMWebLinksFetcher,
    InMemoryCachedLinkFilter,
    build_dynamic_nemweb_links_fetcher_op,
    default_link_filter,
)
from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_fetcher import (
    HTTPNEMWebLinkFetcher,
    build_nemweb_link_fetcher_op,
    default_file_filter,
    default_folder_filter,
    soup_getter,
)
from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_processor import (
    ParquetProcessor,
    S3NemwebLinkProcessor,
    build_nemweb_link_processor_op,
)
from aemo_etl.factories.nemweb_public_files.ops.processed_link_combiner import (
    S3ProcessedLinkCombiner,
    build_process_link_combiner_op,
)

_NOW = dt.datetime(2024, 1, 1, 12, 0, 0, tzinfo=dt.timezone(dt.timedelta(hours=10)))
_UTC_NOW = dt.datetime(2024, 1, 1, 2, 0, 0, tzinfo=timezone.utc)


# ===========================================================================
# models
# ===========================================================================


def test_link_instantiation() -> None:
    link = Link(
        source_absolute_href="https://test.com/file.csv", source_upload_datetime=_NOW
    )
    assert link.source_absolute_href == "https://test.com/file.csv"
    assert link.source_upload_datetime == _NOW


def test_link_no_datetime() -> None:
    link = Link(source_absolute_href="https://test.com/file.csv")
    assert link.source_upload_datetime is None


def test_processed_link_instantiation() -> None:
    pl_link = ProcessedLink(
        source_absolute_href="https://test.com/file.csv",
        source_upload_datetime=_NOW,
        target_s3_href="s3://bucket/file.parquet",
        target_s3_bucket="bucket",
        target_s3_prefix="bronze/vicgas",
        target_s3_name="file.parquet",
        target_ingested_datetime=_UTC_NOW,
    )
    assert pl_link.target_s3_bucket == "bucket"


# ===========================================================================
# nemweb_link_fetcher
# ===========================================================================


def test_default_folder_filter_parent_dir(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    tag = bs4.BeautifulSoup("<a>[To Parent Directory]</a>", "html.parser").find("a")
    assert default_folder_filter(ctx, tag) is False  # type: ignore[arg-type]


def test_default_folder_filter_normal(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    tag = bs4.BeautifulSoup("<a>SOMEFOLDER/</a>", "html.parser").find("a")
    assert default_folder_filter(ctx, tag) is True  # type: ignore[arg-type]


def test_default_file_filter_currentday(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    tag = bs4.BeautifulSoup("<a>CURRENTDAY.ZIP</a>", "html.parser").find("a")
    assert default_file_filter(ctx, tag) is False  # type: ignore[arg-type]


def test_default_file_filter_normal(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    tag = bs4.BeautifulSoup("<a>data.zip</a>", "html.parser").find("a")
    assert default_file_filter(ctx, tag) is True  # type: ignore[arg-type]


def test_soup_getter() -> None:
    soup = soup_getter("<html><body><a>link</a></body></html>")
    assert soup.find("a") is not None


def test_nemweb_link_fetcher_abstract_method_raises() -> None:
    """Abstract fetch body raises NotImplementedError."""
    from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_fetcher import (
        NEMWebLinkFetcher,
    )

    with pytest.raises(NotImplementedError):
        NEMWebLinkFetcher.fetch(None, None, "href")  # type: ignore[arg-type]


def test_build_nemweb_link_fetcher_op_calls_fetcher(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    fetcher = MagicMock(spec=HTTPNEMWebLinkFetcher)
    fetcher.fetch.return_value = []
    op_def = build_nemweb_link_fetcher_op("test", "REPORTS/TEST", fetcher)
    fn = op_def.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = fn(ctx)
    assert result == []
    fetcher.fetch.assert_called_once()


def test_build_nemweb_link_fetcher_op() -> None:
    fetcher = MagicMock(spec=HTTPNEMWebLinkFetcher)
    op_def = build_nemweb_link_fetcher_op("test2", "REPORTS/TEST", fetcher)
    assert op_def is not None


def test_http_nemweb_link_fetcher_fetch(mocker: MockerFixture) -> None:
    """Fetch traverses a folder link then a file link."""
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()

    # HTML for root: one folder + one file
    root_html = (
        "<html><body><a href='/REPORTS/CURRENT/VICGAS/'>VICGAS/</a></body></html>"
    )
    # The previous_element before <a> is stripped of its last token (file size
    # or similar) by the fetcher: join(split()[:-1]). So "PM 1234" → "PM" kept.
    # Format: "%A, %B %d, %Y %I:%M %p"
    sub_html = (
        "<html><body>"
        "Monday, January 01, 2024 12:00 PM 1234"
        '<a href="/REPORTS/CURRENT/VICGAS/data.csv">data.csv</a>'
        "</body></html>"
    )

    call_count = [0]

    def _mock_response(url: str) -> MagicMock:
        resp = MagicMock()
        call_count[0] += 1
        resp.text = root_html if call_count[0] == 1 else sub_html
        return resp

    fetcher = HTTPNEMWebLinkFetcher(request_getter=_mock_response)
    links = fetcher.fetch(ctx, "REPORTS/CURRENT/VICGAS")
    assert len(links) == 1
    assert "data.csv" in links[0].source_absolute_href


def test_http_nemweb_link_fetcher_folder_filter(mocker: MockerFixture) -> None:
    """folder_filter returning False prevents folder traversal."""
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()

    root_html = (
        "<html><body>"
        "<a href='/REPORTS/CURRENT/VICGAS/DUPLICATE/'>DUPLICATE/</a>"
        "</body></html>"
    )

    def _mock_response(url: str) -> MagicMock:
        resp = MagicMock()
        resp.text = root_html
        return resp

    def _reject_all(_ctx: object, tag: bs4.Tag) -> bool:
        return False

    fetcher = HTTPNEMWebLinkFetcher(
        folder_filter=_reject_all,
        request_getter=_mock_response,
    )
    links = fetcher.fetch(ctx, "REPORTS/CURRENT/VICGAS")
    assert links == []


# ===========================================================================
# dynamic_nemweb_links_fetcher
# ===========================================================================


def test_default_link_filter(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    link = Link("https://test.com/file.csv")
    assert default_link_filter(ctx, link) is True


def test_build_dynamic_nemweb_links_fetcher_op_calls_fetcher(
    mocker: MockerFixture,
) -> None:
    ctx = mocker.MagicMock()
    fetcher = MagicMock(spec=FilteredDynamicNEMWebLinksFetcher)
    fetcher.fetch.return_value = []
    op_def = build_dynamic_nemweb_links_fetcher_op("test", "REPORTS/TEST", fetcher)
    fn = op_def.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = fn(ctx, links=[])
    assert result == []
    fetcher.fetch.assert_called_once()


def test_build_dynamic_nemweb_links_fetcher_op() -> None:
    fetcher = MagicMock(spec=FilteredDynamicNEMWebLinksFetcher)
    op_def = build_dynamic_nemweb_links_fetcher_op("test2", "REPORTS/TEST", fetcher)
    assert op_def is not None


def test_filtered_dynamic_fetcher_batch_size(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    links = [Link(f"https://test.com/file{i}.csv", _NOW) for i in range(3)]
    fetcher = FilteredDynamicNEMWebLinksFetcher(batch_size=1)
    outputs = fetcher.fetch(ctx, links)
    # 3 links / batch_size=1 → 3 batches
    assert len(outputs) == 3


def test_filtered_dynamic_fetcher_n_executors(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    links = [Link(f"https://test.com/file{i}.csv", _NOW) for i in range(4)]
    fetcher = FilteredDynamicNEMWebLinksFetcher(n_executors=2)
    outputs = fetcher.fetch(ctx, links)
    # batch_size = 4//2 = 2 → 2 batches
    assert len(outputs) == 2


def test_filtered_dynamic_fetcher_link_filter(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    links = [Link(f"https://test.com/file{i}.csv", _NOW) for i in range(3)]

    def _reject_even(_ctx: object, link: Link) -> bool:
        # reject file0 and file2
        return "1" in link.source_absolute_href

    fetcher = FilteredDynamicNEMWebLinksFetcher(batch_size=10, link_filter=_reject_even)
    outputs = fetcher.fetch(ctx, links)
    assert len(outputs) == 1  # only file1 passes


def test_filtered_dynamic_fetcher_empty_links(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    fetcher = FilteredDynamicNEMWebLinksFetcher()
    outputs = fetcher.fetch(ctx, [])
    assert outputs == []


def test_in_memory_cached_link_filter_table_not_found(mocker: MockerFixture) -> None:
    from deltalake.exceptions import TableNotFoundError

    mocker.patch(
        "aemo_etl.factories.nemweb_public_files.ops.dynamic_nemweb_links_fetcher.scan_delta",
        side_effect=TableNotFoundError("no table"),
    )
    ctx = mocker.MagicMock()
    link = Link("https://test.com/file.csv", _NOW)
    f = InMemoryCachedLinkFilter("s3://bucket/table", ttl_seconds=60)
    assert f(ctx, link) is True


def test_in_memory_cached_link_filter_link_found(mocker: MockerFixture) -> None:
    df = pl.LazyFrame(
        {
            "source_absolute_href": ["https://test.com/existing.csv"],
            "source_upload_datetime": [_UTC_NOW],
        },
        schema={
            "source_absolute_href": pl.String,
            "source_upload_datetime": pl.Datetime("ms", time_zone="UTC"),
        },
    )
    mocker.patch(
        "aemo_etl.factories.nemweb_public_files.ops.dynamic_nemweb_links_fetcher.scan_delta",
        return_value=df,
    )
    ctx = mocker.MagicMock()
    link = Link("https://test.com/existing.csv", _UTC_NOW)
    f = InMemoryCachedLinkFilter("s3://bucket/table", ttl_seconds=60)
    assert f(ctx, link) is False


def test_in_memory_cached_link_filter_link_not_found(mocker: MockerFixture) -> None:
    df = pl.LazyFrame(
        {
            "source_absolute_href": ["https://test.com/other.csv"],
            "source_upload_datetime": [_UTC_NOW],
        },
        schema={
            "source_absolute_href": pl.String,
            "source_upload_datetime": pl.Datetime("ms", time_zone="UTC"),
        },
    )
    mocker.patch(
        "aemo_etl.factories.nemweb_public_files.ops.dynamic_nemweb_links_fetcher.scan_delta",
        return_value=df,
    )
    ctx = mocker.MagicMock()
    link = Link("https://test.com/not_found.csv", _UTC_NOW)
    f = InMemoryCachedLinkFilter("s3://bucket/table", ttl_seconds=60)
    assert f(ctx, link) is True


def test_in_memory_cached_link_filter_ttl_expiry(mocker: MockerFixture) -> None:
    """After TTL the cache is refreshed via set()."""
    df = pl.LazyFrame(
        {
            "source_absolute_href": ["https://test.com/file.csv"],
            "source_upload_datetime": [_UTC_NOW],
        },
        schema={
            "source_absolute_href": pl.String,
            "source_upload_datetime": pl.Datetime("ms", time_zone="UTC"),
        },
    )
    mock_scan = mocker.patch(
        "aemo_etl.factories.nemweb_public_files.ops.dynamic_nemweb_links_fetcher.scan_delta",
        return_value=df,
    )
    f = InMemoryCachedLinkFilter("s3://bucket/table", ttl_seconds=0.0)
    f.set()  # populate cache
    # Patch time so TTL is expired immediately
    mocker.patch(
        "aemo_etl.factories.nemweb_public_files.ops.dynamic_nemweb_links_fetcher.time",
        return_value=f.cache_time + 1.0,
    )
    f.get()  # should call set() again because TTL expired
    assert mock_scan.call_count >= 2


# ===========================================================================
# nemweb_link_processor
# ===========================================================================


def test_build_nemweb_link_processor_op_calls_processor(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    processor = MagicMock(spec=S3NemwebLinkProcessor)
    processor.process.return_value = []
    op_def = build_nemweb_link_processor_op("test", "bucket", "prefix", processor)
    fn = op_def.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = fn(ctx, s3=mock_s3, links=[])
    assert result == []
    processor.process.assert_called_once()


def test_build_nemweb_link_processor_op() -> None:
    processor = MagicMock(spec=S3NemwebLinkProcessor)
    op_def = build_nemweb_link_processor_op("test2", "bucket", "prefix", processor)
    assert op_def is not None


def test_parquet_processor_csv_success(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    csv_content = b"col1,col2\nval1,val2\n"
    mock_response = mocker.MagicMock()
    mock_response.content = csv_content
    getter = mocker.MagicMock(return_value=mock_response)
    link = Link("https://test.com/data.csv", _NOW)
    processor = ParquetProcessor(request_getter=getter)
    buf, filename = processor.process(ctx, link)
    assert filename.endswith(".parquet")
    buf.seek(0)
    assert buf.read(4) == b"PAR1"  # Parquet magic bytes


def test_parquet_processor_csv_fallback(mocker: MockerFixture) -> None:
    """If CSV→Parquet conversion fails, falls back to raw CSV."""
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    csv_content = b"col1,col2\nval1,val2\n"
    mock_response = mocker.MagicMock()
    mock_response.content = csv_content
    getter = mocker.MagicMock(return_value=mock_response)

    mocker.patch(
        "aemo_etl.factories.nemweb_public_files.ops.nemweb_link_processor.read_csv",
        side_effect=RuntimeError("parse error"),
    )
    link = Link("https://test.com/data.csv", _NOW)
    processor = ParquetProcessor(request_getter=getter)
    buf, filename = processor.process(ctx, link)
    # Fallback: original CSV buffer and CSV filename
    assert filename.endswith(".csv")


def test_parquet_processor_non_csv(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    zip_content = b"PK\x03\x04fake_zip"
    mock_response = mocker.MagicMock()
    mock_response.content = zip_content
    getter = mocker.MagicMock(return_value=mock_response)
    link = Link("https://test.com/data.zip", _NOW)
    processor = ParquetProcessor(request_getter=getter)
    buf, filename = processor.process(ctx, link)
    assert filename.endswith(".zip")


def test_s3_nemweb_link_processor_process(mocker: MockerFixture) -> None:
    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()

    mock_buf = BytesIO(b"data")
    mock_buffer_processor = MagicMock()
    mock_buffer_processor.process.return_value = (mock_buf, "file.parquet")

    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3_client = mocker.MagicMock(spec=S3Client)
    mock_s3.get_client.return_value = mock_s3_client

    links = [Link("https://test.com/data.csv", _NOW)]
    processor = S3NemwebLinkProcessor(buffer_processor=mock_buffer_processor)
    result = processor.process(ctx, mock_s3, links, "bucket", "bronze/vicgas")
    assert len(result) == 1
    assert result[0].target_s3_bucket == "bucket"
    mock_s3_client.upload_fileobj.assert_called_once()


# ===========================================================================
# processed_link_combiner
# ===========================================================================


def test_build_process_link_combiner_op_calls_combiner(mocker: MockerFixture) -> None:
    from polars import Schema, String

    ctx = mocker.MagicMock()
    combiner = MagicMock(spec=S3ProcessedLinkCombiner)
    combiner.combine.return_value = pl.LazyFrame({"a": [1]})
    schema = Schema({"source_absolute_href": String})
    op_def = build_process_link_combiner_op(
        "test",
        schema,
        ["source_absolute_href"],
        None,
        None,
        combiner,
    )
    fn = op_def.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = fn(ctx, processed_links=[])
    assert isinstance(result, pl.LazyFrame)
    combiner.combine.assert_called_once()


def test_build_process_link_combiner_op() -> None:
    from polars import Schema, String

    combiner = MagicMock(spec=S3ProcessedLinkCombiner)
    schema = Schema({"source_absolute_href": String})
    op_def = build_process_link_combiner_op(
        "test2",
        schema,
        ["source_absolute_href"],
        None,
        None,
        combiner,
    )
    assert op_def is not None


def test_s3_processed_link_combiner_combine(mocker: MockerFixture) -> None:
    from aemo_etl.factories.nemweb_public_files.assets import SCHEMA

    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    link = ProcessedLink(
        source_absolute_href="https://test.com/file.csv",
        source_upload_datetime=_UTC_NOW,
        target_s3_href="s3://bucket/file.parquet",
        target_s3_bucket="bucket",
        target_s3_prefix="bronze/vicgas",
        target_s3_name="file.parquet",
        target_ingested_datetime=_UTC_NOW,
    )
    # Include None to cover the filtering branch
    processed_links: list[list[ProcessedLink] | None] = [[link], None, [link]]
    combiner = S3ProcessedLinkCombiner()
    result = combiner.combine(ctx, processed_links, SCHEMA, SURROGATE_KEY_SOURCES)
    assert isinstance(result, pl.LazyFrame)
    schema_names = result.collect_schema().names()
    assert "source_absolute_href" in schema_names
    assert "surrogate_key" in schema_names


def test_s3_processed_link_combiner_empty(mocker: MockerFixture) -> None:
    from aemo_etl.factories.nemweb_public_files.assets import SCHEMA

    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    combiner = S3ProcessedLinkCombiner()
    result = combiner.combine(ctx, [None], SCHEMA, SURROGATE_KEY_SOURCES)
    assert isinstance(result, pl.LazyFrame)


# ===========================================================================
# assets factory
# ===========================================================================


def test_nemweb_public_files_asset_factory_creates_asset(mocker: MockerFixture) -> None:
    asset_def = nemweb_public_files_asset_factory(
        name="test_nemweb_asset",
        nemweb_relative_href="REPORTS/CURRENT/TEST",
        s3_landing_prefix="bronze/test",
        nemweb_link_fetcher=MagicMock(spec=HTTPNEMWebLinkFetcher),
        dynamic_nemweb_links_fetcher=MagicMock(spec=FilteredDynamicNEMWebLinksFetcher),
        nemweb_link_processor=MagicMock(spec=S3NemwebLinkProcessor),
        processed_link_combiner=MagicMock(spec=S3ProcessedLinkCombiner),
    )
    assert asset_def is not None


# ===========================================================================
# definitions factory
# ===========================================================================


def test_nemweb_public_files_definitions_factory_returns_definitions() -> None:
    defs = nemweb_public_files_definitions_factory(
        domain="vicgas",
        table_name="bronze_nemweb_public_files_vicgas_test",
        nemweb_relative_href="REPORTS/CURRENT/VicGas",
        cron_schedule="*/15 * * * *",
        n_executors=1,
    )
    assert isinstance(defs, Definitions)


def test_nemweb_definitions_request_getter_retries(mocker: MockerFixture) -> None:
    """Cover the inner request_getter_with_retries closure body."""
    mock_response = mocker.MagicMock()
    mock_response.raise_for_status.return_value = None
    mocker.patch(
        "aemo_etl.factories.nemweb_public_files.definitions.request_get",
        return_value=mock_response,
    )

    defs = nemweb_public_files_definitions_factory(
        domain="vicgas",
        table_name="bronze_nemweb_test2",
        nemweb_relative_href="REPORTS/CURRENT/VicGas",
        cron_schedule="*/15 * * * *",
    )

    # Navigate to the request_getter_with_retries closure via the processor op.
    asset = list(defs.assets)[0]  # type: ignore[call-overload]
    processor_node = next(n for n in asset.node_def.nodes if "processor" in n.name)
    op_fn = processor_node.definition._compute_fn.decorated_fn  # type: ignore[union-attr]
    idx = op_fn.__code__.co_freevars.index("nemweb_link_processor")
    nemweb_processor = op_fn.__closure__[idx].cell_contents
    request_getter = nemweb_processor.buffer_processor.request_getter

    # Call the closure body – this covers the `return request_get(path)` line.
    result = request_getter("https://test.com/file.csv")
    assert result is mock_response
