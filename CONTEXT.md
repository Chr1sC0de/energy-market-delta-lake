# Energy Market Delta Lake

This context defines repo-wide language for the Energy Market Delta Lake
monorepo. It captures terms that affect project structure, test scope, and
engineering decisions across subprojects.

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
The Ralph success path that squash-merges validated issue work onto latest
`origin/main`, pushes `main`, comments evidence, and closes the issue without a
GitHub PR.
_Avoid_: Local PR, draft PR gate

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
- **Local integration** happens after Ralph implementation QA and before closing
  the GitHub issue.
- **Local integration** is not a **Test lane**.

## Example dialogue

> **Dev:** "Should this Dagster asset materialization stay in the unit lane?"
> **Domain expert:** "No. It uses the Dagster runtime in process, so it is a
> **Component test**. Keep only pure transforms and mocked helpers as
> **Unit tests**."

## Flagged ambiguities

- "submodule" was used to mean **Subproject**. There are no Git submodules in
  this repo, so **Subproject** is the canonical term.
- "complete local integration test" was used for a full local stack. Resolved:
  call this an **End-to-end test**, and defer it from the current refactor.
- "local PR" was considered for Ralph's post-QA path. Resolved: call it
  **Local integration** because no GitHub PR object is created.
