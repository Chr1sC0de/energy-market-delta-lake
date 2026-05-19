import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
        SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
        SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_schedule_run_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_schedule_run_context_links,
        schedule_run_empty_state_markdown,
        schedule_run_gas_date_options,
        schedule_run_kpi_frame,
        schedule_run_observation_frame,
        schedule_run_schedule_type_options,
        schedule_run_source_coverage_frame,
        schedule_run_source_system_options,
        schedule_run_timestamp_summary_frame,
        schedule_run_type_summary_frame,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
        SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
        SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_schedule_run_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_schedule_run_context_links,
        schedule_run_empty_state_markdown,
        schedule_run_gas_date_options,
        schedule_run_kpi_frame,
        schedule_run_observation_frame,
        schedule_run_schedule_type_options,
        schedule_run_source_coverage_frame,
        schedule_run_source_system_options,
        schedule_run_timestamp_summary_frame,
        schedule_run_type_summary_frame,
    )


@app.cell
def _(mo, render_dashboard_context_panel, render_schedule_run_context_links):
    mo.vstack(
        [
            mo.md("""
            # Gas Schedule Runs

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect curated gas schedule run
            rows from `silver.gas_model.silver_gas_fact_schedule_run`,
            including Gas Day, source system, schedule type, forecast demand
            version, transmission identifiers, schedule timestamps, and source
            coverage. Freshness, load timing, cache status, and bounded preview
            policy come from the shared gas model loader. Missing LocalStack/AWS
            data and filter matches with no rows render as designed empty
            states instead of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("gas-schedule-runs")),
            mo.Html(render_schedule_run_context_links()),
        ]
    )
    return


@app.cell
def _():
    schedule_run_load_cache = {}
    return (schedule_run_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_schedule_run_table,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
    schedule_run_load_cache,
):
    config = discover_dashboard_config()
    schedule_run_load = cached_load_schedule_run_table(
        config,
        schedule_run_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, schedule_run_load


@app.cell
def _(
    gas_table_load_status_frame, gas_table_load_status_message, mo, schedule_run_load
):
    schedule_run_loads = [schedule_run_load]
    data_health_view = mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(schedule_run_loads)}
                """
            ),
            mo.accordion(
                {
                    "Schedule run read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(schedule_run_loads),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    data_health_view
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
                "silver/gas_model/silver_gas_fact_schedule_run",
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
def _(
    SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
    SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
    SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
    mo,
    schedule_run_gas_date_options,
    schedule_run_load,
    schedule_run_schedule_type_options,
    schedule_run_source_system_options,
):
    gas_date_filter = mo.ui.dropdown(
        options=schedule_run_gas_date_options(schedule_run_load),
        value=SCHEDULE_RUN_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=schedule_run_source_system_options(schedule_run_load),
        value=SCHEDULE_RUN_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )
    schedule_type_filter = mo.ui.dropdown(
        options=schedule_run_schedule_type_options(schedule_run_load),
        value=SCHEDULE_RUN_SCHEDULE_TYPE_FILTER_ALL,
        searchable=True,
        label="Schedule type",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack(
                [gas_date_filter, source_system_filter, schedule_type_filter],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return gas_date_filter, schedule_type_filter, source_system_filter


@app.cell
def _(
    gas_date_filter,
    mo,
    schedule_run_empty_state_markdown,
    schedule_run_kpi_frame,
    schedule_run_load,
    schedule_type_filter,
    source_system_filter,
):
    kpis = schedule_run_kpi_frame(
        schedule_run_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(schedule_run_empty_state_markdown(schedule_run_load))
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Schedule Run Health"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    schedule_run_empty_state_markdown,
    schedule_run_load,
    schedule_run_type_summary_frame,
    schedule_type_filter,
    source_system_filter,
):
    type_summary = schedule_run_type_summary_frame(
        schedule_run_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if type_summary.is_empty():
        type_summary_view = mo.md(schedule_run_empty_state_markdown(schedule_run_load))
    else:
        type_summary_view = mo.ui.table(type_summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Schedule Type And Transmission Summary

            This sampled/recent-only view summarizes loaded schedule runs by
            source, `schedule_type_id`, forecast demand version, Gas Day
            coverage, transmission identifiers, creation, and approval timing.
            """),
            type_summary_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    schedule_run_empty_state_markdown,
    schedule_run_load,
    schedule_run_timestamp_summary_frame,
    schedule_type_filter,
    source_system_filter,
):
    timestamp_summary = schedule_run_timestamp_summary_frame(
        schedule_run_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if timestamp_summary.is_empty():
        timestamp_summary_view = mo.md(
            schedule_run_empty_state_markdown(schedule_run_load)
        )
    else:
        timestamp_summary_view = mo.ui.table(
            timestamp_summary,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md(
                f"""
                ## Timestamp Coverage

                Gas Day: `{gas_date_filter.value}`. Source system:
                `{source_system_filter.value}`. Schedule type:
                `{schedule_type_filter.value}`. Timestamp coverage is
                calculated only from loaded bounded rows.
                """
            ),
            timestamp_summary_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    schedule_run_empty_state_markdown,
    schedule_run_load,
    schedule_run_source_coverage_frame,
    schedule_type_filter,
    source_system_filter,
):
    source_coverage = schedule_run_source_coverage_frame(
        schedule_run_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            schedule_run_empty_state_markdown(schedule_run_load)
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage is calculated from source system, source table, Gas Day,
            schedule type, forecast demand version, source update, and ingest
            fields in the loaded bounded rows.
            """),
            source_coverage_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    schedule_run_empty_state_markdown,
    schedule_run_load,
    schedule_run_observation_frame,
    schedule_type_filter,
    source_system_filter,
):
    observations = schedule_run_observation_frame(
        schedule_run_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(schedule_run_empty_state_markdown(schedule_run_load))
    else:
        observation_view = mo.ui.table(
            observations,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Recent Loaded Schedule Run Preview

            The preview is capped to the dashboard preview rows after the shared
            bounded source read. It keeps schedule type, forecast demand
            version, transmission identifiers, and timestamp fields visible for
            each loaded row.
            """),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
