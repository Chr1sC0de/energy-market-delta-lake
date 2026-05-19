import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        BID_STACK_FACILITY_FILTER_ALL,
        BID_STACK_PARTICIPANT_FILTER_ALL,
        BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
        BID_STACK_ZONE_FILTER_ALL,
        bid_stack_empty_state_markdown,
        bid_stack_facility_options,
        bid_stack_kpi_frame,
        bid_stack_observation_frame,
        bid_stack_participant_options,
        bid_stack_source_summary_frame,
        bid_stack_source_system_options,
        bid_stack_step_summary_frame,
        bid_stack_zone_options,
        cached_load_bid_stack_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_bid_stack_context_links,
        render_dashboard_context_panel,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        BID_STACK_FACILITY_FILTER_ALL,
        BID_STACK_PARTICIPANT_FILTER_ALL,
        BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
        BID_STACK_ZONE_FILTER_ALL,
        bid_stack_empty_state_markdown,
        bid_stack_facility_options,
        bid_stack_kpi_frame,
        bid_stack_observation_frame,
        bid_stack_participant_options,
        bid_stack_source_summary_frame,
        bid_stack_source_system_options,
        bid_stack_step_summary_frame,
        bid_stack_zone_options,
        cached_load_bid_stack_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_bid_stack_context_links,
        render_dashboard_context_panel,
    )


@app.cell
def _(mo, render_bid_stack_context_links, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Gas Bid / Offer Stack

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect curated Bid / Offer stack
            rows from `silver.gas_model.silver_gas_fact_bid_stack`, including
            participant, facility, zone, bid step, bid price, bid quantity,
            source system, and accepted source identifier fields. Freshness,
            load timing, cache status, and bounded preview policy come from the
            shared gas model loader. Missing LocalStack/AWS data and filter
            matches with no rows render as designed empty states instead of
            notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("bid-offer-context")),
            mo.Html(render_bid_stack_context_links()),
        ]
    )
    return


@app.cell
def _():
    bid_stack_load_cache = {}
    return (bid_stack_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    bid_stack_load_cache,
    cached_load_bid_stack_table,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    bid_stack_load = cached_load_bid_stack_table(
        config,
        bid_stack_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return bid_stack_load, config


@app.cell
def _(bid_stack_load, gas_table_load_status_frame, gas_table_load_status_message, mo):
    bid_stack_loads = [bid_stack_load]
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(bid_stack_loads)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "Bid / Offer stack read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(bid_stack_loads),
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
                "silver/gas_model/silver_gas_fact_bid_stack",
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
    BID_STACK_FACILITY_FILTER_ALL,
    BID_STACK_PARTICIPANT_FILTER_ALL,
    BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
    BID_STACK_ZONE_FILTER_ALL,
    bid_stack_facility_options,
    bid_stack_load,
    bid_stack_participant_options,
    bid_stack_source_system_options,
    bid_stack_zone_options,
    mo,
):
    participant_filter = mo.ui.dropdown(
        options=bid_stack_participant_options(bid_stack_load),
        value=BID_STACK_PARTICIPANT_FILTER_ALL,
        searchable=True,
        label="Participant",
        full_width=True,
    )
    facility_filter = mo.ui.dropdown(
        options=bid_stack_facility_options(bid_stack_load),
        value=BID_STACK_FACILITY_FILTER_ALL,
        searchable=True,
        label="Facility",
        full_width=True,
    )
    zone_filter = mo.ui.dropdown(
        options=bid_stack_zone_options(bid_stack_load),
        value=BID_STACK_ZONE_FILTER_ALL,
        searchable=True,
        label="Zone / hub",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=bid_stack_source_system_options(bid_stack_load),
        value=BID_STACK_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack(
                [
                    participant_filter,
                    facility_filter,
                    zone_filter,
                    source_system_filter,
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return facility_filter, participant_filter, source_system_filter, zone_filter


@app.cell
def _(
    bid_stack_empty_state_markdown,
    bid_stack_kpi_frame,
    bid_stack_load,
    facility_filter,
    mo,
    participant_filter,
    source_system_filter,
    zone_filter,
):
    kpis = bid_stack_kpi_frame(
        bid_stack_load,
        participant_filter.value,
        facility_filter.value,
        zone_filter.value,
        source_system_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(bid_stack_empty_state_markdown(bid_stack_load))
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Bid / Offer Stack Summary"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    bid_stack_empty_state_markdown,
    bid_stack_load,
    bid_stack_step_summary_frame,
    facility_filter,
    mo,
    participant_filter,
    source_system_filter,
    zone_filter,
):
    step_summary = bid_stack_step_summary_frame(
        bid_stack_load,
        participant_filter.value,
        facility_filter.value,
        zone_filter.value,
        source_system_filter.value,
    )
    if step_summary.is_empty():
        step_summary_view = mo.md(bid_stack_empty_state_markdown(bid_stack_load))
    else:
        step_summary_view = mo.ui.table(
            step_summary,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md("""
            ## Step, Price, And Quantity Summary

            This sampled/recent-only view summarizes loaded rows by source
            system, zone, facility, and `bid_step`, with participant, bid ID,
            price, and quantity coverage from the bounded read.
            """),
            step_summary_view,
        ]
    )
    return


@app.cell
def _(
    bid_stack_empty_state_markdown,
    bid_stack_load,
    bid_stack_source_summary_frame,
    facility_filter,
    mo,
    participant_filter,
    source_system_filter,
    zone_filter,
):
    source_summary = bid_stack_source_summary_frame(
        bid_stack_load,
        participant_filter.value,
        facility_filter.value,
        zone_filter.value,
        source_system_filter.value,
    )
    if source_summary.is_empty():
        source_summary_view = mo.md(bid_stack_empty_state_markdown(bid_stack_load))
    else:
        source_summary_view = mo.ui.table(source_summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Identifier Coverage

            Coverage groups rows by source system, source table, and source
            report, including counts for accepted source identifiers, source
            files, bid IDs, participants, facilities, zones, and steps.
            """),
            source_summary_view,
        ]
    )
    return


@app.cell
def _(
    bid_stack_empty_state_markdown,
    bid_stack_load,
    bid_stack_observation_frame,
    facility_filter,
    mo,
    participant_filter,
    source_system_filter,
    zone_filter,
):
    observations = bid_stack_observation_frame(
        bid_stack_load,
        participant_filter.value,
        facility_filter.value,
        zone_filter.value,
        source_system_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(bid_stack_empty_state_markdown(bid_stack_load))
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
                ## Recent Loaded Bid / Offer Stack Preview

                Participant: `{participant_filter.value}`. Facility:
                `{facility_filter.value}`. Zone / hub: `{zone_filter.value}`.
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
