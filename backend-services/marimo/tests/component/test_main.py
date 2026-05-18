"""
Test suite for the marimo notebook server (marimoserver.main).

Covers:
  - GET /health — returns 200 with {"status": "ok"}
  - GET / — returns notebook index page listing discovered notebooks
  - Marimo ASGI app is mounted and serves the test notebook
  - MARIMO_NOTEBOOKS_DIR env var is respected
  - app_names is populated correctly from the notebooks directory
"""

import anyio
import httpx

# conftest.py sets MARIMO_NOTEBOOKS_DIR before this import.
from marimoserver.main import NOTEBOOKS_DIR, app, app_names
from tests.component.conftest import TEST_NOTEBOOKS_DIR


def _get(path: str) -> httpx.Response:
    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get(path)

    return anyio.run(request)


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

    def test_test_notebook_exists(self) -> None:
        """The temporary test notebook file exists in the configured dir."""
        assert (NOTEBOOKS_DIR / "test_notebook.py").is_file()


# ---------------------------------------------------------------------------
# TestAppDiscovery
# ---------------------------------------------------------------------------


class TestAppDiscovery:
    def test_app_names_contains_test_notebook(self) -> None:
        """The test_notebook should be discovered and added to app_names."""
        assert "test_notebook" in app_names


# ---------------------------------------------------------------------------
# TestIndexPage
# ---------------------------------------------------------------------------


class TestIndexPage:
    def test_index_returns_html(self) -> None:
        response = _get("/marimo")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_index_lists_notebooks(self) -> None:
        response = _get("/marimo")
        assert "test_notebook" in response.text

    def test_index_uses_shared_theme(self) -> None:
        response = _get("/marimo")
        assert '<link rel="stylesheet" href="/theme.css">' in response.text
        assert "var(--emdl-blue" in response.text
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
