# AWS Pulumi Component Docs

Detailed subsystem documentation for the deployed AWS platform defined in
`infrastructure/aws-pulumi`.

## Table of contents

- [Pages](#pages)
- [Component map](#component-map)
- [Related docs](#related-docs)

## Pages

- [VPC architecture](vpc.md)
- [Connectivity](connectivity.md)
- [Identity and discovery](identity-and-discovery.md)
- [Storage](storage.md)
- [Runtime](runtime.md)
- [Edge and access](edge-and-access.md)
- [Security audit](security-audit.md)

## Component map

| Component class | Doc page |
|---|---|
| `VpcComponentResource` | [vpc.md](vpc.md) |
| `VpcEndpointsComponentResource` | [connectivity.md](connectivity.md) |
| `SecurityGroupsComponentResource` | [connectivity.md](connectivity.md) |
| `IamRolesComponentResource` | [identity-and-discovery.md](identity-and-discovery.md) |
| `ServiceDiscoveryComponentResource` | [identity-and-discovery.md](identity-and-discovery.md) |
| `S3BucketsComponentResource` | [storage.md](storage.md) |
| `DeltaLockingTableComponentResource` | [storage.md](storage.md) |
| `PostgresComponentResource` | [storage.md](storage.md) |
| `ECRComponentResource` | [runtime.md](runtime.md) |
| `EcsClusterComponentResource` | [runtime.md](runtime.md) |
| `DagsterUserCodeServiceComponentResource` | [runtime.md](runtime.md) |
| `DagsterWebserverServiceComponentResource` | [runtime.md](runtime.md) |
| `DagsterDaemonServiceComponentResource` | [runtime.md](runtime.md) |
| `BastionHostComponentResource` | [edge-and-access.md](edge-and-access.md) |
| `FastAPIAuthComponentResource` | [edge-and-access.md](edge-and-access.md) |
| `CaddyServerComponentResource` | [edge-and-access.md](edge-and-access.md) |

Security controls that span multiple components are summarized in
[security-audit.md](security-audit.md).
The Dagster user-code location manifest and its current exploratory review
boundary are described in [runtime.md](runtime.md).

## Related docs

- [AWS Pulumi infrastructure overview](../README.md)
- [Repository architecture](../../../docs/repository/architecture.md)
- [Repository workflow](../../../docs/repository/workflow.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `infrastructure/aws-pulumi/__main__.py`
  - `backend-services/dagster-core/code-locations.aws.toml`
  - `infrastructure/aws-pulumi/code_locations.py`
  - `infrastructure/aws-pulumi/components/vpc.py`
  - `infrastructure/aws-pulumi/components/ecs_services.py`
  - `infrastructure/aws-pulumi/docs/security-audit.md`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
