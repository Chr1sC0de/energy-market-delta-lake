# S9 — Security hardening and threat model

## Objective
Finalize a production-ready baseline with explicit threat mitigations and verification.

## Scope
- Threat model
- Hardening checklist
- Security validation plan

## Proposed implementation
1. Threat model workshops covering:
   - token theft/replay
   - tenant breakout
   - workspace-to-workspace lateral access
   - data exfiltration patterns
2. Hardening baseline:
   - IMDSv2 only
   - encrypted volumes and snapshots
   - SSM-only administration (no public SSH)
   - no static long-lived cloud keys
   - restricted egress where feasible
3. Validation:
   - auth bypass tests
   - policy enforcement tests
   - secret handling checks

## Pulumi changes
- Enforce secure defaults in launch templates, IAM, and SGs.
- Add compliance-oriented tags and audit hooks.

## Deliverables
- Threat model document.
- Security checklist with ownership.
- Go-live security sign-off template.

## Acceptance criteria
- Critical/high findings resolved or explicitly risk-accepted.
- Security review completed before production rollout.
