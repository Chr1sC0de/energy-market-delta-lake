"""Component tests for the schema data dictionary explorer helper."""

from marimoserver.concept_asset_explorer import build_concept_asset_explorer
from marimoserver.dashboard_registry import (
    DashboardAudience,
    DashboardRegistryEntry,
    DashboardStatus,
    SourceChunkReference,
)
from marimoserver.dagster_graphql import (
    DagsterAssetCatalogue,
    DagsterColumnMetadata,
    DagsterTableAsset,
)
from marimoserver.data_dictionary_explorer import (
    DataDictionaryAsset,
    DataDictionaryConcept,
    DataDictionaryExplorer,
    DataDictionarySchemaState,
    build_data_dictionary_explorer,
    data_dictionary_action_markdown,
    data_dictionary_asset_frame,
    data_dictionary_field_frame,
    data_dictionary_mart_frame,
    filter_data_dictionary_explorer,
    gas_model_mart_for_table,
    render_data_dictionary_status_cards,
)


def test_data_dictionary_groups_schema_metadata_by_concept_asset_and_route() -> None:
    entries = (
        _entry(
            concept_id="flow-context",
            title="Flow Context",
            status=DashboardStatus.AVAILABLE,
            notebook_name="flow_dashboard",
            backing_assets=("silver.gas_model.silver_gas_fact_connection_point_flow",),
            market_context_ids=("glossary:flow",),
        ),
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error=None,
        assets=(
            _asset(
                ("silver", "gas_model", "silver_gas_fact_connection_point_flow"),
                columns=(
                    DagsterColumnMetadata(
                        name="gas_date",
                        dtype="Date",
                        description="Gas day.",
                    ),
                    DagsterColumnMetadata(
                        name="actual_quantity_tj",
                        dtype="Float64",
                        description="Actual flow quantity.",
                    ),
                ),
            ),
        ),
    )

    explorer = build_data_dictionary_explorer(
        catalogue,
        build_concept_asset_explorer(entries),
    )
    asset_frame = data_dictionary_asset_frame(explorer)
    field_rows = data_dictionary_field_frame(explorer).to_dicts()
    mart_row = data_dictionary_mart_frame(explorer).row(0, named=True)
    html = render_data_dictionary_status_cards(explorer)

    assert explorer.graphql_available is True
    assert explorer.mapped_asset_count == 1
    assert explorer.schema_asset_count == 1
    assert explorer.field_count == 2
    assert explorer.dashboard_route_count == 1
    assert asset_frame.row(0, named=True)["dashboard routes"] == (
        "Flow Context: /marimo/flow_dashboard/"
    )
    assert field_rows == [
        {
            "concept": "Flow",
            "concept id": "flow-context",
            "mart": "Operations mart",
            "asset key": "silver.gas_model.silver_gas_fact_connection_point_flow",
            "table": "silver_gas_fact_connection_point_flow",
            "dashboard routes": "Flow Context: /marimo/flow_dashboard/",
            "column": "gas_date",
            "type": "Date",
            "description": "Gas day.",
            "schema state": "Schema metadata available",
            "schema source": "Dagster GraphQL table metadata",
            "detail": "2 parsed columns.",
        },
        {
            "concept": "Flow",
            "concept id": "flow-context",
            "mart": "Operations mart",
            "asset key": "silver.gas_model.silver_gas_fact_connection_point_flow",
            "table": "silver_gas_fact_connection_point_flow",
            "dashboard routes": "Flow Context: /marimo/flow_dashboard/",
            "column": "actual_quantity_tj",
            "type": "Float64",
            "description": "Actual flow quantity.",
            "schema state": "Schema metadata available",
            "schema source": "Dagster GraphQL table metadata",
            "detail": "2 parsed columns.",
        },
    ]
    assert mart_row["mart"] == "Operations mart"
    assert mart_row["mapped assets"] == 1
    assert mart_row["fields"] == 2
    assert 'data-mapped-asset-count="1"' in html
    assert 'data-schema-asset-count="1"' in html


