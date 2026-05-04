# Agent Issue Loop

This page documents the repo-local Ralph loop in `scripts/ralph.py`. The loop
uses GitHub Issues as the queue, Codex as the implementation and triage worker,
repo **Test lane** commands as the validation boundary, and **Local
integration** plus **Promotion** as the success path after QA.

## Table of contents

- [Purpose](#purpose)
- [Drain flow](#drain-flow)
- [Labels](#labels)
- [Run modes](#run-modes)
- [Live run preflight](#live-run-preflight)
- [AFK run monitoring](#afk-run-monitoring)
- [Run manifest](#run-manifest)
- [Run inspection and recovery](#run-inspection-and-recovery)
- [Implementation pass](#implementation-pass)
- [Promotion pass](#promotion-pass)
- [Triage pass](#triage-pass)
- [QA policy](#qa-policy)
- [Failure handling](#failure-handling)

## Purpose

Ralph drains agent-ready GitHub issues through a guarded local loop:

1. Find the oldest unblocked `ready-for-agent` issue.
2. Resolve the issue **Delivery mode** and **Integration target**.
3. Run `codex exec` to implement the issue.
4. Run deterministic local QA.
5. Squash-merge validated work onto the latest **Integration target** locally.
6. In **Gitflow delivery**, push `dev`, comment evidence, mark
   `agent-integrated`, and leave the issue open for **Promotion**.
7. In **Trunk delivery**, push `main`, comment evidence, mark `agent-merged`,
   and close the issue.
8. If no ready issue exists, triage the next unblocked issue and rescan.

The loop stops when the queue has no unblocked implementation or triage
candidates, or when `--max-issues` is reached. A plain `--drain` run defaults
to 10 implementation attempts; `--max-issues 0` is the explicit unlimited drain
mode.

Human operators should call Ralph through repo-local skills:

```text
$grill-with-docs <feature idea> -> $to-prd -> $to-issues -> $ralph-triage -> $ralph-loop drain
```

`$ralph-triage` prepares GitHub Issues for drain by setting category, state, and
**Delivery mode** labels. `$ralph-loop` owns the backing script commands.

## Drain flow

```mermaid
flowchart TD
  START[Start drain] --> PREFLIGHT[Validate tools, root worktree, GitHub auth, sandboxed issue access, and labels]
  PREFLIGHT --> READY{Unblocked ready-for-agent issue?}
  READY -->|Yes| CLAIM[Claim issue with agent-running]
  CLAIM --> CONTRACT{Issue contract valid?}
  CONTRACT -->|No| FAIL[Mark agent-failed and comment evidence]
  CONTRACT -->|Yes| MODE[Resolve Delivery mode and Integration target]
  MODE --> WORKTREE[Create issue branch and worktree]
  WORKTREE --> CODEX[Run Codex implementation]
  CODEX --> QA[Run selected Test lane QA]
  QA --> INTEGRATE[Run Local integration]
  INTEGRATE --> DONE{Delivery mode?}
  DONE -->|Gitflow| STAGE[Comment evidence and mark agent-integrated]
  DONE -->|Trunk| CLOSE[Comment evidence, mark agent-merged, close issue]
  STAGE --> LIMIT{Max implementation attempts reached?}
  CLOSE --> LIMIT
  LIMIT -->|No| READY
  LIMIT -->|Yes| STOP[Stop drain]
  READY -->|No| TRIAGE{Unblocked triage candidate?}
  TRIAGE -->|Yes| TRIAGEPASS[Run automated triage]
  TRIAGEPASS --> READY
  TRIAGE -->|No| STOP
  FAIL --> READY
```

## Labels

Triage state labels:

- `needs-triage`
- `needs-info`
- `ready-for-agent`
- `ready-for-human`
- `wontfix`

Category labels:

- `bug`
- `enhancement`

Ralph runtime labels:

- `agent-running`
- `agent-failed`
- `agent-merged`
- `agent-integrated`

Ralph delivery labels:

- `delivery-gitflow`
- `delivery-trunk`

Use `ready-for-agent` as the queue selection signal. `needs-triage`,
`needs-info`, `ready-for-human`, `wontfix`, `agent-running`, `agent-failed`,
`agent-merged`, and `agent-integrated` block implementation.

`delivery-gitflow` is the default **Delivery mode**. `delivery-trunk` is an
opt-in label for small docs, tests, tooling, or script changes. If both delivery
labels are present, Ralph keeps `delivery-gitflow`, removes `delivery-trunk`,
and proceeds through the safer default.

Create or refresh the labels with:

```bash
python3 scripts/ralph.py --bootstrap-labels
```

## Run modes

Dry-run the next action:

```bash
python3 scripts/ralph.py --drain --dry-run
```

Drain up to 10 implementation attempts:

```bash
python3 scripts/ralph.py --drain
```

Drain directly to trunk for small low-risk changes:

```bash
python3 scripts/ralph.py --drain --delivery-mode trunk
```

Drain until only blocked or non-actionable issues remain:

```bash
python3 scripts/ralph.py --drain --max-issues 0
```

Implement one specific issue:

```bash
python3 scripts/ralph.py --issue 25
```

Promote reviewed Gitflow work from `dev` to `main`:

```bash
python3 scripts/ralph.py --promote
```

Override the **Integration target** explicitly when needed:

```bash
python3 scripts/ralph.py --issue 25 --target-branch feature/my-branch
```

Inspect a completed or failed implementation run without mutating GitHub or git
state:

```bash
python3 scripts/ralph.py --inspect-run .ralph/runs/issue-25-20260504T010203Z
```

Recover missing GitHub metadata after verifying the recorded **Local
integration** commit reached the expected **Integration target**:

```bash
python3 scripts/ralph.py --recover-run .ralph/runs/issue-25-20260504T010203Z
```

Bypass the live clean-root preflight only when the operator intentionally wants
Ralph to run with uncommitted root worktree changes:

```bash
python3 scripts/ralph.py --drain --allow-dirty-worktree
```

## Live run preflight

Live `--issue`, `--drain`, and `--promote` runs fail before GitHub issue claim,
worktree creation, **Local integration**, or push when the root worktree has
uncommitted changes. Commit or stash root worktree changes before live Ralph
runs. Use `--allow-dirty-worktree` only for an explicit dirty-worktree
operation. `--dry-run` remains available on a dirty root worktree so operators
can inspect the next Ralph action without mutating issues or branches.

Before a live drain, validate both GitHub API auth and Git push auth for the
expected **Integration target**:

```bash
gh auth status
git push --dry-run origin HEAD:main
```

When using token-based GitHub CLI auth, export `GH_TOKEN` in the shell that runs
Ralph. Do not paste token values into commands, issue comments, docs, or logs.
Ralph also gives spawned Codex subprocesses **Sandboxed issue access** by
default: it resolves a token from `GH_TOKEN`, `GITHUB_TOKEN`, or `gh auth
token`, injects it as `GH_TOKEN`, enables network for the workspace-write Codex
sandbox, and prepends a wrapper that permits only `gh auth status` plus
triage-safe `gh issue` reads and writes. This does not grant Git push access;
Git fetches, **Local integration**, **Integration target** pushes, and
**Promotion** stay in Ralph's outer loop.

Use `HEAD:dev` for Gitflow target validation and `HEAD:main` for trunk or
promotion validation. Run Ralph from a local worktree that is aligned with the
remote branch being operated on. The script fetches the **Integration target**
during implementation and rebases issue work if the target moves, but the
operator should start from a known repo state.

## AFK run monitoring

Ralph writes command logs while subprocesses are still running. Long Codex
implementation attempts write to `codex-implementation-N.jsonl`, triage writes
to `codex-triage.jsonl`, QA writes to `qa-*` logs, and Git operations write to
their named `git-*` logs under the current `.ralph/runs/...` run directory.
While a command is active, the log has `exit: running`; after the command
finishes, Ralph rewrites the same log with the final exit status while
preserving stdout, stderr, command, and cwd.

During logged long-running phases, Ralph prints a heartbeat about every 30
seconds:

```text
Ralph heartbeat: phase=#49: Codex implementation attempt 1; log=/repo/.ralph/runs/issue-49-.../codex-implementation-1.jsonl
```

For AFK drains, use the heartbeat phase to see what Ralph is waiting on and tail
the active log path to inspect live command output. If the terminal only shows
heartbeats and no completion message, the phase is still running. If a command
fails, the same log path appears in the failure output or issue evidence.

## Run manifest

Every implementation run and **Promotion** run writes
`.ralph/runs/.../ralph-run.json`. The manifest is rewritten as milestones
complete, so a failed run still records the last known recovery state.

Key fields for inspection:

- `schema_version`: manifest format version.
- `run_kind`: `implementation` or `promotion`.
- `status` and `stage`: current run outcome and latest milestone.
- `events`: timestamped milestone history.
- `issue`: implementation issue number, title, and URL.
- `github_metadata.issues`: promoted issue numbers and their recorded Gitflow
  integration commits during **Promotion**.
- `delivery_mode`: issue **Delivery mode**; **Promotion** records `gitflow`.
- `integration_target`: branch Ralph is updating for the run.
- `source_branch`: **Promotion** source branch, usually `dev`.
- `branches`: issue, source, and target branch names that apply to the run.
- `paths`: repo root, run directory, worktree container, and implementation,
  integration, or promotion worktree paths.
- `changed_files`: current file diff used for QA and integration.
- `qa_results`: selected QA commands, cwd, log path, and pass/fail state.
- `sandboxed_issue_access`: non-secret token source, wrapper path, allowed
  command set, and network access state for spawned Codex subprocesses.
- `integration_commit`: implementation **Local integration** commit.
- `promotion_commit`: **Promotion** commit pushed to `main`.
- `pushes`: per-branch push state, commit SHA, and push log path.
- `github_metadata`: claim, completion, failure, Promotion comment, label, and
  close state.
- `failure`: user-facing error message and command log path when the run fails.

## Run inspection and recovery

Use `--inspect-run <run_dir>` first when a terminal shows a post-push metadata
failure, a completed issue looks inconsistent in GitHub, or an AFK run needs a
read-only summary. Inspection reads only `<run_dir>/ralph-run.json` and reports
the issue, **Delivery mode**, **Integration target**, QA status, push status,
metadata status, and recommended next action. It does not call `gh`, run git
commands, edit labels, comment, close issues, or change refs.

Use `--recover-run <run_dir>` only for implementation runs whose manifest
records an integration commit. Recovery fetches the expected target branch and
refuses to proceed unless the recorded integration commit is reachable from
`origin/<integration-target>`. This guard keeps GitHub metadata reconciliation
behind proof that the **Local integration** commit reached the expected branch.

After reachability is verified, recovery reconciles GitHub metadata to the
issue's **Delivery mode**:

- **Trunk delivery**: ensure the completion comment exists, remove runtime
  labels, apply `agent-merged`, and close the issue.
- **Gitflow delivery**: ensure the completion comment exists, remove runtime
  labels, apply `agent-integrated`, and leave the issue open for **Promotion**.
  If the issue was closed prematurely, recovery reopens it.

Recovery does not rerun Codex, rerun QA, create commits, push branches, or clean
worktrees. Normal Ralph runs keep fail-stop behavior: if metadata operations
fail after a push, Ralph stops loudly so an operator can inspect the run and
recover deliberately.

## Implementation pass

An implementation issue must have these sections:

- `## What to build`
- `## Acceptance criteria`
- `## Blocked by`

If any referenced blocker in `Blocked by` is still open, Ralph skips the issue.
If the issue contract is malformed, Ralph marks the issue `agent-failed` and
leaves a result comment with the run log path.

Ralph chooses **Delivery mode** from issue labels first, then from the CLI
default. Missing delivery labels are written back to the issue before
implementation. `delivery-gitflow` defaults to `origin/dev`; if that branch does
not exist, Ralph creates it from `origin/main`. Before creating a Gitflow issue
branch, Ralph also syncs `origin/main` into `origin/dev` when `main` is not
already an ancestor of `dev`, so the **Integration target** is not behind trunk.
`delivery-trunk` defaults to `origin/main`. `--target-branch` overrides the
**Integration target** explicitly.

Ralph creates branches named `agent/issue-N-slug` from the **Integration target**
and creates sibling worktrees under the repo worktree container. Codex is
instructed not to commit, push, or edit GitHub issue state; Ralph owns those
steps after QA passes.

After QA passes, Ralph commits the issue branch, fetches the **Integration
target**, and rebases the issue branch if the target moved. A rebase triggers
the selected QA commands again before **Local integration** continues.

For **Local integration**, Ralph creates a temporary detached integration
worktree at latest target, runs `git merge --squash` from the issue branch,
creates one integration commit, pushes it to the target, and posts completion
evidence with the commit SHA, changed files, QA commands, and run log path.
Trunk integration marks the issue `agent-merged` and closes it. Gitflow
integration marks the issue `agent-integrated` and leaves it open for
**Promotion**. Ralph does not open a GitHub draft PR.

```mermaid
sequenceDiagram
  participant Ralph
  participant IssueBranch as Issue branch
  participant Target as Integration target
  participant Integration as Integration worktree
  participant GitHubIssue as GitHub Issue

  Ralph->>IssueBranch: Commit validated issue work
  Ralph->>Target: Fetch latest target
  alt target moved
    Ralph->>IssueBranch: Rebase and rerun selected QA
  end
  Ralph->>Integration: Create detached worktree at target
  Integration->>IssueBranch: git merge --squash
  Integration->>Target: git push HEAD:target
  Ralph->>GitHubIssue: Comment evidence
  alt Trunk delivery
    Ralph->>GitHubIssue: Add agent-merged and close
  else Gitflow delivery
    Ralph->>GitHubIssue: Add agent-integrated
  end
```

## Promotion pass

`python3 scripts/ralph.py --promote` promotes reviewed Gitflow work from
`origin/dev` to `origin/main` by default. Ralph fetches both branches, computes
the changed files between them, runs the aggregate matching **Push check** QA,
merges `origin/dev` into a detached `origin/main` worktree with per-issue commits
preserved, pushes `main`, and then fast-forwards `dev` to the promotion commit so
the next Gitflow drain starts from a `dev` branch that contains `main`.

After the push succeeds, Ralph scans open `agent-integrated` issues. It closes
only issues whose recorded Gitflow integration commit is still in the promoted
`origin/main..origin/dev` range, then comments promotion evidence and replaces
`agent-integrated` with `agent-merged`.

## Triage pass

When no unblocked `ready-for-agent` issue exists, Ralph asks Codex to run the
`ralph-triage` skill on the next unblocked triage candidate:

- unlabeled issues
- `needs-triage` issues
- `needs-info` issues only when reporter activity appears after the latest AI
  triage note

Automated triage may label, comment, or close issues. Every triage comment must
begin with:

```markdown
> *This was generated by AI during triage.*
```

Ralph v1 does not let automated triage write `.out-of-scope/` files. If an
enhancement looks like `wontfix` and needs an out-of-scope record, triage should
mark it `ready-for-human` instead.

Automated triage also applies Ralph delivery labels. It should default to
`delivery-gitflow` and use `delivery-trunk` only for clearly small docs, tests,
tooling, or script changes. Runtime behavior, infrastructure, Dagster, S3,
LocalStack, cross-**Subproject** work, broad refactors, or unclear scope should
stay on `delivery-gitflow`.

## QA policy

For `aemo-etl` changes, Ralph runs from the owning **Subproject**:

```bash
make unit-test
make component-test
make integration-test
make run-prek
```

For root docs/config or cross-**Subproject** changes, Ralph runs:

```bash
prek run -a
```

For Ralph script or unit-test changes, Ralph runs:

```bash
python3 -m unittest discover -s tests
```

If the **Integration target** changes after the implementation worktree was
created, Ralph rebases the issue branch and reruns the selected QA commands
before merging.

During **Promotion**, Ralph computes all files changed between `origin/main` and
`origin/dev`, then runs the matching QA set as an aggregate **Push check** before
pushing `main`.

## Failure handling

Codex or QA failures get one retry in the same worktree. If retry fails, Ralph:

- keeps the failed worktree for inspection
- adds `agent-failed`
- removes `agent-running`
- leaves a result comment with the failing command and log path
- continues drain mode with the next actionable issue

Successful issues remove the implementation worktree, integration worktree, and
temporary issue branch after trunk closure or Gitflow integration. Cleanup
failures are warnings; the pushed commit and GitHub issue metadata remain the
source of truth.

Merge or push failures before the **Integration target** is updated are issue
failures and keep the worktrees for inspection. Failures after the target is
pushed stop the drain because the code may already be published while GitHub
issue metadata may be inconsistent. Promotion failures before `main` is pushed
leave issues open with `agent-integrated`; failures after `main` is pushed stop
the run for the same metadata consistency reason.

Environment failures stop the run. Examples include invalid `gh` auth, missing
labels, unavailable tools, failing Git operations before claim, or unavailable
container-backed **Integration test** dependencies.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `scripts/ralph.py`
  - `docs/agents/triage-labels.md`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `.agents/skills/ralph-triage/SKILL.md`
  - `AGENTS.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, headings, commands, paths, labels, and names`
