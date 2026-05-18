import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import render_dashboard_context_panel
    from marimoserver.table_explorer import (
        DEFAULT_ROW_LIMIT,
        TableAvailability,
        TableQuery,
        cached_table_scan,
        catalogued_table_by_id,
        catalogued_table_group,
        catalogued_table_layers_or_domains,
        discover_table_catalogue,
        discover_storage,
        discover_table_explorer_config,
        explore_table_scan,
        filter_catalogued_tables,
        format_materialization_timestamp,
        overlay_table_catalogue,
    )

    return (
        DEFAULT_ROW_LIMIT,
        TableAvailability,
        TableQuery,
        cached_table_scan,
        catalogued_table_by_id,
        catalogued_table_group,
        catalogued_table_layers_or_domains,
        discover_table_catalogue,
        discover_storage,
        discover_table_explorer_config,
        explore_table_scan,
        filter_catalogued_tables,
        format_materialization_timestamp,
        mo,
        overlay_table_catalogue,
        pl,
        render_dashboard_context_panel,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Table Explorer

            **Dashboard brief**: **Dashboard intent**: Analytical. Data
            engineers and operators use this dashboard to inspect the Dagster
            table asset catalogue, configured S3-compatible buckets, and
            bounded table previews. Freshness comes from Dagster
            materialization metadata when GraphQL is reachable; unavailable
            GraphQL or empty storage is shown as degraded but readable state.
            """),
            mo.Html(render_dashboard_context_panel("gas-model-table-explorer")),
        ]
    )
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
def _():
    table_scan_cache = {}
    return table_scan_cache


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
def _(catalogued_table_group, catalogued_table_layers_or_domains, pl):
    def table_summary_frame(table_catalogue, format_materialization_timestamp):
        rows = []
        for entry in table_catalogue:
            asset = entry.asset
            table = entry.table
            rows.append(
                {
                    "asset key": "" if asset is None else asset.asset_id,
                    "group": catalogued_table_group(entry),
                    "layer/domain": ", ".join(
                        catalogued_table_layers_or_domains(entry)
                    ),
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
def _(catalogued_table_layers_or_domains, pl):
    def asset_metadata_frame(entry, format_materialization_timestamp):
        asset = entry.asset
        table = entry.table
        rows = [
            {"field": "Status", "value": entry.status.value},
            {
                "field": "Layer/domain",
                "value": ", ".join(catalogued_table_layers_or_domains(entry)),
            },
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

    def column_statistics_frame(exploration):
        return pl.DataFrame(
            [
                {
                    "column": statistic.column,
                    "null count": statistic.null_count,
                    "distinct count": statistic.distinct_count,
                }
                for statistic in exploration.column_statistics
            ]
        )

    return column_statistics_frame, schema_frame


@app.cell
def _(config, mo, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "Runtime",
                "AWS endpoint",
                "AWS region",
                "AWS access key",
                "Dagster GraphQL",
                "Configured buckets",
                "Full table scan",
                "Preview row cap",
            ],
            "value": [
                config.runtime_location,
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                config.aws_access_key_id or "(instance profile)",
                config.dagster_graphql_url,
                ", ".join(config.default_buckets),
                str(config.full_table_scan_enabled),
                str(config.max_preview_rows),
            ],
        }
    )

    mo.vstack(
        [
            mo.md("## Configuration"),
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
                table prefixes.
                """
            ),
            kind="warn",
        )

    catalogue_warning
    return


@app.cell
def _(
    TableAvailability,
    catalogued_table_group,
    catalogued_table_layers_or_domains,
    mo,
    table_catalogue,
):
    if table_catalogue:
        group_options = sorted(
            {catalogued_table_group(entry) for entry in table_catalogue}
        )
        layer_domain_options = sorted(
            {
                layer_or_domain
                for entry in table_catalogue
                for layer_or_domain in catalogued_table_layers_or_domains(entry)
            }
        )
        present_statuses = {entry.status.value for entry in table_catalogue}
        status_options = [
            status.value
            for status in TableAvailability
            if status.value in present_statuses
        ]
        group_filter = mo.ui.multiselect(
            options=group_options,
            value=[],
            label="Asset group",
            full_width=True,
        )
        layer_domain_filter = mo.ui.multiselect(
            options=layer_domain_options,
            value=[],
            label="Layer/domain",
            full_width=True,
        )
        status_filter = mo.ui.multiselect(
            options=status_options,
            value=[],
            label="Live status",
            full_width=True,
        )
        asset_search = mo.ui.text(
            placeholder="Search asset key, URI, or description",
            label="Asset search",
            full_width=True,
        )
        catalogue_filter_view = mo.vstack(
            [
                mo.md("## Catalogue Controls"),
                group_filter,
                layer_domain_filter,
                status_filter,
                asset_search,
            ]
        )
    else:
        group_filter = None
        layer_domain_filter = None
        status_filter = None
        asset_search = None
        catalogue_filter_view = mo.md("")

    catalogue_filter_view
    return asset_search, group_filter, layer_domain_filter, status_filter


