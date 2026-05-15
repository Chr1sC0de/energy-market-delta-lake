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
  deploy-repair issue creation, and compatibility re-exports
- `src/ralph_loop/workflow.py`: pure label, **Delivery mode**, QA selection,
  comment, **Issue completion review** trigger, deployment
  classification/execution selection, and recovery policy helpers
- `src/ralph_loop/state.py`: Ralph run and Operator manifest state helpers,
  including **Issue completion review** and deploy-repair issue state
- `tests/unit/`: Ralph unit tests
- `.pre-commit-config.yaml`: Subproject `prek` hook surface

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `AGENTS.md`
  - `OPERATOR.md`
  - `docs/agents/ralph-loop.md`
  - `docs/repository/documentation-sync.md`
  - `scripts/ralph.py`
  - `tools/ralph-loop/.pre-commit-config.yaml`
  - `tools/ralph-loop/Makefile`
  - `tools/ralph-loop/pyproject.toml`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
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
