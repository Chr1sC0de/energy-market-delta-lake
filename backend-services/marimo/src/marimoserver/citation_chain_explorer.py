"""Registry-backed citation-chain explorer rendering for Marimo dashboards."""

from collections.abc import Sequence
from dataclasses import dataclass
from html import escape

from marimoserver.dashboard_registry import (
    DashboardRegistryEntry,
    DashboardStatus,
    SourceChunkReference,
    dashboard_registry,
)


@dataclass(frozen=True)
class CitationChainChunk:
    """One source chunk reference in a registry citation chain."""

    chunk_id: str
    silver_chunk_path: str | None
    source_hash: str | None
    metadata_gaps: tuple[str, ...]

    @property
    def complete(self) -> bool:
        """Return whether the source chunk has path and hash metadata."""
        return len(self.metadata_gaps) == 0


@dataclass(frozen=True)
class CitationChainConcept:
    """One dashboard registry entry prepared for citation-chain inspection."""

    concept_id: str
    title: str
    description: str
    status: DashboardStatus
    notebook_route: str | None
    market_context_ids: tuple[str, ...]
    source_chunks: tuple[CitationChainChunk, ...]
    backing_assets: tuple[str, ...]
    metadata_gaps: tuple[str, ...]

    @property
    def complete(self) -> bool:
        """Return whether this concept has a complete citation chain."""
        return len(self.metadata_gaps) == 0


@dataclass(frozen=True)
class CitationChainExplorer:
    """Complete citation-chain explorer view model."""

    concepts: tuple[CitationChainConcept, ...]
    source_label: str = "Marimo dashboard registry"
    freshness_label: str = "Code-local registry snapshot"
    scope_label: str = (
        "Concept metadata, Market context IDs, source chunks, and source hashes"
    )

    @property
    def complete_concepts(self) -> tuple[CitationChainConcept, ...]:
        """Return concepts with complete citation-chain metadata."""
        return tuple(concept for concept in self.concepts if concept.complete)

    @property
    def coverage_gap_count(self) -> int:
        """Return the total number of registry citation-chain metadata gaps."""
        return sum(len(concept.metadata_gaps) for concept in self.concepts)

    @property
    def source_reference_count(self) -> int:
        """Return the total source chunk reference count."""
        return sum(len(concept.source_chunks) for concept in self.concepts)

    @property
    def source_hashes(self) -> tuple[str, ...]:
        """Return distinct source hashes visible in the citation-chain explorer."""
        source_hashes: list[str] = []
        for concept in self.concepts:
            for chunk in concept.source_chunks:
                if (
                    chunk.source_hash is not None
                    and chunk.source_hash not in source_hashes
                ):
                    source_hashes.append(chunk.source_hash)
        return tuple(source_hashes)


