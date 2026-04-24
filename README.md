# Energy Market Delta Lake

Monorepo for ingesting, orchestrating, and serving Australian energy market data.
The repository combines:

- **Data pipelines** (Dagster + `aemo-etl`) for extraction and transformation.
- **Runtime services** (authentication, notebooks, reverse-proxy, local dependencies).
- **Infrastructure as code** (Pulumi on AWS).
- **Specifications and migration notes** for planned and in-progress work.

## High-level architecture

```mermaid
flowchart LR
  subgraph Sources[External data sources]
    A[AEMO / NEMWeb / VICGAS / GBB]
  end

  subgraph Pipelines[Data pipelines]
    B[aemo-etl Dagster code location]
    C[Dagster webserver + daemon]
  end

  subgraph Storage[Data/storage layer]
    D[(S3 / LocalStack buckets)]
    E[(PostgreSQL Dagster metadata)]
  end

  subgraph Consumers[Consumer-facing services]
    F[Authentication service]
    G[Marimo service]
    H[Caddy]
  end

  subgraph Infra[AWS infrastructure]
    I[Pulumi components]
  end

  A --> B
  B --> D
  B --> E
  C --> B
  C --> E
  F --> C
  G --> C
  H --> F
  I --> C
  I --> D
  I --> E
```

## Repository tree (high-level)

```text
energy-market-delta-lake/
├── backend-services/                 # Local runtime stack and application services
│   ├── compose.yaml                  # Local Dagster stack composition
│   ├── dagster-core/                 # Dagster webserver/daemon image and configs
│   ├── dagster-user/aemo-etl/        # Dagster code location and ETL assets
│   ├── authentication/               # Auth API service
│   ├── marimo/                       # Notebook/application service
│   ├── caddy/                        # Reverse proxy/static entrypoint
│   ├── localstack/                   # Local AWS emulation setup
│   └── postgres/                     # Local Postgres setup
├── infrastructure/
│   └── aws-pulumi/                   # AWS infrastructure definitions and tests
├── specs/                            # Design docs, migration plans, technical notes
├── scripts/                          # Repository-level helper scripts
└── .pre-commit-config.yaml           # Repository quality/lint entrypoint
```

## Component map

- **`backend-services/`**
  - Primary application runtime for local development, centered around Dagster.
  - See `backend-services/README.md` for full local stack setup and operations.
- **`backend-services/dagster-user/aemo-etl/`**
  - Core ETL definitions, sensors, factories, and tests for market datasets.
- **`infrastructure/aws-pulumi/`**
  - Cloud resources and deployment logic for AWS environments.
- **`specs/`**
  - Architecture decisions, migration plans, and implementation notes.
- **`scripts/` + root pre-commit config**
  - Repository workflow tooling (kept secondary to product architecture).

## Where to start

### Run the local backend stack

Follow `backend-services/README.md` to launch the local Dagster stack with
Postgres and LocalStack.

### Work on ETL pipeline code

Start in `backend-services/dagster-user/aemo-etl/README.md`.

### Work on AWS infrastructure

Start in `infrastructure/aws-pulumi/README.md`.

## Development workflow

- Use pre-commit hooks from the repository root:

```bash
prek run -a
```

- Service-specific tests and commands should be run from each sub-project
  directory (`backend-services/...`, `infrastructure/aws-pulumi/...`).
