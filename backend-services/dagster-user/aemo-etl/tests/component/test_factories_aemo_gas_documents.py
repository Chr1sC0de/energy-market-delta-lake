from collections.abc import Callable
from datetime import datetime
from unittest.mock import MagicMock

import polars as pl
import pytest
from botocore.exceptions import ClientError
from dagster import AssetsDefinition, Definitions, MaterializeResult, ScheduleDefinition
from dagster_aws.s3 import S3Resource
from pytest_mock import MockerFixture
from requests import RequestException, Response
from types_boto3_s3 import S3Client

from aemo_etl.asset_organization import GAS_AEMO_MAJOR_PUBLICATIONS_GROUP
from aemo_etl.factories.aemo_gas_documents.assets import (
    AEMO_MAJOR_PUBLICATIONS_DOMAIN,
    AEMO_MAJOR_PUBLICATIONS_PREFIX,
    AEMOGasDocumentSourceWriteResult,
    BRONZE_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOADS_TABLE_NAME,
    DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES,
    aemo_gas_document_sources_asset_factory,
)
from aemo_etl.factories.aemo_gas_documents.definitions import (
    aemo_major_publications_hub_downloads_definitions_factory,
    aemo_gas_document_sources_definitions_factory,
)
from aemo_etl.factories.aemo_gas_documents.manifest import (
    load_default_discovery_report_payload,
    load_default_manifest_payload,
)
from aemo_etl.factories.aemo_gas_documents.models import (
    AEMO_GSOO_CORPUS_SOURCE,
    AEMO_GSOO_URL,
    AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
    AEMO_MAJOR_PUBLICATIONS_HUB_URL,
    AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL,
    AEMO_WA_GSOO_CORPUS_SOURCE,
    AEMO_WA_GSOO_URL,
    AEMOGasDocumentPendingObservation,
    AEMOGasDocumentSourcePage,
)
from aemo_etl.factories.aemo_gas_documents.scraper import normalize_source_url

_PAGE_URL = "https://www.aemo.com.au/energy-systems/gas/component"
_PDF_URL = "https://www.aemo.com.au/-/media/files/gas/component-guide.pdf"
_PDF_BYTES = b"%PDF component\n"
_MAJOR_PUBLICATIONS_PDF_URL = (
    "https://www.aemo.com.au/-/media/files/major-publications/"
    "isp/2026-integrated-system-plan.pdf"
)
_MAJOR_PUBLICATIONS_FAILED_PDF_URL = (
    "https://www.aemo.com.au/-/media/files/major-publications/isp/failed-download.pdf"
)
_MAJOR_PUBLICATIONS_REVIEW_PDF_URL = (
    "https://www.aemo.com.au/-/media/files/major-publications/isp/review-needed.pdf"
)


def _response(*, url: str, text: str = "", content: bytes | None = None) -> Response:
    response = Response()
    response.status_code = 200
    response.url = url
    response.headers["Content-Type"] = "application/pdf" if content else "text/html"
    response._content = content if content is not None else text.encode("utf-8")
    response.encoding = "utf-8"
    return response


def _request_getter() -> Callable[[str], Response]:
    html = f"<html><body><h1>Component</h1><a href='{_PDF_URL}'>Component Guide v1.0</a></body></html>"
    responses = {
        _PAGE_URL: _response(url=_PAGE_URL, text=html),
        _PDF_URL: _response(url=_PDF_URL, content=_PDF_BYTES),
    }

    def _get(url: str) -> Response:
        return responses[url]

    return _get


