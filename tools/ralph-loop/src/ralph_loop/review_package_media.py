from __future__ import annotations

import argparse
import functools
import http.server
import importlib
import socketserver
import sys
import threading
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Protocol, cast
from urllib.parse import urljoin

DEFAULT_TIMEOUT_MS = 90_000


@dataclass(frozen=True)
class ViewportSpec:
    name: str
    width: int
    height: int


VIEWPORTS = (
    ViewportSpec("desktop", 1440, 1100),
    ViewportSpec("narrow", 390, 900),
)


class BrowserPage(Protocol):
    def goto(self, url: str, *, wait_until: str, timeout: float) -> None: ...

    def wait_for_timeout(self, timeout: float) -> None: ...

    def evaluate(self, expression: str, arg: object = None) -> object: ...


class BrowserContext(Protocol):
    def new_page(self) -> BrowserPage: ...

    def close(self) -> None: ...


class Browser(Protocol):
    def new_context(self, **kwargs: object) -> BrowserContext: ...

    def close(self) -> None: ...


class BrowserType(Protocol):
    def launch(self, *, headless: bool) -> Browser: ...


class PlaywrightRuntime(Protocol):
    chromium: BrowserType


class PlaywrightContextManager(Protocol):
    def __enter__(self) -> PlaywrightRuntime: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None: ...


type SyncPlaywright = Callable[[], PlaywrightContextManager]


class ThreadingHttpServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    serve_dir = args.serve_dir.resolve()
    if not serve_dir.is_dir():
        raise SystemExit(f"serve directory does not exist: {serve_dir}")

    routes = tuple(args.route)
    if not routes:
        raise SystemExit("at least one --route is required")

    artifact_dir = args.artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    with _serve_static_dir(serve_dir) as base_url:
        evidence = record_route_videos(
            base_url=base_url,
            routes=routes,
            artifact_dir=artifact_dir,
            name_prefix=args.name_prefix,
            timeout_ms=args.timeout_ms,
        )
    print("\n".join(evidence))
    return 0


def record_route_videos(
    *,
    base_url: str,
    routes: tuple[str, ...],
    artifact_dir: Path,
    name_prefix: str | None,
    timeout_ms: int,
) -> list[str]:
    evidence: list[str] = []
    sync_playwright = _load_sync_playwright()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for route in routes:
                for viewport in VIEWPORTS:
                    video_path = artifact_dir / _video_name(
                        route,
                        viewport,
                        name_prefix=name_prefix,
                    )
                    evidence.extend(
                        _record_one_route(
                            browser,
                            url=urljoin(base_url, route.lstrip("/")),
                            route=route,
                            viewport=viewport,
                            video_path=video_path,
                            timeout_ms=timeout_ms,
                        )
                    )
        finally:
            browser.close()
    return evidence


def _record_one_route(
    browser: Browser,
    *,
    url: str,
    route: str,
    viewport: ViewportSpec,
    video_path: Path,
    timeout_ms: int,
) -> list[str]:
    video_path.parent.mkdir(parents=True, exist_ok=True)
    context = browser.new_context(
        record_video_dir=str(video_path.parent),
        viewport={"width": viewport.width, "height": viewport.height},
    )
    page = context.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=float(timeout_ms))
    page.wait_for_timeout(1_500)
    body_text = page.evaluate("() => document.body?.innerText?.trim() || ''")
    if not isinstance(body_text, str) or body_text == "":
        raise RuntimeError(f"route rendered no visible body text: {route}")
    if "Traceback" in body_text:
        raise RuntimeError(f"route rendered traceback text: {route}")
    context.close()

    video = getattr(page, "video", None)
    if video is None:
        raise RuntimeError(f"Playwright did not record video for {route}")
    recorded_path = Path(video.path())
    if recorded_path != video_path:
        if video_path.exists():
            video_path.unlink()
        recorded_path.replace(video_path)
    if not video_path.exists() or video_path.stat().st_size <= 0:
        raise RuntimeError(f"video artifact was not created: {video_path}")
    return [f"opened {route} at {viewport.name} ({url})", f"video: {video_path}"]


class _StaticServer:
    def __init__(self, serve_dir: Path) -> None:
        self._serve_dir = serve_dir
        self._server: ThreadingHttpServer | None = None
        self._thread: threading.Thread | None = None

    def __enter__(self) -> str:
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler,
            directory=str(self._serve_dir),
        )
        self._server = ThreadingHttpServer(("127.0.0.1", 0), handler)
        host, port = self._server.server_address
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="ralph-review-package-media-server",
            daemon=True,
        )
        self._thread.start()
        return f"http://{host}:{port}/"

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=5)


def _serve_static_dir(serve_dir: Path) -> _StaticServer:
    return _StaticServer(serve_dir)


def _load_sync_playwright() -> SyncPlaywright:
    try:
        module = importlib.import_module("playwright.sync_api")
    except ImportError as import_error:
        raise RuntimeError(
            "Playwright is not installed. Run with "
            "`uv run --with playwright python -m ralph_loop.review_package_media`."
        ) from import_error
    return cast(SyncPlaywright, getattr(module, "sync_playwright"))


def _video_name(
    route: str,
    viewport: ViewportSpec,
    *,
    name_prefix: str | None,
) -> str:
    route_slug = route.strip("/").replace("/", "__") or "root"
    prefix = name_prefix or route_slug
    return f"{prefix}__{viewport.name}.webm"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record Review package route videos from a local static directory."
    )
    parser.add_argument(
        "--serve-dir",
        type=Path,
        required=True,
        help="Static build directory to serve during capture.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        required=True,
        help="Directory where .webm files are written.",
    )
    parser.add_argument(
        "--route",
        action="append",
        default=[],
        help="Route to record. May be passed more than once.",
    )
    parser.add_argument(
        "--name-prefix",
        help="Optional output filename prefix before the viewport suffix.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=DEFAULT_TIMEOUT_MS,
        help="Per-route navigation timeout.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
