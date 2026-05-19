import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        SOURCE_COVERAGE_STATE_GAP,
        cached_load_source_coverage_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_source_coverage_matrix_html,
        source_coverage_empty_state_markdown,
        source_coverage_kpi_frame,
        source_coverage_matrix_frame,
        source_coverage_table_specs_from_catalogue,
        source_coverage_table_specs,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control
    from marimoserver.table_explorer import (
        discover_storage,
        discover_table_catalogue,
        discover_table_explorer_config,
        overlay_table_catalogue,
    )

    return (
        SOURCE_COVERAGE_STATE_GAP,
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
        render_source_coverage_matrix_html,
        source_coverage_empty_state_markdown,
        source_coverage_kpi_frame,
        source_coverage_matrix_frame,
        source_coverage_table_specs_from_catalogue,
        source_coverage_table_specs,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Source Coverage Matrix

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators,
            analysts, and data engineers use this dashboard to inspect which
            source systems and source tables are represented by registry-backed
            `silver.gas_model` facts and dimensions. Data scope is read-only
            Parquet table reads under `silver/gas_model`, plus table explorer
            metadata from S3 discovery and Dagster GraphQL when available.
            Freshness, load timing, cache status, and row-limit policy come
            from the shared gas model loader. Missing `source_table` or
            `source_tables` columns, unavailable GraphQL, empty LocalStack/AWS
            storage, and bounded AWS preview mode render as explicit coverage
            states instead of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("source-coverage-matrix")),
        ]
    )
    return


@app.cell
def _():
    source_coverage_load_cache = {}
    return (source_coverage_load_cache,)


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
    source_coverage_load_cache,
    source_coverage_table_specs_from_catalogue,
):
    config = discover_dashboard_config()
    table_config = discover_table_explorer_config()
    refresh_token = refresh_token_from_control(refresh_data_button)
    storage_discovery = discover_storage(table_config)
    asset_catalogue = discover_table_catalogue(table_config)
    table_catalogue = overlay_table_catalogue(storage_discovery, asset_catalogue)
    coverage_specs = source_coverage_table_specs_from_catalogue(table_catalogue)
    coverage_loads = cached_load_source_coverage_tables(
        config,
        source_coverage_load_cache,
        specs=coverage_specs,
        refresh_token=refresh_token,
    )
    return asset_catalogue, config, coverage_loads, storage_discovery, table_catalogue


@app.cell
def _(
    coverage_loads,
    source_coverage_kpi_frame,
    source_coverage_matrix_frame,
    table_catalogue,
):
    coverage_matrix = source_coverage_matrix_frame(coverage_loads, table_catalogue)
    coverage_kpis = source_coverage_kpi_frame(coverage_loads, coverage_matrix)
    return coverage_kpis, coverage_matrix


@app.cell
def _(
    coverage_loads,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(coverage_loads)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "Source coverage read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(coverage_loads),
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
                "Registered coverage assets",
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
            mo.md(f"## Coverage Inputs{graphql_detail}"),
            mo.ui.table(config_frame, selection=None),
        ]
    )
    return


@app.cell
def _(coverage_kpis, mo):
    mo.vstack(
        [
            mo.md("## Coverage Health"),
            mo.ui.table(coverage_kpis, selection=None),
        ]
    )
    return


@app.cell
def _(coverage_matrix, mo, pl):
    if coverage_matrix.is_empty():
        source_system_filter = None
        coverage_state_filter = None
        asset_search = None
        controls = mo.md("")
    else:
        source_system_options = sorted(
            value
            for value in coverage_matrix.get_column("source system")
            .drop_nulls()
            .cast(pl.String)
            .unique()
            .to_list()
            if value
        )
        coverage_state_options = sorted(
            value
            for value in coverage_matrix.get_column("coverage state")
            .drop_nulls()
            .cast(pl.String)
            .unique()
            .to_list()
            if value
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
            label="Coverage state",
            full_width=True,
        )
        asset_search = mo.ui.text(
            placeholder="Search asset, table, source table, URI, or detail",
            label="Coverage search",
            full_width=True,
        )
        controls = mo.vstack(
            [
                mo.md("## Matrix Controls"),
                mo.hstack(
                    [source_system_filter, coverage_state_filter, asset_search],
                    gap=1,
                ),
            ],
            gap=0.5,
        )

    controls
    return asset_search, coverage_state_filter, source_system_filter


@app.cell
def _(
    asset_search,
    coverage_matrix,
    coverage_state_filter,
    pl,
    source_system_filter,
):
    filtered_coverage_matrix = coverage_matrix
    if source_system_filter is not None and len(source_system_filter.value) > 0:
        filtered_coverage_matrix = filtered_coverage_matrix.filter(
            pl.col("source system").is_in(tuple(source_system_filter.value))
        )
    if coverage_state_filter is not None and len(coverage_state_filter.value) > 0:
        filtered_coverage_matrix = filtered_coverage_matrix.filter(
            pl.col("coverage state").is_in(tuple(coverage_state_filter.value))
        )
    if asset_search is not None and asset_search.value.strip():
        search_term = asset_search.value.strip().lower()
        filtered_coverage_matrix = filtered_coverage_matrix.filter(
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
                pl.col("uri")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
                pl.col("detail")
                .str.to_lowercase()
                .str.contains(search_term, literal=True),
            )
        )
    return (filtered_coverage_matrix,)


@app.cell
def _(
    coverage_loads,
    filtered_coverage_matrix,
    mo,
    render_source_coverage_matrix_html,
    source_coverage_empty_state_markdown,
):
    if filtered_coverage_matrix.is_empty():
        matrix_view = mo.md(source_coverage_empty_state_markdown(coverage_loads))
    else:
        matrix_view = mo.Html(
            render_source_coverage_matrix_html(filtered_coverage_matrix)
        )

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage Matrix

            Each row summarizes a loaded `silver.gas_model` asset and one
            source-system/source-table pair. `source_tables` list values are
            expanded so multi-source rows contribute to each represented source
            table. Link columns open the table explorer or asset metadata view
            when the catalogue overlay exposed a matching row.
            """),
            matrix_view,
        ]
    )
    return


@app.cell
def _(
    SOURCE_COVERAGE_STATE_GAP,
    coverage_matrix,
    mo,
    pl,
    render_source_coverage_matrix_html,
):
    coverage_gaps = coverage_matrix.filter(
        pl.col("coverage state") == SOURCE_COVERAGE_STATE_GAP
    )
    if coverage_gaps.is_empty():
        gap_view = mo.md(
            "No loaded source metadata coverage gaps were found in the current read."
        )
    else:
        gap_view = mo.Html(render_source_coverage_matrix_html(coverage_gaps))

    mo.vstack(
        [
            mo.md("""
            ## Coverage Gaps

            Missing `source_table` or `source_tables` columns and empty source
            metadata values appear here as first-class dashboard rows.
            """),
            gap_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
