import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        FACILITY_FLOW_STORAGE_CONTEXT_ID,
        FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
        FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
        FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
        FACILITY_FLOW_STORAGE_TABLE_NAME,
        cached_load_facility_flow_storage_table,
        discover_dashboard_config,
        facility_flow_storage_daily_frame,
        facility_flow_storage_empty_state_markdown,
        facility_flow_storage_facility_options,
        facility_flow_storage_gas_date_options,
        facility_flow_storage_kpi_frame,
        facility_flow_storage_observation_frame,
        facility_flow_storage_source_coverage_frame,
        facility_flow_storage_source_system_options,
        facility_flow_storage_summary_frame,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_facility_flow_storage_context_links,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        FACILITY_FLOW_STORAGE_CONTEXT_ID,
        FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
        FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
        FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
        FACILITY_FLOW_STORAGE_TABLE_NAME,
        cached_load_facility_flow_storage_table,
        discover_dashboard_config,
        facility_flow_storage_daily_frame,
        facility_flow_storage_empty_state_markdown,
        facility_flow_storage_facility_options,
        facility_flow_storage_gas_date_options,
        facility_flow_storage_kpi_frame,
        facility_flow_storage_observation_frame,
        facility_flow_storage_source_coverage_frame,
        facility_flow_storage_source_system_options,
        facility_flow_storage_summary_frame,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_facility_flow_storage_context_links,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("""
            # Facility Flow And Storage

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators,
            analysts, and stakeholders use this dashboard to inspect
            facility-level demand, supply, transfer, held-in-storage, and
            cushion-gas storage rows from
            `silver_gas_fact_facility_flow_storage`. Data scope is read-only
            bounded recent/sample Parquet data from the configured
            `silver.gas_model` bucket plus Marimo dashboard registry metadata
            for Facility, Flow, and Capacity context. Freshness, source
            coverage, load timing, cache state, latest Gas Day, bounded preview
            policy, and missing-source behavior come from the shared gas model
            loader and dashboard helpers; unavailable tables, empty tables,
            filter misses, and missing columns render as designed empty states
            instead of notebook tracebacks.
            """),
        ]
    )
    return


