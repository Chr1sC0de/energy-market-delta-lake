# Ralph Loop Package

This Subproject owns the repo-local Ralph issue loop implementation. The
operator-facing compatibility command remains at the repository root:

```bash
python3 scripts/ralph.py --help
```

The package also exposes a `ralph` console script when run inside this
Subproject with `uv run`.

## Local QA

Run from this directory:

```bash
make unit-test
make run-prek
```

## Layout

- `src/ralph_loop/cli.py`: Ralph CLI, side-effect adapters, loop controller,
  read-only `--doctor` preflight checks, hermetic Codex subprocess smoke and
  model plumbing, Operator **Integration target** baseline guard, operator-smoke
  execution, deploy-repair issue creation, verified post-push metadata recovery,
  Promotion source-table replay recovery output, Review package media recipe
  orchestration, Review package gate orchestration, bounded Review package
  evidence propagation into **Exploratory acceptance review** and
  **Post-promotion review** prompts, and compatibility re-exports
- `src/ralph_loop/review_package_media.py`: Ralph-owned Playwright helper that
  serves static build output and records Review package route `.webm` videos
- `src/ralph_loop/marimo_review_package_media.py`: Ralph-owned Marimo Review
  package media helper that starts the Marimo FastAPI app on loopback, waits
  for health, runs dashboard browser review, and records `.webm` videos
- `src/ralph_loop/workflow.py`: pure label, **Delivery mode**, QA selection,
  comment, **Issue completion review** trigger, **Security-sensitive change**
  path classification, structured Stiffness ratio parsing, Operator smoke
  request, deployment classification/execution selection, source-table replay
  recovery detection, Review package media route selection, Review package
  validation policy, baseline guard command selection, QA runtime disk guard,
  Codex subprocess command policy, bounded Review package comment
  formatting/parsing, and recovery policy helpers
- `src/ralph_loop/state.py`: Ralph run and Operator manifest state helpers,
  including **Issue completion review**, security-sensitive path evidence,
  structured Stiffness ratio evidence, Operator smoke evidence, adaptive-event
  evidence, source-table replay recovery guidance, active child run status,
  deploy-repair issue state, and checkpointed deploy-repair target state,
  Operator rollup failed-command summaries, rollup requeue recovery
  classification including no-change Codex environment failures, bounded Review
  package rollup and Promotion inventory evidence, and stale detached Operator
  status inputs
- `tests/unit/`: Ralph unit tests
- `.pre-commit-config.yaml`: Subproject `prek` hook surface

## Ralph internals doc

The maintained Ralph internals doc explains the
[one issue attempt lifecycle](../../docs/agents/ralph-loop.md#one-issue-attempt-lifecycle)
from label selection through implementation, QA evidence, **Local integration**,
review evidence, and issue state changes. It also defines Step size, Stiffness
ratio, Residual work, and adaptive events for queue-local retry and recovery
behavior:
[docs/agents/ralph-loop.md](../../docs/agents/ralph-loop.md#adaptive-vocabulary).
Use the same doc's
[Run manifest](../../docs/agents/ralph-loop.md#run-manifest) and
[Run inspection and recovery](../../docs/agents/ralph-loop.md#run-inspection-and-recovery)
sections to distinguish child run manifests, QA run-manifest evidence,
Operator rollups, **Promotion** manifests, and GitHub Issue comments before
choosing manual recovery.
ADR
[0011](../../docs/adr/0011-ralph-adaptive-vocabulary-and-verified-recovery.md)
records the initial stiffness thresholds and verified-only post-push metadata
recovery boundary, including same-run Operator recovery after the Integration
target push and commit reachability are verified.
ADR
[0013](../../docs/adr/0013-ralph-security-sensitive-issue-completion-review.md)
records why **Security-sensitive change** extends **Issue completion review**
instead of adding a separate security gate or scanner block.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `OPERATOR.md`
  - `docs/agents/ralph-loop.md`
  - `docs/adr/0011-ralph-adaptive-vocabulary-and-verified-recovery.md`
  - `docs/adr/0013-ralph-security-sensitive-issue-completion-review.md`
  - `docs/repository/documentation-sync.md`
  - `scripts/ralph.py`
  - `tools/ralph-loop/.pre-commit-config.yaml`
  - `tools/ralph-loop/Makefile`
  - `tools/ralph-loop/pyproject.toml`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/marimo_review_package_media.py`
  - `tools/ralph-loop/src/ralph_loop/review_package_media.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
  - `tools/ralph-loop/tests/unit/test_ralph.py`
  - `tools/ralph-loop/uv.lock`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `make run-prek`
  - `verify commands, package paths, and entrypoints`
