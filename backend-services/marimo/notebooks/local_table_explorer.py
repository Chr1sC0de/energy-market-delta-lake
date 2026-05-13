import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.table_explorer import (
        catalogued_table_by_id,
        discover_table_catalogue,
        discover_storage,
        discover_table_explorer_config,
        format_materialization_timestamp,
        inspect_table,
        overlay_table_catalogue,
    )

    return (
        catalogued_table_by_id,
        discover_table_catalogue,
        discover_storage,
        discover_table_explorer_config,
        format_materialization_timestamp,
        inspect_table,
        mo,
        overlay_table_catalogue,
        pl,
    )


@app.cell
def _(mo):
    mo.md("""
    # Local Table Explorer

    Inspect the local Dagster table asset catalogue and LocalStack-backed Delta
    or parquet table prefixes from the compose buckets.
    """)
    return


@app.cell
def _(
    discover_storage,
    discover_table_catalogue,
    discover_table_explorer_config,
    overlay_table_catalogue,
):
    config = discover_table_explorer_config()
    discovery = discover_storage(config)
    catalogue = discover_table_catalogue(config)
    table_catalogue = overlay_table_catalogue(discovery, catalogue)
    return catalogue, config, discovery, table_catalogue


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

    return bucket_health_frame


@app.cell
def _(pl):
    def table_summary_frame(table_catalogue, format_materialization_timestamp):
        rows = []
        for entry in table_catalogue:
            asset = entry.asset
            table = entry.table
            rows.append(
                {
                    "asset key": "" if asset is None else asset.asset_id,
                    "group": "" if asset is None else asset.group_name,
                    "status": entry.status.value,
                    "local storage": "Live" if table is not None else "",
                    "bucket": "" if table is None else table.bucket,
                    "prefix": "" if table is None else table.prefix or "(bucket root)",
                    "format": "" if table is None else table.table_format.value,
                    "kinds": "" if asset is None else ", ".join(asset.kinds),
                    "columns": 0 if asset is None else len(asset.columns),
                    "latest materialization": ""
                    if asset is None
                    else format_materialization_timestamp(
                        asset.latest_materialization_timestamp
                    ),
                    "uri": entry.uri or "",
                }
            )
        return pl.DataFrame(rows)

    return table_summary_frame


@app.cell
def _(pl):
    def asset_metadata_frame(entry, format_materialization_timestamp):
        asset = entry.asset
        table = entry.table
        rows = [
            {"field": "Status", "value": entry.status.value},
            {
                "field": "Local table",
                "value": "" if table is None else table.display_name,
            },
            {"field": "URI", "value": entry.uri or ""},
        ]
        if asset is not None:
            rows.extend(
                [
                    {"field": "Asset key", "value": asset.asset_id},
                    {"field": "Group", "value": asset.group_name},
                    {"field": "Kinds", "value": ", ".join(asset.kinds)},
                    {
                        "field": "Materializable",
                        "value": str(asset.is_materializable),
                    },
                    {"field": "Executable", "value": str(asset.is_executable)},
                    {
                        "field": "Latest materialization",
                        "value": format_materialization_timestamp(
                            asset.latest_materialization_timestamp
                        ),
                    },
                    {"field": "Description", "value": asset.description or ""},
                ]
            )
        return pl.DataFrame(rows)

    def asset_columns_frame(entry):
        if entry.asset is None:
            return pl.DataFrame()
        return pl.DataFrame(
            [
                {
                    "column": column.name,
                    "type": column.dtype,
                    "description": column.description or "",
                }
                for column in entry.asset.columns
            ]
        )

    return asset_columns_frame, asset_metadata_frame


@app.cell
def _(pl):
    def schema_frame(inspection):
        return pl.DataFrame(
            [
                {"column": column.name, "dtype": column.dtype}
                for column in inspection.schema
            ]
        )

    return schema_frame


@app.cell
def _(config, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AWS endpoint",
                "AWS region",
                "AWS access key",
                "Dagster GraphQL",
                "Default buckets",
            ],
            "value": [
                config.aws_endpoint_url,
                config.aws_region,
                config.aws_access_key_id,
                config.dagster_graphql_url,
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
def _(catalogue, mo):
    if catalogue.error is None:
        catalogue_warning = mo.md("")
    else:
        catalogue_warning = mo.callout(
            mo.md(
                f"""
                Dagster GraphQL is unavailable at `{catalogue.url}`: `{catalogue.error}`.

                Storage discovery and live table preview still work for materialized
                LocalStack prefixes.
                """
            ),
            kind="warn",
        )

    catalogue_warning
    return


@app.cell
def _(format_materialization_timestamp, mo, table_catalogue, table_summary_frame):
    table_summary = table_summary_frame(
        table_catalogue,
        format_materialization_timestamp,
    )

    if table_summary.is_empty():
        table_summary_view = mo.md("""
        ## Table Catalogue

        No table assets or materialized table prefixes were found.

        Materialize assets, seed LocalStack, or start the local Dagster webserver,
        then refresh this notebook.
        """)
    else:
        table_summary_view = mo.vstack(
            [
                mo.md("## Table Catalogue"),
                mo.ui.table(table_summary, selection=None),
            ]
        )

    table_summary_view
    return


@app.cell
def _(mo, table_catalogue):
    if table_catalogue:
        table_options = {
            f"{entry.display_name} - {entry.status.value}": entry.entry_id
            for entry in table_catalogue
        }
        table_picker = mo.ui.dropdown(
            options=table_options,
            value=table_catalogue[0].entry_id,
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
    asset_columns_frame,
    asset_metadata_frame,
    catalogued_table_by_id,
    format_materialization_timestamp,
    mo,
    table_catalogue,
    table_picker,
):
    selected_entry_id = None if table_picker is None else table_picker.value
    selected_entry = catalogued_table_by_id(table_catalogue, selected_entry_id)

    if selected_entry is None:
        selected_asset_view = mo.md("")
    else:
        sections = [
            mo.md(f"### `{selected_entry.display_name}`"),
            mo.ui.table(
                asset_metadata_frame(
                    selected_entry,
                    format_materialization_timestamp,
                ),
                selection=None,
            ),
        ]
        asset_columns = asset_columns_frame(selected_entry)
        if not asset_columns.is_empty():
            sections.extend(
                [
                    mo.md("#### GraphQL Column Metadata"),
                    mo.ui.table(asset_columns, selection=None),
                ]
            )
        selected_asset_view = mo.vstack(sections)

    selected_asset_view
    return selected_entry


@app.cell
def _(
    config,
    inspect_button,
    inspect_table,
    mo,
    schema_frame,
    selected_entry,
):
    selected_table = None if selected_entry is None else selected_entry.table

    if inspect_button is None or selected_table is None:
        if selected_entry is None:
            inspection_view = mo.md("")
        else:
            inspection_view = mo.md(
                "No live local storage prefix is available for preview."
            )
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
