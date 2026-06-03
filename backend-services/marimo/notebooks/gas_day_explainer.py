import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        GAS_DAY_CONTEXT_ID,
        cached_load_gas_day_tables,
        discover_dashboard_config,
        gas_day_bounded_examples_frame,
        gas_day_examples_empty_state_markdown,
        gas_day_field_discovery_frame,
        gas_day_kpi_frame,
        gas_day_table_specs,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        render_dashboard_context_panel,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        GAS_DAY_CONTEXT_ID,
        cached_load_gas_day_tables,
        discover_dashboard_config,
        gas_day_bounded_examples_frame,
        gas_day_examples_empty_state_markdown,
        gas_day_field_discovery_frame,
        gas_day_kpi_frame,
        gas_day_table_specs,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
    )


@app.cell
def _(GAS_DAY_CONTEXT_ID, mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Gas Day Explainer

            **Dashboard brief**: **Dashboard intent**: Analytical. Analysts,
            stakeholders, and data engineers use this dashboard to inspect the
            cited Gas Day Market context metadata, locate date and gas-date
            fields across current registry-backed `silver.gas_model` assets,
            and review bounded examples from loaded curated rows. Data scope is
            the Marimo dashboard registry, Market context ID and source chunk
            metadata copied into that registry, plus read-only bounded Parquet
            samples under `silver/gas_model`. Freshness, row coverage, cache
            status, load timing, and missing-source behavior come from the
            shared gas model loader; unavailable or empty data renders as
            designed empty states instead of notebook tracebacks.
            """),
            mo.Html(render_dashboard_context_panel(GAS_DAY_CONTEXT_ID)),
        ]
    )
    return


@app.cell
def _():
    gas_day_load_cache = {}
    return (gas_day_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_gas_day_tables,
    discover_dashboard_config,
    gas_day_load_cache,
    gas_day_table_specs,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    gas_day_specs = gas_day_table_specs()
    gas_day_loads = cached_load_gas_day_tables(
        config,
        gas_day_load_cache,
        specs=gas_day_specs,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, gas_day_loads, gas_day_specs


@app.cell
def _(gas_day_bounded_examples_frame, gas_day_field_discovery_frame, gas_day_loads):
    field_discovery = gas_day_field_discovery_frame(gas_day_loads)
    bounded_examples = gas_day_bounded_examples_frame(gas_day_loads)
    return bounded_examples, field_discovery


@app.cell
def _(bounded_examples, field_discovery, gas_day_kpi_frame, gas_day_loads):
    gas_day_kpis = gas_day_kpi_frame(
        gas_day_loads,
        field_discovery,
        bounded_examples,
    )
    return (gas_day_kpis,)


@app.cell
def _(gas_day_loads, gas_table_load_status_frame, gas_table_load_status_message, mo):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(gas_day_loads)}
                """
            ),
            mo.accordion(
                {
                    "Gas Day read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(gas_day_loads),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(config, gas_day_kpis, gas_day_specs, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet root",
                "Registry-backed assets",
                "Market context ID",
                "Source chunk ID",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                str(len(gas_day_specs)),
                "glossary:gas-day",
                "chunk-gbb-guide-gas-day",
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.vstack(
        [
            mo.md("## Gas Day Coverage Health"),
            mo.accordion(
                {"Gas day coverage details": mo.ui.table(gas_day_kpis, selection=None)},
                lazy=True,
                multiple=False,
            ),
            mo.accordion(
                {"Coverage inputs": mo.ui.table(config_frame, selection=None)},
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(field_discovery, mo, pl):
    if field_discovery.is_empty():
        field_role_filter = None
        field_search = None
        controls = mo.md("")
    else:
        role_options = sorted(
            value
            for value in field_discovery.get_column("field role")
            .drop_nulls()
            .cast(pl.String)
            .unique()
            .to_list()
            if value
        )
        field_role_filter = mo.ui.multiselect(
            options=role_options,
            value=[],
            label="Field role",
            full_width=True,
        )
        field_search = mo.ui.text(
            placeholder="Search asset, table, field, dtype, status, or detail",
            label="Field search",
            full_width=True,
        )
        controls = mo.vstack(
            [
                mo.md("## Field Controls"),
                mo.hstack([field_role_filter, field_search], gap=1),
            ],
            gap=0.5,
        )

    controls
    return field_role_filter, field_search


@app.cell
def _(field_discovery, field_role_filter, field_search, pl):
    filtered_field_discovery = field_discovery
    if field_role_filter is not None and len(field_role_filter.value) > 0:
        filtered_field_discovery = filtered_field_discovery.filter(
            pl.col("field role").is_in(tuple(field_role_filter.value))
        )
    if field_search is not None and field_search.value.strip():
        _search_term = field_search.value.strip().lower()
        filtered_field_discovery = filtered_field_discovery.filter(
            pl.any_horizontal(
                pl.col("asset")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
                pl.col("table")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
                pl.col("field")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
                pl.col("dtype")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
                pl.col("status")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
                pl.col("detail")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
            )
        )
    return (filtered_field_discovery,)


@app.cell
def _(filtered_field_discovery, mo):
    mo.vstack(
        [
            mo.md("""
            ## Date And Gas-Date Fields

            Field discovery combines known dashboard date metadata with the
            columns present in the bounded table reads. `gas_date`,
            `from_gas_date`, and `to_gas_date` are marked as Gas Day fields;
            date keys, timestamps, and other date columns remain visible as
            related date context.
            """),
            mo.ui.table(filtered_field_discovery, selection=None),
        ]
    )
    return


@app.cell
def _(
    bounded_examples,
    field_role_filter,
    field_search,
    gas_day_examples_empty_state_markdown,
    gas_day_loads,
    mo,
    pl,
):
    filtered_examples = bounded_examples
    if field_role_filter is not None and len(field_role_filter.value) > 0:
        filtered_examples = filtered_examples.filter(
            pl.col("field role").is_in(tuple(field_role_filter.value))
        )
    if field_search is not None and field_search.value.strip():
        _search_term = field_search.value.strip().lower()
        filtered_examples = filtered_examples.filter(
            pl.any_horizontal(
                pl.col("asset")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
                pl.col("table")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
                pl.col("field")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
                pl.col("value")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
                pl.col("context")
                .str.to_lowercase()
                .str.contains(_search_term, literal=True),
            )
        )

    if filtered_examples.is_empty():
        examples_view = mo.md(gas_day_examples_empty_state_markdown(gas_day_loads))
    else:
        examples_view = mo.ui.table(filtered_examples, selection=None)

    mo.vstack(
        [
            mo.md("""
            ## Bounded Examples

            Examples are selected from already bounded table reads. Gas Day
            fields are preferred; tables without a Gas Day field fall back to
            their discovered date fields so available data remains inspectable.
            """),
            examples_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
