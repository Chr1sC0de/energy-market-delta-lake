import marimo

__generated_with = "0.21.1"
app = marimo.App(width="full", html_head_file="head.html")


@app.cell
def _():
    import marimo as mo
    import polars as pl

    from marimoserver.gas_dashboard import (
        PARTICIPANT_CONTEXT_ID,
        PARTICIPANT_DIM_TABLE_NAME,
        PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME,
        cached_load_participant_context_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        participant_context_empty_state_markdown,
        participant_dimension_coverage_frame,
        participant_dimension_preview_frame,
        participant_membership_coverage_frame,
        participant_membership_preview_frame,
        participant_related_market_fact_frame,
        participant_table_specs,
        render_dashboard_context_panel,
        render_participant_context_links,
        table_load_by_name,
    )
    from marimoserver.gas_model_loader import refresh_token_from_control

    return (
        PARTICIPANT_CONTEXT_ID,
        PARTICIPANT_DIM_TABLE_NAME,
        PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME,
        cached_load_participant_context_tables,
        discover_dashboard_config,
        gas_table_load_status_frame,
        gas_table_load_status_message,
        mo,
        participant_context_empty_state_markdown,
        participant_dimension_coverage_frame,
        participant_dimension_preview_frame,
        participant_membership_coverage_frame,
        participant_membership_preview_frame,
        participant_related_market_fact_frame,
        participant_table_specs,
        pl,
        refresh_token_from_control,
        render_dashboard_context_panel,
        render_participant_context_links,
        table_load_by_name,
    )


@app.cell
def _(
    PARTICIPANT_CONTEXT_ID,
    mo,
    render_dashboard_context_panel,
    render_participant_context_links,
):
    mo.vstack(
        [
            mo.md("""
            # Participant Explainer

            **Dashboard brief**: **Dashboard intent**: Analytical. Analysts,
            data engineers, and stakeholders use this dashboard to connect the
            cited Participant Market context to current participant standing
            data, market membership coverage, and participant-facing bid,
            settlement, and facility relationships. Data scope is the Marimo
            dashboard registry, generated-gold path and source chunk metadata
            copied into that registry, plus read-only bounded Parquet samples
            from `silver_gas_dim_participant`,
            `silver_gas_participant_market_membership`,
            `silver_gas_dim_facility`, `silver_gas_fact_bid_stack`, and
            `silver_gas_fact_settlement_activity`. Freshness, row coverage,
            cache status, load timing, row-limit policy, and missing-source
            behavior come from the shared gas model loader; unavailable or
            empty data renders as designed empty states instead of notebook
            tracebacks.
            """),
            mo.Html(render_dashboard_context_panel(PARTICIPANT_CONTEXT_ID)),
            mo.Html(render_participant_context_links()),
        ]
    )
    return


@app.cell
def _():
    participant_load_cache = {}
    return (participant_load_cache,)


@app.cell
def _(mo):
    refresh_data_button = mo.ui.run_button(label="Refresh data")
    mo.hstack([refresh_data_button], justify="start")
    return (refresh_data_button,)


@app.cell
def _(
    cached_load_participant_context_tables,
    discover_dashboard_config,
    participant_load_cache,
    participant_table_specs,
    refresh_data_button,
    refresh_token_from_control,
):
    config = discover_dashboard_config()
    participant_specs = participant_table_specs()
    participant_loads = cached_load_participant_context_tables(
        config,
        participant_load_cache,
        specs=participant_specs,
        refresh_token=refresh_token_from_control(refresh_data_button),
    )
    return config, participant_loads, participant_specs


