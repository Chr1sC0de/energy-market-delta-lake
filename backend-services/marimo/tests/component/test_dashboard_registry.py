"""Component tests for the Marimo dashboard registry."""

import json
from pathlib import Path

import pytest

import marimoserver.dashboard_registry as registry_module
from marimoserver.dashboard_registry import (
    DASHBOARD_REGISTRY_RECORDS,
    ROADMAP_AUDIENCES,
    DashboardAudience,
    DashboardRegistryError,
    DashboardStatus,
    SourceChunkReference,
    dashboard_registry,
    dashboard_registry_payload,
    load_dashboard_registry,
    registry_entry_by_concept_id,
)


REPO_ROOT = Path(__file__).resolve().parents[4]


def _gold_metadata(generated_path: str) -> dict[str, object]:
    text = (REPO_ROOT / generated_path).read_text(encoding="utf-8")
    _, raw_frontmatter, _ = text.split("---", maxsplit=2)
    metadata = json.loads(raw_frontmatter)
    assert isinstance(metadata, dict)
    return metadata


def _gold_source_chunk_ids(*generated_paths: str) -> tuple[str, ...]:
    source_chunk_ids: list[str] = []
    for generated_path in generated_paths:
        raw_chunk_ids = _gold_metadata(generated_path).get("source_chunk_ids", [])
        assert isinstance(raw_chunk_ids, list)
        for chunk_id in raw_chunk_ids:
            assert isinstance(chunk_id, str)
            if chunk_id not in source_chunk_ids:
                source_chunk_ids.append(chunk_id)
    return tuple(source_chunk_ids)


def _gold_source_hashes(*generated_paths: str) -> tuple[str, ...]:
    source_hashes: list[str] = []
    for generated_path in generated_paths:
        raw_hashes = _gold_metadata(generated_path).get("source_hashes", [])
        assert isinstance(raw_hashes, list)
        for source_hash in raw_hashes:
            assert isinstance(source_hash, str)
            if source_hash not in source_hashes:
                source_hashes.append(source_hash)
    return tuple(source_hashes)


