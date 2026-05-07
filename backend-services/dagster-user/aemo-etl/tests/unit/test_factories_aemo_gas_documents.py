import datetime as dt
from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

import bs4
import polars as pl
import pytest
from botocore.exceptions import ClientError
from pytest_mock import MockerFixture
from requests import Response

from aemo_etl.factories.aemo_gas_documents.assets import (
    AEMO_GAS_DOCUMENTS_PREFIX,
    DELTA_MERGE_OPTIONS,
    AEMOGasDocumentSourceWriteResult,
    _land_pdf_once,
    _stable_hash,
    records_to_lazyframe,
    scrape_and_land_aemo_gas_document_sources,
    write_aemo_gas_document_sources_batch,
)
from aemo_etl.factories.aemo_gas_documents.models import (
    AEMOGasDocumentSourcePage,
)
from aemo_etl.factories.aemo_gas_documents.scraper import (
    _page_link_observations,
    child_source_pages,
    clean_document_title,
    discover_aemo_gas_document_observations,
    document_family_id,
    extract_page_title,
    infer_document_kind,
    is_aemo_public_url,
    link_observation,
    normalize_source_url,
    soup_getter,
)

_OBSERVED_AT = dt.datetime(2026, 5, 7, 1, 2, 3, tzinfo=dt.UTC)
_PDF_BYTES = b"%PDF-1.7\nexample\n%%EOF\n"
_PAGE_URL = "https://www.aemo.com.au/energy-systems/gas/example"
_PDF_URL = (
    "https://www.aemo.com.au/-/media/files/gas/example/gas-guide-v2.1.pdf"
    "?rev=ABC&sc_lang=en"
)


def _response(
    *,
    url: str,
    text: str = "",
    content: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> Response:
    response = Response()
    response.status_code = 200
    response.url = url
    response.headers.update(headers or {})
    response._content = content if content is not None else text.encode("utf-8")
    response.encoding = "utf-8"
    return response


def _request_getter(
    responses: dict[str, Response],
) -> Callable[[str], Response]:
    def _get(url: str) -> Response:
        return responses[url]

    return _get


def test_discover_observations_classifies_pdf_non_pdf_and_review_links() -> None:
    html = f"""
    <html>
      <body>
        <h1>Example Gas Page</h1>
        <h2>Guides</h2>
        <a href="{_PDF_URL}">1 May 2026 Gas Guide v2.1 (1.2 MB)</a>
        <a href="/-/media/files/gas/example/template.xlsx">Spreadsheet template</a>
        <a href="https://portal.prod.nemnet.net.au/help">Portal help</a>
        <a href="https://example.com/gas-guide.pdf">External PDF</a>
      </body>
    </html>
    """
    review_url = "https://www.aemo.com.au/energy-systems/gas/review"
    review_html = """
    <html><body><h1>Review</h1><a href="/-/media/files/gas/review/faq.pdf">FAQ PDF</a></body></html>
    """
    observations = discover_aemo_gas_document_observations(
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="example",
                source_page_url=_PAGE_URL,
                include_decision="include",
                include_reason="Included for test",
            ),
            AEMOGasDocumentSourcePage(
                corpus_source="review",
                source_page_url=review_url,
                include_decision="needs_human_review",
                include_reason="Needs review for test",
            ),
            AEMOGasDocumentSourcePage(
                corpus_source="excluded",
                source_page_url="scope://aemo-gas/excluded",
                include_decision="exclude",
                exclude_reason="Excluded scope for test",
                fetch_links=False,
            ),
        ),
        request_getter=_request_getter(
            {
                _PAGE_URL: _response(url=_PAGE_URL, text=html),
                review_url: _response(url=review_url, text=review_html),
            }
        ),
        observed_at=_OBSERVED_AT,
    )

    decisions = [(item.source_url, item.include_decision) for item in observations]

    assert (_PDF_URL, "include") in decisions
    assert (
        "https://www.aemo.com.au/-/media/files/gas/example/template.xlsx",
        "exclude",
    ) in decisions
    assert ("https://portal.prod.nemnet.net.au/help", "exclude") in decisions
    assert ("https://example.com/gas-guide.pdf", "exclude") in decisions
    assert (
        "https://www.aemo.com.au/-/media/files/gas/review/faq.pdf",
        "needs_human_review",
    ) in decisions
    assert ("scope://aemo-gas/excluded", "exclude") in decisions

    pdf_observation = next(item for item in observations if item.source_url == _PDF_URL)
    assert pdf_observation.should_download is True
    assert pdf_observation.source_page_title == "Example Gas Page"
    assert pdf_observation.source_page_section == "Guides"
    assert pdf_observation.document_version == "2.1"
    assert pdf_observation.published_date == "1 May 2026"
    assert pdf_observation.media_revision == "ABC"
    assert pdf_observation.document_kind == "guide"