def _major_publications_fixture_observations(
    observed_at: datetime,
) -> tuple[AEMOGasDocumentPendingObservation, ...]:
    return (
        AEMOGasDocumentPendingObservation(
            observation_type="source_page",
            corpus_source=AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
            source_page_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
            source_page_title="Major publications",
            source_page_section="Energy systems major publications",
            source_page_observed_at=observed_at,
            source_link_text=None,
            source_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
            resolved_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
            normalized_source_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
            source_url_query=None,
            document_family_id=None,
            document_title=None,
            document_kind="source_page",
            include_decision="include",
            include_reason="Fixture major-publications source page.",
            exclude_reason=None,
            document_version=None,
            published_date=None,
            effective_date=None,
            media_revision=None,
            should_download=False,
        ),
        AEMOGasDocumentPendingObservation(
            observation_type="link",
            corpus_source=AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
            source_page_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
            source_page_title="Major publications",
            source_page_section="Integrated System Plan",
            source_page_observed_at=observed_at,
            source_link_text="2026 Integrated System Plan",
            source_url=_MAJOR_PUBLICATIONS_PDF_URL,
            resolved_url=_MAJOR_PUBLICATIONS_PDF_URL,
            normalized_source_url=_MAJOR_PUBLICATIONS_PDF_URL,
            source_url_query=None,
            document_family_id="major-publications__2026-integrated-system-plan",
            document_title="2026 Integrated System Plan",
            document_kind="publication",
            include_decision="include",
            include_reason="Fixture downloadable publication.",
            exclude_reason=None,
            document_version=None,
            published_date=None,
            effective_date=None,
            media_revision=None,
            should_download=True,
        ),
        AEMOGasDocumentPendingObservation(
            observation_type="link",
            corpus_source=AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
            source_page_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
            source_page_title="Major publications",
            source_page_section="Integrated System Plan",
            source_page_observed_at=observed_at,
            source_link_text="Failed publication",
            source_url=_MAJOR_PUBLICATIONS_FAILED_PDF_URL,
            resolved_url=_MAJOR_PUBLICATIONS_FAILED_PDF_URL,
            normalized_source_url=_MAJOR_PUBLICATIONS_FAILED_PDF_URL,
            source_url_query=None,
            document_family_id="major-publications__failed-publication",
            document_title="Failed publication",
            document_kind="publication",
            include_decision="include",
            include_reason="Fixture failed publication.",
            exclude_reason=None,
            document_version=None,
            published_date=None,
            effective_date=None,
            media_revision=None,
            should_download=True,
        ),
        AEMOGasDocumentPendingObservation(
            observation_type="link",
            corpus_source=AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
            source_page_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
            source_page_title="Major publications",
            source_page_section="Integrated System Plan",
            source_page_observed_at=observed_at,
            source_link_text="Review-needed publication",
            source_url=_MAJOR_PUBLICATIONS_REVIEW_PDF_URL,
            resolved_url=_MAJOR_PUBLICATIONS_REVIEW_PDF_URL,
            normalized_source_url=_MAJOR_PUBLICATIONS_REVIEW_PDF_URL,
            source_url_query=None,
            document_family_id="major-publications__review-needed-publication",
            document_title="Review-needed publication",
            document_kind="publication",
            include_decision="needs_human_review",
            include_reason="Fixture review-needed publication.",
            exclude_reason=None,
            document_version=None,
            published_date=None,
            effective_date=None,
            media_revision=None,
            should_download=False,
        ),
    )


def _major_publications_request_getter(url: str) -> Response:
    if url == _MAJOR_PUBLICATIONS_FAILED_PDF_URL:
        raise RequestException("fixture download failed")
    if url != _MAJOR_PUBLICATIONS_PDF_URL:
        raise AssertionError(f"unexpected major-publications media request: {url}")
    return _response(url=url, content=_PDF_BYTES)


def _asset_def() -> AssetsDefinition:
    return aemo_gas_document_sources_asset_factory(
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="component",
                source_page_url=_PAGE_URL,
                include_decision="include",
            ),
        ),
        request_getter=_request_getter(),
        landing_bucket="landing",
        archive_bucket="archive",
        aemo_bucket="aemo",
    )