@app.cell
def _(
    asset_search,
    filter_catalogued_tables,
    group_filter,
    layer_domain_filter,
    status_filter,
    table_catalogue,
):
    filtered_table_catalogue = filter_catalogued_tables(
        table_catalogue,
        groups=() if group_filter is None else tuple(group_filter.value),
        layers_or_domains=()
        if layer_domain_filter is None
        else tuple(layer_domain_filter.value),
        statuses=() if status_filter is None else tuple(status_filter.value),
        search="" if asset_search is None else asset_search.value,
    )
    return filtered_table_catalogue


@app.cell
def _(
    filtered_table_catalogue,
    format_materialization_timestamp,
    mo,
    table_catalogue,
    table_summary_frame,
):
    table_summary = table_summary_frame(
        filtered_table_catalogue,
        format_materialization_timestamp,
    )

    if table_summary.is_empty():
        if table_catalogue:
            table_summary_view = mo.md("""
            ## Table Catalogue

            No table assets match the current controls.
            """)
        else:
            table_summary_view = mo.md("""
            ## Table Catalogue

            No table assets or materialized table prefixes were found.

            Materialize assets or confirm the configured buckets and Dagster webserver,
            then refresh this notebook.
            """)
    else:
        table_summary_view = mo.vstack(
            [
                mo.md(
                    f"""
                    ## Table Catalogue

                    Showing `{len(filtered_table_catalogue)}` of
                    `{len(table_catalogue)}` catalogue rows.
                    """
                ),
                mo.ui.table(table_summary, selection=None),
            ]
        )

    table_summary_view
    return


@app.cell
def _(filtered_table_catalogue, mo):
    if filtered_table_catalogue:
        table_options = {
            f"{entry.display_name} - {entry.status.value}": entry.entry_id
            for entry in filtered_table_catalogue
        }
        table_picker = mo.ui.dropdown(
            options=table_options,
            value=filtered_table_catalogue[0].entry_id,
            searchable=True,
            label="Table",
            full_width=True,
        )
        refresh_scan_button = mo.ui.run_button(label="Refresh table scan")
        inspector_controls = mo.vstack(
            [
                mo.md("## Inspect Table"),
                table_picker,
                refresh_scan_button,
            ]
        )
    else:
        table_picker = None
        refresh_scan_button = None
        inspector_controls = mo.md("""
        ## Inspect Table

        No table is available under the current catalogue controls.
        """)

    inspector_controls
    return refresh_scan_button, table_picker


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
def _(TableAvailability, mo):
    def materialization_guidance_view(entry, table=None, error=None):
        if entry is None:
            return mo.md("")

        if entry.status == TableAvailability.UNMATERIALIZED:
            reason = (
                "Dagster knows this asset, but storage has no materialized "
                "table prefix for it yet."
            )
        elif entry.status == TableAvailability.MISSING:
            reason = (
                "Dagster has materialization metadata, but the expected "
                "table prefix is not present."
            )
        elif table is not None and error is None:
            reason = "The selected table exists but has no preview rows."
        else:
            reason = "The selected table cannot be previewed from storage yet."

        error_detail = "" if error is None else f"\n\nScan detail: `{error}`"
        return mo.callout(
            mo.md(
                f"""
                {reason}

                Materialize the asset in Dagster, or load the required curated
                outputs, then refresh the table scan before expecting preview rows.
                {error_detail}
                """
            ),
            kind="warn",
        )

    return materialization_guidance_view


@app.cell
def _(
    cached_table_scan,
    config,
    refresh_scan_button,
    selected_entry,
    table_scan_cache,
):
    selected_table = None if selected_entry is None else selected_entry.table

    if selected_entry is None or selected_table is None:
        table_scan = None
    else:
        refresh_token = 0 if refresh_scan_button is None else refresh_scan_button.value
        table_scan = cached_table_scan(
            selected_table,
            config,
            table_scan_cache,
            refresh_token=refresh_token,
        )

    return selected_table, table_scan


