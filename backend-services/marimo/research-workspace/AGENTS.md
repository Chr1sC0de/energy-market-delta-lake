# Marimo-Codex Research Workspace

This workspace is for local notebook research only. It is separate from the
curated dashboard image and must not be treated as deployed Codex enablement.

## Notebook Research

- Keep exploratory notebooks under `notebooks/`.
- Prefer small, reproducible marimo notebooks with visible assumptions,
  source paths, and evidence cells.
- Keep notebook state replayable from a clean kernel. Avoid hidden host state,
  manual shell side effects, or credentials stored in notebook cells.
- Use the Subproject's existing dependencies first. Add new notebook
  dependencies only when the research note explains why they are needed.
- Keep durable findings in notebook cells or Markdown issue drafts, not in
  transient terminal output.

## Data Access Boundaries

- Use local-first data only: LocalStack via `AWS_ENDPOINT_URL`, files mounted
  into this workspace, or checked-in sample notebooks.
- Treat `AWS_ACCESS_KEY_ID=test` and `AWS_SECRET_ACCESS_KEY=test` as LocalStack
  mock credentials only.
- Do not access deployed AWS services, production buckets, live credentials, or
  external private datasets from this workspace.
- Do not paste secrets into notebooks, Markdown drafts, environment files, or
  terminal transcripts.
- If research needs non-local data or network access beyond public package/docs
  lookup, stop and ask the Operator to approve the scope first.

## Codex Boundary

- Codex may be used locally by a human Operator against this workspace for
  notebook research and issue-draft preparation.
- Do not launch unattended Codex from compose, container startup, a notebook
  cell, or any deployed service path.
- Do not create commits, pushes, pull requests, GitHub comments, GitHub labels,
  or issue mutations from this workspace.
- Deployed Codex execution is deferred until a dedicated security review
  approves identity, network, filesystem, secret, audit, and rollback controls.

## Issue-Draft Generation

- Write proposed issue drafts under `issue-drafts/`.
- Drafts should use Ralph-ready sections when they are intended for the repo
  queue:
  - `## What to build`
  - `## Acceptance criteria`
  - `## Blocked by`
  - `## Current context`
  - `## Context anchors`
  - `## Stiffness estimate`
  - `## QA plan`
  - `## Review focus` for Exploratory delivery
- Keep generated drafts read-only until the Operator explicitly decides how to
  shape, gate, triage, or publish them through the repo workflow.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `backend-services/compose.yaml`
  - `backend-services/marimo/Dockerfile`
  - `backend-services/marimo/README.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `uv run pytest tests/component`
  - `prek run -a`
  - `verify local-only data, GitHub mutation, and deployed Codex boundaries`
