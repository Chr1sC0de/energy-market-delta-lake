import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        STTM_CAPACITY_SETTLEMENT_COMPONENT_FILTER_ALL,
        STTM_CAPACITY_SETTLEMENT_FACILITY_FILTER_ALL,
        STTM_CAPACITY_SETTLEMENT_GAS_DATE_FILTER_ALL,
        STTM_CAPACITY_SETTLEMENT_HUB_FILTER_ALL,
        STTM_CAPACITY_SETTLEMENT_STAGE_FILTER_ALL,
        cached_load_sttm_capacity_settlement_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_sttm_capacity_settlement_context_links,
        sttm_capacity_settlement_component_options,
        sttm_capacity_settlement_empty_state_markdown,
        sttm_capacity_settlement_facility_options,
        sttm_capacity_settlement_gas_date_options,
        sttm_capacity_settlement_hub_options,
        sttm_capacity_settlement_kpi_frame,
        sttm_capacity_settlement_observation_frame,
        sttm_capacity_settlement_source_coverage_frame,
        sttm_capacity_settlement_stage_options,
        sttm_capacity_settlement_summary_frame,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        STTM_CAPACITY_SETTLEMENT_COMPONENT_FILTER_ALL,
        STTM_CAPACITY_SETTLEMENT_FACILITY_FILTER_ALL,
        STTM_CAPACITY_SETTLEMENT_GAS_DATE_FILTER_ALL,
        STTM_CAPACITY_SETTLEMENT_HUB_FILTER_ALL,
        STTM_CAPACITY_SETTLEMENT_STAGE_FILTER_ALL,
        cached_load_sttm_capacity_settlement_table,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_sttm_capacity_settlement_context_links,
        sttm_capacity_settlement_component_options,
        sttm_capacity_settlement_empty_state_markdown,
        sttm_capacity_settlement_facility_options,
        sttm_capacity_settlement_gas_date_options,
        sttm_capacity_settlement_hub_options,
        sttm_capacity_settlement_kpi_frame,
        sttm_capacity_settlement_observation_frame,
        sttm_capacity_settlement_source_coverage_frame,
        sttm_capacity_settlement_stage_options,
        sttm_capacity_settlement_summary_frame,
    )


