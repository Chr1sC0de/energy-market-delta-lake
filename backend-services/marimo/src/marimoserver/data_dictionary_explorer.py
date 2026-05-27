"""Schema and data dictionary helpers for mapped gas_model assets."""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from enum import StrEnum
from html import escape

import polars as pl

from marimoserver.concept_asset_explorer import (
    ConceptAssetExplorer,
    ConceptAssetLink,
    ConceptAssetMapping,
    ConceptDashboardLink,
    build_concept_asset_explorer,
    table_name_from_asset_id,
)
from marimoserver.dagster_graphql import (
    DagsterAssetCatalogue,
    DagsterColumnMetadata,
    DagsterTableAsset,
)

DATA_DICTIONARY_EXPLORER_CONCEPT_ID = "schema-data-dictionary-explorer"
SILVER_GAS_MODEL_DAGSTER_PREFIX = ("silver", "gas_model")

SHARED_DIMENSION_TABLES = frozenset(
    {
        "silver_gas_dim_date",
        "silver_gas_dim_participant",
        "silver_gas_participant_market_membership",
        "silver_gas_dim_facility",
        "silver_gas_dim_location",
        "silver_gas_dim_connection_point",
        "silver_gas_dim_zone",
        "silver_gas_dim_pipeline_segment",
        "silver_gas_dim_operational_point",
    }
)
OPERATIONS_MART_TABLES = frozenset(
    {
        "silver_gas_fact_connection_point_flow",
        "silver_gas_fact_facility_flow_storage",
        "silver_gas_fact_nomination_forecast",
        "silver_gas_fact_linepack",
        "silver_gas_fact_operational_meter_flow",
    }
)
MARKET_MART_TABLES = frozenset(
    {
        "silver_gas_fact_market_price",
        "silver_gas_fact_schedule_run",
        "silver_gas_fact_scheduled_quantity",
        "silver_gas_fact_bid_stack",
        "silver_gas_fact_sttm_contingency_gas_call",
    }
)
CAPACITY_SETTLEMENT_MART_TABLES = frozenset(
    {
        "silver_gas_fact_capacity_outlook",
        "silver_gas_fact_capacity_transaction",
        "silver_gas_fact_capacity_auction",
        "silver_gas_fact_settlement_activity",
        "silver_gas_fact_customer_transfer",
        "silver_gas_fact_sttm_allocation_quantity",
        "silver_gas_fact_sttm_market_settlement",
        "silver_gas_fact_sttm_capacity_settlement",
        "silver_gas_fact_sttm_mos_stack",
        "silver_gas_fact_sttm_default_allocation_notice",
        "silver_gas_fact_sttm_allocation_limit",
        "silver_gas_fact_sttm_market_parameter",
    }
)
QUALITY_STATUS_MART_TABLES = frozenset(
    {
        "silver_gas_fact_heating_value",
        "silver_gas_fact_gas_quality",
        "silver_gas_fact_scada_pressure",
        "silver_gas_fact_linepack_balance",
        "silver_gas_fact_system_notice",
    }
)


class DataDictionarySchemaState(StrEnum):
    """Schema metadata state for one mapped data dictionary asset."""

    AVAILABLE = "Schema metadata available"
    MISSING_SCHEMA = "Missing schema metadata"
    MISSING_ASSET = "Missing asset metadata"
    GRAPHQL_UNAVAILABLE = "GraphQL unavailable"
    NO_MAPPED_ASSET = "No mapped asset"


@dataclass(frozen=True)
class DataDictionaryAsset:
    """One mapped asset and its schema metadata state."""

    concept_id: str
    concept_title: str
    asset_id: str
    table_name: str | None
    mart: str
    dashboard_links: tuple[ConceptDashboardLink, ...]
    table_explorer_route: str | None
    schema_state: DataDictionarySchemaState
    schema_source: str
    schema_detail: str
    asset_description: str | None
    columns: tuple[DagsterColumnMetadata, ...]

    @property
    def column_count(self) -> int:
        """Return parsed column count for this asset."""
        return len(self.columns)

    @property
    def dashboard_route_label(self) -> str:
        """Return a compact dashboard route label for tables and filters."""
        if len(self.dashboard_links) == 0:
            return "No dashboard route"
        return "; ".join(
            f"{link.title}: {link.navigation_route}" for link in self.dashboard_links
        )


@dataclass(frozen=True)
class DataDictionaryConcept:
    """One concept group in the schema data dictionary."""

    concept_id: str
    title: str
    description: str
    market_context_id: str | None
    assets: tuple[DataDictionaryAsset, ...]
    metadata_gaps: tuple[str, ...]


