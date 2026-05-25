"""Bulk-import all individual GBB/VicGas table definition modules.

Each file has a single module-level statement:
    defs = df_from_s3_keys_definitions_factory(...)

Importing the module executes that statement and covers all lines in the file.
"""

import importlib
import importlib.util
import io
import pkgutil
from datetime import datetime, timezone
from typing import cast

import bs4
from dagster import AssetKey, AssetsDefinition, Definitions
from dagster._core.definitions.unresolved_asset_job_definition import (
    UnresolvedAssetJobDefinition,
)
import polars as pl
from polars import String

from aemo_etl.asset_organization import (
    SOURCE_REPORT_FAMILIES,
    SOURCE_TABLE_REPORT_FAMILY_BY_DOMAIN,
    source_table_group_name,
)
from aemo_etl.defs.raw.gbb._ecs import (
    oom_recovery_spot_ecs_tags,
    pipeline_connection_flow_v2_hotfix_ecs_tags,
    rebuild_sized_spot_ecs_tags,
)

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
    "int660_v1_contingency_gas_bids_and_offers_rpt_1",
    "int661_v1_contingency_gas_called_scheduled_bid_offer_rpt_1",
    "int662_v1_provisional_deviation_rpt_1",
    "int663_v1_provisional_variation_rpt_1",
    "int664_v1_daily_provisional_mos_allocation_rpt_1",
    "int665_v1_mos_stack_data_rpt_1",
    "int666_v1_market_notice_rpt_1",
    "int667_v1_market_parameters_rpt_1",
    "int668_v1_schedule_log_rpt_1",
    "int669_v1_settlement_version_rpt_1",
    "int670_v1_registered_participants_rpt_1",
    "int671_v1_hub_facility_definition_rpt_1",
    "int672_v1_cumulative_price_rpt_1",
    "int673_v1_total_contingency_bid_offer_rpt_1",
    "int674_v1_total_contingency_gas_schedules_rpt_1",
    "int675_v1_default_allocation_notice_rpt_1",
    "int676_v1_rolling_average_price_rpt_1",
    "int677_v1_contingency_gas_price_rpt_1",
    "int678_v1_net_market_balance_daily_amounts_rpt_1",
    "int679_v1_net_market_balance_settlement_amounts_rpt_1",
    "int680_v1_dp_flag_data_rpt_1",
    "int681_v1_daily_provisional_capacity_data_rpt_1",
    "int682_v1_settlement_mos_and_capacity_data_rpt_1",
    "int683_v1_provisional_used_mos_steps_rpt_1",
    "int684_v1_settlement_used_mos_steps_rpt_1",
    "int687_v1_facility_hub_capacity_data_rpt_1",
    "int688_v1_allocation_warning_limit_thresholds_rpt_1",
    "int689_v1_expost_allocation_quantity_rpt_1",
    "int690_v1_deviation_price_data_rpt_1",
    "int691_v1_sttm_ctp_register_rpt_1",
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
        if "gas_date" in spec.schema:
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

    (int660_spec,) = select_source_table_specs(
        specs,
        table="bronze/sttm/bronze_int660_v1_contingency_gas_bids_and_offers_rpt_1",
    )
    assert int660_spec.surrogate_key_sources == (
        "gas_date",
        "contingency_gas_bid_offer_identifier",
        "contingency_gas_bid_offer_step_number",
    )
    assert int660_spec.schema["contingency_gas_bid_offer_step_quantity"] == String

    (int667_spec,) = select_source_table_specs(
        specs,
        table="sttm.bronze_int667_v1_market_parameters_rpt_1",
    )
    assert int667_spec.surrogate_key_sources == (
        "effective_from_date",
        "effective_to_date",
        "parameter_code",
    )
    assert int667_spec.schema["parameter_value"] == String

    (int669_spec,) = select_source_table_specs(
        specs,
        table="int669_v1_settlement_version_rpt_1",
    )
    assert int669_spec.surrogate_key_sources == ("settlement_run_identifier",)
    assert int669_spec.schema["settlement_run_desc"] == String

    (int670_spec,) = select_source_table_specs(
        specs,
        table="sttm.bronze_int670_v1_registered_participants_rpt_1",
    )
    assert int670_spec.surrogate_key_sources == (
        "hub_identifier",
        "company_identifier",
        "organisation_registration_type",
        "registered_capacity",
    )
    assert int670_spec.schema["registration_status"] == String

    (int674_spec,) = select_source_table_specs(
        specs,
        table="bronze/sttm/bronze_int674_v1_total_contingency_gas_schedules_rpt_1",
    )
    assert int674_spec.surrogate_key_sources == (
        "gas_date",
        "hub_identifier",
        "facility_identifier",
        "flow_direction",
        "contingency_gas_bid_offer_type",
    )
    assert int674_spec.schema["contingency_gas_bid_offer_called_quantity"] == String

    (int678_spec,) = select_source_table_specs(
        specs,
        table="int678_v1_net_market_balance_daily_amounts_rpt_1",
    )
    assert int678_spec.surrogate_key_sources == (
        "period_start_date",
        "period_end_date",
        "hub_identifier",
    )
    assert int678_spec.schema["net_market_balance"] == String

    (int679_spec,) = select_source_table_specs(
        specs,
        table="sttm.bronze_int679_v1_net_market_balance_settlement_amounts_rpt_1",
    )
    assert int679_spec.surrogate_key_sources == (
        "settlement_run_identifier",
        "hub_identifier",
    )
    assert int679_spec.schema["total_withdrawals"] == String

    (int682_spec,) = select_source_table_specs(
        specs,
        table="sttm.bronze_int682_v1_settlement_mos_and_capacity_data_rpt_1",
    )
    assert int682_spec.surrogate_key_sources == (
        "settlement_run_identifier",
        "gas_date",
        "hub_identifier",
        "facility_identifier",
    )
    assert int682_spec.schema["mos_allocated_qty"] == String

    (int689_spec,) = select_source_table_specs(
        specs,
        table="int689_v1_expost_allocation_quantity_rpt_1",
    )
    assert int689_spec.surrogate_key_sources == (
        "gas_date",
        "facility_identifier",
        "flow_direction",
    )
    assert int689_spec.schema["allocation_qty_quality_type"] == String

    (int690_spec,) = select_source_table_specs(
        specs,
        table="bronze/sttm/bronze_int690_v1_deviation_price_data_rpt_1",
    )
    assert int690_spec.surrogate_key_sources == ("gas_date", "hub_identifier")
    assert int690_spec.schema["positive_deviation_price"] == String

    (int691_spec,) = select_source_table_specs(
        specs,
        table="sttm.bronze_int691_v1_sttm_ctp_register_rpt_1",
    )
    assert int691_spec.surrogate_key_sources == (
        "hub_identifier",
        "facility_identifier",
        "ctp_identifier",
    )


