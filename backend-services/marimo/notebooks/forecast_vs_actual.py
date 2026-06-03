import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    from datetime import date

    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        FACILITY_FLOW_STORAGE_TABLE_NAME,
        FORECAST_ACTUAL_CONTEXT_ID,
        FORECAST_ACTUAL_FACILITY_FILTER_ALL,
        FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
        FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
        NOMINATION_FORECAST_TABLE_NAME,
        cached_load_forecast_actual_tables,
        discover_dashboard_config,
        forecast_actual_bounded_scope_markdown,
        forecast_actual_comparison_figure,
        forecast_actual_comparison_frame,
        forecast_actual_empty_state_markdown,
        forecast_actual_facility_options,
        forecast_actual_gas_date_options,
        forecast_actual_kpi_frame,
        forecast_actual_source_system_options,
        forecast_actual_storage_frame,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_bounded_data_note_html,
        render_dashboard_context_panel,
        render_forecast_actual_context_links,
        render_kpi_cards_html,
        render_visual_empty_state_html,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        FACILITY_FLOW_STORAGE_TABLE_NAME,
        FORECAST_ACTUAL_CONTEXT_ID,
        FORECAST_ACTUAL_FACILITY_FILTER_ALL,
        FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
        FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
        NOMINATION_FORECAST_TABLE_NAME,
        cached_load_forecast_actual_tables,
        date,
        discover_dashboard_config,
        forecast_actual_bounded_scope_markdown,
        forecast_actual_comparison_figure,
        forecast_actual_comparison_frame,
        forecast_actual_empty_state_markdown,
        forecast_actual_facility_options,
        forecast_actual_gas_date_options,
        forecast_actual_kpi_frame,
        forecast_actual_source_system_options,
        forecast_actual_storage_frame,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_bounded_data_note_html,
        render_dashboard_context_panel,
        render_forecast_actual_context_links,
        render_kpi_cards_html,
        render_visual_empty_state_html,
    )


