"""Code-local registry for curated and planned Marimo gas dashboards."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from functools import cache


class DashboardRegistryError(ValueError):
    """Raised when dashboard registry records are incomplete or invalid."""


class DashboardStatus(StrEnum):
    """Lifecycle state for a dashboard registry entry."""

    AVAILABLE = "available"
    PLANNED = "planned"


class DashboardAudience(StrEnum):
    """Roadmap audience tags used by the Marimo concept gallery."""

    PLATFORM_OPERATIONS = "platform-operations"
    OPERATOR = "operator"
    ANALYST = "analyst"
    STAKEHOLDER = "stakeholder"
    DATA_ENGINEER = "data-engineer"


ROADMAP_AUDIENCES: tuple[DashboardAudience, ...] = (
    DashboardAudience.PLATFORM_OPERATIONS,
    DashboardAudience.OPERATOR,
    DashboardAudience.ANALYST,
    DashboardAudience.STAKEHOLDER,
    DashboardAudience.DATA_ENGINEER,
)

type DashboardRegistryRecord = Mapping[str, object]

_MISSING = object()
_REGISTRY_BACKED_CONCEPT_IDS = frozenset(
    {
        "aws-bounded-read-diagnostics",
        "citation-chain-explorer",
        "concept-to-asset-explorer",
        "glossary-explorer",
        "s3-bucket-health",
        "schema-data-dictionary-explorer",
    }
)


@dataclass(frozen=True)
class SourceChunkReference:
    """Stable source chunk lineage copied from generated corpus metadata."""

    chunk_id: str
    silver_chunk_path: str | None = None
    source_hash: str | None = None

    @property
    def complete(self) -> bool:
        """Return whether this source chunk has its full registry citation chain."""
        return self.silver_chunk_path is not None and self.source_hash is not None

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-serializable source chunk reference."""
        return {
            "chunk_id": self.chunk_id,
            "silver_chunk_path": self.silver_chunk_path,
            "source_hash": self.source_hash,
        }


def _source_chunk_reference(
    chunk_id: str,
    corpus: str,
    document_path: str,
    source_hash: str,
) -> SourceChunkReference:
    return SourceChunkReference(
        chunk_id=chunk_id,
        silver_chunk_path=(
            "tools/gas-market-knowledge-base/generated/silver/chunks/"
            f"{corpus}/{document_path}/sha256-{source_hash}/{chunk_id}.md"
        ),
        source_hash=source_hash,
    )


