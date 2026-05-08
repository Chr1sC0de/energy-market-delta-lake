# Operator Workflow

This guide is the human-facing **Operator workflow** for shaping work, preparing
GitHub Issues, draining Ralph, reviewing `dev`, and running **Promotion**.

Use repo canonical terms from [CONTEXT.md](CONTEXT.md), especially
**Subproject**, **Test lane**, **Fast check**, **Commit check**, **Push check**,
**Local integration**, **Delivery mode**, **Integration target**,
**Sandboxed issue access**, **Full-access implementation pass**,
**Ready issue refresh**, **Exploratory acceptance review**, and **Promotion**.

## Canonical Path

Run the Ralph skill cycle in this order:

```text
$grill-with-docs -> optional $to-prd -> $shape-issues -> $ralph-triage -> $ralph-loop drain -> review dev -> $ralph-loop promote
```

Use `$grill-with-docs` as the default shaping step. It challenges the plan
against `CONTEXT.md`, existing ADRs, and maintained docs, then captures resolved
domain language where needed.

Use `$grill-me` instead when the work only needs a lighter plan review and does
not need doc or domain sync.

Use `$to-prd` only for large, durable, or spec-heavy work where future issues
need a stable product-level reference. Skip it for small changes that can move
straight from shaped plan to GitHub Issues.

Use `$shape-issues` to draft independently grabbable GitHub Issues with
tracer-bullet slices, context anchors, QA plans, embedding-based context
coverage, and stiffness scoring. It writes `.shape-issues/runs/.../report.md`
and `report.json`; after explicit Operator confirmation it may publish the
gated outputs as `needs-triage` issues. `$shape-issues` does not move issues to
`ready-for-agent` and must not edit, comment on, close, reopen, or relabel
existing GitHub Issues. Each implementation draft must include
`## What to build`, `## Acceptance criteria`, and `## Blocked by` before it can
be triaged toward `ready-for-agent`. Exploratory delivery drafts must also
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
until no open `ready-for-agent`, `agent-integrated`, `agent-reviewing`,
`agent-running`, or `agent-failed` issues remain. When no unblocked ready issue
can proceed and open `agent-reviewing` issues remain, the Operator run stops as
`needs_review` and writes an **Exploratory acceptance review** JSON and Markdown
artifact under the Operator run directory instead of treating the queue as a
generic failure.

Codex should launch Operator runs detached, then stop polling child logs:

```bash
python3 scripts/ralph.py --drain-promote-all --detach
```

For a queue that intentionally includes ready `.agents/` workflow issues, the
operator must opt into the **Full-access implementation pass**:

```bash
python3 scripts/ralph.py --drain-promote-all --detach --allow-full-access-implementation
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
want to inspect Ralph's next serial Gitflow or trunk candidate plus bounded
Exploratory candidates. `--exploratory-concurrency` controls the Exploratory
preview bound, defaults to `2`, and has a minimum of `1`. Targeted `--issue`
dry runs still preview only that issue. Use dirty-worktree operation only when
the operator explicitly accepts that risk.

Ready issues that anchor `.agents/` files stop before claim unless the operator
passes `--allow-full-access-implementation`. With that flag, Ralph runs only
those implementation subprocesses as a **Full-access implementation pass**, keeps
their GitHub Issue commands read-only, and hard-stops before QA if the resulting
diff changes files outside the issue's `## Context anchors`.

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
  **Promotion**. That gate rebuilds its local e2e images and validates runtime
  Dagster GraphQL target counts against current source definitions.
- If Marimo runtime files changed, expect Marimo **Component test** and Marimo
  **Commit check** evidence from `backend-services/marimo`. Docs-only Marimo
  changes use the root doc **Commit check** evidence; mixed docs/runtime Marimo
  changes should include both surfaces.
- Confirm no open blocker or manual follow-up should stop the range from
  reaching `main`.

For explicit Exploratory review decisions, create a decision JSON artifact and
apply it through Ralph:

```json
{
  "decisions": [
    {"issue_number": 42, "decision": "accept", "reason": "Reviewed on dev."},
    {"issue_number": 43, "decision": "hold", "reason": "Waiting on product."},
    {"issue_number": 44, "decision": "reject", "reason": "Wrong workflow."}
  ]
}
```

