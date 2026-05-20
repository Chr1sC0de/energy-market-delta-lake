import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        CAPACITY_CONTEXT_ID,
        CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL,
        CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL,
        CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL,
        CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
        CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL,
        CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
        CAPACITY_OUTLOOK_TABLE_NAME,
        cached_load_capacity_outlook_table,
        capacity_outlook_capacity_type_options,
        capacity_outlook_date_range_options,
        capacity_outlook_direction_options,
        capacity_outlook_empty_state_markdown,
        capacity_outlook_facility_options,
        capacity_outlook_kpi_frame,
        capacity_outlook_observation_frame,
        capacity_outlook_source_coverage_frame,
        capacity_outlook_source_coverage_options,
        capacity_outlook_source_system_options,
        capacity_outlook_summary_frame,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_capacity_outlook_context_links,
        render_dashboard_context_panel,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        CAPACITY_CONTEXT_ID,
        CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL,
        CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL,
        CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL,
        CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
        CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL,
        CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
        CAPACITY_OUTLOOK_TABLE_NAME,
        cached_load_capacity_outlook_table,
        capacity_outlook_capacity_type_options,
        capacity_outlook_date_range_options,
        capacity_outlook_direction_options,
        capacity_outlook_empty_state_markdown,
        capacity_outlook_facility_options,
        capacity_outlook_kpi_frame,
        capacity_outlook_observation_frame,
        capacity_outlook_source_coverage_frame,
        capacity_outlook_source_coverage_options,
        capacity_outlook_source_system_options,
        capacity_outlook_summary_frame,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_capacity_outlook_context_links,
        render_dashboard_context_panel,
    )


@app.cell
def _(
    CAPACITY_CONTEXT_ID,
    mo,
    render_capacity_outlook_context_links,
    render_dashboard_context_panel,
):
    mo.vstack(
        [
            mo.md("""
            # Capacity Outlook

            **Dashboard brief**: **Dashboard intent**: Operational. Operators
            and analysts use this dashboard to inspect available capacity
            outlook coverage from `silver_gas_fact_capacity_outlook`, including
            short-term, medium-term, uncontracted, nameplate, and
            connection-point nameplate source coverage where the loaded rows
            expose those sources. Data scope is read-only bounded recent/sample
            Parquet data from the configured `silver.gas_model` bucket plus
            Marimo dashboard registry metadata for Capacity, Facility, Flow,
            Connection Point, and Gas Day context. Freshness, source coverage,
            load timing, cache state, row-limit policy, date-range visibility,
            and missing-source behavior come from the shared gas model loader
            and dashboard helpers; unavailable tables, empty tables, filter
            misses, and missing columns render as designed empty states instead
            of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel(CAPACITY_CONTEXT_ID)),
            mo.Html(render_capacity_outlook_context_links()),
        ]
    )
    return


@app.cell
def _():
    capacity_outlook_load_cache = {}
    return (capacity_outlook_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_capacity_outlook_table,
    capacity_outlook_load_cache,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    capacity_outlook_load = cached_load_capacity_outlook_table(
        config,
        capacity_outlook_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    capacity_outlook_loads = [capacity_outlook_load]
    return config, capacity_outlook_load, capacity_outlook_loads


@app.cell
def _(
    capacity_outlook_loads,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    mo.vstack(
        [
            mo.md(
                "## Data Health\n\n"
                + gas_table_load_status_message(capacity_outlook_loads)
            ),
            mo.accordion(
                {
                    "Capacity outlook read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(capacity_outlook_loads),
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
    CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL,
    CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL,
    CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL,
    CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
    CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL,
    CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
    capacity_outlook_capacity_type_options,
    capacity_outlook_date_range_options,
    capacity_outlook_direction_options,
    capacity_outlook_facility_options,
    capacity_outlook_load,
    capacity_outlook_source_coverage_options,
    capacity_outlook_source_system_options,
    mo,
):
    source_coverage_filter = mo.ui.dropdown(
        options=capacity_outlook_source_coverage_options(capacity_outlook_load),
        value=CAPACITY_OUTLOOK_SOURCE_COVERAGE_FILTER_ALL,
        searchable=True,
        label="Capacity source coverage",
        full_width=True,
    )
    date_range_filter = mo.ui.dropdown(
        options=capacity_outlook_date_range_options(capacity_outlook_load),
        value=CAPACITY_OUTLOOK_DATE_RANGE_FILTER_ALL,
        searchable=True,
        label="Date range",
        full_width=True,
    )
    capacity_type_filter = mo.ui.dropdown(
        options=capacity_outlook_capacity_type_options(capacity_outlook_load),
        value=CAPACITY_OUTLOOK_CAPACITY_TYPE_FILTER_ALL,
        searchable=True,
        label="Capacity type",
        full_width=True,
    )
    direction_filter = mo.ui.dropdown(
        options=capacity_outlook_direction_options(capacity_outlook_load),
        value=CAPACITY_OUTLOOK_DIRECTION_FILTER_ALL,
        searchable=True,
        label="Direction",
        full_width=True,
    )
    facility_filter = mo.ui.dropdown(
        options=capacity_outlook_facility_options(capacity_outlook_load),
        value=CAPACITY_OUTLOOK_FACILITY_FILTER_ALL,
        searchable=True,
        label="Source facility",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=capacity_outlook_source_system_options(capacity_outlook_load),
        value=CAPACITY_OUTLOOK_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            source_coverage_filter,
            date_range_filter,
            capacity_type_filter,
            direction_filter,
            facility_filter,
            source_system_filter,
        ],
        gap=0.75,
    )
    return (
        capacity_type_filter,
        date_range_filter,
        direction_filter,
        facility_filter,
        source_coverage_filter,
        source_system_filter,
    )


@app.cell
def _(
    capacity_outlook_empty_state_markdown,
    capacity_outlook_kpi_frame,
    capacity_outlook_load,
    capacity_type_filter,
    date_range_filter,
    direction_filter,
    facility_filter,
    mo,
    source_coverage_filter,
    source_system_filter,
):
    kpis = capacity_outlook_kpi_frame(
        capacity_outlook_load,
        date_range_filter.value,
        capacity_type_filter.value,
        direction_filter.value,
        facility_filter.value,
        source_coverage_filter.value,
        source_system_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(capacity_outlook_empty_state_markdown(capacity_outlook_load))
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Capacity Outlook Health"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(CAPACITY_OUTLOOK_TABLE_NAME, config, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet table",
                "Generated-gold paths",
                "Source chunk IDs",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"silver/gas_model/{CAPACITY_OUTLOOK_TABLE_NAME}",
                (
                    "capacity.md, facility.md, flow.md, connection-point.md, "
                    "gas-day.md under "
                    "tools/gas-market-knowledge-base/generated/gold/glossary"
                ),
                (
                    "chunk-gbb-procedures-capacity-outlooks, "
                    "chunk-gbb-guide-nameplate-capacity, "
                    "chunk-gbb-guide-connection-point-identifiers, "
                    "chunk-gbb-guide-flow-report, "
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
            "Capacity outlook read configuration": mo.ui.table(
                config_frame,
                selection=None,
            )
        },
        multiple=False,
    )
    return


@app.cell
def _(
    capacity_outlook_empty_state_markdown,
    capacity_outlook_load,
    capacity_outlook_source_coverage_frame,
    capacity_type_filter,
    date_range_filter,
    direction_filter,
    facility_filter,
    mo,
    source_coverage_filter,
    source_system_filter,
):
    source_coverage = capacity_outlook_source_coverage_frame(
        capacity_outlook_load,
        date_range_filter.value,
        capacity_type_filter.value,
        direction_filter.value,
        facility_filter.value,
        source_coverage_filter.value,
        source_system_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            capacity_outlook_empty_state_markdown(capacity_outlook_load)
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage is calculated from source system, source table, capacity
            source family, source facility, capacity type, direction, date
            range, capacity quantity, source update, and ingest fields in the
            loaded bounded rows.
            """),
            source_coverage_view,
        ]
    )
    return


