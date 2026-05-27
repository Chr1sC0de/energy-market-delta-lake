import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
        LINEPACK_CONTEXT_ID,
        LINEPACK_FACILITY_FILTER_ALL,
        LINEPACK_GAS_DATE_FILTER_ALL,
        LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
        LINEPACK_TABLE_NAME,
        LINEPACK_ZONE_FILTER_ALL,
        cached_load_linepack_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        linepack_adequacy_flag_options,
        linepack_empty_state_markdown,
        linepack_facility_options,
        linepack_gas_date_options,
        linepack_kpi_frame,
        linepack_observation_frame,
        linepack_source_coverage_frame,
        linepack_source_system_options,
        linepack_summary_frame,
        linepack_zone_options,
        render_dashboard_context_panel,
        render_linepack_context_links,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
        LINEPACK_CONTEXT_ID,
        LINEPACK_FACILITY_FILTER_ALL,
        LINEPACK_GAS_DATE_FILTER_ALL,
        LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
        LINEPACK_TABLE_NAME,
        LINEPACK_ZONE_FILTER_ALL,
        cached_load_linepack_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        linepack_adequacy_flag_options,
        linepack_empty_state_markdown,
        linepack_facility_options,
        linepack_gas_date_options,
        linepack_kpi_frame,
        linepack_observation_frame,
        linepack_source_coverage_frame,
        linepack_source_system_options,
        linepack_summary_frame,
        linepack_zone_options,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_linepack_context_links,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("""
            # Linepack Adequacy

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators,
            analysts, and stakeholders use this dashboard to inspect bounded
            recent/sample linepack observations from
            `silver_gas_fact_linepack`, including linepack quantity, adequacy
            flag, adequacy description, facility, zone, source-system, and
            source-table coverage where present. Data scope is read-only
            bounded Parquet data from the configured `silver.gas_model` bucket
            plus Marimo dashboard registry metadata for Linepack, Flow,
            Capacity, and MOS context. Freshness, row coverage, load timing,
            cache state, bounded preview policy, and missing-source behavior
            come from the shared gas model loader and dashboard helpers;
            unavailable tables, empty tables, filter misses, and missing
            columns render as designed empty states instead of notebook
            tracebacks.
            """),
        ]
    )
    return


