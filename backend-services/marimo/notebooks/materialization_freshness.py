import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import render_dashboard_context_panel
    from marimoserver.gas_model_loader import refresh_token_from_control
    from marimoserver.table_explorer import (
        MaterializationFreshnessState,
        build_materialization_freshness_summary,
        discover_storage,
        discover_table_catalogue,
        discover_table_explorer_config,
        filter_materialization_freshness_rows,
        materialization_freshness_action_markdown,
        materialization_freshness_frame,
        materialization_freshness_rows,
        materialization_group_freshness_frame,
        materialization_layer_freshness_frame,
        overlay_table_catalogue,
        render_materialization_freshness_status_cards,
    )

    return (
        MaterializationFreshnessState,
        build_materialization_freshness_summary,
        discover_storage,
        discover_table_catalogue,
        discover_table_explorer_config,
        filter_materialization_freshness_rows,
        materialization_freshness_action_markdown,
        materialization_freshness_frame,
        materialization_freshness_rows,
        materialization_group_freshness_frame,
        materialization_layer_freshness_frame,
        mo,
        overlay_table_catalogue,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_materialization_freshness_status_cards,
    )


@app.cell
def _(mo):
    mo.vstack(
        [
            mo.Html("""
            <style>
            @media (max-width: 640px) {
                h1:first-of-type {
                    margin-top: 2.8rem;
                }
            }
            </style>
            """),
            mo.md("""
            # Materialization Freshness

            **Dashboard brief**: **Dashboard intent**: Operational. Platform
            operators and data engineers use this dashboard to find stale,
            unmaterialized, GraphQL-unavailable, and storage-missing table-like
            Dagster assets. Data scope is read-only Dagster GraphQL table asset
            metadata plus configured S3-compatible storage overlay status.
            Freshness comes from latest Dagster materialization timestamps and
            calculated gaps at notebook refresh time. Filters use catalogue
            metadata only; the dashboard does not scan table contents or change
            Dagster definitions, schedules, materialization behavior, ETL code,
            or AWS deployment settings.
            """),
        ]
    )
    return


@app.cell
def _(mo):
    refresh_freshness_button = mo.ui.run_button(label="Refresh freshness")
    refresh_freshness_button
    return (refresh_freshness_button,)


@app.cell
def _(
    build_materialization_freshness_summary,
    discover_storage,
    discover_table_catalogue,
    discover_table_explorer_config,
    materialization_freshness_rows,
    overlay_table_catalogue,
    refresh_freshness_button,
    refresh_token_from_control,
):
    config = discover_table_explorer_config()
    refresh_token = refresh_token_from_control(refresh_freshness_button)
    storage_discovery = discover_storage(config)
    catalogue = discover_table_catalogue(config)
    table_catalogue = overlay_table_catalogue(storage_discovery, catalogue)
    freshness_rows = materialization_freshness_rows(table_catalogue)
    summary = build_materialization_freshness_summary(catalogue, freshness_rows)
    return catalogue, config, freshness_rows, refresh_token, summary, table_catalogue


@app.cell
def _(
    materialization_freshness_action_markdown,
    mo,
    render_materialization_freshness_status_cards,
    summary,
):
    action_kind = "neutral" if summary.degraded_count == 0 else "warn"
    mo.vstack(
        [
            mo.Html(render_materialization_freshness_status_cards(summary)),
            mo.callout(
                mo.md(materialization_freshness_action_markdown(summary)),
                kind=action_kind,
            ),
        ]
    )
    return


@app.cell
def _(config, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "Runtime",
                "Dagster GraphQL",
                "AWS endpoint",
                "AWS region",
                "Configured buckets",
                "Filtering policy",
            ],
            "value": [
                config.runtime_location,
                config.dagster_graphql_url,
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                ", ".join(config.default_buckets),
                "Catalogue metadata only; no table-content scans",
            ],
        }
    )
    mo.vstack(
        [
            mo.md("## Runtime Configuration"),
            mo.ui.table(config_frame, selection=None),
        ]
    )
    return