def _context_and_s3(mocker: MockerFixture) -> tuple[MagicMock, MagicMock, MagicMock]:
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    s3_client = mocker.MagicMock(spec=S3Client)
    s3_client.head_object.side_effect = ClientError(
        {"Error": {"Code": "404"}},
        "HeadObject",
    )
    s3 = mocker.MagicMock(spec=S3Resource)
    s3.get_client.return_value = s3_client
    return context, s3, s3_client


def test_asset_archives_landed_media_only_after_metadata_write(
    mocker: MockerFixture,
) -> None:
    events: list[str] = []

    def _write(*_args: object, **_kwargs: object) -> AEMOGasDocumentSourceWriteResult:
        events.append("write")
        return AEMOGasDocumentSourceWriteResult(
            row_count=2,
            target_exists_before_write=False,
            wrote_table=True,
            write_mode="append",
        )

    asset_def = _asset_def()
    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.write_aemo_gas_document_sources_batch",
        side_effect=_write,
    )
    context, s3, s3_client = _context_and_s3(mocker)
    s3_client.upload_fileobj.side_effect = lambda *_args, **_kwargs: events.append(
        "upload"
    )
    s3_client.copy_object.side_effect = lambda **_kwargs: events.append("copy")

    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[attr-defined, union-attr]
    result = fn(context, s3=s3)

    assert isinstance(result, MaterializeResult)
    assert events == ["upload", "write", "copy"]
    s3_client.copy_object.assert_called_once()
    s3_client.delete_object.assert_called_once()
    metadata = result.metadata
    assert metadata is not None
    assert metadata["included_media_count"] == 1
    assert metadata["landed_media_count"] == 1
    assert metadata["archived_media_count"] == 1


def test_asset_leaves_landing_object_when_metadata_write_fails(
    mocker: MockerFixture,
) -> None:
    asset_def = _asset_def()
    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.write_aemo_gas_document_sources_batch",
        side_effect=RuntimeError("write failed"),
    )
    context, s3, s3_client = _context_and_s3(mocker)

    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[attr-defined, union-attr]

    with pytest.raises(RuntimeError, match="write failed"):
        fn(context, s3=s3)

    s3_client.upload_fileobj.assert_called_once()
    s3_client.copy_object.assert_not_called()
    s3_client.delete_object.assert_not_called()


def test_definitions_factory_registers_asset_job_and_schedule() -> None:
    defs = aemo_gas_document_sources_definitions_factory(
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="component",
                source_page_url="scope://component",
                include_decision="exclude",
                fetch_links=False,
            ),
        ),
        request_getter=_request_getter(),
        cron_schedule="0 4 * * *",
    )

    assert isinstance(defs, Definitions)
    assets = [
        asset for asset in defs.assets or [] if isinstance(asset, AssetsDefinition)
    ]
    schedules = [
        schedule
        for schedule in defs.schedules or []
        if isinstance(schedule, ScheduleDefinition)
    ]
    assert [asset.key.path for asset in assets] == [
        [
            "bronze",
            "aemo_gas_documents",
            "bronze_aemo_gas_document_sources",
        ]
    ]
    assert [job.name for job in defs.jobs or []] == [
        "bronze_aemo_gas_document_sources_job"
    ]
    assert [schedule.cron_schedule for schedule in schedules] == ["0 4 * * *"]


