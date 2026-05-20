import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        STTM_CONTINGENCY_GAS_GRAIN_FILTER_ALL,
        STTM_CONTINGENCY_GAS_HUB_FILTER_ALL,
        STTM_CONTINGENCY_GAS_QUANTITY_TYPE_FILTER_ALL,
        STTM_CONTINGENCY_GAS_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_sttm_contingency_gas_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_sttm_contingency_gas_context_links,
        sttm_contingency_gas_bid_offer_summary_frame,
        sttm_contingency_gas_empty_state_markdown,
        sttm_contingency_gas_grain_options,
        sttm_contingency_gas_grain_summary_frame,
        sttm_contingency_gas_hub_options,
        sttm_contingency_gas_kpi_frame,
        sttm_contingency_gas_observation_frame,
        sttm_contingency_gas_quantity_type_options,
        sttm_contingency_gas_source_summary_frame,
        sttm_contingency_gas_source_system_options,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        STTM_CONTINGENCY_GAS_GRAIN_FILTER_ALL,
        STTM_CONTINGENCY_GAS_HUB_FILTER_ALL,
        STTM_CONTINGENCY_GAS_QUANTITY_TYPE_FILTER_ALL,
        STTM_CONTINGENCY_GAS_SOURCE_SYSTEM_FILTER_ALL,
        cached_load_sttm_contingency_gas_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_sttm_contingency_gas_context_links,
        sttm_contingency_gas_bid_offer_summary_frame,
        sttm_contingency_gas_empty_state_markdown,
        sttm_contingency_gas_grain_options,
        sttm_contingency_gas_grain_summary_frame,
        sttm_contingency_gas_hub_options,
        sttm_contingency_gas_kpi_frame,
        sttm_contingency_gas_observation_frame,
        sttm_contingency_gas_quantity_type_options,
        sttm_contingency_gas_source_summary_frame,
        sttm_contingency_gas_source_system_options,
    )


