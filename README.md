# Energy Market Delta Lake

Monorepo for ingesting, orchestrating, and serving Australian energy market
data. The repository is organized around **Subprojects**; use the owning
Subproject docs for detailed commands, defaults, diagrams, and behavior.

## Start here

- New repo maintainers: [docs/README.md](docs/README.md)
- Human operators: [OPERATOR.md](OPERATOR.md)
- Agents: [AGENTS.md](AGENTS.md) and
  [docs/agents/README.md](docs/agents/README.md)
- Canonical language: [CONTEXT.md](CONTEXT.md)

## Subprojects

- [backend-services](backend-services/README.md): local development and test
  stack for Dagster, LocalStack, Caddy, auth, Postgres, curated Marimo
  dashboards, and the local Marimo-Codex research workspace.
- [backend-services/dagster-user/aemo-etl](backend-services/dagster-user/aemo-etl/README.md):
  Dagster assets, sensors, resources, ETL internals, and **End-to-end test**
  defaults.
- [infrastructure/aws-pulumi](infrastructure/aws-pulumi/README.md): deployed
  AWS platform, Marimo dashboard, Dagster code-location manifest, and cloud
  validation.
- [tools/ralph-loop](tools/ralph-loop/README.md): packaged Ralph issue loop
  CLI, unit tests, and **Commit check** surface.
- [tools/gas-market-knowledge-base](tools/gas-market-knowledge-base/README.md):
  **Gas market knowledge base** tooling, bronze source manifest command,
  archive-prefix completeness audit, archive PDF cache fetcher,
  Docling-based silver document extraction, Docling Hybrid silver chunk
  generation, silver chunk index validation, gold **Market context** citation
  validation, seed glossary rendering helpers, external generated corpus
  roots, unit tests, and **Commit check** surface. ADR
  [0010](docs/adr/0010-gas-market-knowledge-base.md) records the corpus
  architecture.

## Repository docs

- [docs/repository/architecture.md](docs/repository/architecture.md): repo-level
  system boundaries and Subproject responsibilities.
- [docs/repository/workflow.md](docs/repository/workflow.md): production,
  local, operator, and agent workflow map.
- [docs/repository/documentation-sync.md](docs/repository/documentation-sync.md):
  maintained-doc contract, sync metadata, and doc QA ratchets.
- [docs/agents/ralph-loop.md](docs/agents/ralph-loop.md): Ralph internals,
  **Local integration**, **Delivery mode**, **Integration target**,
  **Issue completion review**, **Ready issue refresh**, **Exploratory
  acceptance review**, checkpointed Operator runs, **Promotion**,
  **Post-promotion review**, **Post-Promotion deployment classification**, and
  adaptive Ralph vocabulary, verified-only recovery, source-table archive replay
  recovery, and deploy-repair issue creation behavior.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `CONTEXT.md`
  - `OPERATOR.md`
  - `AGENTS.md`
  - `docs/README.md`
  - `docs/agents/README.md`
  - `docs/agents/ralph-loop.md`
  - `docs/repository/architecture.md`
  - `docs/repository/workflow.md`
  - `docs/repository/documentation-sync.md`
  - `docs/adr/0010-gas-market-knowledge-base.md`
  - `docs/adr/0011-ralph-adaptive-vocabulary-and-verified-recovery.md`
  - `backend-services/README.md`
  - `backend-services/dagster-user/aemo-etl/README.md`
  - `infrastructure/aws-pulumi/README.md`
  - `backend-services/dagster-core/code-locations.aws.toml`
  - `tools/ralph-loop/README.md`
  - `tools/gas-market-knowledge-base/README.md`
- `sync.scope`: `router`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `verify root routes point to owning docs`
