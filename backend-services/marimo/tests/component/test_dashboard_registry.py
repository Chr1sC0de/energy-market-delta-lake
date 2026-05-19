"""Component tests for the Marimo dashboard registry."""

from pathlib import Path

import pytest

from marimoserver.dashboard_registry import (
    DASHBOARD_REGISTRY_RECORDS,
    ROADMAP_AUDIENCES,
    DashboardAudience,
    DashboardRegistryError,
    DashboardStatus,
    dashboard_registry,
    dashboard_registry_payload,
    load_dashboard_registry,
    registry_entry_by_concept_id,
)


REPO_ROOT = Path(__file__).resolve().parents[4]


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
    }
    assert required_fields <= set(entries[0])


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
    assert capacity.status is DashboardStatus.PLANNED
    assert capacity.notebook_route is None
    assert (
        "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md"
        in capacity.generated_gold_paths
    )
    assert "chunk-gbb-procedures-capacity-outlooks" in capacity.source_chunk_ids

    for generated_path in capacity.generated_gold_paths:
        assert (REPO_ROOT / generated_path).is_file()


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
