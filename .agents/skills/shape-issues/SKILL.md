---
name: shape-issues
description: Shape plans, specs, PRDs, or broad requests into repo-local GitHub Issue drafts using tracer-bullet slices and Ralph gate evidence. Use when Codex needs to replace or strengthen to-issues for this repository by producing independently workable issue drafts with required Ralph sections, context anchors, QA plans, embedding-based context coverage, stiffness or step-size scoring, and optional confirmed publication as needs-triage issues before ralph-triage or ralph-loop work.
---

# Shape Issues

Convert shaped plans into independently grabbable GitHub Issue drafts with
explicit context evidence. Version 2 combines tracer-bullet issue shaping with
the repo-local Ralph gate. It can publish confirmed drafts, but only through the
publisher helper and only as `needs-triage` issues. It must not edit, comment
on, close, reopen, or relabel existing GitHub Issues.

## Read First

- Read `CONTEXT.md` for canonical terms.
- Read `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md` for
  the ready issue contract and labels.
- Read `references/gate-contract.md` before running the gate script.
- Read `references/embedding-providers.md` when configuring the embedding
  provider or diagnosing provider failures.

## Workflow

1. Gather the plan, source issue, PRD, review artifact, or user request.
2. Explore the repo enough to name concrete anchors: paths, symbols/constants,
   labels, targets, docs, QA commands, and **Test lanes**.
3. Draft thin vertical tracer-bullet slices that deliver a narrow, verifiable
   path through every affected integration layer needed for the behavior.
   Do not create horizontal layer-only slices such as schema-only, API-only,
   UI-only, docs-only, or tests-only work unless the source request is genuinely
   limited to that layer.
4. Classify every slice as `afk`, `human-decision`, or `exploratory`.
5. Present the slice breakdown to the Operator and ask whether the granularity,
   blockers, and classifications are right. Iterate until approved.
6. Put only implementation slices (`afk` and `exploratory`) in
   `.shape-issues/runs/<slug>/bundle.json`.
7. Run `scripts/shape_issue_gate.py` on the bundle with an embedding provider.
8. Revise the drafts until AFK slices have `action: ready` and Exploratory
   implementation slices have `action: exploratory`.
9. Present the Markdown report, issue drafts, and any report-only
   `human-decision` slices to the Operator.
10. Publish only if the Operator explicitly says the gated outputs are ready to
    publish, then run `scripts/publish_shape_issues.py --confirm-publish`.

## Slice Classes

- `afk`: implementation work an agent can complete without more human
  judgment. It should gate as `ready`.
- `human-decision`: a pre-implementation decision, design review, product
  choice, or architecture question. Keep it out of the gate bundle by default;
  report it to the Operator instead of mapping it to **Exploratory delivery**.
- `exploratory`: implementation work that should produce a durable
  **Exploratory branch** for human review. It must use `delivery-exploratory`,
  include `## Review focus`, and gate as `exploratory`.

Prefer many narrow AFK slices over a few stiff slices. Each implementation slice
should be independently verifiable after **Local integration** or Exploratory
handoff.
An implementation slice is valid only when completing it produces a demonstrable
end-to-end behavior or independently checkable outcome; layer-only prep work
must be merged into the smallest vertical slice that needs it.

## Operator Quiz

Before writing the gate bundle, show the proposed breakdown as a numbered list.
For each slice include title, class, blockers, and any covered user stories or
requirements from the source material. Ask the Operator to confirm:

- whether the granularity is too coarse, too fine, or right
- whether blockers are correct
- whether any slices should merge or split
- whether the `afk`, `human-decision`, and `exploratory` classifications are
  correct

## Issue Body Contract

Every draft issue body must include Ralph's required sections:

- `## What to build`
- `## Acceptance criteria`
- `## Blocked by`

Every draft must also include:

- `## Current context`
- `## Context anchors`
- `## Stiffness estimate`
- `## QA plan`

Exploratory delivery drafts must also include:

- `## Review focus`

When a draft expects a live embedding run outside the sandbox, include:

- `## Operator approval evidence`

This section documents the Operator's intended risk boundary. It is not a tool
approval and must not be treated as permission to bypass Codex escalation,
sandboxing, or external-code review.

Use this shape:

```markdown
## Operator approval evidence

- Purpose: run `$shape-issues` gate against this issue bundle.
- Model: `Qwen/Qwen3-Embedding-0.6B`.
- Remote model code: prohibited; use `--no-trust-remote-code`.
- Downloads: PyPI packages and Hugging Face model files are acceptable.
- Corpus scope: only the files listed in `## Context anchors`.
- Output path: `.shape-issues/runs/<issue-slug>/`.
- Prohibited: secrets, credentials, unlisted repo files, GitHub mutation,
  commits, pushes.
- If the command, model, corpus, or trust settings differ, stop and ask the
  Operator again.
```

`## Operator approval evidence` is separate from publication approval. Publishing
still requires the Operator to explicitly confirm that the gated outputs are
ready to publish.

## Context Anchors

Use structured bullets so the gate can parse them:

```markdown
## Context anchors

- Path: `scripts/ralph.py`
- Symbol: `READY_LABEL`
- Label: `ready-for-agent`
- Target: `dev`
- Doc: `docs/agents/ralph-loop.md`
- QA: `python3 -m unittest discover -s tests`
- Test lane: `root script Unit test`
```

