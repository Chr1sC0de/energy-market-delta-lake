"""Reusable smoke-test helpers for curated Marimo dashboards."""

from dataclasses import dataclass
from pathlib import Path

import anyio
import httpx

from marimoserver.dashboard_registry import (
    DashboardRegistryEntry,
    DashboardStatus,
    dashboard_registry,
)
from marimoserver.main import app

MARIMO_SUBPROJECT_DIR = Path(__file__).resolve().parents[2]
CURATED_NOTEBOOKS_DIR = MARIMO_SUBPROJECT_DIR / "notebooks"


@dataclass(frozen=True)
class DashboardSmokeTarget:
    """One available dashboard notebook and its expected Marimo route."""

    entry: DashboardRegistryEntry
    notebook_path: Path

    @property
    def concept_id(self) -> str:
        """Return the dashboard registry concept ID."""
        return self.entry.concept_id

    @property
    def notebook_name(self) -> str:
        """Return the backing notebook stem."""
        if self.entry.notebook_name is None:
            raise ValueError(f"{self.concept_id} has no notebook_name")
        return self.entry.notebook_name

    @property
    def route(self) -> str:
        """Return the expected FastAPI-mounted Marimo route."""
        if self.entry.notebook_route is None:
            raise ValueError(f"{self.concept_id} has no notebook_route")
        return self.entry.notebook_route


def available_dashboard_entries() -> tuple[DashboardRegistryEntry, ...]:
    """Return registry entries that should be mounted in the dashboard image."""
    return tuple(
        entry
        for entry in dashboard_registry()
        if entry.status is DashboardStatus.AVAILABLE
    )


def curated_notebook_paths(
    notebooks_dir: Path = CURATED_NOTEBOOKS_DIR,
) -> tuple[Path, ...]:
    """Return curated notebook files from the configured notebooks directory."""
    return tuple(sorted(notebooks_dir.glob("*.py")))


def curated_notebook_names(
    notebooks_dir: Path = CURATED_NOTEBOOKS_DIR,
) -> tuple[str, ...]:
    """Return curated notebook stems from the configured notebooks directory."""
    return tuple(path.stem for path in curated_notebook_paths(notebooks_dir))


def dashboard_smoke_targets(
    notebooks_dir: Path = CURATED_NOTEBOOKS_DIR,
) -> tuple[DashboardSmokeTarget, ...]:
    """Return available registry dashboards with matching curated notebooks."""
    paths_by_name = {path.stem: path for path in curated_notebook_paths(notebooks_dir)}
    targets: list[DashboardSmokeTarget] = []

    for entry in available_dashboard_entries():
        if entry.notebook_name is None:
            continue
        notebook_path = paths_by_name.get(entry.notebook_name)
        if notebook_path is None:
            continue
        targets.append(DashboardSmokeTarget(entry=entry, notebook_path=notebook_path))

    return tuple(targets)


def get_fastapi_route(path: str) -> httpx.Response:
    """GET a route from the in-process FastAPI Marimo wrapper."""

    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as client:
            return await client.get(path)

    return anyio.run(request)


def assert_html_response(response: httpx.Response, route: str) -> None:
    """Assert that a FastAPI route returned an HTML document."""
    content_type = response.headers.get("content-type", "")
    assert response.status_code == 200, f"{route} returned {response.status_code}"
    assert "text/html" in content_type
    assert "<html" in response.text.lower()
