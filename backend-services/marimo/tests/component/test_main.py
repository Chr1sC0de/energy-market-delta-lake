"""
Test suite for the marimo notebook server (marimoserver.main).

Covers:
  - GET /health — returns 200 with {"status": "ok"}
  - GET / — returns notebook index page listing discovered notebooks
  - Marimo ASGI app is mounted and serves the test notebook
  - MARIMO_NOTEBOOKS_DIR env var is respected
  - app_names is populated correctly from the notebooks directory
"""

import asyncio

import httpx

# conftest.py sets MARIMO_NOTEBOOKS_DIR before this import.
from marimoserver.main import NOTEBOOKS_DIR, app, app_names
from tests.component.conftest import TEST_NOTEBOOKS_DIR


def get_response(path: str) -> httpx.Response:
    """Return an in-process ASGI response for the Marimo wrapper app."""
    return asyncio.run(get_response_async(path))


async def get_response_async(path: str) -> httpx.Response:
    """Return an in-process ASGI response without TestClient lifespan blocking."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.get(path)


# ---------------------------------------------------------------------------
# TestHealthEndpoint
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    def test_health_returns_200(self) -> None:
        response = get_response("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


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
        response = get_response("/marimo")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_index_lists_notebooks(self) -> None:
        response = get_response("/marimo")
        assert "test_notebook" in response.text

    def test_index_uses_shared_theme(self) -> None:
        response = get_response("/marimo")
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
        response = get_response("/marimo/test_notebook/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