def test_dashboard_registry_parses_structured_entries() -> None:
    entries = dashboard_registry()

    overview = registry_entry_by_concept_id("gas-market-overview", entries)
    missing = registry_entry_by_concept_id("missing-concept", entries)

    assert overview is not None
    assert overview.status is DashboardStatus.AVAILABLE
    assert overview.notebook_name == "sample_energy_market"
    assert overview.notebook_route == "/marimo/sample_energy_market/"
    assert "silver.gas_model.silver_gas_fact_market_price" in overview.backing_assets
    assert missing is None

    source_coverage = registry_entry_by_concept_id("source-coverage-matrix", entries)
    assert source_coverage is not None
    assert source_coverage.status is DashboardStatus.AVAILABLE
    assert source_coverage.notebook_name == "source_coverage_matrix"
    assert source_coverage.notebook_route == "/marimo/source_coverage_matrix/"
    assert DashboardAudience.DATA_ENGINEER in source_coverage.audiences
    assert "silver.gas_model.silver_gas_dim_facility" in (
        source_coverage.backing_assets
    )
    assert "silver.gas_model.silver_gas_fact_customer_transfer" in (
        source_coverage.backing_assets
    )

    lineage = registry_entry_by_concept_id("source-table-lineage-explorer", entries)
    assert lineage is not None
    assert lineage.status is DashboardStatus.AVAILABLE
    assert lineage.notebook_name == "source_table_lineage_explorer"
    assert lineage.notebook_route == "/marimo/source_table_lineage_explorer/"
    assert DashboardAudience.OPERATOR in lineage.audiences
    assert DashboardAudience.ANALYST in lineage.audiences
    assert DashboardAudience.DATA_ENGINEER in lineage.audiences
    assert "silver.gas_model.silver_gas_fact_market_price" in lineage.backing_assets
    assert lineage.generated_gold_paths == (
        "tools/gas-market-knowledge-base/generated/gold/README.md",
    )

    prices = registry_entry_by_concept_id("gas-market-prices", entries)
    assert prices is not None
    assert prices.status is DashboardStatus.AVAILABLE
    assert prices.notebook_name == "gas_market_prices"
    assert prices.notebook_route == "/marimo/gas_market_prices/"
    assert prices.backing_assets == ("silver.gas_model.silver_gas_fact_market_price",)
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md"
        in prices.generated_gold_paths
    )

    schedule_runs = registry_entry_by_concept_id("gas-schedule-runs", entries)
    assert schedule_runs is not None
    assert schedule_runs.status is DashboardStatus.AVAILABLE
    assert schedule_runs.notebook_name == "gas_schedule_runs"
    assert schedule_runs.notebook_route == "/marimo/gas_schedule_runs/"
    assert schedule_runs.backing_assets == (
        "silver.gas_model.silver_gas_fact_schedule_run",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/settlement.md"
        in schedule_runs.generated_gold_paths
    )

    scheduled_quantities = registry_entry_by_concept_id(
        "gas-scheduled-quantities",
        entries,
    )
    assert scheduled_quantities is not None
    assert scheduled_quantities.status is DashboardStatus.AVAILABLE
    assert scheduled_quantities.notebook_name == "gas_scheduled_quantities"
    assert scheduled_quantities.notebook_route == "/marimo/gas_scheduled_quantities/"
    assert scheduled_quantities.backing_assets == (
        "silver.gas_model.silver_gas_fact_scheduled_quantity",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md"
        in scheduled_quantities.generated_gold_paths
    )
    assert scheduled_quantities.source_chunk_ids == _gold_source_chunk_ids(
        *scheduled_quantities.generated_gold_paths,
    )

    settlement = registry_entry_by_concept_id("settlement-context", entries)
    assert settlement is not None
    assert settlement.status is DashboardStatus.AVAILABLE
    assert settlement.notebook_name == "gas_settlement_activity"
    assert settlement.notebook_route == "/marimo/gas_settlement_activity/"
    assert settlement.backing_assets == (
        "silver.gas_model.silver_gas_fact_settlement_activity",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/settlement.md"
        in settlement.generated_gold_paths
    )

    sttm_market_settlement = registry_entry_by_concept_id(
        "sttm-market-settlement",
        entries,
    )
    assert sttm_market_settlement is not None
    assert sttm_market_settlement.status is DashboardStatus.AVAILABLE
    assert sttm_market_settlement.notebook_name == "gas_sttm_market_settlement"
    assert (
        sttm_market_settlement.notebook_route == "/marimo/gas_sttm_market_settlement/"
    )
    assert sttm_market_settlement.backing_assets == (
        "silver.gas_model.silver_gas_fact_sttm_market_settlement",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/settlement.md"
        in sttm_market_settlement.generated_gold_paths
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/hub-zone.md"
        in sttm_market_settlement.generated_gold_paths
    )
    assert sttm_market_settlement.source_chunk_ids == _gold_source_chunk_ids(
        *sttm_market_settlement.generated_gold_paths,
    )

    sttm_capacity_settlement = registry_entry_by_concept_id(
        "sttm-capacity-settlement",
        entries,
    )
    assert sttm_capacity_settlement is not None
    assert sttm_capacity_settlement.status is DashboardStatus.AVAILABLE
    assert sttm_capacity_settlement.notebook_name == "gas_sttm_capacity_settlement"
    assert (
        sttm_capacity_settlement.notebook_route
        == "/marimo/gas_sttm_capacity_settlement/"
    )
    assert sttm_capacity_settlement.backing_assets == (
        "silver.gas_model.silver_gas_fact_sttm_capacity_settlement",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md"
        in sttm_capacity_settlement.generated_gold_paths
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/mos.md"
        in sttm_capacity_settlement.generated_gold_paths
    )
    assert sttm_capacity_settlement.source_chunk_ids == _gold_source_chunk_ids(
        *sttm_capacity_settlement.generated_gold_paths,
    )

    sttm_mos_allocation = registry_entry_by_concept_id(
        "sttm-mos-allocation",
        entries,
    )
    assert sttm_mos_allocation is not None
    assert sttm_mos_allocation.status is DashboardStatus.AVAILABLE
    assert sttm_mos_allocation.notebook_name == "gas_sttm_mos_allocation"
    assert sttm_mos_allocation.notebook_route == "/marimo/gas_sttm_mos_allocation/"
    assert sttm_mos_allocation.backing_assets == (
        "silver.gas_model.silver_gas_fact_sttm_mos_stack",
        "silver.gas_model.silver_gas_fact_sttm_allocation_quantity",
        "silver.gas_model.silver_gas_fact_sttm_allocation_limit",
        "silver.gas_model.silver_gas_fact_sttm_default_allocation_notice",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/mos.md"
        in sttm_mos_allocation.generated_gold_paths
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/allocation.md"
        in sttm_mos_allocation.generated_gold_paths
    )
    assert sttm_mos_allocation.source_chunk_ids == _gold_source_chunk_ids(
        *sttm_mos_allocation.generated_gold_paths,
    )

    readiness = registry_entry_by_concept_id("data-readiness-overview", entries)
    assert readiness is not None
    assert readiness.status is DashboardStatus.AVAILABLE
    assert readiness.notebook_name == "data_readiness_overview"
    assert readiness.notebook_route == "/marimo/data_readiness_overview/"
    assert DashboardAudience.PLATFORM_OPERATIONS in readiness.audiences
    assert DashboardAudience.OPERATOR in readiness.audiences
    assert DashboardAudience.DATA_ENGINEER in readiness.audiences

    bounded_read = registry_entry_by_concept_id(
        "aws-bounded-read-diagnostics",
        entries,
    )
    assert bounded_read is not None
    assert bounded_read.status is DashboardStatus.AVAILABLE
    assert bounded_read.notebook_name == "aws_bounded_read_diagnostics"
    assert bounded_read.notebook_route == "/marimo/aws_bounded_read_diagnostics/"
    assert bounded_read.backing_assets == ()
    assert DashboardAudience.PLATFORM_OPERATIONS in bounded_read.audiences
    assert DashboardAudience.OPERATOR in bounded_read.audiences
    assert DashboardAudience.DATA_ENGINEER in bounded_read.audiences

    catalogue_status = registry_entry_by_concept_id(
        "dagster-asset-catalogue-status",
        entries,
    )
    assert catalogue_status is not None
    assert catalogue_status.status is DashboardStatus.AVAILABLE
    assert catalogue_status.notebook_name == "dagster_asset_catalogue_status"
    assert catalogue_status.notebook_route == "/marimo/dagster_asset_catalogue_status/"
    assert DashboardAudience.PLATFORM_OPERATIONS in catalogue_status.audiences
    assert DashboardAudience.OPERATOR in catalogue_status.audiences
    assert DashboardAudience.DATA_ENGINEER in catalogue_status.audiences
    assert (
        "silver.gas_model.silver_gas_fact_market_price"
        in catalogue_status.backing_assets
    )

    freshness = registry_entry_by_concept_id("materialization-freshness", entries)
    assert freshness is not None
    assert freshness.status is DashboardStatus.AVAILABLE
    assert freshness.notebook_name == "materialization_freshness"
    assert freshness.notebook_route == "/marimo/materialization_freshness/"
    assert DashboardAudience.PLATFORM_OPERATIONS in freshness.audiences
    assert DashboardAudience.OPERATOR in freshness.audiences
    assert DashboardAudience.DATA_ENGINEER in freshness.audiences
    assert "silver.gas_model.silver_gas_fact_market_price" in (freshness.backing_assets)

    storage_health = registry_entry_by_concept_id("s3-bucket-health", entries)
    assert storage_health is not None
    assert storage_health.status is DashboardStatus.AVAILABLE
    assert storage_health.notebook_name == "s3_bucket_health"
    assert storage_health.notebook_route == "/marimo/s3_bucket_health/"
    assert storage_health.backing_assets == ()
    assert DashboardAudience.PLATFORM_OPERATIONS in storage_health.audiences
    assert DashboardAudience.OPERATOR in storage_health.audiences
    assert DashboardAudience.DATA_ENGINEER in storage_health.audiences

    glossary = registry_entry_by_concept_id("glossary-explorer", entries)
    assert glossary is not None
    assert glossary.status is DashboardStatus.AVAILABLE
    assert glossary.notebook_name == "glossary_explorer"
    assert glossary.notebook_route == "/marimo/glossary_explorer/"
    assert glossary.backing_assets == ()
    assert glossary.generated_gold_paths == (
        "tools/gas-market-knowledge-base/generated/gold/glossary/README.md",
    )
    assert glossary.source_chunk_ids == ()

    concept_asset = registry_entry_by_concept_id("concept-to-asset-explorer", entries)
    assert concept_asset is not None
    assert concept_asset.status is DashboardStatus.AVAILABLE
    assert concept_asset.notebook_name == "concept_to_asset_explorer"
    assert concept_asset.notebook_route == "/marimo/concept_to_asset_explorer/"
    assert concept_asset.backing_assets == ()
    assert concept_asset.generated_gold_paths == (
        "tools/gas-market-knowledge-base/generated/gold/glossary/README.md",
    )
    assert DashboardAudience.ANALYST in concept_asset.audiences
    assert DashboardAudience.DATA_ENGINEER in concept_asset.audiences

    data_dictionary = registry_entry_by_concept_id(
        "schema-data-dictionary-explorer",
        entries,
    )
    assert data_dictionary is not None
    assert data_dictionary.status is DashboardStatus.AVAILABLE
    assert data_dictionary.notebook_name == "schema_data_dictionary_explorer"
    assert data_dictionary.notebook_route == "/marimo/schema_data_dictionary_explorer/"
    assert data_dictionary.backing_assets == ()
    assert data_dictionary.generated_gold_paths == (
        "tools/gas-market-knowledge-base/generated/gold/glossary/README.md",
    )
    assert DashboardAudience.ANALYST in data_dictionary.audiences
    assert DashboardAudience.DATA_ENGINEER in data_dictionary.audiences
    assert DashboardAudience.OPERATOR in data_dictionary.audiences

    citation_chain = registry_entry_by_concept_id("citation-chain-explorer", entries)
    assert citation_chain is not None
    assert citation_chain.status is DashboardStatus.AVAILABLE
    assert citation_chain.notebook_name == "citation_chain_explorer"
    assert citation_chain.notebook_route == "/marimo/citation_chain_explorer/"
    assert citation_chain.backing_assets == ()
    assert citation_chain.generated_gold_paths == (
        "tools/gas-market-knowledge-base/generated/gold/README.md",
    )

    notices = registry_entry_by_concept_id("gas-system-notices", entries)
    assert notices is not None
    assert notices.status is DashboardStatus.AVAILABLE
    assert notices.notebook_name == "system_notices"
    assert notices.notebook_route == "/marimo/system_notices/"
    assert "silver.gas_model.silver_gas_fact_system_notice" in notices.backing_assets

    gas_quality = registry_entry_by_concept_id("gas-quality-composition", entries)
    assert gas_quality is not None
    assert gas_quality.status is DashboardStatus.AVAILABLE
    assert gas_quality.notebook_name == "gas_quality_composition"
    assert gas_quality.notebook_route == "/marimo/gas_quality_composition/"
    assert "silver.gas_model.silver_gas_fact_gas_quality" in gas_quality.backing_assets

    facility_flow_storage = registry_entry_by_concept_id(
        "facility-flow-storage",
        entries,
    )
    assert facility_flow_storage is not None
    assert facility_flow_storage.status is DashboardStatus.AVAILABLE
    assert facility_flow_storage.notebook_name == "facility_flow_storage"
    assert facility_flow_storage.notebook_route == "/marimo/facility_flow_storage/"
    assert facility_flow_storage.backing_assets == (
        "silver.gas_model.silver_gas_fact_facility_flow_storage",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/facility.md"
        in facility_flow_storage.generated_gold_paths
    )
    assert facility_flow_storage.source_chunk_ids == _gold_source_chunk_ids(
        *facility_flow_storage.generated_gold_paths,
    )

    forecast_actual = registry_entry_by_concept_id("forecast-vs-actual", entries)
    assert forecast_actual is not None
    assert forecast_actual.status is DashboardStatus.AVAILABLE
    assert forecast_actual.notebook_name == "forecast_vs_actual"
    assert forecast_actual.notebook_route == "/marimo/forecast_vs_actual/"
    assert forecast_actual.backing_assets == (
        "silver.gas_model.silver_gas_fact_nomination_forecast",
        "silver.gas_model.silver_gas_fact_facility_flow_storage",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md"
        in forecast_actual.generated_gold_paths
    )
    assert forecast_actual.source_chunk_ids == _gold_source_chunk_ids(
        *forecast_actual.generated_gold_paths,
    )

    customer_transfer = registry_entry_by_concept_id(
        "gas-customer-transfer-activity",
        entries,
    )
    assert customer_transfer is not None
    assert customer_transfer.status is DashboardStatus.AVAILABLE
    assert customer_transfer.notebook_name == "gas_customer_transfer_activity"
    assert customer_transfer.notebook_route == "/marimo/gas_customer_transfer_activity/"
    assert customer_transfer.backing_assets == (
        "silver.gas_model.silver_gas_fact_customer_transfer",
    )

    bid_stack = registry_entry_by_concept_id("bid-offer-context", entries)
    assert bid_stack is not None
    assert bid_stack.status is DashboardStatus.AVAILABLE
    assert bid_stack.notebook_name == "gas_bid_offer_stack"
    assert bid_stack.notebook_route == "/marimo/gas_bid_offer_stack/"
    assert bid_stack.backing_assets == ("silver.gas_model.silver_gas_fact_bid_stack",)

    contingency_gas = registry_entry_by_concept_id("sttm-contingency-gas", entries)
    assert contingency_gas is not None
    assert contingency_gas.status is DashboardStatus.AVAILABLE
    assert contingency_gas.notebook_name == "gas_sttm_contingency_gas"
    assert contingency_gas.notebook_route == "/marimo/gas_sttm_contingency_gas/"
    assert contingency_gas.backing_assets == (
        "silver.gas_model.silver_gas_fact_sttm_contingency_gas_call",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/bid-offer.md"
        in contingency_gas.generated_gold_paths
    )
    assert contingency_gas.source_chunk_ids == _gold_source_chunk_ids(
        *contingency_gas.generated_gold_paths,
    )

    participant = registry_entry_by_concept_id("participant-context", entries)
    assert participant is not None
    assert participant.status is DashboardStatus.AVAILABLE
    assert participant.notebook_name == "participant_explainer"
    assert participant.notebook_route == "/marimo/participant_explainer/"
    assert participant.backing_assets == (
        "silver.gas_model.silver_gas_dim_participant",
        "silver.gas_model.silver_gas_participant_market_membership",
        "silver.gas_model.silver_gas_dim_facility",
        "silver.gas_model.silver_gas_fact_bid_stack",
        "silver.gas_model.silver_gas_fact_settlement_activity",
    )
    assert participant.source_chunk_ids == _gold_source_chunk_ids(
        *participant.generated_gold_paths,
    )

    facility = registry_entry_by_concept_id("facility-context", entries)
    assert facility is not None
    assert facility.status is DashboardStatus.AVAILABLE
    assert facility.notebook_name == "facility_explainer"
    assert facility.notebook_route == "/marimo/facility_explainer/"
    assert facility.backing_assets == (
        "silver.gas_model.silver_gas_dim_facility",
        "silver.gas_model.silver_gas_fact_facility_flow_storage",
        "silver.gas_model.silver_gas_fact_capacity_outlook",
    )
    assert facility.source_chunk_ids == _gold_source_chunk_ids(
        *facility.generated_gold_paths,
    )

    hub_zone = registry_entry_by_concept_id("hub-zone-context", entries)
    assert hub_zone is not None
    assert hub_zone.status is DashboardStatus.AVAILABLE
    assert hub_zone.notebook_name == "hub_zone_explainer"
    assert hub_zone.notebook_route == "/marimo/hub_zone_explainer/"
    assert "silver.gas_model.silver_gas_dim_zone" in hub_zone.backing_assets
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/hub-zone.md"
        in hub_zone.generated_gold_paths
    )
    assert hub_zone.source_chunk_ids == _gold_source_chunk_ids(
        *hub_zone.generated_gold_paths,
    )

    connection_point = registry_entry_by_concept_id(
        "connection-point-context",
        entries,
    )
    assert connection_point is not None
    assert connection_point.status is DashboardStatus.AVAILABLE
    assert connection_point.notebook_name == "connection_point_explainer"
    assert connection_point.notebook_route == "/marimo/connection_point_explainer/"
    assert connection_point.backing_assets == (
        "silver.gas_model.silver_gas_dim_connection_point",
        "silver.gas_model.silver_gas_dim_facility",
        "silver.gas_model.silver_gas_dim_location",
        "silver.gas_model.silver_gas_dim_zone",
        "silver.gas_model.silver_gas_fact_connection_point_flow",
        "silver.gas_model.silver_gas_fact_capacity_outlook",
    )
    assert connection_point.generated_gold_paths == (
        "tools/gas-market-knowledge-base/generated/gold/glossary/connection-point.md",
    )
    assert connection_point.source_chunk_ids == _gold_source_chunk_ids(
        *connection_point.generated_gold_paths,
    )

    pipeline_connection = registry_entry_by_concept_id(
        "pipeline-connection-operations",
        entries,
    )
    assert pipeline_connection is not None
    assert pipeline_connection.status is DashboardStatus.AVAILABLE
    assert pipeline_connection.notebook_name == "pipeline_connection_operations"
    assert pipeline_connection.notebook_route == (
        "/marimo/pipeline_connection_operations/"
    )
    assert pipeline_connection.backing_assets == (
        "silver.gas_model.silver_gas_dim_connection_point",
        "silver.gas_model.silver_gas_dim_facility",
        "silver.gas_model.silver_gas_dim_pipeline_segment",
        "silver.gas_model.silver_gas_dim_zone",
        "silver.gas_model.silver_gas_fact_connection_point_flow",
        "silver.gas_model.silver_gas_fact_operational_meter_flow",
        "silver.gas_model.silver_gas_fact_capacity_outlook",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/connection-point.md"
        in pipeline_connection.generated_gold_paths
    )
    assert pipeline_connection.source_chunk_ids == _gold_source_chunk_ids(
        *pipeline_connection.generated_gold_paths,
    )

    meter_flow = registry_entry_by_concept_id("operational-meter-flow", entries)
    assert meter_flow is not None
    assert meter_flow.status is DashboardStatus.AVAILABLE
    assert meter_flow.notebook_name == "operational_meter_flow"
    assert meter_flow.notebook_route == "/marimo/operational_meter_flow/"
    assert meter_flow.backing_assets == (
        "silver.gas_model.silver_gas_fact_operational_meter_flow",
        "silver.gas_model.silver_gas_dim_operational_point",
        "silver.gas_model.silver_gas_dim_zone",
        "silver.gas_model.silver_gas_dim_pipeline_segment",
    )
    assert meter_flow.generated_gold_paths == (
        "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
    )
    assert meter_flow.source_chunk_ids == _gold_source_chunk_ids(
        *meter_flow.generated_gold_paths,
    )

    flow = registry_entry_by_concept_id("flow-context", entries)
    assert flow is not None
    assert flow.status is DashboardStatus.AVAILABLE
    assert flow.notebook_name == "flow_operations"
    assert flow.notebook_route == "/marimo/flow_operations/"
    assert flow.backing_assets == (
        "silver.gas_model.silver_gas_fact_connection_point_flow",
        "silver.gas_model.silver_gas_fact_facility_flow_storage",
        "silver.gas_model.silver_gas_fact_nomination_forecast",
        "silver.gas_model.silver_gas_fact_operational_meter_flow",
    )
    assert flow.generated_gold_paths == (
        "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
    )
    assert flow.source_chunk_ids == _gold_source_chunk_ids(
        *flow.generated_gold_paths,
    )

    linepack = registry_entry_by_concept_id("linepack-context", entries)
    assert linepack is not None
    assert linepack.status is DashboardStatus.AVAILABLE
    assert linepack.notebook_name == "linepack_adequacy"
    assert linepack.notebook_route == "/marimo/linepack_adequacy/"
    assert linepack.backing_assets == (
        "silver.gas_model.silver_gas_fact_linepack",
        "silver.gas_model.silver_gas_fact_linepack_balance",
    )
    assert linepack.generated_gold_paths == (
        "tools/gas-market-knowledge-base/generated/gold/glossary/linepack.md",
    )
    assert linepack.source_chunk_ids == _gold_source_chunk_ids(
        *linepack.generated_gold_paths,
    )


