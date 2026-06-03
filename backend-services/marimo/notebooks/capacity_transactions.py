import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        CAPACITY_TRANSACTION_CONTEXT_ID,
        CAPACITY_TRANSACTION_DATE_FILTER_ALL,
        CAPACITY_TRANSACTION_FACILITY_FILTER_ALL,
        CAPACITY_TRANSACTION_LOCATION_FILTER_ALL,
        CAPACITY_TRANSACTION_SOURCE_SYSTEM_FILTER_ALL,
        CAPACITY_TRANSACTION_TABLE_NAME,
        CAPACITY_TRANSACTION_TYPE_FILTER_ALL,
        cached_load_capacity_transaction_table,
        capacity_transaction_date_options,
        capacity_transaction_empty_state_markdown,
        capacity_transaction_facility_options,
        capacity_transaction_kpi_frame,
        capacity_transaction_location_options,
        capacity_transaction_observation_frame,
        capacity_transaction_source_coverage_frame,
        capacity_transaction_source_system_options,
        capacity_transaction_summary_frame,
        capacity_transaction_type_options,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_capacity_transaction_context_links,
        render_dashboard_context_panel,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        CAPACITY_TRANSACTION_CONTEXT_ID,
        CAPACITY_TRANSACTION_DATE_FILTER_ALL,
        CAPACITY_TRANSACTION_FACILITY_FILTER_ALL,
        CAPACITY_TRANSACTION_LOCATION_FILTER_ALL,
        CAPACITY_TRANSACTION_SOURCE_SYSTEM_FILTER_ALL,
        CAPACITY_TRANSACTION_TABLE_NAME,
        CAPACITY_TRANSACTION_TYPE_FILTER_ALL,
        cached_load_capacity_transaction_table,
        capacity_transaction_date_options,
        capacity_transaction_empty_state_markdown,
        capacity_transaction_facility_options,
        capacity_transaction_kpi_frame,
        capacity_transaction_location_options,
        capacity_transaction_observation_frame,
        capacity_transaction_source_coverage_frame,
        capacity_transaction_source_system_options,
        capacity_transaction_summary_frame,
        capacity_transaction_type_options,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_capacity_transaction_context_links,
        render_dashboard_context_panel,
    )


@app.cell
def _(mo):
    source_table_markup = (
        '<code style="white-space: normal; overflow-wrap: anywhere; '
        'word-break: break-word;">'
        "silver.gas_model.<wbr>silver_gas_fact_capacity_<wbr>transaction"
        "</code>"
    )
    mo.vstack(
        [
            mo.md(f"""
            # Capacity Transactions

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect bounded capacity and LNG
            transaction observations from
            {source_table_markup}, including
            transaction type/date, source location/facility, quantity, volume,
            price, source-system, and source-table fields. The view uses
            read-only bounded recent/sample Parquet data from the configured
            `silver.gas_model` bucket plus registry context. Freshness, load
            status, cache state, row-limit policy, and empty or missing-source
            behavior come from the shared gas model loader.
            """),
        ]
    )
    return