def test_major_publications_definitions_register_asset_job_and_materialize_fixture_observations(
    mocker: MockerFixture,
) -> None:
    events: list[str] = []
    captured_target_table_uris: list[str] = []
    captured_rows: list[dict[str, object]] = []

    def _write(
        batch: pl.LazyFrame,
        *,
        target_table_uri: str,
        **_kwargs: object,
    ) -> AEMOGasDocumentSourceWriteResult:
        events.append("write")
        captured_target_table_uris.append(target_table_uri)
        captured_rows.extend(batch.collect().to_dicts())
        return AEMOGasDocumentSourceWriteResult(
            row_count=len(captured_rows),
            target_exists_before_write=True,
            wrote_table=True,
            write_mode="merge",
        )

    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.write_aemo_gas_document_sources_batch",
        side_effect=_write,
    )
    defs = aemo_major_publications_hub_downloads_definitions_factory(
        observation_loader=_major_publications_fixture_observations,
        request_getter=_major_publications_request_getter,
        cron_schedule="30 4 * * *",
        landing_bucket="landing",
        archive_bucket="archive",
        aemo_bucket="aemo",
        process_retry=1,
    )
    assets = [
        asset for asset in defs.assets or [] if isinstance(asset, AssetsDefinition)
    ]
    schedules = [
        schedule
        for schedule in defs.schedules or []
        if isinstance(schedule, ScheduleDefinition)
    ]
    asset_def = assets[0]
    asset_key = asset_def.key

    assert asset_key.path == [
        "bronze",
        AEMO_MAJOR_PUBLICATIONS_DOMAIN,
        BRONZE_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOADS_TABLE_NAME,
    ]
    assert asset_def.group_names_by_key[asset_key] == GAS_AEMO_MAJOR_PUBLICATIONS_GROUP
    assert asset_def.metadata_by_key[asset_key]["source_family"] == (
        AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE
    )
    assert asset_def.metadata_by_key[asset_key]["target_table_uri"] == (
        "s3://aemo/bronze/aemo_major_publications/"
        "bronze_aemo_major_publications_hub_downloads"
    )
    assert [job.name for job in defs.jobs or []] == [
        "bronze_aemo_major_publications_hub_downloads_job"
    ]
    assert [schedule.cron_schedule for schedule in schedules] == ["30 4 * * *"]

    context, s3, s3_client = _context_and_s3(mocker)
    s3_client.upload_fileobj.side_effect = lambda *_args, **_kwargs: events.append(
        "upload"
    )
    s3_client.copy_object.side_effect = lambda **_kwargs: events.append("copy")

    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[attr-defined, union-attr]
    result = fn(context, s3=s3)

    assert isinstance(result, MaterializeResult)
    assert events == ["upload", "write", "copy"]
    assert captured_target_table_uris == [
        "s3://aemo/bronze/aemo_major_publications/"
        "bronze_aemo_major_publications_hub_downloads"
    ]
    assert {row["source_url"] for row in captured_rows} == {
        AEMO_MAJOR_PUBLICATIONS_HUB_URL,
        _MAJOR_PUBLICATIONS_PDF_URL,
        _MAJOR_PUBLICATIONS_FAILED_PDF_URL,
        _MAJOR_PUBLICATIONS_REVIEW_PDF_URL,
    }
    assert result.metadata is not None
    assert result.metadata["target_table_uri"] == captured_target_table_uris[0]
    assert result.metadata["storage_uri"] == captured_target_table_uris[0]
    assert result.metadata["s3_landing_root"] == (
        f"s3://landing/{AEMO_MAJOR_PUBLICATIONS_PREFIX}"
    )
    assert result.metadata["s3_archive_root"] == (
        f"s3://archive/{AEMO_MAJOR_PUBLICATIONS_PREFIX}"
    )
    assert result.metadata["source_page_count"] == 1
    assert result.metadata["included_download_count"] == 1
    assert result.metadata["failed_count"] == 1
    assert result.metadata["review_needed_count"] == 1
    assert result.metadata["included_media_count"] == 1
    assert result.metadata["failed_download_count"] == 1
    assert result.metadata["needs_human_review_observation_count"] == 1
    assert result.metadata["landed_media_count"] == 1
    assert result.metadata["archived_media_count"] == 1


