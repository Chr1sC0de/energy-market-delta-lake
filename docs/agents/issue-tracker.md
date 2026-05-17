# Issue Tracker

This repo tracks work in GitHub Issues for
`Chr1sC0de/energy-market-delta-lake`. GitHub Issues are the board and queue for
Ralph.

## Access

Agent workflows use the `gh` CLI for issue reads and writes. Local auth must
pass before running `$ralph-triage` or `$ralph-loop`:

```bash
gh auth status
```

Ralph provides **Sandboxed issue access** to spawned Codex subprocesses by
default. The sandbox receives a `GH_TOKEN` sourced from the parent environment
or local `gh auth`, and a wrapper limits `gh` to phase-specific issue metadata
commands. Implementation, triage, and **Ready issue refresh** passes may
receive phase-scoped issue access; **Full-access implementation pass** runs for
`.agents/` context-anchor issues keep read-only issue commands. The current
**Issue completion review**, **Ready issue refresh** analysis subprocess, and
**Post-promotion review** also receive read-only issue commands. After
successful **Promotion**, Ralph may
create structured actionable follow-up issues from the review artifact through
its validated create-only helper; the review agent still cannot directly create,
comment, edit, close, or reopen arbitrary GitHub Issues. When checkpointed
Operator deployment fails, Ralph may also create validated deploy-repair issues
from a deploy-failure analysis artifact. That analyzer receives redacted
deployment evidence, read-only issue commands, and no AWS or Pulumi
credentials; it cannot run AWS, Pulumi, or deployment commands or mutate GitHub
Issues directly. Git push auth is separate;
**Local integration**, Exploratory handoff, **Integration target** pushes, and
**Promotion** stay outside the sandbox.

## Queue contract

Use [triage-labels.md](triage-labels.md) for category, state, runtime, and
**Delivery mode** labels. A ready implementation issue must have
`ready-for-agent`, a category label, at most one **Delivery mode** label, and
these sections:

- `## What to build`
- `## Acceptance criteria`
- `## Blocked by`

Ready `delivery-exploratory` issues must also include `## Review focus`, which
states the human judgment the durable **Exploratory branch** needs. Missing
`## Review focus` is a malformed Exploratory delivery contract; Ralph marks the
issue `agent-failed` with evidence before creating an implementation worktree
or publishing an Exploratory handoff.

Ready `delivery-exploratory` issues may also include `## Operator smoke` when
the human review needs a credentialed deployed smoke after the durable
**Exploratory branch** is pushed. The section supports `Smoke id: <id>`,
`Timeout: <seconds>`, and credential-boundary prose for human review. Ralph
validates the smoke id against a hardcoded allowlist before command execution;
unknown smoke ids and smoke sections on non-Exploratory issues fail with issue
evidence. The first allowlisted id is `ec2-run-worker-placement`, which runs
`infrastructure/aws-pulumi/scripts/run-ec2-run-worker-smoke` from the AWS Pulumi
**Subproject** in the issue worktree. These smokes run only from Ralph's
operator-owned outer loop and do not grant AWS or Pulumi credentials to
sandboxed Codex implementation subprocesses.

`## Current context` is optional. **Ready issue refresh** may add or update it,
but existing `ready-for-agent` issues do not need that section to stay ready.
Refreshed issues that remain `ready-for-agent` must still contain the three
required sections above, plus `## Review focus` for `delivery-exploratory`.

Ready issues whose `## Context anchors` include `.agents/` paths require an
operator-approved **Full-access implementation pass**. Without
`--allow-full-access-implementation`, Ralph stops before claim and leaves the
issue unchanged. With the flag, the implementation subprocess gets full
filesystem access, read-only GitHub Issue commands, and a pre-QA diff guard that
fails the issue if changed files leave the listed context anchors.

Ralph implementation prompts treat the issue body as the primary contract. When
recent Ready issue refresh comments exist, Ralph appends only the latest five
comments with the Ready issue refresh audit prefix in a separate prompt section
after the body; normal comments and triage comments are not included.

