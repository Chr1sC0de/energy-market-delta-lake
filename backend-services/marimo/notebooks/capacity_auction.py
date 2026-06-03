import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        CAPACITY_AUCTION_AUCTION_DATE_FILTER_ALL,
        CAPACITY_AUCTION_CAPACITY_PERIOD_FILTER_ALL,
        CAPACITY_AUCTION_CONTEXT_ID,
        CAPACITY_AUCTION_METRIC_FILTER_ALL,
        CAPACITY_AUCTION_SOURCE_SYSTEM_FILTER_ALL,
        CAPACITY_AUCTION_TABLE_NAME,
        CAPACITY_AUCTION_ZONE_FILTER_ALL,
        cached_load_capacity_auction_table,
        capacity_auction_auction_date_options,
        capacity_auction_capacity_period_options,
        capacity_auction_empty_state_markdown,
        capacity_auction_kpi_frame,
        capacity_auction_metric_frame,
        capacity_auction_metric_options,
        capacity_auction_observation_frame,
        capacity_auction_source_system_options,
        capacity_auction_summary_frame,
        capacity_auction_zone_options,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_capacity_auction_context_links,
        render_dashboard_context_panel,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        CAPACITY_AUCTION_AUCTION_DATE_FILTER_ALL,
        CAPACITY_AUCTION_CAPACITY_PERIOD_FILTER_ALL,
        CAPACITY_AUCTION_CONTEXT_ID,
        CAPACITY_AUCTION_METRIC_FILTER_ALL,
        CAPACITY_AUCTION_SOURCE_SYSTEM_FILTER_ALL,
        CAPACITY_AUCTION_TABLE_NAME,
        CAPACITY_AUCTION_ZONE_FILTER_ALL,
        cached_load_capacity_auction_table,
        capacity_auction_auction_date_options,
        capacity_auction_capacity_period_options,
        capacity_auction_empty_state_markdown,
        capacity_auction_kpi_frame,
        capacity_auction_metric_frame,
        capacity_auction_metric_options,
        capacity_auction_observation_frame,
        capacity_auction_source_system_options,
        capacity_auction_summary_frame,
        capacity_auction_zone_options,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_capacity_auction_context_links,
        render_dashboard_context_panel,
    )


