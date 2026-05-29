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
portfolio `.webm` recordings for changed portfolio/static-serving inputs.

## Decision

Gitflow, Trunk, and Exploratory delivery must treat Review package generation
and validation as a blocking gate. Ralph records package state in
`ralph-run.json`, including status, HTML path, generator log path, structured
summary, validation status, optional media metadata, and failure reason.
Successful completion and handoff comments include the package path, summary,
and media artifact paths when present.

Exploratory delivery must run configured Review package media recipes after QA
and any required **Issue completion review**, before pushing the durable
**Exploratory branch**. It then generates and validates the HTML package before
the branch push, any post-push **Operator smoke**, the handoff comment, or the
`agent-reviewing` label transition. Successful Exploratory handoff records the
HTML package, media metadata, the target branch, and the handoff commit. The
package is handoff evidence only; human acceptance or rejection remains a later
explicit **Exploratory acceptance review** decision.

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
and no completion or handoff metadata is written.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `OPERATOR.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/ralph-loop.md`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
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
