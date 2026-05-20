"""Component tests for the registry-backed glossary explorer dashboard."""

from marimoserver.dashboard_registry import (
    DashboardAudience,
    DashboardRegistryEntry,
    DashboardStatus,
    dashboard_registry,
)
from marimoserver.glossary_explorer import (
    GLOSSARY_GOLD_PREFIX,
    GlossaryConcept,
    GlossaryDashboardReference,
    GlossaryExplorer,
    build_glossary_explorer,
    glossary_concept_by_generated_gold_path,
    render_glossary_explorer_html,
)


def test_glossary_explorer_lists_seeded_glossary_concepts_from_registry() -> None:
    entries = dashboard_registry()
    explorer = build_glossary_explorer(entries)
    expected_paths = {
        path
        for entry in entries
        if entry.concept_id.endswith("-context")
        for path in entry.generated_gold_paths
        if path.startswith(GLOSSARY_GOLD_PREFIX)
    }
    concept_paths = {
        concept.generated_gold_path
        for concept in explorer.concepts
        if concept.generated_gold_path is not None
    }

    assert len(explorer.concepts) == 13
    assert concept_paths == expected_paths
    assert {concept.title for concept in explorer.concepts} >= {
        "Bid / Offer",
        "Capacity",
        "Gas Day",
        "Hub / Zone",
        "MOS",
    }


def test_glossary_explorer_builds_concept_details_and_dashboard_references() -> None:
    explorer = build_glossary_explorer()
    capacity = glossary_concept_by_generated_gold_path(
        explorer,
        "tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md",
    )

    assert capacity is not None
    assert glossary_concept_by_generated_gold_path(explorer, "missing.md") is None
    assert capacity.title == "Capacity"
    assert "chunk-gbb-procedures-capacity-outlooks" in capacity.source_chunk_ids
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


def test_glossary_explorer_html_renders_concept_details() -> None:
    html = render_glossary_explorer_html(build_glossary_explorer())

    assert 'data-concept-count="13"' in html
    assert (
        'data-glossary-path="tools/gas-market-knowledge-base/generated/gold/'
        'glossary/capacity.md"'
    ) in html
    assert "generated-gold path" in html
    assert "source chunk IDs" in html
    assert "related concepts" in html
    assert "dashboard links/statuses" in html
    assert "chunk-gbb-procedures-capacity-outlooks" in html
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
        generated_gold_paths=(),
        source_chunks=(),
    )

    explorer = build_glossary_explorer((sparse_entry,))
    html = render_glossary_explorer_html(explorer)

    assert len(explorer.concepts) == 1
    assert explorer.concepts[0].metadata_gaps == (
        "No generated-gold path recorded in the Marimo registry.",
        "No source chunk IDs recorded in the Marimo registry.",
    )
    assert 'data-validation-gap="true"' in html
    assert "validation-visible gaps" in html
    assert "No generated-gold path recorded in the Marimo registry." in html
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
        generated_gold_paths=(),
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
            generated_gold_path="tools/gas-market-knowledge-base/generated/gold/glossary/empty.md",
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
            generated_gold_path="tools/gas-market-knowledge-base/generated/gold/glossary/unmounted.md",
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
