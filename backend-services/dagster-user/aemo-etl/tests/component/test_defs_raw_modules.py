"""Bulk-import all individual GBB/VicGas table definition modules.

Each file has a single module-level statement:
    defs = df_from_s3_keys_definitions_factory(...)

Importing the module executes that statement and covers all lines in the file.
"""

import importlib
import pkgutil
from typing import cast

import bs4
from dagster import Definitions
from dagster._core.definitions.unresolved_asset_job_definition import (
    UnresolvedAssetJobDefinition,
)
from polars import String

from aemo_etl.defs.raw.gbb._ecs import rebuild_sized_spot_ecs_tags


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


def test_import_all_sttm_table_modules() -> None:
    _import_all_under("aemo_etl.defs.raw.sttm")


def test_sttm_int651_source_table_spec_registered_for_archive_replay() -> None:
    from aemo_etl.factories.df_from_s3_keys.source_tables import (
        load_source_table_specs,
        select_source_table_specs,
    )

    (spec,) = select_source_table_specs(
        load_source_table_specs(),
        table="sttm.bronze_int651_v1_ex_ante_market_price_rpt_1",
    )

    assert spec.domain == "sttm"
    assert spec.name_suffix == "int651_v1_ex_ante_market_price_rpt_1"
    assert spec.glob_pattern == "int651_v1_ex_ante_market_price_rpt_1*"
    assert spec.archive_prefix == "bronze/sttm"
    assert spec.target_table_uri("aemo") == (
        "s3://aemo/bronze/sttm/bronze_int651_v1_ex_ante_market_price_rpt_1"
    )
    assert spec.surrogate_key_sources == ("gas_date", "hub_identifier")
    assert spec.schema["gas_date"] == String
    assert spec.schema["ex_ante_market_price"] == String


def test_gbb_pipeline_connection_flow_v1_job_uses_rebuild_sized_ecs_task() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_pipeline_connection_flow_v1 import defs

    job = cast(UnresolvedAssetJobDefinition, next(iter(defs.jobs or ())))

    assert job.tags == rebuild_sized_spot_ecs_tags()


def test_gbb_pipeline_connection_flow_v2_job_uses_rebuild_sized_ecs_task() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_pipeline_connection_flow_v2 import defs

    job = cast(UnresolvedAssetJobDefinition, next(iter(defs.jobs or ())))

    assert job.tags == rebuild_sized_spot_ecs_tags()


def test_gbb_short_term_capacity_outlook_job_uses_rebuild_sized_ecs_task() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_short_term_capacity_outlook import defs

    job = cast(UnresolvedAssetJobDefinition, next(iter(defs.jobs or ())))

    assert job.tags == rebuild_sized_spot_ecs_tags()


def test_gbb_linepack_capacity_adequacy_job_uses_rebuild_sized_ecs_task() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_linepack_capacity_adequacy import defs

    job = cast(UnresolvedAssetJobDefinition, next(iter(defs.jobs or ())))

    assert job.tags == rebuild_sized_spot_ecs_tags()


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
