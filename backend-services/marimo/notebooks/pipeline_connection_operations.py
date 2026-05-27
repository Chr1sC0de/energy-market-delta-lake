import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        PIPELINE_CONNECTION_OPERATIONS_CONTEXT_ID,
        cached_load_pipeline_connection_operations_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        pipeline_connection_flow_summary_frame,
        pipeline_connection_metadata_frame,
        pipeline_connection_operations_empty_state_markdown,
        pipeline_connection_operations_kpi_frame,
        pipeline_connection_operations_table_specs,
        pipeline_connection_relationship_gap_frame,
        render_dashboard_context_panel,
        render_pipeline_connection_operations_context_links,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        PIPELINE_CONNECTION_OPERATIONS_CONTEXT_ID,
        cached_load_pipeline_connection_operations_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pipeline_connection_flow_summary_frame,
        pipeline_connection_metadata_frame,
        pipeline_connection_operations_empty_state_markdown,
        pipeline_connection_operations_kpi_frame,
        pipeline_connection_operations_table_specs,
        pipeline_connection_relationship_gap_frame,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_pipeline_connection_operations_context_links,
    )


@app.cell
def _(
    PIPELINE_CONNECTION_OPERATIONS_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_pipeline_connection_operations_context_links,
):
    mo.vstack(
        [
            mo.md("""
            # Pipeline and Connection Operations

            **Dashboard brief**: **Dashboard intent**: Operational. Operators
            and analysts use this dashboard to inspect Connection Point flow
            beside Facility, Capacity, and pipeline segment context while
            keeping missing conformed relationships visible as relationship
            gaps. Data scope is the Marimo dashboard registry, Market context
            IDs and source chunk metadata recorded in that registry, plus
            read-only bounded Parquet samples from
            `silver_gas_dim_connection_point`, `silver_gas_dim_facility`,
            `silver_gas_dim_pipeline_segment`, `silver_gas_dim_zone`,
            `silver_gas_fact_connection_point_flow`,
            `silver_gas_fact_operational_meter_flow`, and
            `silver_gas_fact_capacity_outlook`. Freshness, row coverage, cache
            status, load timing, bounded AWS preview caps, and missing-source
            behavior come from the shared gas model loader; unavailable,
            empty, or partially related data renders as designed dashboard
            states instead of notebook tracebacks.
            """),
            mo.Html(
                render_dashboard_context_panel(
                    PIPELINE_CONNECTION_OPERATIONS_CONTEXT_ID
                )
            ),
            mo.Html(render_pipeline_connection_operations_context_links()),
        ]
    )
    return


@app.cell
def _():
    pipeline_connection_load_cache = {}
    return (pipeline_connection_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_pipeline_connection_operations_tables,
    discover_dashboard_config,
    pipeline_connection_load_cache,
    pipeline_connection_operations_table_specs,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    pipeline_connection_specs = pipeline_connection_operations_table_specs()
    pipeline_connection_loads = cached_load_pipeline_connection_operations_tables(
        config,
        pipeline_connection_load_cache,
        specs=pipeline_connection_specs,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, pipeline_connection_loads, pipeline_connection_specs


@app.cell
def _(
    pipeline_connection_flow_summary_frame,
    pipeline_connection_loads,
    pipeline_connection_metadata_frame,
    pipeline_connection_operations_kpi_frame,
    pipeline_connection_relationship_gap_frame,
):
    pipeline_connection_kpis = pipeline_connection_operations_kpi_frame(
        pipeline_connection_loads
    )
    pipeline_connection_flows = pipeline_connection_flow_summary_frame(
        pipeline_connection_loads
    )
    pipeline_connection_metadata = pipeline_connection_metadata_frame(
        pipeline_connection_loads
    )
    pipeline_connection_gaps = pipeline_connection_relationship_gap_frame(
        pipeline_connection_loads
    )
    return (
        pipeline_connection_flows,
        pipeline_connection_gaps,
        pipeline_connection_kpis,
        pipeline_connection_metadata,
    )


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
    pipeline_connection_kpis,
    pipeline_connection_loads,
):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(pipeline_connection_loads)}
                """
            ),
            mo.ui.table(pipeline_connection_kpis, selection=None),
            mo.accordion(
                {
                    "Pipeline and Connection read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(pipeline_connection_loads),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(config, mo, pipeline_connection_specs, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet root",
                "Pipeline and Connection assets",
                "Market context IDs",
                "Source chunk IDs",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                str(len(pipeline_connection_specs)),
                (
                    "glossary:connection-point, glossary:facility, "
                    "glossary:flow, glossary:capacity"
                ),
                (
                    "chunk-gbb-guide-connection-point-identifiers, "
                    "chunk-gbb-guide-flow-report, "
                    "chunk-gbb-procedures-capacity-outlooks, "
                    "chunk-gbb-guide-nameplate-capacity, "
                    "chunk-gbb-procedures-facility-nameplate"
                ),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.accordion(
        {"Pipeline and Connection read configuration": mo.ui.table(config_frame)},
        multiple=False,
    )
    return


@app.cell
def _(
    mo,
    pipeline_connection_flows,
    pipeline_connection_loads,
    pipeline_connection_operations_empty_state_markdown,
):
    flow_view = (
        mo.md(
            pipeline_connection_operations_empty_state_markdown(
                pipeline_connection_loads
            )
        )
        if pipeline_connection_flows.is_empty()
        else mo.ui.table(pipeline_connection_flows, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Connection Point Flow Summary"),
            flow_view,
        ]
    )
    return


@app.cell
def _(
    mo,
    pipeline_connection_loads,
    pipeline_connection_metadata,
    pipeline_connection_operations_empty_state_markdown,
):
    metadata_view = (
        mo.md(
            pipeline_connection_operations_empty_state_markdown(
                pipeline_connection_loads
            )
        )
        if pipeline_connection_metadata.is_empty()
        else mo.ui.table(pipeline_connection_metadata, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Pipeline and Connection Metadata"),
            metadata_view,
        ]
    )
    return


@app.cell
def _(
    mo,
    pipeline_connection_gaps,
    pipeline_connection_loads,
    pipeline_connection_operations_empty_state_markdown,
):
    gap_view = (
        mo.md(
            pipeline_connection_operations_empty_state_markdown(
                pipeline_connection_loads
            )
        )
        if pipeline_connection_gaps.is_empty()
        else mo.ui.table(pipeline_connection_gaps, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Relationship Gaps"),
            gap_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
