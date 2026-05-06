"""Bulk-import all individual GBB/VicGas table definition modules.

Each file has a single module-level statement:
    defs = df_from_s3_keys_definitions_factory(...)

Importing the module executes that statement and covers all lines in the file.
"""

import importlib
import pkgutil
from typing import cast

import bs4
from dagster import AssetKey, AssetsDefinition, Definitions
from dagster._core.definitions.unresolved_asset_job_definition import (
    UnresolvedAssetJobDefinition,
)
from polars import String

from aemo_etl.defs.raw.gbb._ecs import rebuild_sized_spot_ecs_tags

STTM_CORE_REPORT_SUFFIXES = (
    "int651_v1_ex_ante_market_price_rpt_1",
    "int652_v1_ex_ante_schedule_quantity_rpt_1",
    "int653_v3_ex_ante_pipeline_price_rpt_1",
    "int654_v1_provisional_market_price_rpt_1",
    "int655_v1_provisional_schedule_quantity_rpt_1",
    "int656_v2_provisional_pipeline_data_rpt_1",
    "int657_v2_ex_post_market_data_rpt_1",
    "int658_v1_latest_allocation_quantity_rpt_1",
    "int659_v1_bid_offer_rpt_1",
)


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


def test_sttm_core_source_table_specs_registered_for_archive_replay() -> None:
    from aemo_etl.factories.df_from_s3_keys.source_tables import (
        load_source_table_specs,
        select_source_table_specs,
    )

    specs = select_source_table_specs(
        load_source_table_specs(),
        domain="sttm",
    )

    assert tuple(spec.name_suffix for spec in specs) == STTM_CORE_REPORT_SUFFIXES
    for spec in specs:
        assert spec.domain == "sttm"
        assert spec.glob_pattern == f"{spec.name_suffix}*"
        assert spec.archive_prefix == "bronze/sttm"
        assert spec.target_table_uri("aemo") == (
            f"s3://aemo/bronze/sttm/bronze_{spec.name_suffix}"
        )
        assert spec.schema["gas_date"] == String

    (int659_spec,) = select_source_table_specs(
        specs,
        table="bronze/sttm/bronze_int659_v1_bid_offer_rpt_1",
    )
    assert int659_spec.surrogate_key_sources == (
        "gas_date",
        "schedule_identifier",
        "bid_offer_identifier",
        "bid_offer_step_number",
    )
    assert int659_spec.schema["step_capped_cumulative_qty"] == String


def test_sttm_event_driven_selection_includes_core_market_bronze_assets() -> None:
    from aemo_etl.definitions import STTM_ASSET_SELECTION

    asset_defs: list[AssetsDefinition] = []
    for suffix in STTM_CORE_REPORT_SUFFIXES:
        module = importlib.import_module(f"aemo_etl.defs.raw.sttm.{suffix}")
        asset_defs.extend(module.defs.assets or [])

    assert STTM_ASSET_SELECTION.resolve(asset_defs) == frozenset(
        AssetKey(["bronze", "sttm", f"bronze_{suffix}"])
        for suffix in STTM_CORE_REPORT_SUFFIXES
    )


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
