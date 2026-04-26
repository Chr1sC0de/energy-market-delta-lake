# AWS Pulumi Infrastructure

Pulumi program for the deployed AWS energy-market platform.

This directory is the source of truth for the main runtime architecture. It
provisions the network, storage, container images, compute platform, and public
entrypoint used by the Dagster-based deployment.

## Table of contents

- [What this stack provisions](#what-this-stack-provisions)
- [Architecture summary](#architecture-summary)
- [Component order](#component-order)
- [Container images and service source](#container-images-and-service-source)
- [Runtime behavior](#runtime-behavior)
- [Configuration](#configuration)
- [Common commands](#common-commands)
- [Relationship to local development](#relationship-to-local-development)
- [Related docs](#related-docs)

## What this stack provisions

From `__main__.py`, the stack builds these layers:

- networking: VPC, public/private subnets, route tables, and VPC endpoints
- security: security groups and IAM roles for EC2 and ECS tasks
- data services: S3 buckets, DynamoDB `delta_log`, PostgreSQL, and a bastion host
- container platform: ECR repositories and image builds, ECS cluster, Cloud Map
- public services: Caddy reverse proxy and FastAPI authentication service
- Dagster services:
  - `aemo-etl` user-code gRPC service
  - Dagster webserver admin
  - Dagster webserver guest
  - Dagster daemon

## Architecture summary

```mermaid
flowchart LR
  subgraph Internet[Internet]
    U[Users]
    S[AEMO / NEMWeb sources]
  end

  subgraph Edge[Public edge]
    C[Caddy EC2 instance]
    A[FastAPI auth EC2 instance]
  end

  subgraph AWS[AWS private services]
    W[Dagster webserver admin ECS service]
    G[Dagster webserver guest ECS service]
    D[Dagster daemon ECS service]
    UCODE[aemo-etl user-code ECS service]
    P[(PostgreSQL EC2)]
    B[(S3 buckets)]
    L[(DynamoDB delta_log)]
    M[Cloud Map namespace]
  end

  subgraph Platform[Platform resources]
    V[VPC + endpoints]
    SG[Security groups]
    IAM[IAM roles]
    E[ECR images]
    ECS[ECS cluster]
  end

  U --> C
  C --> A
  C --> W
  C --> G
  A --> W
  W --> UCODE
  G --> UCODE
  D --> UCODE
  UCODE --> B
  D --> B
  UCODE --> L
  W --> P
  G --> P
  D --> P
  M --> UCODE
  M --> W
  M --> G
  V --> SG
  SG --> ECS
  IAM --> ECS
  E --> ECS
```

## Component order

The dependency order in `__main__.py` is deliberate:

1. `VpcComponentResource`
1. `VpcEndpointsComponentResource`
1. `SecurityGroupsComponentResource`
1. `IamRolesComponentResource`
1. `S3BucketsComponentResource`
1. `DeltaLockingTableComponentResource`
1. `ECRComponentResource`
1. `ServiceDiscoveryComponentResource`
1. `PostgresComponentResource`
1. `BastionHostComponentResource`
1. `EcsClusterComponentResource`
1. `FastAPIAuthComponentResource`
1. `CaddyServerComponentResource`
1. `DagsterUserCodeServiceComponentResource`
1. `DagsterWebserverServiceComponentResource` for admin
1. `DagsterWebserverServiceComponentResource` for guest
1. `DagsterDaemonServiceComponentResource`

In practical terms:

- the network and access controls are created first
- shared storage and image registry come next
- compute and service discovery follow
- public-facing and Dagster runtime services are created last

## Container images and service source

`components/ecr.py` builds and pushes the deployed images directly from the
repository:

- `backend-services/dagster-core` for Dagster webserver and daemon
- `backend-services/dagster-user/aemo-etl` for the gRPC user-code service
- `backend-services/authentication` for the auth service
- `backend-services/caddy` for the public reverse proxy

The Pulumi deployment uses the AWS-targeted Dagster configuration by building
`dagster-core` with `DAGSTER_DEPLOYMENT=aws`.

## Runtime behavior

Key deployed behaviors visible in the infrastructure code:

- Caddy runs on a public EC2 instance and proxies to:
  - `webserver-admin.dagster:3000`
  - `webserver-guest.dagster:3000`
  - the FastAPI auth service
- Dagster services run as ECS Fargate services in private subnets
- Cloud Map provides private DNS names under the `dagster` namespace
- PostgreSQL is used for Dagster run, schedule, and event-log storage
- S3 holds landing, archive, Delta-table, and IO-manager data
- DynamoDB `delta_log` supports Delta locking

## Configuration

This project reads a small set of important config values:

- `ENVIRONMENT`
  - defaults to `dev`
  - contributes to the shared resource prefix
- `ADMINISTRATOR_IPS`
  - used outside local mode for admin-access configuration
- `aws:region`
  - stack region, shown in `Pulumi.dev-ausenergymarket.yaml` as `ap-southeast-2`
- Pulumi secrets for Cognito/auth and public site configuration:
  - `aws-pulumi:cognito_client_id`
  - `aws-pulumi:cognito_server_metadata_url`
  - `aws-pulumi:cognito_token_signing_key_url`
  - `aws-pulumi:cognito_client_secret`
  - `aws-pulumi:website_root_url`
  - `aws-pulumi:developer_email`

The stack name prefix resolves to `"{ENVIRONMENT}-energy-market"`.

## Common commands

Preview infrastructure changes:

```bash
pulumi preview
```

Apply infrastructure changes:

```bash
pulumi up
```

Run the full integration workflow against the default stack:

```bash
AWS_DEFAULT_REGION=ap-southeast-2 scripts/run-integration-tests
```

Run integration tests without applying infrastructure first:

```bash
AWS_DEFAULT_REGION=ap-southeast-2 scripts/run-integration-tests --skip-up
```

Run the integration suite directly:

```bash
PULUMI_INTEGRATION_TESTS=1 PULUMI_STACK=dev-ausenergymarket uv run pytest tests/integration -v
```

## Relationship to local development

The local compose setup under `backend-services/` is not the canonical
architecture. It exists to support development and testing of the deployed
system's services and Dagster workflows.

- Use this directory when you are provisioning or validating AWS resources.
- Use `backend-services/` when you need a local test/dev harness.
- Use `backend-services/dagster-user/aemo-etl/` for ETL definitions and
  Dagster-specific data pipeline docs.

## Related docs

- [Repository overview](../../README.md)
- [Repository architecture](../../docs/architecture.md)
- [Repository workflow](../../docs/workflow.md)
- [VPC architecture notes](docs/vpc.md)
- [Local backend-services stack](../../backend-services/README.md)
