import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo

    from marimoserver.bounded_read_diagnostics import (
        bounded_read_runtime_frame,
        bounded_read_state_frame,
        dashboard_read_behavior_frame,
        render_bounded_read_summary_cards,
    )
    from marimoserver.gas_dashboard import (
        discover_dashboard_config,
        render_dashboard_context_panel,
    )
    from marimoserver.table_explorer import discover_table_explorer_config

    return (
        bounded_read_runtime_frame,
        bounded_read_state_frame,
        dashboard_read_behavior_frame,
        discover_dashboard_config,
        discover_table_explorer_config,
        mo,
        render_bounded_read_summary_cards,
        render_dashboard_context_panel,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # AWS Bounded Read Diagnostics

            **Dashboard brief**: **Dashboard intent**: Operational. Platform
            operators use this dashboard to inspect AWS-mode bounded-read
            policy before opening table-heavy Marimo views. Data scope is
            read-only environment-derived Marimo configuration and dashboard
            registry metadata: runtime location, configured buckets, endpoint
            mode, preview row caps, full-table-scan state, and per-dashboard
            read behavior. Freshness is the latest notebook execution against
            current service environment variables. The dashboard does not scan
            S3 tables, call Dagster GraphQL, write data, or auto-refresh.
            """),
            mo.Html(render_dashboard_context_panel("aws-bounded-read-diagnostics")),
        ]
    )
    return


@app.cell
def _(discover_dashboard_config, discover_table_explorer_config):
    gas_config = discover_dashboard_config()
    table_config = discover_table_explorer_config()
    return gas_config, table_config


@app.cell
def _(gas_config, mo, render_bounded_read_summary_cards, table_config):
    mo.Html(render_bounded_read_summary_cards(gas_config, table_config))
    return


@app.cell
def _(bounded_read_runtime_frame, gas_config, mo, table_config):
    mo.vstack(
        [
            mo.md("## Runtime Policy"),
            mo.ui.table(
                bounded_read_runtime_frame(gas_config, table_config),
                selection=None,
            ),
        ]
    )
    return


@app.cell
def _(bounded_read_state_frame, gas_config, mo, table_config):
    mo.vstack(
        [
            mo.md("## Bounded Read States"),
            mo.ui.table(
                bounded_read_state_frame(gas_config, table_config),
                selection=None,
            ),
        ]
    )
    return


@app.cell
def _(dashboard_read_behavior_frame, gas_config, mo, table_config):
    mo.vstack(
        [
            mo.md("## Per-Dashboard Read Behavior"),
            mo.ui.table(
                dashboard_read_behavior_frame(gas_config, table_config),
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

    Bounded preview and recent-only states mean a dashboard is intentionally
    showing a capped or sorted view. Use this diagnostic before treating row
    counts in table-heavy dashboards as complete source-table counts.
    """)
    return


if __name__ == "__main__":
    app.run()
