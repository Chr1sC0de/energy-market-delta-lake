"""
Test suite for the marimo notebook server (marimoserver.main).

Covers:
  - GET /health — returns 200 with {"status": "ok"}
  - GET /marimo — returns a dashboard concept gallery
  - Marimo ASGI app is mounted and serves the test notebook
  - MARIMO_NOTEBOOKS_DIR env var is respected
  - app_names is populated correctly from the notebooks directory
"""

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import anyio
import httpx
from starlette.types import ASGIApp, Message, Receive, Scope, Send

# conftest.py sets MARIMO_NOTEBOOKS_DIR before this import.
from marimoserver.dashboard_registry import (
    DashboardStatus,
    dashboard_registry,
)
from marimoserver.main import (
    IMMUTABLE_ASSET_CACHE_CONTROL,
    NOTEBOOKS_DIR,
    StaticAssetHeadersMiddleware,
    _render_index_html,
    app,
    app_names,
)
from tests.component.conftest import TEST_NOTEBOOKS_DIR


@dataclass(frozen=True)
class _StaticAssetRef:
    rel: str
    as_type: str | None
    path: str


class _ConceptCardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.cards: dict[str, dict[str, str | None]] = {}

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        concept_id = attributes.get("data-concept-id")
        if concept_id is None:
            return
        self.cards[concept_id] = {
            "tag": tag,
            "href": attributes.get("href"),
            "status": attributes.get("data-status"),
        }


class _NotebookAssetParser(HTMLParser):
    def __init__(self, notebook_route: str) -> None:
        super().__init__()
        self.notebook_route = notebook_route
        self.refs: list[_StaticAssetRef] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        ref = _asset_ref_from_tag(tag, attributes)
        if ref is None:
            return

        path = urlparse(urljoin(self.notebook_route, ref)).path
        self.refs.append(
            _StaticAssetRef(
                rel=attributes.get("rel") or tag,
                as_type=attributes.get("as"),
                path=path,
            )
        )


def _get(path: str) -> httpx.Response:
    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get(path)

    return anyio.run(request)


def _concept_cards(html: str) -> dict[str, dict[str, str | None]]:
    parser = _ConceptCardParser()
    parser.feed(html)
    return parser.cards


def _notebook_asset_refs(
    html: str,
    notebook_route: str,
) -> list[_StaticAssetRef]:
    parser = _NotebookAssetParser(notebook_route)
    parser.feed(html)
    return [ref for ref in parser.refs if "/assets/" in ref.path]


def _asset_ref_from_tag(
    tag: str,
    attributes: dict[str, str | None],
) -> str | None:
    if tag == "link":
        return attributes.get("href")
    if tag == "script":
        return attributes.get("src")
    return None


def _first_asset_path(
    refs: list[_StaticAssetRef],
    suffix: str,
) -> str:
    return next(ref.path for ref in refs if ref.path.endswith(suffix))


async def _plain_text_response_app(
    scope: Scope,
    receive: Receive,
    send: Send,
) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain")],
        }
    )
    await send({"type": "http.response.body", "body": b"ok"})


def _call_asgi(test_app: ASGIApp, scope: Scope) -> list[Message]:
    messages: list[Message] = []

    async def receive() -> Message:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: Message) -> None:
        messages.append(message)

    async def call() -> None:
        await test_app(scope, receive, send)

    anyio.run(call)
    return messages


def _response_start(messages: list[Message]) -> Message:
    return next(
        message for message in messages if message["type"] == "http.response.start"
    )