@app.cell
def _(MaterializationFreshnessState, freshness_rows, mo):
    group_options = tuple(sorted({row.group for row in freshness_rows if row.group}))
    layer_options = tuple(
        sorted(
            {
                layer_or_domain
                for row in freshness_rows
                for layer_or_domain in row.layers_or_domains
            }
        )
    )
    state_options = tuple(state.value for state in MaterializationFreshnessState)
    group_filter = mo.ui.multiselect(
        options=group_options,
        value=[],
        label="Asset group",
        full_width=True,
    )
    layer_filter = mo.ui.multiselect(
        options=layer_options,
        value=[],
        label="Layer or domain",
        full_width=True,
    )
    state_filter = mo.ui.multiselect(
        options=state_options,
        value=[],
        label="Freshness state",
        full_width=True,
    )
    minimum_gap_hours = mo.ui.slider(
        start=0,
        stop=168,
        step=1,
        value=0,
        label="Minimum freshness gap hours",
    )
    asset_search = mo.ui.text(
        placeholder="Search asset, group, layer, state, URI, bucket, or prefix",
        label="Asset search",
        debounce=False,
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Freshness Controls"),
            group_filter,
            layer_filter,
            state_filter,
            minimum_gap_hours,
            asset_search,
        ]
    )
    return asset_search, group_filter, layer_filter, minimum_gap_hours, state_filter


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.Html(render_dashboard_context_panel("materialization-freshness"))
    return


@app.cell
def _(
    asset_search,
    filter_materialization_freshness_rows,
    freshness_rows,
    group_filter,
    layer_filter,
    minimum_gap_hours,
    state_filter,
):
    filtered_freshness_rows = filter_materialization_freshness_rows(
        freshness_rows,
        groups=tuple(group_filter.value),
        layers_or_domains=tuple(layer_filter.value),
        states=tuple(state_filter.value),
        search=asset_search.value,
        minimum_gap_hours=float(minimum_gap_hours.value),
    )
    return (filtered_freshness_rows,)


@app.cell
def _(
    filtered_freshness_rows,
    materialization_group_freshness_frame,
    materialization_layer_freshness_frame,
    mo,
):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Freshness by Group and Layer

                Showing grouped freshness for `{len(filtered_freshness_rows)}`
                metadata rows after filters.
                """
            ),
            mo.ui.table(
                materialization_group_freshness_frame(filtered_freshness_rows),
                selection=None,
            ),
            mo.ui.table(
                materialization_layer_freshness_frame(filtered_freshness_rows),
                selection=None,
            ),
        ]
    )
    return


@app.cell
def _(filtered_freshness_rows, materialization_freshness_frame, mo, summary):
    if summary.row_count == 0:
        detail = "No Dagster table assets or storage prefixes were discovered."
    else:
        detail = (
            f"Showing `{len(filtered_freshness_rows)}` of "
            f"`{summary.row_count}` freshness rows."
        )

    mo.vstack(
        [
            mo.md(f"## Asset Freshness Detail\n\n{detail}"),
            mo.ui.table(
                materialization_freshness_frame(filtered_freshness_rows),
                selection=None,
                page_size=20,
            ),
        ]
    )
    return


@app.cell
def _(catalogue, mo):
    graphql_detail = (
        f"Dagster GraphQL endpoint: `{catalogue.url}`"
        if catalogue.error is None
        else f"Dagster GraphQL unavailable at `{catalogue.url}`: `{catalogue.error}`"
    )
    mo.md(
        f"""
        ## GraphQL Detail

        {graphql_detail}

        This dashboard is read-only. It does not preview table rows or mutate
        Dagster, S3-compatible storage, ETL code, or AWS deployment settings.
        """
    )
    return


if __name__ == "__main__":
    app.run()
