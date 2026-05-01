# AGENTS.md

## Language

- Use the canonical repo terms in `CONTEXT.md`, especially **Subproject**,
  **Test lane**, **Fast check**, **Commit check**, **Push check**, and
  **Local integration**, **Delivery mode**, **Integration target**, and
  **Promotion**.
- Do not use "submodule" for repo projects. There are no Git submodules here.

## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues for `Chr1sC0de/energy-market-delta-lake`.
Ralph uses those issues as the board and queue, then performs successful code
changes through **Local integration**. **Trunk delivery** closes issues after
integration to `main`; **Gitflow delivery** closes them after **Promotion** from
`dev` to `main`. See `docs/agents/issue-tracker.md`.

### Ralph loop

Use the repo-local `ralph-loop` skill for Ralph operation, failure inspection,
**Delivery mode** rules, and **Promotion**.

Use the repo-local `ralph-triage` skill to prepare GitHub Issues for Ralph
drain. Triage sets category, state, and **Delivery mode** labels before
`ralph-loop` drains ready work.

### Triage labels

Use the default triage label vocabulary plus Ralph runtime labels. See
`docs/agents/triage-labels.md`.

### Domain docs

This repo uses a single root `CONTEXT.md` for canonical language. See
`docs/agents/domain.md`.

## Code change

- Work from the owning **Subproject** directory when running project-local
  commands.
- Run relevant QA for the changed behavior and **Test lane**. Use `git add` and
  `prek` where it fits.
- Sync maintained docs with impl/config changes.

## Subproject QA

- Prefer a **Subproject** Makefile or documented command surface for lane-level
  validation when one exists.
- For `backend-services/dagster-user/aemo-etl`, use:
  - `make unit-test` for **Unit test** validation.
  - `make component-test` for **Component test** validation.
  - `make fast-test` for the ETL fast pytest target. This is not the full
    repo **Fast check** because it does not include static checks.
  - `make integration-test` for local **Integration test** validation.
  - `make duplicate-check` for the pylint duplicate-code check.
  - `make run-prek` for the ETL **Commit check** surface.
- Direct `uv run pytest path::test` commands are fine for narrowed debugging.
  Use the Makefile targets again before treating a lane as validated.
- Run ETL **Integration tests** when changes touch LocalStack, S3, Dagster
  integration boundaries, or when doing **Push check** validation. Do not run
  them by default for pure unit-scoped changes.
- Use `make run-prek` for isolated `aemo-etl` changes. Use root `prek run -a`
  for root docs/config changes or cross-subproject changes.

## Doc sync

- Scope: `README.md`, `docs/**/*.md`, maintained `backend-services/**/*.md`, `infrastructure/aws-pulumi/**/*.md`, `backend-services/dagster-user/aemo-etl/**/*.md`
- Out: `specs/`
- Each maintained doc ends with `## Sync metadata`
- Required keys: `sync.owner`, `sync.sources`, `sync.scope`, `sync.qa`
- `sync.sources` rules: repo-relative, literal path, one path per line, only files likely to force doc update
- Changes to this file must check `docs/documentation-sync.md` because that doc
  lists `AGENTS.md` in `sync.sources`.

## Flow

1. `git diff --name-only`
1. `rg` changed path in maintained docs
1. update every doc whose `sync.sources` matches
1. run doc QA

Commands:

```bash
git diff --name-only
rg -n "<changed-file-path>" README.md docs backend-services infrastructure
rg -n "sync.sources|sync.scope|sync.qa" README.md docs backend-services infrastructure
```

## QA

- verify `sync.sources` paths exist
- verify links/anchors resolve
- verify diagrams, commands, env vars, ports, paths, names match impl
- verify TOC matches headings
- no doc match: add coverage or confirm intentionally undocumented
- doc match, no text change: record that decision in review
