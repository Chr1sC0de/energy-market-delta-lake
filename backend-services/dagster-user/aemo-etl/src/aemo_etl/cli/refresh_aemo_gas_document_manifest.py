"""CLI for refreshing the checked-in AEMO gas document media manifest."""

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from types import TracebackType
from typing import Any, Self, cast
from urllib.parse import urlparse

import requests
from requests import Response

from aemo_etl.factories.aemo_gas_documents.manifest import (
    DISCOVERY_REPORT_FILENAME,
    MANIFEST_FILENAME,
    discovery_report_payload,
    dump_manifest_json,
    existing_manifest_entries,
    manifest_payload,
    media_link_manifest_entry,
    source_page_manifest_entry,
)
from aemo_etl.factories.aemo_gas_documents.models import (
    AEMOGasDocumentMediaValidation,
    AEMOGasDocumentPendingObservation,
    AEMOGasDocumentSourcePage,
    DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES,
)
from aemo_etl.factories.aemo_gas_documents.scraper import (
    MEDIA_PATH_FRAGMENT,
    _page_link_observations,
    child_source_pages,
    extract_page_title,
    is_aemo_public_url,
    soup_getter,
)

DEFAULT_COMMIT_MESSAGE = "Refresh AEMO gas document media manifest"
DEFAULT_PAGE_TIMEOUT_MS = 60_000
DEFAULT_REQUEST_TIMEOUT_SECONDS = 30.0

type PageLoader = Callable[[AEMOGasDocumentSourcePage], str]
type MediaValidator = Callable[[str], AEMOGasDocumentMediaValidation]


@dataclass(frozen=True, slots=True)
class RefreshResult:
    """Result summary for a manifest refresh command."""

    manifest_path: Path
    report_path: Path
    manifest_changed: bool
    report_changed: bool
    committed: bool
    media_link_count: int
    media_validation_count: int


class PlaywrightPageLoader:
    """Callable Playwright Chromium source-page loader."""

    def __init__(self, *, timeout_ms: int) -> None:
        """Initialize the loader with a Playwright page timeout."""
        self._timeout_ms = timeout_ms
        self._playwright: Any | None = None
        self._browser: Any | None = None

    def __enter__(self) -> Self:
        """Start Playwright Chromium for source-page discovery."""
        from playwright.sync_api import sync_playwright

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close Chromium and stop Playwright."""
        if self._browser is not None:
            self._browser.close()
        if self._playwright is not None:
            self._playwright.stop()

    def __call__(self, source_page: AEMOGasDocumentSourcePage) -> str:
        """Load one source page and return post-render HTML."""
        if self._browser is None:
            raise RuntimeError("PlaywrightPageLoader must be used as a context manager")
        page = self._browser.new_page()
        try:
            page.goto(
                source_page.source_page_url,
                wait_until="domcontentloaded",
                timeout=self._timeout_ms,
            )
            return cast(str, page.content())
        finally:
            page.close()


def default_manifest_path() -> Path:
    """Return the checked-in default manifest path."""
    return (
        Path(__file__).resolve().parents[1]
        / "factories"
        / "aemo_gas_documents"
        / MANIFEST_FILENAME
    )


def default_report_path() -> Path:
    """Return the checked-in default discovery report path."""
    return default_manifest_path().with_name(DISCOVERY_REPORT_FILENAME)


def build_parser() -> argparse.ArgumentParser:
    """Build the AEMO gas document media manifest refresh parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Refresh the checked-in AEMO gas document media manifest with "
            "Playwright-discovered public AEMO media links."
        )
    )
    parser.add_argument(
        "--manifest-path",
        type=Path,
        default=default_manifest_path(),
        help=f"manifest JSON path (default: {default_manifest_path()})",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=default_report_path(),
        help=f"discovery report JSON path (default: {default_report_path()})",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="write generated files without staging or committing them",
    )
    parser.add_argument(
        "--commit-message",
        default=DEFAULT_COMMIT_MESSAGE,
        help=f"git commit message when committing (default: {DEFAULT_COMMIT_MESSAGE})",
    )
    parser.add_argument(
        "--timeout-ms",
        type=_positive_int,
        default=DEFAULT_PAGE_TIMEOUT_MS,
        help=f"Playwright page timeout in milliseconds (default: {DEFAULT_PAGE_TIMEOUT_MS})",
    )
    parser.add_argument(
        "--request-timeout",
        type=_positive_float,
        default=DEFAULT_REQUEST_TIMEOUT_SECONDS,
        help=(
            "direct media HTTP validation timeout in seconds "
            f"(default: {DEFAULT_REQUEST_TIMEOUT_SECONDS:g})"
        ),
    )
    return parser


