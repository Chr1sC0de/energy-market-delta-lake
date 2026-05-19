"""Source table lineage explorer helpers for Marimo dashboards."""

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from html import escape
from math import isnan
from urllib.parse import quote

import polars as pl

from marimoserver.dashboard_registry import (
    DashboardRegistryEntry,
    dashboard_registry,
)
from marimoserver.gas_dashboard import (
    SOURCE_COVERAGE_STATE_COVERED,
    SOURCE_COVERAGE_STATE_EMPTY,
    SOURCE_COVERAGE_STATE_GAP,
    SOURCE_COVERAGE_STATE_UNAVAILABLE,
    GasTableLoad,
)
from marimoserver.gas_model_loader import format_row_limit

SOURCE_LINEAGE_EXPLORER_CONCEPT_ID = "source-table-lineage-explorer"
SOURCE_LINEAGE_TABLE_EXPLORER_ROUTE = "/marimo/table_explorer/"
SOURCE_LINEAGE_CONCEPT_GALLERY_ROUTE = "/marimo"
SILVER_GAS_MODEL_ASSET_PREFIX = "silver.gas_model."
DEFAULT_SOURCE_LINEAGE_EXAMPLE_LIMIT = 3

_SOURCE_LINEAGE_MISSING_SOURCE_SYSTEM_COLUMN = (
    "(missing source_system/source_systems column)"
)
_SOURCE_LINEAGE_EMPTY_SOURCE_SYSTEM_VALUE = "(empty source_system/source_systems value)"
_SOURCE_LINEAGE_MISSING_SOURCE_TABLE_COLUMN = (
    "(missing source_table/source_tables column)"
)
_SOURCE_LINEAGE_EMPTY_SOURCE_TABLE_VALUE = "(empty source_table/source_tables value)"
_SOURCE_LINEAGE_NO_EXTRA_FIELDS = "(no additional source lineage fields)"
_SOURCE_LINEAGE_NO_POPULATED_VALUES = "(no populated source lineage values)"
_SOURCE_LINEAGE_NO_CONCEPT_CARD = "(no mapped concept card)"
_SOURCE_LINEAGE_NO_DASHBOARD_ROUTE = "(no mapped dashboard route)"
_SOURCE_LINEAGE_NO_MARKET_CONTEXT_PATH = "(no generated Market context path mapped)"
_SOURCE_LINEAGE_NO_SOURCE_CHUNKS = "(no source chunk IDs mapped)"

_SOURCE_LINEAGE_CORE_COLUMNS = frozenset(
    {"source_system", "source_systems", "source_table", "source_tables"}
)
_SOURCE_LINEAGE_SYSTEM_COLUMNS = ("source_system", "source_systems")
_SOURCE_LINEAGE_TABLE_COLUMNS = ("source_table", "source_tables")
_SOURCE_LINEAGE_SCHEMA = {
    "asset": pl.String,
    "section": pl.String,
    "table": pl.String,
    "source system": pl.String,
    "source table": pl.String,
    "coverage state": pl.String,
    "rows loaded": pl.UInt32,
    "row limit": pl.String,
    "source fields": pl.String,
    "lineage fields": pl.String,
    "lineage examples": pl.String,
    "concept cards": pl.String,
    "dashboard routes": pl.String,
    "Market context paths": pl.String,
    "source chunk ids": pl.String,
    "table explorer": pl.String,
    "asset metadata": pl.String,
    "uri": pl.String,
    "detail": pl.String,
}
_SOURCE_LINEAGE_HTML_COLUMNS = (
    "asset",
    "section",
    "source system",
    "source table",
    "coverage state",
    "rows loaded",
    "source fields",
    "lineage fields",
    "lineage examples",
    "concept cards",
    "dashboard routes",
    "Market context paths",
    "table explorer",
    "asset metadata",
    "detail",
)
_SOURCE_LINEAGE_KPI_SCHEMA = {
    "metric": pl.String,
    "value": pl.String,
    "detail": pl.String,
}


