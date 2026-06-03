import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
        CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
        CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_customer_transfer_table,
        customer_transfer_daily_frame,
        customer_transfer_empty_state_markdown,
        customer_transfer_gas_date_options,
        customer_transfer_kpi_frame,
        customer_transfer_market_code_options,
        customer_transfer_observation_frame,
        customer_transfer_source_coverage_frame,
        customer_transfer_source_system_options,
        customer_transfer_summary_frame,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_customer_transfer_context_links,
        render_dashboard_context_panel,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
        CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
        CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_customer_transfer_table,
        customer_transfer_daily_frame,
        customer_transfer_empty_state_markdown,
        customer_transfer_gas_date_options,
        customer_transfer_kpi_frame,
        customer_transfer_market_code_options,
        customer_transfer_observation_frame,
        customer_transfer_source_coverage_frame,
        customer_transfer_source_system_options,
        customer_transfer_summary_frame,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_customer_transfer_context_links,
        render_dashboard_context_panel,
    )


@app.cell
def _(mo):
    mo.md("""
    # Customer Transfer And Retail Activity

    **Dashboard brief**: **Dashboard intent**: Analytical. Operators and
    analysts use this dashboard to inspect the curated customer transfer fact in
    `silver.gas_model`, including transfers lodged, completed, cancelled,
    internal transfers, greenfields received, market code, Gas Day, source
    table, and ingest fields. Freshness, load timing, cache status, and bounded
    preview policy come from the shared gas model loader. Missing
    LocalStack/AWS data and filter matches with no rows render as designed
    empty states instead of notebook tracebacks.
    """)
    return


@app.cell
def _():
    customer_transfer_load_cache = {}
    return (customer_transfer_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_customer_transfer_table,
    customer_transfer_load_cache,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    customer_transfer_load = cached_load_customer_transfer_table(
        config,
        customer_transfer_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, customer_transfer_load


@app.cell
def _(
    customer_transfer_load,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    customer_transfer_loads = [customer_transfer_load]
    mo.vstack(
        [
            mo.md(
                "## Data Health\n\n"
                + gas_table_load_status_message(customer_transfer_loads)
            ),
            mo.accordion(
                {
                    "Customer transfer read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(customer_transfer_loads),
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
    CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
    CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
    CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
    customer_transfer_gas_date_options,
    customer_transfer_load,
    customer_transfer_market_code_options,
    customer_transfer_source_system_options,
    mo,
):
    gas_date_filter = mo.ui.dropdown(
        options=customer_transfer_gas_date_options(customer_transfer_load),
        value=CUSTOMER_TRANSFER_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    market_code_filter = mo.ui.dropdown(
        options=customer_transfer_market_code_options(customer_transfer_load),
        value=CUSTOMER_TRANSFER_MARKET_CODE_FILTER_ALL,
        searchable=True,
        label="Market code",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=customer_transfer_source_system_options(customer_transfer_load),
        value=CUSTOMER_TRANSFER_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            gas_date_filter,
            market_code_filter,
            source_system_filter,
        ],
        gap=0.75,
    )
    return gas_date_filter, market_code_filter, source_system_filter


@app.cell
def _(
    customer_transfer_empty_state_markdown,
    customer_transfer_kpi_frame,
    customer_transfer_load,
    gas_date_filter,
    market_code_filter,
    mo,
    source_system_filter,
):
    kpis = customer_transfer_kpi_frame(
        customer_transfer_load,
        gas_date_filter.value,
        market_code_filter.value,
        source_system_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(customer_transfer_empty_state_markdown(customer_transfer_load))
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Customer Transfer Health"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(mo, render_customer_transfer_context_links, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel("gas-customer-transfer-activity")),
            mo.Html(render_customer_transfer_context_links()),
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
                "silver/gas_model/silver_gas_fact_customer_transfer",
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
    customer_transfer_empty_state_markdown,
    customer_transfer_load,
    customer_transfer_summary_frame,
    gas_date_filter,
    market_code_filter,
    mo,
    source_system_filter,
):
    summary = customer_transfer_summary_frame(
        customer_transfer_load,
        gas_date_filter.value,
        market_code_filter.value,
        source_system_filter.value,
    )
    if summary.is_empty():
        summary_view = mo.md(
            customer_transfer_empty_state_markdown(customer_transfer_load)
        )
    else:
        summary_view = mo.ui.table(summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Market Code Summary

            This bounded view summarizes loaded customer transfer rows by
            `market_code`, source system, and source table, including lodged,
            completed, cancelled, internal transfer, greenfield, Gas Day, and
            ingest fields.
            """),
            summary_view,
        ]
    )
    return


@app.cell
def _(
    customer_transfer_daily_frame,
    customer_transfer_empty_state_markdown,
    customer_transfer_load,
    gas_date_filter,
    market_code_filter,
    mo,
    source_system_filter,
):
    daily = customer_transfer_daily_frame(
        customer_transfer_load,
        gas_date_filter.value,
        market_code_filter.value,
        source_system_filter.value,
    )
    if daily.is_empty():
        daily_view = mo.md(
            customer_transfer_empty_state_markdown(customer_transfer_load)
        )
    else:
        daily_view = mo.ui.table(daily, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Gas Day Activity

            Recent loaded rows are grouped by Gas Day and `market_code` after
            the shared bounded source read and active filters.
            """),
            daily_view,
        ]
    )
    return


@app.cell
def _(
    customer_transfer_empty_state_markdown,
    customer_transfer_load,
    customer_transfer_source_coverage_frame,
    gas_date_filter,
    market_code_filter,
    mo,
    source_system_filter,
):
    source_coverage = customer_transfer_source_coverage_frame(
        customer_transfer_load,
        gas_date_filter.value,
        market_code_filter.value,
        source_system_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            customer_transfer_empty_state_markdown(customer_transfer_load)
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
                            table, `market_code`, Gas Day, source file, source
                            identifier, and ingest fields in the loaded bounded
                            rows.
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
    customer_transfer_empty_state_markdown,
    customer_transfer_load,
    customer_transfer_observation_frame,
    gas_date_filter,
    market_code_filter,
    mo,
    source_system_filter,
):
    observations = customer_transfer_observation_frame(
        customer_transfer_load,
        gas_date_filter.value,
        market_code_filter.value,
        source_system_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            customer_transfer_empty_state_markdown(customer_transfer_load)
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
            ## Recent Loaded Customer Transfer Preview

            The preview is capped to the dashboard preview rows after the
            shared bounded source read. It keeps market code, Gas Day, lodged,
            completed, cancelled, internal transfer, greenfield, and source
            identifier fields visible for each loaded row.
            """),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
