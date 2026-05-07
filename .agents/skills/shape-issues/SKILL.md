---
name: shape-issues
description: Shape plans, specs, PRDs, or broad requests into repo-local Ralph-ready GitHub Issue drafts. Use when Codex needs to replace or strengthen to-issues for this repository by producing independently workable issue drafts with required Ralph sections, context anchors, QA plans, embedding-based context coverage, and stiffness or step-size scoring before ralph-triage or ralph-loop work.
---

# Shape Issues

Convert shaped plans into Ralph-ready issue drafts with explicit context
evidence. This skill is non-mutating in v1: it drafts and scores issues, but it
does not create, label, edit, comment on, or close GitHub Issues.

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
3. Draft a bundle JSON file under `.shape-issues/runs/<slug>/bundle.json`.
4. Run `scripts/shape_issue_gate.py` on the bundle with an embedding provider.
5. Revise the drafts until every issue that should be AFK-drainable has
   `action: ready`.
6. Present the Markdown report and issue drafts to the Operator. Hand off to
   `$ralph-triage` or manual issue creation only after review.

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
      "body": "## What to build\n...\n",
      "labels": ["enhancement", "delivery-gitflow"]
    }
  ]
}
```

For passing drafts, recommend exactly one category label (`bug` or
`enhancement`) and exactly one **Delivery mode** label. The gate reports the
recommended state label; it does not apply labels.

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
