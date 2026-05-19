import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo

    from marimoserver.concept_asset_explorer import (
        build_concept_asset_explorer,
        render_concept_asset_explorer_html,
    )
    from marimoserver.gas_dashboard import render_dashboard_context_panel

    return (
        build_concept_asset_explorer,
        mo,
        render_concept_asset_explorer_html,
        render_dashboard_context_panel,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Concept-to-Asset Explorer

            **Dashboard brief**: **Dashboard intent**: Analytical. Analysts,
            data engineers, and stakeholders use this dashboard to start from
            Market context glossary concepts and see the registry-backed
            `silver.gas_model` assets, available dashboard routes, planned
            dashboard cards, and table explorer entries that support them.
            Data scope is the code-local Marimo dashboard registry only;
            generated gold Markdown and gas-model docs remain read-only
            citation anchors and are not opened at runtime. Freshness is the
            registry snapshot packaged with the deployed dashboard image. The
            dashboard reads no table rows; unmapped concepts and unmapped
            backing assets are rendered as visible coverage gaps.
            """),
            mo.Html(render_dashboard_context_panel("concept-to-asset-explorer")),
        ]
    )
    return


@app.cell
def _(build_concept_asset_explorer):
    concept_asset_explorer = build_concept_asset_explorer()
    return (concept_asset_explorer,)


@app.cell
def _(concept_asset_explorer, mo, render_concept_asset_explorer_html):
    mo.Html(render_concept_asset_explorer_html(concept_asset_explorer))
    return


if __name__ == "__main__":
    app.run()
