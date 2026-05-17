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
**Post-promotion review** keeps read-only issue commands; Ralph-owned
validated follow-up creation happens outside arbitrary sandboxed issue mutation.
_Avoid_: Full GitHub sandbox auth, Git push sandbox auth

**Full-access implementation pass**:
The operator-approved Ralph implementation mode for ready issues whose
`## Context anchors` include `.agents/` paths. The Codex implementation
subprocess runs with full filesystem access, keeps **Sandboxed issue access**
read-only, and must leave a diff confined to the issue's context anchors before
QA or **Local integration** can proceed.
_Avoid_: Agent auto-escalation, unrestricted agent drain

**Issue completion review**:
The automated Ralph review gate that runs after implementation QA has passed
and before **Local integration**, Trunk push, or Exploratory handoff for risky
issue work. It triggers for deployable changed paths, **Agent workflow changes**,
**Trunk delivery**, and high-stiffness issue evidence; failing findings feed
Codex repair attempts from the same per-issue implementation budget.
_Avoid_: Human dev review, Ready issue refresh, Post-promotion review

**Ready issue refresh**:
The Ralph queue-maintenance pass that reconciles open GitHub Issues after a
successful **Local integration** or Exploratory handoff and before the next
`ready-for-agent` issue claim. It may refresh issue context, labels, blockers,
or completed closure evidence so the queue reflects the latest **Integration
target** state.
_Avoid_: Post-promotion review, triage pass

**Operator workflow**:
The human workflow for shaping work, preparing GitHub Issues, draining Ralph,
reviewing `dev`, and running **Promotion**.
_Avoid_: Agent loop, Ralph internals

**Documentation sync**:
The maintained-doc workflow that maps changed repo paths to docs through
`sync.sources`, updates matched docs or records no-change decisions, and
validates metadata, links, anchors, and routes through doc QA and the relevant
**Commit check**.
_Avoid_: Doc sync, best-effort docs update

**Agent skill**:
A reusable local workflow instruction bundle invoked as `$skill-name`.
_Avoid_: AI skill, generic AI capability

**Agent workflow change**:
A change limited to repo-local agent instructions, Ralph loop code,
issue-shaping skills, or operator documentation. Agent workflow changes can
alter how Ralph works, but they do not change deployed AWS runtime resources by
themselves.
_Avoid_: Agent deployment change

**Issue context assessor**:
The bounded `$shape-issues` gate provider that judges whether each draft issue's
declared `Path:` and `Doc:` anchors plus deterministic `rg` evidence snippets
give an implementation agent enough context to work independently. It reports a
per-issue `pass`, `weak`, or `fail` verdict before publication; it is not a
repo exploration pass.
_Avoid_: Embedding coverage, semantic coverage, model corpus scoring

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
The opt-in **Delivery mode** where Ralph publishes issue work to a durable
**Exploratory branch** from `origin/main`, marks the issue `agent-reviewing`,
and leaves it open for human review. Accepted review work can later be merged
to `dev` and enter **Promotion** through explicit acceptance evidence.
_Avoid_: Draft PR mode, branch-only PR

**Exploratory branch**:
The durable per-issue branch Ralph publishes for **Exploratory delivery**.
The default branch name is `agent/exploratory/issue-N-slug`; Ralph creates it
from `origin/main`, refuses to overwrite an existing remote branch, and never
includes it in automatic **Promotion** unless a human accepts the work by
merging it to `dev` with explicit issue evidence.
_Avoid_: Draft PR branch, temporary review worktree

**Exploratory acceptance review**:
The non-mutating Operator review state and artifact for open
`agent-reviewing` issues. It summarizes durable **Exploratory branches** that
need human acceptance or rejection before blocked ready work, drain, or
**Promotion** can continue.
_Avoid_: Queue failure, Promotion gate

**Promotion**:
The Ralph operation that merges reviewed `dev` work into `main` and closes
verified GitHub issues included in that branch range, including Gitflow
**Local integration** commits and accepted Exploratory commits.
_Avoid_: Manual dev merge

**Post-promotion review**:
The default Ralph review agent pass that runs after a **Promotion** attempt with
changed files where a review worktree is available. Successful Promotions run it
after `main` is pushed, `dev` is synced, and verified issue metadata updates
complete; failed or partial Promotion attempts try it as warning-only recovery
review without changing the original Promotion outcome. Successful Promotions
may then create structured actionable follow-up GitHub Issues through Ralph's
validated create-only helper.
_Avoid_: Promotion gate, pre-push review

**Post-Promotion deployment classification**:
The deterministic Ralph decision recorded from a **Promotion** changed-file
inventory. It chooses `no_deployment`, `user_code_redeploy`, or
`full_deployed_workflow`, reports non-triggering **Agent workflow changes** as
context, and prints the recommended deployment action without running AWS or
Pulumi commands.
_Avoid_: Automatic deploy, deployment gate

**AWS/Pulumi credential boundary**:
The Ralph outer-loop boundary for deployed AWS workflow credentials. Direct
**Promotion** may classify and recommend deployment, but AWS and Pulumi commands
run only when an operator or future Ralph outer-loop automation explicitly owns
those credentials; sandboxed Codex subprocesses and **Post-promotion review**
do not receive them.
_Avoid_: Sandbox AWS auth, implicit Pulumi deploy