@app.cell
def _(
    mo, render_dashboard_context_panel, render_sttm_capacity_settlement_context_links
):
    mo.vstack(
        [
            mo.md("""
            # STTM Capacity Settlement

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect curated STTM capacity
            settlement rows in `silver.gas_model`, including settlement run,
            settlement stage, MOS/capacity settlement component, Hub / Zone,
            Facility, Gas Day, quantity, source system, source report, and
            accepted source identifier fields. Freshness, load timing, cache
            status, and bounded preview policy come from the shared gas model
            loader. Missing LocalStack/AWS data and filter matches with no rows
            render as designed empty states instead of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("sttm-capacity-settlement")),
            mo.Html(render_sttm_capacity_settlement_context_links()),
        ]
    )
    return


@app.cell
def _():
    sttm_capacity_settlement_load_cache = {}
    return (sttm_capacity_settlement_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_sttm_capacity_settlement_table,
    discover_dashboard_config,
    refresh_data_button,
    refresh_token_from_control,
    sttm_capacity_settlement_load_cache,
):
    config = discover_dashboard_config()
    sttm_capacity_settlement_load = cached_load_sttm_capacity_settlement_table(
        config,
        sttm_capacity_settlement_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, sttm_capacity_settlement_load


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
    sttm_capacity_settlement_load,
):
    sttm_capacity_settlement_loads = [sttm_capacity_settlement_load]
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(sttm_capacity_settlement_loads)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "STTM capacity settlement read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(sttm_capacity_settlement_loads),
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
                "silver/gas_model/silver_gas_fact_sttm_capacity_settlement",
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
    STTM_CAPACITY_SETTLEMENT_COMPONENT_FILTER_ALL,
    STTM_CAPACITY_SETTLEMENT_FACILITY_FILTER_ALL,
    STTM_CAPACITY_SETTLEMENT_GAS_DATE_FILTER_ALL,
    STTM_CAPACITY_SETTLEMENT_HUB_FILTER_ALL,
    STTM_CAPACITY_SETTLEMENT_STAGE_FILTER_ALL,
    mo,
    sttm_capacity_settlement_component_options,
    sttm_capacity_settlement_facility_options,
    sttm_capacity_settlement_gas_date_options,
    sttm_capacity_settlement_hub_options,
    sttm_capacity_settlement_load,
    sttm_capacity_settlement_stage_options,
):
    gas_date_filter = mo.ui.dropdown(
        options=sttm_capacity_settlement_gas_date_options(
            sttm_capacity_settlement_load
        ),
        value=STTM_CAPACITY_SETTLEMENT_GAS_DATE_FILTER_ALL,
        searchable=True,
        label="Gas Day",
        full_width=True,
    )
    settlement_stage_filter = mo.ui.dropdown(
        options=sttm_capacity_settlement_stage_options(sttm_capacity_settlement_load),
        value=STTM_CAPACITY_SETTLEMENT_STAGE_FILTER_ALL,
        searchable=True,
        label="Settlement stage",
        full_width=True,
    )
    capacity_component_filter = mo.ui.dropdown(
        options=sttm_capacity_settlement_component_options(
            sttm_capacity_settlement_load
        ),
        value=STTM_CAPACITY_SETTLEMENT_COMPONENT_FILTER_ALL,
        searchable=True,
        label="Capacity settlement component",
        full_width=True,
    )
    hub_filter = mo.ui.dropdown(
        options=sttm_capacity_settlement_hub_options(sttm_capacity_settlement_load),
        value=STTM_CAPACITY_SETTLEMENT_HUB_FILTER_ALL,
        searchable=True,
        label="Hub / Zone",
        full_width=True,
    )
    facility_filter = mo.ui.dropdown(
        options=sttm_capacity_settlement_facility_options(
            sttm_capacity_settlement_load
        ),
        value=STTM_CAPACITY_SETTLEMENT_FACILITY_FILTER_ALL,
        searchable=True,
        label="Facility",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack(
                [
                    gas_date_filter,
                    settlement_stage_filter,
                    capacity_component_filter,
                    hub_filter,
                    facility_filter,
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return (
        capacity_component_filter,
        facility_filter,
        gas_date_filter,
        hub_filter,
        settlement_stage_filter,
    )


@app.cell
def _(
    capacity_component_filter,
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    settlement_stage_filter,
    sttm_capacity_settlement_empty_state_markdown,
    sttm_capacity_settlement_kpi_frame,
    sttm_capacity_settlement_load,
):
    kpis = sttm_capacity_settlement_kpi_frame(
        sttm_capacity_settlement_load,
        gas_date_filter.value,
        settlement_stage_filter.value,
        capacity_component_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            sttm_capacity_settlement_empty_state_markdown(sttm_capacity_settlement_load)
        )
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## STTM Capacity Settlement Summary"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    capacity_component_filter,
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    settlement_stage_filter,
    sttm_capacity_settlement_empty_state_markdown,
    sttm_capacity_settlement_load,
    sttm_capacity_settlement_summary_frame,
):
    settlement_summary = sttm_capacity_settlement_summary_frame(
        sttm_capacity_settlement_load,
        gas_date_filter.value,
        settlement_stage_filter.value,
        capacity_component_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if settlement_summary.is_empty():
        settlement_summary_view = mo.md(
            sttm_capacity_settlement_empty_state_markdown(sttm_capacity_settlement_load)
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

            This bounded/recent view groups STTM capacity settlement rows by
            settlement run, settlement stage, MOS/capacity component, Hub /
            Zone, Facility, source report, and quantity coverage.
            """),
            settlement_summary_view,
        ]
    )
    return


@app.cell
def _(
    capacity_component_filter,
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    settlement_stage_filter,
    sttm_capacity_settlement_empty_state_markdown,
    sttm_capacity_settlement_load,
    sttm_capacity_settlement_source_coverage_frame,
):
    source_coverage = sttm_capacity_settlement_source_coverage_frame(
        sttm_capacity_settlement_load,
        gas_date_filter.value,
        settlement_stage_filter.value,
        capacity_component_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            sttm_capacity_settlement_empty_state_markdown(sttm_capacity_settlement_load)
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage groups rows by source system, source table, and source
            report, including settlement run, stage, capacity component, hub,
            facility, Gas Day, quantity, source file, and accepted source
            identifier coverage.
            """),
            source_coverage_view,
        ]
    )
    return


@app.cell
def _(
    capacity_component_filter,
    facility_filter,
    gas_date_filter,
    hub_filter,
    mo,
    settlement_stage_filter,
    sttm_capacity_settlement_empty_state_markdown,
    sttm_capacity_settlement_load,
    sttm_capacity_settlement_observation_frame,
):
    observations = sttm_capacity_settlement_observation_frame(
        sttm_capacity_settlement_load,
        gas_date_filter.value,
        settlement_stage_filter.value,
        capacity_component_filter.value,
        hub_filter.value,
        facility_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(
            sttm_capacity_settlement_empty_state_markdown(sttm_capacity_settlement_load)
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
                ## Recent Loaded STTM Capacity Settlement Preview

                Gas Day: `{gas_date_filter.value}`. Settlement stage:
                `{settlement_stage_filter.value}`. Component:
                `{capacity_component_filter.value}`. Hub / Zone:
                `{hub_filter.value}`. Facility: `{facility_filter.value}`. The
                preview is capped to the dashboard preview rows after the shared
                bounded source read.
                """
            ),
            observation_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
