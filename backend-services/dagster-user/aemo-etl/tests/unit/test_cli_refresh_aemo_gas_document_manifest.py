import argparse
import subprocess
import sys
import types
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from requests import HTTPError, Response

import aemo_etl.cli.refresh_aemo_gas_document_manifest as cli
from aemo_etl.cli.refresh_aemo_gas_document_manifest import (
    _stage_and_commit_generated_files,
    discover_manifest_payloads,
    refresh_aemo_gas_document_media_manifest,
    validate_media_url,
)
from aemo_etl.factories.aemo_gas_documents.assets import (
    AEMO_GAS_DOCUMENT_REQUEST_HEADERS,
)
from aemo_etl.factories.aemo_gas_documents.models import (
    AEMOGasDocumentMediaValidation,
    AEMOGasDocumentSourcePage,
)

_GENERATED_AT = datetime(2026, 5, 11, 1, 2, 3, tzinfo=UTC)
_PAGE_URL = "https://www.aemo.com.au/energy-systems/gas/playwright"
_PDF_URL = "https://www.aemo.com.au/-/media/files/gas/playwright-guide.pdf?rev=ABC"


def _response(
    *,
    url: str,
    status_code: int = 200,
    headers: dict[str, str] | None = None,
) -> Response:
    response = Response()
    response.status_code = status_code
    response.url = url
    response.headers.update(headers or {})
    response.raw = BytesIO()
    response._content = b""
    return response


def _source_page() -> AEMOGasDocumentSourcePage:
    return AEMOGasDocumentSourcePage(
        corpus_source="playwright",
        source_page_url=_PAGE_URL,
        include_decision="include",
        include_reason="Included for test",
    )


def _validation(source_url: str) -> AEMOGasDocumentMediaValidation:
    return AEMOGasDocumentMediaValidation(
        source_url=source_url,
        ok=True,
        status_code=200,
        resolved_url=f"{source_url}&download=1",
        content_type="application/pdf",
        content_length=1234,
        error=None,
    )


def test_discover_manifest_payloads_extracts_public_aemo_media_links() -> None:
    html = f"""
    <html>
      <body>
        <h1>Playwright Page</h1>
        <h2>Guides</h2>
        <a href="{_PDF_URL}">1 May 2026 Playwright Guide v1.2</a>
        <a href="https://example.com/-/media/files/external.pdf">External</a>
        <a href="/energy-systems/gas/playwright/child">Child page</a>
      </body>
    </html>
    """

    manifest, report = discover_manifest_payloads(
        source_pages=(_source_page(), _source_page()),
        page_loader=lambda _source_page: html,
        media_validator=_validation,
        generated_at=_GENERATED_AT,
        existing_payload={"schema_version": 1, "source_pages": [], "media_links": []},
    )

    assert manifest["media_link_count"] == 1
    media_link = manifest["media_links"][0]
    assert media_link["source_url"] == _PDF_URL
    assert media_link["resolved_url"] == f"{_PDF_URL}&download=1"
    assert media_link["source_page_title"] == "Playwright Page"
    assert media_link["source_page_section"] == "Guides"
    assert media_link["include_decision"] == "include"
    assert media_link["media_revision"] == "ABC"
    assert media_link["should_download"] is True
    assert report["media_validations"] == [
        {
            "content_length": 1234,
            "content_type": "application/pdf",
            "ok": True,
            "resolved_url": f"{_PDF_URL}&download=1",
            "source_url": _PDF_URL,
            "status": "ok",
            "status_code": 200,
        }
    ]


def test_discover_manifest_payloads_discovers_child_pages_and_failed_validations() -> (
    None
):
    parent = AEMOGasDocumentSourcePage(
        corpus_source="playwright",
        source_page_url=_PAGE_URL,
        include_decision="include",
        discover_child_pages=True,
    )
    child_url = f"{_PAGE_URL}/child"
    child_pdf_url = "https://www.aemo.com.au/-/media/files/gas/child-guide.pdf"
    html_by_url = {
        _PAGE_URL: f"""
        <html><body>
          <a href="{child_url}">Child</a>
        </body></html>
        """,
        child_url: f"""
        <html><body>
          <a href="{child_pdf_url}">Child Guide</a>
        </body></html>
        """,
    }

    def _failed_validation(source_url: str) -> AEMOGasDocumentMediaValidation:
        return AEMOGasDocumentMediaValidation(
            source_url=source_url,
            ok=False,
            status_code=500,
            resolved_url=f"{source_url}?blocked=1",
            content_type="text/html",
            content_length=None,
            error="blocked",
        )

    manifest, report = discover_manifest_payloads(
        source_pages=(parent,),
        page_loader=lambda source_page: html_by_url[source_page.source_page_url],
        media_validator=_failed_validation,
        generated_at=_GENERATED_AT,
        existing_payload={"schema_version": 1, "source_pages": [], "media_links": []},
    )

    assert manifest["source_page_count"] == 2
    assert manifest["media_link_count"] == 1
    assert manifest["media_links"][0]["source_page_url"] == child_url
    assert manifest["media_links"][0]["resolved_url"] == f"{child_pdf_url}?blocked=1"
    assert manifest["media_links"][0]["should_download"] is False
    assert report["media_validations"][0]["error"] == "blocked"
    assert report["media_validations"][0]["status"] == "failed"


