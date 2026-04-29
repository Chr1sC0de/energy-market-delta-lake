"""Bulk-import all individual GBB/VicGas table definition modules.

Each file has a single module-level statement:
    defs = df_from_s3_keys_definitions_factory(...)

Importing the module executes that statement and covers all lines in the file.
"""

import importlib
import pkgutil

import bs4
from dagster import Definitions


def _import_all_under(package: str) -> None:
    """Import every module in *package* (non-recursive)."""
    top = importlib.import_module(package)
    for _importer, modname, _ispkg in pkgutil.iter_modules(
        path=top.__path__,  # type: ignore[arg-type]
        prefix=f"{package}.",
    ):
        importlib.import_module(modname)


def test_import_all_gbb_table_modules() -> None:
    _import_all_under("aemo_etl.defs.raw.gbb")


def test_import_all_vicgas_table_modules() -> None:
    _import_all_under("aemo_etl.defs.raw.vicgas")


# ---------------------------------------------------------------------------
# nemweb_public_files.py
# ---------------------------------------------------------------------------


def test_gbb_folder_filter_normal() -> None:
    from dagster import OpExecutionContext
    from unittest.mock import MagicMock

    from aemo_etl.defs.raw.nemweb_public_files import gbb_folder_filter

    ctx = MagicMock(spec=OpExecutionContext)
    tag_normal = bs4.BeautifulSoup("<a>SOMEFOLDER/</a>", "html.parser").find("a")
    assert gbb_folder_filter(ctx, tag_normal) is True  # type: ignore[arg-type]


def test_gbb_folder_filter_parent_dir() -> None:
    from unittest.mock import MagicMock
    from dagster import OpExecutionContext

    from aemo_etl.defs.raw.nemweb_public_files import gbb_folder_filter

    ctx = MagicMock(spec=OpExecutionContext)
    tag_parent = bs4.BeautifulSoup("<a>[To Parent Directory]</a>", "html.parser").find(
        "a"
    )
    assert gbb_folder_filter(ctx, tag_parent) is False  # type: ignore[arg-type]


def test_gbb_folder_filter_duplicate() -> None:
    from unittest.mock import MagicMock
    from dagster import OpExecutionContext

    from aemo_etl.defs.raw.nemweb_public_files import gbb_folder_filter

    ctx = MagicMock(spec=OpExecutionContext)
    tag_dup = bs4.BeautifulSoup("<a>DUPLICATE</a>", "html.parser").find("a")
    assert gbb_folder_filter(ctx, tag_dup) is False  # type: ignore[arg-type]


def test_nemweb_public_files_defs() -> None:
    from aemo_etl.defs.raw.nemweb_public_files import defs

    d = defs()
    assert isinstance(d, Definitions)


# ---------------------------------------------------------------------------
# unzipper.py
# ---------------------------------------------------------------------------


def test_unzipper_defs() -> None:
    from aemo_etl.defs.raw.unzipper import defs

    d = defs()
    assert isinstance(d, Definitions)
