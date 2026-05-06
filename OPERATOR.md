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
before it can become `ready-for-agent`. Exploratory delivery issues must also
include `## Review focus` stating the human judgment the durable
**Exploratory branch** needs.

Use `$ralph-triage` to prepare issues for drain. Triage sets exactly one
category label, exactly one state label, and at most one **Delivery mode** label.
Default to **Gitflow delivery** unless the work is a small, low-risk docs,
tests, tooling, or script change that fits **Trunk delivery**, or an explicitly
exploratory change whose `## Review focus` says why it should publish a durable
**Exploratory branch** and remain open with `agent-reviewing`.

Use `$ralph-loop drain` to let Ralph implement ready issues. Ralph owns
worktrees, deterministic QA, **Local integration** for Gitflow or Trunk
delivery, Exploratory branch handoff, **Integration target** pushes, and
GitHub issue metadata after validation. After a successful **Local
integration** or Exploratory handoff, **Ready issue refresh** reconciles the
open issue queue before Ralph claims the next `ready-for-agent` issue.

For unattended queue cleanup after `dev` review, prefer the checkpointed
Operator run path. It drains one ready issue boundary at a time, runs
**Promotion** when `agent-integrated` issues remain, lets successful
**Post-promotion review** create validated follow-up GitHub Issues, and repeats
until no open `ready-for-agent`, `agent-integrated`, `agent-running`, or
`agent-failed` issues remain.

Codex should launch Operator runs detached, then stop polling child logs:

```bash
python3 scripts/ralph.py --drain-promote-all --detach
```

Use the compact status command at issue boundaries:

```bash
python3 scripts/ralph.py --operator-run-status latest
```

The detached launcher prints the Operator run directory and status command, then
exits. Status reads `.ralph/operator-runs/.../operator-run.json` and reports the
current state, last checkpoint, current issue or **Promotion**, child
`.ralph/runs/.../ralph-run.json` paths, queue counts, and recommended next
action. A foreground run is also available for human terminals:

```bash
python3 scripts/ralph.py --drain-promote-all --max-cycles 10
```

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
- For manually recovered Gitflow work, verify the issue has a parseable
  `Ralph Gitflow manual recovery completed.` comment with the recovered `dev`
  commit before Promotion.
- Review the diff for accidental secrets, generated artifacts, unrelated
  refactors, or mismatched docs.
- Check whether changed **Subprojects** require operator attention beyond
  Ralph's aggregate **Push check**.
- If AEMO ETL files changed, expect the AEMO ETL **End-to-end test** gate during
  **Promotion**.
- Confirm no open blocker or manual follow-up should stop the range from
  reaching `main`.

For accepted Exploratory review, merge the durable **Exploratory branch** to
`dev`, add an issue comment that starts with
`Ralph exploratory acceptance completed.` and includes a `Commit: ...` line for
the accepted `dev` commit SHA, remove `agent-reviewing`, and add
`agent-integrated`. For rejected Exploratory review, leave the issue open,
remove `agent-reviewing`, add `ready-for-human`, and comment the review result
and next action. ADR
[0005](docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md)
records why **Exploratory branches** stay outside automatic **Promotion**.

## Promotion

Run `$ralph-loop promote` only after the `dev` review is complete.

Ralph computes the aggregate **Push check**, merges reviewed `dev` work into
`main`, fast-forwards `dev` to the promotion commit, and closes only
`agent-integrated` issues whose recorded Gitflow **Local integration** commit or
documented manual Gitflow recovery commit, or accepted Exploratory commit is
verified in the promoted branch range.

Unverified **Promotion** commits in the range are mandatory
**Post-promotion review** context only. They do not require explicit issue
association before **Promotion**, do not block **Promotion** by themselves, and
do not automatically create GitHub Issues by themselves. Successful
**Promotion** runs may create validated follow-up issues only from structured
actionable **Post-promotion review** drafts; pass
`--skip-post-promotion-followups` to keep review while skipping that creation,
or `--skip-post-promotion-review` to skip both.

If Promotion fails before `main` is pushed, leave issues open and inspect the
run manifest. If it fails after `main` is pushed, stop and inspect before
reconciling GitHub metadata.

When the AEMO ETL **End-to-end test** gate runs, treat its budget report as a
**Promotion** contract, not a local development benchmark. Duration or run-count
failures point to run explosion, queue contention, or environment slowdown;
target-progress, asset-check, or missing-telemetry failures mean the source
revision has not proven the required coverage. Use the printed
`run-manifest.json` path before retrying or reconciling issue state.

## Recovery

Use `$ralph-loop inspect failure` or `python3 scripts/ralph.py --inspect-run
.ralph/runs/...` before changing state. Use recovery only after Ralph verifies
the recorded published commit is reachable from the expected **Integration
target**.

If **Ready issue refresh** fails after **Local integration**, do not roll back
the integrated commit. Inspect `ready_issue_refresh.mutation_results` in the run
manifest, reconcile only the failed GitHub Issue metadata, then restart the
drain once the queue is consistent.

For a checkpointed Operator run, inspect status before opening child logs:

```bash
python3 scripts/ralph.py --operator-run-status latest
```

Follow the recommended next action. Issue failures point to the child
implementation manifest; **Promotion** failures point to the child Promotion
manifest; stopped-by-guard means review progress before rerunning with a larger
`--max-cycles` value.

Keep failed worktrees unless the maintainer asks for cleanup.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `AGENTS.md`
  - `scripts/ralph.py`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `docs/agents/README.md`
  - `docs/agents/ralph-loop.md`
  - `backend-services/scripts/aemo-etl-e2e`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
  - `docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify commands, links, labels, and canonical Ralph terms`