def test_blocked_source_page_preserves_existing_manifest_entries() -> None:
    existing_payload = {
        "schema_version": 1,
        "source_pages": [
            {
                "corpus_source": "playwright",
                "source_page_url": _PAGE_URL,
                "include_decision": "include",
                "status": "previous",
            }
        ],
        "media_links": [
            {
                "corpus_source": "playwright",
                "source_page_url": _PAGE_URL,
                "source_url": _PDF_URL,
                "include_decision": "include",
            }
        ],
    }

    manifest, report = discover_manifest_payloads(
        source_pages=(_source_page(),),
        page_loader=lambda _source_page: (_ for _ in ()).throw(RuntimeError("blocked")),
        media_validator=_validation,
        generated_at=_GENERATED_AT,
        existing_payload=existing_payload,
    )

    assert manifest["source_pages"] == existing_payload["source_pages"]
    assert manifest["media_links"] == existing_payload["media_links"]
    assert report["source_pages"][0]["status"] == "source_page_failed"
    assert report["source_pages"][0]["preserved_media_link_count"] == 1
    assert report["source_pages"][0]["error"] == "blocked"


def test_cloudflare_challenge_page_preserves_existing_manifest_entries() -> None:
    existing_payload = {
        "schema_version": 1,
        "source_pages": [
            {
                "corpus_source": "playwright",
                "source_page_url": _PAGE_URL,
                "include_decision": "include",
                "status": "previous",
            }
        ],
        "media_links": [
            {
                "corpus_source": "playwright",
                "source_page_url": _PAGE_URL,
                "source_url": _PDF_URL,
                "include_decision": "include",
            }
        ],
    }
    html = """
    <html>
      <head>
        <title>Just a moment...</title>
        <script src="https://challenges.cloudflare.com/turnstile/v0/api.js"></script>
      </head>
      <body></body>
    </html>
    """

    manifest, report = discover_manifest_payloads(
        source_pages=(_source_page(),),
        page_loader=lambda _source_page: html,
        media_validator=_validation,
        generated_at=_GENERATED_AT,
        existing_payload=existing_payload,
    )

    assert manifest["source_pages"] == existing_payload["source_pages"]
    assert manifest["media_links"] == existing_payload["media_links"]
    assert report["source_pages"][0]["status"] == "source_page_failed"
    assert "Cloudflare challenge" in report["source_pages"][0]["error"]


def test_playwright_page_loader_uses_chromium_page_content(
    mocker: MockerFixture,
) -> None:
    page = mocker.MagicMock()
    page.content.return_value = "<html>loaded</html>"
    browser = mocker.MagicMock()
    browser.new_page.return_value = page
    chromium = mocker.MagicMock()
    chromium.launch.return_value = browser
    playwright = mocker.MagicMock()
    playwright.chromium = chromium
    manager = mocker.MagicMock()
    manager.start.return_value = playwright
    sync_api = types.ModuleType("playwright.sync_api")
    sync_api.sync_playwright = lambda: manager  # type: ignore[attr-defined]
    mocker.patch.dict(
        sys.modules,
        {
            "playwright": types.ModuleType("playwright"),
            "playwright.sync_api": sync_api,
        },
    )

    with cli.PlaywrightPageLoader(timeout_ms=123) as loader:
        assert loader(_source_page()) == "<html>loaded</html>"

    page.goto.assert_called_once_with(
        _PAGE_URL,
        wait_until="domcontentloaded",
        timeout=123,
    )
    page.close.assert_called_once_with()
    browser.close.assert_called_once_with()
    playwright.stop.assert_called_once_with()


def test_playwright_page_loader_requires_context_manager() -> None:
    loader = cli.PlaywrightPageLoader(timeout_ms=123)

    with pytest.raises(RuntimeError, match="context manager"):
        loader(_source_page())