def build_citation_chain_explorer(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> CitationChainExplorer:
    """Build a citation-chain explorer model from the Marimo registry."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    concepts = tuple(
        _citation_chain_concept(entry)
        for entry in sorted(candidate_entries, key=lambda candidate: candidate.title)
    )
    return CitationChainExplorer(concepts=concepts)


def render_citation_chain_explorer_html(
    explorer: CitationChainExplorer | None = None,
) -> str:
    """Render the citation-chain explorer as self-contained HTML."""
    citation_explorer = (
        build_citation_chain_explorer() if explorer is None else explorer
    )
    concept_links = "\n".join(
        _render_concept_link(concept) for concept in citation_explorer.concepts
    )
    concept_cards = "\n".join(
        _render_concept_card(concept) for concept in citation_explorer.concepts
    )

    return f"""\
<style>
{_citation_chain_explorer_css()}
</style>
<section
    class="citation-chain-explorer"
    data-concept-count="{len(citation_explorer.concepts)}"
    data-complete-concept-count="{len(citation_explorer.complete_concepts)}"
    data-coverage-gap-count="{citation_explorer.coverage_gap_count}"
>
    <section class="citation-chain-health" aria-label="Registry citation health">
        {_health_item("Source", citation_explorer.source_label)}
        {_health_item("Freshness", citation_explorer.freshness_label)}
        {_health_item("Scope", citation_explorer.scope_label)}
        {_health_item("Concepts", str(len(citation_explorer.concepts)))}
        {_health_item("Complete records", str(len(citation_explorer.complete_concepts)))}
        {_health_item("Coverage gaps", str(citation_explorer.coverage_gap_count))}
        {_health_item("Source chunks", str(citation_explorer.source_reference_count))}
        {_health_item("Source hashes", str(len(citation_explorer.source_hashes)))}
    </section>
    <nav class="citation-chain-index" aria-label="Citation-chain concepts">
{concept_links}
    </nav>
    <section class="citation-chain-grid" aria-label="Citation-chain records">
{concept_cards}
    </section>
</section>"""


def _citation_chain_concept(
    entry: DashboardRegistryEntry,
) -> CitationChainConcept:
    source_chunks = tuple(_citation_chain_chunk(chunk) for chunk in entry.source_chunks)
    metadata_gaps = _concept_metadata_gaps(entry, source_chunks)
    return CitationChainConcept(
        concept_id=entry.concept_id,
        title=entry.title,
        description=entry.description,
        status=entry.status,
        notebook_route=entry.notebook_route,
        market_context_ids=entry.market_context_ids,
        source_chunks=source_chunks,
        backing_assets=entry.backing_assets,
        metadata_gaps=metadata_gaps,
    )


def _citation_chain_chunk(chunk: SourceChunkReference) -> CitationChainChunk:
    gaps: list[str] = []
    if chunk.silver_chunk_path is None:
        gaps.append(f"No silver chunk path recorded for `{chunk.chunk_id}`.")
    if chunk.source_hash is None:
        gaps.append(f"No source hash recorded for `{chunk.chunk_id}`.")
    return CitationChainChunk(
        chunk_id=chunk.chunk_id,
        silver_chunk_path=chunk.silver_chunk_path,
        source_hash=chunk.source_hash,
        metadata_gaps=tuple(gaps),
    )


def _concept_metadata_gaps(
    entry: DashboardRegistryEntry,
    source_chunks: Sequence[CitationChainChunk],
) -> tuple[str, ...]:
    gaps: list[str] = []
    if len(entry.market_context_ids) == 0:
        gaps.append("No Market context ID recorded in the Marimo registry.")
    if len(entry.source_chunks) == 0:
        gaps.append("No source chunk IDs recorded in the Marimo registry.")
    for chunk in source_chunks:
        gaps.extend(chunk.metadata_gaps)
    return tuple(gaps)


def _render_concept_link(concept: CitationChainConcept) -> str:
    return (
        f'        <a href="#citation-chain-{escape(concept.concept_id, quote=True)}">'
        f"{escape(concept.title)}</a>"
    )


def _render_concept_card(concept: CitationChainConcept) -> str:
    coverage_state = "complete" if concept.complete else "gap"
    return f"""\
        <article
            class="citation-chain-card"
            id="citation-chain-{escape(concept.concept_id, quote=True)}"
            data-concept-id="{escape(concept.concept_id, quote=True)}"
            data-coverage-state="{coverage_state}"
        >
            <div class="citation-chain-card__header">
                <div>
                    <p class="citation-chain-card__eyebrow">Registry concept</p>
                    <h3>{escape(concept.title)}</h3>
                </div>
                {_render_badge(concept)}
            </div>
            <p class="citation-chain-card__description">
                {escape(concept.description)}
            </p>
            <dl class="citation-chain-card__metadata">
                {_definition_item("Concept ID", concept.concept_id)}
                {_definition_item("Status", concept.status.value)}
                {_definition_item("Route", concept.notebook_route or "No route")}
            </dl>
            {_render_gap_section(concept)}
            {_render_code_list("Market context IDs", concept.market_context_ids)}
            {_render_chunk_list(concept.source_chunks)}
            {_render_code_list("backing assets", concept.backing_assets)}
        </article>"""


def _render_badge(concept: CitationChainConcept) -> str:
    if concept.complete:
        return '<span class="citation-chain-badge citation-chain-badge--ok">Complete</span>'
    return '<span class="citation-chain-badge citation-chain-badge--warn">Coverage gap</span>'


def _render_gap_section(concept: CitationChainConcept) -> str:
    if concept.complete:
        return ""

    gap_rows = "\n".join(
        f"                    <li>{escape(gap)}</li>" for gap in concept.metadata_gaps
    )
    return f"""\
            <section class="citation-chain-card__section citation-chain-card__section--gap">
                <h4>registry coverage gaps</h4>
                <ul>
{gap_rows}
                </ul>
            </section>"""


def _render_chunk_list(chunks: Sequence[CitationChainChunk]) -> str:
    if len(chunks) == 0:
        body = (
            '<p class="citation-chain-empty">'
            "No source chunks recorded in the Marimo registry."
            "</p>"
        )
    else:
        rows = "\n".join(_render_chunk(chunk) for chunk in chunks)
        body = f"<ul>\n{rows}\n                </ul>"

    return f"""\
            <section class="citation-chain-card__section">
                <h4>source chunk chain</h4>
                {body}
            </section>"""


def _render_chunk(chunk: CitationChainChunk) -> str:
    complete = "true" if chunk.complete else "false"
    silver_chunk_path = chunk.silver_chunk_path or "No silver chunk path recorded"
    source_hash = chunk.source_hash or "No source hash recorded"
    return f"""\
                    <li data-chunk-complete="{complete}">
                        <strong>{escape(chunk.chunk_id)}</strong>
                        <dl>
                            {_definition_item("Silver chunk path", silver_chunk_path)}
                            {_definition_item("Source hash", source_hash)}
                        </dl>
                    </li>"""


def _render_code_list(title: str, values: Sequence[str]) -> str:
    if len(values) == 0:
        body = (
            '<p class="citation-chain-empty">'
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
            <section class="citation-chain-card__section">
                <h4>{escape(title)}</h4>
                {body}
            </section>"""


def _definition_item(label: str, value: str) -> str:
    return f"""\
                    <div>
                        <dt>{escape(label)}</dt>
                        <dd>{escape(value)}</dd>
                    </div>"""


def _health_item(label: str, value: str) -> str:
    return f"""\
        <div class="citation-chain-health__item">
            <span>{escape(label)}</span>
            <strong>{escape(value)}</strong>
        </div>"""


def _citation_chain_explorer_css() -> str:
    return """\
.citation-chain-explorer {
    display: grid;
    gap: 1rem;
    color: var(--emdl-ink, #1b2324);
}

.citation-chain-health {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
    gap: 0.75rem;
}

.citation-chain-health__item,
.citation-chain-card {
    min-width: 0;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.citation-chain-health__item {
    display: grid;
    gap: 0.2rem;
    padding: 0.75rem 0.85rem;
}

.citation-chain-health__item span,
.citation-chain-card__eyebrow {
    color: var(--emdl-green, #3e7a54);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.citation-chain-health__item strong,
.citation-chain-card code,
.citation-chain-card dd {
    overflow-wrap: anywhere;
}

.citation-chain-index {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.citation-chain-index a {
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

.citation-chain-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 34rem), 1fr));
    gap: 1rem;
}

.citation-chain-card {
    display: grid;
    align-content: start;
    gap: 0.85rem;
    padding: 1rem;
    box-shadow: var(--emdl-soft-shadow, 0 8px 28px rgb(27 35 36 / 0.08));
}

.citation-chain-card[data-coverage-state="gap"],
.citation-chain-card__section--gap {
    border-color: var(--emdl-amber, #b2682a);
}

.citation-chain-card__header {
    display: flex;
    align-items: start;
    justify-content: space-between;
    gap: 0.75rem;
}

.citation-chain-card h3 {
    margin: 0;
    color: var(--emdl-slate, #354348);
    font-size: 1.15rem;
    line-height: 1.2;
    letter-spacing: 0;
}

.citation-chain-card h4 {
    margin: 0;
    color: var(--emdl-slate, #354348);
    font-size: 0.86rem;
    letter-spacing: 0;
    text-transform: uppercase;
}

.citation-chain-card__description,
.citation-chain-empty {
    margin: 0;
    color: var(--emdl-muted, #566365);
}

.citation-chain-card__metadata,
.citation-chain-card dl {
    display: grid;
    gap: 0.35rem;
    margin: 0;
}

.citation-chain-card__metadata div,
.citation-chain-card li dl div {
    display: grid;
    gap: 0.1rem;
}

.citation-chain-card dt {
    color: var(--emdl-muted, #566365);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.citation-chain-card dd {
    margin: 0;
}

.citation-chain-card__section {
    display: grid;
    gap: 0.45rem;
    min-width: 0;
}

.citation-chain-card__section--gap {
    padding: 0.65rem;
    border: 1px solid rgb(var(--emdl-amber-rgb, 178 104 42) / 0.35);
    border-radius: 6px;
    background: rgb(var(--emdl-amber-rgb, 178 104 42) / 0.1);
}

.citation-chain-card ul {
    display: grid;
    gap: 0.5rem;
    padding: 0;
    margin: 0;
    list-style: none;
}

.citation-chain-card li {
    min-width: 0;
    overflow-wrap: anywhere;
}

.citation-chain-card__section > ul > li {
    display: grid;
    gap: 0.35rem;
    padding: 0.55rem 0.65rem;
    border: 1px solid rgb(var(--emdl-line-rgb, 207 219 214) / 0.7);
    border-radius: 8px;
    background: var(--emdl-paper, #f6f8f3);
}

.citation-chain-card li[data-chunk-complete="false"] {
    border-color: rgb(var(--emdl-amber-rgb, 178 104 42) / 0.45);
}

.citation-chain-badge {
    flex: none;
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 760;
}

.citation-chain-badge--ok {
    color: var(--emdl-green, #3e7a54);
    background: rgb(var(--emdl-green-rgb, 62 122 84) / 0.13);
}

.citation-chain-badge--warn {
    color: var(--emdl-amber, #b2682a);
    background: rgb(var(--emdl-amber-rgb, 178 104 42) / 0.14);
}
"""
