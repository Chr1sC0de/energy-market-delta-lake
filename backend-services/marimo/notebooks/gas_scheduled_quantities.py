import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        SCHEDULED_QUANTITY_GAS_DATE_FILTER_ALL,
        SCHEDULED_QUANTITY_SCHEDULE_TYPE_FILTER_ALL,
        SCHEDULED_QUANTITY_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_scheduled_quantity_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_scheduled_quantity_context_links,
        scheduled_quantity_empty_state_markdown,
        scheduled_quantity_gas_date_options,
        scheduled_quantity_kpi_frame,
        scheduled_quantity_observation_frame,
        scheduled_quantity_schedule_context_frame,
        scheduled_quantity_schedule_type_options,
        scheduled_quantity_source_coverage_frame,
        scheduled_quantity_source_point_frame,
        scheduled_quantity_source_system_options,
        scheduled_quantity_type_summary_frame,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        SCHEDULED_QUANTITY_GAS_DATE_FILTER_ALL,
        SCHEDULED_QUANTITY_SCHEDULE_TYPE_FILTER_ALL,
        SCHEDULED_QUANTITY_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_scheduled_quantity_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_scheduled_quantity_context_links,
        scheduled_quantity_empty_state_markdown,
        scheduled_quantity_gas_date_options,
        scheduled_quantity_kpi_frame,
        scheduled_quantity_observation_frame,
        scheduled_quantity_schedule_context_frame,
        scheduled_quantity_schedule_type_options,
        scheduled_quantity_source_coverage_frame,
        scheduled_quantity_source_point_frame,
        scheduled_quantity_source_system_options,
        scheduled_quantity_type_summary_frame,
    )


