# Documentation Sync Workflow

This page owns the maintained-doc contract, sync metadata rules, and doc QA
ratchets. It keeps documentation updates tied to the files that can make the
docs stale.

## Table of contents

- [Maintained docs](#maintained-docs)
- [Explicit exclusions](#explicit-exclusions)
- [Sync metadata contract](#sync-metadata-contract)
- [Code-change workflow](#code-change-workflow)
- [Automated doc QA](#automated-doc-qa)
- [Documentation QA ratchets](#documentation-qa-ratchets)
- [Issue reconciliation](#issue-reconciliation)
- [Search commands](#search-commands)
- [Related docs](#related-docs)

## Maintained docs

The sync workflow applies to maintained Markdown files in these paths:

- `README.md`
- `OPERATOR.md`
- `docs/**/*.md`
- maintained `backend-services/**/*.md`
- `infrastructure/aws-pulumi/**/*.md`
- `backend-services/dagster-user/aemo-etl/**/*.md`
- `tools/ralph-loop/**/*.md`
- `tools/gas-market-knowledge-base/README.md`

Each maintained doc must end with a visible `## Sync metadata` section.

## Explicit exclusions

Maintained-doc discovery intentionally excludes generated, vendored, cached, and
runtime-only paths:

- `.ralph/`
- `.shape-issues/`
- `.venv/`
- `.git/`
- `.mypy_cache/`
- `.pytest_cache/`
- `.ruff_cache/`
- `__pycache__/`
- `generated/`
- `node_modules/`
- `vendor/`
- `specs/`

The removed legacy `specs/` tree stays out of scope. New maintained design or
migration docs should live under the maintained documentation paths above and
carry sync metadata.

ADR [0010](../adr/0010-gas-market-knowledge-base.md) reserves the external
`$ENERGY_MARKET_CORPUS_ROOT/gas-market/{bronze,silver,gold}` tree for
**Gas market knowledge base** corpus artifacts and
`$ENERGY_MARKET_CORPUS_ROOT/aemo-major-publications/{bronze,silver,gold}` for
the AEMO major publications fixture corpus. Those generated text artifacts are
not maintained router docs under this workflow. The
`tools/gas-market-knowledge-base/README.md` Subproject doc is maintained, but
generated Markdown under that Subproject's explicit `generated/` tree and under
the external corpus root remains corpus output rather than maintained
documentation.

## Sync metadata contract

Required keys:

- `sync.owner`
- `sync.sources`
- `sync.scope`
- `sync.qa`

Formatting rules:

- keep `sync.sources` as repo-relative literal paths
- put one source path on each line
- only list files whose changes are likely to require doc updates
- keep the section at the bottom of the file so reader-facing content stays
  first

## Code-change workflow

Use this flow after implementation changes:

1. Check the changed files with `git diff --name-only`.
2. Search the maintained docs for each changed path.
3. Update every doc whose `sync.sources` contains that path.
4. Run doc QA before commit.

If a changed code file has no matching docs, either add the missing coverage or
explicitly confirm that the file is intentionally undocumented.

If a matching doc does not need any wording changes, record that decision
during review instead of assuming the doc is still correct.

## Automated doc QA

The root unittest suite checks documentation invariants that are too important
to leave as review-only guidance:

- maintained-doc discovery honors the explicit exclusions above
- every maintained doc has required `## Sync metadata`
- every listed `sync.sources` path exists
- internal Markdown file links and anchors resolve
- `docs/README.md` covers the required human task and Subproject routes,
  including the Marimo **Dashboard standard**
- `docs/agents/README.md` covers the required agent workflow routes, including
  the Marimo **Dashboard standard**
- moved repo-level docs do not leave stale references to old paths

Run the automated doc QA with:

```bash
python3 -m unittest discover -s tests
```

The repository **Commit check** also runs Markdown, link, and staged
secret-scan tooling through:

```bash
prek run -a
```

The root Markdown hooks do not carry generated corpus exclusions. Generated
bronze, silver, and gold corpus files are external artifact output, the legacy
`tools/gas-market-knowledge-base/generated/` tree is ignored, and the Gas
market knowledge base **Commit check** rejects staged generated corpus
artifacts before root Markdown linting needs to handle them.

## Documentation QA ratchets

The documentation QA ratchet is staged by **Subproject** and enforced through
the same `prek` command surfaces as code QA:

- The repo **Commit check** is `prek run -a` from the repository root. For a
  single **Subproject**, use that Subproject's documented **Commit check**
  command, such as `make run-prek` for `aemo-etl` or `prek run -a` from
  `infrastructure/aws-pulumi`. These **Commit check** surfaces are the local
  **Fast check** path: static checks plus **Unit tests** and **Component tests**,
  without containers, live network, or deployed cloud resources.
- The root **Commit check** includes the official Gitleaks `gitleaks` hook. It
  runs in staged pre-commit mode so newly staged secrets are blocked without
  requiring Docker or a preinstalled `gitleaks` binary. Public corpus false
  positives must use exact-fingerprint entries in `.gitleaksignore`; do not
  broadly exclude generated corpus directories from secret scanning.
- Ruff owns Python linting and formatting. A Python **Subproject** is under the
  Google-style docstring ratchet only when its `pyproject.toml` selects Ruff `D`
  rules and its hook config runs `ruff check`. The current ratchet covers
  `backend-services/authentication`, `backend-services/marimo`,
  `backend-services/dagster-user/aemo-etl`, `infrastructure/aws-pulumi`, and
  `tools/ralph-loop`, with each Subproject's pyproject defining its test,
  generated, schema-heavy, legacy-entrypoint, or package-controller exclusions.
  AEMO ETL, AWS Pulumi, and Ralph loop also select Ruff `C901` with scoped
  exclusions where existing controller code is intentionally above the default
  complexity threshold.
  `backend-services/dagster-core` is not currently on this ratchet.
- `shfmt` formats shell scripts.
- `shellcheck` checks shell correctness.
- `scripts/check_shell_script_headers.py` enforces shell documentation for
  executable shell scripts: a script with a shell shebang must have a human
  purpose/context comment block immediately after the shebang. Tool directives
  such as `shellcheck` or `shfmt` comments do not count as that human header.

Do not treat a future **Subproject** as covered by the ratchet until its own
hook and project config have been added and the maintained docs name those files
in `sync.sources`.

Most Python project hooks run through `uv run` inside the project that owns the
hook config. AWS Pulumi shell hooks, including `shfmt` and `shellcheck`, are
pinned in that Subproject's uv dev environment. The shared `backend-services`
shell lint hook pins `shellcheck-py` in its hook environment instead of relying
on the caller's `PATH`.

## Issue reconciliation

Issue #73 reconciles the related documentation and Ralph behavior issues this
way:

- #65: `OPERATOR.md` remains the human **Operator workflow** entrypoint, and
  `README.md`, `docs/README.md`, and `docs/agents/README.md` route operators to
  it instead of duplicating the full workflow.
- #66: `OPERATOR.md` remains under **Documentation sync** through this page's
  maintained-doc scope and its own sync metadata.
- #59 and #139: docs-only AEMO ETL and Marimo changes remain aligned with
  Ralph QA selection by keeping docs-only paths on the root doc **Commit check**
  surface. Mixed docs/runtime Marimo changes add Marimo **Component test** and
  **Commit check** evidence from `backend-services/marimo`.
- #57, #58, #61, #62, #88, #89, #91, #92, #94, #95, and #108: current Ralph
  behavior for **Delivery mode**, **Local integration**, Exploratory handoff,
  **Exploratory branch** review state, **Promotion**, accepted Exploratory
  evidence closure, manual Gitflow recovery Promotion closure evidence,
  **Sandboxed issue access**, **Full-access implementation pass**, writable QA
  runtime paths, unverified **Promotion** commit review context,
  **Post-promotion review**, and validated follow-up creation remain owned by
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md). Ralph's compatibility
  command remains `python3 scripts/ralph.py`, and its implementation, unit
  tests, and **Commit check** surface now live in the
  [tools/ralph-loop](../../tools/ralph-loop/README.md) Subproject. The
  **Exploratory branch** automatic-Promotion boundary is recorded in ADR
  [0005](../adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md)
  and the `.agents/` full-access boundary recorded in ADR
  [0007](../adr/0007-ralph-full-access-implementation-pass.md).
- #68: [docs/agents/ralph-loop.md](../agents/ralph-loop.md) defines the
  **Ready issue refresh** contract, including the shared language, audit prefix,
  optional `## Current context`, stale issue handling, and completed closure
  rules.
- #69: Ralph computes bounded **Ready issue refresh** candidates after
  drain-mode **Local integration** or Exploratory handoff using open issues from
  the existing `--issue-limit` scan, with Gitflow, trunk, and Exploratory
  blocker satisfaction described in
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #90: Exploratory-ready issues require `## Review focus` before Ralph can
  publish an Exploratory handoff. The contract and triage expectations live in
  [docs/agents/issue-tracker.md](../agents/issue-tracker.md),
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md), and
  [docs/agents/triage-labels.md](../agents/triage-labels.md).
- #70: Ralph now records a read-only **Ready issue refresh** analysis artifact
  after drain-mode **Local integration** or Exploratory handoff. The artifact
  plans issue updates without mutating GitHub Issues, and
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md) owns the manifest,
  prompt, and failure-stop contract.
- #71: Ralph applies validated **Ready issue refresh** metadata mutations after
  the read-only analysis artifact. Drain mode refreshes by default,
  `--skip-ready-issue-refresh` disables that default, and targeted `--issue`
  runs require `--ready-issue-refresh`. Mutation uses only GitHub Issue metadata
  commands, records per-candidate manifest status, and stops the drain with
  recovery guidance on partial post-**Local integration** metadata failures.
- #133: Parallel drains serialize implementation **Ready issue refresh** behind
  a scheduler claim gate. New claims pause while refresh analysis or metadata
  mutation runs, active Exploratory workers are allowed to finish, and
  **Ready issue refresh**, post-push metadata, or environment fatal stops record
  `drain_scheduler.fatal_stop` recovery evidence in child run manifests.
- #283: Ralph adaptive vocabulary defines Step size, Stiffness ratio, Residual
  work, `hard_stop`, `gated_retry`, and `residual_update` without exposing the
  numerical ODE metaphor. The initial stiffness thresholds and verified-only
  post-push metadata recovery boundary live in ADR
  [0011](../adr/0011-ralph-adaptive-vocabulary-and-verified-recovery.md), with
  operator-facing behavior in
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #127: Successful **Promotion** verified issue closures may trigger **Ready
  issue refresh** before the next ready issue claim. The checkpointed Operator
  loop enables post-Promotion refresh by default, direct `--promote` requires
  `--ready-issue-refresh`, and failures are warning-only because the Promotion
  commit and verified issue closures have already completed.
- #72: Ralph implementation prompts include bounded recent **Ready issue
  refresh** notes after the issue body while keeping the issue body as the
  primary implementation contract.
- #112: Ralph treats default Gitflow branch-sync conflicts and stale
  `agent-sync-main-into-dev` worktrees as drain-stopping pre-claim failures.
  The recovery contract, `branch_sync` manifest fields, and operator guidance
  live in [docs/agents/ralph-loop.md](../agents/ralph-loop.md), with the
  Delivery mode decision summarized in ADR
  [0002](../adr/0002-ralph-delivery-modes.md).
- #113: Ralph recovers implementation commit hooks that rewrite tracked files
  by staging the formatter-modified paths, rerunning the selected
  **Commit check** once, retrying the implementation commit, and recording
  `formatter_recovery` manifest evidence. Retry failures are classified as
  `formatter_rewrite_recovery_failure` with log paths and operator recovery
  guidance in [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #111: Ralph provides a checkpointed Operator run for repeated drain and
  **Promotion** cycles. The Codex-safe detached launch, compact
  `--operator-run-status` inspection, active child run heartbeat, child
  manifest links, checkpoint names, cycle guard, and recovery guidance live in
  [OPERATOR.md](../../OPERATOR.md) and
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #115: Completed or stopped checkpointed Operator runs write
  `operator-run-rollup.md` and `operator-run-rollup.json` beside
  `operator-run.json`. The durable rollups summarize issue outcomes, manual
  recoveries, **Local integration** commits, **Promotion** commits, QA
  surfaces, **Post-promotion review** follow-ups, final queue state, and stop
  or failure reasons without reading child Codex JSONL.
- #136: Checkpointed Operator runs treat `agent-reviewing` as a first-class
  queue state. When open **Exploratory branches** require human acceptance
  review before the queue can proceed, Ralph stops with
  `needs_review`, writes `exploratory-acceptance-review.md` and
  `exploratory-acceptance-review.json`, and keeps GitHub Issues and
  **Integration targets** unchanged. The contract lives in
  [OPERATOR.md](../../OPERATOR.md) and
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md), with the
  automatic-Promotion boundary in ADR
  [0005](../adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md).
- #165: Checkpointed Operator deployment failures may create deploy-repair
  GitHub Issues only through Ralph-owned deploy-failure analysis and validated
  create-only issue creation. The analyzer receives redacted deployment
  evidence, no AWS or Pulumi credentials, and cannot mutate GitHub Issues
  directly. Valid drafts become `bug` issues with exactly one **Delivery mode**
  label and `ready-for-agent`; incomplete drafts are downgraded to
  `needs-triage` with validation evidence. The contract lives in
  [OPERATOR.md](../../OPERATOR.md),
  [docs/agents/issue-tracker.md](../agents/issue-tracker.md),
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md), and ADR
  [0009](../adr/0009-ralph-post-promotion-deployment-classification.md).
- #263: Ralph **Promotion** records source-table archive replay recovery
  guidance when a promoted AEMO ETL `df_from_s3_keys` source-table definition
  changes `surrogate_key_sources`. The manifest stores affected source-table
  IDs and dry-run plus `--replace` `aemo-replay-bronze-archive --table`
  commands without running AWS, Pulumi, deployment, or archive replay commands
  from direct Promotion or sandboxed **Post-promotion review**. The contract
  lives in [OPERATOR.md](../../OPERATOR.md),
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md), ADR
  [0009](../adr/0009-ralph-post-promotion-deployment-classification.md), and
  ADR
  [0003](../adr/0003-bounded-current-state-bronze-source-tables.md).
- #168: Ralph owns the risk-based **Issue completion review** gate after
  implementation QA and before **Local integration**, Trunk push, or
  Exploratory handoff. The gate receives read-only GitHub Issue access, records
  review artifacts in the issue run, feeds failing findings into remaining
  Codex repair attempts, reruns selected QA and review after repair, and fails
  without updating an **Integration target** when the attempt budget is
  exhausted. The canonical term lives in [CONTEXT.md](../../CONTEXT.md), and
  the operational contract lives in [OPERATOR.md](../../OPERATOR.md),
  [docs/agents/issue-tracker.md](../agents/issue-tracker.md), and
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #292: Ralph Gitflow delivery owns a blocking **Review package** gate after
  final changed files, QA evidence, and any required **Issue completion
  review** are known, and before **Local integration** updates `dev`. The
  canonical term lives in [CONTEXT.md](../../CONTEXT.md), the operator contract
  lives in [OPERATOR.md](../../OPERATOR.md),
  [docs/agents/issue-tracker.md](../agents/issue-tracker.md), and
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md), and ADR
  [0012](../adr/0012-ralph-gitflow-review-package-gate.md) records the static
  HTML validation boundary.
- #294: Ralph Trunk delivery reuses the blocking **Review package** gate before
  **Local integration**, the `main` push, completion comments, `agent-merged`,
  or issue closure. The v1 operator contract lives in
  [OPERATOR.md](../../OPERATOR.md),
  [docs/agents/issue-tracker.md](../agents/issue-tracker.md), and
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md), and ADR
  [0012](../adr/0012-ralph-gitflow-review-package-gate.md) now records that
  Gitflow and Trunk share the static HTML validation boundary.
- #293: Ralph Review package media recipes can record sibling artifacts before
  publication. Changed configured Marimo notebook routes record desktop and
  narrow `.webm` files in the issue run directory, link them from the Review
  package for Gitflow and Trunk delivery, record media-only handoff evidence for
  Exploratory delivery, and fail before **Local integration**, **Integration
  target** push, or Exploratory handoff when capture fails. The contract lives in
  [docs/agents/issue-tracker.md](../agents/issue-tracker.md),
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md), ADR
  [0012](../adr/0012-ralph-gitflow-review-package-gate.md), and the
  [Marimo dashboard standard](../../backend-services/marimo/docs/dashboard-standard.md).
- #166: Checkpointed Operator runs record valid deploy-repair issues in
  `deploy_repair.target_issue`, select that issue before unrelated ready work,
  clear the target after a successful deployment retry, and stop after two
  automated deploy-repair cycles. The contract lives in
  [OPERATOR.md](../../OPERATOR.md),
  [docs/agents/issue-tracker.md](../agents/issue-tracker.md), and
  [docs/agents/ralph-loop.md](../agents/ralph-loop.md).
- #176 through #181: The first **Gas market knowledge base** route, ADR,
  Subproject, bronze source manifest command, PDF archive cache fetcher,
  Docling-based silver document extraction, Docling Hybrid chunks, and silver
  chunk index validation were introduced with raw PDFs kept in S3 or the
  ignored `.cache/pdfs/` local cache. Text artifacts live under the Gas market
  corpus root, and cited gold **Market context** pages are corpus artifacts
  rather than maintained router docs. The decision lives in ADR
  [0010](../adr/0010-gas-market-knowledge-base.md), and the Subproject policy
  lives in the
  [Subproject README](../../tools/gas-market-knowledge-base/README.md).
- #241: The **Gas market knowledge base** Subproject added an archive-prefix
  completeness audit for comparing configured archive PDF objects with
  the bronze source manifest, including fixture listing mode for the
  **Unit test** lane. The command surface and QA expectation live in the
  [Subproject README](../../tools/gas-market-knowledge-base/README.md).
- #266: The **Gas market knowledge base** Subproject externalized generated
  bronze, silver, and gold corpus defaults under
  `$ENERGY_MARKET_CORPUS_ROOT/gas-market/{bronze,silver,gold}`, with an unset
  or empty environment variable falling back to
  `~/energy-market-delta-lake-artifacts/corpora`. Repo `generated/` paths
  remain corpus output rather than maintained router docs when present.
- #279: The **Gas market knowledge base** Subproject stopped tracking current
  generated corpus files under `tools/gas-market-knowledge-base/generated/`.
  The tree is ignored, the Subproject **Commit check** rejects staged generated
  bronze, silver, and gold corpus artifacts, and any git-history purge remains
  a separate guarded maintenance issue.
- #274: The Subproject added the AEMO major publications corpus fixture command
  surface. `aemo-publications-corpus build-fixture` writes deterministic
  fixture bronze, silver, silver index, and gold outputs under
  `$ENERGY_MARKET_CORPUS_ROOT/aemo-major-publications/{bronze,silver,gold}` by
  default and validates the fixture build through the AEMO publications corpus
  **Unit test** lane and the Subproject **Commit check**.
- #276: The Subproject added `aemo-publications-corpus validate` for AEMO major
  publications hub and library coverage. The command reports source-family
  counts, supported and unsupported media counts, silver index counts, and gold
  page counts from the external corpus root, and fails clearly for missing
  downloaded metadata, missing source files, stale index rows, and broken gold
  citations.

## Search commands

```bash
git diff --name-only
rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools
rg -n "sync.sources|sync.scope|sync.qa" OPERATOR.md README.md docs backend-services infrastructure tools
```

These commands support the intended flow:

1. code change
2. `rg` search for docs synced to that code
3. doc update
4. QA

## Related docs

- [Repository documentation map](../README.md)
- [Repository architecture](architecture.md)
- [Repository workflow](workflow.md)
- [Ralph loop internals](../agents/ralph-loop.md)
- [Operator workflow](../../OPERATOR.md)
- [Agent policy](../../AGENTS.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `AGENTS.md`
  - `CONTEXT.md`
  - `OPERATOR.md`
  - `README.md`
  - `docs/README.md`
  - `docs/agents/README.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/ralph-loop.md`
  - `docs/adr/0003-bounded-current-state-bronze-source-tables.md`
  - `docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md`
  - `docs/adr/0007-ralph-full-access-implementation-pass.md`
  - `docs/adr/0009-ralph-post-promotion-deployment-classification.md`
  - `docs/adr/0010-gas-market-knowledge-base.md`
  - `docs/adr/0011-ralph-adaptive-vocabulary-and-verified-recovery.md`
  - `docs/adr/0012-ralph-gitflow-review-package-gate.md`
  - `tests/test_documentation_qa_ratchet.py`
  - `.pre-commit-config.yaml`
  - `.gitleaksignore`
  - `.gitignore`
  - `backend-services/.pre-commit-config.yaml`
  - `backend-services/authentication/.pre-commit-config.yaml`
  - `backend-services/authentication/pyproject.toml`
  - `backend-services/dagster-core/pyproject.toml`
  - `backend-services/dagster-user/aemo-etl/.pre-commit-config.yaml`
  - `backend-services/dagster-user/aemo-etl/Makefile`
  - `backend-services/dagster-user/aemo-etl/pyproject.toml`
  - `backend-services/marimo/.pre-commit-config.yaml`
  - `backend-services/marimo/pyproject.toml`
  - `infrastructure/aws-pulumi/.pre-commit-config.yaml`
  - `infrastructure/aws-pulumi/pyproject.toml`
  - `tools/ralph-loop/.pre-commit-config.yaml`
  - `tools/ralph-loop/Makefile`
  - `tools/ralph-loop/README.md`
  - `tools/ralph-loop/pyproject.toml`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/review_package_media.py`
  - `tools/ralph-loop/src/ralph_loop/state.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
  - `tools/ralph-loop/tests/unit/test_ralph.py`
  - `tools/ralph-loop/uv.lock`
  - `tools/gas-market-knowledge-base/.pre-commit-config.yaml`
  - `tools/gas-market-knowledge-base/Makefile`
  - `tools/gas-market-knowledge-base/README.md`
  - `tools/gas-market-knowledge-base/pyproject.toml`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/archive_audit.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/__init__.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/cli.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/corpus_paths.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/fixture_corpus.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/source_manifest.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/validation.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/cli.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/__init__.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/gold_context.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/manifest.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/paths.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/silver_chunks.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/silver_documents.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_paths.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/docling_adapter.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/gold_context.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/pdf_cache.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/silver_chunks.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/silver_documents.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/source_manifest.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_archive_audit.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_aemo_publications.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_cli.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_corpus_core.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_corpus_paths.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_gold_context.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_pdf_cache.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_precommit_policy.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_silver_chunks.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_silver_documents.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_source_manifest.py`
  - `tools/gas-market-knowledge-base/tests/docling/test_silver_documents_docling.py`
  - `tools/gas-market-knowledge-base/uv.lock`
  - `scripts/check_shell_script_headers.py`
  - `scripts/ralph.py`
- `sync.scope`: `operations, tooling`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `prek run -a`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