@dataclass(frozen=True)
class _TableExplorerContext:
    table_explorer_link: str
    asset_metadata_link: str
    uri: str


@dataclass(frozen=True)
class _RegistryLineageLinks:
    concept_cards: tuple[str, ...]
    dashboard_routes: tuple[str, ...]
    market_context_paths: tuple[str, ...]
    source_chunk_ids: tuple[str, ...]


@dataclass
class _LineageAggregate:
    source_system: str
    source_table: str
    coverage_state: str
    detail: str
    rows_loaded: int = 0
    examples_by_field: dict[str, list[str]] = field(default_factory=dict)


def source_lineage_frame(
    loads: Sequence[GasTableLoad],
    table_catalogue: Sequence[object] = (),
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> pl.DataFrame:
    """Return source lineage rows enriched with registry navigation metadata."""
    context_by_table_name = _table_explorer_context_by_table_name(table_catalogue)
    candidate_entries = tuple(dashboard_registry() if entries is None else entries)
    rows: list[dict[str, object]] = []

    for load in loads:
        asset = f"{SILVER_GAS_MODEL_ASSET_PREFIX}{load.spec.table_name}"
        rows.extend(
            _source_lineage_rows(
                load,
                context_by_table_name.get(load.spec.table_name),
                _registry_links_for_asset(asset, candidate_entries),
            )
        )

    if rows:
        return pl.DataFrame(rows, schema=_SOURCE_LINEAGE_SCHEMA)
    return pl.DataFrame(schema=_SOURCE_LINEAGE_SCHEMA)


def source_lineage_kpi_frame(
    loads: Sequence[GasTableLoad],
    lineage: pl.DataFrame,
) -> pl.DataFrame:
    """Return first-viewport KPIs for the source table lineage explorer."""
    loaded_assets = sum(load.available for load in loads)
    explicit_gaps = _lineage_distinct_count(
        lineage,
        "asset",
        coverage_state=SOURCE_COVERAGE_STATE_GAP,
    )
    source_systems = _lineage_distinct_count(
        lineage,
        "source system",
        coverage_state=SOURCE_COVERAGE_STATE_COVERED,
        exclude_labels=True,
    )
    source_tables = _lineage_distinct_count(
        lineage,
        "source table",
        coverage_state=SOURCE_COVERAGE_STATE_COVERED,
        exclude_labels=True,
    )
    mapped_assets = _lineage_distinct_count(
        lineage.filter(pl.col("concept cards") != _SOURCE_LINEAGE_NO_CONCEPT_CARD)
        if not lineage.is_empty()
        else lineage,
        "asset",
    )
    lineage_field_groups = _lineage_distinct_count(
        lineage.filter(pl.col("lineage fields") != _SOURCE_LINEAGE_NO_EXTRA_FIELDS)
        if not lineage.is_empty()
        else lineage,
        "lineage fields",
    )

    return pl.DataFrame(
        [
            {
                "metric": "Requested assets",
                "value": f"{len(loads):,}",
                "detail": "Unique silver.gas_model table reads requested",
            },
            {
                "metric": "Loaded assets",
                "value": f"{loaded_assets:,}",
                "detail": "Tables with at least one loaded bounded row",
            },
            {
                "metric": "Source systems",
                "value": f"{source_systems:,}",
                "detail": "Distinct populated source_system/source_systems values",
            },
            {
                "metric": "Source tables",
                "value": f"{source_tables:,}",
                "detail": "Distinct populated source_table/source_tables values",
            },
            {
                "metric": "Registry mapped assets",
                "value": f"{mapped_assets:,}",
                "detail": "Assets with concept-card or Market context mappings",
            },
            {
                "metric": "Lineage field groups",
                "value": f"{lineage_field_groups:,}",
                "detail": "Distinct extra source lineage field sets found",
            },
            {
                "metric": "Assets with explicit gaps",
                "value": f"{explicit_gaps:,}",
                "detail": "Assets with missing source-system or source-table metadata",
            },
        ],
        schema=_SOURCE_LINEAGE_KPI_SCHEMA,
    )


def source_lineage_empty_state_markdown(loads: Sequence[GasTableLoad]) -> str:
    """Return empty-state copy for the source table lineage explorer."""
    if len(loads) == 0:
        return """
        **No source lineage tables were requested.**

        The explorer expected discovered or registry-backed `silver.gas_model`
        assets but received no table specs. Check the Marimo dashboard registry
        and table catalogue discovery.
        """

    failed_count = sum(load.error is not None for load in loads)
    empty_count = sum(
        load.error is None and (load.dataframe is None or load.dataframe.is_empty())
        for load in loads
    )
    return f"""
    **No source lineage rows are available.**

    The explorer checked `{len(loads)}` `silver.gas_model` assets.
    `{failed_count}` reads were unavailable and `{empty_count}` reads returned
    no rows.

    Materialize or seed the curated gas model outputs, then use
    **Refresh data**.
    """


def render_source_lineage_explorer_html(
    lineage: pl.DataFrame,
    *,
    max_rows: int = 200,
) -> str:
    """Return source lineage rows as a self-contained HTML table."""
    row_limit = max(1, max_rows)
    visible_rows = lineage.head(row_limit).to_dicts()
    hidden_rows = max(0, lineage.height - len(visible_rows))
    body_html = "\n".join(_render_source_lineage_row(row) for row in visible_rows)
    if body_html == "":
        body_html = (
            f'<tr><td colspan="{len(_SOURCE_LINEAGE_HTML_COLUMNS)}" '
            'class="source-lineage-explorer__empty">'
            "No source lineage rows match the current filters."
            "</td></tr>"
        )

    overflow_note = ""
    if hidden_rows > 0:
        overflow_note = (
            '<p class="source-lineage-explorer__overflow">'
            f"{hidden_rows:,} additional rows are hidden by the dashboard "
            "display limit. Narrow the filters to inspect them."
            "</p>"
        )

    return f"""\
<style>
{_source_lineage_css()}
</style>
<div
    class="source-lineage-explorer"
    data-row-count="{lineage.height}"
    data-rendered-row-count="{len(visible_rows)}"
>
    <div class="source-lineage-explorer__scroller">
        <table>
            <thead>
                <tr>
                    {_render_source_lineage_headings()}
                </tr>
            </thead>
            <tbody>
                {body_html}
            </tbody>
        </table>
    </div>
    {overflow_note}
</div>"""


def _source_lineage_rows(
    load: GasTableLoad,
    context: _TableExplorerContext | None,
    registry_links: _RegistryLineageLinks,
) -> list[dict[str, object]]:
    dataframe = load.dataframe
    if load.error is not None:
        return [
            _source_lineage_row(
                load,
                context,
                registry_links,
                source_system="",
                source_table="",
                coverage_state=SOURCE_COVERAGE_STATE_UNAVAILABLE,
                rows_loaded=0,
                source_fields="",
                lineage_fields=_SOURCE_LINEAGE_NO_EXTRA_FIELDS,
                lineage_examples=_SOURCE_LINEAGE_NO_POPULATED_VALUES,
                detail=f"Read detail: {load.error}",
            )
        ]

    if dataframe is None or dataframe.is_empty():
        return [
            _source_lineage_row(
                load,
                context,
                registry_links,
                source_system="",
                source_table="",
                coverage_state=SOURCE_COVERAGE_STATE_EMPTY,
                rows_loaded=0,
                source_fields="",
                lineage_fields=_SOURCE_LINEAGE_NO_EXTRA_FIELDS,
                lineage_examples=_SOURCE_LINEAGE_NO_POPULATED_VALUES,
                detail="The table read succeeded but returned no rows.",
            )
        ]

    source_fields = _source_lineage_field_label(dataframe)
    lineage_fields = _source_lineage_metadata_columns(dataframe)
    aggregate_rows = _source_lineage_aggregates(dataframe, lineage_fields)
    return [
        _source_lineage_row(
            load,
            context,
            registry_links,
            source_system=aggregate.source_system,
            source_table=aggregate.source_table,
            coverage_state=aggregate.coverage_state,
            rows_loaded=aggregate.rows_loaded,
            source_fields=source_fields,
            lineage_fields=_source_lineage_fields_label(lineage_fields),
            lineage_examples=_source_lineage_examples_label(
                aggregate.examples_by_field,
                lineage_fields,
            ),
            detail=aggregate.detail,
        )
        for aggregate in aggregate_rows
    ]


def _source_lineage_aggregates(
    dataframe: pl.DataFrame,
    lineage_fields: Sequence[str],
) -> tuple[_LineageAggregate, ...]:
    system_columns = _present_columns(dataframe, _SOURCE_LINEAGE_SYSTEM_COLUMNS)
    table_columns = _present_columns(dataframe, _SOURCE_LINEAGE_TABLE_COLUMNS)
    aggregates: dict[tuple[str, str, str, str], _LineageAggregate] = {}

    for row in dataframe.to_dicts():
        source_systems = _source_lineage_values_from_columns(
            row,
            system_columns,
            missing_label=_SOURCE_LINEAGE_MISSING_SOURCE_SYSTEM_COLUMN,
            empty_label=_SOURCE_LINEAGE_EMPTY_SOURCE_SYSTEM_VALUE,
        )
        source_tables = _source_lineage_values_from_columns(
            row,
            table_columns,
            missing_label=_SOURCE_LINEAGE_MISSING_SOURCE_TABLE_COLUMN,
            empty_label=_SOURCE_LINEAGE_EMPTY_SOURCE_TABLE_VALUE,
        )

        for source_system in source_systems:
            for source_table in source_tables:
                coverage_state = _source_lineage_state(source_system, source_table)
                detail = _source_lineage_detail(source_system, source_table)
                key = (source_system, source_table, coverage_state, detail)
                aggregate = aggregates.setdefault(
                    key,
                    _LineageAggregate(
                        source_system=source_system,
                        source_table=source_table,
                        coverage_state=coverage_state,
                        detail=detail,
                    ),
                )
                aggregate.rows_loaded += 1
                _add_lineage_examples(aggregate, row, lineage_fields)

    return tuple(
        sorted(
            aggregates.values(),
            key=lambda aggregate: (
                0 if aggregate.coverage_state == SOURCE_COVERAGE_STATE_COVERED else 1,
                -aggregate.rows_loaded,
                aggregate.source_system,
                aggregate.source_table,
            ),
        )
    )


def _source_lineage_row(
    load: GasTableLoad,
    context: _TableExplorerContext | None,
    registry_links: _RegistryLineageLinks,
    *,
    source_system: str,
    source_table: str,
    coverage_state: str,
    rows_loaded: int,
    source_fields: str,
    lineage_fields: str,
    lineage_examples: str,
    detail: str,
) -> dict[str, object]:
    return {
        "asset": f"{SILVER_GAS_MODEL_ASSET_PREFIX}{load.spec.table_name}",
        "section": load.spec.section,
        "table": load.spec.table_name,
        "source system": source_system,
        "source table": source_table,
        "coverage state": coverage_state,
        "rows loaded": rows_loaded,
        "row limit": format_row_limit(load.row_limit),
        "source fields": source_fields,
        "lineage fields": lineage_fields,
        "lineage examples": lineage_examples,
        "concept cards": _join_or_gap(
            registry_links.concept_cards,
            _SOURCE_LINEAGE_NO_CONCEPT_CARD,
        ),
        "dashboard routes": _join_or_gap(
            registry_links.dashboard_routes,
            _SOURCE_LINEAGE_NO_DASHBOARD_ROUTE,
        ),
        "Market context paths": _join_or_gap(
            registry_links.market_context_paths,
            _SOURCE_LINEAGE_NO_MARKET_CONTEXT_PATH,
        ),
        "source chunk ids": _join_or_gap(
            registry_links.source_chunk_ids,
            _SOURCE_LINEAGE_NO_SOURCE_CHUNKS,
        ),
        "table explorer": _table_explorer_link(load, context),
        "asset metadata": "" if context is None else context.asset_metadata_link,
        "uri": load.uri if context is None or context.uri == "" else context.uri,
        "detail": detail,
    }


def _source_lineage_field_label(dataframe: pl.DataFrame) -> str:
    fields = [column for column in dataframe.columns if column.startswith("source_")]
    if fields:
        return ", ".join(fields)
    return "(none)"


def _source_lineage_metadata_columns(dataframe: pl.DataFrame) -> tuple[str, ...]:
    return tuple(
        column
        for column in dataframe.columns
        if column.startswith("source_") and column not in _SOURCE_LINEAGE_CORE_COLUMNS
    )


def _source_lineage_fields_label(fields: Sequence[str]) -> str:
    if fields:
        return ", ".join(fields)
    return _SOURCE_LINEAGE_NO_EXTRA_FIELDS


def _source_lineage_examples_label(
    examples_by_field: Mapping[str, Sequence[str]],
    fields: Sequence[str],
) -> str:
    if len(fields) == 0:
        return _SOURCE_LINEAGE_NO_POPULATED_VALUES

    examples = []
    for field_name in fields:
        values = examples_by_field.get(field_name, ())
        if len(values) == 0:
            continue
        examples.append(f"{field_name}: {', '.join(values)}")

    if examples:
        return "; ".join(examples)
    return _SOURCE_LINEAGE_NO_POPULATED_VALUES


def _source_lineage_values_from_columns(
    row: Mapping[str, object],
    columns: Sequence[str],
    *,
    missing_label: str,
    empty_label: str,
) -> tuple[str, ...]:
    if len(columns) == 0:
        return (missing_label,)

    values: list[str] = []
    for column in columns:
        values.extend(_source_lineage_value_strings(row.get(column)))

    unique_values = tuple(dict.fromkeys(values))
    if unique_values:
        return unique_values
    return (empty_label,)


def _source_lineage_value_strings(value: object | None) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, float) and isnan(value):
        return ()
    if isinstance(value, str):
        stripped = value.strip()
        return (stripped,) if stripped else ()
    if isinstance(value, Sequence) and not isinstance(value, bytes):
        values: list[str] = []
        for item in value:
            values.extend(_source_lineage_value_strings(item))
        return tuple(dict.fromkeys(values))

    text = str(value).strip()
    return (text,) if text else ()