def test_dashboard_registry_payload_includes_required_fields() -> None:
    payload = dashboard_registry_payload()
    entries = payload["entries"]

    assert payload["schema_version"] == 1
    assert payload["audiences"] == [audience.value for audience in ROADMAP_AUDIENCES]
    assert isinstance(entries, list)
    assert entries

    required_fields = {
        "concept_id",
        "title",
        "description",
        "audiences",
        "status",
        "notebook_name",
        "notebook_route",
        "backing_assets",
        "generated_gold_paths",
        "source_chunks",
        "source_chunk_ids",
        "silver_chunk_paths",
        "source_hashes",
    }
    assert required_fields <= set(entries[0])
    assert {
        "chunk_id",
        "silver_chunk_path",
        "source_hash",
    } <= set(entries[0]["source_chunks"][0])


def test_dashboard_registry_covers_planned_and_available_status() -> None:
    statuses = {entry.status for entry in dashboard_registry()}

    assert statuses == {DashboardStatus.AVAILABLE, DashboardStatus.PLANNED}


def test_dashboard_registry_covers_each_roadmap_audience() -> None:
    audiences = {
        audience for entry in dashboard_registry() for audience in entry.audiences
    }

    assert set(ROADMAP_AUDIENCES) <= audiences


def test_dashboard_registry_keeps_gold_context_as_metadata_paths() -> None:
    capacity = registry_entry_by_concept_id("capacity-context")

    assert capacity is not None
    assert capacity.status is DashboardStatus.AVAILABLE
    assert capacity.notebook_name == "capacity_outlook"
    assert capacity.notebook_route == "/marimo/capacity_outlook/"
    assert capacity.backing_assets == (
        "silver.gas_model.silver_gas_fact_capacity_outlook",
    )
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md"
        in capacity.generated_gold_paths
    )
    assert capacity.source_chunk_ids == _gold_source_chunk_ids(
        *capacity.generated_gold_paths,
    )
    assert set(capacity.source_hashes) == set(
        _gold_source_hashes(*capacity.generated_gold_paths),
    )

    for generated_path in capacity.generated_gold_paths:
        assert (REPO_ROOT / generated_path).is_file()

    for chunk_id, silver_chunk_path in zip(
        capacity.source_chunk_ids,
        capacity.silver_chunk_paths,
        strict=True,
    ):
        assert silver_chunk_path.endswith(f"{chunk_id}.md")
        assert (REPO_ROOT / silver_chunk_path).is_file()


