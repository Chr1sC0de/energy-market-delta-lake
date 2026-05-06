# Ralph Uses Delivery Modes For Issue Integration

Ralph supports three **Delivery modes** instead of a single trunk-only success
path. **Gitflow delivery** is the default: Ralph keeps `dev` current with
`main`, integrates validated issue work to `dev`, leaves the issue open with
`agent-integrated`, and later **Promotion** merges reviewed `dev` work to `main`
while closing verified issues. **Trunk delivery** remains available for small
low-risk docs, tests, tooling, or script changes that can integrate directly to
`main` and close immediately. **Exploratory delivery** publishes validated work
to a durable review branch, marks the issue `agent-reviewing`, and leaves it
open for human review; ready Exploratory issues must state that review need in
`## Review focus`. Accepted Exploratory work can then be merged to `dev`, marked
`agent-integrated` with acceptance evidence, and closed by later **Promotion**.

## Consequences

Ralph issue triage now owns delivery-label hygiene. If `delivery-exploratory`
conflicts with Gitflow or trunk labels, Ralph normalizes to
`delivery-exploratory` before implementation because explicit review-branch
selection should win over shared **Integration target** defaults. Exploratory
selection must be backed by an explicit `## Review focus`; otherwise Ralph marks
the issue failed before creating a worktree or publishing a handoff branch. If
only Gitflow and trunk conflict, Ralph normalizes to `delivery-gitflow`.
Promotion must verify the recorded Gitflow integration commit or accepted
Exploratory commit before closing an `agent-integrated` issue, because branch
promotion merges code but does not reliably close GitHub Issues on its own.

Gitflow branch hygiene is part of the Delivery mode contract: before default
Gitflow integration, Ralph merges `origin/main` into `origin/dev` if `dev` is
behind `main`; after successful Promotion, Ralph fast-forwards `dev` to the
promotion commit. Exploratory branch hygiene is also part of the contract:
Ralph creates `agent/exploratory/issue-N-slug` from `origin/main`, refuses to
overwrite an existing remote handoff branch, and skips the **Local integration**
squash-merge path. Recovery follows the issue **Delivery mode**: Trunk delivery
reconciles `agent-merged` and issue closure, Gitflow delivery reconciles
`agent-integrated` and leaves the issue open for **Promotion**, and Exploratory
delivery reconciles `agent-reviewing` and leaves the issue open for review.
After each successful issue **Local integration** or Exploratory handoff,
**Ready issue refresh** reconciles the open issue queue before the next ready
issue claim; the current drain records a read-only analysis artifact with
planned issue updates before any later metadata mutation. This is separate from
the later **Post-promotion review** path.
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
Podman DNS during the gate. Direct launch paces batch submission against
`max_concurrent_runs` so queued runs remain within the Promotion guard budget.
The gate still requires every
materializable `gas_model` asset and final asset-check status to pass. Its e2e
run manifest records the selected scenario, launch mode, target group, target
asset count, selected upstream closure count, skipped live source asset keys,
dependency-wave count, run-batch count, and asset batch size so
**Post-promotion review** can verify the direct-launch coverage without
reconstructing it from logs.
Successful Promotions with changed files record a full source
commit inventory in the **Promotion** manifest,
including each promoted commit SHA and subject. Commits matching verified issue
`integrated_commit` values are treated as verified issue evidence commits, while
other commits remain visible as unverified **Promotion** commits in the manifest
and **Post-promotion review** prompt. Successful Promotions with changed files
run **Post-promotion review** by default after the `main` push, `dev` sync, and
verified issue metadata updates. Failed or partial Promotion attempts with
changed files also try **Post-promotion review** where a source or target
Promotion worktree is available. The read-only review report puts recovery and
consistency guidance before follow-up issue recommendations; review failures
are warning-only and do not change the original Promotion success or failure
status. Ralph saves successful review output as
`post-promotion-review.md`, prints it to the terminal, and records the artifact
path in the **Promotion** manifest.
After a successful **Promotion**, Ralph validates structured follow-up drafts
from the review artifact and creates GitHub Issues by default. Valid drafts
become `ready-for-agent`; invalid drafts become `needs-triage` with validation
evidence; duplicate source markers are skipped; and helper failures after
`main` is pushed are warning-only recovery items in the **Promotion** manifest.
Operators must pass `--skip-post-promotion-followups` to keep review but skip
automatic follow-up creation, or `--skip-post-promotion-review` for an explicit
no-review Promotion that also disables follow-up creation. No-change
Promotions record the review and follow-up states as `skipped_no_changes`.

Unverified **Promotion** commits are review context, not Promotion blockers.
This policy favors review context because **Promotion** has already validated
the full promoted source revision with the aggregate **Push check** and any
required Promotion gate, while issue closure remains limited to verified
Gitflow **Local integration** commits or accepted Exploratory commits. Requiring
explicit issue association for every unverified commit before **Promotion**
would turn review attribution into a pre-promotion gate and could delay
already-reviewed `dev` work without improving the **Integration target** safety
checks. Ralph therefore surfaces unverified commits in the **Promotion**
manifest and **Post-promotion review** prompt, but it does not require issue
association before **Promotion**, does not automatically create GitHub Issues
for those commits by themselves, and expects follow-up issues only when
**Post-promotion review** finds actionable work that satisfies the validated
follow-up contract or needs triage evidence.

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
