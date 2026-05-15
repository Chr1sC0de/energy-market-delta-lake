# Domain Docs

This repo has a single domain context at the root:

- `CONTEXT.md`

There is no `CONTEXT-MAP.md` and no per-Subproject context map. Agent workflows
should read the root context first and use its canonical language across the
repo, especially **Subproject**, **Test lane**, **Fast check**, **Commit check**,
**Push check**, **Local integration**, **Delivery mode**, **Integration target**,
**Exploratory delivery**, **Exploratory branch**, **Sandboxed issue access**,
**Full-access implementation pass**, **Issue completion review**,
**Ready issue refresh**, **Operator workflow**,
**Documentation sync**, **Agent skill**, **Issue context assessor**,
**Exploratory acceptance review**, **Promotion**, **Post-promotion review**,
**Post-Promotion deployment classification**, and
**AWS/Pulumi credential boundary**.

Repo-wide ADRs live in `docs/adr/`. Create ADRs only when a decision is hard to
reverse, surprising without context, and the result of a real trade-off.
The **Issue context assessor** replacement is an in-development `$shape-issues`
workflow change, so it does not require an ADR.

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
  - `docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md`
  - `docs/adr/0007-ralph-full-access-implementation-pass.md`
  - `docs/adr/0009-ralph-post-promotion-deployment-classification.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `verify context layout, links, canonical terms, and ADR path references`