@app.cell
def _(
    CAPACITY_AUCTION_CONTEXT_ID,
    mo,
    render_capacity_auction_context_links,
    render_dashboard_context_panel,
):
    mo.vstack(
        [
            mo.md("""
            # Capacity Auctions

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect bounded capacity auction
            observations from `silver.gas_model.silver_gas_fact_capacity_auction`,
            including auction ID, auction date, Hub / Zone, capacity period,
            quantity, price, auction metric, source-system, and source-table
            fields. Data scope is read-only recent/sample Parquet data from
            the configured `silver.gas_model` bucket plus copied Marimo
            dashboard registry metadata for Capacity, Hub / Zone, market
            overview, source lineage, source coverage, and table explorer
            context. Freshness, load status, cache state, row-limit policy,
            and missing-source behavior come from the shared gas model loader;
            unavailable tables, empty reads, filter misses, and missing columns
            render designed empty states instead of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel(CAPACITY_AUCTION_CONTEXT_ID)),
            mo.Html(render_capacity_auction_context_links()),
        ]
    )
    return


@app.cell
def _():
    capacity_auction_load_cache = {}
    return (capacity_auction_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_capacity_auction_table,
    capacity_auction_load_cache,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    capacity_auction_load = cached_load_capacity_auction_table(
        config,
        capacity_auction_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    capacity_auction_loads = [capacity_auction_load]
    return capacity_auction_load, capacity_auction_loads, config


@app.cell
def _(
    capacity_auction_loads,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    mo.vstack(
        [
            mo.md(
                "## Data Health\n\n"
                + gas_table_load_status_message(capacity_auction_loads)
            ),
            mo.accordion(
                {
                    "Capacity auction read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(capacity_auction_loads),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(CAPACITY_AUCTION_TABLE_NAME, config, mo, pl):
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
                f"silver/gas_model/{CAPACITY_AUCTION_TABLE_NAME}",
                ("glossary:capacity, glossary:hub-zone"),
                (
                    "chunk-sttm-procedures-definitions, "
                    "chunk-sttm-procedures-capacity-settlement, "
                    "chunk-dwgm-operations-capacity-certificates-purpose, "
                    "chunk-dwgm-operations-capacity-certificates-modelling"
                ),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.accordion(
        {
            "Capacity auction read configuration": mo.ui.table(
                config_frame,
                selection=None,
            )
        },
        multiple=False,
    )
    return


@app.cell
def _(
    CAPACITY_AUCTION_AUCTION_DATE_FILTER_ALL,
    CAPACITY_AUCTION_CAPACITY_PERIOD_FILTER_ALL,
    CAPACITY_AUCTION_METRIC_FILTER_ALL,
    CAPACITY_AUCTION_SOURCE_SYSTEM_FILTER_ALL,
    CAPACITY_AUCTION_ZONE_FILTER_ALL,
    capacity_auction_auction_date_options,
    capacity_auction_capacity_period_options,
    capacity_auction_load,
    capacity_auction_metric_options,
    capacity_auction_source_system_options,
    capacity_auction_zone_options,
    mo,
):
    auction_date_filter = mo.ui.dropdown(
        options=capacity_auction_auction_date_options(capacity_auction_load),
        value=CAPACITY_AUCTION_AUCTION_DATE_FILTER_ALL,
        searchable=True,
        label="Auction date",
        full_width=True,
    )
    zone_filter = mo.ui.dropdown(
        options=capacity_auction_zone_options(capacity_auction_load),
        value=CAPACITY_AUCTION_ZONE_FILTER_ALL,
        searchable=True,
        label="Hub / Zone",
        full_width=True,
    )
    capacity_period_filter = mo.ui.dropdown(
        options=capacity_auction_capacity_period_options(capacity_auction_load),
        value=CAPACITY_AUCTION_CAPACITY_PERIOD_FILTER_ALL,
        searchable=True,
        label="Capacity period",
        full_width=True,
    )
    metric_filter = mo.ui.dropdown(
        options=capacity_auction_metric_options(capacity_auction_load),
        value=CAPACITY_AUCTION_METRIC_FILTER_ALL,
        searchable=True,
        label="Auction metric",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=capacity_auction_source_system_options(capacity_auction_load),
        value=CAPACITY_AUCTION_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack(
                [
                    auction_date_filter,
                    zone_filter,
                    capacity_period_filter,
                    metric_filter,
                    source_system_filter,
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return (
        auction_date_filter,
        capacity_period_filter,
        metric_filter,
        source_system_filter,
        zone_filter,
    )


@app.cell
def _(
    auction_date_filter,
    capacity_auction_empty_state_markdown,
    capacity_auction_kpi_frame,
    capacity_auction_load,
    capacity_period_filter,
    metric_filter,
    mo,
    source_system_filter,
    zone_filter,
):
    kpis = capacity_auction_kpi_frame(
        capacity_auction_load,
        auction_date_filter.value,
        zone_filter.value,
        capacity_period_filter.value,
        metric_filter.value,
        source_system_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(capacity_auction_empty_state_markdown(capacity_auction_load))
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Capacity Auction Summary"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    auction_date_filter,
    capacity_auction_empty_state_markdown,
    capacity_auction_load,
    capacity_auction_summary_frame,
    capacity_period_filter,
    metric_filter,
    mo,
    source_system_filter,
    zone_filter,
):
    summary = capacity_auction_summary_frame(
        capacity_auction_load,
        auction_date_filter.value,
        zone_filter.value,
        capacity_period_filter.value,
        metric_filter.value,
        source_system_filter.value,
    )
    if summary.is_empty():
        summary_view = mo.md(
            capacity_auction_empty_state_markdown(capacity_auction_load)
        )
    else:
        summary_view = mo.ui.table(summary, selection=None, page_size=20)

    mo.vstack(
        [
            mo.md("""
            ## Auction, Zone, Period, Quantity, And Price Summary

            This bounded view groups loaded rows by auction ID, auction date,
            Hub / Zone, capacity period, and auction metric, then summarizes
            quantity and price coverage from the current filter set.
            """),
            summary_view,
        ]
    )
    return


@app.cell
def _(
    auction_date_filter,
    capacity_auction_empty_state_markdown,
    capacity_auction_load,
    capacity_auction_metric_frame,
    capacity_period_filter,
    metric_filter,
    mo,
    source_system_filter,
    zone_filter,
):
    metric_summary = capacity_auction_metric_frame(
        capacity_auction_load,
        auction_date_filter.value,
        zone_filter.value,
        capacity_period_filter.value,
        metric_filter.value,
        source_system_filter.value,
    )
    if metric_summary.is_empty():
        metric_view = mo.md(
            capacity_auction_empty_state_markdown(capacity_auction_load)
        )
    else:
        metric_view = mo.ui.table(metric_summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Metric And Source Coverage

            Source coverage groups capacity auction rows by auction metric,
            source system, and source table so metric-specific price and
            quantity coverage stays visible.
            """),
            mo.accordion(
                {"Metric and source coverage detail": metric_view},
                multiple=False,
                lazy=True,
            ),
        ]
    )
    return


@app.cell
def _(
    auction_date_filter,
    capacity_auction_empty_state_markdown,
    capacity_auction_load,
    capacity_auction_observation_frame,
    capacity_period_filter,
    metric_filter,
    mo,
    source_system_filter,
    zone_filter,
):
    observations = capacity_auction_observation_frame(
        capacity_auction_load,
        auction_date_filter.value,
        zone_filter.value,
        capacity_period_filter.value,
        metric_filter.value,
        source_system_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            capacity_auction_empty_state_markdown(capacity_auction_load)
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
                ## Recent Loaded Capacity Auction Preview

                Auction date: `{auction_date_filter.value}`. Hub / Zone:
                `{zone_filter.value}`. Capacity period:
                `{capacity_period_filter.value}`. Auction metric:
                `{metric_filter.value}`. Source system:
                `{source_system_filter.value}`. The preview is capped to the
                dashboard preview rows after the shared bounded source read.
                """
            ),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
