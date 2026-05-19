"""Registry-backed concept-to-asset explorer rendering for Marimo dashboards."""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from html import escape
from urllib.parse import quote

from marimoserver.dashboard_registry import (
    DashboardRegistryEntry,
    DashboardStatus,
    dashboard_registry,
)
from marimoserver.glossary_explorer import (
    GlossaryConcept,
    build_glossary_explorer,
)

CONCEPT_TO_ASSET_EXPLORER_CONCEPT_ID = "concept-to-asset-explorer"
TABLE_EXPLORER_ROUTE = "/marimo/table_explorer/"
CONCEPT_GALLERY_ROUTE = "/marimo"
SILVER_GAS_MODEL_ASSET_PREFIX = "silver.gas_model."


@dataclass(frozen=True)
class ConceptDashboardLink:
    """Dashboard registry entry linked to a Market context concept."""

    concept_id: str
    title: str
    status: DashboardStatus
    notebook_route: str | None
    concept_gallery_route: str

    @property
    def navigation_route(self) -> str:
        """Return the best route for this dashboard reference."""
        if self.status is DashboardStatus.AVAILABLE and self.notebook_route is not None:
            return self.notebook_route
        return self.concept_gallery_route


@dataclass(frozen=True)
class ConceptAssetLink:
    """One backing silver.gas_model asset linked to table explorer."""

    asset_id: str
    table_name: str | None
    table_explorer_route: str | None
    source_concept_ids: tuple[str, ...]
    source_titles: tuple[str, ...]


@dataclass(frozen=True)
class ConceptAssetMapping:
    """One Market context concept and the registry assets supporting it."""

    concept_id: str
    title: str
    description: str
    generated_gold_path: str | None
    source_chunk_ids: tuple[str, ...]
    assets: tuple[ConceptAssetLink, ...]
    available_dashboards: tuple[ConceptDashboardLink, ...]
    planned_dashboards: tuple[ConceptDashboardLink, ...]
    metadata_gaps: tuple[str, ...]

    @property
    def mapped(self) -> bool:
        """Return whether the concept has at least one backing asset."""
        return len(self.assets) > 0


@dataclass(frozen=True)
class ConceptAssetExplorer:
    """Complete concept-to-asset explorer view model."""

    concept_mappings: tuple[ConceptAssetMapping, ...]
    unmapped_assets: tuple[ConceptAssetLink, ...]
    source_label: str = "Marimo dashboard registry"
    freshness_label: str = "Code-local registry snapshot"
    scope_label: str = "Generated-gold glossary concepts and silver.gas_model assets"

    @property
    def unmapped_concepts(self) -> tuple[ConceptAssetMapping, ...]:
        """Return concepts that have no backing silver.gas_model assets."""
        return tuple(mapping for mapping in self.concept_mappings if not mapping.mapped)

    @property
    def mapped_assets(self) -> tuple[ConceptAssetLink, ...]:
        """Return distinct assets that are mapped to at least one concept."""
        links: dict[str, ConceptAssetLink] = {}
        for mapping in self.concept_mappings:
            for asset in mapping.assets:
                links.setdefault(asset.asset_id, asset)
        return tuple(links[asset_id] for asset_id in sorted(links))


