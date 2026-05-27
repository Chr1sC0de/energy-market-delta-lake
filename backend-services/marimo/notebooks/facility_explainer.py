import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        FACILITY_CONTEXT_ID,
        FACILITY_DIM_TABLE_NAME,
        cached_load_facility_context_tables,
        discover_dashboard_config,
        facility_context_empty_state_markdown,
        facility_dimension_coverage_frame,
        facility_dimension_preview_frame,
        facility_relationship_frame,
        facility_table_specs,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_facility_context_links,
        table_load_by_name,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        FACILITY_CONTEXT_ID,
        FACILITY_DIM_TABLE_NAME,
        cached_load_facility_context_tables,
        discover_dashboard_config,
        facility_context_empty_state_markdown,
        facility_dimension_coverage_frame,
        facility_dimension_preview_frame,
        facility_relationship_frame,
        facility_table_specs,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_facility_context_links,
        table_load_by_name,
    )


@app.cell
def _(
    FACILITY_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_facility_context_links,
):
    mo.vstack(
        [
            mo.md("""
            # Facility Explainer

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators,
            analysts, and stakeholders use this dashboard to inspect the cited
            Facility Market context metadata, preview coverage in
            `silver.gas_model.silver_gas_dim_facility`, and trace available
            Facility relationships to participant, zone, flow, storage, and
            capacity context. Data scope is the Marimo dashboard registry,
            Market context ID and source chunk metadata copied into that
            registry, plus read-only bounded Parquet samples from
            `silver_gas_dim_facility`, `silver_gas_fact_facility_flow_storage`,
            and `silver_gas_fact_capacity_outlook`. Freshness, row coverage,
            cache status, load timing, and missing-source behavior come from
            the shared gas model loader; unavailable or empty data renders as
            designed empty states instead of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel(FACILITY_CONTEXT_ID)),
            mo.Html(render_facility_context_links()),
        ]
    )
    return


@app.cell
def _():
    facility_load_cache = {}
    return (facility_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_facility_context_tables,
    discover_dashboard_config,
    facility_load_cache,
    facility_table_specs,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    facility_specs = facility_table_specs()
    facility_loads = cached_load_facility_context_tables(
        config,
        facility_load_cache,
        specs=facility_specs,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, facility_loads, facility_specs


@app.cell
def _(
    FACILITY_DIM_TABLE_NAME,
    facility_dimension_coverage_frame,
    facility_dimension_preview_frame,
    facility_loads,
    facility_relationship_frame,
    table_load_by_name,
):
    facility_load = table_load_by_name(facility_loads, FACILITY_DIM_TABLE_NAME)
    facility_coverage = facility_dimension_coverage_frame(facility_load)
    facility_relationships = facility_relationship_frame(facility_loads)
    facility_preview = facility_dimension_preview_frame(facility_load)
    return facility_coverage, facility_load, facility_preview, facility_relationships


@app.cell
def _(
    facility_loads,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(facility_loads)}
                """
            ),
            mo.accordion(
                {
                    "Facility read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(facility_loads),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(config, facility_coverage, facility_specs, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet root",
                "Facility-oriented assets",
                "Market context ID",
                "Source chunk IDs",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                str(len(facility_specs)),
                "glossary:facility",
                "chunk-gbb-guide-nodes-facilities, chunk-gbb-procedures-facility-nameplate",
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.vstack(
        [
            mo.md("## Facility Coverage Health"),
            mo.ui.table(facility_coverage, selection=None),
            mo.accordion(
                {"Coverage inputs": mo.ui.table(config_frame, selection=None)},
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(
    facility_context_empty_state_markdown,
    facility_loads,
    facility_relationships,
    mo,
):
    relationship_view = (
        mo.md(facility_context_empty_state_markdown(facility_loads))
        if facility_relationships.is_empty()
        else mo.ui.table(facility_relationships, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Facility Relationships"),
            relationship_view,
        ]
    )
    return


@app.cell
def _(
    facility_context_empty_state_markdown,
    facility_loads,
    facility_preview,
    mo,
):
    preview_view = (
        mo.md(facility_context_empty_state_markdown(facility_loads))
        if facility_preview.is_empty()
        else mo.ui.table(facility_preview, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Facility Dimension Preview"),
            preview_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
