import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
        SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
        SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_settlement_activity_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_kpi_cards_html,
        render_dashboard_context_panel,
        render_settlement_activity_context_links,
        render_visual_empty_state_html,
        settlement_activity_activity_type_options,
        settlement_activity_empty_state_markdown,
        settlement_activity_gas_date_options,
        settlement_activity_kpi_frame,
        settlement_activity_observation_frame,
        settlement_activity_source_coverage_frame,
        settlement_activity_source_system_options,
        settlement_activity_summary_frame,
        settlement_activity_summary_figure,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
        SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
        SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_settlement_activity_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_kpi_cards_html,
        render_dashboard_context_panel,
        render_settlement_activity_context_links,
        render_visual_empty_state_html,
        settlement_activity_activity_type_options,
        settlement_activity_empty_state_markdown,
        settlement_activity_gas_date_options,
        settlement_activity_kpi_frame,
        settlement_activity_observation_frame,
        settlement_activity_source_coverage_frame,
        settlement_activity_source_system_options,
        settlement_activity_summary_frame,
        settlement_activity_summary_figure,
    )


@app.cell
def _(mo):
    mo.md("""
    # Gas Settlement Activity

    **Dashboard brief**: **Dashboard intent**: Analytical. Operators and
    analysts use this dashboard to inspect curated settlement activity rows,
    including Settlement version, activity type, schedule, network,
    participant, amount, quantity, percentage, Gas Day, and source coverage
    fields. Freshness, load timing, cache status, and bounded preview policy
    come from the shared gas model loader. Missing LocalStack/AWS data and
    filter matches with no rows render as designed empty states instead of
    notebook tracebacks.
    """)
    return


@app.cell
def _():
    settlement_activity_load_cache = {}
    return (settlement_activity_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_settlement_activity_table,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
    settlement_activity_load_cache,
):
    config = discover_dashboard_config()
    settlement_activity_load = cached_load_settlement_activity_table(
        config,
        settlement_activity_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, settlement_activity_load


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
    settlement_activity_load,
):
    settlement_activity_loads = [settlement_activity_load]
    mo.vstack(
        [
            mo.md(
                "## Data Health\n\n"
                + gas_table_load_status_message(settlement_activity_loads)
            ),
            mo.accordion(
                {
                    "Settlement activity read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(settlement_activity_loads),
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
    SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
    SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
    SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
    mo,
    settlement_activity_activity_type_options,
    settlement_activity_gas_date_options,
    settlement_activity_load,
    settlement_activity_source_system_options,
):
    gas_date_filter = mo.ui.dropdown(
        options=settlement_activity_gas_date_options(settlement_activity_load),
        value=SETTLEMENT_ACTIVITY_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=settlement_activity_source_system_options(settlement_activity_load),
        value=SETTLEMENT_ACTIVITY_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )
    activity_type_filter = mo.ui.dropdown(
        options=settlement_activity_activity_type_options(settlement_activity_load),
        value=SETTLEMENT_ACTIVITY_ACTIVITY_TYPE_FILTER_ALL,
        searchable=True,
        label="Activity type",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            gas_date_filter,
            source_system_filter,
            activity_type_filter,
        ],
        gap=0.75,
    )
    return activity_type_filter, gas_date_filter, source_system_filter


@app.cell
def _(
    activity_type_filter,
    gas_date_filter,
    mo,
    render_kpi_cards_html,
    render_visual_empty_state_html,
    settlement_activity_empty_state_markdown,
    settlement_activity_kpi_frame,
    settlement_activity_load,
    settlement_activity_summary_figure,
    source_system_filter,
):
    kpis = settlement_activity_kpi_frame(
        settlement_activity_load,
        gas_date_filter.value,
        source_system_filter.value,
        activity_type_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            settlement_activity_empty_state_markdown(settlement_activity_load)
        )
        activity_visual = mo.Html(
            render_visual_empty_state_html(
                title="No settlement activity to chart",
                detail=(
                    "The current filters do not match loaded bounded settlement "
                    "activity rows."
                ),
            )
        )
    else:
        kpi_view = mo.Html(
            render_kpi_cards_html(kpis, title="Settlement activity health KPIs")
        )
        activity_visual = mo.ui.plotly(
            settlement_activity_summary_figure(
                settlement_activity_load,
                gas_date_filter.value,
                source_system_filter.value,
                activity_type_filter.value,
            )
        )

    mo.vstack(
        [
            mo.md("## Settlement Activity Health"),
            kpi_view,
            activity_visual,
        ]
    )
    return


@app.cell
def _(mo, render_dashboard_context_panel, render_settlement_activity_context_links):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel("settlement-context")),
            mo.Html(render_settlement_activity_context_links()),
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
                "silver/gas_model/silver_gas_fact_settlement_activity",
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
    activity_type_filter,
    gas_date_filter,
    mo,
    settlement_activity_empty_state_markdown,
    settlement_activity_load,
    settlement_activity_summary_frame,
    source_system_filter,
):
    summary = settlement_activity_summary_frame(
        settlement_activity_load,
        gas_date_filter.value,
        source_system_filter.value,
        activity_type_filter.value,
    )
    if summary.is_empty():
        summary_view = mo.md(
            settlement_activity_empty_state_markdown(settlement_activity_load)
        )
    else:
        summary_view = mo.ui.table(summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Activity And Settlement Version Summary

            This bounded view summarizes loaded settlement activity rows by
            source, `activity_type`, and `settlement_version_id`, with Gas Day,
            schedule, network, participant, amount, quantity, and percentage
            field coverage where available.
            """),
            summary_view,
        ]
    )
    return


@app.cell
def _(
    activity_type_filter,
    gas_date_filter,
    mo,
    settlement_activity_empty_state_markdown,
    settlement_activity_load,
    settlement_activity_source_coverage_frame,
    source_system_filter,
):
    source_coverage = settlement_activity_source_coverage_frame(
        settlement_activity_load,
        gas_date_filter.value,
        source_system_filter.value,
        activity_type_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            settlement_activity_empty_state_markdown(settlement_activity_load)
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
                            Coverage is calculated from source system, source
                            table, activity type, settlement version, schedule,
                            network, participant, source file, source update,
                            ingest, and populated measure fields in the loaded
                            bounded rows.
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


@app.cell
def _(
    activity_type_filter,
    gas_date_filter,
    mo,
    settlement_activity_empty_state_markdown,
    settlement_activity_load,
    settlement_activity_observation_frame,
    source_system_filter,
):
    observations = settlement_activity_observation_frame(
        settlement_activity_load,
        gas_date_filter.value,
        source_system_filter.value,
        activity_type_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            settlement_activity_empty_state_markdown(settlement_activity_load)
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
            ## Recent Loaded Settlement Activity Preview

            The preview is capped to the dashboard preview rows after the shared
            bounded source read. It keeps Settlement version, activity type,
            schedule, network, participant, amount, quantity, percentage, and
            source identifier fields visible for each loaded row.
            """),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
