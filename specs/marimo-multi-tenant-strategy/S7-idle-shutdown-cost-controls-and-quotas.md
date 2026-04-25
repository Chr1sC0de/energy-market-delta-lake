# S7 — Idle shutdown, cost controls, and quotas

## Objective
Control per-user EC2 spend with automated lifecycle rules and clear quota policies.

## Scope
- Idle detection
- Instance sizing tiers
- Cost visibility and controls

## Proposed implementation
1. Track activity heartbeat from broker/workspace.
2. Apply policy thresholds:
   - stop after N idle minutes
   - hibernate where supported
3. Define user tiers (small/medium/large) and approval flow for upgrades.
4. Apply mandatory cost tags and publish daily cost report by user/team.
5. Add safeguards (max concurrent instances, budget alarms).

## Pulumi changes
- Budget/alarm resources.
- Tag policy enforcement and optional SCP/guardrail integration docs.

## Deliverables
- Idle policy matrix by user tier.
- FinOps dashboard spec.
- Escalation workflow for quota exceptions.

## Acceptance criteria
- Idle instances stop automatically and reliably.
- Cost can be sliced by user and tenant.
