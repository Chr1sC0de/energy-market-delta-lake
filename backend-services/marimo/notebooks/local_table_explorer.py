import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.table_explorer import (
        discover_storage,
        discover_table_explorer_config,
        inspect_table,
        table_by_id,
    )

    return (
        discover_storage,
        discover_table_explorer_config,
        inspect_table,
        mo,
        pl,
        table_by_id,
    )


@app.cell
def _(mo):
    mo.md("""
    # Local Table Explorer

    Inspect LocalStack-backed Delta and parquet table prefixes from the local
    compose buckets.
    """)
    return


@app.cell
def _(discover_storage, discover_table_explorer_config):
    config = discover_table_explorer_config()
    discovery = discover_storage(config)
    return config, discovery


@app.cell
def _(pl):
    def bucket_health_frame(discovery):
        rows = []
        for bucket in discovery.buckets:
            if bucket.error is not None:
                status = "Unavailable"
            elif bucket.object_count == 0:
                status = "Empty"
            else:
                status = "Available"

            rows.append(
                {
                    "bucket": bucket.name,
                    "default": bucket.is_default,
                    "discovered": bucket.discovered,
                    "status": status,
                    "objects scanned": bucket.object_count,
                    "table prefixes": bucket.table_count,
                    "truncated": bucket.truncated,
                    "detail": bucket.error or "",
                }
            )
        return pl.DataFrame(rows)

    def table_summary_frame(discovery):
        rows = []
        for table in discovery.tables:
            rows.append(
                {
                    "bucket": table.bucket,
                    "prefix": table.prefix or "(bucket root)",
                    "format": table.table_format.value,
                    "parquet files": len(table.parquet_files),
                    "uri": table.uri,
                }
            )
        return pl.DataFrame(rows)

    def schema_frame(inspection):
        return pl.DataFrame(
            [
                {"column": column.name, "dtype": column.dtype}
                for column in inspection.schema
            ]
        )

    return bucket_health_frame, schema_frame, table_summary_frame


@app.cell
def _(config, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AWS endpoint",
                "AWS region",
                "AWS access key",
                "Default buckets",
            ],
            "value": [
                config.aws_endpoint_url,
                config.aws_region,
                config.aws_access_key_id,
                ", ".join(config.default_buckets),
            ],
        }
    )

    mo.vstack(
        [
            mo.md("## Local AWS Configuration"),
            mo.ui.table(config_frame, selection=None),
        ]
    )
    return


@app.cell
def _(bucket_health_frame, discovery, mo):
    bucket_health = bucket_health_frame(discovery)
    bucket_listing_detail = (
        ""
        if discovery.bucket_listing_error is None
        else f"\n\nBucket listing detail: `{discovery.bucket_listing_error}`"
    )

    mo.vstack(
        [
            mo.md(f"## Bucket Health{bucket_listing_detail}"),
            mo.ui.table(bucket_health, selection=None),
        ]
    )
    return


@app.cell
def _(discovery, mo, table_summary_frame):
    table_summary = table_summary_frame(discovery)

    if table_summary.is_empty():
        table_summary_view = mo.md("""
        ## Table Prefixes

        No materialized table prefixes were found in the local buckets.

        Materialize assets or seed LocalStack, then refresh this notebook.
        """)
    else:
        table_summary_view = mo.vstack(
            [
                mo.md("## Table Prefixes"),
                mo.ui.table(table_summary, selection=None),
            ]
        )

    table_summary_view
    return


@app.cell
def _(discovery, mo):
    if discovery.tables:
        table_options = {
            table.display_name: table.table_id for table in discovery.tables
        }
        table_picker = mo.ui.dropdown(
            options=table_options,
            value=discovery.tables[0].table_id,
            searchable=True,
            label="Table",
            full_width=True,
        )
        inspect_button = mo.ui.run_button(label="Load schema, row count, and preview")
        inspector_controls = mo.vstack(
            [
                mo.md("## Inspect Table"),
                table_picker,
                inspect_button,
            ]
        )
    else:
        table_picker = None
        inspect_button = None
        inspector_controls = mo.md("""
        ## Inspect Table

        No live table prefix is available to inspect yet.
        """)

    inspector_controls
    return inspect_button, table_picker


@app.cell
def _(
    config,
    discovery,
    inspect_button,
    inspect_table,
    mo,
    schema_frame,
    table_by_id,
    table_picker,
):
    selected_table_id = None if table_picker is None else table_picker.value
    selected_table = table_by_id(discovery.tables, selected_table_id)

    if inspect_button is None or selected_table is None:
        inspection_view = mo.md("")
    elif inspect_button.value:
        inspection = inspect_table(selected_table, config)
        if inspection.error is not None:
            inspection_view = mo.md(
                f"""
                ### `{selected_table.display_name}`

                Inspection failed: `{inspection.error}`
                """
            )
        else:
            inspection_view = mo.vstack(
                [
                    mo.md(
                        f"""
                        ### `{selected_table.display_name}`

                        - Format: `{selected_table.table_format.value}`
                        - Rows: `{inspection.row_count}`
                        - URI: `{selected_table.uri}`
                        """
                    ),
                    mo.md("#### Schema"),
                    mo.ui.table(schema_frame(inspection), selection=None),
                    mo.md("#### Preview"),
                    mo.ui.table(inspection.preview, selection=None, page_size=25),
                ]
            )
    else:
        inspection_view = mo.md("")

    inspection_view
    return


if __name__ == "__main__":
    app.run()
