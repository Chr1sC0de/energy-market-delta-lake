"""
Test suite for the marimo notebook server (marimoserver.main).

Covers:
  - GET /health — returns 200 with {"status": "ok"}
  - GET / — returns notebook index page listing discovered notebooks
  - Marimo ASGI app is mounted and serves the test notebook
  - MARIMO_NOTEBOOKS_DIR env var is respected
  - app_names is populated correctly from the notebooks directory
"""

from fastapi.testclient import TestClient

# conftest.py sets MARIMO_NOTEBOOKS_DIR before this import.
from marimoserver.main import NOTEBOOKS_DIR, app, app_names
from tests.component.conftest import TEST_NOTEBOOKS_DIR

# ---------------------------------------------------------------------------
# TestHealthEndpoint
# ---------------------------------------------------------------------------


class TestHealthEndpoint:
    def test_health_returns_200(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/health")
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
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/marimo")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_index_lists_notebooks(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/marimo")
        assert "test_notebook" in response.text


# ---------------------------------------------------------------------------
# TestMarimoMount
# ---------------------------------------------------------------------------


class TestMarimoMount:
    def test_notebook_route_serves_content(self) -> None:
        """
        The test_notebook should be accessible at /test_notebook/.
        Marimo returns 200 with HTML for a valid notebook path.
        """
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/marimo/test_notebook/")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