def test_child_source_pages_discovers_same_scope_non_media_pages() -> None:
    source_page = AEMOGasDocumentSourcePage(
        corpus_source="retail_gas",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "gas-retail-markets/procedures-policies-and-guides"
        ),
        include_decision="include",
        discover_child_pages=True,
    )
    soup = soup_getter(
        """
        <h2>Jurisdictions</h2>
        <a href="/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/nsw">NSW</a>
        <a href="/-/media/files/gas/retail/file.pdf">Media PDF</a>
        <a href="/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/manual.pdf">PDF page</a>
        <a href="https://example.com/energy-systems/gas/gas-retail-markets/procedures-policies-and-guides/qld">External</a>
        <a href="/energy-systems/electricity/not-gas">Other</a>
        <a>No href</a>
        """
    )

    children = child_source_pages(source_page, soup)

    assert [child.source_page_url for child in children] == [
        (
            "https://www.aemo.com.au/energy-systems/gas/"
            "gas-retail-markets/procedures-policies-and-guides/nsw"
        )
    ]
    assert children[0].source_page_title == "NSW"
    assert children[0].source_page_section == "Jurisdictions"


def test_child_source_pages_ignores_non_tag_elements() -> None:
    class _FakeSoup:
        def find_all(self, _name: str) -> list[object]:
            return [object()]

    children = child_source_pages(
        AEMOGasDocumentSourcePage(
            corpus_source="retail_gas",
            source_page_url="https://www.aemo.com.au/energy-systems/gas/retail",
            include_decision="include",
        ),
        cast(bs4.BeautifulSoup, _FakeSoup()),
    )

    assert children == []


def test_document_metadata_helpers_normalize_and_infer_identity() -> None:
    normalized_url, query, revision = normalize_source_url(
        "https://WWW.AEMO.COM.AU/-/Media/Files/Gas/Guide.PDF?sc_lang=en&rev=abc"
    )

    assert normalized_url == (
        "https://www.aemo.com.au/-/media/files/gas/guide.pdf?rev=abc&sc_lang=en"
    )
    assert query == "rev=abc&sc_lang=en"
    assert revision == "abc"
    title = clean_document_title(
        "12 March 2025 Technical Guide to the STTM v16.4 (2 MB)",
        "https://www.aemo.com.au/-/media/files/gas/sttm-guide.pdf",
    )
    assert title == "Technical Guide to the STTM"
    assert document_family_id("sttm", title) == "sttm__technical-guide-to-the-sttm"
    assert (
        infer_document_kind(title, "https://example.com/sttm-guide.pdf")
        == "technical_document"
    )
    assert is_aemo_public_url("mailto:test@example.com") is False
    assert (
        clean_document_title(
            "",
            "https://www.aemo.com.au/-/media/files/gas/unknown_document.pdf",
        )
        == "unknown document"
    )


