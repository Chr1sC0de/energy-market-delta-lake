# Deploy Marimo Dashboard On Private EC2

The repository now needs the curated Marimo dashboard in the AWS deployment, but
the Marimo-Codex research workspace remains local-only pending a separate
security review.

## Decision

Deploy only the curated `marimo-dashboard` image to AWS. The dashboard runs on a
private `t3.small` EC2 instance in the VPC private subnet, with no public IP and
no SSH key. Operators use SSM Session Manager for host access.

Caddy remains the only public ingress. It proxies `/marimo*` to the Cloud Map
name `marimo-dashboard.dagster:2718`. Notebook routes stay behind the existing
FastAPI auth `forward_auth` flow, while `/marimo/health` returns only
`{"status":"ok"}` without authentication for deployed health checks.

The dashboard instance pulls the digest-pinned ECR image built from
`backend-services/marimo` target `dashboard`. It uses an instance profile with
ECR read, SSM managed-instance access, and read-only S3 access to the curated
AEMO and IO-manager buckets. It does not receive static AWS keys. The deployed
runtime sets `DEVELOPMENT_LOCATION=aws`,
`DAGSTER_GRAPHQL_URL=http://webserver-guest.dagster:3000/dagster-webserver/guest/graphql`,
`MARIMO_OUTPUT_MAX_BYTES=16000000`,
`MARIMO_FULL_TABLE_SCAN_ENABLED=false`, and `MARIMO_MAX_PREVIEW_ROWS=100`.

The dashboard service also exposes `/marimo/dashboard-registry.json` from
Marimo-local code constants. The registry carries planned and available
dashboard metadata, including generated-gold paths, source chunk IDs, silver
chunk paths, and source hashes, but the deployed service does not read Gas
market knowledge base generated files at runtime.

The curated image includes an S3 Bucket Health dashboard for configured
S3-compatible bucket reachability, object scans, truncation, bucket errors, and
Delta or Parquet table-prefix discovery. AWS mode checks the configured buckets
only and does not require account-wide S3 bucket listing permission.

The `/marimo` entry route renders the same registry as a concept gallery hub.
Available dashboard cards link to mounted notebook routes, while planned
dashboard cards stay visible without notebook links. Registry-only notebooks
such as the glossary explorer can browse Marimo-local Market context metadata
without adding generated-file reads at runtime.

Caddy does not serve Marimo packaged static assets from its own static root. It
keeps `/marimo/*/assets/*`, notebook favicons, notebook manifests,
`/marimo/health`, and websocket upgrade requests outside Marimo `forward_auth`,
then reverse-proxies those requests directly to `marimo-dashboard`. The Marimo
FastAPI wrapper sets `Cache-Control: public, max-age=31536000, immutable` on
successful `/marimo/<notebook>/assets/*` responses. Marimo-generated notebook
HTML already emits preload hints for its packaged images and fonts plus
`modulepreload` hints for JavaScript chunks, and current component evidence
shows no WASM asset reference that justifies pre-serving packaged WASM.

## Considered options

- Keep Marimo local-only: avoids new AWS resources but leaves the deployed
  dashboard route nonfunctional.
- Deploy Marimo on ECS Fargate: matches Dagster service placement but adds ECS
  service/task-definition surface for a state-light notebook host and complicates
  operator access.
- Deploy the curated dashboard on private EC2: keeps a small, inspectable runtime
  boundary, supports SSM operator access, and matches the current EC2 access
  pattern used by Caddy and auth without exposing another public host.
- Deploy the Marimo-Codex workspace too: rejected for this slice because
  unattended Codex execution requires identity, filesystem, network, secret,
  audit, and rollback controls beyond the dashboard requirement.

## Consequences

The AWS deployment now includes a private Marimo dashboard endpoint and Caddy
route. The dashboard is stateless: notebook files come from the image, and table
data comes from S3 and Dagster GraphQL. Image changes produce digest changes
that update EC2 user data.

AWS-mode table previews are bounded. The shared `silver.gas_model` loader owns
the sample and recent Parquet-prefix read policy, explicit refresh tokens,
session-level table-read cache keys, load timing, and row-limit messaging for
curated dashboard helpers. The table explorer shares the same row-limit
decision and refresh-token normalization. The table explorer still lists
configured buckets and Dagster table assets, but it disables full-table sort,
text search, and selected-column statistics because those require loading full
tables into memory. Local compose keeps full LocalStack table scans for
development.

The local-only Marimo-Codex workspace stays out of Pulumi and remains bound to
`127.0.0.1:2719` in compose.

The dashboard registry and concept gallery are part of the existing Marimo
image contents. Adding or updating registry metadata does not require a
separate Docker build context and does not add AWS write paths.
The glossary explorer stays inside the same boundary: it reads the packaged
registry constants, not generated gold Markdown or live S3 tables.
The concept-to-asset explorer stays inside that registry-only boundary. It maps
Market context glossary concepts to registry backing assets, available
dashboard routes, planned concept-gallery cards, and table explorer deep links
without reading table rows, opening generated gold Markdown, or changing S3,
Dagster, ETL, or AWS permissions.

