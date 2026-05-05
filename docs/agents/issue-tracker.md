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
commands. Implementation and triage passes may receive issue reads and writes;
**Post-promotion review** receives read-only issue commands and drafts any
follow-up issues in its Markdown report. Git push auth is separate; **Local
integration**, **Integration target** pushes, and **Promotion** stay outside
the sandbox.

## Queue contract

Use [triage-labels.md](triage-labels.md) for category, state, runtime, and
**Delivery mode** labels. A ready implementation issue must have
`ready-for-agent`, a category label, at most one **Delivery mode** label, and
these sections:

- `## What to build`
- `## Acceptance criteria`
- `## Blocked by`

Use [ralph-loop.md](ralph-loop.md) for Ralph internals, including
**Delivery mode**, **Local integration**, **Integration target**, **Promotion**,
**Post-promotion review**, run manifests, QA selection, and recovery behavior.
Use [OPERATOR.md](../../OPERATOR.md) for the human **Operator workflow**.
Use `$ralph-curate` when existing open issues need to be compared with the
current branch before changing bodies, labels, blockers, or closure state.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `OPERATOR.md`
  - `.agents/skills/ralph-curate/SKILL.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `docs/agents/README.md`
  - `docs/agents/ralph-loop.md`
  - `docs/agents/triage-labels.md`
  - `scripts/ralph.py`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify repo names, commands, labels, and links`