After implementation QA passes, Ralph runs **Issue completion review** before
**Local integration**, Trunk push, or Exploratory handoff when the changed files
include deployable paths, **Agent workflow changes**, when the issue uses
**Trunk delivery**, or when high-stiffness issue evidence is present. Passing
review lets the normal delivery path continue. Failing review findings become a
repair prompt for remaining `--max-codex-attempts` attempts; Ralph reruns QA and
review after each repair. If the budget is exhausted, Ralph marks the issue
`agent-failed`, preserves worktrees and logs, and does not update an
**Integration target**. This gate is not human `dev` review, **Ready issue
refresh**, or **Post-promotion review**.

`$shape-issues` v2 may create new GitHub Issues only after explicit Operator
confirmation of a passing gate report and pre-publication review Markdown:
`issue-drafts.md` plus one `issue-drafts/*.md` file per draft. Those created
issues enter the board as `needs-triage` only, with source markers for duplicate
detection. `$shape-issues` does not move issues to `ready-for-agent`, and it
must not edit, comment on, close, reopen, or relabel existing issues. Follow-up
verbs after a `$shape-issues` plan keep creating, gating, or publishing issue
drafts; direct implementation requires `$ralph-loop` or an explicit named
GitHub Issue request. Fixture-gated reports can preview with `--dry-run`, but
non-dry-run publication requires `--allow-fixture-publish` and records fixture
provenance in the manifest and issue body. Non-dry-run publication preflights
`gh`, authentication, and target repository access before writing final body
files; later duplicate-search or create failures record their phase, exit code,
stderr summary, and stdout summary in `publish-manifest.json`. `$ralph-triage`
remains responsible for category, state, and **Delivery mode** labels before
Ralph drain.

Deploy-repair issues created from failed deployment evidence use a separate
`ralph-deploy-repair:...` source marker namespace for duplicate detection.
Valid deploy-repair drafts are created with `bug`, exactly one **Delivery
mode** label, and `ready-for-agent`. Invalid or incomplete drafts are still
created, but only with `needs-triage` and Ralph validation evidence in the
issue body.

Valid deploy-repair issues are targeted through checkpointed Operator state,
not through a general priority-label vocabulary. While
`deploy_repair.target_issue` is active in the Operator manifest, that issue is
selected before unrelated ready work and then follows normal implementation,
QA, **Local integration**, **Promotion**, and deployment retry. Once deployment
passes, the Operator clears that state and the ready queue returns to
oldest-first order.

Runtime labels such as `agent-running`, `agent-integrated`, `agent-merged`,
`agent-failed`, and `agent-reviewing` block repeat implementation and automated
triage reconsideration. In particular, `agent-reviewing` means
**Exploratory delivery** has already published a durable **Exploratory branch**
and the issue is waiting for human review. Accepted review moves the issue from
`agent-reviewing` to `agent-integrated` after an explicit decision artifact is
applied: Ralph validates the recorded handoff branch and commit, merges accepted
branches into a temporary `dev` acceptance worktree, runs selected merged-target
QA, pushes `dev`, then comments acceptance evidence and changes labels. If an
accepted branch merge conflicts, Ralph pauses with `acceptance_conflict`, leaves
the acceptance worktree available, writes `decisions.json`, `conflicts.json`,
and `codex-resolution-prompt.md`, and does not push or mutate GitHub Issues
until `--continue-exploratory-acceptance <run_dir>` validates a clean resolved
worktree and reruns merged-target QA. Held review keeps `agent-reviewing` and
comments the reason. Rejected review removes `agent-reviewing`, adds
`ready-for-human`, comments the review result, and leaves the issue open.
Manual Gitflow recovery must add the parseable recovery evidence documented in
[ralph-loop.md](ralph-loop.md) before leaving or applying `agent-integrated`, so
later **Promotion** can verify the recovered `dev` commit before closure.
Checkpointed Operator runs include open `agent-reviewing` issues separately in
their queue snapshot. When no unblocked ready issue can proceed and
`agent-reviewing` issues remain, Ralph stops as `needs_review` with checkpoint
`exploratory_acceptance_review_required` and writes a non-mutating
**Exploratory acceptance review** artifact instead of marking the queue as a
generic failure.
When unblocked ready work exists, checkpointed Operator runs use the same
parallel drain scheduler as plain `--drain`. A single Operator cycle may record
multiple issue checkpoints from serial Gitflow or Trunk attempts and bounded
Exploratory workers before a **Promotion** checkpoint. Promotion starts only
after active Exploratory workers and implementation **Ready issue refresh**
claim gates have settled.
Operator-smoke Exploratory issues are an exclusive serial lane exception: Ralph
does not submit them to the Exploratory worker pool, waits for active issue
workers to finish before claiming them, and does not overlap the smoke issue
with another active implementation worker.

