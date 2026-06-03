import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
        GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
        cached_load_gas_quality_table,
        discover_dashboard_config,
        gas_quality_empty_state_markdown,
        gas_quality_kpi_frame,
        gas_quality_observation_frame,
        gas_quality_quality_type_options,
        gas_quality_source_coverage_frame,
        gas_quality_source_point_options,
        gas_quality_type_summary_frame,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
        GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
        cached_load_gas_quality_table,
        discover_dashboard_config,
        gas_quality_empty_state_markdown,
        gas_quality_kpi_frame,
        gas_quality_observation_frame,
        gas_quality_quality_type_options,
        gas_quality_source_coverage_frame,
        gas_quality_source_point_options,
        gas_quality_type_summary_frame,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Gas Quality And Composition

            **Dashboard brief**: **Dashboard intent**: Analytical. Operators
            and analysts use this dashboard to inspect gas quality and
            composition observations from
            `silver.gas_model.silver_gas_fact_gas_quality`, including quality
            types, units, quantities, gas dates, gas intervals, source points,
            and source-system fields. Freshness, load timing, cache status, and
            bounded preview policy come from the shared gas model loader.
            Missing LocalStack/AWS data and filter matches with no rows render
            as designed empty states instead of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel("gas-quality-composition")),
        ]
    )
    return


@app.cell
def _():
    gas_quality_load_cache = {}
    return (gas_quality_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_gas_quality_table,
    discover_dashboard_config,
    gas_quality_load_cache,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    gas_quality_load = cached_load_gas_quality_table(
        config,
        gas_quality_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, gas_quality_load


@app.cell
def _(gas_quality_load, gas_table_load_status_frame, gas_table_load_status_message, mo):
    quality_loads = [gas_quality_load]
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(quality_loads)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "Gas quality read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(quality_loads),
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
                "silver/gas_model/silver_gas_fact_gas_quality",
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
    GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
    GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
    gas_quality_load,
    gas_quality_quality_type_options,
    gas_quality_source_point_options,
    mo,
):
    quality_type_filter = mo.ui.dropdown(
        options=gas_quality_quality_type_options(gas_quality_load),
        value=GAS_QUALITY_QUALITY_TYPE_FILTER_ALL,
        searchable=True,
        label="Quality type",
        full_width=True,
    )
    source_point_filter = mo.ui.dropdown(
        options=gas_quality_source_point_options(gas_quality_load),
        value=GAS_QUALITY_SOURCE_POINT_FILTER_ALL,
        searchable=True,
        label="Source point",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack([quality_type_filter, source_point_filter], gap=1),
        ],
        gap=0.5,
    )
    return quality_type_filter, source_point_filter


@app.cell
def _(
    gas_quality_empty_state_markdown,
    gas_quality_kpi_frame,
    gas_quality_load,
    mo,
    quality_type_filter,
    source_point_filter,
):
    kpis = gas_quality_kpi_frame(
        gas_quality_load,
        quality_type_filter.value,
        source_point_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(gas_quality_empty_state_markdown(gas_quality_load))
    else:
        kpi_view = mo.ui.table(kpis, selection=None)

    mo.vstack(
        [
            mo.md("## Observation Summary"),
            kpi_view,
        ]
    )
    return


@app.cell
def _(
    gas_quality_empty_state_markdown,
    gas_quality_load,
    gas_quality_type_summary_frame,
    mo,
    quality_type_filter,
    source_point_filter,
):
    type_summary = gas_quality_type_summary_frame(
        gas_quality_load,
        quality_type_filter.value,
        source_point_filter.value,
    )
    if type_summary.is_empty():
        type_summary_view = mo.md(gas_quality_empty_state_markdown(gas_quality_load))
    else:
        type_summary_view = mo.ui.table(type_summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Quality Type And Unit Summary

            Quantity metrics summarize the currently loaded bounded rows by
            `quality_type` and `unit`.
            """),
            type_summary_view,
        ]
    )
    return


@app.cell
def _(
    gas_quality_empty_state_markdown,
    gas_quality_load,
    gas_quality_observation_frame,
    mo,
    quality_type_filter,
    source_point_filter,
):
    observations = gas_quality_observation_frame(
        gas_quality_load,
        quality_type_filter.value,
        source_point_filter.value,
    )
    if observations.is_empty():
        observation_view = mo.md(gas_quality_empty_state_markdown(gas_quality_load))
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
                ## Filtered Observations

                Quality type: `{quality_type_filter.value}`. Source point:
                `{source_point_filter.value}`. The table is capped to the
                dashboard preview rows after the shared bounded source read.
                """
            ),
            observation_view,
        ]
    )
    return


@app.cell
def _(
    gas_quality_empty_state_markdown,
    gas_quality_load,
    gas_quality_source_coverage_frame,
    mo,
    quality_type_filter,
    source_point_filter,
):
    source_coverage = gas_quality_source_coverage_frame(
        gas_quality_load,
        quality_type_filter.value,
        source_point_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(gas_quality_empty_state_markdown(gas_quality_load))
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage groups observations by `source_system` and `source_table`,
            with quality type, unit, source point, gas-date, source-update, and
            ingest coverage for the currently loaded rows.
            """),
            mo.accordion(
                {"Gas quality source coverage detail": source_coverage_view},
                multiple=False,
                lazy=True,
            ),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