@app.cell
def _(
    mo,
    render_dashboard_context_panel,
    render_sttm_contingency_gas_context_links,
):
    mo.vstack(
        [
            mo.md("""
            # STTM Contingency Gas

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect curated STTM contingency
            gas call rows in `silver.gas_model`, including Gas Day,
            contingency grain, quantity type, hub, facility, participant,
            Bid / Offer identifier, step, price, quantity, approval, source
            system, and accepted source identifier fields. Freshness, load
            timing, cache status, and bounded preview policy come from the
            shared gas model loader. Missing LocalStack/AWS data and filter
            matches with no rows render as designed empty states instead of
            notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("sttm-contingency-gas")),
            mo.Html(render_sttm_contingency_gas_context_links()),
        ]
    )
    return


@app.cell
def _():
    contingency_gas_load_cache = {}
    return (contingency_gas_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_sttm_contingency_gas_table,
    contingency_gas_load_cache,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    contingency_gas_load = cached_load_sttm_contingency_gas_table(
        config,
        contingency_gas_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, contingency_gas_load


@app.cell
def _(
    contingency_gas_load,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    contingency_gas_loads = [contingency_gas_load]
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(contingency_gas_loads)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "STTM contingency gas read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(contingency_gas_loads),
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
                "silver/gas_model/silver_gas_fact_sttm_contingency_gas_call",
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
    STTM_CONTINGENCY_GAS_GRAIN_FILTER_ALL,
    STTM_CONTINGENCY_GAS_HUB_FILTER_ALL,
    STTM_CONTINGENCY_GAS_QUANTITY_TYPE_FILTER_ALL,
    STTM_CONTINGENCY_GAS_SOURCE_SYSTEM_FILTER_ALL,
    contingency_gas_load,
    mo,
    sttm_contingency_gas_grain_options,
    sttm_contingency_gas_hub_options,
    sttm_contingency_gas_quantity_type_options,
    sttm_contingency_gas_source_system_options,
):
    grain_filter = mo.ui.dropdown(
        options=sttm_contingency_gas_grain_options(contingency_gas_load),
        value=STTM_CONTINGENCY_GAS_GRAIN_FILTER_ALL,
        searchable=True,
        label="Contingency grain",
        full_width=True,
    )
    quantity_type_filter = mo.ui.dropdown(
        options=sttm_contingency_gas_quantity_type_options(contingency_gas_load),
        value=STTM_CONTINGENCY_GAS_QUANTITY_TYPE_FILTER_ALL,
        searchable=True,
        label="Quantity type",
        full_width=True,
    )
    hub_filter = mo.ui.dropdown(
        options=sttm_contingency_gas_hub_options(contingency_gas_load),
        value=STTM_CONTINGENCY_GAS_HUB_FILTER_ALL,
        searchable=True,
        label="Hub",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=sttm_contingency_gas_source_system_options(contingency_gas_load),
        value=STTM_CONTINGENCY_GAS_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack(
                [
                    grain_filter,
                    quantity_type_filter,
                    hub_filter,
                    source_system_filter,
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return grain_filter, hub_filter, quantity_type_filter, source_system_filter


@app.cell
def _(
    contingency_gas_load,
    grain_filter,
    hub_filter,
    mo,
    quantity_type_filter,
    source_system_filter,
    sttm_contingency_gas_empty_state_markdown,
    sttm_contingency_gas_kpi_frame,
):
    kpis = sttm_contingency_gas_kpi_frame(
        contingency_gas_load,
        grain_filter.value,
        quantity_type_filter.value,
        hub_filter.value,
        source_system_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            sttm_contingency_gas_empty_state_markdown(contingency_gas_load)
        )
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## STTM Contingency Gas Summary"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    contingency_gas_load,
    grain_filter,
    hub_filter,
    mo,
    quantity_type_filter,
    source_system_filter,
    sttm_contingency_gas_empty_state_markdown,
    sttm_contingency_gas_grain_summary_frame,
):
    grain_summary = sttm_contingency_gas_grain_summary_frame(
        contingency_gas_load,
        grain_filter.value,
        quantity_type_filter.value,
        hub_filter.value,
        source_system_filter.value,
    )
    if grain_summary.is_empty():
        grain_summary_view = mo.md(
            sttm_contingency_gas_empty_state_markdown(contingency_gas_load)
        )
    else:
        grain_summary_view = mo.ui.table(grain_summary, selection=None, page_size=20)

    mo.vstack(
        [
            mo.md("""
            ## Contingency Grain And Quantity Summary

            This sampled/recent-only view summarizes loaded rows by contingency
            grain, quantity type, source system, and hub, preserving the accepted
            source grains used by the curated fact.
            """),
            grain_summary_view,
        ]
    )
    return


@app.cell
def _(
    contingency_gas_load,
    grain_filter,
    hub_filter,
    mo,
    quantity_type_filter,
    source_system_filter,
    sttm_contingency_gas_bid_offer_summary_frame,
    sttm_contingency_gas_empty_state_markdown,
):
    bid_offer_summary = sttm_contingency_gas_bid_offer_summary_frame(
        contingency_gas_load,
        grain_filter.value,
        quantity_type_filter.value,
        hub_filter.value,
        source_system_filter.value,
    )
    if bid_offer_summary.is_empty():
        bid_offer_summary_view = mo.md(
            sttm_contingency_gas_empty_state_markdown(contingency_gas_load)
        )
    else:
        bid_offer_summary_view = mo.ui.table(
            bid_offer_summary,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Bid / Offer Context

            Rows with contingency Bid / Offer identifiers, bid steps, prices,
            or cumulative bid quantities are grouped here so call, schedule, and
            Bid / Offer context can be compared without leaving the dashboard.
            """),
            bid_offer_summary_view,
        ]
    )
    return


@app.cell
def _(
    contingency_gas_load,
    grain_filter,
    hub_filter,
    mo,
    quantity_type_filter,
    source_system_filter,
    sttm_contingency_gas_empty_state_markdown,
    sttm_contingency_gas_source_summary_frame,
):
    source_summary = sttm_contingency_gas_source_summary_frame(
        contingency_gas_load,
        grain_filter.value,
        quantity_type_filter.value,
        hub_filter.value,
        source_system_filter.value,
    )
    if source_summary.is_empty():
        source_summary_view = mo.md(
            sttm_contingency_gas_empty_state_markdown(contingency_gas_load)
        )
    else:
        source_summary_view = mo.ui.table(source_summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Identifier Coverage

            Coverage groups rows by source system, source table, and source
            report, including accepted source identifiers, source files, Gas Day
            span, and freshness timestamps.
            """),
            source_summary_view,
        ]
    )
    return


@app.cell
def _(
    contingency_gas_load,
    grain_filter,
    hub_filter,
    mo,
    quantity_type_filter,
    source_system_filter,
    sttm_contingency_gas_empty_state_markdown,
    sttm_contingency_gas_observation_frame,
):
    observations = sttm_contingency_gas_observation_frame(
        contingency_gas_load,
        grain_filter.value,
        quantity_type_filter.value,
        hub_filter.value,
        source_system_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            sttm_contingency_gas_empty_state_markdown(contingency_gas_load)
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
                ## Recent Loaded STTM Contingency Gas Preview

                Contingency grain: `{grain_filter.value}`. Quantity type:
                `{quantity_type_filter.value}`. Hub: `{hub_filter.value}`.
                Source system: `{source_system_filter.value}`. The preview is
                capped to the dashboard preview rows after the shared bounded
                source read.
                """
            ),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
