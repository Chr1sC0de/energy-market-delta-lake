# S6 — Workspace persistence and backup

## Objective
Keep user work durable while treating compute as disposable.

## Scope
- Workspace filesystem conventions
- Backup/restore workflows
- Retention policies

## Proposed implementation
1. Standard layout:
   - `/workspace/<user_id>/apps`
   - `/workspace/<user_id>/data`
   - `/workspace/<user_id>/.cache`
2. Persist via encrypted EBS volume attached to workspace.
3. Scheduled snapshots and/or incremental sync to S3.
4. Restore flow creates replacement instance and reattaches/restores volume snapshot.

## Pulumi changes
- Define EBS encryption defaults and tagging.
- Define backup scheduling resources (or document external scheduler integration).

## Deliverables
- Backup policy document (RPO/RTO targets).
- Restore runbook with step-by-step commands.
- Data retention and deletion policy.

## Acceptance criteria
- User notebooks survive stop/start and instance replacement.
- Restore drill succeeds in non-prod within target RTO.
