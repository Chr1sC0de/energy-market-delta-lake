import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    from datetime import date

    import marimo as mo

    from marimoserver.gas_dashboard import (
        discover_dashboard_config,
        render_dashboard_context_panel,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control
    from marimoserver.gbb_interactive_map import (
        GBB_MAP_CONTEXT_PANELS,
        build_gbb_map_model,
        cached_load_gbb_map_tables,
        check_gbb_map_s3_endpoint,
        facility_records_frame,
        map_load_status_frame,
        map_load_status_message,
        map_load_status_summary,
        normalize_gas_date,
        pipeline_records_frame,
        render_gbb_map_html,
    )

    return (
        GBB_MAP_CONTEXT_PANELS,
        build_gbb_map_model,
        cached_load_gbb_map_tables,
        check_gbb_map_s3_endpoint,
        date,
        discover_dashboard_config,
        facility_records_frame,
        map_load_status_frame,
        map_load_status_message,
        map_load_status_summary,
        mo,
        normalize_gas_date,
        pipeline_records_frame,
        render_dashboard_context_panel,
        render_gbb_map_html,
        refresh_token_from_control,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.Html('<div style="height: 2rem;" aria-hidden="true"></div>'),
            mo.md("""
            # GBB Interactive Map

            **Dashboard brief**: **Dashboard intent**: Operational. Operators
            and analysts use this dashboard to inspect GBB facility topology,
            pipeline flow, storage, production, nominations, and capacity
            outlook inputs from configured `silver.gas_model` tables. Freshness,
            row-limit policy, cache status, and availability are reported from
            the loaded map input tables; unavailable LocalStack data falls back
            to static topology with diagnostics.
            """),
        ]
    )
    return


@app.cell
def _():
    gbb_map_load_cache = {}
    return gbb_map_load_cache


@app.cell
def _(date, mo):
    gas_date_picker = mo.ui.date(value=date.today(), label="Gas day")
    view_picker = mo.ui.radio(
        options=["Summary", "Pipeline", "Production", "Storage"],
        value="Summary",
        label="View",
        inline=False,
    )
    refresh_data_button = mo.ui.run_button(label="Refresh data")

    mo.vstack(
        [
            mo.hstack([gas_date_picker, refresh_data_button], justify="start", gap=1),
            view_picker,
        ],
        gap=0.5,
    )
    return gas_date_picker, refresh_data_button, view_picker


@app.cell
def _(
    cached_load_gbb_map_tables,
    check_gbb_map_s3_endpoint,
    discover_dashboard_config,
    gbb_map_load_cache,
    gas_date_picker,
    normalize_gas_date,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    selected_gas_date = normalize_gas_date(gas_date_picker.value)
    loaded_map_tables = cached_load_gbb_map_tables(
        config,
        gbb_map_load_cache,
        endpoint_checker=check_gbb_map_s3_endpoint,
        gas_date=selected_gas_date,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return loaded_map_tables, selected_gas_date


@app.cell
def _(
    loaded_map_tables,
    map_load_status_frame,
    map_load_status_message,
    map_load_status_summary,
    mo,
):
    degraded = any(not load.available for load in loaded_map_tables)
    input_status = mo.callout(
        map_load_status_summary(loaded_map_tables),
        kind="warn" if degraded else "success",
    )

    mo.vstack(
        [
            input_status,
            mo.accordion(
                {
                    "Map input diagnostics": mo.vstack(
                        [
                            mo.md(map_load_status_message(loaded_map_tables)),
                            mo.ui.table(
                                map_load_status_frame(loaded_map_tables),
                                selection=None,
                            ),
                        ]
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(
    build_gbb_map_model,
    loaded_map_tables,
    selected_gas_date,
    view_picker,
):
    selected_view = view_picker.value
    map_model = build_gbb_map_model(loaded_map_tables, selected_gas_date)
    return map_model, selected_view


@app.cell
def _(map_model, mo, render_gbb_map_html, selected_view):
    mo.Html(render_gbb_map_html(map_model, selected_view))
    return


@app.cell
def _(
    facility_records_frame,
    map_model,
    mo,
    pipeline_records_frame,
    selected_view,
):
    if selected_view in ("Production", "Storage"):
        records = [
            record for record in map_model.facilities if record.kind == selected_view
        ]
        selected_frame = facility_records_frame(records)
    else:
        selected_frame = pipeline_records_frame(map_model.pipelines)

    mo.vstack(
        [
            mo.md("### Selected view data"),
            mo.ui.table(selected_frame, selection=None),
        ]
    )
    return


@app.cell
def _(GBB_MAP_CONTEXT_PANELS, mo, render_dashboard_context_panel):
    context_panels = {
        "GBB interactive map": mo.Html(
            render_dashboard_context_panel("gbb-interactive-map")
        )
    }
    context_panels.update(
        {
            f"{label} concept": mo.Html(render_dashboard_context_panel(concept_id))
            for label, concept_id in GBB_MAP_CONTEXT_PANELS
        }
    )

    mo.vstack(
        [
            mo.md("## Registry and Roadmap Context"),
            mo.accordion(context_panels, multiple=False),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
