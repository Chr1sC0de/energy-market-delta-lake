# Triage Labels

The `ralph-triage` skill uses canonical roles and this repo maps those roles
directly to GitHub label strings.

## Category labels

- `bug`: something is broken.
- `enhancement`: new feature or improvement.

## State labels

- `needs-triage`: maintainer needs to evaluate.
- `needs-info`: waiting on reporter information.
- `ready-for-agent`: fully specified and ready for an AFK agent.
- `ready-for-human`: needs human implementation.
- `wontfix`: will not be actioned.

Every triaged issue should carry exactly one category label and one state label.
If state labels conflict, stop and ask the maintainer before making further
changes.

## Ralph runtime labels

Ralph owns these labels while processing the issue queue:

- `agent-running`: Ralph has claimed an implementation issue.
- `agent-failed`: Ralph failed after retry and left logs for inspection.
- `agent-merged`: Ralph pushed **Local integration** and closed the issue.
- `agent-integrated`: Ralph integrated Gitflow work to `dev`, manual Gitflow
  recovery evidence records a recovered `dev` commit, or accepted Exploratory
  work was merged to `dev`; the issue waits for **Promotion** to `main`.
- `agent-reviewing`: Ralph published exploratory work to a durable
  **Exploratory branch**; the issue waits for human review.

Runtime labels are not triage state labels. `ready-for-agent` remains the queue
selection label for implementation. **Ready issue refresh** may transition an
issue out of `ready-for-agent` when the latest **Local integration** or
Exploratory handoff leaves the issue stale, unclear, obsolete, or already
satisfied. Ralph's current drain first records a read-only **Ready issue
refresh** analysis artifact with planned transitions; that subprocess is not
allowed to mutate labels or issue state. Runtime labels including
`agent-reviewing` block repeat implementation, **Ready issue refresh** candidate
selection, and automated triage reconsideration.

Human review owns the `agent-reviewing` transition. Accepted Exploratory review
merges the durable **Exploratory branch** to `dev`, records
`Ralph exploratory acceptance completed.` evidence with the accepted `dev`
commit, removes `agent-reviewing`, and adds `agent-integrated`. Rejected review
leaves the issue open, removes `agent-reviewing`, adds `ready-for-human`,
comments the review result, and must not add `agent-integrated`.

## Ralph delivery labels

Ralph and triage use these labels to choose the issue **Delivery mode**:

- `delivery-gitflow`: default; integrate to `dev`, review, then close during
  **Promotion** to `main`.
- `delivery-trunk`: opt-in for small docs, tests, tooling, or script changes
  that can integrate directly to `main`.
- `delivery-exploratory`: opt-in for changes that need a durable
  **Exploratory branch** instead of direct trunk closure or Gitflow
  **Promotion**. Use it only when the issue intent is explicit and the issue
  body includes `## Review focus` describing the human judgment the branch
  needs.

An issue should carry at most one delivery label. If `delivery-exploratory`
conflicts with Gitflow or trunk labels, Ralph keeps `delivery-exploratory` and
removes the others. If only Gitflow and trunk conflict, Ralph keeps
`delivery-gitflow`, removes `delivery-trunk`, and proceeds through the safer
default path.

Use [ralph-loop.md](ralph-loop.md) for the Ralph behavior behind these labels
and [issue-tracker.md](issue-tracker.md) for the GitHub Issue queue contract.
ADR
[0005](../adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md)
records why **Exploratory branches** stay outside automatic **Promotion**.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `OPERATOR.md`
  - `docs/agents/README.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/ralph-loop.md`
  - `docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md`
  - `scripts/ralph.py`
  - `.agents/skills/ralph-curate/SKILL.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `.agents/skills/ralph-issue-refresh/SKILL.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify label names match script constants and GitHub labels`
