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
- **Documentation sync** policy:
  [docs/repository/documentation-sync.md](../repository/documentation-sync.md)
- Marimo **Dashboard standard** for curated dashboard work:
  [backend-services/marimo/docs/dashboard-standard.md](../../backend-services/marimo/docs/dashboard-standard.md)

## Ralph and issue work

- Ralph internals, **Local integration**, **Delivery mode**, **Integration
  target**, **Full-access implementation pass**, **Issue completion review**,
  **Ready issue refresh**, **Exploratory acceptance review**, **Promotion**, and
  **Post-promotion review**, including **Post-Promotion deployment
  classification**, source-table archive replay recovery, deploy-repair issue
  creation after failed checkpointed deployment evidence, and checkpointed
  Operator runs:
  [ralph-loop.md](ralph-loop.md)
- GitHub Issue queue rules:
  [issue-tracker.md](issue-tracker.md)
- Triage and Ralph label vocabulary:
  [triage-labels.md](triage-labels.md)
- Domain doc layout:
  [domain.md](domain.md)
- **Gas market knowledge base** language and architecture:
  ADR [0010](../adr/0010-gas-market-knowledge-base.md) and the
  [Subproject README](../../tools/gas-market-knowledge-base/README.md).

## Skills

- **Agent skills** are reusable local workflow instruction bundles invoked as
  `$skill-name`.
- Use `$repo-knowledge-base` for repo-owned gas-market corpus questions,
  generated bronze/silver/gold artifact lookup, generated chunk citation, and
  cited gold **Market context** writing or review:
  [SKILL.md](../../.agents/skills/repo-knowledge-base/SKILL.md). Factual
  market claims must cite generated chunk evidence with `chunk_id` and source
  hash details, and generated corpus Markdown stays outside maintained
  **Documentation sync** router docs.
- Use `$shape-issues` before `$ralph-triage` to turn shaped plans into
  tracer-bullet issue drafts with context anchors, QA plans, **Issue context
  assessor** evidence, and stiffness scoring. The gate writes `report.md`,
  `report.json`, `issue-drafts.md`, and per-draft `issue-drafts/*.md` review
  files before publication. Version 2 may publish explicitly confirmed gated
  outputs as `needs-triage` issues only. Follow-up verbs after a
  `$shape-issues` plan continue issue-draft execution; direct implementation
  requires `$ralph-loop` or an explicit named GitHub Issue request.
  Fixture-gated reports can preview with `--dry-run`, but non-dry-run
  publication requires `--allow-fixture-publish`, preflights `gh`
  authentication and repository access, and records fixture provenance.
  Codex-owned live gates use `run_live_shape_issue_gate.py`; Codex-owned
  publication can use `--publish-backend auto` to fall back to a create-only
  GitHub connector plan when local `gh` auth is unavailable.
- Use `$ralph-curate` to review open GitHub Issues against the current branch
  and propose stale, satisfied, blocked, or mislabeled issue updates.
- Use `$ralph-issue-refresh` to reconcile ready issues after **Local
  integration**, Exploratory handoff, or successful **Promotion** verified issue
  closure; it must not accept or reject `agent-reviewing` work.
- Use `$ralph-triage` to prepare GitHub Issues for drain with category, state,
  and **Delivery mode** labels, including `delivery-exploratory` only when
  `## Review focus` explains the needed **Exploratory branch** review.
- Use `$ralph-loop` to drain ready issues, launch checkpointed Operator runs,
  publish **Exploratory branches** for Exploratory handoff, inspect failures,
  handle **Issue completion review** failures, handle **Exploratory acceptance
  review**, and run **Promotion**. Human review accepts Exploratory work by
  moving it to `agent-integrated`, or rejects it by moving it to
  `ready-for-human`.
  The backing CLI is packaged in
  [tools/ralph-loop](../../tools/ralph-loop/README.md), while the compatibility
  command remains `python3 scripts/ralph.py`.
- Use `$grill-with-docs`, `$to-prd`, and `$shape-issues` before Ralph when the
  work needs shaping or issue creation.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `OPERATOR.md`
  - `CONTEXT.md`
  - `.agents/skills/shape-issues/SKILL.md`
  - `.agents/skills/shape-issues/scripts/shape_issue_gate.py`
  - `.agents/skills/shape-issues/scripts/codex_context_assessor.py`
  - `.agents/skills/shape-issues/scripts/run_live_shape_issue_gate.py`
  - `.agents/skills/shape-issues/scripts/publish_shape_issues.py`
  - `.agents/skills/ralph-curate/SKILL.md`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `.agents/skills/ralph-issue-refresh/SKILL.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `.agents/skills/repo-knowledge-base/SKILL.md`
  - `tools/ralph-loop/README.md`
  - `tools/gas-market-knowledge-base/README.md`
  - `backend-services/marimo/docs/dashboard-standard.md`
  - `docs/agents/ralph-loop.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
  - `docs/agents/domain.md`
  - `docs/repository/documentation-sync.md`
  - `docs/adr/0007-ralph-full-access-implementation-pass.md`
  - `docs/adr/0003-bounded-current-state-bronze-source-tables.md`
  - `docs/adr/0009-ralph-post-promotion-deployment-classification.md`
  - `docs/adr/0010-gas-market-knowledge-base.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `verify agent workflow map links resolve`
