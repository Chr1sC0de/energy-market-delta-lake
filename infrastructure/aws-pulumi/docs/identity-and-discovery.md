# Identity And Discovery

This page covers the control-plane components that let instances and tasks
assume the correct permissions and discover one another inside the private
network.

## Table of contents

- [What this page covers](#what-this-page-covers)
- [IAM role model](#iam-role-model)
- [Service discovery topology](#service-discovery-topology)
- [Component summary](#component-summary)
- [Permission boundaries](#permission-boundaries)
- [Related docs](#related-docs)

## What this page covers

- `IamRolesComponentResource`
- `ServiceDiscoveryComponentResource`

## IAM role model

```mermaid
flowchart TB
    subgraph EC2Roles[EC2 instance roles]
        BASTIONROLE[Bastion role]
        BASTIONPROFILE[Bastion instance profile]
    end

    subgraph ECSRoles[ECS task roles]
        WEBEXEC[Webserver execution role]
        WEBTASK[Webserver task role]
        DAEMONEXEC[Daemon execution role]
        DAEMONTASK[Daemon task role]
    end

    SSM[Amazon SSM Managed Instance / ReadOnly]
    ECRPOLICY[ECS task execution policy]
    ECSAPI[ECS orchestration APIs]
    DDB[DynamoDB delta_log]
    S3[S3 data-lake buckets]
    SECRETS[Secrets Manager]

    BASTIONROLE --> SSM
    BASTIONPROFILE --> BASTIONROLE
    WEBEXEC --> ECRPOLICY
    DAEMONEXEC --> ECRPOLICY
    WEBTASK --> ECSAPI
    DAEMONTASK --> ECSAPI
    DAEMONTASK --> DDB
    DAEMONTASK --> S3
    DAEMONTASK --> SECRETS
```

The role split is deliberate:

- execution roles cover image pulls, task startup, and log shipping
- task roles cover what the running containers can do at runtime
- the daemon task role is broader because it launches and supervises Dagster
  work on ECS

## Service discovery topology

```mermaid
flowchart LR
    subgraph CloudMap[Cloud Map namespace: dagster]
        NAMESPACE[Private DNS namespace]
        UCODE[aemo-etl]
        ADMIN[webserver-admin]
        GUEST[webserver-guest]
    end

    subgraph Callers[Private callers]
        CADDY[Caddy]
        WEB[Dagster webservers]
        DAEMON[Dagster daemon]
    end

    WEB --> UCODE
    DAEMON --> UCODE
    CADDY --> ADMIN
    CADDY --> GUEST
    NAMESPACE --> UCODE
    NAMESPACE --> ADMIN
    NAMESPACE --> GUEST
```

The namespace is private to the VPC and currently backs:

- `aemo-etl.dagster:4000`
- `webserver-admin.dagster:3000`
- `webserver-guest.dagster:3000`

The daemon is not registered because it does not accept inbound traffic.

## Component summary

| Component | Key resources | Purpose |
|---|---|---|
| `IamRolesComponentResource` | 1 EC2 instance profile, 2 ECS execution roles, 2 ECS task roles | Separate bootstrap permissions from runtime permissions |
| `ServiceDiscoveryComponentResource` | 1 Cloud Map private DNS namespace | Give private service names to the ECS runtime |

## Permission boundaries

- The bastion host gets SSM-centric EC2 permissions through an instance
  profile.
- The webserver task role can inspect and stop ECS tasks and pass roles to
  ECS tasks when launching work.
- The daemon execution role adds `ssm:GetParameters` so daemon tasks can start
  cleanly with their bootstrap configuration.
- The daemon task role includes:
  - ECS orchestration calls
  - Secrets Manager reads
  - DynamoDB access to `delta_log`
  - S3 access to the environment-scoped `*-energy-market*` buckets
  - `iam:PassRole` for ECS task launches

## Related docs

- [Connectivity](connectivity.md)
- [Storage](storage.md)
- [Runtime](runtime.md)
- [Edge and access](edge-and-access.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `infrastructure/aws-pulumi/components/iam_roles.py`
  - `infrastructure/aws-pulumi/components/service_discovery.py`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