@app.cell
def _():
    capacity_transaction_load_cache = {}
    return (capacity_transaction_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_capacity_transaction_table,
    capacity_transaction_load_cache,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    capacity_transaction_load = cached_load_capacity_transaction_table(
        config,
        capacity_transaction_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    capacity_transaction_loads = [capacity_transaction_load]
    return capacity_transaction_load, capacity_transaction_loads, config


@app.cell
def _(
    capacity_transaction_loads,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
):
    mo.vstack(
        [
            mo.md(
                "## Data Health\n\n"
                + gas_table_load_status_message(capacity_transaction_loads)
            ),
            mo.accordion(
                {
                    "Capacity transaction read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(capacity_transaction_loads),
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
    CAPACITY_TRANSACTION_CONTEXT_ID,
    mo,
    render_capacity_transaction_context_links,
    render_dashboard_context_panel,
):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(CAPACITY_TRANSACTION_CONTEXT_ID)),
            mo.Html(render_capacity_transaction_context_links()),
        ]
    )
    return


@app.cell
def _(CAPACITY_TRANSACTION_TABLE_NAME, config, mo, pl):
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
                f"silver/gas_model/{CAPACITY_TRANSACTION_TABLE_NAME}",
                "glossary:capacity",
                (
                    "chunk-gbb-procedures-capacity-outlooks, "
                    "chunk-gbb-guide-nameplate-capacity"
                ),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.accordion(
        {
            "Capacity transaction read configuration": mo.ui.table(
                config_frame,
                selection=None,
            )
        },
        multiple=False,
    )
    return


@app.cell
def _(
    CAPACITY_TRANSACTION_DATE_FILTER_ALL,
    CAPACITY_TRANSACTION_FACILITY_FILTER_ALL,
    CAPACITY_TRANSACTION_LOCATION_FILTER_ALL,
    CAPACITY_TRANSACTION_SOURCE_SYSTEM_FILTER_ALL,
    CAPACITY_TRANSACTION_TYPE_FILTER_ALL,
    capacity_transaction_date_options,
    capacity_transaction_facility_options,
    capacity_transaction_load,
    capacity_transaction_location_options,
    capacity_transaction_source_system_options,
    capacity_transaction_type_options,
    mo,
):
    transaction_type_filter = mo.ui.dropdown(
        options=capacity_transaction_type_options(capacity_transaction_load),
        value=CAPACITY_TRANSACTION_TYPE_FILTER_ALL,
        searchable=True,
        label="Transaction type",
        full_width=True,
    )
    transaction_date_filter = mo.ui.dropdown(
        options=capacity_transaction_date_options(capacity_transaction_load),
        value=CAPACITY_TRANSACTION_DATE_FILTER_ALL,
        searchable=True,
        label="Transaction date",
        full_width=True,
    )
    location_filter = mo.ui.dropdown(
        options=capacity_transaction_location_options(capacity_transaction_load),
        value=CAPACITY_TRANSACTION_LOCATION_FILTER_ALL,
        searchable=True,
        label="Source location",
        full_width=True,
    )
    facility_filter = mo.ui.dropdown(
        options=capacity_transaction_facility_options(capacity_transaction_load),
        value=CAPACITY_TRANSACTION_FACILITY_FILTER_ALL,
        searchable=True,
        label="Source facility",
        full_width=True,
    )
    source_system_filter = mo.ui.dropdown(
        options=capacity_transaction_source_system_options(capacity_transaction_load),
        value=CAPACITY_TRANSACTION_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack(
                [
                    transaction_type_filter,
                    transaction_date_filter,
                    location_filter,
                    facility_filter,
                    source_system_filter,
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return (
        facility_filter,
        location_filter,
        source_system_filter,
        transaction_date_filter,
        transaction_type_filter,
    )


@app.cell
def _(
    capacity_transaction_empty_state_markdown,
    capacity_transaction_kpi_frame,
    capacity_transaction_load,
    facility_filter,
    location_filter,
    mo,
    source_system_filter,
    transaction_date_filter,
    transaction_type_filter,
):
    kpis = capacity_transaction_kpi_frame(
        capacity_transaction_load,
        transaction_type_filter.value,
        transaction_date_filter.value,
        location_filter.value,
        facility_filter.value,
        source_system_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            capacity_transaction_empty_state_markdown(capacity_transaction_load)
        )
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Capacity Transaction Summary"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    capacity_transaction_empty_state_markdown,
    capacity_transaction_load,
    capacity_transaction_summary_frame,
    facility_filter,
    location_filter,
    mo,
    source_system_filter,
    transaction_date_filter,
    transaction_type_filter,
):
    summary = capacity_transaction_summary_frame(
        capacity_transaction_load,
        transaction_type_filter.value,
        transaction_date_filter.value,
        location_filter.value,
        facility_filter.value,
        source_system_filter.value,
    )
    if summary.is_empty():
        summary_view = mo.md(
            capacity_transaction_empty_state_markdown(capacity_transaction_load)
        )
    else:
        summary_view = mo.ui.table(summary, selection=None, page_size=20)

    mo.vstack(
        [
            mo.md("""
            ## Type, Date, Location, Quantity, Volume, And Price Summary

            This bounded view groups loaded rows by transaction type,
            transaction date, supply period, source location, and source
            facility, then summarizes quantity, LNG volume, and price coverage
            from the current filter set.
            """),
            summary_view,
        ]
    )
    return


@app.cell
def _(
    capacity_transaction_empty_state_markdown,
    capacity_transaction_load,
    capacity_transaction_source_coverage_frame,
    facility_filter,
    location_filter,
    mo,
    source_system_filter,
    transaction_date_filter,
    transaction_type_filter,
):
    source_coverage = capacity_transaction_source_coverage_frame(
        capacity_transaction_load,
        transaction_type_filter.value,
        transaction_date_filter.value,
        location_filter.value,
        facility_filter.value,
        source_system_filter.value,
    )
    if source_coverage.is_empty():
        source_view = mo.md(
            capacity_transaction_empty_state_markdown(capacity_transaction_load)
        )
    else:
        source_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Source coverage groups transaction rows by source system and source
            table so capacity transaction, LNG transaction, and LNG shipment
            coverage stays visible.
            """),
            mo.accordion(
                {"Transaction source coverage detail": source_view},
                multiple=False,
                lazy=True,
            ),
        ]
    )
    return


@app.cell
def _(
    capacity_transaction_empty_state_markdown,
    capacity_transaction_load,
    capacity_transaction_observation_frame,
    facility_filter,
    location_filter,
    mo,
    source_system_filter,
    transaction_date_filter,
    transaction_type_filter,
):
    observations = capacity_transaction_observation_frame(
        capacity_transaction_load,
        transaction_type_filter.value,
        transaction_date_filter.value,
        location_filter.value,
        facility_filter.value,
        source_system_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            capacity_transaction_empty_state_markdown(capacity_transaction_load)
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
                ## Recent Loaded Capacity Transaction Preview

                Transaction type: `{transaction_type_filter.value}`.
                Transaction date: `{transaction_date_filter.value}`. Source
                location: `{location_filter.value}`. Source facility:
                `{facility_filter.value}`. Source system:
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
