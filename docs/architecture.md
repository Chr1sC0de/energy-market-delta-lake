# Repository Architecture

This repository's main architecture is the AWS deployment provisioned from
`infrastructure/aws-pulumi`. The local compose stack exists to support
development and testing of that deployed platform.

## Table of contents

- [AWS deployed system](#aws-deployed-system)
- [Local test and development harness](#local-test-and-development-harness)
- [Repository responsibilities](#repository-responsibilities)
- [Related docs](#related-docs)

## AWS deployed system

```mermaid
flowchart LR
  subgraph Sources[External sources]
    SRC[AEMO / NEMWeb public files]
  end

  subgraph Public[Public entry]
    C[Caddy]
    AUTH[Authentication service]
  end

  subgraph Dagster[Dagster runtime]
    ADMIN[Webserver admin]
    GUEST[Webserver guest]
    DAEMON[Daemon]
    USERCODE[aemo-etl gRPC user code]
  end

  subgraph Data[State and storage]
    S3[(S3 buckets)]
    PG[(PostgreSQL)]
    DDB[(DynamoDB delta_log)]
  end

  subgraph AWS[AWS platform]
    VPC[VPC + endpoints]
    ECS[ECS cluster]
    CM[Cloud Map]
    ECR[ECR]
    IAM[IAM roles]
    SG[Security groups]
  end

  SRC --> USERCODE
  C --> AUTH
  C --> ADMIN
  C --> GUEST
  AUTH --> ADMIN
  ADMIN --> USERCODE
  GUEST --> USERCODE
  DAEMON --> USERCODE
  USERCODE --> S3
  DAEMON --> S3
  USERCODE --> DDB
  ADMIN --> PG
  GUEST --> PG
  DAEMON --> PG
  VPC --> SG
  IAM --> ECS
  SG --> ECS
  ECR --> ECS
  ECS --> ADMIN
  ECS --> GUEST
  ECS --> DAEMON
  ECS --> USERCODE
  CM --> ADMIN
  CM --> GUEST
  CM --> USERCODE
```

## Local test and development harness

```mermaid
flowchart LR
  subgraph Local[Local compose environment]
    CADDY[Caddy]
    AUTH[Authentication]
    ADMIN[Dagster admin]
    GUEST[Dagster guest]
    DAEMON[Dagster daemon]
    USERCODE[aemo-etl]
    LS[LocalStack]
    PG[(Postgres)]
    MARIMO[Marimo]
  end

  CADDY --> AUTH
  CADDY --> ADMIN
  CADDY --> GUEST
  CADDY --> MARIMO
  AUTH --> ADMIN
  ADMIN --> USERCODE
  GUEST --> USERCODE
  DAEMON --> USERCODE
  USERCODE --> LS
  DAEMON --> LS
  ADMIN --> PG
  GUEST --> PG
  DAEMON --> PG
```

This local stack is intentionally broader than the deployed stack in some areas.
For example, `marimo` is part of local compose but is not provisioned by the
current Pulumi deployment.

## Repository responsibilities

- `infrastructure/aws-pulumi`
  - provisions the canonical AWS platform and deployed runtime
- `backend-services/dagster-user/aemo-etl`
  - defines Dagster assets, sensors, resources, and ETL-specific docs
- `backend-services/dagster-core`
  - provides the Dagster runtime image and environment-specific configuration
- `backend-services/authentication`
  - implements the OIDC/session bridge used in front of protected routes
- `backend-services/caddy`
  - provides the reverse-proxy image and routing rules
- `backend-services/marimo`
  - local notebook-oriented service used in the test/dev harness
- `specs`
  - captures migration notes, design intent, and implementation plans

## Related docs

- [Repository workflow](workflow.md)
- [AWS Pulumi infrastructure](../infrastructure/aws-pulumi/README.md)
- [aemo-etl architecture](../backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md)
- [Specs and design notes](../specs/README.md)
