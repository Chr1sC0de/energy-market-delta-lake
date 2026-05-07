# Documentation Sync Workflow

This page owns the maintained-doc contract, sync metadata rules, and doc QA
ratchets. It keeps documentation updates tied to the files that can make the
docs stale.

## Table of contents

- [Maintained docs](#maintained-docs)
- [Explicit exclusions](#explicit-exclusions)
- [Sync metadata contract](#sync-metadata-contract)
- [Code-change workflow](#code-change-workflow)
- [Automated doc QA](#automated-doc-qa)
- [Documentation QA ratchets](#documentation-qa-ratchets)
- [Issue reconciliation](#issue-reconciliation)
- [Search commands](#search-commands)
- [Related docs](#related-docs)

## Maintained docs

The sync workflow applies to maintained Markdown files in these paths:

- `README.md`
- `OPERATOR.md`
- `docs/**/*.md`
- maintained `backend-services/**/*.md`
- `infrastructure/aws-pulumi/**/*.md`
- `backend-services/dagster-user/aemo-etl/**/*.md`

Each maintained doc must end with a visible `## Sync metadata` section.

## Explicit exclusions

Maintained-doc discovery intentionally excludes generated, vendored, cached, and
runtime-only paths:

- `.ralph/`
- `.shape-issues/`
- `.venv/`
- `.git/`
- `.mypy_cache/`
- `.pytest_cache/`
- `.ruff_cache/`
- `__pycache__/`
- `generated/`
- `vendor/`
- `specs/`

The removed legacy `specs/` tree stays out of scope. New maintained design or
migration docs should live under the maintained documentation paths above and
carry sync metadata.

## Sync metadata contract

Required keys:

- `sync.owner`
- `sync.sources`
- `sync.scope`
- `sync.qa`

Formatting rules:

- keep `sync.sources` as repo-relative literal paths
- put one source path on each line
- only list files whose changes are likely to require doc updates
- keep the section at the bottom of the file so reader-facing content stays
  first

## Code-change workflow

Use this flow after implementation changes:

1. Check the changed files with `git diff --name-only`.
2. Search the maintained docs for each changed path.
3. Update every doc whose `sync.sources` contains that path.
4. Run doc QA before commit.

If a changed code file has no matching docs, either add the missing coverage or
explicitly confirm that the file is intentionally undocumented.

If a matching doc does not need any wording changes, record that decision
during review instead of assuming the doc is still correct.

## Automated doc QA

The root unittest suite checks documentation invariants that are too important
to leave as review-only guidance:

- maintained-doc discovery honors the explicit exclusions above
- every maintained doc has required `## Sync metadata`
- every listed `sync.sources` path exists
- internal Markdown file links and anchors resolve
- `docs/README.md` covers the required human task and Subproject routes
- `docs/agents/README.md` covers the required agent workflow routes
- moved repo-level docs do not leave stale references to old paths

Run the automated doc QA with:

```bash
python3 -m unittest discover -s tests
```

The repository **Commit check** also runs Markdown, link, and staged
secret-scan tooling through:

```bash
prek run -a
```

## Documentation QA ratchets

The documentation QA ratchet is staged by **Subproject** and enforced through
the same `prek` command surfaces as code QA:

- The repo **Commit check** is `prek run -a` from the repository root. For a
  single **Subproject**, use that Subproject's documented **Commit check**
  command, such as `make run-prek` for `aemo-etl` or `prek run -a` from
  `infrastructure/aws-pulumi`. These **Commit check** surfaces are the local
  **Fast check** path: static checks plus **Unit tests** and **Component tests**,
  without containers, live network, or deployed cloud resources.
- The root **Commit check** includes the official Gitleaks `gitleaks` hook. It
  runs in staged pre-commit mode so newly staged secrets are blocked without
  requiring Docker or a preinstalled `gitleaks` binary.
- Ruff owns Python linting and formatting. A Python **Subproject** is under the
  Google-style docstring ratchet only when its `pyproject.toml` selects Ruff `D`
  rules and its hook config runs `ruff check`. The current ratchet covers
  `backend-services/authentication`, `backend-services/marimo`,
  `backend-services/dagster-user/aemo-etl`, and
  `infrastructure/aws-pulumi`, with each Subproject's pyproject defining its
  test, generated, schema-heavy, or entrypoint exclusions. AEMO ETL and AWS
  Pulumi also select Ruff `C901` with Ruff's default complexity threshold.
  `backend-services/dagster-core` is not currently on this ratchet.
- `shfmt` formats shell scripts.
- `shellcheck` checks shell correctness.
- `scripts/check_shell_script_headers.py` enforces shell documentation for
  executable shell scripts: a script with a shell shebang must have a human
  purpose/context comment block immediately after the shebang. Tool directives
  such as `shellcheck` or `shfmt` comments do not count as that human header.

Do not treat a future **Subproject** as covered by the ratchet until its own
hook and project config have been added and the maintained docs name those files
in `sync.sources`.

Most Python project hooks run through `uv run` inside the project that owns the
hook config. AWS Pulumi shell hooks, including `shfmt` and `shellcheck`, are
pinned in that Subproject's uv dev environment. The shared `backend-services`
shell lint hook pins `shellcheck-py` in its hook environment instead of relying
on the caller's `PATH`.

## Issue reconciliation

Issue #73 reconciles the related documentation and Ralph behavior issues this
way:

- #65: `OPERATOR.md` remains the human **Operator workflow** entrypoint, and
  `README.md`, `docs/README.md`, and `docs/agents/README.md` route operators to
  it instead of duplicating the full workflow.
- #66: `OPERATOR.md` remains under documentation sync through this page's
  maintained-doc scope and its own sync metadata.
- #59: docs-only AEMO ETL changes remain aligned with Ralph QA selection by
  keeping docs-only AEMO ETL paths on the root doc **Commit check** surface.
- #57, #58, #61, #62, #88, #89, #91, #92, #94, #95, and #108: current Ralph
  behavior for **Delivery mode**, **Local integration**, Exploratory handoff,
  **Exploratory branch** review state, **Promotion**, accepted Exploratory
  evidence closure, manual Gitflow recovery Promotion closure evidence,
  **Sandboxed issue access**, writable QA runtime paths, unverified
  **Promotion** commit review context, **Post-promotion review**, and validated
  follow-up creation remain owned by
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md), with the
  **Exploratory branch** automatic-Promotion boundary recorded in ADR
  [0005](../adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md).
- #68: [docs/agents/ralph-loop.md](../agents/ralph-loop.md) defines the
  **Ready issue refresh** contract, including the shared language, audit prefix,
  optional `## Current context`, stale issue handling, and completed closure
  rules.
- #69: Ralph computes bounded **Ready issue refresh** candidates after
  drain-mode **Local integration** or Exploratory handoff using open issues from
  the existing `--issue-limit` scan, with Gitflow, trunk, and Exploratory
  blocker satisfaction described in
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #90: Exploratory-ready issues require `## Review focus` before Ralph can
  publish an Exploratory handoff. The contract and triage expectations live in
  [docs/agents/issue-tracker.md](../agents/issue-tracker.md),
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md), and
  [docs/agents/triage-labels.md](../agents/triage-labels.md).
- #70: Ralph now records a read-only **Ready issue refresh** analysis artifact
  after drain-mode **Local integration** or Exploratory handoff. The artifact
  plans issue updates without mutating GitHub Issues, and
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md) owns the manifest,
  prompt, and failure-stop contract.
- #71: Ralph applies validated **Ready issue refresh** metadata mutations after
  the read-only analysis artifact. Drain mode refreshes by default,
  `--skip-ready-issue-refresh` disables that default, and targeted `--issue`
  runs require `--ready-issue-refresh`. Mutation uses only GitHub Issue metadata
  commands, records per-candidate manifest status, and stops the drain with
  recovery guidance on partial post-**Local integration** metadata failures.
- #127: Successful **Promotion** verified issue closures may trigger **Ready
  issue refresh** before the next ready issue claim. The checkpointed Operator
  loop enables post-Promotion refresh by default, direct `--promote` requires
  `--ready-issue-refresh`, and failures are warning-only because the Promotion
  commit and verified issue closures have already completed.
- #72: Ralph implementation prompts include bounded recent **Ready issue
  refresh** notes after the issue body while keeping the issue body as the
  primary implementation contract.
- #112: Ralph treats default Gitflow branch-sync conflicts and stale
  `agent-sync-main-into-dev` worktrees as drain-stopping pre-claim failures.
  The recovery contract, `branch_sync` manifest fields, and operator guidance
  live in [docs/agents/ralph-loop.md](../agents/ralph-loop.md), with the
  Delivery mode decision summarized in ADR
  [0002](../adr/0002-ralph-delivery-modes.md).
- #113: Ralph recovers implementation commit hooks that rewrite tracked files
  by staging the formatter-modified paths, rerunning the selected
  **Commit check** once, retrying the implementation commit, and recording
  `formatter_recovery` manifest evidence. Retry failures are classified as
  `formatter_rewrite_recovery_failure` with log paths and operator recovery
  guidance in [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #111: Ralph provides a checkpointed Operator run for repeated drain and
  **Promotion** cycles. The Codex-safe detached launch, compact
  `--operator-run-status` inspection, child manifest links, checkpoint names,
  cycle guard, and recovery guidance live in
  [OPERATOR.md](../../OPERATOR.md) and
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #115: Completed or stopped checkpointed Operator runs write
  `operator-run-rollup.md` and `operator-run-rollup.json` beside
  `operator-run.json`. The durable rollups summarize issue outcomes, manual
  recoveries, **Local integration** commits, **Promotion** commits, QA
  surfaces, **Post-promotion review** follow-ups, final queue state, and stop
  or failure reasons without reading child Codex JSONL.

## Search commands

```bash
git diff --name-only
rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure
rg -n "sync.sources|sync.scope|sync.qa" OPERATOR.md README.md docs backend-services infrastructure
```

These commands support the intended flow:

1. code change
2. `rg` search for docs synced to that code
3. doc update
4. QA

## Related docs

- [Repository documentation map](../README.md)
- [Repository architecture](architecture.md)
- [Repository workflow](workflow.md)
- [Ralph loop internals](../agents/ralph-loop.md)
- [Operator workflow](../../OPERATOR.md)
- [Agent policy](../../AGENTS.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `AGENTS.md`
  - `OPERATOR.md`
  - `README.md`
  - `docs/README.md`
  - `docs/agents/README.md`
  - `docs/agents/ralph-loop.md`
  - `docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md`
  - `tests/test_documentation_qa_ratchet.py`
  - `.pre-commit-config.yaml`
  - `backend-services/.pre-commit-config.yaml`
  - `backend-services/authentication/.pre-commit-config.yaml`
  - `backend-services/authentication/pyproject.toml`
  - `backend-services/dagster-core/pyproject.toml`
  - `backend-services/dagster-user/aemo-etl/.pre-commit-config.yaml`
  - `backend-services/dagster-user/aemo-etl/Makefile`
  - `backend-services/dagster-user/aemo-etl/pyproject.toml`
  - `backend-services/marimo/.pre-commit-config.yaml`
  - `backend-services/marimo/pyproject.toml`
  - `infrastructure/aws-pulumi/.pre-commit-config.yaml`
  - `infrastructure/aws-pulumi/pyproject.toml`
  - `scripts/check_shell_script_headers.py`
  - `scripts/ralph.py`
- `sync.scope`: `operations, tooling`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `prek run -a`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
