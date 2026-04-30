# Issue Tracker

This repo tracks work in GitHub Issues for
`Chr1sC0de/energy-market-delta-lake`.

Agent workflows should use the `gh` CLI for issue reads and writes. Local `gh`
auth must pass before running triage or the Ralph loop:

```bash
gh auth status
```

The Ralph loop uses GitHub Issues as its queue and opens draft PRs back to the
same repository.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `scripts/ralph.py`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify repo names, commands, labels, and links`