```bash
python3 scripts/ralph.py --apply-exploratory-acceptance-decisions path/to/decisions.json
```

Accepted decisions merge the durable **Exploratory branch** into a temporary
acceptance worktree based on `origin/dev`, run selected merged-target QA from
the resulting changed files, push `dev` only after QA passes, then comment
`Ralph exploratory acceptance completed.`, remove `agent-reviewing`, and add
`agent-integrated`. If an accepted branch merge conflicts, Ralph pauses with
`acceptance_conflict`, leaves the acceptance worktree in place, and writes
`decisions.json`, `conflicts.json`, and `codex-resolution-prompt.md` under the
run directory without pushing or mutating GitHub Issues. Resolve only that
acceptance worktree, preserve accepted issue intent, commit the resolution so
the worktree is clean, then continue with:

```bash
python3 scripts/ralph.py --continue-exploratory-acceptance .ralph/runs/exploratory-acceptance-20260504T010203Z
```

The continue command validates the paused run artifacts, refuses stale,
missing, mismatched, dirty, or still-conflicted state, reruns merged-target QA,
pushes `dev`, and only then applies acceptance comments and labels. Held
decisions keep `agent-reviewing` and comment the reason. Rejected decisions
leave the issue open, remove `agent-reviewing`, add `ready-for-human`, and
comment the review result and next action. ADR
[0005](docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md)
records why **Exploratory branches** stay outside automatic **Promotion**.

If Operator status reports `needs_review` with checkpoint
`exploratory_acceptance_review_required`, read
`exploratory-acceptance-review.md` first. It lists each `agent-reviewing` issue,
durable **Exploratory branch**, handoff commit, changed files, recorded QA
evidence, detectable missing **Test lane** evidence, mergeability against
`origin/dev`, and ready issues blocked by the review decision. Run the
`$ralph-loop` Exploratory acceptance review flow, then accept or reject the
listed issues before rerunning drain or **Promotion**.

## Promotion

Run `$ralph-loop promote` only after the `dev` review is complete.

Ralph computes the aggregate **Push check**, merges reviewed `dev` work into
`main`, fast-forwards remote `dev` to the promotion commit, and closes only
`agent-integrated` issues whose recorded Gitflow **Local integration** commit
or documented manual Gitflow recovery commit, or accepted Exploratory commit is
verified in the promoted branch range. After successful **Promotion**, Ralph
also fast-forwards clean checked-out local `dev` or `main` worktrees when the
local branch can safely move to the Promotion commit; dirty or diverged local
worktrees are left untouched with recovery guidance in the run manifest.

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
target-count mismatches, target-progress, asset-check, or missing-telemetry
failures mean the source revision has not proven the required coverage. Use the printed
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

If a **Full-access implementation pass** reports `diff_out_of_scope`, inspect
the child implementation worktree, keep only files named by the issue's
`## Context anchors`, and rerun Ralph for that issue. Ralph does not run QA or
**Local integration** for out-of-anchor full-access diffs.

For a checkpointed Operator run, inspect status before opening child logs:

```bash
python3 scripts/ralph.py --operator-run-status latest
```

Completed or stopped runs write `operator-run-rollup.md` and
`operator-run-rollup.json` beside `operator-run.json`. Read the Markdown rollup
first for the full drain-and-**Promotion** summary: succeeded and failed issues,
manual recoveries, **Local integration** commits, **Promotion** commits, QA
surfaces, **Post-promotion review** follow-ups, final queue state, and the stop
or failure reason. Runs that stop for **Exploratory acceptance review** also
write `exploratory-acceptance-review.md` and
`exploratory-acceptance-review.json` beside the rollup. Use the JSON rollup for
tooling or status-oriented review without tailing child Codex JSONL or rich
command logs.

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
  - `.agents/skills/shape-issues/SKILL.md`
  - `.agents/skills/shape-issues/scripts/publish_shape_issues.py`
  - `scripts/ralph.py`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `docs/agents/README.md`
  - `docs/agents/ralph-loop.md`
  - `backend-services/scripts/aemo-etl-e2e`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
  - `docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md`
  - `docs/adr/0007-ralph-full-access-implementation-pass.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify commands, links, labels, and canonical Ralph terms`