def _source_lineage_state(source_system: str, source_table: str) -> str:
    if source_system in {
        _SOURCE_LINEAGE_MISSING_SOURCE_SYSTEM_COLUMN,
        _SOURCE_LINEAGE_EMPTY_SOURCE_SYSTEM_VALUE,
    }:
        return SOURCE_COVERAGE_STATE_GAP
    if source_table in {
        _SOURCE_LINEAGE_MISSING_SOURCE_TABLE_COLUMN,
        _SOURCE_LINEAGE_EMPTY_SOURCE_TABLE_VALUE,
    }:
        return SOURCE_COVERAGE_STATE_GAP
    return SOURCE_COVERAGE_STATE_COVERED


def _source_lineage_detail(source_system: str, source_table: str) -> str:
    gap_details: list[str] = []
    if source_system == _SOURCE_LINEAGE_MISSING_SOURCE_SYSTEM_COLUMN:
        gap_details.append(
            "Missing source_system/source_systems columns; cannot identify "
            "source systems for these loaded rows."
        )
    elif source_system == _SOURCE_LINEAGE_EMPTY_SOURCE_SYSTEM_VALUE:
        gap_details.append(
            "source_system/source_systems columns are present but empty for "
            "these loaded rows."
        )

    if source_table == _SOURCE_LINEAGE_MISSING_SOURCE_TABLE_COLUMN:
        gap_details.append(
            "Missing source_table/source_tables columns; cannot identify source "
            "tables for these loaded rows."
        )
    elif source_table == _SOURCE_LINEAGE_EMPTY_SOURCE_TABLE_VALUE:
        gap_details.append(
            "source_table/source_tables columns are present but empty for these "
            "loaded rows."
        )

    if gap_details:
        return " ".join(gap_details)
    return "Source system and source table metadata are populated in loaded rows."


