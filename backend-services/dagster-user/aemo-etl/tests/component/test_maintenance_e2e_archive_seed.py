"""Component tests for deriving the e2e archive seed spec from Dagster defs."""

from aemo_etl.asset_organization import GAS_MODEL_TARGET_SELECTOR
from aemo_etl.definitions import defs
from aemo_etl.maintenance.e2e_archive_seed import (
    build_gas_model_archive_seed_spec,
)


def test_gas_model_archive_seed_spec_uses_defs_asset_graph() -> None:
    spec = build_gas_model_archive_seed_spec(defs())
    source_table_ids = {source_table.table_id for source_table in spec.source_tables}
    zip_domains = {zip_domain.domain for zip_domain in spec.zip_domains}

    assert spec.target == GAS_MODEL_TARGET_SELECTOR
    assert "gbb.bronze_gasbb_facilities" in source_table_ids
    assert "sttm.bronze_int670_v1_registered_participants_rpt_1" in source_table_ids
    assert "sttm.bronze_int691_v1_sttm_ctp_register_rpt_1" in source_table_ids
    assert "vicgas.bronze_int041_v4_market_and_reference_prices_1" in source_table_ids
    assert len(source_table_ids) == 111
    assert (
        sum(source_table.domain == "sttm" for source_table in spec.source_tables) == 34
    )
    assert zip_domains == {"gbb", "sttm", "vicgas"}
    assert all(
        source_table.archive_prefix == f"bronze/{source_table.domain}"
        for source_table in spec.source_tables
    )
    assert all(zip_domain.glob_pattern == "*.zip" for zip_domain in spec.zip_domains)
