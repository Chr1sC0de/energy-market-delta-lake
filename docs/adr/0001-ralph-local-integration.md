# Ralph Uses Local Integration After Issue QA

Ralph keeps GitHub Issues as the visible board and queue, but successful
implementation work is integrated locally instead of opening a GitHub PR. This
keeps the board useful for planning while making the AFK loop responsible for
the whole validated path: squash-merge onto latest `origin/main`, push `main`,
comment completion evidence, and close the issue.

ADR 0002 generalizes this trunk-only path with **Delivery modes**. The
trunk-style behavior described here remains the **Trunk delivery** path.

## Considered options

- GitHub PRs as the success gate: preserves a familiar review object, but keeps
  merging outside the loop and leaves completed agent work waiting on PR
  handling.
- Repo-local task files: removes GitHub from the queue, but loses the existing
  board views.
- **Local integration**: keeps GitHub Issues for visibility while making Ralph's
  successful issue pass self-contained.

## Consequences

Ralph must be conservative around git drift. If `origin/main` moves after the
issue worktree is created, Ralph rebases the issue branch and reruns selected QA
before squash-merging. If `main` is pushed but issue metadata cannot be updated,
the drain stops because code and board state may no longer agree.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `scripts/ralph.py`
  - `docs/agent-issue-loop.md`
  - `CONTEXT.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify decision text matches Ralph workflow and canonical terms`
