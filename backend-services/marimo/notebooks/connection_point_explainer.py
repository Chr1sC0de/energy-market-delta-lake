import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        CONNECTION_POINT_CONTEXT_ID,
        CONNECTION_POINT_DIM_TABLE_NAME,
        cached_load_connection_point_context_tables,
        connection_point_context_empty_state_markdown,
        connection_point_dimension_coverage_frame,
        connection_point_dimension_preview_frame,
        connection_point_relationship_frame,
        connection_point_source_system_frame,
        connection_point_table_specs,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_connection_point_context_links,
        render_dimension_coverage_diagram_html,
        render_dashboard_context_panel,
        render_kpi_cards_html,
        render_relationship_diagram_html,
        table_load_by_name,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        CONNECTION_POINT_CONTEXT_ID,
        CONNECTION_POINT_DIM_TABLE_NAME,
        cached_load_connection_point_context_tables,
        connection_point_context_empty_state_markdown,
        connection_point_dimension_coverage_frame,
        connection_point_dimension_preview_frame,
        connection_point_relationship_frame,
        connection_point_source_system_frame,
        connection_point_table_specs,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_connection_point_context_links,
        render_dimension_coverage_diagram_html,
        render_dashboard_context_panel,
        render_kpi_cards_html,
        render_relationship_diagram_html,
        table_load_by_name,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("""
            # Connection Point Explainer

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators,
            analysts, and stakeholders use this dashboard to inspect cited
            Connection Point Market context metadata, preview coverage in
            `silver.gas_model.silver_gas_dim_connection_point`, and trace
            available relationships to Facility, Location, Hub / Zone, flow
            direction, actual flow, and capacity context. Data scope is the
            Marimo dashboard registry, Market context ID and source chunk
            metadata copied into that registry, plus read-only bounded Parquet
            samples from `silver_gas_dim_connection_point`,
            `silver_gas_dim_facility`, `silver_gas_dim_location`,
            `silver_gas_dim_zone`, `silver_gas_fact_connection_point_flow`,
            and `silver_gas_fact_capacity_outlook`. Freshness, row coverage,
            cache status, load timing, and missing-source behavior come from
            the shared gas model loader; unavailable or empty data renders as
            designed empty states instead of notebook tracebacks.
            """),
        ]
    )
    return


@app.cell
def _():
    connection_point_load_cache = {}
    return (connection_point_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_connection_point_context_tables,
    connection_point_load_cache,
    connection_point_table_specs,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    connection_point_specs = connection_point_table_specs()
    connection_point_loads = cached_load_connection_point_context_tables(
        config,
        connection_point_load_cache,
        specs=connection_point_specs,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, connection_point_loads, connection_point_specs


@app.cell
def _(
    CONNECTION_POINT_DIM_TABLE_NAME,
    connection_point_dimension_coverage_frame,
    connection_point_dimension_preview_frame,
    connection_point_loads,
    connection_point_relationship_frame,
    connection_point_source_system_frame,
    table_load_by_name,
):
    connection_point_load = table_load_by_name(
        connection_point_loads,
        CONNECTION_POINT_DIM_TABLE_NAME,
    )
    connection_point_coverage = connection_point_dimension_coverage_frame(
        connection_point_load
    )
    connection_point_sources = connection_point_source_system_frame(
        connection_point_load
    )
    connection_point_relationships = connection_point_relationship_frame(
        connection_point_loads
    )
    connection_point_preview = connection_point_dimension_preview_frame(
        connection_point_load
    )
    return (
        connection_point_coverage,
        connection_point_load,
        connection_point_preview,
        connection_point_relationships,
        connection_point_sources,
    )


@app.cell
def _(
    connection_point_loads,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(connection_point_loads)}
                """
            ),
            mo.accordion(
                {
                    "Connection Point read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(connection_point_loads),
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
    config,
    connection_point_coverage,
    connection_point_relationships,
    connection_point_specs,
    mo,
    pl,
    render_dimension_coverage_diagram_html,
    render_kpi_cards_html,
    render_relationship_diagram_html,
):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet root",
                "Connection Point-oriented assets",
                "Market context ID",
                "Source chunk IDs",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                str(len(connection_point_specs)),
                ("glossary:connection-point"),
                (
                    "chunk-gbb-guide-connection-point-identifiers, "
                    "chunk-gbb-guide-flow-report"
                ),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.vstack(
        [
            mo.md("## Connection Point Coverage Health"),
            mo.Html(
                render_kpi_cards_html(
                    connection_point_coverage,
                    title="Connection Point coverage KPIs",
                    empty_message=(
                        "No Connection Point coverage metrics are available."
                    ),
                )
            ),
            mo.Html(
                render_relationship_diagram_html(
                    connection_point_relationships,
                    title="Connection Point relationship map",
                    empty_message=(
                        "No Connection Point relationship rows are available "
                        "in the loaded bounded reads."
                    ),
                )
            ),
            mo.Html(
                render_dimension_coverage_diagram_html(
                    connection_point_coverage,
                    title="Connection Point dimension coverage",
                    empty_message=(
                        "No Connection Point dimension coverage rows are "
                        "available in the loaded bounded reads."
                    ),
                )
            ),
            mo.accordion(
                {
                    "Connection point coverage details": mo.ui.table(
                        connection_point_coverage,
                        selection=None,
                    )
                },
                lazy=True,
                multiple=False,
            ),
            mo.accordion(
                {"Coverage inputs": mo.ui.table(config_frame, selection=None)},
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(
    CONNECTION_POINT_CONTEXT_ID,
    mo,
    render_connection_point_context_links,
    render_dashboard_context_panel,
):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(CONNECTION_POINT_CONTEXT_ID)),
            mo.Html(render_connection_point_context_links()),
        ]
    )
    return


@app.cell
def _(
    connection_point_context_empty_state_markdown,
    connection_point_loads,
    connection_point_sources,
    mo,
):
    source_view = (
        mo.md(connection_point_context_empty_state_markdown(connection_point_loads))
        if connection_point_sources.is_empty()
        else mo.ui.table(connection_point_sources, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Source Systems"),
            source_view,
        ]
    )
    return


@app.cell
def _(
    connection_point_context_empty_state_markdown,
    connection_point_loads,
    connection_point_relationships,
    mo,
):
    relationship_view = (
        mo.md(connection_point_context_empty_state_markdown(connection_point_loads))
        if connection_point_relationships.is_empty()
        else mo.ui.table(connection_point_relationships, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Connection Point Relationships"),
            relationship_view,
        ]
    )
    return


@app.cell
def _(
    connection_point_context_empty_state_markdown,
    connection_point_loads,
    connection_point_preview,
    mo,
):
    preview_view = (
        mo.md(connection_point_context_empty_state_markdown(connection_point_loads))
        if connection_point_preview.is_empty()
        else mo.ui.table(connection_point_preview, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Connection Point Dimension Preview"),
            preview_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
