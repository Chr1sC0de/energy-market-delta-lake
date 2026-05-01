# Issue Tracker

This repo tracks work in GitHub Issues for
`Chr1sC0de/energy-market-delta-lake`.

Agent workflows should use the `gh` CLI for issue reads and writes. Local `gh`
auth must pass before running `$ralph-triage` or `$ralph-loop`:

```bash
gh auth status
```

The Ralph loop uses GitHub Issues as its queue and board. Successful
implementation work uses **Local integration** instead of GitHub PRs. In
default **Gitflow delivery**, Ralph squash-merges validated work to `dev`,
comments evidence, and leaves the issue open with `agent-integrated`; Ralph
later closes verified issues during **Promotion** from `dev` to `main`. In
opt-in **Trunk delivery**, Ralph integrates directly to `main`, comments
evidence, and closes the issue.

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
