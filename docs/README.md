# Documentation Map

Use this page as the human documentation map by task and **Subproject**. Root
and index pages route to owning pages; detailed commands, defaults, diagrams,
and behavior belong on the owning Subproject or repository page.

## By task

- Shape, drain, review `dev`, run **Promotion**, or inspect a checkpointed
  Operator run:
  [OPERATOR.md](../OPERATOR.md)
- Return to the root router:
  [README.md](../README.md)
- Read canonical repo language:
  [CONTEXT.md](../CONTEXT.md)
- Understand repo architecture:
  [repository/architecture.md](repository/architecture.md)
- Understand production and local workflow:
  [repository/workflow.md](repository/workflow.md)
- Maintain docs and sync metadata:
  [repository/documentation-sync.md](repository/documentation-sync.md)
- Follow agent policy:
  [AGENTS.md](../AGENTS.md)
- Find agent workflow docs:
  [agents/README.md](agents/README.md)
- Inspect ADRs:
  [adr/](adr/)

## By Subproject

- Local stack:
  [backend-services/README.md](../backend-services/README.md)
- Authentication service:
  [backend-services/authentication/README.md](../backend-services/authentication/README.md)
- Marimo notebook service:
  [backend-services/marimo/README.md](../backend-services/marimo/README.md)
- AEMO ETL:
  [backend-services/dagster-user/aemo-etl/README.md](../backend-services/dagster-user/aemo-etl/README.md)
- AEMO ETL architecture:
  [backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md](../backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md)
- AEMO ETL ingestion flows:
  [backend-services/dagster-user/aemo-etl/docs/architecture/ingestion_flows.md](../backend-services/dagster-user/aemo-etl/docs/architecture/ingestion_flows.md)
- AEMO ETL gas model:
  [backend-services/dagster-user/aemo-etl/docs/gas_model/README.md](../backend-services/dagster-user/aemo-etl/docs/gas_model/README.md)
- AWS Pulumi platform:
  [infrastructure/aws-pulumi/README.md](../infrastructure/aws-pulumi/README.md)
- AWS Pulumi component docs:
  [infrastructure/aws-pulumi/docs/README.md](../infrastructure/aws-pulumi/docs/README.md)

## Repository pages

- [repository/architecture.md](repository/architecture.md)
- [repository/workflow.md](repository/workflow.md)
- [repository/documentation-sync.md](repository/documentation-sync.md)
- [agents/README.md](agents/README.md)
- [agents/ralph-loop.md](agents/ralph-loop.md)
- [agents/issue-tracker.md](agents/issue-tracker.md)
- [agents/triage-labels.md](agents/triage-labels.md)
- [agents/domain.md](agents/domain.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `README.md`
  - `OPERATOR.md`
  - `AGENTS.md`
  - `CONTEXT.md`
  - `docs/agents/README.md`
  - `docs/repository/architecture.md`
  - `docs/repository/workflow.md`
  - `docs/repository/documentation-sync.md`
  - `backend-services/README.md`
  - `backend-services/authentication/README.md`
  - `backend-services/marimo/README.md`
  - `backend-services/dagster-user/aemo-etl/README.md`
  - `backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md`
  - `backend-services/dagster-user/aemo-etl/docs/architecture/ingestion_flows.md`
  - `backend-services/dagster-user/aemo-etl/docs/gas_model/README.md`
  - `infrastructure/aws-pulumi/README.md`
  - `infrastructure/aws-pulumi/docs/README.md`
- `sync.scope`: `router`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify task and Subproject coverage links resolve`
