# S0 — Baseline architecture alignment

## Objective
Define exactly how the new Marimo plane fits into the existing Pulumi architecture without breaking current Dagster services.

## Scope
- Inventory current components: VPC, security groups, ECS cluster/services, Caddy, FastAPI auth, Postgres, S3, DynamoDB.
- Propose new component boundaries for Marimo-specific resources.
- Establish naming/tagging conventions for cost attribution and ownership.

## Proposed implementation
1. Create a `marimo/` component namespace in Pulumi for:
   - `MarimoBrokerComponentResource`
   - `MarimoWorkspaceComponentResource`
   - `MarimoWorkspaceSecurityGroupsComponentResource`
2. Keep existing Dagster ECS services unchanged; expose curated data through a dedicated SDK/API path.
3. Add a resource dependency graph diagram and ADR documenting why Marimo remains a separate plane.

## Pulumi changes
- Add placeholder component files and exports only (no runtime deployment in S0).
- Add stack config keys for Marimo naming and default region assumptions.

## Deliverables
- ADR markdown under `specs/`.
- Pulumi module map diagram.
- Standard tag schema: `owner`, `user_id`, `tenant`, `service`, `environment`, `cost_center`.

## Acceptance criteria
- Integration points are documented and approved.
- No changes to existing Dagster service behavior.
