import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        STTM_MARKET_SETTLEMENT_COMPONENT_FILTER_ALL,
        STTM_MARKET_SETTLEMENT_GAS_DATE_FILTER_ALL,
        STTM_MARKET_SETTLEMENT_PERIOD_FILTER_ALL,
        STTM_MARKET_SETTLEMENT_STAGE_FILTER_ALL,
        cached_load_sttm_market_settlement_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_sttm_market_settlement_context_links,
        sttm_market_settlement_component_options,
        sttm_market_settlement_empty_state_markdown,
        sttm_market_settlement_gas_date_options,
        sttm_market_settlement_kpi_frame,
        sttm_market_settlement_observation_frame,
        sttm_market_settlement_period_options,
        sttm_market_settlement_source_coverage_frame,
        sttm_market_settlement_stage_options,
        sttm_market_settlement_summary_frame,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        STTM_MARKET_SETTLEMENT_COMPONENT_FILTER_ALL,
        STTM_MARKET_SETTLEMENT_GAS_DATE_FILTER_ALL,
        STTM_MARKET_SETTLEMENT_PERIOD_FILTER_ALL,
        STTM_MARKET_SETTLEMENT_STAGE_FILTER_ALL,
        cached_load_sttm_market_settlement_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_sttm_market_settlement_context_links,
        sttm_market_settlement_component_options,
        sttm_market_settlement_empty_state_markdown,
        sttm_market_settlement_gas_date_options,
        sttm_market_settlement_kpi_frame,
        sttm_market_settlement_observation_frame,
        sttm_market_settlement_period_options,
        sttm_market_settlement_source_coverage_frame,
        sttm_market_settlement_stage_options,
        sttm_market_settlement_summary_frame,
    )


@app.cell
def _(mo, render_dashboard_context_panel, render_sttm_market_settlement_context_links):
    mo.vstack(
        [
            mo.md("""
            # STTM Market Settlement

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect curated STTM market
            settlement rows in `silver.gas_model`, including settlement run,
            settlement stage, component, Hub / Zone, Facility, Gas Day,
            settlement-period, quantity, amount, source system, and accepted
            source identifier fields. Freshness, load timing, cache status, and
            bounded preview policy come from the shared gas model loader.
            Missing LocalStack/AWS data and filter matches with no rows render
            as designed empty states instead of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("sttm-market-settlement")),
            mo.Html(render_sttm_market_settlement_context_links()),
        ]
    )
    return


@app.cell
def _():
    sttm_market_settlement_load_cache = {}
    return (sttm_market_settlement_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_sttm_market_settlement_table,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
    sttm_market_settlement_load_cache,
):
    config = discover_dashboard_config()
    sttm_market_settlement_load = cached_load_sttm_market_settlement_table(
        config,
        sttm_market_settlement_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, sttm_market_settlement_load


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
    sttm_market_settlement_load,
):
    sttm_market_settlement_loads = [sttm_market_settlement_load]
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(sttm_market_settlement_loads)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "STTM market settlement read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(sttm_market_settlement_loads),
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
                "silver/gas_model/silver_gas_fact_sttm_market_settlement",
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
    STTM_MARKET_SETTLEMENT_COMPONENT_FILTER_ALL,
    STTM_MARKET_SETTLEMENT_GAS_DATE_FILTER_ALL,
    STTM_MARKET_SETTLEMENT_PERIOD_FILTER_ALL,
    STTM_MARKET_SETTLEMENT_STAGE_FILTER_ALL,
    mo,
    sttm_market_settlement_component_options,
    sttm_market_settlement_gas_date_options,
    sttm_market_settlement_load,
    sttm_market_settlement_period_options,
    sttm_market_settlement_stage_options,
):
    gas_date_filter = mo.ui.dropdown(
        options=sttm_market_settlement_gas_date_options(sttm_market_settlement_load),
        value=STTM_MARKET_SETTLEMENT_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    period_filter = mo.ui.dropdown(
        options=sttm_market_settlement_period_options(sttm_market_settlement_load),
        value=STTM_MARKET_SETTLEMENT_PERIOD_FILTER_ALL,
        searchable=True,
        label="Settlement period",
        full_width=True,
    )
    settlement_stage_filter = mo.ui.dropdown(
        options=sttm_market_settlement_stage_options(sttm_market_settlement_load),
        value=STTM_MARKET_SETTLEMENT_STAGE_FILTER_ALL,
        searchable=True,
        label="Settlement stage",
        full_width=True,
    )
    settlement_component_filter = mo.ui.dropdown(
        options=sttm_market_settlement_component_options(sttm_market_settlement_load),
        value=STTM_MARKET_SETTLEMENT_COMPONENT_FILTER_ALL,
        searchable=True,
        label="Component",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack(
                [
                    gas_date_filter,
                    period_filter,
                    settlement_stage_filter,
                    settlement_component_filter,
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return (
        gas_date_filter,
        period_filter,
        settlement_component_filter,
        settlement_stage_filter,
    )


@app.cell
def _(
    gas_date_filter,
    mo,
    period_filter,
    settlement_component_filter,
    settlement_stage_filter,
    sttm_market_settlement_empty_state_markdown,
    sttm_market_settlement_kpi_frame,
    sttm_market_settlement_load,
):
    kpis = sttm_market_settlement_kpi_frame(
        sttm_market_settlement_load,
        gas_date_filter.value,
        period_filter.value,
        settlement_stage_filter.value,
        settlement_component_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            sttm_market_settlement_empty_state_markdown(sttm_market_settlement_load)
        )
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## STTM Market Settlement Summary"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    period_filter,
    settlement_component_filter,
    settlement_stage_filter,
    sttm_market_settlement_empty_state_markdown,
    sttm_market_settlement_load,
    sttm_market_settlement_summary_frame,
):
    settlement_summary = sttm_market_settlement_summary_frame(
        sttm_market_settlement_load,
        gas_date_filter.value,
        period_filter.value,
        settlement_stage_filter.value,
        settlement_component_filter.value,
    )
    if settlement_summary.is_empty():
        settlement_summary_view = mo.md(
            sttm_market_settlement_empty_state_markdown(sttm_market_settlement_load)
        )
    else:
        settlement_summary_view = mo.ui.table(
            settlement_summary,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Settlement Run, Component, Hub, And Facility Summary

            This bounded/recent view groups STTM market settlement rows by
            settlement run, settlement stage, component, Hub / Zone, Facility,
            source report, and settlement period while retaining quantity and
            amount coverage.
            """),
            settlement_summary_view,
        ]
    )
    return