After a successful drain-mode **Local integration**, Exploratory handoff, or
successful **Promotion** verified issue closure, Ralph computes **Ready issue
refresh** candidates from open issues within `--issue-limit`. The candidate scan
keeps unblocked `ready-for-agent` issues in queue order, excludes issues with
runtime stop labels, and treats the issue that was just completed as a
satisfied blocker for candidate selection even when Gitflow leaves it open with
`agent-integrated` until **Promotion** or Exploratory delivery leaves it open
with `agent-reviewing` for human review. Post-Promotion candidate selection
also includes stale `needs-triage` or unlabeled issues whose blockers are all
satisfied and whose `## Blocked by` section names at least one newly closed
promoted issue. Ralph then runs a read-only analysis subprocess using
`$ralph-issue-refresh`. That subprocess receives the integrated or promoted
issue context, **Delivery mode**, **Integration target**, relevant commit,
changed files, QA evidence, run log path, and candidate issue bodies, then writes
`ready-issue-refresh-analysis.md` under the current `.ralph/runs/issue-.../`
or `.ralph/runs/promote-.../` directory. It records planned issue updates and a
structured mutation plan, but is not allowed to mutate GitHub Issues itself.
Ralph's outer loop applies validated refresh comments, body edits, label
transitions, and completed closures with GitHub Issue metadata commands only.
When candidates were selected, the analysis must include a parseable fenced
`json` plan with `ready_issue_refresh_mutations`; candidates with no metadata
update use an explicit `no_change` entry. Reports with no selected candidates
may omit mutation JSON. The run manifest records per-candidate mutation status
and recovery guidance for partial failures. Malformed or missing mutation JSON
for selected implementation candidates stops the drain before scheduling further
issue attempts. In parallel drains, the scheduler pauses new claims while
implementation **Ready issue refresh** analysis or metadata mutation runs,
allows already active Exploratory workers to finish, and records
`drain_scheduler.fatal_stop` recovery evidence in child run manifests for fatal
refresh, post-push metadata, or environment failures. Post-Promotion refresh
failures are warning-only after successful **Promotion**.

Use [ralph-loop.md](ralph-loop.md) for Ralph internals, including
**Delivery mode**, **Local integration**, **Integration target**, **Promotion**,
**Issue completion review**, **Ready issue refresh**, checkpointed Operator
runs, **Post-promotion review**, **Exploratory acceptance review**, run
manifests, QA selection, and recovery behavior.
Use [OPERATOR.md](../../OPERATOR.md) for the human **Operator workflow**.
Use `$ralph-curate` when existing open issues need to be compared with the
current branch before changing bodies, labels, blockers, or closure state.
Use ADR
[0005](../adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md)
for the decision that keeps **Exploratory branches** outside automatic
**Promotion** until human acceptance evidence reaches `dev`.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `OPERATOR.md`
  - `.agents/skills/shape-issues/SKILL.md`
  - `.agents/skills/shape-issues/scripts/shape_issue_gate.py`
  - `.agents/skills/shape-issues/scripts/codex_context_assessor.py`
  - `.agents/skills/shape-issues/scripts/publish_shape_issues.py`
  - `.agents/skills/ralph-curate/SKILL.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `.agents/skills/ralph-issue-refresh/SKILL.md`
  - `docs/agents/README.md`
  - `docs/agents/ralph-loop.md`
  - `docs/agents/triage-labels.md`
  - `docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md`
  - `docs/adr/0007-ralph-full-access-implementation-pass.md`
  - `scripts/ralph.py`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `verify repo names, commands, labels, and links`
