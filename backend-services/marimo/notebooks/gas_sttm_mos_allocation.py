import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        STTM_MOS_ALLOCATION_CONTEXT_ID,
        STTM_MOS_ALLOCATION_FACILITY_FILTER_ALL,
        STTM_MOS_ALLOCATION_GAS_DATE_FILTER_ALL,
        STTM_MOS_ALLOCATION_HUB_FILTER_ALL,
        STTM_MOS_ALLOCATION_SOURCE_SYSTEM_FILTER_ALL,
        STTM_MOS_ALLOCATION_TABLE_SPECS,
        cached_load_sttm_mos_allocation_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        render_dashboard_context_panel,
        render_sttm_mos_allocation_context_links,
        sttm_allocation_limit_summary_frame,
        sttm_allocation_quantity_summary_frame,
        sttm_default_allocation_notice_summary_frame,
        sttm_mos_allocation_empty_state_markdown,
        sttm_mos_allocation_facility_options,
        sttm_mos_allocation_fact_summary_frame,
        sttm_mos_allocation_gas_date_options,
        sttm_mos_allocation_hub_options,
        sttm_mos_allocation_kpi_frame,
        sttm_mos_allocation_source_coverage_frame,
        sttm_mos_allocation_source_system_options,
        sttm_mos_stack_summary_frame,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        STTM_MOS_ALLOCATION_CONTEXT_ID,
        STTM_MOS_ALLOCATION_FACILITY_FILTER_ALL,
        STTM_MOS_ALLOCATION_GAS_DATE_FILTER_ALL,
        STTM_MOS_ALLOCATION_HUB_FILTER_ALL,
        STTM_MOS_ALLOCATION_SOURCE_SYSTEM_FILTER_ALL,
        STTM_MOS_ALLOCATION_TABLE_SPECS,
        cached_load_sttm_mos_allocation_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_sttm_mos_allocation_context_links,
        sttm_allocation_limit_summary_frame,
        sttm_allocation_quantity_summary_frame,
        sttm_default_allocation_notice_summary_frame,
        sttm_mos_allocation_empty_state_markdown,
        sttm_mos_allocation_facility_options,
        sttm_mos_allocation_fact_summary_frame,
        sttm_mos_allocation_gas_date_options,
        sttm_mos_allocation_hub_options,
        sttm_mos_allocation_kpi_frame,
        sttm_mos_allocation_source_coverage_frame,
        sttm_mos_allocation_source_system_options,
        sttm_mos_stack_summary_frame,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.md("""
            # STTM MOS And Allocation

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect curated STTM MOS stack,
            allocation quantities/limits, and default allocation notices in
            `silver.gas_model`. Scope covers the four STTM MOS/allocation facts,
            filterable by Gas Day, source system, Hub / Zone, and Facility.
            Freshness, load timing, cache status, and bounded-read policy come
            from the shared loader; missing data and no-match filters render as
            designed empty states instead of Python error output.
            """),
        ]
    )
    return


