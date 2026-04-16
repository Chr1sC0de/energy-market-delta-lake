"""Minimal tests covering all uncovered lines in nemweb_public_files ops."""

from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

import bs4
import polars as pl
import pytest
from dagster import OpExecutionContext, build_op_context
from dagster_aws.s3 import S3Resource
from types_boto3_s3 import S3Client

from aemo_etl.factories.assets.nemweb_public_files.models import Link, ProcessedLink
from tests.utils import MakeBucketProtocol
from aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_nemweb_links_fetcher import (
    FilteredDynamicNEMWebLinksFetcher,
    InMemoryCachedLinkFilter,
    build_dynamic_nemweb_links_fetcher_op,
    default_link_filter,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_zip_links_fetcher import (
    S3DynamicZipLinksFetcher,
    build_dynamic_zip_link_fetcher_op,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.file_unzipper import (
    S3FileUnzipper,
    build_unzip_files_op,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.nemweb_link_fetcher import (
    HTTPNEMWebLinkFetcher,
    NEMWebLinkFetcher,
    build_nemweb_link_fetcher_op,
    default_file_filter,
    default_folder_filter,
    soup_getter,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.nemweb_link_processor import (
    ParquetProcessor,
    S3NemwebLinkProcessor,
    build_nemweb_link_processor_op,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.processed_link_combiner import (
    S3ProcessedLinkCombiner,
    build_process_link_combiner_op,
)


# ─── helpers ──────────────────────────────────────────────────────────────────


def _ctx() -> OpExecutionContext:
    return build_op_context()


def _link(href: str = "https://www.nemweb.com.au/file.zip") -> Link:
    return Link(
        source_absolute_href=href,
        source_upload_datetime=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def _processed_link(href: str = "https://www.nemweb.com.au/file.zip") -> ProcessedLink:
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return ProcessedLink(
        source_absolute_href=href,
        target_s3_href="s3://bucket/prefix/file.parquet",
        target_s3_bucket="bucket",
        target_s3_prefix="prefix",
        target_s3_name="file.parquet",
        target_ingested_datetime=now,
        source_upload_datetime=now,
    )


# ─── dynamic_nemweb_links_fetcher ─────────────────────────────────────────────


def test_default_link_filter() -> None:
    assert default_link_filter(_ctx(), MagicMock()) is True


def test_build_dynamic_nemweb_links_fetcher_op_delegates() -> None:
    mock_fetcher = MagicMock()
    mock_fetcher.fetch.return_value = []
    op_def = build_dynamic_nemweb_links_fetcher_op("x", "/href", mock_fetcher)
    result = op_def.compute_fn.decorated_fn(context=_ctx(), links=[])  # type: ignore[union-attr]
    mock_fetcher.fetch.assert_called_once()
    assert result == []


def test_filtered_dynamic_nemweb_links_fetcher_batching() -> None:
    fetcher = FilteredDynamicNEMWebLinksFetcher(batch_size=2)
    links = [_link(f"https://host/f{i}.zip") for i in range(5)]
    outputs = fetcher.fetch(_ctx(), links)
    assert len(outputs) >= 1
    for out in outputs:
        assert len(out.value) <= 2  # type: ignore[arg-type]


def test_filtered_dynamic_nemweb_links_fetcher_filter() -> None:
    # Only even-indexed links pass the filter
    links = [_link(f"https://host/f{i}.zip") for i in range(4)]
    counter = [0]

    def every_other(_ctx: object, _link: object) -> bool:
        result = counter[0] % 2 == 0
        counter[0] += 1
        return result

    fetcher = FilteredDynamicNEMWebLinksFetcher(link_filter=every_other, batch_size=4)
    outputs = fetcher.fetch(_ctx(), links)
    # 2 of 4 links pass → one batch
    total = sum(len(o.value) for o in outputs)  # type: ignore[arg-type]
    assert total == 2


def test_in_memory_cached_link_filter_table_not_found() -> None:
    from deltalake.exceptions import TableNotFoundError

    filt = InMemoryCachedLinkFilter(table_path="s3://fake/path", ttl_seconds=60)
    with patch(
        "aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_nemweb_links_fetcher.scan_delta",
        side_effect=TableNotFoundError("not found"),
    ):
        result = filt(_ctx(), _link())
    assert result is True


def test_in_memory_cached_link_filter_found_in_table() -> None:
    link = _link()
    mock_df = MagicMock()
    # simulate len > 0: found in table
    mock_df.filter.return_value.select.return_value.collect.return_value.item.return_value = 1
    mock_df.collect_schema.return_value = {
        "source_upload_datetime": pl.Datetime("ms", "UTC")
    }
    filt = InMemoryCachedLinkFilter(table_path="s3://fake/path", ttl_seconds=60)
    filt._cache = mock_df
    filt.cache_time = float("inf")  # never expire
    result = filt(_ctx(), link)
    assert result is False


def test_in_memory_cached_link_filter_not_found_in_table() -> None:
    link = _link()
    mock_df = MagicMock()
    mock_df.filter.return_value.select.return_value.collect.return_value.item.return_value = 0
    mock_df.collect_schema.return_value = {
        "source_upload_datetime": pl.Datetime("ms", "UTC")
    }
    filt = InMemoryCachedLinkFilter(table_path="s3://fake/path", ttl_seconds=60)
    filt._cache = mock_df
    filt.cache_time = float("inf")
    result = filt(_ctx(), link)
    assert result is True


def test_in_memory_cached_link_filter_ttl_refresh() -> None:
    link = _link()
    mock_df = MagicMock()
    mock_df.filter.return_value.select.return_value.collect.return_value.item.return_value = 0
    mock_df.collect_schema.return_value = {
        "source_upload_datetime": pl.Datetime("ms", "UTC")
    }
    filt = InMemoryCachedLinkFilter(table_path="s3://fake/path", ttl_seconds=0)
    # set an expired cache
    filt._cache = mock_df
    filt.cache_time = 0.0  # expired immediately
    with patch(
        "aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_nemweb_links_fetcher.scan_delta",
        return_value=mock_df,
    ):
        result = filt(_ctx(), link)
    assert isinstance(result, bool)


# ─── dynamic_zip_links_fetcher ────────────────────────────────────────────────


def test_build_dynamic_zip_link_fetcher_op_delegates() -> None:
    from dagster import DynamicOutput

    mock_fetcher = MagicMock()
    mock_fetcher.fetch.return_value = iter(
        [DynamicOutput("prefix/a.zip", mapping_key="a_zip")]
    )
    op_def = build_dynamic_zip_link_fetcher_op("x", "bucket", "prefix", mock_fetcher)
    results = list(
        op_def.compute_fn.decorated_fn(context=_ctx(), s3=MagicMock(spec=S3Resource))  # type: ignore[union-attr]
    )
    mock_fetcher.fetch.assert_called_once()
    assert len(results) == 1


def test_s3_dynamic_zip_links_fetcher_no_zip(
    s3: S3Client, make_bucket: MakeBucketProtocol
) -> None:
    bucket = make_bucket("zip-test")
    s3_resource = MagicMock(spec=S3Resource)
    s3_resource.get_client.return_value = s3
    fetcher = S3DynamicZipLinksFetcher()
    results = list(fetcher.fetch(bucket, "prefix", _ctx(), s3_resource))
    assert results == []


def test_s3_dynamic_zip_links_fetcher_with_zip(
    s3: S3Client, make_bucket: MakeBucketProtocol
) -> None:
    bucket = make_bucket("zip-test-2")

    # upload a dummy .zip
    buf = BytesIO()
    with ZipFile(buf, "w") as zf:
        zf.writestr("data.csv", "a,b\n1,2\n")
    buf.seek(0)
    s3.upload_fileobj(buf, bucket, "prefix/archive.zip")

    s3_resource = MagicMock(spec=S3Resource)
    s3_resource.get_client.return_value = s3
    fetcher = S3DynamicZipLinksFetcher()
    results = list(fetcher.fetch(bucket, "prefix", _ctx(), s3_resource))
    assert len(results) == 1
    assert results[0].value == "prefix/archive.zip"  # type: ignore[union-attr]


# ─── file_unzipper ────────────────────────────────────────────────────────────


def test_build_unzip_files_op_delegates() -> None:
    mock_unzipper = MagicMock()
    mock_unzipper.unzip.return_value = []
    op_def = build_unzip_files_op("x", "bucket", "prefix", mock_unzipper)
    result = op_def.compute_fn.decorated_fn(  # type: ignore[union-attr]
        context=_ctx(), s3=MagicMock(spec=S3Resource), s3_source_key="k"
    )
    mock_unzipper.unzip.assert_called_once()
    assert result == []


def test_s3_file_unzipper_no_such_key(
    s3: S3Client, make_bucket: MakeBucketProtocol
) -> None:
    bucket = make_bucket("unzip-test")
    s3_resource = MagicMock(spec=S3Resource)
    s3_resource.get_client.return_value = s3
    unzipper = S3FileUnzipper()
    result = unzipper.unzip(_ctx(), s3_resource, "nonexistent.zip", bucket, "prefix")
    assert result == []


def test_s3_file_unzipper_csv_to_parquet(
    s3: S3Client, make_bucket: MakeBucketProtocol
) -> None:
    bucket = make_bucket("unzip-csv")

    buf = BytesIO()
    with ZipFile(buf, "w") as zf:
        zf.writestr("data.csv", "a,b\n1,2\n3,4\n")
    buf.seek(0)
    s3.upload_fileobj(buf, bucket, "prefix/data.zip")

    s3_resource = MagicMock(spec=S3Resource)
    s3_resource.get_client.return_value = s3
    unzipper = S3FileUnzipper()
    result = unzipper.unzip(_ctx(), s3_resource, "prefix/data.zip", bucket, "prefix")
    assert len(result) == 1
    assert result[0]["Key"].endswith(".parquet")


def test_s3_file_unzipper_non_csv(
    s3: S3Client, make_bucket: MakeBucketProtocol
) -> None:
    bucket = make_bucket("unzip-non-csv")

    buf = BytesIO()
    with ZipFile(buf, "w") as zf:
        zf.writestr("data.parquet", b"PAR1" + b"\x00" * 10)
    buf.seek(0)
    s3.upload_fileobj(buf, bucket, "prefix/data.zip")

    s3_resource = MagicMock(spec=S3Resource)
    s3_resource.get_client.return_value = s3
    unzipper = S3FileUnzipper()
    result = unzipper.unzip(_ctx(), s3_resource, "prefix/data.zip", bucket, "prefix")
    assert len(result) == 1
    assert result[0]["Key"].endswith(".parquet")


def test_s3_file_unzipper_csv_conversion_failure(
    s3: S3Client, make_bucket: MakeBucketProtocol
) -> None:
    bucket = make_bucket("unzip-fail")

    buf = BytesIO()
    with ZipFile(buf, "w") as zf:
        zf.writestr("bad.csv", "a,b\n1,2\n")
    buf.seek(0)
    s3.upload_fileobj(buf, bucket, "prefix/bad.zip")

    s3_resource = MagicMock(spec=S3Resource)
    s3_resource.get_client.return_value = s3
    unzipper = S3FileUnzipper()
    with patch(
        "aemo_etl.factories.assets.nemweb_public_files.ops.file_unzipper.read_csv",
        side_effect=Exception("parse error"),
    ):
        result = unzipper.unzip(_ctx(), s3_resource, "prefix/bad.zip", bucket, "prefix")
    assert len(result) == 1
    assert result[0]["Key"].endswith(".csv")


# ─── nemweb_link_fetcher ──────────────────────────────────────────────────────


def test_default_folder_filter_keeps_non_parent() -> None:
    tag = MagicMock(spec=bs4.Tag)
    tag.text = "SomeFolder/"
    assert default_folder_filter(_ctx(), tag) is True


def test_default_folder_filter_drops_parent() -> None:
    tag = MagicMock(spec=bs4.Tag)
    tag.text = "[To Parent Directory]"
    assert default_folder_filter(_ctx(), tag) is False


def test_default_file_filter_keeps_normal() -> None:
    tag = MagicMock(spec=bs4.Tag)
    tag.text = "DATA_20240101.ZIP"
    assert default_file_filter(_ctx(), tag) is True


def test_default_file_filter_drops_currentday() -> None:
    tag = MagicMock(spec=bs4.Tag)
    tag.text = "CURRENTDAY.ZIP"
    assert default_file_filter(_ctx(), tag) is False


def test_soup_getter() -> None:
    result = soup_getter("<html><a href='/x'>link</a></html>")
    assert isinstance(result, bs4.BeautifulSoup)


def test_nemweb_link_fetcher_abstract_raises() -> None:
    with pytest.raises(NotImplementedError):
        NEMWebLinkFetcher.fetch(None, _ctx(), "/href")  # type: ignore[arg-type]


def test_build_nemweb_link_fetcher_op_delegates() -> None:
    mock_fetcher = MagicMock()
    mock_fetcher.fetch.return_value = []
    op_def = build_nemweb_link_fetcher_op("x", "/href", mock_fetcher)
    result = op_def.compute_fn.decorated_fn(context=_ctx())  # type: ignore[union-attr]
    mock_fetcher.fetch.assert_called_once()
    assert result == []


def test_http_nemweb_link_fetcher_single_page() -> None:
    # NemWeb format: "Day, Month DD, YYYY HH:MM AM/PM SIZE <a>..."
    # The parser drops the last whitespace-separated token (size) before the link.
    html = (
        "<html><body>"
        "Thursday, January 01, 2024 12:00 AM 1024 "
        '<a href="/Reports/file.zip">file.zip</a>'
        "</body></html>"
    )
    mock_response = MagicMock()
    mock_response.text = html

    fetcher = HTTPNEMWebLinkFetcher(
        request_getter=lambda _: mock_response,
    )
    links = fetcher.fetch(_ctx(), "Reports/")
    assert len(links) == 1
    assert links[0].source_absolute_href == "https://www.nemweb.com.au/Reports/file.zip"


def test_http_nemweb_link_fetcher_follows_folder() -> None:
    folder_html = '<html><body><a href="/Reports/sub/">sub/</a></body></html>'
    file_html = (
        "<html><body>"
        "Thursday, January 01, 2024 12:00 AM 1024 "
        '<a href="/Reports/sub/data.zip">data.zip</a>'
        "</body></html>"
    )
    calls = [0]

    def getter(url: str) -> MagicMock:
        r = MagicMock()
        r.text = folder_html if calls[0] == 0 else file_html
        calls[0] += 1
        return r

    fetcher = HTTPNEMWebLinkFetcher(request_getter=getter)
    links = fetcher.fetch(_ctx(), "Reports/")
    assert any("data.zip" in lnk.source_absolute_href for lnk in links)


# ─── nemweb_link_processor ────────────────────────────────────────────────────


def test_build_nemweb_link_processor_op_delegates() -> None:
    mock_processor = MagicMock()
    mock_processor.process.return_value = []
    op_def = build_nemweb_link_processor_op("x", "bucket", "prefix", mock_processor)
    result = op_def.compute_fn.decorated_fn(  # type: ignore[union-attr]
        context=_ctx(), s3=MagicMock(spec=S3Resource), links=[]
    )
    mock_processor.process.assert_called_once()
    assert result == []


def test_parquet_processor_csv() -> None:
    csv_content = b"a,b\n1,2\n3,4\n"
    mock_response = MagicMock()
    mock_response.content = csv_content

    processor = ParquetProcessor(request_getter=lambda _: mock_response)
    link = _link("https://host/data.csv")
    buf, fname = processor.process(_ctx(), link)
    assert fname.endswith(".parquet")
    buf.seek(0)
    assert buf.read(4) == b"PAR1"


def test_parquet_processor_csv_failure_fallback() -> None:
    mock_response = MagicMock()
    mock_response.content = b"a,b\n1,2\n"

    processor = ParquetProcessor(request_getter=lambda _: mock_response)
    link = _link("https://host/bad.csv")
    with patch(
        "aemo_etl.factories.assets.nemweb_public_files.ops.nemweb_link_processor.read_csv",
        side_effect=Exception("parse error"),
    ):
        buf, fname = processor.process(_ctx(), link)
    assert fname.endswith(".csv")


def test_parquet_processor_non_csv() -> None:
    mock_response = MagicMock()
    mock_response.content = b"PAR1" + b"\x00" * 50

    processor = ParquetProcessor(request_getter=lambda _: mock_response)
    link = _link("https://host/data.zip")
    buf, fname = processor.process(_ctx(), link)
    assert fname.endswith(".zip")


def test_s3_nemweb_link_processor_process() -> None:
    mock_s3_client = MagicMock()
    mock_s3_resource = MagicMock(spec=S3Resource)
    mock_s3_resource.get_client.return_value = mock_s3_client

    mock_buffer_processor = MagicMock()
    buf = BytesIO(b"data")
    mock_buffer_processor.process.return_value = (buf, "file.parquet")

    processor = S3NemwebLinkProcessor(buffer_processor=mock_buffer_processor)
    links = [_link()]
    result = processor.process(_ctx(), mock_s3_resource, links, "bucket", "prefix")

    assert len(result) == 1
    assert result[0].target_s3_name == "file.parquet"


# ─── processed_link_combiner ──────────────────────────────────────────────────


def test_build_process_link_combiner_op_delegates() -> None:
    from polars import Schema, String

    mock_combiner = MagicMock()
    mock_combiner.combine.return_value = pl.LazyFrame()
    schema = Schema({"surrogate_key": String})
    op_def = build_process_link_combiner_op(
        "x", schema, ["surrogate_key"], None, {}, mock_combiner
    )
    result = op_def.compute_fn.decorated_fn(context=_ctx(), processed_links=[[]])  # type: ignore[union-attr]
    mock_combiner.combine.assert_called_once()
    assert isinstance(result, pl.LazyFrame)


def test_s3_processed_link_combiner_combine() -> None:
    from aemo_etl.factories.assets.nemweb_public_files.factory import (
        SCHEMA,
        SURROGATE_KEY_SOURCES,
    )

    combiner = S3ProcessedLinkCombiner()
    links: list[list[ProcessedLink] | None] = [[_processed_link()], None]
    result = combiner.combine(_ctx(), links, SCHEMA, SURROGATE_KEY_SOURCES)
    assert isinstance(result, pl.LazyFrame)
    rows = result.collect()
    assert len(rows) == 1
    assert rows["target_s3_name"][0] == "file.parquet"