def _add_lineage_examples(
    aggregate: _LineageAggregate,
    row: Mapping[str, object],
    lineage_fields: Sequence[str],
) -> None:
    for field_name in lineage_fields:
        values = _source_lineage_value_strings(row.get(field_name))
        if len(values) == 0:
            continue
        field_examples = aggregate.examples_by_field.setdefault(field_name, [])
        for value in values:
            if value in field_examples:
                continue
            if len(field_examples) >= DEFAULT_SOURCE_LINEAGE_EXAMPLE_LIMIT:
                break
            field_examples.append(value)


def _registry_links_for_asset(
    asset: str,
    entries: Sequence[DashboardRegistryEntry],
) -> _RegistryLineageLinks:
    matched_entries = tuple(entry for entry in entries if asset in entry.backing_assets)
    return _RegistryLineageLinks(
        concept_cards=tuple(
            f"{entry.title} -> {SOURCE_LINEAGE_CONCEPT_GALLERY_ROUTE}"
            f"#concept-{entry.concept_id}"
            for entry in matched_entries
        ),
        dashboard_routes=tuple(
            f"{entry.title} -> {entry.notebook_route}"
            for entry in matched_entries
            if entry.notebook_route is not None
        ),
        market_context_paths=_unique_values(
            path for entry in matched_entries for path in entry.generated_gold_paths
        ),
        source_chunk_ids=_unique_values(
            chunk_id for entry in matched_entries for chunk_id in entry.source_chunk_ids
        ),
    )


