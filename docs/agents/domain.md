# Domain Docs

This repo has a single domain context at the root:

- `CONTEXT.md`

There is no `CONTEXT-MAP.md` and no per-Subproject context map. Agent workflows
should read the root context first and use its canonical language across the
repo, especially **Subproject**, **Test lane**, **Fast check**, **Commit check**,
**Push check**, **Local integration**, **Delivery mode**, **Integration target**,
**Exploratory delivery**, **Exploratory branch**, **Sandboxed issue access**,
**Full-access implementation pass**, **Issue completion review**,
**Review package**, **Security-sensitive change**, **Ready issue refresh**,
**Operator workflow**, **Documentation sync**, **Agent skill**, **Issue context
assessor**, **Exploratory acceptance review**, **Promotion**, **Post-promotion
review**, **Post-Promotion deployment classification**, **AWS/Pulumi credential
boundary**, **Gas market knowledge base**, **Market context**, **Dashboard
standard**, **Dashboard brief**, and **Dashboard intent**.

Repo-wide ADRs live in `docs/adr/`. Create ADRs only when a decision is hard to
reverse, surprising without context, and the result of a real trade-off.
The **Issue context assessor** replacement is an in-development `$shape-issues`
workflow change, so it does not require an ADR.
ADR [0011](../adr/0011-ralph-adaptive-vocabulary-and-verified-recovery.md)
records the adaptive Ralph vocabulary for Step size, Stiffness ratio, Residual
work, adaptive events, and verified-only post-push metadata recovery.
ADR [0013](../adr/0013-ralph-security-sensitive-issue-completion-review.md)
records why **Security-sensitive change** extends **Issue completion review**
instead of adding a separate security gate or hard-blocking scanner.
ADR [0010](../adr/0010-gas-market-knowledge-base.md) records the planned
`tools/gas-market-knowledge-base` **Subproject** and the first **Market
context** corpus architecture. The
[Subproject README](../../tools/gas-market-knowledge-base/README.md) owns the
bronze source manifest command, archive-prefix completeness audit, archive PDF
cache fetcher, Docling-based silver document extraction, Docling Hybrid silver
chunk generation, silver chunk index validation, gold **Market context**
citation validation, seed glossary rendering helpers, AEMO major publications
corpus fixture build, and external generated-artifact policy.

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
  - `docs/adr/0010-gas-market-knowledge-base.md`
  - `docs/adr/0011-ralph-adaptive-vocabulary-and-verified-recovery.md`
  - `docs/adr/0013-ralph-security-sensitive-issue-completion-review.md`
  - `tools/gas-market-knowledge-base/README.md`
  - `backend-services/marimo/docs/dashboard-standard.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `verify context layout, links, canonical terms, and ADR path references`
