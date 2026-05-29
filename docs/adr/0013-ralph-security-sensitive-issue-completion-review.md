# Ralph Extends Issue Completion Review For Security-Sensitive Changes

Ralph already runs **Issue completion review** after implementation QA and
before **Local integration**, Trunk push, or Exploratory handoff when risk
triggers require another automated pass. Prior work added the path-based
trigger shape and manifest fields for security-sensitive paths. Ralph now also
collects redacted added-line diff evidence for high-signal security review
signals. This ADR records why that evidence extends the existing gate instead
of adding a separate security gate or hard-blocking scanner.

Security-sensitive paths exclude ordinary maintained Markdown docs before
matching security-relevant surfaces, but they can include canonical and operator
files such as `AGENTS.md`, `CONTEXT.md`, `OPERATOR.md`, Agent workflow docs,
Ralph loop files, and other changed files that can affect credentials,
automation authority, dependency execution, containers, GitHub workflow
execution, infrastructure, authentication, Ralph behavior, or other
security-relevant operator surfaces. The classification combines path evidence
with deterministic added-line diff evidence. It does not try to prove that a
change is secure or insecure.

## Decision

Ralph treats **Security-sensitive change** as one trigger reason for **Issue
completion review**. It keeps the existing gate name, placement, read-only issue
access, and repair-loop behavior.

When the final changed-file inventory contains security-sensitive paths, Ralph
records those paths in the implementation manifest under
`issue_completion_review.security_sensitive_paths`, includes them in the
bounded review prompt, and keeps them verbatim in the prompt's risk-relevant
changed-file evidence when the changed-file inventory is large. The review
agent checks the completed implementation after QA, with the issue contract,
changed files, QA evidence, **Delivery mode**, **Integration target**, run
manifest path, and trigger reasons available as review evidence.

Ralph also scans the implementation diff against `origin/<base>...HEAD` before
review. It considers added lines only, ignoring deleted lines and unchanged
context lines, and records redacted evidence in
`issue_completion_review.security_diff_evidence`. Evidence patterns cover
secret or private-key markers, credential environment names, shell or network
execution markers, IAM, auth, CORS, security-group or permission changes, and
dependency or lockfile changes. Matched diff evidence can add
`Security-sensitive change` to the review reasons even when the changed path is
otherwise ordinary. After any **Issue completion review** repair, Ralph refreshes
the diff evidence from the repaired branch before rerunning the review prompt.

Failing findings do not hard-block through a separate scanner. They feed the
same **Issue completion review** repair loop as other review findings and
consume the same per-issue implementation attempt budget. Ralph reruns selected
QA and review after each repair before any **Integration target** update,
Trunk push, or Exploratory handoff. Concrete blockers in `## Security review`
are carried into the repair prompt with ordinary `## Findings`, and the
completion comment plus manifest preserve enough attempt evidence to inspect
the security review failure, repair, QA rerun, refreshed redacted security
evidence, and review rerun sequence.

The review subprocess keeps read-only **Sandboxed issue access**. It may use
`gh auth status`, `gh issue view`, `gh issue list`, and `gh issue status` only.
It must not create issues directly, comment, label, close, reopen, edit GitHub
Issues, commit, push, or update refs. Ralph's outer loop owns any later GitHub
Issue metadata mutation allowed by other phases.

Every accepted **Issue completion review** artifact includes a
`## Security review` section. That section records concrete repairable security
blockers and residual security risk, while `## Review result` remains the
pass/fail source of truth. Missing `## Security review` is treated as an
invalid review result before **Local integration**, Trunk push, or Exploratory
handoff.

## Considered options

- Add a separate security gate after QA: this would duplicate **Issue
  completion review** placement, reporting, retry, and manifest semantics while
  making operators reason about two pre-integration review gates.
- Add a hard-blocking scanner: this would sound stronger but would create false
  confidence because the current trigger is evidence collection for review, not
  proof that a change is secure or insecure. It would also add a new failure
  class without a repair-loop boundary.
- Reuse **Issue completion review** with a **Security-sensitive change** trigger:
  this keeps one automated pre-integration review gate and makes security-relevant
  paths discoverable in the manifest and review prompt.

## Consequences

Operators have one place to inspect risky issue review outcomes:
`issue-completion-review.md`, `codex-issue-completion-review.jsonl`, and the
`issue_completion_review` section in `ralph-run.json`. Completion comments also
summarize the review and repair attempt sequence after successful publication.
The artifact's `## Security review` section makes the security assessment
explicit for every review run. Security-sensitive paths and redacted diff
matches are evidence for why the gate ran, not a new **Delivery mode**, label,
CLI flag, or GitHub Issue permission.

The evidence trigger can produce conservative review coverage for automation,
credentials, dependency, and infrastructure-adjacent changes without granting
the review agent new authority. The tradeoff is that evidence classification
does not prove a change is secure; it only forces the existing **Issue
completion review** to inspect security-relevant scope before Ralph publishes
the work.

Future changes to the path list, prompt evidence, manifest fields, or read-only
review access must update this ADR, `CONTEXT.md`, Ralph docs, and issue-tracker
docs together.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/ralph-loop.md`
  - `docs/adr/0004-ralph-sandboxed-issue-access.md`
  - `docs/adr/0009-ralph-post-promotion-deployment-classification.md`
  - `tools/ralph-loop/README.md`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
- `sync.scope`: `operations, security`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `cd tools/ralph-loop && make run-prek`
  - `prek run -a`
  - `verify Security-sensitive change remains an Issue completion review trigger, not a new gate or GitHub Issue permission`