def _table_explorer_context_by_table_name(
    table_catalogue: Sequence[object],
) -> dict[str, _TableExplorerContext]:
    contexts: dict[str, _TableExplorerContext] = {}
    for entry in table_catalogue:
        table_name = _table_name_from_catalogue_entry(entry)
        if table_name is None or table_name in contexts:
            continue
        contexts[table_name] = _table_explorer_context_from_entry(entry)
    return contexts


def _table_explorer_context_from_entry(entry: object) -> _TableExplorerContext:
    entry_id = _catalogue_entry_id(entry)
    has_asset = getattr(entry, "asset", None) is not None
    uri = getattr(entry, "uri", None)
    uri_text = uri if isinstance(uri, str) else ""

    if entry_id == "":
        table_link = SOURCE_LINEAGE_TABLE_EXPLORER_ROUTE
        asset_link = ""
    else:
        encoded_entry_id = quote(entry_id, safe="")
        table_link = f"{SOURCE_LINEAGE_TABLE_EXPLORER_ROUTE}?table={encoded_entry_id}"
        asset_link = (
            f"{SOURCE_LINEAGE_TABLE_EXPLORER_ROUTE}?asset={encoded_entry_id}"
            if has_asset
            else ""
        )

    return _TableExplorerContext(
        table_explorer_link=table_link,
        asset_metadata_link=asset_link,
        uri=uri_text,
    )