**Fit-plus-extend modeling**:
A data-platform modeling policy where new source coverage reuses existing shared
facts and dimensions when the source grain and meaning match, then adds a new
shared fact when the source has a real grain that does not fit current assets.
_Avoid_: Force-fit modeling, source-only area

**Source-spec gap**:
A live source artifact that the platform can discover or land, but does not yet
model as curated coverage because the repository lacks a usable source
definition for its fields, grain, and meaning.
_Avoid_: Implemented gap, ignored report

**Gas market knowledge base**:
The repo-level **Subproject** at `tools/gas-market-knowledge-base` for turning
gas-market source documents into reviewable text artifacts for agents and
operators. AEMO ETL keeps discovering and archiving source PDF bytes; the
knowledge base owns PDF text extraction, retrieval chunks, and cited gold
knowledge pages after those pipeline slices are implemented.
_Avoid_: AEMO ETL wiki, vector store, PDF side effect

**Market context**:
A cited, agent-authored gold knowledge page that synthesizes gas-market source
documents for a named market, artifact, concept, or workflow. It belongs to the
**Gas market knowledge base** corpus and must cite the extracted text artifacts
it uses.
_Avoid_: Uncited summary, fully automated wiki page

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
- **Local integration** happens after Ralph implementation QA and any required
  **Issue completion review** for **Trunk delivery** and **Gitflow delivery**,
  before either issue closure or **Promotion**.
- **Local integration** is not a **Test lane**.
- **Sandboxed issue access** may update GitHub Issue metadata when the Ralph
  phase grants write commands, but it must not update an **Integration target**.
- A **Full-access implementation pass** is allowed only when the operator passes
  the explicit Ralph flag and the ready issue anchors `.agents/` work; it keeps
  GitHub Issue commands read-only inside the subprocess and fails before QA if
  changed files leave the issue anchors.
- **Ready issue refresh** runs after a successful **Local integration** or
  **Exploratory delivery** handoff and before Ralph claims the next
  `ready-for-agent` issue in a drain.
- **Ready issue refresh** may mutate GitHub Issue metadata under its audit
  contract; it is not **Promotion** and is not **Post-promotion review**.
- **Issue completion review** is a pre-**Local integration** automated gate on a
  single implemented issue. It is not human `dev` review, it is not **Ready
  issue refresh**, and it is not **Post-promotion review**.
- A checkpointed **Operator workflow** drain uses the same lane-aware scheduler
  as plain drain: Gitflow and Trunk attempts stay serial, eligible
  **Exploratory delivery** attempts use the configured worker pool, and one
  Operator cycle may record multiple issue checkpoints before **Promotion**.
- **Promotion** in a checkpointed **Operator workflow** starts only after active
  Exploratory workers, implementation **Ready issue refresh** gates, and
  scheduler metadata updates have settled.
- The **Operator workflow** is the human entrypoint; Ralph internals remain on
  the agent-facing Ralph documentation page.
- **Documentation sync** is not a **Test lane**. It is a maintained-doc
  contract validated through doc QA and the relevant **Commit check**.
- **Documentation sync** runs when changed repo paths match maintained doc
  `sync.sources`, or when a change introduces new behavior that needs maintained
  doc coverage.
- An **Agent skill** can support the **Operator workflow** or Ralph internals,
  but it is not itself a **Delivery mode**, **Test lane**, or **Integration
  target**.
- The **Issue context assessor** is part of the in-development
  `$shape-issues` workflow. Replacing the earlier draft coverage mechanism does
  not require an ADR because it does not establish a durable repo architecture
  decision.
- A **Delivery mode** selects an **Integration target**.
- **Gitflow delivery** uses `dev` as the default **Integration target**.
- **Trunk delivery** uses `main` as the default **Integration target**.
- **Exploratory delivery** uses an **Exploratory branch** as the default
  **Integration target** and pushes that branch without a **Local integration**
  squash merge.
- An **Exploratory branch** stays outside automatic **Promotion** until accepted
  review evidence records the `dev` commit that made the work reachable from
  the Gitflow source branch.
- **Exploratory acceptance review** is a named Operator stop state, not an
  implementation failure. It does not push, comment, edit labels, close issues,
  or update **Integration targets**; it writes review artifacts for the human
  decision on `agent-reviewing` issues.
- **Promotion** closes only issues whose Gitflow `dev` integration commit or
  accepted Exploratory commit is verified in the promoted branch range.
- **Post-promotion review** happens after **Promotion** attempts where possible;
  it is not a **Push check** gate and it is not **Ready issue refresh**. The
  review agent uses read-only GitHub Issue access. After successful
  **Promotion**, Ralph may create follow-up issues from structured review drafts
  through a validated create-only helper: valid drafts become
  `ready-for-agent`, invalid drafts become `needs-triage`, and helper failures
  are warning-only because `main` has already been pushed.