def test_page_and_link_helpers_apply_fallbacks_and_effective_dates() -> None:
    source_page = AEMOGasDocumentSourcePage(
        corpus_source="excluded",
        source_page_url=_PAGE_URL,
        include_decision="exclude",
        include_reason="Scoped but excluded",
        exclude_reason="Out of first slice",
        source_page_section="Configured section",
    )
    soup = soup_getter(
        """
        <html>
          <head><title>Fallback Title</title></head>
          <body>
            <a>Missing href</a>
            <a href="https://example.com/external.pdf">External</a>
            <a href="/-/media/files/gas/excluded.pdf">Effective date: 1 June 2026 Procedure v1.2</a>
            <a href="/-/media/files/gas/excluded.pdf">Effective date: 1 June 2026 Procedure v1.2</a>
          </body>
        </html>
        """
    )

    observations = _page_link_observations(
        source_page,
        soup,
        observed_at=_OBSERVED_AT,
        page_url=_PAGE_URL,
        page_title=extract_page_title(soup, None),
    )

    assert (
        extract_page_title(soup_getter("<html><body></body></html>"), "Configured")
        == "Configured"
    )
    missing_href = soup_getter("<a>Missing href</a>").find("a")
    assert isinstance(missing_href, bs4.Tag)
    assert (
        link_observation(
            source_page,
            missing_href,
            observed_at=_OBSERVED_AT,
            page_url=_PAGE_URL,
            page_title=None,
        )
        is None
    )
    assert [item.source_url for item in observations] == [
        "https://example.com/external.pdf",
        "https://www.aemo.com.au/-/media/files/gas/excluded.pdf",
    ]
    assert observations[0].exclude_reason == "Out of first slice"
    assert observations[1].effective_date == "1 June 2026"
    assert observations[1].include_decision == "exclude"


def test_page_link_observations_ignores_non_tag_elements() -> None:
    class _FakeSoup:
        def find_all(self, _name: str) -> list[object]:
            return [object()]

    observations = _page_link_observations(
        AEMOGasDocumentSourcePage(
            corpus_source="example",
            source_page_url=_PAGE_URL,
            include_decision="include",
        ),
        cast(bs4.BeautifulSoup, _FakeSoup()),
        observed_at=_OBSERVED_AT,
        page_url=_PAGE_URL,
        page_title=None,
    )

    assert observations == []


def test_discover_observations_deduplicates_pages_and_discovers_children() -> None:
    child_url = f"{_PAGE_URL}/child"
    parent_html = f"""
    <html><body>
      <h1>Parent</h1>
      <a href="{child_url}">Child page</a>
    </body></html>
    """
    child_html = """
    <html><body>
      <h1>Child</h1>
      <a href="/-/media/files/gas/child.pdf">Child guide.pdf</a>
    </body></html>
    """

    observations = discover_aemo_gas_document_observations(
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="example",
                source_page_url=_PAGE_URL,
                include_decision="include",
                discover_child_pages=True,
            ),
            AEMOGasDocumentSourcePage(
                corpus_source="example",
                source_page_url=_PAGE_URL,
                include_decision="include",
            ),
        ),
        request_getter=_request_getter(
            {
                _PAGE_URL: _response(url=_PAGE_URL, text=parent_html),
                child_url: _response(url=child_url, text=child_html),
            }
        ),
    )

    assert [item.source_page_url for item in observations].count(_PAGE_URL) == 2
    assert any(item.source_page_url == child_url for item in observations)


