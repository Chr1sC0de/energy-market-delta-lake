"""
Conftest for the marimo server test suite.

Sets MARIMO_NOTEBOOKS_DIR to a temporary directory containing a minimal
marimo notebook so that tests do not depend on the real notebooks/ folder.
"""

import os
import tempfile
import textwrap

import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        item.add_marker(pytest.mark.component)


# ---------------------------------------------------------------------------
# Create a temp directory with a minimal valid marimo notebook before the
# app module is imported.
# ---------------------------------------------------------------------------
_tmp_dir = tempfile.mkdtemp(prefix="marimo_test_notebooks_")

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

with open(os.path.join(_tmp_dir, "test_notebook.py"), "w") as f:
    f.write(_notebook_content)

os.environ["MARIMO_NOTEBOOKS_DIR"] = _tmp_dir

TEST_NOTEBOOKS_DIR = _tmp_dir