def _table_name_from_catalogue_entry(entry: object) -> str | None:
    for reference in _catalogue_references(entry):
        table_name = _table_name_from_reference(reference)
        if table_name is not None:
            return table_name
    return None


def _catalogue_references(entry: object) -> tuple[str, ...]:
    references: list[str] = []
    asset = getattr(entry, "asset", None)
    if asset is not None:
        _append_catalogue_reference(references, asset, "asset_id")
        _append_catalogue_reference(references, asset, "uri")

    table = getattr(entry, "table", None)
    if table is not None:
        _append_catalogue_reference(references, table, "prefix")
        _append_catalogue_reference(references, table, "uri")

    _append_catalogue_reference(references, entry, "uri")
    return tuple(references)


def _append_catalogue_reference(
    references: list[str],
    source: object,
    attribute: str,
) -> None:
    value = getattr(source, attribute, "")
    if isinstance(value, str):
        references.append(value)


def _table_name_from_reference(reference: str) -> str | None:
    if reference.startswith(SILVER_GAS_MODEL_ASSET_PREFIX):
        return reference.removeprefix(SILVER_GAS_MODEL_ASSET_PREFIX).split(
            ".",
            maxsplit=1,
        )[0]

    path_marker = "silver/gas_model/"
    if path_marker not in reference:
        return None

    suffix = reference.split(path_marker, maxsplit=1)[1].strip("/")
    if suffix == "":
        return None
    return suffix.split("/", maxsplit=1)[0]