def test_scrape_and_land_downloads_included_pdfs_and_records_metadata() -> None:
    html = f"""
    <html><body>
      <h1>Example Gas Page</h1>
      <a href="{_PDF_URL}">Gas Guide v2.1</a>
      <a href="/-/media/files/gas/example/workbook.xlsx">Workbook</a>
    </body></html>
    """
    s3_client = MagicMock()
    s3_client.head_object.side_effect = ClientError(
        {"Error": {"Code": "404"}},
        "HeadObject",
    )
    result = scrape_and_land_aemo_gas_document_sources(
        s3_client=s3_client,
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="example",
                source_page_url=_PAGE_URL,
                include_decision="include",
            ),
            AEMOGasDocumentSourcePage(
                corpus_source="review",
                source_page_url="scope://aemo-gas/review",
                include_decision="needs_human_review",
                fetch_links=False,
            ),
        ),
        request_getter=_request_getter(
            {
                _PAGE_URL: _response(url=_PAGE_URL, text=html),
                _PDF_URL: _response(
                    url=f"{_PDF_URL}&resolved=true",
                    content=_PDF_BYTES,
                    headers={
                        "Content-Type": "application/pdf",
                        "Content-Length": str(len(_PDF_BYTES)),
                        "ETag": '"abc"',
                        "Last-Modified": "Thu, 07 May 2026 00:00:00 GMT",
                    },
                ),
            }
        ),
        landing_bucket="landing",
        archive_bucket="archive",
        observed_at=_OBSERVED_AT,
    )

    pdf_records = [record for record in result.records if record.content_sha256]

    assert result.included_pdf_count == 1
    assert result.excluded_observation_count == 1
    assert result.needs_human_review_observation_count == 1
    assert len(result.landed_keys) == 1
    assert result.landed_keys[0].startswith(f"{AEMO_GAS_DOCUMENTS_PREFIX}/")
    assert result.landed_keys[0].endswith(".pdf")
    s3_client.upload_fileobj.assert_called_once()
    assert pdf_records[0].content_type == "application/pdf"
    assert pdf_records[0].content_length == len(_PDF_BYTES)
    assert pdf_records[0].resolved_url == f"{_PDF_URL}&resolved=true"
    assert pdf_records[0].storage_uri == f"s3://archive/{result.landed_keys[0]}"
    assert pdf_records[0].document_version_id == pdf_records[0].content_sha256

    frame = records_to_lazyframe(result.records, ingested_timestamp=_OBSERVED_AT)
    collected = frame.collect()
    assert collected.height == 4
    assert dict(collected.schema)["content_length"] == pl.Int64
    assert set(collected["include_decision"].to_list()) == {
        "include",
        "exclude",
        "needs_human_review",
    }


def test_scrape_and_land_deduplicates_landed_pdf_bytes() -> None:
    pdf_url_two = "https://www.aemo.com.au/-/media/files/gas/example/gas-guide-copy.pdf"
    html = f"""
    <html><body>
      <h1>Example Gas Page</h1>
      <a href="{_PDF_URL}">Gas Guide v2.1</a>
      <a href="{pdf_url_two}">Gas Guide copy v2.1</a>
    </body></html>
    """
    s3_client = MagicMock()
    s3_client.head_object.side_effect = ClientError(
        {"Error": {"Code": "404"}},
        "HeadObject",
    )

    result = scrape_and_land_aemo_gas_document_sources(
        s3_client=s3_client,
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="example",
                source_page_url=_PAGE_URL,
                include_decision="include",
            ),
        ),
        request_getter=_request_getter(
            {
                _PAGE_URL: _response(url=_PAGE_URL, text=html),
                _PDF_URL: _response(
                    url="",
                    content=_PDF_BYTES,
                    headers={"Content-Length": "not-a-number"},
                ),
                pdf_url_two: _response(url=pdf_url_two, content=_PDF_BYTES),
            }
        ),
        landing_bucket="landing",
        archive_bucket="archive",
        observed_at=_OBSERVED_AT,
    )

    pdf_records = [record for record in result.records if record.content_sha256]

    assert result.included_pdf_count == 2
    assert len(result.landed_keys) == 1
    s3_client.upload_fileobj.assert_called_once()
    assert pdf_records[0].content_length == len(_PDF_BYTES)
    assert pdf_records[0].resolved_url == _PDF_URL
    assert pdf_records[0].target_s3_key == pdf_records[1].target_s3_key


