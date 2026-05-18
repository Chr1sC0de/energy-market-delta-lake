"""
Conftest for the marimo server test suite.

Sets MARIMO_NOTEBOOKS_DIR to a temporary directory containing a minimal
marimo notebook so that tests do not depend on the real notebooks/ folder.
"""

import os
import tempfile
import textwrap
from pathlib import Path

import pytest

from marimoserver.dashboard_registry import DashboardStatus, dashboard_registry


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        item.add_marker(pytest.mark.component)


def available_registry_notebook_names() -> tuple[str, ...]:
    """Return available dashboard notebook names from the registry."""
    return tuple(
        entry.notebook_name
        for entry in dashboard_registry()
        if entry.status is DashboardStatus.AVAILABLE and entry.notebook_name is not None
    )


# ---------------------------------------------------------------------------
# Create a temp directory with a minimal valid marimo notebook before the
# app module is imported.
# ---------------------------------------------------------------------------
_tmp_dir = Path(tempfile.mkdtemp(prefix="marimo_test_notebooks_"))

_notebook_content = textwrap.dedent("""\
    import marimo

    __generated_with = "0.21.1"
    app = marimo.App(width="medium")


    @app.cell
    def _():
        import marimo as mo
        return (mo,)


    @app.cell
    def _(mo):
        mo.md("# Test Notebook")
        return


    if __name__ == "__main__":
        app.run()
""")

for _notebook_name in ("test_notebook", *available_registry_notebook_names()):
    (_tmp_dir / f"{_notebook_name}.py").write_text(
        _notebook_content,
        encoding="utf-8",
    )

os.environ["MARIMO_NOTEBOOKS_DIR"] = str(_tmp_dir)

TEST_NOTEBOOKS_DIR = str(_tmp_dir)