def test_dashboard_registry_parsing_rejects_missing_required_field() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    del record["concept_id"]

    with pytest.raises(DashboardRegistryError, match="concept_id"):
        load_dashboard_registry([record])


def test_dashboard_registry_parsing_rejects_non_string_field() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["title"] = 5

    with pytest.raises(DashboardRegistryError, match="title must be a string"):
        load_dashboard_registry([record])


def test_dashboard_registry_parsing_rejects_blank_required_field() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["title"] = "  "

    with pytest.raises(DashboardRegistryError, match="title"):
        load_dashboard_registry([record])


def test_dashboard_registry_parsing_rejects_unknown_status() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["status"] = "draft"

    with pytest.raises(DashboardRegistryError, match="unknown status"):
        load_dashboard_registry([record])


def test_dashboard_registry_parsing_rejects_unknown_audience() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["audiences"] = ("unknown-audience",)

    with pytest.raises(DashboardRegistryError, match="unknown audience"):
        load_dashboard_registry([record])


def test_dashboard_registry_parsing_rejects_empty_audience_tuple() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["audiences"] = ()

    with pytest.raises(DashboardRegistryError, match="must not be empty"):
        load_dashboard_registry([record])


def test_dashboard_registry_requires_available_notebooks() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    del record["notebook_name"]

    with pytest.raises(DashboardRegistryError, match="available"):
        load_dashboard_registry([record])


