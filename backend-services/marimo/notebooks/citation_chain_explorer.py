import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo

    from marimoserver.citation_chain_explorer import (
        build_citation_chain_explorer,
        render_citation_chain_explorer_html,
    )
    from marimoserver.gas_dashboard import render_dashboard_context_panel

    return (
        build_citation_chain_explorer,
        mo,
        render_citation_chain_explorer_html,
        render_dashboard_context_panel,
    )


@app.cell
def _(mo, render_dashboard_context_panel):
    mo.vstack(
        [
            mo.md("""
            # Citation-Chain Explorer

            **Dashboard brief**: **Dashboard intent**: Analytical. Analysts,
            data engineers, and operators audit the Marimo-local citation chain
            from dashboard concepts to generated-gold paths, source chunk IDs,
            silver chunk paths, and source hashes. Data scope is the Marimo
            dashboard registry in code; generated artifacts remain read-only
            citation anchors and are not opened at runtime. Freshness is the
            packaged registry snapshot, and missing citation fields render as
            coverage gaps.
            """),
            mo.Html(render_dashboard_context_panel("citation-chain-explorer")),
        ]
    )
    return


@app.cell
def _(build_citation_chain_explorer):
    citation_chain_explorer = build_citation_chain_explorer()
    return (citation_chain_explorer,)


@app.cell
def _(citation_chain_explorer, mo, render_citation_chain_explorer_html):
    mo.Html(render_citation_chain_explorer_html(citation_chain_explorer))
    return


if __name__ == "__main__":
    app.run()
