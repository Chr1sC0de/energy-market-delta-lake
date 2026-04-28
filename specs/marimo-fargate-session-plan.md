# Marimo Fargate Session Launcher Plan

## Goal

Add a user-facing Marimo launch flow where an authenticated Cognito user clicks a Caddy-exposed Marimo link, sees a wait screen while an AWS Fargate task starts, and is then routed into a per-user Marimo coding container with persistent storage mounted on every launch.

This is a planning document only. It does not yet change runtime behavior.

## Current repo context

The repository already has the pieces this feature should integrate with:

- `backend-services/caddy/` for the public reverse proxy.
- `backend-services/authentication/` for the FastAPI authentication/session service.
- `backend-services/marimo/` for the local notebook service.
- `infrastructure/aws-pulumi/` as the canonical AWS deployment source.
- ECS, Cloud Map, IAM, ECR, VPC, and Caddy are already part of the deployed architecture.
- Cognito is available and should be the source of truth for user identity.

The proposed implementation should extend those existing pieces rather than creating a separate deployment system.

## Target user experience

1. User opens the Marimo link exposed through Caddy, for example `/marimo`.
2. The request is authenticated through Cognito and the existing auth/session service.
3. The backend creates or reuses a Marimo session for the Cognito user.
4. If no task is ready, the user sees a wait page: `Starting your Marimo workspace...`.
5. The backend starts an ECS Fargate task for the user's Marimo workspace.
6. The task mounts the user's persistent workspace volume.
7. The backend waits until Marimo is reachable and healthy.
8. The wait page redirects the user to the ready Marimo session URL.
9. While the user is active, the task remains running.
10. After logout, manual stop, or idle timeout, the backend stops the task.
11. On the next launch, the same user volume is mounted again.

## Proposed architecture

```mermaid
flowchart LR
  U[User browser] --> C[Caddy]
  C --> A[Authentication service]
  A --> CG[Cognito]
  A --> S[Marimo session manager]
  S --> ECS[ECS RunTask API]
  ECS --> T[Fargate Marimo task]
  T --> EFS[(EFS user workspace)]
  C --> S
  S --> T
```

Caddy should stay responsible for public HTTPS routing. It should not directly orchestrate Fargate. The orchestration should live in the authenticated backend/session manager.

Cognito should be the source of truth for identity. The session manager should use the verified Cognito identity to decide which Marimo session to create, reuse, route, or stop.

## Identity and routing model

Use Cognito as the identity layer and keep public routing opaque.

Recommended identity mapping:

| Concept | Value |
|---|---|
| Durable user ID | Cognito `sub` claim |
| Display/audit email | Cognito email claim, if present |
| Public session route | Random opaque `session_id` |
| Workspace identity | Derived from Cognito `sub`, not from user input |
| Task context | Injected by trusted session manager only |

Recommended route shape:

```text
/marimo
/marimo/sessions/{opaque_session_id}
/marimo/sessions/{opaque_session_id}/wait
/api/marimo/sessions/{opaque_session_id}
```

Avoid routes such as:

```text
/marimo/{email}
/marimo/{cognito_sub}
/marimo/{user_supplied_name}
```

Every request for a session-scoped route should validate that the current Cognito user owns the target session before proxying to Marimo.

## Main components

### 1. Session manager

Add Marimo session lifecycle endpoints to the existing authentication/FastAPI service, or create a sibling backend service if separation is preferred.

