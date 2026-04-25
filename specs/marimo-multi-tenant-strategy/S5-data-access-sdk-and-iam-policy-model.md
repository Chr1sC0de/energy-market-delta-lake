# S5 — Data access SDK and IAM policy model

## Objective
Provide a safe interface for Marimo notebooks to access approved data with tenant-scoped permissions.

## Scope
- SDK API design
- IAM scoping
- Data policy mapping

## Proposed implementation
1. Create internal Python SDK with typed methods:
   - `get_asset(name, partition=...)`
   - `query_dataset(dataset_id, filters=...)`
2. SDK injects user/tenant context from broker token claims.
3. Map workspace role -> IAM policy templates:
   - S3 prefix constraints
   - Lake Formation/Snowflake/Databricks role constraints
4. Emit structured audit events for every read/query action.

## Pulumi changes
- Add IAM policy documents and instance-profile attachments per workspace tier.
- Add config references for data platform role mappings.

## Deliverables
- SDK package skeleton + API contract.
- IAM policy library.
- Audit event schema.

## Acceptance criteria
- Out-of-scope dataset requests are denied.
- Data access events are attributable to individual users.
