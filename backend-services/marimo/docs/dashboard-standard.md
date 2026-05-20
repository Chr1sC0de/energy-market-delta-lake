# Marimo Dashboard Standard

This standard keeps curated Marimo dashboards useful, reviewable, and visually
consistent across local compose and the deployed AWS dashboard. Use it before
adding or changing notebooks under `backend-services/marimo/notebooks/`.

## Table of contents

- [Dashboard brief](#dashboard-brief)
- [Dashboard intents](#dashboard-intents)
- [First viewport](#first-viewport)
- [Useful dashboard rules](#useful-dashboard-rules)
- [Visual rules](#visual-rules)
- [Agent development loop](#agent-development-loop)
- [Future shared primitives](#future-shared-primitives)
- [Validation](#validation)

## Dashboard brief

Every curated dashboard must have a short **Dashboard brief** near the top of
the notebook. It may be a visible first-screen Markdown cell or a plainly named
constant used by the first-screen UI. It must state:

- **Dashboard intent**: Operational, Analytical, or Stakeholder.
- Audience and job-to-be-done.
- Data scope, including source tables, buckets, GraphQL dependencies, or local
  cache assumptions.
- Freshness signal and known data limits, including AWS preview caps,
  LocalStack-only assumptions, missing-source behavior, or static display
  metadata.

Do not start a curated dashboard with a long methodology note. Put detailed
methodology lower in the notebook or behind an accordion.

When a curated dashboard has a Marimo dashboard registry concept, render the
shared context panel near the top of the notebook. The panel should show the
registry concept summary, dashboard usage metadata, related concepts,
generated-gold paths, source chunk IDs, silver chunk paths, source hashes, and
backing `silver.gas_model` assets without reading generated gold Markdown at
runtime.

## Dashboard intents

Choose one primary intent before designing the dashboard:

- **Operational**: Helps an operator diagnose data availability, freshness,
  degraded states, and high-signal market conditions quickly.
- **Analytical**: Helps an analyst explore, filter, compare, and inspect data
  at table or asset level.
- **Stakeholder**: Helps a less technical reader understand a curated
  read-only story with polished summaries and minimal controls.

The intent changes the density and control surface:

- Operational dashboards favor status, freshness, current exceptions, and
  drilldown after the main status surface.
- Analytical dashboards may put filters and tables closer to the top when those
  controls are the work surface.
- Stakeholder dashboards favor readable summaries, charts, maps, and restrained
  detail tables.

## First viewport

The first viewport must behave like a decision cockpit:

- Title, intent, and short job-to-be-done.
- Always-visible data health: source, freshness, load status, row coverage, and
  degraded-state warnings.
- Primary controls that affect the first-screen view.
- Top KPIs, map, chart, or status summary before detailed tables.

For most dashboards, tables are drilldown. A table can be the first primary
surface only when the **Dashboard intent** is Analytical and the table is the
main tool.

## Useful dashboard rules

- Every control must have a visible effect, a sensible default, and a known
  empty state.
- Expensive bounded table reads should use explicit refresh controls and
  session-level caches. Do not add auto-refresh timers by default; show load
  timing and row-limit policy near the relevant data-health surface.
- Local Marimo runtime output is capped at 16 MB through Subproject config and
  local compose service environment. This supports the current GBB Interactive
  Map `Summary` Plotly iframe output; do not use the cap as a substitute for
  bounded data reads or reviewed visual output size in new dashboard work.
- Prefer fewer controls that were exercised during development over broad
  control panels that were not reviewed.
- Show degraded states as designed UI, not traceback text. Empty LocalStack
  data, unavailable Dagster GraphQL, bounded AWS preview mode, and missing
  materializations must still produce a readable dashboard.
- Keep local development pointed at LocalStack or checked-in sample data unless
  the Operator approves non-local data access.
- Keep notebooks thin. Reusable data shaping, formatting, and HTML generation
  belong in `src/marimoserver/` helpers with **Component test** coverage.
  Notebook cells should compose configuration, controls, and views.

## Visual rules

- Use the repo theme. Curated notebooks should load `notebooks/head.html` when
  they need shared styling and should use the `--emdl-*` CSS tokens from
  `backend-services/caddy/public/theme.css` for custom HTML.
- Lead with KPIs, charts, maps, status summaries, or other visual summaries
  when they communicate the answer faster than a table.
- Keep visual hierarchy restrained and operational. Use compact headings,
  stable dimensions, clear labels, and enough spacing for scanning.
- Use color to encode meaning: success, warning, unavailable, flow,
  utilisation, category, or selection. Do not introduce a notebook-specific
  palette unless the data needs it.
- Do not rely on a single large table as the whole dashboard unless the
  **Dashboard intent** is Analytical.
- Avoid overlapping controls, wrapping labels that hide values, horizontal page
  overflow, and charts or maps that collapse at narrow widths.

## Agent development loop

Agents changing curated dashboards must use a Playwright review loop during
development when a local browser environment is available:

1. Run the target notebook locally through `uv run marimo run` or the
   FastAPI-mounted `/marimo/<notebook>/` route.
2. Open the dashboard at a normal desktop viewport and a narrow viewport.
3. Capture and inspect screenshots for layout, visual hierarchy, text overflow,
   first-viewport usefulness, and degraded-state presentation.
4. Exercise every primary control and confirm the visible result changes as
   intended.
5. Iterate on visual and usefulness issues before final QA.

The final handoff must summarize the Playwright review evidence: pages opened,
viewports reviewed, controls exercised, and visual or interaction fixes made.
Do not store screenshot artifacts by default; save them only when an issue or
Operator explicitly asks for durable artifacts.

## Future shared primitives

When a dashboard change needs repeated custom layout, implement shared helpers
before duplicating one-off HTML across notebooks. The first helper surface
should cover:

- dashboard header and brief rendering
- dashboard context panel
- data-health strip or cards
- KPI grid
- status and degraded-state banners
- section layout
- empty-state and error-state views
- compact detail table wrapper

The helpers should live under `src/marimoserver/`, use the repo theme tokens,
escape user or data text before embedding HTML, and have focused **Component
test** coverage. Existing notebooks do not need to be retrofitted until their
own dashboard issue touches the relevant surface.

## Validation

For docs-only standard changes, run the root **Commit check**:

```bash
prek run -a
```

For runtime dashboard changes, run Marimo validation from this **Subproject**:

```bash
uv run pytest tests/component
prek run -a
```

Mixed maintained-doc and runtime dashboard changes also run the root
**Commit check** from the repository root.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `AGENTS.md`
  - `CONTEXT.md`
  - `backend-services/marimo/README.md`
  - `backend-services/marimo/pyproject.toml`
  - `backend-services/compose.yaml`
  - `backend-services/marimo/research-workspace/AGENTS.md`
  - `backend-services/marimo/src/marimoserver/main.py`
  - `backend-services/marimo/src/marimoserver/gas_dashboard.py`
  - `backend-services/marimo/src/marimoserver/bounded_read_diagnostics.py`
  - `backend-services/marimo/src/marimoserver/gas_model_loader.py`
  - `backend-services/marimo/src/marimoserver/gbb_interactive_map.py`
  - `backend-services/marimo/src/marimoserver/glossary_explorer.py`
  - `backend-services/marimo/src/marimoserver/concept_asset_explorer.py`
  - `backend-services/marimo/src/marimoserver/data_dictionary_explorer.py`
  - `backend-services/marimo/src/marimoserver/citation_chain_explorer.py`
  - `backend-services/marimo/src/marimoserver/source_lineage_explorer.py`
  - `backend-services/marimo/src/marimoserver/table_explorer.py`
  - `backend-services/marimo/src/marimoserver/data_readiness.py`
  - `backend-services/marimo/notebooks/head.html`
  - `backend-services/marimo/notebooks/sample_energy_market.py`
  - `backend-services/marimo/notebooks/gbb_interactive_map.py`
  - `backend-services/marimo/notebooks/table_explorer.py`
  - `backend-services/marimo/notebooks/source_coverage_matrix.py`
  - `backend-services/marimo/notebooks/source_table_lineage_explorer.py`
  - `backend-services/marimo/notebooks/gas_day_explainer.py`
  - `backend-services/marimo/notebooks/data_readiness_overview.py`
  - `backend-services/marimo/notebooks/aws_bounded_read_diagnostics.py`
  - `backend-services/marimo/notebooks/dagster_asset_catalogue_status.py`
  - `backend-services/marimo/notebooks/materialization_freshness.py`
  - `backend-services/marimo/notebooks/s3_bucket_health.py`
  - `backend-services/marimo/notebooks/glossary_explorer.py`
  - `backend-services/marimo/notebooks/concept_to_asset_explorer.py`
  - `backend-services/marimo/notebooks/schema_data_dictionary_explorer.py`
  - `backend-services/marimo/notebooks/citation_chain_explorer.py`
  - `backend-services/marimo/notebooks/system_notices.py`
  - `backend-services/marimo/notebooks/gas_market_prices.py`
  - `backend-services/marimo/notebooks/gas_schedule_runs.py`
  - `backend-services/marimo/notebooks/facility_explainer.py`
  - `backend-services/marimo/notebooks/participant_explainer.py`
  - `backend-services/marimo/notebooks/hub_zone_explainer.py`
  - `backend-services/marimo/notebooks/connection_point_explainer.py`
  - `backend-services/marimo/notebooks/flow_operations.py`
  - `backend-services/marimo/notebooks/pipeline_connection_operations.py`
  - `backend-services/marimo/notebooks/forecast_vs_actual.py`
  - `backend-services/marimo/notebooks/gas_settlement_activity.py`
  - `backend-services/marimo/notebooks/gas_customer_transfer_activity.py`
  - `backend-services/marimo/notebooks/facility_flow_storage.py`
  - `backend-services/marimo/notebooks/capacity_outlook.py`
  - `backend-services/marimo/notebooks/linepack_adequacy.py`
  - `backend-services/marimo/notebooks/nomination_demand_forecast.py`
  - `backend-services/marimo/notebooks/gas_bid_offer_stack.py`
  - `backend-services/marimo/notebooks/gas_quality_composition.py`
  - `backend-services/caddy/public/theme.css`
- `sync.scope`: `interface`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `prek run -a`
  - `verify dashboard brief, intent, data health, Playwright review evidence, links, and theme usage`
