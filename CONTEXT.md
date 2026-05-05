# Energy Market Delta Lake

This context defines repo-wide language for the Energy Market Delta Lake
monorepo. It captures terms that affect project structure, test scope, and
engineering decisions across **Subprojects**.

## Language

**Subproject**:
A separately configured project inside the monorepo with its own dependency,
tooling, or test boundary.
_Avoid_: Submodule, package

**Pytest subproject**:
A **Subproject** that owns a pytest suite and runs it from that subproject's
working directory.
_Avoid_: Test module

**Test lane**:
A repo-standard test category that defines dependency boundaries and expected
runtime cost.
_Avoid_: Test type, test level

**Unit test**:
A test that exercises pure or mocked code without framework runtime, containers,
live network, or deployed cloud resources.
_Avoid_: Fast test

**Component test**:
An in-process composition test that exercises framework/runtime wiring without
real external services.
_Avoid_: Service test, contract test

**Integration test**:
A test that uses a real local external dependency such as LocalStack or Podman.
_Avoid_: Component test

**Deployed test**:
A test that runs against already-deployed cloud resources.
_Avoid_: Integration test, live integration test

**End-to-end test**:
A test that exercises the complete local service stack across subprojects.
_Avoid_: Complete local integration test, system test

**Fast check**:
A check set intended for short local feedback. It runs only **Unit tests** and
**Component tests**, plus static checks, without containers, live network, or
deployed cloud resources.
_Avoid_: Unit check

**Commit check**:
A **Fast check** expected before commit, usually through `prek` pre-commit
hooks.
_Avoid_: Pre-commit test

**Push check**:
A check expected before pushing. It may include guarded **Integration tests**,
but must not include **Deployed tests** by default.
_Avoid_: Pre-push test

**Local integration**:
The Ralph action that squash-merges validated issue work onto an
**Integration target** without a GitHub PR.
_Avoid_: Local PR, draft PR gate

**Sandboxed issue access**:
The Ralph boundary that lets spawned Codex subprocesses use authenticated
GitHub Issue commands without owning **Local integration** or **Promotion**.
The allowed commands can be read-only or write-limited by Ralph phase.
_Avoid_: Full GitHub sandbox auth, Git push sandbox auth

**Ready issue refresh**:
The Ralph queue-maintenance pass that reconciles open GitHub Issues after a
successful **Local integration** and before the next `ready-for-agent` issue
claim. It may refresh issue context, labels, blockers, or completed closure
evidence so the queue reflects the latest **Integration target** state.
_Avoid_: Post-promotion review, triage pass

**Operator workflow**:
The human workflow for shaping work, preparing GitHub Issues, draining Ralph,
reviewing `dev`, and running **Promotion**.
_Avoid_: Agent loop, Ralph internals

**Delivery mode**:
The Ralph branch strategy that decides where validated issue work is integrated
and when its GitHub issue is closed.
_Avoid_: Agent type, agent kind

**Integration target**:
The explicit remote branch that Ralph updates after issue QA.
_Avoid_: Current branch, working branch

**Gitflow delivery**:
The default **Delivery mode** where Ralph integrates issue work to `dev` for
review before **Promotion** to `main`.
_Avoid_: Development-agent mode

**Trunk delivery**:
The opt-in **Delivery mode** where Ralph integrates issue work directly to
`main` and closes the issue after QA.
_Avoid_: Fast agent mode

**Exploratory delivery**:
The opt-in **Delivery mode** where Ralph integrates issue work to a durable
review branch, marks the issue `agent-reviewing`, and leaves it open for human
review.
_Avoid_: Draft PR mode, branch-only PR

**Promotion**:
The Ralph operation that merges reviewed `dev` work into `main` and closes the
verified GitHub issues included in that branch range.
_Avoid_: Manual dev merge

**Post-promotion review**:
The default Ralph review agent pass that runs after a **Promotion** attempt with
changed files where a review worktree is available. Successful Promotions run it
after `main` is pushed, `dev` is synced, and verified issue metadata updates
complete; failed or partial Promotion attempts try it as warning-only recovery
review without changing the original Promotion outcome.
_Avoid_: Promotion gate, pre-push review

## Relationships

