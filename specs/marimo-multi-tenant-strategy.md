# Marimo + Dagster multi-tenant analytics strategy (per-user EC2)

## Table of contents
- [1) Context and goal](#1-context-and-goal)
- [2) Current Pulumi baseline (what already exists)](#2-current-pulumi-baseline-what-already-exists)
- [3) Target architecture for per-user marimo services](#3-target-architecture-for-per-user-marimo-services)
- [4) Spec backlog broken into subtasks](#4-spec-backlog-broken-into-subtasks)
- [5) Detailed spec cards (work one at a time)](#5-detailed-spec-cards-work-one-at-a-time)
- [6) Suggested implementation order](#6-suggested-implementation-order)
- [7) Risks and open decisions](#7-risks-and-open-decisions)

## 1) Context and goal

You want a user-by-user analytics environment where each authenticated user can:

- sign in and launch their own marimo service
- query curated data from the Dagster ecosystem
- use Polars + plotting libraries interactively
- operate in isolated compute/network boundaries

This document expands the initial strategy into an actionable specification backlog so we can execute one spec at a time.

## 2) Current Pulumi baseline (what already exists)

From the current `infrastructure/aws-pulumi` stack:

1. **Network foundation exists**
   - Single VPC, public + private subnets, custom NAT instance routing.
2. **Security groups exist for current services**
   - Bastion, Dagster webserver/user-code/daemon, Postgres, Caddy, FastAPI auth.
3. **Existing auth edge exists**
   - FastAPI auth EC2 service (private subnet), Caddy EC2 reverse proxy (public subnet), Cognito-related env config.
4. **Dagster runtime exists on ECS Fargate**
   - User code, daemon, webserver admin/guest with service discovery.
5. **Core data infra exists**
   - S3 buckets + DynamoDB lock table + Postgres.

### Implication for this project

We should **extend** this architecture (not replace it):

- keep Dagster on ECS and treat it as orchestration/control plane for data production
- add a new per-user marimo service plane that reads governed outputs
- reuse existing auth/caddy patterns where useful, but introduce explicit per-user session brokering

## 3) Target architecture for per-user marimo services

### Control plane (shared)

- **Identity provider**: existing Cognito integration remains source of user identity.
- **Session broker API** (new): maps authenticated user → assigned marimo instance and issues short-lived access token.
- **Provisioner worker** (new): start/stop/create/terminate per-user EC2 instances and persistent volumes.
- **State store** (new): user→instance mapping, lifecycle state, policy tier, last-activity timestamps.

### Data plane (per user)

- Dedicated EC2 instance per user (or per active user cohort).
- marimo service bound to localhost behind local reverse proxy.
- Python runtime includes `polars`, plotting libs, and internal data access SDK.
- Instance profile IAM with tenant-scoped least privilege.
- Optional per-user persistent EBS for workspace state.

### Data access pattern

- marimo code consumes data through an internal SDK/API surface.
- SDK uses short-lived credentials and enforces tenant/user context.
- Fine-grained data policy must be enforced at query/data platform layer (not notebook-only).

## 4) Spec backlog broken into subtasks

> Status key: `todo`, `in-progress`, `blocked`, `done`.

| Spec ID | Subtask | Outcome | Dependencies | Status |
|---|---|---|---|---|
| S0 | Baseline architecture alignment | Confirm how new marimo plane integrates with existing Pulumi modules and routing | none | todo |
| S1 | Identity + session broker | Authenticated user gets signed marimo session and deterministic routing | S0 | todo |
| S2 | Per-user compute lifecycle | Provision/start/stop/terminate per-user EC2 reliably | S0, S1 | todo |
| S3 | Marimo runtime image & bootstrap | Standardized marimo + polars runtime with hardening and observability | S2 | todo |
| S4 | Networking and ingress model | Private compute + controlled ingress from authenticated edge only | S0, S1, S2 | todo |
| S5 | Data access SDK + IAM policy model | Controlled access to Dagster outputs and data stores with tenant scope | S1, S3 | todo |
| S6 | Workspace persistence and backup | Durable per-user notebooks/artifacts with restore process | S2, S3 | todo |
| S7 | Idle shutdown, cost controls, quotas | Predictable spend and auto-lifecycle management | S2, S6 | todo |
| S8 | Observability, audit, SLOs | End-to-end traceability and operational readiness | S1-S7 | todo |
| S9 | Security hardening + threat model | Baseline controls documented and validated | S1-S8 | todo |

## 5) Detailed spec cards (work one at a time)

## S0 — Baseline architecture alignment

**Goal**
Define where to add new Pulumi components (`marimo_broker`, `marimo_instances`, `marimo_security_groups`, etc.) without destabilizing existing Dagster components.

**Deliverables**
- Architecture decision record (ADR) for integration points.
- Pulumi module map showing existing vs new component ownership.
- Naming/tagging conventions for marimo resources.

**Acceptance criteria**
- Clear boundary documented: Dagster orchestration vs user analytics plane.
- No required breaking changes to existing ECS Dagster services.

## S1 — Identity + session broker

**Goal**
After Cognito login, user receives short-lived broker token and lands on their own marimo service.

**Deliverables**
- Broker API contract (`/session/start`, `/session/status`, `/session/stop`).
- Token schema (claims: `sub`, `tenant`, `instance_id`, `exp`).
- AuthN/AuthZ checks between edge proxy, broker, and marimo instance.

**Acceptance criteria**
- User cannot access another user instance even with URL guessing.
- Session token expires quickly and is rotated/reissued safely.

## S2 — Per-user compute lifecycle

**Goal**
Automate creation and lifecycle of one EC2 workspace per user.

**Deliverables**
- Provisioning workflow (create instance + attach volume + register route).
- Resume workflow (start/hibernate wake + health check gate).
- Termination workflow (snapshot/archive + cleanup).

**Acceptance criteria**
- p95 warm resume under agreed threshold.
- Deterministic idempotent provisioning for repeated requests.

## S3 — Marimo runtime image & bootstrap

**Goal**
Create repeatable runtime with marimo, polars, plotting libs, and security defaults.

**Deliverables**
- Golden AMI or bootstrapped instance profile for runtime install.
- Standard library bundle (`polars`, `pyarrow`, plotting package choices).
- Startup service definition (systemd/container) with health endpoint.

**Acceptance criteria**
- Same runtime versions across users in same release.
- No unauthenticated public marimo endpoint exposure.

## S4 — Networking and ingress model

**Goal**
Ensure user instances are private and only reachable through authenticated routing.

**Deliverables**
- New SG rules for broker/edge-to-marimo traffic.
- Private subnet placement and route strategy.
- DNS/routing strategy for user-specific endpoints.

**Acceptance criteria**
- No direct internet ingress to marimo instances.
- All ingress requests are identity-bound and auditable.

## S5 — Data access SDK + IAM policy model

**Goal**
Provide a safe API in marimo notebooks for querying approved datasets.

**Deliverables**
- Internal SDK package and allowed API surface.
- IAM policy templates scoped by tenant/user prefix.
- Data policy mapping (row/column/asset-level where applicable).

**Acceptance criteria**
- Access denied for out-of-scope datasets.
- SDK emits structured audit events on reads.

## S6 — Workspace persistence and backup

**Goal**
Persist notebooks/artifacts while keeping compute disposable.

**Deliverables**
- User workspace filesystem layout and retention policy.
- Backup pipeline (EBS snapshots and/or S3 sync).
- Restore workflow for replacement instance.

**Acceptance criteria**
- User data survives stop/start and controlled replacement.
- Recovery runbook validated in non-prod.

## S7 — Idle shutdown, cost controls, quotas

**Goal**
Keep per-user EC2 model financially manageable.

**Deliverables**
- Idle detection and stop policy.
- Per-user size tier and budget guardrails.
- Cost attribution tags and dashboard dimensions.

**Acceptance criteria**
- Instances auto-stop after policy idle threshold.
- Monthly cost report available by user/team.

## S8 — Observability, audit, SLOs

**Goal**
Make service operable with clear reliability targets.

**Deliverables**
- Metrics: login-to-ready, broker latency, start failure rate, marimo health.
- Logs: auth decisions, provisioning actions, SDK data reads.
- Alerting + runbooks for top failure modes.

**Acceptance criteria**
- SLO dashboard exists and alerts are actionable.
- Incident triage can reconstruct user session path.

## S9 — Security hardening + threat model

**Goal**
Formalize baseline controls and validate them before broader rollout.

**Deliverables**
- Threat model (identity spoofing, lateral access, data exfiltration scenarios).
- Hardening checklist (IMDSv2, EBS encryption, SSM-only admin, no static keys).
- Security test plan (auth bypass, tenant breakout, secret leakage).

**Acceptance criteria**
- Critical/high findings resolved or risk-accepted explicitly.
- Security sign-off before production onboarding.

## 6) Suggested implementation order

Recommended order for iterative delivery:

1. **S0** architecture alignment
2. **S1** identity/session broker contract
3. **S2** lifecycle automation
4. **S3** runtime standardization
5. **S4** network controls
6. **S5** data access SDK
7. **S6** persistence/backup
8. **S7** cost controls
9. **S8** observability
10. **S9** security hardening sign-off

This sequence gets a secure MVP quickly, then layers governance and operational maturity.

## 7) Risks and open decisions

Open decisions to resolve early:

- Should user instances be long-lived (persistent) or mostly ephemeral with fast restore?
- Should routing remain Caddy-centric or move to ALB + OIDC for broker integration?
- What is the minimum approved plotting stack (e.g., Plotly/Altair/Matplotlib) for marimo?
- Is one instance per user required always, or can low-risk users share pooled compute tiers?

Known risks:

- Per-user EC2 can become expensive without strict idle controls.
- Identity/routing misconfiguration is a high-impact security risk.
- Data policy gaps in backend systems cannot be fixed purely in notebook code.
