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
  stack for Dagster, LocalStack, Caddy, auth, Postgres, and notebooks.
- [backend-services/dagster-user/aemo-etl](backend-services/dagster-user/aemo-etl/README.md):
  Dagster assets, sensors, resources, ETL internals, and **End-to-end test**
  defaults.
- [infrastructure/aws-pulumi](infrastructure/aws-pulumi/README.md): deployed
  AWS platform and cloud validation.

## Repository docs

- [docs/repository/architecture.md](docs/repository/architecture.md): repo-level
  system boundaries and Subproject responsibilities.
- [docs/repository/workflow.md](docs/repository/workflow.md): production,
  local, operator, and agent workflow map.
- [docs/repository/documentation-sync.md](docs/repository/documentation-sync.md):
  maintained-doc contract, sync metadata, and doc QA ratchets.
- [docs/agents/ralph-loop.md](docs/agents/ralph-loop.md): Ralph internals,
  **Local integration**, **Delivery mode**, **Integration target**,
  **Ready issue refresh**, checkpointed Operator runs, **Promotion**, and
  **Post-promotion review** behavior.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `CONTEXT.md`
  - `OPERATOR.md`
  - `AGENTS.md`
  - `docs/README.md`
  - `docs/agents/README.md`
  - `docs/repository/architecture.md`
  - `docs/repository/workflow.md`
  - `docs/repository/documentation-sync.md`
  - `backend-services/README.md`
  - `backend-services/dagster-user/aemo-etl/README.md`
  - `infrastructure/aws-pulumi/README.md`
- `sync.scope`: `router`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify root routes point to owning docs`