- A **Pytest subproject** is one kind of **Subproject**.
- A **Pytest subproject** may have one or more **Test lanes**.
- A **Unit test** must not depend on framework runtime, containers, live network,
  or deployed cloud resources.
- A **Component test** may use in-process framework runtimes such as FastAPI
  `TestClient`, Pulumi runtime mocks, or Dagster `execute_in_process`.
- An **Integration test** may use LocalStack or Podman, but not deployed cloud
  resources.
- A **Deployed test** must be opt-in and guarded because it can inspect live
  deployed infrastructure.
- An **End-to-end test** spans multiple **Subprojects** and is deferred from the
  current test refactor.
- A **Commit check** runs the **Fast check** set.
- A **Push check** may add local **Integration tests** to the **Fast check** set.
- **Local integration** happens after Ralph implementation QA and before either
  issue closure or **Promotion**.
- **Local integration** is not a **Test lane**.
- **Sandboxed issue access** may update GitHub Issue metadata when the Ralph
  phase grants write commands, but it must not update an **Integration target**.
- **Ready issue refresh** runs after a successful **Local integration** and
  before Ralph claims the next `ready-for-agent` issue in a drain.
- **Ready issue refresh** may mutate GitHub Issue metadata under its audit
  contract; it is not **Promotion** and is not **Post-promotion review**.
- The **Operator workflow** is the human entrypoint; Ralph internals remain on
  the agent-facing Ralph documentation page.
- A **Delivery mode** selects an **Integration target**.
- **Gitflow delivery** uses `dev` as the default **Integration target**.
- **Trunk delivery** uses `main` as the default **Integration target**.
- **Exploratory delivery** uses a per-issue `agent/review/issue-N-slug` branch
  as the default **Integration target**.
- **Promotion** closes only issues whose `dev` integration commit is verified in
  the promoted branch range.
- **Post-promotion review** happens after **Promotion** attempts where possible;
  it is not a **Push check** gate, it is not **Ready issue refresh**, and it
  uses read-only GitHub Issue access.

## Example dialogue

> **Dev:** "Should this Dagster asset materialization stay in the unit lane?"
> **Domain expert:** "No. It uses the Dagster runtime in process, so it is a
> **Component test**. Keep only pure transforms and mocked helpers as
> **Unit tests**."
>
> **Dev:** "Can the sandboxed Codex pass close or label an issue during Ralph?"
> **Domain expert:** "Only when that Ralph phase grants issue write commands
> through **Sandboxed issue access**. **Ready issue refresh** may mutate issues
> under its audit contract, but **Post-promotion review** is read-only, and no
> sandboxed pass can perform **Local integration** or **Promotion**."

## Flagged ambiguities

- "submodule" was used to mean **Subproject**. There are no Git submodules in
  this repo, so **Subproject** is the canonical term.
- "complete local integration test" was used for a full local stack. Resolved:
  call this an **End-to-end test**, and defer it from the current refactor.
- "local PR" was considered for Ralph's post-QA path. Resolved: call it
  **Local integration** because no GitHub PR object is created.
- "current working branch" was considered for Ralph branch selection. Resolved:
  use an explicit **Integration target** so worktree context does not choose
  where Ralph publishes.
- "gitflow agents" and "trunk agents" were considered for issue allocation.
  Resolved: use **Delivery mode** labels because the Ralph loop is the same
  agent workflow in both cases.
- "gh auth in the sandbox" was used ambiguously for GitHub Issues and Git push.
  Resolved: use **Sandboxed issue access** for issue metadata only; **Local
  integration**, **Integration target** pushes, and **Promotion** stay outside
  the sandbox.
- "operator runbook" and "agent loop" were used together for Ralph operation.
  Resolved: use **Operator workflow** for the human entrypoint and keep Ralph
  internals on the agent-facing Ralph documentation page.
- "post-promotion check" could imply a pre-push gate. Resolved: use
  **Post-promotion review** for the default review agent pass that runs after
  **Promotion** attempts where possible.
- "queue review" after each issue could be confused with
  **Post-promotion review**. Resolved: use **Ready issue refresh** for
  post-**Local integration** queue reconciliation before the next ready issue
  claim.
