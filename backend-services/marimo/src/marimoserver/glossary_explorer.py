"""Registry-backed glossary explorer rendering for Marimo dashboards."""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from html import escape

from marimoserver.dashboard_registry import (
    DashboardRegistryEntry,
    DashboardStatus,
    dashboard_registry,
)

GLOSSARY_GOLD_PREFIX = "tools/gas-market-knowledge-base/generated/gold/glossary/"
GLOSSARY_INDEX_PATH = f"{GLOSSARY_GOLD_PREFIX}README.md"
GLOSSARY_CONTEXT_SUFFIX = "-context"
DEFAULT_RELATED_CONCEPT_LIMIT = 6


@dataclass(frozen=True)
class GlossaryDashboardReference:
    """Dashboard registry entry linked to a glossary concept."""

    concept_id: str
    title: str
    status: DashboardStatus
    notebook_route: str | None


@dataclass(frozen=True)
class RelatedGlossaryConcept:
    """Related glossary concept summary rendered inside a concept card."""

    concept_id: str
    title: str
    generated_gold_path: str | None


@dataclass(frozen=True)
class GlossaryConcept:
    """One generated glossary concept derived from registry metadata."""

    concept_id: str
    title: str
    description: str
    generated_gold_path: str | None
    source_chunk_ids: tuple[str, ...]
    dashboard_references: tuple[GlossaryDashboardReference, ...]
    related_concepts: tuple[RelatedGlossaryConcept, ...]
    metadata_gaps: tuple[str, ...]
    backing_assets: tuple[str, ...]


@dataclass(frozen=True)
class GlossaryExplorer:
    """Complete glossary explorer view model."""

    concepts: tuple[GlossaryConcept, ...]
    source_label: str = "Marimo dashboard registry"
    freshness_label: str = "Code-local registry snapshot"
    scope_label: str = "Generated gold metadata paths only"


@dataclass(frozen=True)
class _GlossarySeed:
    key: str
    entry: DashboardRegistryEntry
    generated_gold_path: str | None


def build_glossary_explorer(
    entries: Sequence[DashboardRegistryEntry] | None = None,
    related_limit: int = DEFAULT_RELATED_CONCEPT_LIMIT,
) -> GlossaryExplorer:
    """Build a glossary explorer model from the Marimo dashboard registry."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    seeds = _glossary_seeds(candidate_entries)
    concepts = tuple(
        _glossary_concept_from_seed(seed, candidate_entries) for seed in seeds
    )
    concepts = tuple(
        replace(
            concept,
            related_concepts=_related_glossary_concepts(
                concept,
                concepts,
                related_limit,
            ),
        )
        for concept in concepts
    )
    return GlossaryExplorer(concepts=concepts)


def render_glossary_explorer_html(
    explorer: GlossaryExplorer | None = None,
) -> str:
    """Render the glossary explorer as self-contained HTML."""
    glossary_explorer = build_glossary_explorer() if explorer is None else explorer
    concept_cards = "\n".join(
        _render_concept_card(concept) for concept in glossary_explorer.concepts
    )
    concept_links = "\n".join(
        _render_concept_link(concept) for concept in glossary_explorer.concepts
    )
    metadata_gap_count = sum(
        len(concept.metadata_gaps) for concept in glossary_explorer.concepts
    )
    available_dashboard_count = len(
        {
            reference.concept_id
            for concept in glossary_explorer.concepts
            for reference in concept.dashboard_references
            if reference.status is DashboardStatus.AVAILABLE
            and reference.notebook_route is not None
        }
    )
    planned_dashboard_count = len(
        {
            reference.concept_id
            for concept in glossary_explorer.concepts
            for reference in concept.dashboard_references
            if reference.status is DashboardStatus.PLANNED
        }
    )

    return f"""\
<style>
{_glossary_explorer_css()}
</style>
<section
    class="glossary-explorer"
    data-concept-count="{len(glossary_explorer.concepts)}"
    data-metadata-gap-count="{metadata_gap_count}"
