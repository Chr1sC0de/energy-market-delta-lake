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
        TableAvailability,
        asset_catalogue_action_markdown,
        asset_schema_metadata_frame,
        build_asset_catalogue_summary,
        catalogued_table_group,
        discover_storage,
        discover_table_catalogue,
        discover_table_explorer_config,
        filter_catalogued_tables,
        overlay_table_catalogue,
        render_asset_catalogue_status_cards,
        table_asset_catalogue_frame,
    )

    return (
        TableAvailability,
        asset_catalogue_action_markdown,
        asset_schema_metadata_frame,
        build_asset_catalogue_summary,
        catalogued_table_group,
        discover_storage,
        discover_table_catalogue,
        discover_table_explorer_config,
        filter_catalogued_tables,
        mo,
        overlay_table_catalogue,
        pl,
        refresh_token_from_control,
        render_asset_catalogue_status_cards,
        render_dashboard_context_panel,
        table_asset_catalogue_frame,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Dagster Asset Catalogue Status

            **Dashboard brief**: **Dashboard intent**: Operational. Platform
            operators and data engineers use this dashboard to check Dagster
            GraphQL table asset catalogue health, table coverage, asset groups,
            kinds, materializable and executable flags, latest materialization
            metadata, URI coverage, and schema metadata. Data scope is
            read-only Dagster GraphQL plus configured S3-compatible storage
            discovery. Freshness is the latest notebook refresh; GraphQL
            outages render an unavailable state while storage-only rows remain
            visible for local table-prefix triage.
            """),
            mo.Html(render_dashboard_context_panel("dagster-asset-catalogue-status")),
        ]
    )
    return


@app.cell
def _(mo):
    refresh_catalogue_button = mo.ui.run_button(label="Refresh catalogue status")
    refresh_catalogue_button
    return (refresh_catalogue_button,)


@app.cell
def _(
    build_asset_catalogue_summary,
    discover_storage,
    discover_table_catalogue,
    discover_table_explorer_config,
    overlay_table_catalogue,
    refresh_catalogue_button,
    refresh_token_from_control,
):
    config = discover_table_explorer_config()
    refresh_token = refresh_token_from_control(refresh_catalogue_button)
    storage_discovery = discover_storage(config)
    catalogue = discover_table_catalogue(config)
    table_catalogue = overlay_table_catalogue(storage_discovery, catalogue)
    summary = build_asset_catalogue_summary(catalogue, table_catalogue)
    return catalogue, config, refresh_token, summary, table_catalogue


@app.cell
def _(
    asset_catalogue_action_markdown,
    mo,
    render_asset_catalogue_status_cards,
    summary,
):
    action_kind = "neutral" if summary.degraded_table_count == 0 else "warn"
    mo.vstack(
        [
            mo.Html(render_asset_catalogue_status_cards(summary)),
            mo.callout(
                mo.md(asset_catalogue_action_markdown(summary)),
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
                "GraphQL configuration",
                "AWS endpoint",
                "AWS region",
                "Configured buckets",
            ],
            "value": [
                config.runtime_location,
                config.dagster_graphql_url,
                "Configured" if config.dagster_graphql_url else "Missing",
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                ", ".join(config.default_buckets),
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
def _(TableAvailability, catalogued_table_group, mo, table_catalogue):
    group_options = tuple(
        sorted({catalogued_table_group(entry) for entry in table_catalogue})
    )
    status_options = tuple(status.value for status in TableAvailability)
    group_filter = mo.ui.multiselect(
        options=group_options,
        value=[],
        label="Asset group",
        full_width=True,
    )
    status_filter = mo.ui.multiselect(
        options=status_options,
        value=[],
        label="Catalogue status",
        full_width=True,
    )
    asset_search = mo.ui.text(
        placeholder="Search asset, kind, URI, group, bucket, or prefix",
        label="Asset search",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Catalogue Controls"),
            group_filter,
            status_filter,
            asset_search,
        ]
    )
    return asset_search, group_filter, status_filter


@app.cell
def _(
    asset_search,
    filter_catalogued_tables,
    group_filter,
    status_filter,
    table_catalogue,
):
    filtered_catalogue = filter_catalogued_tables(
        table_catalogue,
        groups=tuple(group_filter.value),
        statuses=tuple(status_filter.value),
        search=asset_search.value,
    )
    return (filtered_catalogue,)


@app.cell
def _(filtered_catalogue, mo, summary, table_asset_catalogue_frame):
    if summary.overlaid_table_count == 0:
        detail = "No Dagster table assets or storage prefixes were discovered."
    else:
        detail = (
            f"Showing `{len(filtered_catalogue)}` of "
            f"`{summary.overlaid_table_count}` overlaid catalogue rows."
        )

    mo.vstack(
        [
            mo.md(f"## Table Asset Catalogue\n\n{detail}"),
            mo.ui.table(
                table_asset_catalogue_frame(filtered_catalogue),
                selection=None,
                page_size=15,
            ),
        ]
    )
    return


@app.cell
def _(asset_schema_metadata_frame, filtered_catalogue, mo):
    mo.vstack(
        [
            mo.md("## Schema Metadata"),
            mo.ui.table(
                asset_schema_metadata_frame(filtered_catalogue),
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

        This dashboard is read-only. It does not change Dagster asset
        definitions, schedules, materializations, or deployment configuration.
        """
    )
    return


if __name__ == "__main__":
    app.run()
