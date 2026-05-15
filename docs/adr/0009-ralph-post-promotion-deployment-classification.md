# Ralph Classifies Post-Promotion Deployment Need

Ralph **Promotion** already records the promoted changed-file inventory, runs the
aggregate **Push check**, records the promoted commit inventory, closes verified
issues, runs **Post-promotion review**, and may run **Ready issue refresh**.
After a successful Promotion, operators still need a deterministic answer to
whether the promoted range requires no deployed AWS action, a Dagster user-code
redeploy, or the full deployed AWS workflow.

The repository also needs a clear credential boundary. Promotion runs inside
Ralph's outer loop, but sandboxed Codex subprocesses and **Post-promotion
review** do not own AWS or Pulumi credentials. Direct `$ralph-loop promote`
therefore must not silently run deployed workflow commands.

## Decision

Ralph records **Post-Promotion deployment classification** from the Promotion
changed-file inventory and prints the recommended deployment action. The
classifier is pure and path based:

- `no_deployment`: no AWS deployment is recommended. A Promotion containing
  only **Agent workflow changes** selects this tier with an explicit skip
  reason.
- `user_code_redeploy`: deployed AEMO ETL user-code runtime paths changed and
  no full deployed AWS workflow path changed. The recommendation is
  `infrastructure/aws-pulumi/scripts/redeploy-user-code`.
- `full_deployed_workflow`: Pulumi, service runtime, image, Dagster core, auth,
  Caddy, Marimo, code-location topology, or mixed deployed-platform paths
  changed. The recommendation is
  `infrastructure/aws-pulumi/scripts/run-integration-tests`.

When a Promotion mixes **Agent workflow changes** with deployable paths, Ralph
classifies from the deployable subset and reports the Agent workflow paths as
non-triggering context. Direct `$ralph-loop promote` records the decision under
`deployment_classification` in the Promotion manifest and prints the
recommendation, but does not invoke AWS, Pulumi, or deployment scripts.

The **AWS/Pulumi credential boundary** remains in the operator/Ralph outer loop:
deployment commands may run only when an operator or future Ralph outer-loop
automation explicitly owns the AWS and Pulumi credentials. Sandboxed Codex
subprocesses and **Post-promotion review** remain outside that credential
boundary.

## Consequences

Operators can review the Promotion manifest and terminal output to decide the
post-Promotion deployed action without re-reading every changed path. Agent
workflow-only Promotions have a deterministic no-deploy rule, so Ralph changes
do not create needless AWS work.

The user-code redeploy tier preserves the narrow existing AWS Pulumi command for
Dagster user-code image, task definition, and ECS service updates. Platform,
service runtime, image, Dagster core, auth, Caddy, Marimo, Pulumi, and
code-location topology changes stay on the full deployed AWS workflow because
they can affect resources outside the targeted user-code redeploy.

This ADR does not add automatic deployment execution. A future ADR can define a
Ralph-owned deployment executor, credential checks, retry behavior, and
manifest evidence for AWS/Pulumi command execution.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `CONTEXT.md`
  - `OPERATOR.md`
  - `docs/agents/ralph-loop.md`
  - `tools/ralph-loop/README.md`
  - `scripts/ralph.py`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
  - `tools/ralph-loop/tests/unit/test_ralph.py`
  - `infrastructure/aws-pulumi/scripts/redeploy-user-code`
  - `infrastructure/aws-pulumi/scripts/run-integration-tests`
- `sync.scope`: `operations, deployment`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `cd tools/ralph-loop && make unit-test`
  - `cd tools/ralph-loop && make run-prek`
  - `python3 -m unittest discover -s tests`
  - `verify deployment tiers and credential boundary match Ralph behavior`
