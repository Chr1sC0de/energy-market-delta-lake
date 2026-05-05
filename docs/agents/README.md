# Agent Workflow Map

Use this page as the agent documentation map. The imperative policy lives in
[AGENTS.md](../../AGENTS.md); this page routes to supporting agent docs.

## Workflow entrypoints

- Agent policy:
  [AGENTS.md](../../AGENTS.md)
- Human **Operator workflow**:
  [OPERATOR.md](../../OPERATOR.md)
- Canonical language:
  [CONTEXT.md](../../CONTEXT.md)
- Documentation sync policy:
  [docs/repository/documentation-sync.md](../repository/documentation-sync.md)

## Ralph and issue work

- Ralph internals, **Local integration**, **Delivery mode**, **Integration
  target**, **Ready issue refresh**, **Promotion**, and
  **Post-promotion review**:
  [ralph-loop.md](ralph-loop.md)
- GitHub Issue queue rules:
  [issue-tracker.md](issue-tracker.md)
- Triage and Ralph label vocabulary:
  [triage-labels.md](triage-labels.md)
- Domain doc layout:
  [domain.md](domain.md)

## Skills

- Use `$ralph-curate` to review open GitHub Issues against the current branch
  and propose stale, satisfied, blocked, or mislabeled issue updates.
- Use `$ralph-issue-refresh` to reconcile ready issues after **Local
  integration** and before the next ready issue claim.
- Use `$ralph-triage` to prepare GitHub Issues for drain.
- Use `$ralph-loop` to drain ready issues, inspect failures, and run
  **Promotion**.
- Use `$grill-with-docs`, `$to-prd`, and `$to-issues` before Ralph when the
  work needs shaping or issue creation.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `OPERATOR.md`
  - `CONTEXT.md`
  - `.agents/skills/ralph-curate/SKILL.md`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `.agents/skills/ralph-issue-refresh/SKILL.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `docs/agents/ralph-loop.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
  - `docs/agents/domain.md`
  - `docs/repository/documentation-sync.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify agent workflow map links resolve`