def build_concept_asset_explorer(
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> ConceptAssetExplorer:
    """Build a concept-to-asset explorer model from the Marimo registry."""
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    entries_by_concept_id = {entry.concept_id: entry for entry in candidate_entries}
    glossary_explorer = build_glossary_explorer(candidate_entries)
    concept_mappings = tuple(
        _concept_asset_mapping(concept, entries_by_concept_id)
        for concept in glossary_explorer.concepts
    )
    mapped_asset_ids = {
        asset.asset_id for mapping in concept_mappings for asset in mapping.assets
    }
    unmapped_assets = _unmapped_asset_links(candidate_entries, mapped_asset_ids)
    return ConceptAssetExplorer(
        concept_mappings=concept_mappings,
        unmapped_assets=unmapped_assets,
    )


def concept_mapping_by_title(
    explorer: ConceptAssetExplorer,
    title: str,
) -> ConceptAssetMapping | None:
    """Return one concept mapping by case-insensitive title."""
    normalized_title = title.strip().casefold()
    for mapping in explorer.concept_mappings:
        if mapping.title.casefold() == normalized_title:
            return mapping
    return None


def table_explorer_route_for_asset(asset_id: str) -> str | None:
    """Return a table explorer deep link for a registry backing asset."""
    table_name = table_name_from_asset_id(asset_id)
    if table_name is None:
        return None
    entry_id = f"asset:silver/gas_model/{table_name}"
    return f"{TABLE_EXPLORER_ROUTE}?asset={quote(entry_id, safe='')}"


def table_name_from_asset_id(asset_id: str) -> str | None:
    """Return a silver.gas_model table name from a registry asset ID."""
    stripped_asset_id = asset_id.strip()
    if not stripped_asset_id.startswith(SILVER_GAS_MODEL_ASSET_PREFIX):
        return None
    table_name = stripped_asset_id.removeprefix(SILVER_GAS_MODEL_ASSET_PREFIX)
    if table_name == "" or "/" in table_name:
        return None
    return table_name


def render_concept_asset_explorer_html(
    explorer: ConceptAssetExplorer | None = None,
) -> str:
    """Render the concept-to-asset explorer as self-contained HTML."""
    concept_explorer = build_concept_asset_explorer() if explorer is None else explorer
    concept_links = "\n".join(
        _render_concept_index_link(mapping)
        for mapping in concept_explorer.concept_mappings
    )
    concept_cards = "\n".join(
        _render_concept_mapping_card(mapping)
        for mapping in concept_explorer.concept_mappings
    )
    available_dashboard_count = len(
        {
            dashboard.concept_id
            for mapping in concept_explorer.concept_mappings
            for dashboard in mapping.available_dashboards
        }
    )
    planned_dashboard_count = len(
        {
            dashboard.concept_id
            for mapping in concept_explorer.concept_mappings
            for dashboard in mapping.planned_dashboards
        }
    )

    return f"""\
<style>
{_concept_asset_explorer_css()}
</style>
<section
    class="concept-asset-explorer"
    data-concept-count="{len(concept_explorer.concept_mappings)}"
    data-mapped-asset-count="{len(concept_explorer.mapped_assets)}"
    data-unmapped-concept-count="{len(concept_explorer.unmapped_concepts)}"
    data-unmapped-asset-count="{len(concept_explorer.unmapped_assets)}"
>
    <section class="concept-asset-health" aria-label="Registry coverage health">
        {_health_item("Source", concept_explorer.source_label)}
        {_health_item("Freshness", concept_explorer.freshness_label)}
        {_health_item("Scope", concept_explorer.scope_label)}
        {_health_item("Concepts", f"{len(concept_explorer.concept_mappings)} glossary concepts")}
        {_health_item("Mapped assets", str(len(concept_explorer.mapped_assets)))}
        {_health_item("Available dashboards", str(available_dashboard_count))}
        {_health_item("Planned dashboards", str(planned_dashboard_count))}
        {_health_item("Coverage gaps", _coverage_gap_label(concept_explorer))}
    </section>
    <nav class="concept-asset-index" aria-label="Market context concepts">
{concept_links}
    </nav>
    <section class="concept-asset-grid" aria-label="Concept-to-asset mappings">
{concept_cards}
    </section>
    {_render_coverage_gaps(concept_explorer)}
</section>"""


def _concept_asset_mapping(
    concept: GlossaryConcept,
    entries_by_concept_id: dict[str, DashboardRegistryEntry],
) -> ConceptAssetMapping:
    source_entries = tuple(
        entry
        for reference in concept.dashboard_references
        if (entry := entries_by_concept_id.get(reference.concept_id)) is not None
    )
    asset_ids = _sorted_unique(
        asset_id for entry in source_entries for asset_id in entry.backing_assets
    )
    assets = tuple(_asset_link(asset_id, source_entries) for asset_id in asset_ids)
    dashboard_links = tuple(
        _dashboard_link(entry)
        for entry in source_entries
        if entry.concept_id != CONCEPT_TO_ASSET_EXPLORER_CONCEPT_ID
    )
    available_dashboards = tuple(
        link for link in dashboard_links if link.status is DashboardStatus.AVAILABLE
    )
    planned_dashboards = tuple(
        link for link in dashboard_links if link.status is DashboardStatus.PLANNED
    )
    metadata_gaps = list(concept.metadata_gaps)
    if len(assets) == 0:
        metadata_gaps.append(
            "No backing silver.gas_model assets are mapped to this concept."
        )

    return ConceptAssetMapping(
        concept_id=concept.concept_id,
        title=concept.title,
        description=concept.description,
        generated_gold_path=concept.generated_gold_path,
        source_chunk_ids=concept.source_chunk_ids,
        assets=assets,
        available_dashboards=available_dashboards,
        planned_dashboards=planned_dashboards,
        metadata_gaps=tuple(metadata_gaps),
    )


def _unmapped_asset_links(
    entries: Sequence[DashboardRegistryEntry],
    mapped_asset_ids: set[str],
) -> tuple[ConceptAssetLink, ...]:
    all_asset_ids = _sorted_unique(
        asset_id for entry in entries for asset_id in entry.backing_assets
    )
    unmapped_asset_ids = tuple(
        asset_id for asset_id in all_asset_ids if asset_id not in mapped_asset_ids
    )
    return tuple(_asset_link(asset_id, entries) for asset_id in unmapped_asset_ids)


def _asset_link(
    asset_id: str,
    source_entries: Sequence[DashboardRegistryEntry],
) -> ConceptAssetLink:
    source_matches = tuple(
        entry for entry in source_entries if asset_id in entry.backing_assets
    )
    return ConceptAssetLink(
        asset_id=asset_id,
        table_name=table_name_from_asset_id(asset_id),
        table_explorer_route=table_explorer_route_for_asset(asset_id),
        source_concept_ids=tuple(entry.concept_id for entry in source_matches),
        source_titles=tuple(entry.title for entry in source_matches),
    )


def _dashboard_link(entry: DashboardRegistryEntry) -> ConceptDashboardLink:
    return ConceptDashboardLink(
        concept_id=entry.concept_id,
        title=entry.title,
        status=entry.status,
        notebook_route=entry.notebook_route,
        concept_gallery_route=_concept_gallery_route(entry.concept_id),
    )


def _sorted_unique(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted(dict.fromkeys(values)))


def _coverage_gap_label(explorer: ConceptAssetExplorer) -> str:
    gap_count = len(explorer.unmapped_concepts) + len(explorer.unmapped_assets)
    if gap_count == 0:
        return "0"
    return f"{gap_count} visible"


def _concept_gallery_route(concept_id: str) -> str:
    return f"{CONCEPT_GALLERY_ROUTE}#concept-{quote(concept_id, safe='')}"


def _render_concept_index_link(mapping: ConceptAssetMapping) -> str:
    return (
        f'        <a href="#concept-asset-{escape(mapping.concept_id, quote=True)}">'
        f"{escape(mapping.title)}</a>"
    )


def _render_concept_mapping_card(mapping: ConceptAssetMapping) -> str:
    generated_gold_path = mapping.generated_gold_path or ""
    coverage_state = "mapped" if mapping.mapped else "unmapped-concept"
    return f"""\
        <article
            class="concept-asset-card"
            id="concept-asset-{escape(mapping.concept_id, quote=True)}"
            data-concept-id="{escape(mapping.concept_id, quote=True)}"
            data-generated-gold-path="{escape(generated_gold_path, quote=True)}"
            data-coverage-state="{coverage_state}"
        >
            <div class="concept-asset-card__header">
                <div>
                    <p class="concept-asset-card__eyebrow">Market context concept</p>
                    <h3>{escape(mapping.title)}</h3>
                </div>
                {_coverage_badge(mapping)}
            </div>
            <p class="concept-asset-card__description">{escape(mapping.description)}</p>
            {_render_metadata_gaps(mapping.metadata_gaps)}
            {_render_asset_list("Backing assets", mapping.assets)}
            {_render_dashboard_links("Available dashboards", mapping.available_dashboards)}
            {_render_dashboard_links("Planned dashboards", mapping.planned_dashboards)}
            {_render_code_list("Generated-gold path", _single_value_tuple(mapping.generated_gold_path))}
            {_render_code_list("Source chunk IDs", mapping.source_chunk_ids)}
        </article>"""


def _coverage_badge(mapping: ConceptAssetMapping) -> str:
    if mapping.mapped:
        return '<span class="concept-asset-badge concept-asset-badge--ok">Mapped</span>'
    return '<span class="concept-asset-badge concept-asset-badge--warn">Coverage gap</span>'


def _render_metadata_gaps(gaps: Sequence[str]) -> str:
    if len(gaps) == 0:
        return ""
    items = "\n".join(f"                    <li>{escape(gap)}</li>" for gap in gaps)
    return f"""\
            <section class="concept-asset-card__section concept-asset-card__section--gap">
                <h4>coverage gaps</h4>
                <ul>
{items}
                </ul>
            </section>"""


def _render_asset_list(title: str, assets: Sequence[ConceptAssetLink]) -> str:
    if len(assets) == 0:
        body = (
            '<p class="concept-asset-empty">'
            "No backing silver.gas_model assets are mapped in the registry."
            "</p>"
        )
    else:
        rows = "\n".join(_render_asset_item(asset) for asset in assets)
        body = f"<ul>\n{rows}\n                </ul>"

    return f"""\
            <section class="concept-asset-card__section">
                <h4>{escape(title)}</h4>
                {body}
            </section>"""


def _render_asset_item(asset: ConceptAssetLink) -> str:
    table_route = asset.table_explorer_route
    if table_route is None:
        table_link = '<span class="concept-asset-muted">No table explorer link</span>'
    else:
        table_link = (
            f'<a href="{escape(table_route, quote=True)}" '
            'data-link-scope="table explorer entry">Open table</a>'
        )
    source_titles = ", ".join(asset.source_titles)
    source_detail = (
        "No source dashboard recorded"
        if source_titles == ""
        else f"Source: {source_titles}"
    )
    return f"""\
                    <li data-asset-id="{escape(asset.asset_id, quote=True)}">
                        <code>{escape(asset.asset_id)}</code>
                        <span>{escape(source_detail)}</span>
                        {table_link}
                    </li>"""


def _render_dashboard_links(
    title: str,
    dashboards: Sequence[ConceptDashboardLink],
) -> str:
    if len(dashboards) == 0:
        body = (
            '<p class="concept-asset-empty">'
            f"No {escape(title.lower())} are linked in the registry."
            "</p>"
        )
    else:
        rows = "\n".join(_render_dashboard_link(dashboard) for dashboard in dashboards)
        body = f"<ul>\n{rows}\n                </ul>"

    return f"""\
            <section class="concept-asset-card__section">
                <h4>{escape(title)}</h4>
                {body}
            </section>"""


def _render_dashboard_link(dashboard: ConceptDashboardLink) -> str:
    return f"""\
                    <li data-dashboard-status="{escape(dashboard.status.value, quote=True)}">
                        <a href="{escape(dashboard.navigation_route, quote=True)}">
                            {escape(dashboard.title)}
                        </a>
                        <code>{escape(dashboard.concept_id)}</code>
                    </li>"""


def _render_code_list(title: str, values: Sequence[str]) -> str:
    if len(values) == 0:
        body = (
            '<p class="concept-asset-empty">'
            f"No {escape(title.lower())} recorded in the registry."
            "</p>"
        )
    else:
        rows = "\n".join(
            f"                    <li><code>{escape(value)}</code></li>"
            for value in values
        )
        body = f"<ul>\n{rows}\n                </ul>"

    return f"""\
            <section class="concept-asset-card__section">
                <h4>{escape(title)}</h4>
                {body}
            </section>"""


def _single_value_tuple(value: str | None) -> tuple[str, ...]:
    if value is None:
        return ()
    return (value,)


def _render_coverage_gaps(explorer: ConceptAssetExplorer) -> str:
    return f"""\
    <section class="concept-asset-gaps" aria-label="Coverage gaps">
        <article class="concept-asset-gap-panel" data-gap-kind="unmapped-concepts">
            <h3>Unmapped concepts</h3>
            {_render_unmapped_concepts(explorer.unmapped_concepts)}
        </article>
        <article class="concept-asset-gap-panel" data-gap-kind="unmapped-assets">
            <h3>Unmapped assets</h3>
            {_render_unmapped_assets(explorer.unmapped_assets)}
        </article>
    </section>"""


def _render_unmapped_concepts(
    mappings: Sequence[ConceptAssetMapping],
) -> str:
    if len(mappings) == 0:
        return (
            '<p class="concept-asset-empty">'
            "No unmapped registry glossary concepts detected."
            "</p>"
        )

    rows = "\n".join(
        f"""\
                <li data-concept-id="{escape(mapping.concept_id, quote=True)}">
                    <a href="#concept-asset-{escape(mapping.concept_id, quote=True)}">
                        {escape(mapping.title)}
                    </a>
                    <span>{escape("; ".join(mapping.metadata_gaps))}</span>
                </li>"""
        for mapping in mappings
    )
    return f"<ul>\n{rows}\n            </ul>"


def _render_unmapped_assets(assets: Sequence[ConceptAssetLink]) -> str:
    if len(assets) == 0:
        return (
            '<p class="concept-asset-empty">'
            "No unmapped registry backing assets detected."
            "</p>"
        )

    rows = "\n".join(_render_unmapped_asset(asset) for asset in assets)
    return f"<ul>\n{rows}\n            </ul>"


def _render_unmapped_asset(asset: ConceptAssetLink) -> str:
    table_route = asset.table_explorer_route
    source_titles = ", ".join(asset.source_titles)
    if table_route is None:
        table_link = '<span class="concept-asset-muted">No table explorer link</span>'
    else:
        table_link = f'<a href="{escape(table_route, quote=True)}">Open table</a>'
    return f"""\
                <li data-asset-id="{escape(asset.asset_id, quote=True)}">
                    <code>{escape(asset.asset_id)}</code>
                    <span>{escape(source_titles or "No source dashboard recorded")}</span>
                    {table_link}
                </li>"""


def _health_item(label: str, value: str) -> str:
    return f"""\
        <div class="concept-asset-health__item">
            <span>{escape(label)}</span>
            <strong>{escape(value)}</strong>
        </div>"""


def _concept_asset_explorer_css() -> str:
    return """\
.concept-asset-explorer {
    display: grid;
    gap: 1rem;
    color: var(--emdl-ink, #1b2324);
}

.concept-asset-health {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(12rem, 1fr));
    gap: 0.75rem;
}

.concept-asset-health__item,
.concept-asset-card,
.concept-asset-gap-panel {
    min-width: 0;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
}

.concept-asset-health__item {
    display: grid;
    gap: 0.2rem;
    padding: 0.75rem 0.85rem;
}

.concept-asset-health__item span,
.concept-asset-card__eyebrow {
    color: var(--emdl-green, #3e7a54);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.concept-asset-health__item strong,
.concept-asset-card code,
.concept-asset-gap-panel code {
    overflow-wrap: anywhere;
}

.concept-asset-index {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.concept-asset-index a {
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

.concept-asset-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 34rem), 1fr));
    gap: 1rem;
}

.concept-asset-card,
.concept-asset-gap-panel {
    display: grid;
    align-content: start;
    gap: 0.85rem;
    padding: 1rem;
    box-shadow: var(--emdl-soft-shadow, 0 8px 28px rgb(27 35 36 / 0.08));
}

.concept-asset-card[data-coverage-state="unmapped-concept"],
.concept-asset-card__section--gap,
.concept-asset-gap-panel {
    border-color: var(--emdl-amber, #b2682a);
}

.concept-asset-card__header {
    display: flex;
    align-items: start;
    justify-content: space-between;
    gap: 0.75rem;
}

.concept-asset-card h3,
.concept-asset-gap-panel h3 {
    margin: 0;
    color: var(--emdl-slate, #354348);
    font-size: 1.15rem;
    line-height: 1.2;
    letter-spacing: 0;
}

.concept-asset-card__description,
.concept-asset-empty,
.concept-asset-muted {
    color: var(--emdl-muted, #566365);
}

.concept-asset-card__section {
    display: grid;
    gap: 0.45rem;
}

.concept-asset-card__section h4 {
    margin: 0;
    color: var(--emdl-slate, #354348);
    font-size: 0.86rem;
    letter-spacing: 0;
}

.concept-asset-card ul,
.concept-asset-gap-panel ul {
    display: grid;
    gap: 0.5rem;
    padding: 0;
    margin: 0;
    list-style: none;
}

.concept-asset-card li,
.concept-asset-gap-panel li {
    display: grid;
    gap: 0.25rem;
    padding: 0.55rem 0.65rem;
    border: 1px solid rgb(var(--emdl-line-rgb, 207 219 214) / 0.7);
    border-radius: 8px;
    background: var(--emdl-paper, #f6f8f3);
}

.concept-asset-card a,
.concept-asset-gap-panel a {
    color: var(--emdl-blue, #166791);
    font-weight: 720;
    text-decoration: none;
}

.concept-asset-badge {
    flex: none;
    padding: 0.25rem 0.5rem;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 760;
}

.concept-asset-badge--ok {
    color: var(--emdl-green, #3e7a54);
    background: rgb(var(--emdl-green-rgb, 62 122 84) / 0.13);
}

.concept-asset-badge--warn {
    color: var(--emdl-amber, #b2682a);
    background: rgb(var(--emdl-amber-rgb, 178 104 42) / 0.14);
}

.concept-asset-gaps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 28rem), 1fr));
    gap: 1rem;
}
"""