def test_dashboard_registry_rejects_empty_records() -> None:
    with pytest.raises(DashboardRegistryError, match="must contain entries"):
        load_dashboard_registry([])


def test_dashboard_registry_rejects_duplicate_concepts() -> None:
    records = _registry_records()
    records[1]["concept_id"] = records[0]["concept_id"]

    with pytest.raises(DashboardRegistryError, match="duplicate concept_id"):
        load_dashboard_registry(records)


def test_dashboard_registry_requires_planned_and_available_entries() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])

    with pytest.raises(DashboardRegistryError, match="planned and available"):
        load_dashboard_registry([record])


def test_dashboard_registry_requires_each_roadmap_audience() -> None:
    records = _registry_records()
    for record in records:
        audiences = record["audiences"]
        assert isinstance(audiences, tuple)
        record["audiences"] = tuple(
            audience for audience in audiences if audience != "data-engineer"
        )

    with pytest.raises(DashboardRegistryError, match="audience coverage"):
        load_dashboard_registry(records)


def test_dashboard_registry_rejects_non_slug_concept_id() -> None:
    records = _registry_records()
    records[0]["concept_id"] = "bad slug"

    with pytest.raises(DashboardRegistryError, match="slug-like"):
        load_dashboard_registry(records)


def test_dashboard_registry_rejects_non_gas_model_backing_asset() -> None:
    records = _registry_records()
    records[0]["backing_assets"] = ("bronze.gas_model.raw_table",)

    with pytest.raises(DashboardRegistryError, match="outside silver.gas_model"):
        load_dashboard_registry(records)