@app.cell
def _():
    linepack_load_cache = {}
    return (linepack_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_linepack_table,
    discover_dashboard_config,
    linepack_load_cache,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    linepack_load = cached_load_linepack_table(
        config,
        linepack_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    linepack_loads = [linepack_load]
    return config, linepack_load, linepack_loads


@app.cell
def _(gas_table_load_status_frame, gas_table_load_status_message, linepack_loads, mo):
    mo.vstack(
        [
            mo.md("## Data Health\n\n" + gas_table_load_status_message(linepack_loads)),
            mo.accordion(
                {
                    "Linepack read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(linepack_loads),
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
    LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
    LINEPACK_FACILITY_FILTER_ALL,
    LINEPACK_GAS_DATE_FILTER_ALL,
    LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
    LINEPACK_ZONE_FILTER_ALL,
    linepack_adequacy_flag_options,
    linepack_facility_options,
    linepack_gas_date_options,
    linepack_load,
    linepack_source_system_options,
    linepack_zone_options,
    mo,
):
    gas_date_filter = mo.ui.dropdown(
        options=linepack_gas_date_options(linepack_load),
        value=LINEPACK_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    facility_filter = mo.ui.dropdown(
        options=linepack_facility_options(linepack_load),
        value=LINEPACK_FACILITY_FILTER_ALL,
        searchable=True,
        label="Source facility",
        full_width=True,
    )
    zone_filter = mo.ui.dropdown(
        options=linepack_zone_options(linepack_load),
        value=LINEPACK_ZONE_FILTER_ALL,
        searchable=True,
        label="Zone",
        full_width=True,
    )
    adequacy_flag_filter = mo.ui.dropdown(
        options=linepack_adequacy_flag_options(linepack_load),
        value=LINEPACK_ADEQUACY_FLAG_FILTER_ALL,
        searchable=True,
        label="Adequacy flag",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=linepack_source_system_options(linepack_load),
        value=LINEPACK_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            gas_date_filter,
            facility_filter,
            zone_filter,
            adequacy_flag_filter,
            source_system_filter,
        ],
        gap=0.75,
    )
    return (
        adequacy_flag_filter,
        facility_filter,
        gas_date_filter,
        source_system_filter,
        zone_filter,
    )


@app.cell
def _(
    adequacy_flag_filter,
    facility_filter,
    gas_date_filter,
    linepack_empty_state_markdown,
    linepack_kpi_frame,
    linepack_load,
    mo,
    source_system_filter,
    zone_filter,
):
    kpis = linepack_kpi_frame(
        linepack_load,
        gas_date_filter.value,
        facility_filter.value,
        zone_filter.value,
        adequacy_flag_filter.value,
        source_system_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(linepack_empty_state_markdown(linepack_load))
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Linepack Adequacy Health"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    LINEPACK_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_linepack_context_links,
):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(LINEPACK_CONTEXT_ID)),
            mo.Html(render_linepack_context_links()),
        ]
    )
    return


@app.cell
def _(LINEPACK_TABLE_NAME, config, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet table",
                "Market context IDs",
                "Source chunk IDs",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"silver/gas_model/{LINEPACK_TABLE_NAME}",
                ("glossary:linepack, glossary:flow, glossary:capacity, glossary:mos"),
                (
                    "chunk-sttm-procedures-definitions, "
                    "chunk-gbb-procedures-linepack-capacity-adequacy, "
                    "chunk-gbb-guide-flow-report, "
                    "chunk-gbb-procedures-capacity-outlooks, "
                    "chunk-sttm-procedures-mos-estimates"
                ),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.accordion(
        {
            "Linepack read configuration": mo.ui.table(
                config_frame,
                selection=None,
            )
        },
        multiple=False,
    )
    return


@app.cell
def _(
    adequacy_flag_filter,
    facility_filter,
    gas_date_filter,
    linepack_empty_state_markdown,
    linepack_load,
    linepack_source_coverage_frame,
    mo,
    source_system_filter,
    zone_filter,
):
    source_coverage = linepack_source_coverage_frame(
        linepack_load,
        gas_date_filter.value,
        facility_filter.value,
        zone_filter.value,
        adequacy_flag_filter.value,
        source_system_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(linepack_empty_state_markdown(linepack_load))
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage is calculated from source system, source table, facility,
            zone, Gas Day, linepack quantity, adequacy fields, source file,
            source update, and ingest fields in the loaded bounded rows.
            """),
            source_coverage_view,
        ]
    )
    return


@app.cell
def _(
    adequacy_flag_filter,
    facility_filter,
    gas_date_filter,
    linepack_empty_state_markdown,
    linepack_load,
    linepack_summary_frame,
    mo,
    source_system_filter,
    zone_filter,
):
    summary = linepack_summary_frame(
        linepack_load,
        gas_date_filter.value,
        facility_filter.value,
        zone_filter.value,
        adequacy_flag_filter.value,
        source_system_filter.value,
    )
    if summary.is_empty():
        summary_view = mo.md(linepack_empty_state_markdown(linepack_load))
    else:
        summary_view = mo.ui.table(summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Facility, Zone, And Adequacy Summary

            This bounded view summarizes loaded linepack quantity and adequacy
            state by source, facility, zone, and adequacy description after
            active filters.
            """),
            summary_view,
        ]
    )
    return


@app.cell
def _(
    adequacy_flag_filter,
    facility_filter,
    gas_date_filter,
    linepack_empty_state_markdown,
    linepack_load,
    linepack_observation_frame,
    mo,
    source_system_filter,
    zone_filter,
):
    observations = linepack_observation_frame(
        linepack_load,
        gas_date_filter.value,
        facility_filter.value,
        zone_filter.value,
        adequacy_flag_filter.value,
        source_system_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(linepack_empty_state_markdown(linepack_load))
    else:
        observation_view = mo.ui.table(
            observations,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Recent Loaded Linepack Preview

            The preview is capped to the dashboard preview rows after the
            shared bounded source read. It keeps Gas Day, observation time,
            facility, zone, linepack quantity, adequacy state, source update,
            and ingest fields visible for each loaded row.
            """),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
