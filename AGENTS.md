# AGENTS.md

## Code change

- Run relevant QA. Use `prek` where it fits.
- Sync maintained docs with impl/config changes.

## Doc sync

- Scope: `README.md`, `docs/*.md`, maintained `backend-services/**/*.md`, `infrastructure/aws-pulumi/**/*.md`, `backend-services/dagster-user/aemo-etl/**/*.md`
- Out: `specs/`
- Each maintained doc ends with `## Sync metadata`
- Required keys: `sync.owner`, `sync.sources`, `sync.scope`, `sync.qa`
- `sync.sources` rules: repo-relative, literal path, one path per line, only files likely to force doc update

## Flow

1. `git diff --name-only`
2. `rg` changed path in maintained docs
3. update every doc whose `sync.sources` matches
4. run doc QA

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
