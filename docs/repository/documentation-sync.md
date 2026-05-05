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

The repository **Commit check** also runs Markdown and link tooling through:

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
- Ruff owns Python linting and formatting. A Python **Subproject** is under the
  Google-style docstring ratchet only when its `pyproject.toml` selects Ruff `D`
  rules and its hook config runs `ruff check`. The current ratchet covers
  `backend-services/authentication`, `backend-services/marimo`,
  `backend-services/dagster-user/aemo-etl`, and
  `infrastructure/aws-pulumi`, with each Subproject's pyproject defining its
  test, generated, schema-heavy, or entrypoint exclusions.
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
- #57, #58, and #61: current Ralph behavior for **Delivery mode**, **Local
  integration**, **Promotion**, **Sandboxed issue access**, writable QA runtime
  paths, and **Post-promotion review** remains owned by
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #68 through #72: [docs/agents/ralph-loop.md](../agents/ralph-loop.md)
  reserves space for future **Ready issue refresh** documentation without
  defining the concept before those implementation issues land.

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