@app.cell
def _(
    FORECAST_ACTUAL_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_forecast_actual_context_links,
):
    mo.vstack(
        [
            mo.md("""
            # Forecast Vs Actual Flow And Storage

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators,
            analysts, and stakeholders use this dashboard to compare bounded
            nomination or demand forecast rows from
            `silver_gas_fact_nomination_forecast` with available actual
            facility flow/storage rows from
            `silver_gas_fact_facility_flow_storage`. Data scope is read-only
            bounded recent/sample Parquet data from the configured
            `silver.gas_model` bucket plus Marimo dashboard registry metadata.
            Freshness, source coverage, load timing, cache state, latest Gas
            Day, AWS sampled/recent-only preview policy, join coverage, and
            missing-source behavior come from the shared gas model loader and
            dashboard helpers. The dashboard joins only loaded rows sharing Gas
            Day, source facility, and source location identifiers; unmatched
            forecast or actual rows stay visible as designed states instead of
            notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel(FORECAST_ACTUAL_CONTEXT_ID)),
            mo.Html(render_forecast_actual_context_links()),
        ]
    )
    return


@app.cell
def _():
    forecast_actual_load_cache = {}
    return (forecast_actual_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_forecast_actual_tables,
    date,
    discover_dashboard_config,
    forecast_actual_load_cache,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    forecast_reference_date = date.today()
    forecast_actual_loads = cached_load_forecast_actual_tables(
        config,
        forecast_actual_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, forecast_actual_loads, forecast_reference_date


@app.cell
def _(
    config,
    forecast_actual_bounded_scope_markdown,
    forecast_actual_loads,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    mo.vstack(
        [
            mo.md(
                "## Data Health\n\n"
                + gas_table_load_status_message(forecast_actual_loads)
                + "\n\n"
                + forecast_actual_bounded_scope_markdown(config, forecast_actual_loads)
            ),
            mo.accordion(
                {
                    "Forecast-vs-actual read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(forecast_actual_loads),
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
    FORECAST_ACTUAL_FACILITY_FILTER_ALL,
    FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
    FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
    forecast_actual_facility_options,
    forecast_actual_gas_date_options,
    forecast_actual_loads,
    forecast_actual_source_system_options,
    mo,
):
    gas_date_filter = mo.ui.dropdown(
        options=forecast_actual_gas_date_options(forecast_actual_loads),
        value=FORECAST_ACTUAL_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    facility_filter = mo.ui.dropdown(
        options=forecast_actual_facility_options(forecast_actual_loads),
        value=FORECAST_ACTUAL_FACILITY_FILTER_ALL,
        searchable=True,
        label="Source facility",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=forecast_actual_source_system_options(forecast_actual_loads),
        value=FORECAST_ACTUAL_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            gas_date_filter,
            facility_filter,
            source_system_filter,
        ],
        gap=0.75,
    )
    return facility_filter, gas_date_filter, source_system_filter


@app.cell
def _(
    facility_filter,
    forecast_actual_empty_state_markdown,
    forecast_actual_comparison_figure,
    forecast_actual_kpi_frame,
    forecast_actual_loads,
    forecast_reference_date,
    gas_date_filter,
    mo,
    render_bounded_data_note_html,
    render_kpi_cards_html,
    render_visual_empty_state_html,
    source_system_filter,
):
    kpis = forecast_actual_kpi_frame(
        forecast_actual_loads,
        gas_date_filter.value,
        facility_filter.value,
        source_system_filter.value,
        as_of_date=forecast_reference_date,
    )
    comparison_figure = forecast_actual_comparison_figure(
        forecast_actual_loads,
        gas_date_filter.value,
        facility_filter.value,
        source_system_filter.value,
        as_of_date=forecast_reference_date,
        height=320,
    )
    comparison_has_data = len(comparison_figure.data) > 0
    if kpis.is_empty() and not comparison_has_data:
        forecast_actual_health_visual = mo.Html(
            render_visual_empty_state_html(
                title="No forecast-vs-actual comparison",
                detail=(
                    "No loaded forecast or actual rows match the current read "
                    "and filters; drilldown empty-state detail remains below."
                ),
                action="Refresh data or widen the current filters.",
                compact=True,
            )
        )
    else:
        if kpis.is_empty():
            kpi_view = mo.md(
                forecast_actual_empty_state_markdown(forecast_actual_loads)
            )
        else:
            kpi_view = mo.Html(
                render_kpi_cards_html(kpis, title="Forecast-vs-actual health KPIs")
            )
        comparison_visual_view = (
            mo.ui.plotly(comparison_figure)
            if comparison_has_data
            else mo.Html(
                render_visual_empty_state_html(
                    title="No demand comparison chart",
                    detail="The bounded read and filters do not contain comparable forecast or actual demand measures.",
                    action="Refresh data or widen the current filters.",
                    compact=True,
                )
            )
        )
        forecast_actual_health_visual = mo.vstack([kpi_view, comparison_visual_view])

    mo.vstack(
        [
            mo.md("""
            ## Forecast-Vs-Actual Health

            Matched groups share `gas_date`, `source_facility_id`, and
            `source_location_id` in the currently loaded bounded rows.
            """),
            forecast_actual_health_visual,
            mo.Html(
                render_bounded_data_note_html(
                    title="Visuals use the loaded bounded rows",
                    detail=(
                        "KPI cards and the demand comparison chart respect the "
                        "current filters, reference date, refresh state, cache "
                        "state, and bounded read policy shown above."
                    ),
                )
            ),
        ]
    )
    return


@app.cell
def _(
    FACILITY_FLOW_STORAGE_TABLE_NAME,
    NOMINATION_FORECAST_TABLE_NAME,
    config,
    forecast_reference_date,
    mo,
    pl,
):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Forecast table",
                "Actual table",
                "Forecast reference date",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"silver/gas_model/{NOMINATION_FORECAST_TABLE_NAME}",
                f"silver/gas_model/{FACILITY_FLOW_STORAGE_TABLE_NAME}",
                str(forecast_reference_date),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.accordion(
        {
            "Forecast-vs-actual read configuration": mo.ui.table(
                config_frame,
                selection=None,
            )
        },
        multiple=False,
    )
    return


@app.cell
def _(
    facility_filter,
    forecast_actual_comparison_frame,
    forecast_actual_empty_state_markdown,
    forecast_actual_loads,
    forecast_reference_date,
    gas_date_filter,
    mo,
    source_system_filter,
):
    comparison = forecast_actual_comparison_frame(
        forecast_actual_loads,
        gas_date_filter.value,
        facility_filter.value,
        source_system_filter.value,
        as_of_date=forecast_reference_date,
    )
    if comparison.is_empty():
        comparison_view = mo.md(
            forecast_actual_empty_state_markdown(forecast_actual_loads)
        )
    else:
        comparison_view = mo.ui.table(
            comparison,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Flow Forecast And Actual Comparison

            Actual `demand_tj`, `supply_tj`, `transfer_in_tj`, and
            `transfer_out_tj` values are converted to GJ before comparing with
            forecast measures. Unmatched bounded rows remain visible as
            forecast-only or actual-only groups.
            """),
            comparison_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    forecast_actual_empty_state_markdown,
    forecast_actual_loads,
    forecast_actual_storage_frame,
    forecast_reference_date,
    gas_date_filter,
    mo,
    source_system_filter,
):
    storage = forecast_actual_storage_frame(
        forecast_actual_loads,
        gas_date_filter.value,
        facility_filter.value,
        source_system_filter.value,
        as_of_date=forecast_reference_date,
    )
    if storage.is_empty():
        storage_view = mo.md(
            forecast_actual_empty_state_markdown(forecast_actual_loads)
        )
    else:
        storage_view = mo.ui.table(
            storage,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Actual Storage Side-By-Side

            Nomination forecasts do not carry equivalent storage forecast
            measures, so held-in-storage and cushion-gas storage are shown as
            actual observations with forecast coverage status for the same
            bounded Gas Day and facility/location group.
            """),
            storage_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
