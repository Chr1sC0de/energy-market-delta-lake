---
name: ralph-loop
description: >-
  Operate the repo-local Ralph GitHub Issue loop, including Gitflow/trunk
  Delivery mode selection, failure inspection, and Promotion. Use when running
  Ralph, debugging Ralph results, choosing delivery labels, or promoting dev to
  main.
---

# Ralph Loop

Use this skill for operational work around `scripts/ralph.py`. The script is the
source of truth; this skill is a compact runbook for agents.

## Read First

- Read `CONTEXT.md` for canonical terms: **Delivery mode**, **Integration target**,
  **Local integration**, and **Promotion**.
- Read `docs/agents/ralph-loop.md` before changing workflow behavior.
- Use GitHub Issues as the queue. Do not invent local task files.
- Use `$ralph-triage` to prepare issues before drain; this skill runs and
  inspects the loop after issues are ready.

## Delivery Modes

- Default to **Gitflow delivery**: `delivery-gitflow`, integrate to `dev`, mark
  `agent-integrated`, leave the issue open.
- Use **Trunk delivery** only for small docs, tests, tooling, or script changes:
  `delivery-trunk`, integrate to `main`, mark `agent-merged`, close the issue.
- Avoid trunk for runtime behavior, infrastructure, Dagster, S3, LocalStack,
  cross-**Subproject** work, broad refactors, or unclear scope.
- If both delivery labels exist, keep `delivery-gitflow` and remove
  `delivery-trunk`.

## Commands

Use high-level requests when invoking this skill:

- `$ralph-loop bootstrap labels`
- `$ralph-loop dry-run drain`
- `$ralph-loop drain`
- `$ralph-loop drain trunk`
- `$ralph-loop issue 25`
- `$ralph-loop promote`
- `$ralph-loop inspect failure`

The backing commands are:

```bash
python3 scripts/ralph.py --bootstrap-labels
python3 scripts/ralph.py --drain --dry-run
python3 scripts/ralph.py --drain
python3 scripts/ralph.py --drain --delivery-mode trunk
python3 scripts/ralph.py --issue 25
python3 scripts/ralph.py --promote
```

Live `--issue`, `--drain`, and `--promote` runs require a clean root worktree.
Ralph checks `git status --porcelain` before claiming issues, creating
worktrees, running **Local integration**, or pushing an **Integration target**.
`--dry-run` stays usable from a dirty root worktree. Use
`--allow-dirty-worktree` only when the operator explicitly accepts
dirty-worktree operation.

Spawned Codex subprocesses get **Sandboxed issue access** by default. Refresh
local GitHub API auth with `gh auth login -h github.com --git-protocol ssh` or
export `GH_TOKEN`; Ralph injects `GH_TOKEN` into the sandbox and wraps `gh` so
only issue metadata commands are available. Git push auth and **Local
integration** remain in Ralph's outer loop.

Plain `--drain` stops after 10 implementation attempts by default. Use
`--max-issues 0` only for explicit unlimited drain mode.

Use `--target-branch <branch>` only when the maintainer explicitly wants a
non-default **Integration target**.

## Failure Inspection

1. Read the issue result comment and run log path.
2. Inspect `.ralph/runs/...` logs for the failing command.
3. Keep failed worktrees unless the maintainer asks for cleanup.
4. Fix code only in the relevant repo worktree, then rerun the relevant Ralph or
   QA command.

## Promotion

Use `$ralph-loop promote` after reviewing `dev`. Ralph runs the aggregate
**Push check**, merges `dev` into `main`, then closes only `agent-integrated`
issues whose recorded integration commit is verified in the promoted range.
