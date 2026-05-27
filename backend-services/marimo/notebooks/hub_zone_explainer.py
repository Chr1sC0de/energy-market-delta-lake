import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        HUB_ZONE_CONTEXT_ID,
        HUB_ZONE_DIM_TABLE_NAME,
        cached_load_hub_zone_context_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        hub_zone_context_empty_state_markdown,
        hub_zone_dimension_coverage_frame,
        hub_zone_identifier_preview_frame,
        hub_zone_source_system_frame,
        hub_zone_table_specs,
        render_dashboard_context_panel,
        render_hub_zone_context_links,
        table_load_by_name,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        HUB_ZONE_CONTEXT_ID,
        HUB_ZONE_DIM_TABLE_NAME,
        cached_load_hub_zone_context_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        hub_zone_context_empty_state_markdown,
        hub_zone_dimension_coverage_frame,
        hub_zone_identifier_preview_frame,
        hub_zone_source_system_frame,
        hub_zone_table_specs,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_hub_zone_context_links,
        table_load_by_name,
    )


@app.cell
def _(mo):
    mo.md("""
    # Hub / Zone

    **Dashboard brief**: **Dashboard intent**: Analytical. Analysts and
    stakeholders use this dashboard to connect the generated Hub / Zone Market
    context to the current `silver_gas_dim_zone` dimension, inspect STTM hub and
    DWGM/GBB zone coverage, and follow related operational or market-analysis
    dashboards. Data scope is the Marimo dashboard registry, Market context ID
    and source chunk metadata copied into that registry, plus a read-only
    bounded Parquet sample from `silver_gas_dim_zone`. Freshness, row coverage,
    cache status, load timing, row-limit policy, and missing-source behavior
    come from the shared gas model loader; unavailable or empty data renders as
    designed empty states instead of notebook tracebacks.
    """)
    return


@app.cell
def _():
    hub_zone_load_cache = {}
    return (hub_zone_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_hub_zone_context_tables,
    discover_dashboard_config,
    hub_zone_load_cache,
    hub_zone_table_specs,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    hub_zone_specs = hub_zone_table_specs()
    hub_zone_loads = cached_load_hub_zone_context_tables(
        config,
        hub_zone_load_cache,
        specs=hub_zone_specs,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, hub_zone_loads, hub_zone_specs


@app.cell
def _(
    HUB_ZONE_DIM_TABLE_NAME,
    hub_zone_dimension_coverage_frame,
    hub_zone_identifier_preview_frame,
    hub_zone_loads,
    hub_zone_source_system_frame,
    table_load_by_name,
):
    hub_zone_load = table_load_by_name(hub_zone_loads, HUB_ZONE_DIM_TABLE_NAME)
    hub_zone_coverage = hub_zone_dimension_coverage_frame(hub_zone_load)
    hub_zone_sources = hub_zone_source_system_frame(hub_zone_load)
    hub_zone_identifiers = hub_zone_identifier_preview_frame(hub_zone_load)
    return hub_zone_coverage, hub_zone_identifiers, hub_zone_load, hub_zone_sources


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    hub_zone_loads,
    mo,
):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(hub_zone_loads)}
                """
            ),
            mo.accordion(
                {
                    "Hub / Zone read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(hub_zone_loads),
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
    HUB_ZONE_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_hub_zone_context_links,
):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(HUB_ZONE_CONTEXT_ID)),
            mo.Html(render_hub_zone_context_links()),
        ]
    )
    return


@app.cell
def _(config, hub_zone_coverage, hub_zone_specs, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet root",
                "Hub / Zone assets",
                "Market context ID",
                "Source chunk IDs",
                "Source-qualified grain",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                str(len(hub_zone_specs)),
                "glossary:hub-zone",
                (
                    "chunk-sttm-procedures-definitions, "
                    "chunk-sttm-procedures-settlement-terms, "
                    "chunk-dwgm-operations-glossary-schedule, "
                    "chunk-dwgm-operations-capacity-certificates-modelling"
                ),
                "source_system + zone_type + source_zone_id",
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.vstack(
        [
            mo.md("## Hub / Zone Coverage Health"),
            mo.ui.table(hub_zone_coverage, selection=None),
            mo.accordion(
                {"Coverage inputs": mo.ui.table(config_frame, selection=None)},
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(
    hub_zone_context_empty_state_markdown,
    hub_zone_loads,
    hub_zone_sources,
    mo,
):
    source_view = (
        mo.md(hub_zone_context_empty_state_markdown(hub_zone_loads))
        if hub_zone_sources.is_empty()
        else mo.ui.table(hub_zone_sources, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Source System Coverage"),
            source_view,
        ]
    )
    return


@app.cell
def _(
    hub_zone_context_empty_state_markdown,
    hub_zone_identifiers,
    hub_zone_loads,
    mo,
):
    identifier_view = (
        mo.md(hub_zone_context_empty_state_markdown(hub_zone_loads))
        if hub_zone_identifiers.is_empty()
        else mo.ui.table(hub_zone_identifiers, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Source-Qualified Hub / Zone Identifiers"),
            identifier_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