@dataclass(frozen=True)
class DataDictionaryExplorer:
    """Complete schema data dictionary view model."""

    url: str
    graphql_available: bool
    graphql_error: str | None
    concepts: tuple[DataDictionaryConcept, ...]
    source_label: str = "Dagster GraphQL and Marimo dashboard registry"
    freshness_label: str = "Latest notebook refresh"
    scope_label: str = "Mapped silver.gas_model assets"

    @property
    def assets(self) -> tuple[DataDictionaryAsset, ...]:
        """Return flattened concept-asset rows."""
        return tuple(asset for concept in self.concepts for asset in concept.assets)

    @property
    def mapped_asset_count(self) -> int:
        """Return distinct mapped asset count."""
        return len({asset.asset_id for asset in self.assets})

    @property
    def schema_asset_count(self) -> int:
        """Return distinct assets with parsed column metadata."""
        return len(
            {
                asset.asset_id
                for asset in self.assets
                if asset.schema_state is DataDictionarySchemaState.AVAILABLE
            }
        )

    @property
    def missing_schema_asset_count(self) -> int:
        """Return distinct assets without usable schema metadata."""
        return len(
            {
                asset.asset_id
                for asset in self.assets
                if asset.schema_state is not DataDictionarySchemaState.AVAILABLE
            }
        )

    @property
    def field_count(self) -> int:
        """Return parsed field count across concept-asset rows."""
        return sum(asset.column_count for asset in self.assets)

    @property
    def dashboard_route_count(self) -> int:
        """Return distinct dashboard route count represented by mapped assets."""
        return len(
            {
                link.navigation_route
                for asset in self.assets
                for link in asset.dashboard_links
            }
        )


def build_data_dictionary_explorer(
    catalogue: DagsterAssetCatalogue,
    concept_explorer: ConceptAssetExplorer | None = None,
) -> DataDictionaryExplorer:
    """Build a schema data dictionary from GraphQL metadata and registry mapping."""
    mapped_explorer = (
        build_concept_asset_explorer() if concept_explorer is None else concept_explorer
    )
    assets_by_registry_id = _dagster_assets_by_registry_id(catalogue.assets)
    concepts = tuple(
        _data_dictionary_concept(
            mapping,
            catalogue=catalogue,
            assets_by_registry_id=assets_by_registry_id,
        )
        for mapping in mapped_explorer.concept_mappings
    )
    return DataDictionaryExplorer(
        url=catalogue.url,
        graphql_available=catalogue.available,
        graphql_error=catalogue.error,
        concepts=concepts,
    )


def filter_data_dictionary_explorer(
    explorer: DataDictionaryExplorer,
    *,
    concept_ids: Sequence[str] = (),
    marts: Sequence[str] = (),
    schema_states: Sequence[str | DataDictionarySchemaState] = (),
    search: str = "",
) -> DataDictionaryExplorer:
    """Return a filtered data dictionary while preserving concept grouping."""
    concept_id_filter = set(concept_ids)
    mart_filter = set(marts)
    state_filter = {
        state.value if isinstance(state, DataDictionarySchemaState) else state
        for state in schema_states
    }
    search_term = search.strip().casefold()

    concepts: list[DataDictionaryConcept] = []
    for concept in explorer.concepts:
        if concept_id_filter and concept.concept_id not in concept_id_filter:
            continue
        filtered_assets = tuple(
            asset
            for asset in concept.assets
            if _asset_matches_filters(
                asset,
                mart_filter=mart_filter,
                state_filter=state_filter,
                search_term=search_term,
            )
        )
        if filtered_assets:
            concepts.append(replace(concept, assets=filtered_assets))

    return replace(explorer, concepts=tuple(concepts))


def data_dictionary_asset_frame(
    explorer: DataDictionaryExplorer,
) -> pl.DataFrame:
    """Return one row per mapped concept asset."""
    rows = [
        {
            "concept": asset.concept_title,
            "concept id": asset.concept_id,
            "mart": asset.mart,
            "asset key": asset.asset_id,
            "table": asset.table_name or "",
            "schema state": asset.schema_state.value,
            "columns": asset.column_count,
            "schema source": asset.schema_source,
            "detail": asset.schema_detail,
            "dashboard routes": asset.dashboard_route_label,
            "table explorer route": asset.table_explorer_route or "",
            "asset description": asset.asset_description or "",
        }
        for asset in explorer.assets
    ]
    if rows:
        return pl.DataFrame(rows)
    return pl.DataFrame(
        [
            {
                "concept": "No mapped schema assets",
                "concept id": "",
                "mart": "",
                "asset key": "",
                "table": "",
                "schema state": DataDictionarySchemaState.NO_MAPPED_ASSET.value,
                "columns": 0,
                "schema source": "",
                "detail": "No mapped concept-to-asset rows match the current filters.",
                "dashboard routes": "",
                "table explorer route": "",
                "asset description": "",
            }
        ]
    )


