import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        SYSTEM_NOTICE_CRITICAL_FILTER_CRITICAL,
        SYSTEM_NOTICE_CRITICAL_FILTER_OPTIONS,
        SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE_RECENT,
        SYSTEM_NOTICE_WINDOW_FILTER_OPTIONS,
        cached_load_system_notice_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        system_notice_empty_state_markdown,
        system_notice_kpi_frame,
        system_notice_source_coverage_frame,
        system_notice_summary_frame,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        SYSTEM_NOTICE_CRITICAL_FILTER_CRITICAL,
        SYSTEM_NOTICE_CRITICAL_FILTER_OPTIONS,
        SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE_RECENT,
        SYSTEM_NOTICE_WINDOW_FILTER_OPTIONS,
        cached_load_system_notice_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        system_notice_empty_state_markdown,
        system_notice_kpi_frame,
        system_notice_source_coverage_frame,
        system_notice_summary_frame,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Gas System Notices

            **Dashboard brief**: **Dashboard intent**: Operational. Operators
            and analysts use this dashboard to review curated gas system
            notices, critical flags, active windows, messages, URL paths, and
            source coverage from
            `silver.gas_model.silver_gas_fact_system_notice`. Freshness,
            load timing, cache status, and bounded preview policy come from the
            shared gas model loader. Missing LocalStack/AWS data and filter
            matches with no notices render as designed empty states instead of
            notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("gas-system-notices")),
        ]
    )
    return


@app.cell
def _():
    system_notice_load_cache = {}
    return (system_notice_load_cache,)


@app.cell
def _(
    SYSTEM_NOTICE_CRITICAL_FILTER_CRITICAL,
    SYSTEM_NOTICE_CRITICAL_FILTER_OPTIONS,
    SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE_RECENT,
    SYSTEM_NOTICE_WINDOW_FILTER_OPTIONS,
    mo,
):
    refresh_data_button = mo.ui.button(
        label="Refresh data",
        value=0,
        on_click=lambda value: value + 1,
    )
    critical_filter = mo.ui.radio(
        options=SYSTEM_NOTICE_CRITICAL_FILTER_OPTIONS,
        value=SYSTEM_NOTICE_CRITICAL_FILTER_CRITICAL,
        label="Critical status",
        inline=True,
    )
    window_filter = mo.ui.radio(
        options=SYSTEM_NOTICE_WINDOW_FILTER_OPTIONS,
        value=SYSTEM_NOTICE_WINDOW_FILTER_ACTIVE_RECENT,
        label="Notice window",
        inline=True,
    )

    mo.vstack(
        [
            mo.hstack([refresh_data_button], justify="start"),
            critical_filter,
            window_filter,
        ],
        gap=0.5,
    )
    return critical_filter, refresh_data_button, window_filter


@app.cell
def _(
    cached_load_system_notice_table,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
    system_notice_load_cache,
):
    config = discover_dashboard_config()
    system_notice_load = cached_load_system_notice_table(
        config,
        system_notice_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, system_notice_load


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
    system_notice_load,
):
    notice_loads = [system_notice_load]
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(notice_loads)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "System notice read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(notice_loads),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(config, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet table",
                "AWS endpoint",
                "AWS region",
                "Environment",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                "silver/gas_model/silver_gas_fact_system_notice",
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                config.development_environment,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.ui.table(config_frame, selection=None)
    return


@app.cell
def _(mo, system_notice_kpi_frame, system_notice_load):
    kpis = system_notice_kpi_frame(system_notice_load)
    if kpis.is_empty():
        kpi_view = mo.callout(
            mo.md("System notice KPIs are unavailable until notice data loads."),
            kind="neutral",
        )
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Notice Summary"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    critical_filter,
    mo,
    system_notice_empty_state_markdown,
    system_notice_load,
    system_notice_summary_frame,
    window_filter,
):
    notice_rows = system_notice_summary_frame(
        system_notice_load,
        critical_filter.value,
        window_filter.value,
    )
    if notice_rows.is_empty():
        notice_table_view = mo.callout(
            mo.md(system_notice_empty_state_markdown(system_notice_load)),
            kind="neutral",
        )
    else:
        notice_table_view = mo.ui.table(
            notice_rows,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md(
                f"""
                ## Filtered Notices

                Critical status: `{critical_filter.value}`. Notice window:
                `{window_filter.value}`. The table is capped to the dashboard
                preview rows after the shared bounded source read.
                """
            ),
            notice_table_view,
        ]
    )
    return


@app.cell
def _(
    mo,
    system_notice_empty_state_markdown,
    system_notice_load,
    system_notice_source_coverage_frame,
):
    source_coverage = system_notice_source_coverage_frame(system_notice_load)
    if source_coverage.is_empty():
        source_coverage_view = mo.callout(
            mo.md(system_notice_empty_state_markdown(system_notice_load)),
            kind="neutral",
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage groups notices by `source_system` and `source_table`, with
            critical and active counts for the currently loaded rows.
            """),
            source_coverage_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
