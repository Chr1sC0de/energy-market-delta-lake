import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo

    from marimoserver.gas_dashboard import render_dashboard_context_panel
    from marimoserver.glossary_explorer import (
        build_glossary_explorer,
        render_glossary_explorer_html,
    )

    return (
        build_glossary_explorer,
        mo,
        render_dashboard_context_panel,
        render_glossary_explorer_html,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Glossary Explorer

            **Dashboard brief**: **Dashboard intent**: Analytical. Analysts,
            stakeholders, and data engineers use this dashboard to browse the
            Marimo-local Market context registry for generated glossary
            concepts, Market context IDs, source chunk IDs, related
            concepts, and dashboard availability. Data scope is the code-local
            dashboard registry only; generated Market context artifacts stay read-only
            citation context and is not opened at runtime. Freshness is the
            registry snapshot packaged with the deployed dashboard image.
            Missing Market context IDs or source chunk IDs render as
            validation-visible gaps.
            """),
            mo.Html(render_dashboard_context_panel("glossary-explorer")),
        ]
    )
    return


@app.cell
def _(build_glossary_explorer):
    glossary_explorer = build_glossary_explorer()
    return (glossary_explorer,)


@app.cell
def _(glossary_explorer, mo, render_glossary_explorer_html):
    mo.Html(render_glossary_explorer_html(glossary_explorer))
    return


if __name__ == "__main__":
    app.run()