def refresh_aemo_gas_document_media_manifest(
    *,
    manifest_path: Path = default_manifest_path(),
    report_path: Path = default_report_path(),
    source_pages: Iterable[AEMOGasDocumentSourcePage] = (
        DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES
    ),
    page_loader: PageLoader,
    media_validator: MediaValidator,
    commit: bool,
    commit_message: str = DEFAULT_COMMIT_MESSAGE,
    generated_at: datetime | None = None,
) -> RefreshResult:
    """Refresh manifest/report files and optionally commit generated changes."""
    effective_generated_at = generated_at or datetime.now(UTC)
    existing_payload = _read_json_file(manifest_path)
    manifest, report = discover_manifest_payloads(
        source_pages=source_pages,
        page_loader=page_loader,
        media_validator=media_validator,
        generated_at=effective_generated_at,
        existing_payload=existing_payload,
    )
    manifest_changed = _write_if_changed(
        manifest_path,
        dump_manifest_json(manifest),
    )
    report_changed = _write_if_changed(report_path, dump_manifest_json(report))
    committed = False
    if commit and (manifest_changed or report_changed):
        committed = _stage_and_commit_generated_files(
            (manifest_path, report_path),
            commit_message=commit_message,
        )
    return RefreshResult(
        manifest_path=manifest_path,
        report_path=report_path,
        manifest_changed=manifest_changed,
        report_changed=report_changed,
        committed=committed,
        media_link_count=cast(int, manifest["media_link_count"]),
        media_validation_count=cast(int, report["media_validation_count"]),
    )


