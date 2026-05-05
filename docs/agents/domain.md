# Domain Docs

This repo has a single domain context at the root:

- `CONTEXT.md`

There is no `CONTEXT-MAP.md` and no per-Subproject context map. Agent workflows
should read the root context first and use its canonical language across the
repo, especially **Subproject**, **Test lane**, **Fast check**, **Commit check**,
**Push check**, **Local integration**, **Delivery mode**, **Integration target**,
**Sandboxed issue access**, **Operator workflow**, **Promotion**, and
**Post-promotion review**.

Repo-wide ADRs live in `docs/adr/`. Create ADRs only when a decision is hard to
reverse, surprising without context, and the result of a real trade-off.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `AGENTS.md`
  - `OPERATOR.md`
  - `docs/agents/README.md`
  - `docs/adr/0001-ralph-local-integration.md`
  - `docs/adr/0002-ralph-delivery-modes.md`
  - `docs/adr/0004-ralph-sandboxed-issue-access.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify context layout, links, canonical terms, and ADR path references`
