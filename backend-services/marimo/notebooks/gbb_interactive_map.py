import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    from datetime import date

    import marimo as mo

    from marimoserver.gas_dashboard import discover_dashboard_config
    from marimoserver.gbb_interactive_map import (
        build_gbb_map_model,
        check_gbb_map_s3_endpoint,
        facility_records_frame,
        load_gbb_map_tables,
        map_load_status_frame,
        normalize_gas_date,
        pipeline_records_frame,
        render_gbb_map_html,
    )

    return (
        build_gbb_map_model,
        check_gbb_map_s3_endpoint,
        date,
        discover_dashboard_config,
        facility_records_frame,
        load_gbb_map_tables,
        map_load_status_frame,
        mo,
        normalize_gas_date,
        pipeline_records_frame,
        render_gbb_map_html,
    )


@app.cell
def _(date, mo):
    gas_date_picker = mo.ui.date(value=date.today(), label="Gas day")
    view_picker = mo.ui.radio(
        options=["Summary", "Pipeline", "Production", "Storage"],
        value="Summary",
        label="View",
        inline=True,
    )

    mo.hstack([gas_date_picker, view_picker], justify="start", gap=1)
    return gas_date_picker, view_picker


@app.cell
def _(check_gbb_map_s3_endpoint, discover_dashboard_config, load_gbb_map_tables):
    config = discover_dashboard_config()
    loaded_map_tables = load_gbb_map_tables(
        config,
        endpoint_checker=check_gbb_map_s3_endpoint,
    )
    return config, loaded_map_tables


@app.cell
def _(
    build_gbb_map_model,
    gas_date_picker,
    loaded_map_tables,
    normalize_gas_date,
    view_picker,
):
    selected_gas_date = normalize_gas_date(gas_date_picker.value)
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
def _(loaded_map_tables, map_load_status_frame, mo):
    failed_count = sum(load.error is not None for load in loaded_map_tables)
    if failed_count == 0:
        input_status = mo.callout("All map input tables loaded.", kind="success")
    else:
        input_status = mo.callout(
            (
                f"{failed_count} map input tables could not be read from S3. "
                "The map is showing static topology until LocalStack has the "
                "materialized gas_model tables."
            ),
            kind="warn",
        )

    mo.vstack(
        [
            input_status,
            mo.accordion(
                {
                    "Map input diagnostics": mo.ui.table(
                        map_load_status_frame(loaded_map_tables),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
