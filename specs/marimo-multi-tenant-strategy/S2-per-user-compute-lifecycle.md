# S2 — Per-user compute lifecycle

## Objective
Automate creation, start, stop, and termination of one Marimo workspace instance per user.

## Scope
- Provisioning orchestration
- Health checks
- Idempotency and retry behavior

## Proposed implementation
1. Provisioning path:
   - Create EC2 from hardened AMI
   - Attach encrypted EBS volume
   - Attach workspace IAM instance profile
   - Register workspace state in DB
2. Start/resume path:
   - Start stopped instance
   - Poll SSM or health endpoint until ready
3. Stop/hibernate path:
   - Idle timeout trigger from broker activity
   - Persist state and stop safely
4. Termination path:
   - Snapshot/backup volume
   - Delete instance, detach/cleanup networking

## Pulumi + runtime changes
- Pulumi defines launch template, IAM profile, SGs, subnet placement.
- Runtime worker executes lifecycle via AWS SDK with idempotency keys.

## Deliverables
- State machine diagram.
- Failure policy matrix (timeouts, retries, dead-letter handling).
- Runbook for orphaned resources.

## Acceptance criteria
- Repeated start/provision requests are safe and deterministic.
- p95 warm resume and cold provision metrics published.