def test_major_publications_default_sources_retain_hub_and_library_rows(
    mocker: MockerFixture,
) -> None:
    hub_media_url = (
        "https://www.aemo.com.au/-/media/files/major-publications/isp/report.pdf"
        "?rev=ABC&sc_lang=en"
    )
    library_media_url = (
        "https://www.aemo.com.au/-/MEDIA/files/major-publications/isp/report.pdf"
        "?sc_lang=en&rev=ABC"
    )
    html_by_url = {
        AEMO_MAJOR_PUBLICATIONS_HUB_URL: f"""
        <html><body>
          <h1>Major publications</h1>
          <a href="{hub_media_url}">Shared publication</a>
        </body></html>
        """,
        AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL: f"""
        <html><body>
          <h1>Major publications library</h1>
          <a href="{library_media_url}">Shared publication in library</a>
        </body></html>
        """,
        AEMO_GSOO_URL: "<html><body><h1>GSOO</h1></body></html>",
        AEMO_WA_GSOO_URL: "<html><body><h1>WA GSOO</h1></body></html>",
    }
    requested_media_urls: list[str] = []
    captured_rows: list[dict[str, object]] = []

    def _get(url: str) -> Response:
        if url in html_by_url:
            return _response(url=url, text=html_by_url[url])
        requested_media_urls.append(url)
        if url == hub_media_url:
            return _response(url=url, content=_PDF_BYTES)
        raise AssertionError(f"unexpected media request: {url}")

    def _write(
        batch: pl.LazyFrame, **_kwargs: object
    ) -> AEMOGasDocumentSourceWriteResult:
        captured_rows.extend(batch.collect().to_dicts())
        return AEMOGasDocumentSourceWriteResult(
            row_count=len(captured_rows),
            target_exists_before_write=True,
            wrote_table=True,
            write_mode="merge",
        )

    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.write_aemo_gas_document_sources_batch",
        side_effect=_write,
    )
    defs = aemo_major_publications_hub_downloads_definitions_factory(
        request_getter=_get,
        landing_bucket="landing",
        archive_bucket="archive",
        aemo_bucket="aemo",
        process_retry=1,
    )
    asset_def = next(
        asset for asset in defs.assets or [] if isinstance(asset, AssetsDefinition)
    )
    asset_key = asset_def.key
    context, s3, s3_client = _context_and_s3(mocker)

    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[attr-defined, union-attr]
    result = fn(context, s3=s3)

    media_rows = [row for row in captured_rows if row["content_sha256"] is not None]

    assert isinstance(result, MaterializeResult)
    assert asset_def.metadata_by_key[asset_key]["configured_source_page_count"] == 4
    assert requested_media_urls == [hub_media_url]
    assert result.metadata is not None
    assert result.metadata["source_page_count"] == 4
    assert result.metadata["included_media_count"] == 2
    assert result.metadata["landed_media_count"] == 1
    assert result.metadata["archived_media_count"] == 1
    assert {
        row["source_url"]
        for row in captured_rows
        if row["observation_type"] == "source_page"
    } == {
        AEMO_MAJOR_PUBLICATIONS_HUB_URL,
        AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL,
        AEMO_GSOO_URL,
        AEMO_WA_GSOO_URL,
    }
    assert {row["source_page_url"] for row in media_rows} == {
        AEMO_MAJOR_PUBLICATIONS_HUB_URL,
        AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL,
    }
    assert {row["source_url"] for row in media_rows} == {
        hub_media_url,
        library_media_url,
    }
    assert len({row["target_s3_key"] for row in media_rows}) == 1
    s3_client.upload_fileobj.assert_called_once()
    s3_client.copy_object.assert_called_once()


