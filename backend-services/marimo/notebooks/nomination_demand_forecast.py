import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    from datetime import date

    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        NOMINATION_FORECAST_CONTEXT_ID,
        NOMINATION_FORECAST_FACILITY_FILTER_ALL,
        NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
        NOMINATION_FORECAST_LOCATION_FILTER_ALL,
        NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
        NOMINATION_FORECAST_TABLE_NAME,
        cached_load_nomination_forecast_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        nomination_forecast_daily_frame,
        nomination_forecast_empty_state_markdown,
        nomination_forecast_facility_options,
        nomination_forecast_gas_date_options,
        nomination_forecast_kpi_frame,
        nomination_forecast_location_options,
        nomination_forecast_observation_frame,
        nomination_forecast_source_coverage_frame,
        nomination_forecast_source_system_options,
        nomination_forecast_summary_frame,
        render_dashboard_context_panel,
        render_nomination_forecast_context_links,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        NOMINATION_FORECAST_CONTEXT_ID,
        NOMINATION_FORECAST_FACILITY_FILTER_ALL,
        NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
        NOMINATION_FORECAST_LOCATION_FILTER_ALL,
        NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
        NOMINATION_FORECAST_TABLE_NAME,
        cached_load_nomination_forecast_table,
        date,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        nomination_forecast_daily_frame,
        nomination_forecast_empty_state_markdown,
        nomination_forecast_facility_options,
        nomination_forecast_gas_date_options,
        nomination_forecast_kpi_frame,
        nomination_forecast_location_options,
        nomination_forecast_observation_frame,
        nomination_forecast_source_coverage_frame,
        nomination_forecast_source_system_options,
        nomination_forecast_summary_frame,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_nomination_forecast_context_links,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("""
            # Nomination And Demand Forecast

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators,
            analysts, and stakeholders use this dashboard to inspect nomination
            and demand forecast rows from
            `silver_gas_fact_nomination_forecast`, with Flow, Facility, and Gas
            Day context. Data scope is read-only bounded recent/sample Parquet
            data from the configured `silver.gas_model` bucket plus Marimo
            dashboard registry metadata. Freshness, source coverage, load
            timing, cache state, latest Gas Day, bounded preview policy,
            current/future forecast horizon, historical forecast labelling, and
            missing-source behavior come from the shared gas model loader and
            dashboard helpers; historical actuals are not loaded by this
            forecast-only dashboard, and unavailable tables, empty tables,
            filter misses, and missing columns render as designed empty states
            instead of notebook tracebacks.
            """),
        ]
    )
    return