def test_data_dictionary_renders_missing_schema_and_asset_metadata_explicitly() -> None:
    entries = (
        _entry(
            concept_id="capacity-context",
            title="Capacity Context",
            status=DashboardStatus.PLANNED,
            notebook_name=None,
            backing_assets=(
                "silver.gas_model.silver_gas_fact_capacity_outlook",
                "silver.gas_model.silver_gas_fact_capacity_transaction",
            ),
            market_context_ids=("glossary:capacity",),
        ),
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error=None,
        assets=(
            _asset(
                ("silver", "gas_model", "silver_gas_fact_capacity_outlook"),
                columns=(),
            ),
        ),
    )

    explorer = build_data_dictionary_explorer(
        catalogue,
        build_concept_asset_explorer(entries),
    )
    asset_rows = data_dictionary_asset_frame(explorer).to_dicts()
    field_rows = data_dictionary_field_frame(explorer).to_dicts()
    action_markdown = data_dictionary_action_markdown(explorer)

    assert [row["schema state"] for row in asset_rows] == [
        "Missing schema metadata",
        "Missing asset metadata",
    ]
    assert [row["column"] for row in field_rows] == [
        "No schema metadata",
        "No schema metadata",
    ]
    assert "no parsed column schema metadata" in field_rows[0]["detail"]
    assert "returned no table asset metadata" in field_rows[1]["detail"]
    assert "Schema metadata" in action_markdown


def test_data_dictionary_keeps_concept_grouping_when_graphql_unavailable() -> None:
    entries = (
        _entry(
            concept_id="schedule-context",
            title="Schedule Context",
            status=DashboardStatus.PLANNED,
            notebook_name=None,
            backing_assets=("silver.gas_model.silver_gas_fact_schedule_run",),
            market_context_ids=("glossary:schedule",),
        ),
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error="Connection refused",
        assets=(),
    )

    explorer = build_data_dictionary_explorer(
        catalogue,
        build_concept_asset_explorer(entries),
    )
    field_row = data_dictionary_field_frame(explorer).row(0, named=True)

    assert explorer.graphql_available is False
    assert explorer.missing_schema_asset_count == 1
    assert field_row["concept"] == "Schedule"
    assert field_row["mart"] == "Market mart"
    assert field_row["schema state"] == "GraphQL unavailable"
    assert field_row["detail"] == "Connection refused"
    assert "Concept-to-asset grouping remains visible" in (
        data_dictionary_action_markdown(explorer)
    )


def test_data_dictionary_filters_by_concept_mart_state_and_search() -> None:
    entries = (
        _entry(
            concept_id="flow-context",
            title="Flow Context",
            status=DashboardStatus.PLANNED,
            notebook_name=None,
            backing_assets=("silver.gas_model.silver_gas_fact_connection_point_flow",),
            market_context_ids=("glossary:flow",),
        ),
        _entry(
            concept_id="quality-context",
            title="Quality Context",
            status=DashboardStatus.PLANNED,
            notebook_name=None,
            backing_assets=("silver.gas_model.silver_gas_fact_gas_quality",),
            market_context_ids=("glossary:quality",),
        ),
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error=None,
        assets=(
            _asset(
                ("silver", "gas_model", "silver_gas_fact_connection_point_flow"),
                columns=(DagsterColumnMetadata("actual_quantity_tj", "Float64", ""),),
            ),
        ),
    )
    explorer = build_data_dictionary_explorer(
        catalogue,
        build_concept_asset_explorer(entries),
    )

    filtered = filter_data_dictionary_explorer(
        explorer,
        concept_ids=("flow-context",),
        marts=("Operations mart",),
        schema_states=(DataDictionarySchemaState.AVAILABLE,),
        search="actual_quantity",
    )

    assert [concept.concept_id for concept in filtered.concepts] == ["flow-context"]
    assert [asset.asset_id for asset in filtered.assets] == [
        "silver.gas_model.silver_gas_fact_connection_point_flow"
    ]
    assert gas_model_mart_for_table("silver_gas_dim_facility") == "Shared dimensions"
    assert gas_model_mart_for_table("silver_gas_fact_market_price") == "Market mart"
    assert (
        gas_model_mart_for_table("silver_gas_fact_capacity_outlook")
        == "Capacity and settlement mart"
    )
    assert (
        gas_model_mart_for_table("silver_gas_fact_gas_quality")
        == "Quality and status mart"
    )