def test_major_publications_defaults_materialize_gsoo_and_wa_gsoo_bundle_media(
    mocker: MockerFixture,
) -> None:
    gsoo_child_url = f"{AEMO_GSOO_URL}/2025-gas-statement-of-opportunities"
    gsoo_report_url = (
        "https://www.aemo.com.au/-/media/files/gas/national-planning-and-"
        "forecasting/gsoo/2026/2026-gas-statement-of-opportunities.pdf"
    )
    gsoo_data_url = (
        "https://www.aemo.com.au/-/media/files/gas/national-planning-and-"
        "forecasting/gsoo/2026/2026-gsoo-report-figures-and-data.xlsx"
    )
    gsoo_child_report_url = (
        "https://www.aemo.com.au/-/media/files/gas/national-planning-and-"
        "forecasting/gsoo/2025/2025-gas-statement-of-opportunities.pdf"
    )
    wa_report_url = (
        "https://www.aemo.com.au/-/media/files/gas/wa-gsoo/2025/"
        "2025-wa-gas-statement-of-opportunities.pdf"
    )
    media_urls = {
        gsoo_report_url,
        gsoo_data_url,
        gsoo_child_report_url,
        wa_report_url,
    }
    html_by_url = {
        AEMO_MAJOR_PUBLICATIONS_HUB_URL: """
        <html><body><h1>Major publications</h1></body></html>
        """,
        AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL: """
        <html><body><h1>Major publications library</h1></body></html>
        """,
        AEMO_GSOO_URL: f"""
        <html>
          <body>
            <h1>Gas Statement of Opportunities</h1>
            <a href="{gsoo_report_url}">2026 Gas Statement of Opportunities</a>
            <a href="{gsoo_data_url}">2026 GSOO report figures and data</a>
            <a href="{gsoo_child_url}">2025 Gas Statement of Opportunities</a>
          </body>
        </html>
        """,
        AEMO_WA_GSOO_URL: f"""
        <html>
          <body>
            <h1>WA Gas Statement of Opportunities</h1>
            <a href="{wa_report_url}">2025 WA Gas Statement of Opportunities</a>
          </body>
        </html>
        """,
        gsoo_child_url: f"""
        <html>
          <body>
            <h1>2025 Gas Statement of Opportunities</h1>
            <a href="{gsoo_child_report_url}">2025 Gas Statement of Opportunities</a>
          </body>
        </html>
        """,
    }
    requested_pages: list[str] = []
    requested_media: list[str] = []
    captured_rows: list[dict[str, object]] = []

    def _get(url: str) -> Response:
        if url in html_by_url:
            requested_pages.append(url)
            return _response(url=url, text=html_by_url[url])
        if url in media_urls:
            requested_media.append(url)
            return _response(url=url, content=f"fixture media: {url}".encode())
        raise AssertionError(f"unexpected GSOO bundle request: {url}")

    def _write(
        batch: pl.LazyFrame,
        *,
        target_table_uri: str,
        **_kwargs: object,
    ) -> AEMOGasDocumentSourceWriteResult:
        captured_rows.extend(batch.collect().to_dicts())
        assert target_table_uri == (
            "s3://aemo/bronze/aemo_major_publications/"
            "bronze_aemo_major_publications_hub_downloads"
        )
        return AEMOGasDocumentSourceWriteResult(
            row_count=len(captured_rows),
            target_exists_before_write=True,
            wrote_table=True,
            write_mode="merge",
        )

    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.write_aemo_gas_document_sources_batch",
        side_effect=_write,
    )
    defs = aemo_major_publications_hub_downloads_definitions_factory(
        request_getter=_get,
        landing_bucket="landing",
        archive_bucket="archive",
        aemo_bucket="aemo",
        process_retry=1,
    )
    asset_def = next(
        asset for asset in defs.assets or [] if isinstance(asset, AssetsDefinition)
    )
    asset_key = asset_def.key
    context, s3, s3_client = _context_and_s3(mocker)

    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[attr-defined, union-attr]
    result = fn(context, s3=s3)

    downloaded_rows = [row for row in captured_rows if row["source_url"] in media_urls]

    assert isinstance(result, MaterializeResult)
    assert asset_def.metadata_by_key[asset_key]["configured_source_page_count"] == 4
    assert requested_pages == [
        AEMO_MAJOR_PUBLICATIONS_HUB_URL,
        AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL,
        AEMO_GSOO_URL,
        AEMO_WA_GSOO_URL,
        gsoo_child_url,
    ]
    assert set(requested_media) == media_urls
    assert {row["corpus_source"] for row in downloaded_rows} == {
        AEMO_GSOO_CORPUS_SOURCE,
        AEMO_WA_GSOO_CORPUS_SOURCE,
    }
    assert all(
        str(row["target_s3_key"]).startswith(AEMO_MAJOR_PUBLICATIONS_PREFIX)
        for row in downloaded_rows
    )
    assert result.metadata is not None
    assert result.metadata["source_page_count"] == 5
    assert result.metadata["included_media_count"] == len(media_urls)
    assert result.metadata["landed_media_count"] == len(media_urls)
    assert result.metadata["archived_media_count"] == len(media_urls)
    assert s3_client.upload_fileobj.call_count == len(media_urls)
    assert s3_client.copy_object.call_count == len(media_urls)
    assert len(DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES) == 4