@app.cell
def _():
    facility_flow_storage_load_cache = {}
    return (facility_flow_storage_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_facility_flow_storage_table,
    discover_dashboard_config,
    facility_flow_storage_load_cache,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    facility_flow_storage_load = cached_load_facility_flow_storage_table(
        config,
        facility_flow_storage_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    facility_flow_storage_loads = [facility_flow_storage_load]
    return config, facility_flow_storage_load, facility_flow_storage_loads


@app.cell
def _(
    facility_flow_storage_loads,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    mo.vstack(
        [
            mo.md(
                "## Data Health\n\n"
                + gas_table_load_status_message(facility_flow_storage_loads)
            ),
            mo.accordion(
                {
                    "Facility flow/storage read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(facility_flow_storage_loads),
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
    FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
    FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
    FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
    facility_flow_storage_facility_options,
    facility_flow_storage_gas_date_options,
    facility_flow_storage_load,
    facility_flow_storage_source_system_options,
    mo,
):
    gas_date_filter = mo.ui.dropdown(
        options=facility_flow_storage_gas_date_options(facility_flow_storage_load),
        value=FACILITY_FLOW_STORAGE_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    facility_filter = mo.ui.dropdown(
        options=facility_flow_storage_facility_options(facility_flow_storage_load),
        value=FACILITY_FLOW_STORAGE_FACILITY_FILTER_ALL,
        searchable=True,
        label="Source facility",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=facility_flow_storage_source_system_options(facility_flow_storage_load),
        value=FACILITY_FLOW_STORAGE_SOURCE_SYSTEM_FILTER_ALL,
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
    facility_flow_storage_empty_state_markdown,
    facility_flow_storage_kpi_frame,
    facility_flow_storage_load,
    gas_date_filter,
    mo,
    source_system_filter,
):
    kpis = facility_flow_storage_kpi_frame(
        facility_flow_storage_load,
        gas_date_filter.value,
        facility_filter.value,
        source_system_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            facility_flow_storage_empty_state_markdown(facility_flow_storage_load)
        )
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Facility Flow And Storage Health"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    FACILITY_FLOW_STORAGE_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_facility_flow_storage_context_links,
):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(FACILITY_FLOW_STORAGE_CONTEXT_ID)),
            mo.Html(render_facility_flow_storage_context_links()),
        ]
    )
    return


@app.cell
def _(FACILITY_FLOW_STORAGE_TABLE_NAME, config, mo, pl):
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
                f"silver/gas_model/{FACILITY_FLOW_STORAGE_TABLE_NAME}",
                (
                    "facility.md, flow.md, capacity.md under "
                    "tools/gas-market-knowledge-base/generated/gold/glossary"
                ),
                (
                    "chunk-gbb-guide-nodes-facilities, "
                    "chunk-gbb-procedures-daily-flow-storage, "
                    "chunk-gbb-guide-flow-report, "
                    "chunk-gbb-procedures-capacity-outlooks"
                ),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.accordion(
        {
            "Facility flow/storage read configuration": mo.ui.table(
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
    facility_flow_storage_empty_state_markdown,
    facility_flow_storage_load,
    facility_flow_storage_source_coverage_frame,
    gas_date_filter,
    mo,
    source_system_filter,
):
    source_coverage = facility_flow_storage_source_coverage_frame(
        facility_flow_storage_load,
        gas_date_filter.value,
        facility_filter.value,
        source_system_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            facility_flow_storage_empty_state_markdown(facility_flow_storage_load)
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage is calculated from source system, source table, source
            facility, source location, Gas Day, source file, source update, and
            ingest fields in the loaded bounded rows.
            """),
            source_coverage_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    facility_flow_storage_empty_state_markdown,
    facility_flow_storage_load,
    facility_flow_storage_summary_frame,
    gas_date_filter,
    mo,
    source_system_filter,
):
    summary = facility_flow_storage_summary_frame(
        facility_flow_storage_load,
        gas_date_filter.value,
        facility_filter.value,
        source_system_filter.value,
    )
    if summary.is_empty():
        summary_view = mo.md(
            facility_flow_storage_empty_state_markdown(facility_flow_storage_load)
        )
    else:
        summary_view = mo.ui.table(summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Facility Summary

            This bounded view summarizes loaded rows by source system, source
            table, facility key, source facility, and source location.
            """),
            summary_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    facility_flow_storage_daily_frame,
    facility_flow_storage_empty_state_markdown,
    facility_flow_storage_load,
    gas_date_filter,
    mo,
    source_system_filter,
):
    daily = facility_flow_storage_daily_frame(
        facility_flow_storage_load,
        gas_date_filter.value,
        facility_filter.value,
        source_system_filter.value,
    )
    if daily.is_empty():
        daily_view = mo.md(
            facility_flow_storage_empty_state_markdown(facility_flow_storage_load)
        )
    else:
        daily_view = mo.ui.table(daily, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Recent Gas Day Totals

            Recent loaded rows are grouped by Gas Day after the shared bounded
            source read and active filters.
            """),
            daily_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    facility_flow_storage_empty_state_markdown,
    facility_flow_storage_load,
    facility_flow_storage_observation_frame,
    gas_date_filter,
    mo,
    source_system_filter,
):
    observations = facility_flow_storage_observation_frame(
        facility_flow_storage_load,
        gas_date_filter.value,
        facility_filter.value,
        source_system_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            facility_flow_storage_empty_state_markdown(facility_flow_storage_load)
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
            ## Recent Loaded Facility Flow And Storage Preview

            The preview is capped to the dashboard preview rows after the
            shared bounded source read. It keeps Facility, Gas Day, demand,
            supply, transfer, storage, source update, and ingest fields visible
            for each loaded row.
            """),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
