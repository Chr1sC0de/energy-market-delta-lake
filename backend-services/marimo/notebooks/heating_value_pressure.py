import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        HEATING_VALUE_PRESSURE_CONTEXT_ID,
        HEATING_VALUE_PRESSURE_IDENTIFIER_FILTER_ALL,
        HEATING_VALUE_PRESSURE_SOURCE_SYSTEM_FILTER_ALL,
        HEATING_VALUE_PRESSURE_SOURCE_TABLE_FILTER_ALL,
        cached_load_heating_value_pressure_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        heating_value_observation_frame,
        heating_value_pressure_empty_state_markdown,
        heating_value_pressure_field_summary_frame,
        heating_value_pressure_identifier_frame,
        heating_value_pressure_identifier_options,
        heating_value_pressure_kpi_frame,
        heating_value_pressure_source_coverage_frame,
        heating_value_pressure_source_system_options,
        heating_value_pressure_source_table_options,
        render_dashboard_context_panel,
        render_heating_value_pressure_context_links,
        scada_pressure_observation_frame,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        HEATING_VALUE_PRESSURE_CONTEXT_ID,
        HEATING_VALUE_PRESSURE_IDENTIFIER_FILTER_ALL,
        HEATING_VALUE_PRESSURE_SOURCE_SYSTEM_FILTER_ALL,
        HEATING_VALUE_PRESSURE_SOURCE_TABLE_FILTER_ALL,
        cached_load_heating_value_pressure_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        heating_value_observation_frame,
        heating_value_pressure_empty_state_markdown,
        heating_value_pressure_field_summary_frame,
        heating_value_pressure_identifier_frame,
        heating_value_pressure_identifier_options,
        heating_value_pressure_kpi_frame,
        heating_value_pressure_source_coverage_frame,
        heating_value_pressure_source_system_options,
        heating_value_pressure_source_table_options,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_heating_value_pressure_context_links,
        scada_pressure_observation_frame,
    )


@app.cell
def _(mo):
    mo.md("""
    # Heating Value And SCADA Pressure

    **Dashboard brief**: **Dashboard intent**: Analytical. Operators and
    analysts use this dashboard to inspect bounded heating value and SCADA
    pressure observations from the silver gas model facts. It summarizes
    heating value fields, pressure fields, gas date/time fields, and source
    coverage while explicitly labeling source-qualified zone and node
    identifiers because these facts do not currently carry conformed dimension
    keys. Freshness, load timing, cache status, and bounded preview policy come
    from the shared gas model loader. Missing LocalStack/AWS data and filter
    matches with no rows render as designed empty states instead of notebook
    tracebacks.
    """)
    return


@app.cell
def _():
    heating_value_pressure_load_cache = {}
    return (heating_value_pressure_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_heating_value_pressure_tables,
    discover_dashboard_config,
    heating_value_pressure_load_cache,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    heating_value_pressure_loads = cached_load_heating_value_pressure_tables(
        config,
        heating_value_pressure_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, heating_value_pressure_loads


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    heating_value_pressure_loads,
    mo,
):
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(heating_value_pressure_loads)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "Heating value and pressure read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(heating_value_pressure_loads),
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
    HEATING_VALUE_PRESSURE_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_heating_value_pressure_context_links,
):
    mo.vstack(
        [
            mo.Html(render_dashboard_context_panel(HEATING_VALUE_PRESSURE_CONTEXT_ID)),
            mo.Html(render_heating_value_pressure_context_links()),
        ]
    )
    return


