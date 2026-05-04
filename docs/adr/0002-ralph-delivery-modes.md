# Ralph Uses Delivery Modes For Issue Integration

Ralph now supports two **Delivery modes** instead of a single trunk-only success
path. **Gitflow delivery** is the default: Ralph keeps `dev` current with
`main`, integrates validated issue work to `dev`, leaves the issue open with
`agent-integrated`, and later **Promotion** merges reviewed `dev` work to `main`
while closing verified issues. **Trunk delivery** remains available for small
low-risk docs, tests, tooling, or script changes that can integrate directly to
`main` and close immediately.

## Consequences

Ralph issue triage now owns delivery-label hygiene. If both delivery labels are
present, Ralph normalizes to `delivery-gitflow` before implementation. Promotion
must verify the recorded Gitflow integration commit before closing an
`agent-integrated` issue, because branch promotion merges code but does not
reliably close GitHub Issues on its own.

Gitflow branch hygiene is part of the Delivery mode contract: before default
Gitflow integration, Ralph merges `origin/main` into `origin/dev` if `dev` is
behind `main`; after successful Promotion, Ralph fast-forwards `dev` to the
promotion commit. Recovery also follows the issue **Delivery mode**: Trunk
delivery reconciles `agent-merged` and issue closure, while Gitflow delivery
reconciles `agent-integrated` and leaves the issue open for **Promotion**.
When a **Promotion** range includes AEMO ETL **Subproject** files, the AEMO ETL
**End-to-end test** gate runs before any merge, push, branch sync, metadata
update, or issue closure so `main` is not updated before that local stack passes.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `scripts/ralph.py`
  - `docs/agent-issue-loop.md`
  - `CONTEXT.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify decision text matches Ralph workflow and canonical terms`