def test_definitions_factory_default_getter_uses_retrying_request_get(
    mocker: MockerFixture,
) -> None:
    page_url = "https://www.aemo.com.au/energy-systems/gas/default-getter"
    request_get = mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.definitions.request_get_aemo_gas_document",
        return_value=_response(
            url=page_url,
            text="<html><body><h1>Default getter</h1></body></html>",
        ),
    )
    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.write_aemo_gas_document_sources_batch",
        return_value=AEMOGasDocumentSourceWriteResult(
            row_count=1,
            target_exists_before_write=True,
            wrote_table=False,
            write_mode="skip",
        ),
    )
    defs = aemo_gas_document_sources_definitions_factory(
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="component",
                source_page_url=page_url,
                include_decision="include",
            ),
        ),
        process_retry=1,
    )
    asset_def = next(
        asset for asset in defs.assets or [] if isinstance(asset, AssetsDefinition)
    )
    context, s3, s3_client = _context_and_s3(mocker)

    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[attr-defined, union-attr]
    result = fn(context, s3=s3)

    assert isinstance(result, MaterializeResult)
    request_get.assert_called_once_with(page_url)
    s3_client.copy_object.assert_not_called()


def test_asset_discovers_major_publications_hub_observations_without_landing(
    mocker: MockerFixture,
) -> None:
    child_url = f"{AEMO_MAJOR_PUBLICATIONS_HUB_URL}integrated-system-plan-isp"
    hub_media_url = (
        "https://www.aemo.com.au/-/media/files/major-publications/"
        "isp/2026-integrated-system-plan.pdf?rev=HUB"
    )
    child_media_url = (
        "https://www.aemo.com.au/-/media/files/major-publications/"
        "isp/2026-integrated-system-plan-appendix.pdf?rev=CHILD"
    )
    html_by_url = {
        AEMO_MAJOR_PUBLICATIONS_HUB_URL: f"""
        <html>
          <head>
            <link rel="stylesheet" href="/assets/site.css">
            <script src="/assets/site.js"></script>
          </head>
          <body>
            <h1>Major publications</h1>
            <a href="/energy-systems/electricity">Electricity navigation</a>
            <a href="{child_url}">Integrated System Plan</a>
            <a href="{child_url}">Integrated System Plan</a>
            <a href="{hub_media_url}">2026 Integrated System Plan</a>
          </body>
        </html>
        """,
        child_url: f"""
        <html>
          <body>
            <h1>Integrated System Plan</h1>
            <a href="{child_media_url}">2026 ISP Appendix</a>
            <a href="https://example.com/isp.pdf">External report</a>
          </body>
        </html>
        """,
    }
    captured_rows: list[dict[str, object]] = []

    def _write(
        batch: pl.LazyFrame, **_kwargs: object
    ) -> AEMOGasDocumentSourceWriteResult:
        captured_rows.extend(batch.collect().to_dicts())
        return AEMOGasDocumentSourceWriteResult(
            row_count=len(captured_rows),
            target_exists_before_write=True,
            wrote_table=False,
            write_mode="skip",
        )

    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.write_aemo_gas_document_sources_batch",
        side_effect=_write,
    )
    asset_def = aemo_gas_document_sources_asset_factory(
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source=AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
                source_page_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
                include_decision="needs_human_review",
                include_reason="Observation-only major publications test scope.",
                discover_child_pages=True,
            ),
        ),
        request_getter=lambda url: _response(url=url, text=html_by_url[url]),
        landing_bucket="landing",
        archive_bucket="archive",
        aemo_bucket="aemo",
    )
    context, s3, s3_client = _context_and_s3(mocker)

    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[attr-defined, union-attr]
    result = fn(context, s3=s3)

    assert isinstance(result, MaterializeResult)
    assert result.metadata is not None
    assert result.metadata["included_media_count"] == 0
    assert result.metadata["landed_media_count"] == 0
    assert result.metadata["needs_human_review_observation_count"] == 6
    assert result.metadata["excluded_observation_count"] == 1
    assert {row["source_url"] for row in captured_rows} == {
        AEMO_MAJOR_PUBLICATIONS_HUB_URL,
        child_url,
        "https://www.aemo.com.au/energy-systems/electricity",
        hub_media_url,
        child_media_url,
        "https://example.com/isp.pdf",
    }
    assert all(row["content_sha256"] is None for row in captured_rows)
    s3_client.upload_fileobj.assert_not_called()


