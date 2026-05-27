import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        OPERATIONAL_METER_FLOW_CONTEXT_ID,
        cached_load_operational_meter_flow_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        operational_meter_flow_empty_state_markdown,
        operational_meter_flow_kpi_frame,
        operational_meter_flow_point_context_frame,
        operational_meter_flow_relationship_gap_frame,
        operational_meter_flow_summary_frame,
        operational_meter_flow_table_specs,
        render_dashboard_context_panel,
        render_operational_meter_flow_context_links,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        OPERATIONAL_METER_FLOW_CONTEXT_ID,
        cached_load_operational_meter_flow_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        operational_meter_flow_empty_state_markdown,
        operational_meter_flow_kpi_frame,
        operational_meter_flow_point_context_frame,
        operational_meter_flow_relationship_gap_frame,
        operational_meter_flow_summary_frame,
        operational_meter_flow_table_specs,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_operational_meter_flow_context_links,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("""
            # Operational Meter Flow

            **Dashboard brief**: **Dashboard intent**: Operational. Operators
            and analysts use this dashboard to inspect VICGAS operational meter
            flow quantity, gas interval, point type, flow direction, source
            point identifiers, and relationship coverage to Operational Point,
            Hub / Zone, and Pipeline segment dimensions. Data scope is
            read-only bounded Parquet samples from
            `silver_gas_fact_operational_meter_flow`,
            `silver_gas_dim_operational_point`, `silver_gas_dim_zone`,
            `silver_gas_dim_pipeline_segment`, and copied dashboard registry
            metadata. Freshness, row coverage, cache state, load timing,
            bounded AWS preview caps, and missing-source behavior come from the
            shared loader; missing dimension relationships render as explicit
            coverage gaps.
            """),
        ]
    )
    return


@app.cell
def _():
    operational_meter_flow_load_cache = {}
    return (operational_meter_flow_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_operational_meter_flow_tables,
    discover_dashboard_config,
    operational_meter_flow_load_cache,
    operational_meter_flow_table_specs,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    meter_flow_specs = operational_meter_flow_table_specs()
    meter_flow_loads = cached_load_operational_meter_flow_tables(
        config,
        operational_meter_flow_load_cache,
        specs=meter_flow_specs,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, meter_flow_loads, meter_flow_specs


@app.cell
def _(
    meter_flow_loads,
    operational_meter_flow_kpi_frame,
    operational_meter_flow_point_context_frame,
    operational_meter_flow_relationship_gap_frame,
    operational_meter_flow_summary_frame,
):
    meter_flow_kpis = operational_meter_flow_kpi_frame(meter_flow_loads)
    meter_flow_summary = operational_meter_flow_summary_frame(meter_flow_loads)
    meter_flow_point_context = operational_meter_flow_point_context_frame(
        meter_flow_loads
    )
    meter_flow_gaps = operational_meter_flow_relationship_gap_frame(meter_flow_loads)
    return (
        meter_flow_gaps,
        meter_flow_kpis,
        meter_flow_point_context,
        meter_flow_summary,
    )


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    meter_flow_kpis,
    meter_flow_loads,
    mo,
):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(meter_flow_loads)}
                """
            ),
            mo.ui.table(meter_flow_kpis, selection=None),
            mo.accordion(
                {
                    "Operational Meter Flow read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(meter_flow_loads),
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
    OPERATIONAL_METER_FLOW_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_operational_meter_flow_context_links,
):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(OPERATIONAL_METER_FLOW_CONTEXT_ID)),
            mo.Html(render_operational_meter_flow_context_links()),
        ]
    )
    return


@app.cell
def _(config, meter_flow_specs, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet root",
                "Operational Meter Flow assets",
                "Market context ID",
                "Source chunk IDs",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                str(len(meter_flow_specs)),
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
        {"Operational Meter Flow read configuration": mo.ui.table(config_frame)},
        multiple=False,
    )
    return


@app.cell
def _(
    meter_flow_loads,
    meter_flow_summary,
    mo,
    operational_meter_flow_empty_state_markdown,
):
    summary_view = (
        mo.md(operational_meter_flow_empty_state_markdown(meter_flow_loads))
        if meter_flow_summary.is_empty()
        else mo.ui.table(meter_flow_summary, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Meter Flow Summary"),
            summary_view,
        ]
    )
    return


@app.cell
def _(
    meter_flow_loads,
    meter_flow_point_context,
    mo,
    operational_meter_flow_empty_state_markdown,
):
    point_context_view = (
        mo.md(operational_meter_flow_empty_state_markdown(meter_flow_loads))
        if meter_flow_point_context.is_empty()
        else mo.ui.table(meter_flow_point_context, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Operational Point Dimension Context"),
            point_context_view,
        ]
    )
    return


@app.cell
def _(
    meter_flow_gaps,
    meter_flow_loads,
    mo,
    operational_meter_flow_empty_state_markdown,
):
    gap_view = (
        mo.md(operational_meter_flow_empty_state_markdown(meter_flow_loads))
        if meter_flow_gaps.is_empty()
        else mo.ui.table(meter_flow_gaps, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Relationship Coverage Gaps"),
            gap_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