Initial endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /marimo` | Cognito-authenticated entrypoint. Creates/reuses a session and returns the wait page or redirects if already ready. |
| `GET /marimo/sessions/{session_id}/wait` | Wait screen. Polls status and redirects when ready. |
| `GET /api/marimo/sessions/{session_id}` | Returns `starting`, `ready`, `failed`, or `stopped`. |
| `POST /api/marimo/sessions/{session_id}/stop` | Stops a user's running task. |
| `ANY /marimo/sessions/{session_id}/{path:path}` | Optional backend proxy to the user's Marimo task. |

The session manager should own:

- Cognito token/session validation or integration with the existing auth service;
- user-to-session mapping using Cognito `sub`;
- per-route authorization for session ownership;
- ECS task launch;
- task readiness polling;
- task private IP / service discovery lookup;
- idle timeout tracking;
- task cleanup;
- failure state and error messages.

### 2. Cognito integration

The existing auth/session service should validate Cognito before allowing Marimo session creation or routing.

Validation requirements:

- validate token issuer;
- validate audience/client ID;
- validate expiry;
- validate signature against the Cognito user pool JWKS;
- extract the Cognito `sub` claim as the stable user ID;
- treat email as mutable display metadata, not as the primary key.

Implementation options:

#### Option A: Existing auth service validates Cognito, preferred

Caddy routes `/marimo` and related paths to the existing auth/session service. That service validates the Cognito session/JWT and passes the verified identity into the session manager code path.

Pros:

- aligned with the current repo structure;
- keeps identity and session lifecycle in one trusted backend;
- easiest place to enforce ownership checks before proxying.

#### Option B: Caddy forward-auth style gate

Caddy asks the auth service to validate the request before routing protected paths. The auth service can return trusted identity headers to internal upstreams.

Pros:

- keeps Caddy as the shared edge gate;
- can protect multiple services consistently.

Cons:

- only internal services should trust identity headers;
- the session manager must still re-check ownership and avoid trusting browser-provided headers.

#### Option C: ALB + Cognito authentication

An AWS Application Load Balancer can perform Cognito authentication before traffic reaches services.

Pros:

- AWS-managed authentication at the load balancer layer.

Cons:

- larger architectural change because the repo currently treats Caddy as the public edge;
- does not remove the need for a session manager or ownership checks.

Recommendation: use Option A for the first implementation.

### 3. Session state

Use a durable store rather than only process memory. Candidate stores:

- DynamoDB table, preferred for deployed AWS;
- PostgreSQL if reusing the existing database is simpler;
- in-memory only for local proof-of-concept.

Suggested fields:

| Field | Notes |
|---|---|
| `session_id` | Random opaque ID. Do not expose raw user IDs as routing IDs. |
| `user_id` | Cognito `sub` claim. |
| `user_email` | Optional audit/debug field from Cognito. Do not use as the primary key. |
| `status` | `starting`, `ready`, `failed`, `stopping`, `stopped`. |
| `ecs_task_arn` | Fargate task ARN. |
| `task_private_ip` | Set after ENI attachment is available. |
| `task_port` | Marimo port, likely `2718`. |
| `workspace_path` | User EFS path or access point ID derived from Cognito `sub`. |
| `created_at` | Session creation time. |
| `ready_at` | When Marimo passed readiness checks. |
| `last_seen_at` | Updated by proxied requests or polling. |
| `stopped_at` | Set when cleanup completes. |
| `failure_reason` | User-visible summary for failed starts. |

Add a uniqueness guard so one Cognito user cannot accidentally create duplicate active sessions unless multi-session workspaces are intentionally supported.

### 4. Fargate task definition

Create a dedicated Marimo trainer task definition in Pulumi.

It should include:

- Marimo container image from ECR.
- Container command similar to `marimo edit --host 0.0.0.0 --port 2718 /workspace`.
- Port mapping for Marimo.
- CloudWatch logs.
- Task role with only the permissions needed by the trainer.
- Execution role for pulling ECR images and writing logs.
- Environment variables populated at launch by the trusted session manager:
  - `USER_ID` or `COGNITO_SUB`
  - `USER_EMAIL`
  - `SESSION_ID`
  - `WORKSPACE_DIR=/workspace`
  - any project-specific config needed by the trainer.

The browser must not be able to choose or override these values.

### 5. Persistent workspace volume

Use EFS for persistent user workspaces.

Preferred production model:

- one EFS filesystem for Marimo workspaces;
- one EFS access point per Cognito user, or per-user directories with enforced POSIX ownership;
- Fargate task mounts the user's workspace at `/workspace`;
- container runs as a non-root user matching the EFS access point ownership.

Example logical layout:

```text
/efs/marimo-workspaces/{cognito_sub}/
```

Mounted inside the container as:

```text
/workspace
```

If EFS access points are used, store the access point ID in session/user metadata and ensure the task can only mount the correct workspace.

### 6. Readiness and wait screen

The wait page should poll the session manager instead of directly polling the task.

Readiness criteria:

1. Cognito session is still valid.
2. Current Cognito user owns the session being polled.
3. ECS task status is `RUNNING`.
4. Task ENI/private IP has been discovered.
5. Marimo TCP port is reachable from the session manager or proxy layer.
6. Optional HTTP readiness endpoint returns success.

Status API examples:

```json
{ "status": "starting", "message": "Starting your workspace" }
```

```json
{ "status": "ready", "url": "/marimo/sessions/abc123/" }
```

```json
{ "status": "failed", "message": "Workspace failed to start. Please try again." }
```

### 7. Routing strategy

There are two viable approaches.

#### Option A: Backend proxy, preferred for MVP

Caddy routes all Marimo session paths to the session manager. The session manager validates Cognito ownership and proxies HTTP and WebSocket traffic to the correct Fargate task.

Pros:

- Caddy config remains mostly static.
- Session routing logic stays in application code.
- Easier to show wait/failure states.
- Easier to guarantee Cognito ownership checks before proxying.

Cons:

- The backend must correctly proxy WebSockets.
- The backend becomes part of the data path.

#### Option B: Dynamic Caddy upstreams

The session manager updates Caddy's dynamic config or service discovery once a task is ready.

Pros:

- Caddy handles the proxy data path.
- Cleaner separation once stable.

Cons:

- More moving parts.
- Stale route cleanup is harder.
- Need careful admin API security.
- Authorization must still be enforced before routing to a task.

Recommendation: start with Option A, then evaluate Option B if proxy throughput or complexity becomes an issue.

### 8. Idle shutdown

The session manager should stop tasks when they are no longer in use.

Initial policy:

- update `last_seen_at` on wait-page polling and proxied Marimo traffic;
- stop sessions idle for 30 minutes;
- stop sessions immediately when the user clicks a Stop button;
- periodically reconcile session records against ECS to clean up orphaned tasks.

A scheduled cleanup loop can run in the session manager or as a small ECS scheduled task.

### 9. Security requirements

- Require Cognito authentication before creating or accessing a session.
- Validate Cognito issuer, audience/client ID, expiry, and signature.
- Use Cognito `sub` as the durable user ID.
- Treat email as display metadata only.
- Authorize every session route: users can only access their own sessions.
- Use random opaque session IDs.
- Do not expose Cognito `sub`, email, or task private IPs in public routes.
- Do not trust browser-provided identity headers or workspace paths.
- Inject identity into Fargate tasks only from the trusted session manager.
- Keep Marimo tasks in private subnets.
- Restrict security groups so only the proxy/session manager can reach Marimo task ports.
- Run containers as non-root where possible.
- Scope IAM task roles narrowly.
- Avoid passing secrets directly as plain environment variables unless necessary.
- Prefer Secrets Manager or SSM Parameter Store for sensitive values.
- Ensure WebSocket routes go through the same auth and session checks.
- Prefer EFS access points or strict per-user POSIX ownership to prevent cross-user data access.

### 10. Pulumi infrastructure work

Add infrastructure for:

- Marimo trainer ECR repository or image reference.
- ECS task definition for Marimo trainer sessions.
- IAM task execution role and task role.
- CloudWatch log group.
- EFS filesystem, access points, mount targets, and security groups.
- Security group rules from Caddy/session manager to Marimo tasks.
- Optional DynamoDB session table keyed by opaque session ID and indexed by Cognito `sub`.
- Required Cognito, ECS, EFS, and session-router environment variables for the auth/session service.

### 11. Local development plan

For local compose:

- keep the existing local Marimo service;
- add a fake/local session manager mode that starts or proxies to the local Marimo container instead of ECS;
- use a local fake Cognito identity or existing local auth test identity;
- use a local bind mount as the workspace volume;
- keep route shape aligned with production, e.g. `/marimo/sessions/{session_id}`.

This allows the wait page, Cognito-derived identity mapping, ownership checks, and routing behavior to be tested without AWS.

## Suggested implementation phases

### Phase 1: Planning and interfaces

- Land this plan.
- Decide whether the session manager lives inside `backend-services/authentication/` or as a new service.
- Confirm desired route shape.
- Confirm Cognito user pool/client configuration needed by the backend.
- Confirm whether session state should use DynamoDB or PostgreSQL.

### Phase 2: Local proof of concept

- Add wait page.
- Add session status API.
- Add local session state.
- Add Cognito/local-auth identity abstraction.
- Proxy to the existing local Marimo service.
- Validate WebSocket behavior through Caddy.
- Validate session ownership checks.

### Phase 3: AWS task launch

- Add ECS RunTask integration.
- Add task status polling.
- Discover task private IP.
- Pass trusted Cognito-derived context into the task.
- Add failure handling and retry behavior.
- Add manual stop endpoint.

### Phase 4: Persistent workspaces

- Add EFS infrastructure in Pulumi.
- Map Cognito `sub` to per-user workspace or access point.
- Mount per-user workspace into Fargate tasks.
- Validate file persistence across task restarts.
- Lock down filesystem permissions.

### Phase 5: Production hardening

- Add durable session table.
- Add idle timeout cleanup.
- Add orphan ECS task reconciliation.
- Add metrics/logging.
- Add rate limits and per-user task quotas.
- Add user-facing failure states.
- Add integration tests for route authorization.

## Acceptance criteria

MVP acceptance:

- An authenticated Cognito user can click `/marimo`.
- The user sees a wait screen while no Marimo task is ready.
- A Marimo Fargate task starts for that Cognito user.
- The user is redirected to Marimo after readiness succeeds.
- The user can create or edit a file in `/workspace`.
- Stopping and relaunching the task preserves files in `/workspace`.
- Another Cognito user cannot access the first user's session URL.
- The task stops after the configured idle timeout.

Production acceptance:

- Sessions survive session-manager restarts.
- Orphaned ECS tasks are reconciled and stopped.
- EFS permissions prevent cross-user data access.
- Caddy/WebSocket routing is reliable for Marimo usage.
- CloudWatch logs make failed starts diagnosable.
- Costs are bounded with per-user/session quotas.
- Cognito token validation and session ownership checks are covered by tests.

## Open questions

- Should the session manager be part of the existing authentication service or a separate service?
- Which Cognito user pool and app client should the Marimo router trust?
- Should the stable user ID always be Cognito `sub`, or is there an existing app-specific user ID mapped from Cognito?
- Should users get one active Marimo session or multiple named workspaces?
- What should the idle timeout be?
- Should each user get an EFS access point, or should access be enforced by directory ownership?
- Is the Marimo trainer image the existing `backend-services/marimo` image or a new purpose-built image?
- Does the trainer need access to project AWS data buckets, and if so, should access be scoped per user?

## Risks

| Risk | Mitigation |
|---|---|
| Fargate cold starts feel slow | Wait screen with progress states; optionally warm pool later. |
| Duplicate tasks for same user | Use idempotent session creation and locking keyed by Cognito `sub`. |
| Task starts but Marimo is not usable | Require app-level readiness checks before redirecting. |
| WebSockets fail through proxy | Test Marimo editing through Caddy in local compose before AWS rollout. |
| EFS permissions leak user data | Prefer EFS access points and non-root containers. |
| Identity headers are spoofed | Validate Cognito in the trusted backend and do not trust browser-provided headers. |
| Idle cleanup misses tasks | Add reconciliation against ECS `ListTasks`/`DescribeTasks`. |
| Costs grow unexpectedly | Add quotas, idle timeout, max session duration, and alarms. |

## Non-goals for the first PR

- Implementing the full Fargate launcher.
- Changing the deployed Caddy config.
- Changing the Marimo image.
- Adding EFS infrastructure.
- Adding production IAM policies.

Those should follow after the route shape, Cognito integration model, and session-manager ownership are agreed.
