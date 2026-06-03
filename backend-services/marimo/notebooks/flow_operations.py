import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        FLOW_CONTEXT_ID,
        cached_load_flow_context_tables,
        discover_dashboard_config,
        flow_context_empty_state_markdown,
        flow_kpi_frame,
        flow_recent_observation_frame,
        flow_source_summary_frame,
        flow_table_specs,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_flow_context_links,
        render_flow_source_status_html,
        render_kpi_cards_html,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        FLOW_CONTEXT_ID,
        cached_load_flow_context_tables,
        discover_dashboard_config,
        flow_context_empty_state_markdown,
        flow_kpi_frame,
        flow_recent_observation_frame,
        flow_source_summary_frame,
        flow_table_specs,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_flow_context_links,
        render_flow_source_status_html,
        render_kpi_cards_html,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("""
            # Flow Operations

            **Dashboard brief**: **Dashboard intent**: Operational. Operators,
            analysts, and stakeholders use this dashboard to inspect current
            bounded Flow readiness across actual connection point flow,
            facility flow/storage, nomination forecasts, and operational meter
            flow. Data scope is the Marimo dashboard registry, Market context
            IDs and source chunk metadata recorded in that registry, plus
            read-only bounded Parquet samples from
            `silver_gas_fact_connection_point_flow`,
            `silver_gas_fact_facility_flow_storage`,
            `silver_gas_fact_nomination_forecast`, and
            `silver_gas_fact_operational_meter_flow`. Freshness, row coverage,
            cache status, load timing, source-system coverage, and
            missing-source behavior come from the shared gas model loader;
            unavailable tables, empty tables, and missing columns render as
            designed empty states instead of notebook tracebacks.
            """),
        ]
    )
    return


@app.cell
def _():
    flow_load_cache = {}
    return (flow_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_flow_context_tables,
    discover_dashboard_config,
    flow_load_cache,
    flow_table_specs,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    flow_specs = flow_table_specs()
    flow_loads = cached_load_flow_context_tables(
        config,
        flow_load_cache,
        specs=flow_specs,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, flow_loads, flow_specs


@app.cell
def _(
    flow_kpi_frame,
    flow_loads,
    flow_recent_observation_frame,
    flow_source_summary_frame,
):
    flow_kpis = flow_kpi_frame(flow_loads)
    flow_sources = flow_source_summary_frame(flow_loads)
    flow_recent_observations = flow_recent_observation_frame(flow_loads)
    return flow_kpis, flow_recent_observations, flow_sources


@app.cell
def _(
    flow_kpis,
    flow_loads,
    flow_sources,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
    render_flow_source_status_html,
    render_kpi_cards_html,
):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(flow_loads)}
                """
            ),
            mo.Html(render_kpi_cards_html(flow_kpis, title="Flow operations KPIs")),
            mo.Html(render_flow_source_status_html(flow_sources)),
            mo.accordion(
                {
                    "Flow read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(flow_loads),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(config, flow_specs, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet root",
                "Flow-oriented assets",
                "Market context ID",
                "Source chunk IDs",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                str(len(flow_specs)),
                "glossary:flow",
                (
                    "chunk-gbb-guide-flow-report, "
                    "chunk-gbb-procedures-scheduled-flow, "
                    "chunk-sttm-procedures-settlement-terms"
                ),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.accordion(
        {"Flow read configuration": mo.ui.table(config_frame, selection=None)},
        multiple=False,
    )
    return


@app.cell
def _(FLOW_CONTEXT_ID, mo, render_dashboard_context_panel, render_flow_context_links):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(FLOW_CONTEXT_ID)),
            mo.Html(render_flow_context_links()),
        ]
    )
    return


@app.cell
def _(flow_context_empty_state_markdown, flow_loads, flow_sources, mo):
    source_view = (
        mo.md(flow_context_empty_state_markdown(flow_loads))
        if flow_sources.is_empty()
        else mo.ui.table(flow_sources, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Source System Coverage"),
            mo.accordion(
                {"Source system coverage detail": source_view},
                multiple=False,
                lazy=True,
            ),
        ]
    )
    return


@app.cell
def _(flow_context_empty_state_markdown, flow_loads, flow_recent_observations, mo):
    recent_view = (
        mo.md(flow_context_empty_state_markdown(flow_loads))
        if flow_recent_observations.is_empty()
        else mo.ui.table(flow_recent_observations, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Recent / Sample Flow Observations"),
            recent_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
