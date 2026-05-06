# Ralph Uses Local Integration After Issue QA

Ralph keeps GitHub Issues as the visible board and queue, but successful
implementation work is integrated locally instead of opening a GitHub PR. This
keeps the board useful for planning while making the AFK loop responsible for
the whole validated path: squash-merge onto latest `origin/main`, push `main`,
comment completion evidence, and close the issue.

ADR 0002 generalizes this trunk-only path with **Delivery modes**. The
trunk-style behavior described here remains the **Trunk delivery** path.
Gitflow delivery uses the same post-QA **Local integration** mechanism against
`dev`; Exploratory delivery publishes a durable handoff branch without a
**Local integration** squash merge.

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
latest `origin/main`. Gitflow delivery keeps `origin/dev` current with
`origin/main` before issue branches are created, then rebases and reruns selected
QA if the **Integration target** moves before squash-merging. Exploratory
delivery fails clearly if the durable review branch already exists, otherwise
creates `agent/exploratory/issue-N-slug` from `origin/main` and pushes that
validated branch for human review without running **Local integration**. If a
target branch is pushed but issue metadata cannot be updated, the drain stops
because code and board state may no longer agree.
Operators inspect that run with
`--inspect-run` and recover metadata with `--recover-run` only after Ralph
verifies the recorded **Local integration** commit or Exploratory handoff commit
is reachable from the expected **Integration target**. Ralph also blocks live
implementation and **Promotion** runs on a dirty root worktree unless the
operator passes `--allow-dirty-worktree`; dry-run remains available for queue
inspection without issue or branch mutation. After a successful issue **Local
integration** or Exploratory handoff, **Ready issue refresh** reconciles
follow-on GitHub Issues before the next ready issue claim so the queue reflects
the updated **Integration target**. Ralph records the first step as a read-only
analysis artifact, then its outer loop applies validated GitHub Issue metadata
updates only. Refresh mutation failures stop the drain with per-candidate
manifest evidence and recovery guidance, without rolling back the integrated
commit or rewriting the **Integration target**.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `scripts/ralph.py`
  - `docs/agents/ralph-loop.md`
  - `CONTEXT.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify decision text matches Ralph workflow and canonical terms`
