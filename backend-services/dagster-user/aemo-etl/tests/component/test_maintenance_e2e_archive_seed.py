"""Component tests for deriving the e2e archive seed spec from Dagster defs."""

from aemo_etl.definitions import defs
from aemo_etl.maintenance.e2e_archive_seed import (
    build_gas_model_archive_seed_spec,
)


def test_gas_model_archive_seed_spec_uses_defs_asset_graph() -> None:
    spec = build_gas_model_archive_seed_spec(defs())
    source_table_ids = {source_table.table_id for source_table in spec.source_tables}
    zip_domains = {zip_domain.domain for zip_domain in spec.zip_domains}

    assert spec.target == "gas_model"
    assert "gbb.bronze_gasbb_facilities" in source_table_ids
    assert "sttm.bronze_int670_v1_registered_participants_rpt_1" in source_table_ids
    assert "vicgas.bronze_int041_v4_market_and_reference_prices_1" in source_table_ids
    assert zip_domains == {"gbb", "sttm", "vicgas"}
    assert all(
        source_table.archive_prefix == f"bronze/{source_table.domain}"
        for source_table in spec.source_tables
    )
    assert all(zip_domain.glob_pattern == "*.zip" for zip_domain in spec.zip_domains)
