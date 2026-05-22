# Ralph Uses Local Integration After Issue QA

Ralph keeps GitHub Issues as the visible board and queue, but successful
implementation work is integrated locally instead of opening a GitHub PR. This
keeps the board useful for planning while making the AFK loop responsible for
the whole validated path: implementation QA, any required **Issue completion
review**, squash-merge onto latest `origin/main`, push `main`, comment
completion evidence, and close the issue.

ADR 0002 generalizes this trunk-only path with **Delivery modes**. The
trunk-style behavior described here remains the **Trunk delivery** path.
Gitflow delivery uses the same post-QA **Local integration** mechanism against
`dev`; Exploratory delivery publishes a durable **Exploratory branch** without
a **Local integration** squash merge.

## Considered options

- GitHub PRs as the success gate: preserves a familiar review object, but keeps
  merging outside the loop and leaves completed agent work waiting on PR
  handling.
- Repo-local task files: removes GitHub from the queue, but loses the existing
  board views.
- **Local integration**: keeps GitHub Issues for visibility while making Ralph's
  successful issue pass self-contained.

## Consequences

Ralph must be conservative around git drift. Trunk delivery integrates against
latest `origin/main` only after selected QA and any required **Issue completion
review** pass. Gitflow delivery keeps `origin/dev` current with `origin/main`
before issue branches are created. That branch sync is a
pre-claim drain precondition: merge conflicts or stale branch-sync worktrees
stop the drain with manifest recovery guidance instead of cascading unrelated
issue failures. Ralph then rebases and reruns selected QA if the **Integration
target** moves before squash-merging, then reruns any required **Issue
completion review** before updating the target. Exploratory delivery fails
clearly if the durable **Exploratory branch** already exists,
otherwise creates `agent/exploratory/issue-N-slug` from `origin/main` and
pushes that validated branch for human review without running **Local
integration**; any required **Issue completion review** also passes before that
handoff. If a
target branch is pushed but issue metadata cannot be updated, the drain stops
because code and board state may no longer agree.
Operators inspect that run with
`--inspect-run` and recover metadata with `--recover-run` only after Ralph
verifies the recorded **Local integration** commit or Exploratory handoff commit
is reachable from the expected **Integration target**. Ralph also blocks live
implementation and **Promotion** runs on a dirty root worktree unless the
operator passes `--allow-dirty-worktree`; dry-run remains available for queue
inspection without issue or branch mutation. Failed implementation runs that
passed QA and **Issue completion review** before any recorded
`integration_commit` or **Integration target** push may use Ralph-owned
pre-push requeue recovery instead: Ralph preserves a local implementation
backup ref, cleans only manifest-derived Ralph worktrees and issue branches,
comments the evidence, and returns the issue to `ready-for-agent` without
creating or pushing a **Local integration** commit. After a successful issue
**Local integration** or Exploratory handoff, **Ready issue refresh** reconciles
follow-on GitHub Issues before Ralph schedules further issue attempts so the
queue reflects the updated **Integration target**. Parallel drain may still let
already active Exploratory workers finish. Ralph records the first step as a
read-only analysis artifact, then its outer loop applies validated GitHub Issue
metadata updates only. Refresh mutation failures stop the drain with
per-candidate manifest evidence and recovery guidance, without rolling back the
integrated commit or rewriting the **Integration target**.
Checkpointed Operator drains also run a targeted **Integration target** baseline
guard before new claims in high-risk states, using the Ralph loop **Commit
check** on a detached target worktree. That guard catches target-branch health
failures before unrelated issue work is claimed; it does not change the
issue-specific QA, **Local integration**, or Promotion **Push check**
responsibilities described by this ADR.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `scripts/ralph.py`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
  - `docs/agents/ralph-loop.md`
  - `CONTEXT.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `verify decision text matches Ralph workflow and canonical terms`