def test_validate_media_url_records_http_metadata_and_errors() -> None:
    response = _response(
        url=f"{_PDF_URL}&resolved=1",
        status_code=403,
        headers={"Content-Type": "text/html", "Content-Length": "99"},
    )

    def _get(_source_url: str, _timeout: float) -> Response:
        response.reason = "Forbidden"
        raise_error = HTTPError("403 Client Error")
        response.raise_for_status = lambda: (_ for _ in ()).throw(raise_error)  # type: ignore[method-assign]
        return response

    validation = validate_media_url(_PDF_URL, request_getter=_get)

    assert validation.ok is False
    assert validation.status_code == 403
    assert validation.resolved_url == f"{_PDF_URL}&resolved=1"
    assert validation.content_type == "text/html"
    assert validation.content_length == 99
    assert validation.error == "403 Client Error"


def test_validate_media_url_uses_default_streaming_getter(
    mocker: MockerFixture,
) -> None:
    response = _response(
        url=f"{_PDF_URL}&resolved=1",
        headers={"Content-Type": "application/pdf", "Content-Length": "42"},
    )
    get = mocker.patch(
        "aemo_etl.cli.refresh_aemo_gas_document_manifest.requests.get",
        return_value=response,
    )

    validation = validate_media_url(_PDF_URL, request_timeout=4.5)

    get.assert_called_once_with(
        _PDF_URL,
        headers=AEMO_GAS_DOCUMENT_REQUEST_HEADERS,
        timeout=4.5,
        stream=True,
    )
    assert validation.ok is True
    assert validation.status_code == 200
    assert validation.content_length == 42


def test_validate_media_url_records_request_errors_without_response() -> None:
    validation = validate_media_url(
        _PDF_URL,
        request_getter=lambda _source_url, _timeout: (_ for _ in ()).throw(
            RuntimeError("network unavailable")
        ),
    )

    assert validation.ok is False
    assert validation.status_code is None
    assert validation.resolved_url == _PDF_URL
    assert validation.error == "network unavailable"


def test_main_success_and_error_paths(
    tmp_path: Path,
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
) -> None:
    class _FakeLoader:
        def __init__(self, *, timeout_ms: int) -> None:
            self.timeout_ms = timeout_ms

        def __enter__(self) -> cli.PageLoader:
            return lambda _source_page: ""

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc_value: BaseException | None,
            traceback: object | None,
        ) -> None:
            return None

    mocker.patch.object(cli, "PlaywrightPageLoader", _FakeLoader)
    refresh = mocker.patch.object(
        cli,
        "refresh_aemo_gas_document_media_manifest",
        return_value=cli.RefreshResult(
            manifest_path=tmp_path / "manifest.json",
            report_path=tmp_path / "report.json",
            manifest_changed=True,
            report_changed=True,
            committed=False,
            media_link_count=1,
            media_validation_count=1,
        ),
    )

    assert cli.main(["--no-commit", "--timeout-ms", "123"]) == 0

    assert "generated files written" in capsys.readouterr().out
    assert refresh.call_args.kwargs["commit"] is False

    refresh.side_effect = ValueError("bad input")
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--no-commit"])
    assert exit_info.value.code == 2

    refresh.side_effect = RuntimeError("unexpected")
    assert cli.main(["--no-commit"]) == 1
    assert "unexpected" in capsys.readouterr().err


def test_parser_helpers_reject_non_positive_values() -> None:
    assert cli.default_manifest_path().name == "aemo_gas_document_media_manifest.json"
    assert (
        cli.default_report_path().name
        == "aemo_gas_document_media_discovery_report.json"
    )
    assert cli.build_parser().parse_args(["--timeout-ms", "5"]).timeout_ms == 5
    assert cli._positive_float("1.5") == 1.5
    with pytest.raises(argparse.ArgumentTypeError):
        cli._positive_int("0")
    with pytest.raises(argparse.ArgumentTypeError):
        cli._positive_float("-1")


def test_media_validator_for_timeout_passes_timeout(
    mocker: MockerFixture,
) -> None:
    validate = mocker.patch.object(
        cli,
        "validate_media_url",
        return_value=_validation(_PDF_URL),
    )

    validation = cli._media_validator_for_timeout(12.5)(_PDF_URL)

    assert validation.source_url == _PDF_URL
    validate.assert_called_once_with(_PDF_URL, request_timeout=12.5)


