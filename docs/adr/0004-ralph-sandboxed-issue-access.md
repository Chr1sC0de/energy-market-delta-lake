# Ralph Uses Sandboxed Issue Access For GitHub Issue Metadata

Ralph spawned Codex subprocesses may use **Sandboxed issue access** for
authenticated GitHub Issue reads and writes. Ralph injects a `GH_TOKEN` sourced
from the parent environment or local `gh auth`, enables network for the
workspace-write Codex sandbox, and places a wrapper ahead of `gh` so the
sandbox can use only `gh auth status` and a triage-safe `gh issue` command set.

## Considered options

- Keep sandboxed Codex subprocesses unauthenticated: preserves the smallest
  sandbox boundary, but blocks AFK triage and issue metadata workflows.
- Expose the local `gh` credential store: works with `gh auth login`, but makes
  the sandbox depend on mutable host credential files.
- Use **Sandboxed issue access**: keeps GitHub Issues usable inside Ralph while
  leaving **Local integration**, Git push auth, and **Promotion** outside the
  sandbox.

## Consequences

Operators may refresh local auth with `gh auth login -h github.com
--git-protocol ssh` or export `GH_TOKEN`; Ralph still injects only `GH_TOKEN`
into sandboxed Codex command environments. Git fetch and push continue to use
the repository remote, usually SSH, and remain part of Ralph's outer loop.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `scripts/ralph.py`
  - `docs/agent-issue-loop.md`
  - `CONTEXT.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify decision text matches Ralph sandbox, issue metadata, and Git auth boundaries`