- **Post-Promotion deployment classification** happens from the promoted
  changed-file inventory. **Agent workflow changes** alone choose
  `no_deployment`; deployed AEMO ETL user-code runtime paths choose
  `user_code_redeploy`; deployed AWS platform, service runtime, image, Dagster
  core, auth, Caddy, Marimo, Pulumi, or code-location topology paths choose
  `full_deployed_workflow`.
- The **AWS/Pulumi credential boundary** keeps deployment credentials outside
  sandboxed Codex subprocesses. Direct **Promotion** records and prints a
  deployment recommendation, but does not run AWS or Pulumi commands.
- **Fit-plus-extend modeling** keeps shared data-platform tables aligned to
  domain grain: source rows join existing shared facts and dimensions where the
  meaning matches, and new shared facts are added only for distinct source
  grains.
- A **Source-spec gap** may be discovered or landed, but it remains outside
  curated **Fit-plus-extend modeling** until a usable source definition is
  available.
- The **Gas market knowledge base** is a separate **Subproject**, not a side
  effect of AEMO ETL asset materialization.
- **Market context** pages are gold corpus artifacts for cited explanation.
  They are not source PDF bytes, silver retrieval chunks, or uncited generated
  summaries.

## Example dialogue

> **Dev:** "Should this Dagster asset materialization stay in the unit lane?"
> **Domain expert:** "No. It uses the Dagster runtime in process, so it is a
> **Component test**. Keep only pure transforms and mocked helpers as
> **Unit tests**."
>
> **Dev:** "Can the sandboxed Codex pass close or label an issue during Ralph?"
> **Domain expert:** "Only when that Ralph phase grants issue write commands
> through **Sandboxed issue access**. **Ready issue refresh** may mutate issues
> under its audit contract, but the **Post-promotion review** agent is
> read-only. Ralph may create validated follow-up issues after successful
> **Promotion** through its helper, and no sandboxed pass can perform
> **Local integration**, Exploratory handoff, or **Promotion**."
>
> **Dev:** "Can Ralph edit `.agents` workflow files during drain?"
> **Domain expert:** "Only through a **Full-access implementation pass**. The
> issue must anchor `.agents/` paths, the operator must pass the explicit flag,
> and Ralph must verify the resulting diff stays inside the issue anchors before
> any QA or **Local integration**."
>
> **Dev:** "Is `$shape-issues` an AI capability or an **Agent skill**?"
> **Domain expert:** "It is an **Agent skill**: a reusable local workflow
> instruction bundle invoked by name inside the **Operator workflow**."
>
> **Dev:** "Did this **Promotion** deploy because Ralph changed itself?"
> **Domain expert:** "No. A promoted **Agent workflow change** is
> non-triggering context for **Post-Promotion deployment classification**.
> Ralph records and prints `no_deployment` unless deployable AWS or AEMO ETL
> user-code runtime paths are also in the changed-file inventory."

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
  integration**, Exploratory handoff, **Integration target** pushes, and
  **Promotion** stay outside the sandbox.
- "full access" was used ambiguously for filesystem access, GitHub issue
  mutation, and Git push. Resolved: use **Full-access implementation pass** only
  for operator-approved `.agents/` filesystem edits; GitHub Issue commands stay
  read-only inside that pass and **Local integration**, **Integration target**
  pushes, and **Promotion** stay in Ralph's outer loop.
- "operator runbook" and "agent loop" were used together for Ralph operation.
  Resolved: use **Operator workflow** for the human entrypoint and keep Ralph
  internals on the agent-facing Ralph documentation page.
- "AI skill" was used for repo-local workflow instructions. Resolved: use
  **Agent skill** because skills are reusable local instruction bundles invoked
  as `$skill-name`, not generic model abilities.
- "post-promotion check" could imply a pre-push gate. Resolved: use
  **Post-promotion review** for the default review agent pass that runs after
  **Promotion** attempts where possible.
- "queue review" after each issue could be confused with
  **Post-promotion review**. Resolved: use **Ready issue refresh** for
  post-**Local integration** or Exploratory handoff queue reconciliation before
  the next ready issue claim.
- "completion review" could be confused with the human review of `dev` before
  **Promotion**. Resolved: use **Issue completion review** only for Ralph's
  automated pre-**Local integration** gate on risky issue work.
- "post-Promotion deploy" could imply that direct `$ralph-loop promote` owns
  AWS credentials and runs deployment commands. Resolved: use
  **Post-Promotion deployment classification** for the report-only decision and
  **AWS/Pulumi credential boundary** for the operator-owned credential line.
- "review branch" could imply a GitHub PR branch or a temporary worktree.
  Resolved: use **Exploratory branch** for the durable branch Ralph publishes
  during **Exploratory delivery**.
- "STTM-only area" and "force every STTM report into current facts" were
  considered for `gas_model` expansion. Resolved: use **Fit-plus-extend
  modeling** so matching grains enrich shared assets and distinct grains become
  new shared facts.
- "wiki", "vector store", and "PDF extraction inside AEMO ETL" were considered
  for the gas-market document corpus. Resolved: use **Gas market knowledge
  base** for the separate Subproject, and use **Market context** for cited gold
  pages authored from extracted text artifacts.
