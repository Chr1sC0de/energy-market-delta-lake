# Edge And Access

This page documents the EC2-based access layer around the private Dagster
runtime: the bastion host for operators, the FastAPI auth host, and the public
Caddy reverse proxy, and the private Marimo dashboard reached through Caddy.

## Table of contents

- [What this page covers](#what-this-page-covers)
- [Public request flow](#public-request-flow)
- [Operator access flow](#operator-access-flow)
- [Component summary](#component-summary)
- [Implementation notes](#implementation-notes)
- [Related docs](#related-docs)

## What this page covers

- `BastionHostComponentResource`
- `FastAPIAuthComponentResource`
- `MarimoDashboardComponentResource`
- `CaddyServerComponentResource`

## Public request flow

```mermaid
flowchart LR
    USER[User browser]
    DNS[Route 53 A record]
    CADDY[Caddy EC2 + Elastic IP]
    AUTH[FastAPI auth EC2]
    ADMIN[webserver-admin.dagster:3000]
    GUEST[webserver-guest.dagster:3000]
    MARIMO[marimo-dashboard.dagster:2718]

    USER --> DNS
    DNS --> CADDY
    CADDY --> AUTH
    CADDY --> ADMIN
    CADDY --> GUEST
    CADDY --> MARIMO
    AUTH --> ADMIN
```

The public edge is intentionally thin:

- Caddy is the only internet-facing runtime host
- FastAPI auth stays in the private subnet
- Dagster webservers stay in ECS private networking behind Caddy
- Marimo stays in the private subnet behind Caddy and exposes only a minimal
  unauthenticated health route at `/marimo/health`
- EC2 hosts require IMDSv2 and encrypted root volumes

## Operator access flow

```mermaid
flowchart LR
    ADMINIPS[Administrator IPs]
    BASTION[Bastion host]
    CADDY[Caddy host]
    AUTH[FastAPI auth host]
    MARIMO[Marimo dashboard host]
    PG[(Postgres)]
    WEB[Dagster webserver]

    ADMINIPS -->|SSH 22| BASTION
    ADMINIPS -->|SSH 22| CADDY
    BASTION -->|SSH 22| AUTH
    BASTION -->|5432| PG
    BASTION -->|3000| WEB
    ADMINIPS -.->|SSM Session Manager| MARIMO
```

## Component summary

| Component | Placement | Key resources | Purpose |
|---|---|---|---|
| `BastionHostComponentResource` | public subnet | EC2 instance, EIP, SSH key pair, SSM params | controlled operator entry point |
| `FastAPIAuthComponentResource` | private subnet | EC2 instance, ECR-read role, digest-pinned Docker bootstrap | OIDC/session bridge for protected routes |
| `MarimoDashboardComponentResource` | private subnet | EC2 instance with encrypted 30 GiB `gp3` root volume, ECR-read and SSM role, Cloud Map service, read-only S3 policy | curated dashboard notebook service |
| `CaddyServerComponentResource` | public subnet | EC2 instance, EIP, 1 GiB EBS volume, Route 53 record | public TLS termination and reverse proxy |

## Implementation notes

- The bastion host uses the shared bastion instance profile from
  `IamRolesComponentResource` and stores its instance ID and key-pair ID in
  SSM.
- The FastAPI auth host stores Cognito values in SSM SecureString parameters,
  fetches them at boot, and passes them to the digest-pinned auth container
  without embedding secret values in EC2 user data.
- The Marimo dashboard host has no public IP and no SSH key. Operators use SSM
  Session Manager, and the instance role can read only the curated AEMO and
  IO-manager buckets.
- The Caddy host:
  - pulls the digest-pinned `dagster/caddy` image from ECR
  - serves the Astro-generated root portfolio, protected `/marimo` catalogue
    shell, and shared `/theme.css` asset before proxying application routes
  - mounts a dedicated encrypted EBS volume at `/mnt/caddy-certs`
  - persists certificate state under `/data`
  - creates a Route 53 A record for `ausenergymarketdata.com`
  - proxies to Cloud Map names for the private Dagster webservers and to the
    auth host private IP on port `8000`
  - protects the Caddy-served `/marimo` catalogue with Marimo auth, then proxies
    `/marimo/dashboard-registry.json`, notebook routes, packaged assets,
    websockets, and `/marimo/health` to `marimo-dashboard.dagster:2718`

## Related docs

- [Connectivity](connectivity.md)
- [Identity and discovery](identity-and-discovery.md)
- [Runtime](runtime.md)
- [Storage](storage.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `infrastructure/aws-pulumi/components/bastion_host.py`
  - `infrastructure/aws-pulumi/components/fastapi_auth.py`
  - `infrastructure/aws-pulumi/components/marimo.py`
  - `infrastructure/aws-pulumi/components/caddy.py`
  - `backend-services/caddy/Caddyfile`
  - `backend-services/caddy/Dockerfile`
  - `backend-services/caddy/package.json`
  - `backend-services/caddy/src/pages/index.astro`
  - `backend-services/caddy/src/pages/marimo.astro`
  - `backend-services/caddy/public/theme.css`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