@app.cell
def _(
    capacity_outlook_empty_state_markdown,
    capacity_outlook_load,
    capacity_outlook_summary_frame,
    capacity_type_filter,
    date_range_filter,
    direction_filter,
    facility_filter,
    mo,
    source_coverage_filter,
    source_system_filter,
):
    summary = capacity_outlook_summary_frame(
        capacity_outlook_load,
        date_range_filter.value,
        capacity_type_filter.value,
        direction_filter.value,
        facility_filter.value,
        source_coverage_filter.value,
        source_system_filter.value,
    )
    if summary.is_empty():
        summary_view = mo.md(
            capacity_outlook_empty_state_markdown(capacity_outlook_load)
        )
    else:
        summary_view = mo.ui.table(summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Capacity Summary

            This bounded view summarizes loaded rows by capacity source
            coverage, source system, source table, source facility, facility,
            capacity type, direction, and date range.
            """),
            summary_view,
        ]
    )
    return


@app.cell
def _(
    capacity_outlook_empty_state_markdown,
    capacity_outlook_load,
    capacity_outlook_observation_frame,
    capacity_type_filter,
    date_range_filter,
    direction_filter,
    facility_filter,
    mo,
    source_coverage_filter,
    source_system_filter,
):
    observations = capacity_outlook_observation_frame(
        capacity_outlook_load,
        date_range_filter.value,
        capacity_type_filter.value,
        direction_filter.value,
        facility_filter.value,
        source_coverage_filter.value,
        source_system_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            capacity_outlook_empty_state_markdown(capacity_outlook_load)
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
            ## Recent Loaded Capacity Outlook Preview

            The preview is capped to the dashboard preview rows after the
            shared bounded source read. It keeps capacity source coverage,
            date range, outlook month/year, source facility, facility,
            capacity type, direction, location identifiers, quantity,
            source update, and ingest fields visible for each loaded row.
            """),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