The schema data dictionary explorer stays inside the same read-only boundary.
It combines Dagster GraphQL table schema metadata with the concept-to-asset
mapping to group mapped `silver.gas_model` fields by Market context concept,
gas-model mart, asset, and dashboard route. Missing GraphQL or missing column
metadata remains visible as dashboard state instead of changing ETL schemas,
asset checks, generated docs, S3 data, or AWS permissions.

The data readiness overview remains within that read-only dashboard boundary.
It reuses the existing S3 discovery, Dagster GraphQL catalogue, and bounded-read
helper surfaces to show platform operations readiness without changing Dagster
asset definitions, ETL materialization behavior, LocalStack setup, or AWS
infrastructure.

The table explorer remains inside the same read-only boundary while acting as
the dashboard-roadmap workbench for selected table rows. It keeps existing
bounded preview, GraphQL fallback, and storage-only behavior, and now links
selected rows to the data readiness overview, AWS bounded-read diagnostics, and
registry-backed concept-gallery metadata for mapped `silver.gas_model` assets.

The materialization freshness dashboard stays inside the same boundary. It
uses Dagster GraphQL catalogue metadata plus the existing storage overlay to
show latest materialization timestamps, group and layer freshness gaps,
unmaterialized assets, GraphQL-unavailable rows, and storage-missing assets
without reading table contents, changing Dagster definitions, or adding AWS
write paths.

The AWS bounded-read diagnostics dashboard stays inside the same boundary. It
renders runtime location, endpoint mode, configured buckets, preview row caps,
full-table-scan state, bounded-read states, and per-dashboard read behavior
from Marimo environment configuration and registry metadata only, without
scanning S3 tables, calling Dagster GraphQL, changing AWS permissions, adding
write paths, or adding auto-refresh behavior.

The S3 Bucket Health dashboard stays inside the same boundary. It reuses the
table explorer's configured-bucket S3 discovery and table-prefix classifier,
then renders operator health states for reachable, empty, truncated, missing,
and unavailable buckets without changing S3 write paths, LocalStack
provisioning, bucket infrastructure, or ETL materialization behavior.

The system notices dashboard stays inside the same boundary. It reads the
curated `silver.gas_model.silver_gas_fact_system_notice` Parquet output through
the shared bounded loader and session cache, then filters and summarizes loaded
notice rows without changing system notice ETL, ingestion, alerting, or AWS
infrastructure.

The market prices dashboard stays inside the same boundary. It reads the
curated `silver.gas_model.silver_gas_fact_market_price` Parquet output through
the shared bounded loader and session cache, then filters and summarizes loaded
price rows without changing market price ETL, source ingestion, pricing
semantics, or asset schemas.

The schedule runs dashboard stays inside the same boundary. It reads the
curated `silver.gas_model.silver_gas_fact_schedule_run` Parquet output through
the shared bounded loader and session cache, then filters and summarizes loaded
schedule rows without changing schedule ETL, source ingestion, scheduling
semantics, or asset schemas.

The settlement activity dashboard stays inside the same boundary. It reads the
curated `silver.gas_model.silver_gas_fact_settlement_activity` Parquet output
through the shared bounded loader and session cache, then filters and
summarizes loaded settlement activity rows without changing settlement ETL,
source ingestion, settlement semantics, or asset schemas.

The customer transfer and retail activity dashboard stays inside the same
boundary. It reads the curated
`silver.gas_model.silver_gas_fact_customer_transfer` Parquet output through
the shared bounded loader and session cache, then filters and summarizes
loaded customer transfer rows without changing customer transfer ETL, source
ingestion, market-code semantics, or asset schemas.

The Bid / Offer stack dashboard stays inside the same boundary. It reads the
curated `silver.gas_model.silver_gas_fact_bid_stack` Parquet output through the
shared bounded loader and session cache, then filters and summarizes loaded bid
stack rows without changing bid stack ETL, source ingestion, participant or
facility modeling, or market semantics.

The gas quality and composition dashboard stays inside the same boundary. It
reads the curated `silver.gas_model.silver_gas_fact_gas_quality` Parquet output
through the shared bounded loader and session cache, then filters and
summarizes loaded quality and composition rows without changing gas quality ETL,
schemas, source ingestion, or quality calculations.

The source coverage matrix dashboard stays inside the same boundary. It reads
bounded rows from registry-backed `silver.gas_model` facts and dimensions,
expands `source_table` and `source_tables` metadata where present, and renders
missing source metadata as coverage gaps without changing ETL definitions,
source ingestion, asset schemas, or AWS infrastructure.

The source table lineage explorer stays inside the same boundary. It reuses
bounded source metadata reads and the table catalogue overlay to connect
curated `silver.gas_model` assets to source systems, source tables, extra
`source_*` lineage fields, registry concept cards, generated Market context
paths, table explorer links, and asset metadata links without changing ETL
lineage fields, generated gold Markdown, asset schemas, or AWS infrastructure.

The Gas Day explainer dashboard stays inside the same boundary. It renders the
registry-backed Gas Day context panel from copied generated-gold path and
source chunk metadata, then reads bounded samples from registry-backed
`silver.gas_model` assets to show date-field coverage and examples without
changing ETL date modeling, generated glossary files, asset schemas, or AWS
infrastructure.