SOURCE_CHUNK_REFERENCES: tuple[SourceChunkReference, ...] = (
    _source_chunk_reference(
        "chunk-dwgm-operations-capacity-certificates-modelling",
        "dwgm",
        "operations-procedures-2026",
        "dac5b2d83b332770261fdfb80ab07389611cc06cb1f48a2886bf1e9097d1fe07",
    ),
    _source_chunk_reference(
        "chunk-dwgm-operations-capacity-certificates-purpose",
        "dwgm",
        "operations-procedures-2026",
        "dac5b2d83b332770261fdfb80ab07389611cc06cb1f48a2886bf1e9097d1fe07",
    ),
    _source_chunk_reference(
        "chunk-dwgm-operations-glossary-schedule",
        "dwgm",
        "operations-procedures-2026",
        "dac5b2d83b332770261fdfb80ab07389611cc06cb1f48a2886bf1e9097d1fe07",
    ),
    _source_chunk_reference(
        "chunk-dwgm-settlement-pricing-schedule-allocation",
        "dwgm",
        "settlement-procedures-2024",
        "7318c369099f952b1b8264e72e71908d741d07d917f303d135e7b507ea5f2eb8",
    ),
    _source_chunk_reference(
        "chunk-dwgm-settlement-purpose",
        "dwgm",
        "settlement-procedures-2024",
        "7318c369099f952b1b8264e72e71908d741d07d917f303d135e7b507ea5f2eb8",
    ),
    _source_chunk_reference(
        "chunk-dwgm-settlement-withdrawal-allocation",
        "dwgm",
        "settlement-procedures-2024",
        "7318c369099f952b1b8264e72e71908d741d07d917f303d135e7b507ea5f2eb8",
    ),
    _source_chunk_reference(
        "chunk-gbb-guide-connection-point-identifiers",
        "gbb",
        "guide-to-gbb-reports",
        "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
    ),
    _source_chunk_reference(
        "chunk-gbb-guide-flow-report",
        "gbb",
        "guide-to-gbb-reports",
        "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
    ),
    _source_chunk_reference(
        "chunk-gbb-guide-gas-day",
        "gbb",
        "guide-to-gbb-reports",
        "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
    ),
    _source_chunk_reference(
        "chunk-gbb-guide-medium-capacity-outlook",
        "gbb",
        "guide-to-gbb-reports",
        "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
    ),
    _source_chunk_reference(
        "chunk-gbb-guide-nameplate-capacity",
        "gbb",
        "guide-to-gbb-reports",
        "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
    ),
    _source_chunk_reference(
        "chunk-gbb-guide-nodes-facilities",
        "gbb",
        "guide-to-gbb-reports",
        "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
    ),
    _source_chunk_reference(
        "chunk-gbb-guide-participants-report",
        "gbb",
        "guide-to-gbb-reports",
        "9f7cf6f33b646de55e0593af8612953bcaa59665fddf019fcdbf02da31720410",
    ),
    _source_chunk_reference(
        "chunk-gbb-procedures-capacity-outlooks",
        "gbb",
        "bb-procedures",
        "f8b62c200c0e087fd69e1634ee041832c6f7cdfbf26800b2a572a27c02f35e35",
    ),
    _source_chunk_reference(
        "chunk-gbb-procedures-daily-flow-storage",
        "gbb",
        "bb-procedures",
        "f8b62c200c0e087fd69e1634ee041832c6f7cdfbf26800b2a572a27c02f35e35",
    ),
    _source_chunk_reference(
        "chunk-gbb-procedures-facility-nameplate",
        "gbb",
        "bb-procedures",
        "f8b62c200c0e087fd69e1634ee041832c6f7cdfbf26800b2a572a27c02f35e35",
    ),
    _source_chunk_reference(
        "chunk-gbb-procedures-linepack-capacity-adequacy",
        "gbb",
        "bb-procedures",
        "f8b62c200c0e087fd69e1634ee041832c6f7cdfbf26800b2a572a27c02f35e35",
    ),
    _source_chunk_reference(
        "chunk-gbb-procedures-registration",
        "gbb",
        "bb-procedures",
        "f8b62c200c0e087fd69e1634ee041832c6f7cdfbf26800b2a572a27c02f35e35",
    ),
    _source_chunk_reference(
        "chunk-gbb-procedures-scheduled-flow",
        "gbb",
        "bb-procedures",
        "f8b62c200c0e087fd69e1634ee041832c6f7cdfbf26800b2a572a27c02f35e35",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-bid-offer-price-steps",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-capacity-settlement",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-contingency-gas-bids",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-definitions",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-market-schedule-variation",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-mos-estimates",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-mos-settlement",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-settlement-amounts",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-settlement-terms",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-shortfall-settlement",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-spa-outputs",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
    _source_chunk_reference(
        "chunk-sttm-procedures-spa-requirements",
        "sttm",
        "sttm-procedures-2025",
        "285e6efed74bf48ab2c707804c70ac0ea431fca4d0acf4a00dd9358a1a846c93",
    ),
)


@dataclass(frozen=True)
class DashboardRegistryEntry:
    """One planned or available dashboard concept exposed to Marimo."""

    concept_id: str
    title: str
    description: str
    audiences: tuple[DashboardAudience, ...]
    status: DashboardStatus
    notebook_name: str | None
    backing_assets: tuple[str, ...]
    generated_gold_paths: tuple[str, ...]
    source_chunks: tuple[SourceChunkReference, ...]

    @property
    def notebook_route(self) -> str | None:
        """Return the deployed Marimo route when a backing notebook exists."""
        if self.notebook_name is None:
            return None
        return f"/marimo/{self.notebook_name}/"

    @property
    def source_chunk_ids(self) -> tuple[str, ...]:
        """Return source chunk IDs without their wrapper metadata."""
        return tuple(chunk.chunk_id for chunk in self.source_chunks)

    @property
    def silver_chunk_paths(self) -> tuple[str, ...]:
        """Return recorded silver chunk paths for this entry."""
        paths: list[str] = []
        for chunk in self.source_chunks:
            if chunk.silver_chunk_path is not None:
                paths.append(chunk.silver_chunk_path)
        return tuple(paths)

    @property
    def source_hashes(self) -> tuple[str, ...]:
        """Return recorded source document hashes for this entry."""
        source_hashes: list[str] = []
        for chunk in self.source_chunks:
            if chunk.source_hash is not None and chunk.source_hash not in source_hashes:
                source_hashes.append(chunk.source_hash)
        return tuple(source_hashes)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable dashboard registry entry."""
        return {
            "concept_id": self.concept_id,
            "title": self.title,
            "description": self.description,
            "audiences": [audience.value for audience in self.audiences],
            "status": self.status.value,
            "notebook_name": self.notebook_name,
            "notebook_route": self.notebook_route,
            "backing_assets": list(self.backing_assets),
            "generated_gold_paths": list(self.generated_gold_paths),
            "source_chunks": [chunk.to_dict() for chunk in self.source_chunks],
            "source_chunk_ids": list(self.source_chunk_ids),
            "silver_chunk_paths": list(self.silver_chunk_paths),
            "source_hashes": list(self.source_hashes),
        }


DASHBOARD_REGISTRY_RECORDS: tuple[DashboardRegistryRecord, ...] = (
    {
        "concept_id": "gas-market-overview",
        "title": "Gas Market Overview",
        "description": (
            "Available first-look dashboard for prices, schedules, flow, "
            "capacity, and source coverage across curated gas_model outputs."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "sample_energy_market",
        "backing_assets": (
            "silver.gas_model.silver_gas_fact_market_price",
            "silver.gas_model.silver_gas_fact_schedule_run",
            "silver.gas_model.silver_gas_fact_scheduled_quantity",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_facility_flow_storage",
            "silver.gas_model.silver_gas_fact_linepack",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
            "silver.gas_model.silver_gas_fact_capacity_auction",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/README.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-gas-day",
            "chunk-sttm-procedures-spa-requirements",
            "chunk-sttm-procedures-spa-outputs",
            "chunk-dwgm-operations-glossary-schedule",
            "chunk-gbb-guide-flow-report",
            "chunk-gbb-procedures-scheduled-flow",
            "chunk-sttm-procedures-settlement-terms",
            "chunk-gbb-procedures-capacity-outlooks",
            "chunk-gbb-guide-nameplate-capacity",
            "chunk-sttm-procedures-definitions",
            "chunk-dwgm-operations-capacity-certificates-purpose",
        ),
    },
    {
        "concept_id": "source-coverage-matrix",
        "title": "Source Coverage Matrix",
        "description": (
            "Available analytical dashboard for source-system and source-table "
            "coverage across registry-backed silver.gas_model facts and "
            "dimensions, including explicit metadata gaps."
        ),
        "audiences": ("operator", "analyst", "data-engineer"),
        "status": "available",
        "notebook_name": "source_coverage_matrix",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_date",
            "silver.gas_model.silver_gas_dim_participant",
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_dim_location",
            "silver.gas_model.silver_gas_dim_connection_point",
            "silver.gas_model.silver_gas_dim_zone",
            "silver.gas_model.silver_gas_dim_pipeline_segment",
            "silver.gas_model.silver_gas_dim_operational_point",
            "silver.gas_model.silver_gas_participant_market_membership",
            "silver.gas_model.silver_gas_fact_market_price",
            "silver.gas_model.silver_gas_fact_schedule_run",
            "silver.gas_model.silver_gas_fact_scheduled_quantity",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_facility_flow_storage",
            "silver.gas_model.silver_gas_fact_nomination_forecast",
            "silver.gas_model.silver_gas_fact_operational_meter_flow",
            "silver.gas_model.silver_gas_fact_linepack",
            "silver.gas_model.silver_gas_fact_linepack_balance",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
            "silver.gas_model.silver_gas_fact_capacity_transaction",
            "silver.gas_model.silver_gas_fact_capacity_auction",
            "silver.gas_model.silver_gas_fact_sttm_capacity_settlement",
            "silver.gas_model.silver_gas_fact_sttm_market_parameter",
            "silver.gas_model.silver_gas_fact_bid_stack",
            "silver.gas_model.silver_gas_fact_sttm_allocation_quantity",
            "silver.gas_model.silver_gas_fact_sttm_allocation_limit",
            "silver.gas_model.silver_gas_fact_sttm_default_allocation_notice",
            "silver.gas_model.silver_gas_fact_settlement_activity",
            "silver.gas_model.silver_gas_fact_sttm_mos_stack",
            "silver.gas_model.silver_gas_fact_system_notice",
            "silver.gas_model.silver_gas_fact_gas_quality",
            "silver.gas_model.silver_gas_fact_customer_transfer",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/README.md",
        ),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "source-table-lineage-explorer",
        "title": "Source Table Lineage Explorer",
        "description": (
            "Available analytical dashboard for moving from curated "
            "silver.gas_model assets to source systems, source tables, source "
            "lineage fields, concept cards, generated Market context paths, "
            "and table explorer metadata links."
        ),
        "audiences": ("operator", "analyst", "data-engineer"),
        "status": "available",
        "notebook_name": "source_table_lineage_explorer",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_date",
            "silver.gas_model.silver_gas_dim_participant",
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_dim_location",
            "silver.gas_model.silver_gas_dim_connection_point",
            "silver.gas_model.silver_gas_dim_zone",
            "silver.gas_model.silver_gas_dim_pipeline_segment",
            "silver.gas_model.silver_gas_dim_operational_point",
            "silver.gas_model.silver_gas_participant_market_membership",
            "silver.gas_model.silver_gas_fact_market_price",
            "silver.gas_model.silver_gas_fact_schedule_run",
            "silver.gas_model.silver_gas_fact_scheduled_quantity",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_facility_flow_storage",
            "silver.gas_model.silver_gas_fact_nomination_forecast",
            "silver.gas_model.silver_gas_fact_operational_meter_flow",
            "silver.gas_model.silver_gas_fact_linepack",
            "silver.gas_model.silver_gas_fact_linepack_balance",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
            "silver.gas_model.silver_gas_fact_capacity_transaction",
            "silver.gas_model.silver_gas_fact_capacity_auction",
            "silver.gas_model.silver_gas_fact_sttm_capacity_settlement",
            "silver.gas_model.silver_gas_fact_sttm_market_parameter",
            "silver.gas_model.silver_gas_fact_bid_stack",
            "silver.gas_model.silver_gas_fact_sttm_allocation_quantity",
            "silver.gas_model.silver_gas_fact_sttm_allocation_limit",
            "silver.gas_model.silver_gas_fact_sttm_default_allocation_notice",
            "silver.gas_model.silver_gas_fact_settlement_activity",
            "silver.gas_model.silver_gas_fact_sttm_mos_stack",
            "silver.gas_model.silver_gas_fact_system_notice",
            "silver.gas_model.silver_gas_fact_gas_quality",
            "silver.gas_model.silver_gas_fact_customer_transfer",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/README.md",
        ),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "gas-market-prices",
        "title": "Gas Market Prices",
        "description": (
            "Available analytical dashboard for gas market price types, source "
            "systems, source tables, gas-date filters, available price "
            "measures, bounded trend diagnostics, exception candidates, and "
            "Schedule context links from the curated market price fact."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "gas_market_prices",
        "backing_assets": ("silver.gas_model.silver_gas_fact_market_price",),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md",
        ),
        "source_chunk_ids": (
            "chunk-sttm-procedures-spa-requirements",
            "chunk-sttm-procedures-spa-outputs",
            "chunk-dwgm-operations-glossary-schedule",
        ),
    },
    {
        "concept_id": "gas-schedule-runs",
        "title": "Gas Schedule Runs",
        "description": (
            "Available analytical dashboard for schedule types, transmission "
            "identifiers, forecast demand versions, schedule timestamps, Gas Day "
            "filters, and source coverage from the curated schedule run fact."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "gas_schedule_runs",
        "backing_assets": ("silver.gas_model.silver_gas_fact_schedule_run",),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/settlement.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-gas-day",
            "chunk-sttm-procedures-spa-requirements",
            "chunk-sttm-procedures-spa-outputs",
            "chunk-dwgm-operations-glossary-schedule",
            "chunk-sttm-procedures-settlement-terms",
        ),
    },
    {
        "concept_id": "gas-scheduled-quantities",
        "title": "Gas Scheduled Quantities",
        "description": (
            "Available analytical dashboard for quantity types, schedule "
            "types, source points, quantity, volume, amount, source coverage, "
            "and schedule-run link context from the curated scheduled "
            "quantity fact."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "gas_scheduled_quantities",
        "backing_assets": ("silver.gas_model.silver_gas_fact_scheduled_quantity",),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-gas-day",
            "chunk-sttm-procedures-spa-requirements",
            "chunk-sttm-procedures-spa-outputs",
            "chunk-dwgm-operations-glossary-schedule",
            "chunk-gbb-procedures-scheduled-flow",
        ),
    },
    {
        "concept_id": "gbb-interactive-map",
        "title": "GBB Interactive Map",
        "description": (
            "Available map dashboard for facility topology, pipeline flow, "
            "nominations, storage, and capacity outlooks."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "gbb_interactive_map",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_dim_location",
            "silver.gas_model.silver_gas_dim_connection_point",
            "silver.gas_model.silver_gas_fact_facility_flow_storage",
            "silver.gas_model.silver_gas_fact_nomination_forecast",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/facility.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/connection-point.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/linepack.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-nodes-facilities",
            "chunk-gbb-procedures-facility-nameplate",
            "chunk-gbb-guide-connection-point-identifiers",
            "chunk-gbb-guide-flow-report",
            "chunk-gbb-procedures-scheduled-flow",
            "chunk-sttm-procedures-settlement-terms",
            "chunk-gbb-procedures-capacity-outlooks",
            "chunk-gbb-guide-nameplate-capacity",
            "chunk-sttm-procedures-definitions",
            "chunk-dwgm-operations-capacity-certificates-purpose",
            "chunk-gbb-procedures-linepack-capacity-adequacy",
        ),
    },
    {
        "concept_id": "facility-flow-storage",
        "title": "Facility Flow And Storage",
        "description": (
            "Available analytical dashboard for facility-level demand, supply, "
            "transfer, held-in-storage, cushion-gas storage, source coverage, "
            "and latest Gas Day from the curated facility flow/storage fact."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "facility_flow_storage",
        "backing_assets": ("silver.gas_model.silver_gas_fact_facility_flow_storage",),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/facility.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-nodes-facilities",
            "chunk-gbb-procedures-daily-flow-storage",
            "chunk-gbb-guide-flow-report",
            "chunk-gbb-procedures-capacity-outlooks",
        ),
    },
    {
        "concept_id": "nomination-demand-forecast",
        "title": "Nomination And Demand Forecast",
        "description": (
            "Available analytical dashboard for nomination and demand forecast "
            "rows, forecast type/version coverage, current/future forecast "
            "horizons, source-system filters, and facility/location navigation."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "nomination_demand_forecast",
        "backing_assets": ("silver.gas_model.silver_gas_fact_nomination_forecast",),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/facility.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-flow-report",
            "chunk-gbb-procedures-scheduled-flow",
            "chunk-gbb-guide-nodes-facilities",
            "chunk-gbb-guide-gas-day",
        ),
    },
    {
        "concept_id": "forecast-vs-actual",
        "title": "Forecast Vs Actual Flow And Storage",
        "description": (
            "Available analytical dashboard comparing bounded nomination or "
            "demand forecasts against actual facility flow/storage observations "
            "where the loaded facts share Gas Day and source facility/location "
            "identifiers."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "forecast_vs_actual",
        "backing_assets": (
            "silver.gas_model.silver_gas_fact_nomination_forecast",
            "silver.gas_model.silver_gas_fact_facility_flow_storage",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/facility.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-flow-report",
            "chunk-gbb-procedures-scheduled-flow",
            "chunk-gbb-procedures-daily-flow-storage",
            "chunk-gbb-guide-nodes-facilities",
            "chunk-gbb-guide-gas-day",
        ),
    },
    {
        "concept_id": "gas-model-table-explorer",
        "title": "Gas Model Table Explorer",
        "description": (
            "Available analytical dashboard for storage health, Dagster table "
            "asset catalogue overlays, and bounded table previews."
        ),
        "audiences": ("data-engineer", "operator", "analyst"),
        "status": "available",
        "notebook_name": "table_explorer",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_date",
            "silver.gas_model.silver_gas_dim_participant",
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_fact_market_price",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/README.md",
        ),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "data-readiness-overview",
        "title": "Data Readiness Overview",
        "description": (
            "Available platform operations dashboard for configured S3 buckets, "
            "discovered table prefixes, Dagster catalogue status, "
            "materialization freshness, and bounded-read policy."
        ),
        "audiences": ("platform-operations", "operator", "data-engineer"),
        "status": "available",
        "notebook_name": "data_readiness_overview",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_date",
            "silver.gas_model.silver_gas_dim_participant",
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_fact_market_price",
            "silver.gas_model.silver_gas_fact_schedule_run",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
        ),
        "generated_gold_paths": (),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "aws-bounded-read-diagnostics",
        "title": "AWS Bounded Read Diagnostics",
        "description": (
            "Available platform operations diagnostic view for runtime location, "
            "endpoint mode, configured buckets, preview row caps, full-table-scan "
            "state, and per-dashboard bounded-read behavior."
        ),
        "audiences": ("platform-operations", "operator", "data-engineer"),
        "status": "available",
        "notebook_name": "aws_bounded_read_diagnostics",
        "backing_assets": (),
        "generated_gold_paths": (),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "dagster-asset-catalogue-status",
        "title": "Dagster Asset Catalogue Status",
        "description": (
            "Available operational dashboard for Dagster GraphQL table asset "
            "catalogue health, table coverage, latest materialization metadata, "
            "URI coverage, executable flags, and schema metadata."
        ),
        "audiences": ("platform-operations", "operator", "data-engineer"),
        "status": "available",
        "notebook_name": "dagster_asset_catalogue_status",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_date",
            "silver.gas_model.silver_gas_dim_participant",
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_fact_market_price",
            "silver.gas_model.silver_gas_fact_schedule_run",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
        ),
        "generated_gold_paths": (),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "materialization-freshness",
        "title": "Materialization Freshness",
        "description": (
            "Available operational dashboard for latest Dagster materialization "
            "timestamps, freshness gaps by group and layer, unmaterialized "
            "assets, GraphQL-unavailable rows, and storage-missing assets."
        ),
        "audiences": ("platform-operations", "operator", "data-engineer"),
        "status": "available",
        "notebook_name": "materialization_freshness",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_date",
            "silver.gas_model.silver_gas_dim_participant",
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_fact_market_price",
            "silver.gas_model.silver_gas_fact_schedule_run",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
        ),
        "generated_gold_paths": (),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "s3-bucket-health",
        "title": "S3 Bucket Health",
        "description": (
            "Available platform operations dashboard for configured "
            "S3-compatible bucket reachability, object scans, truncation, "
            "errors, and Delta or Parquet table-prefix discovery."
        ),
        "audiences": ("platform-operations", "operator", "data-engineer"),
        "status": "available",
        "notebook_name": "s3_bucket_health",
        "backing_assets": (),
        "generated_gold_paths": (),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "glossary-explorer",
        "title": "Glossary Explorer",
        "description": (
            "Available analytical dashboard for browsing generated glossary "
            "concept metadata, cited source chunks, related concepts, and "
            "planned or available dashboard states from the Marimo registry."
        ),
        "audiences": ("analyst", "stakeholder", "data-engineer"),
        "status": "available",
        "notebook_name": "glossary_explorer",
        "backing_assets": (),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/README.md",
        ),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "concept-to-asset-explorer",
        "title": "Concept-to-Asset Explorer",
        "description": (
            "Available analytical dashboard for mapping Market context glossary "
            "concepts to backing silver.gas_model assets, dashboard routes, "
            "planned dashboard cards, and table explorer deep links."
        ),
        "audiences": ("analyst", "data-engineer", "stakeholder"),
        "status": "available",
        "notebook_name": "concept_to_asset_explorer",
        "backing_assets": (),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/README.md",
        ),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "schema-data-dictionary-explorer",
        "title": "Schema Data Dictionary Explorer",
        "description": (
            "Available analytical dashboard for inspecting Dagster schema "
            "metadata for registry-mapped silver.gas_model assets by concept, "
            "mart, asset, and dashboard route."
        ),
        "audiences": ("analyst", "data-engineer", "operator"),
        "status": "available",
        "notebook_name": "schema_data_dictionary_explorer",
        "backing_assets": (),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/README.md",
        ),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "citation-chain-explorer",
        "title": "Citation-Chain Explorer",
        "description": (
            "Available analytical dashboard for auditing registry citation "
            "metadata from dashboard concepts to generated-gold paths, source "
            "chunk IDs, silver chunk paths, and source hashes."
        ),
        "audiences": ("analyst", "data-engineer", "operator"),
        "status": "available",
        "notebook_name": "citation_chain_explorer",
        "backing_assets": (),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/README.md",
        ),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "gas-system-notices",
        "title": "Gas System Notices",
        "description": (
            "Available operational dashboard for critical gas system notices, "
            "active or recent notice windows, message fields, URL paths, and "
            "source coverage from the curated system notice fact."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "system_notices",
        "backing_assets": ("silver.gas_model.silver_gas_fact_system_notice",),
        "generated_gold_paths": (),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "gas-quality-composition",
        "title": "Gas Quality And Composition",
        "description": (
            "Available analytical dashboard for gas quality and composition "
            "observations, quality types, units, source points, quantities, "
            "gas intervals, and source coverage from the curated gas quality fact."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "gas_quality_composition",
        "backing_assets": ("silver.gas_model.silver_gas_fact_gas_quality",),
        "generated_gold_paths": (),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "heating-value-pressure",
        "title": "Heating Value And SCADA Pressure",
        "description": (
            "Available analytical dashboard for heating value and SCADA "
            "pressure observations, source-qualified zone and node "
            "identifiers, gas dates, measurement timestamps, and source "
            "coverage from the curated quality/status facts."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "heating_value_pressure",
        "backing_assets": (
            "silver.gas_model.silver_gas_fact_heating_value",
            "silver.gas_model.silver_gas_fact_scada_pressure",
        ),
        "generated_gold_paths": (),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "gas-customer-transfer-activity",
        "title": "Customer Transfer And Retail Activity",
        "description": (
            "Available analytical dashboard for customer transfers lodged, "
            "completed, cancelled, internal transfers, greenfields received, "
            "market code, Gas Day filters, and source coverage from the "
            "curated customer transfer fact."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "gas_customer_transfer_activity",
        "backing_assets": ("silver.gas_model.silver_gas_fact_customer_transfer",),
        "generated_gold_paths": (),
        "source_chunk_ids": (),
    },
    {
        "concept_id": "gas-day-context",
        "title": "Gas Day Context",
        "description": (
            "Available explainer dashboard for Gas Day glossary metadata, "
            "date and gas-date field coverage, and bounded examples across "
            "current curated gas_model assets."
        ),
        "audiences": ("analyst", "stakeholder", "data-engineer"),
        "status": "available",
        "notebook_name": "gas_day_explainer",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_date",
            "silver.gas_model.silver_gas_fact_market_price",
            "silver.gas_model.silver_gas_fact_schedule_run",
            "silver.gas_model.silver_gas_fact_scheduled_quantity",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_facility_flow_storage",
            "silver.gas_model.silver_gas_fact_linepack",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
            "silver.gas_model.silver_gas_fact_bid_stack",
            "silver.gas_model.silver_gas_fact_settlement_activity",
            "silver.gas_model.silver_gas_fact_customer_transfer",
            "silver.gas_model.silver_gas_fact_gas_quality",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md",
        ),
        "source_chunk_ids": ("chunk-gbb-guide-gas-day",),
    },
    {
        "concept_id": "participant-context",
        "title": "Participant Context",
        "description": (
            "Available explainer dashboard for Participant glossary metadata, "
            "current participant standing data, market memberships, and "
            "participant-facing bid, settlement, and facility relationships."
        ),
        "audiences": ("analyst", "data-engineer", "stakeholder"),
        "status": "available",
        "notebook_name": "participant_explainer",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_participant",
            "silver.gas_model.silver_gas_participant_market_membership",
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_fact_bid_stack",
            "silver.gas_model.silver_gas_fact_settlement_activity",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/participant.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-participants-report",
            "chunk-gbb-procedures-registration",
            "chunk-sttm-procedures-settlement-terms",
        ),
    },
    {
        "concept_id": "facility-context",
        "title": "Facility Context",
        "description": (
            "Available explainer dashboard for Facility glossary metadata, "
            "facility standing-data coverage, participant and zone keys, "
            "flow/storage measures, capacity outlooks, and related dashboard "
            "routes."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "facility_explainer",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_fact_facility_flow_storage",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/facility.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-nodes-facilities",
            "chunk-gbb-procedures-facility-nameplate",
        ),
    },
    {
        "concept_id": "hub-zone-context",
        "title": "Hub / Zone Context",
        "description": (
            "Available explainer dashboard for generated Hub / Zone context, "
            "source-qualified STTM hub and DWGM zone identifiers, current "
            "silver_gas_dim_zone coverage, and downstream market-analysis "
            "dashboards."
        ),
        "audiences": ("analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "hub_zone_explainer",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_zone",
            "silver.gas_model.silver_gas_fact_capacity_auction",
            "silver.gas_model.silver_gas_fact_sttm_market_parameter",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/hub-zone.md",
        ),
        "source_chunk_ids": (
            "chunk-sttm-procedures-definitions",
            "chunk-sttm-procedures-settlement-terms",
            "chunk-dwgm-operations-glossary-schedule",
            "chunk-dwgm-operations-capacity-certificates-modelling",
        ),
    },
    {
        "concept_id": "connection-point-context",
        "title": "Connection Point Context",
        "description": (
            "Available explainer dashboard for connection-point identifiers, "
            "flow directions, facility, location, and zone relationships, "
            "actual flow rows, capacity outlook context, and related dashboard "
            "routes."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "connection_point_explainer",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_connection_point",
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_dim_location",
            "silver.gas_model.silver_gas_dim_zone",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/connection-point.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-connection-point-identifiers",
            "chunk-gbb-guide-flow-report",
        ),
    },
    {
        "concept_id": "pipeline-connection-operations",
        "title": "Pipeline and Connection Operations",
        "description": (
            "Available operational dashboard linking Connection Point, "
            "Facility, Flow, Capacity, pipeline segment metadata, and visible "
            "relationship gaps without changing gas_model relationship "
            "modeling."
        ),
        "audiences": ("operator", "analyst", "data-engineer"),
        "status": "available",
        "notebook_name": "pipeline_connection_operations",
        "backing_assets": (
            "silver.gas_model.silver_gas_dim_connection_point",
            "silver.gas_model.silver_gas_dim_facility",
            "silver.gas_model.silver_gas_dim_pipeline_segment",
            "silver.gas_model.silver_gas_dim_zone",
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_operational_meter_flow",
            "silver.gas_model.silver_gas_fact_capacity_outlook",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/connection-point.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/facility.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-connection-point-identifiers",
            "chunk-gbb-guide-flow-report",
            "chunk-gbb-procedures-capacity-outlooks",
            "chunk-gbb-guide-nameplate-capacity",
            "chunk-gbb-procedures-facility-nameplate",
        ),
    },
    {
        "concept_id": "operational-meter-flow",
        "title": "Operational Meter Flow",
        "description": (
            "Available operational dashboard for VICGAS operational meter "
            "flow quantities, gas intervals, point identifiers, direction, "
            "and explicit Operational Point, Hub / Zone, and Pipeline segment "
            "relationship gaps."
        ),
        "audiences": ("operator", "analyst", "data-engineer"),
        "status": "available",
        "notebook_name": "operational_meter_flow",
        "backing_assets": (
            "silver.gas_model.silver_gas_fact_operational_meter_flow",
            "silver.gas_model.silver_gas_dim_operational_point",
            "silver.gas_model.silver_gas_dim_zone",
            "silver.gas_model.silver_gas_dim_pipeline_segment",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-flow-report",
            "chunk-gbb-procedures-scheduled-flow",
            "chunk-sttm-procedures-settlement-terms",
        ),
    },
    {
        "concept_id": "schedule-context",
        "title": "Schedule Context",
        "description": (
            "Planned concept panel for schedule runs, scheduled quantities, "
            "bid stacks, and market schedule lineage."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "planned",
        "backing_assets": (
            "silver.gas_model.silver_gas_fact_schedule_run",
            "silver.gas_model.silver_gas_fact_scheduled_quantity",
            "silver.gas_model.silver_gas_fact_bid_stack",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md",
        ),
        "source_chunk_ids": (
            "chunk-sttm-procedures-spa-requirements",
            "chunk-sttm-procedures-spa-outputs",
            "chunk-dwgm-operations-glossary-schedule",
        ),
    },
    {
        "concept_id": "bid-offer-context",
        "title": "Bid / Offer Stack",
        "description": (
            "Available analytical dashboard for Bid / Offer stack steps, "
            "participants, facilities, zones, prices, quantities, source "
            "systems, and accepted source identifiers from the curated bid "
            "stack fact."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "gas_bid_offer_stack",
        "backing_assets": ("silver.gas_model.silver_gas_fact_bid_stack",),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/bid-offer.md",
        ),
        "source_chunk_ids": (
            "chunk-sttm-procedures-bid-offer-price-steps",
            "chunk-sttm-procedures-contingency-gas-bids",
            "chunk-dwgm-operations-glossary-schedule",
        ),
    },
    {
        "concept_id": "allocation-context",
        "title": "Allocation Context",
        "description": (
            "Planned concept panel for STTM allocation quantities, warning "
            "limits, default allocation notices, and DWGM allocation context."
        ),
        "audiences": ("operator", "analyst"),
        "status": "planned",
        "backing_assets": (
            "silver.gas_model.silver_gas_fact_sttm_allocation_quantity",
            "silver.gas_model.silver_gas_fact_sttm_allocation_limit",
            "silver.gas_model.silver_gas_fact_sttm_default_allocation_notice",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/allocation.md",
        ),
        "source_chunk_ids": (
            "chunk-dwgm-settlement-pricing-schedule-allocation",
            "chunk-dwgm-settlement-withdrawal-allocation",
            "chunk-sttm-procedures-capacity-settlement",
        ),
    },
    {
        "concept_id": "settlement-context",
        "title": "Settlement Context",
        "description": (
            "Available analytical dashboard for settlement activities, "
            "versions, activity types, schedules, networks, participants, "
            "amounts, quantities, percentages, Gas Day filters, and source "
            "coverage from the curated settlement activity fact."
        ),
        "audiences": ("analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "gas_settlement_activity",
        "backing_assets": ("silver.gas_model.silver_gas_fact_settlement_activity",),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/settlement.md",
        ),
        "source_chunk_ids": (
            "chunk-sttm-procedures-settlement-terms",
            "chunk-sttm-procedures-settlement-amounts",
            "chunk-sttm-procedures-shortfall-settlement",
            "chunk-dwgm-settlement-purpose",
        ),
    },
    {
        "concept_id": "capacity-context",
        "title": "Capacity Context",
        "description": (
            "Available operational dashboard for capacity outlook rows, source "
            "coverage, date ranges, capacity types, directions, facilities, "
            "and related Facility, Flow, and Connection Point context."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "capacity_outlook",
        "backing_assets": ("silver.gas_model.silver_gas_fact_capacity_outlook",),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-procedures-capacity-outlooks",
            "chunk-gbb-guide-nameplate-capacity",
            "chunk-sttm-procedures-definitions",
            "chunk-dwgm-operations-capacity-certificates-purpose",
        ),
    },
    {
        "concept_id": "capacity-auctions",
        "title": "Capacity Auctions",
        "description": (
            "Available analytical dashboard for capacity auction observations, "
            "auction dates, Hub / Zone values, capacity periods, quantities, "
            "prices, auction metrics, and related Capacity and market-analysis "
            "context."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "capacity_auction",
        "backing_assets": ("silver.gas_model.silver_gas_fact_capacity_auction",),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
            "tools/gas-market-knowledge-base/generated/gold/glossary/hub-zone.md",
        ),
        "source_chunk_ids": (
            "chunk-sttm-procedures-definitions",
            "chunk-sttm-procedures-capacity-settlement",
            "chunk-dwgm-operations-capacity-certificates-purpose",
            "chunk-dwgm-operations-capacity-certificates-modelling",
        ),
    },
    {
        "concept_id": "mos-context",
        "title": "MOS Context",
        "description": (
            "Planned concept panel for STTM market operator service estimates, "
            "settlement, and stack steps."
        ),
        "audiences": ("analyst", "stakeholder"),
        "status": "planned",
        "backing_assets": (
            "silver.gas_model.silver_gas_fact_sttm_mos_stack",
            "silver.gas_model.silver_gas_fact_sttm_capacity_settlement",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/mos.md",
        ),
        "source_chunk_ids": (
            "chunk-sttm-procedures-mos-estimates",
            "chunk-sttm-procedures-mos-settlement",
            "chunk-sttm-procedures-capacity-settlement",
        ),
    },
    {
        "concept_id": "linepack-context",
        "title": "Linepack Context",
        "description": (
            "Available analytical dashboard for linepack observations, "
            "adequacy flags, adequacy descriptions, facility and zone "
            "coverage, and related Flow, Capacity, and MOS context."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "linepack_adequacy",
        "backing_assets": (
            "silver.gas_model.silver_gas_fact_linepack",
            "silver.gas_model.silver_gas_fact_linepack_balance",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/linepack.md",
        ),
        "source_chunk_ids": (
            "chunk-sttm-procedures-definitions",
            "chunk-gbb-procedures-linepack-capacity-adequacy",
        ),
    },
    {
        "concept_id": "flow-context",
        "title": "Flow Context",
        "description": (
            "Available operational dashboard for actual flows, scheduled flow, "
            "nominations, and operational meter flow."
        ),
        "audiences": ("operator", "analyst", "stakeholder"),
        "status": "available",
        "notebook_name": "flow_operations",
        "backing_assets": (
            "silver.gas_model.silver_gas_fact_connection_point_flow",
            "silver.gas_model.silver_gas_fact_facility_flow_storage",
            "silver.gas_model.silver_gas_fact_nomination_forecast",
            "silver.gas_model.silver_gas_fact_operational_meter_flow",
        ),
        "generated_gold_paths": (
            "tools/gas-market-knowledge-base/generated/gold/glossary/flow.md",
        ),
        "source_chunk_ids": (
            "chunk-gbb-guide-flow-report",
            "chunk-gbb-procedures-scheduled-flow",
            "chunk-sttm-procedures-settlement-terms",
        ),
    },
)


@cache
def dashboard_registry() -> tuple[DashboardRegistryEntry, ...]:
    """Return the parsed dashboard registry."""
    return load_dashboard_registry(DASHBOARD_REGISTRY_RECORDS)


def dashboard_registry_payload() -> dict[str, object]:
    """Return a JSON-serializable registry payload for Marimo clients."""
    return {
        "schema_version": 1,
        "audiences": [audience.value for audience in ROADMAP_AUDIENCES],
        "entries": [entry.to_dict() for entry in dashboard_registry()],
    }


def registry_entry_by_concept_id(
    concept_id: str,
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> DashboardRegistryEntry | None:
    """Return one registry entry by concept ID."""
    candidate_entries = dashboard_registry() if entries is None else entries
    for entry in candidate_entries:
        if entry.concept_id == concept_id:
            return entry
    return None


def load_dashboard_registry(
    records: Sequence[DashboardRegistryRecord],
) -> tuple[DashboardRegistryEntry, ...]:
    """Parse and validate raw dashboard registry records."""
    entries = tuple(
        _entry_from_record(record, index) for index, record in enumerate(records)
    )
    _validate_registry(entries)
    return entries


def _entry_from_record(
    record: DashboardRegistryRecord,
    index: int,
) -> DashboardRegistryEntry:
    concept_id = _required_str(record, "concept_id", index)
    title = _required_str(record, "title", index)
    description = _required_str(record, "description", index)
    status = _status_from_value(_required_str(record, "status", index), index)
    audiences = _audiences_from_values(
        _required_str_tuple(record, "audiences", index),
        index,
    )
    notebook_name = _optional_str(record, "notebook_name", index)
    backing_assets = _str_tuple(record, "backing_assets", index)
    generated_gold_paths = _str_tuple(record, "generated_gold_paths", index)
    source_chunks = _source_chunks_from_record(record, index)

    if status is DashboardStatus.AVAILABLE and notebook_name is None:
        raise DashboardRegistryError(
            f"dashboard registry record {index} is available but has no notebook_name"
        )

    return DashboardRegistryEntry(
        concept_id=concept_id,
        title=title,
        description=description,
        audiences=audiences,
        status=status,
        notebook_name=notebook_name,
        backing_assets=backing_assets,
        generated_gold_paths=generated_gold_paths,
        source_chunks=source_chunks,
    )


def _source_chunks_from_record(
    record: DashboardRegistryRecord,
    index: int,
) -> tuple[SourceChunkReference, ...]:
    raw_source_chunks = record.get("source_chunks", _MISSING)
    if raw_source_chunks is _MISSING:
        return tuple(
            _source_chunk_reference_by_id(chunk_id)
            for chunk_id in _str_tuple(record, "source_chunk_ids", index)
        )

    if not isinstance(raw_source_chunks, tuple):
        raise DashboardRegistryError(
            f"dashboard registry record {index} field source_chunks must be a tuple"
        )

    source_chunks: list[SourceChunkReference] = []
    for raw_chunk in raw_source_chunks:
        if not isinstance(raw_chunk, Mapping):
            raise DashboardRegistryError(
                f"dashboard registry record {index} field source_chunks must "
                "contain mapping records"
            )
        source_chunks.append(_source_chunk_from_mapping(raw_chunk, index))
    return tuple(source_chunks)


def _source_chunk_reference_by_id(chunk_id: str) -> SourceChunkReference:
    source_chunks_by_id = {chunk.chunk_id: chunk for chunk in SOURCE_CHUNK_REFERENCES}
    return source_chunks_by_id.get(chunk_id, SourceChunkReference(chunk_id=chunk_id))


def _source_chunk_from_mapping(
    raw_chunk: Mapping[str, object],
    index: int,
) -> SourceChunkReference:
    chunk_id = _required_str(raw_chunk, "chunk_id", index)
    return SourceChunkReference(
        chunk_id=chunk_id,
        silver_chunk_path=_optional_str(raw_chunk, "silver_chunk_path", index),
        source_hash=_optional_str(raw_chunk, "source_hash", index),
    )


def _validate_registry(entries: Sequence[DashboardRegistryEntry]) -> None:
    if len(entries) == 0:
        raise DashboardRegistryError("dashboard registry must contain entries")

    concept_ids = [entry.concept_id for entry in entries]
    duplicate_ids = sorted(
        concept_id
        for concept_id in set(concept_ids)
        if concept_ids.count(concept_id) > 1
    )
    if duplicate_ids:
        raise DashboardRegistryError(
            f"dashboard registry has duplicate concept_id values: {duplicate_ids}"
        )

    statuses = {entry.status for entry in entries}
    required_statuses = {DashboardStatus.AVAILABLE, DashboardStatus.PLANNED}
    if not required_statuses <= statuses:
        raise DashboardRegistryError(
            "dashboard registry must include planned and available entries"
        )

    audiences = {audience for entry in entries for audience in entry.audiences}
    missing_audiences = [
        audience for audience in ROADMAP_AUDIENCES if audience not in audiences
    ]
    if missing_audiences:
        missing = [audience.value for audience in missing_audiences]
        raise DashboardRegistryError(
            f"dashboard registry missing audience coverage: {missing}"
        )

    for entry in entries:
        _validate_entry(entry)


def _validate_entry(entry: DashboardRegistryEntry) -> None:
    if not entry.concept_id.replace("-", "").isalnum():
        raise DashboardRegistryError(
            f"dashboard registry concept_id is not slug-like: {entry.concept_id}"
        )

    if (
        len(entry.backing_assets) == 0
        and entry.concept_id not in _REGISTRY_BACKED_CONCEPT_IDS
    ):
        raise DashboardRegistryError(
            f"{entry.concept_id} backing_assets must not be empty"
        )

    for asset in entry.backing_assets:
        if not asset.startswith("silver.gas_model."):
            raise DashboardRegistryError(
                f"{entry.concept_id} backing asset is outside silver.gas_model: {asset}"
            )

    if entry.generated_gold_paths and not entry.source_chunks:
        if not _generated_gold_paths_are_indexes(entry.generated_gold_paths):
            raise DashboardRegistryError(
                f"{entry.concept_id} has generated gold paths without source chunks"
            )


def _generated_gold_paths_are_indexes(paths: Sequence[str]) -> bool:
    return all(path.endswith("/README.md") for path in paths)


def _status_from_value(value: str, index: int) -> DashboardStatus:
    try:
        return DashboardStatus(value)
    except ValueError as error:
        raise DashboardRegistryError(
            f"dashboard registry record {index} has unknown status: {value}"
        ) from error


def _audiences_from_values(
    values: Sequence[str],
    index: int,
) -> tuple[DashboardAudience, ...]:
    audiences: list[DashboardAudience] = []
    for value in values:
        try:
            audiences.append(DashboardAudience(value))
        except ValueError as error:
            raise DashboardRegistryError(
                f"dashboard registry record {index} has unknown audience: {value}"
            ) from error

    return tuple(dict.fromkeys(audiences))


def _required_str(record: DashboardRegistryRecord, field: str, index: int) -> str:
    value = _optional_str(record, field, index)
    if value is None:
        raise DashboardRegistryError(
            f"dashboard registry record {index} is missing required field: {field}"
        )
    return value


def _optional_str(
    record: DashboardRegistryRecord,
    field: str,
    index: int,
) -> str | None:
    value = record.get(field, _MISSING)
    if value is _MISSING:
        return None
    if not isinstance(value, str):
        raise DashboardRegistryError(
            f"dashboard registry record {index} field {field} must be a string"
        )
    stripped = value.strip()
    if stripped == "":
        return None
    return stripped


def _required_str_tuple(
    record: DashboardRegistryRecord,
    field: str,
    index: int,
) -> tuple[str, ...]:
    values = _str_tuple(record, field, index)
    if len(values) == 0:
        raise DashboardRegistryError(
            f"dashboard registry record {index} field {field} must not be empty"
        )
    return values


def _str_tuple(
    record: DashboardRegistryRecord,
    field: str,
    index: int,
) -> tuple[str, ...]:
    value = record.get(field, ())
    if not isinstance(value, tuple):
        raise DashboardRegistryError(
            f"dashboard registry record {index} field {field} must be a tuple"
        )

    values: list[str] = []
    for item in value:
        if not isinstance(item, str):
            raise DashboardRegistryError(
                f"dashboard registry record {index} field {field} must contain strings"
            )
        stripped = item.strip()
        if stripped == "":
            raise DashboardRegistryError(
                f"dashboard registry record {index} field {field} contains a blank value"
            )
        values.append(stripped)
    return tuple(values)
