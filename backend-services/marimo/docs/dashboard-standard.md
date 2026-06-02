# Marimo Dashboard Standard

Curated Marimo dashboards are repo-owned operator surfaces, not ad hoc
notebooks. This standard is the authoring contract for notebooks under
`backend-services/marimo/notebooks/` and for helper code that renders those
notebooks in local compose or the deployed AWS dashboard.

## Table of contents

- [Authoring contract](#authoring-contract)
- [Dashboard brief](#dashboard-brief)
- [Dashboard intent](#dashboard-intent)
- [Always-visible data health](#always-visible-data-health)
- [Bounded loaders](#bounded-loaders)
- [Shared rendering primitives](#shared-rendering-primitives)
- [Layout and interaction](#layout-and-interaction)
- [Browser review evidence](#browser-review-evidence)
- [Validation](#validation)

## Authoring contract

Every curated dashboard author must:

- Write or keep a short **Dashboard brief** near the top of the notebook.
- Choose one primary **Dashboard intent**: Operational, Analytical, or
  Stakeholder.
- Keep data health visible in the first viewport before detailed tables.
- Read `silver.gas_model` data through bounded loader helpers, with explicit
  refresh controls and session caches for expensive reads.
- Use shared rendering helpers from `src/marimoserver/` for registry context,
  load status, bounded-scope copy, KPIs, links, empty states, and repeated HTML
  surfaces.
- Treat unavailable LocalStack or AWS data, unavailable Dagster GraphQL, missing
  materializations, empty reads, and bounded AWS preview mode as designed
  dashboard states.
- Record Playwright or browser review evidence in the handoff when local
  browser review is available.

Keep per-dashboard details in the notebook brief, helper tests, or the
per-dashboard README reference section. This standard explains the shared
contract and avoids repeating each dashboard's source list or workflow.

## Dashboard brief

Every curated dashboard must have a short **Dashboard brief** near the top of
the notebook. It can be a visible first-screen Markdown cell or a plainly named
constant used by the first-screen UI. It must state:

- **Dashboard intent**: Operational, Analytical, or Stakeholder.
- Audience and job-to-be-done.
- Data scope, including source tables, buckets, GraphQL dependencies, or local
  cache assumptions.
- Freshness signal and known data limits, including AWS preview caps,
  LocalStack-only assumptions, missing-source behavior, or static display
  metadata.

Start the dashboard with the user-facing job and the health of the data behind
it. Put methodology, source caveats, and long table descriptions lower in the
notebook or behind an accordion.

Registry-backed dashboards must render the shared context panel near the top of
the notebook with `render_dashboard_context_panel("<concept-id>")`. The helper
uses code-local `DashboardRegistryEntry` metadata from
`src/marimoserver/dashboard_registry.py`; it shows the concept summary,
dashboard usage metadata, related concepts, Market context IDs, source chunk
IDs, silver chunk paths, source hashes, and backing `silver.gas_model` assets
without reading generated Market context Markdown at runtime.

## Dashboard intent

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

## Always-visible data health

Data health must appear in the first viewport and stay scannable before a user
opens detailed diagnostics. A dashboard can use cards, a strip, callouts, or a
compact table, but the surface must cover:

- source or dependency name, such as S3 bucket, Dagster GraphQL, registry
  metadata, or `silver.gas_model` table
- freshness signal or an explicit statement that the dashboard has no live
  freshness input
- load status, including available, empty, unavailable, truncated, or
  storage-only states where those states apply
- row coverage, loaded-row count, preview cap, and full-scan policy
- cache and refresh state for reads controlled by explicit refresh buttons
- degraded-state warnings and the user action or limitation they imply

Use `gas_table_load_status_message()` and `gas_table_load_status_frame()` for
bounded gas-model table reads. The summary belongs outside an accordion;
detailed per-table diagnostics can sit inside one.

## Bounded loaders

Dashboard code must preserve the bounded-read policy enforced by
`src/marimoserver/gas_model_loader.py`:

- `bounded_row_limit()` returns no row cap when full table scans are enabled and
  otherwise caps each preview at the configured `MARIMO_MAX_PREVIEW_ROWS` value.
- `load_gas_model_tables()` and `cached_load_gas_model_tables()` read configured
  tables and return unavailable-state details instead of surfacing notebook
  tracebacks.
- Domain-specific cached loaders in `gas_dashboard.py` reuse the same policy
  for prices, schedules, flows, settlement, capacity, quality, explainers, and
  source-coverage surfaces.
- `refresh_token_from_control()` lets explicit Marimo controls invalidate the
  session cache without adding automatic timers.

Use explicit refresh buttons for expensive reads. Show load timing, cache
status, row counts, and row-limit policy near the data-health surface. Local
Marimo runtime output is capped at 16 MB through Subproject config and local
compose service environment, but that cap is an output guard only. It does not
replace bounded reads, reviewed visual output size, or dashboard-specific empty
states.

## Shared rendering primitives

Prefer existing helper surfaces before writing notebook-local HTML:

- registry context: `render_dashboard_context_panel()` and
  dashboard-specific context link helpers
- bounded read health: `gas_table_load_status_message()`,
  `gas_table_load_status_frame()`, bounded-scope Markdown helpers, and
  row-limit formatting from the loader
- dashboard summaries: KPI-frame helpers, status-frame helpers, source-option
  helpers, and chart/table input frames
- degraded states: dashboard-specific `*_empty_state_markdown()` helpers and
  compact error messages from the bounded loader

When a dashboard change needs repeated custom layout, add or extend a helper
under `src/marimoserver/` before duplicating one-off HTML across notebooks.
Helpers should use the repo theme tokens, escape user or data text before
embedding HTML, and carry focused **Component test** coverage. Existing
notebooks do not need retrofitting until their own dashboard issue touches that
surface.

## Layout and interaction

The first viewport must behave like an operator work surface:

- title, intent, and short job-to-be-done
- data health summary
- primary controls that affect the first-screen view
- top KPIs, map, chart, or status summary before detailed tables

For most dashboards, tables are drilldown. A table can be the first primary
surface only when the **Dashboard intent** is Analytical and the table is the
main tool.

Coverage drilldown tables belong in collapsed lazy accordions. Keep coverage
health, KPIs, filters, bounded-read status, degraded-state callouts, and
diagnostics summaries visible outside those accordions so operators can judge
the read before expanding detailed matrix rows.

Every control must have a visible effect, a sensible default, and a known empty
state. Prefer fewer controls that authors exercised during browser review over
broad control panels that authors did not review.

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
- Keep local development pointed at LocalStack or checked-in sample data unless
  the Operator approves non-local data access.
- Keep notebooks thin. Reusable data shaping, formatting, and HTML generation
  belong in `src/marimoserver/` helpers with **Component test** coverage.
  Notebook cells should compose configuration, controls, and views.

## Browser review evidence

Current repo practice expects agents changing curated dashboards to use a
Playwright or browser review loop during development when a local browser
environment is available:

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

Ralph Review package videos are a separate durable artifact path. They are
recorded only when Ralph has a configured Review package media recipe, such as
a changed curated notebook route under `backend-services/marimo/notebooks/`
that maps to a configured or registry-backed `/marimo/<notebook>/` dashboard
route. Ordinary development-review screenshots remain temporary unless an
issue or Operator explicitly asks for durable artifacts.

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
  - `backend-services/marimo/scripts/review_promoted_dashboards.py`
  - `backend-services/marimo/src/marimoserver/dashboard_registry.py`
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
  - `backend-services/marimo/notebooks/gas_scheduled_quantities.py`
  - `backend-services/marimo/notebooks/facility_explainer.py`
  - `backend-services/marimo/notebooks/participant_explainer.py`
  - `backend-services/marimo/notebooks/hub_zone_explainer.py`
  - `backend-services/marimo/notebooks/connection_point_explainer.py`
  - `backend-services/marimo/notebooks/flow_operations.py`
  - `backend-services/marimo/notebooks/operational_meter_flow.py`
  - `backend-services/marimo/notebooks/pipeline_connection_operations.py`
  - `backend-services/marimo/notebooks/forecast_vs_actual.py`
  - `backend-services/marimo/notebooks/gas_settlement_activity.py`
  - `backend-services/marimo/notebooks/gas_sttm_market_settlement.py`
  - `backend-services/marimo/notebooks/gas_sttm_capacity_settlement.py`
  - `backend-services/marimo/notebooks/gas_sttm_mos_allocation.py`
  - `backend-services/marimo/notebooks/gas_customer_transfer_activity.py`
  - `backend-services/marimo/notebooks/facility_flow_storage.py`
  - `backend-services/marimo/notebooks/capacity_outlook.py`
  - `backend-services/marimo/notebooks/capacity_auction.py`
  - `backend-services/marimo/notebooks/capacity_transactions.py`
  - `backend-services/marimo/notebooks/linepack_adequacy.py`
  - `backend-services/marimo/notebooks/nomination_demand_forecast.py`
  - `backend-services/marimo/notebooks/gas_bid_offer_stack.py`
  - `backend-services/marimo/notebooks/gas_sttm_contingency_gas.py`
  - `backend-services/marimo/notebooks/gas_quality_composition.py`
  - `backend-services/marimo/notebooks/heating_value_pressure.py`
  - `backend-services/caddy/public/theme.css`
- `sync.scope`: `interface`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `prek run -a`
  - `verify dashboard brief, intent, data health, Playwright review evidence, links, and theme usage`