>
    <section class="glossary-health" aria-label="Registry health">
        {_health_item("Source", glossary_explorer.source_label)}
        {_health_item("Freshness", glossary_explorer.freshness_label)}
        {_health_item("Concepts", f"{len(glossary_explorer.concepts)} seeded glossary concepts")}
        {_health_item("Scope", glossary_explorer.scope_label)}
        {_health_item("Available dashboards", str(available_dashboard_count))}
        {_health_item("Planned dashboards", str(planned_dashboard_count))}
        {_health_item("Validation gaps", str(metadata_gap_count))}
    </section>
    <nav class="glossary-index" aria-label="Glossary concept index">
{concept_links}
    </nav>
    <section class="glossary-grid" aria-label="Glossary concept details">
{concept_cards}
    </section>
</section>"""


def glossary_concept_by_generated_gold_path(
    explorer: GlossaryExplorer,
    generated_gold_path: str,
) -> GlossaryConcept | None:
    """Return one glossary concept by generated-gold path."""
    for concept in explorer.concepts:
        if concept.generated_gold_path == generated_gold_path:
            return concept
    return None


def _glossary_seeds(
    entries: Sequence[DashboardRegistryEntry],
) -> tuple[_GlossarySeed, ...]:
    seeds_by_key: dict[str, _GlossarySeed] = {}

    for entry in entries:
        glossary_paths = _glossary_page_paths(entry)
        if _is_seed_glossary_entry(entry):
            if len(glossary_paths) == 0:
                key = f"entry:{entry.concept_id}"
                seeds_by_key.setdefault(
                    key,
                    _GlossarySeed(
                        key=key,
                        entry=entry,
                        generated_gold_path=None,
                    ),
                )
            for path in glossary_paths:
                seeds_by_key.setdefault(
                    path,
                    _GlossarySeed(
                        key=path,
                        entry=entry,
                        generated_gold_path=path,
                    ),
                )

    for entry in entries:
        for path in _glossary_page_paths(entry):
            seeds_by_key.setdefault(
                path,
                _GlossarySeed(key=path, entry=entry, generated_gold_path=path),
            )

    return tuple(
        sorted(
            seeds_by_key.values(),
            key=lambda seed: _title_from_seed(seed),
        )
    )


def _glossary_concept_from_seed(
    seed: _GlossarySeed,
    entries: Sequence[DashboardRegistryEntry],
) -> GlossaryConcept:
    source_chunk_ids = seed.entry.source_chunk_ids
    dashboard_references = _dashboard_references_for_seed(seed, entries)
    metadata_gaps = _metadata_gaps(seed.generated_gold_path, source_chunk_ids)

    return GlossaryConcept(
        concept_id=seed.entry.concept_id,
        title=_title_from_seed(seed),
        description=seed.entry.description,
        generated_gold_path=seed.generated_gold_path,
        source_chunk_ids=source_chunk_ids,
        dashboard_references=dashboard_references,
        related_concepts=(),
        metadata_gaps=metadata_gaps,
        backing_assets=seed.entry.backing_assets,
    )


def _dashboard_references_for_seed(
    seed: _GlossarySeed,
    entries: Sequence[DashboardRegistryEntry],
) -> tuple[GlossaryDashboardReference, ...]:
    if seed.generated_gold_path is None:
        linked_entries = (seed.entry,)
    else:
        linked_entries = tuple(
            entry
            for entry in entries
            if seed.generated_gold_path in entry.generated_gold_paths
        )

    references = tuple(
        GlossaryDashboardReference(
            concept_id=entry.concept_id,
            title=entry.title,
            status=entry.status,
            notebook_route=entry.notebook_route,
        )
        for entry in linked_entries
    )
    return tuple(
        sorted(
            references,
            key=lambda reference: (
                0 if reference.status is DashboardStatus.AVAILABLE else 1,
                reference.title,
            ),
        )
    )


def _related_glossary_concepts(
    concept: GlossaryConcept,
    concepts: Sequence[GlossaryConcept],
    limit: int,
) -> tuple[RelatedGlossaryConcept, ...]:
    if limit <= 0:
        return ()

    source_chunks = set(concept.source_chunk_ids)
    dashboard_ids = {reference.concept_id for reference in concept.dashboard_references}
    backing_assets = set(concept.backing_assets)
    scored_concepts: list[tuple[int, str, GlossaryConcept]] = []

    for candidate in concepts:
        if candidate.concept_id == concept.concept_id:
            continue

        score = (
            len(source_chunks & set(candidate.source_chunk_ids)) * 3
            + len(
                dashboard_ids
                & {reference.concept_id for reference in candidate.dashboard_references}
            )
            * 2
            + len(backing_assets & set(candidate.backing_assets))
        )
        if score == 0:
            continue
        scored_concepts.append((score, candidate.title, candidate))

    return tuple(
        RelatedGlossaryConcept(
            concept_id=candidate.concept_id,
            title=candidate.title,
            generated_gold_path=candidate.generated_gold_path,
        )
        for _, _, candidate in sorted(
            scored_concepts,
            key=lambda scored_concept: (-scored_concept[0], scored_concept[1]),
        )[:limit]
    )


def _metadata_gaps(
    generated_gold_path: str | None,
    source_chunk_ids: Sequence[str],
) -> tuple[str, ...]:
    gaps: list[str] = []
    if generated_gold_path is None:
        gaps.append("No generated-gold path recorded in the Marimo registry.")
    if len(source_chunk_ids) == 0:
        gaps.append("No source chunk IDs recorded in the Marimo registry.")
    return tuple(gaps)


def _glossary_page_paths(entry: DashboardRegistryEntry) -> tuple[str, ...]:
    return tuple(
        path
        for path in entry.generated_gold_paths
        if path.startswith(GLOSSARY_GOLD_PREFIX)
        and path.endswith(".md")
        and path != GLOSSARY_INDEX_PATH
    )


def _is_seed_glossary_entry(entry: DashboardRegistryEntry) -> bool:
    return entry.concept_id.endswith(GLOSSARY_CONTEXT_SUFFIX)


def _title_from_seed(seed: _GlossarySeed) -> str:
    if seed.generated_gold_path is not None:
        return _title_from_glossary_path(seed.generated_gold_path)

    title = seed.entry.title
    if title.endswith(" Context"):
        return title[: -len(" Context")]
    return title


def _title_from_glossary_path(generated_gold_path: str) -> str:
    slug = generated_gold_path.removeprefix(GLOSSARY_GOLD_PREFIX).removesuffix(".md")
    special_titles = {
        "bid-offer": "Bid / Offer",
        "hub-zone": "Hub / Zone",
        "mos": "MOS",
    }
    if slug in special_titles:
        return special_titles[slug]
    return " ".join(word.title() for word in slug.split("-"))


def _render_concept_link(concept: GlossaryConcept) -> str:
    return (
        f'        <a href="#glossary-{escape(concept.concept_id, quote=True)}">'
        f"{escape(concept.title)}</a>"
    )


def _render_concept_card(concept: GlossaryConcept) -> str:
    validation_gap = "true" if concept.metadata_gaps else "false"
    generated_path = concept.generated_gold_path or ""

    return f"""\
        <article
            class="glossary-card"
            id="glossary-{escape(concept.concept_id, quote=True)}"
            data-concept-id="{escape(concept.concept_id, quote=True)}"
            data-glossary-path="{escape(generated_path, quote=True)}"
            data-validation-gap="{validation_gap}"
        >
            <div class="glossary-card__header">
                <div>
                    <p class="glossary-card__eyebrow">Glossary concept</p>
                    <h3>{escape(concept.title)}</h3>
                </div>
                {_render_gap_badge(concept)}
            </div>
            <p class="glossary-card__description">{escape(concept.description)}</p>
            {_render_gap_section(concept)}
            {_render_generated_path(concept)}
            {_render_code_list("source chunk IDs", concept.source_chunk_ids)}
            {_render_related_concepts(concept.related_concepts)}
            {_render_dashboard_references(concept.dashboard_references)}
        </article>"""


def _render_gap_badge(concept: GlossaryConcept) -> str:
    if concept.metadata_gaps:
        return '<span class="glossary-badge glossary-badge--warn">Metadata gap</span>'
    return '<span class="glossary-badge glossary-badge--ok">Cited metadata</span>'


def _render_gap_section(concept: GlossaryConcept) -> str:
    if not concept.metadata_gaps:
        return ""

    gaps = "\n".join(
        f"                    <li>{escape(gap)}</li>" for gap in concept.metadata_gaps
    )
    return f"""\
            <section class="glossary-card__section glossary-card__section--gap">
                <h4>validation-visible gaps</h4>
                <ul>
{gaps}
                </ul>
            </section>"""


def _render_generated_path(concept: GlossaryConcept) -> str:
    if concept.generated_gold_path is None:
        body = (
            '<p class="glossary-empty">'
            "No generated-gold path recorded in the Marimo registry."
            "</p>"
        )
    else:
        body = f"<code>{escape(concept.generated_gold_path)}</code>"

    return f"""\
            <section class="glossary-card__section">
                <h4>generated-gold path</h4>
                {body}
            </section>"""


def _render_code_list(title: str, values: Sequence[str]) -> str:
    if len(values) == 0:
        body = (
            '<p class="glossary-empty">'
            f"No {escape(title)} recorded in the Marimo registry."
            "</p>"
        )
    else:
        rows = "\n".join(
            f"                    <li><code>{escape(value)}</code></li>"
            for value in values
        )
        body = f"<ul>\n{rows}\n                </ul>"

    return f"""\
            <section class="glossary-card__section">
                <h4>{escape(title)}</h4>
                {body}
            </section>"""


def _render_related_concepts(
    related_concepts: Sequence[RelatedGlossaryConcept],
) -> str:
    if len(related_concepts) == 0:
        body = (
            '<p class="glossary-empty">'
            "No related concepts share dashboard links, source chunk IDs, "
            "or backing assets in the Marimo registry."
            "</p>"
        )
    else:
        rows = "\n".join(
            _render_related_concept(related_concept)
            for related_concept in related_concepts
        )
        body = f"<ul>\n{rows}\n                </ul>"

    return f"""\
            <section class="glossary-card__section">
                <h4>related concepts</h4>
                {body}
            </section>"""


def _render_related_concept(related_concept: RelatedGlossaryConcept) -> str:
    return f"""\
                    <li>
                        <a href="#glossary-{escape(related_concept.concept_id, quote=True)}">
                            {escape(related_concept.title)}
                        </a>
                        <code>{escape(related_concept.concept_id)}</code>
                    </li>"""


def _render_dashboard_references(
    dashboard_references: Sequence[GlossaryDashboardReference],
) -> str:
    if len(dashboard_references) == 0:
        body = (
            '<p class="glossary-empty">'
            "No dashboard registry entries are linked to this glossary concept."
            "</p>"
        )
    else:
        rows = "\n".join(
            _render_dashboard_reference(reference) for reference in dashboard_references
        )
        body = f"<ul>\n{rows}\n                </ul>"

    return f"""\
            <section class="glossary-card__section">
                <h4>dashboard links/statuses</h4>
                {body}
            </section>"""


def _render_dashboard_reference(reference: GlossaryDashboardReference) -> str:
    status_label = _dashboard_status_label(reference)
    title = escape(reference.title)
    route = reference.notebook_route
    if reference.status is DashboardStatus.AVAILABLE and route is not None:
        title_html = f'<a href="{escape(route, quote=True)}">{title}</a>'
    else:
        title_html = f"<span>{title}</span>"

    return f"""\
                    <li data-dashboard-status="{escape(reference.status.value, quote=True)}">
                        {title_html}
                        <span class="glossary-status">{escape(status_label)}</span>
                        <code>{escape(reference.concept_id)}</code>
                    </li>"""


def _dashboard_status_label(reference: GlossaryDashboardReference) -> str:
    if (
        reference.status is DashboardStatus.AVAILABLE
        and reference.notebook_route is not None
    ):
        return "Available dashboard"
    if reference.status is DashboardStatus.PLANNED:
        return "Planned dashboard"
    return "Unavailable dashboard"


def _health_item(label: str, value: str) -> str:
    return f"""\
        <div class="glossary-health__item">
            <span>{escape(label)}</span>
            <strong>{escape(value)}</strong>
        </div>"""


def _glossary_explorer_css() -> str:
    return """\