@app.cell
def _(
    gas_date_filter,
    mo,
    period_filter,
    settlement_component_filter,
    settlement_stage_filter,
    sttm_market_settlement_empty_state_markdown,
    sttm_market_settlement_load,
    sttm_market_settlement_source_coverage_frame,
):
    source_coverage = sttm_market_settlement_source_coverage_frame(
        sttm_market_settlement_load,
        gas_date_filter.value,
        period_filter.value,
        settlement_stage_filter.value,
        settlement_component_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            sttm_market_settlement_empty_state_markdown(sttm_market_settlement_load)
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
                            Coverage groups rows by source system, source table,
                            and source report, including settlement run, stage,
                            component, hub, facility, Gas Day, settlement
                            period, quantity, amount, source file, and accepted
                            source identifier coverage.
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
    gas_date_filter,
    mo,
    period_filter,
    settlement_component_filter,
    settlement_stage_filter,
    sttm_market_settlement_empty_state_markdown,
    sttm_market_settlement_load,
    sttm_market_settlement_observation_frame,
):
    observations = sttm_market_settlement_observation_frame(
        sttm_market_settlement_load,
        gas_date_filter.value,
        period_filter.value,
        settlement_stage_filter.value,
        settlement_component_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            sttm_market_settlement_empty_state_markdown(sttm_market_settlement_load)
        )
    else:
        observation_view = mo.ui.table(
            observations,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md(
                f"""
                ## Recent Loaded STTM Market Settlement Preview

                Gas Day: `{gas_date_filter.value}`. Settlement period:
                `{period_filter.value}`. Settlement stage:
                `{settlement_stage_filter.value}`. Component:
                `{settlement_component_filter.value}`. The preview is capped
                to the dashboard preview rows after the shared bounded source
                read.
                """
            ),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