def data_dictionary_field_frame(
    explorer: DataDictionaryExplorer,
) -> pl.DataFrame:
    """Return one row per parsed column, including explicit missing-schema rows."""
    rows: list[dict[str, object]] = []
    for concept in explorer.concepts:
        if len(concept.assets) == 0:
            rows.append(
                {
                    "concept": concept.title,
                    "concept id": concept.concept_id,
                    "mart": "",
                    "asset key": "No mapped silver.gas_model assets",
                    "table": "",
                    "dashboard routes": "",
                    "column": "",
                    "type": "",
                    "description": (
                        "No backing silver.gas_model assets are mapped to this concept."
                    ),
                    "schema state": DataDictionarySchemaState.NO_MAPPED_ASSET.value,
                    "schema source": "Marimo dashboard registry",
                    "detail": "; ".join(concept.metadata_gaps),
                }
            )
        for asset in concept.assets:
            rows.extend(_field_rows_for_asset(asset))

    if rows:
        return pl.DataFrame(rows)

    return pl.DataFrame(
        [
            {
                "concept": "No mapped schema fields",
                "concept id": "",
                "mart": "",
                "asset key": "",
                "table": "",
                "dashboard routes": "",
                "column": "",
                "type": "",
                "description": ("No data dictionary fields match the current filters."),
                "schema state": DataDictionarySchemaState.NO_MAPPED_ASSET.value,
                "schema source": "",
                "detail": "",
            }
        ]
    )


def data_dictionary_mart_frame(
    explorer: DataDictionaryExplorer,
) -> pl.DataFrame:
    """Return schema coverage grouped by gas-model mart."""
    rows: list[dict[str, object]] = []
    for mart in sorted({asset.mart for asset in explorer.assets}):
        mart_assets = tuple(asset for asset in explorer.assets if asset.mart == mart)
        distinct_asset_ids = {asset.asset_id for asset in mart_assets}
        schema_asset_ids = {
            asset.asset_id
            for asset in mart_assets
            if asset.schema_state is DataDictionarySchemaState.AVAILABLE
        }
        rows.append(
            {
                "mart": mart,
                "concept groups": len({asset.concept_id for asset in mart_assets}),
                "mapped assets": len(distinct_asset_ids),
                "assets with schema": len(schema_asset_ids),
                "missing schema assets": len(distinct_asset_ids - schema_asset_ids),
                "fields": sum(asset.column_count for asset in mart_assets),
                "dashboard routes": len(
                    {
                        link.navigation_route
                        for asset in mart_assets
                        for link in asset.dashboard_links
                    }
                ),
            }
        )

    if rows:
        return pl.DataFrame(rows)

    return pl.DataFrame(
        [
            {
                "mart": "No mapped marts",
                "concept groups": 0,
                "mapped assets": 0,
                "assets with schema": 0,
                "missing schema assets": 0,
                "fields": 0,
                "dashboard routes": 0,
            }
        ]
    )


def data_dictionary_action_markdown(explorer: DataDictionaryExplorer) -> str:
    """Return action guidance for data dictionary degraded states."""
    actions: list[str] = []
    if not explorer.graphql_available:
        actions.append(
            "Dagster GraphQL: confirm `DAGSTER_GRAPHQL_URL`, Dagster webserver "
            "health, and reverse-proxy path. Concept-to-asset grouping remains "
            "visible, but schema metadata is unavailable."
        )
    if explorer.missing_schema_asset_count > 0:
        actions.append(
            "Schema metadata: mapped assets without parsed column metadata are "
            "kept in the dictionary with an explicit missing-state row."
        )
    if explorer.mapped_asset_count == 0:
        actions.append(
            "Concept mapping: no mapped `silver.gas_model` assets are currently "
            "available for the selected filters."
        )

    if not actions:
        return (
            "Mapped `silver.gas_model` assets have usable schema metadata for "
            "the current data dictionary view."
        )
    return "\n".join(f"- {action}" for action in actions)


