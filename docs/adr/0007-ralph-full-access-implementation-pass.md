# Ralph Gates Full-Access Implementation Passes For Agent Workflow Files

Ralph normally runs Codex implementation subprocesses with the workspace-write
Codex sandbox. In this environment, `.agents/` is mounted read-only, so issues
that intentionally change repo-local agent workflow files need a different
filesystem boundary from normal implementation work.

## Decision

Ralph supports an explicit **Full-access implementation pass** only for ready
issues whose `## Context anchors` include `.agents/` paths. The operator must
pass `--allow-full-access-implementation`; otherwise Ralph stops before claiming
the issue, creating a worktree, or marking it failed.

When enabled, only the Codex implementation subprocess for those anchored issues
runs with Codex's approvals-and-sandbox bypass. Its **Sandboxed issue access**
is read-only: `gh auth status`, `gh issue view`, `gh issue list`, and
`gh issue status`. Ralph still owns GitHub Issue metadata, **Local integration**,
Exploratory handoff, **Integration target** pushes, and **Promotion** in the
outer loop.

After each full-access Codex implementation attempt returns, Ralph reads the
worktree diff before QA. Every changed file must match an issue context anchor.
Directory anchors count as prefixes. If any changed file is outside those
anchors, Ralph records `full_access_implementation.status: diff_out_of_scope`,
skips retry, skips QA, skips **Local integration** or Exploratory handoff, keeps
the worktree, and reports recovery guidance.

## Considered options

- Keep `.agents/` edits unsupported in Ralph: preserves the smallest sandbox
  boundary but blocks Ralph from maintaining its own repo-local workflow docs and
  skills.
- Run all Ralph implementation work with full filesystem access: removes the
  mount problem but makes ordinary product, data, and infrastructure work too
  broad.
- Gate full filesystem access by issue context anchors and an operator flag:
  keeps normal issues on workspace-write, permits intentional `.agents/` work
  through Codex's explicit bypass flag, and gives Ralph a deterministic pre-QA
  escape check.

## Consequences

Issue shapers must include exact `.agents/` context anchors for workflow-file
changes. Operators must opt in with `--allow-full-access-implementation` for
drains that include those ready issues. A full-access issue can still inspect
GitHub Issues, but it cannot mutate issue state from inside the Codex
subprocess. The run manifest records the enablement state, required anchors,
changed files, out-of-scope files, and recovery guidance.

Normal ready issues remain on the workspace-write Codex sandbox and keep their
existing phase-limited **Sandboxed issue access**.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `scripts/ralph.py`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
  - `tools/ralph-loop/tests/unit/test_ralph.py`
  - `CONTEXT.md`
  - `OPERATOR.md`
  - `docs/agents/ralph-loop.md`
  - `docs/agents/issue-tracker.md`
  - `docs/adr/0004-ralph-sandboxed-issue-access.md`
  - `.agents/skills/ralph-loop/SKILL.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `verify full-access boundary, sandboxed issue access, commands, and links`
