# Ralph Uses Adaptive Vocabulary With Verified-Only Recovery

Ralph now needs one vocabulary for shaped issue size, hidden coupling pressure,
remaining queue work, and recovery after a boundary has already been crossed.
Later implementation issues should use that vocabulary without exposing the
numerical ODE metaphor as product language.

## Decision

Ralph documentation uses these terms:

- **Step size**: the size and reversibility of a Ralph work slice, not a runtime
  execution step. Smaller steps have bounded changed files, clear **Test lane**
  evidence, and recovery that stays inside one issue or queue update.
- **Stiffness ratio**: hidden-coupling and blast-radius pressure divided by the
  slice's safe feedback step. The current `$shape-issues` gate emits explicit
  `step_size`, `safe_feedback_step`, `hidden_coupling_pressure`, `ratio`,
  `ratio_level`, and `recommended_action` fields, while retaining the legacy
  0-100 stiffness score and level for compatibility.
- **Residual work**: the verified remaining delta after **Local integration**,
  failed metadata publication, failed **Promotion**, or **Ready issue refresh**.
- **Adaptive event**: one of `hard_stop`, `gated_retry`, or `residual_update`.

The initial score thresholds use the existing `$shape-issues` gate score:

- score below `55`: normal issue shaping can continue when the **Issue context
  assessor** passes and the issue declares one **Delivery mode**.
- score from `55` through `69`: route to `human-review` unless the Operator
  narrows the Step size or records an override.
- score `70` or higher: route to `split` by default. The Operator may choose
  **Exploratory delivery** only when durable human review is the reason and the
  issue includes `## Review focus`.

The structured Stiffness ratio bands are `low < 1.5`, `medium < 2.5`,
`high < 4.0`, and `extreme >= 4.0` by default. Medium ratio evidence remains
visible for Operator review. High ratio evidence requires split or an Operator
override, and extreme ratio evidence requires split or **Exploratory delivery**
with `## Review focus` plus **Issue completion review**.

High-stiffness evidence in an already ready issue does not rewrite the
**Delivery mode**. It triggers **Issue completion review** after QA and before
**Local integration**, a Trunk push, or Exploratory handoff. Ralph accepts both
legacy score evidence and structured `## Stiffness estimate` ratio fields; high
or extreme ratio levels, explicit completion-review requirements, and Operator
overrides that require review all preserve that review gate.

Adaptive events have these boundaries:

- `gated_retry`: a Codex, QA, or **Issue completion review** gate failed before
  any **Integration target** update or Exploratory branch push. Ralph may retry
  only while the issue has `--max-codex-attempts` budget.
- `hard_stop`: Ralph stops automatic recovery because continuing would risk an
  inconsistent queue, unsafe environment, partial push, or policy boundary.
  `hard_stop` has no automatic Codex retry and does not consume the per-issue
  Codex attempt budget.
- `residual_update`: Ralph has verified the crossed boundary and can update the
  remaining queue or GitHub Issue metadata without changing code.

Post-push metadata recovery is verified-only. Ralph may repair comments, labels,
body text, or issue closure only after it verifies that the recorded **Local
integration**, Exploratory handoff, accepted Exploratory commit, or
**Promotion** commit is reachable from the expected **Integration target** or
promoted range and that the run manifest still carries the recorded QA evidence.
Same-run Operator recovery then treats **Ready issue refresh** as residual queue
work: after metadata recovery it records refresh as pending, uses the existing
refresh analysis and mutation path under the claim gate, and records claim
resume only after refresh completes or the Operator explicitly disabled it. If
Ralph cannot verify the boundary, it must stop as `hard_stop` and require
operator inspection before any manual metadata change.

Runtime feedback is queue-local unless an Operator changes policy. Ralph may use
an adaptive event to steer the current issue run, checkpointed Operator cycle,
or **Ready issue refresh** candidate set. It must not adjust future thresholds,
global retry budgets, **Delivery mode** policy, or maintained docs/config
without an explicit Operator-owned policy change.
**Ready issue refresh** may include completed issue ratio evidence, adaptive
events, residual work, blocker notes, split notes, and candidate routing hints
in its prompt and mutation metadata. Those fields remain evidence for bounded
queue-local issue metadata updates; they are not a policy publication channel.
When a refresh mutation plan is unsafe but the live queue can be made safe
without changing code, Ralph records candidate-level warning statuses such as
`auto_normalized_closed_blockers`, `skipped_invalid_plan`, or
`quarantined_needs_triage` and completes refresh with warnings. This is still a
`residual_update` style queue repair: malformed JSON, missing mutation plans,
auth failures, network failures, and GitHub write failures remain `hard_stop`
boundaries for implementation refresh.

## Considered options

- Expose the ODE metaphor directly: preserves the origin of the idea, but
  forces later issue authors to learn an implementation metaphor instead of the
  repo's operational terms.
- Let each issue define local terms: avoids upfront documentation, but makes
  Step size, stiffness, retry, and residual recovery evidence inconsistent
  across Ralph runs.
- Define repo-local adaptive vocabulary and keep recovery verified-only:
  gives later implementation slices stable names, reuses the existing
  `$shape-issues` thresholds, and keeps post-push repair inside Ralph's evidence
  boundary.

## Consequences

Issue shaping can discuss Step size and Stiffness ratio without changing the
canonical **Delivery mode** vocabulary. The `$shape-issues` gate remains the
first routing surface: low score or ratio evidence can proceed, medium evidence
needs human review or narrowing, and high score or ratio evidence splits unless
an Operator records an override. Extreme ratio evidence needs split or
**Exploratory delivery** with explicit review focus.

Ralph run manifests record adaptive-event evidence without changing recovery
policy. `gated_retry` remains tied to the per-issue Codex attempt budget and
only applies before a pushed boundary. `hard_stop` remains an outer-loop stop
that preserves evidence, records no automatic retry and no attempt-budget
consumption, and requires inspection. `residual_update` keeps verified
follow-on metadata changes separate from unverified code repair.

Verified-only post-push recovery prevents Ralph from hiding a partial publish.
If code reached the expected branch and QA evidence is still recorded, Ralph can
repair issue metadata. If verification fails, operators inspect branch state,
run manifests, and GitHub Issue state before choosing manual recovery.
Checkpointed Operator runs can apply that verified metadata repair in the same
Operator cycle after a child implementation stops with a post-push metadata
failure. The Operator still uses the same boundary: manifest push evidence,
passed QA evidence, and commit reachability from the recorded **Integration
target**. Successful same-run repair is recorded as `residual_update` evidence;
if the child run had already recorded a drain-scheduler fatal stop, that marker
is updated to recovered before the child run is marked succeeded. Unverified
commits or missing boundary evidence remain `hard_stop` recovery states with no
GitHub Issue metadata mutation.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `AGENTS.md`
  - `OPERATOR.md`
  - `.agents/skills/shape-issues/SKILL.md`
  - `.agents/skills/shape-issues/references/gate-contract.md`
  - `.agents/skills/shape-issues/scripts/shape_issue_gate.py`
  - `.agents/skills/ralph-loop/SKILL.md`
  - `.agents/skills/ralph-issue-refresh/SKILL.md`
  - `docs/agents/README.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/ralph-loop.md`
  - `scripts/ralph.py`
  - `tools/ralph-loop/README.md`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
  - `tools/ralph-loop/tests/unit/test_ralph.py`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `cd tools/ralph-loop && make run-prek`
  - `verify adaptive vocabulary, thresholds, and verified-only recovery boundary`
