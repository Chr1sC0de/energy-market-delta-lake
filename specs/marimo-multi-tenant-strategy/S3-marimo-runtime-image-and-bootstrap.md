# S3 — Marimo runtime image and bootstrap

## Objective
Standardize the per-user runtime with marimo, polars, plotting stack, and security defaults.

## Scope
- Runtime packaging
- Startup service
- Patch/version strategy

## Proposed implementation
1. Build a hardened base image/AMI containing:
   - Python + marimo
   - polars/pyarrow
   - approved plotting libraries (plotly + altair or matplotlib)
2. Bootstrap script installs only pinned dependencies.
3. Run marimo via systemd or container with:
   - localhost binding only
   - health endpoint
   - resource limits and log shipping
4. Add version manifest for reproducibility and rollback.

## Pulumi changes
- Add AMI id/version config in stack settings.
- Add user-data template version hash for controlled rollouts.

## Deliverables
- Runtime bill of materials (BOM).
- Base image build pipeline spec.
- Startup/health script and validation checklist.

## Acceptance criteria
- Workspace runtime versions are consistent per release channel.
- marimo process is never directly internet-exposed.