@app.cell
def _():
    nomination_forecast_load_cache = {}
    return (nomination_forecast_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_nomination_forecast_table,
    date,
    discover_dashboard_config,
    nomination_forecast_load_cache,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    forecast_reference_date = date.today()
    nomination_forecast_load = cached_load_nomination_forecast_table(
        config,
        nomination_forecast_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    nomination_forecast_loads = [nomination_forecast_load]
    return (
        config,
        forecast_reference_date,
        nomination_forecast_load,
        nomination_forecast_loads,
    )


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
    nomination_forecast_loads,
):
    mo.vstack(
        [
            mo.md(
                "## Data Health\n\n"
                + gas_table_load_status_message(nomination_forecast_loads)
            ),
            mo.accordion(
                {
                    "Nomination forecast read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(nomination_forecast_loads),
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
    NOMINATION_FORECAST_FACILITY_FILTER_ALL,
    NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
    NOMINATION_FORECAST_LOCATION_FILTER_ALL,
    NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
    mo,
    nomination_forecast_facility_options,
    nomination_forecast_gas_date_options,
    nomination_forecast_load,
    nomination_forecast_location_options,
    nomination_forecast_source_system_options,
):
    gas_date_filter = mo.ui.dropdown(
        options=nomination_forecast_gas_date_options(nomination_forecast_load),
        value=NOMINATION_FORECAST_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=nomination_forecast_source_system_options(nomination_forecast_load),
        value=NOMINATION_FORECAST_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )
    facility_filter = mo.ui.dropdown(
        options=nomination_forecast_facility_options(nomination_forecast_load),
        value=NOMINATION_FORECAST_FACILITY_FILTER_ALL,
        searchable=True,
        label="Source facility",
        full_width=True,
    )
    location_filter = mo.ui.dropdown(
        options=nomination_forecast_location_options(nomination_forecast_load),
        value=NOMINATION_FORECAST_LOCATION_FILTER_ALL,
        searchable=True,
        label="Source location",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            gas_date_filter,
            source_system_filter,
            facility_filter,
            location_filter,
        ],
        gap=0.75,
    )
    return facility_filter, gas_date_filter, location_filter, source_system_filter


@app.cell
def _(
    facility_filter,
    forecast_reference_date,
    gas_date_filter,
    location_filter,
    mo,
    nomination_forecast_empty_state_markdown,
    nomination_forecast_kpi_frame,
    nomination_forecast_load,
    source_system_filter,
):
    kpis = nomination_forecast_kpi_frame(
        nomination_forecast_load,
        gas_date_filter.value,
        source_system_filter.value,
        facility_filter.value,
        location_filter.value,
        as_of_date=forecast_reference_date,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            nomination_forecast_empty_state_markdown(nomination_forecast_load)
        )
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Forecast Health

            Forecast horizon labels compare `gas_date` with the reference date
            captured when the dashboard loaded. Historical actuals are outside
            this forecast-only fact and are not mixed into these summaries.
            """),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    NOMINATION_FORECAST_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_nomination_forecast_context_links,
):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(NOMINATION_FORECAST_CONTEXT_ID)),
            mo.Html(render_nomination_forecast_context_links()),
        ]
    )
    return


@app.cell
def _(NOMINATION_FORECAST_TABLE_NAME, config, forecast_reference_date, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet table",
                "Forecast reference date",
                "Generated-gold paths",
                "Source chunk IDs",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"silver/gas_model/{NOMINATION_FORECAST_TABLE_NAME}",
                str(forecast_reference_date),
                (
                    "flow.md, facility.md, gas-day.md under "
                    "tools/gas-market-knowledge-base/generated/gold/glossary"
                ),
                (
                    "chunk-gbb-guide-flow-report, "
                    "chunk-gbb-procedures-scheduled-flow, "
                    "chunk-gbb-guide-nodes-facilities, "
                    "chunk-gbb-guide-gas-day"
                ),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.accordion(
        {
            "Nomination forecast read configuration": mo.ui.table(
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
    forecast_reference_date,
    gas_date_filter,
    location_filter,
    mo,
    nomination_forecast_empty_state_markdown,
    nomination_forecast_load,
    nomination_forecast_source_coverage_frame,
    source_system_filter,
):
    source_coverage = nomination_forecast_source_coverage_frame(
        nomination_forecast_load,
        gas_date_filter.value,
        source_system_filter.value,
        facility_filter.value,
        location_filter.value,
        as_of_date=forecast_reference_date,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            nomination_forecast_empty_state_markdown(nomination_forecast_load)
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage is calculated from source system, source table, forecast
            type/version, Gas Day, facility, location, source file, source
            update, and ingest fields in the loaded bounded rows.
            """),
            source_coverage_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    forecast_reference_date,
    gas_date_filter,
    location_filter,
    mo,
    nomination_forecast_empty_state_markdown,
    nomination_forecast_load,
    nomination_forecast_summary_frame,
    source_system_filter,
):
    summary = nomination_forecast_summary_frame(
        nomination_forecast_load,
        gas_date_filter.value,
        source_system_filter.value,
        facility_filter.value,
        location_filter.value,
        as_of_date=forecast_reference_date,
    )
    if summary.is_empty():
        summary_view = mo.md(
            nomination_forecast_empty_state_markdown(nomination_forecast_load)
        )
    else:
        summary_view = mo.ui.table(summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Forecast Type And Version Summary

            This bounded view summarizes loaded rows by `forecast_type`,
            `forecast_version`, and forecast horizon after active filters.
            """),
            summary_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    forecast_reference_date,
    gas_date_filter,
    location_filter,
    mo,
    nomination_forecast_daily_frame,
    nomination_forecast_empty_state_markdown,
    nomination_forecast_load,
    source_system_filter,
):
    daily = nomination_forecast_daily_frame(
        nomination_forecast_load,
        gas_date_filter.value,
        source_system_filter.value,
        facility_filter.value,
        location_filter.value,
        as_of_date=forecast_reference_date,
    )
    if daily.is_empty():
        daily_view = mo.md(
            nomination_forecast_empty_state_markdown(nomination_forecast_load)
        )
    else:
        daily_view = mo.ui.table(daily, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Recent Gas Day Forecast Totals

            Recent loaded rows are grouped by Gas Day and forecast horizon after
            the shared bounded source read and active filters.
            """),
            daily_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    forecast_reference_date,
    gas_date_filter,
    location_filter,
    mo,
    nomination_forecast_empty_state_markdown,
    nomination_forecast_load,
    nomination_forecast_observation_frame,
    source_system_filter,
):
    observations = nomination_forecast_observation_frame(
        nomination_forecast_load,
        gas_date_filter.value,
        source_system_filter.value,
        facility_filter.value,
        location_filter.value,
        as_of_date=forecast_reference_date,
    )
    if observations.is_empty():
        observation_view = mo.md(
            nomination_forecast_empty_state_markdown(nomination_forecast_load)
        )
    else:
        observation_view = mo.ui.table(
            observations,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Recent Loaded Nomination Forecast Preview

            The preview is capped to the dashboard preview rows after the
            shared bounded source read. It keeps forecast type/version, Gas Day,
            facility/location, forecast measures, source update, and ingest
            fields visible for each loaded row.
            """),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