def test_refresh_commits_generated_files_by_default(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    commit = mocker.patch(
        "aemo_etl.cli.refresh_aemo_gas_document_manifest._stage_and_commit_generated_files",
        return_value=True,
    )

    result = refresh_aemo_gas_document_media_manifest(
        manifest_path=tmp_path / "manifest.json",
        report_path=tmp_path / "report.json",
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="skip",
                source_page_url="scope://skip",
                include_decision="exclude",
                fetch_links=False,
            ),
        ),
        page_loader=lambda _source_page: "",
        media_validator=_validation,
        commit=True,
        generated_at=_GENERATED_AT,
    )

    assert result.committed is True
    commit.assert_called_once_with(
        (tmp_path / "manifest.json", tmp_path / "report.json"),
        commit_message="Refresh AEMO gas document media manifest",
    )


def test_no_commit_writes_files_without_staging(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    commit = mocker.patch(
        "aemo_etl.cli.refresh_aemo_gas_document_manifest._stage_and_commit_generated_files",
        return_value=True,
    )

    result = refresh_aemo_gas_document_media_manifest(
        manifest_path=tmp_path / "manifest.json",
        report_path=tmp_path / "report.json",
        source_pages=(
            AEMOGasDocumentSourcePage(
                corpus_source="skip",
                source_page_url="scope://skip",
                include_decision="exclude",
                fetch_links=False,
            ),
        ),
        page_loader=lambda _source_page: "",
        media_validator=_validation,
        commit=False,
        generated_at=_GENERATED_AT,
    )

    assert result.manifest_changed is True
    assert result.report_changed is True
    assert result.committed is False
    commit.assert_not_called()


def test_stage_and_commit_uses_generated_file_pathspecs(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    commands: list[list[str]] = []

    def _run(
        cmd: list[str],
        *,
        check: bool,
        capture_output: bool,
        text: bool,
        cwd: Path,
    ) -> subprocess.CompletedProcess[str]:
        assert check is True
        assert capture_output is True
        assert text is True
        commands.append(cmd)
        if cmd[1:3] == ["rev-parse", "--show-toplevel"]:
            return subprocess.CompletedProcess(cmd, 0, stdout=str(tmp_path), stderr="")
        if cmd[1] == "status":
            return subprocess.CompletedProcess(
                cmd, 0, stdout="M manifest.json\n", stderr=""
            )
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    mocker.patch("subprocess.run", side_effect=_run)

    committed = _stage_and_commit_generated_files(
        (tmp_path / "manifest.json", tmp_path / "report.json"),
        commit_message="Refresh test",
    )

    assert committed is True
    assert commands[1] == ["git", "add", "--", "manifest.json", "report.json"]
    assert commands[3] == [
        "git",
        "commit",
        "-m",
        "Refresh test",
        "--",
        "manifest.json",
        "report.json",
    ]


def test_stage_and_commit_skips_empty_generated_diff(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    def _run(
        cmd: list[str],
        *,
        check: bool,
        capture_output: bool,
        text: bool,
        cwd: Path,
    ) -> subprocess.CompletedProcess[str]:
        if cmd[1:3] == ["rev-parse", "--show-toplevel"]:
            return subprocess.CompletedProcess(cmd, 0, stdout=str(tmp_path), stderr="")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    mocker.patch("subprocess.run", side_effect=_run)

    assert (
        _stage_and_commit_generated_files(
            (tmp_path / "manifest.json", tmp_path / "report.json"),
            commit_message="Refresh test",
        )
        is False
    )


def test_refresh_reports_unchanged_files_without_commit(
    tmp_path: Path,
    mocker: MockerFixture,
) -> None:
    result = refresh_aemo_gas_document_media_manifest(
        manifest_path=tmp_path / "manifest.json",
        report_path=tmp_path / "report.json",
        source_pages=(),
        page_loader=lambda _source_page: "",
        media_validator=_validation,
        commit=False,
        generated_at=_GENERATED_AT,
    )
    commit = mocker.patch(
        "aemo_etl.cli.refresh_aemo_gas_document_manifest._stage_and_commit_generated_files",
        return_value=True,
    )

    second_result = refresh_aemo_gas_document_media_manifest(
        manifest_path=result.manifest_path,
        report_path=result.report_path,
        source_pages=(),
        page_loader=lambda _source_page: "",
        media_validator=_validation,
        commit=True,
        generated_at=_GENERATED_AT,
    )

    assert second_result.manifest_changed is False
    assert second_result.report_changed is False
    assert second_result.committed is False
    assert "generated files unchanged" in cli._format_result(second_result)
    assert "generated files committed" in cli._format_result(
        cli.RefreshResult(
            manifest_path=tmp_path / "manifest.json",
            report_path=tmp_path / "report.json",
            manifest_changed=True,
            report_changed=True,
            committed=True,
            media_link_count=0,
            media_validation_count=0,
        )
    )
    commit.assert_not_called()