def render_data_dictionary_status_cards(explorer: DataDictionaryExplorer) -> str:
    """Render first-viewport data dictionary status cards."""
    graph_state = "Ready" if explorer.graphql_available else "GraphQL unavailable"
    schema_label = f"{explorer.schema_asset_count}/{explorer.mapped_asset_count}"
    cards = (
        _status_card(
            "Source",
            graph_state,
            explorer.url,
            "ready" if explorer.graphql_available else "warn",
        ),
        _status_card("Scope", explorer.scope_label, "Concept-to-asset mapped tables"),
        _status_card(
            "Schema coverage",
            schema_label,
            f"{explorer.missing_schema_asset_count} mapped assets need metadata",
            "ready" if explorer.missing_schema_asset_count == 0 else "warn",
        ),
        _status_card(
            "Fields",
            str(explorer.field_count),
            "Parsed column metadata rows",
        ),
        _status_card(
            "Concept groups",
            str(len(explorer.concepts)),
            f"{explorer.dashboard_route_count} dashboard routes represented",
        ),
    )
    return f"""\
<style>
{_data_dictionary_status_css()}
</style>
<section
    class="data-dictionary-status-grid"
    aria-label="Schema data dictionary health"
    data-mapped-asset-count="{explorer.mapped_asset_count}"
    data-schema-asset-count="{explorer.schema_asset_count}"
    data-field-count="{explorer.field_count}"
>
{"".join(cards)}
</section>"""


def gas_model_mart_for_table(table_name: str | None) -> str:
    """Return the documented gas-model mart for a table name."""
    if table_name is None or table_name == "":
        return "Unmapped mart"
    if table_name in SHARED_DIMENSION_TABLES:
        return "Shared dimensions"
    if table_name in OPERATIONS_MART_TABLES:
        return "Operations mart"
    if table_name in MARKET_MART_TABLES:
        return "Market mart"
    if table_name in CAPACITY_SETTLEMENT_MART_TABLES:
        return "Capacity and settlement mart"
    if table_name in QUALITY_STATUS_MART_TABLES:
        return "Quality and status mart"
    return "Unclassified mart"


def _data_dictionary_concept(
    mapping: ConceptAssetMapping,
    *,
    catalogue: DagsterAssetCatalogue,
    assets_by_registry_id: dict[str, DagsterTableAsset],
) -> DataDictionaryConcept:
    dashboard_links = mapping.available_dashboards + mapping.planned_dashboards
    assets = tuple(
        _data_dictionary_asset(
            asset_link,
            mapping=mapping,
            dashboard_links=dashboard_links,
            catalogue=catalogue,
            dagster_asset=assets_by_registry_id.get(asset_link.asset_id),
        )
        for asset_link in mapping.assets
    )
    return DataDictionaryConcept(
        concept_id=mapping.concept_id,
        title=mapping.title,
        description=mapping.description,
        market_context_id=mapping.market_context_id,
        assets=assets,
        metadata_gaps=mapping.metadata_gaps,
    )


def _data_dictionary_asset(
    asset_link: ConceptAssetLink,
    *,
    mapping: ConceptAssetMapping,
    dashboard_links: tuple[ConceptDashboardLink, ...],
    catalogue: DagsterAssetCatalogue,
    dagster_asset: DagsterTableAsset | None,
) -> DataDictionaryAsset:
    table_name = asset_link.table_name
    schema_state, schema_source, schema_detail = _schema_state(
        catalogue,
        dagster_asset,
        asset_link.asset_id,
    )
    return DataDictionaryAsset(
        concept_id=mapping.concept_id,
        concept_title=mapping.title,
        asset_id=asset_link.asset_id,
        table_name=table_name,
        mart=gas_model_mart_for_table(table_name),
        dashboard_links=dashboard_links,
        table_explorer_route=asset_link.table_explorer_route,
        schema_state=schema_state,
        schema_source=schema_source,
        schema_detail=schema_detail,
        asset_description=None if dagster_asset is None else dagster_asset.description,
        columns=() if dagster_asset is None else dagster_asset.columns,
    )


def _schema_state(
    catalogue: DagsterAssetCatalogue,
    dagster_asset: DagsterTableAsset | None,
    asset_id: str,
) -> tuple[DataDictionarySchemaState, str, str]:
    if not catalogue.available:
        return (
            DataDictionarySchemaState.GRAPHQL_UNAVAILABLE,
            "Dagster GraphQL",
            catalogue.error or "Dagster GraphQL is unavailable.",
        )
    if dagster_asset is None:
        return (
            DataDictionarySchemaState.MISSING_ASSET,
            "Dagster GraphQL table metadata",
            f"Dagster GraphQL returned no table asset metadata for `{asset_id}`.",
        )
    if dagster_asset.columns:
        return (
            DataDictionarySchemaState.AVAILABLE,
            "Dagster GraphQL table metadata",
            f"{len(dagster_asset.columns)} parsed columns.",
        )
    return (
        DataDictionarySchemaState.MISSING_SCHEMA,
        "Dagster GraphQL table metadata",
        "Dagster GraphQL returned the table asset but no parsed column schema metadata.",
    )