def test_land_pdf_once_skips_existing_objects_and_raises_unexpected_errors() -> None:
    s3_client = MagicMock()

    assert (
        _land_pdf_once(
            s3_client=s3_client,
            landing_bucket="landing",
            key="bronze/aemo_gas_documents/existing.pdf",
            content=_PDF_BYTES,
        )
        is False
    )
    s3_client.upload_fileobj.assert_not_called()

    s3_client.head_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied"}},
        "HeadObject",
    )
    with pytest.raises(ClientError):
        _land_pdf_once(
            s3_client=s3_client,
            landing_bucket="landing",
            key="bronze/aemo_gas_documents/error.pdf",
            content=_PDF_BYTES,
        )


def test_records_to_lazyframe_preserves_empty_schema() -> None:
    frame = records_to_lazyframe([], ingested_timestamp=_OBSERVED_AT)

    assert frame.collect().height == 0
    assert dict(frame.collect_schema())["content_sha256"] == pl.String


def test_stable_hash_accepts_datetimes() -> None:
    assert _stable_hash([_OBSERVED_AT]) == _stable_hash([_OBSERVED_AT])


def test_write_aemo_gas_document_sources_batch_appends_when_table_missing(
    mocker: MockerFixture,
) -> None:
    batch = pl.LazyFrame({"surrogate_key": ["key"], "source_content_hash": ["hash"]})
    sink_delta = mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)
    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.table_exists",
        return_value=False,
    )

    result = write_aemo_gas_document_sources_batch(
        batch, target_table_uri="s3://aemo/table"
    )

    sink_delta.assert_called_once_with("s3://aemo/table", mode="append")
    assert result == AEMOGasDocumentSourceWriteResult(
        row_count=1,
        target_exists_before_write=False,
        wrote_table=True,
        write_mode="append",
    )


def test_write_aemo_gas_document_sources_batch_skips_empty_existing_table(
    mocker: MockerFixture,
) -> None:
    batch = records_to_lazyframe([], ingested_timestamp=_OBSERVED_AT)
    sink_delta = mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)
    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.table_exists",
        return_value=True,
    )

    result = write_aemo_gas_document_sources_batch(
        batch, target_table_uri="s3://aemo/table"
    )

    sink_delta.assert_not_called()
    assert result == AEMOGasDocumentSourceWriteResult(
        row_count=0,
        target_exists_before_write=True,
        wrote_table=False,
        write_mode="skip",
    )


def test_write_aemo_gas_document_sources_batch_merges_existing_table(
    mocker: MockerFixture,
) -> None:
    batch = pl.LazyFrame({"surrogate_key": ["key"], "source_content_hash": ["hash"]})
    merge_builder = mocker.MagicMock()
    merge_builder.when_matched_update_all.return_value = merge_builder
    merge_builder.when_not_matched_insert_all.return_value = merge_builder
    sink_delta = mocker.patch.object(
        pl.LazyFrame,
        "sink_delta",
        return_value=merge_builder,
    )
    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.table_exists",
        return_value=True,
    )
    logger = mocker.MagicMock()

    result = write_aemo_gas_document_sources_batch(
        batch,
        target_table_uri="s3://aemo/table",
        logger=logger,
    )

    sink_delta.assert_called_once_with(
        "s3://aemo/table",
        mode="merge",
        delta_merge_options=DELTA_MERGE_OPTIONS,
    )
    merge_builder.when_matched_update_all.assert_called_once_with(
        predicate=(
            "target.source_content_hash IS NULL OR "
            "source.source_content_hash != target.source_content_hash"
        )
    )
    merge_builder.when_not_matched_insert_all.assert_called_once_with()
    merge_builder.execute.assert_called_once_with()
    assert logger.info.call_count == 2
    assert result == AEMOGasDocumentSourceWriteResult(
        row_count=1,
        target_exists_before_write=True,
        wrote_table=True,
        write_mode="merge",
    )