The Facility explainer dashboard stays inside the same boundary. It renders
the registry-backed Facility context panel from copied generated-gold path and
source chunk metadata, then reads bounded samples from
`silver_gas_dim_facility`, `silver_gas_fact_facility_flow_storage`, and
`silver_gas_fact_capacity_outlook` to show facility standing-data coverage and
relationships to participant, zone, flow, storage, and capacity context without
changing ETL facility modeling, generated glossary files, asset schemas, or AWS
infrastructure.

The Flow operations dashboard stays inside the same boundary. It renders the
registry-backed Flow context panel from copied generated-gold path and source
chunk metadata, then reads bounded recent samples from
`silver_gas_fact_connection_point_flow`,
`silver_gas_fact_facility_flow_storage`,
`silver_gas_fact_nomination_forecast`, and
`silver_gas_fact_operational_meter_flow` to show source-system coverage and
recent/sample flow measures without changing ETL flow modeling, generated
glossary files, asset schemas, or AWS infrastructure.

The Facility flow and storage dashboard stays inside the same boundary. It
renders copied Facility, Flow, and Capacity context metadata from the Marimo
registry, then reads bounded recent samples from
`silver_gas_fact_facility_flow_storage` to show facility-level demand, supply,
transfer, storage, source-system coverage, source-table coverage, and latest
Gas Day without changing ETL flow/storage modeling, generated glossary files,
asset schemas, or AWS infrastructure.

The forecast-vs-actual dashboard stays inside the same boundary. It reads
bounded recent samples from `silver_gas_fact_nomination_forecast` and
`silver_gas_fact_facility_flow_storage`, joins only loaded rows with matching
Gas Day and source facility/location identifiers, and shows forecast-only or
actual-only groups when one input is unavailable without changing ETL grain,
forecast semantics, actual-flow modeling, or AWS infrastructure.

Static asset optimization stays limited to immutable HTTP caching for
content-hashed Marimo package assets. Extra preload changes, pre-serving
packaged WASM, and auto-refresh timer behavior remain deferred until route or
browser evidence shows a specific cold-start bottleneck.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `infrastructure/aws-pulumi/__main__.py`
  - `infrastructure/aws-pulumi/components/marimo.py`
  - `infrastructure/aws-pulumi/components/caddy.py`
  - `infrastructure/aws-pulumi/components/ecr.py`
  - `infrastructure/aws-pulumi/components/security_groups.py`
  - `infrastructure/aws-pulumi/components/service_discovery.py`
  - `backend-services/caddy/Caddyfile`
  - `backend-services/marimo/Dockerfile`
  - `backend-services/marimo/src/marimoserver/main.py`
  - `backend-services/marimo/src/marimoserver/dashboard_registry.py`
  - `backend-services/marimo/src/marimoserver/gas_dashboard.py`
  - `backend-services/marimo/src/marimoserver/bounded_read_diagnostics.py`
  - `backend-services/marimo/src/marimoserver/gas_model_loader.py`
  - `backend-services/marimo/src/marimoserver/table_explorer.py`
  - `backend-services/marimo/src/marimoserver/data_readiness.py`
  - `backend-services/marimo/src/marimoserver/glossary_explorer.py`
  - `backend-services/marimo/src/marimoserver/concept_asset_explorer.py`
  - `backend-services/marimo/src/marimoserver/data_dictionary_explorer.py`
  - `backend-services/marimo/src/marimoserver/citation_chain_explorer.py`
  - `backend-services/marimo/src/marimoserver/source_lineage_explorer.py`
  - `backend-services/marimo/notebooks/sample_energy_market.py`
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
  - `backend-services/marimo/notebooks/gas_settlement_activity.py`
  - `backend-services/marimo/notebooks/gas_customer_transfer_activity.py`
  - `backend-services/marimo/notebooks/facility_flow_storage.py`
  - `backend-services/marimo/notebooks/capacity_outlook.py`
  - `backend-services/marimo/notebooks/linepack_adequacy.py`
  - `backend-services/marimo/notebooks/nomination_demand_forecast.py`
  - `backend-services/marimo/notebooks/forecast_vs_actual.py`
  - `backend-services/marimo/notebooks/gas_bid_offer_stack.py`
  - `backend-services/marimo/notebooks/gas_quality_composition.py`
  - `backend-services/marimo/tests/component/test_dashboard_registry.py`
  - `backend-services/marimo/tests/component/test_main.py`
  - `backend-services/marimo/tests/component/test_local_image_split.py`
  - `backend-services/marimo/tests/component/test_table_explorer.py`
  - `backend-services/marimo/tests/component/test_data_readiness.py`
  - `backend-services/marimo/tests/component/test_dashboard_smoke.py`
  - `backend-services/marimo/tests/component/test_gas_dashboard.py`
  - `backend-services/marimo/tests/component/test_data_dictionary_explorer.py`
  - `backend-services/marimo/tests/component/test_glossary_explorer.py`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify routes, IAM permissions, Cloud Map names, env vars, and notebook limits`
