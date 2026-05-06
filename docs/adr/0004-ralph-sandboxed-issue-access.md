# Ralph Uses Sandboxed Issue Access For GitHub Issue Metadata

Ralph spawned Codex subprocesses may use **Sandboxed issue access** for
authenticated GitHub Issue access. Ralph injects a `GH_TOKEN` sourced from the
parent environment or local `gh auth`, enables network for the workspace-write
Codex sandbox, and places a wrapper ahead of `gh` so the sandbox can use only
`gh auth status` and the phase-specific `gh issue` command set. Implementation
and triage passes may use triage-safe issue reads and writes. The
**Post-promotion review** pass gets read-only issue access and cannot create
issues directly, comment, label, close, reopen, or edit issues. After a
successful **Promotion**, Ralph may create structured follow-up issues through
its own validated create-only helper.

## Considered options

- Keep sandboxed Codex subprocesses unauthenticated: preserves the smallest
  sandbox boundary, but blocks AFK triage and issue metadata workflows.
- Expose the local `gh` credential store: works with `gh auth login`, but makes
  the sandbox depend on mutable host credential files.
- Use **Sandboxed issue access**: keeps GitHub Issues usable inside Ralph while
  leaving **Local integration**, Exploratory handoff, Git push auth, and
  **Promotion** outside the sandbox.

## Consequences

Operators may refresh local auth with `gh auth login -h github.com
--git-protocol ssh` or export `GH_TOKEN`; Ralph still injects only `GH_TOKEN`
into sandboxed Codex command environments. Git fetch and push continue to use
the repository remote, usually SSH, and remain part of Ralph's outer loop.
**Ready issue refresh** may receive phase-limited write commands for comments,
body updates, label transitions, and completed closures after **Local
integration** or Exploratory handoff and before the next ready issue claim.
**Post-promotion review** agent access stays read-only for successful, failed,
and partial **Promotion** attempts: the review agent drafts structured
actionable follow-up GitHub Issues in `post-promotion-review.md` only when it
finds actionable work, and Ralph does not grant it issue mutation commands.
For successful **Promotion** runs, Ralph then uses a create-only helper to
validate each draft before creating any GitHub Issue. The helper creates
`ready-for-agent` issues only when the draft includes `## What to build`,
`## Acceptance criteria`, `## Blocked by`, one category label, and one
**Delivery mode** label; otherwise it creates `needs-triage` issues with
validation evidence. Each created issue receives a deterministic source marker
based on the **Promotion** commit and finding ID so reruns skip duplicates.
Helper failures after `main` is pushed are warning-only and recorded with
recovery guidance in the **Promotion** manifest and review artifact.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `scripts/ralph.py`
  - `docs/agents/ralph-loop.md`
  - `CONTEXT.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify decision text matches Ralph sandbox, issue metadata, and Git auth boundaries`
