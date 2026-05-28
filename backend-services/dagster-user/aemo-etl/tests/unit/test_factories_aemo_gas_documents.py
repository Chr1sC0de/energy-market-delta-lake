import datetime as dt
import hashlib
from collections.abc import Callable
from typing import cast
from unittest.mock import MagicMock

import bs4
import polars as pl
import pytest
from botocore.exceptions import ClientError
from pytest_mock import MockerFixture
from requests import HTTPError, Response

from aemo_etl.factories.aemo_gas_documents.assets import (
    AEMO_GAS_DOCUMENTS_PREFIX,
    AEMO_GAS_DOCUMENT_REQUEST_HEADERS,
    AEMO_GAS_DOCUMENT_REQUEST_TIMEOUT_SECONDS,
    DELTA_MERGE_OPTIONS,
    AEMOGasDocumentSourceWriteResult,
    DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES,
    _land_media_once,
    _media_key,
    land_aemo_gas_document_observations,
    _stable_hash,
    records_to_lazyframe,
    request_get_aemo_gas_document,
    scrape_and_land_aemo_gas_document_sources,
    write_aemo_gas_document_sources_batch,
)
from aemo_etl.factories.aemo_gas_documents.models import (
    AEMO_GSOO_CORPUS_SOURCE,
    AEMO_GSOO_URL,
    AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
    AEMO_MAJOR_PUBLICATIONS_HUB_URL,
    AEMO_WA_GSOO_CORPUS_SOURCE,
    AEMO_WA_GSOO_URL,
    AEMOGasDocumentSourcePage,
    DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES,
)
from aemo_etl.factories.aemo_gas_documents.manifest import (
    discovery_report_payload,
    dump_manifest_json,
    existing_manifest_entries,
    load_default_discovery_report_payload,
    load_default_aemo_gas_document_observations,
    load_default_manifest_payload,
    manifest_payload,
    media_link_manifest_entry,
    observations_from_manifest_payload,
    source_page_manifest_entry,
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
_XLSX_BYTES = b"PK\x03\x04 workbook\n"
_PAGE_URL = "https://www.aemo.com.au/energy-systems/gas/example"
_PDF_URL = (
    "https://www.aemo.com.au/-/media/files/gas/example/gas-guide-v2.1.pdf"
    "?rev=ABC&sc_lang=en"
)
_XLSX_URL = "https://www.aemo.com.au/-/media/files/gas/example/workbook.xlsx"


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


def test_request_get_aemo_gas_document_uses_browser_compatible_headers(
    mocker: MockerFixture,
) -> None:
    get = mocker.patch("aemo_etl.factories.aemo_gas_documents.assets.requests.get")
    get.return_value = _response(url=_PDF_URL, content=_PDF_BYTES)

    response = request_get_aemo_gas_document(_PDF_URL)

    assert response.content == _PDF_BYTES
    get.assert_called_once_with(
        _PDF_URL,
        headers=AEMO_GAS_DOCUMENT_REQUEST_HEADERS,
        timeout=AEMO_GAS_DOCUMENT_REQUEST_TIMEOUT_SECONDS,
    )


def test_discover_observations_classifies_media_and_review_links() -> None:
    html = f"""
    <html>
      <body>
        <h1>Example Gas Page</h1>
        <h2>Guides</h2>
        <a href="{_PDF_URL}">1 May 2026 Gas Guide v2.1 (1.2 MB)</a>
        <a href="{_XLSX_URL}">Spreadsheet template</a>
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
        _XLSX_URL,
        "include",
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
    xlsx_observation = next(
        item for item in observations if item.source_url == _XLSX_URL
    )
    assert xlsx_observation.should_download is True


def test_discover_observations_records_failed_source_page_and_continues() -> None:
    failed_url = "https://www.aemo.com.au/energy-systems/gas/blocked"
    html = f"""
    <html>
      <body>
        <h1>Example Gas Page</h1>
        <a href="{_PDF_URL}">Gas Guide v2.1</a>
      </body>
    </html>
    """

    def _get(url: str) -> Response:
        if url == failed_url:
            raise HTTPError("403 Client Error: Forbidden for url")
        return _response(url=url, text=html)

    observations = discover_aemo_gas_document_observations(
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="blocked",
                source_page_url=failed_url,
                include_decision="include",
                include_reason="Configured source page for test.",
            ),
            AEMOGasDocumentSourcePage(
                corpus_source="example",
                source_page_url=_PAGE_URL,
                include_decision="include",
                include_reason="Included for test",
            ),
        ),
        request_getter=_get,
        observed_at=_OBSERVED_AT,
    )

    failed_observation = observations[0]
    pdf_observation = next(item for item in observations if item.source_url == _PDF_URL)

    assert failed_observation.observation_type == "source_page"
    assert failed_observation.source_url == failed_url
    assert failed_observation.include_decision == "needs_human_review"
    assert failed_observation.should_download is False
    assert "Source page load failed" in (failed_observation.exclude_reason or "")
    assert pdf_observation.include_decision == "include"
    assert pdf_observation.should_download is True


def test_default_source_pages_include_major_publications_hub_scope() -> None:
    source_pages = [
        source_page
        for source_page in DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES
        if source_page.corpus_source == AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE
    ]

    assert len(source_pages) == 1
    assert source_pages[0].source_page_url == AEMO_MAJOR_PUBLICATIONS_HUB_URL
    assert source_pages[0].include_decision == "needs_human_review"
    assert source_pages[0].discover_child_pages is True
    assert source_pages[0].fetch_links is True


def test_default_major_publications_download_source_pages_include_gsoo_bundles() -> (
    None
):
    source_pages_by_source = {
        source_page.corpus_source: source_page
        for source_page in DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES
    }

    assert list(source_pages_by_source) == [
        AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
        AEMO_GSOO_CORPUS_SOURCE,
        AEMO_WA_GSOO_CORPUS_SOURCE,
    ]
    assert (
        source_pages_by_source[AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE].source_page_url
        == AEMO_MAJOR_PUBLICATIONS_HUB_URL
    )
    assert source_pages_by_source[AEMO_GSOO_CORPUS_SOURCE].source_page_url == (
        AEMO_GSOO_URL
    )
    assert source_pages_by_source[AEMO_WA_GSOO_CORPUS_SOURCE].source_page_url == (
        AEMO_WA_GSOO_URL
    )
    assert all(
        source_page.include_decision == "include"
        for source_page in DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES
    )
    assert all(
        source_page.discover_child_pages
        for source_page in DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES
    )


def test_major_publications_hub_discovers_review_source_pages_and_links() -> None:
    child_url = f"{AEMO_MAJOR_PUBLICATIONS_HUB_URL}integrated-system-plan-isp"
    hub_media_url = (
        "https://www.aemo.com.au/-/media/files/major-publications/"
        "isp/2026-integrated-system-plan.pdf?rev=HUB"
    )
    child_media_url = (
        "https://www.aemo.com.au/-/media/files/major-publications/"
        "isp/2026-integrated-system-plan-appendix.pdf?rev=CHILD"
    )
    hub_html = f"""
    <html>
      <head>
        <link rel="stylesheet" href="/assets/site.css">
        <script src="/assets/site.js"></script>
      </head>
      <body>
        <h1>Major publications</h1>
        <nav>
          <a href="/energy-systems/electricity">Electricity navigation</a>
        </nav>
        <section>
          <h2>Planning</h2>
          <a href="integrated-system-plan-isp">Integrated System Plan</a>
          <a href="{child_url}">Integrated System Plan</a>
          <a href="{hub_media_url}">2026 Integrated System Plan</a>
          <a href="{hub_media_url}">2026 Integrated System Plan</a>
          <a href="https://example.com/isp.pdf">External report</a>
        </section>
      </body>
    </html>
    """
    child_html = f"""
    <html>
      <body>
        <h1>Integrated System Plan</h1>
        <a href="{child_media_url}">2026 ISP Appendix</a>
        <a href="/energy-systems/gas">Gas navigation</a>
      </body>
    </html>
    """

    observations = discover_aemo_gas_document_observations(
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source=AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
                source_page_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
                include_decision="needs_human_review",
                include_reason="Observation-only major publications test scope.",
                discover_child_pages=True,
            ),
        ),
        request_getter=_request_getter(
            {
                AEMO_MAJOR_PUBLICATIONS_HUB_URL: _response(
                    url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
                    text=hub_html,
                ),
                child_url: _response(url=child_url, text=child_html),
            }
        ),
        observed_at=_OBSERVED_AT,
    )

    source_page_urls = [
        item.source_url
        for item in observations
        if item.observation_type == "source_page"
    ]
    link_observations = [
        item for item in observations if item.observation_type == "link"
    ]
    link_urls = [item.source_url for item in link_observations]

    assert source_page_urls == [AEMO_MAJOR_PUBLICATIONS_HUB_URL, child_url]
    assert link_urls.count(child_url) == 1
    assert link_urls.count(hub_media_url) == 1
    assert child_media_url in link_urls
    assert "/assets/site.css" not in link_urls
    assert "/assets/site.js" not in link_urls
    assert all(item.include_decision != "include" for item in link_observations)
    assert all(item.should_download is False for item in link_observations)
    external_observation = next(
        item
        for item in link_observations
        if item.source_url == "https://example.com/isp.pdf"
    )
    assert external_observation.include_decision == "exclude"


def test_gsoo_and_wa_gsoo_pages_discover_publication_bundle_media_and_audit_links() -> (
    None
):
    gsoo_child_url = f"{AEMO_GSOO_URL}/2025-gas-statement-of-opportunities"
    gsoo_report_url = (
        "https://www.aemo.com.au/-/media/files/gas/national-planning-and-"
        "forecasting/gsoo/2026/2026-gas-statement-of-opportunities.pdf?rev=GSOO"
    )
    gsoo_data_url = (
        "https://www.aemo.com.au/-/media/files/gas/national-planning-and-"
        "forecasting/gsoo/2026/2026-gsoo-report-figures-and-data.xlsx"
    )
    gsoo_child_report_url = (
        "https://www.aemo.com.au/-/media/files/gas/national-planning-and-"
        "forecasting/gsoo/2025/2025-gas-statement-of-opportunities.pdf"
    )
    gas_forecasting_portal_url = "https://forecasting.aemo.com.au/Gas"
    wa_report_url = (
        "https://www.aemo.com.au/-/media/files/gas/wa-gsoo/2025/"
        "2025-wa-gas-statement-of-opportunities.pdf?rev=WAGSOO"
    )
    wa_data_url = (
        "https://www.aemo.com.au/-/media/files/gas/wa-gsoo/2025/"
        "2025-wa-gsoo-data-register.xlsx"
    )
    wa_media_release_url = "https://www.aemo.com.au/newsroom/media-release/wa-gsoo-2025"
    gsoo_html = f"""
    <html>
      <body>
        <h1>Gas Statement of Opportunities</h1>
        <h2>2026 GSOO report</h2>
        <a href="{gsoo_report_url}">26/03/2026 2026 Gas Statement of Opportunities</a>
        <h2>Supporting material</h2>
        <a href="{gas_forecasting_portal_url}">View the Gas forecasting data portal</a>
        <a href="{gsoo_data_url}">26/03/2026 2026 GSOO report figures and data</a>
        <h2>Previous GSOO reports</h2>
        <a href="{gsoo_child_url}">2025 Gas Statement of Opportunities</a>
      </body>
    </html>
    """
    gsoo_child_html = f"""
    <html>
      <body>
        <h1>2025 Gas Statement of Opportunities</h1>
        <a href="{gsoo_child_report_url}">2025 Gas Statement of Opportunities</a>
      </body>
    </html>
    """
    wa_html = f"""
    <html>
      <body>
        <h1>WA Gas Statement of Opportunities</h1>
        <h2>WA Gas Statement of Opportunities - December 2025</h2>
        <a href="{wa_report_url}">19/12/2025 2025 WA Gas Statement of Opportunities</a>
        <h2>Supporting documents</h2>
        <a href="{wa_data_url}">19/12/2025 2025 WA GSOO Data Register - Figures</a>
        <a href="{wa_media_release_url}">Media release: WA domestic gas market</a>
      </body>
    </html>
    """
    source_pages = tuple(
        source_page
        for source_page in DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES
        if source_page.corpus_source
        in {AEMO_GSOO_CORPUS_SOURCE, AEMO_WA_GSOO_CORPUS_SOURCE}
    )

    observations = discover_aemo_gas_document_observations(
        source_pages=source_pages,
        request_getter=_request_getter(
            {
                AEMO_GSOO_URL: _response(url=AEMO_GSOO_URL, text=gsoo_html),
                AEMO_WA_GSOO_URL: _response(url=AEMO_WA_GSOO_URL, text=wa_html),
                gsoo_child_url: _response(url=gsoo_child_url, text=gsoo_child_html),
            }
        ),
        observed_at=_OBSERVED_AT,
    )

    source_page_urls = [
        item.source_url
        for item in observations
        if item.observation_type == "source_page"
    ]
    link_observations = [
        item for item in observations if item.observation_type == "link"
    ]
    included_urls = {
        item.source_url
        for item in link_observations
        if item.include_decision == "include" and item.should_download
    }
    link_by_url = {item.source_url: item for item in link_observations}

    assert source_page_urls == [AEMO_GSOO_URL, AEMO_WA_GSOO_URL, gsoo_child_url]
    assert included_urls == {
        gsoo_report_url,
        gsoo_data_url,
        gsoo_child_report_url,
        wa_report_url,
        wa_data_url,
    }
    assert link_by_url[gsoo_report_url].corpus_source == AEMO_GSOO_CORPUS_SOURCE
    assert link_by_url[gsoo_data_url].source_page_section == "Supporting material"
    assert link_by_url[gsoo_child_report_url].source_page_url == gsoo_child_url
    assert link_by_url[wa_report_url].corpus_source == AEMO_WA_GSOO_CORPUS_SOURCE
    assert link_by_url[gas_forecasting_portal_url].include_decision == "exclude"
    assert link_by_url[wa_media_release_url].include_decision == "exclude"
    assert link_by_url[gsoo_child_url].should_download is False


def test_manifest_payload_recreates_source_page_and_media_observations() -> None:
    payload = {
        "schema_version": 1,
        "generated_at": "2026-05-10T00:00:00Z",
        "source_pages": [
            {
                "corpus_source": "example",
                "source_page_url": _PAGE_URL,
                "source_page_title": "Example Gas Page",
                "include_decision": "include",
                "include_reason": "Included for test",
            }
        ],
        "media_links": [
            {
                "corpus_source": "example",
                "source_page_url": _PAGE_URL,
                "source_page_title": "Example Gas Page",
                "source_page_section": "Guides",
                "source_link_text": "1 May 2026 Gas Guide v2.1",
                "source_url": _PDF_URL,
                "resolved_url": f"{_PDF_URL}&resolved=true",
                "document_kind": "guide",
                "include_decision": "include",
                "include_reason": "Included for test",
                "media_revision": "ABC",
            }
        ],
    }

    observations = observations_from_manifest_payload(
        payload,
        observed_at=_OBSERVED_AT,
    )

    assert [item.observation_type for item in observations] == ["source_page", "link"]
    assert observations[0].source_page_title == "Example Gas Page"
    assert observations[1].should_download is True
    assert observations[1].resolved_url == f"{_PDF_URL}&resolved=true"
    assert observations[1].document_family_id == "example__gas-guide"
    assert observations[1].document_version == "2.1"
    assert observations[1].published_date == "1 May 2026"
    assert observations[1].media_revision == "ABC"


def test_default_manifest_loads_packaged_source_page_and_media_observations() -> None:
    payload = load_default_manifest_payload()
    observations = load_default_aemo_gas_document_observations(
        observed_at=_OBSERVED_AT,
    )
    source_page_observations = [
        item for item in observations if item.observation_type == "source_page"
    ]
    media_observations = [
        item for item in observations if item.observation_type == "link"
    ]

    assert payload["schema_version"] == 1
    assert payload["media_link_count"] > 0
    assert len(source_page_observations) == payload["source_page_count"]
    assert len(media_observations) == payload["media_link_count"]
    assert any(item.should_download for item in media_observations)
    assert all(
        item.source_url.startswith("https://www.aemo.com.au/-/media/")
        for item in media_observations
    )


def test_default_manifest_does_not_download_failed_media_validations() -> None:
    manifest = load_default_manifest_payload()
    report = load_default_discovery_report_payload()
    failed_urls = {
        validation["source_url"]
        for validation in report["media_validations"]
        if validation["ok"] is False
    }
    downloadable_urls = {
        media_link["source_url"]
        for media_link in manifest["media_links"]
        if media_link["should_download"] is True
    }
    held_failed_urls = {
        media_link["source_url"]
        for media_link in manifest["media_links"]
        if media_link["source_url"] in failed_urls
        and media_link["should_download"] is False
    }

    assert failed_urls
    assert downloadable_urls
    assert held_failed_urls
    assert failed_urls.isdisjoint(downloadable_urls)


def test_manifest_helpers_dump_and_index_entries() -> None:
    source_page = AEMOGasDocumentSourcePage(
        corpus_source="example",
        source_page_url=_PAGE_URL,
        include_decision="include",
        include_reason="Included for test",
    )
    source_entry = source_page_manifest_entry(
        source_page,
        observed_at=_OBSERVED_AT,
        status="refreshed",
    )
    observation = observations_from_manifest_payload(
        {
            "schema_version": 1,
            "generated_at": "2026-05-10T00:00:00Z",
            "source_pages": [source_entry],
            "media_links": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "source_url": _PDF_URL,
                    "include_decision": "include",
                }
            ],
        },
        observed_at=_OBSERVED_AT,
    )[1]
    media_entry = media_link_manifest_entry(observation)
    payload = manifest_payload(
        generated_at=_OBSERVED_AT,
        source_pages=[source_entry],
        media_links=[media_entry],
    )
    report = discovery_report_payload(
        generated_at=_OBSERVED_AT,
        source_pages=[{"source_page_url": _PAGE_URL}],
        media_validations=[{"source_url": _PDF_URL}],
    )
    source_pages, media_links = existing_manifest_entries(payload)

    assert source_pages[_PAGE_URL]["status"] == "refreshed"
    assert media_links[_PAGE_URL] == [media_entry]
    assert '"media_link_count": 1' in dump_manifest_json(payload)
    assert report["media_validation_count"] == 1


def test_manifest_uses_generation_timestamp_fallbacks() -> None:
    observations = observations_from_manifest_payload(
        {
            "schema_version": 1,
            "generated_at": "2026-05-11T10:00:00+10:00",
            "source_pages": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "include_decision": "include",
                }
            ],
            "media_links": [],
        }
    )
    observations_without_generated_at = observations_from_manifest_payload(
        {
            "schema_version": 1,
            "source_pages": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "include_decision": "include",
                }
            ],
        }
    )

    assert observations[0].source_page_observed_at == dt.datetime(
        2026,
        5,
        11,
        0,
        0,
        tzinfo=dt.UTC,
    )
    assert observations_without_generated_at[0].source_page_observed_at.tzinfo == dt.UTC


def test_manifest_respects_explicit_should_download_false() -> None:
    observations = observations_from_manifest_payload(
        {
            "schema_version": 1,
            "generated_at": "2026-05-11T00:00:00Z",
            "source_pages": [],
            "media_links": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "source_url": _PDF_URL,
                    "include_decision": "include",
                    "should_download": False,
                }
            ],
        }
    )

    assert observations[0].include_decision == "include"
    assert observations[0].should_download is False


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": 2, "source_pages": [], "media_links": []},
        {"schema_version": 1, "source_pages": {}, "media_links": []},
        {"schema_version": 1, "source_pages": [object()], "media_links": []},
        {
            "schema_version": 1,
            "source_pages": [
                {
                    "corpus_source": "",
                    "source_page_url": _PAGE_URL,
                    "include_decision": "include",
                }
            ],
            "media_links": [],
        },
        {
            "schema_version": 1,
            "source_pages": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "include_decision": "include",
                    "include_reason": 5,
                }
            ],
            "media_links": [],
        },
        {
            "schema_version": 1,
            "source_pages": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "include_decision": "include",
                    "fetch_links": "yes",
                }
            ],
            "media_links": [],
        },
        {
            "schema_version": 1,
            "source_pages": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "include_decision": "maybe",
                }
            ],
            "media_links": [],
        },
        {
            "schema_version": 1,
            "source_pages": [],
            "media_links": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "source_url": _PDF_URL,
                    "include_decision": "include",
                    "should_download": "yes",
                }
            ],
        },
    ],
)
def test_manifest_rejects_invalid_payloads(payload: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        observations_from_manifest_payload(payload)


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


def test_scrape_and_land_downloads_included_media_and_records_metadata() -> None:
    html = f"""
    <html><body>
      <h1>Example Gas Page</h1>
      <a href="{_PDF_URL}">Gas Guide v2.1</a>
      <a href="{_XLSX_URL}">Workbook</a>
      <a href="https://example.com/workbook.xlsx">External workbook</a>
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
                _XLSX_URL: _response(
                    url=_XLSX_URL,
                    content=_XLSX_BYTES,
                    headers={
                        "Content-Type": (
                            "application/vnd.openxmlformats-officedocument."
                            "spreadsheetml.sheet"
                        ),
                    },
                ),
            }
        ),
        landing_bucket="landing",
        archive_bucket="archive",
        observed_at=_OBSERVED_AT,
    )

    media_records = [record for record in result.records if record.content_sha256]

    assert result.included_media_count == 2
    assert result.excluded_observation_count == 1
    assert result.needs_human_review_observation_count == 1
    assert len(result.landed_keys) == 2
    assert all(
        key.startswith(f"{AEMO_GAS_DOCUMENTS_PREFIX}/") for key in result.landed_keys
    )
    assert {key.rsplit(".", 1)[-1] for key in result.landed_keys} == {"pdf", "xlsx"}
    assert s3_client.upload_fileobj.call_count == 2
    assert media_records[0].content_type == "application/pdf"
    assert media_records[0].content_length == len(_PDF_BYTES)
    assert media_records[0].resolved_url == f"{_PDF_URL}&resolved=true"
    assert media_records[0].storage_uri == f"s3://archive/{result.landed_keys[0]}"
    assert media_records[0].document_version_id == media_records[0].content_sha256
    assert media_records[1].content_type == (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert media_records[1].target_s3_key is not None
    assert media_records[1].target_s3_key.endswith(".xlsx")

    frame = records_to_lazyframe(result.records, ingested_timestamp=_OBSERVED_AT)
    collected = frame.collect()
    assert collected.height == 5
    assert dict(collected.schema)["content_length"] == pl.Int64
    assert set(collected["include_decision"].to_list()) == {
        "include",
        "exclude",
        "needs_human_review",
    }


def test_land_manifest_observations_downloads_included_hub_media_urls() -> None:
    hub_pdf_url = (
        "https://www.aemo.com.au/-/media/files/major-publications/isp/report.pdf"
    )
    hub_xlsx_url = (
        "https://www.aemo.com.au/-/media/files/major-publications/isp/workbook.xlsx"
    )
    observations = observations_from_manifest_payload(
        {
            "schema_version": 1,
            "generated_at": "2026-05-10T00:00:00Z",
            "source_pages": [
                {
                    "corpus_source": AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
                    "source_page_url": AEMO_MAJOR_PUBLICATIONS_HUB_URL,
                    "source_page_title": "Major publications",
                    "include_decision": "include",
                }
            ],
            "media_links": [
                {
                    "corpus_source": AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
                    "source_page_url": AEMO_MAJOR_PUBLICATIONS_HUB_URL,
                    "source_link_text": "Gas Guide v2.1",
                    "source_url": hub_pdf_url,
                    "include_decision": "include",
                },
                {
                    "corpus_source": AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
                    "source_page_url": AEMO_MAJOR_PUBLICATIONS_HUB_URL,
                    "source_link_text": "Workbook",
                    "source_url": hub_xlsx_url,
                    "include_decision": "include",
                },
            ],
        },
        observed_at=_OBSERVED_AT,
    )
    requested_urls: list[str] = []
    s3_client = MagicMock()
    s3_client.head_object.side_effect = ClientError(
        {"Error": {"Code": "404"}},
        "HeadObject",
    )

    def _get(url: str) -> Response:
        requested_urls.append(url)
        if url == hub_pdf_url:
            return _response(
                url=url,
                content=_PDF_BYTES,
                headers={"Content-Type": "application/pdf"},
            )
        if url == hub_xlsx_url:
            return _response(
                url=url,
                content=_XLSX_BYTES,
                headers={
                    "Content-Type": (
                        "application/vnd.openxmlformats-officedocument."
                        "spreadsheetml.sheet"
                    )
                },
            )
        raise AssertionError(f"unexpected source-page request: {url}")

    result = land_aemo_gas_document_observations(
        s3_client=s3_client,
        observations=observations,
        request_getter=_get,
        landing_bucket="landing",
        archive_bucket="archive",
    )

    assert requested_urls == [hub_pdf_url, hub_xlsx_url]
    assert result.included_media_count == 2
    assert result.excluded_observation_count == 0
    assert len(result.records) == 3


def test_land_manifest_observations_records_runtime_download_failures() -> None:
    observations = observations_from_manifest_payload(
        {
            "schema_version": 1,
            "generated_at": "2026-05-10T00:00:00Z",
            "source_pages": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "source_page_title": "Example Gas Page",
                    "include_decision": "include",
                }
            ],
            "media_links": [
                {
                    "corpus_source": "example",
                    "source_page_url": _PAGE_URL,
                    "source_link_text": "Gas Guide v2.1",
                    "source_url": _PDF_URL,
                    "include_decision": "include",
                }
            ],
        },
        observed_at=_OBSERVED_AT,
    )
    requested_urls: list[str] = []
    s3_client = MagicMock()
    logger = MagicMock()

    def _get(url: str) -> Response:
        requested_urls.append(url)
        response = _response(url=url, text="blocked")
        response.status_code = 403
        raise HTTPError("403 Client Error: Forbidden for url", response=response)

    result = land_aemo_gas_document_observations(
        s3_client=s3_client,
        observations=observations,
        request_getter=_get,
        landing_bucket="landing",
        archive_bucket="archive",
        logger=logger,
    )

    failed_record = next(
        record for record in result.records if record.source_url == _PDF_URL
    )

    assert requested_urls == [_PDF_URL]
    assert result.failed_download_count == 1
    assert result.included_media_count == 0
    assert result.landed_keys == []
    assert failed_record.content_sha256 is None
    assert failed_record.target_s3_key is None
    assert failed_record.exclude_reason == (
        "Download failed during materialization: 403 Client Error: Forbidden for url"
    )
    logger.warning.assert_called_once()
    warning_args = logger.warning.call_args.args
    assert warning_args[0] == "recording AEMO gas document download failure for %s: %s"
    assert warning_args[1] == _PDF_URL
    assert str(warning_args[2]) == "403 Client Error: Forbidden for url"
    s3_client.upload_fileobj.assert_not_called()


