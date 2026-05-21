import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.data_readiness import (
        bucket_readiness_frame,
        build_data_readiness_overview,
        dagster_materialization_frame,
        readiness_action_markdown,
        render_readiness_cards,
        table_readiness_frame,
    )
    from marimoserver.gas_dashboard import render_dashboard_context_panel
    from marimoserver.gas_model_loader import bounded_row_limit
    from marimoserver.gas_model_loader import refresh_token_from_control
    from marimoserver.table_explorer import (
        discover_storage,
        discover_table_catalogue,
        discover_table_explorer_config,
        overlay_table_catalogue,
    )

    return (
        bounded_row_limit,
        bucket_readiness_frame,
        build_data_readiness_overview,
        dagster_materialization_frame,
        discover_storage,
        discover_table_catalogue,
        discover_table_explorer_config,
        mo,
        overlay_table_catalogue,
        pl,
        readiness_action_markdown,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_readiness_cards,
        table_readiness_frame,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Data Readiness Overview

            **Dashboard brief**: **Dashboard intent**: Operational. Platform
            operators use this dashboard as the first stop for configured S3
            buckets, discovered table prefixes, Dagster GraphQL availability,
            latest materialization freshness, and bounded-read policy. Data
            scope is read-only S3-compatible storage plus Dagster table asset
            metadata. Freshness comes from Dagster materialization timestamps
            when GraphQL is reachable. Missing LocalStack/AWS data, unavailable
            GraphQL, and bounded AWS preview mode are degraded states that keep
            the dashboard readable.
            """),
            mo.Html(render_dashboard_context_panel("data-readiness-overview")),
        ]
    )
    return


@app.cell
def _(mo):
    refresh_readiness_button = mo.ui.button(
        label="Refresh readiness",
        value=0,
        on_click=lambda value: value + 1,
    )
    refresh_readiness_button
    return (refresh_readiness_button,)


@app.cell
def _(
    discover_storage,
    discover_table_catalogue,
    discover_table_explorer_config,
    overlay_table_catalogue,
    refresh_readiness_button,
    refresh_token_from_control,
):
    config = discover_table_explorer_config()
    refresh_token = refresh_token_from_control(refresh_readiness_button)
    discovery = discover_storage(config)
    catalogue = discover_table_catalogue(config)
    table_catalogue = overlay_table_catalogue(discovery, catalogue)
    return catalogue, config, discovery, refresh_token, table_catalogue


@app.cell
def _(
    build_data_readiness_overview,
    catalogue,
    config,
    discovery,
    mo,
    readiness_action_markdown,
    render_readiness_cards,
    table_catalogue,
):
    overview = build_data_readiness_overview(
        config,
        discovery,
        catalogue,
        table_catalogue,
    )
    action_callout_kind = "neutral" if not overview.action_items else "warn"
    mo.vstack(
        [
            mo.Html(render_readiness_cards(overview.cards)),
            mo.callout(
                mo.md(readiness_action_markdown(overview)),
                kind=action_callout_kind,
            ),
        ]
    )
    return (overview,)


@app.cell
def _(bounded_row_limit, config, mo, pl):
    row_limit = bounded_row_limit(config)
    read_policy = (
        "Full table scans enabled"
        if row_limit is None
        else f"Bounded preview: {row_limit} rows max"
    )
    config_frame = pl.DataFrame(
        {
            "setting": [
                "Runtime",
                "AWS endpoint",
                "AWS region",
                "Configured buckets",
                "Dagster GraphQL",
                "Read policy",
                "Full table scan",
            ],
            "value": [
                config.runtime_location,
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                ", ".join(config.default_buckets),
                config.dagster_graphql_url,
                read_policy,
                str(config.full_table_scan_enabled),
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
def _(bucket_readiness_frame, discovery, mo):
    bucket_frame = bucket_readiness_frame(discovery)
    bucket_listing_detail = (
        ""
        if discovery.bucket_listing_error is None
        else f"\n\nBucket listing detail: `{discovery.bucket_listing_error}`"
    )
    mo.vstack(
        [
            mo.md(f"## S3 Bucket Readiness{bucket_listing_detail}"),
            mo.ui.table(bucket_frame, selection=None),
        ]
    )
    return


@app.cell
def _(mo, table_catalogue, table_readiness_frame):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Table Catalogue Readiness

                The catalogue currently has `{len(table_catalogue)}` overlaid
                Dagster/storage rows.
                """
            ),
            mo.ui.table(table_readiness_frame(table_catalogue), selection=None),
        ]
    )
    return


@app.cell
def _(catalogue, dagster_materialization_frame, mo):
    graphql_detail = (
        f"Dagster GraphQL endpoint: `{catalogue.url}`"
        if catalogue.error is None
        else f"Dagster GraphQL unavailable at `{catalogue.url}`: `{catalogue.error}`"
    )
    mo.vstack(
        [
            mo.md(f"## Dagster Materialization Freshness\n\n{graphql_detail}"),
            mo.ui.table(
                dagster_materialization_frame(catalogue),
                selection=None,
                page_size=15,
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Operator Notes

    This dashboard does not preview table contents. Use the Gas Model Table
    Explorer when a readiness row needs schema, rows, column metadata, or a
    bounded storage preview.
    """)
    return


if __name__ == "__main__":
    app.run()
