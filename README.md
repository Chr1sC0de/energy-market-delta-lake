# Energy Market Delta Lake

Monorepo for ingesting, orchestrating, and serving Australian energy market data.

The canonical system architecture is the AWS deployment provisioned from
`infrastructure/aws-pulumi`. Local compose under `backend-services/` exists to
support development, testing, and validation of the deployed platform.

## Table of contents

- [What this repo contains](#what-this-repo-contains)
- [Canonical architecture](#canonical-architecture)
- [Workflow](#workflow)
- [Repository layout](#repository-layout)
- [Local development and testing](#local-development-and-testing)
- [Documentation map](#documentation-map)
- [Prerequisites](#prerequisites)
- [Tooling](#tooling)
- [Commands](#commands)
- [Deployment](#deployment)

## What this repo contains

- Dagster-based ETL code in `backend-services/dagster-user/aemo-etl`
- Dagster runtime, auth, proxy, and local support services in `backend-services`
- AWS infrastructure as code in `infrastructure/aws-pulumi`

## Canonical architecture

```mermaid
flowchart LR
  subgraph Sources[External sources]
    A[AEMO / NEMWeb / VICGAS / GBB]
  end

  subgraph Edge[Public edge]
    B[Caddy]
    C[Authentication service]
  end

  subgraph Dagster[Dagster on AWS]
    D[Dagster webserver admin]
    E[Dagster webserver guest]
    F[Dagster daemon]
    G[aemo-etl user-code gRPC service]
  end

  subgraph Data[State and storage]
    H[(S3 Delta + landing/archive buckets)]
    I[(PostgreSQL Dagster metadata)]
    J[(DynamoDB delta_log lock table)]
  end

  subgraph Platform[AWS platform]
    K[VPC + endpoints + security groups]
    L[ECS + Cloud Map + IAM + ECR]
  end

  A --> G
  B --> C
  B --> D
  B --> E
  C --> D
  D --> G
  E --> G
  F --> G
  G --> H
  F --> H
  G --> J
  D --> I
  E --> I
  F --> I
  K --> L
  L --> D
  L --> E
  L --> F
  L --> G
```

The deployed stack provisions:

- public Caddy entrypoint on EC2
- FastAPI authentication service
- Dagster admin and guest webservers
- Dagster daemon
- `aemo-etl` gRPC user-code service
- PostgreSQL for Dagster run, schedule, and event-log storage
- S3 buckets for landing, archive, Delta tables, and IO-manager payloads
- DynamoDB `delta_log` locking table
- VPC, endpoints, security groups, IAM roles, ECR repositories, ECS, and Cloud Map

See [docs/architecture.md](docs/architecture.md) for the fuller system view.

## Workflow

At a high level the deployed workflow is:

1. Discovery assets poll public AEMO/NEMWeb sources and land files in S3.
1. Unzipper sensors expand zipped inputs and archive successful zip payloads.
1. Event-driven bronze assets ingest landed files into Delta tables.
1. Source-specific silver assets deduplicate and standardize current-state tables.
1. `gas_model` assets build shared dimensions and marts from the source silver layer.
1. A daily Delta maintenance job compacts and full-vacuums Delta-backed tables.
1. Dagster metadata and orchestration state live in PostgreSQL, while data products live in S3-backed Delta tables.

The orchestration details come from the Dagster definitions in
`backend-services/dagster-user/aemo-etl`, including event-driven sensors and
automation-conditioned downstream assets. The Delta maintenance schedule runs
`delta_table_vacuum_job` at 02:00 Australia/Melbourne and uses full vacuum
retention `0` for unreferenced Delta files unless an asset overrides maintenance
settings in its metadata.

See [docs/workflow.md](docs/workflow.md) for the repo-level workflow summary and
[backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md](backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md)
for ETL internals.

## Repository layout

```text
energy-market-delta-lake/
├── backend-services/                 # Local dev/test harness and service source
│   ├── dagster-core/                 # Dagster webserver/daemon image and config
│   ├── dagster-user/aemo-etl/        # Dagster code location and ETL docs
│   ├── authentication/               # OIDC session/auth service
│   ├── caddy/                        # Reverse proxy image/config
│   ├── marimo/                       # Local notebook service
│   ├── localstack/                   # Local AWS emulation bootstrap
│   └── postgres/                     # Local PostgreSQL image/setup
├── docs/                             # Repo-level architecture and workflow docs
├── infrastructure/
│   └── aws-pulumi/                   # Canonical AWS deployment definitions
└── scripts/                          # Repo-level helper scripts
```

## Local development and testing

`backend-services/compose.yaml` is a local development and testing harness. It is
useful for validating service interactions, running Dagster locally, and working
against LocalStack-backed storage, but it is not the primary architecture.

Typical local flow:

```bash
cd backend-services
source .envrc
podman-compose up --build -d
```

The local entrypoint is Caddy at `https://localhost`.

Use the local stack when you need:

- local Dagster UI and daemon behavior
- LocalStack-backed S3 and DynamoDB-compatible workflows
- local auth/proxy integration checks
- notebook experimentation through `marimo`

See [backend-services/README.md](backend-services/README.md) for the local stack.

## Documentation map

Follow the docs in repository order:

### `docs/`

- [docs/architecture.md](docs/architecture.md)
- [docs/agent-issue-loop.md](docs/agent-issue-loop.md)
- [docs/documentation-sync.md](docs/documentation-sync.md)
- [docs/workflow.md](docs/workflow.md)
- [docs/agents/issue-tracker.md](docs/agents/issue-tracker.md)
- [docs/agents/triage-labels.md](docs/agents/triage-labels.md)
- [docs/agents/domain.md](docs/agents/domain.md)

### `backend-services/`

- [backend-services/README.md](backend-services/README.md)
- [backend-services/authentication/README.md](backend-services/authentication/README.md)
- [backend-services/marimo/README.md](backend-services/marimo/README.md)

### `backend-services/dagster-user/aemo-etl/`

- [backend-services/dagster-user/aemo-etl/README.md](backend-services/dagster-user/aemo-etl/README.md)
- [backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md](backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md)
- [backend-services/dagster-user/aemo-etl/docs/gas_model/README.md](backend-services/dagster-user/aemo-etl/docs/gas_model/README.md)

### `infrastructure/aws-pulumi/`

- [infrastructure/aws-pulumi/README.md](infrastructure/aws-pulumi/README.md)
- [infrastructure/aws-pulumi/docs/README.md](infrastructure/aws-pulumi/docs/README.md)
- [infrastructure/aws-pulumi/docs/vpc.md](infrastructure/aws-pulumi/docs/vpc.md)

## Prerequisites

| Tool | Suggested version | Used for |
|---|---:|---|
| Python | 3.11+ | Repo tooling and service development |
| uv | latest | Python dependency and tool management |
| Podman + podman-compose | see `backend-services/README.md` | Local test/dev stack |
| Pulumi CLI | latest | AWS infrastructure deployment |
| `prek` | latest | Repository lint/format/test hooks |
| `lychee` | latest | Offline root Markdown link checks |

## Tooling

`prek` is the workspace hook runner for this repo. Run it from the repository
root so it can discover the root hooks and subproject hook configs.

The configured hooks cover:

- generic file hygiene from `pre-commit-hooks`, including trailing whitespace,
  final newlines, YAML syntax, and large-file checks
- Dockerfile linting with `hadolint`
- Markdown linting and formatting with `rumdl`
- offline root Markdown link checking with `lychee`
- shell formatting, linting, and executable-script header documentation with
  `shfmt`, `shellcheck`, and `scripts/check_shell_script_headers.py`
- Python project metadata formatting with `pyproject-fmt`
- Python linting and formatting with `ruff`
- Python type checking with `zuban`
- Python tests with `pytest`, split into explicit unit, component,
  integration, and deployed lanes where a subproject needs them
- Dagster definition and config validation with `dg check defs`,
  `dg check toml`, and `dg check yaml` for the ETL project

Most Python project hooks run through `uv run` inside the project that owns the
hook config. System hooks such as `shellcheck` must also be available on
`PATH` where the relevant subproject config uses them directly.

## Commands

| Scope | Command |
|---|---|
| Install git hooks | `prek install` |
| Repository-wide hooks | `prek run -a` |
| Root Markdown link check | `prek run lychee -a` |
| ETL fast tests | `cd backend-services/dagster-user/aemo-etl && make fast-test` |
| ETL local integration tests | `cd backend-services/dagster-user/aemo-etl && make integration-test` |
| AWS Pulumi fast tests | `cd infrastructure/aws-pulumi && uv run pytest tests/unit tests/component -x -q` |
| AWS Pulumi deployed tests | `cd infrastructure/aws-pulumi && PULUMI_INTEGRATION_TESTS=1 uv run pytest tests/deployed -v` |
| Local stack | `cd backend-services && source .envrc && podman-compose up --build -d` |

## Deployment

Pulumi is the source of truth for deployed infrastructure:

```bash
cd infrastructure/aws-pulumi
pulumi preview
pulumi up
```

See [infrastructure/aws-pulumi/README.md](infrastructure/aws-pulumi/README.md)
for stack details, component breakdown, and deployed-test commands.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `.pre-commit-config.yaml`
  - `CONTEXT.md`
  - `AGENTS.md`
  - `backend-services/.pre-commit-config.yaml`
  - `backend-services/authentication/.pre-commit-config.yaml`
  - `backend-services/dagster-user/aemo-etl/.pre-commit-config.yaml`
  - `backend-services/dagster-user/aemo-etl/Makefile`
  - `backend-services/marimo/.pre-commit-config.yaml`
  - `infrastructure/aws-pulumi/__main__.py`
  - `infrastructure/aws-pulumi/.pre-commit-config.yaml`
  - `infrastructure/aws-pulumi/scripts/run-integration-tests`
  - `backend-services/compose.yaml`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/delta_tables.py`
  - `scripts/check_shell_script_headers.py`
  - `scripts/ralph.py`
- `sync.scope`: `architecture, tooling`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
