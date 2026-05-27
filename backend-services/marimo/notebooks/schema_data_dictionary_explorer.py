import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.data_dictionary_explorer import (
        data_dictionary_action_markdown,
        data_dictionary_asset_frame,
        data_dictionary_field_frame,
        data_dictionary_mart_frame,
        build_data_dictionary_explorer,
        filter_data_dictionary_explorer,
        render_data_dictionary_status_cards,
    )
    from marimoserver.gas_dashboard import render_dashboard_context_panel
    from marimoserver.gas_model_loader import refresh_token_from_control
    from marimoserver.table_explorer import (
        discover_table_catalogue,
        discover_table_explorer_config,
    )

    return (
        build_data_dictionary_explorer,
        data_dictionary_action_markdown,
        data_dictionary_asset_frame,
        data_dictionary_field_frame,
        data_dictionary_mart_frame,
        discover_table_catalogue,
        discover_table_explorer_config,
        filter_data_dictionary_explorer,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_data_dictionary_status_cards,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("""
            # Schema Data Dictionary Explorer

            **Dashboard brief**: **Dashboard intent**: Analytical. Analysts,
            operators, and data engineers use this dashboard to inspect current
            column metadata for registry-mapped `silver.gas_model` assets by
            Market context concept, gas-model mart, asset, and dashboard route.
            Data scope is read-only Dagster GraphQL table metadata and the
            code-local Marimo concept-to-asset mapping; it does not scan table
            rows, change ETL schemas, or open generated Market context
            artifacts at runtime. Freshness is the latest notebook refresh. Unavailable
            GraphQL, missing Dagster asset metadata, and assets without parsed
            schema metadata render as explicit data dictionary states.
            """),
        ]
    )
    return


@app.cell
def _(mo):
    refresh_dictionary_button = mo.ui.run_button(label="Refresh data dictionary")
    refresh_dictionary_button
    return (refresh_dictionary_button,)


@app.cell
def _(
    build_data_dictionary_explorer,
    discover_table_catalogue,
    discover_table_explorer_config,
    refresh_dictionary_button,
    refresh_token_from_control,
):
    config = discover_table_explorer_config()
    refresh_token = refresh_token_from_control(refresh_dictionary_button)
    catalogue = discover_table_catalogue(config)
    data_dictionary = build_data_dictionary_explorer(catalogue)
    return catalogue, config, data_dictionary, refresh_token


@app.cell
def _(
    data_dictionary,
    data_dictionary_action_markdown,
    mo,
    render_data_dictionary_status_cards,
):
    action_kind = (
        "neutral" if data_dictionary.missing_schema_asset_count == 0 else "warn"
    )
    mo.vstack(
        [
            mo.Html(render_data_dictionary_status_cards(data_dictionary)),
            mo.callout(
                mo.md(data_dictionary_action_markdown(data_dictionary)),
                kind=action_kind,
            ),
        ]
    )
    return


@app.cell
def _(config, data_dictionary, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "Runtime",
                "Dagster GraphQL",
                "GraphQL status",
                "Schema source",
                "Concept source",
                "Filtering policy",
            ],
            "value": [
                config.runtime_location,
                config.dagster_graphql_url,
                "Available" if data_dictionary.graphql_available else "Unavailable",
                "Read-only Dagster table metadata",
                "Marimo dashboard registry concept-to-asset mapping",
                "Metadata only; no table-content scans",
            ],
        }
    )
    mo.vstack(
        [
            mo.md("## Runtime Configuration"),
            mo.ui.table(config_frame, selection=None),
        ]
    )
    return


@app.cell
def _(data_dictionary, mo):
    concept_options = tuple(concept.concept_id for concept in data_dictionary.concepts)
    mart_options = tuple(sorted({asset.mart for asset in data_dictionary.assets}))
    schema_state_options = tuple(
        sorted({asset.schema_state.value for asset in data_dictionary.assets})
    )
    concept_filter = mo.ui.multiselect(
        options=concept_options,
        value=[],
        label="Concept group",
        full_width=True,
    )
    mart_filter = mo.ui.multiselect(
        options=mart_options,
        value=[],
        label="Gas-model mart",
        full_width=True,
    )
    schema_state_filter = mo.ui.multiselect(
        options=schema_state_options,
        value=[],
        label="Schema state",
        full_width=True,
    )
    dictionary_search = mo.ui.text(
        placeholder="Search concept, mart, asset, dashboard route, column, or metadata state",
        label="Dictionary search",
        debounce=False,
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Dictionary Controls"),
            concept_filter,
            mart_filter,
            schema_state_filter,
            dictionary_search,
        ]
    )
    return concept_filter, dictionary_search, mart_filter, schema_state_filter


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.Html(render_dashboard_context_panel("schema-data-dictionary-explorer"))
    return


@app.cell
def _(
    concept_filter,
    data_dictionary,
    dictionary_search,
    filter_data_dictionary_explorer,
    mart_filter,
    schema_state_filter,
):
    filtered_dictionary = filter_data_dictionary_explorer(
        data_dictionary,
        concept_ids=tuple(concept_filter.value),
        marts=tuple(mart_filter.value),
        schema_states=tuple(schema_state_filter.value),
        search=dictionary_search.value,
    )
    return (filtered_dictionary,)


@app.cell
def _(data_dictionary_mart_frame, filtered_dictionary, mo):
    mo.vstack(
        [
            mo.md("## Mart Coverage"),
            mo.ui.table(
                data_dictionary_mart_frame(filtered_dictionary),
                selection=None,
                page_size=10,
            ),
        ]
    )
    return


@app.cell
def _(data_dictionary_asset_frame, filtered_dictionary, mo):
    mo.vstack(
        [
            mo.md("## Concept Asset Dictionary"),
            mo.ui.table(
                data_dictionary_asset_frame(filtered_dictionary),
                selection=None,
                page_size=15,
            ),
        ]
    )
    return


@app.cell
def _(data_dictionary_field_frame, filtered_dictionary, mo):
    mo.vstack(
        [
            mo.md("## Column Metadata"),
            mo.ui.table(
                data_dictionary_field_frame(filtered_dictionary),
                selection=None,
                page_size=25,
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