def test_dashboard_registry_rejects_gold_paths_without_source_chunks() -> None:
    records = _registry_records()
    records[-1]["generated_gold_paths"] = (
        "tools/gas-market-knowledge-base/generated/gold/glossary/missing-context.md",
    )
    records[-1]["source_chunk_ids"] = ()

    with pytest.raises(DashboardRegistryError, match="without source chunks"):
        load_dashboard_registry(records)


def test_dashboard_registry_allows_index_gold_path_without_source_chunks() -> None:
    records = _registry_records()
    records[0]["concept_id"] = "index-context"
    records[0]["generated_gold_paths"] = (
        "tools/gas-market-knowledge-base/generated/gold/glossary/README.md",
    )
    records[0]["source_chunk_ids"] = ()

    entries = load_dashboard_registry(records)

    index = registry_entry_by_concept_id("index-context", entries)
    assert index is not None
    assert index.generated_gold_paths == records[0]["generated_gold_paths"]
    assert index.source_chunk_ids == ()


def test_dashboard_registry_parses_structured_source_chunks() -> None:
    records = _registry_records()
    records[0]["concept_id"] = "structured-context"
    records[0]["source_chunks"] = (
        {
            "chunk_id": "chunk-structured",
            "silver_chunk_path": (
                "tools/gas-market-knowledge-base/generated/silver/chunks/"
                "structured/chunk-structured.md"
            ),
            "source_hash": "structured-source-hash",
        },
    )

    entries = load_dashboard_registry(records)
    structured = registry_entry_by_concept_id("structured-context", entries)

    assert structured is not None
    assert structured.source_chunk_ids == ("chunk-structured",)
    assert structured.silver_chunk_paths == (
        "tools/gas-market-knowledge-base/generated/silver/chunks/"
        "structured/chunk-structured.md",
    )
    assert structured.source_hashes == ("structured-source-hash",)
    assert structured.source_chunks[0].complete