# ---------------------------------------------------------------------------
# TestHealthEndpoint
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    def test_health_returns_200(self) -> None:
        response = _get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_marimo_health_returns_200(self) -> None:
        response = _get("/marimo/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestDashboardRegistryEndpoint:
    def test_dashboard_registry_returns_json_payload(self) -> None:
        response = _get("/marimo/dashboard-registry.json")

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        payload = response.json()
        assert payload["schema_version"] == 1
        assert "operator" in payload["audiences"]
        assert any(
            entry["concept_id"] == "gas-market-overview"
            and entry["notebook_route"] == "/marimo/sample_energy_market/"
            for entry in payload["entries"]
        )


class TestStaticAssetHeadersMiddleware:
    def test_non_http_scopes_pass_through(self) -> None:
        seen_scope_types: list[str] = []

        async def app_to_wrap(
            scope: Scope,
            receive: Receive,
            send: Send,
        ) -> None:
            seen_scope_types.append(scope["type"])

        middleware = StaticAssetHeadersMiddleware(app_to_wrap)

        messages = _call_asgi(middleware, {"type": "lifespan"})

        assert seen_scope_types == ["lifespan"]
        assert messages == []

    def test_woff2_asset_response_gets_font_type_and_cache_header(self) -> None:
        middleware = StaticAssetHeadersMiddleware(_plain_text_response_app)

        messages = _call_asgi(
            middleware,
            {"type": "http", "path": "/marimo/test_notebook/assets/font-a1b2.woff2"},
        )
        headers = dict(_response_start(messages)["headers"])

        assert headers[b"content-type"] == b"font/woff2"
        assert headers[b"cache-control"] == IMMUTABLE_ASSET_CACHE_CONTROL.encode()


# ---------------------------------------------------------------------------
# TestNotebooksDir
# ---------------------------------------------------------------------------


class TestNotebooksDir:
    def test_notebooks_dir_from_env(self) -> None:
        """MARIMO_NOTEBOOKS_DIR env var is picked up by the app."""
        assert str(NOTEBOOKS_DIR) == TEST_NOTEBOOKS_DIR

    def test_registry_notebooks_exist(self) -> None:
        """The temporary registry notebook files exist in the configured dir."""
        for name in (
            "sample_energy_market",
            "gbb_interactive_map",
            "table_explorer",
            "data_readiness_overview",
            "test_notebook",
        ):
            assert (NOTEBOOKS_DIR / f"{name}.py").is_file()


# ---------------------------------------------------------------------------
# TestAppDiscovery
# ---------------------------------------------------------------------------


class TestAppDiscovery:
    def test_app_names_contains_registry_notebooks(self) -> None:
        """Registry-backed notebooks should be discovered and added to app_names."""
        assert {
            "sample_energy_market",
            "gbb_interactive_map",
            "table_explorer",
            "data_readiness_overview",
        } <= set(app_names)


# ---------------------------------------------------------------------------
# TestIndexPage
# ---------------------------------------------------------------------------


class TestIndexPage:
    def test_index_returns_html(self) -> None:
        response = _get("/marimo")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_index_renders_concept_gallery_cards(self) -> None:
        response = _get("/marimo")
        cards = _concept_cards(response.text)

        assert "gas-market-overview" in cards
        assert "capacity-context" in cards
        assert "Marimo concept gallery" in response.text
        assert "Audience filters" in response.text
        assert 'href="#concept-gas-market-overview"' in response.text
        assert 'class="audience-filter"' in response.text

    def test_index_links_available_cards_to_mounted_notebooks(self) -> None:
        response = _get("/marimo")
        cards = _concept_cards(response.text)

        for entry in dashboard_registry():
            if entry.status is not DashboardStatus.AVAILABLE:
                continue

            assert entry.notebook_name in app_names
            assert entry.notebook_route is not None
            assert cards[entry.concept_id] == {
                "tag": "a",
                "href": entry.notebook_route,
                "status": "available",
            }

    def test_index_renders_planned_cards_without_notebook_links(self) -> None:
        response = _get("/marimo")
        cards = _concept_cards(response.text)

        for entry in dashboard_registry():
            if entry.status is not DashboardStatus.PLANNED:
                continue

            assert entry.notebook_route is None
            assert cards[entry.concept_id] == {
                "tag": "article",
                "href": None,
                "status": "planned",
            }

        assert "Planned dashboard" in response.text
        assert 'href="/marimo/capacity-context/"' not in response.text

    def test_index_keeps_available_cards_unlinked_when_notebook_not_mounted(
        self,
    ) -> None:
        html = _render_index_html(mounted_notebook_names=set())
        cards = _concept_cards(html)
        overview = next(
            entry
            for entry in dashboard_registry()
            if entry.concept_id == "gas-market-overview"
        )

        assert overview.notebook_route is not None
        assert cards[overview.concept_id] == {
            "tag": "article",
            "href": None,
            "status": "available",
        }
        assert f'href="{overview.notebook_route}"' not in html
        assert "Not mounted" in html
        assert "Notebook not present in this image" in html

    def test_index_uses_shared_theme(self) -> None:
        response = _get("/marimo")
        assert '<link rel="stylesheet" href="/theme.css">' in response.text
        assert "var(--emdl-blue" in response.text
        assert "var(--emdl-paper" in response.text
        assert "#1a73e8" not in response.text

    def test_index_does_not_emit_auto_refresh_timer(self) -> None:
        response = _get("/marimo")
        html = response.text.lower()

        assert 'http-equiv="refresh"' not in html
        assert "setinterval(" not in html
        assert "settimeout(" not in html


# ---------------------------------------------------------------------------
# TestMarimoMount
# ---------------------------------------------------------------------------


class TestMarimoMount:
    def test_notebook_route_serves_content(self) -> None:
        """
        The test_notebook should be accessible at /marimo/test_notebook/.
        Marimo returns 200 with HTML for a valid notebook path.
        """
        response = _get("/marimo/test_notebook/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_notebook_html_keeps_marimo_preload_hints_for_static_assets(
        self,
    ) -> None:
        route = "/marimo/test_notebook/"
        response = _get(route)

        refs = _notebook_asset_refs(response.text, route)

        assert any(
            ref.rel == "preload"
            and ref.as_type == "image"
            and ref.path.endswith(".png")
            for ref in refs
        )
        assert any(
            ref.rel == "preload" and ref.as_type == "font" and ref.path.endswith(".ttf")
            for ref in refs
        )
        assert any(
            ref.rel == "modulepreload" and ref.path.endswith(".js") for ref in refs
        )
        assert all(ref.path.startswith(f"{route}assets/") for ref in refs)
        assert ".wasm" not in response.text.lower()

    def test_notebook_static_asset_routes_have_content_types_and_cache_headers(
        self,
    ) -> None:
        route = "/marimo/test_notebook/"
        response = _get(route)
        refs = _notebook_asset_refs(response.text, route)
        expected_content_types = {
            ".png": "image/png",
            ".ttf": "font/ttf",
            ".js": "text/javascript",
            ".css": "text/css",
        }

        for suffix, content_type in expected_content_types.items():
            asset_path = _first_asset_path(refs, suffix)
            asset_response = _get(asset_path)

            assert asset_response.status_code == 200
            assert asset_response.headers["content-type"].startswith(content_type)
            assert (
                asset_response.headers["cache-control"] == IMMUTABLE_ASSET_CACHE_CONTROL
            )
            assert asset_response.headers["etag"]

    def test_unhashed_notebook_metadata_routes_are_not_immutable_cached(
        self,
    ) -> None:
        manifest_response = _get("/marimo/test_notebook/manifest.json")
        favicon_response = _get("/marimo/test_notebook/favicon.ico")

        assert manifest_response.status_code == 200
        assert manifest_response.headers["content-type"].startswith("application/json")
        assert "cache-control" not in manifest_response.headers
        assert favicon_response.status_code == 200
        assert favicon_response.headers["content-type"].startswith(
            "image/vnd.microsoft.icon"
        )
        assert "cache-control" not in favicon_response.headers
