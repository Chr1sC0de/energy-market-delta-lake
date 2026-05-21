import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        MARKET_PRICE_GAS_DATE_FILTER_ALL,
        MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
        MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
        MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
        cached_load_market_price_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        market_price_bounded_scope_markdown,
        market_price_empty_state_markdown,
        market_price_exception_frame,
        market_price_gas_date_options,
        market_price_kpi_frame,
        market_price_observation_frame,
        market_price_price_type_options,
        market_price_source_system_options,
        market_price_source_table_options,
        market_price_trend_diagnostic_frame,
        market_price_trend_frame,
        market_price_type_summary_frame,
        render_dashboard_context_panel,
        render_market_price_context_links,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        MARKET_PRICE_GAS_DATE_FILTER_ALL,
        MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
        MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
        MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
        cached_load_market_price_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        market_price_bounded_scope_markdown,
        market_price_empty_state_markdown,
        market_price_exception_frame,
        market_price_gas_date_options,
        market_price_kpi_frame,
        market_price_observation_frame,
        market_price_price_type_options,
        market_price_source_system_options,
        market_price_source_table_options,
        market_price_trend_diagnostic_frame,
        market_price_trend_frame,
        market_price_type_summary_frame,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_market_price_context_links,
    )


@app.cell
def _(mo, render_dashboard_context_panel, render_market_price_context_links):
    mo.vstack(
        [
            mo.md("""
            # Gas Market Prices

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect curated gas market price
            observations from
            `silver.gas_model.silver_gas_fact_market_price`, including
            `price_type`, `source_system`, `source_table`, `gas_date`,
            Schedule context fields, populated price measures, bounded trend
            diagnostics, and recent/sample exception candidates. Freshness,
            load timing, cache status, and bounded preview policy come from
            the shared gas model loader. Missing LocalStack/AWS data and
            filter matches with no rows render as designed empty states instead
            of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("gas-market-prices")),
            mo.Html(render_market_price_context_links()),
        ]
    )
    return


@app.cell
def _():
    market_price_load_cache = {}
    return (market_price_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.button(
        label="Refresh data",
        value=0,
        on_click=lambda value: value + 1,
    )
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_market_price_table,
    discover_dashboard_config,
    market_price_load_cache,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    market_price_load = cached_load_market_price_table(
        config,
        market_price_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, market_price_load


@app.cell
def _(
    config,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    market_price_bounded_scope_markdown,
    market_price_load,
    mo,
):
    price_loads = [market_price_load]
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(price_loads)),
                kind="neutral",
            ),
            mo.callout(
                mo.md(market_price_bounded_scope_markdown(config, market_price_load)),
                kind="warn" if config.aws_runtime else "neutral",
            ),
            mo.accordion(
                {
                    "Market price read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(price_loads),
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
                "silver/gas_model/silver_gas_fact_market_price",
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
    MARKET_PRICE_GAS_DATE_FILTER_ALL,
    MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
    MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
    MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
    market_price_load,
    market_price_gas_date_options,
    market_price_price_type_options,
    market_price_source_system_options,
    market_price_source_table_options,
    mo,
):
    gas_date_filter = mo.ui.dropdown(
        options=market_price_gas_date_options(market_price_load),
        value=MARKET_PRICE_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas date",
        full_width=True,
    )
    price_type_filter = mo.ui.dropdown(
        options=market_price_price_type_options(market_price_load),
        value=MARKET_PRICE_PRICE_TYPE_FILTER_ALL,
        searchable=True,
        label="Price type",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=market_price_source_system_options(market_price_load),
        value=MARKET_PRICE_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )
    source_table_filter = mo.ui.dropdown(
        options=market_price_source_table_options(market_price_load),
        value=MARKET_PRICE_SOURCE_TABLE_FILTER_ALL,
        searchable=True,
        label="Source table",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack(
                [
                    gas_date_filter,
                    price_type_filter,
                    source_system_filter,
                    source_table_filter,
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return gas_date_filter, price_type_filter, source_system_filter, source_table_filter


@app.cell
def _(
    market_price_empty_state_markdown,
    market_price_kpi_frame,
    market_price_load,
    mo,
    gas_date_filter,
    price_type_filter,
    source_system_filter,
    source_table_filter,
):
    kpis = market_price_kpi_frame(
        market_price_load,
        price_type_filter.value,
        source_system_filter.value,
        source_table_filter.value,
        gas_date_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(market_price_empty_state_markdown(market_price_load))
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Price Health"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    market_price_empty_state_markdown,
    market_price_load,
    market_price_type_summary_frame,
    mo,
    gas_date_filter,
    price_type_filter,
    source_system_filter,
    source_table_filter,
):
    type_summary = market_price_type_summary_frame(
        market_price_load,
        price_type_filter.value,
        source_system_filter.value,
        source_table_filter.value,
        gas_date_filter.value,
    )
    if type_summary.is_empty():
        type_summary_view = mo.md(market_price_empty_state_markdown(market_price_load))
    else:
        type_summary_view = mo.ui.table(type_summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Price Type And Source Summary

            This sampled/recent-only view summarizes the currently loaded
            bounded rows by `gas_date`, `price_type`, `source_system`,
            `source_table`, and populated price measure columns.
            """),
            type_summary_view,
        ]
    )
    return


