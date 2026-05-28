# Ralph Gitflow Delivery Uses A Blocking Review Package Gate

Ralph Gitflow delivery now generates a per-issue **Review package** after final
changed files, QA evidence, and any required **Issue completion review** are
known, and before **Local integration** updates `dev`. The artifact is an
ignored local `review-package.html` in the issue run directory. It gives the
operator a human-facing static summary of the issue contract, changed files, QA
evidence, and review state before the work becomes part of the Gitflow
**Integration target**.

## Decision

Gitflow delivery must treat Review package generation and validation as a
blocking gate. Ralph records package state in `ralph-run.json`, including
status, HTML path, generator log path, structured summary, validation status,
and failure reason. Successful Gitflow completion comments include the package
path and summary.

The validator accepts only bounded offline static HTML with required review
sections. It rejects scripts, external URLs or assets, inline JavaScript,
JavaScript URLs, `file:` URLs, absolute local file reads, missing issue or
changed-file evidence, and oversized output. Generation failure, validation
failure, or generator-created repo edits fail the issue before **Local
integration**, before any `dev` push, and before `agent-integrated`.

## Consequences

Gitflow issue failures at this gate remain Ralph-owned pre-push failures:
worktrees, logs, and `review-package.html` evidence are preserved for operator
inspection, but no **Integration target** is updated and no completion metadata
is written. Trunk and Exploratory delivery do not use this gate yet; later
slices can reuse the same manifest model and validator when their delivery
contracts need a Review package.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `OPERATOR.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/ralph-loop.md`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
  - `tools/ralph-loop/tests/unit/test_ralph.py`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `cd tools/ralph-loop && make unit-test`
  - `cd tools/ralph-loop && make run-prek`