def _field_rows_for_asset(asset: DataDictionaryAsset) -> tuple[dict[str, object], ...]:
    if asset.columns:
        return tuple(_field_row(asset, column) for column in asset.columns)
    return (
        _field_row(
            asset,
            DagsterColumnMetadata(
                name="No schema metadata",
                dtype="",
                description=asset.schema_detail,
            ),
        ),
    )


def _field_row(
    asset: DataDictionaryAsset,
    column: DagsterColumnMetadata,
) -> dict[str, object]:
    return {
        "concept": asset.concept_title,
        "concept id": asset.concept_id,
        "mart": asset.mart,
        "asset key": asset.asset_id,
        "table": asset.table_name or "",
        "dashboard routes": asset.dashboard_route_label,
        "column": column.name,
        "type": column.dtype,
        "description": column.description or "",
        "schema state": asset.schema_state.value,
        "schema source": asset.schema_source,
        "detail": asset.schema_detail,
    }


def _asset_matches_filters(
    asset: DataDictionaryAsset,
    *,
    mart_filter: set[str],
    state_filter: set[str],
    search_term: str,
) -> bool:
    if mart_filter and asset.mart not in mart_filter:
        return False
    if state_filter and asset.schema_state.value not in state_filter:
        return False
    if search_term == "":
        return True
    searchable = " ".join(
        (
            asset.concept_title,
            asset.concept_id,
            asset.asset_id,
            asset.table_name or "",
            asset.mart,
            asset.dashboard_route_label,
            asset.schema_state.value,
            asset.schema_detail,
            " ".join(column.name for column in asset.columns),
            " ".join(column.description or "" for column in asset.columns),
        )
    ).casefold()
    return search_term in searchable


def _dagster_assets_by_registry_id(
    assets: Sequence[DagsterTableAsset],
) -> dict[str, DagsterTableAsset]:
    assets_by_id: dict[str, DagsterTableAsset] = {}
    for asset in assets:
        registry_asset_id = _registry_asset_id_from_dagster_asset(asset)
        if registry_asset_id is not None:
            assets_by_id[registry_asset_id] = asset
    return assets_by_id


def _registry_asset_id_from_dagster_asset(asset: DagsterTableAsset) -> str | None:
    if (
        asset.asset_key[:2] == SILVER_GAS_MODEL_DAGSTER_PREFIX
        and len(asset.asset_key) == 3
    ):
        return f"silver.gas_model.{asset.asset_key[2]}"
    dotted_asset_id = asset.asset_id.replace("/", ".")
    if table_name_from_asset_id(dotted_asset_id) is None:
        return None
    return dotted_asset_id


def _status_card(
    label: str,
    value: str,
    detail: str,
    state: str = "neutral",
) -> str:
    return f"""\
    <article class="data-dictionary-status data-dictionary-status--{escape(state, quote=True)}">
        <span>{escape(label)}</span>
        <strong>{escape(value)}</strong>
        <p>{escape(detail)}</p>
    </article>"""


def _data_dictionary_status_css() -> str:
    return """\
.data-dictionary-status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 12rem), 1fr));
    gap: 0.75rem;
    color: var(--emdl-ink, #1b2324);
}

.data-dictionary-status {
    display: grid;
    gap: 0.25rem;
    min-width: 0;
    padding: 0.85rem;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
    box-shadow: var(--emdl-soft-shadow, 0 8px 28px rgb(27 35 36 / 0.08));
}

.data-dictionary-status--warn {
    border-color: var(--emdl-amber, #b2682a);
}

.data-dictionary-status span {
    color: var(--emdl-green, #3e7a54);
    font-size: 0.74rem;
    font-weight: 720;
    letter-spacing: 0;
    text-transform: uppercase;
}

.data-dictionary-status strong {
    overflow-wrap: anywhere;
    color: var(--emdl-slate, #354348);
    font-size: 1.15rem;
    line-height: 1.15;
}

.data-dictionary-status p {
    margin: 0;
    overflow-wrap: anywhere;
    color: var(--emdl-muted, #566365);
    font-size: 0.86rem;
}
"""