@app.cell
def _(DEFAULT_ROW_LIMIT, config, mo, table_scan):
    if (
        table_scan is not None
        and table_scan.error is None
        and table_scan.dataframe.columns
    ):
        column_options = tuple(table_scan.dataframe.columns)
        max_row_limit = config.max_preview_rows if table_scan.is_limited else 10_000
        row_limit = mo.ui.number(
            start=1,
            stop=max_row_limit,
            step=1,
            value=min(DEFAULT_ROW_LIMIT, max_row_limit),
            label="Row limit",
        )
        column_picker = mo.ui.multiselect(
            options=column_options,
            value=column_options,
            label="Columns",
            full_width=True,
        )
        control_items = [mo.md("## Preview Controls"), row_limit, column_picker]
        if table_scan.is_limited:
            sort_column_picker = None
            sort_direction_picker = None
            text_search = None
            control_items.append(
                mo.callout(
                    mo.md(
                        "This deployment loads a bounded preview, so text search, "
                        "sorting, and column statistics are disabled."
                    ),
                    kind="neutral",
                )
            )
        else:
            sort_column_picker = mo.ui.dropdown(
                options={
                    "No sort": "",
                    **{column: column for column in column_options},
                },
                value="",
                searchable=True,
                label="Sort column",
                full_width=True,
            )
            sort_direction_picker = mo.ui.dropdown(
                options=("Ascending", "Descending"),
                value="Ascending",
                label="Sort direction",
            )
            text_search = mo.ui.text(
                placeholder="Search selected columns",
                label="Text search",
                full_width=True,
            )
            control_items.extend(
                [
                    sort_column_picker,
                    sort_direction_picker,
                    text_search,
                ]
            )
        exploration_controls = mo.vstack(control_items)
    else:
        row_limit = None
        column_picker = None
        sort_column_picker = None
        sort_direction_picker = None
        text_search = None
        exploration_controls = mo.md("")

    exploration_controls
    return (
        column_picker,
        row_limit,
        sort_column_picker,
        sort_direction_picker,
        text_search,
    )


@app.cell
def _(
    DEFAULT_ROW_LIMIT,
    TableQuery,
    column_picker,
    column_statistics_frame,
    explore_table_scan,
    materialization_guidance_view,
    mo,
    row_limit,
    schema_frame,
    selected_entry,
    selected_table,
    sort_column_picker,
    sort_direction_picker,
    table_scan,
    text_search,
):
    if selected_entry is None:
        inspection_view = mo.md("")
    elif selected_table is None:
        inspection_view = materialization_guidance_view(selected_entry)
    elif table_scan is None:
        inspection_view = mo.md("")
    elif table_scan.error is not None:
        inspection_view = materialization_guidance_view(
            selected_entry,
            selected_table,
            table_scan.error,
        )
    else:
        selected_row_limit = (
            DEFAULT_ROW_LIMIT
            if row_limit is None or row_limit.value is None
            else int(row_limit.value)
        )
        selected_columns = (
            ()
            if column_picker is None
            else tuple(str(column) for column in column_picker.value)
        )
        sort_column = (
            None
            if sort_column_picker is None or sort_column_picker.value == ""
            else str(sort_column_picker.value)
        )
        text_search_value = "" if text_search is None else text_search.value
        exploration = explore_table_scan(
            table_scan,
            TableQuery(
                row_limit=selected_row_limit,
                columns=selected_columns,
                sort_column=sort_column,
                sort_descending=sort_direction_picker is not None
                and sort_direction_picker.value == "Descending",
                text_search=text_search_value,
            ),
        )
        row_count_label = (
            "Preview rows loaded" if exploration.is_limited else "Exact rows"
        )
        filtered_count_line = (
            ""
            if exploration.is_limited
            else f"- Rows after text search: `{exploration.filtered_row_count}`"
        )

        sections = [
            mo.md(
                f"""
                ### `{selected_table.display_name}`

                - Format: `{selected_table.table_format.value}`
                - {row_count_label}: `{exploration.row_count}`
                {filtered_count_line}
                - URI: `{selected_table.uri}`
                """
            ),
            mo.md("#### Schema"),
            mo.ui.table(schema_frame(exploration), selection=None),
        ]
        statistics = column_statistics_frame(exploration)
        if not statistics.is_empty():
            sections.extend(
                [
                    mo.md("#### Selected Column Statistics"),
                    mo.ui.table(statistics, selection=None),
                ]
            )
        if exploration.row_count == 0:
            sections.append(
                materialization_guidance_view(selected_entry, selected_table)
            )
        elif exploration.filtered_row_count == 0:
            sections.append(mo.md("No rows match the current text search."))
        else:
            sections.extend(
                [
                    mo.md("#### Preview"),
                    mo.ui.table(
                        exploration.preview,
                        selection=None,
                        page_size=min(25, max(1, selected_row_limit)),
                    ),
                ]
            )
        inspection_view = mo.vstack(sections)

    inspection_view
    return


if __name__ == "__main__":
    app.run()