.glossary-explorer {
    display: grid;
    gap: 1rem;
    color: var(--emdl-ink, #1b2324);
}

.glossary-health {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
    gap: 0.75rem;
}

.glossary-health__item {
    display: grid;
    gap: 0.2rem;
    min-width: 0;
    padding: 0.75rem 0.85rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.glossary-health__item span {
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.glossary-health__item strong {
    overflow-wrap: anywhere;
}

.glossary-index {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.glossary-index a {
    display: inline-flex;
    align-items: center;
    min-height: 2rem;
    padding: 0.35rem 0.65rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 999px;
    color: var(--emdl-blue, #166791);
    background: rgb(var(--emdl-panel-rgb, 255 255 255) / 0.9);
    font-size: 0.88rem;
    font-weight: 700;
    text-decoration: none;
}

.glossary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 30rem), 1fr));
    gap: 1rem;
}

.glossary-card {
    display: grid;
    align-content: start;
    gap: 0.85rem;
    min-width: 0;
    padding: 1rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
    box-shadow: var(--emdl-soft-shadow, 0 8px 28px rgb(27 35 36 / 0.08));
}

.glossary-card[data-validation-gap="true"] {
    border-color: var(--emdl-amber, #b2682a);
}

.glossary-card__header {
    display: flex;
    align-items: start;
    justify-content: space-between;
    gap: 0.8rem;
}

.glossary-card__eyebrow {
    margin: 0 0 0.2rem;
    color: var(--emdl-green, #3e7a54);
    font-size: 0.72rem;
    font-weight: 740;
    letter-spacing: 0;
    text-transform: uppercase;
}

.glossary-card h3,
.glossary-card h4 {
    margin: 0;
    color: var(--emdl-slate, #354348);
    letter-spacing: 0;
}

.glossary-card h3 {
    font-size: 1.18rem;
    line-height: 1.2;
}

.glossary-card h4 {
    font-size: 0.86rem;
    text-transform: uppercase;
}

.glossary-card__description,
.glossary-empty {
    margin: 0;
    color: var(--emdl-muted, #566365);
}

.glossary-card__section {
    display: grid;
    gap: 0.45rem;
    min-width: 0;
}

.glossary-card__section--gap {
    padding: 0.65rem;
    border: 1px solid rgb(var(--emdl-amber-rgb, 178 104 42) / 0.35);
    border-radius: 6px;
    background: rgb(var(--emdl-amber-rgb, 178 104 42) / 0.1);
}

.glossary-card ul {
    display: grid;
    gap: 0.35rem;
    padding: 0;
    margin: 0;
    list-style: none;
}

.glossary-card li {
    min-width: 0;
    overflow-wrap: anywhere;
}

.glossary-card code {
    color: var(--emdl-slate, #354348);
    white-space: normal;
}

.glossary-card a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
}

.glossary-badge,
.glossary-status {
    display: inline-flex;
    align-items: center;
    width: max-content;
    min-height: 1.55rem;
    padding: 0.2rem 0.5rem;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 760;
}

.glossary-badge--ok {
    color: var(--emdl-green, #3e7a54);
    background: rgb(var(--emdl-green-rgb, 62 122 84) / 0.13);
}

.glossary-badge--warn {
    color: var(--emdl-amber, #b2682a);
    background: rgb(var(--emdl-amber-rgb, 178 104 42) / 0.14);
}

.glossary-status {
    margin-inline: 0.35rem;
    color: var(--emdl-muted, #566365);
    background: var(--emdl-service-band, #eef4f1);
}
"""