@app.cell
def _(
    market_price_empty_state_markdown,
    market_price_load,
    market_price_trend_diagnostic_frame,
    mo,
    gas_date_filter,
    price_type_filter,
    source_system_filter,
    source_table_filter,
):
    trend_diagnostics = market_price_trend_diagnostic_frame(
        market_price_load,
        price_type_filter.value,
        source_system_filter.value,
        source_table_filter.value,
        gas_date_filter.value,
    )
    if trend_diagnostics.is_empty():
        trend_diagnostics_view = mo.md(
            market_price_empty_state_markdown(market_price_load)
        )
    else:
        trend_diagnostics_view = mo.ui.table(
            trend_diagnostics,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Bounded Price Trend Diagnostics

            This bounded view compares first and latest loaded daily averages
            by source, price type, and price measure. In AWS mode it is a
            sampled/recent-only diagnostic, not a full historical scan.
            """),
            trend_diagnostics_view,
        ]
    )
    return


@app.cell
def _(
    market_price_empty_state_markdown,
    market_price_exception_frame,
    market_price_load,
    mo,
    gas_date_filter,
    price_type_filter,
    source_system_filter,
    source_table_filter,
):
    exception_candidates = market_price_exception_frame(
        market_price_load,
        price_type_filter.value,
        source_system_filter.value,
        source_table_filter.value,
        gas_date_filter.value,
    )
    if exception_candidates.is_empty():
        exception_candidates_view = mo.md(
            market_price_empty_state_markdown(market_price_load)
        )
    else:
        exception_candidates_view = mo.ui.table(
            exception_candidates,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Bounded Price Exception Candidates

            Candidate rows come from missing price measures, non-positive
            values, and bounded high/low range edges in the loaded sample. In
            AWS mode this view is explicitly bounded to recent/sample rows.
            """),
            exception_candidates_view,
        ]
    )
    return


@app.cell
def _(
    market_price_empty_state_markdown,
    market_price_load,
    market_price_trend_frame,
    mo,
    gas_date_filter,
    price_type_filter,
    source_system_filter,
    source_table_filter,
):
    trend = market_price_trend_frame(
        market_price_load,
        price_type_filter.value,
        source_system_filter.value,
        source_table_filter.value,
        gas_date_filter.value,
    )
    if trend.is_empty():
        trend_view = mo.md(market_price_empty_state_markdown(market_price_load))
    else:
        trend_view = mo.ui.table(
            trend,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md(
                f"""
                ## Bounded Recent Loaded Price Trend

                Gas date: `{gas_date_filter.value}`. Price type:
                `{price_type_filter.value}`. Source system:
                `{source_system_filter.value}`. Source table:
                `{source_table_filter.value}`. This trend is calculated only
                from the loaded bounded rows and is not a full historical scan
                when preview limits are active.
                """
            ),
            trend_view,
        ]
    )
    return


@app.cell
def _(
    market_price_empty_state_markdown,
    market_price_load,
    market_price_observation_frame,
    mo,
    gas_date_filter,
    price_type_filter,
    source_system_filter,
    source_table_filter,
):
    observations = market_price_observation_frame(
        market_price_load,
        price_type_filter.value,
        source_system_filter.value,
        source_table_filter.value,
        gas_date_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(market_price_empty_state_markdown(market_price_load))
    else:
        observation_view = mo.ui.table(
            observations,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Recent Loaded Price Preview

            The preview is capped to the dashboard preview rows after the shared
            bounded source read. Schedule columns are displayed where source
            rows carry schedule type, interval, or transmission context.
            """),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
