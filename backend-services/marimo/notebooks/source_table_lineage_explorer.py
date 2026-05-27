import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        SOURCE_COVERAGE_STATE_EMPTY,
        SOURCE_COVERAGE_STATE_GAP,
        SOURCE_COVERAGE_STATE_UNAVAILABLE,
        cached_load_source_coverage_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        source_coverage_table_specs_from_catalogue,
        source_coverage_table_specs,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control
    from marimoserver.source_lineage_explorer import (
        render_source_lineage_explorer_html,
        source_lineage_empty_state_markdown,
        source_lineage_frame,
        source_lineage_kpi_frame,
    )
    from marimoserver.table_explorer import (
        discover_storage,
        discover_table_catalogue,
        discover_table_explorer_config,
        overlay_table_catalogue,
    )

    return (
        SOURCE_COVERAGE_STATE_EMPTY,
        SOURCE_COVERAGE_STATE_GAP,
        SOURCE_COVERAGE_STATE_UNAVAILABLE,
        cached_load_source_coverage_tables,
        discover_dashboard_config,
        discover_storage,
        discover_table_catalogue,
        discover_table_explorer_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        overlay_table_catalogue,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_source_lineage_explorer_html,
        source_coverage_table_specs_from_catalogue,
        source_coverage_table_specs,
        source_lineage_empty_state_markdown,
        source_lineage_frame,
        source_lineage_kpi_frame,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("""
            # Source Table Lineage Explorer

            **Dashboard brief**: **Dashboard intent**: Analytical. Analysts,
            operators, and data engineers start from curated `silver.gas_model`
            tables, inspect represented source systems and tables, and follow
            registry mappings to concept cards, Market context IDs,
            table metadata, and asset metadata. Data scope is bounded Parquet
            reads plus S3/Dagster catalogue metadata and the code-local Marimo
            dashboard registry. Freshness, load timing, cache state, row-limit
            policy, missing lineage fields, unavailable GraphQL, empty storage,
            and bounded AWS preview mode render as explicit states.
            """),
        ]
    )
    return


@app.cell
def _():
    source_lineage_load_cache = {}
    return (source_lineage_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_source_coverage_tables,
    discover_dashboard_config,
    discover_storage,
    discover_table_catalogue,
    discover_table_explorer_config,
    overlay_table_catalogue,
    refresh_data_button,
    refresh_token_from_control,
    source_coverage_table_specs,
    source_coverage_table_specs_from_catalogue,
    source_lineage_load_cache,
):
    config = discover_dashboard_config()
    table_config = discover_table_explorer_config()
    refresh_token = refresh_token_from_control(refresh_data_button)
    storage_discovery = discover_storage(table_config)
    asset_catalogue = discover_table_catalogue(table_config)
    table_catalogue = overlay_table_catalogue(storage_discovery, asset_catalogue)
    lineage_specs = source_coverage_table_specs_from_catalogue(table_catalogue)
    if len(lineage_specs) == 0:
        lineage_specs = source_coverage_table_specs()
    lineage_loads = cached_load_source_coverage_tables(
        config,
        source_lineage_load_cache,
        specs=lineage_specs,
        refresh_token=refresh_token,
    )
    return asset_catalogue, config, lineage_loads, storage_discovery, table_catalogue


