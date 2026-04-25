# S1 — Identity and session broker

## Objective
Issue short-lived, user-bound sessions that route each authenticated user to their own Marimo workspace.

## Scope
- Broker API design
- Token/session model
- Edge integration path from current auth stack

## Proposed implementation
1. Build a broker service (FastAPI) in private subnet/ECS service.
2. Add endpoints:
   - `POST /session/start`
   - `GET /session/status`
   - `POST /session/stop`
3. On successful Cognito-authenticated identity, map `sub -> workspace_id`.
4. Mint short-lived JWT (5–15 min) with claims: `sub`, `tenant`, `workspace_id`, `roles`, `exp`, `jti`.
5. Caddy/ALB forwards only requests with valid broker-issued token to workspace.

## Data model
- `users` table: user metadata and tenant mapping.
- `workspaces` table: workspace lifecycle + instance metadata.
- `sessions` table: current/expired session records for audit.

## Pulumi changes
- New broker compute resource (start as EC2 or ECS Fargate).
- Secret/config wiring for token-signing key and issuer metadata.

## Deliverables
- OpenAPI spec for broker.
- Sequence diagram for login-to-workspace handoff.
- Token validation middleware contract for edge.

## Acceptance criteria
- User cannot access another user's workspace by URL manipulation.
- Expired/revoked token access denied at edge.
