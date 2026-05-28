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
The checkpointed **Operator workflow** can own those credentials in the Ralph
outer loop after **Promotion** cleanup has completed.

The same pure path classifier can also identify risky issue attempts before
**Local integration**. That pre-integration use is a review trigger only:
**Issue completion review** may run for deployable changed paths, but it still
does not run AWS, Pulumi, or deployment scripts.
Security-sensitive path classification follows the same review-trigger pattern:
it can require **Issue completion review**, but it does not change
**Post-Promotion deployment classification** and does not run deployment,
scanner, AWS, or Pulumi commands.

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
  `infrastructure/aws-pulumi/scripts/run-integration-tests --with-idempotency`.

When a Promotion mixes **Agent workflow changes** with deployable paths, Ralph
classifies from the deployable subset and reports the Agent workflow paths as
non-triggering context. Direct `$ralph-loop promote` records the decision under
`deployment_classification` in the Promotion manifest and prints the
recommendation, but does not invoke AWS, Pulumi, or deployment scripts.
Issue attempts reuse the same classification snapshot in the implementation
manifest when **Issue completion review** is required by deployable paths.

Ralph also records source-table archive replay recovery guidance alongside, not
inside, the deployment tier. When a Promotion changes `surrogate_key_sources`
for an existing AEMO ETL `df_from_s3_keys` raw source-table definition, Ralph
compares the Promotion base and source revision, maps the changed definition to
its source-table ID, and writes `source_table_replay_recovery` in the Promotion
manifest. Each affected table records old and new key sources plus dry-run and
`--replace` commands from the AEMO ETL **Subproject**:

```bash
uv run aemo-replay-bronze-archive --table <table>
uv run aemo-replay-bronze-archive --table <table> --replace
```

This recovery guidance does not change the deployment tier. A promoted
source-table key migration can still classify as `user_code_redeploy`; the
archive replay commands are additional operator recovery instructions.

The checkpointed Operator path consumes the recorded decision after successful
Promotion metadata updates, **Post-promotion review**, follow-up creation, and
post-Promotion **Ready issue refresh**. It records `deployment_execution` in
the Promotion child manifest and a deployment checkpoint in the Operator
manifest. `no_deployment` skips command execution. `user_code_redeploy` runs
`infrastructure/aws-pulumi/scripts/redeploy-user-code`. The
`full_deployed_workflow` tier runs
`infrastructure/aws-pulumi/scripts/run-integration-tests --with-idempotency` so
the log carries both **Deployed test** evidence and full-tier idempotency
evidence.

The **AWS/Pulumi credential boundary** remains in the operator/Ralph outer loop:
deployment commands may run only when the checkpointed Operator path or another
explicit Ralph outer-loop automation owns the AWS and Pulumi credentials.
Sandboxed Codex subprocesses and **Post-promotion review** remain outside that
credential boundary. Source-table archive replay follows the same boundary:
Ralph may record and print `aemo-replay-bronze-archive` dry-run and `--replace`
commands, but direct Promotion and sandboxed **Post-promotion review** must not
run them.
Allowlisted **Operator smoke** commands for selected **Exploratory delivery**
issues use the same boundary: Codex may prepare scripts and docs, but the
credentialed deployed smoke runs only from Ralph's operator-owned outer loop
after the **Exploratory branch** is pushed.
AFK issue QA for deployable infrastructure work may update local tests and
future deployed-test expectations, but it does not run `pulumi up`, AWS CLI
live checks, deployed tests, or
`infrastructure/aws-pulumi/scripts/run-integration-tests`.

## Consequences

Operators can review the Promotion manifest and terminal output to decide the
post-Promotion deployed action without re-reading every changed path. Agent
workflow-only Promotions have a deterministic no-deploy rule, so Ralph changes
do not create needless AWS work.

Operators can also see when source-table key migrations need table-specific
archive replay. The manifest preserves deterministic table IDs and commands, so
operators can dry-run the archive scope before replacing current-state bronze
tables whose old key shape may have left retained rows that normal ingestion
will not delete.

The user-code redeploy tier preserves the narrow existing AWS Pulumi command for
Dagster user-code image, task definition, and ECS service updates. Platform,
service runtime, image, Dagster core, auth, Caddy, Marimo, Pulumi, and
code-location topology changes stay on the full deployed AWS workflow because
they can affect resources outside the targeted user-code redeploy.

Direct `$ralph-loop promote` remains report-only. The checkpointed Operator path
now adds the bounded deployment executor and a failure-only deploy-repair issue
creation pass. When the checkpointed deployment command or its **Deployed test**
evidence fails, Ralph analyzes redacted deployment evidence without AWS/Pulumi
credentials, validates structured repair drafts, creates valid `bug`
`ready-for-agent` issues with exactly one **Delivery mode** label, and
downgrades incomplete drafts to `needs-triage`. Valid ready deploy-repair issues
are targeted through checkpointed Operator state, not general priority labels.
The targeted repair issue still follows normal implementation, **Local
integration**, **Promotion**, and deployment retry; successful deployment clears
the target state. One Operator run starts at most two automated deploy-repair
cycles before stopping with recovery guidance and preserved logs. It still does
not add a separate credential preflight beyond the invoked AWS/Pulumi command
failures recorded in the manifests.

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
  - `docs/adr/0013-ralph-security-sensitive-issue-completion-review.md`
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
