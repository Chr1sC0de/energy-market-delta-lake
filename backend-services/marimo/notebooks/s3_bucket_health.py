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
        TableFormat,
        build_bucket_health_summary,
        discover_storage,
        discover_table_explorer_config,
        filter_table_prefixes,
        render_storage_health_cards,
        s3_bucket_health_frame,
        storage_health_action_markdown,
        table_prefix_discovery_frame,
    )

    return (
        TableFormat,
        build_bucket_health_summary,
        discover_storage,
        discover_table_explorer_config,
        filter_table_prefixes,
        mo,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_storage_health_cards,
        s3_bucket_health_frame,
        storage_health_action_markdown,
        table_prefix_discovery_frame,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # S3 Bucket Health

            **Dashboard brief**: **Dashboard intent**: Operational. Platform
            operators use this dashboard to check configured S3-compatible AEMO,
            landing, archive, and IO-manager bucket reachability, object
            discovery, truncation, bucket errors, and Delta or Parquet
            table-like prefixes. Data scope is read-only configured storage
            discovery. Freshness is the latest notebook refresh; each bucket
            scan is capped by the discovery object limit, and AWS mode checks
            configured buckets without account-wide bucket listing.
            """),
            mo.Html(render_dashboard_context_panel("s3-bucket-health")),
        ]
    )
    return


@app.cell
def _(mo):
    refresh_storage_button = mo.ui.run_button(label="Refresh storage health")
    refresh_storage_button
    return (refresh_storage_button,)


@app.cell
def _(
    build_bucket_health_summary,
    discover_storage,
    discover_table_explorer_config,
    refresh_storage_button,
    refresh_token_from_control,
):
    config = discover_table_explorer_config()
    refresh_token = refresh_token_from_control(refresh_storage_button)
    discovery = discover_storage(config)
    summary = build_bucket_health_summary(config, discovery)
    return config, discovery, refresh_token, summary


@app.cell
def _(
    mo,
    render_storage_health_cards,
    storage_health_action_markdown,
    summary,
):
    action_kind = "neutral" if summary.degraded_bucket_count == 0 else "warn"
    mo.vstack(
        [
            mo.Html(render_storage_health_cards(summary)),
            mo.callout(
                mo.md(storage_health_action_markdown(summary)),
                kind=action_kind,
            ),
        ]
    )
    return


@app.cell
def _(config, mo, pl, summary):
    listing_policy = (
        "Configured buckets only"
        if config.aws_runtime
        else "Configured buckets plus local prefix discovery"
    )
    config_frame = pl.DataFrame(
        {
            "setting": [
                "Runtime",
                "AWS endpoint",
                "AWS region",
                "Bucket listing policy",
                "Configured buckets",
                "Discovery object cap",
            ],
            "value": [
                config.runtime_location,
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                listing_policy,
                ", ".join(config.default_buckets),
                str(summary.discovery_object_limit),
            ],
        }
    )

    mo.vstack(
        [
            mo.md("## Storage Configuration"),
            mo.ui.table(config_frame, selection=None),
        ]
    )
    return


@app.cell
def _(discovery, mo, s3_bucket_health_frame):
    bucket_listing_detail = (
        ""
        if discovery.bucket_listing_error is None
        else f"\n\nBucket listing detail: `{discovery.bucket_listing_error}`"
    )
    mo.vstack(
        [
            mo.md(f"## Bucket Health{bucket_listing_detail}"),
            mo.ui.table(s3_bucket_health_frame(discovery), selection=None),
        ]
    )
    return


@app.cell
def _(TableFormat, discovery, mo):
    bucket_options = tuple(bucket.name for bucket in discovery.buckets)
    format_options = tuple(table_format.value for table_format in TableFormat)
    bucket_filter = mo.ui.multiselect(
        options=bucket_options,
        value=[],
        label="Bucket",
        full_width=True,
    )
    format_filter = mo.ui.multiselect(
        options=format_options,
        value=[],
        label="Table format",
        full_width=True,
    )
    prefix_search = mo.ui.text(
        placeholder="Search prefix, URI, or file",
        label="Prefix search",
        full_width=True,
    )

    mo.vstack(
        [
            mo.md("## Table Prefix Controls"),
            bucket_filter,
            format_filter,
            prefix_search,
        ]
    )
    return bucket_filter, format_filter, prefix_search


@app.cell
def _(
    bucket_filter,
    discovery,
    filter_table_prefixes,
    format_filter,
    prefix_search,
):
    filtered_prefixes = filter_table_prefixes(
        discovery.tables,
        buckets=tuple(bucket_filter.value),
        formats=tuple(format_filter.value),
        search=prefix_search.value,
    )
    return (filtered_prefixes,)


@app.cell
def _(filtered_prefixes, mo, summary, table_prefix_discovery_frame):
    if summary.table_prefix_count == 0:
        prefix_detail = "No Delta or Parquet table-like prefixes were discovered."
    else:
        prefix_detail = (
            f"Showing `{len(filtered_prefixes)}` of "
            f"`{summary.table_prefix_count}` discovered table-like prefixes."
        )

    mo.vstack(
        [
            mo.md(f"## Table Prefix Discovery\n\n{prefix_detail}"),
            mo.ui.table(
                table_prefix_discovery_frame(filtered_prefixes),
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

    Use the Gas Model Table Explorer when a discovered prefix needs schema,
    row preview, column metadata, or Dagster catalogue overlay detail.
    """)
    return


if __name__ == "__main__":
    app.run()
