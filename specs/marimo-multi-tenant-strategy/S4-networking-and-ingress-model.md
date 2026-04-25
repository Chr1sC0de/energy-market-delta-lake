# S4 — Networking and ingress model

## Objective
Enforce private-only workspace networking and authenticated ingress.

## Scope
- Security group model
- Routing design
- Private subnet + egress model

## Proposed implementation
1. Place workspace instances in private subnets only.
2. Create dedicated SGs:
   - `marimo-workspace-sg` (ingress only from edge/broker)
   - `marimo-broker-sg`
3. Restrict inbound ports to one app port from trusted SG only.
4. Route strategy:
   - Preferred: ALB + OIDC/JWT auth + broker-aware routing
   - Transitional: Caddy validates broker token and forwards to workspace private IP
5. Add VPC endpoints where possible to reduce open egress dependencies.

## Pulumi changes
- Add SG resources and SG-to-SG rules.
- Add target-group/routing resources if ALB path selected.

## Deliverables
- Network diagram with trust boundaries.
- Ingress/egress policy table.
- Threat checks for lateral movement.

## Acceptance criteria
- No direct public ingress path to workspace instances.
- All workspace requests are identity-scoped and logged.