@app.cell
def _(
    PARTICIPANT_DIM_TABLE_NAME,
    PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME,
    participant_dimension_coverage_frame,
    participant_dimension_preview_frame,
    participant_loads,
    participant_membership_coverage_frame,
    participant_membership_preview_frame,
    participant_related_market_fact_frame,
    table_load_by_name,
):
    participant_load = table_load_by_name(
        participant_loads,
        PARTICIPANT_DIM_TABLE_NAME,
    )
    membership_load = table_load_by_name(
        participant_loads,
        PARTICIPANT_MARKET_MEMBERSHIP_TABLE_NAME,
    )
    participant_coverage = participant_dimension_coverage_frame(participant_load)
    membership_coverage = participant_membership_coverage_frame(membership_load)
    participant_preview = participant_dimension_preview_frame(participant_load)
    membership_preview = participant_membership_preview_frame(membership_load)
    related_market_facts = participant_related_market_fact_frame(participant_loads)
    return (
        membership_coverage,
        membership_load,
        membership_preview,
        participant_coverage,
        participant_load,
        participant_preview,
        related_market_facts,
    )


@app.cell
def _(
    gas_table_load_status_frame,
    gas_table_load_status_message,
    mo,
    participant_loads,
):
    mo.vstack(
        [
            mo.md(
                f"""
                ## Data Health

                {gas_table_load_status_message(participant_loads)}
                """
            ),
            mo.accordion(
                {
                    "Participant read diagnostics": mo.ui.table(
                        gas_table_load_status_frame(participant_loads),
                        selection=None,
                    )
                },
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(config, mo, participant_coverage, participant_specs, pl):
    config_frame = pl.DataFrame(
        {
            "setting": [
                "AEMO bucket",
                "Parquet root",
                "Participant-oriented assets",
                "Generated-gold path",
                "Source chunk IDs",
                "Core participant grain",
                "Membership grain",
                "AWS endpoint",
                "AWS region",
                "Preview rows",
            ],
            "value": [
                config.aemo_bucket,
                f"s3://{config.aemo_bucket}/silver/gas_model",
                str(len(participant_specs)),
                "tools/gas-market-knowledge-base/generated/gold/glossary/participant.md",
                (
                    "chunk-gbb-guide-participants-report, "
                    "chunk-gbb-procedures-registration, "
                    "chunk-sttm-procedures-settlement-terms"
                ),
                "one current row per merged gas participant identity",
                (
                    "participant, source system, market code, and optional "
                    "STTM hub or registration role"
                ),
                config.aws_endpoint_url or "(default AWS)",
                config.aws_region,
                str(config.max_preview_rows),
            ],
        }
    )
    mo.vstack(
        [
            mo.md("## Participant Coverage Health"),
            mo.ui.table(participant_coverage, selection=None),
            mo.accordion(
                {"Coverage inputs": mo.ui.table(config_frame, selection=None)},
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(
    membership_coverage,
    membership_preview,
    mo,
    participant_context_empty_state_markdown,
    participant_loads,
):
    membership_coverage_view = (
        mo.md(participant_context_empty_state_markdown(participant_loads))
        if membership_coverage.is_empty()
        else mo.ui.table(membership_coverage, selection=None)
    )
    membership_preview_view = (
        mo.md(participant_context_empty_state_markdown(participant_loads))
        if membership_preview.is_empty()
        else mo.ui.table(membership_preview, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Participant Market Membership"),
            membership_coverage_view,
            mo.accordion(
                {"Membership preview": membership_preview_view},
                multiple=False,
            ),
        ]
    )
    return


@app.cell
def _(
    mo,
    participant_context_empty_state_markdown,
    participant_loads,
    related_market_facts,
):
    related_fact_view = (
        mo.md(participant_context_empty_state_markdown(participant_loads))
        if related_market_facts.is_empty()
        else mo.ui.table(related_market_facts, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Participant-Related Market Facts"),
            related_fact_view,
        ]
    )
    return


@app.cell
def _(
    mo,
    participant_context_empty_state_markdown,
    participant_loads,
    participant_preview,
):
    participant_preview_view = (
        mo.md(participant_context_empty_state_markdown(participant_loads))
        if participant_preview.is_empty()
        else mo.ui.table(participant_preview, selection=None)
    )

    mo.vstack(
        [
            mo.md("## Participant Dimension Preview"),
            participant_preview_view,
        ]
    )
    return


if __name__ == "__main__":
    app.run()
