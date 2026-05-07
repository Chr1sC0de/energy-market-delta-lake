# Shape Issues Gate Contract

The gate is a deterministic sensor for `$shape-issues`. It checks that each
draft issue can be worked independently and that its expected step size is not
too large for default Ralph drain.

## Inputs

- Bundle JSON with `summary`, `shared_context`, optional `operator_overrides`,
  and an `issues` array.
- Each issue has `id`, `title`, `body`, and `labels`.
- Version 2 bundles may include publisher metadata such as `classification` and
  `blocked_by`; the gate ignores those fields and the publisher consumes them
  after the report is written.
- The repo root supplies the context corpus from tracked files.

## Readiness Rules

An issue can be reported as `ready` only when it has:

- `## What to build`, `## Acceptance criteria`, and `## Blocked by`
- `## Current context`, `## Context anchors`, `## Stiffness estimate`, and
  `## QA plan`
- `## Review focus` when `delivery-exploratory` is recommended
- optional `## Operator approval evidence` when a draft expects live model,
  network, dependency-download, or unsandboxed execution approval context
- exactly one category label and one **Delivery mode** label
- parseable anchors for paths/docs, symbols/constants, labels/targets, and
  QA/Test lane evidence
- embedding matches between the issue query and repo corpus above the configured
  semantic threshold
- stiffness below the split threshold, unless an Operator override is recorded

## Stiffness Signals

The gate treats these as step-size or stiffness signals:

- multiple **Subprojects** or repo areas in anchors or semantic matches
- Integration, End-to-end, Deployed, LocalStack, S3, Dagster, infrastructure,
  schema, **Promotion**, or cross-Subproject language
- many acceptance criteria
- vague blockers or placeholder context
- semantic matches spread across many unrelated repo areas

High stiffness recommends `split`. Medium stiffness remains visible in the
report so the Operator can tune scope before publishing.

The stiffness scan is section-aware. It reads implementation-relevant sections:
`## What to build`, `## Acceptance criteria`, `## Current context`, and
`## QA plan`. It treats `## Stiffness estimate` as the author's declared
estimate and records mismatches between that estimate and the computed score.
It does not scan `## Operator approval evidence` for raw stiffness terms.

Line-level boundary language suppresses stiff keyword hits when the issue says
the work does not cross a boundary. Examples include `does not`, `do not`,
`without`, `out of scope`, `non-goal`, `prohibited`, `must not`, and `no`.
Suppressed terms are still reported as ignored evidence.

For root agent workflow work, `.agents/`, root `tests/`, `OPERATOR.md`,
`AGENTS.md`, `docs/agents/`, and related root agent docs count as one scoring
surface. Backend **Subprojects**, infrastructure projects, and unrelated repo
areas remain separate scoring surfaces.

## Outputs

- `report.json`: machine-readable thresholds, model/provider metadata, bundle
  digest, issue scores, actions, semantic matches, validation reasons,
  declared/computed stiffness mismatch, ignored stiffness mentions, scoring
  surfaces, and any Operator approval evidence found in issue bodies. Each
  issue entry includes a `source_digest`; the top-level `bundle_digest` lets the
  publisher refuse stale bundle/report pairs.
- `report.md`: Operator-readable evidence for the issue bundle.

Operator approval evidence is recorded only as context. It does not grant tool
permission and must not bypass Codex escalation or sandbox review.