def test_definitions_factory_default_asset_uses_packaged_manifest_media_only(
    mocker: MockerFixture,
) -> None:
    manifest = load_default_manifest_payload()
    report = load_default_discovery_report_payload()
    failed_urls = {
        validation["source_url"]
        for validation in report["media_validations"]
        if validation["ok"] is False
    }
    failed_indexes = [
        index
        for index, media_link in enumerate(manifest["media_links"])
        if media_link["source_url"] in failed_urls
        and media_link["should_download"] is False
    ]
    downloadable_urls = [
        str(media_link["source_url"])
        for media_link in manifest["media_links"]
        if media_link["should_download"] is True
    ]
    downloadable_normalized_urls = {
        normalize_source_url(source_url)[0] for source_url in downloadable_urls
    }
    later_downloadable_url = next(
        media_link["source_url"]
        for index, media_link in enumerate(manifest["media_links"])
        if failed_indexes
        and index > failed_indexes[0]
        and media_link["should_download"] is True
    )
    requested_urls: list[str] = []

    def _get(url: str) -> Response:
        requested_urls.append(url)
        if not url.startswith("https://www.aemo.com.au/-/media/"):
            raise AssertionError(f"unexpected source-page request: {url}")
        if url in failed_urls:
            raise AssertionError(f"unexpected failed media request: {url}")
        return _response(url=url, content=_PDF_BYTES)

    mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.assets.write_aemo_gas_document_sources_batch",
        return_value=AEMOGasDocumentSourceWriteResult(
            row_count=2,
            target_exists_before_write=True,
            wrote_table=False,
            write_mode="skip",
        ),
    )
    defs = aemo_gas_document_sources_definitions_factory(
        request_getter=_get,
        process_retry=1,
    )
    asset_def = next(
        asset for asset in defs.assets or [] if isinstance(asset, AssetsDefinition)
    )
    context, s3, s3_client = _context_and_s3(mocker)

    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[attr-defined, union-attr]
    result = fn(context, s3=s3)

    assert isinstance(result, MaterializeResult)
    assert failed_indexes
    assert requested_urls
    assert later_downloadable_url in requested_urls
    assert result.metadata is not None
    assert result.metadata["included_media_count"] == len(downloadable_urls)
    assert len(requested_urls) == len(downloadable_normalized_urls)
    s3_client.copy_object.assert_not_called()


def test_root_defs_registers_aemo_gas_document_job() -> None:
    from aemo_etl.definitions import defs

    result = defs()
    job_names = {job.name for job in result.jobs or []}

    assert "bronze_aemo_gas_document_sources_job" in job_names
    assert "bronze_aemo_major_publications_hub_downloads_job" in job_names
