"""
Test suite for the marimo notebook server (marimoserver.main).

Covers:
  - GET /health — returns 200 with {"status": "ok"}
  - GET /marimo — returns a dashboard concept gallery
  - Marimo ASGI app is mounted and serves the test notebook
  - MARIMO_NOTEBOOKS_DIR env var is respected
  - app_names is populated correctly from the notebooks directory
"""

from html.parser import HTMLParser

import anyio
import httpx

# conftest.py sets MARIMO_NOTEBOOKS_DIR before this import.
from marimoserver.dashboard_registry import (
    DashboardStatus,
    dashboard_registry,
)
from marimoserver.main import NOTEBOOKS_DIR, _render_index_html, app, app_names
from tests.component.conftest import TEST_NOTEBOOKS_DIR


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
            "test_notebook",
        ):
            assert (NOTEBOOKS_DIR / f"{name}.py").is_file()


# ---------------------------------------------------------------------------
# TestAppDiscovery
# ---------------------------------------------------------------------------


class TestAppDiscovery:
    def test_app_names_contains_registry_notebooks(self) -> None:
        """Registry-backed notebooks should be discovered and added to app_names."""
        assert {"sample_energy_market", "gbb_interactive_map", "table_explorer"} <= set(
            app_names
        )


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
