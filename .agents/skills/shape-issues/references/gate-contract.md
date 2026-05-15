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
- The repo root supplies the bounded evidence corpus. The gate assembles it
  from declared `Path:` and `Doc:` anchors plus up to eight deterministic `rg`
  candidate files per issue.
- The **Issue context assessor** command reads one JSON request from stdin and
  writes one JSON response to stdout.

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
- an **Issue context assessor** verdict of `pass` with cited paths and reasons
  that refer only to supplied evidence
- stiffness below the split threshold, unless an Operator override is recorded

## Stiffness Signals

The gate treats these as step-size or stiffness signals:

- multiple **Subprojects** or repo areas in anchors or supplied context evidence
- Integration, End-to-end, Deployed, LocalStack, S3, Dagster, infrastructure,
  schema, **Promotion**, or cross-Subproject language
- many acceptance criteria
- vague blockers or placeholder context
- supplied context evidence spread across many unrelated repo areas

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

- `report.json`: machine-readable thresholds, **Issue context assessor**
  provider metadata, recorded corpus digest, bundle digest, issue scores,
  actions, `context_assessment`, bounded context evidence, validation reasons,
  declared/computed stiffness mismatch, ignored stiffness mentions, scoring
  surfaces, and any Operator approval evidence found in issue bodies. Each
  issue entry includes a `source_digest`; the top-level `bundle_digest` lets the
  publisher refuse stale bundle/report pairs.
- `report.md`: Operator-readable evidence for the issue bundle, including the
  assessor provider, corpus digest, per-issue context verdicts, cited paths, and
  stiffness evidence.

## Publication Policy

The publisher treats `report.json` `context_assessor.provider` as part of the
publish contract. Reports from the fixture assessor may be previewed with
`--dry-run` without any extra flag, but non-dry-run GitHub Issue publication
must use `--allow-fixture-publish`. When that override is used, the publisher
records the fixture provider in `publish-manifest.json` and in the final issue
body so `$ralph-triage` and later reviewers can see that readiness came from
fixture evidence rather than the live **Issue context assessor**.

Operator approval evidence is recorded only as context. It does not grant tool
permission and must not bypass Codex escalation or sandbox review.
