# Issue Tracker

This repo tracks work in GitHub Issues for
`Chr1sC0de/energy-market-delta-lake`.

Agent workflows should use the `gh` CLI for issue reads and writes. Local `gh`
auth must pass before running `$ralph-triage` or `$ralph-loop`:

```bash
gh auth status
```

Ralph provides **Sandboxed issue access** to spawned Codex subprocesses by
default. The sandbox receives a `GH_TOKEN` sourced from the parent environment
or local `gh auth`, and a wrapper limits `gh` to issue metadata commands. Git
push auth is separate; **Local integration**, **Integration target** pushes,
and **Promotion** stay outside the sandbox.
Spawned Codex subprocesses and Ralph-run QA commands also receive writable QA
runtime path variables. Operator-provided `DAGSTER_HOME`, `XDG_CACHE_HOME`, and
`UV_CACHE_DIR` values are preserved; unset or empty values fall back under
`/tmp/ralph-qa-runtime/<repo-slug>/<run-dir-name>/`.

The Ralph loop uses GitHub Issues as its queue and board. Successful
implementation work uses **Local integration** instead of GitHub PRs. In
default **Gitflow delivery**, Ralph squash-merges validated work to `dev`,
comments evidence, and leaves the issue open with `agent-integrated`. Ralph
syncs `main` into `dev` before Gitflow integration when needed, then later
closes verified issues during **Promotion** from `dev` to `main` and
fast-forwards `dev` to the promotion commit. In opt-in **Trunk delivery**, Ralph
integrates directly to `main`, comments evidence, and closes the issue. A plain
drain has a default budget of 10 implementation attempts; `--max-issues 0` is
the explicit unlimited drain mode. Live `--issue`, `--drain`, and `--promote`
runs require a clean root worktree before issue claim, worktree creation,
**Local integration**, or push; `--allow-dirty-worktree` is the explicit
override and `--dry-run` remains usable on dirty worktrees. When a **Promotion**
range includes AEMO ETL **Subproject** files, Ralph runs the aggregate
**Push check** and AEMO ETL **End-to-end test** gate from an isolated source
worktree fixed at the fetched source-branch revision, before any Promotion
merge, push, branch sync, metadata update, or issue closure. Each
implementation and **Promotion** run keeps `.ralph/runs/.../ralph-run.json`
updated with the issue, **Delivery mode**, **Integration target**, Promotion
source tree, QA, QA runtime environment, push, commit, and GitHub metadata
state for inspection and recovery. Use `--inspect-run <run_dir>` for a
read-only manifest summary. Use
`--recover-run <run_dir>` only after Ralph verifies the recorded **Local
integration** commit is reachable from the expected **Integration target**.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `scripts/ralph.py`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify repo names, commands, labels, and links`