@app.cell
def _(config, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Heating value table",
                "SCADA pressure table",
                "AWS endpoint",
                "AWS region",
                "Environment",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                "silver/gas_model/silver_gas_fact_heating_value",
                "silver/gas_model/silver_gas_fact_scada_pressure",
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
    HEATING_VALUE_PRESSURE_IDENTIFIER_FILTER_ALL,
    HEATING_VALUE_PRESSURE_SOURCE_SYSTEM_FILTER_ALL,
    HEATING_VALUE_PRESSURE_SOURCE_TABLE_FILTER_ALL,
    heating_value_pressure_identifier_options,
    heating_value_pressure_loads,
    heating_value_pressure_source_system_options,
    heating_value_pressure_source_table_options,
    mo,
):
    source_system_filter = mo.ui.dropdown(
        options=heating_value_pressure_source_system_options(
            heating_value_pressure_loads
        ),
        value=HEATING_VALUE_PRESSURE_SOURCE_SYSTEM_FILTER_ALL,
        searchable=True,
        label="Source system",
        full_width=True,
    )
    source_table_filter = mo.ui.dropdown(
        options=heating_value_pressure_source_table_options(
            heating_value_pressure_loads
        ),
        value=HEATING_VALUE_PRESSURE_SOURCE_TABLE_FILTER_ALL,
        searchable=True,
        label="Source table",
        full_width=True,
    )
    identifier_filter = mo.ui.dropdown(
        options=heating_value_pressure_identifier_options(heating_value_pressure_loads),
        value=HEATING_VALUE_PRESSURE_IDENTIFIER_FILTER_ALL,
        searchable=True,
        label="Source-qualified identifier",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Filters"),
            mo.hstack(
                [source_system_filter, source_table_filter, identifier_filter],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return identifier_filter, source_system_filter, source_table_filter


@app.cell
def _(
    heating_value_pressure_empty_state_markdown,
    heating_value_pressure_kpi_frame,
    heating_value_pressure_loads,
    identifier_filter,
    mo,
    source_system_filter,
    source_table_filter,
):
    kpis = heating_value_pressure_kpi_frame(
        heating_value_pressure_loads,
        source_system_filter.value,
        source_table_filter.value,
        identifier_filter.value,
    )
    if kpis.is_empty():
        kpi_view = mo.md(
            heating_value_pressure_empty_state_markdown(heating_value_pressure_loads)
        )
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
    heating_value_pressure_empty_state_markdown,
    heating_value_pressure_field_summary_frame,
    heating_value_pressure_loads,
    identifier_filter,
    mo,
    source_system_filter,
    source_table_filter,
):
    field_summary = heating_value_pressure_field_summary_frame(
        heating_value_pressure_loads,
        source_system_filter.value,
        source_table_filter.value,
        identifier_filter.value,
    )
    if field_summary.is_empty():
        field_summary_view = mo.md(
            heating_value_pressure_empty_state_markdown(heating_value_pressure_loads)
        )
    else:
        field_summary_view = mo.ui.table(field_summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Field Coverage

            Coverage summarizes loaded heating value, pressure, Gas Day,
            measurement timestamp, source update, and source identifier fields
            after the current filters.
            """),
            field_summary_view,
        ]
    )
    return


@app.cell
def _(
    heating_value_pressure_empty_state_markdown,
    heating_value_pressure_identifier_frame,
    heating_value_pressure_loads,
    identifier_filter,
    mo,
    source_system_filter,
    source_table_filter,
):
    identifier_summary = heating_value_pressure_identifier_frame(
        heating_value_pressure_loads,
        source_system_filter.value,
        source_table_filter.value,
        identifier_filter.value,
    )
    if identifier_summary.is_empty():
        identifier_view = mo.md(
            heating_value_pressure_empty_state_markdown(heating_value_pressure_loads)
        )
    else:
        identifier_view = mo.ui.table(identifier_summary, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source-Qualified Identifiers

            The heating value fact uses `source_zone_id` and the pressure fact
            uses `source_node_id`. These rows intentionally do not imply
            conformed zone, point, or operational dimension relationships.
            """),
            identifier_view,
        ]
    )
    return


@app.cell
def _(
    heating_value_pressure_empty_state_markdown,
    heating_value_pressure_loads,
    heating_value_pressure_source_coverage_frame,
    identifier_filter,
    mo,
    source_system_filter,
    source_table_filter,
):
    source_coverage = heating_value_pressure_source_coverage_frame(
        heating_value_pressure_loads,
        source_system_filter.value,
        source_table_filter.value,
        identifier_filter.value,
    )
    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            heating_value_pressure_empty_state_markdown(heating_value_pressure_loads)
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Source Coverage

            Coverage groups observations by fact, `source_system`, and
            `source_table`, with source-qualified identifier counts, measure
            coverage, Gas Day, pressure measurement, source-update, and ingest
            freshness where those fields are present.
            """),
            source_coverage_view,
        ]
    )
    return


@app.cell
def _(
    heating_value_observation_frame,
    heating_value_pressure_empty_state_markdown,
    heating_value_pressure_loads,
    identifier_filter,
    mo,
    source_system_filter,
    source_table_filter,
):
    heating_observations = heating_value_observation_frame(
        heating_value_pressure_loads,
        source_system_filter.value,
        source_table_filter.value,
        identifier_filter.value,
    )
    if heating_observations.is_empty():
        heating_view = mo.md(
            heating_value_pressure_empty_state_markdown(heating_value_pressure_loads)
        )
    else:
        heating_view = mo.ui.table(
            heating_observations,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md(
                f"""
                ## Heating Value Observations

                Source system: `{source_system_filter.value}`. Source table:
                `{source_table_filter.value}`. Source-qualified identifier:
                `{identifier_filter.value}`. The table is capped to the
                dashboard preview rows after the shared bounded source read.
                """
            ),
            heating_view,
        ]
    )
    return


@app.cell
def _(
    heating_value_pressure_empty_state_markdown,
    heating_value_pressure_loads,
    identifier_filter,
    mo,
    scada_pressure_observation_frame,
    source_system_filter,
    source_table_filter,
):
    pressure_observations = scada_pressure_observation_frame(
        heating_value_pressure_loads,
        source_system_filter.value,
        source_table_filter.value,
        identifier_filter.value,
    )
    if pressure_observations.is_empty():
        pressure_view = mo.md(
            heating_value_pressure_empty_state_markdown(heating_value_pressure_loads)
        )
    else:
        pressure_view = mo.ui.table(
            pressure_observations,
            selection=None,
            page_size=20,
        )

    mo.vstack(
        [
            mo.md(
                f"""
                ## SCADA Pressure Observations

                Source system: `{source_system_filter.value}`. Source table:
                `{source_table_filter.value}`. Source-qualified identifier:
                `{identifier_filter.value}`. The table is capped to the
                dashboard preview rows after the shared bounded source read.
                """
            ),
            pressure_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