Passing AFK-ready drafts need enough anchors to let a child Codex session work
independently without rediscovering the basic repo surface.

Keep implementation path detail in this section and `## Current context`. Keep
`## What to build` focused on the end-to-end behavior so stale paths do not
become the implementation contract.

## Bundle Format

Write bundle JSON with this shape:

```json
{
  "summary": "Short description of the work being split.",
  "shared_context": [
    "Bundle-level anchors or decisions shared by all drafts."
  ],
  "operator_overrides": {
    "issue-id": "Why the Operator accepts a high-stiffness draft."
  },
  "issues": [
    {
      "id": "stable-issue-id",
      "title": "Issue title",
      "classification": "afk",
      "blocked_by": ["earlier-issue-id"],
      "body": "## What to build\n...\n",
      "labels": ["enhancement", "delivery-gitflow"]
    }
  ]
}
```

`blocked_by` uses stable draft IDs. The publisher rewrites those IDs to real
GitHub Issue references after creating or finding blocker issues.

For passing drafts, recommend exactly one category label (`bug` or
`enhancement`) and exactly one **Delivery mode** label. The gate reports the
recommended state label; it does not apply labels. The publisher ignores those
ready-state recommendations and creates new issues with `needs-triage` only, so
`$ralph-triage` still owns the ready queue transition.

## Gate Command

Default live provider command:

```bash
uv run --with sentence-transformers --with torch \
  python .agents/skills/shape-issues/scripts/hf_embed_jsonl.py \
  --model Qwen/Qwen3-Embedding-8B
```

Run the gate:

```bash
python3 .agents/skills/shape-issues/scripts/shape_issue_gate.py \
  .shape-issues/runs/<slug>/bundle.json \
  --repo-root . \
  --embedding-command "uv run --with sentence-transformers --with torch python .agents/skills/shape-issues/scripts/hf_embed_jsonl.py --model Qwen/Qwen3-Embedding-8B" \
  --out-dir .shape-issues/runs/<slug>
```

The gate writes `report.md` and `report.json`. Runtime outputs under
`.shape-issues/` are ignored by git.

## Publish Command

After Operator confirmation, publish gated outputs:

```bash
python3 .agents/skills/shape-issues/scripts/publish_shape_issues.py \
  .shape-issues/runs/<slug>/bundle.json \
  --repo Chr1sC0de/energy-market-delta-lake \
  --confirm-publish
```

Preview without creating issues:

```bash
python3 .agents/skills/shape-issues/scripts/publish_shape_issues.py \
  .shape-issues/runs/<slug>/bundle.json \
  --repo Chr1sC0de/energy-market-delta-lake \
  --confirm-publish \
  --dry-run
```

The publisher:

- refuses to run without `--confirm-publish`
- refuses gate actions other than `ready` and `exploratory`
- refuses missing, `human-decision`, or mismatched classifications
- refuses when `bundle.json` content no longer matches `report.json`
- refuses duplicate issue IDs, source markers, or generated body paths
- creates only `needs-triage` issues
- never mutates existing issues
- writes `publish-manifest.json` and final issue bodies under the run directory
- adds deterministic source markers, searches for duplicates before create,
  and skips duplicates
- publishes blockers first and rewrites `## Blocked by` to real `#N` or
  `/issues/N` references before dependent issues are created

If publication fails partway through, inspect `publish-manifest.json` and rerun
the same command after fixing the cause. Existing source markers make reruns
skip issues that were already created.

## Gate Actions

- `ready`: the issue is ready to hand to `$ralph-triage` as AFK-drainable.
- `needs-context`: required sections, labels, anchors, QA, or semantic coverage
  are missing.
- `split`: the issue is too stiff or oversized for default AFK drain.
- `exploratory`: use only when the issue explicitly needs durable human review
  and includes `## Review focus`.
- `human-review`: the issue is clear enough to discuss but should not be AFK.

High stiffness defaults to `split`. The Operator may override that only by
recording an `operator_overrides` entry in the bundle.

`operator_overrides` is only for stiffness/step-size decisions. Do not use it
for security, network, dependency-download, or unsandboxed execution approval.

## Stiffness Scoring

The gate scores implementation-relevant sections: `## What to build`,
`## Acceptance criteria`, `## Current context`, and `## QA plan`.
`## Stiffness estimate` is treated as the author's declared estimate, not as
raw keyword evidence.

The scorer ignores stiff terms in explicit negative or boundary-setting
phrases such as `does not`, `do not`, `without`, `out of scope`, `non-goal`,
`prohibited`, `must not`, and `no`. It also excludes
`## Operator approval evidence` from raw stiffness scanning.

Root agent workflow files count as one scoring surface when they are the actual
scope: `.agents/`, root `tests/`, `OPERATOR.md`, `AGENTS.md`,
`docs/agents/`, and related root agent docs. Broader **Subproject** or
infrastructure paths still count as separate surfaces.

The report includes computed stiffness level, declared stiffness level, whether
the declared estimate mismatches the computed score, positive evidence reasons,
ignored excluded-term mentions, and surface areas used for scoring.

## Subagent Audit

Use subagent audit only when the Operator explicitly asks for it, or when a
borderline/high-stiffness bundle needs a second pass. Pass the bundle and gate
report as raw artifacts; do not pass expected answers.
