import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        cached_load_gas_model_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
        render_kpi_cards_html,
        table_load_by_name,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        cached_load_gas_model_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        render_dashboard_context_panel,
        render_kpi_cards_html,
        refresh_token_from_control,
        table_load_by_name,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Local Gas Market Overview

            **Dashboard brief**: **Dashboard intent**: Operational. Operators
            and analysts use this dashboard to inspect curated gas market
            prices, schedules, flow, capacity, and source coverage from
            configured `silver.gas_model` tables. Freshness and row coverage
            come from loaded table metadata; empty or missing LocalStack inputs
            are shown as designed unavailable states.
            """),
            mo.Html(render_dashboard_context_panel("gas-market-overview")),
        ]
    )
    return


@app.cell
def _():
    gas_model_load_cache = {}
    return gas_model_load_cache


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return refresh_data_button


@app.cell
def _(
    cached_load_gas_model_tables,
    discover_dashboard_config,
    gas_model_load_cache,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    loaded_tables = cached_load_gas_model_tables(
        config,
        gas_model_load_cache,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, loaded_tables


@app.cell
def _(gas_table_load_status_frame, gas_table_load_status_message, loaded_tables, mo):
    mo.vstack(
        [
            mo.callout(
                mo.md(gas_table_load_status_message(loaded_tables)),
                kind="neutral",
            ),
            mo.accordion(
                {
                    "Table read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(loaded_tables),
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
                "Parquet root",
                "AWS endpoint",
                "AWS region",
                "Environment",
                "Name prefix",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                config.development_environment,
                config.name_prefix,
            ],
        }
    )

    mo.vstack(
        [
            mo.md(
                """
                ## Configuration

                The dashboard uses the same S3-compatible settings as the
                Marimo service. Bucket discovery prefers `AEMO_BUCKET` when it is
                set, otherwise it derives the bucket from
                `DEVELOPMENT_ENVIRONMENT` and `NAME_PREFIX`.
                """
            ),
            mo.ui.table(config_frame),
        ]
    )
    return


@app.cell
def _(pl):  # noqa: C901
    def date_range(load):
        dataframe = load.dataframe
        if dataframe is None or dataframe.is_empty():
            return "No rows"

        for column in load.spec.date_columns:
            if column not in dataframe.columns:
                continue

            values = dataframe.get_column(column).drop_nulls()
            if values.is_empty():
                continue

            return f"{values.min()} to {values.max()}"

        return "No date column"

    def latest_ingest(load):
        dataframe = load.dataframe
        if (
            dataframe is None
            or dataframe.is_empty()
            or "ingested_timestamp" not in dataframe.columns
        ):
            return ""

        values = dataframe.get_column("ingested_timestamp").drop_nulls()
        if values.is_empty():
            return ""
        return str(values.max())

    def source_values(dataframe, column):
        if column not in dataframe.columns:
            return []
        return sorted(
            str(value)
            for value in dataframe.get_column(column).drop_nulls().unique().to_list()
            if value is not None
        )

    def source_table_values(dataframe):
        if "source_table" in dataframe.columns:
            return source_values(dataframe, "source_table")
        if "source_tables" not in dataframe.columns:
            return []

        exploded = dataframe.select(
            pl.col("source_tables").explode().alias("source_table")
        ).drop_nulls()
        if exploded.is_empty():
            return []
        return sorted(
            str(value)
            for value in exploded.get_column("source_table").unique().to_list()
            if value is not None
        )

    def source_count(load):
        dataframe = load.dataframe
        if dataframe is None or dataframe.is_empty():
            return 0
        return len(source_table_values(dataframe))

    def summary_frame(loads):
        rows = []
        for load in loads:
            dataframe = load.dataframe
            row_count = dataframe.height if dataframe is not None else 0
            rows.append(
                {
                    "section": load.spec.section,
                    "asset": load.spec.table_name,
                    "status": "Available" if load.available else "Empty or missing",
                    "rows": row_count,
                    "source tables": source_count(load),
                    "date range": date_range(load),
                    "latest ingest": latest_ingest(load),
                    "uri": load.uri,
                }
            )
        return pl.DataFrame(rows)

    def sample_summary_kpi_frame(summary):
        if summary.is_empty():
            return pl.DataFrame(
                schema={"metric": pl.String, "value": pl.String, "detail": pl.String}
            )

        available = summary.filter(pl.col("status") == "Available")
        latest_ingests = [
            value
            for value in summary.get_column("latest ingest").drop_nulls().to_list()
            if str(value)
        ]
        return pl.DataFrame(
            [
                {
                    "metric": "Available gas_model outputs",
                    "value": f"{available.height:,}",
                    "detail": f"{summary.height:,} configured dashboard input tables checked",
                },
                {
                    "metric": "Loaded rows",
                    "value": f"{int(summary.get_column('rows').sum() or 0):,}",
                    "detail": "Rows available across the loaded sample tables",
                },
                {
                    "metric": "Represented source tables",
                    "value": f"{int(summary.get_column('source tables').sum() or 0):,}",
                    "detail": "Source-table references across loaded dashboard inputs",
                },
                {
                    "metric": "Latest ingest",
                    "value": max(latest_ingests) if latest_ingests else "unknown",
                    "detail": "Maximum ingested_timestamp across loaded tables",
                },
            ]
        )

    def select_preview(load, limit=50):
        dataframe = load.dataframe
        if dataframe is None or dataframe.is_empty():
            return pl.DataFrame()

        columns = [
            column
            for column in load.spec.preview_columns
            if column in dataframe.columns
        ]
        preview = dataframe.select(columns) if columns else dataframe

        for column in load.spec.date_columns:
            if column in preview.columns:
                preview = preview.sort(column, descending=True, nulls_last=True)
                break

        return preview.head(limit)

    def empty_state(title, table_names):
        table_list = "\n".join(f"- `{table_name}`" for table_name in table_names)
        return f"""
        ## {title}

        **No data is available for this section yet.**

        The dashboard checked these `silver.gas_model` outputs:

        {table_list}

        Materialize the gas_model assets in Dagster or load the curated outputs,
        then refresh this notebook.
        """

    def section_stack(mo, title, load, description, summary_view=None):
        if load is None or not load.available:
            table_names = [] if load is None else [load.spec.table_name]
            return mo.md(empty_state(title, table_names))

        elements = [
            mo.md(
                f"""
                ## {title}

                {description}

                - Rows: `{load.dataframe.height}`
                - Source tables: `{source_count(load)}`
                - Date range: `{date_range(load)}`
                - Latest ingest: `{latest_ingest(load) or "unknown"}`
                """
            )
        ]
        if summary_view is not None:
            elements.append(summary_view)
        elements.append(mo.ui.table(select_preview(load)))
        return mo.vstack(elements)

    def price_summary_frame(load):
        if load is None:
            return pl.DataFrame()

        dataframe = load.dataframe
        if dataframe is None or dataframe.is_empty():
            return pl.DataFrame()

        groups = [
            column
            for column in ("source_system", "price_type")
            if column in dataframe.columns
        ]
        if not groups:
            return pl.DataFrame()

        aggregations = [pl.len().alias("rows")]
        if "gas_date" in dataframe.columns:
            aggregations.append(pl.col("gas_date").max().alias("latest gas date"))
        for column in (
            "price_value_gst_ex",
            "weighted_average_price_gst_ex",
            "cumulative_price",
            "administered_price",
        ):
            if column in dataframe.columns:
                aggregations.append(
                    pl.col(column).mean().round(2).alias(f"avg {column}")
                )

        return (
            dataframe.group_by(groups).agg(aggregations).sort("rows", descending=True)
        )

    def price_kpi_frame(summary):
        if summary.is_empty():
            return pl.DataFrame(
                schema={"metric": pl.String, "value": pl.String, "detail": pl.String}
            )

        price_measure_columns = [
            column for column in summary.columns if column.startswith("avg ")
        ]
        rows = [
            {
                "metric": "Price groups",
                "value": f"{summary.height:,}",
                "detail": "Source-system and price-type groups in the loaded sample",
            },
            {
                "metric": "Loaded price rows",
                "value": f"{int(summary.get_column('rows').sum() or 0):,}",
                "detail": "Market-price rows represented by grouped summaries",
            },
        ]
        if "latest gas date" in summary.columns:
            rows.append(
                {
                    "metric": "Latest gas date",
                    "value": str(summary.get_column("latest gas date").max()),
                    "detail": "Maximum gas_date across loaded market-price rows",
                }
            )
        rows.append(
            {
                "metric": "Price measures",
                "value": f"{len(price_measure_columns):,}",
                "detail": ", ".join(
                    column.removeprefix("avg ") for column in price_measure_columns
                )
                or "No price measure columns",
            }
        )
        return pl.DataFrame(rows)

    def scheduled_quantity_summary_frame(load):
        if load is None:
            return pl.DataFrame()

        dataframe = load.dataframe
        if dataframe is None or dataframe.is_empty():
            return pl.DataFrame()

        groups = [
            column
            for column in ("source_system", "quantity_type")
            if column in dataframe.columns
        ]
        if not groups:
            return pl.DataFrame()

        aggregations = [pl.len().alias("rows")]
        if "gas_date" in dataframe.columns:
            aggregations.append(pl.col("gas_date").max().alias("latest gas date"))
        if "quantity_gj" in dataframe.columns:
            aggregations.append(pl.col("quantity_gj").sum().round(2).alias("total GJ"))

        return (
            dataframe.group_by(groups).agg(aggregations).sort("rows", descending=True)
        )

    def scheduled_quantity_kpi_frame(summary):
        if summary.is_empty():
            return pl.DataFrame(
                schema={"metric": pl.String, "value": pl.String, "detail": pl.String}
            )

        rows = [
            {
                "metric": "Quantity groups",
                "value": f"{summary.height:,}",
                "detail": "Source-system and quantity-type groups in the loaded sample",
            },
            {
                "metric": "Loaded quantity rows",
                "value": f"{int(summary.get_column('rows').sum() or 0):,}",
                "detail": "Scheduled-quantity rows represented by grouped summaries",
            },
        ]
        if "total GJ" in summary.columns:
            total_gj = summary.get_column("total GJ").sum()
            rows.append(
                {
                    "metric": "Total scheduled quantity",
                    "value": f"{float(total_gj or 0):,.2f}",
                    "detail": "Sum of quantity_gj in loaded sample rows",
                }
            )
        if "latest gas date" in summary.columns:
            rows.append(
                {
                    "metric": "Latest gas date",
                    "value": str(summary.get_column("latest gas date").max()),
                    "detail": "Maximum gas_date across loaded scheduled quantities",
                }
            )
        return pl.DataFrame(rows)

    def metric_total(dataframe, column):
        if dataframe is None or column not in dataframe.columns:
            return None
        values = dataframe.get_column(column).drop_nulls()
        if values.is_empty():
            return None
        return round(float(values.sum()), 2)

    def flow_capacity_summary_frame(loads):
        metric_columns = {
            "silver_gas_fact_connection_point_flow": "actual_quantity_tj",
            "silver_gas_fact_facility_flow_storage": "held_in_storage_tj",
            "silver_gas_fact_linepack": "actual_linepack_gj",
            "silver_gas_fact_capacity_outlook": "capacity_quantity_tj",
            "silver_gas_fact_capacity_auction": "quantity_gj",
        }
        rows = []
        for load in loads:
            if load.spec.table_name not in metric_columns:
                continue

            dataframe = load.dataframe
            row_count = dataframe.height if dataframe is not None else 0
            metric_column = metric_columns[load.spec.table_name]
            rows.append(
                {
                    "asset": load.spec.table_name,
                    "status": "Available" if load.available else "Empty or missing",
                    "rows": row_count,
                    "metric": metric_column,
                    "total": metric_total(dataframe, metric_column),
                    "date range": date_range(load),
                }
            )

        return pl.DataFrame(rows)

    def flow_capacity_kpi_frame(summary):
        if summary.is_empty():
            return pl.DataFrame(
                schema={"metric": pl.String, "value": pl.String, "detail": pl.String}
            )

        available = summary.filter(pl.col("status") == "Available")
        totals = summary.get_column("total").drop_nulls()
        return pl.DataFrame(
            [
                {
                    "metric": "Available flow/capacity assets",
                    "value": f"{available.height:,}",
                    "detail": f"{summary.height:,} configured flow and capacity summary assets checked",
                },
                {
                    "metric": "Loaded flow/capacity rows",
                    "value": f"{int(summary.get_column('rows').sum() or 0):,}",
                    "detail": "Rows available across flow, storage, linepack, and capacity tables",
                },
                {
                    "metric": "Metric totals available",
                    "value": f"{totals.len():,}",
                    "detail": "Assets with a non-null operational metric total",
                },
                {
                    "metric": "Metric columns",
                    "value": f"{summary.get_column('metric').n_unique():,}",
                    "detail": "Distinct flow, storage, linepack, and capacity measures inspected",
                },
            ]
        )

    def source_coverage_frame(loads):
        rows = []
        for load in loads:
            dataframe = load.dataframe
            if dataframe is None or dataframe.is_empty():
                continue

            source_systems = source_values(dataframe, "source_system")
            source_tables = source_table_values(dataframe)
            rows.append(
                {
                    "section": load.spec.section,
                    "asset": load.spec.table_name,
                    "rows": dataframe.height,
                    "source systems": ", ".join(source_systems),
                    "source table count": len(source_tables),
                    "source tables": ", ".join(source_tables),
                }
            )

        return pl.DataFrame(rows)

    return (
        empty_state,
        flow_capacity_kpi_frame,
        flow_capacity_summary_frame,
        price_kpi_frame,
        price_summary_frame,
        sample_summary_kpi_frame,
        scheduled_quantity_summary_frame,
        scheduled_quantity_kpi_frame,
        section_stack,
        select_preview,
        source_coverage_frame,
        summary_frame,
    )


@app.cell
def _(
    loaded_tables, mo, render_kpi_cards_html, sample_summary_kpi_frame, summary_frame
):
    table_summary = summary_frame(loaded_tables)
    table_summary_kpis = sample_summary_kpi_frame(table_summary)

    mo.vstack(
        [
            mo.md(
                """
                ## Gas Model Outputs

                Each row reflects a dashboard input table under
                `silver/gas_model`.
                """
            ),
            mo.Html(
                render_kpi_cards_html(
                    table_summary_kpis,
                    title="Gas model output KPIs",
                )
            ),
        ]
    )
    return


@app.cell
def _(
    loaded_tables,
    mo,
    price_kpi_frame,
    price_summary_frame,
    render_kpi_cards_html,
    section_stack,
    table_load_by_name,
):
    price_load = table_load_by_name(
        loaded_tables,
        "silver_gas_fact_market_price",
    )
    price_summary = price_summary_frame(price_load)
    price_summary_view = None
    if not price_summary.is_empty():
        price_summary_view = mo.vstack(
            [
                mo.md("### Price Summary"),
                mo.Html(
                    render_kpi_cards_html(
                        price_kpi_frame(price_summary),
                        title="Price summary KPIs",
                    )
                ),
            ]
        )

    elements = [
        section_stack(
            mo,
            "Prices",
            price_load,
            "Latest market-price rows across VICGAS and STTM sources.",
            summary_view=price_summary_view,
        )
    ]

    mo.vstack(elements)
    return


@app.cell
def _(
    empty_state,
    loaded_tables,
    mo,
    render_kpi_cards_html,
    scheduled_quantity_kpi_frame,
    scheduled_quantity_summary_frame,
    select_preview,
    table_load_by_name,
):
    schedule_run_load = table_load_by_name(
        loaded_tables,
        "silver_gas_fact_schedule_run",
    )
    scheduled_quantity_load = table_load_by_name(
        loaded_tables,
        "silver_gas_fact_scheduled_quantity",
    )

    schedule_elements = [mo.md("## Schedules")]
    if schedule_run_load is not None and schedule_run_load.available:
        schedule_elements.append(mo.md("### Schedule Runs"))
        schedule_elements.append(mo.ui.table(select_preview(schedule_run_load)))
    if scheduled_quantity_load is not None and scheduled_quantity_load.available:
        quantity_summary = scheduled_quantity_summary_frame(scheduled_quantity_load)
        schedule_elements.append(mo.md("### Scheduled Quantities"))
        if not quantity_summary.is_empty():
            schedule_elements.append(mo.md("### Quantity Summary"))
            schedule_elements.append(
                mo.Html(
                    render_kpi_cards_html(
                        scheduled_quantity_kpi_frame(quantity_summary),
                        title="Scheduled quantity summary KPIs",
                    )
                )
            )
        schedule_elements.append(mo.ui.table(select_preview(scheduled_quantity_load)))

    if len(schedule_elements) == 1:
        schedule_elements = [
            mo.md(
                empty_state(
                    "Schedules",
                    [
                        "silver_gas_fact_schedule_run",
                        "silver_gas_fact_scheduled_quantity",
                    ],
                )
            )
        ]

    mo.vstack(schedule_elements)
    return


@app.cell
def _(
    empty_state,
    flow_capacity_kpi_frame,
    flow_capacity_summary_frame,
    loaded_tables,
    mo,
    render_kpi_cards_html,
    select_preview,
):
    flow_capacity_loads = [
        load for load in loaded_tables if load.spec.section == "Flow and capacity"
    ]
    flow_capacity_summary = flow_capacity_summary_frame(flow_capacity_loads)
    flow_capacity_elements = [
        mo.md(
            """
            ## Flow and Capacity

            Operational flow, storage, linepack, and capacity facts from
            available gas_model outputs.
            """
        )
    ]

    if not flow_capacity_summary.is_empty():
        flow_capacity_elements.append(
            mo.Html(
                render_kpi_cards_html(
                    flow_capacity_kpi_frame(flow_capacity_summary),
                    title="Flow and capacity summary KPIs",
                )
            )
        )

    for load in flow_capacity_loads:
        if load.available:
            flow_capacity_elements.append(mo.md(f"### {load.spec.label}"))
            flow_capacity_elements.append(mo.ui.table(select_preview(load)))

    if len(flow_capacity_elements) == 1:
        flow_capacity_elements = [
            mo.md(
                empty_state(
                    "Flow and Capacity",
                    [load.spec.table_name for load in flow_capacity_loads],
                )
            )
        ]

    mo.vstack(flow_capacity_elements)
    return


@app.cell
def _(empty_state, loaded_tables, mo, source_coverage_frame):
    source_coverage = source_coverage_frame(loaded_tables)

    if source_coverage.is_empty():
        source_coverage_view = mo.md(
            empty_state(
                "Source Coverage",
                [load.spec.table_name for load in loaded_tables],
            )
        )
    else:
        source_coverage_view = mo.ui.table(source_coverage)

    mo.vstack(
        [
            mo.md(
                """
                ## Source Coverage

                Coverage is calculated from `source_system`, `source_table`,
                and `source_tables` fields on the loaded gas_model outputs.
                """
            ),
            mo.accordion(
                {"Overview source coverage detail": source_coverage_view},
                multiple=False,
                lazy=True,
            ),
        ]
    )

    return


if __name__ == "__main__":
    app.run()
