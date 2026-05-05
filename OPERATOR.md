# Operator Workflow

This guide is the human-facing **Operator workflow** for shaping work, preparing
GitHub Issues, draining Ralph, reviewing `dev`, and running **Promotion**.

Use repo canonical terms from [CONTEXT.md](CONTEXT.md), especially
**Subproject**, **Test lane**, **Fast check**, **Commit check**, **Push check**,
**Local integration**, **Delivery mode**, **Integration target**,
**Sandboxed issue access**, **Ready issue refresh**, and **Promotion**.

## Canonical Path

Run the Ralph skill cycle in this order:

```text
$grill-with-docs -> optional $to-prd -> $to-issues -> $ralph-triage -> $ralph-loop drain -> review dev -> $ralph-loop promote
```

Use `$grill-with-docs` as the default shaping step. It challenges the plan
against `CONTEXT.md`, existing ADRs, and maintained docs, then captures resolved
domain language where needed.

Use `$grill-me` instead when the work only needs a lighter plan review and does
not need doc or domain sync.

Use `$to-prd` only for large, durable, or spec-heavy work where future issues
need a stable product-level reference. Skip it for small changes that can move
straight from shaped plan to GitHub Issues.

Use `$to-issues` to create independently grabbable GitHub Issues. Each issue
must include `## What to build`, `## Acceptance criteria`, and `## Blocked by`
before it can become `ready-for-agent`.

Use `$ralph-triage` to prepare issues for drain. Triage sets exactly one
category label, exactly one state label, and at most one **Delivery mode** label.
Default to **Gitflow delivery** unless the work is a small, low-risk docs,
tests, tooling, or script change that fits **Trunk delivery**, or an explicitly
exploratory change that should publish a durable review branch and remain open
with `agent-reviewing`.

Use `$ralph-loop drain` to let Ralph implement ready issues. Ralph owns
worktrees, deterministic QA, **Local integration**, **Integration target**
pushes, and GitHub issue metadata after validation. After a successful
**Local integration**, **Ready issue refresh** reconciles the open issue queue
before Ralph claims the next `ready-for-agent` issue.

## Before Drain

Start from a clean root worktree for live Ralph operations:

```bash
git status --short
gh auth status
```

For Gitflow drains, confirm push auth against `dev`; for trunk drains, confirm
push auth against `main`:

```bash
git push --dry-run origin HEAD:dev
git push --dry-run origin HEAD:main
```

Use `$ralph-loop dry-run drain` when the root worktree is dirty or when you only
want to inspect Ralph's next action. Use dirty-worktree operation only when the
operator explicitly accepts that risk.

## Review Dev

Before `$ralph-loop promote`, review the **Integration target** that will be
promoted from `dev` to `main`.

Use this checklist:

- Confirm the root worktree is clean with `git status --short`.
- Fetch current refs with `git fetch origin main dev`.
- Inspect the promotion range with `git log --oneline --decorate origin/main..origin/dev`.
- Inspect changed files with `git diff --stat origin/main..origin/dev` and `git diff --name-only origin/main..origin/dev`.
- Match each included issue to its Ralph evidence and verify it is marked
  `agent-integrated`.
- Review the diff for accidental secrets, generated artifacts, unrelated
  refactors, or mismatched docs.
- Check whether changed **Subprojects** require operator attention beyond
  Ralph's aggregate **Push check**.
- If AEMO ETL files changed, expect the AEMO ETL **End-to-end test** gate during
  **Promotion**.
- Confirm no open blocker or manual follow-up should stop the range from
  reaching `main`.

## Promotion

Run `$ralph-loop promote` only after the `dev` review is complete.

Ralph computes the aggregate **Push check**, merges reviewed `dev` work into
`main`, fast-forwards `dev` to the promotion commit, and closes only
`agent-integrated` issues whose recorded Gitflow **Local integration** commit is
verified in the promoted branch range.

If Promotion fails before `main` is pushed, leave issues open and inspect the
run manifest. If it fails after `main` is pushed, stop and inspect before
reconciling GitHub metadata.

## Recovery

Use `$ralph-loop inspect failure` or `python3 scripts/ralph.py --inspect-run
.ralph/runs/...` before changing state. Use recovery only after Ralph verifies
the recorded **Local integration** commit is reachable from the expected
**Integration target**.

Keep failed worktrees unless the maintainer asks for cleanup.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `AGENTS.md`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `docs/agents/README.md`
  - `docs/agents/ralph-loop.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify commands, links, labels, and canonical Ralph terms`
