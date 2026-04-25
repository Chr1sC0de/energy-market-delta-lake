# S0 — Baseline architecture alignment

## Objective
Define exactly how the new Marimo plane fits into the existing Pulumi architecture without breaking current Dagster services.

## Scope
- Inventory current components: VPC, security groups, ECS cluster/services, Caddy, FastAPI auth, Postgres, S3, DynamoDB.
- Propose new component boundaries for Marimo-specific resources.
- Establish naming/tagging conventions for cost attribution and ownership.

## Component model (what each component does)

## Existing components we keep as-is

### 1) `VpcComponentResource` (existing)
- Owns VPC, public/private subnet baseline, and routing primitives.
- Marimo plane reuses this VPC and private subnet model.

### 2) `SecurityGroupsComponentResource` (existing)
- Owns SGs for Dagster webserver/user-code/daemon, Postgres, bastion, Caddy, FastAPI auth.
- Marimo adds a **separate SG component** to avoid coupling with current Dagster SG lifecycle.

### 3) `EcsClusterComponentResource` + Dagster ECS services (existing)
- Runs Dagster control plane and pipelines.
- No direct code/runtime changes in S0; Marimo is an adjacent analytics plane.

### 4) `FastAPIAuthComponentResource` + `CaddyServerComponentResource` (existing)
- Current auth edge and reverse-proxy path.
- In S0, these remain stable; we only define how broker/session integration will attach later.

### 5) Postgres / S3 / DynamoDB components (existing)
- Continue serving existing system responsibilities.
- S0 only defines where Marimo metadata should live (not yet provisioned).

## New components introduced by Marimo plane

### A) `MarimoBrokerComponentResource` (new)
**Purpose**: control-plane API that maps authenticated users to workspace lifecycle and routing state.

**Responsibilities**
- Validate incoming authenticated identity assertions.
- Resolve `user_id -> workspace_id` mapping.
- Trigger lifecycle actions (`start`, `stop`, `status`) via provisioner service.
- Mint short-lived workspace access tokens.

**Does not do**
- Run user code.
- Query large datasets directly.

### B) `MarimoProvisionerComponentResource` (new)
**Purpose**: orchestrate EC2 workspace lifecycle.

**Responsibilities**
- Create/start/stop/terminate per-user EC2 instances.
- Attach encrypted EBS workspace volumes.
- Register readiness and health state back to metadata store.

**Does not do**
- Handle user HTTP traffic.
- Handle auth UX.

### C) `MarimoWorkspaceComponentResource` (new)
**Purpose**: define launch template/runtime identity for user workspace instances.

**Responsibilities**
- Launch template, AMI pinning, instance profile/IAM, tags.
- Bootstrapping marimo runtime + internal SDK.
- Emit health telemetry and activity heartbeats.

### D) `MarimoWorkspaceSecurityGroupsComponentResource` (new)
**Purpose**: isolate workspace network boundaries.

**Responsibilities**
- Permit ingress only from trusted edge/broker SG(s).
- Permit explicit egress required for data access + telemetry.
- Block workspace-to-workspace lateral connectivity by default.

### E) `MarimoMetadataStoreComponentResource` (new)
**Purpose**: persistence for workspace mapping and state.

**Candidate storage options**
- DynamoDB table (`user_id` partition key, `workspace_id` sort key) for lifecycle and routing state.
- Optional Postgres schema if relational reporting is preferred.

**Stores**
- Workspace lifecycle (`provisioning`, `running`, `stopped`, `error`).
- Routing target + last health check timestamp.
- Policy tier and quota metadata.

## Interaction flow (high-level)

1. User authenticates with existing auth stack (Cognito/FastAPI auth path).
2. Edge calls broker with authenticated identity context.
3. Broker checks metadata store for user workspace state.
4. If needed, broker asks provisioner to start/provision workspace.
5. Provisioner updates workspace state until healthy.
6. Broker returns signed session + route target.
7. Edge routes user traffic only to assigned workspace.

## Interfaces defined in S0 (for S1/S2 to implement)

### Broker API surface (contract placeholder)
- `POST /session/start`
- `GET /session/status`
- `POST /session/stop`

### Provisioner API surface (internal)
- `POST /workspaces/{workspace_id}/start`
- `POST /workspaces/{workspace_id}/stop`
- `POST /workspaces/{workspace_id}/provision`
- `GET /workspaces/{workspace_id}/health`

### Metadata schema (minimum)
- `workspace_id`
- `user_id`
- `tenant_id`
- `state`
- `instance_id`
- `private_ip`
- `last_heartbeat_at`
- `policy_tier`

## Pulumi implementation boundaries

## New module layout (proposed)
- `infrastructure/aws-pulumi/components/marimo_broker.py`
- `infrastructure/aws-pulumi/components/marimo_provisioner.py`
- `infrastructure/aws-pulumi/components/marimo_workspace.py`
- `infrastructure/aws-pulumi/components/marimo_workspace_security_groups.py`
- `infrastructure/aws-pulumi/components/marimo_metadata_store.py`

## `__main__.py` placement (proposed order)
After existing VPC/security/auth foundations are created:
1. `marimo_metadata_store`
2. `marimo_workspace_security_groups`
3. `marimo_broker`
4. `marimo_provisioner`
5. `marimo_workspace` (template/shared defs, not one resource per user in Pulumi)

> Note: per-user instance creation should be runtime-driven by broker/provisioner, not statically declared as one Pulumi resource per user.

## Naming/tagging conventions

### Resource naming
- Prefix: `${ENVIRONMENT}-energy-market-marimo-*`
- Examples:
  - `${NAME}-marimo-broker`
  - `${NAME}-marimo-provisioner`
  - `${NAME}-marimo-workspace-lt`

### Required tags
- `service=marimo`
- `component=<broker|provisioner|workspace|metadata>`
- `environment=<dev|staging|prod>`
- `owner=<team>`
- `tenant=<tenant_id>` (runtime resources)
- `user_id=<user_id>` (workspace EC2/EBS runtime resources)
- `cost_center=<finops key>`

## Failure domains and ownership

- **Broker down**: no new session starts, but running workspaces can continue serving existing sessions.
- **Provisioner down**: no lifecycle transitions; broker returns retryable status.
- **Metadata store degraded**: routing/state uncertainty; broker must fail closed.
- **Workspace unhealthy**: broker/provisioner can recycle or replace instance.

Ownership split:
- Platform team: broker, provisioner, metadata store, Pulumi modules.
- Data platform: SDK/data policy definitions.
- Security: IAM baseline and auth/token standards.

## Deliverables
- ADR markdown under `specs/` describing component boundaries.
- Pulumi module map diagram (existing vs marimo-new).
- Sequence diagram from auth -> broker -> provisioner -> workspace route.
- Tagging and naming policy documented.

## Acceptance criteria
- Integration points are documented and approved.
- No changes to existing Dagster service behavior in this phase.
- A clear handoff contract exists for S1 (broker/session) and S2 (lifecycle automation).
