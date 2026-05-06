# Ralph Uses Delivery Modes For Issue Integration

Ralph supports three **Delivery modes** instead of a single trunk-only success
path. **Gitflow delivery** is the default: Ralph keeps `dev` current with
`main`, integrates validated issue work to `dev`, leaves the issue open with
`agent-integrated`, and later **Promotion** merges reviewed `dev` work to `main`
while closing verified issues. **Trunk delivery** remains available for small
low-risk docs, tests, tooling, or script changes that can integrate directly to
`main` and close immediately. **Exploratory delivery** publishes validated work
to a durable review branch, marks the issue `agent-reviewing`, and leaves it
open for human review.

## Consequences

Ralph issue triage now owns delivery-label hygiene. If `delivery-exploratory`
conflicts with Gitflow or trunk labels, Ralph normalizes to
`delivery-exploratory` before implementation because explicit review-branch
selection should win over shared **Integration target** defaults. If only
Gitflow and trunk conflict, Ralph normalizes to `delivery-gitflow`. Promotion
must verify the recorded Gitflow integration commit before closing an
`agent-integrated` issue, because branch promotion merges code but does not
reliably close GitHub Issues on its own.

Gitflow branch hygiene is part of the Delivery mode contract: before default
Gitflow integration, Ralph merges `origin/main` into `origin/dev` if `dev` is
behind `main`; after successful Promotion, Ralph fast-forwards `dev` to the
promotion commit. Recovery also follows the issue **Delivery mode**: Trunk
delivery reconciles `agent-merged` and issue closure, Gitflow delivery
reconciles `agent-integrated` and leaves the issue open for **Promotion**, and
Exploratory delivery reconciles `agent-reviewing` and leaves the issue open for
review.
After each successful issue **Local integration**, **Ready issue refresh**
reconciles the open issue queue before the next ready issue claim; this is
separate from the later **Post-promotion review** path.
When a **Promotion** range includes non-doc runtime files in the AEMO ETL
**Subproject**, the AEMO ETL **End-to-end test** gate runs from the same
isolated source worktree as the aggregate **Push check**, before any merge,
push, branch sync, metadata update, or issue closure, so `main` is not updated
before the fetched source revision passes. Ralph selects the
`promotion-gas-model` scenario for that gate: it may narrow incidental seed and
automation volume and launch explicit dependency-wave asset batches for the
`gas_model` upstream asset graph while skipping live
`bronze_nemweb_public_files_*` discovery/listing assets. Those batches run
in-process inside Podman run-worker containers to reduce LocalStack and Delta
Lake DynamoDB lock-table contention, and the generated stack uses fixed service
IPs for Postgres, LocalStack, and the AEMO ETL code server to avoid relying on
Podman DNS during the gate. The gate still requires every
materializable `gas_model` asset and final asset-check status to pass.
Successful Promotions with changed files record a full source
commit inventory in the **Promotion** manifest,
including each promoted commit SHA and subject. Commits matching verified issue
`integrated_commit` values are classified as verified **Local integration**
commits, while other commits remain visible as unverified **Promotion** commits
in the manifest and **Post-promotion review** prompt. Successful Promotions
with changed files then run **Post-promotion review** by default; Ralph saves
the read-only review report as `post-promotion-review.md`, prints it to the
terminal, and records the artifact path in the **Promotion** manifest.
Operators must pass `--skip-post-promotion-review` for an explicit no-review
Promotion, and no-change Promotions record the review state as
`skipped_no_changes`.

Unverified **Promotion** commits are review context, not Promotion blockers.
This policy favors review context because **Promotion** has already validated
the full promoted source revision with the aggregate **Push check** and any
required Promotion gate, while issue closure remains limited to verified
Gitflow **Local integration** commits. Requiring explicit issue association for
every unverified commit before **Promotion** would turn review attribution into
a pre-promotion gate and could delay already-reviewed `dev` work without
improving the **Integration target** safety checks. Ralph therefore surfaces
unverified commits in the **Promotion** manifest and **Post-promotion review**
prompt, but it does not require issue association before **Promotion**, does not
automatically create GitHub Issues for those commits, and expects follow-up
issues only when **Post-promotion review** finds actionable work.

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