def test_dashboard_registry_resolves_legacy_source_chunk_references() -> None:
    known = registry_module._source_chunk_reference_by_id("chunk-gbb-guide-gas-day")
    unknown = registry_module._source_chunk_reference_by_id("chunk-unknown")

    assert known.chunk_id == "chunk-gbb-guide-gas-day"
    assert known.complete
    assert unknown == SourceChunkReference(chunk_id="chunk-unknown")


def test_dashboard_registry_repo_root_finds_checkout_root(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    index_path = (
        repo_root
        / "tools/gas-market-knowledge-base/generated/silver/index/chunks.jsonl"
    )
    index_path.parent.mkdir(parents=True)
    index_path.write_text("", encoding="utf-8")
    module_path = (
        repo_root / "backend-services/marimo/src/marimoserver/dashboard_registry.py"
    )

    assert registry_module._repo_root_for_module(module_path) == repo_root


def test_dashboard_registry_repo_root_falls_back_for_packaged_image_path(
    tmp_path: Path,
) -> None:
    module_path = tmp_path / "opt/marimo/marimoserver/dashboard_registry.py"

    assert registry_module._repo_root_for_module(module_path) == (
        tmp_path / "opt/marimo"
    )


def test_dashboard_registry_repo_root_preserves_source_checkout_depth(
    tmp_path: Path,
) -> None:
    repo_root = tmp_path / "repo"
    module_path = (
        repo_root / "backend-services/marimo/src/marimoserver/dashboard_registry.py"
    )

    assert registry_module._repo_root_for_module(module_path) == repo_root


def test_dashboard_registry_repo_root_handles_shallow_module_paths() -> None:
    assert registry_module._repo_root_for_module(Path("/opt/module.py")) == Path("/")
    assert registry_module._repo_root_for_module(Path("/module.py")) == Path("/")


def test_dashboard_registry_reads_generated_chunk_index_defensively(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    index_path = tmp_path / "chunks.jsonl"
    index_path.write_text(
        "\n".join(
            (
                "",
                '"not a mapping"',
                json.dumps({"chunk_id": "missing-fields"}),
                json.dumps(
                    {
                        "chunk_id": "chunk-valid",
                        "path": "generated/silver/chunks/x/chunk-valid.md",
                        "content_sha256": "source-hash",
                    }
                ),
            )
        ),
        encoding="utf-8",
    )
    registry_module._generated_source_chunk_references_by_id.cache_clear()
    monkeypatch.setattr(registry_module, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry_module, "_SILVER_CHUNK_INDEX_PATH", "chunks.jsonl")

    try:
        references = registry_module._generated_source_chunk_references_by_id()
    finally:
        registry_module._generated_source_chunk_references_by_id.cache_clear()

    assert tuple(references) == ("chunk-valid",)
    assert references["chunk-valid"].silver_chunk_path == (
        "tools/gas-market-knowledge-base/generated/silver/chunks/x/chunk-valid.md"
    )
    assert references["chunk-valid"].source_hash == "source-hash"


def test_dashboard_registry_rejects_invalid_generated_chunk_index_json(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "chunks.jsonl").write_text("{not-json", encoding="utf-8")
    registry_module._generated_source_chunk_references_by_id.cache_clear()
    monkeypatch.setattr(registry_module, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry_module, "_SILVER_CHUNK_INDEX_PATH", "chunks.jsonl")

    try:
        with pytest.raises(DashboardRegistryError, match="not valid JSON"):
            registry_module._generated_source_chunk_references_by_id()
    finally:
        registry_module._generated_source_chunk_references_by_id.cache_clear()


def test_dashboard_registry_generated_gold_metadata_handles_absent_or_invalid_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(registry_module, "_REPO_ROOT", tmp_path)
    (tmp_path / "plain.md").write_text("# Plain", encoding="utf-8")
    (tmp_path / "unterminated.md").write_text("---\n{}", encoding="utf-8")
    (tmp_path / "empty.md").write_text("---\n\n---\n", encoding="utf-8")
    (tmp_path / "list.md").write_text("---\n[]\n---\n", encoding="utf-8")

    assert registry_module._generated_gold_metadata("missing.md") == {}
    assert registry_module._generated_gold_metadata("plain.md") == {}
    assert registry_module._generated_gold_metadata("unterminated.md") == {}
    assert registry_module._generated_gold_metadata("empty.md") == {}
    assert registry_module._generated_gold_metadata("list.md") == {}


def test_dashboard_registry_validates_generated_gold_source_chunk_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    (tmp_path / "chunks.jsonl").write_text(
        json.dumps(
            {
                "chunk_id": "chunk-valid",
                "path": "generated/silver/chunks/x/chunk-valid.md",
                "content_sha256": "source-hash",
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "not-list.md").write_text(
        '---\n{"source_chunk_ids": "chunk-valid"}\n---\n',
        encoding="utf-8",
    )
    (tmp_path / "not-string.md").write_text(
        '---\n{"source_chunk_ids": [5]}\n---\n',
        encoding="utf-8",
    )
    (tmp_path / "valid.md").write_text(
        '---\n{"source_chunk_ids": ["chunk-valid", "chunk-valid", "chunk-missing"]}\n---\n',
        encoding="utf-8",
    )
    registry_module._generated_source_chunk_references_by_id.cache_clear()
    monkeypatch.setattr(registry_module, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry_module, "_SILVER_CHUNK_INDEX_PATH", "chunks.jsonl")

    try:
        with pytest.raises(DashboardRegistryError, match="must be a list"):
            registry_module._source_chunks_from_generated_gold_paths(
                ("not-list.md",), 1
            )
        with pytest.raises(DashboardRegistryError, match="must contain strings"):
            registry_module._source_chunks_from_generated_gold_paths(
                ("not-string.md",),
                1,
            )

        source_chunks = registry_module._source_chunks_from_generated_gold_paths(
            ("valid.md",),
            1,
        )
    finally:
        registry_module._generated_source_chunk_references_by_id.cache_clear()

    assert tuple(chunk.chunk_id for chunk in source_chunks) == (
        "chunk-valid",
        "chunk-missing",
    )
    assert source_chunks[0].complete
    assert not source_chunks[1].complete


def test_dashboard_registry_ignores_generated_gold_paths_without_chunk_index(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry_module._generated_source_chunk_references_by_id.cache_clear()
    monkeypatch.setattr(registry_module, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(registry_module, "_SILVER_CHUNK_INDEX_PATH", "missing.jsonl")

    try:
        assert (
            registry_module._source_chunks_from_generated_gold_paths(
                ("missing.md",),
                1,
            )
            == ()
        )
    finally:
        registry_module._generated_source_chunk_references_by_id.cache_clear()


def test_dashboard_registry_rejects_non_tuple_source_chunks() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["source_chunks"] = []

    with pytest.raises(DashboardRegistryError, match="source_chunks must be a tuple"):
        load_dashboard_registry([record])


def test_dashboard_registry_rejects_non_mapping_source_chunk_records() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["source_chunks"] = ("chunk-only",)

    with pytest.raises(
        DashboardRegistryError,
        match="source_chunks must contain mapping records",
    ):
        load_dashboard_registry([record])


def test_dashboard_registry_rejects_empty_required_tuple() -> None:
    records = _registry_records()
    records[0]["backing_assets"] = ()

    with pytest.raises(DashboardRegistryError, match="must not be empty"):
        load_dashboard_registry(records)


def test_dashboard_registry_rejects_non_tuple_sequence_field() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["backing_assets"] = ["silver.gas_model.table"]

    with pytest.raises(DashboardRegistryError, match="must be a tuple"):
        load_dashboard_registry([record])


def test_dashboard_registry_rejects_non_string_tuple_item() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["backing_assets"] = (5,)

    with pytest.raises(DashboardRegistryError, match="must contain strings"):
        load_dashboard_registry([record])


def test_dashboard_registry_rejects_blank_tuple_item() -> None:
    record = dict(DASHBOARD_REGISTRY_RECORDS[0])
    record["backing_assets"] = (" ",)

    with pytest.raises(DashboardRegistryError, match="contains a blank"):
        load_dashboard_registry([record])


def _registry_records() -> list[dict[str, object]]:
    return [dict(record) for record in DASHBOARD_REGISTRY_RECORDS]
