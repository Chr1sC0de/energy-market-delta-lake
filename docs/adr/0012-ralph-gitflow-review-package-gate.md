# Ralph Delivery Uses A Blocking Review Package Gate

Ralph Gitflow and Trunk delivery now generate a per-issue **Review package**
after final changed files, QA evidence, and any required **Issue completion
review** are known, and before **Local integration** updates `dev` or `main`.
The artifact is an ignored local `review-package.html` in the issue run
directory. It gives the operator a human-facing static summary of the issue
contract, changed files, QA evidence, and review state before the work becomes
part of the **Integration target**. Configured Review package media recipes may
add sibling artifacts, such as Marimo dashboard `.webm` recordings for changed
notebook routes. Exploratory delivery does not generate the HTML package, but
it still runs configured media recipes before publishing the Exploratory
handoff.

## Decision

Gitflow and Trunk delivery must treat Review package generation and validation as a
blocking gate. Ralph records package state in `ralph-run.json`, including
status, HTML path, generator log path, structured summary, validation status,
optional media metadata, and failure reason. Successful Gitflow and Trunk
completion comments include the package path, summary, and media artifact paths
when present.

Exploratory delivery must run configured Review package media recipes after QA
and any required **Issue completion review**, before pushing the durable
**Exploratory branch**. Successful media-only Exploratory handoff records media
metadata in the same manifest field and includes the artifact paths in the
completion comment, with `validation_status: not_required` because no HTML
package is generated or validated.

The validator accepts only bounded offline static HTML with required review
sections. It rejects scripts, external URLs or assets, inline JavaScript,
JavaScript URLs, `file:` URLs, absolute local file reads, missing issue or
changed-file evidence, and oversized output, while permitting links to sibling
`.webm` media artifacts recorded by Ralph. Media capture failure, generation
failure, validation failure, or generator-created repo edits fail the issue
before **Local integration**, before any `dev` or `main` push, before
`agent-integrated` or `agent-merged`, and before Trunk issue closure. For
Exploratory delivery, media capture failure fails the issue before pushing the
Exploratory handoff or applying `agent-reviewing`.

## Consequences

Gitflow and Trunk issue failures at this gate remain Ralph-owned pre-push
failures: worktrees, logs, and `review-package.html` evidence are preserved for
operator inspection, but no **Integration target** is updated and no completion
metadata is written. Exploratory media failures are also Ralph-owned pre-push
failures: the durable **Exploratory branch** is not pushed and the issue is not
marked `agent-reviewing`.

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
