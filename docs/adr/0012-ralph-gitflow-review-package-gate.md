# Ralph Delivery Uses A Blocking Review Package Gate

Ralph Gitflow, Trunk, and Exploratory delivery now generate a per-issue
**Review package** after final changed files, QA evidence, and any required
**Issue completion review** are known, and before Ralph publishes the issue
work. The artifact is an ignored local `review-package.html` in the issue run
directory. It gives the operator a human-facing static summary of the issue
contract, changed files, QA evidence, and review state before work becomes part
of the **Integration target** or a durable **Exploratory branch**. Configured
Review package media recipes may add sibling artifacts, such as Marimo
dashboard `.webm` recordings for changed notebook routes or Caddy root
portfolio and dashboard-listing `.webm` recordings for changed
portfolio/static-serving inputs. Marimo media capture is Ralph-owned: Ralph
starts the Marimo FastAPI server from the issue worktree on a free loopback
port unless an operator supplies an explicit review base URL.

## Decision

Gitflow, Trunk, and Exploratory delivery must treat Review package generation
and validation as a blocking gate. Ralph records package state in
`ralph-run.json`, including status, HTML path, generator log path, structured
summary, validation status, optional media metadata, and failure reason.
Successful completion and handoff comments include package status, local HTML
path, media count, summary, and media artifact paths when present. Operator
rollups, **Exploratory acceptance review** artifacts, Promotion context, and
Promotion issue comments, and **Post-promotion review** prompts propagate only
this bounded metadata and do not inline generated HTML.

Exploratory delivery must run configured Review package media recipes after QA
and any required **Issue completion review**, before pushing the durable
**Exploratory branch**. It then generates and validates the HTML package before
the branch push, any post-push **Operator smoke**, the handoff comment, or the
`agent-reviewing` label transition. Successful Exploratory handoff records the
HTML package, media metadata, the target branch, and the handoff commit. The
package is handoff evidence only; human acceptance or rejection remains a later
explicit **Exploratory acceptance review** decision. Legacy handoffs created
before package evidence was recorded remain valid absent context.

The validator accepts only bounded offline static HTML with required review
sections. It rejects scripts, external URLs or assets, inline JavaScript,
JavaScript URLs, `file:` URLs, absolute local file reads, missing issue or
changed-file evidence, and oversized output, while permitting links to sibling
`.webm` media artifacts recorded by Ralph. Media capture failure, generation
failure, validation failure, or generator-created repo edits fail the issue
before **Local integration**, before any `dev` or `main` push, before
`agent-integrated` or `agent-merged`, before Trunk issue closure, and before an
Exploratory branch push or `agent-reviewing`. Exploratory packages must also
include a visible `Review focus` section so the first-glance report names the
human review question.

## Consequences

Failures at this gate remain Ralph-owned pre-push failures: worktrees, logs,
and any generated `review-package.html` evidence are preserved for operator
inspection, but no **Integration target** or **Exploratory branch** is updated
and no completion or handoff metadata is written. `--inspect-run`, Operator
status, and Operator rollups surface the generator log, validation reason,
media failures, and next safe action for these package failures before an
operator opens raw Codex JSONL or browser media logs. Checkpointed Operator
runs may automatically requeue eligible pre-push package failures under the
configured per-issue limit, but limit exhaustion leaves the issue failed for
operator inspection.
During **Promotion**, package summaries and paths follow only the verified
issue-to-commit evidence mapping. Ralph does not infer per-issue package
ownership from unverified Promotion commits or from the full Promotion
changed-file inventory.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `OPERATOR.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/ralph-loop.md`
  - `tools/ralph-loop/pyproject.toml`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/marimo_review_package_media.py`
  - `tools/ralph-loop/src/ralph_loop/review_package_media.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
  - `tools/ralph-loop/tests/unit/test_ralph.py`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `cd tools/ralph-loop && make unit-test`
  - `cd tools/ralph-loop && make run-prek`
