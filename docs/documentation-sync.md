# Documentation Sync Workflow

This page defines how maintained Markdown docs stay in sync with code and
configuration changes across the repo.

## Table of contents

- [Scope](#scope)
- [Sync metadata contract](#sync-metadata-contract)
- [Code-change workflow](#code-change-workflow)
- [QA checklist](#qa-checklist)
- [Search commands](#search-commands)
- [Related docs](#related-docs)

## Scope

The sync workflow applies to maintained documentation files:

- `README.md`
- `OPERATOR.md`
- `docs/**/*.md`
- maintained `backend-services/**/*.md`
- `infrastructure/aws-pulumi/**/*.md`
- `backend-services/dagster-user/aemo-etl/**/*.md`

The removed legacy `specs/` tree stays out of scope. New maintained design or
migration docs should live under the maintained documentation paths above and
carry sync metadata.

## Sync metadata contract

Each maintained doc ends with a visible `## Sync metadata` section.

Required keys:

- `sync.owner`
- `sync.sources`
- `sync.scope`
- `sync.qa`

Formatting rules:

- keep `sync.sources` as repo-relative literal paths
- put one source path on each line
- only list files whose changes are likely to require doc updates
- keep the section at the bottom of the file so the reader-facing content stays first

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

## QA checklist

For each doc updated because of implementation changes:

- verify every `sync.sources` path still exists
- verify links and anchors still resolve
- verify diagrams still match actual dependencies, ports, names, and directions
- verify commands, env vars, paths, and resource names still match implementation
- verify the table of contents still matches the headings

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

- [Repository architecture](architecture.md)
- [Repository workflow](workflow.md)
- [Agent issue loop](agent-issue-loop.md)
- [Repository root README](../README.md)
- [Operator workflow](../OPERATOR.md)
- [Agent policy](../AGENTS.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `AGENTS.md`
  - `OPERATOR.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
