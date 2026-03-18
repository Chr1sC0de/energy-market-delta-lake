# Pre-commit hooks

This worktree contains the pre-commit hook configuration for the monorepo. It
uses [prek](https://prek.j178.dev) in workspace mode — the root
`.pre-commit-config.yaml` anchors the workspace and prek auto-discovers
sub-project configs recursively.

## Structure

```
.pre-commit-config.yaml                           # Workspace root (no hooks, entry point only)
scripts/
├── install-hooks.sh                              # One-time machine setup
└── post-checkout                                 # Git hook — auto-installs prek on worktree add
backend-services/
└── dagster-user/
    └── aemo-etl/
        └── .pre-commit-config.yaml               # Sub-project hooks (orphan: true)
```

## Setup — new machine or fresh clone

Run once after cloning:

```bash
bash scripts/install-hooks.sh
```

This will:

1. Copy `scripts/post-checkout` into the bare repo's shared `hooks/` directory.
1. Run `prek install` so the current worktree's pre-commit hook is active immediately.

After that, any `git worktree add` will automatically install prek via the
`post-checkout` hook — no further action required.

### Prerequisites

`prek` must be on your PATH before running the setup script. Install it with
any of:

```bash
# recommended
uv tool install prek

# alternatives
pip install prek
pipx install prek
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/j178/prek/releases/latest/download/prek-installer.sh | sh
```

## Running hooks manually

From the worktree root, run all hooks against all files:

```bash
prek run -a
```

Run a specific hook by ID:

```bash
prek run ruff-check
prek run pytest
```

Run hooks for a specific sub-project only:

```bash
prek run backend-services/dagster-user/aemo-etl/
```

## Adding a new sub-project

1. Create a `.pre-commit-config.yaml` in the sub-project directory.
1. Add `orphan: true` at the top so its files are not double-processed by the
   workspace root.
1. Use `uv run <tool>` as the entry prefix for any `language: system`
   hooks so they resolve the correct virtual environment automatically,
   regardless of what is active in the calling shell.

Example:

```yaml
orphan: true
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff check
        language: system
        entry: uv run ruff check
        types: [python]
```

Run `prek run -a --refresh` after adding a new config to force prek to
re-scan the workspace.

## How it works

```
git commit
  └─> <bare-repo>/hooks/pre-commit      (installed by prek install)
        └─> prek run
              ├─> .pre-commit-config.yaml              (repos: [] — workspace anchor)
              └─> backend-services/dagster-user/aemo-etl/.pre-commit-config.yaml
                    └─> all sub-project hooks run with aemo-etl as cwd
                        (uv run resolves the correct .venv)

git worktree add <path> <branch>
  └─> <bare-repo>/hooks/post-checkout   (installed by scripts/install-hooks.sh)
        └─> prek install --overwrite    (idempotent — safe to run repeatedly)
```

The bare repo's `hooks/` directory is shared across all worktrees, so
`post-checkout` and `pre-commit` apply everywhere without per-worktree setup.