@app.cell
def _():
    sttm_mos_allocation_load_cache = {}
    return (sttm_mos_allocation_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_sttm_mos_allocation_tables,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
    sttm_mos_allocation_load_cache,
):
    config = discover_dashboard_config()
    sttm_mos_allocation_loads = cached_load_sttm_mos_allocation_tables(
        config,
        sttm_mos_allocation_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, sttm_mos_allocation_loads


@app.cell
def _(
    gas_table_load_status_frame,
    mo,
    sttm_mos_allocation_loads,
):
    available_table_count = sum(load.available for load in sttm_mos_allocation_loads)
    unavailable_table_count = sum(
        load.error is not None for load in sttm_mos_allocation_loads
    )
    cache_hit_count = sum(load.cache_hit for load in sttm_mos_allocation_loads)
    total_duration_seconds = sum(
        load.load_duration_seconds for load in sttm_mos_allocation_loads
    )
    row_limits = {
        load.row_limit
        for load in sttm_mos_allocation_loads
        if load.row_limit is not None
    }
    if len(sttm_mos_allocation_loads) == 0:
        read_policy = "No table reads requested"
    elif not row_limits:
        read_policy = "Full table scans enabled"
    elif len(row_limits) == 1:
        read_policy = f"Preview limited to {row_limits.pop()} rows per table"
    else:
        read_policy = "Mixed bounded preview row limits"

    mo.vstack(
        [
            mo.md(
                "## Data Health\n\n"
                f"**Tables**: {available_table_count} of "
                f"{len(sttm_mos_allocation_loads)} available; "
                f"**unavailable**: {unavailable_table_count}; "
                f"**load**: {total_duration_seconds:.2f} s; "
                f"**cache**: {cache_hit_count} hits; "
                f"**read policy**: {read_policy}."
            ),
            mo.accordion(
                {
                    "STTM MOS/allocation read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(sttm_mos_allocation_loads),
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
    STTM_MOS_ALLOCATION_FACILITY_FILTER_ALL,
    STTM_MOS_ALLOCATION_GAS_DATE_FILTER_ALL,
    STTM_MOS_ALLOCATION_HUB_FILTER_ALL,
    STTM_MOS_ALLOCATION_SOURCE_SYSTEM_FILTER_ALL,
    mo,
    sttm_mos_allocation_facility_options,
    sttm_mos_allocation_gas_date_options,
    sttm_mos_allocation_hub_options,
    sttm_mos_allocation_loads,
    sttm_mos_allocation_source_system_options,
):
    gas_date_filter = mo.ui.dropdown(
        options=sttm_mos_allocation_gas_date_options(sttm_mos_allocation_loads),
        value=STTM_MOS_ALLOCATION_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=sttm_mos_allocation_source_system_options(sttm_mos_allocation_loads),
        value=STTM_MOS_ALLOCATION_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )
    hub_filter = mo.ui.dropdown(
        options=sttm_mos_allocation_hub_options(sttm_mos_allocation_loads),
        value=STTM_MOS_ALLOCATION_HUB_FILTER_ALL,
        searchable=True,
        label="Hub / Zone",
        full_width=True,
    )
    facility_filter = mo.ui.dropdown(
        options=sttm_mos_allocation_facility_options(sttm_mos_allocation_loads),
        value=STTM_MOS_ALLOCATION_FACILITY_FILTER_ALL,
        searchable=True,
        label="Facility",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack([gas_date_filter, source_system_filter], gap=1),
            mo.hstack([hub_filter, facility_filter], gap=1),
        ],
        gap=0.5,
    )
    return facility_filter, gas_date_filter, hub_filter, source_system_filter


@app.cell
def _(
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    source_system_filter,
    sttm_mos_allocation_empty_state_markdown,
    sttm_mos_allocation_fact_summary_frame,
    sttm_mos_allocation_kpi_frame,
    sttm_mos_allocation_loads,
):
    kpis = sttm_mos_allocation_kpi_frame(
        sttm_mos_allocation_loads,
        gas_date_filter.value,
        source_system_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    fact_summary = sttm_mos_allocation_fact_summary_frame(
        sttm_mos_allocation_loads,
        gas_date_filter.value,
        source_system_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            sttm_mos_allocation_empty_state_markdown(sttm_mos_allocation_loads)
        )
    else:
        kpi_view = mo.ui.table(kpis, selection=None)
    if fact_summary.is_empty():
        fact_summary_view = mo.md(
            sttm_mos_allocation_empty_state_markdown(sttm_mos_allocation_loads)
        )
    else:
        fact_summary_view = mo.ui.table(fact_summary, selection=None)

    mo.vstack(
        [
            mo.md("## STTM MOS And Allocation Summary"),
            kpi_view,
            fact_summary_view,
        ]
    )
    return


@app.cell
def _(
    STTM_MOS_ALLOCATION_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_sttm_mos_allocation_context_links,
):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(STTM_MOS_ALLOCATION_CONTEXT_ID)),
            mo.Html(render_sttm_mos_allocation_context_links()),
        ]
    )
    return


@app.cell
def _(STTM_MOS_ALLOCATION_TABLE_SPECS, config, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet root",
                "MOS/allocation facts",
                "AWS endpoint",
                "AWS region",
                "Environment",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                ", ".join(spec.table_name for spec in STTM_MOS_ALLOCATION_TABLE_SPECS),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                config.development_environment,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.vstack(
        [
            mo.md("## Runtime Configuration"),
            mo.ui.table(config_frame, selection=None),
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    source_system_filter,
    sttm_mos_allocation_empty_state_markdown,
    sttm_mos_allocation_loads,
    sttm_mos_stack_summary_frame,
):
    mos_stack_summary = sttm_mos_stack_summary_frame(
        sttm_mos_allocation_loads,
        gas_date_filter.value,
        source_system_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if mos_stack_summary.is_empty():
        mos_stack_view = mo.md(
            sttm_mos_allocation_empty_state_markdown(sttm_mos_allocation_loads)
        )
    else:
        mos_stack_view = mo.ui.table(mos_stack_summary, selection=None, page_size=20)

    mo.vstack(
        [
            mo.md("""
            ## MOS Stack

            This bounded/recent view groups MOS stack rows by MOS stack context,
            settlement run, stack type, Hub / Zone, Facility, participant,
            source report, estimated maximum quantity, used step quantity, and
            step price coverage.
            """),
            mos_stack_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    source_system_filter,
    sttm_allocation_quantity_summary_frame,
    sttm_mos_allocation_empty_state_markdown,
    sttm_mos_allocation_loads,
):
    allocation_quantity_summary = sttm_allocation_quantity_summary_frame(
        sttm_mos_allocation_loads,
        gas_date_filter.value,
        source_system_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if allocation_quantity_summary.is_empty():
        allocation_quantity_view = mo.md(
            sttm_mos_allocation_empty_state_markdown(sttm_mos_allocation_loads)
        )
    else:
        allocation_quantity_view = mo.ui.table(
            allocation_quantity_summary,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Allocation Quantity

            This bounded/recent view groups STTM allocation quantity rows by
            allocation version, flow direction, allocation quality type, Hub /
            Zone, Facility, source report, and quantity including MOS.
            """),
            allocation_quantity_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    source_system_filter,
    sttm_allocation_limit_summary_frame,
    sttm_mos_allocation_empty_state_markdown,
    sttm_mos_allocation_loads,
):
    allocation_limit_summary = sttm_allocation_limit_summary_frame(
        sttm_mos_allocation_loads,
        gas_date_filter.value,
        source_system_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if allocation_limit_summary.is_empty():
        allocation_limit_view = mo.md(
            sttm_mos_allocation_empty_state_markdown(sttm_mos_allocation_loads)
        )
    else:
        allocation_limit_view = mo.ui.table(
            allocation_limit_summary,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Allocation Limits

            This bounded/recent view groups STTM allocation warning limits by
            Hub / Zone, Facility, source report, upper warning limit, lower
            warning limit, source report timestamp, and source update coverage.
            """),
            allocation_limit_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    source_system_filter,
    sttm_default_allocation_notice_summary_frame,
    sttm_mos_allocation_empty_state_markdown,
    sttm_mos_allocation_loads,
):
    default_notice_summary = sttm_default_allocation_notice_summary_frame(
        sttm_mos_allocation_loads,
        gas_date_filter.value,
        source_system_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if default_notice_summary.is_empty():
        default_notice_view = mo.md(
            sttm_mos_allocation_empty_state_markdown(sttm_mos_allocation_loads)
        )
    else:
        default_notice_view = mo.ui.table(
            default_notice_summary,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Default Allocation Notices

            This bounded/recent view groups STTM default allocation notices by
            notice identifier, Hub / Zone, Facility, source report, and notice
            message coverage.
            """),
            default_notice_view,
        ]
    )
    return


@app.cell
def _(
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    source_system_filter,
    sttm_mos_allocation_empty_state_markdown,
    sttm_mos_allocation_loads,
    sttm_mos_allocation_source_coverage_frame,
):
    source_coverage = sttm_mos_allocation_source_coverage_frame(
        sttm_mos_allocation_loads,
        gas_date_filter.value,
        source_system_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            sttm_mos_allocation_empty_state_markdown(sttm_mos_allocation_loads)
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("## Source Coverage"),
            mo.accordion(
                {
                    "Source coverage drilldown": mo.vstack(
                        [
                            mo.md("""
                            Coverage groups each MOS/allocation fact by source
                            system, source table, source report, Gas Day, Hub /
                            Zone, Facility, source file, and accepted source
                            identifier coverage.
                            """),
                            source_coverage_view,
                        ]
                    )
                },
                multiple=False,
                lazy=True,
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