def test_scrape_and_land_deduplicates_landed_media_bytes() -> None:
    csv_url = "https://www.aemo.com.au/-/media/files/gas/example/workbook-copy.csv"
    html = f"""
    <html><body>
      <h1>Example Gas Page</h1>
      <a href="{_XLSX_URL}">Workbook</a>
      <a href="{csv_url}">Workbook copy</a>
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
                _XLSX_URL: _response(
                    url="",
                    content=_XLSX_BYTES,
                    headers={"Content-Length": "not-a-number"},
                ),
                csv_url: _response(
                    url=csv_url,
                    content=_XLSX_BYTES,
                    headers={"Content-Type": "text/csv"},
                ),
            }
        ),
        landing_bucket="landing",
        archive_bucket="archive",
        observed_at=_OBSERVED_AT,
    )

    media_records = [record for record in result.records if record.content_sha256]

    assert result.included_media_count == 2
    assert len(result.landed_keys) == 1
    assert result.landed_keys[0].endswith(".xlsx")
    s3_client.upload_fileobj.assert_called_once()
    assert media_records[0].content_length == len(_XLSX_BYTES)
    assert media_records[0].resolved_url == _XLSX_URL
    assert media_records[0].target_s3_key == media_records[1].target_s3_key


def test_land_media_once_skips_existing_objects_and_raises_unexpected_errors() -> None:
    s3_client = MagicMock()

    assert (
        _land_media_once(
            s3_client=s3_client,
            landing_bucket="landing",
            key="bronze/aemo_gas_documents/existing.pdf",
            content=_PDF_BYTES,
            content_type="application/pdf",
        )
        is False
    )
    s3_client.upload_fileobj.assert_not_called()

    s3_client.head_object.side_effect = ClientError(
        {"Error": {"Code": "AccessDenied"}},
        "HeadObject",
    )
    with pytest.raises(ClientError):
        _land_media_once(
            s3_client=s3_client,
            landing_bucket="landing",
            key="bronze/aemo_gas_documents/error.pdf",
            content=_PDF_BYTES,
            content_type="application/pdf",
        )


def test_records_to_lazyframe_preserves_empty_schema() -> None:
    frame = records_to_lazyframe([], ingested_timestamp=_OBSERVED_AT)

    assert frame.collect().height == 0
    assert dict(frame.collect_schema())["content_sha256"] == pl.String


def test_stable_hash_accepts_datetimes() -> None:
    assert _stable_hash([_OBSERVED_AT]) == _stable_hash([_OBSERVED_AT])


def test_media_key_preserves_safe_extension_or_content_type_suffix() -> None:
    content_sha256 = hashlib.sha256(_XLSX_BYTES).hexdigest()

    assert _media_key(
        content_sha256=content_sha256,
        source_url="https://www.aemo.com.au/-/media/files/report.XLSX?rev=1",
        content_type="application/octet-stream",
    ).endswith(".xlsx")
    assert _media_key(
        content_sha256=content_sha256,
        source_url="https://www.aemo.com.au/-/media/files/download?rev=1",
        content_type="text/csv; charset=utf-8",
    ).endswith(".csv")
    assert _media_key(
        content_sha256=content_sha256,
        source_url="https://www.aemo.com.au/-/media/files/download",
        content_type="application/json",
    ).endswith(".json")
    assert _media_key(
        content_sha256=content_sha256,
        source_url="https://www.aemo.com.au/-/media/files/download",
        content_type="application/x-not-a-real-content-type",
    ).endswith(".bin")
    assert _media_key(
        content_sha256=content_sha256,
        source_url="https://www.aemo.com.au/-/media/files/download",
        content_type=None,
    ).endswith(".bin")


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