def _catalogue_entry_id(entry: object) -> str:
    entry_id = getattr(entry, "entry_id", "")
    return entry_id if isinstance(entry_id, str) else ""


def _table_explorer_link(
    load: GasTableLoad,
    context: _TableExplorerContext | None,
) -> str:
    if context is not None and context.table_explorer_link != "":
        return context.table_explorer_link
    table_name = quote(load.spec.table_name, safe="")
    return f"{SOURCE_LINEAGE_TABLE_EXPLORER_ROUTE}?search={table_name}"


def _present_columns(
    dataframe: pl.DataFrame, candidates: Sequence[str]
) -> tuple[str, ...]:
    return tuple(column for column in candidates if column in dataframe.columns)


def _lineage_distinct_count(
    lineage: pl.DataFrame,
    column: str,
    *,
    coverage_state: str | None = None,
    exclude_labels: bool = False,
) -> int:
    if lineage.is_empty() or column not in lineage.columns:
        return 0

    filtered = lineage
    if coverage_state is not None:
        filtered = filtered.filter(pl.col("coverage state") == coverage_state)
    if filtered.is_empty():
        return 0

    values = (
        filtered.get_column(column)
        .drop_nulls()
        .cast(pl.String, strict=False)
        .unique()
        .to_list()
    )
    if exclude_labels:
        values = [value for value in values if not _is_gap_label(value)]
    return len([value for value in values if value.strip()])


def _is_gap_label(value: str) -> bool:
    return value.startswith("(") and value.endswith(")")


def _unique_values(values: Iterable[str]) -> tuple[str, ...]:
    unique: dict[str, None] = {}
    for value in values:
        stripped = value.strip()
        if stripped:
            unique.setdefault(stripped, None)
    return tuple(unique)


def _join_or_gap(values: Sequence[str], gap: str) -> str:
    if len(values) == 0:
        return gap
    return "\n".join(values)


def _render_source_lineage_headings() -> str:
    return "\n".join(
        f'<th scope="col">{escape(column)}</th>'
        for column in _SOURCE_LINEAGE_HTML_COLUMNS
    )


def _render_source_lineage_row(row: Mapping[str, object]) -> str:
    cells = "\n".join(
        _render_source_lineage_cell(row, column)
        for column in _SOURCE_LINEAGE_HTML_COLUMNS
    )
    coverage_state = _source_lineage_text(row.get("coverage state"))
    return f"""\
<tr data-coverage-state="{escape(coverage_state, quote=True)}">
    {cells}
</tr>"""


def _render_source_lineage_cell(row: Mapping[str, object], column: str) -> str:
    if column == "concept cards":
        return _render_link_list_cell(row.get(column), target="concept-card")
    if column == "dashboard routes":
        return _render_link_list_cell(row.get(column), target="dashboard-route")
    if column == "table explorer":
        return _render_route_cell(
            row.get(column),
            label="Open table",
            target="table-explorer",
            asset=row.get("asset"),
        )
    if column == "asset metadata":
        return _render_route_cell(
            row.get(column),
            label="Open asset",
            target="asset-metadata",
            asset=row.get("asset"),
        )
    if column == "Market context paths":
        return _render_market_context_cell(row.get(column))

    text = _source_lineage_text(row.get(column))
    return f"<td>{escape(text)}</td>"


def _render_link_list_cell(value: object, *, target: str) -> str:
    links = _route_link_items(value)
    if len(links) == 0:
        text = _source_lineage_text(value)
        if " -> " in text:
            text = "Unavailable"
        return f'<td class="source-lineage-explorer__muted">{escape(text)}</td>'

    rendered_links = "\n".join(
        (
            '<a class="source-lineage-explorer__link" '
            f'data-link-target="{escape(target, quote=True)}" '
            f'href="{escape(href, quote=True)}">'
            f"{escape(label)}</a>"
        )
        for label, href in links
    )
    return f'<td class="source-lineage-explorer__link-list">{rendered_links}</td>'


