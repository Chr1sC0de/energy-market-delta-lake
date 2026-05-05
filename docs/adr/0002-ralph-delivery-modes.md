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
After each successful issue **Local integration**, **Ready issue refresh**
reconciles the open issue queue before the next ready issue claim; this is
separate from the later **Post-promotion review** path.
When a **Promotion** range includes non-doc runtime files in the AEMO ETL
**Subproject**, the AEMO ETL **End-to-end test** gate runs from the same
isolated source worktree as the aggregate **Push check**, before any merge,
push, branch sync, metadata update, or issue closure, so `main` is not updated
before the fetched source revision passes. Successful Promotions with changed
files then run **Post-promotion review** by default; Ralph saves the read-only
review report as `post-promotion-review.md`, prints it to the terminal, and
records the artifact path in the **Promotion** manifest. Operators must pass
`--skip-post-promotion-review` for an explicit no-review Promotion, and
no-change Promotions record the review state as `skipped_no_changes`.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `scripts/ralph.py`
  - `docs/agents/ralph-loop.md`
  - `CONTEXT.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify decision text matches Ralph workflow and canonical terms`
