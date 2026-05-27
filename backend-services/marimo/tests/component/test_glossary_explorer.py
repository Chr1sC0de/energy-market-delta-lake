"""Component tests for the registry-backed glossary explorer dashboard."""

from marimoserver.dashboard_registry import (
    DashboardAudience,
    DashboardRegistryEntry,
    DashboardStatus,
    dashboard_registry,
    registry_entry_by_concept_id,
)
from marimoserver.glossary_explorer import (
    GLOSSARY_MARKET_CONTEXT_PREFIX,
    GlossaryConcept,
    GlossaryDashboardReference,
    GlossaryExplorer,
    build_glossary_explorer,
    glossary_concept_by_generated_gold_path,
    glossary_concept_by_market_context_id,
    render_glossary_explorer_html,
)


def test_glossary_explorer_lists_seeded_glossary_concepts_from_registry() -> None:
    entries = dashboard_registry()
    explorer = build_glossary_explorer(entries)
    expected_ids = {
        market_context_id
        for entry in entries
        if entry.concept_id.endswith("-context")
        for market_context_id in entry.market_context_ids
        if market_context_id.startswith(GLOSSARY_MARKET_CONTEXT_PREFIX)
    }
    concept_ids = {
        concept.market_context_id
        for concept in explorer.concepts
        if concept.market_context_id is not None
    }

    assert len(explorer.concepts) == 13
    assert concept_ids == expected_ids
    assert {concept.title for concept in explorer.concepts} >= {
        "Bid / Offer",
        "Capacity",
        "Gas Day",
        "Hub / Zone",
        "MOS",
    }


def test_glossary_explorer_builds_concept_details_and_dashboard_references() -> None:
    explorer = build_glossary_explorer()
    capacity = glossary_concept_by_market_context_id(
        explorer,
        "glossary:capacity",
    )

    assert capacity is not None
    assert glossary_concept_by_market_context_id(explorer, "glossary:missing") is None
    assert capacity.title == "Capacity"
    capacity_entry = registry_entry_by_concept_id("capacity-context")
    assert capacity_entry is not None
    assert capacity.source_chunk_ids == capacity_entry.source_chunk_ids
    assert any(
        reference.title == "Gas Market Overview"
        and reference.status is DashboardStatus.AVAILABLE
        and reference.notebook_route == "/marimo/sample_energy_market/"
        for reference in capacity.dashboard_references
    )
    assert any(
        reference.title == "Capacity Context"
        and reference.status is DashboardStatus.AVAILABLE
        and reference.notebook_route == "/marimo/capacity_outlook/"
        for reference in capacity.dashboard_references
    )
    assert any(
        related.title in {"Flow", "Hub / Zone"} for related in capacity.related_concepts
    )


def test_glossary_explorer_supports_legacy_generated_path_lookup() -> None:
    explorer = build_glossary_explorer()
    capacity = glossary_concept_by_generated_gold_path(
        explorer,
        "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
    )

    assert capacity is not None
    assert capacity.market_context_id == "glossary:capacity"
    assert glossary_concept_by_generated_gold_path(explorer, "missing.md") is None


def test_glossary_explorer_html_renders_concept_details() -> None:
    html = render_glossary_explorer_html(build_glossary_explorer())

    assert 'data-concept-count="13"' in html
    assert 'data-market-context-id="glossary:capacity"' in html
    assert "Market context ID" in html
    assert "source chunk IDs" in html
    assert "related concepts" in html
    assert "dashboard links/statuses" in html
    capacity_entry = registry_entry_by_concept_id("capacity-context")
    assert capacity_entry is not None
    assert capacity_entry.source_chunk_ids[0] in html
    assert 'href="/marimo/sample_energy_market/"' in html


def test_glossary_explorer_can_render_without_related_concepts() -> None:
    explorer = build_glossary_explorer(related_limit=0)

    assert all(not concept.related_concepts for concept in explorer.concepts)
    assert "No related concepts share dashboard links" in render_glossary_explorer_html(
        explorer
    )


def test_glossary_explorer_html_renders_unavailable_dashboard_states() -> None:
    html = render_glossary_explorer_html(build_glossary_explorer())

    assert 'data-dashboard-status="planned"' in html
    assert "Planned dashboard" in html
    assert 'href="/marimo/capacity-context/"' not in html


def test_glossary_explorer_html_marks_missing_metadata_as_validation_gap() -> None:
    sparse_entry = DashboardRegistryEntry(
        concept_id="sparse-context",
        title="Sparse",
        description="Concept metadata missing citation fields.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.sparse_table",),
        market_context_ids=(),
        source_chunks=(),
    )

    explorer = build_glossary_explorer((sparse_entry,))
    html = render_glossary_explorer_html(explorer)

    assert len(explorer.concepts) == 1
    assert explorer.concepts[0].metadata_gaps == (
        "No Market context ID recorded in the Marimo registry.",
        "No source chunk IDs recorded in the Marimo registry.",
    )
    assert 'data-validation-gap="true"' in html
    assert "validation-visible gaps" in html
    assert "No Market context ID recorded in the Marimo registry." in html
    assert "No source chunk IDs recorded in the Marimo registry." in html


def test_glossary_explorer_strips_context_suffix_for_missing_path_seed() -> None:
    entry = DashboardRegistryEntry(
        concept_id="suffix-context",
        title="Suffix Context",
        description="Concept metadata missing a generated path.",
        audiences=(DashboardAudience.ANALYST,),
        status=DashboardStatus.PLANNED,
        notebook_name=None,
        backing_assets=("silver.gas_model.suffix_table",),
        market_context_ids=(),
        source_chunks=(),
    )

    explorer = build_glossary_explorer((entry,))

    assert explorer.concepts[0].title == "Suffix"


def test_glossary_explorer_html_renders_empty_and_unmounted_dashboard_states() -> None:
    concepts = (
        GlossaryConcept(
            concept_id="empty-context",
            title="Empty",
            description="Concept with no dashboard references.",
            market_context_id="glossary:empty",
            source_chunk_ids=("chunk-empty",),
            dashboard_references=(),
            related_concepts=(),
            metadata_gaps=(),
            backing_assets=("silver.gas_model.empty_table",),
        ),
        GlossaryConcept(
            concept_id="unmounted-context",
            title="Unmounted",
            description="Concept with an available registry entry but no route.",
            market_context_id="glossary:unmounted",
            source_chunk_ids=("chunk-unmounted",),
            dashboard_references=(
                GlossaryDashboardReference(
                    concept_id="unmounted-dashboard",
                    title="Unmounted Dashboard",
                    status=DashboardStatus.AVAILABLE,
                    notebook_route=None,
                ),
            ),
            related_concepts=(),
            metadata_gaps=(),
            backing_assets=("silver.gas_model.unmounted_table",),
        ),
    )

    html = render_glossary_explorer_html(GlossaryExplorer(concepts=concepts))

    assert "No dashboard registry entries are linked to this glossary concept." in html
    assert "Unavailable dashboard" in html