def _render_route_cell(
    value: object,
    *,
    label: str,
    target: str,
    asset: object,
) -> str:
    href = _route_href(value)
    if href == "":
        return '<td class="source-lineage-explorer__muted">Unavailable</td>'

    asset_label = _source_lineage_text(asset)
    aria_label = f"{label} for {asset_label}"
    return (
        '<td class="source-lineage-explorer__link-list">'
        '<a class="source-lineage-explorer__link" '
        f'data-link-target="{escape(target, quote=True)}" '
        f'href="{escape(href, quote=True)}" '
        f'aria-label="{escape(aria_label, quote=True)}">'
        f"{escape(label)}</a></td>"
    )


def _render_market_context_cell(value: object) -> str:
    paths = _plain_list_items(value)
    if len(paths) == 0:
        text = _source_lineage_text(value)
        return f'<td class="source-lineage-explorer__muted">{escape(text)}</td>'

    rendered_paths = "\n".join(
        (
            '<code class="source-lineage-explorer__path" '
            f'data-market-context-path="{escape(path, quote=True)}">'
            f"{escape(path)}</code>"
        )
        for path in paths
    )
    return f"<td>{rendered_paths}</td>"


def _route_link_items(value: object) -> tuple[tuple[str, str], ...]:
    items: list[tuple[str, str]] = []
    for item in _plain_list_items(value):
        if " -> " in item:
            label, href = item.rsplit(" -> ", maxsplit=1)
        else:
            label = item
            href = item
        safe_href = _route_href(href)
        if safe_href != "":
            items.append((label, safe_href))
    return tuple(items)


def _plain_list_items(value: object) -> tuple[str, ...]:
    if not isinstance(value, str):
        return ()
    return tuple(item.strip() for item in value.splitlines() if item.strip())


def _route_href(value: object | None) -> str:
    if not isinstance(value, str):
        return ""

    href = value.strip()
    if href.startswith("/marimo"):
        return href
    return ""


def _source_lineage_text(value: object | None) -> str:
    if value is None:
        return ""
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value:,}"
    return str(value)


def _source_lineage_css() -> str:
    return """\
.source-lineage-explorer {
    border: 1px solid var(--emdl-line);
    border-radius: 8px;
    background: var(--emdl-panel);
    overflow: hidden;
}

.source-lineage-explorer__scroller {
    overflow-x: auto;
}

.source-lineage-explorer table {
    width: 100%;
    min-width: 98rem;
    border-collapse: collapse;
    font-size: 0.88rem;
}

.source-lineage-explorer th,
.source-lineage-explorer td {
    border-bottom: 1px solid var(--emdl-line);
    padding: 0.55rem 0.65rem;
    text-align: left;
    vertical-align: top;
}

.source-lineage-explorer th {
    color: var(--emdl-muted);
    font-size: 0.76rem;
    font-weight: 700;
    text-transform: uppercase;
}

.source-lineage-explorer td {
    color: var(--emdl-ink);
    max-width: 22rem;
    overflow-wrap: anywhere;
}

.source-lineage-explorer tbody tr:last-child td {
    border-bottom: 0;
}

.source-lineage-explorer__link-list {
    display: grid;
    gap: 0.3rem;
}

.source-lineage-explorer__link {
    color: var(--emdl-blue);
    font-weight: 700;
    text-decoration: none;
}

.source-lineage-explorer__link:hover {
    text-decoration: underline;
}

.source-lineage-explorer__path {
    display: block;
    white-space: normal;
}

.source-lineage-explorer__muted,
.source-lineage-explorer__overflow,
.source-lineage-explorer__empty {
    color: var(--emdl-muted);
}

.source-lineage-explorer__overflow {
    margin: 0;
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--emdl-line);
    font-size: 0.85rem;
}
"""
