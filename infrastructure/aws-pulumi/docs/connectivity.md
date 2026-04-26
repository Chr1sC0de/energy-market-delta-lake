# Connectivity

This page covers the AWS-network connectivity controls layered on top of the
base VPC: VPC endpoints for private AWS API access and security groups for
service-to-service traffic.

## Table of contents

- [What this page covers](#what-this-page-covers)
- [VPC endpoint topology](#vpc-endpoint-topology)
- [Security-group trust graph](#security-group-trust-graph)
- [Component summary](#component-summary)
- [Traffic rules](#traffic-rules)
- [Related docs](#related-docs)

## What this page covers

- `VpcEndpointsComponentResource`
- `SecurityGroupsComponentResource`

The VPC itself, subnets, NAT instance, and route tables are documented in
[vpc.md](vpc.md).

## VPC endpoint topology

```mermaid
flowchart LR
    subgraph PrivateSubnet[Private subnet]
        ECS[ECS tasks]
        PG[Postgres EC2]
        AUTH[FastAPI auth EC2]
    end

    subgraph EndpointSG[VPC endpoint security group]
        EPSG[HTTPS from VPC CIDR]
    end

    subgraph InterfaceEndpoints[Interface endpoints]
        ECRAPI[ECR API]
        ECRDKR[ECR DKR]
        LOGS[CloudWatch Logs]
        SSM[SSM]
    end

    subgraph GatewayEndpoints[Gateway endpoints]
        S3[S3]
        DDB[DynamoDB]
    end

    ECS --> ECRAPI
    ECS --> ECRDKR
    ECS --> LOGS
    ECS --> SSM
    ECS --> S3
    ECS --> DDB
    AUTH --> ECRAPI
    AUTH --> ECRDKR
    PG --> SSM
    ECRAPI --- EPSG
    ECRDKR --- EPSG
    LOGS --- EPSG
    SSM --- EPSG
```

The component creates:

- interface endpoints in the private subnet for `ecr.api`, `ecr.dkr`, `logs`,
  and `ssm`
- gateway endpoints attached to the private route table for `s3` and
  `dynamodb`
- one dedicated security group allowing HTTPS from the VPC CIDR to the
  interface endpoints

## Security-group trust graph

```mermaid
flowchart LR
    ADMIN[Administrator IPs]
    BASTION[Bastion SG]
    CADDY[Caddy SG]
    AUTH[FastAPI auth SG]
    WEB[Dagster webserver SG]
    USERCODE[Dagster user-code SG]
    DAEMON[Dagster daemon SG]
    PG[Postgres SG]

    ADMIN -->|SSH 22| BASTION
    ADMIN -->|SSH 22| CADDY
    INTERNET[Internet] -->|HTTP 80 / HTTPS 443| CADDY
    CADDY -->|8000| AUTH
    CADDY -->|3000| WEB
    BASTION -->|3000| WEB
    WEB -->|4000| USERCODE
    DAEMON -->|4000| USERCODE
    WEB -->|5432| PG
    USERCODE -->|5432| PG
    DAEMON -->|5432| PG
    BASTION -->|5432| PG
    BASTION -->|SSH 22| AUTH
```

## Component summary

| Component | Key resources | Purpose |
|---|---|---|
| `VpcEndpointsComponentResource` | endpoint SG, 4 interface endpoints, 2 gateway endpoints | Keep AWS API access inside the VPC where possible |
| `SecurityGroupsComponentResource` | 7 service security groups plus explicit ingress/egress rules | Encode allowed operator access and service-to-service paths |

## Traffic rules

- Caddy is the only internet-facing service security group.
- FastAPI auth is private and only accepts traffic from Caddy plus SSH from the
  bastion host.
- Dagster webservers accept port `3000` from Caddy and the bastion host.
- Dagster user-code accepts gRPC port `4000` only from the webserver and
  daemon.
- Postgres accepts port `5432` from the Dagster ECS services plus the bastion
  host for manual administration.
- The daemon has no inbound rules because it only initiates outbound
  connections.

## Related docs

- [VPC architecture](vpc.md)
- [Identity and discovery](identity-and-discovery.md)
- [Runtime](runtime.md)
- [Edge and access](edge-and-access.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `infrastructure/aws-pulumi/components/vpc_endpoints.py`
  - `infrastructure/aws-pulumi/components/security_groups.py`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