def test_source_table_specs_have_complete_source_report_family_assignments() -> None:
    from aemo_etl.factories.df_from_s3_keys.source_tables import (
        load_source_table_specs,
    )

    specs_by_id = {
        (spec.domain, spec.name_suffix): spec
        for spec in load_source_table_specs()
        if spec.domain in SOURCE_TABLE_REPORT_FAMILY_BY_DOMAIN
    }
    expected_ids = {
        (domain, name_suffix)
        for domain, source_tables in SOURCE_TABLE_REPORT_FAMILY_BY_DOMAIN.items()
        for name_suffix in source_tables
    }

    assert set(specs_by_id) == expected_ids
    for spec in specs_by_id.values():
        assert spec.report_family in SOURCE_REPORT_FAMILIES
        assert (
            source_table_group_name(
                domain=spec.domain,
                name_suffix=spec.name_suffix,
            )
            == f"gas_{spec.domain}_{spec.report_family}"
        )


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


def test_sttm_landing_only_gap_modules_are_not_typed_source_tables() -> None:
    assert (
        importlib.util.find_spec("aemo_etl.defs.raw.sttm.int685_v1_sttm_prices_rpt_13")
        is None
    )
    assert (
        importlib.util.find_spec("aemo_etl.defs.raw.sttm.int685b_v1_sttm_prices_rpt_13")
        is None
    )


def test_gbb_pipeline_connection_flow_v1_job_uses_rebuild_sized_ecs_task() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_pipeline_connection_flow_v1 import defs

    job = cast(UnresolvedAssetJobDefinition, next(iter(defs.jobs or ())))

    assert job.tags == rebuild_sized_spot_ecs_tags()


def test_gbb_pipeline_connection_flow_v2_job_uses_hotfix_sized_ecs_task() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_pipeline_connection_flow_v2 import defs

    job = cast(UnresolvedAssetJobDefinition, next(iter(defs.jobs or ())))

    assert job.tags == pipeline_connection_flow_v2_hotfix_ecs_tags()


def test_gbb_actual_flow_storage_job_uses_oom_recovery_ecs_task() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_actual_flow_storage import defs

    job = cast(UnresolvedAssetJobDefinition, next(iter(defs.jobs or ())))

    assert job.tags == oom_recovery_spot_ecs_tags()


def test_gbb_nomination_and_forecast_job_uses_oom_recovery_ecs_task() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_nomination_and_forecast import defs

    job = cast(UnresolvedAssetJobDefinition, next(iter(defs.jobs or ())))

    assert job.tags == oom_recovery_spot_ecs_tags()