@app.cell
def _(mo, render_dashboard_context_panel, render_scheduled_quantity_context_links):
    mo.vstack(
        [
            mo.md("""
            # Gas Scheduled Quantities

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect scheduled quantity rows
            from `silver.gas_model.silver_gas_fact_scheduled_quantity`,
            including Gas Day, source system, schedule type, quantity type,
            source point, transmission identifiers, quantity, volume, amount,
            and source coverage. Freshness, load timing, cache status, and
            bounded preview policy come from the shared gas model loader.
            Missing LocalStack/AWS data and filter matches with no rows render
            as designed empty states instead of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("gas-scheduled-quantities")),
            mo.Html(render_scheduled_quantity_context_links()),
        ]
    )
    return


@app.cell
def _():
    scheduled_quantity_load_cache = {}
    return (scheduled_quantity_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_scheduled_quantity_table,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
    scheduled_quantity_load_cache,
):
    config = discover_dashboard_config()
    scheduled_quantity_load = cached_load_scheduled_quantity_table(
        config,
        scheduled_quantity_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, scheduled_quantity_load


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
    scheduled_quantity_load,
):
    scheduled_quantity_loads = [scheduled_quantity_load]
    data_health_view = mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(scheduled_quantity_loads)}
                """
            ),
            mo.accordion(
                {
                    "Scheduled quantity read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(scheduled_quantity_loads),
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
                "silver/gas_model/silver_gas_fact_scheduled_quantity",
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
    SCHEDULED_QUANTITY_GAS_DATE_FILTER_ALL,
    SCHEDULED_QUANTITY_SCHEDULE_TYPE_FILTER_ALL,
    SCHEDULED_QUANTITY_SOURCE_SYSTEM_FILTER_ALL,
    mo,
    scheduled_quantity_gas_date_options,
    scheduled_quantity_load,
    scheduled_quantity_schedule_type_options,
    scheduled_quantity_source_system_options,
):
    gas_date_filter = mo.ui.dropdown(
        options=scheduled_quantity_gas_date_options(scheduled_quantity_load),
        value=SCHEDULED_QUANTITY_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=scheduled_quantity_source_system_options(scheduled_quantity_load),
        value=SCHEDULED_QUANTITY_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )
    schedule_type_filter = mo.ui.dropdown(
        options=scheduled_quantity_schedule_type_options(scheduled_quantity_load),
        value=SCHEDULED_QUANTITY_SCHEDULE_TYPE_FILTER_ALL,
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
    scheduled_quantity_empty_state_markdown,
    scheduled_quantity_kpi_frame,
    scheduled_quantity_load,
    schedule_type_filter,
    source_system_filter,
):
    kpis = scheduled_quantity_kpi_frame(
        scheduled_quantity_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            scheduled_quantity_empty_state_markdown(scheduled_quantity_load)
        )
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Scheduled Quantity Health"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    scheduled_quantity_empty_state_markdown,
    scheduled_quantity_load,
    scheduled_quantity_type_summary_frame,
    schedule_type_filter,
    source_system_filter,
):
    type_summary = scheduled_quantity_type_summary_frame(
        scheduled_quantity_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if type_summary.is_empty():
        type_summary_view = mo.md(
            scheduled_quantity_empty_state_markdown(scheduled_quantity_load)
        )
    else:
        type_summary_view = mo.ui.table(
            type_summary,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Quantity Type And Schedule Type Summary

            This sampled/recent-only view summarizes loaded scheduled quantity
            rows by source, `quantity_type`, `schedule_type_id`, source point
            coverage, quantity, volume, amount, and Gas Day coverage.
            """),
            type_summary_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    scheduled_quantity_empty_state_markdown,
    scheduled_quantity_load,
    scheduled_quantity_source_point_frame,
    schedule_type_filter,
    source_system_filter,
):
    source_points = scheduled_quantity_source_point_frame(
        scheduled_quantity_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if source_points.is_empty():
        source_point_view = mo.md(
            scheduled_quantity_empty_state_markdown(scheduled_quantity_load)
        )
    else:
        source_point_view = mo.ui.table(
            source_points,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Source Point Quantities

            Source point summaries keep the physical source-qualified point
            visible next to schedule type, quantity, volume, and amount totals.
            """),
            source_point_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    scheduled_quantity_empty_state_markdown,
    scheduled_quantity_load,
    scheduled_quantity_schedule_context_frame,
    schedule_type_filter,
    source_system_filter,
):
    schedule_context = scheduled_quantity_schedule_context_frame(
        scheduled_quantity_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if schedule_context.is_empty():
        schedule_context_view = mo.md(
            scheduled_quantity_empty_state_markdown(scheduled_quantity_load)
        )
    else:
        schedule_context_view = mo.ui.table(
            schedule_context,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Schedule Run Link Context

            Scheduled quantity rows expose Gas Day, source system,
            `schedule_type_id`, and transmission identifiers where the source
            data provides them. Use these fields with the Schedule Runs
            dashboard for schedule-run context.
            """),
            schedule_context_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    scheduled_quantity_empty_state_markdown,
    scheduled_quantity_load,
    scheduled_quantity_source_coverage_frame,
    schedule_type_filter,
    source_system_filter,
):
    source_coverage = scheduled_quantity_source_coverage_frame(
        scheduled_quantity_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            scheduled_quantity_empty_state_markdown(scheduled_quantity_load)
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage is calculated from source system, source table, Gas Day,
            quantity type, schedule type, source point, source file, source
            identifier, source update, and ingest fields in the loaded bounded
            rows.
            """),
            source_coverage_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    scheduled_quantity_empty_state_markdown,
    scheduled_quantity_load,
    scheduled_quantity_observation_frame,
    schedule_type_filter,
    source_system_filter,
):
    observations = scheduled_quantity_observation_frame(
        scheduled_quantity_load,
        gas_date_filter.value,
        source_system_filter.value,
        schedule_type_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            scheduled_quantity_empty_state_markdown(scheduled_quantity_load)
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
            ## Recent Loaded Scheduled Quantity Preview

            The preview is capped to the dashboard preview rows after the shared
            bounded source read. It keeps quantity type, schedule type, source
            point, transmission, quantity, volume, amount, and source lineage
            visible for each loaded row.
            """),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
