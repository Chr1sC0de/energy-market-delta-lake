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
- `agent-integrated`: Ralph integrated Gitflow work to `dev`; the issue waits
  for **Promotion** to `main`.

Runtime labels are not triage state labels. `ready-for-agent` remains the queue
selection label for implementation.

## Ralph delivery labels

Ralph and triage use these labels to choose the issue **Delivery mode**:

- `delivery-gitflow`: default; integrate to `dev`, review, then close during
  **Promotion** to `main`.
- `delivery-trunk`: opt-in for small docs, tests, tooling, or script changes
  that can integrate directly to `main`.

An issue should carry at most one delivery label. If both are present, Ralph
keeps `delivery-gitflow`, removes `delivery-trunk`, and proceeds through the
safer default path.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `scripts/ralph.py`
  - `.agents/skills/ralph-triage/SKILL.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify label names match script constants and GitHub labels`