def test_gbb_nameplate_rating_key_distinguishes_location_names() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_nameplate_rating_hook import defs

    asset = next(
        asset for asset in defs.assets or () if isinstance(asset, AssetsDefinition)
    )
    assert isinstance(asset, AssetsDefinition)
    (asset_key,) = asset.keys

    assert asset.metadata_by_key[asset_key]["surrogate_key_sources"] == [
        "facilityid",
        "capacitytype",
        "flowdirection",
        "effectivedate",
        "lastupdated",
        "receiptlocation",
        "receiptlocationname",
        "deliverylocation",
        "deliverylocationname",
    ]


def test_gbb_medium_term_capacity_outlook_key_distinguishes_location_names() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_medium_term_capacity_outlook import defs

    asset = next(
        asset for asset in defs.assets or () if isinstance(asset, AssetsDefinition)
    )
    assert isinstance(asset, AssetsDefinition)
    (asset_key,) = asset.keys

    assert asset.metadata_by_key[asset_key]["surrogate_key_sources"] == [
        "FromGasDate",
        "ToGasDate",
        "FacilityId",
        "CapacityType",
        "FlowDirection",
        "ReceiptLocation",
        "ReceiptLocationName",
        "DeliveryLocation",
        "DeliveryLocationName",
        "LastUpdated",
    ]


def test_gbb_gsh_gas_trades_key_distinguishes_trade_price_and_quantity() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_gsh_gas_trades_hook import defs

    asset = next(
        asset for asset in defs.assets or () if isinstance(asset, AssetsDefinition)
    )
    assert isinstance(asset, AssetsDefinition)
    (asset_key,) = asset.keys

    assert asset.metadata_by_key[asset_key]["surrogate_key_sources"] == [
        "TRADE_DATE",
        "TYPE",
        "PRODUCT",
        "LOCATION",
        "TRADE_PRICE",
        "DAILY_QTY_GJ",
        "START_DATE",
        "END_DATE",
        "MANUAL_TRADE",
    ]


def test_gbb_field_interest_v2_key_distinguishes_group_members() -> None:
    from aemo_etl.defs.raw.gbb.gasbb_field_interest_v2 import defs
    from aemo_etl.factories.df_from_s3_keys.source_tables import (
        load_source_table_specs,
        select_source_table_specs,
    )

    expected_key_sources = [
        "FieldInterestId",
        "CompanyId",
        "EffectiveDate",
        "GroupMembers",
    ]
    asset = next(
        asset for asset in defs.assets or () if isinstance(asset, AssetsDefinition)
    )
    assert isinstance(asset, AssetsDefinition)
    (asset_key,) = asset.keys

    assert asset.metadata_by_key[asset_key]["surrogate_key_sources"] == (
        expected_key_sources
    )

    (spec,) = select_source_table_specs(
        load_source_table_specs(),
        table="gbb.bronze_gasbb_field_interest_v2",
    )
    assert spec.surrogate_key_sources == tuple(expected_key_sources)


def test_gbb_field_interest_v2_group_member_rows_have_distinct_keys() -> None:
    from aemo_etl.factories.df_from_s3_keys.assets import (
        source_table_bronze_frame_from_bytes,
    )
    from aemo_etl.factories.df_from_s3_keys.current_state import (
        collapse_current_state_batch,
    )
    from aemo_etl.factories.df_from_s3_keys.source_tables import (
        load_source_table_specs,
        select_source_table_specs,
    )

    (spec,) = select_source_table_specs(
        load_source_table_specs(),
        table="gbb.bronze_gasbb_field_interest_v2",
    )
    source = pl.DataFrame(
        {
            "FieldName": ["PL 275", "PL 275"],
            "FieldInterestId": [840099, 840099],
            "CompanyId": [106, 106],
            "CompanyName": ["QGC Pty Limited", "QGC Pty Limited"],
            "GroupMembers": ["BG International Ltd", "QGC Upstream Holdings Pty Ltd"],
            "PercentageShare": ["20.625", "20.0"],
            "EffectiveDate": ["2023/03/15", "2023/03/15"],
        }
    )
    buffer = io.BytesIO()
    source.write_parquet(buffer)

    batch = source_table_bronze_frame_from_bytes(
        s3_bucket="landing",
        s3_key="bronze/gbb/gasbbgasfieldinterest~260522133726.parquet",
        object_bytes=buffer.getvalue(),
        schema=spec.schema,
        surrogate_key_sources=spec.surrogate_key_sources,
        current_time=datetime(2026, 5, 22, tzinfo=timezone.utc),
        source_file_bucket="archive",
    )

    collapsed = collapse_current_state_batch(batch).collect()

    assert collapsed.height == 2
    assert collapsed["surrogate_key"].n_unique() == 2


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
