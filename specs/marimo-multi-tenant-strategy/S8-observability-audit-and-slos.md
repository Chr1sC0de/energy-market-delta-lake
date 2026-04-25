# S8 — Observability, audit, and SLOs

## Objective
Make the platform operable with actionable telemetry and reliable incident triage.

## Scope
- Metrics, logs, traces
- SLO definitions
- Alerting and runbooks

## Proposed implementation
1. Metrics:
   - login-to-ready latency
   - broker API latency/error rate
   - provision success/failure rate
   - workspace health and utilization
2. Logs:
   - auth decisions
   - provisioning actions
   - SDK read/query events
3. Tracing:
   - correlate request from login -> broker -> workspace -> data access
4. Alerts for SLO burn and critical failures.

## Pulumi changes
- CloudWatch log groups, metric filters, alarms, dashboards.
- Optional integration with external observability platforms.

## Deliverables
- SLO definitions and alert thresholds.
- Dashboard layouts.
- Incident runbooks (top 5 failure modes).

## Acceptance criteria
- On-call can identify user-impacting failure within minutes.
- Session-level audit trail is reconstructible end-to-end.
