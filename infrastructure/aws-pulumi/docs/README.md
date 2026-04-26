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

## Related docs

- [AWS Pulumi infrastructure overview](../README.md)
- [Repository architecture](../../../docs/architecture.md)
- [Repository workflow](../../../docs/workflow.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `infrastructure/aws-pulumi/__main__.py`
  - `infrastructure/aws-pulumi/components/vpc.py`
  - `infrastructure/aws-pulumi/components/ecs_services.py`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
