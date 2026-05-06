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
receive issue reads and writes; **Post-promotion review** receives read-only
issue commands and drafts only actionable follow-up issues in its Markdown
report without creating them automatically. Git push auth is separate; **Local
integration**, Exploratory handoff, **Integration target** pushes, and
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
states the human judgment the durable review branch needs. Missing
`## Review focus` is a malformed Exploratory delivery contract; Ralph marks the
issue `agent-failed` with evidence before creating an implementation worktree
or publishing an Exploratory handoff.

`## Current context` is optional. **Ready issue refresh** may add or update it,
but existing `ready-for-agent` issues do not need that section to stay ready.
Refreshed issues that remain `ready-for-agent` must still contain the three
required sections above, plus `## Review focus` for `delivery-exploratory`.

Ralph implementation prompts treat the issue body as the primary contract. When
recent Ready issue refresh comments exist, Ralph appends only the latest five
comments with the Ready issue refresh audit prefix in a separate prompt section
after the body; normal comments and triage comments are not included.

Runtime labels such as `agent-running`, `agent-integrated`, `agent-merged`,
`agent-failed`, and `agent-reviewing` block repeat implementation and automated
triage reconsideration. In particular, `agent-reviewing` means **Exploratory
delivery** has already published a durable review branch and the issue is
waiting for human review.

After a successful drain-mode **Local integration** or Exploratory handoff,
Ralph computes **Ready issue refresh** candidates from open issues within
`--issue-limit`. The candidate scan keeps unblocked `ready-for-agent` issues in
queue order, excludes issues with runtime stop labels, and treats the issue that
was just completed as a satisfied blocker for candidate selection even when
Gitflow leaves it open with `agent-integrated` until **Promotion** or
Exploratory delivery leaves it open with `agent-reviewing` for human review.

Use [ralph-loop.md](ralph-loop.md) for Ralph internals, including
**Delivery mode**, **Local integration**, **Integration target**, **Promotion**,
**Ready issue refresh**, **Post-promotion review**, run manifests, QA
selection, and recovery behavior.
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
  - `.agents/skills/ralph-issue-refresh/SKILL.md`
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
