from collections.abc import Callable
from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError
from dagster import AssetsDefinition, Definitions, MaterializeResult, ScheduleDefinition
from dagster_aws.s3 import S3Resource
from pytest_mock import MockerFixture
from requests import Response
from types_boto3_s3 import S3Client

from aemo_etl.factories.aemo_gas_documents.assets import (
    AEMOGasDocumentSourceWriteResult,
    aemo_gas_document_sources_asset_factory,
)
from aemo_etl.factories.aemo_gas_documents.definitions import (
    aemo_gas_document_sources_definitions_factory,
)
from aemo_etl.factories.aemo_gas_documents.models import AEMOGasDocumentSourcePage

_PAGE_URL = "https://www.aemo.com.au/energy-systems/gas/component"
_PDF_URL = "https://www.aemo.com.au/-/media/files/gas/component-guide.pdf"
_PDF_BYTES = b"%PDF component\n"


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


def test_asset_archives_landed_pdf_only_after_metadata_write(
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
    assert metadata["included_pdf_count"] == 1
    assert metadata["landed_pdf_count"] == 1
    assert metadata["archived_pdf_count"] == 1


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


def test_definitions_factory_default_getter_uses_retrying_request_get(
    mocker: MockerFixture,
) -> None:
    page_url = "https://www.aemo.com.au/energy-systems/gas/default-getter"
    request_get = mocker.patch(
        "aemo_etl.factories.aemo_gas_documents.definitions.request_get",
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


def test_root_defs_registers_aemo_gas_document_job() -> None:
    from aemo_etl.definitions import defs

    result = defs()
    job_names = {job.name for job in result.jobs or []}

    assert "bronze_aemo_gas_document_sources_job" in job_names