def test_data_dictionary_empty_states_and_fallbacks_are_explicit() -> None:
    empty_explorer = DataDictionaryExplorer(
        url="http://dagster/graphql",
        graphql_available=True,
        graphql_error=None,
        concepts=(),
    )
    no_asset_explorer = DataDictionaryExplorer(
        url="http://dagster/graphql",
        graphql_available=True,
        graphql_error=None,
        concepts=(
            DataDictionaryConcept(
                concept_id="empty-context",
                title="Empty",
                description="No mapped assets.",
                market_context_id=None,
                assets=(),
                metadata_gaps=(
                    "No backing silver.gas_model assets are mapped to this concept.",
                ),
            ),
        ),
    )
    no_route_asset = DataDictionaryAsset(
        concept_id="fixture-context",
        concept_title="Fixture",
        asset_id="silver.gas_model.silver_gas_fact_market_price",
        table_name="silver_gas_fact_market_price",
        mart="Market mart",
        dashboard_links=(),
        table_explorer_route=None,
        schema_state=DataDictionarySchemaState.AVAILABLE,
        schema_source="Dagster GraphQL table metadata",
        schema_detail="1 parsed columns.",
        asset_description=None,
        columns=(DagsterColumnMetadata("price", "Float64", None),),
    )
    available_explorer = DataDictionaryExplorer(
        url="http://dagster/graphql",
        graphql_available=True,
        graphql_error=None,
        concepts=(
            DataDictionaryConcept(
                concept_id="fixture-context",
                title="Fixture",
                description="Fixture concept.",
                market_context_id=None,
                assets=(no_route_asset,),
                metadata_gaps=(),
            ),
        ),
    )

    assert (
        data_dictionary_asset_frame(empty_explorer).row(0, named=True)["schema state"]
        == "No mapped asset"
    )
    assert (
        data_dictionary_field_frame(empty_explorer).row(0, named=True)["concept"]
        == "No mapped schema fields"
    )
    assert data_dictionary_mart_frame(empty_explorer).row(0, named=True)["mart"] == (
        "No mapped marts"
    )
    assert "no mapped `silver.gas_model` assets" in data_dictionary_action_markdown(
        empty_explorer
    )
    assert (
        data_dictionary_field_frame(no_asset_explorer).row(0, named=True)["asset key"]
        == "No mapped silver.gas_model assets"
    )
    assert no_route_asset.dashboard_route_label == "No dashboard route"
    assert data_dictionary_action_markdown(available_explorer) == (
        "Mapped `silver.gas_model` assets have usable schema metadata for "
        "the current data dictionary view."
    )
    assert gas_model_mart_for_table(None) == "Unmapped mart"
    assert gas_model_mart_for_table("silver_gas_unknown_table") == ("Unclassified mart")
    assert (
        filter_data_dictionary_explorer(
            available_explorer,
            marts=("Operations mart",),
        ).assets
        == ()
    )
    assert (
        filter_data_dictionary_explorer(
            available_explorer,
            schema_states=("Missing schema metadata",),
        ).assets
        == ()
    )
    assert filter_data_dictionary_explorer(available_explorer, search="").assets == (
        no_route_asset,
    )


def test_data_dictionary_accepts_dotted_dagster_asset_id_fallbacks() -> None:
    entries = (
        _entry(
            concept_id="price-context",
            title="Price Context",
            status=DashboardStatus.PLANNED,
            notebook_name=None,
            backing_assets=("silver.gas_model.silver_gas_fact_market_price",),
            market_context_ids=("glossary:price",),
        ),
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        error=None,
        assets=(
            _asset(
                ("silver.gas_model.silver_gas_fact_market_price",),
                columns=(DagsterColumnMetadata("price", "Float64", None),),
            ),
            _asset(
                ("bronze", "raw", "ignored_table"),
                columns=(DagsterColumnMetadata("id", "String", None),),
            ),
        ),
    )

    explorer = build_data_dictionary_explorer(
        catalogue,
        build_concept_asset_explorer(entries),
    )

    assert explorer.schema_asset_count == 1
    assert data_dictionary_field_frame(explorer).row(0, named=True)["column"] == "price"


def _entry(
    *,
    concept_id: str,
    title: str,
    status: DashboardStatus,
    notebook_name: str | None,
    backing_assets: tuple[str, ...],
    market_context_ids: tuple[str, ...],
) -> DashboardRegistryEntry:
    return DashboardRegistryEntry(
        concept_id=concept_id,
        title=title,
        description=f"{title} dashboard fixture.",
        audiences=(DashboardAudience.ANALYST,),
        status=status,
        notebook_name=notebook_name,
        backing_assets=backing_assets,
        market_context_ids=market_context_ids,
        source_chunks=(SourceChunkReference("chunk-fixture"),),
    )


def _asset(
    asset_key: tuple[str, ...],
    *,
    columns: tuple[DagsterColumnMetadata, ...],
) -> DagsterTableAsset:
    return DagsterTableAsset(
        asset_key=asset_key,
        group_name="gas_model",
        kinds=("table",),
        description="Asset description.",
        uri=f"s3://dev-energy-market-aemo/{'/'.join(asset_key)}",
        columns=columns,
        is_materializable=True,
        is_executable=True,
        latest_materialization_timestamp=1_714_000_000,
    )