@app.cell
def _(lineage_loads, source_lineage_frame, source_lineage_kpi_frame, table_catalogue):
    source_lineage = source_lineage_frame(lineage_loads, table_catalogue)
    lineage_kpis = source_lineage_kpi_frame(lineage_loads, source_lineage)
    return lineage_kpis, source_lineage


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    lineage_loads,
    mo,
):
    mo.vstack(
        [
            mo.md("## Data Health"),
            mo.callout(
                mo.md(gas_table_load_status_message(lineage_loads)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "Source lineage read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(lineage_loads),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(
    asset_catalogue,
    config,
    mo,
    pl,
    source_coverage_table_specs,
    storage_discovery,
    table_catalogue,
):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Registered source assets",
                "Loaded catalogue rows",
                "Discovered table prefixes",
                "Dagster GraphQL",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                str(len(source_coverage_table_specs())),
                str(len(table_catalogue)),
                str(len(storage_discovery.tables)),
                asset_catalogue.url,
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    graphql_detail = (
        ""
        if asset_catalogue.error is None
        else f"\n\nDagster GraphQL detail: `{asset_catalogue.error}`"
    )
    mo.vstack(
        [
            mo.md(f"## Lineage Inputs{graphql_detail}"),
            mo.ui.table(config_frame, selection=None),
        ]
    )
    return


@app.cell
def _(lineage_kpis, mo):
    mo.vstack(
        [
            mo.md("## Lineage Health"),
            mo.ui.table(lineage_kpis, selection=None),
        ]
    )
    return


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.Html(render_dashboard_context_panel("source-table-lineage-explorer"))
    return


@app.cell
def _(mo, pl, source_lineage):
    if source_lineage.is_empty():
        asset_filter = None
        source_system_filter = None
        coverage_state_filter = None
        lineage_search = None
        controls = mo.md("")
    else:
        asset_options = sorted(
            value
            for value in source_lineage.get_column("asset")
            .drop_nulls()
            .cast(pl.String)
            .unique()
            .to_list()
            if value
        )
        source_system_options = sorted(
            value
            for value in source_lineage.get_column("source system")
            .drop_nulls()
            .cast(pl.String)
            .unique()
            .to_list()
            if value
        )
        coverage_state_options = sorted(
            value
            for value in source_lineage.get_column("coverage state")
            .drop_nulls()
            .cast(pl.String)
            .unique()
            .to_list()
            if value
        )
        asset_filter = mo.ui.multiselect(
            options=asset_options,
            value=[],
            label="Curated asset",
            full_width=True,
        )
        source_system_filter = mo.ui.multiselect(
            options=source_system_options,
            value=[],
            label="Source system",
            full_width=True,
        )
        coverage_state_filter = mo.ui.multiselect(
            options=coverage_state_options,
            value=[],
            label="Lineage state",
            full_width=True,
        )
        lineage_search = mo.ui.text(
            placeholder="Search asset, source table, lineage field, path, or detail",
            label="Lineage search",
            full_width=True,
        )
        controls = mo.vstack(
            [
                mo.md("## Explorer Controls"),
                mo.hstack(
                    [
                        asset_filter,
                        source_system_filter,
                        coverage_state_filter,
                        lineage_search,
                    ],
                    gap=1,
                ),
            ],
            gap=0.5,
        )

    controls
    return asset_filter, coverage_state_filter, lineage_search, source_system_filter


@app.cell
def _(
    asset_filter,
    coverage_state_filter,
    lineage_search,
    pl,
    source_lineage,
    source_system_filter,
):
    filtered_source_lineage = source_lineage
    if asset_filter is not None and len(asset_filter.value) > 0:
        filtered_source_lineage = filtered_source_lineage.filter(
            pl.col("asset").is_in(tuple(asset_filter.value))
        )
    if source_system_filter is not None and len(source_system_filter.value) > 0:
        filtered_source_lineage = filtered_source_lineage.filter(
            pl.col("source system").is_in(tuple(source_system_filter.value))
        )
    if coverage_state_filter is not None and len(coverage_state_filter.value) > 0:
        filtered_source_lineage = filtered_source_lineage.filter(
            pl.col("coverage state").is_in(tuple(coverage_state_filter.value))
        )
    if lineage_search is not None and lineage_search.value.strip():
        search_term = lineage_search.value.strip().lower()
        filtered_source_lineage = filtered_source_lineage.filter(
            pl.any_horizontal(
                pl.col("asset")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
                pl.col("table")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
                pl.col("source table")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
                pl.col("lineage fields")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
                pl.col("lineage examples")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
                pl.col("concept cards")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
                pl.col("Market context IDs")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
                pl.col("detail")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
            )
        )
    return (filtered_source_lineage,)


@app.cell
def _(
    filtered_source_lineage,
    lineage_loads,
    mo,
    render_source_lineage_explorer_html,
    source_lineage_empty_state_markdown,
):
    if filtered_source_lineage.is_empty():
        lineage_view = mo.md(source_lineage_empty_state_markdown(lineage_loads))
    else:
        lineage_view = mo.Html(
            render_source_lineage_explorer_html(filtered_source_lineage)
        )

    mo.vstack(
        [
            mo.md("""
            ## Source Table Lineage

            Each row summarizes one curated `silver.gas_model` asset and one
            represented source-system/source-table pair. Scalar `source_table`
            values and list-based `source_tables` values are expanded into
            navigation rows. Extra `source_*` fields, such as source files,
            source identifiers, source timestamps, and surrogate keys, are
            shown when present.
            """),
            lineage_view,
        ]
    )
    return


@app.cell
def _(
    SOURCE_COVERAGE_STATE_EMPTY,
    SOURCE_COVERAGE_STATE_GAP,
    SOURCE_COVERAGE_STATE_UNAVAILABLE,
    mo,
    pl,
    render_source_lineage_explorer_html,
    source_lineage,
):
    gap_states = (
        SOURCE_COVERAGE_STATE_GAP,
        SOURCE_COVERAGE_STATE_EMPTY,
        SOURCE_COVERAGE_STATE_UNAVAILABLE,
    )
    lineage_gaps = source_lineage.filter(pl.col("coverage state").is_in(gap_states))
    if lineage_gaps.is_empty():
        gap_view = mo.md(
            "No loaded source table lineage gaps were found in the current read."
        )
    else:
        gap_view = mo.Html(render_source_lineage_explorer_html(lineage_gaps))

    mo.vstack(
        [
            mo.md("""
            ## Lineage Gaps

            Missing source-system fields, missing source-table fields, empty
            metadata values, unavailable reads, and empty reads appear here as
            first-class explorer rows.
            """),
            gap_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