def discover_manifest_payloads(
    *,
    source_pages: Iterable[AEMOGasDocumentSourcePage],
    page_loader: PageLoader,
    media_validator: MediaValidator,
    generated_at: datetime,
    existing_payload: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Discover media links and return manifest plus discovery report payloads."""
    existing_source_pages, existing_media_links = existing_manifest_entries(
        existing_payload
    )
    manifest_source_pages: list[Mapping[str, Any]] = []
    manifest_media_links: list[Mapping[str, Any]] = []
    report_source_pages: list[Mapping[str, Any]] = []
    media_validations: list[Mapping[str, Any]] = []
    queued_pages = list(source_pages)
    seen_pages: set[str] = set()

    while queued_pages:
        source_page = queued_pages.pop(0)
        if source_page.source_page_url in seen_pages:
            continue
        seen_pages.add(source_page.source_page_url)

        if not _should_fetch_source_page(source_page):
            preserved = existing_media_links.get(source_page.source_page_url, [])
            manifest_source_pages.append(
                source_page_manifest_entry(
                    source_page,
                    observed_at=generated_at,
                    status="skipped_fetch_disabled",
                )
            )
            manifest_media_links.extend(preserved)
            report_source_pages.append(
                _source_page_report_entry(
                    source_page=source_page,
                    status="skipped_fetch_disabled",
                    candidate_media_link_count=0,
                    preserved_media_link_count=len(preserved),
                )
            )
            continue

        try:
            html = page_loader(source_page)
            _raise_if_blocked_source_page(html)
        except Exception as error:
            preserved = existing_media_links.get(source_page.source_page_url, [])
            manifest_source_pages.append(
                existing_source_pages.get(source_page.source_page_url)
                or source_page_manifest_entry(
                    source_page,
                    observed_at=generated_at,
                    status="source_page_failed",
                    error=str(error),
                )
            )
            manifest_media_links.extend(preserved)
            report_source_pages.append(
                _source_page_report_entry(
                    source_page=source_page,
                    status="source_page_failed",
                    candidate_media_link_count=0,
                    preserved_media_link_count=len(preserved),
                    error=str(error),
                )
            )
            continue

        soup = soup_getter(html)
        page_title = extract_page_title(soup, source_page.source_page_title)
        manifest_source_pages.append(
            source_page_manifest_entry(
                source_page,
                observed_at=generated_at,
                source_page_title=page_title,
                status="refreshed",
            )
        )
        media_observations = _media_link_observations(
            source_page,
            html,
            observed_at=generated_at,
            page_title=page_title,
        )
        for observation in media_observations:
            validation = media_validator(observation.source_url)
            media_validations.append(_media_validation_report_entry(validation))
            if validation.ok:
                observation = replace(observation, resolved_url=validation.resolved_url)
            else:
                observation = replace(
                    observation,
                    resolved_url=validation.resolved_url,
                    should_download=False,
                )
            manifest_media_links.append(media_link_manifest_entry(observation))

        report_source_pages.append(
            _source_page_report_entry(
                source_page=source_page,
                status="refreshed",
                candidate_media_link_count=len(media_observations),
                preserved_media_link_count=0,
            )
        )
        if source_page.discover_child_pages:
            queued_pages.extend(child_source_pages(source_page, soup))

    return (
        manifest_payload(
            generated_at=generated_at,
            source_pages=manifest_source_pages,
            media_links=manifest_media_links,
        ),
        discovery_report_payload(
            generated_at=generated_at,
            source_pages=report_source_pages,
            media_validations=media_validations,
        ),
    )


def validate_media_url(
    source_url: str,
    *,
    request_timeout: float = DEFAULT_REQUEST_TIMEOUT_SECONDS,
    request_getter: Callable[[str, float], Response] | None = None,
) -> AEMOGasDocumentMediaValidation:
    """Validate one direct media URL with a normal HTTP GET request."""
    response: Response | None = None
    try:
        if request_getter is None:
            response = _request_media_url(source_url, request_timeout)
        else:
            response = request_getter(source_url, request_timeout)
        response.raise_for_status()
        return _media_validation_from_response(source_url, response, error=None)
    except Exception as error:
        if response is not None:
            return _media_validation_from_response(
                source_url,
                response,
                error=str(error),
            )
        return AEMOGasDocumentMediaValidation(
            source_url=source_url,
            ok=False,
            status_code=None,
            resolved_url=source_url,
            content_type=None,
            content_length=None,
            error=str(error),
        )
    finally:
        if response is not None:
            response.close()


def main(argv: Sequence[str] | None = None) -> int:
    """Run the AEMO gas document media manifest refresh CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    media_validator = _media_validator_for_timeout(args.request_timeout)
    try:
        with PlaywrightPageLoader(timeout_ms=args.timeout_ms) as page_loader:
            result = refresh_aemo_gas_document_media_manifest(
                manifest_path=args.manifest_path,
                report_path=args.report_path,
                page_loader=page_loader,
                media_validator=media_validator,
                commit=not args.no_commit,
                commit_message=args.commit_message,
            )
    except ValueError as error:
        parser.exit(2, f"error: {error}\n")
    except Exception as error:
        sys.stderr.write(f"error: {error}\n")
        return 1

    sys.stdout.write(_format_result(result))
    return 0


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def _should_fetch_source_page(source_page: AEMOGasDocumentSourcePage) -> bool:
    parsed = urlparse(source_page.source_page_url)
    return source_page.fetch_links and parsed.scheme in {"http", "https"}


def _media_link_observations(
    source_page: AEMOGasDocumentSourcePage,
    html: str,
    *,
    observed_at: datetime,
    page_title: str | None,
) -> list[AEMOGasDocumentPendingObservation]:
    soup = soup_getter(html)
    return [
        observation
        for observation in _page_link_observations(
            source_page,
            soup,
            observed_at=observed_at,
            page_url=source_page.source_page_url,
            page_title=page_title,
        )
        if _is_public_aemo_media_url(observation.source_url)
    ]


def _raise_if_blocked_source_page(html: str) -> None:
    if _is_cloudflare_challenge_page(html):
        raise RuntimeError("AEMO source page returned a Cloudflare challenge page")


def _is_cloudflare_challenge_page(html: str) -> bool:
    normalized = html.lower()
    return (
        "challenges.cloudflare.com" in normalized
        and "<title>just a moment" in normalized
    )


def _is_public_aemo_media_url(source_url: str) -> bool:
    return (
        is_aemo_public_url(source_url)
        and MEDIA_PATH_FRAGMENT in urlparse(source_url).path.lower()
    )


def _source_page_report_entry(
    *,
    source_page: AEMOGasDocumentSourcePage,
    status: str,
    candidate_media_link_count: int,
    preserved_media_link_count: int,
    error: str | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "corpus_source": source_page.corpus_source,
        "source_page_url": source_page.source_page_url,
        "status": status,
        "candidate_media_link_count": candidate_media_link_count,
        "preserved_media_link_count": preserved_media_link_count,
    }
    if error is not None:
        entry["error"] = error
    return entry


def _media_validation_report_entry(
    validation: AEMOGasDocumentMediaValidation,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "source_url": validation.source_url,
        "ok": validation.ok,
        "status": "ok" if validation.ok else "failed",
        "status_code": validation.status_code,
        "resolved_url": validation.resolved_url,
        "content_type": validation.content_type,
        "content_length": validation.content_length,
    }
    if validation.error is not None:
        entry["error"] = validation.error
    return entry


def _media_validator_for_timeout(request_timeout: float) -> MediaValidator:
    def _validate(source_url: str) -> AEMOGasDocumentMediaValidation:
        return validate_media_url(source_url, request_timeout=request_timeout)

    return _validate


def _request_media_url(source_url: str, request_timeout: float) -> Response:
    return requests.get(source_url, timeout=request_timeout, stream=True)


def _media_validation_from_response(
    source_url: str,
    response: Response,
    *,
    error: str | None,
) -> AEMOGasDocumentMediaValidation:
    content_length_header = response.headers.get("Content-Length")
    content_length = None
    if content_length_header is not None and content_length_header.isdigit():
        content_length = int(content_length_header)
    return AEMOGasDocumentMediaValidation(
        source_url=source_url,
        ok=error is None,
        status_code=response.status_code,
        resolved_url=response.url or source_url,
        content_type=response.headers.get("Content-Type"),
        content_length=content_length,
        error=error,
    )


def _read_json_file(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        return {"schema_version": 1, "source_pages": [], "media_links": []}
    return cast(Mapping[str, Any], json.loads(path.read_text(encoding="utf-8")))


def _write_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def _stage_and_commit_generated_files(
    paths: Sequence[Path],
    *,
    commit_message: str,
) -> bool:
    git_root = _git_root(paths[0].parent)
    relative_paths = [str(path.resolve().relative_to(git_root)) for path in paths]
    _run_git(["add", "--", *relative_paths], cwd=git_root)
    status = _run_git(["status", "--porcelain", "--", *relative_paths], cwd=git_root)
    if status == "":
        return False
    _run_git(["commit", "-m", commit_message, "--", *relative_paths], cwd=git_root)
    return True


def _git_root(cwd: Path) -> Path:
    output = _run_git(["rev-parse", "--show-toplevel"], cwd=cwd)
    return Path(output).resolve()


def _run_git(args: Sequence[str], *, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
        cwd=cwd,
    )
    return result.stdout.strip()


def _format_result(result: RefreshResult) -> str:
    if not result.manifest_changed and not result.report_changed:
        change_line = "generated files unchanged"
    elif result.committed:
        change_line = "generated files committed"
    else:
        change_line = "generated files written"
    return (
        f"{change_line}\n"
        f"manifest: {result.manifest_path}\n"
        f"report: {result.report_path}\n"
        f"media links: {result.media_link_count}\n"
        f"media validations: {result.media_validation_count}\n"
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
