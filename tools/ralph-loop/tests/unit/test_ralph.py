from __future__ import annotations

import html
import io
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch

from ralph_loop import cli as ralph
from ralph_loop import state as ralph_state
from ralph_loop import workflow as ralph_workflow

REPO_ROOT = Path(__file__).resolve().parents[4]


IMPLEMENTATION_BODY = """## What to build
Build it.

## Acceptance criteria
- [ ] It works.

## Blocked by
None
"""

E2E_IMPLEMENTATION_BODY = (
    IMPLEMENTATION_BODY
    + """
## Context anchors

- Test lane: `AEMO ETL End-to-end test`
"""
)

AGENTS_IMPLEMENTATION_BODY = """## What to build
Update the agent workflow.

## Acceptance criteria
- [ ] The workflow is documented.

## Blocked by
None

## Context anchors
- Path: `.agents/skills/ralph-loop/SKILL.md`
- Doc: `docs/agents/ralph-loop.md`
"""

RALPH_SELF_UPDATE_BODY = """## What to build
Update the Ralph loop.

## Acceptance criteria
- [ ] The Operator restart checkpoint remains stable.

## Blocked by
None

## Context anchors
- Path: `tools/ralph-loop/src/ralph_loop/cli.py`
- Path: `scripts/ralph.py`
"""

EXPLORATORY_IMPLEMENTATION_BODY = """## What to build
Build it.

## Acceptance criteria
- [ ] It works.

## Blocked by
None

## Review focus
Review whether this branch should become the production workflow.
"""

OPERATOR_SMOKE_BODY = (
    EXPLORATORY_IMPLEMENTATION_BODY
    + """
## Operator smoke

Smoke id: ec2-run-worker-placement
Timeout: 120

This smoke must run only from the Ralph outer loop with operator-owned
AWS/Pulumi credentials. Sandboxed Codex implementation subprocesses must not
receive AWS or Pulumi credentials.
"""
)


def implementation_body_with_blockers(*blockers: int) -> str:
    blocked_by = (
        "\n".join(f"- #{blocker}" for blocker in blockers) if blockers else "None"
    )
    return f"""## What to build
Build it.

## Acceptance criteria
- [ ] It works.

## Blocked by
{blocked_by}
"""


def ready_issue_refresh_body(text: str) -> str:
    return f"{ralph.AI_READY_ISSUE_REFRESH_DISCLAIMER}\n\n{text}"


POST_PROMOTION_REVIEW_MARKDOWN = """# Post-promotion Review

## Findings

No blocking findings.

## Learnings

- Promotion evidence stayed consistent after `main` push and `dev` sync.

## Recovery and Consistency Guidance

- No recovery needed for this Promotion.

## Follow-up GitHub Issue Drafts

```json
[
  {
    "finding_id": "harden-promotion-evidence-checks",
    "title": "Harden Promotion evidence checks",
    "body": "## What to build\\nHarden Promotion evidence checks so future Ralph changes preserve verified issue metadata behavior.\\n\\n## Acceptance criteria\\n- [ ] Promotion reports continue to include verified issue evidence.\\n\\n## Blocked by\\nNone\\n",
    "labels": ["enhancement", "delivery-gitflow"]
  }
]
```
"""

ISSUE_COMPLETION_REVIEW_PASS_MARKDOWN = """# Issue completion review

## Review result

pass

## Findings

No blocking findings.

## Residual risk

None.
"""

ISSUE_COMPLETION_REVIEW_FAIL_MARKDOWN = """# Issue completion review

## Review result

fail

## Findings

- `scripts/ralph.py` does not implement the requested review gate.

## Residual risk

The issue would be integrated incomplete.
"""

REVIEW_PACKAGE_HTML = """<!doctype html>
<html>
<head><meta charset="utf-8"><title>Review package for issue #42</title></head>
<body>
<h1>Review package for issue #42</h1>
<h2>Summary</h2>
<p>Issue #42 is ready for Gitflow Local integration.</p>
<h2>Changed files</h2>
<ul><li>scripts/ralph.py</li></ul>
<h2>QA evidence</h2>
<p>QA passed.</p>
<h2>Issue completion review</h2>
<p>Issue completion review passed.</p>
</body>
</html>
"""


def review_package_html_for_prompt(prompt: str) -> str:
    changed_section = prompt.split("- Changed files:", maxsplit=1)[1].split(
        "- QA evidence:",
        maxsplit=1,
    )[0]
    changed_files = [
        line.split("`", maxsplit=2)[1]
        for line in changed_section.splitlines()
        if "`" in line
    ]
    issue_title = "Issue #42"
    for line in prompt.splitlines():
        if line.strip().startswith("- Issue: `#42 "):
            issue_title = line.split("`", maxsplit=2)[1]
            break
    changed_items = "\n".join(f"<li>{html.escape(path)}</li>" for path in changed_files)
    return f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Review package for issue #42</title></head>
<body>
<h1>Review package for issue #42</h1>
<h2>Summary</h2>
<p>{html.escape(issue_title)} is ready for Local integration.</p>
<h2>Changed files</h2>
<ul>{changed_items}</ul>
<h2>QA evidence</h2>
<p>QA passed.</p>
<h2>Issue completion review</h2>
<p>Issue completion review passed.</p>
</body>
</html>
"""


DEPLOY_REPAIR_BODY = """## What to build
Repair the failed deployed workflow command so the Operator deployment checkpoint can complete.

## Acceptance criteria
- [ ] The failed deployment command completes successfully.
- [ ] Deployed test evidence is recorded as passed.

## Blocked by
None

## Current context
The checkpointed Operator deployment failed after Promotion.

## Context anchors
- Path: `infrastructure/aws-pulumi/scripts/run-integration-tests`
- Path: `backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py`
- Test lane: `Ralph loop Unit test`

## QA/deploy verification plan
- Run `make unit-test` from `tools/ralph-loop`.
- Rerun the checkpointed Operator deployment after credentials are available to the outer loop.
"""

DEPLOY_FAILURE_ANALYSIS_MARKDOWN = """# Deploy Failure Analysis

## Findings

The checkpointed deployment command failed after Promotion.

## Deploy Repair GitHub Issue Drafts

```json
[
  {
    "finding_id": "restore-operator-deployment",
    "title": "Repair checkpointed Operator deployment failure",
    "body": %s,
    "labels": ["bug", "delivery-gitflow"]
  }
]
```

## Evidence

- The deployment command returned exit code 1.

## Open Questions

None.
""" % json.dumps(DEPLOY_REPAIR_BODY)

READY_ISSUE_REFRESH_ANALYSIS_MARKDOWN = """# Ready Issue Refresh Analysis

## Summary

One candidate issue was reviewed without mutating GitHub Issues.

## Integrated Work

- Integrated issue #42 published `merge-sha`.

## Candidate Issue Update Plan

- #43: no change planned.

## Candidate Issue Mutation Plan

```json
{
  "ready_issue_refresh_mutations": [
    {
      "issue_number": 43,
      "action": "no_change",
      "comment": null,
      "body": null,
      "add_labels": [],
      "remove_labels": [],
      "close_as_completed": false
    }
  ]
}
```

## Evidence

- Candidate issue body remained actionable.

## Open Questions

None.
"""

READY_ISSUE_REFRESH_MISSING_PLAN_MARKDOWN = """# Ready Issue Refresh Analysis

## Summary

One candidate issue was reviewed without mutating GitHub Issues.

## Integrated Work

- Integrated issue #42 published `merge-sha`.

## Candidate Issue Update Plan

- #43: no change planned.

## Evidence

- Candidate issue body remained actionable.

## Open Questions

None.
"""

READY_ISSUE_REFRESH_MALFORMED_MUTATION_MARKDOWN = """# Ready Issue Refresh Analysis

## Summary

One candidate issue was reviewed without mutating GitHub Issues.

## Integrated Work

- Integrated issue #42 published `merge-sha`.

## Candidate Issue Update Plan

- #43: no change planned.

## Candidate Issue Mutation Plan

```json
{
  "ready_issue_refresh_mutations": [
    {
      "issue_number": 43,
      "action": "no_change",
    }
  ]
}
```

## Evidence

- Candidate issue body remained actionable.

## Open Questions

None.
"""

READY_ISSUE_REFRESH_COMPLETED_MARKDOWN = """# Ready Issue Refresh Analysis

## Summary

One candidate issue is already satisfied.

## Integrated Work

- Integrated issue #42 published `merge-sha`.

## Candidate Issue Update Plan

- #43: close as completed with evidence.

## Candidate Issue Mutation Plan

```json
{
  "ready_issue_refresh_mutations": [
    {
      "issue_number": 43,
      "action": "completed",
      "comment": "Issue #43 is already satisfied by merge-sha.",
      "body": null,
      "add_labels": [],
      "remove_labels": [],
      "close_as_completed": true
    }
  ]
}
```

## Evidence

- Candidate acceptance criteria are satisfied by the integrated change.

## Open Questions

None.
"""

READY_ISSUE_REFRESH_NEEDS_TRIAGE_MARKDOWN = """# Ready Issue Refresh Analysis

## Summary

One candidate issue needs maintainer review.

## Integrated Work

- Integrated issue #42 published `merge-sha`.

## Candidate Issue Update Plan

- #43: stale but unclear, needs triage.

## Candidate Issue Mutation Plan

```json
{
  "ready_issue_refresh_mutations": [
    {
      "issue_number": 43,
      "action": "needs_triage",
      "comment": "The issue contract may be stale after merge-sha, but the correct update is unclear."
    }
  ]
}
```

## Evidence

- The blocker changed after Local integration.

## Open Questions

None.
"""

POST_PROMOTION_READY_ISSUE_REFRESH_MARKDOWN = """# Ready Issue Refresh Analysis

## Summary

Two candidate issues were reviewed after Promotion closed #42.

## Integrated Work

- Promotion closed #42 after `promotion-sha`.

## Candidate Issue Update Plan

- #117: move back to ready-for-agent because its only blocker was closed by Promotion.
- #122: no change planned.

## Candidate Issue Mutation Plan

```json
{
  "ready_issue_refresh_mutations": [
    {
      "issue_number": 117,
      "action": "update",
      "comment": "Promotion closed #42, the only blocker for this issue. Move it back to ready-for-agent before the next claim.",
      "body": null,
      "add_labels": ["ready-for-agent"],
      "remove_labels": ["needs-triage"],
      "close_as_completed": false
    },
    {
      "issue_number": 122,
      "action": "no_change",
      "comment": null,
      "body": null,
      "add_labels": [],
      "remove_labels": [],
      "close_as_completed": false
    }
  ]
}
```

## Evidence

- #117 only named #42 in `## Blocked by`.
- #122 remains ready but does not need a scope update.

## Open Questions

None.
"""


def make_issue(
    labels: set[str],
    body: str = "",
    *,
    number: int = 42,
    title: str = "Implement thing",
    created_at: datetime | None = None,
):
    return ralph.Issue(
        number=number,
        title=title,
        body=body,
        labels=frozenset(labels),
        created_at=created_at or datetime(2026, 4, 30, tzinfo=UTC),
        updated_at=datetime(2026, 4, 30, tzinfo=UTC),
        url=f"https://github.com/example/repo/issues/{number}",
        comments=0,
        author="reporter",
    )


def load_run_manifest(tmp_path: Path, run_glob: str = "issue-42-*") -> dict[str, Any]:
    manifest_path = next((tmp_path / "logs").glob(f"{run_glob}/ralph-run.json"))
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def write_minimal_child_manifest(
    log_root: Path,
    *,
    name: str,
    status: str = "succeeded",
    run_kind: str = "implementation",
) -> Path:
    run_dir = log_root / name
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / ralph.MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(
            {
                "schema_version": ralph.MANIFEST_SCHEMA_VERSION,
                "run_kind": run_kind,
                "status": status,
                "paths": {"run_dir": str(run_dir)},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest_path


@dataclass(frozen=True)
class FakeCall:
    args: tuple[str, ...]
    cwd: Path
    input_text: str | None
    log_path: Path | None
    phase: str | None
    execute_in_dry_run: bool
    env: dict[str, str] | None
    timeout_seconds: int | float | None


class FakeRunner:
    def __init__(
        self,
        *,
        status_outputs: list[str] | None = None,
        diff_outputs: list[str] | None = None,
        rev_parse_outputs: list[str] | None = None,
        command_outputs: dict[tuple[str, ...], list[str]] | None = None,
        fail_commands: set[tuple[str, ...]] | dict[tuple[str, ...], int] | None = None,
        fail_command_attempts: dict[tuple[str, ...], list[tuple[int, str]]]
        | None = None,
        fail_post_promotion_review: bool = False,
        issue_completion_review_markdowns: list[str] | None = None,
        review_package_html: str = REVIEW_PACKAGE_HTML,
        fail_review_package: bool = False,
        fail_marimo_review_media: bool = False,
        fail_ready_issue_refresh_analysis: bool = False,
        ready_issue_refresh_analysis_markdown: str = READY_ISSUE_REFRESH_ANALYSIS_MARKDOWN,
        fail_deploy_failure_analysis: bool = False,
        deploy_failure_analysis_markdown: str = DEPLOY_FAILURE_ANALYSIS_MARKDOWN,
        fail_issue_create: bool = False,
        timeout_commands: set[tuple[str, ...]] | None = None,
    ) -> None:
        self.dry_run = False
        self.calls: list[FakeCall] = []
        self.status_outputs = status_outputs or []
        self.diff_outputs = diff_outputs or []
        self.rev_parse_outputs = rev_parse_outputs or []
        self.command_outputs = command_outputs or {}
        self.fail_command_attempts = fail_command_attempts or {}
        self.fail_post_promotion_review = fail_post_promotion_review
        self.issue_completion_review_markdowns = issue_completion_review_markdowns or []
        self.review_package_html = review_package_html
        self.fail_review_package = fail_review_package
        self.fail_marimo_review_media = fail_marimo_review_media
        self.fail_ready_issue_refresh_analysis = fail_ready_issue_refresh_analysis
        self.ready_issue_refresh_analysis_markdown = (
            ready_issue_refresh_analysis_markdown
        )
        self.fail_deploy_failure_analysis = fail_deploy_failure_analysis
        self.deploy_failure_analysis_markdown = deploy_failure_analysis_markdown
        self.fail_issue_create = fail_issue_create
        self.timeout_commands = timeout_commands or set()
        self.created_issue_number = 99
        if isinstance(fail_commands, dict):
            self.fail_commands = fail_commands
        else:
            self.fail_commands = {command: 1 for command in fail_commands or set()}

    def run(
        self,
        args: list[str],
        *,
        cwd: Path,
        input_text: str | None = None,
        log_path: Path | None = None,
        phase: str | None = None,
        execute_in_dry_run: bool = True,
        env: dict[str, str] | None = None,
        timeout_seconds: int | float | None = None,
    ):
        command = tuple(args)
        self.calls.append(
            FakeCall(
                args=command,
                cwd=cwd,
                input_text=input_text,
                log_path=log_path,
                phase=phase,
                execute_in_dry_run=execute_in_dry_run,
                env=env,
                timeout_seconds=timeout_seconds,
            )
        )
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("fake log", encoding="utf-8")
        if (
            command in self.fail_command_attempts
            and self.fail_command_attempts[command]
        ):
            returncode, stderr = self.fail_command_attempts[command].pop(0)
            raise ralph.CommandFailure(
                args,
                cwd,
                returncode,
                "",
                stderr,
                log_path,
            )
        if command in self.fail_commands:
            raise ralph.CommandFailure(
                args,
                cwd,
                self.fail_commands[command],
                "",
                "fake failure",
                log_path,
            )
        if command in self.timeout_commands:
            raise ralph.CommandTimeout(
                args,
                cwd,
                timeout_seconds or 0,
                "",
                "fake timeout",
                log_path,
            )
        if command in self.command_outputs:
            return ralph.CompletedCommand(
                stdout=self.command_outputs[command].pop(0),
                stderr="",
            )
        if (
            command[:6]
            == (
                "uv",
                "run",
                "--with",
                "playwright",
                "python",
                "scripts/review_promoted_dashboards.py",
            )
            and "--videos" in command
        ):
            if self.fail_marimo_review_media:
                raise ralph.CommandFailure(
                    args,
                    cwd,
                    1,
                    "",
                    "fake media failure",
                    log_path,
                )
            artifact_dir = Path(command[command.index("--artifact-dir") + 1])
            routes = [
                command[index + 1]
                for index, value in enumerate(command)
                if value == "--route"
            ]
            artifact_dir.mkdir(parents=True, exist_ok=True)
            for route in routes:
                for viewport in ("desktop", "narrow"):
                    video_path = artifact_dir / ralph.marimo_review_video_name(
                        route, viewport
                    )
                    video_path.write_bytes(b"fake webm")
            return ralph.CompletedCommand(stdout="fake media evidence\n", stderr="")
        if command == ("git", "status", "--porcelain"):
            stdout = self.status_outputs.pop(0) if self.status_outputs else ""
            return ralph.CompletedCommand(stdout=stdout, stderr="")
        if command[:3] == ("git", "diff", "--name-only"):
            return ralph.CompletedCommand(stdout=self.diff_outputs.pop(0), stderr="")
        if command[:2] == ("git", "rev-parse"):
            return ralph.CompletedCommand(
                stdout=self.rev_parse_outputs.pop(0), stderr=""
            )
        if command[:5] == ("git", "ls-remote", "--exit-code", "--heads", "origin"):
            branch = command[5]
            return ralph.CompletedCommand(
                stdout=f"abc123\trefs/heads/{branch}\n",
                stderr="",
            )
        if command[:3] == ("gh", "issue", "list"):
            return ralph.CompletedCommand(stdout="[]", stderr="")
        if command[:3] == ("gh", "issue", "create"):
            if self.fail_issue_create:
                raise ralph.CommandFailure(
                    args,
                    cwd,
                    1,
                    "",
                    "fake issue create failure",
                    log_path,
                )
            number = self.created_issue_number
            self.created_issue_number += 1
            return ralph.CompletedCommand(
                stdout=f"https://github.com/example/repo/issues/{number}\n",
                stderr="",
            )
        if command[:3] == ("gh", "issue", "view") and "comments" in command:
            return ralph.CompletedCommand(
                stdout=json.dumps({"comments": []}), stderr=""
            )
        if command[:3] == ("gh", "issue", "view") and "state" in command:
            return ralph.CompletedCommand(
                stdout=json.dumps({"state": "OPEN"}), stderr=""
            )
        if command[:3] == ("gh", "issue", "view"):
            return ralph.CompletedCommand(
                stdout=issue_view_output(labels=["agent-reviewing"]),
                stderr="",
            )
        if command == ("gh", "auth", "token"):
            return ralph.CompletedCommand(stdout="fake-gh-token\n", stderr="")
        if command[:2] == ("codex", "exec") and input_text is not None:
            if "Run an Issue completion review" in input_text:
                markdown = (
                    self.issue_completion_review_markdowns.pop(0)
                    if self.issue_completion_review_markdowns
                    else ISSUE_COMPLETION_REVIEW_PASS_MARKDOWN
                )
                return ralph.CompletedCommand(stdout=markdown, stderr="")
            if (
                "Repair GitHub issue" in input_text
                and "Issue completion review" in input_text
            ):
                return ralph.CompletedCommand(stdout="", stderr="")
            if "Generate a Review package" in input_text:
                if self.fail_review_package:
                    raise ralph.CommandFailure(
                        args,
                        cwd,
                        1,
                        "",
                        "fake Review package failure",
                        log_path,
                    )
                review_package_html = (
                    review_package_html_for_prompt(input_text)
                    if self.review_package_html == REVIEW_PACKAGE_HTML
                    else self.review_package_html
                )
                return ralph.CompletedCommand(
                    stdout=review_package_html,
                    stderr="",
                )
            if "Run a Post-promotion review" in input_text:
                if self.fail_post_promotion_review:
                    raise ralph.CommandFailure(
                        args,
                        cwd,
                        1,
                        "",
                        "fake review failure",
                        log_path,
                    )
                return ralph.CompletedCommand(
                    stdout=POST_PROMOTION_REVIEW_MARKDOWN,
                    stderr="",
                )
            if "Run a read-only Ready issue refresh analysis" in input_text:
                if self.fail_ready_issue_refresh_analysis:
                    raise ralph.CommandFailure(
                        args,
                        cwd,
                        1,
                        "",
                        "fake Ready issue refresh analysis failure",
                        log_path,
                    )
                return ralph.CompletedCommand(
                    stdout=self.ready_issue_refresh_analysis_markdown,
                    stderr="",
                )
            if "Run a deploy-failure analysis" in input_text:
                if self.fail_deploy_failure_analysis:
                    raise ralph.CommandFailure(
                        args,
                        cwd,
                        1,
                        "",
                        "fake deploy failure analysis failure",
                        log_path,
                    )
                return ralph.CompletedCommand(
                    stdout=self.deploy_failure_analysis_markdown,
                    stderr="",
                )
        if command and command[0].endswith("run-ec2-run-worker-smoke"):
            evidence_path = cwd / ".ralph-operator-smoke-evidence.json"
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text(
                json.dumps(
                    {"status": "success", "smoke_id": "ec2-run-worker-placement"}
                )
                + "\n",
                encoding="utf-8",
            )
            if log_path is not None:
                log_path.write_text(
                    "\n".join(
                        [
                            f"$ {ralph.format_command(args)}",
                            f"cwd: {cwd}",
                            "exit: 0",
                            "",
                            "STDOUT:",
                            f"run manifest: {evidence_path}",
                            "",
                            "STDERR:",
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )
        return ralph.CompletedCommand(stdout="", stderr="")


class E2EManifestRetryRunner(FakeRunner):
    e2e_command = ("scripts/aemo-etl-e2e", "run", "--scenario", "full-gas-model")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.e2e_attempts = 0
        self.success_manifest_path: Path | None = None

    def run(
        self,
        args: list[str],
        *,
        cwd: Path,
        input_text: str | None = None,
        log_path: Path | None = None,
        phase: str | None = None,
        execute_in_dry_run: bool = True,
        env: dict[str, str] | None = None,
        timeout_seconds: int | float | None = None,
    ):
        command = tuple(args)
        if command != self.e2e_command:
            return super().run(
                args,
                cwd=cwd,
                input_text=input_text,
                log_path=log_path,
                phase=phase,
                execute_in_dry_run=execute_in_dry_run,
                env=env,
                timeout_seconds=timeout_seconds,
            )

        self.calls.append(
            FakeCall(
                args=command,
                cwd=cwd,
                input_text=input_text,
                log_path=log_path,
                phase=phase,
                execute_in_dry_run=execute_in_dry_run,
                env=env,
                timeout_seconds=timeout_seconds,
            )
        )
        self.e2e_attempts += 1
        manifest_path = (
            cwd
            / ".e2e"
            / "aemo-etl"
            / "runs"
            / f"attempt-{self.e2e_attempts}"
            / "run-manifest.json"
        )
        status = "failed" if self.e2e_attempts == 1 else "success"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(self._manifest_payload(status=status), indent=2) + "\n",
            encoding="utf-8",
        )
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(
                "\n".join(
                    [
                        f"$ {ralph.format_command(args)}",
                        f"cwd: {cwd}",
                        f"exit: {1 if self.e2e_attempts == 1 else 0}",
                        "",
                        "STDOUT:",
                        "E2E budget report (informational):",
                        f"- run manifest: {manifest_path}",
                        "- target progress: 37/37 materialized",
                        "- final asset-check status: 0 failed / 0 missing",
                        "run manifest: " + str(manifest_path),
                        "",
                        "STDERR:",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
        if self.e2e_attempts == 1:
            raise ralph.CommandFailure(
                args,
                cwd,
                1,
                "",
                "first e2e attempt failed",
                log_path,
            )
        self.success_manifest_path = manifest_path
        return ralph.CompletedCommand(stdout="", stderr="")

    @staticmethod
    def _manifest_payload(*, status: str) -> dict[str, Any]:
        observations = {
            "total_gate_duration_seconds": 623,
            "peak_active_run_count": 6,
            "peak_queued_run_count": 6,
            "successful_run_count": 67,
            "total_run_count": 67,
            "materialized_target_asset_count": 37,
            "target_asset_count": 37,
            "target_asset_check_count": 144,
            "missing_target_asset_count": 0,
            "failed_target_asset_count": 0,
            "missing_asset_check_count": 0,
            "failed_asset_check_count": 0,
        }
        return {
            "run_id": f"attempt-{status}",
            "status": status,
            "cleanup": "completed-after-success"
            if status == "success"
            else "preserved-after-failure",
            "options": {
                "scenario": "full-gas-model",
                "launch_mode": "direct-upstream-asset-launch",
                "max_concurrent_runs": 6,
            },
            "source_definitions": {
                "executable_asset_count": 37,
                "asset_check_count": 144,
            },
            "dataflow": {
                "scenario_evidence": {
                    "scenario": "full-gas-model",
                    "launch_mode": "direct-upstream-asset-launch",
                    "target_group": "gas_model",
                    "target_asset_count": 37,
                    "target_asset_check_count": 144,
                    "batch_count": 67,
                }
            },
            "telemetry": {
                "total_gate_duration_seconds": 623,
                "dagster_dataflow": {
                    "peak_active_run_count": 6,
                    "peak_queued_run_count": 6,
                    "final_run_status_counts": {"SUCCESS": 67},
                    "final_target_progress": {
                        "materialized_target_asset_count": 37,
                        "target_asset_count": 37,
                        "missing_target_asset_count": 0,
                        "failed_target_asset_count": 0,
                    },
                    "final_missing_asset_check_count": 0,
                    "final_failed_asset_check_count": 0,
                },
            },
            "budget": {
                "status": "not-enforced",
                "observations": observations,
            },
        }


def make_loop(
    tmp_path: Path,
    runner: FakeRunner,
    *,
    delivery_mode: str = ralph.TRUNK_MODE,
    target_branch: str | None = None,
    source_branch: str = ralph.DEFAULT_GITFLOW_BRANCH,
    promote: bool = False,
    skip_post_promotion_review: bool = False,
    skip_post_promotion_followups: bool = False,
    ready_issue_refresh_enabled: bool | None = None,
    skip_ready_issue_refresh: bool = False,
    issue: int | None = None,
    drain: bool = False,
    max_issues: int = ralph.DEFAULT_DRAIN_BUDGET,
    max_codex_attempts: int = ralph.DEFAULT_CODEX_ATTEMPT_BUDGET,
    exploratory_concurrency: int = ralph.DEFAULT_EXPLORATORY_CONCURRENCY,
    dry_run: bool = False,
    allow_dirty_worktree: bool = False,
    allow_full_access_implementation: bool = False,
    issue_limit: int = 100,
) -> ralph.RalphLoop:
    repo_root = tmp_path / "repo"
    worktree_container = tmp_path / "worktrees"
    log_root = tmp_path / "logs"
    repo_root.mkdir(exist_ok=True)
    worktree_container.mkdir(exist_ok=True)
    config = ralph.LoopConfig(
        repo_root=repo_root,
        repo="example/repo",
        delivery_mode=delivery_mode,
        target_branch=target_branch,
        source_branch=source_branch,
        promote=promote,
        skip_post_promotion_review=skip_post_promotion_review,
        skip_post_promotion_followups=skip_post_promotion_followups,
        ready_issue_refresh_enabled=(
            drain
            if ready_issue_refresh_enabled is None
            else ready_issue_refresh_enabled
        ),
        skip_ready_issue_refresh=skip_ready_issue_refresh,
        issue=issue,
        drain=drain,
        max_issues=max_issues,
        max_codex_attempts=max_codex_attempts,
        exploratory_concurrency=exploratory_concurrency,
        dry_run=dry_run,
        allow_dirty_worktree=allow_dirty_worktree,
        allow_full_access_implementation=allow_full_access_implementation,
        bootstrap_labels=False,
        issue_limit=issue_limit,
        log_root=log_root,
        worktree_container=worktree_container,
    )
    runner.dry_run = dry_run
    return ralph.RalphLoop(config, runner)


def implementation_attempt_context(
    tmp_path: Path,
    loop: ralph.RalphLoop,
    issue: ralph.Issue,
):
    delivery_plan = ralph.resolve_delivery_plan(
        issue,
        default_mode=loop.config.delivery_mode,
        target_branch=loop.config.target_branch,
    )
    branch, worktree_path, integration_path = loop._branch_and_worktrees(issue)
    worktree_path.mkdir(parents=True)
    run_dir = tmp_path / "logs" / "issue-42-test"
    manifest = ralph.RunManifest.for_implementation(
        run_dir=run_dir,
        issue=issue,
        delivery_plan=delivery_plan,
        branch=branch,
        worktree_path=worktree_path,
        integration_path=integration_path,
        config=loop.config,
    )
    access_plan = ralph.issue_implementation_access_plan(issue)
    return worktree_path, run_dir, manifest, access_plan


def deploy_repair_test_context(
    tmp_path: Path,
    loop: ralph.RalphLoop,
) -> tuple[
    Path,
    ralph.RunManifest,
    ralph.PostPromotionDeploymentClassification,
    ralph.PostPromotionDeploymentCommand,
    ralph.CommandFailure,
]:
    run_dir = tmp_path / "logs" / "promote-deploy-failure"
    run_dir.mkdir(parents=True)
    source_path = tmp_path / "worktrees" / "source"
    promote_path = tmp_path / "worktrees" / "promote"
    manifest = ralph.RunManifest.for_promotion(
        run_dir=run_dir,
        source_branch="dev",
        target_branch="main",
        source_path=source_path,
        promote_path=promote_path,
        config=loop.config,
    )
    manifest.record_source_tree(
        branch="dev",
        revision="source-sha",
        worktree_path=source_path,
    )
    manifest.record_changed_files(
        ["infrastructure/aws-pulumi/components/ecs_services.py"],
        stage="promotion_changes_detected",
    )
    classification = ralph.classify_post_promotion_deployment(
        ["infrastructure/aws-pulumi/components/ecs_services.py"]
    )
    manifest.record_deployment_classification(classification)
    manifest.record_promotion_commit("promotion-sha", branch="main")
    command = ralph.post_promotion_deployment_command(
        classification,
        repo_root=loop.config.repo_root,
    )
    assert command is not None
    log_path = run_dir / command.log_name
    log_path.write_text(
        "\n".join(
            [
                "$ run-integration-tests",
                "AWS_SECRET_ACCESS_KEY=raw-secret-value",
                "PULUMI_ACCESS_TOKEN=pulumi-secret-value",
                "Deployed test failed: asset check failed",
            ]
        ),
        encoding="utf-8",
    )
    error = ralph.CommandFailure(
        list(command.args),
        command.cwd,
        1,
        "",
        "Deployed test failed",
        log_path,
    )
    manifest.record_deployment_execution(
        "failed",
        tier=classification.tier,
        reason=classification.reason,
        command_path=command.command_path,
        command=command.args,
        cwd=command.cwd,
        log_path=log_path,
        exit_status=1,
        error=str(error),
        deployed_test_evidence=ralph.deployment_deployed_test_evidence(
            command,
            status="failed",
            log_path=log_path,
        ),
        full_tier_idempotency_evidence=ralph.deployment_idempotency_evidence(
            command,
            status="failed",
            log_path=log_path,
        ),
    )
    return run_dir, manifest, classification, command, error


def write_recovery_manifest(
    tmp_path: Path,
    *,
    delivery_mode: str = ralph.TRUNK_MODE,
    target_branch: str = ralph.DEFAULT_TRUNK_BRANCH,
    metadata_status: str = "failed",
    push_status: str = "pushed",
    commit_sha: str = "abc1234",
    review_package: dict[str, Any] | None = None,
) -> Path:
    run_dir = tmp_path / "logs" / "issue-42-20260504T010203Z"
    run_dir.mkdir(parents=True)
    manifest = {
        "schema_version": ralph.MANIFEST_SCHEMA_VERSION,
        "run_kind": "implementation",
        "status": "failed",
        "stage": "failed",
        "repo": "example/repo",
        "issue": {
            "number": 42,
            "title": "Implement thing",
            "url": "https://github.com/example/repo/issues/42",
        },
        "delivery_mode": delivery_mode,
        "integration_target": target_branch,
        "paths": {"run_dir": str(run_dir), "repo_root": str(tmp_path / "repo")},
        "changed_files": ["scripts/ralph.py"],
        "qa_results": [
            {
                "name": "Ralph loop Commit check",
                "command": ["make", "run-prek"],
                "cwd": str(tmp_path / "repo"),
                "log_path": str(run_dir / "qa.log"),
                "status": "passed",
            }
        ],
        "integration_commit": {"sha": commit_sha, "branch": target_branch},
        "pushes": {
            "integration_target": {
                "branch": target_branch,
                "status": push_status,
                "commit": commit_sha,
                "log_path": str(run_dir / f"git-push-{target_branch}.log"),
            }
        },
        "github_metadata": {"status": metadata_status},
        "failure": {"message": "Post-push issue metadata failed", "log_path": None},
        "events": [],
    }
    if review_package is not None:
        manifest["review_package"] = review_package
    (run_dir / "ralph-run.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return run_dir


def write_failed_pre_push_requeue_manifest(tmp_path: Path) -> Path:
    run_dir = tmp_path / "logs" / "issue-234-20260504T010203Z"
    repo_root = tmp_path / "repo"
    worktree_container = tmp_path / "worktrees"
    implementation_worktree = worktree_container / "agent-issue-234"
    integration_worktree = worktree_container / "agent-integrate-issue-234"
    review_artifact = run_dir / "issue-completion-review.md"
    review_log = run_dir / "codex-issue-completion-review.jsonl"
    failure_log = run_dir / "integration-git-commit.log"
    run_dir.mkdir(parents=True)
    manifest = {
        "schema_version": ralph.MANIFEST_SCHEMA_VERSION,
        "run_kind": "implementation",
        "status": "failed",
        "stage": "failed",
        "repo": "example/repo",
        "issue": {
            "number": 234,
            "title": "Fix Marimo dashboard",
            "url": "https://github.com/example/repo/issues/234",
        },
        "delivery_mode": ralph.GITFLOW_MODE,
        "integration_target": ralph.DEFAULT_GITFLOW_BRANCH,
        "branches": {
            "issue": "agent/issue-234-fix-marimo-dashboard",
            "integration_target": ralph.DEFAULT_GITFLOW_BRANCH,
        },
        "paths": {
            "run_dir": str(run_dir),
            "repo_root": str(repo_root),
            "worktree_container": str(worktree_container),
            "implementation_worktree": str(implementation_worktree),
            "integration_worktree": str(integration_worktree),
            "branch_sync_worktree": None,
        },
        "changed_files": [
            "backend-services/marimo/notebooks/dashboard.py",
            "backend-services/marimo/tests/component/test_dashboard.py",
        ],
        "commits": {"base": "base-sha", "latest_base": "base-sha"},
        "qa_results": [
            {
                "name": "Marimo Component tests",
                "command": ["uv", "run", "pytest", "tests/component"],
                "cwd": str(repo_root / "backend-services" / "marimo"),
                "log_path": str(run_dir / "qa-marimo-component.log"),
                "status": "passed",
            },
            {
                "name": "Marimo Commit check",
                "command": ["prek", "run", "-a"],
                "cwd": str(repo_root / "backend-services" / "marimo"),
                "log_path": str(run_dir / "qa-marimo-prek.log"),
                "status": "passed",
            },
            {
                "name": "Root Commit check",
                "command": ["prek", "run", "-a"],
                "cwd": str(repo_root),
                "log_path": str(run_dir / "qa-root-prek.log"),
                "status": "passed",
            },
        ],
        "issue_completion_review": {
            "enabled": True,
            "required": True,
            "status": "passed",
            "reasons": ["agent_workflow_change"],
            "log_path": str(review_log),
            "artifact_path": str(review_artifact),
            "attempts": [
                {
                    "attempt": 1,
                    "status": "passed",
                    "log_path": str(review_log),
                    "artifact_path": str(review_artifact),
                    "result": "pass",
                }
            ],
            "repair_attempts": [],
            "failure": None,
        },
        "integration_commit": None,
        "pushes": {},
        "github_metadata": {
            "status": "failure_commented",
            "add_labels": [ralph.AGENT_FAILED_LABEL],
            "remove_labels": [ralph.AGENT_RUNNING_LABEL, ralph.READY_LABEL],
        },
        "failure": {
            "message": "Command failed: git commit",
            "log_path": str(failure_log),
        },
        "events": [
            {"stage": "committing_local_integration", "status": "running"},
            {"stage": "failed", "status": "failed"},
        ],
    }
    (run_dir / "ralph-run.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return run_dir


def issue_view_output(*, labels: list[str] | None = None) -> str:
    return json.dumps(
        {
            "number": 42,
            "title": "Implement thing",
            "body": IMPLEMENTATION_BODY,
            "labels": [{"name": label} for label in labels or []],
            "createdAt": "2026-04-30T00:00:00Z",
            "updatedAt": "2026-04-30T00:00:00Z",
            "url": "https://github.com/example/repo/issues/42",
            "comments": [],
            "author": {"login": "reporter"},
        }
    )


def issue_payload(
    number: int,
    labels: list[str],
    body: str = IMPLEMENTATION_BODY,
    created_at: str = "2026-04-30T00:00:00Z",
) -> dict[str, Any]:
    return {
        "number": number,
        "title": f"Issue {number}",
        "body": body,
        "labels": [{"name": label} for label in labels],
        "createdAt": created_at,
        "updatedAt": "2026-04-30T00:00:00Z",
        "url": f"https://github.com/example/repo/issues/{number}",
        "comments": [],
        "author": {"login": "reporter"},
    }


def issue_list_command(*, limit: int = 100) -> tuple[str, ...]:
    return (
        "gh",
        "issue",
        "list",
        "-R",
        "example/repo",
        "--state",
        "open",
        "--limit",
        str(limit),
        "--json",
        "number,title,body,labels,createdAt,updatedAt,url,comments,author",
    )


def exploratory_handoff_comments_output(
    *,
    branch: str = "agent/exploratory/issue-42-implement-thing",
    commit: str = "abc1234",
    changed_files: list[str] | None = None,
) -> str:
    file_lines = [f"- `{path}`" for path in changed_files or ["scripts/ralph.py"]]
    body = "\n".join(
        [
            "Ralph exploratory handoff completed.",
            "",
            f"Commit: `{commit}`",
            "Delivery mode: `exploratory`",
            f"Target branch: `{branch}`",
            "",
            "## Changed files",
            "",
            *file_lines,
            "",
            "## QA",
            "",
            "- `make run-prek` from `/repo`",
            "",
        ]
    )
    return json.dumps({"comments": [{"body": body}]})


def issue_state_command(number: int) -> tuple[str, ...]:
    return (
        "gh",
        "issue",
        "view",
        str(number),
        "-R",
        "example/repo",
        "--json",
        "state",
    )


def issue_view_command(number: int) -> tuple[str, ...]:
    return (
        "gh",
        "issue",
        "view",
        str(number),
        "-R",
        "example/repo",
        "--json",
        "number,title,body,labels,createdAt,updatedAt,url,comments,author",
    )


def issue_comments_command(number: int) -> tuple[str, ...]:
    return (
        "gh",
        "issue",
        "view",
        str(number),
        "-R",
        "example/repo",
        "--comments",
        "--json",
        "comments",
    )


class CountingRalphLoop(ralph.RalphLoop):
    def __init__(
        self, config: ralph.LoopConfig, runner: FakeRunner, ready_count: int
    ) -> None:
        super().__init__(config, runner)
        self.ready_count = ready_count
        self.implemented = 0

    def _validate_tools(self) -> None:
        pass

    def _validate_labels(self) -> None:
        pass

    def _next_ready_issue(self) -> ralph.Issue | None:
        if self.implemented >= self.ready_count:
            return None
        return make_issue(
            {"ready-for-agent"},
            IMPLEMENTATION_BODY,
            number=42 + self.implemented,
        )

    def _ready_implementation_candidates(self) -> list[ralph.Issue]:
        issue = self._next_ready_issue()
        if issue is None:
            return []
        return [issue]

    def _handle_implementation(self, issue: ralph.Issue) -> None:
        self.implemented += 1

    def _next_triage_issue(self) -> ralph.Issue | None:
        return None


class PreflightProbeLoop(ralph.RalphLoop):
    def __init__(self, config: ralph.LoopConfig, runner: FakeRunner) -> None:
        super().__init__(config, runner)
        self.ready_returned = False
        self.implemented = 0
        self.promoted = False

    def _validate_tools(self) -> None:
        pass

    def _validate_labels(self) -> None:
        pass

    def _next_ready_issue(self) -> ralph.Issue | None:
        if self.ready_returned:
            return None
        self.ready_returned = True
        return make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

    def _ready_implementation_candidates(self) -> list[ralph.Issue]:
        issue = self._next_ready_issue()
        if issue is None:
            return []
        return [issue]

    def _handle_implementation(self, issue: ralph.Issue) -> None:
        self.implemented += 1

    def _next_triage_issue(self) -> ralph.Issue | None:
        return None

    def _promote(self) -> None:
        self.promoted = True


class TwoReadyIssueLoop(ralph.RalphLoop):
    def __init__(self, config: ralph.LoopConfig, runner: FakeRunner) -> None:
        super().__init__(config, runner)
        self.ready_calls = 0

    def _validate_tools(self) -> None:
        pass

    def _validate_labels(self) -> None:
        pass

    def _validate_clean_root_worktree_for_live_run(self) -> None:
        pass

    def _next_ready_issue(self) -> ralph.Issue | None:
        self.ready_calls += 1
        if self.ready_calls == 1:
            return make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=42)
        if self.ready_calls == 2:
            return make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43)
        return None

    def _ready_implementation_candidates(self) -> list[ralph.Issue]:
        issue = self._next_ready_issue()
        if issue is None:
            return []
        return [issue]

    def _next_triage_issue(self) -> ralph.Issue | None:
        return None


class DryRunPreviewLoop(ralph.RalphLoop):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        candidates: list[ralph.Issue],
    ) -> None:
        super().__init__(config, runner)
        self.candidates = candidates

    def _validate_tools(self) -> None:
        pass

    def _validate_labels(self) -> None:
        pass

    def _validate_clean_root_worktree_for_live_run(self) -> None:
        pass

    def _ready_implementation_candidates(self) -> list[ralph.Issue]:
        return list(self.candidates)

    def _next_triage_issue(self) -> ralph.Issue | None:
        return None


class LaneSchedulerProbeLoop(ralph.RalphLoop):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        candidates: list[ralph.Issue],
        *,
        issue_failures: set[int] | None = None,
        blocked_issue_numbers: set[int] | None = None,
    ) -> None:
        super().__init__(config, runner)
        self.candidates = list(candidates)
        self.issue_failures = issue_failures or set()
        self.blocked_issue_numbers = blocked_issue_numbers or set()
        self.started_events = {
            issue.number: threading.Event() for issue in self.candidates
        }
        self.release_events = {
            issue.number: threading.Event()
            for issue in self.candidates
            if issue.number in self.blocked_issue_numbers
        }
        self.claimed_numbers: list[int] = []
        self.serial_started: list[int] = []
        self.exploratory_started: list[int] = []
        self.completed_numbers: list[int] = []
        self.failed_numbers: list[int] = []
        self.active_serial = 0
        self.max_active_serial = 0
        self.active_exploratory = 0
        self.max_active_exploratory = 0
        self._claimed_issue_numbers: set[int] = set()
        self._lock = threading.Lock()

    def _validate_tools(self) -> None:
        pass

    def _validate_labels(self) -> None:
        pass

    def _validate_clean_root_worktree_for_live_run(self) -> None:
        pass

    def _ready_implementation_candidates(self) -> list[ralph.Issue]:
        with self._lock:
            claimed = set(self._claimed_issue_numbers)
        return [issue for issue in self.candidates if issue.number not in claimed]

    def _next_triage_issue(self) -> ralph.Issue | None:
        return None

    def _handle_implementation(self, issue: ralph.Issue) -> None:
        delivery_plan = ralph.resolve_delivery_plan(
            issue,
            default_mode=self.config.delivery_mode,
            target_branch=self.config.target_branch,
        )
        is_exploratory = delivery_plan.mode == ralph.EXPLORATORY_MODE and not (
            ralph.issue_requests_operator_smoke(issue)
        )
        with self._lock:
            self._claimed_issue_numbers.add(issue.number)
            self.claimed_numbers.append(issue.number)
            if is_exploratory:
                self.exploratory_started.append(issue.number)
                self.active_exploratory += 1
                self.max_active_exploratory = max(
                    self.max_active_exploratory,
                    self.active_exploratory,
                )
            else:
                self.serial_started.append(issue.number)
                self.active_serial += 1
                self.max_active_serial = max(
                    self.max_active_serial,
                    self.active_serial,
                )
        self.started_events[issue.number].set()
        try:
            if issue.number in self.issue_failures:
                with self._lock:
                    self.failed_numbers.append(issue.number)
                raise ralph.IssueFailure(f"simulated issue failure for #{issue.number}")
            release_event = self.release_events.get(issue.number)
            if release_event is not None:
                release_event.wait(timeout=5)
            with self._lock:
                self.completed_numbers.append(issue.number)
        finally:
            with self._lock:
                if is_exploratory:
                    self.active_exploratory -= 1
                else:
                    self.active_serial -= 1


class TriageDuringExploratoryProbeLoop(LaneSchedulerProbeLoop):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        candidates: list[ralph.Issue],
        *,
        issue_failures: set[int] | None = None,
        blocked_issue_numbers: set[int] | None = None,
        triage_failure: ralph.RalphError | None = None,
    ) -> None:
        super().__init__(
            config,
            runner,
            candidates,
            issue_failures=issue_failures,
            blocked_issue_numbers=blocked_issue_numbers,
        )
        self.triage_failure = triage_failure
        self.triage_started_numbers: list[int] = []
        self.triage_started_event = threading.Event()

    def _next_triage_issue(self) -> ralph.Issue | None:
        return ralph.RalphLoop._next_triage_issue(self)

    def _run_triage(self, issue: ralph.Issue) -> None:
        self.triage_started_numbers.append(issue.number)
        self.triage_started_event.set()
        if self.triage_failure is not None:
            raise self.triage_failure


class RefreshGateSchedulerProbeLoop(ralph.RalphLoop):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        candidates: list[ralph.Issue],
        *,
        refresh_issue_numbers: set[int] | None = None,
        refresh_failure_issue_numbers: set[int] | None = None,
        fatal_kinds: dict[int, str] | None = None,
        blocked_issue_numbers: set[int] | None = None,
    ) -> None:
        super().__init__(config, runner)
        self.candidates = list(candidates)
        self.refresh_issue_numbers = refresh_issue_numbers or set()
        self.refresh_failure_issue_numbers = refresh_failure_issue_numbers or set()
        self.fatal_kinds = fatal_kinds or {}
        self.blocked_issue_numbers = blocked_issue_numbers or set()
        self.started_events = {
            issue.number: threading.Event() for issue in self.candidates
        }
        self.completed_events = {
            issue.number: threading.Event() for issue in self.candidates
        }
        self.release_events = {
            issue.number: threading.Event()
            for issue in self.candidates
            if issue.number in self.blocked_issue_numbers
        }
        refresh_numbers = (
            self.refresh_issue_numbers | self.refresh_failure_issue_numbers
        )
        self.refresh_started_events = {
            issue_number: threading.Event() for issue_number in refresh_numbers
        }
        self.refresh_release_events = {
            issue_number: threading.Event() for issue_number in refresh_numbers
        }
        self.fatal_release_events = {
            issue_number: threading.Event() for issue_number in self.fatal_kinds
        }
        self.fatal_started_events = {
            issue_number: threading.Event() for issue_number in self.fatal_kinds
        }
        self.claimed_numbers: list[int] = []
        self.completed_numbers: list[int] = []
        self._claimed_issue_numbers: set[int] = set()
        self._lock = threading.Lock()

    def _validate_tools(self) -> None:
        pass

    def _validate_labels(self) -> None:
        pass

    def _validate_clean_root_worktree_for_live_run(self) -> None:
        pass

    def _ready_implementation_candidates(self) -> list[ralph.Issue]:
        with self._lock:
            claimed = set(self._claimed_issue_numbers)
        return [issue for issue in self.candidates if issue.number not in claimed]

    def _next_triage_issue(self) -> ralph.Issue | None:
        return None

    def _new_manifest(
        self,
        issue: ralph.Issue,
        delivery_plan: ralph.DeliveryPlan,
    ) -> ralph.RunManifest:
        run_dir = self._run_dir(issue)
        run_dir.mkdir(parents=True, exist_ok=True)
        branch = f"agent/exploratory/issue-{issue.number}-probe"
        return ralph.RunManifest.for_implementation(
            run_dir=run_dir,
            issue=issue,
            delivery_plan=delivery_plan,
            branch=branch,
            worktree_path=self.config.worktree_container / f"issue-{issue.number}",
            integration_path=None,
            config=self.config,
        )

    def _fatal_error_for_issue(
        self,
        issue: ralph.Issue,
        run_dir: Path,
    ) -> ralph.RalphError:
        kind = self.fatal_kinds[issue.number]
        log_path = run_dir / f"{kind}-failure.log"
        if kind == "post_push":
            return ralph.PostPushFailure(
                f"simulated post-push failure for #{issue.number}",
                log_path=log_path,
            )
        if kind == "environment":
            return ralph.EnvironmentFailure(
                f"simulated environment failure for #{issue.number}",
                log_path=log_path,
            )
        raise AssertionError(f"unknown fatal kind: {kind}")

    def _run_probe_refresh(
        self,
        issue: ralph.Issue,
        manifest: ralph.RunManifest,
        *,
        fail: bool,
    ) -> None:
        run_dir = Path(manifest.data["paths"]["run_dir"])
        log_path = run_dir / "codex-ready-issue-refresh-analysis.jsonl"
        artifact_path = run_dir / ralph.READY_ISSUE_REFRESH_ANALYSIS_ARTIFACT_NAME
        manifest.record_ready_issue_refresh(
            "running",
            candidates=[],
            log_path=log_path,
            artifact_path=artifact_path,
        )
        self.refresh_started_events[issue.number].set()
        self.refresh_release_events[issue.number].wait(timeout=5)
        if fail:
            error = ralph.ReadyIssueRefreshFailure(
                f"simulated Ready issue refresh failure for #{issue.number}",
                log_path=log_path,
            )
            manifest.record_ready_issue_refresh(
                "failed",
                candidates=[],
                log_path=log_path,
                artifact_path=artifact_path,
                error=str(error),
            )
            manifest.record_failure(error, log_path=log_path)
            raise error
        manifest.record_ready_issue_refresh(
            "completed",
            candidates=[],
            log_path=log_path,
            artifact_path=artifact_path,
        )

    def _handle_implementation(
        self,
        issue: ralph.Issue,
    ) -> ralph.RunManifest | None:
        delivery_plan = ralph.resolve_delivery_plan(
            issue,
            default_mode=self.config.delivery_mode,
            target_branch=self.config.target_branch,
        )
        manifest = self._new_manifest(issue, delivery_plan)
        with self._lock:
            self._claimed_issue_numbers.add(issue.number)
            self.claimed_numbers.append(issue.number)
        self.started_events[issue.number].set()

        try:
            fatal_release = self.fatal_release_events.get(issue.number)
            if fatal_release is not None:
                fatal_release.wait(timeout=5)
                self.fatal_started_events[issue.number].set()
                error = self._fatal_error_for_issue(
                    issue,
                    Path(manifest.data["paths"]["run_dir"]),
                )
                manifest.record_failure(
                    error,
                    log_path=getattr(error, "log_path", None),
                )
                raise error

            release_event = self.release_events.get(issue.number)
            if release_event is not None:
                release_event.wait(timeout=5)

            if (
                issue.number in self.refresh_issue_numbers
                or issue.number in self.refresh_failure_issue_numbers
            ):
                self._run_with_ready_issue_refresh_claim_gate(
                    issue,
                    lambda: self._run_probe_refresh(
                        issue,
                        manifest,
                        fail=issue.number in self.refresh_failure_issue_numbers,
                    ),
                )

            with self._lock:
                self.completed_numbers.append(issue.number)
            self.completed_events[issue.number].set()
            manifest.record_success()
            return manifest
        except ralph.RalphError:
            raise


class NoValidationRalphLoop(ralph.RalphLoop):
    def _validate_tools(self) -> None:
        pass

    def _validate_labels(self) -> None:
        pass


def operator_snapshot(
    *,
    ready: list[ralph.Issue] | None = None,
    integrated: list[ralph.Issue] | None = None,
    reviewing: list[ralph.Issue] | None = None,
    running: list[ralph.Issue] | None = None,
    failed: list[ralph.Issue] | None = None,
) -> ralph.OperatorQueueSnapshot:
    return ralph.OperatorQueueSnapshot(
        ready=tuple(ready or []),
        integrated=tuple(integrated or []),
        reviewing=tuple(reviewing or []),
        running=tuple(running or []),
        failed=tuple(failed or []),
    )


def write_child_manifest(
    log_root: Path,
    *,
    name: str,
    run_kind: str,
    status: str,
    stage: str | None = None,
    started_at: str | None = None,
    updated_at: str | None = None,
    events: list[dict[str, Any]] | None = None,
    issue: ralph.Issue | None = None,
    delivery_mode: str = ralph.GITFLOW_MODE,
    integration_target: str = ralph.DEFAULT_GITFLOW_BRANCH,
    integration_commit: str | None = None,
    promotion_commit: str | None = None,
    promoted_issues: list[dict[str, Any]] | None = None,
    manual_recoveries: list[dict[str, Any]] | None = None,
    unverified_commits: list[dict[str, Any]] | None = None,
    changed_files: list[str] | None = None,
    qa_results: list[dict[str, Any]] | None = None,
    post_promotion_review_artifact: Path | None = None,
    followups_status: str | None = None,
    created_followups: int = 0,
    failure: dict[str, Any] | None = None,
) -> Path:
    run_dir = log_root / name
    run_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "schema_version": ralph.MANIFEST_SCHEMA_VERSION,
        "run_kind": run_kind,
        "status": status,
        "stage": stage or status,
        "paths": {"run_dir": str(run_dir)},
        "changed_files": changed_files or ["scripts/ralph.py"],
        "qa_results": qa_results
        or [
            {
                "name": "scripted check",
                "command": ["python3", "-m", "unittest", "tests.test_ralph"],
                "cwd": str(log_root.parent.parent),
                "log_path": str(run_dir / "scripted-check.log"),
                "status": "passed" if status == "succeeded" else "failed",
            }
        ],
        "events": events or [],
    }
    if started_at is not None:
        payload["started_at"] = started_at
    if updated_at is not None:
        payload["updated_at"] = updated_at
    if issue is not None:
        payload["issue"] = {
            "number": issue.number,
            "title": issue.title,
            "url": issue.url,
        }
    if run_kind == "implementation":
        payload["delivery_mode"] = delivery_mode
        payload["integration_target"] = integration_target
        payload["integration_commit"] = (
            {"sha": integration_commit, "branch": integration_target}
            if integration_commit is not None
            else None
        )
    if run_kind == "promotion":
        payload["source_branch"] = ralph.DEFAULT_GITFLOW_BRANCH
        payload["integration_target"] = ralph.DEFAULT_TRUNK_BRANCH
        payload["promotion_commit"] = (
            {"sha": promotion_commit, "branch": ralph.DEFAULT_TRUNK_BRANCH}
            if promotion_commit is not None
            else None
        )
        metadata_issues = list(promoted_issues or [])
        metadata_issues.extend(manual_recoveries or [])
        payload["github_metadata"] = {
            "status": (
                "verified_issues_with_warnings"
                if manual_recoveries
                else "verified_issues"
            ),
            "issues": metadata_issues,
        }
        payload["promotion_commit_inventory"] = {
            "status": "classified",
            "base_ref": "origin/main",
            "head_ref": "origin/dev",
            "commits": unverified_commits or [],
        }
        payload["post_promotion_review"] = {
            "enabled": True,
            "status": "completed",
            "log_path": str(run_dir / "codex-post-promotion-review.jsonl"),
            "artifact_path": str(
                post_promotion_review_artifact or run_dir / "post-promotion-review.md"
            ),
        }
    if followups_status is not None:
        payload["post_promotion_followups"] = {
            "status": followups_status,
            "created": [
                {"number": 100 + index, "url": f"https://example.test/{index}"}
                for index in range(created_followups)
            ],
            "duplicates": [],
            "validation_downgrades": [],
            "failures": [],
        }
    if failure is not None:
        payload["failure"] = failure
    manifest_path = run_dir / ralph.MANIFEST_NAME
    manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return manifest_path


class ScriptedOperatorRun(ralph.RalphOperatorRun):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        *,
        run_dir: Path,
        max_cycles: int,
        snapshots: list[ralph.OperatorQueueSnapshot],
    ) -> None:
        super().__init__(config, runner, run_dir=run_dir, max_cycles=max_cycles)
        self.snapshots = snapshots
        self.current_snapshot: ralph.OperatorQueueSnapshot | None = None
        self.issue_runs = 0
        self.promotion_runs = 0
        self.issue_commits: dict[int, str] = {}

    def _validate_operator_preflight(self) -> None:
        pass

    def _queue_snapshot(self) -> ralph.OperatorQueueSnapshot:
        if not self.snapshots:
            return operator_snapshot()
        self.current_snapshot = self.snapshots.pop(0)
        return self.current_snapshot

    def _next_ready_issue(self) -> ralph.Issue | None:
        if self.current_snapshot is None or not self.current_snapshot.ready:
            return None
        return self.current_snapshot.ready[0]

    def _run_drain_scheduler_checkpoint(self) -> None:
        if self.current_snapshot is None:
            return
        for issue in self.current_snapshot.ready:
            self._run_issue_checkpoint(issue)

    def _run_issue_checkpoint(self, issue: ralph.Issue) -> None:
        self.issue_runs += 1
        integration_commit = f"local-integration-{issue.number}-{self.issue_runs}"
        self.issue_commits[issue.number] = integration_commit
        self.manifest.record_current_issue(issue)
        manifest_path = write_child_manifest(
            self.config.log_root,
            name=f"issue-{issue.number}-scripted-{self.issue_runs}",
            run_kind="implementation",
            status="succeeded",
            issue=issue,
            integration_commit=integration_commit,
        )
        self.manifest.record_checkpoint(
            "issue_succeeded",
            message=f"Issue #{issue.number} completed.",
            child_manifest_path=manifest_path,
            issue=issue,
        )
        self.manifest.clear_current()

    def _run_promotion_checkpoint(self) -> None:
        self.promotion_runs += 1
        source_branch = self.config.source_branch
        target_branch = ralph.DEFAULT_TRUNK_BRANCH
        self.manifest.record_current_promotion(
            source_branch=source_branch,
            target_branch=target_branch,
        )
        self.manifest.record_checkpoint(
            "before_promotion",
            message=f"Starting Promotion from {source_branch} to {target_branch}.",
        )
        integrated_issues = (
            self.current_snapshot.integrated
            if self.current_snapshot is not None
            else ()
        )
        manifest_path = write_child_manifest(
            self.config.log_root,
            name=f"promote-scripted-{self.promotion_runs}",
            run_kind="promotion",
            status="succeeded",
            promotion_commit=f"promotion-{self.promotion_runs}-sha",
            promoted_issues=[
                {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.url,
                    "integrated_commit": self.issue_commits.get(issue.number),
                    "metadata_status": "closed",
                }
                for issue in integrated_issues
            ],
            followups_status="completed",
            created_followups=1 if self.promotion_runs == 1 else 0,
        )
        self.manifest.record_checkpoint(
            "promotion_succeeded",
            message="Promotion completed.",
            child_manifest_path=manifest_path,
        )
        self._record_post_promotion_followup_checkpoint(manifest_path)
        self.manifest.clear_current()


class BlockedReadyOperatorRun(ScriptedOperatorRun):
    def _next_ready_issue(self) -> ralph.Issue | None:
        return None


class ParallelSchedulerOperatorRun(ScriptedOperatorRun):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        *,
        run_dir: Path,
        max_cycles: int,
        snapshots: list[ralph.OperatorQueueSnapshot],
        events: list[str],
    ) -> None:
        super().__init__(
            config,
            runner,
            run_dir=run_dir,
            max_cycles=max_cycles,
            snapshots=snapshots,
        )
        self.events = events
        self.observed_exploratory_concurrency: int | None = None
        self.loop = self

    def _run_drain_scheduler_checkpoint(self) -> None:
        ralph.RalphOperatorRun._run_drain_scheduler_checkpoint(self)

    def _run_drain_scheduler(self) -> None:
        self.events.append("scheduler_started")
        self.observed_exploratory_concurrency = self.config.exploratory_concurrency
        if self.current_snapshot is None:
            return
        for issue in self.current_snapshot.ready:
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=self.config.delivery_mode,
                target_branch=self.config.target_branch,
            )
            self.issue_runs += 1
            integration_commit = (
                f"scheduler-{delivery_plan.mode}-{issue.number}-{self.issue_runs}"
            )
            self.issue_commits[issue.number] = integration_commit
            write_child_manifest(
                self.config.log_root,
                name=f"issue-{issue.number}-scheduler-{self.issue_runs}",
                run_kind="implementation",
                status="succeeded",
                issue=issue,
                delivery_mode=delivery_plan.mode,
                integration_target=delivery_plan.target_branch,
                integration_commit=integration_commit,
            )
        self.events.append("ready_issue_refresh_settled")

    def _run_promotion_checkpoint(self) -> None:
        self.events.append("promotion_started")
        super()._run_promotion_checkpoint()


class PostPushMetadataRecoveryLoop(ralph.RalphLoop):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        *,
        delivery_mode: str = ralph.GITFLOW_MODE,
        target_branch: str = ralph.DEFAULT_GITFLOW_BRANCH,
        metadata_status: str = "failed",
        push_status: str = "pushed",
        commit_sha: str = "abc1234",
    ) -> None:
        super().__init__(config, runner)
        self.delivery_mode = delivery_mode
        self.target_branch = target_branch
        self.metadata_status = metadata_status
        self.push_status = push_status
        self.commit_sha = commit_sha
        self.manifest_path: Path | None = None

    def _run_drain_scheduler(self) -> None:
        run_dir = write_recovery_manifest(
            self.config.log_root.parent,
            delivery_mode=self.delivery_mode,
            target_branch=self.target_branch,
            metadata_status=self.metadata_status,
            push_status=self.push_status,
            commit_sha=self.commit_sha,
        )
        self.manifest_path = run_dir / ralph.MANIFEST_NAME
        raise ralph.PostPushFailure(
            "simulated post-push issue metadata failure",
            log_path=run_dir / "gh-issue-metadata.log",
            manifest_path=self.manifest_path,
        )


class SelfUpdateGuardLoop(ralph.RalphLoop):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        *,
        issues: list[ralph.Issue],
        changed_files_by_issue: dict[int, list[str]],
    ) -> None:
        super().__init__(config, runner)
        self.issues = issues
        self.changed_files_by_issue = changed_files_by_issue
        self.handled_issue_numbers: list[int] = []
        self._stop_after_ralph_loop_self_update = True

    def _ready_implementation_candidate_plans(
        self,
        *,
        exclude_issue_numbers: set[int],
    ) -> list[ralph.ReadyImplementationCandidate]:
        candidates: list[ralph.ReadyImplementationCandidate] = []
        for issue in self.issues:
            if issue.number in self.handled_issue_numbers:
                continue
            if issue.number in exclude_issue_numbers:
                continue
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=self.config.delivery_mode,
                target_branch=self.config.target_branch,
            )
            candidates.append(ralph.ReadyImplementationCandidate(issue, delivery_plan))
        return candidates

    def _handle_implementation(self, issue: ralph.Issue) -> ralph.RunManifest:
        self.handled_issue_numbers.append(issue.number)
        manifest_path = write_child_manifest(
            self.config.log_root,
            name=f"issue-{issue.number}-self-update-guard",
            run_kind="implementation",
            status="succeeded",
            issue=issue,
            integration_commit=f"local-integration-{issue.number}",
            changed_files=self.changed_files_by_issue.get(
                issue.number,
                ["README.md"],
            ),
        )
        return ralph.load_run_manifest(manifest_path.parent)


class SelfUpdateGuardOperatorRun(ScriptedOperatorRun):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        *,
        run_dir: Path,
        max_cycles: int,
        snapshots: list[ralph.OperatorQueueSnapshot],
        issues: list[ralph.Issue],
        changed_files_by_issue: dict[int, list[str]],
    ) -> None:
        super().__init__(
            config,
            runner,
            run_dir=run_dir,
            max_cycles=max_cycles,
            snapshots=snapshots,
        )
        self.guard_loop = SelfUpdateGuardLoop(
            config,
            runner,
            issues=issues,
            changed_files_by_issue=changed_files_by_issue,
        )
        self.loop = self.guard_loop
        self.github = self.guard_loop.github

    def _run_drain_scheduler_checkpoint(self) -> None:
        ralph.RalphOperatorRun._run_drain_scheduler_checkpoint(self)


class BaselineGuardLoop(ralph.RalphLoop):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        *,
        issues: list[ralph.Issue],
    ) -> None:
        super().__init__(config, runner)
        self.issues = issues
        self.handled_issue_numbers: list[int] = []
        self._operator_integration_target_baseline_guard_enabled = True

    def _issue_pool(self) -> list[ralph.Issue]:
        return list(self.issues)

    def _has_open_blockers(self, issue: ralph.Issue) -> bool:
        return False

    def _next_triage_issue(self) -> ralph.Issue | None:
        return None

    def _handle_implementation(self, issue: ralph.Issue) -> ralph.RunManifest | None:
        self.handled_issue_numbers.append(issue.number)
        self.issues = [
            existing for existing in self.issues if existing.number != issue.number
        ]
        return None


class PromotionClassificationGit:
    def __init__(
        self,
        changed_files: list[str],
        file_texts: dict[tuple[str, str], str | None] | None = None,
    ) -> None:
        self.changed_files = changed_files
        self.file_texts = file_texts or {}

    def fetch_base(self, base: str, *, run_dir: Path) -> None:
        pass

    def rev_parse(self, ref: str, *, cwd: Path | None = None) -> str:
        if ref == "HEAD":
            return "promotion-sha"
        if ref.startswith("origin/"):
            return "source-sha"
        return "sha"

    def changed_files_between(self, *, base_ref: str, head_ref: str) -> list[str]:
        return sorted(self.changed_files)

    def file_text_at_ref(self, ref: str, path: str) -> str | None:
        return self.file_texts.get((ref, path))

    def promoted_source_commits(
        self, *, base_ref: str, head_ref: str
    ) -> list[ralph.PromotedSourceCommit]:
        return []

    def add_detached_worktree(
        self,
        *,
        path: Path,
        ref: str,
        run_dir: Path,
        log_name: str = "git-worktree-add-integration.log",
    ) -> None:
        path.mkdir(parents=True, exist_ok=False)

    def merge_no_ff(
        self,
        *,
        cwd: Path,
        ref: str,
        message: str,
        run_dir: Path,
        log_name: str = "git-merge-promotion.log",
    ) -> None:
        pass

    def push_head(
        self,
        *,
        cwd: Path,
        branch: str,
        run_dir: Path,
        log_name: str | None = None,
    ) -> None:
        pass

    def remove_worktree(self, path: Path, *, run_dir: Path, log_name: str) -> None:
        path.rmdir()

    def worktrees(self) -> list[ralph.GitWorktree]:
        return []


class PromotionClassificationProbeLoop(ralph.RalphLoop):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        changed_files: list[str],
        file_texts: dict[tuple[str, str], str | None] | None = None,
    ) -> None:
        super().__init__(config, runner)
        self.git = PromotionClassificationGit(changed_files, file_texts=file_texts)

    def _run_qa_commands(
        self,
        changed_files: list[str],
        repo_root: Path,
        run_dir: Path,
        *,
        log_prefix: str,
        subject: str,
        manifest: ralph.RunManifest | None = None,
        issue_body: str | None = None,
    ) -> list[ralph.QAResult]:
        return []

    def _run_promotion_gate_commands(
        self,
        changed_files: list[str],
        repo_root: Path,
        run_dir: Path,
        *,
        manifest: ralph.RunManifest,
    ) -> list[ralph.QAResult]:
        return []

    def _verified_integrated_issues(
        self,
        *,
        source_branch: str,
        source_ref: str,
        target_branch: str,
    ) -> tuple[list[tuple[ralph.Issue, str]], list[ralph.PromotionIssueWarning]]:
        return [], []

    def _close_promoted_issues(
        self,
        integrated_issues: list[tuple[ralph.Issue, str]],
        *,
        promotion_sha: str,
        source_branch: str,
        target_branch: str,
        changed_files: list[str],
        qa_results: list[ralph.QAResult],
        run_dir: Path,
        manifest: ralph.RunManifest,
    ) -> None:
        pass

    def _sync_source_branch_after_promotion(
        self,
        *,
        source_branch: str,
        target_branch: str,
        promotion_sha: str,
        promote_path: Path,
        run_dir: Path,
        manifest: ralph.RunManifest,
    ) -> bool:
        return False

    def _run_post_promotion_review(
        self,
        *,
        source_branch: str,
        target_branch: str,
        source_revision: str,
        promotion_sha: str | None,
        changed_files: list[str],
        integrated_issues: list[tuple[ralph.Issue, str]],
        promotion_commit_inventory: list[dict[str, Any]],
        review_path: Path,
        run_dir: Path,
        manifest: ralph.RunManifest,
        promotion_outcome: str,
        promotion_error: str | None,
    ) -> Path | None:
        manifest.record_post_promotion_review(
            "skipped_by_test", reason="Promotion classification probe."
        )
        return None

    def _run_post_promotion_followups(
        self,
        *,
        source_branch: str,
        target_branch: str,
        source_revision: str,
        promotion_sha: str,
        artifact_path: Path | None,
        run_dir: Path,
        manifest: ralph.RunManifest,
    ) -> None:
        manifest.record_post_promotion_followups(
            "skipped_by_test", reason="Promotion classification probe."
        )

    def _run_post_promotion_ready_issue_refresh(
        self,
        *,
        source_branch: str,
        target_branch: str,
        source_revision: str,
        promotion_sha: str,
        changed_files: list[str],
        qa_results: list[ralph.QAResult],
        promoted_issues: list[tuple[ralph.Issue, str]],
        review_artifact_path: Path | None,
        analysis_path: Path,
        run_dir: Path,
        manifest: ralph.RunManifest,
    ) -> None:
        manifest.record_ready_issue_refresh(
            "skipped_by_test",
            enabled=False,
            reason="Promotion classification probe.",
        )

    def _fast_forward_checked_out_local_branches_after_promotion(
        self,
        *,
        source_branch: str,
        target_branch: str,
        promotion_sha: str,
        source_branch_synced: bool,
        run_dir: Path,
        manifest: ralph.RunManifest,
    ) -> None:
        pass


class PromotionDeploymentProbeLoop(PromotionClassificationProbeLoop):
    def _run_post_promotion_followups(
        self,
        *,
        source_branch: str,
        target_branch: str,
        source_revision: str,
        promotion_sha: str,
        artifact_path: Path | None,
        run_dir: Path,
        manifest: ralph.RunManifest,
    ) -> None:
        manifest.record_post_promotion_followups(
            "completed_no_drafts",
            created=[],
            duplicates=[],
            validation_downgrades=[],
            failures=[],
            reason="Deployment checkpoint probe.",
        )

    def _run_post_promotion_ready_issue_refresh(
        self,
        *,
        source_branch: str,
        target_branch: str,
        source_revision: str,
        promotion_sha: str,
        changed_files: list[str],
        qa_results: list[ralph.QAResult],
        promoted_issues: list[tuple[ralph.Issue, str]],
        review_artifact_path: Path | None,
        analysis_path: Path,
        run_dir: Path,
        manifest: ralph.RunManifest,
    ) -> None:
        manifest.record_ready_issue_refresh(
            "completed",
            enabled=True,
            candidates=[],
            log_path=run_dir / "codex-ready-issue-refresh-analysis.jsonl",
            artifact_path=run_dir / ralph.READY_ISSUE_REFRESH_ANALYSIS_ARTIFACT_NAME,
        )


class PromotionDeploymentOperatorRun(ralph.RalphOperatorRun):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        *,
        run_dir: Path,
        max_cycles: int,
        snapshots: list[ralph.OperatorQueueSnapshot],
        changed_files: list[str],
    ) -> None:
        super().__init__(config, runner, run_dir=run_dir, max_cycles=max_cycles)
        self.snapshots = snapshots
        self.loop = PromotionDeploymentProbeLoop(config, runner, changed_files)
        self.github = self.loop.github

    def _validate_operator_preflight(self) -> None:
        pass

    def _queue_snapshot(self) -> ralph.OperatorQueueSnapshot:
        if not self.snapshots:
            return operator_snapshot()
        return self.snapshots.pop(0)

    def _next_ready_issue(self) -> ralph.Issue | None:
        return None


class TargetedDeploymentOperatorRun(PromotionDeploymentOperatorRun):
    def __init__(
        self,
        config: ralph.LoopConfig,
        runner: FakeRunner,
        *,
        run_dir: Path,
        max_cycles: int,
        snapshots: list[ralph.OperatorQueueSnapshot],
        changed_files: list[str],
    ) -> None:
        super().__init__(
            config,
            runner,
            run_dir=run_dir,
            max_cycles=max_cycles,
            snapshots=snapshots,
            changed_files=changed_files,
        )
        self.current_snapshot: ralph.OperatorQueueSnapshot | None = None
        self.issue_runs = 0
        self.scheduler_runs = 0
        self.implemented_issue_numbers: list[int] = []

    def _queue_snapshot(self) -> ralph.OperatorQueueSnapshot:
        snapshot = super()._queue_snapshot()
        self.current_snapshot = snapshot
        return snapshot

    def _next_ready_issue(self) -> ralph.Issue | None:
        if self.current_snapshot is None or not self.current_snapshot.ready:
            return None
        return self.current_snapshot.ready[0]

    def _run_drain_scheduler_checkpoint(self) -> None:
        self.scheduler_runs += 1
        if self.current_snapshot is None:
            return
        for issue in self.current_snapshot.ready:
            self._run_issue_checkpoint(issue)

    def _run_issue_checkpoint(self, issue: ralph.Issue) -> None:
        self.issue_runs += 1
        self.implemented_issue_numbers.append(issue.number)
        self.manifest.record_current_issue(issue)
        manifest_path = write_child_manifest(
            self.config.log_root,
            name=f"issue-{issue.number}-targeted-{self.issue_runs}",
            run_kind="implementation",
            status="succeeded",
            issue=issue,
            integration_commit=f"local-integration-{issue.number}-{self.issue_runs}",
        )
        self.manifest.record_checkpoint(
            "issue_succeeded",
            message=f"Issue #{issue.number} completed.",
            child_manifest_path=manifest_path,
            issue=issue,
        )
        self.manifest.clear_current()


class RalphHelperTests(unittest.TestCase):
    def test_cli_reexports_extracted_workflow_and_state_helpers(self) -> None:
        self.assertIs(ralph.resolve_delivery_plan, ralph_workflow.resolve_delivery_plan)
        self.assertIs(ralph.parse_blockers, ralph_workflow.parse_blockers)
        self.assertIs(ralph.RunManifest, ralph_state.RunManifest)
        self.assertIs(ralph.OperatorRunManifest, ralph_state.OperatorRunManifest)

    def test_review_package_validation_rejects_external_style_tag_url(
        self,
    ) -> None:
        html = REVIEW_PACKAGE_HTML.replace(
            "</head>",
            "<style>body{background:url(https://example.com/leak.png)}</style></head>",
        )

        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "review-package.html"
            html_path.write_text(html, encoding="utf-8")

            with self.assertRaises(ralph.ReviewPackageFailure) as context:
                ralph.validate_review_package_html(
                    html_path,
                    issue_number=42,
                    changed_files=["scripts/ralph.py"],
                    qa_results=[],
                )

        self.assertIn("CSS url() assets", str(context.exception))

    def test_changed_marimo_notebook_routes_map_to_mounted_routes(self) -> None:
        self.assertEqual(
            ralph.changed_marimo_notebook_routes(
                [
                    "backend-services/marimo/notebooks/gas_market_prices.py",
                    "./backend-services/marimo/notebooks/gas_market_prices.py",
                    "backend-services/marimo/notebooks/head.html",
                    "backend-services/marimo/src/marimoserver/main.py",
                ]
            ),
            ("/marimo/gas_market_prices/",),
        )

    def test_review_package_validation_allows_sibling_webm_links(self) -> None:
        html = REVIEW_PACKAGE_HTML.replace(
            "</body>",
            '<p><a href="marimo__gas_market_prices__desktop.webm">'
            "desktop video</a></p></body>",
        )

        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "review-package.html"
            html_path.write_text(html, encoding="utf-8")

            summary = ralph.validate_review_package_html(
                html_path,
                issue_number=42,
                changed_files=["scripts/ralph.py"],
                qa_results=[],
            )

        self.assertEqual(summary.issue_number, 42)

    def test_review_package_validation_rejects_external_style_attribute_url(
        self,
    ) -> None:
        html = REVIEW_PACKAGE_HTML.replace(
            "<body>",
            '<body style="background-image:url(https://example.com/leak.png)">',
        )

        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "review-package.html"
            html_path.write_text(html, encoding="utf-8")

            with self.assertRaises(ralph.ReviewPackageFailure) as context:
                ralph.validate_review_package_html(
                    html_path,
                    issue_number=42,
                    changed_files=["scripts/ralph.py"],
                    qa_results=[],
                )

        self.assertIn("CSS url() assets", str(context.exception))

    def test_review_package_validation_rejects_url_bearing_asset_attributes(
        self,
    ) -> None:
        cases = {
            "srcset": (
                '<img srcset="https://example.com/leak.png 1x" alt="">',
                "srcset",
            ),
            "object archive": (
                '<object archive="https://example.com/a.jar"></object>',
                "archive",
            ),
        }

        for name, (snippet, expected) in cases.items():
            with self.subTest(name=name):
                html = REVIEW_PACKAGE_HTML.replace("</body>", f"{snippet}</body>")

                with tempfile.TemporaryDirectory() as tmp:
                    html_path = Path(tmp) / "review-package.html"
                    html_path.write_text(html, encoding="utf-8")

                    with self.assertRaises(ralph.ReviewPackageFailure) as context:
                        ralph.validate_review_package_html(
                            html_path,
                            issue_number=42,
                            changed_files=["scripts/ralph.py"],
                            qa_results=[],
                        )

                self.assertIn(expected, str(context.exception))

    def test_review_package_validation_rejects_relative_href_assets(
        self,
    ) -> None:
        cases = {
            "stylesheet": (
                '<link rel="stylesheet" href="review.css">',
                "relative URLs or embedded assets",
            ),
            "preload": (
                '<link rel="preload" as="image" href="review.png">',
                "relative URLs or embedded assets",
            ),
            "base": (
                '<base href="assets/">',
                "relative URLs or embedded assets",
            ),
        }

        for name, (snippet, expected) in cases.items():
            with self.subTest(name=name):
                html = REVIEW_PACKAGE_HTML.replace("</head>", f"{snippet}</head>")

                with tempfile.TemporaryDirectory() as tmp:
                    html_path = Path(tmp) / "review-package.html"
                    html_path.write_text(html, encoding="utf-8")

                    with self.assertRaises(ralph.ReviewPackageFailure) as context:
                        ralph.validate_review_package_html(
                            html_path,
                            issue_number=42,
                            changed_files=["scripts/ralph.py"],
                            qa_results=[],
                        )

                self.assertIn(expected, str(context.exception))

    def test_review_package_validation_rejects_meta_refresh_content_url(
        self,
    ) -> None:
        html = REVIEW_PACKAGE_HTML.replace(
            "</head>",
            (
                '<meta http-equiv="refresh" '
                'content="0; url=https://example.com/leak"></head>'
            ),
        )

        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "review-package.html"
            html_path.write_text(html, encoding="utf-8")

            with self.assertRaises(ralph.ReviewPackageFailure) as context:
                ralph.validate_review_package_html(
                    html_path,
                    issue_number=42,
                    changed_files=["scripts/ralph.py"],
                    qa_results=[],
                )

        self.assertIn("external URLs or embedded assets", str(context.exception))

    def test_review_package_validation_rejects_srcdoc_script_content(
        self,
    ) -> None:
        html = REVIEW_PACKAGE_HTML.replace(
            "</body>",
            '<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;"></iframe></body>',
        )

        with tempfile.TemporaryDirectory() as tmp:
            html_path = Path(tmp) / "review-package.html"
            html_path.write_text(html, encoding="utf-8")

            with self.assertRaises(ralph.ReviewPackageFailure) as context:
                ralph.validate_review_package_html(
                    html_path,
                    issue_number=42,
                    changed_files=["scripts/ralph.py"],
                    qa_results=[],
                )

        self.assertIn("srcdoc: script tag is not allowed", str(context.exception))

    def test_issue_completion_review_prompt_keeps_small_changed_file_list(
        self,
    ) -> None:
        issue = make_issue({ralph.READY_LABEL}, IMPLEMENTATION_BODY)
        delivery_plan = ralph.DeliveryPlan(
            mode=ralph.GITFLOW_MODE,
            target_branch=ralph.DEFAULT_GITFLOW_BRANCH,
            label=ralph.DELIVERY_GITFLOW_LABEL,
            add_labels=(),
            remove_labels=(),
        )
        changed_files = ["README.md", "docs/agents/ralph-loop.md"]
        trigger = ralph.issue_completion_review_trigger(
            issue=issue,
            delivery_plan=delivery_plan,
            changed_files=changed_files,
        )

        prompt = ralph.issue_completion_review_prompt(
            repo="example/repo",
            issue=issue,
            delivery_plan=delivery_plan,
            changed_files=changed_files,
            qa_results=[],
            run_dir=Path("/tmp/ralph-run"),
            trigger=trigger,
        )

        self.assertIn("- `README.md`\n- `docs/agents/ralph-loop.md`", prompt)
        self.assertNotIn("Total changed files", prompt)

    def test_issue_completion_review_prompt_summarizes_large_changed_file_list(
        self,
    ) -> None:
        issue = make_issue({ralph.READY_LABEL}, IMPLEMENTATION_BODY)
        delivery_plan = ralph.DeliveryPlan(
            mode=ralph.GITFLOW_MODE,
            target_branch=ralph.DEFAULT_GITFLOW_BRANCH,
            label=ralph.DELIVERY_GITFLOW_LABEL,
            add_labels=(),
            remove_labels=(),
        )
        generated_files = [
            "tools/gas-market-knowledge-base/generated/silver/chunks/"
            f"chunk-{index:03}.md"
            for index in range(600)
        ]
        changed_files = [
            *generated_files,
            "docs/agents/ralph-loop.md",
            "infrastructure/aws-pulumi/components/ecs_services.py",
        ]
        trigger = ralph.issue_completion_review_trigger(
            issue=issue,
            delivery_plan=delivery_plan,
            changed_files=changed_files,
        )

        prompt = ralph.issue_completion_review_prompt(
            repo="example/repo",
            issue=issue,
            delivery_plan=delivery_plan,
            changed_files=changed_files,
            qa_results=[],
            run_dir=Path("/tmp/ralph-run"),
            trigger=trigger,
        )

        self.assertLess(len(prompt), ralph.ISSUE_COMPLETION_REVIEW_PROMPT_CHAR_LIMIT)
        self.assertIn("- Total changed files: `602`", prompt)
        self.assertIn("`tools/gas-market-knowledge-base/generated/**`: 600", prompt)
        self.assertIn("- Risk-relevant paths kept verbatim:", prompt)
        self.assertIn("- `docs/agents/ralph-loop.md`", prompt)
        self.assertIn(
            "- `infrastructure/aws-pulumi/components/ecs_services.py`",
            prompt,
        )
        self.assertIn('"non_triggering_paths": {', prompt)
        self.assertIn('"total_count": 601', prompt)
        self.assertNotIn("chunk-599.md", prompt)

    def test_issue_completion_review_repair_prompt_summarizes_large_changed_file_list(
        self,
    ) -> None:
        generated_files = [
            "tools/gas-market-knowledge-base/generated/silver/chunks/"
            f"chunk-{index:03}.md"
            for index in range(600)
        ]
        changed_files = [
            *generated_files,
            "docs/agents/ralph-loop.md",
        ]

        prompt = ralph.issue_completion_review_repair_prompt(
            issue=make_issue({ralph.READY_LABEL}, IMPLEMENTATION_BODY),
            changed_files=changed_files,
            qa_results=[],
            findings="- Missing generated corpus policy update.",
            artifact_path=Path("/tmp/issue-completion-review.md"),
        )

        self.assertIn("Changed files before repair:", prompt)
        self.assertIn("- Total changed files: `601`", prompt)
        self.assertIn("`tools/gas-market-knowledge-base/generated/**`: 600", prompt)
        self.assertIn("- `docs/agents/ralph-loop.md`", prompt)
        self.assertNotIn("chunk-599.md", prompt)

    def test_issue_completion_review_prompt_size_guard_fails_before_codex(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({ralph.READY_LABEL}, IMPLEMENTATION_BODY)
            worktree_path, run_dir, manifest, _ = implementation_attempt_context(
                tmp_path,
                loop,
                issue,
            )
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            changed_files = ["docs/agents/ralph-loop.md"]
            trigger = ralph.issue_completion_review_trigger(
                issue=issue,
                delivery_plan=delivery_plan,
                changed_files=changed_files,
            )

            with patch.object(ralph, "ISSUE_COMPLETION_REVIEW_PROMPT_CHAR_LIMIT", 10):
                with self.assertRaisesRegex(
                    ralph.IssueFailure,
                    "Issue completion review prompt exceeded",
                ):
                    loop._run_issue_completion_review(
                        issue,
                        delivery_plan=delivery_plan,
                        changed_files=changed_files,
                        qa_results=[],
                        worktree_path=worktree_path,
                        run_dir=run_dir,
                        manifest=manifest,
                        trigger=trigger,
                        review_attempt=1,
                    )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        self.assertFalse(
            any(call.args[:2] == ("codex", "exec") for call in runner.calls)
        )
        self.assertEqual(
            manifest_payload["issue_completion_review"]["status"],
            "failed_prompt_too_large",
        )
        self.assertIn(
            "Issue completion review prompt exceeded",
            manifest_payload["issue_completion_review"]["failure"]["message"],
        )

    def test_run_manifest_records_adaptive_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, FakeRunner())
            issue = make_issue({ralph.READY_LABEL}, IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=issue,
                delivery_plan=delivery_plan,
                branch="agent/issue-42-implement-thing",
                worktree_path=tmp_path / "worktrees" / "issue",
                integration_path=tmp_path / "worktrees" / "integration",
                config=loop.config,
            )

            manifest.record_adaptive_event(
                "hard_stop",
                trigger_reason="Integration target verification failed.",
                residual_work_summary="Operator must inspect branch and issue metadata.",
            )
            manifest.record_adaptive_event(
                "gated_retry",
                trigger_reason="Unit test failed before Local integration.",
            )
            manifest.record_adaptive_event(
                "residual_update",
                trigger_reason="Ready issue refresh found stale blocker text.",
                issue_number=43,
                residual_work_summary="Refresh #43 blocker evidence.",
            )
            loaded = ralph.load_run_manifest(run_dir)

        adaptive_events = loaded.data["adaptive_events"]
        self.assertEqual(
            [event["event_type"] for event in adaptive_events],
            ["hard_stop", "gated_retry", "residual_update"],
        )
        hard_stop = adaptive_events[0]
        self.assertEqual(hard_stop["issue_number"], 42)
        self.assertFalse(hard_stop["automatic_retry_allowed"])
        self.assertFalse(hard_stop["consumes_attempt_budget"])
        self.assertIn("Operator must inspect", hard_stop["residual_work_summary"])
        gated_retry = adaptive_events[1]
        self.assertTrue(gated_retry["automatic_retry_allowed"])
        self.assertTrue(gated_retry["consumes_attempt_budget"])
        residual_update = adaptive_events[2]
        self.assertEqual(residual_update["issue_number"], 43)
        self.assertFalse(residual_update["automatic_retry_allowed"])
        self.assertFalse(residual_update["consumes_attempt_budget"])
        self.assertTrue(
            any(
                event["stage"] == "adaptive_hard_stop"
                for event in loaded.data["events"]
            )
        )

    def test_run_manifest_rejects_hard_stop_budget_consumption(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, FakeRunner())
            issue = make_issue({ralph.READY_LABEL}, IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            manifest = ralph.RunManifest.for_implementation(
                run_dir=tmp_path / "logs" / "issue-42-test",
                issue=issue,
                delivery_plan=delivery_plan,
                branch="agent/issue-42-implement-thing",
                worktree_path=tmp_path / "worktrees" / "issue",
                integration_path=tmp_path / "worktrees" / "integration",
                config=loop.config,
            )

            with self.assertRaises(ralph.RalphError) as caught:
                manifest.record_adaptive_event(
                    "hard_stop",
                    trigger_reason="Unsafe recovery boundary.",
                    automatic_retry_allowed=True,
                    consumes_attempt_budget=True,
                )

        self.assertIn("must not allow automatic Codex retry", str(caught.exception))

    def test_next_ready_issue_remains_oldest_first_without_deploy_repair_state(
        self,
    ) -> None:
        runner = FakeRunner(
            command_outputs={
                issue_list_command(): [
                    json.dumps(
                        [
                            issue_payload(
                                77,
                                [ralph.READY_LABEL],
                                created_at="2026-05-02T00:00:00Z",
                            ),
                            issue_payload(
                                76,
                                [ralph.READY_LABEL],
                                created_at="2026-05-01T00:00:00Z",
                            ),
                        ]
                    )
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner, drain=True)
            issue = loop._next_ready_issue()

        self.assertIsNotNone(issue)
        assert issue is not None
        self.assertEqual(issue.number, 76)

    def test_post_promotion_deployment_classifier_skips_agent_workflow_only(
        self,
    ) -> None:
        classification = ralph.classify_post_promotion_deployment(
            [
                ".agents/skills/ralph-loop/SKILL.md",
                "tools/ralph-loop/src/ralph_loop/cli.py",
                "docs/agents/ralph-loop.md",
            ]
        )

        self.assertEqual(
            classification.tier,
            ralph.POST_PROMOTION_DEPLOYMENT_NO_DEPLOY,
        )
        self.assertIn("Only Agent workflow changes", classification.reason)
        self.assertEqual(
            classification.agent_workflow_paths,
            (
                ".agents/skills/ralph-loop/SKILL.md",
                "docs/agents/ralph-loop.md",
                "tools/ralph-loop/src/ralph_loop/cli.py",
            ),
        )
        self.assertEqual(classification.deployable_paths, ())

    def test_post_promotion_deployment_classifier_selects_user_code_redeploy(
        self,
    ) -> None:
        classification = ralph.classify_post_promotion_deployment(
            [
                "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py",
                "backend-services/dagster-user/aemo-etl/Dockerfile",
            ]
        )

        self.assertEqual(
            classification.tier,
            ralph.POST_PROMOTION_DEPLOYMENT_USER_CODE,
        )
        self.assertEqual(
            classification.user_code_redeploy_paths,
            (
                "backend-services/dagster-user/aemo-etl/Dockerfile",
                "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py",
            ),
        )
        self.assertIn("redeploy-user-code", classification.recommended_action)
        self.assertEqual(classification.full_workflow_paths, ())

    def test_post_promotion_deployment_classifier_selects_full_workflow(
        self,
    ) -> None:
        cases = {
            "Pulumi": "infrastructure/aws-pulumi/__main__.py",
            "service runtime": "backend-services/dagster-core/dagster.aws.yaml",
            "image": "backend-services/authentication/Dockerfile",
            "Dagster core": "backend-services/dagster-core/Dockerfile",
            "auth": "backend-services/authentication/main.py",
            "Caddy": "backend-services/caddy/Caddyfile",
            "Marimo": "backend-services/marimo/src/marimoserver/main.py",
            "code-location topology": (
                "backend-services/dagster-core/code-locations.aws.toml"
            ),
        }

        for label, path in cases.items():
            with self.subTest(label=label):
                classification = ralph.classify_post_promotion_deployment([path])

                self.assertEqual(
                    classification.tier,
                    ralph.POST_PROMOTION_DEPLOYMENT_FULL,
                )
                self.assertEqual(classification.full_workflow_paths, (path,))
                self.assertIn(
                    "run-integration-tests", classification.recommended_action
                )

    def test_post_promotion_deployment_classifier_promotes_mixed_deployables_to_full(
        self,
    ) -> None:
        classification = ralph.classify_post_promotion_deployment(
            [
                "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py",
                "infrastructure/aws-pulumi/components/ecs_services.py",
            ]
        )

        self.assertEqual(
            classification.tier,
            ralph.POST_PROMOTION_DEPLOYMENT_FULL,
        )
        self.assertEqual(
            classification.deployable_paths,
            (
                "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py",
                "infrastructure/aws-pulumi/components/ecs_services.py",
            ),
        )

    def test_post_promotion_deployment_classifier_reports_agent_context(
        self,
    ) -> None:
        classification = ralph.classify_post_promotion_deployment(
            [
                ".agents/skills/ralph-loop/SKILL.md",
                "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py",
            ]
        )

        self.assertEqual(
            classification.tier,
            ralph.POST_PROMOTION_DEPLOYMENT_USER_CODE,
        )
        self.assertEqual(
            classification.agent_workflow_paths,
            (".agents/skills/ralph-loop/SKILL.md",),
        )
        self.assertIn(
            ".agents/skills/ralph-loop/SKILL.md",
            classification.non_triggering_paths,
        )

    def test_issue_completion_review_triggers_for_risk_signals(self) -> None:
        delivery_plan = ralph.DeliveryPlan(
            mode=ralph.GITFLOW_MODE,
            target_branch="dev",
            label=ralph.DELIVERY_GITFLOW_LABEL,
            add_labels=(),
            remove_labels=(),
        )
        issue = make_issue(
            {"ready-for-agent"},
            IMPLEMENTATION_BODY
            + "\n## Stiffness estimate\n\nHigh. The slice is broad.\n",
        )

        trigger = ralph.issue_completion_review_trigger(
            issue=issue,
            delivery_plan=delivery_plan,
            changed_files=[
                "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py",
                "docs/agents/ralph-loop.md",
            ],
        )

        self.assertTrue(trigger.required)
        self.assertEqual(
            trigger.reasons,
            (
                "deployable changed paths",
                "Agent workflow changes",
                "high-stiffness issue evidence",
            ),
        )
        self.assertEqual(
            trigger.deployment_classification.deployable_paths,
            ("backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py",),
        )

    def test_stiffness_ratio_evidence_parses_structured_high_ratio(self) -> None:
        body = (
            IMPLEMENTATION_BODY
            + """
## Stiffness estimate

- Step size: `1.0`
- Safe feedback step: `1.0`
- Hidden-coupling pressure: `2.5`
- Stiffness ratio: `2.5`
- Ratio level: `high`
- Recommended routing action: `human-review`
"""
        )

        evidence = ralph.stiffness_ratio_evidence(body)

        self.assertEqual(evidence.ratio_value, 2.5)
        self.assertEqual(evidence.ratio_level, "high")
        self.assertEqual(evidence.recommended_action, "human-review")
        self.assertTrue(evidence.completion_review_required)
        self.assertEqual(
            evidence.evidence,
            ("Declared Stiffness ratio is `2.5` (high).",),
        )

    def test_stiffness_ratio_evidence_parses_extreme_ratio_value(self) -> None:
        body = (
            IMPLEMENTATION_BODY
            + """
## Stiffness estimate

- Stiffness ratio: `4.0`
- Recommended action: `split`
"""
        )

        evidence = ralph.stiffness_ratio_evidence(body)

        self.assertEqual(evidence.ratio_value, 4.0)
        self.assertEqual(evidence.ratio_level, "extreme")
        self.assertEqual(evidence.recommended_action, "split")
        self.assertTrue(evidence.completion_review_required)

    def test_declared_high_stiffness_evidence_keeps_legacy_score(self) -> None:
        body = IMPLEMENTATION_BODY + "\nStiffness: `70` (medium)\n"

        self.assertEqual(
            ralph.declared_high_stiffness_evidence(body),
            ("Stiffness: `70` (medium)",),
        )

    def test_issue_completion_review_triggers_for_structured_ratio(self) -> None:
        trigger = ralph.issue_completion_review_trigger(
            issue=make_issue(
                {"ready-for-agent"},
                IMPLEMENTATION_BODY
                + """
## Stiffness estimate

- Stiffness ratio: `4.2`
- Ratio level: `extreme`
- Recommended routing action: `split`
""",
            ),
            delivery_plan=ralph.DeliveryPlan(
                mode=ralph.GITFLOW_MODE,
                target_branch="dev",
                label=ralph.DELIVERY_GITFLOW_LABEL,
                add_labels=(),
                remove_labels=(),
            ),
            changed_files=["README.md"],
        )

        self.assertTrue(trigger.required)
        self.assertEqual(trigger.reasons, ("high-stiffness issue evidence",))
        self.assertEqual(
            trigger.high_stiffness_evidence,
            ("Declared Stiffness ratio is `4.2` (extreme).",),
        )
        self.assertEqual(
            trigger.to_manifest()["stiffness_ratio_evidence"],
            {
                "ratio_value": 4.2,
                "ratio_level": "extreme",
                "recommended_action": "split",
                "operator_override": None,
                "operator_override_requires_review": False,
                "completion_review_required": True,
                "evidence": ["Declared Stiffness ratio is `4.2` (extreme)."],
            },
        )

    def test_issue_completion_review_triggers_for_override_required(self) -> None:
        trigger = ralph.issue_completion_review_trigger(
            issue=make_issue(
                {"ready-for-agent"},
                IMPLEMENTATION_BODY
                + """
## Stiffness estimate

- Stiffness ratio: `1.2`
- Ratio level: `low`
- Recommended routing action: `ready`
- Operator override: Requires Issue completion review before Local integration.
""",
            ),
            delivery_plan=ralph.DeliveryPlan(
                mode=ralph.GITFLOW_MODE,
                target_branch="dev",
                label=ralph.DELIVERY_GITFLOW_LABEL,
                add_labels=(),
                remove_labels=(),
            ),
            changed_files=["README.md"],
        )

        self.assertTrue(trigger.required)
        self.assertEqual(trigger.reasons, ("high-stiffness issue evidence",))
        self.assertEqual(
            trigger.high_stiffness_evidence,
            ("Operator override requires Issue completion review.",),
        )
        self.assertTrue(
            trigger.stiffness_ratio_evidence.operator_override_requires_review
        )

    def test_issue_completion_review_ignores_non_required_override(self) -> None:
        trigger = ralph.issue_completion_review_trigger(
            issue=make_issue(
                {"ready-for-agent"},
                IMPLEMENTATION_BODY
                + """
## Stiffness estimate

- Stiffness ratio: `1.2`
- Ratio level: `low`
- Recommended routing action: `ready`
- Operator override: Review is not required for this bounded issue.
""",
            ),
            delivery_plan=ralph.DeliveryPlan(
                mode=ralph.GITFLOW_MODE,
                target_branch="dev",
                label=ralph.DELIVERY_GITFLOW_LABEL,
                add_labels=(),
                remove_labels=(),
            ),
            changed_files=["README.md"],
        )

        self.assertFalse(trigger.required)
        self.assertEqual(trigger.high_stiffness_evidence, ())
        self.assertFalse(
            trigger.stiffness_ratio_evidence.operator_override_requires_review
        )

    def test_issue_completion_review_triggers_for_trunk_delivery(self) -> None:
        trigger = ralph.issue_completion_review_trigger(
            issue=make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY),
            delivery_plan=ralph.DeliveryPlan(
                mode=ralph.TRUNK_MODE,
                target_branch="main",
                label=ralph.DELIVERY_TRUNK_LABEL,
                add_labels=(),
                remove_labels=(),
            ),
            changed_files=["README.md"],
        )

        self.assertTrue(trigger.required)
        self.assertEqual(trigger.reasons, ("Trunk delivery",))

    def test_issue_completion_review_skips_low_risk_gitflow_change(self) -> None:
        trigger = ralph.issue_completion_review_trigger(
            issue=make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY),
            delivery_plan=ralph.DeliveryPlan(
                mode=ralph.GITFLOW_MODE,
                target_branch="dev",
                label=ralph.DELIVERY_GITFLOW_LABEL,
                add_labels=(),
                remove_labels=(),
            ),
            changed_files=["README.md"],
        )

        self.assertFalse(trigger.required)
        self.assertEqual(trigger.reasons, ())

    def test_direct_promotion_records_and_prints_deployment_classification(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = make_loop(tmp_path, runner, promote=True).config
            loop = PromotionClassificationProbeLoop(
                config,
                runner,
                [
                    ".agents/skills/ralph-loop/SKILL.md",
                    "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py",
                ],
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                manifest = loop._promote()

            payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        deployment = payload["deployment_classification"]
        self.assertEqual(deployment["status"], "classified")
        self.assertEqual(
            deployment["tier"],
            ralph.POST_PROMOTION_DEPLOYMENT_USER_CODE,
        )
        self.assertEqual(
            deployment["agent_workflow_paths"],
            [".agents/skills/ralph-loop/SKILL.md"],
        )
        recovery = payload["source_table_replay_recovery"]
        self.assertEqual(
            recovery["status"],
            ralph.POST_PROMOTION_SOURCE_TABLE_REPLAY_NOT_REQUIRED,
        )
        self.assertEqual(recovery["affected_tables"], [])
        self.assertIn("Post-Promotion deployment tier", stdout.getvalue())
        self.assertIn("redeploy-user-code", stdout.getvalue())
        self.assertNotIn("aemo-replay-bronze-archive", stdout.getvalue())
        deployment_commands = {
            ralph.POST_PROMOTION_DEPLOYMENT_REDEPLOY_USER_CODE_COMMAND,
            ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_COMMAND,
        }
        self.assertFalse(
            any(
                call.args and call.args[0] in deployment_commands
                for call in runner.calls
            )
        )

    def test_direct_promotion_records_source_table_replay_recovery_guidance(
        self,
    ) -> None:
        gbb_path = (
            "backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/gbb/"
            "gasbb_field_interest_v2.py"
        )
        vicgas_path = (
            "backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/vicgas/"
            "int934_v4_ecgs_contacts_1.py"
        )
        gbb_old = """
defs = df_from_s3_keys_definitions_factory(
    domain="gbb",
    name_suffix="gasbb_field_interest_v2",
    glob_pattern="gasbbgasfieldinterest*",
    schema={},
    schema_descriptions={},
    surrogate_key_sources=["FieldInterestId", "CompanyId", "EffectiveDate"],
)
"""
        gbb_new = """
defs = df_from_s3_keys_definitions_factory(
    domain="gbb",
    name_suffix="gasbb_field_interest_v2",
    glob_pattern="gasbbgasfieldinterest*",
    schema={},
    schema_descriptions={},
    surrogate_key_sources=[
        "FieldInterestId",
        "CompanyId",
        "EffectiveDate",
        "GroupMembers",
    ],
)
"""
        vicgas_old = """
defs = df_from_s3_keys_definitions_factory(
    domain="vicgas",
    name_suffix="int934_v4_ecgs_contacts_1",
    glob_pattern="int934_v4_ecgs_contacts_1*",
    schema={},
    schema_descriptions={},
    surrogate_key_sources=["company_id", "first_name", "last_name"],
)
"""
        vicgas_new = """
defs = df_from_s3_keys_definitions_factory(
    domain="vicgas",
    name_suffix="int934_v4_ecgs_contacts_1",
    glob_pattern="int934_v4_ecgs_contacts_1*",
    schema={},
    schema_descriptions={},
    surrogate_key_sources=[
        "company_id",
        "first_name",
        "last_name",
        "contact_email",
    ],
)
"""
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config = make_loop(tmp_path, runner, promote=True).config
            loop = PromotionClassificationProbeLoop(
                config,
                runner,
                [gbb_path, vicgas_path],
                file_texts={
                    ("origin/main", gbb_path): gbb_old,
                    ("source-sha", gbb_path): gbb_new,
                    ("origin/main", vicgas_path): vicgas_old,
                    ("source-sha", vicgas_path): vicgas_new,
                },
            )

            stdout = io.StringIO()
            with redirect_stdout(stdout):
                manifest = loop._promote()

            payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        deployment = payload["deployment_classification"]
        self.assertEqual(
            deployment["tier"],
            ralph.POST_PROMOTION_DEPLOYMENT_USER_CODE,
        )
        recovery = payload["source_table_replay_recovery"]
        self.assertEqual(
            recovery["status"],
            ralph.POST_PROMOTION_SOURCE_TABLE_REPLAY_REQUIRED,
        )
        self.assertEqual(
            [table["table_id"] for table in recovery["affected_tables"]],
            [
                "gbb.bronze_gasbb_field_interest_v2",
                "vicgas.bronze_int934_v4_ecgs_contacts_1",
            ],
        )
        self.assertEqual(
            recovery["affected_tables"][0]["old_surrogate_key_sources"],
            ["FieldInterestId", "CompanyId", "EffectiveDate"],
        )
        self.assertEqual(
            recovery["affected_tables"][0]["new_surrogate_key_sources"],
            ["FieldInterestId", "CompanyId", "EffectiveDate", "GroupMembers"],
        )
        self.assertEqual(
            recovery["affected_tables"][1]["old_surrogate_key_sources"],
            ["company_id", "first_name", "last_name"],
        )
        self.assertEqual(
            recovery["affected_tables"][1]["new_surrogate_key_sources"],
            ["company_id", "first_name", "last_name", "contact_email"],
        )
        for table in recovery["affected_tables"]:
            self.assertEqual(table["dry_run"]["cwd"], ralph.AEMO_ETL_SUBPROJECT_PATH)
            self.assertEqual(table["replace"]["cwd"], ralph.AEMO_ETL_SUBPROJECT_PATH)
            self.assertIn("aemo-replay-bronze-archive", table["dry_run"]["command"])
            self.assertNotIn("--replace", table["dry_run"]["command"])
            self.assertIn("--replace", table["replace"]["command"])

        output = stdout.getvalue()
        self.assertIn("Post-Promotion deployment tier: user_code_redeploy", output)
        self.assertIn("Source-table archive replay recovery required", output)
        self.assertIn(
            "uv run aemo-replay-bronze-archive --table "
            "gbb.bronze_gasbb_field_interest_v2",
            output,
        )
        self.assertIn(
            "uv run aemo-replay-bronze-archive --table "
            "vicgas.bronze_int934_v4_ecgs_contacts_1 --replace",
            output,
        )

    def test_parse_repo_slug_accepts_common_github_remote_forms(self) -> None:
        cases = {
            "git@github.com:Owner/repo.git": "Owner/repo",
            "https://github.com/Owner/repo.git": "Owner/repo",
            "https://github.com/Owner/repo": "Owner/repo",
            "ssh://git@github.com/Owner/repo.git": "Owner/repo",
        }
        for remote, expected in cases.items():
            with self.subTest(remote=remote):
                self.assertEqual(ralph.parse_repo_slug(remote), expected)

    def test_issue_from_gh_counts_comment_lists_from_issue_list_payload(self) -> None:
        issue = ralph.Issue.from_gh(
            {
                "number": 42,
                "title": "Implement thing",
                "body": "",
                "labels": [{"name": "ready-for-agent"}],
                "createdAt": "2026-04-30T00:00:00Z",
                "updatedAt": "2026-04-30T00:00:00Z",
                "url": "https://github.com/example/repo/issues/42",
                "comments": [{"id": "one"}, {"id": "two"}],
                "author": {"login": "reporter"},
            }
        )

        self.assertEqual(issue.comments, 2)

    def test_ready_issue_refresh_notes_filter_limit_and_order_by_created_at(
        self,
    ) -> None:
        comments = [
            {
                "body": ready_issue_refresh_body("refresh 4"),
                "createdAt": "2026-05-04T00:00:00Z",
            },
            {
                "body": "Normal maintainer comment.",
                "createdAt": "2026-05-08T00:00:00Z",
            },
            {
                "body": f"{ralph.AI_TRIAGE_DISCLAIMER}\n\nTriage comment.",
                "createdAt": "2026-05-09T00:00:00Z",
            },
            {
                "body": ready_issue_refresh_body("refresh 2"),
                "createdAt": "2026-05-02T00:00:00Z",
            },
            {
                "body": ready_issue_refresh_body("refresh 7"),
                "createdAt": "2026-05-07T00:00:00Z",
            },
            {
                "body": ready_issue_refresh_body("refresh 1"),
                "createdAt": "2026-05-01T00:00:00Z",
            },
            {
                "body": ready_issue_refresh_body("refresh 5"),
                "createdAt": "2026-05-05T00:00:00Z",
            },
            {
                "body": ready_issue_refresh_body("refresh 3"),
                "createdAt": "2026-05-03T00:00:00Z",
            },
            {
                "body": ready_issue_refresh_body("refresh 6"),
                "createdAt": "2026-05-06T00:00:00Z",
            },
        ]

        notes = ralph.ready_issue_refresh_notes(comments)

        self.assertEqual(
            notes,
            [
                ready_issue_refresh_body("refresh 3"),
                ready_issue_refresh_body("refresh 4"),
                ready_issue_refresh_body("refresh 5"),
                ready_issue_refresh_body("refresh 6"),
                ready_issue_refresh_body("refresh 7"),
            ],
        )

    def test_ready_issue_refresh_notes_preserve_input_order_without_timestamps(
        self,
    ) -> None:
        comments = [
            {"body": ready_issue_refresh_body(f"refresh {index}")}
            for index in range(1, 7)
        ]

        notes = ralph.ready_issue_refresh_notes(comments)

        self.assertEqual(
            notes,
            [
                ready_issue_refresh_body("refresh 2"),
                ready_issue_refresh_body("refresh 3"),
                ready_issue_refresh_body("refresh 4"),
                ready_issue_refresh_body("refresh 5"),
                ready_issue_refresh_body("refresh 6"),
            ],
        )

    def test_implementation_prompt_places_refresh_notes_after_issue_body(self) -> None:
        issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
        note = ready_issue_refresh_body("Blocker #68 was satisfied on main.")

        prompt = ralph.implementation_prompt(issue, ready_issue_refresh_notes=[note])

        body_index = prompt.index(IMPLEMENTATION_BODY.strip())
        section_index = prompt.index("Recent Ready issue refresh notes:")
        note_index = prompt.index(note)
        self.assertLess(body_index, section_index)
        self.assertLess(section_index, note_index)
        self.assertIn("## What to build", prompt[:section_index])
        self.assertIn(
            "Treat the issue body above as the primary implementation contract.", prompt
        )

    def test_implementation_prompt_omits_refresh_section_when_no_notes(self) -> None:
        issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

        prompt = ralph.implementation_prompt(issue, ready_issue_refresh_notes=[])

        self.assertNotIn("Recent Ready issue refresh notes:", prompt)

    def test_slugify_limits_and_normalizes_titles(self) -> None:
        self.assertEqual(
            ralph.slugify("Introduce shared S3 pending-object planning!"),
            "introduce-shared-s3-pending-object-planning",
        )
        self.assertEqual(ralph.slugify("!!!"), "issue")
        self.assertLessEqual(len(ralph.slugify("x" * 100)), 56)

    def test_load_exploratory_acceptance_decisions_accepts_review_issue_shape(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decision_file = Path(tmp) / "decisions.json"
            decision_file.write_text(
                json.dumps(
                    {
                        "issues": [
                            {
                                "issue": {"number": 42},
                                "decision": "accept",
                                "reason": "Looks good.",
                            },
                            {
                                "issue_number": "43",
                                "decision": "hold",
                                "reason": "Waiting for operator review.",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            decisions = ralph.load_exploratory_acceptance_decisions(decision_file)

        self.assertEqual(
            decisions,
            [
                ralph.ExploratoryAcceptanceDecision(42, "accept", "Looks good."),
                ralph.ExploratoryAcceptanceDecision(
                    43,
                    "hold",
                    "Waiting for operator review.",
                ),
            ],
        )

    def test_load_exploratory_acceptance_decisions_rejects_missing_hold_reason(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decision_file = Path(tmp) / "decisions.json"
            decision_file.write_text(
                json.dumps({"decisions": [{"issue_number": 42, "decision": "hold"}]}),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError) as context:
                ralph.load_exploratory_acceptance_decisions(decision_file)

        self.assertIn("non-empty reason", str(context.exception))

    def test_required_issue_sections_are_case_insensitive(self) -> None:
        body = """## What to build
Build it.

## Acceptance criteria
- [ ] It works.

## Blocked by
None
"""
        self.assertEqual(ralph.missing_required_sections(body), [])

    def test_required_issue_sections_report_missing_or_empty_sections(self) -> None:
        body = """## What to build
Build it.

## Acceptance criteria
"""
        self.assertEqual(
            ralph.missing_required_sections(body),
            ["Acceptance criteria", "Blocked by"],
        )

    def test_exploratory_required_issue_sections_include_review_focus(self) -> None:
        required_sections = ralph.required_issue_sections_for_delivery_mode(
            ralph.EXPLORATORY_MODE
        )

        self.assertEqual(
            ralph.missing_required_sections(
                IMPLEMENTATION_BODY,
                required_sections=required_sections,
            ),
            ["Review focus"],
        )
        self.assertEqual(
            ralph.missing_required_sections(
                EXPLORATORY_IMPLEMENTATION_BODY,
                required_sections=required_sections,
            ),
            [],
        )

    def test_operator_smoke_section_parses_valid_request(self) -> None:
        request = ralph.parse_operator_smoke_request(OPERATOR_SMOKE_BODY)

        self.assertIsNotNone(request)
        assert request is not None
        self.assertEqual(request.smoke_id, "ec2-run-worker-placement")
        self.assertEqual(request.timeout_seconds, 120)
        self.assertIn("operator-owned", request.prose)

    def test_operator_smoke_rejects_unknown_smoke_id(self) -> None:
        body = OPERATOR_SMOKE_BODY.replace(
            "Smoke id: ec2-run-worker-placement",
            "Smoke id: unknown-smoke",
        )
        issue = make_issue(
            {ralph.DELIVERY_EXPLORATORY_LABEL},
            body,
        )
        plan = ralph.resolve_delivery_plan(
            issue,
            default_mode=ralph.GITFLOW_MODE,
            target_branch=None,
        )

        with self.assertRaises(ralph.IssueFailure) as context:
            ralph.validate_operator_smoke_request(issue, delivery_plan=plan)

        self.assertIn(
            "Unknown Operator smoke id `unknown-smoke`", str(context.exception)
        )

    def test_operator_smoke_rejects_non_exploratory_delivery(self) -> None:
        issue = make_issue({ralph.DELIVERY_GITFLOW_LABEL}, OPERATOR_SMOKE_BODY)
        plan = ralph.resolve_delivery_plan(
            issue,
            default_mode=ralph.GITFLOW_MODE,
            target_branch=None,
        )

        with self.assertRaises(ralph.IssueFailure) as context:
            ralph.validate_operator_smoke_request(issue, delivery_plan=plan)

        self.assertIn("only supported for Exploratory delivery", str(context.exception))

    def test_post_promotion_followup_validation_requires_ready_contract(self) -> None:
        valid = ralph.PostPromotionFollowupDraft(
            title="Create follow-up",
            body=IMPLEMENTATION_BODY,
            labels=("enhancement", "delivery-gitflow"),
            finding_id="create-follow-up",
        )
        invalid = ralph.PostPromotionFollowupDraft(
            title="Incomplete follow-up",
            body="## What to build\nBuild it.\n",
            labels=("delivery-gitflow",),
            finding_id="incomplete-follow-up",
        )

        valid_result = ralph.validate_post_promotion_followup_draft(valid)
        invalid_result = ralph.validate_post_promotion_followup_draft(invalid)

        self.assertTrue(valid_result.ready)
        self.assertEqual(
            valid_result.labels,
            ("delivery-gitflow", "enhancement", "ready-for-agent"),
        )
        self.assertFalse(invalid_result.ready)
        self.assertEqual(invalid_result.labels, ("needs-triage",))
        self.assertTrue(
            any(
                "Missing required issue section" in reason
                for reason in invalid_result.reasons
            )
        )
        self.assertTrue(
            any("category label" in reason for reason in invalid_result.reasons)
        )

    def test_post_promotion_followup_drafts_parse_structured_json_section(self) -> None:
        drafts = ralph.post_promotion_followup_drafts_from_markdown(
            POST_PROMOTION_REVIEW_MARKDOWN
        )

        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0].finding_id, "harden-promotion-evidence-checks")
        self.assertEqual(drafts[0].title, "Harden Promotion evidence checks")
        self.assertIn("## What to build", drafts[0].body)
        self.assertEqual(drafts[0].labels, ("delivery-gitflow", "enhancement"))

    def test_deploy_repair_validation_requires_bug_ready_contract(self) -> None:
        valid = ralph.DeployRepairDraft(
            title="Repair deployment",
            body=DEPLOY_REPAIR_BODY,
            labels=("bug", "delivery-gitflow"),
            finding_id="repair-deployment",
        )
        invalid = ralph.DeployRepairDraft(
            title="Incomplete repair",
            body="## What to build\nRepair it.\n",
            labels=("enhancement", "delivery-gitflow"),
            finding_id="incomplete-repair",
        )

        valid_result = ralph.validate_deploy_repair_draft(valid)
        invalid_result = ralph.validate_deploy_repair_draft(invalid)

        self.assertTrue(valid_result.ready)
        self.assertEqual(
            valid_result.labels,
            ("bug", "delivery-gitflow", "ready-for-agent"),
        )
        self.assertFalse(invalid_result.ready)
        self.assertEqual(invalid_result.labels, ("needs-triage",))
        self.assertTrue(
            any(
                "Missing required issue section" in reason
                for reason in invalid_result.reasons
            )
        )
        self.assertTrue(
            any(
                "Expected deploy-repair category label `bug`" in reason
                for reason in invalid_result.reasons
            )
        )

    def test_deploy_repair_drafts_parse_structured_json_section(self) -> None:
        drafts = ralph.deploy_repair_drafts_from_markdown(
            DEPLOY_FAILURE_ANALYSIS_MARKDOWN
        )

        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0].finding_id, "restore-operator-deployment")
        self.assertEqual(
            drafts[0].title, "Repair checkpointed Operator deployment failure"
        )
        self.assertIn("## QA/deploy verification plan", drafts[0].body)
        self.assertEqual(drafts[0].labels, ("bug", "delivery-gitflow"))

    def test_deploy_failure_analysis_prompt_redacts_and_prohibits_mutation(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            _, manifest, classification, command, _ = deploy_repair_test_context(
                tmp_path,
                loop,
            )
            redacted_log = ralph.redact_deploy_failure_evidence(
                "AWS_SECRET_ACCESS_KEY=raw-secret-value\n"
                "PULUMI_ACCESS_TOKEN=pulumi-secret-value\n"
                "token=generic-secret\n"
            )
            prompt = ralph.deploy_failure_analysis_prompt(
                repo=loop.config.repo,
                classification=classification,
                command=command,
                manifest=manifest,
                deployment_execution=manifest.data["deployment_execution"],
                redacted_command_log=redacted_log,
            )

        self.assertNotIn("raw-secret-value", prompt)
        self.assertNotIn("pulumi-secret-value", prompt)
        self.assertNotIn("generic-secret", prompt)
        self.assertIn("Do not edit repo files, commit, push", prompt)
        self.assertIn("run AWS commands", prompt)
        self.assertIn("run Pulumi", prompt)
        self.assertIn("create GitHub Issues", prompt)
        self.assertIn("Changed-file classification", prompt)
        self.assertIn("Deployed-test failure summaries", prompt)
        self.assertIn("Redacted command logs", prompt)

    def test_parse_blockers_reads_issue_references_from_blocked_by_section(
        self,
    ) -> None:
        body = """## What to build
Build it.

## Blocked by
- #25
- https://github.com/example/repo/issues/19
- #25

## Notes
#999 is unrelated because it is outside the section.
"""
        self.assertEqual(ralph.parse_blockers(body), [19, 25])

    def test_ready_candidate_requires_ready_label_and_no_stop_labels(self) -> None:
        self.assertTrue(ralph.is_ready_candidate(make_issue({"ready-for-agent"})))
        self.assertFalse(ralph.is_ready_candidate(make_issue({"needs-triage"})))
        self.assertFalse(
            ralph.is_ready_candidate(make_issue({"ready-for-agent", "agent-running"}))
        )
        self.assertFalse(
            ralph.is_ready_candidate(make_issue({"ready-for-agent", "agent-merged"}))
        )
        self.assertFalse(
            ralph.is_ready_candidate(make_issue({"ready-for-agent", "agent-reviewing"}))
        )

    def test_ready_issue_refresh_candidates_include_gitflow_dependents(self) -> None:
        issues = [
            make_issue(
                {"ready-for-agent"},
                implementation_body_with_blockers(42),
                number=43,
                title="Follow-on work",
            ),
            make_issue(
                {"ready-for-agent"},
                implementation_body_with_blockers(99),
                number=44,
                title="Still blocked follow-on work",
            ),
        ]

        candidates = ralph.select_ready_issue_refresh_candidates(
            issues,
            just_integrated_issue_number=42,
            blocker_state=lambda _number: "OPEN",
        )

        self.assertEqual([issue.number for issue in candidates], [43])

    def test_ready_issue_refresh_candidates_include_trunk_closed_blocker_dependents(
        self,
    ) -> None:
        issues = [
            make_issue(
                {"ready-for-agent"},
                implementation_body_with_blockers(42),
                number=43,
                title="Trunk follow-on work",
            )
        ]

        candidates = ralph.select_ready_issue_refresh_candidates(
            issues,
            just_integrated_issue_number=42,
            blocker_state=lambda _number: "CLOSED",
        )

        self.assertEqual([issue.number for issue in candidates], [43])

    def test_ready_issue_refresh_candidates_include_next_ready_issues_in_queue_order(
        self,
    ) -> None:
        issues = [
            make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43),
            make_issue({"needs-triage"}, IMPLEMENTATION_BODY, number=44),
            make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=45),
        ]

        candidates = ralph.select_ready_issue_refresh_candidates(
            issues,
            just_integrated_issue_number=42,
            blocker_state=lambda _number: "CLOSED",
        )

        self.assertEqual([issue.number for issue in candidates], [43, 45])

    def test_ready_issue_refresh_candidates_exclude_stop_labels(self) -> None:
        stop_labels = [
            "agent-running",
            "agent-failed",
            "agent-merged",
            "agent-integrated",
            "agent-reviewing",
        ]
        issues = [
            make_issue(
                {"ready-for-agent", stop_label}, IMPLEMENTATION_BODY, number=number
            )
            for number, stop_label in enumerate(stop_labels, start=43)
        ]

        candidates = ralph.select_ready_issue_refresh_candidates(
            issues,
            just_integrated_issue_number=42,
            blocker_state=lambda _number: "CLOSED",
        )

        self.assertEqual(candidates, [])

    def test_post_promotion_ready_issue_refresh_candidates_include_retriage_blockers(
        self,
    ) -> None:
        issues = [
            make_issue(
                {"needs-triage"},
                implementation_body_with_blockers(42),
                number=117,
                title="Blocked only by promoted issue",
            ),
            make_issue(
                {"needs-triage"},
                implementation_body_with_blockers(42, 99),
                number=118,
                title="Still has an open blocker",
            ),
            make_issue(
                {"ready-for-agent"},
                IMPLEMENTATION_BODY,
                number=122,
                title="Existing ready issue",
            ),
            make_issue(
                {"needs-triage", "agent-running"},
                implementation_body_with_blockers(42),
                number=123,
                title="Runtime labels still block refresh",
            ),
        ]

        candidates = ralph.select_post_promotion_ready_issue_refresh_candidates(
            issues,
            promoted_issue_numbers={42},
            blocker_state=lambda number: "OPEN" if number == 99 else "CLOSED",
        )

        self.assertEqual([issue.number for issue in candidates], [117, 122])

    def test_ready_issue_refresh_candidates_respect_issue_limit_scan_bound(
        self,
    ) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "2",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        runner = FakeRunner(
            command_outputs={
                issue_list_command: [
                    json.dumps(
                        [
                            issue_payload(43, ["ready-for-agent"]),
                            issue_payload(44, ["ready-for-agent"]),
                        ]
                    )
                ]
            }
        )

        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner, issue_limit=2)
            candidates = loop._ready_issue_refresh_candidates(
                make_issue({"agent-merged"}, number=42)
            )

        self.assertEqual([issue.number for issue in candidates], [43, 44])
        self.assertIn(issue_list_command, [call.args for call in runner.calls])

    def test_ready_issue_refresh_analysis_prompt_is_read_only_and_contains_context(
        self,
    ) -> None:
        integrated_issue = make_issue(
            {"agent-merged"},
            IMPLEMENTATION_BODY,
            number=42,
            title="Integrated work",
        )
        candidate = make_issue(
            {"ready-for-agent"},
            implementation_body_with_blockers(42),
            number=43,
            title="Refresh candidate",
        )
        delivery_plan = ralph.DeliveryPlan(
            mode=ralph.TRUNK_MODE,
            target_branch="main",
            label=ralph.DELIVERY_TRUNK_LABEL,
            add_labels=(),
            remove_labels=(),
        )
        qa_result = ralph.QAResult(
            command=ralph.QACommand(
                ("make", "run-prek"),
                Path("/repo"),
                "Ralph loop Commit check",
            ),
            log_path=Path("/logs/qa.log"),
        )

        prompt = ralph.ready_issue_refresh_analysis_prompt(
            repo="example/repo",
            integrated_issue=integrated_issue,
            delivery_plan=delivery_plan,
            commit_sha="merge-sha",
            changed_files=["scripts/ralph.py"],
            qa_results=[qa_result],
            run_dir=Path("/logs/issue-42-test"),
            candidates=[candidate],
            adaptive_events=[
                {
                    "event_type": "residual_update",
                    "issue_number": 43,
                    "trigger_reason": "Candidate blocker was satisfied by Local integration.",
                    "residual_work_summary": "Refresh #43 blocker evidence before claim.",
                    "automatic_retry_allowed": False,
                    "consumes_attempt_budget": False,
                }
            ],
            completed_issue_ratio_evidence=(
                "1 completed issue out of 2 refresh-visible issues."
            ),
        )

        self.assertIn("Use the repo-local $ralph-issue-refresh skill", prompt)
        self.assertIn(
            "Do not comment, edit labels, edit issue bodies, close issues", prompt
        )
        self.assertIn(
            "Do not run `gh issue comment`, `gh issue edit`, `gh issue close`", prompt
        )
        self.assertIn("commit, push, pull, fetch, merge, rebase, reset", prompt)
        self.assertIn("Delivery mode: `trunk`", prompt)
        self.assertIn("Integration target: `main`", prompt)
        self.assertIn("Local integration commit: `merge-sha`", prompt)
        self.assertIn("- `scripts/ralph.py`", prompt)
        self.assertIn("`make run-prek` from `/repo`", prompt)
        self.assertIn("Run logs: `/logs/issue-42-test`", prompt)
        self.assertIn("## What to build", prompt)
        self.assertIn("### Candidate issue #43: Refresh candidate", prompt)
        self.assertIn("- #42", prompt)
        self.assertIn("# Ready Issue Refresh Analysis", prompt)
        self.assertIn("## Candidate Issue Update Plan", prompt)
        self.assertIn("## Candidate Issue Mutation Plan", prompt)
        self.assertIn("ready_issue_refresh_mutations", prompt)
        self.assertIn("Completed issue ratio evidence", prompt)
        self.assertIn("1 completed issue out of 2 refresh-visible issues.", prompt)
        self.assertIn("Adaptive events recorded during this run", prompt)
        self.assertIn("`residual_update` for #43", prompt)
        self.assertIn("Refresh #43 blocker evidence before claim.", prompt)
        self.assertIn("Residual work summary", prompt)
        self.assertIn("blocker_update_note", prompt)
        self.assertIn("split_note", prompt)
        self.assertIn("routing_hint", prompt)
        self.assertIn("Do not propose global policy, threshold", prompt)

    def test_ready_issue_refresh_mutation_parser_enforces_comment_prefix(self) -> None:
        candidate = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43)

        mutations = ralph.ready_issue_refresh_mutations_from_markdown(
            READY_ISSUE_REFRESH_NEEDS_TRIAGE_MARKDOWN,
            candidates=[candidate],
        )

        self.assertEqual(len(mutations), 1)
        self.assertEqual(mutations[0].action, "needs_triage")
        self.assertEqual(mutations[0].add_labels, (ralph.NEEDS_TRIAGE_LABEL,))
        self.assertIn(ralph.READY_LABEL, mutations[0].remove_labels)
        assert mutations[0].comment is not None
        self.assertTrue(
            mutations[0].comment.startswith(ralph.AI_READY_ISSUE_REFRESH_DISCLAIMER)
        )

    def test_ready_issue_refresh_mutation_parser_accepts_adaptive_fields(
        self,
    ) -> None:
        candidate = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43)
        markdown = """# Ready Issue Refresh Analysis

## Candidate Issue Mutation Plan

```json
{
  "ready_issue_refresh_mutations": [
    {
      "issue_number": 43,
      "action": "update",
      "comment": "Blocker evidence refreshed after Local integration.",
      "completed_issue_ratio_evidence": "1 of 2 refresh-visible issues completed.",
      "residual_work_summary": "Update Blocked by after #42 integration.",
      "blocker_update_note": "Remove #42 from Blocked by.",
      "split_note": "Keep remaining work in the same queue-local issue.",
      "routing_hint": "Ready after blocker evidence refresh.",
      "unsupported_queue_note": {"ignored": true},
      "adaptive_event": {
        "event_type": "residual_update",
        "issue_number": 43,
        "trigger_reason": "Local integration satisfied #42.",
        "residual_work_summary": "Refresh #43 before next claim.",
        "automatic_retry_allowed": false,
        "consumes_attempt_budget": false
      }
    }
  ]
}
```
"""

        mutations = ralph.ready_issue_refresh_mutations_from_markdown(
            markdown,
            candidates=[candidate],
        )

        self.assertEqual(len(mutations), 1)
        mutation = mutations[0]
        self.assertEqual(mutation.action, "update")
        assert mutation.adaptive_metadata is not None
        self.assertEqual(
            mutation.adaptive_metadata["completed_issue_ratio_evidence"],
            "1 of 2 refresh-visible issues completed.",
        )
        self.assertEqual(
            mutation.adaptive_metadata["adaptive_event"]["event_type"],
            "residual_update",
        )
        self.assertEqual(
            mutation.adaptive_metadata["blocker_update_note"],
            "Remove #42 from Blocked by.",
        )
        self.assertNotIn("unsupported_queue_note", mutation.adaptive_metadata)

    def test_ready_issue_refresh_mutation_parser_rejects_global_threshold_fields(
        self,
    ) -> None:
        candidate = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43)
        markdown = """# Ready Issue Refresh Analysis

## Candidate Issue Mutation Plan

```json
{
  "ready_issue_refresh_mutations": [
    {
      "issue_number": 43,
      "action": "no_change",
      "global_threshold": "raise drain budget"
    }
  ]
}
```
"""

        with self.assertRaisesRegex(ValueError, "global policy or threshold"):
            ralph.ready_issue_refresh_mutations_from_markdown(
                markdown,
                candidates=[candidate],
            )

    def test_ready_issue_refresh_mutation_parser_rejects_malformed_json(self) -> None:
        candidate = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43)

        with self.assertRaisesRegex(ValueError, "malformed JSON"):
            ralph.ready_issue_refresh_mutations_from_markdown(
                READY_ISSUE_REFRESH_MALFORMED_MUTATION_MARKDOWN,
                candidates=[candidate],
            )

    def test_ready_issue_refresh_mutation_parser_requires_plan_for_candidates(
        self,
    ) -> None:
        candidate = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43)

        with self.assertRaisesRegex(ValueError, "required when candidate issues exist"):
            ralph.ready_issue_refresh_mutations_from_markdown(
                READY_ISSUE_REFRESH_MISSING_PLAN_MARKDOWN,
                candidates=[candidate],
            )

    def test_ready_issue_refresh_mutation_parser_allows_no_plan_without_candidates(
        self,
    ) -> None:
        mutations = ralph.ready_issue_refresh_mutations_from_markdown(
            READY_ISSUE_REFRESH_MISSING_PLAN_MARKDOWN,
            candidates=[],
        )

        self.assertEqual(mutations, [])

    def test_ready_issue_refresh_ready_contract_rejects_missing_sections(self) -> None:
        with self.assertRaises(ValueError) as caught:
            ralph.validate_ready_issue_refresh_ready_contract(
                issue_number=43,
                labels=frozenset({ralph.READY_LABEL}),
                body="## What to build\nBuild it.\n",
            )

        self.assertIn("## Acceptance criteria", str(caught.exception))
        self.assertIn("## Blocked by", str(caught.exception))

    def test_basic_triage_candidate_accepts_unlabeled_and_needs_triage(self) -> None:
        self.assertTrue(ralph.is_basic_triage_candidate(make_issue(set())))
        self.assertTrue(ralph.is_basic_triage_candidate(make_issue({"needs-triage"})))
        self.assertFalse(
            ralph.is_basic_triage_candidate(make_issue({"ready-for-agent"}))
        )
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"wontfix"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"agent-merged"})))
        self.assertFalse(
            ralph.is_basic_triage_candidate(make_issue({"agent-reviewing"}))
        )

    def test_agent_reviewing_blocks_needs_info_triage_reconsideration(self) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        payload = [
            {
                "number": 42,
                "title": "Implement thing",
                "body": IMPLEMENTATION_BODY,
                "labels": [{"name": "needs-info"}, {"name": "agent-reviewing"}],
                "createdAt": "2026-04-30T00:00:00Z",
                "updatedAt": "2026-04-30T00:00:00Z",
                "url": "https://github.com/example/repo/issues/42",
                "comments": [],
                "author": {"login": "reporter"},
            }
        ]
        runner = FakeRunner(command_outputs={issue_list_command: [json.dumps(payload)]})

        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner)

            self.assertIsNone(loop._next_triage_issue())

        commands = [call.args for call in runner.calls]
        self.assertNotIn(("gh", "api", "user", "--jq", ".login"), commands)

    def test_delivery_plan_defaults_to_gitflow_and_adds_label(self) -> None:
        plan = ralph.resolve_delivery_plan(
            make_issue({"ready-for-agent"}),
            default_mode=ralph.GITFLOW_MODE,
            target_branch=None,
        )

        self.assertEqual(plan.mode, ralph.GITFLOW_MODE)
        self.assertEqual(plan.target_branch, "dev")
        self.assertEqual(plan.add_labels, ("delivery-gitflow",))

    def test_delivery_plan_normalizes_conflict_to_gitflow(self) -> None:
        plan = ralph.resolve_delivery_plan(
            make_issue({"ready-for-agent", "delivery-gitflow", "delivery-trunk"}),
            default_mode=ralph.TRUNK_MODE,
            target_branch=None,
        )

        self.assertEqual(plan.mode, ralph.GITFLOW_MODE)
        self.assertEqual(plan.remove_labels, ("delivery-trunk",))

    def test_delivery_plan_defaults_to_exploratory_branch(self) -> None:
        plan = ralph.resolve_delivery_plan(
            make_issue({"ready-for-agent"}),
            default_mode=ralph.EXPLORATORY_MODE,
            target_branch=None,
        )

        self.assertEqual(plan.mode, ralph.EXPLORATORY_MODE)
        self.assertEqual(
            plan.target_branch, "agent/exploratory/issue-42-implement-thing"
        )
        self.assertEqual(plan.add_labels, ("delivery-exploratory",))

    def test_delivery_plan_exploratory_wins_conflicting_delivery_labels(self) -> None:
        plan = ralph.resolve_delivery_plan(
            make_issue(
                {
                    "ready-for-agent",
                    "delivery-exploratory",
                    "delivery-gitflow",
                    "delivery-trunk",
                }
            ),
            default_mode=ralph.GITFLOW_MODE,
            target_branch=None,
        )

        self.assertEqual(plan.mode, ralph.EXPLORATORY_MODE)
        self.assertEqual(plan.remove_labels, ("delivery-gitflow", "delivery-trunk"))

    def test_exploratory_mergeability_reports_conflict_without_push_or_issue_mutation(
        self,
    ) -> None:
        merge_tree_command = (
            "git",
            "merge-tree",
            "--write-tree",
            "--name-only",
            "origin/dev",
            "origin/agent/exploratory/issue-42-try-it",
        )
        runner = FakeRunner(fail_commands={merge_tree_command: 1})
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)

            payload = ralph.exploratory_mergeability_payload(
                git=loop.git,
                source_branch=ralph.DEFAULT_GITFLOW_BRANCH,
                review_branch="agent/exploratory/issue-42-try-it",
                run_dir=tmp_path / "run",
            )

        commands = [call.args for call in runner.calls]
        self.assertEqual(payload["status"], "conflicts")
        self.assertEqual(payload["source_ref"], "origin/dev")
        self.assertEqual(
            payload["review_ref"], "origin/agent/exploratory/issue-42-try-it"
        )
        self.assertIn(("git", "fetch", "origin", "dev"), commands)
        self.assertIn(
            ("git", "fetch", "origin", "agent/exploratory/issue-42-try-it"), commands
        )
        self.assertIn(merge_tree_command, commands)
        self.assertFalse(
            any(command[:3] == ("git", "push", "origin") for command in commands)
        )
        self.assertFalse(any(command[:2] == ("gh", "issue") for command in commands))

    def test_label_specs_include_exploratory_delivery_and_reviewing_state(self) -> None:
        label_names = {label.name for label in ralph.LABEL_SPECS}

        self.assertIn("delivery-exploratory", label_names)
        self.assertIn("agent-reviewing", label_names)

    def test_triage_prompt_uses_ralph_triage_skill(self) -> None:
        prompt = ralph.triage_prompt(make_issue({"needs-triage"}), "example/repo")

        self.assertIn("Use the $ralph-triage skill", prompt)
        self.assertNotIn("Use the $triage skill", prompt)
        self.assertIn(ralph.AI_TRIAGE_DISCLAIMER, prompt)
        self.assertIn("Do not edit repo", prompt)
        self.assertIn("Apply `delivery-exploratory` only when", prompt)
        self.assertIn("## Review focus", prompt)

    def test_select_qa_commands_for_aemo_etl_runtime_only_changes(self) -> None:
        commands = ralph.select_qa_commands(
            ["backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"],
            Path("/repo"),
        )
        names = [command.name for command in commands]
        self.assertEqual(
            names,
            [
                "aemo-etl Commit check",
                "aemo-etl Integration test",
            ],
        )

    def test_select_qa_commands_for_aemo_etl_docs_only_changes(self) -> None:
        commands = ralph.select_qa_commands(
            [
                "backend-services/dagster-user/aemo-etl/README.md",
                "backend-services/dagster-user/aemo-etl/docs/architecture/"
                "high_level_architecture.md",
            ],
            Path("/repo"),
        )
        names = [command.name for command in commands]

        self.assertEqual(names, ["root Commit check"])

    def test_select_qa_commands_for_mixed_aemo_etl_docs_and_runtime_changes(
        self,
    ) -> None:
        commands = ralph.select_qa_commands(
            [
                "backend-services/dagster-user/aemo-etl/docs/development/local_development.md",
                "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py",
            ],
            Path("/repo"),
        )
        names = [command.name for command in commands]

        self.assertEqual(
            names,
            [
                "aemo-etl Commit check",
                "root Commit check",
                "aemo-etl Integration test",
            ],
        )

    def test_select_qa_commands_adds_declared_aemo_etl_end_to_end_lane(self) -> None:
        commands = ralph.select_qa_commands(
            ["backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"],
            Path("/repo"),
            issue_body="\n".join(
                [
                    "## Context anchors",
                    "",
                    "- Test lane: `AEMO ETL End-to-end test`",
                ]
            ),
        )

        self.assertEqual(
            [(command.name, command.args, command.cwd) for command in commands],
            [
                (
                    "aemo-etl Commit check",
                    ("make", "run-prek"),
                    Path("/repo/backend-services/dagster-user/aemo-etl"),
                ),
                (
                    "aemo-etl Integration test",
                    ("make", "integration-test"),
                    Path("/repo/backend-services/dagster-user/aemo-etl"),
                ),
                (
                    "aemo-etl End-to-end test",
                    ("scripts/aemo-etl-e2e", "run", "--scenario", "full-gas-model"),
                    Path("/repo/backend-services"),
                ),
            ],
        )

    def test_select_qa_commands_adds_declared_aemo_etl_e2e_qa_command(self) -> None:
        commands = ralph.select_qa_commands(
            ["backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"],
            Path("/repo"),
            issue_body="\n".join(
                [
                    "## Context anchors",
                    "",
                    "- QA: `backend-services/scripts/aemo-etl-e2e run --scenario "
                    "full-gas-model`",
                ]
            ),
        )

        self.assertEqual(commands[-1].name, "aemo-etl End-to-end test")
        self.assertEqual(
            commands[-1].args,
            ("scripts/aemo-etl-e2e", "run", "--scenario", "full-gas-model"),
        )
        self.assertEqual(commands[-1].cwd, Path("/repo/backend-services"))

    def test_declared_aemo_etl_e2e_qa_includes_backend_e2e_script_changes(
        self,
    ) -> None:
        commands = ralph.select_qa_commands(
            ["backend-services/scripts/aemo-etl-e2e"],
            Path("/repo"),
            issue_body="\n".join(
                [
                    "## Context anchors",
                    "",
                    "- Test lane: `AEMO ETL End-to-end test`",
                ]
            ),
        )

        self.assertIn("root Commit check", [command.name for command in commands])
        self.assertEqual(commands[-1].name, "aemo-etl End-to-end test")
        self.assertEqual(commands[-1].cwd, Path("/repo/backend-services"))

    def test_declared_aemo_etl_end_to_end_lane_requires_recorded_evidence(
        self,
    ) -> None:
        issue = make_issue(
            {ralph.READY_LABEL},
            body="\n".join(
                [
                    "## Context anchors",
                    "",
                    "- Test lane: `AEMO ETL End-to-end test`",
                ]
            ),
        )
        qa_results = [
            ralph.QAResult(
                command=ralph.QACommand(
                    ("make", "run-prek"),
                    Path("/repo/backend-services/dagster-user/aemo-etl"),
                    "aemo-etl Commit check",
                ),
                log_path=Path("/logs/qa.log"),
            )
        ]

        with self.assertRaises(ralph.IssueFailure) as context:
            ralph.validate_declared_issue_qa_evidence(issue, qa_results)

        self.assertIn("AEMO ETL End-to-end test", str(context.exception))
        self.assertIn("before Local integration", str(context.exception))

    def test_declared_aemo_etl_end_to_end_lane_accepts_recorded_evidence(
        self,
    ) -> None:
        issue = make_issue(
            {ralph.READY_LABEL},
            body="\n".join(
                [
                    "## Context anchors",
                    "",
                    "- Test lane: `AEMO ETL End-to-end test`",
                ]
            ),
        )
        qa_results = [
            ralph.QAResult(
                command=ralph.QACommand(
                    ("scripts/aemo-etl-e2e", "run", "--scenario", "full-gas-model"),
                    Path("/repo/backend-services"),
                    "aemo-etl End-to-end test",
                ),
                log_path=Path("/logs/e2e.log"),
            )
        ]

        ralph.validate_declared_issue_qa_evidence(issue, qa_results)

    def test_select_qa_commands_for_marimo_runtime_only_changes(self) -> None:
        commands = ralph.select_qa_commands(
            ["backend-services/marimo/src/marimoserver/main.py"],
            Path("/repo"),
        )

        self.assertEqual(
            [(command.name, command.args, command.cwd) for command in commands],
            [
                (
                    "Marimo Component test",
                    ("uv", "run", "pytest", "tests/component"),
                    Path("/repo/backend-services/marimo"),
                ),
                (
                    "Marimo Commit check",
                    ("prek", "run", "-a"),
                    Path("/repo/backend-services/marimo"),
                ),
            ],
        )

    def test_select_qa_commands_for_marimo_docs_only_changes(self) -> None:
        commands = ralph.select_qa_commands(
            ["backend-services/marimo/README.md"],
            Path("/repo"),
        )
        names = [command.name for command in commands]

        self.assertEqual(names, ["root Commit check"])

    def test_select_qa_commands_for_mixed_marimo_docs_and_runtime_changes(self) -> None:
        commands = ralph.select_qa_commands(
            [
                "backend-services/marimo/README.md",
                "backend-services/marimo/src/marimoserver/main.py",
            ],
            Path("/repo"),
        )
        names = [command.name for command in commands]

        self.assertEqual(
            names,
            [
                "Marimo Component test",
                "Marimo Commit check",
                "root Commit check",
            ],
        )

    def test_select_qa_commands_for_gas_market_knowledge_base_changes(self) -> None:
        commands = ralph.select_qa_commands(
            [
                "tools/gas-market-knowledge-base/src/"
                "gas_market_knowledge_base/pdf_cache.py",
                "tools/gas-market-knowledge-base/tests/unit/test_cli.py",
            ],
            Path("/repo"),
        )

        self.assertEqual(
            [(command.name, command.args, command.cwd) for command in commands],
            [
                (
                    "Gas market knowledge base Unit test",
                    ("make", "unit-test"),
                    Path("/repo/tools/gas-market-knowledge-base"),
                ),
                (
                    "Gas market knowledge base Commit check",
                    ("make", "run-prek"),
                    Path("/repo/tools/gas-market-knowledge-base"),
                ),
            ],
        )

    def test_gas_market_knowledge_base_generated_markdown_is_not_maintained_doc(
        self,
    ) -> None:
        self.assertFalse(
            ralph.root_prek_needed(
                "tools/gas-market-knowledge-base/generated/gold/context.md"
            )
        )

    def test_marimo_runtime_matching_uses_whole_subproject_prefix(self) -> None:
        self.assertTrue(
            ralph.has_marimo_runtime_change(
                ["backend-services/marimo/src/marimoserver/main.py"]
            )
        )
        self.assertFalse(
            ralph.has_marimo_runtime_change(["backend-services/marimo/README.md"])
        )
        self.assertFalse(
            ralph.has_marimo_runtime_change(
                [
                    "backend-services/marimo",
                    "backend-services/marimo-old/src/module.py",
                    "backend-services/marimoREADME.md",
                ]
            )
        )

    def test_protected_aemo_etl_matching_uses_whole_subproject_prefix(self) -> None:
        self.assertTrue(
            ralph.has_protected_aemo_etl_change(
                ["backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"]
            )
        )
        self.assertFalse(
            ralph.has_protected_aemo_etl_change(
                [
                    "backend-services/dagster-user/aemo-etl/docs/architecture/"
                    "high_level_architecture.md"
                ]
            )
        )
        self.assertFalse(
            ralph.has_protected_aemo_etl_change(
                [
                    "backend-services/dagster-user/aemo-etl",
                    "backend-services/dagster-user/aemo-etl-old/src/module.py",
                    "backend-services/dagster-user/aemo-etlREADME.md",
                ]
            )
        )

    def test_aemo_etl_runtime_matching_includes_non_doc_subproject_paths(self) -> None:
        runtime_paths = (
            "backend-services/dagster-user/aemo-etl/pyproject.toml",
            "backend-services/dagster-user/aemo-etl/.localstack.env",
            "backend-services/dagster-user/aemo-etl/scripts/example",
            "backend-services/dagster-user/aemo-etl/tests/unit/test_example.py",
            "backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/resources.py",
            "backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/e2e_archive_seed.py",
        )

        for path in runtime_paths:
            with self.subTest(path=path):
                self.assertTrue(ralph.has_protected_aemo_etl_change([path]))

    def test_select_promotion_gate_commands_for_aemo_etl_changes(self) -> None:
        seed_root = Path("/seed-cache")
        commands = ralph.select_promotion_gate_commands(
            ["backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"],
            Path("/repo"),
            seed_root=seed_root,
        )

        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0].name, "aemo-etl End-to-end test")
        self.assertEqual(
            commands[0].args,
            (
                "scripts/aemo-etl-e2e",
                "run",
                "--rebuild",
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1800",
                "--max-concurrent-runs",
                "6",
                "--seed-root",
                str(seed_root),
            ),
        )
        self.assertEqual(commands[0].cwd, Path("/repo/backend-services"))

    def test_select_promotion_gate_commands_allows_default_seed_root(self) -> None:
        commands = ralph.select_promotion_gate_commands(
            ["backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"],
            Path("/repo"),
        )

        self.assertEqual(
            commands[0].args,
            (
                "scripts/aemo-etl-e2e",
                "run",
                "--rebuild",
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1800",
                "--max-concurrent-runs",
                "6",
            ),
        )

    def test_select_promotion_gate_commands_skips_aemo_etl_docs_only_changes(
        self,
    ) -> None:
        commands = ralph.select_promotion_gate_commands(
            [
                "backend-services/dagster-user/aemo-etl/docs/architecture/"
                "high_level_architecture.md"
            ],
            Path("/repo"),
        )

        self.assertEqual(commands, [])

    def test_select_qa_commands_for_docs_and_script_changes(self) -> None:
        commands = ralph.select_qa_commands(
            ["docs/repository/workflow.md", "scripts/ralph.py"], Path("/repo")
        )
        names = [command.name for command in commands]
        self.assertEqual(names, ["root Commit check", "Ralph loop Commit check"])

    def test_select_qa_commands_for_ralph_loop_docs_changes(self) -> None:
        commands = ralph.select_qa_commands(
            ["tools/ralph-loop/README.md"],
            Path("/repo"),
        )

        self.assertEqual(
            [(command.name, command.cwd) for command in commands],
            [
                ("root Commit check", Path("/repo")),
                ("Ralph loop Commit check", Path("/repo/tools/ralph-loop")),
            ],
        )

    def test_select_promotion_gate_commands_skips_non_aemo_changes(self) -> None:
        commands = ralph.select_promotion_gate_commands(
            ["scripts/ralph.py"], Path("/repo")
        )

        self.assertEqual(commands, [])

    def test_parse_git_status_paths_includes_untracked_and_renamed_files(self) -> None:
        status = "\n".join(
            [
                " M scripts/ralph.py",
                "?? tools/ralph-loop/tests/unit/test_ralph.py",
                "R  old-name.md -> docs/agents/ralph-loop.md",
            ]
        )
        self.assertEqual(
            ralph.parse_git_status_paths(status),
            [
                "docs/agents/ralph-loop.md",
                "scripts/ralph.py",
                "tools/ralph-loop/tests/unit/test_ralph.py",
            ],
        )

    def test_parse_git_status_tracked_unstaged_paths_excludes_untracked_files(
        self,
    ) -> None:
        status = "\n".join(
            [
                "M  README.md",
                "MM docs/agents/ralph-loop.md",
                "AM backend-services/dagster-user/aemo-etl/src/new_asset.py",
                "?? scratch.txt",
                "RM old-name.md -> docs/agents/renamed.md",
            ]
        )
        self.assertEqual(
            ralph.parse_git_status_tracked_unstaged_paths(status),
            [
                "backend-services/dagster-user/aemo-etl/src/new_asset.py",
                "docs/agents/ralph-loop.md",
                "docs/agents/renamed.md",
            ],
        )

    def test_parse_git_worktree_list_porcelain_reads_checked_out_branches(self) -> None:
        output = "\n".join(
            [
                "worktree /repo",
                "HEAD dev-old",
                "branch refs/heads/dev",
                "",
                "worktree /repo-main",
                "HEAD main-old",
                "branch refs/heads/main",
                "",
                "worktree /repo-detached",
                "HEAD detached-sha",
                "detached",
                "",
            ]
        )

        self.assertEqual(
            ralph.parse_git_worktree_list_porcelain(output),
            [
                ralph.GitWorktree(Path("/repo"), "dev-old", "dev"),
                ralph.GitWorktree(Path("/repo-main"), "main-old", "main"),
                ralph.GitWorktree(Path("/repo-detached"), "detached-sha", None),
            ],
        )

    def test_environment_failure_detection_matches_container_tool_errors(self) -> None:
        error = ralph.CommandFailure(
            ["make", "integration-test"],
            Path("/repo"),
            1,
            "",
            "podman: command not found",
            None,
        )
        self.assertTrue(ralph.looks_like_environment_failure(error))

    def test_codex_exec_command_uses_supported_unattended_flags(self) -> None:
        self.assertEqual(
            ralph.codex_exec_command(Path("/repo")),
            [
                "codex",
                "exec",
                "--cd",
                "/repo",
                "--sandbox",
                "workspace-write",
                "-c",
                "sandbox_workspace_write.network_access=true",
                "-c",
                'shell_environment_policy.inherit="all"',
                "-c",
                "shell_environment_policy.ignore_default_excludes=true",
                "-c",
                "shell_environment_policy.include_only="
                + json.dumps(list(ralph.SANDBOX_CODEX_ENV_INCLUDE_ONLY)),
                "--json",
                "-",
            ],
        )
        self.assertNotIn("--full-auto", ralph.codex_exec_command(Path("/repo")))

    def test_codex_exec_command_can_use_full_access_bypass(self) -> None:
        command = ralph.codex_exec_command(
            Path("/repo"),
            sandbox_mode=ralph.FULL_ACCESS_CODEX_SANDBOX,
        )

        self.assertIn("--dangerously-bypass-approvals-and-sandbox", command)
        self.assertNotIn("--sandbox", command)
        self.assertNotIn("--full-auto", command)

    def test_context_anchor_paths_detect_agent_workflow_anchors(self) -> None:
        issue = make_issue({"ready-for-agent"}, AGENTS_IMPLEMENTATION_BODY)

        access_plan = ralph.issue_implementation_access_plan(issue)

        self.assertTrue(access_plan.full_access_required)
        self.assertEqual(
            access_plan.context_anchor_paths,
            (
                ralph.ContextAnchorPath(
                    ".agents/skills/ralph-loop/SKILL.md",
                    prefix=False,
                ),
                ralph.ContextAnchorPath("docs/agents/ralph-loop.md", prefix=False),
            ),
        )

    def test_changed_files_outside_context_anchors_treats_directory_anchor_as_prefix(
        self,
    ) -> None:
        anchors = (
            ralph.ContextAnchorPath(".agents/skills/ralph-loop", prefix=True),
            ralph.ContextAnchorPath("docs/agents/ralph-loop.md", prefix=False),
        )
        with tempfile.TemporaryDirectory() as tmp:
            worktree = Path(tmp)
            (worktree / ".agents" / "skills" / "ralph-loop").mkdir(parents=True)

            out_of_scope = ralph.changed_files_outside_context_anchors(
                [
                    ".agents/skills/ralph-loop/SKILL.md",
                    "docs/agents/ralph-loop.md",
                    "scripts/ralph.py",
                ],
                anchors,
                worktree_path=worktree,
            )

        self.assertEqual(out_of_scope, ["scripts/ralph.py"])

    def test_qa_runtime_env_uses_operator_values_when_present(self) -> None:
        operator_env = {
            "DAGSTER_HOME": "/operator/dagster",
            "XDG_CACHE_HOME": "/operator/cache",
            "UV_CACHE_DIR": "/operator/uv-cache",
        }

        runtime_env = ralph.resolve_qa_runtime_env(
            repo="example/repo",
            run_dir=Path("/tmp/ralph-test-run"),
            base_env=operator_env,
        )

        self.assertEqual(runtime_env.values, operator_env)
        self.assertEqual(
            runtime_env.metadata["DAGSTER_HOME"],
            {"value": "/operator/dagster", "source": "operator"},
        )
        self.assertEqual(runtime_env.metadata["XDG_CACHE_HOME"]["source"], "operator")
        self.assertEqual(runtime_env.metadata["UV_CACHE_DIR"]["source"], "operator")

    def test_qa_runtime_env_falls_back_to_run_scoped_tmp_paths(self) -> None:
        runtime_env = ralph.resolve_qa_runtime_env(
            repo="example/repo",
            run_dir=Path("/work/.ralph/runs/issue-42-20260504T010203Z"),
            base_env={},
        )
        runtime_root = (
            Path("/tmp")
            / ralph.QA_RUNTIME_ROOT_DIR_NAME
            / "example-repo"
            / "issue-42-20260504T010203Z"
        )

        self.assertEqual(
            runtime_env.values,
            {
                "DAGSTER_HOME": str(runtime_root / "dagster-home"),
                "XDG_CACHE_HOME": str(runtime_root / "xdg-cache"),
                "UV_CACHE_DIR": str(runtime_root / "uv-cache"),
            },
        )
        for name, value in runtime_env.values.items():
            with self.subTest(name=name):
                self.assertEqual(runtime_env.metadata[name]["source"], "ralph_default")
                self.assertTrue(Path(value).is_dir())

    def test_qa_runtime_cleanup_removes_only_succeeded_default_run_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = f"example/cleanup-{tmp_path.name}"
            log_root = tmp_path / "logs"
            repo_runtime_root = ralph.default_qa_runtime_repo_root(repo)
            shutil.rmtree(repo_runtime_root, ignore_errors=True)
            try:
                succeeded = repo_runtime_root / "issue-1-succeeded"
                failed = repo_runtime_root / "issue-2-failed"
                active = repo_runtime_root / "issue-3-active"
                missing_manifest = repo_runtime_root / "issue-4-missing"
                for path in (succeeded, failed, active, missing_manifest):
                    (path / "uv-cache").mkdir(parents=True)
                    (path / "uv-cache" / "payload.txt").write_text(
                        "payload",
                        encoding="utf-8",
                    )
                write_minimal_child_manifest(log_root, name=succeeded.name)
                write_minimal_child_manifest(
                    log_root, name=failed.name, status="failed"
                )
                write_minimal_child_manifest(log_root, name=active.name)

                actions = ralph.cleanup_completed_qa_runtime_dirs(
                    repo=repo,
                    log_root=log_root,
                    active_run_dirs=(log_root / active.name,),
                )
            finally:
                shutil.rmtree(repo_runtime_root, ignore_errors=True)

        statuses = {action.path.name: action.status for action in actions}
        reasons = {action.path.name: action.reason for action in actions}
        self.assertEqual(statuses[succeeded.name], "removed")
        self.assertEqual(statuses[failed.name], "skipped")
        self.assertEqual(statuses[active.name], "skipped")
        self.assertEqual(statuses[missing_manifest.name], "skipped")
        self.assertIn("did not succeed", reasons[failed.name])
        self.assertIn("active run directory", reasons[active.name])
        self.assertIn("manifest not found", reasons[missing_manifest.name])

    def test_qa_runtime_cleanup_refuses_non_ralph_owned_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            outside = tmp_path / "not-ralph-owned"
            outside.mkdir()

            with self.assertRaises(ralph.QARuntimeCleanupRefusal):
                ralph.validate_qa_runtime_cleanup_target(
                    outside,
                    repo="example/repo",
                    log_root=tmp_path / "logs",
                )

    def test_qa_runtime_preflight_reports_sources_and_cleans_before_failure(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = f"example/preflight-{tmp_path.name}"
            log_root = tmp_path / "logs"
            run_dir = log_root / "issue-10-current"
            old_run = "issue-9-old"
            repo_runtime_root = ralph.default_qa_runtime_repo_root(repo)
            shutil.rmtree(repo_runtime_root, ignore_errors=True)
            try:
                (repo_runtime_root / old_run / "uv-cache").mkdir(parents=True)
                write_minimal_child_manifest(log_root, name=old_run)
                current_runtime_root = ralph.default_qa_runtime_root(repo, run_dir)
                readings = [
                    ralph.QARuntimeCapacity(
                        repo_runtime_root, free_bytes=10, free_inodes=10
                    ),
                    ralph.QARuntimeCapacity(
                        repo_runtime_root, free_bytes=200, free_inodes=200
                    ),
                ]

                def capacity_reader(path: Path) -> ralph.QARuntimeCapacity:
                    self.assertEqual(path, repo_runtime_root)
                    if len(readings) == 2:
                        self.assertFalse(current_runtime_root.exists())
                    return readings.pop(0)

                result = ralph.qa_runtime_disk_preflight(
                    repo=repo,
                    run_dir=run_dir,
                    log_root=log_root,
                    label="unit preflight",
                    base_env={
                        ralph.QA_RUNTIME_MIN_FREE_BYTES_ENV: "100",
                        ralph.QA_RUNTIME_MIN_FREE_INODES_ENV: "100",
                    },
                    capacity_reader=capacity_reader,
                )
                created_default_dirs = all(
                    Path(value).is_dir()
                    for value in result.qa_runtime_env.values.values()
                )
            finally:
                shutil.rmtree(repo_runtime_root, ignore_errors=True)

        lines = "\n".join(ralph.qa_runtime_preflight_lines(result))
        statuses = {
            action.path.name: action.status for action in result.cleanup_actions
        }
        self.assertEqual(statuses[old_run], "removed")
        self.assertNotIn(run_dir.name, statuses)
        self.assertEqual(result.failed_signals, ())
        self.assertTrue(created_default_dirs)
        self.assertIn("DAGSTER_HOME: ralph_default ->", lines)
        self.assertIn("XDG_CACHE_HOME: ralph_default ->", lines)
        self.assertIn("UV_CACHE_DIR: ralph_default ->", lines)

    def test_qa_runtime_preflight_preserves_operator_provided_cache_paths(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo = f"example/operator-cache-{tmp_path.name}"
            log_root = tmp_path / "logs"
            run_dir = log_root / "issue-11-current"
            old_run = "issue-8-old"
            repo_runtime_root = ralph.default_qa_runtime_repo_root(repo)
            shutil.rmtree(repo_runtime_root, ignore_errors=True)
            try:
                (repo_runtime_root / old_run / "uv-cache").mkdir(parents=True)
                write_minimal_child_manifest(log_root, name=old_run)
                capacity = ralph.QARuntimeCapacity(
                    repo_runtime_root,
                    free_bytes=10,
                    free_inodes=10,
                )

                result = ralph.qa_runtime_disk_preflight(
                    repo=repo,
                    run_dir=run_dir,
                    log_root=log_root,
                    label="operator cache preflight",
                    base_env={
                        "DAGSTER_HOME": str(tmp_path / "operator-dagster"),
                        "XDG_CACHE_HOME": str(tmp_path / "operator-cache"),
                        "UV_CACHE_DIR": str(tmp_path / "operator-uv"),
                        ralph.QA_RUNTIME_MIN_FREE_BYTES_ENV: "100",
                        ralph.QA_RUNTIME_MIN_FREE_INODES_ENV: "100",
                    },
                    capacity_reader=lambda path: capacity,
                )
                preserved = (repo_runtime_root / old_run).is_dir()
            finally:
                shutil.rmtree(repo_runtime_root, ignore_errors=True)

        self.assertEqual(result.cleanup_actions, ())
        self.assertTrue(preserved)
        self.assertFalse(ralph.qa_runtime_capacity_failed(result))
        self.assertEqual(
            result.qa_runtime_env.metadata["UV_CACHE_DIR"]["source"],
            "operator",
        )

    def test_sandbox_token_uses_parent_gh_token_first(self) -> None:
        runner = FakeRunner()
        with patch.dict(
            ralph.os.environ,
            {"GH_TOKEN": " parent-token ", "GITHUB_TOKEN": "fallback-token"},
            clear=True,
        ):
            token, source = ralph.resolve_sandbox_gh_token(runner, Path("/repo"))

        self.assertEqual(token, "parent-token")
        self.assertEqual(source, "env:GH_TOKEN")
        self.assertEqual(runner.calls, [])

    def test_sandbox_token_falls_back_to_gh_auth_token(self) -> None:
        runner = FakeRunner()
        with patch.dict(ralph.os.environ, {}, clear=True):
            token, source = ralph.resolve_sandbox_gh_token(runner, Path("/repo"))

        self.assertEqual(token, "fake-gh-token")
        self.assertEqual(source, "gh-auth")
        self.assertEqual(runner.calls[0].args, ("gh", "auth", "token"))

    def test_sandbox_codex_env_injects_only_gh_token_auth(self) -> None:
        access = ralph.SandboxIssueAccess(
            token="sandbox-token",
            token_source="env:GH_TOKEN",
            wrapper_path=Path("/tmp/ralph-sandbox-bin/gh"),
            repo="example/repo",
            allowed_issue_commands=ralph.SANDBOX_ALLOWED_GH_ISSUE_COMMANDS,
        )

        with patch.dict(
            ralph.os.environ,
            {
                "PATH": "/usr/bin",
                "GITHUB_TOKEN": "remove-me",
                "GH_CONFIG_DIR": "/home/user/.config/gh",
            },
            clear=True,
        ):
            env = ralph.codex_env_for_sandbox_issue_access(access)

        self.assertEqual(env["GH_TOKEN"], "sandbox-token")
        self.assertEqual(env["GH_REPO"], "example/repo")
        self.assertEqual(env["GH_PROMPT_DISABLED"], "1")
        self.assertEqual(env["PATH"], "/tmp/ralph-sandbox-bin:/usr/bin")
        self.assertNotIn("GITHUB_TOKEN", env)
        self.assertNotIn("GH_CONFIG_DIR", env)

    def test_sandbox_gh_wrapper_allows_only_triage_safe_issue_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            captured_args = tmp_path / "captured-args.txt"
            real_gh = tmp_path / "real-gh"
            real_gh.write_text(
                "#!/usr/bin/env sh\n"
                "printf '%s\\n' \"$@\" > "
                f"{ralph.shlex.quote(str(captured_args))}\n",
                encoding="utf-8",
            )
            real_gh.chmod(0o700)
            wrapper = tmp_path / "bin" / "gh"

            ralph.write_sandbox_gh_wrapper(wrapper, real_gh)
            subprocess.run(
                [str(wrapper), "issue", "edit", "42", "--add-label", "ready-for-agent"],
                check=True,
            )
            self.assertEqual(
                captured_args.read_text(encoding="utf-8").splitlines(),
                ["issue", "edit", "42", "--add-label", "ready-for-agent"],
            )

            blocked = subprocess.run(
                [str(wrapper), "api", "user"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(blocked.returncode, 126)
            self.assertIn("blocked gh command", blocked.stderr)

            blocked_issue = subprocess.run(
                [str(wrapper), "issue", "delete", "42"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(blocked_issue.returncode, 126)

    def test_sandbox_gh_wrapper_read_only_blocks_issue_mutations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            captured_args = tmp_path / "captured-args.txt"
            real_gh = tmp_path / "real-gh"
            real_gh.write_text(
                "#!/usr/bin/env sh\n"
                "printf '%s\\n' \"$@\" > "
                f"{ralph.shlex.quote(str(captured_args))}\n",
                encoding="utf-8",
            )
            real_gh.chmod(0o700)
            wrapper = tmp_path / "bin" / "gh"

            ralph.write_sandbox_gh_wrapper(
                wrapper,
                real_gh,
                allowed_issue_commands=ralph.SANDBOX_READ_ONLY_GH_ISSUE_COMMANDS,
            )
            subprocess.run(
                [str(wrapper), "issue", "view", "42"],
                check=True,
            )
            self.assertEqual(
                captured_args.read_text(encoding="utf-8").splitlines(),
                ["issue", "view", "42"],
            )

            mutation_commands = [
                ["issue", "comment", "42", "--body", "nope"],
                ["issue", "edit", "42", "--add-label", "ready-for-agent"],
                ["issue", "close", "42"],
                ["issue", "reopen", "42"],
                ["issue", "create", "--title", "nope"],
            ]
            for mutation_command in mutation_commands:
                with self.subTest(command=mutation_command):
                    blocked = subprocess.run(
                        [str(wrapper), *mutation_command],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(blocked.returncode, 126)
                    self.assertIn("blocked gh command", blocked.stderr)

    def test_post_promotion_review_markdown_reads_codex_json_final_message(
        self,
    ) -> None:
        stdout = "\n".join(
            [
                json.dumps({"type": "session_configured", "session_id": "test"}),
                json.dumps(
                    {
                        "type": "item.completed",
                        "item": {
                            "type": "message",
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "output_text",
                                    "text": POST_PROMOTION_REVIEW_MARKDOWN,
                                }
                            ],
                        },
                    }
                ),
            ]
        )

        self.assertEqual(
            ralph.post_promotion_review_markdown_from_stdout(stdout),
            POST_PROMOTION_REVIEW_MARKDOWN.strip(),
        )

    def test_run_codex_injects_sandbox_issue_access_without_recording_token(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            runner = FakeRunner()
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            branch, worktree_path, integration_path = loop._branch_and_worktrees(issue)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=issue,
                delivery_plan=delivery_plan,
                branch=branch,
                worktree_path=worktree_path,
                integration_path=integration_path,
                config=loop.config,
            )

            with patch.dict(ralph.os.environ, {}, clear=True):
                loop._run_codex(
                    "prompt",
                    loop.config.repo_root,
                    run_dir / "codex.jsonl",
                    phase="test codex",
                    manifest=manifest,
                )

            codex_call = next(
                call for call in runner.calls if call.args[:2] == ("codex", "exec")
            )
            self.assertEqual(
                codex_call.args[codex_call.args.index("--sandbox") + 1],
                ralph.WORKSPACE_WRITE_CODEX_SANDBOX,
            )
            self.assertIsNotNone(codex_call.env)
            assert codex_call.env is not None
            self.assertEqual(codex_call.env["GH_TOKEN"], "fake-gh-token")
            self.assertEqual(codex_call.env["GH_REPO"], "example/repo")
            runtime_root = ralph.default_qa_runtime_root("example/repo", run_dir)
            self.assertEqual(
                codex_call.env["DAGSTER_HOME"],
                str(runtime_root / "dagster-home"),
            )
            self.assertEqual(
                codex_call.env["XDG_CACHE_HOME"],
                str(runtime_root / "xdg-cache"),
            )
            self.assertEqual(
                codex_call.env["UV_CACHE_DIR"],
                str(runtime_root / "uv-cache"),
            )
            wrapper_path = run_dir / ralph.SANDBOX_GH_WRAPPER_DIR_NAME / "gh"
            self.assertTrue(wrapper_path.exists())
            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))
            manifest_text = json.dumps(manifest_payload)
            self.assertIn('"token_source": "gh-auth"', manifest_text)
            self.assertIn(str(wrapper_path), manifest_text)
            self.assertNotIn("fake-gh-token", manifest_text)
            self.assertEqual(
                manifest_payload["qa_runtime_env"]["variables"]["DAGSTER_HOME"][
                    "source"
                ],
                "ralph_default",
            )
            self.assertEqual(
                manifest_payload["qa_runtime_env"]["variables"]["UV_CACHE_DIR"][
                    "value"
                ],
                str(runtime_root / "uv-cache"),
            )

    def test_default_worktree_container_matches_sibling_worktree_layout(self) -> None:
        current = Path("/work/repo__worktrees/refactor")
        self.assertEqual(
            ralph.default_worktree_container(current),
            Path("/work/repo__worktrees"),
        )
        main = Path("/work/repo")
        self.assertEqual(
            ralph.default_worktree_container(main), Path("/work/repo__worktrees")
        )

    def test_build_config_defaults_to_gitflow_without_target_branch(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(ralph.parse_args([]), runner)

        self.assertEqual(config.delivery_mode, ralph.GITFLOW_MODE)
        self.assertIsNone(config.target_branch)
        self.assertFalse(config.skip_post_promotion_review)
        self.assertFalse(config.skip_post_promotion_followups)
        self.assertFalse(config.ready_issue_refresh_enabled)
        self.assertFalse(config.skip_ready_issue_refresh)
        self.assertEqual(
            config.exploratory_concurrency,
            ralph.DEFAULT_EXPLORATORY_CONCURRENCY,
        )
        self.assertEqual(
            config.max_codex_attempts,
            ralph.DEFAULT_CODEX_ATTEMPT_BUDGET,
        )

    def test_parse_args_help_describes_default_drain_budget(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output), self.assertRaises(SystemExit):
            ralph.parse_args(["--help"])

        help_text = output.getvalue()
        self.assertIn("Defaults to", help_text)
        self.assertIn("10. Use 0 for unlimited", help_text)
        self.assertIn("--allow-dirty-worktree", help_text)
        self.assertIn("--skip-post-promotion-review", help_text)
        self.assertIn("--skip-post-promotion-followups", help_text)
        self.assertIn("--ready-issue-refresh", help_text)
        self.assertIn("--skip-ready-issue-refresh", help_text)
        self.assertIn("--allow-full-access-implementation", help_text)
        self.assertIn("--max-codex-attempts", help_text)
        self.assertIn("Defaults to 5", help_text)
        self.assertIn("--exploratory-concurrency", help_text)
        self.assertIn("Defaults to 2", help_text)
        self.assertIn("--doctor", help_text)
        self.assertIn("--shape-issues-run", help_text)
        self.assertIn("exploratory", help_text)

    def test_parse_args_rejects_shape_issues_run_without_doctor(self) -> None:
        output = io.StringIO()

        with redirect_stderr(output), self.assertRaises(SystemExit) as caught:
            ralph.parse_args(["--shape-issues-run", ".shape-issues/runs/demo"])

        self.assertEqual(caught.exception.code, 2)
        self.assertIn(
            "--shape-issues-run is only supported with --doctor", output.getvalue()
        )

    def test_parse_args_rejects_exploratory_concurrency_below_one(self) -> None:
        output = io.StringIO()

        with redirect_stderr(output), self.assertRaises(SystemExit) as caught:
            ralph.parse_args(["--exploratory-concurrency", "0"])

        self.assertEqual(caught.exception.code, 2)
        self.assertIn(
            "--exploratory-concurrency must be 1 or greater", output.getvalue()
        )

    def test_parse_args_rejects_max_codex_attempts_below_one(self) -> None:
        output = io.StringIO()

        with redirect_stderr(output), self.assertRaises(SystemExit) as caught:
            ralph.parse_args(["--max-codex-attempts", "0"])

        self.assertEqual(caught.exception.code, 2)
        self.assertIn("--max-codex-attempts must be 1 or greater", output.getvalue())

    def test_build_config_records_exploratory_concurrency(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(
            ralph.parse_args(["--exploratory-concurrency", "4"]),
            runner,
        )

        self.assertEqual(config.exploratory_concurrency, 4)

    def test_build_config_records_max_codex_attempts(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(
            ralph.parse_args(["--max-codex-attempts", "7"]),
            runner,
        )

        self.assertEqual(config.max_codex_attempts, 7)

    def test_run_manifests_record_configuration(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                max_codex_attempts=7,
                exploratory_concurrency=5,
            )
            issue = make_issue({ralph.READY_LABEL}, IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            implementation_manifest = ralph.RunManifest.for_implementation(
                run_dir=tmp_path / "logs" / "issue-42-test",
                issue=issue,
                delivery_plan=delivery_plan,
                branch="agent/issue-42-implement-thing",
                worktree_path=tmp_path / "worktrees" / "issue",
                integration_path=tmp_path / "worktrees" / "integration",
                config=loop.config,
            )
            promotion_manifest = ralph.RunManifest.for_promotion(
                run_dir=tmp_path / "logs" / "promote-test",
                source_branch=ralph.DEFAULT_GITFLOW_BRANCH,
                target_branch=ralph.DEFAULT_TRUNK_BRANCH,
                source_path=tmp_path / "worktrees" / "source",
                promote_path=tmp_path / "worktrees" / "promote",
                config=loop.config,
            )
            operator_manifest = ralph.OperatorRunManifest.start(
                run_dir=tmp_path / "operator" / "operator-test",
                config=loop.config,
                max_cycles=3,
            )

            payloads = [
                json.loads(implementation_manifest.path.read_text(encoding="utf-8")),
                json.loads(promotion_manifest.path.read_text(encoding="utf-8")),
                json.loads(operator_manifest.path.read_text(encoding="utf-8")),
            ]

        for payload in payloads:
            self.assertEqual(payload["configuration"]["exploratory_concurrency"], 5)
            self.assertEqual(payload["configuration"]["max_codex_attempts"], 7)

    def test_build_config_enables_ready_issue_refresh_for_drain_by_default(
        self,
    ) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(ralph.parse_args(["--drain"]), runner)

        self.assertTrue(config.ready_issue_refresh_enabled)
        self.assertFalse(config.skip_ready_issue_refresh)

    def test_build_config_skips_default_ready_issue_refresh_for_drain(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(
            ralph.parse_args(["--drain", "--skip-ready-issue-refresh"]),
            runner,
        )

        self.assertFalse(config.ready_issue_refresh_enabled)
        self.assertTrue(config.skip_ready_issue_refresh)

    def test_build_config_enables_ready_issue_refresh_for_targeted_issue(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(
            ralph.parse_args(["--issue", "42", "--ready-issue-refresh"]),
            runner,
        )

        self.assertTrue(config.ready_issue_refresh_enabled)

    def test_build_config_records_post_promotion_review_skip_flag(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(
            ralph.parse_args(["--promote", "--skip-post-promotion-review"]),
            runner,
        )

        self.assertTrue(config.promote)
        self.assertTrue(config.skip_post_promotion_review)

    def test_build_config_records_post_promotion_followup_skip_flag(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(
            ralph.parse_args(["--promote", "--skip-post-promotion-followups"]),
            runner,
        )

        self.assertTrue(config.promote)
        self.assertTrue(config.skip_post_promotion_followups)

    def test_dirty_root_worktree_message_lists_changed_paths_and_override(self) -> None:
        message = ralph.dirty_root_worktree_message(
            Path("/repo"),
            " M scripts/ralph.py\n?? tools/ralph-loop/tests/unit/test_ralph.py\n",
        )

        self.assertIn("Root worktree has uncommitted changes: /repo", message)
        self.assertIn("--allow-dirty-worktree", message)
        self.assertIn("- scripts/ralph.py", message)
        self.assertIn("- tools/ralph-loop/tests/unit/test_ralph.py", message)

    def test_drain_defaults_to_ten_implementation_attempts(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                drain=True,
                max_issues=ralph.parse_args(["--drain"]).max_issues,
            )
            counting_loop = CountingRalphLoop(loop.config, runner, ready_count=12)
            output = io.StringIO()

            with redirect_stdout(output):
                counting_loop.run()

        self.assertEqual(counting_loop.implemented, 10)
        self.assertIn("Reached --max-issues 10.", output.getvalue())

    def test_max_issues_zero_keeps_drain_unlimited(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                drain=True,
                max_issues=ralph.parse_args(
                    ["--drain", "--max-issues", "0"]
                ).max_issues,
            )
            counting_loop = CountingRalphLoop(loop.config, runner, ready_count=12)
            output = io.StringIO()

            with redirect_stdout(output):
                counting_loop.run()

        self.assertEqual(counting_loop.implemented, 12)
        self.assertNotIn("Reached --max-issues", output.getvalue())

    def test_build_config_base_alias_uses_trunk_compatibility(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(ralph.parse_args(["--base", "main"]), runner)

        self.assertEqual(config.delivery_mode, ralph.TRUNK_MODE)
        self.assertEqual(config.target_branch, "main")

    def test_build_config_accepts_exploratory_delivery_mode(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(
            ralph.parse_args(["--delivery-mode", "exploratory"]),
            runner,
        )

        self.assertEqual(config.delivery_mode, ralph.EXPLORATORY_MODE)
        self.assertIsNone(config.target_branch)

    def test_build_config_records_full_access_implementation_flag(self) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): ["/work/repo\n"],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )

        config = ralph.build_config(
            ralph.parse_args(["--allow-full-access-implementation"]),
            runner,
        )

        self.assertTrue(config.allow_full_access_implementation)

    def test_ralph_doctor_checks_drain_promote_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            label_payload = json.dumps(
                [{"name": label.name} for label in ralph.LABEL_SPECS]
            )
            runner = FakeRunner(
                command_outputs={
                    ("git", "rev-parse", "--show-toplevel"): [str(repo_root) + "\n"],
                    ("git", "config", "--get", "remote.origin.url"): [
                        "git@github.com:example/repo.git\n"
                    ],
                    (
                        "gh",
                        "label",
                        "list",
                        "-R",
                        "example/repo",
                        "--limit",
                        "200",
                        "--json",
                        "name",
                    ): [label_payload],
                }
            )
            args = ralph.parse_args(["--doctor", "--drain-promote-all"])

            with patch.object(ralph.shutil, "which", return_value="/usr/bin/tool"):
                result = ralph.run_ralph_doctor(args, runner)

        self.assertEqual(result["status"], "passed")
        self.assertIn(
            ("git", "push", "--dry-run", "origin", "HEAD:dev"),
            [call.args for call in runner.calls],
        )
        self.assertIn(
            ("git", "push", "--dry-run", "origin", "HEAD:main"),
            [call.args for call in runner.calls],
        )

    def test_shape_issues_doctor_requires_live_runner_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            run_dir = repo_root / ".shape-issues" / "runs" / "demo"
            run_dir.mkdir(parents=True)
            (run_dir / "bundle.json").write_text("{}", encoding="utf-8")
            (run_dir / "report.json").write_text(
                json.dumps(
                    {
                        "bundle_digest": "abc",
                        "context_assessor": {"provider": "codex"},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                ralph.EnvironmentFailure, "live_assessor_runner"
            ):
                ralph.inspect_shape_issues_run_for_doctor(run_dir, repo_root)

    def test_dirty_root_blocks_live_issue_drain_and_promote_before_side_effects(
        self,
    ) -> None:
        cases = [
            {"issue": 42},
            {"drain": True},
            {"promote": True},
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                runner = FakeRunner(status_outputs=[" M scripts/ralph.py\n"])
                with tempfile.TemporaryDirectory() as tmp:
                    loop = make_loop(Path(tmp), runner, **kwargs)
                    probe = PreflightProbeLoop(loop.config, runner)

                    with self.assertRaises(ralph.RalphError) as caught:
                        probe.run()

                self.assertIn(
                    "Root worktree has uncommitted changes", str(caught.exception)
                )
                self.assertEqual(probe.implemented, 0)
                self.assertFalse(probe.promoted)
                commands = [call.args for call in runner.calls]
                self.assertEqual(commands, [("git", "status", "--porcelain")])
                self.assertNotIn(
                    (
                        "gh",
                        "issue",
                        "edit",
                        "42",
                        "-R",
                        "example/repo",
                        "--add-label",
                        "agent-running",
                    ),
                    commands,
                )
                self.assertFalse(
                    any(
                        command[:3] == ("git", "worktree", "add")
                        for command in commands
                    )
                )
                self.assertFalse(
                    any(
                        command[:3] == ("git", "push", "origin") for command in commands
                    )
                )

    def test_allow_dirty_worktree_bypasses_live_preflight(self) -> None:
        runner = FakeRunner(status_outputs=[" M scripts/ralph.py\n"])
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                drain=True,
                allow_dirty_worktree=True,
            )
            probe = PreflightProbeLoop(loop.config, runner)
            output = io.StringIO()

            with redirect_stdout(output):
                probe.run()

        self.assertEqual(probe.implemented, 1)
        self.assertIn(
            "Clean root worktree preflight bypassed by --allow-dirty-worktree.",
            output.getvalue(),
        )
        commands = [call.args for call in runner.calls]
        self.assertNotIn(("git", "status", "--porcelain"), commands)

    def test_dry_run_remains_usable_with_dirty_root_worktree(self) -> None:
        runner = FakeRunner(status_outputs=[" M scripts/ralph.py\n"])
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                issue=42,
                dry_run=True,
            )
            probe = PreflightProbeLoop(loop.config, runner)
            output = io.StringIO()

            with redirect_stdout(output):
                probe.run()

        self.assertEqual(probe.implemented, 0)
        self.assertIn(
            "DRY RUN: would implement #42: Implement thing", output.getvalue()
        )
        commands = [call.args for call in runner.calls]
        self.assertNotIn(("git", "status", "--porcelain"), commands)

    def test_drain_dry_run_previews_serial_and_bounded_exploratory_candidates(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                exploratory_concurrency=2,
                dry_run=True,
            )
            probe = DryRunPreviewLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                        title="Unlabeled exploration",
                    ),
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_TRUNK_LABEL},
                        IMPLEMENTATION_BODY,
                        number=42,
                        title="Labeled trunk work",
                    ),
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=43,
                        title="Labeled exploration",
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=44,
                        title="Overflow exploration",
                    ),
                ],
            )
            output = io.StringIO()

            with redirect_stdout(output):
                probe.run()

        text = output.getvalue()
        self.assertIn(
            "DRY RUN: serial candidate #42: Labeled trunk work "
            "(Delivery mode: trunk, Integration target: main)",
            text,
        )
        self.assertIn(
            "DRY RUN: Exploratory candidate #41: Unlabeled exploration "
            "(Delivery mode: exploratory, Integration target: "
            "agent/exploratory/issue-41-unlabeled-exploration)",
            text,
        )
        self.assertIn(
            "DRY RUN: Exploratory candidate #43: Labeled exploration "
            "(Delivery mode: exploratory, Integration target: "
            "agent/exploratory/issue-43-labeled-exploration)",
            text,
        )
        self.assertNotIn("#44: Overflow exploration", text)
        self.assertIn(
            "DRY RUN: showing 2 of 3 eligible Exploratory candidates "
            "(--exploratory-concurrency 2).",
            text,
        )
        self.assertIn(
            "DRY RUN: after each previewed Local integration or Exploratory "
            "handoff, would select Ready issue refresh candidates within "
            "--issue-limit 100.",
            text,
        )
        commands = [call.args for call in runner.calls]
        self.assertFalse(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )

    def test_drain_dry_run_previews_operator_smoke_without_execution(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                exploratory_concurrency=2,
                dry_run=True,
            )
            probe = DryRunPreviewLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                        OPERATOR_SMOKE_BODY,
                        number=41,
                        title="Credentialed smoke",
                    ),
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=42,
                        title="Plain exploration",
                    ),
                ],
            )
            output = io.StringIO()

            with redirect_stdout(output):
                probe.run()

        text = output.getvalue()
        self.assertIn(
            "DRY RUN: serial candidate #41: Credentialed smoke "
            "(Delivery mode: exploratory, Integration target: "
            "agent/exploratory/issue-41-credentialed-smoke)",
            text,
        )
        self.assertIn("DRY RUN: Operator smoke `ec2-run-worker-placement`", text)
        self.assertIn("run-ec2-run-worker-smoke", text)
        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any("run-ec2-run-worker-smoke" in " ".join(command) for command in commands)
        )

    def test_drain_scheduler_resolves_delivery_modes_before_lane_selection(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=4,
                exploratory_concurrency=2,
            )
            probe = LaneSchedulerProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    ),
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_TRUNK_LABEL},
                        IMPLEMENTATION_BODY,
                        number=42,
                    ),
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=43,
                    ),
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                        IMPLEMENTATION_BODY,
                        number=44,
                    ),
                ],
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                probe.run()

        self.assertEqual(probe.serial_started, [42, 44])
        self.assertEqual(probe.exploratory_started, [41, 43])
        self.assertEqual(probe.max_active_serial, 1)

    def test_drain_scheduler_runs_operator_smoke_issue_in_exclusive_serial_lane(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=2,
                exploratory_concurrency=2,
            )
            probe = LaneSchedulerProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                        OPERATOR_SMOKE_BODY,
                        number=41,
                        title="Credentialed smoke",
                    ),
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=42,
                        title="Parallel exploration",
                    ),
                ],
                blocked_issue_numbers={41, 42},
            )
            errors: list[BaseException] = []

            def run_probe() -> None:
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertFalse(probe.started_events[42].wait(timeout=0.05))
                probe.release_events[41].set()
                self.assertTrue(probe.started_events[42].wait(timeout=1))
            finally:
                for event in probe.release_events.values():
                    event.set()
                worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        if errors:
            raise errors[0]
        self.assertEqual(probe.serial_started, [41])
        self.assertEqual(probe.exploratory_started, [42])
        self.assertEqual(probe.max_active_exploratory, 1)
        self.assertEqual(probe.max_active_serial, 1)

    def test_drain_scheduler_limits_exploratory_worker_pool(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=3,
                exploratory_concurrency=2,
            )
            probe = LaneSchedulerProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=42,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=43,
                    ),
                ],
                blocked_issue_numbers={41, 42, 43},
            )
            errors: list[BaseException] = []

            def run_probe() -> None:
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertTrue(probe.started_events[42].wait(timeout=1))
                self.assertFalse(probe.started_events[43].wait(timeout=0.05))
                probe.release_events[41].set()
                self.assertTrue(probe.started_events[43].wait(timeout=1))
            finally:
                for event in probe.release_events.values():
                    event.set()
                worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        if errors:
            raise errors[0]
        self.assertLessEqual(probe.max_active_exploratory, 2)
        self.assertEqual(probe.exploratory_started, [41, 42, 43])

    def test_max_issues_waits_for_active_exploratory_workers(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=2,
                exploratory_concurrency=2,
            )
            probe = LaneSchedulerProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=42,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=43,
                    ),
                ],
                blocked_issue_numbers={41, 42},
            )
            errors: list[BaseException] = []

            def run_probe() -> None:
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertTrue(probe.started_events[42].wait(timeout=1))
                self.assertFalse(probe.started_events[43].wait(timeout=0.05))
                self.assertTrue(worker.is_alive())
            finally:
                for event in probe.release_events.values():
                    event.set()
                worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        if errors:
            raise errors[0]
        self.assertEqual(probe.exploratory_started, [41, 42])
        self.assertEqual(sorted(probe.completed_numbers), [41, 42])
        self.assertNotIn(43, probe.claimed_numbers)

    def test_scheduler_runs_triage_while_exploratory_workers_are_active(
        self,
    ) -> None:
        runner = FakeRunner(
            command_outputs={
                issue_list_command(): [
                    json.dumps([issue_payload(101, [ralph.NEEDS_TRIAGE_LABEL])]),
                    "[]",
                    "[]",
                    "[]",
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=2,
                exploratory_concurrency=1,
            )
            probe = TriageDuringExploratoryProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    )
                ],
                blocked_issue_numbers={41},
            )
            errors: list[BaseException] = []

            def run_probe() -> None:
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertTrue(probe.triage_started_event.wait(timeout=1))
                self.assertTrue(worker.is_alive())
            finally:
                probe.release_events[41].set()
                worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        if errors:
            raise errors[0]
        self.assertEqual(probe.exploratory_started, [41])
        self.assertEqual(probe.triage_started_numbers, [101])

    def test_scheduler_prioritizes_serial_ready_issue_over_triage(self) -> None:
        runner = FakeRunner(
            command_outputs={
                issue_list_command(): [
                    json.dumps([issue_payload(101, [ralph.NEEDS_TRIAGE_LABEL])]),
                    "[]",
                    "[]",
                    "[]",
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=3,
                exploratory_concurrency=1,
            )
            probe = TriageDuringExploratoryProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    ),
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_TRUNK_LABEL},
                        IMPLEMENTATION_BODY,
                        number=42,
                    ),
                ],
                blocked_issue_numbers={41, 42},
            )
            errors: list[BaseException] = []

            def run_probe() -> None:
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertTrue(probe.started_events[42].wait(timeout=1))
                self.assertFalse(probe.triage_started_event.wait(timeout=0.05))
                probe.release_events[42].set()
                self.assertTrue(probe.triage_started_event.wait(timeout=1))
            finally:
                for event in probe.release_events.values():
                    event.set()
                worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        if errors:
            raise errors[0]
        self.assertEqual(probe.serial_started, [42])
        self.assertEqual(probe.triage_started_numbers, [101])

    def test_scheduler_triage_is_excluded_from_max_issues_budget(self) -> None:
        runner = FakeRunner(
            command_outputs={
                issue_list_command(): [
                    json.dumps([issue_payload(101, [ralph.NEEDS_TRIAGE_LABEL])]),
                    "[]",
                    "[]",
                    "[]",
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=1,
                exploratory_concurrency=1,
            )
            probe = TriageDuringExploratoryProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=42,
                    ),
                ],
                blocked_issue_numbers={41},
            )
            errors: list[BaseException] = []

            def run_probe() -> None:
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertTrue(probe.triage_started_event.wait(timeout=1))
                self.assertFalse(probe.started_events[42].wait(timeout=0.05))
            finally:
                probe.release_events[41].set()
                worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        if errors:
            raise errors[0]
        self.assertEqual(probe.exploratory_started, [41])
        self.assertEqual(probe.triage_started_numbers, [101])
        self.assertNotIn(42, probe.claimed_numbers)

    def test_scheduler_triage_keeps_existing_candidate_filters(self) -> None:
        runner = FakeRunner(
            command_outputs={
                issue_list_command(): [
                    json.dumps(
                        [
                            issue_payload(
                                101,
                                [ralph.NEEDS_TRIAGE_LABEL],
                                implementation_body_with_blockers(99),
                            ),
                            issue_payload(
                                102,
                                [
                                    ralph.NEEDS_TRIAGE_LABEL,
                                    ralph.AGENT_REVIEWING_LABEL,
                                ],
                            ),
                            issue_payload(103, [ralph.NEEDS_TRIAGE_LABEL]),
                            issue_payload(104, [ralph.NEEDS_TRIAGE_LABEL]),
                        ]
                    ),
                    "[]",
                    "[]",
                    "[]",
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=2,
                exploratory_concurrency=1,
            )
            probe = TriageDuringExploratoryProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    )
                ],
                blocked_issue_numbers={41},
            )
            probe.triaged_this_run.add(103)
            errors: list[BaseException] = []

            def run_probe() -> None:
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertTrue(probe.triage_started_event.wait(timeout=1))
            finally:
                probe.release_events[41].set()
                worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        if errors:
            raise errors[0]
        self.assertEqual(probe.triage_started_numbers, [104])

    def test_scheduler_triage_failure_waits_for_active_exploratory_workers(
        self,
    ) -> None:
        runner = FakeRunner(
            command_outputs={
                issue_list_command(): [
                    json.dumps([issue_payload(101, [ralph.NEEDS_TRIAGE_LABEL])])
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=2,
                exploratory_concurrency=1,
            )
            triage_failure = ralph.CommandFailure(
                ["codex", "exec"],
                loop.config.repo_root,
                1,
                "",
                "fake triage failure",
                None,
            )
            probe = TriageDuringExploratoryProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    )
                ],
                blocked_issue_numbers={41},
                triage_failure=triage_failure,
            )
            errors: list[BaseException] = []

            def run_probe() -> None:
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertTrue(probe.triage_started_event.wait(timeout=1))
                self.assertTrue(worker.is_alive())
                probe.release_events[41].set()
            finally:
                probe.release_events[41].set()
                worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        self.assertEqual(errors, [triage_failure])
        self.assertEqual(probe.completed_numbers, [41])

    def test_ready_issue_refresh_gate_pauses_claims_while_active_workers_finish(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=3,
                exploratory_concurrency=2,
            )
            probe = RefreshGateSchedulerProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=42,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=43,
                    ),
                ],
                refresh_issue_numbers={41},
                blocked_issue_numbers={42},
            )
            errors: list[BaseException] = []

            def run_probe() -> None:
                try:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertTrue(probe.started_events[42].wait(timeout=1))
                self.assertTrue(probe.refresh_started_events[41].wait(timeout=1))
                probe.release_events[42].set()
                self.assertTrue(probe.completed_events[42].wait(timeout=1))
                self.assertFalse(probe.started_events[43].wait(timeout=0.05))
                probe.refresh_release_events[41].set()
                self.assertTrue(probe.started_events[43].wait(timeout=1))
            finally:
                for event in probe.release_events.values():
                    event.set()
                for event in probe.refresh_release_events.values():
                    event.set()
                worker.join(timeout=2)

        self.assertFalse(worker.is_alive())
        if errors:
            raise errors[0]
        self.assertEqual(sorted(probe.claimed_numbers), [41, 42, 43])

    def test_ready_issue_refresh_failure_stops_claims_and_records_fatal_stop(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=3,
                exploratory_concurrency=2,
            )
            probe = RefreshGateSchedulerProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=42,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=43,
                    ),
                ],
                refresh_failure_issue_numbers={41},
                blocked_issue_numbers={42},
            )
            errors: list[BaseException] = []
            stdout = io.StringIO()
            stderr = io.StringIO()

            def run_probe() -> None:
                try:
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        probe.run()
                except BaseException as error:
                    errors.append(error)

            worker = threading.Thread(target=run_probe)
            worker.start()
            try:
                self.assertTrue(probe.started_events[41].wait(timeout=1))
                self.assertTrue(probe.started_events[42].wait(timeout=1))
                self.assertTrue(probe.refresh_started_events[41].wait(timeout=1))
                probe.refresh_release_events[41].set()
                self.assertFalse(probe.started_events[43].wait(timeout=0.05))
                probe.release_events[42].set()
                self.assertTrue(probe.completed_events[42].wait(timeout=1))
            finally:
                for event in probe.release_events.values():
                    event.set()
                for event in probe.refresh_release_events.values():
                    event.set()
                worker.join(timeout=2)

            manifest_41 = load_run_manifest(tmp_path, run_glob="issue-41-*")
            manifest_42 = load_run_manifest(tmp_path, run_glob="issue-42-*")

        self.assertFalse(worker.is_alive())
        self.assertTrue(errors)
        self.assertIsInstance(errors[0], ralph.ReadyIssueRefreshFailure)
        self.assertNotIn(43, probe.claimed_numbers)
        self.assertIn("Ready issue refresh gate active", stdout.getvalue())
        self.assertIn(
            "Fatal drain stop: ready_issue_refresh_failure", stderr.getvalue()
        )
        self.assertEqual(
            manifest_41["drain_scheduler"]["fatal_stop"]["status"], "triggered"
        )
        self.assertEqual(
            manifest_42["drain_scheduler"]["fatal_stop"]["status"], "observed"
        )
        self.assertEqual(
            manifest_42["drain_scheduler"]["fatal_stop"]["reason"],
            "ready_issue_refresh_failure",
        )

    def test_post_push_and_environment_failures_stop_claims_after_active_workers(
        self,
    ) -> None:
        for fatal_kind, expected_error, expected_reason in [
            ("post_push", ralph.PostPushFailure, "post_push_failure"),
            ("environment", ralph.EnvironmentFailure, "environment_failure"),
        ]:
            with self.subTest(fatal_kind=fatal_kind):
                runner = FakeRunner()
                with tempfile.TemporaryDirectory() as tmp:
                    tmp_path = Path(tmp)
                    loop = make_loop(
                        tmp_path,
                        runner,
                        delivery_mode=ralph.EXPLORATORY_MODE,
                        drain=True,
                        max_issues=3,
                        exploratory_concurrency=2,
                    )
                    probe = RefreshGateSchedulerProbeLoop(
                        loop.config,
                        runner,
                        [
                            make_issue(
                                {ralph.READY_LABEL},
                                EXPLORATORY_IMPLEMENTATION_BODY,
                                number=41,
                            ),
                            make_issue(
                                {ralph.READY_LABEL},
                                EXPLORATORY_IMPLEMENTATION_BODY,
                                number=42,
                            ),
                            make_issue(
                                {ralph.READY_LABEL},
                                EXPLORATORY_IMPLEMENTATION_BODY,
                                number=43,
                            ),
                        ],
                        fatal_kinds={41: fatal_kind},
                        blocked_issue_numbers={42},
                    )
                    errors: list[BaseException] = []
                    stderr = io.StringIO()

                    def run_probe() -> None:
                        try:
                            with (
                                redirect_stdout(io.StringIO()),
                                redirect_stderr(stderr),
                            ):
                                probe.run()
                        except BaseException as error:
                            errors.append(error)

                    worker = threading.Thread(target=run_probe)
                    worker.start()
                    try:
                        self.assertTrue(probe.started_events[41].wait(timeout=1))
                        self.assertTrue(probe.started_events[42].wait(timeout=1))
                        probe.fatal_release_events[41].set()
                        self.assertTrue(probe.fatal_started_events[41].wait(timeout=1))
                        self.assertFalse(probe.started_events[43].wait(timeout=0.05))
                        probe.release_events[42].set()
                        self.assertTrue(probe.completed_events[42].wait(timeout=1))
                    finally:
                        for event in probe.release_events.values():
                            event.set()
                        for event in probe.fatal_release_events.values():
                            event.set()
                        worker.join(timeout=2)

                    manifest_41 = load_run_manifest(tmp_path, run_glob="issue-41-*")
                    manifest_42 = load_run_manifest(tmp_path, run_glob="issue-42-*")

                self.assertFalse(worker.is_alive())
                self.assertTrue(errors)
                self.assertIsInstance(errors[0], expected_error)
                self.assertNotIn(43, probe.claimed_numbers)
                self.assertIn(f"Fatal drain stop: {expected_reason}", stderr.getvalue())
                self.assertEqual(
                    manifest_41["drain_scheduler"]["fatal_stop"]["status"],
                    "triggered",
                )
                self.assertEqual(
                    manifest_42["drain_scheduler"]["fatal_stop"]["status"],
                    "observed",
                )
                self.assertEqual(
                    manifest_42["drain_scheduler"]["fatal_stop"]["reason"],
                    expected_reason,
                )

    def test_issue_failure_in_exploratory_lane_does_not_stop_unrelated_work(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
                max_issues=3,
                exploratory_concurrency=2,
            )
            probe = LaneSchedulerProbeLoop(
                loop.config,
                runner,
                [
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=41,
                    ),
                    make_issue(
                        {ralph.READY_LABEL},
                        EXPLORATORY_IMPLEMENTATION_BODY,
                        number=42,
                    ),
                    make_issue(
                        {ralph.READY_LABEL, ralph.DELIVERY_TRUNK_LABEL},
                        IMPLEMENTATION_BODY,
                        number=43,
                    ),
                ],
                issue_failures={41},
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                probe.run()

        self.assertEqual(probe.failed_numbers, [41])
        self.assertIn(42, probe.completed_numbers)
        self.assertIn(43, probe.completed_numbers)

    def test_targeted_issue_does_not_use_parallel_drain_scheduler(self) -> None:
        class TargetedProbeLoop(PreflightProbeLoop):
            def __init__(self, config: ralph.LoopConfig, runner: FakeRunner) -> None:
                super().__init__(config, runner)
                self.scheduler_called = False

            def _run_drain_scheduler(self) -> None:
                self.scheduler_called = True
                raise AssertionError("targeted issue should remain single-issue path")

        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                drain=True,
                issue=42,
            )
            probe = TargetedProbeLoop(loop.config, runner)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                probe.run()

        self.assertEqual(probe.implemented, 1)
        self.assertFalse(probe.scheduler_called)

    def test_completion_comment_records_local_integration_evidence(self) -> None:
        issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
        qa_results = [
            ralph.QAResult(
                command=ralph.QACommand(
                    ("make", "run-prek"),
                    Path("/repo"),
                    "Ralph loop Commit check",
                ),
                log_path=Path("/logs/qa.log"),
            )
        ]

        comment = ralph.build_completion_comment(
            issue,
            "abc123",
            ["scripts/ralph.py"],
            qa_results,
            Path("/logs/run"),
            delivery_plan=ralph.DeliveryPlan(
                mode=ralph.TRUNK_MODE,
                target_branch="main",
                label="delivery-trunk",
                add_labels=(),
                remove_labels=(),
            ),
        )

        self.assertIn("Ralph trunk integration completed.", comment)
        self.assertIn("Commit: `abc123`", comment)
        self.assertIn("Delivery mode: `trunk`", comment)
        self.assertIn("- `scripts/ralph.py`", comment)
        self.assertIn("make run-prek", comment)
        self.assertIn("Issue #42 will be closed by the Ralph loop.", comment)

    def test_exploratory_completion_comment_records_review_branch(self) -> None:
        issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
        qa_results = [
            ralph.QAResult(
                command=ralph.QACommand(
                    ("make", "run-prek"),
                    Path("/repo"),
                    "Ralph loop Commit check",
                ),
                log_path=Path("/logs/qa.log"),
            )
        ]

        comment = ralph.build_completion_comment(
            issue,
            "abc123",
            ["scripts/ralph.py"],
            qa_results,
            Path("/logs/run"),
            delivery_plan=ralph.DeliveryPlan(
                mode=ralph.EXPLORATORY_MODE,
                target_branch="agent/exploratory/issue-42-implement-thing",
                label="delivery-exploratory",
                add_labels=(),
                remove_labels=(),
            ),
        )

        self.assertIn("Ralph exploratory handoff completed.", comment)
        self.assertIn("Delivery mode: `exploratory`", comment)
        self.assertIn(
            "Target branch: `agent/exploratory/issue-42-implement-thing`", comment
        )
        self.assertIn("Issue #42 is ready for review on", comment)

    def test_user_facing_error_includes_command_stderr(self) -> None:
        error = ralph.CommandFailure(
            ["gh", "auth", "status"],
            Path("/repo"),
            1,
            "",
            "The token in default is invalid.",
            None,
        )

        message = ralph.user_facing_error(error)

        self.assertIn("Command: gh auth status", message)
        self.assertIn("Exit code: 1", message)
        self.assertIn("The token in default is invalid.", message)


class RalphRunInspectionRecoveryTests(unittest.TestCase):
    def _requeue_manifest_paths(self, run_dir: Path) -> tuple[Path, Path, str, str]:
        manifest = json.loads((run_dir / "ralph-run.json").read_text(encoding="utf-8"))
        paths = manifest["paths"]
        branches = manifest["branches"]
        return (
            Path(paths["implementation_worktree"]),
            Path(paths["integration_worktree"]),
            branches["issue"],
            f"refs/ralph/requeue/{ralph.slugify(run_dir.name)}",
        )

    def _requeue_worktree_list(
        self,
        *,
        repo_root: Path,
        implementation_worktree: Path,
        integration_worktree: Path,
        issue_branch: str,
        implementation_head: str = "impl-sha",
        integration_head: str = "integration-sha",
    ) -> str:
        return "\n".join(
            [
                f"worktree {repo_root}",
                "HEAD base-sha",
                "branch refs/heads/main",
                "",
                f"worktree {implementation_worktree}",
                f"HEAD {implementation_head}",
                f"branch refs/heads/{issue_branch}",
                "",
                f"worktree {integration_worktree}",
                f"HEAD {integration_head}",
                "detached",
                "",
            ]
        )

    def _requeue_command_outputs(
        self,
        *,
        run_dir: Path,
        implementation_worktree: Path,
        integration_worktree: Path,
        issue_branch: str,
        backup_ref: str,
        labels: list[str] | None = None,
        comments: list[dict[str, Any]] | None = None,
        implementation_head: str = "impl-sha",
        integration_head: str = "integration-sha",
    ) -> dict[tuple[str, ...], list[str]]:
        repo_root = run_dir.parents[1] / "repo"
        return {
            issue_view_command(234): [
                json.dumps(
                    issue_payload(
                        234,
                        labels
                        or [
                            ralph.AGENT_FAILED_LABEL,
                            "enhancement",
                            ralph.DELIVERY_GITFLOW_LABEL,
                        ],
                    )
                )
            ],
            issue_comments_command(234): [json.dumps({"comments": comments or []})],
            ("git", "worktree", "list", "--porcelain"): [
                self._requeue_worktree_list(
                    repo_root=repo_root,
                    implementation_worktree=implementation_worktree,
                    integration_worktree=integration_worktree,
                    issue_branch=issue_branch,
                    implementation_head=implementation_head,
                    integration_head=integration_head,
                )
            ],
            (
                "git",
                "for-each-ref",
                "--format=%(objectname)",
                "--count=1",
                f"refs/heads/{issue_branch}",
            ): [f"{implementation_head}\n"],
            (
                "git",
                "for-each-ref",
                "--format=%(objectname)",
                "--count=1",
                backup_ref,
            ): [""],
        }

    def test_inspect_run_reports_manifest_state_without_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_recovery_manifest(
                Path(tmp),
                metadata_status="completion_commented",
            )
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_run(run_dir)

        text = output.getvalue()
        self.assertIn("Issue: #42 Implement thing", text)
        self.assertIn("Delivery mode: trunk", text)
        self.assertIn("Integration target: main", text)
        self.assertIn("QA status: passed (1/1)", text)
        self.assertIn("Push status: pushed (main @ abc1234)", text)
        self.assertIn("Metadata status: completion_commented", text)
        self.assertIn("Adaptive events: none", text)
        self.assertIn("Requeue eligibility: not eligible", text)
        self.assertIn("manifest already records integration_commit", text)
        self.assertIn("manifest records a pushed Integration target", text)
        self.assertIn("--recover-run", text)

    def test_inspect_run_reports_adaptive_event_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_recovery_manifest(
                Path(tmp),
                metadata_status="failed",
            )
            manifest_path = run_dir / "ralph-run.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["adaptive_events"] = [
                {
                    "timestamp": "2026-05-28T00:00:00Z",
                    "event_type": "hard_stop",
                    "trigger_reason": "Post-push boundary could not be verified.",
                    "issue_number": 42,
                    "residual_work_summary": "Inspect issue metadata and branch state.",
                    "automatic_retry_allowed": False,
                    "consumes_attempt_budget": False,
                }
            ]
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_run(run_dir)

        text = output.getvalue()
        self.assertIn("Adaptive events:", text)
        self.assertIn("hard_stop issue #42", text)
        self.assertIn("automatic_retry=no", text)
        self.assertIn("consumes_attempt_budget=no", text)
        self.assertIn("residual_work=Inspect issue metadata and branch state.", text)
        self.assertIn("Hard stop recorded: Post-push boundary", text)
        self.assertIn("Do not run an automatic Codex retry", text)
        self.assertNotIn("Verify the recorded commit", text)

    def test_inspect_run_reports_requeue_eligible_pre_push_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_failed_pre_push_requeue_manifest(tmp_path)
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_run(run_dir)

        text = output.getvalue()
        self.assertIn("Issue: #234 Fix Marimo dashboard", text)
        self.assertIn("Delivery mode: gitflow", text)
        self.assertIn("Integration target: dev", text)
        self.assertIn("QA status: passed (3/3)", text)
        self.assertIn("Issue completion review status: passed (pass)", text)
        self.assertIn("Push status: not_started", text)
        self.assertIn("Requeue eligibility: eligible", text)
        self.assertIn("implementation QA passed", text)
        self.assertIn("no integration_commit was recorded", text)
        self.assertIn("no Integration target push was recorded", text)
        self.assertIn(
            f"container={tmp_path / 'worktrees'}; "
            f"implementation={tmp_path / 'worktrees' / 'agent-issue-234'}; "
            f"integration={tmp_path / 'worktrees' / 'agent-integrate-issue-234'}",
            text,
        )
        self.assertIn(
            "Local issue branch: agent/issue-234-fix-marimo-dashboard",
            text,
        )
        self.assertIn(
            "GitHub labels: future requeue would add ready-for-agent and remove agent-failed",
            text,
        )
        self.assertIn(
            "manifest failure labeling evidence: added agent-failed; "
            "removed agent-running, ready-for-agent",
            text,
        )
        self.assertIn(
            "GitHub labels: future requeue would preserve delivery-gitflow", text
        )
        self.assertIn(
            "Run evidence: Issue completion review passed (pass); artifact:",
            text,
        )
        self.assertIn("Run evidence: failure Command failed: git commit", text)
        self.assertIn("integration-git-commit.log", text)
        self.assertIn(
            f"python3 scripts/ralph.py --recover-run {run_dir} --dry-run",
            text,
        )
        self.assertIn(
            f"rerun without `--dry-run`: "
            f"`python3 scripts/ralph.py --recover-run {run_dir}`",
            text,
        )
        self.assertNotIn("--recover-run is not applicable", text)

    def test_recover_run_dry_run_reports_pre_push_requeue_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_failed_pre_push_requeue_manifest(tmp_path)
            implementation_worktree, integration_worktree, issue_branch, backup_ref = (
                self._requeue_manifest_paths(run_dir)
            )
            implementation_worktree.mkdir(parents=True)
            integration_worktree.mkdir(parents=True)
            runner = FakeRunner(
                status_outputs=["", ""],
                command_outputs=self._requeue_command_outputs(
                    run_dir=run_dir,
                    implementation_worktree=implementation_worktree,
                    integration_worktree=integration_worktree,
                    issue_branch=issue_branch,
                    backup_ref=backup_ref,
                ),
                fail_commands={
                    (
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        "impl-sha",
                        "origin/dev",
                    ),
                    (
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        "integration-sha",
                        "origin/dev",
                    ),
                },
            )
            loop = make_loop(
                tmp_path,
                runner,
                delivery_mode=ralph.GITFLOW_MODE,
                dry_run=True,
            )
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

        text = output.getvalue()
        commands = [call.args for call in runner.calls]
        self.assertIn("Ralph pre-push requeue recovery", text)
        self.assertIn("Issue: #234 Issue 234", text)
        self.assertIn("Eligibility: eligible", text)
        self.assertIn("Labels to add: ready-for-agent", text)
        self.assertIn("Labels to remove: agent-failed", text)
        self.assertIn(f"Backup ref: would create {backup_ref} -> impl-sha", text)
        self.assertIn(
            f"- implementation_worktree: will remove {implementation_worktree}",
            text,
        )
        self.assertIn(
            f"- integration_worktree: will remove {integration_worktree}",
            text,
        )
        self.assertIn(
            f"- local_issue_branch: will delete {issue_branch}",
            text,
        )
        self.assertIn(ralph.PRE_PUSH_REQUEUE_COMMENT_TITLE, text)
        self.assertFalse(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertFalse(
            any(command[:2] == ("make", "run-prek") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(
                command[:3] == ("git", "update-ref", backup_ref) for command in commands
            )
        )

    def test_recover_run_requeue_allows_integration_worktree_at_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_failed_pre_push_requeue_manifest(tmp_path)
            implementation_worktree, integration_worktree, issue_branch, backup_ref = (
                self._requeue_manifest_paths(run_dir)
            )
            implementation_worktree.mkdir(parents=True)
            integration_worktree.mkdir(parents=True)
            runner = FakeRunner(
                status_outputs=["", ""],
                command_outputs=self._requeue_command_outputs(
                    run_dir=run_dir,
                    implementation_worktree=implementation_worktree,
                    integration_worktree=integration_worktree,
                    issue_branch=issue_branch,
                    backup_ref=backup_ref,
                    integration_head="base-sha",
                ),
                fail_commands={
                    (
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        "impl-sha",
                        "origin/dev",
                    ),
                },
            )
            loop = make_loop(
                tmp_path,
                runner,
                delivery_mode=ralph.GITFLOW_MODE,
                dry_run=True,
            )

            with redirect_stdout(io.StringIO()):
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

        self.assertFalse(
            any(
                call.args
                == (
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    "base-sha",
                    "origin/dev",
                )
                for call in runner.calls
            )
        )

    def test_recover_run_requeues_pre_push_failure_and_cleans_local_artifacts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_failed_pre_push_requeue_manifest(tmp_path)
            implementation_worktree, integration_worktree, issue_branch, backup_ref = (
                self._requeue_manifest_paths(run_dir)
            )
            implementation_worktree.mkdir(parents=True)
            integration_worktree.mkdir(parents=True)
            runner = FakeRunner(
                status_outputs=["", ""],
                command_outputs=self._requeue_command_outputs(
                    run_dir=run_dir,
                    implementation_worktree=implementation_worktree,
                    integration_worktree=integration_worktree,
                    issue_branch=issue_branch,
                    backup_ref=backup_ref,
                ),
                fail_commands={
                    (
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        "impl-sha",
                        "origin/dev",
                    ),
                    (
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        "integration-sha",
                        "origin/dev",
                    ),
                },
            )
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

            comment = (run_dir / "issue-234-comment.md").read_text(encoding="utf-8")
            manifest = json.loads(
                (run_dir / "ralph-run.json").read_text(encoding="utf-8")
            )

        commands = [call.args for call in runner.calls]
        self.assertIn(
            ("git", "update-ref", backup_ref, "impl-sha"),
            commands,
        )
        self.assertIn(
            ("git", "worktree", "remove", str(implementation_worktree)),
            commands,
        )
        self.assertIn(
            ("git", "worktree", "remove", str(integration_worktree)),
            commands,
        )
        self.assertIn(("git", "branch", "-D", issue_branch), commands)
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "234",
                "-R",
                "example/repo",
                "--add-label",
                "ready-for-agent",
                "--remove-label",
                "agent-failed",
            ),
            commands,
        )
        self.assertIn(ralph.PRE_PUSH_REQUEUE_COMMENT_TITLE, comment)
        self.assertIn(
            f"Preserved implementation commit: `impl-sha` at `{backup_ref}`", comment
        )
        self.assertIn("Delivery mode: `gitflow`", comment)
        self.assertIn("Integration target: `dev`", comment)
        self.assertEqual(manifest["github_metadata"]["status"], "pre_push_requeued")
        self.assertEqual(manifest["github_metadata"]["backup_ref"], backup_ref)
        self.assertFalse(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertFalse(
            any(command[:3] == ("git", "push", "origin") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )

    def test_recover_run_requeue_is_idempotent_after_partial_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_failed_pre_push_requeue_manifest(tmp_path)
            (
                _implementation_worktree,
                _integration_worktree,
                issue_branch,
                backup_ref,
            ) = self._requeue_manifest_paths(run_dir)
            comment_body = "\n".join(
                [
                    ralph.PRE_PUSH_REQUEUE_COMMENT_TITLE,
                    "",
                    f"Recovered from run: `{run_dir}`",
                    f"Preserved implementation commit: `impl-sha` at `{backup_ref}`",
                ]
            )
            runner = FakeRunner(
                command_outputs={
                    issue_view_command(234): [
                        json.dumps(
                            issue_payload(
                                234,
                                [
                                    ralph.READY_LABEL,
                                    "enhancement",
                                    ralph.DELIVERY_GITFLOW_LABEL,
                                ],
                            )
                        )
                    ],
                    issue_comments_command(234): [
                        json.dumps({"comments": [{"body": comment_body}]})
                    ],
                    ("git", "worktree", "list", "--porcelain"): [""],
                    (
                        "git",
                        "for-each-ref",
                        "--format=%(objectname)",
                        "--count=1",
                        f"refs/heads/{issue_branch}",
                    ): [""],
                    (
                        "git",
                        "for-each-ref",
                        "--format=%(objectname)",
                        "--count=1",
                        backup_ref,
                    ): ["impl-sha\n"],
                },
                fail_commands={
                    (
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        "impl-sha",
                        "origin/dev",
                    )
                },
            )
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

            manifest = json.loads(
                (run_dir / "ralph-run.json").read_text(encoding="utf-8")
            )

        text = output.getvalue()
        commands = [call.args for call in runner.calls]
        self.assertIn("backup ref already preserved", text)
        self.assertIn("already absent", text)
        self.assertIn("pre-push requeue comment already present", text)
        self.assertIn("requeue labels already reconciled", text)
        self.assertEqual(manifest["github_metadata"]["status"], "pre_push_requeued")
        self.assertFalse(
            any(command[:2] == ("git", "update-ref") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "remove") for command in commands)
        )
        self.assertFalse(any(command[:2] == ("git", "branch") for command in commands))
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )

    def test_recover_run_refuses_pre_push_requeue_when_target_contains_work(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_failed_pre_push_requeue_manifest(tmp_path)
            implementation_worktree, integration_worktree, issue_branch, backup_ref = (
                self._requeue_manifest_paths(run_dir)
            )
            runner = FakeRunner(
                command_outputs=self._requeue_command_outputs(
                    run_dir=run_dir,
                    implementation_worktree=implementation_worktree,
                    integration_worktree=integration_worktree,
                    issue_branch=issue_branch,
                    backup_ref=backup_ref,
                )
            )
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)

            with self.assertRaises(ralph.RalphError) as caught:
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

        commands = [call.args for call in runner.calls]
        self.assertIn("already reachable from origin/dev", str(caught.exception))
        self.assertFalse(
            any(command[:2] == ("git", "update-ref") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )

    def test_recover_run_refuses_dirty_requeue_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_failed_pre_push_requeue_manifest(tmp_path)
            implementation_worktree, integration_worktree, issue_branch, backup_ref = (
                self._requeue_manifest_paths(run_dir)
            )
            implementation_worktree.mkdir(parents=True)
            integration_worktree.mkdir(parents=True)
            runner = FakeRunner(
                status_outputs=[" M tools/ralph-loop/src/ralph_loop/cli.py\n"],
                command_outputs=self._requeue_command_outputs(
                    run_dir=run_dir,
                    implementation_worktree=implementation_worktree,
                    integration_worktree=integration_worktree,
                    issue_branch=issue_branch,
                    backup_ref=backup_ref,
                ),
            )
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)

            with self.assertRaises(ralph.RalphError) as caught:
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

        commands = [call.args for call in runner.calls]
        self.assertIn("implementation_worktree is dirty", str(caught.exception))
        self.assertFalse(
            any(command[:2] == ("git", "update-ref") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )

    def test_inspect_run_reports_branch_sync_recovery_guidance(self) -> None:
        guidance = "Inspect `/worktrees/agent-sync-main-into-dev` before rerunning Ralph drain."
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = write_recovery_manifest(Path(tmp))
            manifest_path = run_dir / "ralph-run.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["integration_commit"] = None
            manifest["pushes"] = {}
            manifest["branch_sync"] = {
                "status": "failed",
                "source_branch": "main",
                "target_branch": "dev",
                "worktree_path": "/worktrees/agent-sync-main-into-dev",
                "log_path": str(run_dir / "git-merge-main-into-dev.log"),
                "conflicted_files": ["scripts/ralph.py"],
                "recovery_guidance": guidance,
                "failure_type": "merge_conflict",
                "error": "merge conflict",
            }
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_run(run_dir)

        text = output.getvalue()
        self.assertIn("Branch sync status: failed", text)
        self.assertIn(guidance, text)
        self.assertNotIn("--recover-run", text)

    def test_inspect_run_reports_acceptance_conflict_continue_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = tmp_path / "logs" / "exploratory-acceptance-20260504T010203Z"
            acceptance_path = tmp_path / "worktrees" / "agent-exploratory-acceptance"
            run_dir.mkdir(parents=True)
            manifest = {
                "schema_version": ralph.MANIFEST_SCHEMA_VERSION,
                "run_kind": "exploratory_acceptance_apply",
                "status": ralph.EXPLORATORY_ACCEPTANCE_CONFLICT_STATUS,
                "delivery_mode": ralph.EXPLORATORY_MODE,
                "integration_target": "dev",
                "source_branch": "dev",
                "paths": {
                    "run_dir": str(run_dir),
                    "repo_root": str(tmp_path / "repo"),
                    "acceptance_worktree": str(acceptance_path),
                },
                "qa_results": [],
                "pushes": {},
                "github_metadata": {"status": "not_started"},
                "ready_issue_refresh": {"status": "not_started"},
                "events": [],
            }
            (run_dir / "ralph-run.json").write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_run(run_dir)

        text = output.getvalue()
        self.assertIn(f"Paused acceptance worktree: {acceptance_path}", text)
        self.assertIn(
            "Continue command: python3 scripts/ralph.py "
            f"--continue-exploratory-acceptance {run_dir}",
            text,
        )
        self.assertIn("Recommended next action:", text)


class RalphOperatorRunTests(unittest.TestCase):
    def test_operator_preflight_reports_runtime_env_sources(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ScriptedOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=1,
                snapshots=[],
            )

            with patch.dict(
                ralph.os.environ,
                {
                    "PATH": "/usr/bin",
                    "UV_CACHE_DIR": "/operator/uv-cache",
                    ralph.QA_RUNTIME_MIN_FREE_BYTES_ENV: "0",
                    ralph.QA_RUNTIME_MIN_FREE_INODES_ENV: "0",
                },
                clear=True,
            ):
                output = io.StringIO()
                with redirect_stdout(output):
                    operator._preflight_qa_runtime_disk(label="Operator launch")

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())

        text = output.getvalue()
        self.assertIn("QA runtime disk preflight (Operator launch)", text)
        self.assertIn("DAGSTER_HOME: ralph_default ->", text)
        self.assertIn("UV_CACHE_DIR: operator -> /operator/uv-cache", text)
        preflight_event = next(
            event
            for event in manifest["events"]
            if event["state"] == "qa_runtime_disk_preflight"
        )
        self.assertEqual(
            preflight_event["details"]["variables"]["UV_CACHE_DIR"]["source"],
            "operator",
        )

    def test_operator_auto_recovers_verified_post_push_metadata_failure(self) -> None:
        runner = FakeRunner(
            command_outputs={
                issue_view_command(42): [
                    issue_view_output(labels=[ralph.AGENT_RUNNING_LABEL])
                ],
                issue_comments_command(42): [json.dumps({"comments": []})],
                issue_state_command(42): [json.dumps({"state": "OPEN"})],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                drain=True,
                delivery_mode=ralph.GITFLOW_MODE,
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ralph.RalphOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=1,
            )
            recovery_loop = PostPushMetadataRecoveryLoop(loop.config, runner)
            operator.loop = recovery_loop
            operator.github = recovery_loop.github
            output = io.StringIO()

            with redirect_stdout(output), redirect_stderr(io.StringIO()):
                operator._run_drain_scheduler_checkpoint()

            child_manifest = json.loads(
                recovery_loop.manifest_path.read_text(encoding="utf-8")
            )
            operator_manifest = json.loads(
                (run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text(encoding="utf-8")
            )
            comment = (
                recovery_loop.manifest_path.parent / "issue-42-comment.md"
            ).read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "fetch", "origin", "dev"), commands)
        self.assertIn(
            ("git", "merge-base", "--is-ancestor", "abc1234", "origin/dev"),
            commands,
        )
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "42",
                "-R",
                "example/repo",
                "--add-label",
                "agent-integrated",
                "--remove-label",
                "agent-running",
                "--remove-label",
                "agent-failed",
                "--remove-label",
                "agent-merged",
                "--remove-label",
                "ready-for-agent",
            ),
            commands,
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )
        self.assertEqual(child_manifest["status"], "succeeded")
        self.assertEqual(child_manifest["stage"], "metadata_recovery_resume_decision")
        self.assertEqual(
            child_manifest["github_metadata"]["status"],
            "marked_integrated",
        )
        self.assertEqual(child_manifest["ready_issue_refresh"]["status"], "completed")
        self.assertEqual(
            child_manifest["adaptive_events"][-1]["event_type"],
            "residual_update",
        )
        self.assertIn("Ralph Gitflow integration completed.", comment)
        self.assertIn("Commit: `abc1234`", comment)
        checkpoints = [
            checkpoint["checkpoint"] for checkpoint in operator_manifest["checkpoints"]
        ]
        self.assertLess(
            checkpoints.index("issue_metadata_recovered"),
            checkpoints.index("metadata_recovery_resume_allowed"),
        )
        self.assertLess(
            checkpoints.index("metadata_recovery_resume_allowed"),
            checkpoints.index("issue_succeeded"),
        )
        recovery_events = [event["stage"] for event in child_manifest["events"]]
        self.assertLess(
            recovery_events.index("verified_metadata_recovered"),
            recovery_events.index(
                "ready_issue_refresh_pending_after_metadata_recovery"
            ),
        )
        self.assertLess(
            recovery_events.index("ready_issue_refresh_completed"),
            recovery_events.index("metadata_recovery_resume_decision"),
        )
        self.assertIn(
            "Operator verified post-push metadata recovery", output.getvalue()
        )

    def test_operator_metadata_recovery_is_idempotent_when_manifest_complete(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                drain=True,
                delivery_mode=ralph.GITFLOW_MODE,
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ralph.RalphOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=1,
            )
            recovery_loop = PostPushMetadataRecoveryLoop(
                loop.config,
                runner,
                metadata_status="marked_integrated",
            )
            operator.loop = recovery_loop
            operator.github = recovery_loop.github

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                operator._run_drain_scheduler_checkpoint()

            child_manifest = json.loads(
                recovery_loop.manifest_path.read_text(encoding="utf-8")
            )

        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "fetch", "origin", "dev"), commands)
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "view") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertEqual(child_manifest["status"], "succeeded")
        self.assertEqual(
            child_manifest["stage"],
            "metadata_recovery_resume_decision",
        )
        self.assertEqual(child_manifest["ready_issue_refresh"]["status"], "completed")
        self.assertEqual(
            child_manifest["github_metadata"]["status"],
            "marked_integrated",
        )
        self.assertEqual(
            child_manifest["adaptive_events"][-1]["event_type"],
            "residual_update",
        )

    def test_operator_metadata_recovery_blocks_resume_when_refresh_pending_fails(
        self,
    ) -> None:
        runner = FakeRunner(
            command_outputs={
                issue_view_command(42): [
                    issue_view_output(labels=[ralph.AGENT_RUNNING_LABEL])
                ],
                issue_comments_command(42): [json.dumps({"comments": []})],
                issue_state_command(42): [json.dumps({"state": "OPEN"})],
            },
            fail_ready_issue_refresh_analysis=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                drain=True,
                delivery_mode=ralph.GITFLOW_MODE,
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ralph.RalphOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=1,
            )
            recovery_loop = PostPushMetadataRecoveryLoop(loop.config, runner)
            operator.loop = recovery_loop
            operator.github = recovery_loop.github

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(ralph.ReadyIssueRefreshFailure):
                    operator._run_drain_scheduler_checkpoint()

            child_manifest = json.loads(
                recovery_loop.manifest_path.read_text(encoding="utf-8")
            )
            operator_manifest = json.loads(
                (run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text(encoding="utf-8")
            )

        checkpoints = [
            checkpoint["checkpoint"] for checkpoint in operator_manifest["checkpoints"]
        ]
        self.assertIn("issue_metadata_recovered", checkpoints)
        self.assertNotIn("metadata_recovery_resume_allowed", checkpoints)
        self.assertNotIn("issue_succeeded", checkpoints)
        self.assertEqual(child_manifest["status"], "failed")
        self.assertEqual(child_manifest["ready_issue_refresh"]["status"], "failed")
        recovery_events = [event["stage"] for event in child_manifest["events"]]
        self.assertLess(
            recovery_events.index("verified_metadata_recovered"),
            recovery_events.index(
                "ready_issue_refresh_pending_after_metadata_recovery"
            ),
        )
        self.assertIn("metadata_recovery_resume_decision", recovery_events)
        resume_event = next(
            event
            for event in child_manifest["events"]
            if event["stage"] == "metadata_recovery_resume_decision"
        )
        self.assertEqual(
            resume_event["details"]["resume_decision"],
            "blocked_ready_issue_refresh",
        )

    def test_operator_metadata_recovery_refuses_unverified_commit(self) -> None:
        ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "abc1234",
            "origin/dev",
        )
        runner = FakeRunner(fail_commands={ancestor_command: 1})
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                drain=True,
                delivery_mode=ralph.GITFLOW_MODE,
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ralph.RalphOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=1,
            )
            recovery_loop = PostPushMetadataRecoveryLoop(loop.config, runner)
            operator.loop = recovery_loop
            operator.github = recovery_loop.github

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(ralph.RalphError) as caught:
                    operator._run_drain_scheduler_checkpoint()

            child_manifest = json.loads(
                recovery_loop.manifest_path.read_text(encoding="utf-8")
            )
            operator_manifest = json.loads(
                (run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text(encoding="utf-8")
            )

        commands = [call.args for call in runner.calls]
        self.assertIn(
            "not reachable from expected Integration target",
            str(caught.exception),
        )
        self.assertNotIn(issue_view_command(42), commands)
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertEqual(
            child_manifest["adaptive_events"][-1]["event_type"],
            "hard_stop",
        )
        self.assertEqual(operator_manifest["status"], "failed")
        self.assertEqual(
            operator_manifest["last_checkpoint"]["checkpoint"],
            "issue_failed",
        )

    def test_operator_skips_post_promotion_deployment_when_classifier_has_no_deploy(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
                title="Agent workflow change",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = PromotionDeploymentOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=2,
                snapshots=[operator_snapshot(integrated=[integrated_issue])],
                changed_files=[
                    ".agents/skills/ralph-loop/SKILL.md",
                    "tools/ralph-loop/src/ralph_loop/cli.py",
                ],
            )

            with redirect_stdout(io.StringIO()):
                operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())
            promotion_manifest_path = Path(
                next(
                    child["path"]
                    for child in manifest["child_run_manifests"]
                    if child["kind"] == "promotion"
                )
            )
            promotion_manifest = json.loads(
                promotion_manifest_path.read_text(encoding="utf-8")
            )

        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        self.assertIn("deployment_skipped", checkpoints)
        self.assertLess(
            checkpoints.index("post_promotion_ready_issue_refresh"),
            checkpoints.index("deployment_skipped"),
        )
        self.assertEqual(
            promotion_manifest["deployment_execution"]["status"],
            "skipped_no_deployment",
        )
        self.assertEqual(
            promotion_manifest["deployment_execution"]["tier"],
            ralph.POST_PROMOTION_DEPLOYMENT_NO_DEPLOY,
        )
        self.assertFalse(
            any(
                str(call.args[0]).endswith("redeploy-user-code")
                or str(call.args[0]).endswith("run-integration-tests")
                for call in runner.calls
                if call.args
            )
        )

    def test_operator_runs_user_code_redeploy_after_promotion_refresh(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=43,
                title="AEMO ETL runtime change",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = PromotionDeploymentOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=2,
                snapshots=[operator_snapshot(integrated=[integrated_issue])],
                changed_files=[
                    "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"
                ],
            )

            with redirect_stdout(io.StringIO()):
                operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())
            promotion_manifest_path = Path(
                next(
                    child["path"]
                    for child in manifest["child_run_manifests"]
                    if child["kind"] == "promotion"
                )
            )
            promotion_manifest = json.loads(
                promotion_manifest_path.read_text(encoding="utf-8")
            )

        expected_command = (
            loop.config.repo_root
            / ralph.POST_PROMOTION_DEPLOYMENT_REDEPLOY_USER_CODE_COMMAND
        )
        deployment_calls = [
            call
            for call in runner.calls
            if call.args and call.args[0] == str(expected_command)
        ]
        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        self.assertEqual(len(deployment_calls), 1)
        self.assertEqual(
            deployment_calls[0].cwd,
            loop.config.repo_root / "infrastructure" / "aws-pulumi",
        )
        self.assertEqual(deployment_calls[0].execute_in_dry_run, False)
        self.assertLess(
            checkpoints.index("post_promotion_ready_issue_refresh"),
            checkpoints.index("deployment_started"),
        )
        self.assertLess(
            checkpoints.index("deployment_started"),
            checkpoints.index("deployment_succeeded"),
        )
        deployment = promotion_manifest["deployment_execution"]
        self.assertEqual(deployment["status"], "succeeded")
        self.assertEqual(deployment["exit_status"], 0)
        self.assertEqual(
            deployment["command_path"],
            ralph.POST_PROMOTION_DEPLOYMENT_REDEPLOY_USER_CODE_COMMAND,
        )
        self.assertEqual(
            deployment["deployed_test_evidence"]["status"],
            "not_applicable",
        )

    def test_operator_runs_full_deployed_workflow_with_idempotency_evidence(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=44,
                title="Pulumi runtime change",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = PromotionDeploymentOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=2,
                snapshots=[operator_snapshot(integrated=[integrated_issue])],
                changed_files=["infrastructure/aws-pulumi/components/ecs_services.py"],
            )

            with redirect_stdout(io.StringIO()):
                operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())
            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            promotion_manifest_path = Path(
                next(
                    child["path"]
                    for child in manifest["child_run_manifests"]
                    if child["kind"] == "promotion"
                )
            )
            promotion_manifest = json.loads(
                promotion_manifest_path.read_text(encoding="utf-8")
            )

        expected_command = (
            loop.config.repo_root
            / ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_COMMAND
        )
        deployment_calls = [
            call
            for call in runner.calls
            if call.args and call.args[0] == str(expected_command)
        ]
        self.assertEqual(len(deployment_calls), 1)
        self.assertIn(
            ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_IDEMPOTENCY_ARG,
            deployment_calls[0].args,
        )
        deployment = promotion_manifest["deployment_execution"]
        self.assertEqual(deployment["status"], "succeeded")
        self.assertEqual(
            deployment["command_path"],
            ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_COMMAND,
        )
        self.assertEqual(deployment["deployed_test_evidence"]["status"], "passed")
        self.assertEqual(
            deployment["full_tier_idempotency_evidence"]["status"],
            "passed",
        )
        self.assertEqual(
            deployment["full_tier_idempotency_evidence"]["argument"],
            ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_IDEMPOTENCY_ARG,
        )
        operator_deployment_checkpoint = next(
            checkpoint
            for checkpoint in manifest["checkpoints"]
            if checkpoint["checkpoint"] == "deployment_succeeded"
        )
        self.assertEqual(
            operator_deployment_checkpoint["details"]["command_path"],
            ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_COMMAND,
        )
        self.assertEqual(
            operator_deployment_checkpoint["details"]["exit_status"],
            0,
        )
        self.assertEqual(
            operator_deployment_checkpoint["details"]["deployed_test_evidence"][
                "status"
            ],
            "passed",
        )
        self.assertEqual(
            manifest["last_checkpoint"]["checkpoint"],
            "queue_clean",
        )
        self.assertEqual(
            rollup["deployment_executions"][0]["command_path"],
            ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_COMMAND,
        )

    def test_operator_deployment_failure_creates_deploy_repair_issue_and_records_manifests(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            probe_runner = FakeRunner()
            loop = make_loop(tmp_path, probe_runner, drain=True)
            expected_command = (
                str(
                    loop.config.repo_root
                    / ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_COMMAND
                ),
                ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_IDEMPOTENCY_ARG,
            )
            runner = FakeRunner(fail_commands={expected_command})
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=45,
                title="Pulumi runtime change",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = PromotionDeploymentOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=2,
                snapshots=[operator_snapshot(integrated=[integrated_issue])],
                changed_files=["infrastructure/aws-pulumi/components/ecs_services.py"],
            )

            with self.assertRaises(ralph.RalphError):
                with redirect_stdout(io.StringIO()):
                    operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())
            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            promotion_manifest_path = Path(
                next(
                    child["path"]
                    for child in manifest["child_run_manifests"]
                    if child["kind"] == "promotion"
                )
            )
            promotion_manifest = json.loads(
                promotion_manifest_path.read_text(encoding="utf-8")
            )

        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        self.assertIn("deploy_repair_issue_creation", checkpoints)
        self.assertIn("deployment_failed", checkpoints)
        self.assertLess(
            checkpoints.index("deploy_repair_issue_creation"),
            checkpoints.index("deployment_failed"),
        )
        self.assertEqual(promotion_manifest["deployment_execution"]["status"], "failed")
        self.assertEqual(
            promotion_manifest["deploy_repair_issues"]["status"],
            "completed",
        )
        self.assertEqual(
            promotion_manifest["deploy_repair_issues"]["created"][0][
                "validation_status"
            ],
            "ready",
        )
        self.assertEqual(manifest["deploy_repair"]["status"], "active")
        self.assertEqual(manifest["deploy_repair"]["target_issue"]["number"], 99)
        self.assertEqual(manifest["deploy_repair"]["cycle_count"], 1)
        self.assertEqual(
            rollup["deploy_repair_issues"][0]["created"][0]["number"],
            99,
        )

    def test_operator_targets_active_deploy_repair_before_unrelated_ready_issue(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            unrelated_issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=40,
                title="Older unrelated work",
            )
            repair_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=99,
                title="Repair deployment",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = TargetedDeploymentOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=6,
                snapshots=[
                    operator_snapshot(ready=[unrelated_issue, repair_issue]),
                    operator_snapshot(
                        integrated=[
                            make_issue(
                                {ralph.AGENT_INTEGRATED_LABEL},
                                IMPLEMENTATION_BODY,
                                number=99,
                                title="Repair deployment",
                            )
                        ]
                    ),
                    operator_snapshot(ready=[unrelated_issue]),
                    operator_snapshot(),
                ],
                changed_files=[
                    "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"
                ],
            )
            operator.manifest.record_deploy_repair_target(
                {
                    "number": 99,
                    "title": "Repair deployment",
                    "url": "https://github.com/example/repo/issues/99",
                    "labels": [
                        "bug",
                        ralph.DELIVERY_GITFLOW_LABEL,
                        ralph.READY_LABEL,
                    ],
                    "source_marker": "ralph-deploy-repair:seed",
                    "validation_status": "ready",
                },
                child_manifest_path=None,
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())

        self.assertEqual(operator.implemented_issue_numbers, [99, 40])
        self.assertEqual(operator.scheduler_runs, 1)
        self.assertEqual(manifest["deploy_repair"]["status"], "inactive")
        self.assertIsNone(manifest["deploy_repair"]["target_issue"])
        self.assertEqual(manifest["deploy_repair"]["cycle_count"], 1)

    def test_operator_stops_after_two_automated_deploy_repair_cycles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            probe_runner = FakeRunner()
            loop = make_loop(tmp_path, probe_runner, drain=True)
            expected_command = (
                str(
                    loop.config.repo_root
                    / ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_COMMAND
                ),
                ralph.POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_IDEMPOTENCY_ARG,
            )
            runner = FakeRunner(fail_commands={expected_command})
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=101,
                title="Second repair integrated",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = PromotionDeploymentOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=2,
                snapshots=[operator_snapshot(integrated=[integrated_issue])],
                changed_files=["infrastructure/aws-pulumi/components/ecs_services.py"],
            )
            operator.manifest.data["deploy_repair"] = {
                "status": "active",
                "target_issue": {
                    "number": 101,
                    "title": "Second repair integrated",
                    "url": "https://github.com/example/repo/issues/101",
                    "labels": ["bug", ralph.DELIVERY_GITFLOW_LABEL, ralph.READY_LABEL],
                    "source_marker": "ralph-deploy-repair:second",
                    "validation_status": "ready",
                },
                "cycle_count": 2,
                "cycle_limit": ralph.DEFAULT_DEPLOY_REPAIR_CYCLE_LIMIT,
                "history": [],
            }

            with self.assertRaises(ralph.RalphError):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())

        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        self.assertIn("deploy_repair_cycle_limit_reached", checkpoints)
        self.assertEqual(manifest["deploy_repair"]["cycle_count"], 2)
        self.assertIn("cycle limit", manifest["recovery_guidance"])
        self.assertIn("#99", manifest["recovery_guidance"])

    def test_operator_foreground_repeats_drain_promotion_until_queue_clean(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            initial_issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
                title="Initial work",
            )
            followup_issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=99,
                title="Post-promotion follow-up",
            )
            snapshots = [
                operator_snapshot(ready=[initial_issue]),
                operator_snapshot(
                    integrated=[
                        make_issue(
                            {ralph.AGENT_INTEGRATED_LABEL},
                            IMPLEMENTATION_BODY,
                            number=42,
                            title="Initial work",
                        )
                    ]
                ),
                operator_snapshot(ready=[followup_issue]),
                operator_snapshot(
                    integrated=[
                        make_issue(
                            {ralph.AGENT_INTEGRATED_LABEL},
                            IMPLEMENTATION_BODY,
                            number=99,
                            title="Post-promotion follow-up",
                        )
                    ]
                ),
                operator_snapshot(),
            ]
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ScriptedOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=6,
                snapshots=snapshots,
            )

            with redirect_stdout(io.StringIO()):
                operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())
            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            markdown = (run_dir / ralph.OPERATOR_ROLLUP_MARKDOWN_NAME).read_text(
                encoding="utf-8"
            )

        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual(manifest["state"], "queue_clean")
        self.assertEqual(checkpoints.count("issue_succeeded"), 2)
        self.assertEqual(checkpoints.count("before_promotion"), 2)
        self.assertEqual(checkpoints.count("promotion_succeeded"), 2)
        self.assertEqual(checkpoints.count("post_promotion_followup_creation"), 2)
        self.assertEqual(checkpoints[-1], "queue_clean")
        self.assertEqual(len(manifest["child_run_manifests"]), 4)
        self.assertTrue(
            any(
                child["kind"] == "promotion" and child["status"] == "succeeded"
                for child in manifest["child_run_manifests"]
            )
        )
        self.assertEqual(rollup["summary"]["succeeded_issues"], 2)
        self.assertEqual(rollup["summary"]["promotions"], 2)
        self.assertEqual(rollup["summary"]["local_integrations"], 2)
        self.assertTrue(rollup["summary"]["final_queue_clean"])
        self.assertEqual(
            rollup["post_promotion_followups"][0]["created"],
            [{"number": 100, "url": "https://example.test/0"}],
        )
        self.assertIn("#42 Initial work", markdown)
        self.assertIn("Local integration `local-integration-42-1`", markdown)
        self.assertIn("Promotion commit `promotion-1-sha`", markdown)
        self.assertIn("- clean=yes", markdown)

    def test_operator_promotes_integrated_backlog_before_ready_claim_at_startup(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            ready_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=99,
                title="Ready follow-up",
            )
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
                title="Integrated backlog",
            )
            ready_integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=99,
                title="Ready follow-up",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ScriptedOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=4,
                snapshots=[
                    operator_snapshot(
                        ready=[ready_issue],
                        integrated=[integrated_issue],
                    ),
                    operator_snapshot(ready=[ready_issue]),
                    operator_snapshot(integrated=[ready_integrated_issue]),
                    operator_snapshot(),
                ],
            )

            with redirect_stdout(io.StringIO()):
                operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())

        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        first_promotion_index = checkpoints.index("before_promotion")
        first_issue_index = checkpoints.index("issue_succeeded")
        self.assertLess(first_promotion_index, first_issue_index)
        self.assertEqual(operator.issue_runs, 1)
        self.assertEqual(operator.promotion_runs, 2)
        self.assertEqual(manifest["status"], "succeeded")

    def test_operator_starts_ready_queue_when_no_integrated_backlog(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            oldest_ready = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
                title="Oldest ready work",
            )
            newer_ready = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=99,
                title="Newer ready work",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ScriptedOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=2,
                snapshots=[
                    operator_snapshot(ready=[oldest_ready, newer_ready]),
                    operator_snapshot(),
                ],
            )

            with redirect_stdout(io.StringIO()):
                operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())

        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        succeeded_issues = [
            entry["issue"]["number"]
            for entry in manifest["checkpoints"]
            if entry["checkpoint"] == "issue_succeeded"
        ]
        self.assertLess(
            checkpoints.index("issue_succeeded"),
            checkpoints.index("queue_clean"),
        )
        self.assertNotIn("before_promotion", checkpoints)
        self.assertEqual(succeeded_issues, [42, 99])

    def test_operator_baseline_guard_skips_low_risk_ready_queue(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            ready_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
            )
            guard_loop = BaselineGuardLoop(
                loop.config,
                runner,
                issues=[ready_issue],
            )

            with redirect_stdout(io.StringIO()):
                guard_loop._run_drain_scheduler()

        self.assertEqual(guard_loop.handled_issue_numbers, [42])
        self.assertFalse(
            any(call.args == ("make", "run-prek") for call in runner.calls)
        )

    def test_operator_baseline_guard_runs_for_integrated_backlog_queue(
        self,
    ) -> None:
        runner = FakeRunner(rev_parse_outputs=["target-sha\n"])
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=41,
            )
            ready_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
            )
            guard_loop = BaselineGuardLoop(
                loop.config,
                runner,
                issues=[integrated_issue, ready_issue],
            )
            output = io.StringIO()

            with redirect_stdout(output):
                guard_loop._run_drain_scheduler()

        baseline_calls = [
            call for call in runner.calls if call.args == ("make", "run-prek")
        ]
        self.assertEqual(guard_loop.handled_issue_numbers, [42])
        self.assertEqual(len(baseline_calls), 1)
        self.assertTrue(str(baseline_calls[0].cwd).endswith("/tools/ralph-loop"))
        self.assertIn("agent-integrated backlog exists", output.getvalue())

    def test_operator_baseline_guard_healthy_result_is_cached_by_target_sha(
        self,
    ) -> None:
        runner = FakeRunner(rev_parse_outputs=["target-sha\n", "target-sha\n"])
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=41,
            )
            first_ready = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
            )
            second_ready = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=43,
            )
            guard_loop = BaselineGuardLoop(
                loop.config,
                runner,
                issues=[integrated_issue, first_ready, second_ready],
            )

            with redirect_stdout(io.StringIO()):
                guard_loop._run_drain_scheduler()

        baseline_calls = [
            call for call in runner.calls if call.args == ("make", "run-prek")
        ]
        self.assertEqual(guard_loop.handled_issue_numbers, [42, 43])
        self.assertEqual(len(baseline_calls), 1)

    def test_operator_baseline_guard_failing_baseline_stops_before_claim(
        self,
    ) -> None:
        runner = FakeRunner(
            rev_parse_outputs=["target-sha\n"],
            fail_commands={("make", "run-prek")},
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=41,
            )
            ready_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
            )
            guard_loop = BaselineGuardLoop(
                loop.config,
                runner,
                issues=[integrated_issue, ready_issue],
            )

            with self.assertRaises(ralph.IntegrationTargetBaselineFailure) as caught:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    guard_loop._run_drain_scheduler()

        text = str(caught.exception)
        self.assertEqual(guard_loop.handled_issue_numbers, [])
        self.assertIn("Failing command: `make run-prek`", text)
        self.assertIn("Test lane: `Ralph loop Commit check`", text)
        self.assertIn("Recovery guidance:", text)
        self.assertFalse(
            any(call.args[:3] == ("git", "worktree", "remove") for call in runner.calls)
        )

    def test_operator_baseline_guard_runs_for_agent_workflow_change_queue(
        self,
    ) -> None:
        runner = FakeRunner(rev_parse_outputs=["target-sha\n"])
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            ready_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                AGENTS_IMPLEMENTATION_BODY,
                number=42,
            )
            guard_loop = BaselineGuardLoop(
                loop.config,
                runner,
                issues=[ready_issue],
            )
            output = io.StringIO()

            with redirect_stdout(output):
                guard_loop._run_drain_scheduler()

        baseline_calls = [
            call for call in runner.calls if call.args == ("make", "run-prek")
        ]
        self.assertEqual(guard_loop.handled_issue_numbers, [42])
        self.assertEqual(len(baseline_calls), 1)
        self.assertIn("declares Agent workflow context anchors", output.getvalue())

    def test_operator_recovery_guidance_names_integrated_backlog_when_blocked(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
                title="Integrated backlog",
            )
            failed_issue = make_issue(
                {ralph.AGENT_FAILED_LABEL},
                IMPLEMENTATION_BODY,
                number=77,
                title="Needs recovery",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ScriptedOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=2,
                snapshots=[
                    operator_snapshot(
                        integrated=[integrated_issue],
                        failed=[failed_issue],
                    )
                ],
            )

            with self.assertRaises(ralph.RalphError):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    operator.run()

            status_output = io.StringIO()
            with redirect_stdout(status_output):
                ralph.inspect_operator_run_status(str(run_dir), runner)
            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())
            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )

        guidance = manifest["recovery_guidance"]
        self.assertIn("agent-failed issue(s)", guidance)
        self.assertIn("#77", guidance)
        self.assertIn("agent-integrated issue(s)", guidance)
        self.assertIn("#42", guidance)
        self.assertIn("#42", status_output.getvalue())
        self.assertIn("#77", status_output.getvalue())
        self.assertIn("#42", rollup["stop_reason"]["recovery_guidance"])
        self.assertIn("#77", rollup["stop_reason"]["recovery_guidance"])
        self.assertEqual(rollup["final_queue"]["counts"]["integrated"], 1)
        self.assertEqual(rollup["final_queue"]["counts"]["failed"], 1)

    def test_operator_stops_after_ralph_loop_self_update_before_next_claim(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                drain=True,
                delivery_mode=ralph.GITFLOW_MODE,
            )
            self_update_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=173,
                title="Update Ralph loop",
            )
            next_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=174,
                title="Next ready work",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = SelfUpdateGuardOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=3,
                snapshots=[operator_snapshot(ready=[self_update_issue, next_issue])],
                issues=[self_update_issue, next_issue],
                changed_files_by_issue={
                    173: ["tools/ralph-loop/src/ralph_loop/cli.py"],
                    174: ["README.md"],
                },
            )

            with self.assertRaises(ralph.RalphSelfUpdateRestartRequired):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())

        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        self.assertEqual(operator.guard_loop.handled_issue_numbers, [173])
        self.assertEqual(checkpoints.count("issue_succeeded"), 1)
        self.assertIn("ralph_self_update_restart_required", checkpoints)
        self.assertNotIn("before_promotion", checkpoints)
        self.assertEqual(manifest["status"], "failed")
        self.assertIn(
            "restart the Operator command",
            manifest["recovery_guidance"],
        )
        self.assertIn(
            "tools/ralph-loop/src/ralph_loop/cli.py",
            manifest["recovery_guidance"],
        )

    def test_operator_isolates_ralph_loop_self_update_from_exploratory_claims(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                drain=True,
                delivery_mode=ralph.GITFLOW_MODE,
                exploratory_concurrency=2,
            )
            exploratory_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                EXPLORATORY_IMPLEMENTATION_BODY,
                number=172,
                title="Explore unrelated work",
            )
            self_update_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                RALPH_SELF_UPDATE_BODY,
                number=173,
                title="Update Ralph loop",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = SelfUpdateGuardOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=3,
                snapshots=[
                    operator_snapshot(ready=[exploratory_issue, self_update_issue])
                ],
                issues=[exploratory_issue, self_update_issue],
                changed_files_by_issue={
                    172: ["README.md"],
                    173: ["scripts/ralph.py"],
                },
            )

            with self.assertRaises(ralph.RalphSelfUpdateRestartRequired):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())

        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        self.assertEqual(operator.guard_loop.handled_issue_numbers, [173])
        self.assertEqual(checkpoints.count("issue_succeeded"), 1)
        self.assertIn("ralph_self_update_restart_required", checkpoints)
        self.assertNotIn(
            172,
            [
                child["issue"]["number"]
                for child in manifest["child_run_manifests"]
                if isinstance(child.get("issue"), dict)
            ],
        )

    def test_operator_records_parallel_scheduler_issue_checkpoints_before_promotion(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                drain=True,
                delivery_mode=ralph.GITFLOW_MODE,
                exploratory_concurrency=3,
            )
            exploratory_one = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                EXPLORATORY_IMPLEMENTATION_BODY,
                number=41,
                title="Explore first path",
            )
            exploratory_two = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                EXPLORATORY_IMPLEMENTATION_BODY,
                number=42,
                title="Explore second path",
            )
            gitflow_issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=43,
                title="Integrate serial path",
            )
            integrated_issue = make_issue(
                {ralph.AGENT_INTEGRATED_LABEL},
                IMPLEMENTATION_BODY,
                number=43,
                title="Integrate serial path",
            )
            events: list[str] = []
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ParallelSchedulerOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=3,
                snapshots=[
                    operator_snapshot(
                        ready=[exploratory_one, exploratory_two, gitflow_issue]
                    ),
                    operator_snapshot(integrated=[integrated_issue]),
                    operator_snapshot(),
                ],
                events=events,
            )

            with redirect_stdout(io.StringIO()):
                operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())
            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )

        checkpoints = [entry["checkpoint"] for entry in manifest["checkpoints"]]
        issue_checkpoint_indexes = [
            index
            for index, checkpoint in enumerate(checkpoints)
            if checkpoint == "issue_succeeded"
        ]
        promotion_index = checkpoints.index("before_promotion")
        self.assertEqual(operator.observed_exploratory_concurrency, 3)
        self.assertEqual(
            events,
            ["scheduler_started", "ready_issue_refresh_settled", "promotion_started"],
        )
        self.assertEqual(len(issue_checkpoint_indexes), 3)
        self.assertTrue(
            all(index < promotion_index for index in issue_checkpoint_indexes)
        )
        self.assertEqual(len(manifest["child_run_manifests"]), 4)
        self.assertEqual(rollup["summary"]["succeeded_issues"], 3)
        self.assertEqual(
            [entry["issue"]["number"] for entry in rollup["issues"]["succeeded"]],
            [41, 42, 43],
        )

    def test_operator_rollup_records_operator_smoke_status_and_log_path(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            issue = make_issue(
                {ralph.DELIVERY_EXPLORATORY_LABEL},
                OPERATOR_SMOKE_BODY,
                number=42,
                title="Credentialed smoke",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator_manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=1,
            )
            child_run_dir = tmp_path / "logs" / "issue-42-smoke"
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=ralph.EXPLORATORY_MODE,
                target_branch=None,
            )
            worktree_path = (
                tmp_path / "worktrees" / "agent-exploratory-issue-42-credentialed-smoke"
            )
            child_manifest = ralph.RunManifest.for_implementation(
                run_dir=child_run_dir,
                issue=issue,
                delivery_plan=delivery_plan,
                branch=delivery_plan.target_branch,
                worktree_path=worktree_path,
                integration_path=None,
                config=loop.config,
            )
            smoke_log = child_run_dir / "operator-smoke.log"
            smoke_result = ralph.OperatorSmokeResult(
                smoke_id="ec2-run-worker-placement",
                command_path=ralph.OPERATOR_SMOKE_EC2_RUN_WORKER_PLACEMENT_COMMAND,
                command_args=(
                    str(
                        worktree_path
                        / ralph.OPERATOR_SMOKE_EC2_RUN_WORKER_PLACEMENT_COMMAND
                    ),
                ),
                cwd=worktree_path / ralph.OPERATOR_SMOKE_EC2_RUN_WORKER_PLACEMENT_CWD,
                log_path=smoke_log,
                timeout_seconds=120,
                evidence_path=child_run_dir / "operator-smoke-evidence.json",
                exit_status=0,
                status="succeeded",
            )
            child_manifest.record_operator_smoke("succeeded", result=smoke_result)
            child_manifest.record_success()
            operator_manifest.record_checkpoint(
                "issue_succeeded",
                message="Issue #42 completed.",
                child_manifest_path=child_manifest.path,
                issue=issue,
            )
            operator_manifest.record_queue(operator_snapshot())
            operator_manifest.record_checkpoint(
                "queue_clean",
                message="No open ready-for-agent, agent-integrated, agent-running, or agent-failed issues remain.",
                status="succeeded",
            )
            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            markdown = (run_dir / ralph.OPERATOR_ROLLUP_MARKDOWN_NAME).read_text(
                encoding="utf-8"
            )

        self.assertEqual(rollup["summary"]["operator_smokes"], 1)
        self.assertEqual(rollup["operator_smokes"][0]["status"], "succeeded")
        self.assertEqual(rollup["operator_smokes"][0]["log_path"], str(smoke_log))
        self.assertIn("## Operator Smokes", markdown)
        self.assertIn(str(smoke_log), markdown)

    def test_operator_stops_needs_review_and_writes_exploratory_acceptance_review(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            reviewing_body = (
                EXPLORATORY_IMPLEMENTATION_BODY
                + "\n## Context anchors\n"
                + "- Test lane: `Ralph loop Commit check`\n"
                + "- Test lane: `root Commit check`\n"
            )
            reviewing_issue = make_issue(
                {ralph.AGENT_REVIEWING_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL},
                reviewing_body,
                number=42,
                title="Explore workflow",
            )
            blocked_ready_issue = make_issue(
                {ralph.READY_LABEL},
                implementation_body_with_blockers(42),
                number=136,
                title="Dependent ready work",
            )
            operator = BlockedReadyOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=3,
                snapshots=[
                    operator_snapshot(
                        ready=[blocked_ready_issue],
                        reviewing=[reviewing_issue],
                    )
                ],
            )
            handoff_branch = "agent/exploratory/issue-42-explore-workflow"
            child_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="issue-42-exploratory-handoff",
                run_kind="implementation",
                status="succeeded",
                issue=reviewing_issue,
                delivery_mode=ralph.EXPLORATORY_MODE,
                integration_target=handoff_branch,
                integration_commit="handoff-sha",
                changed_files=[
                    "scripts/ralph.py",
                    "tools/ralph-loop/tests/unit/test_ralph.py",
                ],
                qa_results=[
                    {
                        "name": "Ralph loop Commit check",
                        "command": ["make", "run-prek"],
                        "cwd": str(tmp_path / "repo"),
                        "log_path": str(
                            tmp_path / "repo" / ".ralph" / "runs" / "unit.log"
                        ),
                        "status": "passed",
                    }
                ],
            )
            operator.manifest.record_child_run(child_manifest_path)
            output = io.StringIO()

            with redirect_stdout(output):
                operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())
            review = json.loads(
                (run_dir / ralph.EXPLORATORY_ACCEPTANCE_REVIEW_JSON_NAME).read_text(
                    encoding="utf-8"
                )
            )
            review_markdown = (
                run_dir / ralph.EXPLORATORY_ACCEPTANCE_REVIEW_MARKDOWN_NAME
            ).read_text(encoding="utf-8")
            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            status_output = io.StringIO()
            with redirect_stdout(status_output):
                ralph.inspect_operator_run_status(str(run_dir), runner)

        commands = [call.args for call in runner.calls]
        self.assertEqual(manifest["status"], "needs_review")
        self.assertEqual(manifest["state"], "exploratory_acceptance_review_required")
        self.assertEqual(
            manifest["last_checkpoint"]["checkpoint"],
            "exploratory_acceptance_review_required",
        )
        self.assertEqual(manifest["queue"]["reviewing"][0]["number"], 42)
        self.assertEqual(review["status"], "needs_review")
        self.assertEqual(review["source_ref"], "origin/dev")
        self.assertEqual(review["issues"][0]["branch"], handoff_branch)
        self.assertEqual(review["issues"][0]["handoff_commit"], "handoff-sha")
        self.assertEqual(
            review["issues"][0]["changed_files"],
            ["scripts/ralph.py", "tools/ralph-loop/tests/unit/test_ralph.py"],
        )
        self.assertEqual(
            review["issues"][0]["downstream_ready_issues"][0]["number"],
            136,
        )
        self.assertEqual(
            review["issues"][0]["missing_test_lane_evidence"],
            ["root Commit check"],
        )
        self.assertEqual(review["issues"][0]["mergeability"]["status"], "clean")
        self.assertEqual(rollup["operator_run"]["status"], "needs_review")
        self.assertEqual(
            rollup["exploratory_acceptance_review"]["status"], "needs_review"
        )
        self.assertEqual(rollup["final_queue"]["counts"]["reviewing"], 1)
        self.assertIn("### #42 Explore workflow", review_markdown)
        self.assertIn("#136 Dependent ready work", review_markdown)
        self.assertIn(
            "Run the $ralph-loop Exploratory acceptance review flow", output.getvalue()
        )
        self.assertIn(
            "Queue: ready=1, integrated=0, reviewing=1", status_output.getvalue()
        )
        self.assertIn("Recommended next action:", status_output.getvalue())
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )

    def test_operator_keeps_queue_blocked_for_non_review_blocked_ready_issue(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            blocked_ready_issue = make_issue(
                {ralph.READY_LABEL},
                implementation_body_with_blockers(99),
                number=136,
                title="Blocked ready work",
            )
            operator = BlockedReadyOperatorRun(
                loop.config,
                runner,
                run_dir=run_dir,
                max_cycles=3,
                snapshots=[operator_snapshot(ready=[blocked_ready_issue])],
            )

            with self.assertRaises(ralph.RalphError):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    operator.run()

            manifest = json.loads((run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text())

        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["state"], "failed")
        self.assertEqual(manifest["last_checkpoint"]["checkpoint"], "queue_blocked")

    def test_operator_rollup_records_failed_attempt_manual_recovery_and_guard_stop(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            failed_issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=77,
                title="Broken attempt",
            )
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=1,
            )
            failed_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="issue-77-failed",
                run_kind="implementation",
                status="failed",
                issue=failed_issue,
                qa_results=[
                    {
                        "name": "script Unit test",
                        "command": ["python3", "-m", "unittest", "tests.test_ralph"],
                        "cwd": str(tmp_path / "repo"),
                        "log_path": str(
                            tmp_path / "repo" / ".ralph" / "runs" / "unit.log"
                        ),
                        "status": "failed",
                    }
                ],
            )
            manifest.record_checkpoint(
                "issue_failed",
                message="Issue #77 failed.",
                child_manifest_path=failed_manifest_path,
                issue=failed_issue,
                status="failed",
                recovery_guidance="Inspect issue #77 before rerunning.",
            )
            manual_recovery_issue = {
                "number": 102,
                "title": "Recover issue integration",
                "url": "https://github.com/example/repo/issues/102",
                "integrated_commit": None,
                "metadata_status": "manual_recovery_commit_unparseable",
                "warning": (
                    "#102 has manual Gitflow recovery evidence but no parseable "
                    "integrated commit for Promotion closure."
                ),
                "recovery_action": "Reconcile the manual recovery evidence.",
            }
            promotion_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="promote-manual-recovery",
                run_kind="promotion",
                status="succeeded",
                promotion_commit="promotion-manual-sha",
                manual_recoveries=[manual_recovery_issue],
                unverified_commits=[
                    {
                        "sha": "manual-recovery-sha",
                        "subject": "Manual Gitflow recovery for issue 102",
                        "classification": "unverified_promotion_commit",
                    }
                ],
                followups_status="completed_with_warnings",
                created_followups=1,
            )
            manifest.record_checkpoint(
                "promotion_succeeded",
                message="Promotion completed.",
                child_manifest_path=promotion_manifest_path,
            )
            manifest.record_checkpoint(
                "post_promotion_followup_creation",
                message="Post-promotion follow-up creation completed with warnings.",
                child_manifest_path=promotion_manifest_path,
                details={"status": "completed_with_warnings"},
            )
            manifest.record_queue(operator_snapshot(failed=[failed_issue]))
            manifest.record_checkpoint(
                "stopped_by_guard",
                message="Reached --max-cycles 1.",
                status="failed",
                recovery_guidance="Review progress before raising --max-cycles.",
            )

            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            markdown = (run_dir / ralph.OPERATOR_ROLLUP_MARKDOWN_NAME).read_text(
                encoding="utf-8"
            )

        self.assertEqual(rollup["summary"]["failed_issues"], 1)
        self.assertEqual(rollup["summary"]["manual_recoveries"], 1)
        self.assertEqual(rollup["summary"]["failed_attempts"], 1)
        self.assertFalse(rollup["summary"]["final_queue_clean"])
        self.assertEqual(rollup["final_queue"]["counts"]["failed"], 1)
        self.assertTrue(rollup["stop_reason"]["stopped_by_guard"])
        self.assertEqual(
            rollup["failed_attempts"][0]["manifest_path"],
            str(failed_manifest_path),
        )
        self.assertEqual(
            rollup["manual_recoveries"][0]["manifest_path"],
            str(promotion_manifest_path),
        )
        self.assertIn("Manual recovery: #102 Recover issue integration", markdown)
        self.assertIn("Checkpoint: `stopped_by_guard`", markdown)

    def test_operator_rollup_summarizes_local_integration_commit_failure(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=234,
                title="Local integration failure",
            )
            commit_log = (
                loop.config.log_root
                / "issue-234-local-integration-failed"
                / "integration-git-commit.log"
            )
            child_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="issue-234-local-integration-failed",
                run_kind="implementation",
                status="failed",
                issue=issue,
                qa_results=[
                    {
                        "name": "Ralph loop Unit test",
                        "command": ["make", "unit-test"],
                        "cwd": str(tmp_path / "repo" / "tools" / "ralph-loop"),
                        "log_path": str(
                            loop.config.log_root
                            / "issue-234-local-integration-failed"
                            / "ralph-loop-unit-test.log"
                        ),
                        "status": "passed",
                    }
                ],
                failure={
                    "message": "Command failed (1): git commit -m Local integration",
                    "log_path": str(commit_log),
                },
            )
            ralph.write_command_log(
                commit_log,
                ["git", "commit", "-m", "Ralph Local integration for issue 234"],
                tmp_path / "repo" / "tools" / "ralph-loop",
                "",
                (
                    "Ralph loop Unit test failed during the root Commit check.\n"
                    "tools/ralph-loop tests/unit/test_ralph.py::test_rollup FAILED\n"
                ),
                1,
            )
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=1,
            )
            manifest.record_checkpoint(
                "issue_failed",
                message="Issue #234 failed.",
                child_manifest_path=child_manifest_path,
                issue=issue,
                status="failed",
                recovery_guidance="Inspect issue #234 before rerunning.",
            )

            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            markdown = (run_dir / ralph.OPERATOR_ROLLUP_MARKDOWN_NAME).read_text(
                encoding="utf-8"
            )

        summary = rollup["issues"]["failed"][0]["failure_summary"]
        self.assertEqual(summary["failure_type"], "issue_failed")
        self.assertEqual(summary["phase"], "Local integration commit")
        self.assertEqual(
            summary["command_text"],
            "git commit -m 'Ralph Local integration for issue 234'",
        )
        self.assertEqual(summary["exit_code"], 1)
        self.assertEqual(summary["primary_log_path"], str(commit_log))
        self.assertIn("Ralph loop Unit test failed", summary["excerpt"])
        self.assertIn("Failure summary", markdown)
        self.assertIn("Local integration commit", markdown)
        self.assertIn("Ralph loop Unit test failed", markdown)

    def test_operator_rollup_summarizes_formatter_recovery_commit_check_failure(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=242,
                title="Formatter recovery failure",
            )
            commit_check_log = (
                loop.config.log_root
                / "issue-242-formatter-recovery-failed"
                / "formatter-recovery-commit-check-1-gas-market-knowledge-base-commit-check.log"
            )
            child_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="issue-242-formatter-recovery-failed",
                run_kind="implementation",
                status="failed",
                issue=issue,
                qa_results=[
                    {
                        "name": "gas-market-knowledge-base Commit check",
                        "command": ["make", "run-prek"],
                        "cwd": str(
                            tmp_path / "repo" / "tools" / "gas-market-knowledge-base"
                        ),
                        "log_path": str(commit_check_log),
                        "status": "failed",
                    }
                ],
                failure={
                    "message": (
                        "Formatter-rewrite recovery failure: Commit check failed "
                        "during formatter recovery"
                    ),
                    "type": ralph.FORMATTER_REWRITE_RECOVERY_FAILURE_TYPE,
                    "log_path": str(commit_check_log),
                    "commit_check_log_paths": [str(commit_check_log)],
                },
            )
            ralph.write_command_log(
                commit_check_log,
                ["make", "run-prek"],
                tmp_path / "repo" / "tools" / "gas-market-knowledge-base",
                "",
                (
                    "check-added-large-files...................................Failed\n"
                    "generated/silver/aemo-gas-statement-1.md (624 KB) exceeds 500 KB\n"
                    "generated/silver/aemo-gas-statement-2.md (612 KB) exceeds 500 KB\n"
                    "generated/silver/aemo-gas-statement-3.md (601 KB) exceeds 500 KB\n"
                    "generated/silver/aemo-gas-statement-4.md (599 KB) exceeds 500 KB\n"
                    "generated/silver/aemo-gas-statement-5.md (588 KB) exceeds 500 KB\n"
                    "generated/silver/aemo-gas-statement-6.md (577 KB) exceeds 500 KB\n"
                ),
                1,
            )
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=1,
            )
            manifest.record_checkpoint(
                "issue_failed",
                message="Issue #242 failed.",
                child_manifest_path=child_manifest_path,
                issue=issue,
                status="failed",
                recovery_guidance="Inspect issue #242 before rerunning.",
            )

            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            markdown = (run_dir / ralph.OPERATOR_ROLLUP_MARKDOWN_NAME).read_text(
                encoding="utf-8"
            )

        summary = rollup["issues"]["failed"][0]["failure_summary"]
        self.assertEqual(
            summary["failure_type"],
            ralph.FORMATTER_REWRITE_RECOVERY_FAILURE_TYPE,
        )
        self.assertEqual(summary["test_lane"], "gas-market-knowledge-base Commit check")
        self.assertEqual(summary["phase"], "formatter recovery Commit check")
        self.assertEqual(summary["command"], ["make", "run-prek"])
        self.assertEqual(summary["exit_code"], 1)
        self.assertEqual(summary["primary_log_path"], str(commit_check_log))
        self.assertIn("check-added-large-files", summary["excerpt"])
        self.assertIn("generated/silver/aemo-gas-statement-6.md", summary["excerpt"])
        self.assertIn("gas-market-knowledge-base Commit check", markdown)
        self.assertIn("check-added-large-files", markdown)

    def test_operator_rollup_summarizes_failed_promotion_commit_check(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, drain=True, delivery_mode=ralph.GITFLOW_MODE
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            promotion_log = (
                loop.config.log_root
                / "promote-dev-to-main-failed"
                / "promotion-qa-1-ralph-loop-commit-check.log"
            )
            child_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="promote-dev-to-main-failed",
                run_kind="promotion",
                status="failed",
                qa_results=[
                    {
                        "name": "Ralph loop Commit check",
                        "command": ["make", "run-prek"],
                        "cwd": str(tmp_path / "repo" / "tools" / "ralph-loop"),
                        "log_path": str(promotion_log),
                        "status": "failed",
                    }
                ],
                failure={
                    "message": "Command failed (1): make run-prek",
                    "log_path": str(promotion_log),
                },
            )
            ralph.write_command_log(
                promotion_log,
                ["make", "run-prek"],
                tmp_path / "repo" / "tools" / "ralph-loop",
                "",
                "zuban failed on Promotion-only type checks\n",
                1,
            )
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=1,
            )
            manifest.record_checkpoint(
                "promotion_failed",
                message="Promotion failed.",
                child_manifest_path=child_manifest_path,
                status="failed",
                recovery_guidance="Inspect the failed Promotion.",
            )

            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            markdown = (run_dir / ralph.OPERATOR_ROLLUP_MARKDOWN_NAME).read_text(
                encoding="utf-8"
            )

        summary = rollup["promotions"][0]["failure_summary"]
        self.assertEqual(summary["failure_type"], "qa_failed")
        self.assertEqual(summary["checkpoint"], "promotion_failed")
        self.assertEqual(summary["test_lane"], "Ralph loop Commit check")
        self.assertEqual(summary["phase"], "Promotion QA")
        self.assertEqual(summary["command"], ["make", "run-prek"])
        self.assertEqual(summary["exit_code"], 1)
        self.assertEqual(summary["primary_log_path"], str(promotion_log))
        self.assertIn("zuban failed", summary["excerpt"])
        self.assertIn("Ralph loop Commit check", markdown)
        self.assertIn("zuban failed", markdown)

    def test_operator_rollup_failure_summary_handles_bad_manifest_and_missing_log(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            missing_manifest_issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=301,
                title="Missing manifest",
            )
            malformed_manifest_issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=302,
                title="Malformed manifest",
            )
            missing_log_issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=303,
                title="Missing log",
            )
            missing_manifest_path = (
                loop.config.log_root / "issue-301-missing" / ralph.MANIFEST_NAME
            )
            malformed_manifest_path = (
                loop.config.log_root / "issue-302-malformed" / ralph.MANIFEST_NAME
            )
            malformed_manifest_path.parent.mkdir(parents=True, exist_ok=True)
            malformed_manifest_path.write_text("{not-json", encoding="utf-8")
            missing_log_path = (
                loop.config.log_root / "issue-303-missing-log" / "missing.log"
            )
            child_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="issue-303-missing-log",
                run_kind="implementation",
                status="failed",
                issue=missing_log_issue,
                failure={
                    "message": "Command failed (1): make run-prek",
                    "log_path": str(missing_log_path),
                },
            )
            comment_path = child_manifest_path.parent / "issue-303-comment.md"
            comment_path.write_text(
                "Agent issue loop failed: Commit check log vanished.\n",
                encoding="utf-8",
            )
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=1,
            )
            manifest.record_checkpoint(
                "issue_failed",
                message="Issue #301 failed.",
                child_manifest_path=missing_manifest_path,
                issue=missing_manifest_issue,
                status="failed",
            )
            manifest.record_checkpoint(
                "issue_failed",
                message="Issue #302 failed.",
                child_manifest_path=malformed_manifest_path,
                issue=malformed_manifest_issue,
                status="failed",
            )
            manifest.record_checkpoint(
                "issue_failed",
                message="Issue #303 failed.",
                child_manifest_path=child_manifest_path,
                issue=missing_log_issue,
                status="failed",
            )

            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            markdown = (run_dir / ralph.OPERATOR_ROLLUP_MARKDOWN_NAME).read_text(
                encoding="utf-8"
            )

        summaries = {
            entry["issue"]["number"]: entry["failure_summary"]
            for entry in rollup["issues"]["failed"]
        }
        self.assertEqual(summaries[301]["failure_type"], "manifest_missing")
        self.assertEqual(summaries[302]["failure_type"], "manifest_invalid")
        self.assertEqual(summaries[303]["log_read_status"], "missing")
        self.assertEqual(summaries[303]["excerpt_source"], "failure_comment")
        self.assertIn("Commit check log vanished", summaries[303]["excerpt"])
        self.assertIn("manifest_missing", markdown)
        self.assertIn("manifest_invalid", markdown)
        self.assertIn("Commit check log vanished", markdown)

    def test_operator_status_reports_compact_issue_boundary_state(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=42,
                title="Boundary work",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            child_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="issue-42-status-test",
                run_kind="implementation",
                status="succeeded",
                issue=issue,
            )
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=3,
            )
            manifest.record_queue(operator_snapshot(integrated=[issue]))
            manifest.record_checkpoint(
                "issue_succeeded",
                message="Issue #42 completed.",
                child_manifest_path=child_manifest_path,
                issue=issue,
            )
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_operator_run_status(str(run_dir), runner)

        text = output.getvalue()
        self.assertIn("Ralph Operator run status", text)
        self.assertIn(f"Operator run directory: {run_dir}", text)
        self.assertIn("Last checkpoint: issue_succeeded: Issue #42 completed.", text)
        self.assertIn(
            "Queue: ready=0, integrated=1, reviewing=0, running=0, failed=0", text
        )
        self.assertNotIn("Active child:", text)
        self.assertIn(f"- implementation #42 succeeded: {child_manifest_path}", text)
        self.assertIn("Rollup artifacts:", text)
        self.assertIn(str(run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME), text)
        self.assertIn("Recommended next action:", text)

    def test_operator_status_reports_active_issue_child_heartbeat(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=250,
                title="Surface active child run heartbeat",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            child_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="issue-250-active-child",
                run_kind="implementation",
                status="running",
                stage="codex_attempt_running",
                started_at="2026-05-21T00:00:00Z",
                updated_at="2026-05-21T00:05:00Z",
                events=[
                    {
                        "timestamp": "2026-05-21T00:05:00Z",
                        "stage": "codex_attempt_running",
                        "status": "running",
                    }
                ],
                issue=issue,
            )
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=3,
            )
            manifest.record_cycle(1)
            manifest.record_queue(operator_snapshot(ready=[issue]))
            manifest.record_current_issue(issue)
            manifest.record_active_child_manifest(child_manifest_path)
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_operator_run_status(str(run_dir), runner)

            manifest_data = json.loads(
                (run_dir / ralph.OPERATOR_MANIFEST_NAME).read_text(encoding="utf-8")
            )

        text = output.getvalue()
        self.assertNotEqual(
            (manifest_data.get("last_checkpoint") or {}).get("checkpoint"),
            "before_promotion",
        )
        self.assertIn(
            "Current: issue #250 Surface active child run heartbeat",
            text,
        )
        self.assertIn("Active child:", text)
        self.assertIn("Run: implementation running / codex_attempt_running", text)
        self.assertIn(f"Run directory: {child_manifest_path.parent}", text)
        self.assertIn(f"Manifest: {child_manifest_path}", text)
        self.assertIn("Elapsed:", text)
        self.assertIn(
            "Last child checkpoint: codex_attempt_running at 2026-05-21T00:05:00Z",
            text,
        )
        self.assertIn("Last child heartbeat: 2026-05-21T00:05:00Z", text)
        self.assertIn(
            "Queue: ready=1, integrated=0, reviewing=0, running=0, failed=0",
            text,
        )
        self.assertIn(f"- implementation #250 running: {child_manifest_path}", text)
        self.assertNotIn("codex-implementation", text)

    def test_operator_status_reports_active_promotion_child_phase(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            child_manifest_path = write_child_manifest(
                loop.config.log_root,
                name="promote-active-child",
                run_kind="promotion",
                status="running",
                stage="fetching_branches",
                started_at="2026-05-21T01:00:00Z",
                updated_at="2026-05-21T01:04:00Z",
                events=[
                    {
                        "timestamp": "2026-05-21T01:04:00Z",
                        "stage": "fetching_branches",
                        "status": "running",
                    }
                ],
                promotion_commit=None,
            )
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=3,
            )
            manifest.record_current_promotion(
                source_branch=ralph.DEFAULT_GITFLOW_BRANCH,
                target_branch=ralph.DEFAULT_TRUNK_BRANCH,
            )
            manifest.record_active_child_manifest(child_manifest_path)
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_operator_run_status(str(run_dir), runner)

        text = output.getvalue()
        self.assertIn("Current: Promotion dev -> main", text)
        self.assertIn("Active child:", text)
        self.assertIn("Run: promotion running / fetching_branches", text)
        self.assertIn(f"Run directory: {child_manifest_path.parent}", text)
        self.assertIn(f"Manifest: {child_manifest_path}", text)
        self.assertIn(
            "Last child checkpoint: fetching_branches at 2026-05-21T01:04:00Z",
            text,
        )
        self.assertIn("Last child heartbeat: 2026-05-21T01:04:00Z", text)

    def test_operator_status_reports_stopped_run_without_active_child(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            issue = make_issue(
                {ralph.READY_LABEL},
                IMPLEMENTATION_BODY,
                number=77,
                title="Still queued",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=1,
            )
            manifest.record_queue(operator_snapshot(ready=[issue]))
            manifest.clear_current()
            manifest.record_checkpoint(
                "stopped_by_guard",
                message="Reached --max-cycles 1.",
                status="failed",
                recovery_guidance="Review progress before raising --max-cycles.",
            )
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_operator_run_status(str(run_dir), runner)

        text = output.getvalue()
        self.assertIn(
            "Last checkpoint: stopped_by_guard: Reached --max-cycles 1.",
            text,
        )
        self.assertIn("Current: none", text)
        self.assertNotIn("Active child:", text)
        self.assertIn(
            "Queue: ready=1, integrated=0, reviewing=0, running=0, failed=0",
            text,
        )
        self.assertIn("Review progress before raising --max-cycles.", text)

    def test_operator_status_and_rollup_report_requeue_eligible_failed_issue(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            child_run_dir = write_failed_pre_push_requeue_manifest(tmp_path)
            child_manifest_path = child_run_dir / ralph.MANIFEST_NAME
            issue = make_issue(
                {ralph.AGENT_FAILED_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=234,
                title="Fix Marimo dashboard",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            manifest = ralph.OperatorRunManifest.start(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=3,
            )
            manifest.record_child_run(child_manifest_path)
            manifest.record_queue(operator_snapshot(failed=[issue]))
            manifest.record_checkpoint(
                "queue_blocked",
                message="agent-failed issue(s) remain and need operator recovery.",
                status="failed",
                recovery_guidance="Inspect failed issues.",
            )
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_operator_run_status(str(run_dir), runner)

            rollup = json.loads(
                (run_dir / ralph.OPERATOR_ROLLUP_JSON_NAME).read_text(encoding="utf-8")
            )
            markdown = (run_dir / ralph.OPERATOR_ROLLUP_MARKDOWN_NAME).read_text(
                encoding="utf-8"
            )

        text = output.getvalue()
        self.assertIn("Requeue recovery:", text)
        self.assertIn("#234 Fix Marimo dashboard: eligible_pre_push_requeue", text)
        self.assertIn(
            f"python3 scripts/ralph.py --recover-run {child_run_dir} --dry-run",
            text,
        )
        self.assertIn("Do not start a competing Operator run", text)
        self.assertEqual(rollup["summary"]["pre_push_requeue_eligible"], 1)
        self.assertEqual(
            rollup["requeue_recovery"]["eligible_pre_push"][0]["issue"]["number"],
            234,
        )
        self.assertIn("## Requeue Recovery", markdown)
        self.assertIn("eligible_pre_push_requeue", markdown)

    def test_operator_requeue_recovery_classifies_non_requeue_failures(
        self,
    ) -> None:
        def child_source(
            issue_number: int,
            child_data: dict[str, Any],
        ) -> dict[str, Any]:
            return {
                "manifest_path": f"/logs/issue-{issue_number}/ralph-run.json",
                "manifest_read_status": "loaded",
                "manifest_error": None,
                "kind": "implementation",
                "status": child_data["status"],
                "stage": child_data["stage"],
                "issue": {
                    "number": issue_number,
                    "title": f"Issue {issue_number}",
                    "url": f"https://example.test/{issue_number}",
                },
                "data": child_data,
            }

        def failed_child(
            issue_number: int,
            *,
            qa_status: str = "passed",
            review_status: str = "passed",
            integration_commit: dict[str, str] | None = None,
            push_status: str | None = None,
            branch_sync_status: str = "not_started",
            failure_message: str = "Command failed",
        ) -> dict[str, Any]:
            pushes = {}
            if push_status is not None:
                pushes = {
                    "integration_target": {
                        "status": push_status,
                        "branch": ralph.DEFAULT_GITFLOW_BRANCH,
                        "commit": "abc1234",
                    }
                }
            return {
                "run_kind": "implementation",
                "status": "failed",
                "stage": "failed",
                "issue": {
                    "number": issue_number,
                    "title": f"Issue {issue_number}",
                    "url": f"https://example.test/{issue_number}",
                },
                "paths": {"run_dir": f"/logs/issue-{issue_number}"},
                "integration_commit": integration_commit,
                "pushes": pushes,
                "branch_sync": {"status": branch_sync_status},
                "qa_results": [{"status": qa_status}],
                "issue_completion_review": {"status": review_status},
                "failure": {"message": failure_message},
            }

        issue_numbers = [301, 302, 303, 304]
        final_queue = {
            "issues": {
                "failed": [
                    {
                        "number": number,
                        "title": f"Issue {number}",
                        "url": f"https://example.test/{number}",
                    }
                    for number in issue_numbers
                ]
            }
        }
        child_sources = [
            child_source(
                301,
                failed_child(
                    301,
                    integration_commit={
                        "sha": "abc1234",
                        "branch": ralph.DEFAULT_GITFLOW_BRANCH,
                    },
                    push_status="pushed",
                ),
            ),
            child_source(
                302,
                failed_child(302, branch_sync_status="failed"),
            ),
            child_source(
                303,
                failed_child(
                    303,
                    qa_status="not_started",
                    review_status="not_started",
                    failure_message="Missing required issue section(s): QA plan",
                ),
            ),
            child_source(
                304,
                failed_child(304, qa_status="failed"),
            ),
        ]

        recovery = ralph.operator_rollup_requeue_recovery(final_queue, child_sources)

        classifications = {
            entry["issue"]["number"]: entry["classification"]
            for entry in recovery["failed_issues"]
        }
        self.assertEqual(classifications[301], "post_push_metadata_recovery")
        self.assertEqual(classifications[302], "manual_gitflow_recovery")
        self.assertEqual(classifications[303], "malformed_issue_contract")
        self.assertEqual(classifications[304], "unrecoverable_implementation_failure")
        guidance = " ".join(entry["guidance"] for entry in recovery["failed_issues"])
        self.assertIn("post-push metadata recovery", guidance)
        self.assertIn("manual Gitflow recovery", guidance)
        self.assertIn("issue contract is malformed", guidance)
        self.assertIn("did not pass the gates needed for requeue", guidance)

    def test_operator_status_marks_stopped_detached_manifest_as_stale(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            ralph.OperatorRunManifest.for_detached_launch(
                run_dir=run_dir,
                config=loop.config,
                max_cycles=3,
                command=["python3", "scripts/ralph.py", "--drain-promote-all"],
                stdout_log=run_dir / "operator-stdout.log",
                stderr_log=run_dir / "operator-stderr.log",
                pid=99_999_999,
            )
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.inspect_operator_run_status(str(run_dir), runner)

        text = output.getvalue()
        self.assertIn("Detached run:", text)
        self.assertIn("pid=99999999 stopped", text)
        self.assertIn("Detached status may be stale", text)
        self.assertIn("manifest still says running", text)

    def test_operator_claims_requeued_ready_issue_through_normal_scan(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            issue = make_issue(
                {ralph.READY_LABEL, ralph.DELIVERY_GITFLOW_LABEL},
                IMPLEMENTATION_BODY,
                number=234,
                title="Fix Marimo dashboard",
            )
            run_dir = tmp_path / "repo" / ".ralph" / "operator-runs" / "operator-test"
            operator = ScriptedOperatorRun(
                make_loop(tmp_path, runner, drain=True).config,
                runner,
                run_dir=run_dir,
                max_cycles=1,
                snapshots=[
                    operator_snapshot(ready=[issue]),
                    operator_snapshot(),
                ],
            )

            operator.run()

        self.assertEqual(operator.issue_runs, 1)
        self.assertEqual(operator.issue_commits[234], "local-integration-234-1")

    def test_detached_operator_launch_prints_status_command_without_waiting(
        self,
    ) -> None:
        runner = FakeRunner(
            command_outputs={
                ("git", "rev-parse", "--show-toplevel"): [],
                ("git", "config", "--get", "remote.origin.url"): [
                    "git@github.com:example/repo.git\n"
                ],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp) / "repo"
            repo_root.mkdir()
            runner.command_outputs[("git", "rev-parse", "--show-toplevel")] = [
                f"{repo_root}\n"
            ]
            parsed = ralph.parse_args(
                [
                    "--drain-promote-all",
                    "--detach",
                    "--max-cycles",
                    "3",
                    "--max-codex-attempts",
                    "7",
                    "--exploratory-concurrency",
                    "4",
                    "--skip-post-promotion-followups",
                    "--allow-full-access-implementation",
                ]
            )
            process = type("DummyProcess", (), {"pid": 321})()
            output = io.StringIO()

            with patch.object(ralph.subprocess, "Popen", return_value=process) as popen:
                with redirect_stdout(output):
                    ralph.launch_detached_operator_run(parsed, runner)

            manifest_path = next(
                repo_root.glob(".ralph/operator-runs/operator-*/operator-run.json")
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        text = output.getvalue()
        child_command = popen.call_args.args[0]
        self.assertIn("Operator run directory:", text)
        self.assertIn(
            "Status command: python3 scripts/ralph.py --operator-run-status", text
        )
        self.assertIn("--operator-run-dir", child_command)
        self.assertIn("--max-cycles", child_command)
        self.assertIn("3", child_command)
        self.assertIn("--max-codex-attempts", child_command)
        self.assertIn("7", child_command)
        self.assertIn("--exploratory-concurrency", child_command)
        self.assertIn("4", child_command)
        self.assertIn("--skip-post-promotion-followups", child_command)
        self.assertIn("--allow-full-access-implementation", child_command)
        self.assertEqual(manifest["last_checkpoint"]["checkpoint"], "detached_launched")
        self.assertEqual(manifest["detached"]["pid"], 321)
        self.assertEqual(manifest["configuration"]["max_codex_attempts"], 7)
        self.assertEqual(manifest["configuration"]["exploratory_concurrency"], 4)

    def test_operator_docs_include_codex_safe_command_strings(self) -> None:
        repo_root = REPO_ROOT
        docs = [
            repo_root / "OPERATOR.md",
            repo_root / "docs" / "agents" / "ralph-loop.md",
        ]

        for doc_path in docs:
            with self.subTest(path=doc_path):
                text = doc_path.read_text(encoding="utf-8")
                self.assertIn(
                    "python3 scripts/ralph.py --drain-promote-all --detach",
                    text,
                )
                self.assertIn(
                    "python3 scripts/ralph.py --operator-run-status latest",
                    text,
                )

    def test_recover_run_refuses_when_commit_not_reachable_from_target(self) -> None:
        ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "abc1234",
            "origin/main",
        )
        runner = FakeRunner(fail_commands={ancestor_command: 1})
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_recovery_manifest(tmp_path)
            loop = make_loop(tmp_path, runner)

            with self.assertRaises(ralph.RalphError) as caught:
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

        self.assertIn(
            "not reachable from expected Integration target", str(caught.exception)
        )
        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "fetch", "origin", "main"), commands)
        self.assertNotIn(
            (
                "gh",
                "issue",
                "comment",
                "42",
                "-R",
                "example/repo",
                "--body-file",
            ),
            [command[:7] for command in commands],
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )

    def test_recover_run_reconciles_trunk_comment_labels_and_closure(self) -> None:
        issue_view_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_state_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--json",
            "state",
        )
        runner = FakeRunner(
            command_outputs={
                issue_view_command: [
                    issue_view_output(labels=[ralph.AGENT_RUNNING_LABEL])
                ],
                issue_state_command: [json.dumps({"state": "OPEN"})],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            review_package_path = (
                tmp_path / "logs" / "issue-42-20260504T010203Z" / "review-package.html"
            )
            run_dir = write_recovery_manifest(
                tmp_path,
                review_package={
                    "status": "passed",
                    "validation_status": "passed",
                    "html_path": str(review_package_path),
                    "summary": {
                        "title": "Review package for issue #42",
                        "changed_file_count": 1,
                        "qa_result_count": 1,
                    },
                },
            )
            loop = make_loop(tmp_path, runner)
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

            comment_path = run_dir / "issue-42-comment.md"
            comment = comment_path.read_text(encoding="utf-8")
            manifest = json.loads(
                (run_dir / "ralph-run.json").read_text(encoding="utf-8")
            )

        commands = [call.args for call in runner.calls]
        self.assertIn("Ralph trunk integration completed.", comment)
        self.assertIn("Commit: `abc1234`", comment)
        self.assertIn("## Review package", comment)
        self.assertIn(f"- HTML: `{review_package_path}`", comment)
        self.assertIn(
            "- Summary: Review package for issue #42; 1 changed file(s); 1 QA result(s)",
            comment,
        )
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "42",
                "-R",
                "example/repo",
                "--add-label",
                "agent-merged",
                "--remove-label",
                "agent-running",
                "--remove-label",
                "agent-failed",
                "--remove-label",
                "agent-integrated",
                "--remove-label",
                "ready-for-agent",
            ),
            commands,
        )
        self.assertIn(
            (
                "gh",
                "issue",
                "close",
                "42",
                "-R",
                "example/repo",
                "--reason",
                "completed",
            ),
            commands,
        )
        self.assertEqual(manifest["github_metadata"]["status"], "closed")
        self.assertIn(
            "Recovered issue #42 trunk metadata for abc1234.", output.getvalue()
        )

    def test_recover_run_reconciles_gitflow_without_closing_issue(self) -> None:
        issue_view_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_state_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--json",
            "state",
        )
        runner = FakeRunner(
            command_outputs={
                issue_view_command: [
                    issue_view_output(labels=[ralph.AGENT_RUNNING_LABEL])
                ],
                issue_state_command: [json.dumps({"state": "OPEN"})],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_recovery_manifest(
                tmp_path,
                delivery_mode=ralph.GITFLOW_MODE,
                target_branch=ralph.DEFAULT_GITFLOW_BRANCH,
            )
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

            manifest = json.loads(
                (run_dir / "ralph-run.json").read_text(encoding="utf-8")
            )

        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "fetch", "origin", "dev"), commands)
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "42",
                "-R",
                "example/repo",
                "--add-label",
                "agent-integrated",
                "--remove-label",
                "agent-running",
                "--remove-label",
                "agent-failed",
                "--remove-label",
                "agent-merged",
                "--remove-label",
                "ready-for-agent",
            ),
            commands,
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )
        self.assertEqual(manifest["github_metadata"]["status"], "marked_integrated")
        self.assertIn(
            "Recovered issue #42 Gitflow metadata for abc1234.", output.getvalue()
        )


class RalphExploratoryAcceptanceApplyTests(unittest.TestCase):
    def _decision_file(
        self,
        tmp_path: Path,
        decisions: list[dict[str, Any]],
    ) -> Path:
        decision_file = tmp_path / "repo" / "decisions.json"
        decision_file.write_text(
            json.dumps({"decisions": decisions}),
            encoding="utf-8",
        )
        return decision_file

    def _reviewing_issue_output(self, *, labels: list[str] | None = None) -> str:
        return json.dumps(
            issue_payload(
                42,
                labels
                or [ralph.AGENT_REVIEWING_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL],
                EXPLORATORY_IMPLEMENTATION_BODY,
            )
        )

    def _runner_for_reviewing_issue(
        self,
        *,
        branch: str = "agent/exploratory/issue-42-implement-thing",
        commit: str = "abc1234",
        labels: list[str] | None = None,
        extra_outputs: dict[tuple[str, ...], list[str]] | None = None,
        **runner_kwargs: Any,
    ) -> FakeRunner:
        command_outputs = {
            issue_state_command(42): [json.dumps({"state": "OPEN"})],
            issue_view_command(42): [self._reviewing_issue_output(labels=labels)],
            issue_comments_command(42): [
                exploratory_handoff_comments_output(branch=branch, commit=commit)
            ],
        }
        if extra_outputs is not None:
            command_outputs.update(extra_outputs)
        return FakeRunner(command_outputs=command_outputs, **runner_kwargs)

    def _pause_acceptance_conflict(
        self,
        tmp_path: Path,
        *,
        handoff_branch: str = "agent/exploratory/issue-42-implement-thing",
    ) -> tuple[ralph.RunManifest, FakeRunner]:
        merge_command = (
            "git",
            "merge",
            "--no-ff",
            f"origin/{handoff_branch}",
            "-m",
            "Accept Exploratory issue #42: Issue 42",
        )
        runner = self._runner_for_reviewing_issue(
            branch=handoff_branch,
            diff_outputs=["docs/repository/architecture-exploration.md\n"],
            rev_parse_outputs=["abc1234\n", "source-sha\n"],
            fail_commands={merge_command},
        )
        loop = make_loop(tmp_path, runner, source_branch=ralph.DEFAULT_GITFLOW_BRANCH)
        decision_file = self._decision_file(
            tmp_path,
            [{"issue_number": 42, "decision": "accept", "reason": "Approved."}],
        )

        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            manifest = loop._apply_exploratory_acceptance_decisions(decision_file)
        return manifest, runner

    def test_accept_merges_runs_qa_pushes_then_updates_metadata(self) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        runner = self._runner_for_reviewing_issue(
            branch=handoff_branch,
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=[
                "abc1234\n",
                "source-sha\n",
                "def5678\n",
                "def5678\n",
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path, runner, source_branch=ralph.DEFAULT_GITFLOW_BRANCH
            )
            decision_file = self._decision_file(
                tmp_path,
                [{"issue_number": 42, "decision": "accept", "reason": "Approved."}],
            )

            with redirect_stdout(io.StringIO()):
                manifest = loop._apply_exploratory_acceptance_decisions(decision_file)

            comment_path = next(
                tmp_path.glob("logs/exploratory-acceptance-*/issue-42-comment.md")
            )
            comment = comment_path.read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        push_command = ("git", "push", "origin", "HEAD:dev")
        push_index = commands.index(push_command)
        mutation_indexes = [
            index
            for index, command in enumerate(commands)
            if command[:3]
            in {
                ("gh", "issue", "comment"),
                ("gh", "issue", "edit"),
            }
        ]
        self.assertTrue(mutation_indexes)
        self.assertTrue(all(index > push_index for index in mutation_indexes))
        self.assertIn(
            (
                "git",
                "worktree",
                "add",
                "--detach",
                manifest.data["paths"]["acceptance_worktree"],
                "origin/dev",
            ),
            commands,
        )
        self.assertIn(
            (
                "git",
                "merge",
                "--no-ff",
                f"origin/{handoff_branch}",
                "-m",
                "Accept Exploratory issue #42: Issue 42",
            ),
            commands,
        )
        self.assertIn(
            ("make", "run-prek"),
            commands,
        )
        self.assertIn(ralph.EXPLORATORY_ACCEPTANCE_COMMENT_TITLE, comment)
        self.assertIn("Commit: `def5678`", comment)
        self.assertIn(f"Exploratory branch: `{handoff_branch}`", comment)
        self.assertIn("Handoff commit: `abc1234`", comment)
        self.assertEqual(manifest.data["status"], "succeeded")
        self.assertEqual(manifest.data["decisions"][0]["status"], "metadata_applied")

    def test_accept_merge_conflict_pauses_with_artifacts_without_mutation(self) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest, runner = self._pause_acceptance_conflict(
                tmp_path,
                handoff_branch=handoff_branch,
            )
            run_dir = Path(manifest.data["paths"]["run_dir"])
            decisions = json.loads(
                (
                    run_dir / ralph.EXPLORATORY_ACCEPTANCE_DECISIONS_ARTIFACT_NAME
                ).read_text(encoding="utf-8")
            )
            conflicts = json.loads(
                (
                    run_dir / ralph.EXPLORATORY_ACCEPTANCE_CONFLICTS_ARTIFACT_NAME
                ).read_text(encoding="utf-8")
            )
            prompt = (
                run_dir / ralph.EXPLORATORY_ACCEPTANCE_CODEX_PROMPT_NAME
            ).read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        self.assertEqual(
            manifest.data["status"],
            ralph.EXPLORATORY_ACCEPTANCE_CONFLICT_STATUS,
        )
        self.assertEqual(
            manifest.data["acceptance_conflict"]["conflicted_files"],
            ["docs/repository/architecture-exploration.md"],
        )
        self.assertEqual(
            decisions["status"], ralph.EXPLORATORY_ACCEPTANCE_CONFLICT_STATUS
        )
        self.assertEqual(decisions["decisions"][0]["decision"], "accept")
        self.assertEqual(decisions["decisions"][0]["status"], "acceptance_conflict")
        self.assertEqual(conflicts["current_branch"], handoff_branch)
        self.assertIn(
            "codex-resolution-prompt.md",
            conflicts["artifacts"]["codex_resolution_prompt"],
        )
        self.assertIn("Resolve only the paused acceptance worktree", prompt)
        self.assertIn("Preserve accepted issue intent", prompt)
        self.assertIn("--continue-exploratory-acceptance", prompt)
        self.assertFalse(any(command[:2] == ("git", "push") for command in commands))
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "remove") for command in commands)
        )

    def test_continue_acceptance_conflict_runs_qa_pushes_then_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paused_manifest, _pause_runner = self._pause_acceptance_conflict(tmp_path)
            run_dir = Path(paused_manifest.data["paths"]["run_dir"])
            acceptance_path = Path(paused_manifest.data["paths"]["acceptance_worktree"])
            acceptance_path.mkdir(parents=True)
            runner = self._runner_for_reviewing_issue(
                diff_outputs=["", "scripts/ralph.py\n"],
                status_outputs=["", ""],
                rev_parse_outputs=["abc1234\n", "source-sha\n", "resolved-sha\n"],
            )
            loop = make_loop(tmp_path, runner)

            with redirect_stdout(io.StringIO()):
                manifest = loop._continue_exploratory_acceptance(run_dir)

            comment = next(run_dir.glob("issue-42-comment.md")).read_text(
                encoding="utf-8"
            )

        commands = [call.args for call in runner.calls]
        push_command = ("git", "push", "origin", "HEAD:dev")
        push_index = commands.index(push_command)
        qa_indexes = [
            index
            for index, command in enumerate(commands)
            if command
            in {
                ("prek", "run", "-a"),
                ("make", "run-prek"),
            }
        ]
        mutation_indexes = [
            index
            for index, command in enumerate(commands)
            if command[:3]
            in {
                ("gh", "issue", "comment"),
                ("gh", "issue", "edit"),
            }
        ]
        self.assertTrue(qa_indexes)
        self.assertTrue(all(index < push_index for index in qa_indexes))
        self.assertTrue(mutation_indexes)
        self.assertTrue(all(index > push_index for index in mutation_indexes))
        self.assertEqual(manifest.data["status"], "succeeded")
        self.assertEqual(manifest.data["integration_commit"]["sha"], "resolved-sha")
        self.assertIn(ralph.EXPLORATORY_ACCEPTANCE_COMMENT_TITLE, comment)
        self.assertIn("Commit: `resolved-sha`", comment)
        self.assertEqual(manifest.data["decisions"][0]["status"], "metadata_applied")

    def test_continue_multi_issue_acceptance_conflict_preserves_issue_commits(
        self,
    ) -> None:
        source_commit = "a6c6673000000000000000000000000000000000"
        handoff_123 = "1de18a5000000000000000000000000000000000"
        handoff_153 = "b6ff18e000000000000000000000000000000000"
        handoff_157 = "f1f16fb000000000000000000000000000000000"
        acceptance_123 = "189fb1017d9fca4d7b4aef1bc27b589599a60cff"
        acceptance_153 = "3f140d7b2cf749ad4c5c67c442736f1b4a5086b0"
        acceptance_157 = "9c12f1258cf680849829a91fab0b94c8eeed886a"
        targets = [
            (123, "agent/exploratory/issue-123-marimo-images", handoff_123),
            (153, "agent/exploratory/issue-153-aws-deploy", handoff_153),
            (157, "agent/exploratory/issue-157-caddy-portfolio", handoff_157),
        ]

        def reviewing_issue_outputs() -> dict[tuple[str, ...], list[str]]:
            return {
                command: outputs
                for issue_number, branch, handoff_commit in targets
                for command, outputs in {
                    issue_state_command(issue_number): [json.dumps({"state": "OPEN"})],
                    issue_view_command(issue_number): [
                        json.dumps(
                            issue_payload(
                                issue_number,
                                [
                                    ralph.AGENT_REVIEWING_LABEL,
                                    ralph.DELIVERY_EXPLORATORY_LABEL,
                                ],
                                EXPLORATORY_IMPLEMENTATION_BODY,
                            )
                        )
                    ],
                    issue_comments_command(issue_number): [
                        exploratory_handoff_comments_output(
                            branch=branch,
                            commit=handoff_commit,
                        )
                    ],
                }.items()
            }

        conflict_merge_command = (
            "git",
            "merge",
            "--no-ff",
            "origin/agent/exploratory/issue-157-caddy-portfolio",
            "-m",
            "Accept Exploratory issue #157: Issue 157",
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pause_runner = FakeRunner(
                diff_outputs=["docs/repository/architecture-exploration.md\n"],
                rev_parse_outputs=[
                    f"{handoff_123}\n",
                    f"{handoff_153}\n",
                    f"{handoff_157}\n",
                    f"{source_commit}\n",
                    f"{acceptance_123}\n",
                    f"{acceptance_153}\n",
                ],
                command_outputs=reviewing_issue_outputs(),
                fail_commands={conflict_merge_command},
            )
            loop = make_loop(
                tmp_path,
                pause_runner,
                source_branch=ralph.DEFAULT_GITFLOW_BRANCH,
            )
            decision_file = self._decision_file(
                tmp_path,
                [
                    {"issue_number": issue_number, "decision": "accept"}
                    for issue_number, _branch, _handoff_commit in targets
                ],
            )
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                paused_manifest = loop._apply_exploratory_acceptance_decisions(
                    decision_file
                )

            run_dir = Path(paused_manifest.data["paths"]["run_dir"])
            acceptance_path = Path(paused_manifest.data["paths"]["acceptance_worktree"])
            acceptance_path.mkdir(parents=True)
            continue_runner = FakeRunner(
                diff_outputs=["", "scripts/ralph.py\n"],
                status_outputs=["", ""],
                rev_parse_outputs=[
                    f"{handoff_123}\n",
                    f"{handoff_153}\n",
                    f"{handoff_157}\n",
                    f"{source_commit}\n",
                    f"{acceptance_157}\n",
                ],
                command_outputs={
                    **reviewing_issue_outputs(),
                    (
                        "git",
                        "rev-list",
                        "--first-parent",
                        "--reverse",
                        f"{source_commit}..{acceptance_157}",
                    ): [
                        "\n".join([acceptance_123, acceptance_153, acceptance_157])
                        + "\n"
                    ],
                },
                fail_commands={
                    (
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        handoff_153,
                        acceptance_123,
                    ): 1,
                    (
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        handoff_157,
                        acceptance_123,
                    ): 1,
                    (
                        "git",
                        "merge-base",
                        "--is-ancestor",
                        handoff_157,
                        acceptance_153,
                    ): 1,
                },
            )
            loop = make_loop(tmp_path, continue_runner)

            with redirect_stdout(io.StringIO()):
                manifest = loop._continue_exploratory_acceptance(run_dir)

            comments = {
                issue_number: (run_dir / f"issue-{issue_number}-comment.md").read_text(
                    encoding="utf-8"
                )
                for issue_number, _branch, _handoff_commit in targets
            }

        decisions = {
            int(entry["issue_number"]): entry for entry in manifest.data["decisions"]
        }
        self.assertIn(f"Commit: `{acceptance_123}`", comments[123])
        self.assertIn(f"Commit: `{acceptance_153}`", comments[153])
        self.assertIn(f"Commit: `{acceptance_157}`", comments[157])
        self.assertEqual(decisions[123]["acceptance_commit"], acceptance_123)
        self.assertEqual(decisions[153]["acceptance_commit"], acceptance_153)
        self.assertEqual(decisions[157]["acceptance_commit"], acceptance_157)
        self.assertEqual(manifest.data["integration_commit"]["sha"], acceptance_157)

    def test_continue_acceptance_conflict_refuses_dirty_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paused_manifest, _pause_runner = self._pause_acceptance_conflict(tmp_path)
            run_dir = Path(paused_manifest.data["paths"]["run_dir"])
            acceptance_path = Path(paused_manifest.data["paths"]["acceptance_worktree"])
            acceptance_path.mkdir(parents=True)
            runner = self._runner_for_reviewing_issue(
                diff_outputs=[""],
                status_outputs=[" M docs/repository/architecture-exploration.md\n"],
                rev_parse_outputs=["abc1234\n"],
            )
            loop = make_loop(tmp_path, runner)

            with self.assertRaises(ralph.IssueFailure) as caught:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._continue_exploratory_acceptance(run_dir)

        commands = [call.args for call in runner.calls]
        self.assertEqual(
            caught.exception.failure_type, "exploratory_acceptance_dirty_worktree"
        )
        self.assertIn(
            "git status --porcelain", caught.exception.recovery_guidance or ""
        )
        self.assertFalse(any(command[:2] == ("git", "push") for command in commands))
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )

    def test_continue_acceptance_conflict_refuses_missing_decision_artifact(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paused_manifest, _pause_runner = self._pause_acceptance_conflict(tmp_path)
            run_dir = Path(paused_manifest.data["paths"]["run_dir"])
            acceptance_path = Path(paused_manifest.data["paths"]["acceptance_worktree"])
            acceptance_path.mkdir(parents=True)
            (run_dir / ralph.EXPLORATORY_ACCEPTANCE_DECISIONS_ARTIFACT_NAME).unlink()
            runner = self._runner_for_reviewing_issue()
            loop = make_loop(tmp_path, runner)

            with self.assertRaises(ralph.IssueFailure) as caught:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._continue_exploratory_acceptance(run_dir)

        self.assertEqual(
            caught.exception.failure_type,
            "exploratory_acceptance_missing_decisions_artifact",
        )
        self.assertIn(
            "paused run directory is incomplete",
            str(caught.exception.recovery_guidance),
        )

    def test_continue_acceptance_conflict_refuses_stale_source_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paused_manifest, _pause_runner = self._pause_acceptance_conflict(tmp_path)
            run_dir = Path(paused_manifest.data["paths"]["run_dir"])
            acceptance_path = Path(paused_manifest.data["paths"]["acceptance_worktree"])
            acceptance_path.mkdir(parents=True)
            runner = self._runner_for_reviewing_issue(
                diff_outputs=[""],
                status_outputs=[""],
                rev_parse_outputs=["abc1234\n", "new-source-sha\n"],
            )
            loop = make_loop(tmp_path, runner)

            with self.assertRaises(ralph.IssueFailure) as caught:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._continue_exploratory_acceptance(run_dir)

        self.assertEqual(
            caught.exception.failure_type,
            "exploratory_acceptance_stale_source_branch",
        )
        self.assertIn("Do not push", caught.exception.recovery_guidance or "")

    def test_continue_acceptance_conflict_refuses_mismatched_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            paused_manifest, _pause_runner = self._pause_acceptance_conflict(tmp_path)
            run_dir = Path(paused_manifest.data["paths"]["run_dir"])
            acceptance_path = Path(paused_manifest.data["paths"]["acceptance_worktree"])
            acceptance_path.mkdir(parents=True)
            decisions_path = (
                run_dir / ralph.EXPLORATORY_ACCEPTANCE_DECISIONS_ARTIFACT_NAME
            )
            payload = json.loads(decisions_path.read_text(encoding="utf-8"))
            payload["decisions"][0]["decision"] = "reject"
            decisions_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            runner = self._runner_for_reviewing_issue()
            loop = make_loop(tmp_path, runner)

            with self.assertRaises(ralph.IssueFailure) as caught:
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._continue_exploratory_acceptance(run_dir)

        self.assertEqual(
            caught.exception.failure_type,
            "exploratory_acceptance_mismatched_decisions_artifact",
        )

    def test_accept_qa_failure_leaves_metadata_unchanged_before_push(self) -> None:
        runner = self._runner_for_reviewing_issue(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["abc1234\n", "source-sha\n", "def5678\n"],
            fail_commands={
                ("make", "run-prek"),
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            decision_file = self._decision_file(
                tmp_path,
                [{"issue_number": 42, "decision": "accept"}],
            )

            with self.assertRaises(ralph.IssueFailure):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._apply_exploratory_acceptance_decisions(decision_file)

            manifest = json.loads(
                next(
                    tmp_path.glob("logs/exploratory-acceptance-*/ralph-run.json")
                ).read_text(encoding="utf-8")
            )

        commands = [call.args for call in runner.calls]
        self.assertNotIn(("git", "push", "origin", "HEAD:dev"), commands)
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertIn(
            "No accepted issue metadata was changed",
            manifest["failure"]["recovery_guidance"],
        )

    def test_hold_comments_reason_without_push_or_label_change(self) -> None:
        runner = self._runner_for_reviewing_issue(
            rev_parse_outputs=["abc1234\n"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            decision_file = self._decision_file(
                tmp_path,
                [
                    {
                        "issue_number": 42,
                        "decision": "hold",
                        "reason": "Needs another product review.",
                    }
                ],
            )

            with redirect_stdout(io.StringIO()):
                loop._apply_exploratory_acceptance_decisions(decision_file)

            comment = next(
                tmp_path.glob("logs/exploratory-acceptance-*/issue-42-comment.md")
            ).read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        self.assertFalse(any(command[:2] == ("git", "push") for command in commands))
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "add") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertIn("Ralph exploratory acceptance held.", comment)
        self.assertIn("Needs another product review.", comment)
        self.assertIn("remains `agent-reviewing`", comment)

    def test_reject_comments_and_moves_issue_to_ready_for_human(self) -> None:
        runner = self._runner_for_reviewing_issue(
            rev_parse_outputs=["abc1234\n"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            decision_file = self._decision_file(
                tmp_path,
                [
                    {
                        "issue_number": 42,
                        "decision": "reject",
                        "reason": "The review branch changes the wrong workflow.",
                    }
                ],
            )

            with redirect_stdout(io.StringIO()):
                loop._apply_exploratory_acceptance_decisions(decision_file)

            comment = next(
                tmp_path.glob("logs/exploratory-acceptance-*/issue-42-comment.md")
            ).read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        self.assertFalse(any(command[:2] == ("git", "push") for command in commands))
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "42",
                "-R",
                "example/repo",
                "--add-label",
                "ready-for-human",
                "--remove-label",
                "agent-reviewing",
                "--remove-label",
                "agent-integrated",
                "--remove-label",
                "agent-running",
                "--remove-label",
                "agent-failed",
                "--remove-label",
                "agent-merged",
                "--remove-label",
                "ready-for-agent",
            ),
            commands,
        )
        command_text = " ".join(" ".join(command) for command in commands)
        self.assertNotIn("--add-label agent-integrated", command_text)
        self.assertIn("Ralph exploratory acceptance rejected.", comment)
        self.assertIn("wrong workflow", comment)

    def test_validation_requires_agent_reviewing_label_before_metadata_mutation(
        self,
    ) -> None:
        runner = self._runner_for_reviewing_issue(
            labels=[ralph.DELIVERY_EXPLORATORY_LABEL],
            rev_parse_outputs=[],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            decision_file = self._decision_file(
                tmp_path,
                [{"issue_number": 42, "decision": "accept"}],
            )

            with self.assertRaises(ralph.IssueFailure):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._apply_exploratory_acceptance_decisions(decision_file)

        commands = [call.args for call in runner.calls]
        self.assertFalse(any(command[:2] == ("git", "push") for command in commands))
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )


class CommandRunnerTests(unittest.TestCase):
    def test_command_runner_streams_log_and_heartbeat_while_command_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            log_path = tmp_path / "stream.log"
            runner = ralph.CommandRunner(dry_run=False, heartbeat_interval=0.05)
            command = [
                sys.executable,
                "-c",
                (
                    "import sys, time; "
                    "print('first line', flush=True); "
                    "time.sleep(0.5); "
                    "print('second line', flush=True); "
                    "print('error line', file=sys.stderr, flush=True)"
                ),
            ]
            result_box: dict[str, ralph.CompletedCommand] = {}
            error_box: dict[str, BaseException] = {}

            def run_command() -> None:
                try:
                    result_box["result"] = runner.run(
                        command,
                        cwd=tmp_path,
                        log_path=log_path,
                        phase="streaming test phase",
                    )
                except BaseException as error:
                    error_box["error"] = error

            output = io.StringIO()
            with redirect_stdout(output):
                thread = threading.Thread(target=run_command)
                thread.start()
                deadline = time.monotonic() + 2.0
                streamed_log = ""
                while time.monotonic() < deadline:
                    if log_path.exists():
                        streamed_log = log_path.read_text(encoding="utf-8")
                        if "first line" in streamed_log:
                            break
                    time.sleep(0.01)
                else:
                    self.fail("command log did not stream first stdout line")

                self.assertIn("exit: running", streamed_log)
                self.assertTrue(thread.is_alive())
                thread.join(timeout=3.0)

            self.assertFalse(thread.is_alive())
            if "error" in error_box:
                raise error_box["error"]

            result = result_box["result"]
            final_log = log_path.read_text(encoding="utf-8")
            self.assertEqual(result.stdout, "first line\nsecond line\n")
            self.assertEqual(result.stderr, "error line\n")
            self.assertIn(f"$ {ralph.format_command(command)}", final_log)
            self.assertIn(f"cwd: {tmp_path}", final_log)
            self.assertIn("exit: 0", final_log)
            self.assertIn("STDOUT:\nfirst line\nsecond line\n", final_log)
            self.assertIn("STDERR:\nerror line\n", final_log)
            self.assertIn(
                "Ralph heartbeat: phase=streaming test phase; log=", output.getvalue()
            )

    def test_command_runner_failure_preserves_command_log_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            log_path = tmp_path / "failure.log"
            runner = ralph.CommandRunner(dry_run=False)
            command = [
                sys.executable,
                "-c",
                (
                    "import sys; "
                    "print('before failure'); "
                    "print('failure detail', file=sys.stderr); "
                    "raise SystemExit(7)"
                ),
            ]

            with self.assertRaises(ralph.CommandFailure) as caught:
                runner.run(
                    command,
                    cwd=tmp_path,
                    log_path=log_path,
                    phase="failure logging phase",
                )

            error = caught.exception
            log = log_path.read_text(encoding="utf-8")
            self.assertEqual(error.returncode, 7)
            self.assertEqual(error.stdout, "before failure\n")
            self.assertEqual(error.stderr, "failure detail\n")
            self.assertIn(f"$ {ralph.format_command(command)}", log)
            self.assertIn(f"cwd: {tmp_path}", log)
            self.assertIn("exit: 7", log)
            self.assertIn("STDOUT:\nbefore failure\n", log)
            self.assertIn("STDERR:\nfailure detail\n", log)

    def test_command_runner_timeout_preserves_partial_log(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            log_path = tmp_path / "timeout.log"
            runner = ralph.CommandRunner(dry_run=False, heartbeat_interval=0)
            command = [
                sys.executable,
                "-c",
                ("import time; print('before timeout', flush=True); time.sleep(1.0)"),
            ]

            with self.assertRaises(ralph.CommandTimeout) as caught:
                runner.run(
                    command,
                    cwd=tmp_path,
                    log_path=log_path,
                    phase="timeout logging phase",
                    timeout_seconds=0.3,
                )

            error = caught.exception
            log = log_path.read_text(encoding="utf-8")
            self.assertEqual(error.returncode, 124)
            self.assertEqual(error.stdout, "before timeout\n")
            self.assertIn("exit: 124", log)
            self.assertIn("STDOUT:\nbefore timeout\n", log)


class RalphLoopLocalIntegrationTests(unittest.TestCase):
    def test_malformed_issue_marks_failed_without_creating_worktree(self) -> None:
        runner = FakeRunner()
        malformed_body = """## What to build
Build it.

## Acceptance criteria
"""
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, malformed_body)
                )

            comment_path = next(
                (Path(tmp) / "logs").glob("issue-42-*/issue-42-comment.md")
            )
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(Path(tmp))

        commands = [call.args for call in runner.calls]
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "42",
                "-R",
                "example/repo",
                "--add-label",
                "agent-running",
                "--add-label",
                "delivery-trunk",
                "--remove-label",
                "ready-for-agent",
                "--remove-label",
                "agent-failed",
                "--remove-label",
                "agent-merged",
                "--remove-label",
                "agent-integrated",
            ),
            commands,
        )
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "42",
                "-R",
                "example/repo",
                "--add-label",
                "agent-failed",
                "--remove-label",
                "agent-running",
                "--remove-label",
                "ready-for-agent",
            ),
            commands,
        )
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "add") for command in commands)
        )
        self.assertIn(
            "Missing required issue section(s): Acceptance criteria, Blocked by",
            comment,
        )
        self.assertEqual(manifest["run_kind"], "implementation")
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["delivery_mode"], "trunk")
        self.assertEqual(manifest["integration_target"], "main")
        self.assertEqual(manifest["github_metadata"]["status"], "failure_commented")
        self.assertIn("Missing required issue section", manifest["failure"]["message"])

    def test_exploratory_issue_without_review_focus_fails_before_handoff(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue(
                {"ready-for-agent", "delivery-exploratory"},
                IMPLEMENTATION_BODY,
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(issue)

            comment_path = next(tmp_path.glob("logs/issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertFalse(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "add") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("git", "push", "origin") for command in commands)
        )
        self.assertIn("Missing required issue section(s): Review focus", comment)
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["delivery_mode"], "exploratory")
        self.assertEqual(
            manifest["integration_target"],
            "agent/exploratory/issue-42-implement-thing",
        )
        self.assertEqual(manifest["github_metadata"]["status"], "failure_commented")
        self.assertIn("Review focus", manifest["failure"]["message"])

    def test_unknown_operator_smoke_id_fails_with_issue_evidence_before_command(
        self,
    ) -> None:
        runner = FakeRunner()
        body = OPERATOR_SMOKE_BODY.replace(
            "Smoke id: ec2-run-worker-placement",
            "Smoke id: unknown-smoke",
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.EXPLORATORY_MODE)
            issue = make_issue({"ready-for-agent"}, body)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(issue)

            comment_path = next(tmp_path.glob("logs/issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any("run-ec2-run-worker-smoke" in " ".join(command) for command in commands)
        )
        self.assertFalse(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "add") for command in commands)
        )
        self.assertIn("Unknown Operator smoke id `unknown-smoke`", comment)
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["operator_smoke"]["status"], "not_requested")

    def test_qa_commands_receive_fallback_runtime_env_and_record_manifest(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            branch, worktree_path, integration_path = loop._branch_and_worktrees(issue)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=issue,
                delivery_plan=delivery_plan,
                branch=branch,
                worktree_path=worktree_path,
                integration_path=integration_path,
                config=loop.config,
            )

            with patch.dict(ralph.os.environ, {"PATH": "/usr/bin"}, clear=True):
                with redirect_stdout(io.StringIO()):
                    loop._run_qa_commands(
                        ["scripts/ralph.py"],
                        loop.config.repo_root,
                        run_dir,
                        log_prefix="qa",
                        subject="#42",
                        manifest=manifest,
                    )

            qa_call = next(
                call for call in runner.calls if call.args == ("make", "run-prek")
            )
            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        self.assertIsNotNone(qa_call.env)
        assert qa_call.env is not None
        runtime_root = ralph.default_qa_runtime_root("example/repo", run_dir)
        self.assertEqual(
            qa_call.env["DAGSTER_HOME"],
            str(runtime_root / "dagster-home"),
        )
        self.assertEqual(
            qa_call.env["XDG_CACHE_HOME"],
            str(runtime_root / "xdg-cache"),
        )
        self.assertEqual(
            qa_call.env["UV_CACHE_DIR"],
            str(runtime_root / "uv-cache"),
        )
        self.assertEqual(
            manifest_payload["qa_runtime_env"]["variables"]["DAGSTER_HOME"]["source"],
            "ralph_default",
        )
        self.assertEqual(
            manifest_payload["qa_runtime_env"]["variables"]["UV_CACHE_DIR"]["value"],
            str(runtime_root / "uv-cache"),
        )
        self.assertEqual(manifest_payload["qa_results"][0]["status"], "passed")

    def test_no_space_qa_command_failure_is_environment_failure(self) -> None:
        runner = FakeRunner(
            fail_command_attempts={
                ("make", "run-prek"): [
                    (
                        1,
                        "OSError: [Errno 28] No space left on device: '/tmp/uv-cache'",
                    )
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            branch, worktree_path, integration_path = loop._branch_and_worktrees(issue)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=issue,
                delivery_plan=delivery_plan,
                branch=branch,
                worktree_path=worktree_path,
                integration_path=integration_path,
                config=loop.config,
            )

            with patch.dict(
                ralph.os.environ,
                {
                    "PATH": "/usr/bin",
                    ralph.QA_RUNTIME_MIN_FREE_BYTES_ENV: "0",
                    ralph.QA_RUNTIME_MIN_FREE_INODES_ENV: "0",
                },
                clear=True,
            ):
                with self.assertRaises(ralph.EnvironmentFailure) as caught:
                    with redirect_stdout(io.StringIO()):
                        loop._run_qa_commands(
                            ["scripts/ralph.py"],
                            loop.config.repo_root,
                            run_dir,
                            log_prefix="qa",
                            subject="#42",
                            manifest=manifest,
                        )
            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        self.assertEqual(caught.exception.failure_type, "qa_runtime_no_space_left")
        self.assertIn("No space left on device", str(caught.exception))
        self.assertIn("Capacity signal", str(caught.exception))
        self.assertIn("Next action", str(caught.exception))
        self.assertIn("/tmp/uv-cache", str(caught.exception))
        self.assertIn(
            "rerun the Operator command or targeted issue",
            caught.exception.recovery_guidance or "",
        )
        self.assertEqual(manifest_payload["qa_results"][0]["status"], "failed")

    def test_no_space_qa_command_failure_names_operator_cache_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            operator_uv_cache = tmp_path / "operator-uv-cache"
            runner = FakeRunner(
                fail_command_attempts={
                    ("make", "run-prek"): [
                        (
                            1,
                            "OSError: [Errno 28] No space left on device: "
                            f"'{operator_uv_cache}'",
                        )
                    ]
                }
            )
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            branch, worktree_path, integration_path = loop._branch_and_worktrees(issue)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=issue,
                delivery_plan=delivery_plan,
                branch=branch,
                worktree_path=worktree_path,
                integration_path=integration_path,
                config=loop.config,
            )

            with patch.dict(
                ralph.os.environ,
                {
                    "PATH": "/usr/bin",
                    "DAGSTER_HOME": str(tmp_path / "operator-dagster"),
                    "XDG_CACHE_HOME": str(tmp_path / "operator-xdg-cache"),
                    "UV_CACHE_DIR": str(operator_uv_cache),
                    ralph.QA_RUNTIME_MIN_FREE_BYTES_ENV: str(sys.maxsize),
                    ralph.QA_RUNTIME_MIN_FREE_INODES_ENV: str(sys.maxsize),
                },
                clear=True,
            ):
                with self.assertRaises(ralph.EnvironmentFailure) as caught:
                    with redirect_stdout(io.StringIO()):
                        loop._run_qa_commands(
                            ["scripts/ralph.py"],
                            loop.config.repo_root,
                            run_dir,
                            log_prefix="qa",
                            subject="#42",
                            manifest=manifest,
                        )

        text = str(caught.exception)
        default_runtime_root = ralph.default_qa_runtime_root("example/repo", run_dir)
        self.assertEqual(caught.exception.failure_type, "qa_runtime_no_space_left")
        self.assertIn(str(operator_uv_cache), text)
        self.assertNotIn(str(default_runtime_root), text)
        self.assertIn("Capacity signal: free bytes, free inodes", text)
        self.assertIn("Next action", text)
        self.assertIn(str(operator_uv_cache), caught.exception.recovery_guidance or "")
        self.assertIn(
            "rerun the Operator command or targeted issue",
            caught.exception.recovery_guidance or "",
        )

    def test_docs_only_aemo_etl_qa_selection_records_manifest_command(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            branch, worktree_path, integration_path = loop._branch_and_worktrees(issue)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=issue,
                delivery_plan=delivery_plan,
                branch=branch,
                worktree_path=worktree_path,
                integration_path=integration_path,
                config=loop.config,
            )

            with patch.dict(ralph.os.environ, {"PATH": "/usr/bin"}, clear=True):
                with redirect_stdout(io.StringIO()):
                    loop._run_qa_commands(
                        [
                            "backend-services/dagster-user/aemo-etl/docs/development/"
                            "local_development.md"
                        ],
                        loop.config.repo_root,
                        run_dir,
                        log_prefix="qa",
                        subject="#42",
                        manifest=manifest,
                    )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        self.assertEqual(
            manifest_payload["qa_results"],
            [
                {
                    "name": "root Commit check",
                    "command": ["prek", "run", "-a"],
                    "cwd": str(loop.config.repo_root),
                    "log_path": str(run_dir / "qa-1-root-commit-check.log"),
                    "status": "passed",
                }
            ],
        )

    def test_successful_implementation_squash_merges_pushes_comments_and_closes(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            output = io.StringIO()

            with redirect_stdout(output):
                loop._handle_implementation(issue)

            commands = [call.args for call in runner.calls]
            phases = [call.phase for call in runner.calls]
            self.assertIn(
                ("git", "merge", "--squash", "agent/issue-42-implement-thing"),
                commands,
            )
            self.assertIn(("git", "push", "origin", "HEAD:main"), commands)
            review_call = next(
                call
                for call in runner.calls
                if call.input_text is not None
                and "Run an Issue completion review" in call.input_text
            )
            review_index = runner.calls.index(review_call)
            package_call = next(
                call
                for call in runner.calls
                if call.input_text is not None
                and "Generate a Review package" in call.input_text
            )
            package_index = runner.calls.index(package_call)
            merge_index = commands.index(
                ("git", "merge", "--squash", "agent/issue-42-implement-thing")
            )
            push_index = commands.index(("git", "push", "origin", "HEAD:main"))
            close_index = commands.index(
                (
                    "gh",
                    "issue",
                    "close",
                    "42",
                    "-R",
                    "example/repo",
                    "--reason",
                    "completed",
                )
            )
            self.assertLess(review_index, merge_index)
            self.assertLess(package_index, merge_index)
            self.assertLess(package_index, push_index)
            self.assertLess(package_index, close_index)
            self.assertIn(
                (
                    "gh",
                    "issue",
                    "close",
                    "42",
                    "-R",
                    "example/repo",
                    "--reason",
                    "completed",
                ),
                commands,
            )
            self.assertFalse(
                any(command[:3] == ("gh", "pr", "create") for command in commands)
            )
            progress = output.getvalue()
            self.assertIn("#42: claiming issue with agent-running", progress)
            self.assertIn("#42: running QA Ralph loop Commit check", progress)
            self.assertIn("#42: pushing merge-sha to main", progress)
            self.assertIn("Issue #42 merged to main: merge-sha", progress)
            self.assertIn("#42: Codex implementation attempt 1", phases)
            self.assertIn("#42: QA Ralph loop Commit check", phases)

            comment_path = next(
                (Path(tmp) / "logs").glob("issue-42-*/issue-42-comment.md")
            )
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(Path(tmp))
            self.assertIn("Ralph trunk integration completed.", comment)
            self.assertIn("Commit: `merge-sha`", comment)
            self.assertIn("## Review package", comment)
            self.assertIn("review-package.html", comment)
            self.assertEqual(manifest["status"], "succeeded")
            self.assertEqual(manifest["issue"]["number"], 42)
            self.assertEqual(manifest["delivery_mode"], "trunk")
            self.assertEqual(manifest["integration_target"], "main")
            self.assertEqual(
                manifest["branches"]["issue"], "agent/issue-42-implement-thing"
            )
            self.assertEqual(manifest["integration_commit"]["sha"], "merge-sha")
            self.assertEqual(
                manifest["pushes"]["integration_target"]["status"], "pushed"
            )
            self.assertEqual(manifest["github_metadata"]["status"], "closed")
            self.assertEqual(manifest["qa_results"][0]["status"], "passed")
            self.assertEqual(manifest["issue_completion_review"]["status"], "passed")
            self.assertEqual(
                manifest["issue_completion_review"]["reasons"],
                ["Agent workflow changes", "Trunk delivery"],
            )
            self.assertEqual(
                manifest["issue_completion_review"]["artifact_path"],
                str(
                    next(
                        (Path(tmp) / "logs").glob(
                            "issue-42-*/issue-completion-review.md"
                        )
                    )
                ),
            )
            package_path = next(
                (Path(tmp) / "logs").glob("issue-42-*/review-package.html")
            )
            package_log = next(
                (Path(tmp) / "logs").glob("issue-42-*/codex-review-package.jsonl")
            )
            self.assertEqual(manifest["review_package"]["status"], "passed")
            self.assertEqual(manifest["review_package"]["validation_status"], "passed")
            self.assertEqual(manifest["review_package"]["html_path"], str(package_path))
            self.assertEqual(
                manifest["review_package"]["generator_log_path"],
                str(package_log),
            )
            self.assertEqual(
                manifest["review_package"]["summary"]["changed_file_count"],
                1,
            )

    def test_trunk_review_package_records_marimo_changed_notebook_videos(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[
                " M backend-services/marimo/notebooks/gas_market_prices.py\n",
                " M backend-services/marimo/notebooks/gas_market_prices.py\n",
            ],
            diff_outputs=["backend-services/marimo/notebooks/gas_market_prices.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)
            comment_path = next(
                (tmp_path / "logs").glob("issue-42-*/issue-42-comment.md")
            )
            package_path = next(
                (tmp_path / "logs").glob("issue-42-*/review-package.html")
            )

            media = manifest["review_package"]["media"]
            self.assertEqual(
                [(item["route"], item["viewport"]) for item in media],
                [
                    ("/marimo/gas_market_prices/", "desktop"),
                    ("/marimo/gas_market_prices/", "narrow"),
                ],
            )
            for item in media:
                self.assertTrue(Path(item["path"]).exists())
                self.assertEqual(item["format"], "webm")
            package_html = package_path.read_text(encoding="utf-8")
            self.assertIn("Review package media", package_html)
            self.assertIn("marimo__gas_market_prices__desktop.webm", package_html)
            comment = comment_path.read_text(encoding="utf-8")
            self.assertIn("## Review package", comment)
            self.assertIn("Media", comment)
            self.assertIn("/marimo/gas_market_prices/", comment)
            media_call = next(
                call
                for call in runner.calls
                if call.args[:6]
                == (
                    "uv",
                    "run",
                    "--with",
                    "playwright",
                    "python",
                    "scripts/review_promoted_dashboards.py",
                )
            )
            browser_install_call = next(
                call
                for call in runner.calls
                if call.args
                == (
                    "uv",
                    "run",
                    "--with",
                    "playwright",
                    "playwright",
                    "install",
                    "chromium",
                )
            )
            self.assertEqual(browser_install_call.cwd.name, "marimo")
            self.assertEqual(media_call.cwd.name, "marimo")
            self.assertIn("--videos", media_call.args)
            self.assertIn("--route", media_call.args)

    def test_trunk_marimo_media_failure_stops_before_main_push(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[
                " M backend-services/marimo/notebooks/gas_market_prices.py\n",
                " M backend-services/marimo/notebooks/gas_market_prices.py\n",
            ],
            diff_outputs=["backend-services/marimo/notebooks/gas_market_prices.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_marimo_review_media=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                manifest_obj = loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertIsNotNone(manifest_obj)
        self.assertFalse(
            any(command[:3] == ("git", "merge", "--squash") for command in commands)
        )
        self.assertNotIn(("git", "push", "origin", "HEAD:main"), commands)
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["review_package"]["status"], "failed")
        self.assertIn(
            "Marimo Review package media capture failed",
            manifest["review_package"]["failure_reason"],
        )

    def test_trunk_review_package_validation_failure_stops_before_main_push(
        self,
    ) -> None:
        invalid_html = REVIEW_PACKAGE_HTML.replace(
            "<h2>QA evidence</h2>",
            '<script src="https://example.com/app.js"></script><h2>QA evidence</h2>',
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            review_package_html=invalid_html,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                manifest_obj = loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertIsNotNone(manifest_obj)
        self.assertFalse(
            any(command[:3] == ("git", "merge", "--squash") for command in commands)
        )
        self.assertNotIn(("git", "push", "origin", "HEAD:main"), commands)
        self.assertFalse(
            any(
                command[:4] == ("gh", "issue", "edit", "42")
                and "--add-label" in command
                and command[command.index("--add-label") + 1] == "agent-merged"
                for command in commands
            )
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["review_package"]["status"], "validation_failed")
        self.assertEqual(manifest["review_package"]["validation_status"], "failed")
        self.assertIn("script tag", manifest["review_package"]["failure_reason"])

    def test_trunk_review_package_generation_failure_stops_before_main_push(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_review_package=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(command[:3] == ("git", "merge", "--squash") for command in commands)
        )
        self.assertNotIn(("git", "push", "origin", "HEAD:main"), commands)
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["review_package"]["status"], "failed")
        self.assertIn(
            "Review package generation failed",
            manifest["review_package"]["failure_reason"],
        )

    def test_issue_completion_review_failure_repairs_reruns_qa_and_review(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n"] * 4,
            diff_outputs=["scripts/ralph.py\n", "scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            issue_completion_review_markdowns=[
                ISSUE_COMPLETION_REVIEW_FAIL_MARKDOWN,
                ISSUE_COMPLETION_REVIEW_PASS_MARKDOWN,
            ],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, max_codex_attempts=2)

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(tmp_path)

        review_calls = [
            call
            for call in runner.calls
            if call.input_text is not None
            and "Run an Issue completion review" in call.input_text
        ]
        repair_call = next(
            call
            for call in runner.calls
            if call.input_text is not None
            and "Repair GitHub issue #42 after Issue completion review findings"
            in call.input_text
        )
        qa_calls = [call for call in runner.calls if call.args == ("make", "run-prek")]
        commands = [call.args for call in runner.calls]

        self.assertEqual(len(review_calls), 2)
        self.assertIn(
            "`scripts/ralph.py` does not implement the requested review gate",
            repair_call.input_text,
        )
        self.assertEqual(len(qa_calls), 2)
        self.assertIn(
            (
                "git",
                "commit",
                "-m",
                "Apply Issue completion review repairs for issue #42: Implement thing",
            ),
            commands,
        )
        self.assertIn(("git", "push", "origin", "HEAD:main"), commands)
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual(manifest["issue_completion_review"]["status"], "passed")
        self.assertEqual(
            [
                attempt["result"]
                for attempt in manifest["issue_completion_review"]["attempts"]
            ],
            ["fail", "pass"],
        )
        self.assertEqual(
            [attempt["attempt"] for attempt in manifest["codex_attempts"]],
            [1, 2],
        )

    def test_issue_completion_review_exhaustion_fails_before_local_integration(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n"] * 2,
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n"],
            issue_completion_review_markdowns=[ISSUE_COMPLETION_REVIEW_FAIL_MARKDOWN],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, max_codex_attempts=1)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(tmp_path)
            comment = next(
                tmp_path.glob("logs/issue-42-*/issue-42-comment.md")
            ).read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        self.assertNotIn(
            ("git", "merge", "--squash", "agent/issue-42-implement-thing"),
            commands,
        )
        self.assertNotIn(("git", "push", "origin", "HEAD:main"), commands)
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "42",
                "-R",
                "example/repo",
                "--add-label",
                "agent-failed",
                "--remove-label",
                "agent-running",
                "--remove-label",
                "ready-for-agent",
            ),
            commands,
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(
            manifest["issue_completion_review"]["status"], "failed_exhausted"
        )
        self.assertEqual(
            manifest["failure"]["type"],
            ralph.ISSUE_COMPLETION_REVIEW_FAILURE_TYPE,
        )
        self.assertIn("Issue completion review failed", comment)

    def test_successful_e2e_retry_reports_durable_run_manifest_evidence(self) -> None:
        changed_path = (
            "backend-services/dagster-user/aemo-etl/src/aemo_etl/assets/foo.py"
        )
        runner = E2EManifestRetryRunner(
            status_outputs=[f" M {changed_path}\n"] * 3,
            diff_outputs=[f"{changed_path}\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, E2E_IMPLEMENTATION_BODY)
                )

            run_dir = next(tmp_path.glob("logs/issue-42-*"))
            comment = (run_dir / "issue-42-comment.md").read_text(encoding="utf-8")
            manifest = load_run_manifest(tmp_path)

            e2e_results = [
                result
                for result in manifest["qa_results"]
                if result["name"] == ralph.AEMO_ETL_E2E_QA_NAME
            ]
            self.assertEqual(
                [result["status"] for result in e2e_results],
                ["failed", "passed"],
            )
            failed_result, passed_result = e2e_results
            self.assertNotIn("run_manifest_evidence", failed_result)
            evidence = passed_result["run_manifest_evidence"]
            artifact_path = Path(evidence["artifact_path"])

            self.assertEqual(
                evidence["source_path"],
                str(runner.success_manifest_path),
            )
            self.assertTrue(artifact_path.is_relative_to(run_dir))
            self.assertTrue(artifact_path.exists())
            self.assertEqual(
                json.loads(artifact_path.read_text(encoding="utf-8"))["status"],
                "success",
            )
            self.assertIn(str(artifact_path), comment)
            self.assertIn("qa-retry-3-aemo-etl-end-to-end-test", comment)
            self.assertNotIn(
                "qa-3-aemo-etl-end-to-end-test-run-manifest.json",
                comment,
            )
            self.assertIn("scenario `full-gas-model`", comment)
            self.assertIn("target progress `37/37 materialized`", comment)
            self.assertIn("asset checks `144`", comment)

    def test_codex_failures_retry_until_configured_attempt_budget_succeeds(
        self,
    ) -> None:
        runner = FakeRunner(status_outputs=[" M scripts/ralph.py\n"])
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, max_codex_attempts=3)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            worktree_path, run_dir, manifest, access_plan = (
                implementation_attempt_context(tmp_path, loop, issue)
            )
            codex_command = tuple(ralph.codex_exec_command(worktree_path))
            runner.fail_command_attempts[codex_command] = [
                (1, "first codex failure"),
                (1, "second codex failure"),
            ]

            with redirect_stdout(io.StringIO()):
                loop._implement_with_retry(
                    issue,
                    worktree_path,
                    run_dir,
                    manifest,
                    access_plan=access_plan,
                )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        codex_calls = [
            call for call in runner.calls if call.args[:2] == ("codex", "exec")
        ]
        prompts = [call.input_text for call in codex_calls]
        log_names = [
            call.log_path.name for call in codex_calls if call.log_path is not None
        ]
        self.assertEqual(len(codex_calls), 3)
        self.assertNotIn("Failure detail:", prompts[0])
        self.assertIn("first codex failure", prompts[1])
        self.assertIn("second codex failure", prompts[2])
        self.assertEqual(
            log_names,
            [
                "codex-implementation-1.jsonl",
                "codex-implementation-2.jsonl",
                "codex-implementation-3.jsonl",
            ],
        )
        self.assertEqual(
            [attempt["status"] for attempt in manifest_payload["codex_attempts"]],
            ["failed", "failed", "completed"],
        )
        self.assertEqual(manifest_payload["qa_results"][0]["status"], "passed")

    def test_qa_failures_consume_codex_attempt_budget_and_retry_until_success(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n"] * 3,
            fail_command_attempts={
                ("make", "run-prek"): [
                    (1, "first QA failure"),
                    (1, "second QA failure"),
                ]
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, max_codex_attempts=3)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            worktree_path, run_dir, manifest, access_plan = (
                implementation_attempt_context(tmp_path, loop, issue)
            )

            with redirect_stdout(io.StringIO()):
                loop._implement_with_retry(
                    issue,
                    worktree_path,
                    run_dir,
                    manifest,
                    access_plan=access_plan,
                )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        codex_calls = [
            call for call in runner.calls if call.args[:2] == ("codex", "exec")
        ]
        qa_calls = [call for call in runner.calls if call.args == ("make", "run-prek")]
        prompts = [call.input_text for call in codex_calls]
        qa_log_names = [
            call.log_path.name for call in qa_calls if call.log_path is not None
        ]

        self.assertEqual(len(codex_calls), 3)
        self.assertEqual(len(qa_calls), 3)
        self.assertIn("first QA failure", prompts[1])
        self.assertIn("second QA failure", prompts[2])
        self.assertEqual(
            qa_log_names,
            [
                "qa-1-ralph-loop-commit-check.log",
                "qa-retry-1-ralph-loop-commit-check.log",
                "qa-retry-3-1-ralph-loop-commit-check.log",
            ],
        )
        self.assertEqual(
            [attempt["status"] for attempt in manifest_payload["codex_attempts"]],
            ["completed", "completed", "completed"],
        )
        self.assertEqual(
            [result["status"] for result in manifest_payload["qa_results"]],
            ["failed", "failed", "passed"],
        )

    def test_qa_failure_exhausts_configured_codex_attempt_budget(self) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n"] * 2,
            fail_command_attempts={
                ("make", "run-prek"): [
                    (1, "first QA failure"),
                    (1, "second QA failure"),
                ]
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, max_codex_attempts=2)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            worktree_path, run_dir, manifest, access_plan = (
                implementation_attempt_context(tmp_path, loop, issue)
            )
            output = io.StringIO()

            with redirect_stdout(output), self.assertRaises(ralph.CommandFailure):
                loop._implement_with_retry(
                    issue,
                    worktree_path,
                    run_dir,
                    manifest,
                    access_plan=access_plan,
                )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        codex_calls = [
            call for call in runner.calls if call.args[:2] == ("codex", "exec")
        ]
        prompts = [call.input_text for call in codex_calls]

        self.assertEqual(len(codex_calls), 2)
        self.assertIn("first QA failure", prompts[1])
        self.assertIn("exhausted --max-codex-attempts 2", output.getvalue())
        self.assertEqual(
            [attempt["status"] for attempt in manifest_payload["codex_attempts"]],
            ["completed", "completed"],
        )
        self.assertEqual(
            [result["status"] for result in manifest_payload["qa_results"]],
            ["failed", "failed"],
        )

    def test_agents_issue_without_full_access_flag_stops_before_claim(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, AGENTS_IMPLEMENTATION_BODY)

            with self.assertRaises(ralph.EnvironmentFailure) as caught:
                loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)

        self.assertIn("Full-access implementation", str(caught.exception))
        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "add") for command in commands)
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["github_metadata"]["status"], "not_started")
        self.assertEqual(
            manifest["full_access_implementation"]["status"],
            "blocked_missing_operator_flag",
        )

    def test_full_access_implementation_uses_bypass_and_read_only_issue_commands(
        self,
    ) -> None:
        changed = (
            " M .agents/skills/ralph-loop/SKILL.md\n M docs/agents/ralph-loop.md\n"
        )
        runner = FakeRunner(status_outputs=[changed, changed])
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                allow_full_access_implementation=True,
            )
            issue = make_issue({"ready-for-agent"}, AGENTS_IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            branch, worktree_path, integration_path = loop._branch_and_worktrees(issue)
            worktree_path.mkdir(parents=True)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=issue,
                delivery_plan=delivery_plan,
                branch=branch,
                worktree_path=worktree_path,
                integration_path=integration_path,
                config=loop.config,
            )
            access_plan = ralph.issue_implementation_access_plan(issue)

            with redirect_stdout(io.StringIO()):
                loop._implement_with_retry(
                    issue,
                    worktree_path,
                    run_dir,
                    manifest,
                    access_plan=access_plan,
                )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        codex_call = next(
            call for call in runner.calls if call.args[:2] == ("codex", "exec")
        )
        self.assertIn("--dangerously-bypass-approvals-and-sandbox", codex_call.args)
        self.assertNotIn("--sandbox", codex_call.args)
        self.assertNotIn("--full-auto", codex_call.args)
        self.assertEqual(
            manifest_payload["sandboxed_issue_access"]["allowed_commands"],
            [
                "gh auth status",
                "gh issue view",
                "gh issue list",
                "gh issue status",
            ],
        )
        self.assertEqual(
            manifest_payload["full_access_implementation"]["status"],
            "diff_confined",
        )
        self.assertIn(("prek", "run", "-a"), [call.args for call in runner.calls])

    def test_full_access_out_of_anchor_diff_fails_before_qa_and_retry(self) -> None:
        runner = FakeRunner(
            status_outputs=[
                " M .agents/skills/ralph-loop/SKILL.md\n M scripts/ralph.py\n"
            ]
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                allow_full_access_implementation=True,
            )
            issue = make_issue({"ready-for-agent"}, AGENTS_IMPLEMENTATION_BODY)
            delivery_plan = ralph.resolve_delivery_plan(
                issue,
                default_mode=loop.config.delivery_mode,
                target_branch=loop.config.target_branch,
            )
            branch, worktree_path, integration_path = loop._branch_and_worktrees(issue)
            worktree_path.mkdir(parents=True)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=issue,
                delivery_plan=delivery_plan,
                branch=branch,
                worktree_path=worktree_path,
                integration_path=integration_path,
                config=loop.config,
            )
            access_plan = ralph.issue_implementation_access_plan(issue)

            with self.assertRaises(ralph.FullAccessImplementationScopeFailure):
                with redirect_stdout(io.StringIO()):
                    loop._implement_with_retry(
                        issue,
                        worktree_path,
                        run_dir,
                        manifest,
                        access_plan=access_plan,
                    )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        commands = [call.args for call in runner.calls]
        self.assertEqual(
            sum(1 for command in commands if command[:2] == ("codex", "exec")),
            1,
        )
        self.assertNotIn(("prek", "run", "-a"), commands)
        self.assertNotIn(("make", "run-prek"), commands)
        self.assertEqual(
            manifest_payload["full_access_implementation"]["status"],
            "diff_out_of_scope",
        )
        self.assertEqual(
            manifest_payload["full_access_implementation"]["out_of_scope_files"],
            ["scripts/ralph.py"],
        )

    def test_end_of_file_fixer_commit_recovery_stages_reruns_commit_check_and_retries(
        self,
    ) -> None:
        doc_path = "docs/agents/ralph-loop.md"
        commit_command = ("git", "commit", "-m", "Implement issue #42: Implement thing")
        runner = FakeRunner(
            status_outputs=[
                f" M {doc_path}\n",
                f" M {doc_path}\n",
                f"MM {doc_path}\n",
                f"M  {doc_path}\n",
            ],
            diff_outputs=[f"{doc_path}\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_command_attempts={
                commit_command: [
                    (
                        1,
                        "end-of-file-fixer...........................................Failed\n"
                        "- hook id: end-of-file-fixer\n"
                        "- files were modified by this hook\n",
                    )
                ]
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        commit_log_names = [
            call.log_path.name
            for call in runner.calls
            if call.args == commit_command and call.log_path is not None
        ]
        self.assertEqual(
            commit_log_names,
            [
                "issue-git-commit.log",
                "issue-formatter-recovery-git-commit.log",
                "integration-git-commit.log",
            ],
        )
        recovery_add_index = commands.index(("git", "add", "--", doc_path))
        recovery_check_index = commands.index(("prek", "run", "-a"), recovery_add_index)
        retry_commit_index = next(
            index
            for index, call in enumerate(runner.calls)
            if call.args == commit_command
            and call.log_path is not None
            and call.log_path.name == "issue-formatter-recovery-git-commit.log"
        )
        self.assertLess(recovery_add_index, recovery_check_index)
        self.assertLess(recovery_check_index, retry_commit_index)
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual(manifest["formatter_recovery"]["status"], "recovered")
        self.assertEqual(manifest["formatter_recovery"]["modified_files"], [doc_path])
        self.assertEqual(manifest["formatter_recovery"]["staged_files"], [doc_path])
        self.assertEqual(
            manifest["formatter_recovery"]["commit_check_results"][0]["name"],
            "root Commit check",
        )
        self.assertEqual(manifest["qa_results"][-1]["name"], "root Commit check")

    def test_ruff_format_commit_recovery_failure_is_classified(self) -> None:
        aemo_path = "backend-services/dagster-user/aemo-etl/src/aemo_etl/assets/foo.py"
        commit_command = ("git", "commit", "-m", "Implement issue #42: Implement thing")
        runner = FakeRunner(
            status_outputs=[
                f" M {aemo_path}\n",
                f" M {aemo_path}\n",
                f"MM {aemo_path}\n",
                f"M  {aemo_path}\n",
            ],
            rev_parse_outputs=["base-sha\n"],
            fail_command_attempts={
                commit_command: [
                    (
                        1,
                        "ruff format.................................................Failed\n"
                        "- hook id: ruff-format\n"
                        "- files were modified by this hook\n",
                    ),
                    (1, "git commit failed again after formatter recovery\n"),
                ]
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(tmp_path)
            comment = next(
                tmp_path.glob("logs/issue-42-*/issue-42-comment.md")
            ).read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        run_prek_command = ("make", "run-prek")
        self.assertEqual(commands.count(run_prek_command), 2)
        self.assertNotIn(
            ("git", "merge", "--squash", "agent/issue-42-implement-thing"), commands
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["formatter_recovery"]["status"], "failed")
        self.assertEqual(
            manifest["formatter_recovery"]["failure_type"],
            ralph.FORMATTER_REWRITE_RECOVERY_FAILURE_TYPE,
        )
        self.assertEqual(
            manifest["failure"]["type"],
            ralph.FORMATTER_REWRITE_RECOVERY_FAILURE_TYPE,
        )
        self.assertEqual(manifest["failure"]["modified_files"], [aemo_path])
        self.assertIn(
            "issue-git-commit.log", manifest["failure"]["initial_commit_log_path"]
        )
        self.assertIn(
            "formatter-recovery-commit-check-1-aemo-etl-commit-check.log",
            manifest["failure"]["commit_check_log_paths"][0],
        )
        self.assertIn(
            "issue-formatter-recovery-git-commit.log",
            manifest["failure"]["retry_commit_log_path"],
        )
        self.assertIn("Formatter-rewrite recovery failure", comment)
        self.assertIn("Commit check logs", comment)
        self.assertIn("Recovery guidance", comment)

    def test_implementation_fetches_refresh_notes_before_codex_prompt(self) -> None:
        issue_comments_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        included_note = ready_issue_refresh_body(
            "Issue body blockers changed after #68."
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            command_outputs={
                issue_comments_command: [
                    json.dumps(
                        {
                            "comments": [
                                {
                                    "body": "Maintainer discussion.",
                                    "createdAt": "2026-05-01T00:00:00Z",
                                },
                                {
                                    "body": f"{ralph.AI_TRIAGE_DISCLAIMER}\n\nTriage note.",
                                    "createdAt": "2026-05-02T00:00:00Z",
                                },
                                {
                                    "body": included_note,
                                    "createdAt": "2026-05-03T00:00:00Z",
                                },
                            ]
                        }
                    )
                ]
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(issue)

        commands = [call.args for call in runner.calls]
        codex_call = next(
            call for call in runner.calls if call.args[:2] == ("codex", "exec")
        )
        codex_index = runner.calls.index(codex_call)
        self.assertLess(commands.index(issue_comments_command), codex_index)
        self.assertIsNotNone(codex_call.input_text)
        assert codex_call.input_text is not None
        self.assertIn("Recent Ready issue refresh notes:", codex_call.input_text)
        self.assertIn(included_note, codex_call.input_text)
        self.assertNotIn("Maintainer discussion.", codex_call.input_text)
        self.assertNotIn("Triage note.", codex_call.input_text)

    def test_implementation_comment_fetch_failure_stops_before_codex(self) -> None:
        issue_comments_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        runner = FakeRunner(
            rev_parse_outputs=["base-sha\n"],
            fail_commands={issue_comments_command: 1},
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)
            comment_path = next(tmp_path.glob("logs/issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        self.assertIn(issue_comments_command, commands)
        self.assertFalse(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["github_metadata"]["status"], "failure_commented")
        self.assertIn("Command failed", manifest["failure"]["message"])
        self.assertIn("Command failed", comment)

    def test_drain_selects_ready_issue_refresh_candidates_after_local_integration(
        self,
    ) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            command_outputs={
                issue_list_command: [
                    json.dumps([issue_payload(43, ["ready-for-agent"])])
                ]
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            output = io.StringIO()

            with redirect_stdout(output):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(tmp_path)
            artifact_path = next(
                tmp_path.glob("logs/issue-42-*/ready-issue-refresh-analysis.md")
            )
            artifact = artifact_path.read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        analysis_call = next(
            call
            for call in runner.calls
            if call.input_text is not None
            and "Run a read-only Ready issue refresh analysis" in call.input_text
        )
        analysis_index = runner.calls.index(analysis_call)
        close_command = (
            "gh",
            "issue",
            "close",
            "42",
            "-R",
            "example/repo",
            "--reason",
            "completed",
        )
        self.assertIn(issue_list_command, commands)
        self.assertLess(
            commands.index(close_command), commands.index(issue_list_command)
        )
        self.assertLess(commands.index(issue_list_command), analysis_index)
        self.assertIn(
            "Ready issue refresh candidate selection found 1 candidate(s) after "
            "Local integration of #42.",
            output.getvalue(),
        )
        self.assertIn("- #43: Issue 43", output.getvalue())
        self.assertIn(
            "Running read-only Ready issue refresh analysis for #42.", output.getvalue()
        )
        self.assertEqual(
            artifact, READY_ISSUE_REFRESH_ANALYSIS_MARKDOWN.rstrip() + "\n"
        )
        self.assertEqual(manifest["ready_issue_refresh"]["status"], "completed")
        self.assertEqual(
            manifest["ready_issue_refresh"]["candidate_issue_numbers"], [43]
        )
        self.assertEqual(
            manifest["ready_issue_refresh"]["artifact_path"],
            str(artifact_path),
        )
        self.assertIsNone(manifest["ready_issue_refresh"]["failure"])
        mutation = manifest["ready_issue_refresh"]["mutation_results"][0]
        self.assertEqual(mutation["issue_number"], 43)
        self.assertEqual(mutation["status"], "skipped_no_change")
        self.assertEqual(mutation["action"], "no_change")
        self.assertIn("--output-last-message", analysis_call.args)
        self.assertIn(str(artifact_path), analysis_call.args)
        self.assertIn("### Candidate issue #43: Issue 43", analysis_call.input_text)
        self.assertIn("Local integration commit: `merge-sha`", analysis_call.input_text)
        allowed_commands = manifest["sandboxed_issue_access"]["allowed_commands"]
        self.assertIn("gh issue view", allowed_commands)
        self.assertNotIn("gh issue comment", allowed_commands)
        self.assertNotIn("gh issue edit", allowed_commands)
        self.assertNotIn("gh issue close", allowed_commands)
        self.assertNotIn("gh issue create", allowed_commands)
        after_analysis_commands = [
            call.args for call in runner.calls[analysis_index + 1 :]
        ]
        self.assertFalse(
            any(
                command[:3]
                in {
                    ("gh", "issue", "comment"),
                    ("gh", "issue", "edit"),
                    ("gh", "issue", "close"),
                    ("gh", "issue", "create"),
                    ("gh", "issue", "reopen"),
                }
                for command in after_analysis_commands
            )
        )

    def test_ready_issue_refresh_no_candidates_allows_report_without_mutation_plan(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            ready_issue_refresh_analysis_markdown=READY_ISSUE_REFRESH_MISSING_PLAN_MARKDOWN,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(tmp_path)

        self.assertEqual(manifest["ready_issue_refresh"]["status"], "completed")
        self.assertEqual(manifest["ready_issue_refresh"]["candidate_issue_numbers"], [])
        self.assertEqual(manifest["ready_issue_refresh"]["mutation_results"], [])

    def test_drain_applies_ready_issue_refresh_completed_mutation_by_default(
        self,
    ) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        candidate_view_command = (
            "gh",
            "issue",
            "view",
            "43",
            "-R",
            "example/repo",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        candidate_state_command = (
            "gh",
            "issue",
            "view",
            "43",
            "-R",
            "example/repo",
            "--json",
            "state",
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            ready_issue_refresh_analysis_markdown=READY_ISSUE_REFRESH_COMPLETED_MARKDOWN,
            command_outputs={
                issue_list_command: [
                    json.dumps([issue_payload(43, ["ready-for-agent"])])
                ],
                candidate_view_command: [
                    json.dumps(issue_payload(43, ["ready-for-agent"]))
                ],
                candidate_state_command: [json.dumps({"state": "OPEN"})],
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            output = io.StringIO()

            with redirect_stdout(output):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            comment = next(
                tmp_path.glob("logs/issue-42-*/issue-43-comment.md")
            ).read_text(encoding="utf-8")
            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        analysis_call = next(
            call
            for call in runner.calls
            if call.input_text is not None
            and "Run a read-only Ready issue refresh analysis" in call.input_text
        )
        analysis_index = runner.calls.index(analysis_call)
        self.assertTrue(comment.startswith(ralph.AI_READY_ISSUE_REFRESH_DISCLAIMER))
        self.assertIn("Issue #43 is already satisfied by merge-sha.", comment)
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "43",
                "-R",
                "example/repo",
                "--remove-label",
                "ready-for-agent",
            ),
            commands,
        )
        self.assertIn(
            (
                "gh",
                "issue",
                "close",
                "43",
                "-R",
                "example/repo",
                "--reason",
                "completed",
            ),
            commands,
        )
        close_43 = (
            "gh",
            "issue",
            "close",
            "43",
            "-R",
            "example/repo",
            "--reason",
            "completed",
        )
        mutation_commands = [
            call.args
            for call in runner.calls[analysis_index + 1 : commands.index(close_43) + 1]
        ]
        self.assertFalse(any(command[:1] == ("git",) for command in mutation_commands))
        self.assertFalse(
            any(command[:2] == ("codex", "exec") for command in mutation_commands)
        )
        self.assertIn(
            "Applying Ready issue refresh metadata mutations", output.getvalue()
        )
        mutation = manifest["ready_issue_refresh"]["mutation_results"][0]
        self.assertEqual(mutation["issue_number"], 43)
        self.assertEqual(mutation["status"], "completed")
        self.assertEqual(mutation["action"], "completed")
        self.assertEqual(mutation["operations"]["comment"], "created")
        self.assertEqual(mutation["operations"]["closure"], "closed_completed")

    def test_skip_ready_issue_refresh_disables_default_drain_refresh(self) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                drain=True,
                ready_issue_refresh_enabled=False,
                skip_ready_issue_refresh=True,
            )

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "list") for command in commands)
        )
        self.assertFalse(
            any(
                call.input_text is not None
                and "Run a read-only Ready issue refresh analysis" in call.input_text
                for call in runner.calls
            )
        )
        self.assertFalse(manifest["ready_issue_refresh"]["enabled"])
        self.assertEqual(manifest["ready_issue_refresh"]["status"], "not_started")

    def test_targeted_issue_opt_in_runs_ready_issue_refresh_after_integration(
        self,
    ) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            command_outputs={
                issue_list_command: [
                    json.dumps([issue_payload(43, ["ready-for-agent"])])
                ]
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                issue=42,
                ready_issue_refresh_enabled=True,
            )

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertIn(issue_list_command, commands)
        self.assertEqual(manifest["ready_issue_refresh"]["status"], "completed")
        self.assertEqual(
            manifest["ready_issue_refresh"]["candidate_issue_numbers"], [43]
        )

    def test_ready_issue_refresh_needs_triage_mutation_transitions_labels_and_comments(
        self,
    ) -> None:
        candidate_view_command = (
            "gh",
            "issue",
            "view",
            "43",
            "-R",
            "example/repo",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        runner = FakeRunner(
            command_outputs={
                candidate_view_command: [
                    json.dumps(issue_payload(43, ["ready-for-agent"]))
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY),
                delivery_plan=ralph.DeliveryPlan(
                    mode=ralph.TRUNK_MODE,
                    target_branch="main",
                    label=ralph.DELIVERY_TRUNK_LABEL,
                    add_labels=(),
                    remove_labels=(),
                ),
                branch="agent/issue-42-implement-thing",
                worktree_path=tmp_path / "worktrees" / "issue",
                integration_path=tmp_path / "worktrees" / "integration",
                config=loop.config,
            )

            with redirect_stdout(io.StringIO()):
                loop._apply_ready_issue_refresh_mutations(
                    analysis_markdown=READY_ISSUE_REFRESH_NEEDS_TRIAGE_MARKDOWN,
                    candidates=[
                        make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43)
                    ],
                    run_dir=run_dir,
                    manifest=manifest,
                )

            comment = (run_dir / "issue-43-comment.md").read_text(encoding="utf-8")
            payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        commands = [call.args for call in runner.calls]
        self.assertTrue(comment.startswith(ralph.AI_READY_ISSUE_REFRESH_DISCLAIMER))
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "43",
                "-R",
                "example/repo",
                "--add-label",
                "needs-triage",
                "--remove-label",
                "ready-for-agent",
            ),
            commands,
        )
        self.assertIn(
            (
                "gh",
                "issue",
                "comment",
                "43",
                "-R",
                "example/repo",
                "--body-file",
                str(run_dir / "issue-43-comment.md"),
            ),
            commands,
        )
        mutation = payload["ready_issue_refresh"]["mutation_results"][0]
        self.assertEqual(mutation["status"], "completed")
        self.assertEqual(mutation["operations"]["labels"]["added"], ["needs-triage"])
        self.assertEqual(
            mutation["operations"]["labels"]["removed"], ["ready-for-agent"]
        )

    def test_ready_issue_refresh_body_update_preserves_ready_contract(self) -> None:
        candidate_view_command = (
            "gh",
            "issue",
            "view",
            "43",
            "-R",
            "example/repo",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        updated_body = (
            "## What to build\n"
            "Build it with refreshed context.\n\n"
            "## Acceptance criteria\n"
            "- [ ] It works.\n\n"
            "## Blocked by\n"
            "None\n\n"
            "## Current context\n"
            "Blocker #42 is satisfied on the Integration target.\n"
        )
        mutation_markdown = f"""# Ready Issue Refresh Analysis

## Candidate Issue Mutation Plan

```json
{{
  "ready_issue_refresh_mutations": [
    {{
      "issue_number": 43,
      "action": "update",
      "body": {json.dumps(updated_body)}
    }}
  ]
}}
```
"""
        runner = FakeRunner(
            command_outputs={
                candidate_view_command: [
                    json.dumps(issue_payload(43, ["ready-for-agent"]))
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY),
                delivery_plan=ralph.DeliveryPlan(
                    mode=ralph.TRUNK_MODE,
                    target_branch="main",
                    label=ralph.DELIVERY_TRUNK_LABEL,
                    add_labels=(),
                    remove_labels=(),
                ),
                branch="agent/issue-42-implement-thing",
                worktree_path=tmp_path / "worktrees" / "issue",
                integration_path=tmp_path / "worktrees" / "integration",
                config=loop.config,
            )

            with redirect_stdout(io.StringIO()):
                loop._apply_ready_issue_refresh_mutations(
                    analysis_markdown=mutation_markdown,
                    candidates=[
                        make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43)
                    ],
                    run_dir=run_dir,
                    manifest=manifest,
                )

            body = (run_dir / "issue-43-body.md").read_text(encoding="utf-8")
            payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        commands = [call.args for call in runner.calls]
        self.assertEqual(body, updated_body.strip())
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "43",
                "-R",
                "example/repo",
                "--body-file",
                str(run_dir / "issue-43-body.md"),
            ),
            commands,
        )
        mutation = payload["ready_issue_refresh"]["mutation_results"][0]
        self.assertEqual(mutation["operations"]["body"], "updated")

    def test_ready_issue_refresh_mutation_rerun_is_idempotent(self) -> None:
        candidate_view_command = (
            "gh",
            "issue",
            "view",
            "43",
            "-R",
            "example/repo",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        candidate_comments_command = (
            "gh",
            "issue",
            "view",
            "43",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        existing_comment = ready_issue_refresh_body(
            "The issue contract may be stale after merge-sha, but the correct update is unclear."
        )
        runner = FakeRunner(
            command_outputs={
                candidate_view_command: [
                    json.dumps(issue_payload(43, ["needs-triage"]))
                ],
                candidate_comments_command: [
                    json.dumps({"comments": [{"body": existing_comment}]})
                ],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner)
            run_dir = tmp_path / "logs" / "issue-42-test"
            manifest = ralph.RunManifest.for_implementation(
                run_dir=run_dir,
                issue=make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY),
                delivery_plan=ralph.DeliveryPlan(
                    mode=ralph.TRUNK_MODE,
                    target_branch="main",
                    label=ralph.DELIVERY_TRUNK_LABEL,
                    add_labels=(),
                    remove_labels=(),
                ),
                branch="agent/issue-42-implement-thing",
                worktree_path=tmp_path / "worktrees" / "issue",
                integration_path=tmp_path / "worktrees" / "integration",
                config=loop.config,
            )

            with redirect_stdout(io.StringIO()):
                loop._apply_ready_issue_refresh_mutations(
                    analysis_markdown=READY_ISSUE_REFRESH_NEEDS_TRIAGE_MARKDOWN,
                    candidates=[
                        make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY, number=43)
                    ],
                    run_dir=run_dir,
                    manifest=manifest,
                )

            payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )
        mutation = payload["ready_issue_refresh"]["mutation_results"][0]
        self.assertEqual(mutation["operations"]["labels"], "unchanged")
        self.assertEqual(mutation["operations"]["comment"], "already_present")

    def test_ready_issue_refresh_malformed_mutation_json_fails_and_stops_drain(
        self,
    ) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            ready_issue_refresh_analysis_markdown=READY_ISSUE_REFRESH_MALFORMED_MUTATION_MARKDOWN,
            command_outputs={
                issue_list_command: [
                    json.dumps([issue_payload(43, ["ready-for-agent"])])
                ]
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            base_loop = make_loop(tmp_path, runner, drain=True)
            loop = TwoReadyIssueLoop(base_loop.config, runner)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(ralph.ReadyIssueRefreshFailure):
                    loop.run()

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertEqual(loop.ready_calls, 1)
        self.assertFalse(
            any(command[:4] == ("gh", "issue", "view", "43") for command in commands)
        )
        self.assertFalse(
            any(command[:4] == ("gh", "issue", "edit", "43") for command in commands)
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["integration_commit"]["sha"], "merge-sha")
        self.assertEqual(manifest["pushes"]["integration_target"]["status"], "pushed")
        self.assertEqual(manifest["ready_issue_refresh"]["status"], "failed")
        self.assertIn(
            "malformed JSON",
            manifest["ready_issue_refresh"]["failure"]["message"],
        )
        self.assertEqual(manifest["ready_issue_refresh"]["mutation_results"], [])

    def test_ready_issue_refresh_partial_mutation_failure_records_candidate_status_and_stops(
        self,
    ) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        view_43 = (
            "gh",
            "issue",
            "view",
            "43",
            "-R",
            "example/repo",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        view_44 = (
            "gh",
            "issue",
            "view",
            "44",
            "-R",
            "example/repo",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        state_43 = (
            "gh",
            "issue",
            "view",
            "43",
            "-R",
            "example/repo",
            "--json",
            "state",
        )
        fail_edit_44 = (
            "gh",
            "issue",
            "edit",
            "44",
            "-R",
            "example/repo",
            "--add-label",
            "needs-triage",
            "--remove-label",
            "ready-for-agent",
        )
        mutation_markdown = READY_ISSUE_REFRESH_COMPLETED_MARKDOWN.replace(
            "    }\n  ]",
            "    },\n"
            "    {\n"
            '      "issue_number": 44,\n'
            '      "action": "needs_triage",\n'
            '      "comment": "Issue #44 needs maintainer review after merge-sha."\n'
            "    }\n"
            "  ]",
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            ready_issue_refresh_analysis_markdown=mutation_markdown,
            command_outputs={
                issue_list_command: [
                    json.dumps(
                        [
                            issue_payload(43, ["ready-for-agent"]),
                            issue_payload(44, ["ready-for-agent"]),
                        ]
                    )
                ],
                view_43: [json.dumps(issue_payload(43, ["ready-for-agent"]))],
                view_44: [json.dumps(issue_payload(44, ["ready-for-agent"]))],
                state_43: [json.dumps({"state": "OPEN"})],
            },
            fail_commands={fail_edit_44: 1},
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            base_loop = make_loop(tmp_path, runner, drain=True)
            loop = TwoReadyIssueLoop(base_loop.config, runner)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(ralph.ReadyIssueRefreshFailure) as caught:
                    loop.run()

            manifest = load_run_manifest(tmp_path)

        self.assertEqual(loop.ready_calls, 1)
        self.assertIn("Recovery guidance", str(caught.exception))
        self.assertIn("Do not roll back the integrated commit", str(caught.exception))
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["integration_commit"]["sha"], "merge-sha")
        self.assertEqual(manifest["pushes"]["integration_target"]["status"], "pushed")
        self.assertEqual(manifest["ready_issue_refresh"]["status"], "failed")
        self.assertIn("recovery_guidance", manifest["ready_issue_refresh"])
        results = {
            item["issue_number"]: item
            for item in manifest["ready_issue_refresh"]["mutation_results"]
        }
        self.assertEqual(results[43]["status"], "completed")
        self.assertEqual(results[44]["status"], "failed")

    def test_ready_issue_refresh_analysis_failure_stops_drain_after_integration(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_ready_issue_refresh_analysis=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            base_loop = make_loop(tmp_path, runner, drain=True)
            loop = TwoReadyIssueLoop(base_loop.config, runner)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(ralph.ReadyIssueRefreshFailure):
                    loop.run()

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "push", "origin", "HEAD:main"), commands)
        self.assertIn(
            (
                "gh",
                "issue",
                "close",
                "42",
                "-R",
                "example/repo",
                "--reason",
                "completed",
            ),
            commands,
        )
        self.assertEqual(loop.ready_calls, 1)
        self.assertFalse(
            any(command[:4] == ("gh", "issue", "edit", "43") for command in commands)
        )
        self.assertFalse(any(command[:2] == ("git", "reset") for command in commands))
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["integration_commit"]["sha"], "merge-sha")
        self.assertEqual(manifest["pushes"]["integration_target"]["status"], "pushed")
        self.assertEqual(manifest["github_metadata"]["status"], "closed")
        self.assertEqual(manifest["ready_issue_refresh"]["status"], "failed")
        self.assertIn(
            "Command failed",
            manifest["ready_issue_refresh"]["failure"]["message"],
        )
        self.assertIn(
            "Ready issue refresh analysis failed after Local integration of #42",
            manifest["failure"]["message"],
        )

    def test_gitflow_implementation_creates_dev_integrates_and_leaves_issue_open(
        self,
    ) -> None:
        ls_remote = ("git", "ls-remote", "--exit-code", "--heads", "origin", "dev")
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_commands={ls_remote: 2},
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            output = io.StringIO()

            with redirect_stdout(output):
                loop._handle_implementation(issue)

            commands = [call.args for call in runner.calls]
            review_call = next(
                call
                for call in runner.calls
                if call.input_text is not None
                and "Run an Issue completion review" in call.input_text
            )
            review_index = runner.calls.index(review_call)
            merge_index = commands.index(
                ("git", "merge", "--squash", "agent/issue-42-implement-thing")
            )
            self.assertLess(review_index, merge_index)
            self.assertIn(
                ("git", "push", "origin", "origin/main:refs/heads/dev"), commands
            )
            self.assertIn(("git", "push", "origin", "HEAD:dev"), commands)
            self.assertIn(
                (
                    "gh",
                    "issue",
                    "edit",
                    "42",
                    "-R",
                    "example/repo",
                    "--add-label",
                    "agent-integrated",
                    "--remove-label",
                    "agent-running",
                    "--remove-label",
                    "agent-failed",
                    "--remove-label",
                    "agent-merged",
                ),
                commands,
            )
            self.assertFalse(
                any(command[:3] == ("gh", "issue", "close") for command in commands)
            )
            self.assertIn("Issue #42 integrated to dev: merge-sha", output.getvalue())

            comment_path = next(
                (Path(tmp) / "logs").glob("issue-42-*/issue-42-comment.md")
            )
            comment = comment_path.read_text(encoding="utf-8")
            self.assertIn("Ralph Gitflow integration completed.", comment)
            self.assertIn("Target branch: `dev`", comment)
            self.assertIn("## Review package", comment)
            self.assertIn("review-package.html", comment)
            self.assertIn("will stay open until Ralph promotes `dev`", comment)
            manifest = load_run_manifest(tmp_path)
            review_artifact = next(
                (tmp_path / "logs").glob("issue-42-*/issue-completion-review.md")
            )
            review_log = next(
                (tmp_path / "logs").glob(
                    "issue-42-*/codex-issue-completion-review.jsonl"
                )
            )
            self.assertEqual(manifest["issue_completion_review"]["status"], "passed")
            self.assertIs(manifest["issue_completion_review"]["required"], True)
            self.assertEqual(
                manifest["issue_completion_review"]["reasons"],
                ["Agent workflow changes"],
            )
            self.assertEqual(
                manifest["issue_completion_review"]["artifact_path"],
                str(review_artifact),
            )
            self.assertEqual(
                manifest["issue_completion_review"]["log_path"],
                str(review_log),
            )
            package_path = next(
                (tmp_path / "logs").glob("issue-42-*/review-package.html")
            )
            package_log = next(
                (tmp_path / "logs").glob("issue-42-*/codex-review-package.jsonl")
            )
            self.assertEqual(manifest["review_package"]["status"], "passed")
            self.assertEqual(manifest["review_package"]["validation_status"], "passed")
            self.assertEqual(manifest["review_package"]["html_path"], str(package_path))
            self.assertEqual(
                manifest["review_package"]["generator_log_path"],
                str(package_log),
            )
            self.assertEqual(
                manifest["review_package"]["summary"]["changed_file_count"],
                1,
            )

    def test_gitflow_review_package_validation_failure_stops_before_integration(
        self,
    ) -> None:
        invalid_html = REVIEW_PACKAGE_HTML.replace(
            "<h2>QA evidence</h2>",
            '<script src="https://example.com/app.js"></script><h2>QA evidence</h2>',
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            review_package_html=invalid_html,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                manifest_obj = loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertIsNotNone(manifest_obj)
        self.assertFalse(
            any(command[:3] == ("git", "merge", "--squash") for command in commands)
        )
        self.assertNotIn(("git", "push", "origin", "HEAD:dev"), commands)
        self.assertFalse(
            any(
                command[:4] == ("gh", "issue", "edit", "42")
                and "--add-label" in command
                and command[command.index("--add-label") + 1] == "agent-integrated"
                for command in commands
            )
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["review_package"]["status"], "validation_failed")
        self.assertEqual(manifest["review_package"]["validation_status"], "failed")
        self.assertIn("script tag", manifest["review_package"]["failure_reason"])

    def test_gitflow_review_package_generation_failure_stops_before_dev_push(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_review_package=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(command[:3] == ("git", "merge", "--squash") for command in commands)
        )
        self.assertNotIn(("git", "push", "origin", "HEAD:dev"), commands)
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["review_package"]["status"], "failed")
        self.assertIn(
            "Review package generation failed",
            manifest["review_package"]["failure_reason"],
        )

    def test_gitflow_review_package_generator_repo_edits_fail_before_integration(
        self,
    ) -> None:
        runner = FakeRunner(
            status_outputs=[
                " M scripts/ralph.py\n",
                " M scripts/ralph.py\n",
                " M CONTEXT.md\n",
            ],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(command[:3] == ("git", "merge", "--squash") for command in commands)
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["review_package"]["status"], "failed")
        self.assertIn(
            "modified the implementation worktree",
            manifest["review_package"]["failure_reason"],
        )

    def test_exploratory_implementation_pushes_handoff_branch_and_marks_reviewing(
        self,
    ) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        ls_remote = (
            "git",
            "ls-remote",
            "--exit-code",
            "--heads",
            "origin",
            handoff_branch,
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_commands={ls_remote: 2},
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner, delivery_mode=ralph.EXPLORATORY_MODE)
            issue = make_issue({"ready-for-agent"}, EXPLORATORY_IMPLEMENTATION_BODY)
            output = io.StringIO()

            with redirect_stdout(output):
                loop._handle_implementation(issue)

            worktree_path = (
                Path(tmp) / "worktrees" / "agent-exploratory-issue-42-implement-thing"
            )
            commands = [call.args for call in runner.calls]
            self.assertIn(
                (
                    "git",
                    "worktree",
                    "add",
                    "-b",
                    handoff_branch,
                    str(worktree_path),
                    "origin/main",
                ),
                commands,
            )
            self.assertNotIn(
                ("git", "push", "origin", f"origin/main:refs/heads/{handoff_branch}"),
                commands,
            )
            self.assertFalse(
                any(command[:3] == ("git", "merge", "--squash") for command in commands)
            )
            self.assertIn(("git", "push", "origin", f"HEAD:{handoff_branch}"), commands)
            self.assertIn(
                (
                    "gh",
                    "issue",
                    "edit",
                    "42",
                    "-R",
                    "example/repo",
                    "--add-label",
                    "agent-reviewing",
                    "--remove-label",
                    "agent-running",
                    "--remove-label",
                    "agent-failed",
                    "--remove-label",
                    "agent-merged",
                    "--remove-label",
                    "agent-integrated",
                ),
                commands,
            )
            self.assertFalse(
                any(command[:3] == ("gh", "issue", "close") for command in commands)
            )
            self.assertIn(
                f"Issue #42 ready for review on {handoff_branch}: merge-sha",
                output.getvalue(),
            )

            comment_path = next(
                (Path(tmp) / "logs").glob("issue-42-*/issue-42-comment.md")
            )
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(Path(tmp))
            self.assertIn("Ralph exploratory handoff completed.", comment)
            self.assertIn(f"Target branch: `{handoff_branch}`", comment)
            self.assertEqual(manifest["delivery_mode"], "exploratory")
            self.assertEqual(manifest["integration_target"], handoff_branch)
            self.assertEqual(manifest["branches"]["issue"], handoff_branch)
            self.assertEqual(manifest["github_metadata"]["status"], "marked_reviewing")

    def test_exploratory_marimo_media_failure_stops_before_handoff(
        self,
    ) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        ls_remote = (
            "git",
            "ls-remote",
            "--exit-code",
            "--heads",
            "origin",
            handoff_branch,
        )
        runner = FakeRunner(
            status_outputs=[
                " M backend-services/marimo/notebooks/gas_market_prices.py\n",
                " M backend-services/marimo/notebooks/gas_market_prices.py\n",
            ],
            diff_outputs=["backend-services/marimo/notebooks/gas_market_prices.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_commands={ls_remote: 2},
            fail_marimo_review_media=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.EXPLORATORY_MODE)
            issue = make_issue({"ready-for-agent"}, EXPLORATORY_IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                manifest_obj = loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertIsNotNone(manifest_obj)
        self.assertFalse(
            any(
                command == ("git", "push", "origin", f"HEAD:{handoff_branch}")
                for command in commands
            )
        )
        self.assertFalse(
            any(
                command[:6] == ("gh", "issue", "edit", "42", "-R", "example/repo")
                and "agent-reviewing" in command
                for command in commands
            )
        )
        media_call = next(
            call
            for call in runner.calls
            if call.args[:6]
            == (
                "uv",
                "run",
                "--with",
                "playwright",
                "python",
                "scripts/review_promoted_dashboards.py",
            )
        )
        self.assertEqual(media_call.cwd.name, "marimo")
        self.assertIn("--videos", media_call.args)
        self.assertIn("--route", media_call.args)
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["review_package"]["status"], "failed")
        self.assertIn(
            "Marimo Review package media capture failed",
            manifest["review_package"]["failure_reason"],
        )

    def test_exploratory_marimo_media_success_records_handoff_evidence(
        self,
    ) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        ls_remote = (
            "git",
            "ls-remote",
            "--exit-code",
            "--heads",
            "origin",
            handoff_branch,
        )
        runner = FakeRunner(
            status_outputs=[
                " M backend-services/marimo/notebooks/gas_market_prices.py\n",
                " M backend-services/marimo/notebooks/gas_market_prices.py\n",
            ],
            diff_outputs=["backend-services/marimo/notebooks/gas_market_prices.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_commands={ls_remote: 2},
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.EXPLORATORY_MODE)
            issue = make_issue({"ready-for-agent"}, EXPLORATORY_IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)
            comment_path = next(tmp_path.glob("logs/issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "push", "origin", f"HEAD:{handoff_branch}"), commands)
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual(manifest["review_package"]["status"], "media_captured")
        self.assertEqual(
            manifest["review_package"]["validation_status"], "not_required"
        )
        self.assertEqual(
            [
                (item["route"], item["viewport"])
                for item in manifest["review_package"]["media"]
            ],
            [
                ("/marimo/gas_market_prices/", "desktop"),
                ("/marimo/gas_market_prices/", "narrow"),
            ],
        )
        self.assertIn("## Review package", comment)
        self.assertIn("Review package media captured.", comment)
        self.assertNotIn("- HTML:", comment)
        self.assertIn("/marimo/gas_market_prices/", comment)

    def test_exploratory_operator_smoke_runs_after_push_and_records_evidence(
        self,
    ) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        ls_remote = (
            "git",
            "ls-remote",
            "--exit-code",
            "--heads",
            "origin",
            handoff_branch,
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_commands={ls_remote: 2},
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.EXPLORATORY_MODE)
            issue = make_issue({"ready-for-agent"}, OPERATOR_SMOKE_BODY)

            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(issue)

            worktree_path = (
                tmp_path / "worktrees" / "agent-exploratory-issue-42-implement-thing"
            )
            smoke_command = (
                str(
                    worktree_path
                    / ralph.OPERATOR_SMOKE_EC2_RUN_WORKER_PLACEMENT_COMMAND
                ),
            )
            commands = [call.args for call in runner.calls]
            push_index = commands.index(
                ("git", "push", "origin", f"HEAD:{handoff_branch}")
            )
            smoke_index = commands.index(smoke_command)
            reviewing_index = commands.index(
                (
                    "gh",
                    "issue",
                    "edit",
                    "42",
                    "-R",
                    "example/repo",
                    "--add-label",
                    "agent-reviewing",
                    "--remove-label",
                    "agent-running",
                    "--remove-label",
                    "agent-failed",
                    "--remove-label",
                    "agent-merged",
                    "--remove-label",
                    "agent-integrated",
                )
            )
            comment_path = next(tmp_path.glob("logs/issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(tmp_path)

        smoke_call = runner.calls[smoke_index]
        self.assertLess(push_index, smoke_index)
        self.assertLess(smoke_index, reviewing_index)
        self.assertEqual(
            smoke_call.cwd,
            worktree_path / ralph.OPERATOR_SMOKE_EC2_RUN_WORKER_PLACEMENT_CWD,
        )
        self.assertEqual(smoke_call.timeout_seconds, 120)
        self.assertEqual(manifest["operator_smoke"]["status"], "succeeded")
        self.assertEqual(
            manifest["operator_smoke"]["smoke_id"],
            "ec2-run-worker-placement",
        )
        self.assertEqual(manifest["operator_smoke"]["exit_status"], 0)
        self.assertIsNotNone(manifest["operator_smoke"]["evidence_path"])
        self.assertIn("## Operator smoke", comment)
        self.assertIn("Smoke id: `ec2-run-worker-placement`", comment)
        self.assertIn(manifest["operator_smoke"]["evidence_path"], comment)

    def test_operator_smoke_failure_marks_failed_without_reviewing_transition(
        self,
    ) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        ls_remote = (
            "git",
            "ls-remote",
            "--exit-code",
            "--heads",
            "origin",
            handoff_branch,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            worktree_path = (
                tmp_path / "worktrees" / "agent-exploratory-issue-42-implement-thing"
            )
            smoke_command = (
                str(
                    worktree_path
                    / ralph.OPERATOR_SMOKE_EC2_RUN_WORKER_PLACEMENT_COMMAND
                ),
            )
            runner = FakeRunner(
                status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
                diff_outputs=["scripts/ralph.py\n"],
                rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
                fail_commands={ls_remote: 2, smoke_command: 1},
            )
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.EXPLORATORY_MODE)
            issue = make_issue({"ready-for-agent"}, OPERATOR_SMOKE_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(issue)

            comment_path = next(tmp_path.glob("logs/issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "push", "origin", f"HEAD:{handoff_branch}"), commands)
        self.assertIn(smoke_command, commands)
        self.assertFalse(
            any(
                command[:6] == ("gh", "issue", "edit", "42", "-R", "example/repo")
                and "agent-reviewing" in command
                for command in commands
            )
        )
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "42",
                "-R",
                "example/repo",
                "--add-label",
                "agent-failed",
                "--remove-label",
                "agent-running",
                "--remove-label",
                "ready-for-agent",
            ),
            commands,
        )
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "remove") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("git", "branch", "-D") for command in commands)
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["operator_smoke"]["status"], "failed")
        self.assertEqual(manifest["operator_smoke"]["exit_status"], 1)
        self.assertEqual(manifest["failure"]["type"], ralph.OPERATOR_SMOKE_FAILURE_TYPE)
        self.assertIn("Operator smoke `ec2-run-worker-placement` failed", comment)

    def test_operator_smoke_timeout_records_timeout_without_reviewing_transition(
        self,
    ) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        ls_remote = (
            "git",
            "ls-remote",
            "--exit-code",
            "--heads",
            "origin",
            handoff_branch,
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            worktree_path = (
                tmp_path / "worktrees" / "agent-exploratory-issue-42-implement-thing"
            )
            smoke_command = (
                str(
                    worktree_path
                    / ralph.OPERATOR_SMOKE_EC2_RUN_WORKER_PLACEMENT_COMMAND
                ),
            )
            runner = FakeRunner(
                status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
                diff_outputs=["scripts/ralph.py\n"],
                rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
                fail_commands={ls_remote: 2},
                timeout_commands={smoke_command},
            )
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.EXPLORATORY_MODE)
            issue = make_issue({"ready-for-agent"}, OPERATOR_SMOKE_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(issue)

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(
                command[:6] == ("gh", "issue", "edit", "42", "-R", "example/repo")
                and "agent-reviewing" in command
                for command in commands
            )
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["operator_smoke"]["status"], "timed_out")
        self.assertEqual(manifest["operator_smoke"]["exit_status"], 124)
        self.assertEqual(
            manifest["failure"]["type"],
            ralph.OPERATOR_SMOKE_TIMEOUT_FAILURE_TYPE,
        )

    def test_exploratory_implementation_fails_if_remote_branch_exists(self) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        ls_remote = (
            "git",
            "ls-remote",
            "--exit-code",
            "--heads",
            "origin",
            handoff_branch,
        )
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.EXPLORATORY_MODE)
            issue = make_issue({"ready-for-agent"}, EXPLORATORY_IMPLEMENTATION_BODY)

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(issue)

            comment_path = next(tmp_path.glob("logs/issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertIn(ls_remote, commands)
        self.assertFalse(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "add") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("git", "push", "origin") for command in commands)
        )
        self.assertIn(
            f"Remote Exploratory branch already exists: origin/{handoff_branch}",
            comment,
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["github_metadata"]["status"], "failure_commented")

    def test_drain_reports_ready_issue_refresh_after_exploratory_handoff(self) -> None:
        handoff_branch = "agent/exploratory/issue-42-implement-thing"
        ls_remote = (
            "git",
            "ls-remote",
            "--exit-code",
            "--heads",
            "origin",
            handoff_branch,
        )
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            command_outputs={
                issue_list_command: [
                    json.dumps([issue_payload(43, ["ready-for-agent"])])
                ]
            },
            fail_commands={ls_remote: 2},
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(
                Path(tmp),
                runner,
                delivery_mode=ralph.EXPLORATORY_MODE,
                drain=True,
            )
            output = io.StringIO()

            with redirect_stdout(output):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, EXPLORATORY_IMPLEMENTATION_BODY)
                )

        commands = [call.args for call in runner.calls]
        reviewing_command = (
            "gh",
            "issue",
            "edit",
            "42",
            "-R",
            "example/repo",
            "--add-label",
            "agent-reviewing",
            "--remove-label",
            "agent-running",
            "--remove-label",
            "agent-failed",
            "--remove-label",
            "agent-merged",
            "--remove-label",
            "agent-integrated",
        )
        self.assertIn(issue_list_command, commands)
        self.assertLess(
            commands.index(reviewing_command), commands.index(issue_list_command)
        )
        self.assertIn(
            "Ready issue refresh candidate selection found 1 candidate(s) after "
            "Exploratory handoff of #42.",
            output.getvalue(),
        )

    def test_gitflow_implementation_syncs_dev_with_main_before_issue_branch(
        self,
    ) -> None:
        ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "origin/main",
            "origin/dev",
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["sync-sha\n", "base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_commands={ancestor_command: 1},
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner, delivery_mode=ralph.GITFLOW_MODE)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            output = io.StringIO()

            with redirect_stdout(output):
                loop._handle_implementation(issue)

            worktrees = Path(tmp) / "worktrees"
            sync_path = worktrees / "agent-sync-main-into-dev"
            issue_path = worktrees / "agent-issue-42-implement-thing"

        commands = [call.args for call in runner.calls]
        sync_push = ("git", "push", "origin", "HEAD:dev")
        issue_worktree = (
            "git",
            "worktree",
            "add",
            "-b",
            "agent/issue-42-implement-thing",
            str(issue_path),
            "origin/dev",
        )
        self.assertIn(
            ("git", "worktree", "add", "--detach", str(sync_path), "origin/dev"),
            commands,
        )
        self.assertIn(
            ("git", "merge", "--no-ff", "origin/main", "-m", "Sync main into dev"),
            commands,
        )
        self.assertLess(commands.index(sync_push), commands.index(issue_worktree))
        self.assertIn(
            ("git", "worktree", "remove", str(sync_path)),
            commands,
        )
        self.assertIn("Syncing origin/main into origin/dev", output.getvalue())

    def test_gitflow_branch_sync_conflict_records_manifest_and_stops_before_claim(
        self,
    ) -> None:
        ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "origin/main",
            "origin/dev",
        )
        merge_command = (
            "git",
            "merge",
            "--no-ff",
            "origin/main",
            "-m",
            "Sync main into dev",
        )
        runner = FakeRunner(
            diff_outputs=["docs/conflicted.md\nscripts/ralph.py\n"],
            fail_commands={
                ancestor_command: 1,
                merge_command: 1,
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)
            sync_path = tmp_path / "worktrees" / "agent-sync-main-into-dev"
            output = io.StringIO()

            with self.assertRaises(ralph.BranchSyncFailure):
                with redirect_stdout(output), redirect_stderr(io.StringIO()):
                    loop._handle_implementation(
                        make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                    )

            manifest = load_run_manifest(tmp_path)
            merge_log = next(
                (tmp_path / "logs").glob("issue-42-*/git-merge-main-into-dev.log")
            )

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertEqual(manifest["github_metadata"]["status"], "not_started")
        self.assertEqual(manifest["branch_sync"]["status"], "failed")
        self.assertEqual(manifest["branch_sync"]["failure_type"], "merge_conflict")
        self.assertEqual(
            manifest["branch_sync"]["conflicted_files"],
            ["docs/conflicted.md", "scripts/ralph.py"],
        )
        self.assertEqual(manifest["branch_sync"]["worktree_path"], str(sync_path))
        self.assertEqual(manifest["paths"]["branch_sync_worktree"], str(sync_path))
        self.assertEqual(manifest["branch_sync"]["log_path"], str(merge_log))
        self.assertEqual(manifest["failure"]["log_path"], str(merge_log))
        self.assertIn(
            "git worktree remove --force", manifest["branch_sync"]["recovery_guidance"]
        )
        self.assertIn("Syncing origin/main into origin/dev", output.getvalue())

    def test_stale_branch_sync_worktree_stops_before_claim_with_guidance(self) -> None:
        ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "origin/main",
            "origin/dev",
        )
        runner = FakeRunner(fail_commands={ancestor_command: 1})
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, delivery_mode=ralph.GITFLOW_MODE)
            sync_path = tmp_path / "worktrees" / "agent-sync-main-into-dev"
            sync_path.mkdir(parents=True)

            with self.assertRaises(ralph.BranchSyncFailure):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._handle_implementation(
                        make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                    )

            manifest = load_run_manifest(tmp_path)

        commands = [call.args for call in runner.calls]
        self.assertNotIn(
            ("git", "worktree", "add", "--detach", str(sync_path), "origin/dev"),
            commands,
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertEqual(manifest["github_metadata"]["status"], "not_started")
        self.assertEqual(manifest["branch_sync"]["status"], "failed")
        self.assertEqual(manifest["branch_sync"]["failure_type"], "stale_worktree")
        self.assertEqual(manifest["branch_sync"]["worktree_path"], str(sync_path))
        self.assertIn(
            "existing branch-sync worktree",
            manifest["branch_sync"]["recovery_guidance"],
        )

    def test_branch_sync_conflict_stops_drain_without_repeated_ready_issue_failures(
        self,
    ) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "origin/main",
            "origin/dev",
        )
        merge_command = (
            "git",
            "merge",
            "--no-ff",
            "origin/main",
            "-m",
            "Sync main into dev",
        )
        runner = FakeRunner(
            diff_outputs=["docs/conflicted.md\n"],
            command_outputs={
                issue_list_command: [
                    json.dumps(
                        [
                            issue_payload(42, ["ready-for-agent"]),
                            issue_payload(43, ["ready-for-agent"]),
                        ]
                    )
                ]
            },
            fail_commands={
                ancestor_command: 1,
                merge_command: 1,
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            base_loop = make_loop(
                tmp_path,
                runner,
                delivery_mode=ralph.GITFLOW_MODE,
                drain=True,
                max_issues=0,
            )
            loop = NoValidationRalphLoop(base_loop.config, runner)

            with self.assertRaises(ralph.BranchSyncFailure):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop.run()

            manifest = load_run_manifest(tmp_path)
            issue_43_runs = list((tmp_path / "logs").glob("issue-43-*"))

        commands = [call.args for call in runner.calls]
        issue_edits = [
            command for command in commands if command[:3] == ("gh", "issue", "edit")
        ]
        self.assertEqual(issue_edits, [])
        self.assertEqual(commands.count(issue_list_command), 1)
        self.assertEqual(issue_43_runs, [])
        self.assertEqual(manifest["branch_sync"]["failure_type"], "merge_conflict")

    def test_base_drift_rebases_and_reruns_qa_before_squash_merge(self) -> None:
        runner = FakeRunner(
            status_outputs=[
                " M scripts/ralph.py\n",
                " M scripts/ralph.py\n",
                " M scripts/ralph.py\n",
            ],
            diff_outputs=["scripts/ralph.py\n", "scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "new-base-sha\n", "merge-sha\n"],
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner)
            with redirect_stdout(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "rebase", "origin/main"), commands)
        qa_commands = [
            command for command in commands if command == ("make", "run-prek")
        ]
        self.assertEqual(len(qa_commands), 2)
        self.assertIn(
            (
                "git",
                "commit",
                "-m",
                "Apply post-rebase QA updates for issue #42: Implement thing",
            ),
            commands,
        )

    def test_failed_qa_persists_failed_manifest_state(self) -> None:
        qa_command = ("make", "run-prek")
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n"]
            * ralph.DEFAULT_CODEX_ATTEMPT_BUDGET,
            rev_parse_outputs=["base-sha\n"],
            fail_commands={qa_command},
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(Path(tmp))

        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["github_metadata"]["status"], "failure_commented")
        self.assertIn("Command failed", manifest["failure"]["message"])
        failed_qa = [
            result
            for result in manifest["qa_results"]
            if result["name"] == "Ralph loop Commit check"
            and result["status"] == "failed"
        ]
        self.assertGreaterEqual(len(failed_qa), 1)
        self.assertTrue(
            any(event["stage"] == "qa_failed" for event in manifest["events"])
        )

    def test_aemo_etl_commit_check_failure_stops_before_integration_test(self) -> None:
        qa_command = ("make", "run-prek")
        changed_file = (
            " M backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py\n"
        )
        runner = FakeRunner(
            status_outputs=[changed_file] * ralph.DEFAULT_CODEX_ATTEMPT_BUDGET,
            rev_parse_outputs=["base-sha\n"],
            fail_commands={qa_command},
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._handle_implementation(
                    make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                )

            manifest = load_run_manifest(Path(tmp))

        commands = [call.args for call in runner.calls]
        self.assertIn(qa_command, commands)
        self.assertNotIn(("make", "integration-test"), commands)
        failed_qa = [
            result
            for result in manifest["qa_results"]
            if result["name"] == "aemo-etl Commit check"
            and result["status"] == "failed"
        ]
        self.assertGreaterEqual(len(failed_qa), 1)

    def test_promotion_merges_dev_and_closes_verified_integrated_issue(self) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_comments_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        target_ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "abc1234",
            "origin/main",
        )
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )
        issue_payload = [
            {
                "number": 42,
                "title": "Implement thing",
                "body": IMPLEMENTATION_BODY,
                "labels": [{"name": "agent-integrated"}],
                "createdAt": "2026-04-30T00:00:00Z",
                "updatedAt": "2026-04-30T00:00:00Z",
                "url": "https://github.com/example/repo/issues/42",
                "comments": [],
                "author": {"login": "reporter"},
            }
        ]
        comments_payload = {
            "comments": [
                {
                    "body": "\n".join(
                        [
                            "Ralph Gitflow integration completed.",
                            "",
                            "Commit: `abc1234`",
                        ]
                    )
                }
            ]
        }
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            command_outputs={
                issue_list_command: [json.dumps(issue_payload)],
                issue_comments_command: [json.dumps(comments_payload)],
                promotion_log_command: [
                    (
                        "abc1234\x00Ralph Local integration for issue 42\n"
                        "def5678\x00Manual follow-up after issue integration\n"
                    )
                ],
            },
            fail_commands={target_ancestor_command: 1},
        )

        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner, promote=True)
            output = io.StringIO()
            with redirect_stdout(output):
                loop._promote()

            comment_path = next(
                (Path(tmp) / "logs").glob("promote-*/issue-42-comment.md")
            )
            comment = comment_path.read_text(encoding="utf-8")
            artifact_path = next(
                (Path(tmp) / "logs").glob("promote-*/post-promotion-review.md")
            )
            artifact = artifact_path.read_text(encoding="utf-8")
            followup_body_path = next(
                (Path(tmp) / "logs").glob(
                    "promote-*/post-promotion-followup-ralph-post-promotion-followup-*.md"
                )
            )
            followup_body = followup_body_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(Path(tmp), run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        source_path = Path(tmp) / "worktrees" / "agent-promote-source-dev-to-main"
        promote_path = Path(tmp) / "worktrees" / "agent-promote-dev-to-main"
        source_worktree = (
            "git",
            "worktree",
            "add",
            "--detach",
            str(source_path),
            "source-sha",
        )
        promote_worktree = (
            "git",
            "worktree",
            "add",
            "--detach",
            str(promote_path),
            "origin/main",
        )
        qa_command = ("make", "run-prek")
        source_worktree_index = commands.index(source_worktree)
        qa_index = commands.index(qa_command)
        promote_worktree_index = commands.index(promote_worktree)
        self.assertLess(source_worktree_index, qa_index)
        self.assertLess(qa_index, promote_worktree_index)
        self.assertEqual(runner.calls[qa_index].cwd, source_path / "tools/ralph-loop")
        self.assertIn(
            ("git", "merge", "--no-ff", "source-sha", "-m", "Promote dev to main"),
            commands,
        )
        self.assertIn(("git", "push", "origin", "HEAD:main"), commands)
        self.assertIn(("git", "push", "origin", "HEAD:dev"), commands)
        edit_command = (
            "gh",
            "issue",
            "edit",
            "42",
            "-R",
            "example/repo",
            "--add-label",
            "agent-merged",
            "--remove-label",
            "agent-integrated",
            "--remove-label",
            "agent-reviewing",
            "--remove-label",
            "agent-running",
            "--remove-label",
            "agent-failed",
        )
        close_command = (
            "gh",
            "issue",
            "close",
            "42",
            "-R",
            "example/repo",
            "--reason",
            "completed",
        )
        self.assertIn(edit_command, commands)
        self.assertIn(close_command, commands)
        self.assertNotIn(("scripts/aemo-etl-e2e", "run"), commands)
        review_command = tuple(
            ralph.codex_exec_command(
                promote_path,
                output_last_message=artifact_path,
            )
        )
        review_index = commands.index(review_command)
        cleanup_index = commands.index(("git", "worktree", "remove", str(promote_path)))
        self.assertLess(
            commands.index(("git", "push", "origin", "HEAD:main")),
            review_index,
        )
        self.assertLess(
            commands.index(("git", "push", "origin", "HEAD:dev")),
            review_index,
        )
        self.assertLess(commands.index(edit_command), review_index)
        self.assertLess(commands.index(close_command), review_index)
        self.assertLess(review_index, cleanup_index)
        self.assertEqual(runner.calls[review_index].cwd, promote_path)
        self.assertIn("--output-last-message", runner.calls[review_index].args)
        self.assertIn(
            "Run a Post-promotion review", runner.calls[review_index].input_text
        )
        self.assertIn("## Learnings", runner.calls[review_index].input_text)
        self.assertIn(
            "## Recovery and Consistency Guidance",
            runner.calls[review_index].input_text,
        )
        self.assertIn(
            "## Follow-up GitHub Issue Drafts", runner.calls[review_index].input_text
        )
        self.assertIn(
            "Do not create the follow-up issues yourself.",
            runner.calls[review_index].input_text,
        )
        self.assertIn(
            "run archive replay commands",
            runner.calls[review_index].input_text,
        )
        self.assertIn(
            "Source-table archive replay recovery guidance",
            runner.calls[review_index].input_text,
        )
        self.assertIn(
            "Automatic validated follow-up issue creation is enabled.",
            runner.calls[review_index].input_text,
        )
        self.assertLess(
            runner.calls[review_index].input_text.index(
                "## Recovery and Consistency Guidance"
            ),
            runner.calls[review_index].input_text.index(
                "## Follow-up GitHub Issue Drafts"
            ),
        )
        self.assertIn(
            "Promotion outcome: `succeeded`",
            runner.calls[review_index].input_text,
        )
        self.assertIn("Promotion error: `None`", runner.calls[review_index].input_text)
        self.assertIn(
            "`abc1234` Ralph Local integration for issue 42 - "
            "verified issue evidence commit for #42 Implement thing",
            runner.calls[review_index].input_text,
        )
        self.assertIn(
            "`def5678` Manual follow-up after issue integration - "
            "unverified Promotion commit",
            runner.calls[review_index].input_text,
        )
        self.assertIn(
            "Promoted files (full Promotion range, not per-issue ownership):",
            runner.calls[review_index].input_text,
        )
        self.assertIn(POST_PROMOTION_REVIEW_MARKDOWN.strip(), output.getvalue())
        self.assertEqual(artifact, POST_PROMOTION_REVIEW_MARKDOWN.rstrip() + "\n")
        self.assertIn('"finding_id": "harden-promotion-evidence-checks"', artifact)
        self.assertIn('"title": "Harden Promotion evidence checks"', artifact)
        self.assertIn("## Acceptance criteria", artifact)
        self.assertIn('"labels": ["enhancement", "delivery-gitflow"]', artifact)
        self.assertIn("## Ralph source", followup_body)
        self.assertIn(
            "Source marker: `ralph-post-promotion-followup:promotion-sha:harden-promotion-evidence-checks`",
            followup_body,
        )
        self.assertIn("Ralph promotion completed.", comment)
        self.assertIn("Promotion commit: `promotion-sha`", comment)
        self.assertIn("Integrated commit: `abc1234`", comment)
        self.assertIn("## Promotion file inventory", comment)
        self.assertIn(
            "These files are from the full Promotion range, not only issue #42.",
            comment,
        )
        self.assertEqual(manifest["run_kind"], "promotion")
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual(manifest["delivery_mode"], "gitflow")
        self.assertEqual(manifest["source_branch"], "dev")
        self.assertEqual(manifest["integration_target"], "main")
        self.assertEqual(
            manifest["paths"]["promotion_source_worktree"],
            str(source_path),
        )
        self.assertEqual(manifest["promotion_worktree_preflight"]["status"], "passed")
        self.assertEqual(
            [
                check["role"]
                for check in manifest["promotion_worktree_preflight"]["checks"]
            ],
            ["source", "target"],
        )
        self.assertEqual(
            manifest["source_tree"],
            {
                "branch": "dev",
                "revision": "source-sha",
                "worktree": str(source_path),
            },
        )
        self.assertEqual(manifest["promotion_commit"]["sha"], "promotion-sha")
        self.assertEqual(
            manifest["promotion_commit_inventory"]["base_ref"],
            "origin/main",
        )
        self.assertEqual(
            manifest["promotion_commit_inventory"]["head_ref"],
            "source-sha",
        )
        self.assertEqual(manifest["promotion_commit_inventory"]["status"], "classified")
        self.assertEqual(
            manifest["promotion_commit_inventory"]["commits"],
            [
                {
                    "sha": "abc1234",
                    "subject": "Ralph Local integration for issue 42",
                    "verified_local_integration": True,
                    "classification": "verified_local_integration",
                    "issue": {
                        "number": 42,
                        "title": "Implement thing",
                        "url": "https://github.com/example/repo/issues/42",
                    },
                    "integrated_commit": "abc1234",
                },
                {
                    "sha": "def5678",
                    "subject": "Manual follow-up after issue integration",
                    "verified_local_integration": False,
                    "classification": "unverified_promotion_commit",
                },
            ],
        )
        self.assertEqual(manifest["post_promotion_review"]["status"], "completed")
        self.assertIn(
            "codex-post-promotion-review.jsonl",
            manifest["post_promotion_review"]["log_path"],
        )
        self.assertEqual(
            manifest["post_promotion_review"]["artifact_path"],
            str(artifact_path),
        )
        allowed_commands = manifest["sandboxed_issue_access"]["allowed_commands"]
        self.assertIn("gh issue view", allowed_commands)
        self.assertNotIn("gh issue comment", allowed_commands)
        self.assertNotIn("gh issue edit", allowed_commands)
        self.assertNotIn("gh issue close", allowed_commands)
        self.assertNotIn("gh issue create", allowed_commands)
        create_commands = [
            command for command in commands if command[:3] == ("gh", "issue", "create")
        ]
        self.assertEqual(len(create_commands), 1)
        create_index = commands.index(create_commands[0])
        self.assertLess(review_index, create_index)
        self.assertLess(create_index, cleanup_index)
        self.assertIn("--label", create_commands[0])
        self.assertIn("ready-for-agent", create_commands[0])
        self.assertIn("enhancement", create_commands[0])
        self.assertIn("delivery-gitflow", create_commands[0])
        self.assertEqual(manifest["post_promotion_followups"]["status"], "completed")
        self.assertEqual(
            manifest["post_promotion_followups"]["created"][0]["url"],
            "https://github.com/example/repo/issues/99",
        )
        self.assertEqual(
            manifest["post_promotion_followups"]["created"][0]["source_marker"],
            "ralph-post-promotion-followup:promotion-sha:harden-promotion-evidence-checks",
        )
        self.assertEqual(manifest["post_promotion_followups"]["duplicates"], [])
        self.assertEqual(
            manifest["post_promotion_followups"]["validation_downgrades"], []
        )
        self.assertEqual(manifest["post_promotion_followups"]["failures"], [])
        self.assertEqual(manifest["pushes"]["promotion_target"]["status"], "pushed")
        self.assertEqual(manifest["pushes"]["source_branch_sync"]["status"], "pushed")
        self.assertEqual(manifest["github_metadata"]["issues"][0]["number"], 42)
        self.assertEqual(
            manifest["github_metadata"]["issues"][0]["integrated_commit"],
            "abc1234",
        )
        self.assertEqual(
            manifest["github_metadata"]["issues"][0]["metadata_status"],
            "closed",
        )
        self.assertFalse(manifest["ready_issue_refresh"]["enabled"])
        self.assertEqual(manifest["ready_issue_refresh"]["status"], "skipped_disabled")

    def test_stale_promotion_source_worktree_stops_before_qa_or_push(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo_path = tmp_path / "repo"
            source_path = tmp_path / "worktrees" / "agent-promote-source-dev-to-main"
            source_path.mkdir(parents=True)
            runner = FakeRunner(
                diff_outputs=["scripts/ralph.py\n"],
                rev_parse_outputs=["source-sha\n"],
                command_outputs={
                    ("git", "worktree", "list", "--porcelain"): [
                        "\n".join(
                            [
                                f"worktree {repo_path}",
                                "HEAD source-sha",
                                "branch refs/heads/dev",
                                "",
                                f"worktree {source_path}",
                                "HEAD stale-sha",
                                "detached",
                                "",
                            ]
                        )
                    ]
                },
            )
            loop = make_loop(tmp_path, runner, promote=True)

            with self.assertRaises(ralph.RalphError):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        self.assertNotIn(
            ("git", "worktree", "add", "--detach", str(source_path), "source-sha"),
            commands,
        )
        self.assertFalse(any(command == ("make", "run-prek") for command in commands))
        self.assertFalse(
            any(command[:3] == ("git", "push", "origin") for command in commands)
        )
        preflight = manifest["promotion_worktree_preflight"]
        self.assertEqual(preflight["status"], "failed")
        self.assertEqual(preflight["failure_type"], "stale_worktree")
        self.assertIn(str(source_path), preflight["recovery_guidance"])
        self.assertIn("git worktree remove", preflight["recovery_guidance"])
        source_check = preflight["checks"][0]
        self.assertEqual(source_check["role"], "source")
        self.assertTrue(source_check["exists"])
        self.assertTrue(source_check["registered"])
        self.assertEqual(source_check["head"], "stale-sha")
        self.assertFalse(source_check["dirty"])
        self.assertEqual(manifest["qa_results"], [])
        self.assertEqual(manifest["promotion_commit"], None)
        self.assertEqual(manifest["pushes"], {})

    def test_stale_promotion_target_worktree_stops_before_worktree_creation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo_path = tmp_path / "repo"
            source_path = tmp_path / "worktrees" / "agent-promote-source-dev-to-main"
            promote_path = tmp_path / "worktrees" / "agent-promote-dev-to-main"
            promote_path.mkdir(parents=True)
            runner = FakeRunner(
                diff_outputs=["scripts/ralph.py\n"],
                rev_parse_outputs=["source-sha\n"],
                command_outputs={
                    ("git", "worktree", "list", "--porcelain"): [
                        "\n".join(
                            [
                                f"worktree {repo_path}",
                                "HEAD source-sha",
                                "branch refs/heads/dev",
                                "",
                                f"worktree {promote_path}",
                                "HEAD stale-target-sha",
                                "detached",
                                "",
                            ]
                        )
                    ]
                },
            )
            loop = make_loop(tmp_path, runner, promote=True)

            with self.assertRaises(ralph.RalphError):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        self.assertNotIn(
            ("git", "worktree", "add", "--detach", str(source_path), "source-sha"),
            commands,
        )
        self.assertNotIn(
            ("git", "worktree", "add", "--detach", str(promote_path), "origin/main"),
            commands,
        )
        preflight = manifest["promotion_worktree_preflight"]
        self.assertEqual(preflight["status"], "failed")
        self.assertEqual(preflight["failure_type"], "stale_worktree")
        self.assertEqual(preflight["checks"][1]["role"], "target")
        self.assertEqual(preflight["checks"][1]["head"], "stale-target-sha")
        self.assertIn(str(promote_path), preflight["recovery_guidance"])

    def test_promotion_records_distinct_metadata_command_logs_for_each_issue(
        self,
    ) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_42_comments_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        issue_43_comments_command = (
            "gh",
            "issue",
            "view",
            "43",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        issue_42_target_ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "abc1234",
            "origin/main",
        )
        issue_43_target_ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "def5678",
            "origin/main",
        )
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )

        def integration_comments(commit_sha: str) -> str:
            return json.dumps(
                {
                    "comments": [
                        {
                            "body": "\n".join(
                                [
                                    "Ralph Gitflow integration completed.",
                                    "",
                                    f"Commit: `{commit_sha}`",
                                ]
                            )
                        }
                    ]
                }
            )

        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            command_outputs={
                issue_list_command: [
                    json.dumps(
                        [
                            issue_payload(42, ["agent-integrated"]),
                            issue_payload(43, ["agent-integrated"]),
                        ]
                    )
                ],
                issue_42_comments_command: [integration_comments("abc1234")],
                issue_43_comments_command: [integration_comments("def5678")],
                promotion_log_command: [
                    (
                        "abc1234\x00Ralph Local integration for issue 42\n"
                        "def5678\x00Ralph Local integration for issue 43\n"
                    )
                ],
            },
            fail_commands={
                issue_42_target_ancestor_command: 1,
                issue_43_target_ancestor_command: 1,
            },
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")
            metadata_by_issue = {
                issue["number"]: issue
                for issue in manifest["github_metadata"]["issues"]
            }
            issue_42_log_paths = metadata_by_issue[42]["metadata_log_paths"]
            issue_43_log_paths = metadata_by_issue[43]["metadata_log_paths"]
            run_dir = Path(manifest["paths"]["run_dir"])
            all_metadata_log_paths = [
                Path(issue_log_paths[step])
                for issue_log_paths in (issue_42_log_paths, issue_43_log_paths)
                for step in ("comment", "label", "close")
            ]
            close_log_paths = [
                Path(issue_42_log_paths["close"]),
                Path(issue_43_log_paths["close"]),
            ]

            self.assertEqual(
                issue_42_log_paths,
                {
                    step: str(run_dir / f"gh-issue-42-promotion-{step}.log")
                    for step in ("comment", "label", "close")
                },
            )
            self.assertEqual(
                issue_43_log_paths,
                {
                    step: str(run_dir / f"gh-issue-43-promotion-{step}.log")
                    for step in ("comment", "label", "close")
                },
            )
            self.assertEqual(len(set(all_metadata_log_paths)), 6)
            self.assertNotEqual(close_log_paths[0], close_log_paths[1])
            for log_path in all_metadata_log_paths:
                self.assertTrue(log_path.exists(), log_path)

        command_log_paths = {
            call.args: call.log_path
            for call in runner.calls
            if call.args[:3]
            in {
                ("gh", "issue", "comment"),
                ("gh", "issue", "edit"),
                ("gh", "issue", "close"),
            }
        }
        self.assertEqual(
            command_log_paths[
                (
                    "gh",
                    "issue",
                    "close",
                    "42",
                    "-R",
                    "example/repo",
                    "--reason",
                    "completed",
                )
            ],
            close_log_paths[0],
        )
        self.assertEqual(
            command_log_paths[
                (
                    "gh",
                    "issue",
                    "close",
                    "43",
                    "-R",
                    "example/repo",
                    "--reason",
                    "completed",
                )
            ],
            close_log_paths[1],
        )

    def test_promotion_runs_ready_issue_refresh_after_verified_closures(self) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_comments_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        candidate_view_command = (
            "gh",
            "issue",
            "view",
            "117",
            "-R",
            "example/repo",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        target_ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "abc1234",
            "origin/main",
        )
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )
        promoted_issue = issue_payload(42, ["agent-integrated"])
        retriage_candidate = issue_payload(
            117,
            ["needs-triage"],
            implementation_body_with_blockers(42),
        )
        ready_candidate = issue_payload(122, ["ready-for-agent"])
        comments_payload = {
            "comments": [
                {
                    "body": "\n".join(
                        [
                            "Ralph Gitflow integration completed.",
                            "",
                            "Commit: `abc1234`",
                        ]
                    )
                }
            ]
        }
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            ready_issue_refresh_analysis_markdown=POST_PROMOTION_READY_ISSUE_REFRESH_MARKDOWN,
            command_outputs={
                issue_list_command: [
                    json.dumps([promoted_issue]),
                    json.dumps([retriage_candidate, ready_candidate]),
                ],
                issue_comments_command: [json.dumps(comments_payload)],
                candidate_view_command: [json.dumps(retriage_candidate)],
                promotion_log_command: [
                    "abc1234\x00Ralph Local integration for issue 42\n"
                ],
            },
            fail_commands={target_ancestor_command: 1},
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                ready_issue_refresh_enabled=True,
            )
            output = io.StringIO()

            with redirect_stdout(output):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")
            artifact_path = next(
                tmp_path.glob("logs/promote-*/ready-issue-refresh-analysis.md")
            )
            artifact = artifact_path.read_text(encoding="utf-8")
            comment = next(
                tmp_path.glob("logs/promote-*/issue-117-comment.md")
            ).read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        issue_list_indexes = [
            index
            for index, command in enumerate(commands)
            if command == issue_list_command
        ]
        close_command = (
            "gh",
            "issue",
            "close",
            "42",
            "-R",
            "example/repo",
            "--reason",
            "completed",
        )
        label_command = (
            "gh",
            "issue",
            "edit",
            "117",
            "-R",
            "example/repo",
            "--add-label",
            "ready-for-agent",
            "--remove-label",
            "needs-triage",
        )
        review_call = next(
            call
            for call in runner.calls
            if call.input_text is not None
            and "Run a Post-promotion review" in call.input_text
        )
        refresh_call = next(
            call
            for call in runner.calls
            if call.input_text is not None
            and "after successful Promotion closed verified" in call.input_text
        )
        self.assertEqual(len(issue_list_indexes), 2)
        self.assertLess(commands.index(close_command), issue_list_indexes[1])
        self.assertLess(
            runner.calls.index(review_call), runner.calls.index(refresh_call)
        )
        self.assertIn(label_command, commands)
        self.assertTrue(comment.startswith(ralph.AI_READY_ISSUE_REFRESH_DISCLAIMER))
        self.assertIn("Promotion closed #42", comment)
        self.assertIn(
            "Ready issue refresh candidate selection found 2 candidate(s) after "
            "Promotion closure of #42.",
            output.getvalue(),
        )
        self.assertEqual(
            artifact, POST_PROMOTION_READY_ISSUE_REFRESH_MARKDOWN.rstrip() + "\n"
        )
        self.assertIn("Post-promotion review notes:", refresh_call.input_text)
        self.assertIn(
            '"title": "Harden Promotion evidence checks"', refresh_call.input_text
        )
        self.assertIn("### Candidate issue #117: Issue 117", refresh_call.input_text)
        self.assertEqual(manifest["status"], "succeeded")
        self.assertIsNone(manifest["failure"])
        self.assertEqual(manifest["ready_issue_refresh"]["status"], "completed")
        self.assertEqual(
            manifest["ready_issue_refresh"]["candidate_issue_numbers"],
            [117, 122],
        )
        results = {
            item["issue_number"]: item
            for item in manifest["ready_issue_refresh"]["mutation_results"]
        }
        self.assertEqual(results[117]["status"], "completed")
        self.assertEqual(
            results[117]["operations"]["labels"]["added"], ["ready-for-agent"]
        )
        self.assertEqual(
            results[117]["operations"]["labels"]["removed"], ["needs-triage"]
        )
        self.assertEqual(results[122]["status"], "skipped_no_change")

    def test_promotion_fast_forwards_clean_checked_out_local_branches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo_path = tmp_path / "repo"
            main_path = tmp_path / "main-worktree"
            runner = FakeRunner(
                diff_outputs=["scripts/ralph.py\n"],
                rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
                status_outputs=["", ""],
                command_outputs={
                    ("git", "worktree", "list", "--porcelain"): [
                        "\n".join(
                            [
                                f"worktree {repo_path}",
                                "HEAD dev-old",
                                "branch refs/heads/dev",
                                "",
                                f"worktree {main_path}",
                                "HEAD main-old",
                                "branch refs/heads/main",
                                "",
                            ]
                        )
                    ],
                },
            )
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        fast_forward_calls = [
            call
            for call in runner.calls
            if call.args == ("git", "merge", "--ff-only", "promotion-sha")
        ]
        self.assertEqual(
            [call.cwd for call in fast_forward_calls],
            [repo_path, main_path],
        )
        local_fast_forwards = manifest["local_branch_fast_forwards"]
        self.assertEqual(
            local_fast_forwards["source_branch"]["status"],
            "fast_forwarded",
        )
        self.assertEqual(
            local_fast_forwards["source_branch"]["worktree_path"],
            str(repo_path),
        )
        self.assertEqual(
            local_fast_forwards["integration_target"]["status"],
            "fast_forwarded",
        )
        self.assertEqual(
            local_fast_forwards["integration_target"]["worktree_path"],
            str(main_path),
        )

    def test_promotion_records_recovery_for_dirty_checked_out_local_branch(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            main_path = tmp_path / "main-worktree"
            runner = FakeRunner(
                diff_outputs=["scripts/ralph.py\n"],
                rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
                status_outputs=[" M README.md\n"],
                command_outputs={
                    ("git", "worktree", "list", "--porcelain"): [
                        "\n".join(
                            [
                                f"worktree {main_path}",
                                "HEAD main-old",
                                "branch refs/heads/main",
                                "",
                            ]
                        )
                    ],
                    (
                        "git",
                        "for-each-ref",
                        "--format=%(objectname)",
                        "--count=1",
                        "refs/heads/dev",
                    ): ["dev-old\n"],
                },
            )
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        self.assertFalse(
            any(
                call.args == ("git", "merge", "--ff-only", "promotion-sha")
                for call in runner.calls
            )
        )
        target_fast_forward = manifest["local_branch_fast_forwards"][
            "integration_target"
        ]
        self.assertEqual(target_fast_forward["status"], "skipped_dirty_worktree")
        self.assertEqual(target_fast_forward["worktree_path"], str(main_path))
        self.assertIn("uncommitted changes", target_fast_forward["reason"])
        self.assertEqual(
            target_fast_forward["recovery_command"],
            ralph.format_command(
                ["git", "-C", str(main_path), "pull", "--ff-only", "origin", "main"]
            ),
        )

    def test_promotion_from_unrelated_worktree_updates_checked_out_target_only(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo_path = tmp_path / "repo"
            main_path = tmp_path / "main-worktree"
            runner = FakeRunner(
                diff_outputs=["scripts/ralph.py\n"],
                rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
                status_outputs=[""],
                command_outputs={
                    ("git", "worktree", "list", "--porcelain"): [
                        "\n".join(
                            [
                                f"worktree {repo_path}",
                                "HEAD feature-old",
                                "branch refs/heads/agent/issue-114",
                                "",
                                f"worktree {main_path}",
                                "HEAD main-old",
                                "branch refs/heads/main",
                                "",
                            ]
                        )
                    ],
                    (
                        "git",
                        "for-each-ref",
                        "--format=%(objectname)",
                        "--count=1",
                        "refs/heads/dev",
                    ): ["dev-old\n"],
                },
            )
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        fast_forward_calls = [
            call
            for call in runner.calls
            if call.args == ("git", "merge", "--ff-only", "promotion-sha")
        ]
        self.assertEqual([call.cwd for call in fast_forward_calls], [main_path])
        self.assertEqual(
            manifest["local_branch_fast_forwards"]["source_branch"]["status"],
            "skipped_not_checked_out",
        )
        self.assertEqual(
            manifest["local_branch_fast_forwards"]["source_branch"]["current_commit"],
            "dev-old",
        )
        self.assertEqual(
            manifest["local_branch_fast_forwards"]["source_branch"]["recovery_command"],
            ralph.format_command(
                ["git", "-C", str(repo_path), "fetch", "origin", "dev:dev"]
            ),
        )
        self.assertEqual(
            manifest["local_branch_fast_forwards"]["integration_target"]["status"],
            "fast_forwarded",
        )

    def test_promotion_ignores_detached_promotion_worktrees_for_local_branches(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo_path = tmp_path / "repo"
            source_path = tmp_path / "worktrees" / "agent-promote-source-dev-to-main"
            promote_path = tmp_path / "worktrees" / "agent-promote-dev-to-main"
            runner = FakeRunner(
                diff_outputs=["scripts/ralph.py\n"],
                rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
                command_outputs={
                    ("git", "worktree", "list", "--porcelain"): [
                        "\n".join(
                            [
                                f"worktree {source_path}",
                                "HEAD source-sha",
                                "detached",
                                "",
                                f"worktree {promote_path}",
                                "HEAD promotion-sha",
                                "detached",
                                "",
                            ]
                        )
                    ],
                    (
                        "git",
                        "for-each-ref",
                        "--format=%(objectname)",
                        "--count=1",
                        "refs/heads/dev",
                    ): ["dev-old\n"],
                    (
                        "git",
                        "for-each-ref",
                        "--format=%(objectname)",
                        "--count=1",
                        "refs/heads/main",
                    ): ["main-old\n"],
                },
            )
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        fast_forward_calls = [
            call
            for call in runner.calls
            if call.args == ("git", "merge", "--ff-only", "promotion-sha")
        ]
        self.assertEqual(fast_forward_calls, [])
        local_fast_forwards = manifest["local_branch_fast_forwards"]
        self.assertEqual(
            local_fast_forwards["source_branch"]["status"],
            "skipped_not_checked_out",
        )
        self.assertEqual(
            local_fast_forwards["source_branch"]["current_commit"],
            "dev-old",
        )
        self.assertEqual(
            local_fast_forwards["source_branch"]["recovery_command"],
            ralph.format_command(
                ["git", "-C", str(repo_path), "fetch", "origin", "dev:dev"]
            ),
        )
        self.assertEqual(
            local_fast_forwards["integration_target"]["status"],
            "skipped_not_checked_out",
        )
        self.assertEqual(
            local_fast_forwards["integration_target"]["current_commit"],
            "main-old",
        )
        self.assertEqual(
            local_fast_forwards["integration_target"]["recovery_command"],
            ralph.format_command(
                ["git", "-C", str(repo_path), "fetch", "origin", "main:main"]
            ),
        )

    def test_promotion_records_recovery_for_missing_local_branches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            repo_path = tmp_path / "repo"
            runner = FakeRunner(
                diff_outputs=["scripts/ralph.py\n"],
                rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
                command_outputs={
                    ("git", "worktree", "list", "--porcelain"): [""],
                },
            )
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        local_fast_forwards = manifest["local_branch_fast_forwards"]
        for role, branch in (
            ("source_branch", "dev"),
            ("integration_target", "main"),
        ):
            self.assertEqual(
                local_fast_forwards[role]["status"],
                "skipped_missing_local_branch",
            )
            self.assertIsNone(local_fast_forwards[role]["current_commit"])
            self.assertEqual(
                local_fast_forwards[role]["target_commit"], "promotion-sha"
            )
            self.assertIn("does not exist", local_fast_forwards[role]["reason"])
            self.assertEqual(
                local_fast_forwards[role]["recovery_command"],
                ralph.format_command(
                    [
                        "git",
                        "-C",
                        str(repo_path),
                        "fetch",
                        "origin",
                        f"{branch}:{branch}",
                    ]
                ),
            )

    def test_promotion_closes_manually_recovered_gitflow_issue_with_parseable_evidence(
        self,
    ) -> None:
        recovered_sha = "7c4599f152ca03b125d9ef4c93fdd1900af2195c"
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_comments_command = (
            "gh",
            "issue",
            "view",
            "102",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        target_ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            recovered_sha,
            "origin/main",
        )
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )
        issue_payload = [
            {
                "number": 102,
                "title": "Recover issue integration",
                "body": IMPLEMENTATION_BODY,
                "labels": [{"name": "agent-integrated"}],
                "createdAt": "2026-04-30T00:00:00Z",
                "updatedAt": "2026-04-30T00:00:00Z",
                "url": "https://github.com/example/repo/issues/102",
                "comments": [],
                "author": {"login": "reporter"},
            }
        ]
        comments_payload = {
            "comments": [
                {
                    "body": "\n".join(
                        [
                            "Ralph implementation failed after issue QA passed.",
                            "",
                            "Manifest integration_commit: `null`",
                        ]
                    )
                },
                {
                    "body": "\n".join(
                        [
                            ralph.MANUAL_GITFLOW_RECOVERY_COMMENT_TITLE,
                            "",
                            f"Commit: `{recovered_sha}`",
                            "Delivery mode: `gitflow`",
                            "Target branch: `dev`",
                            "Recovered from run: `.ralph/runs/issue-102-failed`",
                        ]
                    )
                },
            ]
        }
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            command_outputs={
                issue_list_command: [json.dumps(issue_payload)],
                issue_comments_command: [json.dumps(comments_payload)],
                promotion_log_command: [
                    f"{recovered_sha}\x00Manual Gitflow recovery for issue 102\n"
                ],
            },
            fail_commands={target_ancestor_command: 1},
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                loop._promote()

            comment_path = next(tmp_path.glob("logs/promote-*/issue-102-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        edit_command = (
            "gh",
            "issue",
            "edit",
            "102",
            "-R",
            "example/repo",
            "--add-label",
            "agent-merged",
            "--remove-label",
            "agent-integrated",
            "--remove-label",
            "agent-reviewing",
            "--remove-label",
            "agent-running",
            "--remove-label",
            "agent-failed",
        )
        close_command = (
            "gh",
            "issue",
            "close",
            "102",
            "-R",
            "example/repo",
            "--reason",
            "completed",
        )
        self.assertEqual(stderr.getvalue(), "")
        self.assertIn(edit_command, commands)
        self.assertIn(close_command, commands)
        self.assertIn(
            "Integrated commit: `7c4599f152ca03b125d9ef4c93fdd1900af2195c`",
            comment,
        )
        self.assertEqual(
            manifest["promotion_commit_inventory"]["commits"],
            [
                {
                    "sha": recovered_sha,
                    "subject": "Manual Gitflow recovery for issue 102",
                    "verified_local_integration": True,
                    "classification": "verified_local_integration",
                    "issue": {
                        "number": 102,
                        "title": "Recover issue integration",
                        "url": "https://github.com/example/repo/issues/102",
                    },
                    "integrated_commit": recovered_sha,
                },
            ],
        )
        self.assertEqual(manifest["github_metadata"]["status"], "closed")
        self.assertEqual(manifest["github_metadata"]["issues"][0]["number"], 102)
        self.assertEqual(
            manifest["github_metadata"]["issues"][0]["integrated_commit"],
            recovered_sha,
        )
        self.assertEqual(
            manifest["github_metadata"]["issues"][0]["metadata_status"],
            "closed",
        )

    def test_promotion_closes_recovered_gitflow_issue_with_local_integration_commit_line(
        self,
    ) -> None:
        recovered_sha = "114676ec1523a91c4d6cc94c7201cd44a30c310a"
        issue_list = issue_list_command()
        issue_comments = issue_comments_command(242)
        target_ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            recovered_sha,
            "origin/main",
        )
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )
        recovered_comment = "\n".join(
            [
                "Recovered stale Ralph run and completed Gitflow Local integration "
                "for this issue.",
                "",
                "Integrated to `dev`:",
                f"- Local integration commit: `{recovered_sha}`.",
                "- Pushed `dev`: `27a9bfa5..114676ec`.",
                "",
                "Leaving this open under `delivery-gitflow` for Promotion from "
                "`dev` to `main`.",
            ]
        )
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            command_outputs={
                issue_list: [json.dumps([issue_payload(242, ["agent-integrated"])])],
                issue_comments: [
                    json.dumps({"comments": [{"body": recovered_comment}]})
                ],
                promotion_log_command: [
                    f"{recovered_sha}\x00Recovered Gitflow Local integration\n"
                ],
            },
            fail_commands={target_ancestor_command: 1},
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )

            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        self.assertIn(
            (
                "gh",
                "issue",
                "close",
                "242",
                "-R",
                "example/repo",
                "--reason",
                "completed",
            ),
            commands,
        )
        self.assertEqual(
            manifest["promotion_commit_inventory"]["commits"],
            [
                {
                    "sha": recovered_sha,
                    "subject": "Recovered Gitflow Local integration",
                    "verified_local_integration": True,
                    "classification": "verified_local_integration",
                    "issue": {
                        "number": 242,
                        "title": "Issue 242",
                        "url": "https://github.com/example/repo/issues/242",
                    },
                    "integrated_commit": recovered_sha,
                },
            ],
        )
        self.assertEqual(manifest["github_metadata"]["issues"][0]["number"], 242)
        self.assertEqual(
            manifest["github_metadata"]["issues"][0]["integrated_commit"],
            recovered_sha,
        )
        self.assertEqual(
            manifest["github_metadata"]["issues"][0]["metadata_status"],
            "closed",
        )

    def test_promotion_records_recovery_for_integrated_commit_already_on_target(
        self,
    ) -> None:
        recovered_sha = "114676ec1523a91c4d6cc94c7201cd44a30c310a"
        issue_list = issue_list_command()
        issue_comments = issue_comments_command(242)
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )
        recovered_comment = "\n".join(
            [
                "Recovered stale Ralph run and completed Gitflow Local integration "
                "for this issue.",
                "",
                "Integrated to `dev`:",
                f"- Local integration commit: `{recovered_sha}`.",
                "",
                "Leaving this open under `delivery-gitflow` for Promotion from "
                "`dev` to `main`.",
            ]
        )
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            command_outputs={
                issue_list: [json.dumps([issue_payload(242, ["agent-integrated"])])],
                issue_comments: [
                    json.dumps({"comments": [{"body": recovered_comment}]})
                ],
                promotion_log_command: [
                    "def5678\x00Manual follow-up after issue integration\n"
                ],
            },
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )
        self.assertIn(
            f"Promotion warning: #242 has recorded Gitflow Local integration commit "
            f"{recovered_sha} already reachable from origin/main",
            stderr.getvalue(),
        )
        self.assertEqual(
            manifest["promotion_commit_inventory"]["commits"],
            [
                {
                    "sha": "def5678",
                    "subject": "Manual follow-up after issue integration",
                    "verified_local_integration": False,
                    "classification": "unverified_promotion_commit",
                },
            ],
        )
        self.assertEqual(
            manifest["github_metadata"]["status"],
            "verified_issues_with_warnings",
        )
        self.assertEqual(
            manifest["github_metadata"]["issues"],
            [
                {
                    "number": 242,
                    "title": "Issue 242",
                    "url": "https://github.com/example/repo/issues/242",
                    "integrated_commit": recovered_sha,
                    "metadata_status": "integrated_commit_already_promoted",
                    "warning": (
                        "#242 has recorded Gitflow Local integration commit "
                        f"{recovered_sha} already reachable from origin/main, but "
                        "the GitHub Issue is still open with agent-integrated."
                    ),
                    "recovery_action": (
                        "Confirm issue #242 is still open with `agent-integrated`, "
                        "then replace `agent-integrated` with `agent-merged` and "
                        "close it as completed, or rerun Ready issue refresh to "
                        "reconcile the stale post-Promotion metadata."
                    ),
                },
            ],
        )

    def test_promotion_warns_on_unparseable_manual_recovery_evidence(self) -> None:
        recovered_sha = "7c4599f152ca03b125d9ef4c93fdd1900af2195c"
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_comments_command = (
            "gh",
            "issue",
            "view",
            "102",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )
        issue_payload = [
            {
                "number": 102,
                "title": "Recover issue integration",
                "body": IMPLEMENTATION_BODY,
                "labels": [{"name": "agent-integrated"}],
                "createdAt": "2026-04-30T00:00:00Z",
                "updatedAt": "2026-04-30T00:00:00Z",
                "url": "https://github.com/example/repo/issues/102",
                "comments": [],
                "author": {"login": "reporter"},
            }
        ]
        comments_payload = {
            "comments": [
                {
                    "body": "\n".join(
                        [
                            "Ralph implementation failed after issue QA passed.",
                            "",
                            "Manifest integration_commit: `null`",
                        ]
                    )
                },
                {
                    "body": (
                        "Manual recovery: manually recovered the Gitflow integration "
                        f"to dev with {recovered_sha}, then added agent-integrated."
                    )
                },
            ]
        }
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            command_outputs={
                issue_list_command: [json.dumps(issue_payload)],
                issue_comments_command: [json.dumps(comments_payload)],
                promotion_log_command: [
                    f"{recovered_sha}\x00Manual Gitflow recovery for issue 102\n"
                ],
            },
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )
        self.assertIn(
            "Promotion warning: #102 has manual Gitflow recovery evidence but no "
            "parseable integrated commit for Promotion closure.",
            stderr.getvalue(),
        )
        self.assertIn(ralph.MANUAL_GITFLOW_RECOVERY_COMMENT_TITLE, stderr.getvalue())
        self.assertEqual(
            manifest["promotion_commit_inventory"]["commits"],
            [
                {
                    "sha": recovered_sha,
                    "subject": "Manual Gitflow recovery for issue 102",
                    "verified_local_integration": False,
                    "classification": "unverified_promotion_commit",
                },
            ],
        )
        self.assertEqual(
            manifest["github_metadata"]["status"],
            "verified_issues_with_warnings",
        )
        self.assertEqual(
            manifest["github_metadata"]["issues"],
            [
                {
                    "number": 102,
                    "title": "Recover issue integration",
                    "url": "https://github.com/example/repo/issues/102",
                    "integrated_commit": None,
                    "metadata_status": "manual_recovery_commit_unparseable",
                    "warning": (
                        "#102 has manual Gitflow recovery evidence but no parseable "
                        "integrated commit for Promotion closure."
                    ),
                    "recovery_action": (
                        "Verify the recovered commit is reachable from `origin/dev` "
                        "and not already on `origin/main`, then add an issue comment "
                        "that starts with `Ralph Gitflow manual recovery completed.` "
                        "and includes a `Commit:` line with the dev commit SHA in "
                        "backticks before rerunning Promotion, or reconcile the issue "
                        "manually."
                    ),
                },
            ],
        )

    def test_promotion_closes_accepted_exploratory_issue(self) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_comments_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        target_ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "abc1234",
            "origin/main",
        )
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )
        issue_payload = [
            {
                "number": 42,
                "title": "Try exploratory workflow",
                "body": EXPLORATORY_IMPLEMENTATION_BODY,
                "labels": [
                    {"name": "agent-integrated"},
                    {"name": "delivery-exploratory"},
                ],
                "createdAt": "2026-04-30T00:00:00Z",
                "updatedAt": "2026-04-30T00:00:00Z",
                "url": "https://github.com/example/repo/issues/42",
                "comments": [],
                "author": {"login": "reporter"},
            }
        ]
        comments_payload = {
            "comments": [
                {
                    "body": "\n".join(
                        [
                            "Ralph exploratory handoff completed.",
                            "",
                            "Commit: `aaaaaaa`",
                        ]
                    )
                },
                {
                    "body": "\n".join(
                        [
                            "Ralph exploratory acceptance completed.",
                            "",
                            "Commit: `abc1234`",
                        ]
                    )
                },
            ]
        }
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            command_outputs={
                issue_list_command: [json.dumps(issue_payload)],
                issue_comments_command: [json.dumps(comments_payload)],
                promotion_log_command: [
                    "abc1234\x00Merge accepted Exploratory issue 42\n",
                ],
            },
            fail_commands={target_ancestor_command: 1},
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )
            with redirect_stdout(io.StringIO()):
                loop._promote()

            comment_path = next(tmp_path.glob("logs/promote-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        self.assertIn(
            (
                "gh",
                "issue",
                "edit",
                "42",
                "-R",
                "example/repo",
                "--add-label",
                "agent-merged",
                "--remove-label",
                "agent-integrated",
                "--remove-label",
                "agent-reviewing",
                "--remove-label",
                "agent-running",
                "--remove-label",
                "agent-failed",
            ),
            commands,
        )
        self.assertIn(
            (
                "gh",
                "issue",
                "close",
                "42",
                "-R",
                "example/repo",
                "--reason",
                "completed",
            ),
            commands,
        )
        self.assertIn("Integrated commit: `abc1234`", comment)
        self.assertEqual(manifest["github_metadata"]["issues"][0]["number"], 42)
        self.assertEqual(
            manifest["github_metadata"]["issues"][0]["integrated_commit"],
            "abc1234",
        )

    def test_promotion_classifies_resumed_exploratory_acceptance_commits(
        self,
    ) -> None:
        acceptance_123 = "189fb1017d9fca4d7b4aef1bc27b589599a60cff"
        acceptance_153 = "3f140d7b2cf749ad4c5c67c442736f1b4a5086b0"
        acceptance_157 = "9c12f1258cf680849829a91fab0b94c8eeed886a"
        accepted_issues = [
            (123, acceptance_123, "Split local Marimo dashboard images"),
            (153, acceptance_153, "Prototype manifest-driven AWS deployment"),
            (157, acceptance_157, "Redesign Caddy root portfolio"),
        ]
        issue_list_payload = [
            {
                **issue_payload(
                    issue_number,
                    [ralph.AGENT_INTEGRATED_LABEL, ralph.DELIVERY_EXPLORATORY_LABEL],
                    EXPLORATORY_IMPLEMENTATION_BODY,
                ),
                "title": title,
            }
            for issue_number, _commit, title in accepted_issues
        ]
        command_outputs: dict[tuple[str, ...], list[str]] = {
            issue_list_command(): [json.dumps(issue_list_payload)],
            (
                "git",
                "log",
                "--reverse",
                "--format=%H%x00%s",
                "origin/main..source-sha",
            ): [
                "\n".join(
                    f"{commit}\x00Accept Exploratory issue #{issue_number}: {title}"
                    for issue_number, commit, title in accepted_issues
                )
                + "\n"
            ],
        }
        for issue_number, commit, _title in accepted_issues:
            command_outputs[issue_comments_command(issue_number)] = [
                json.dumps(
                    {
                        "comments": [
                            {
                                "body": "\n".join(
                                    [
                                        "Ralph exploratory acceptance completed.",
                                        "",
                                        f"Commit: `{commit}`",
                                    ]
                                )
                            }
                        ]
                    }
                )
            ]

        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            command_outputs=command_outputs,
            fail_commands={
                (
                    "git",
                    "merge-base",
                    "--is-ancestor",
                    commit,
                    "origin/main",
                ): 1
                for _issue_number, commit, _title in accepted_issues
            },
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_followups=True,
            )
            with redirect_stdout(io.StringIO()):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        review_prompt = next(
            call.input_text
            for call in runner.calls
            if call.input_text is not None
            and "Run a Post-promotion review" in call.input_text
        )
        self.assertEqual(
            [
                entry["issue"]["number"]
                for entry in manifest["promotion_commit_inventory"]["commits"]
            ],
            [123, 153, 157],
        )
        self.assertEqual(
            [
                issue["integrated_commit"]
                for issue in manifest["github_metadata"]["issues"]
            ],
            [acceptance_123, acceptance_153, acceptance_157],
        )
        self.assertIn(
            f"`{acceptance_123}` Accept Exploratory issue #123: "
            "Split local Marimo dashboard images - verified issue evidence commit "
            "for #123 Split local Marimo dashboard images",
            review_prompt,
        )
        self.assertIn(
            f"`{acceptance_153}` Accept Exploratory issue #153: "
            "Prototype manifest-driven AWS deployment - verified issue evidence "
            "commit for #153 Prototype manifest-driven AWS deployment",
            review_prompt,
        )
        self.assertIn(
            f"`{acceptance_157}` Accept Exploratory issue #157: "
            "Redesign Caddy root portfolio - verified issue evidence commit "
            "for #157 Redesign Caddy root portfolio",
            review_prompt,
        )

    def test_promotion_inventory_prompt_lists_shared_commit_issue_mappings(
        self,
    ) -> None:
        shared_commit = "9c12f1258cf680849829a91fab0b94c8eeed886a"
        entries = ralph.promotion_commit_inventory_entries(
            [
                ralph.PromotedSourceCommit(
                    sha=shared_commit,
                    subject="Manual resumed Exploratory acceptance",
                )
            ],
            [
                (
                    make_issue(
                        {ralph.AGENT_INTEGRATED_LABEL},
                        number=123,
                        title="First accepted issue",
                    ),
                    shared_commit,
                ),
                (
                    make_issue(
                        {ralph.AGENT_INTEGRATED_LABEL},
                        number=153,
                        title="Second accepted issue",
                    ),
                    shared_commit,
                ),
            ],
        )

        self.assertNotIn("issue", entries[0])
        self.assertEqual(
            entries[0]["issues"],
            [
                {
                    "number": 123,
                    "title": "First accepted issue",
                    "url": "https://github.com/example/repo/issues/123",
                },
                {
                    "number": 153,
                    "title": "Second accepted issue",
                    "url": "https://github.com/example/repo/issues/153",
                },
            ],
        )
        self.assertEqual(
            ralph.promotion_commit_inventory_prompt_lines(entries),
            (
                f"- `{shared_commit}` Manual resumed Exploratory acceptance - "
                "verified issue evidence commit for #123 First accepted issue, "
                "#153 Second accepted issue"
            ),
        )

    def test_promotion_skip_post_promotion_review_flag_disables_review_agent(
        self,
    ) -> None:
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
            )
            output = io.StringIO()

            with redirect_stdout(output):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        promote_path = Path(tmp) / "worktrees" / "agent-promote-dev-to-main"
        commands = [call.args for call in runner.calls]
        self.assertNotIn(tuple(ralph.codex_exec_command(promote_path)), commands)
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "create") for command in commands)
        )
        self.assertIn(
            "Post-promotion review skipped by --skip-post-promotion-review.",
            output.getvalue(),
        )
        self.assertFalse(manifest["post_promotion_review"]["enabled"])
        self.assertEqual(
            manifest["post_promotion_review"]["status"],
            "skipped_by_operator",
        )
        self.assertFalse(manifest["post_promotion_followups"]["enabled"])
        self.assertEqual(
            manifest["post_promotion_followups"]["status"],
            "skipped_review_disabled",
        )

    def test_promotion_skip_post_promotion_followups_keeps_review_but_disables_create(
        self,
    ) -> None:
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_followups=True,
            )
            output = io.StringIO()

            with redirect_stdout(output):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")
            artifact_path = next(
                tmp_path.glob("logs/promote-*/post-promotion-review.md")
            )

        commands = [call.args for call in runner.calls]
        promote_path = Path(tmp) / "worktrees" / "agent-promote-dev-to-main"
        review_command = tuple(
            ralph.codex_exec_command(
                promote_path,
                output_last_message=artifact_path,
            )
        )
        self.assertIn(review_command, commands)
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "create") for command in commands)
        )
        review_index = commands.index(review_command)
        self.assertIn(
            "Automatic validated follow-up issue creation is disabled for this Promotion attempt.",
            runner.calls[review_index].input_text,
        )
        self.assertIn(
            "Post-promotion follow-up issue creation skipped by operator.",
            output.getvalue(),
        )
        self.assertFalse(manifest["post_promotion_followups"]["enabled"])
        self.assertEqual(
            manifest["post_promotion_followups"]["status"],
            "skipped_by_operator",
        )

    def test_post_promotion_followup_invalid_draft_creates_needs_triage_with_evidence(
        self,
    ) -> None:
        review_markdown = """# Post-promotion Review

## Findings

Actionable follow-up found.

## Learnings

None.

## Recovery and Consistency Guidance

None.

## Follow-up GitHub Issue Drafts

```json
[
  {
    "finding_id": "incomplete-follow-up",
    "title": "Incomplete follow-up",
    "body": "## What to build\\nBuild it.\\n",
    "labels": ["delivery-gitflow"]
  }
]
```
"""
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            run_dir = tmp_path / "logs" / "promote-test"
            run_dir.mkdir(parents=True)
            artifact_path = run_dir / "post-promotion-review.md"
            artifact_path.write_text(review_markdown, encoding="utf-8")
            manifest = ralph.RunManifest.for_promotion(
                run_dir=run_dir,
                source_branch="dev",
                target_branch="main",
                source_path=tmp_path / "worktrees" / "source",
                promote_path=tmp_path / "worktrees" / "promote",
                config=loop.config,
            )

            with redirect_stdout(io.StringIO()):
                loop._run_post_promotion_followups(
                    source_branch="dev",
                    target_branch="main",
                    source_revision="source-sha",
                    promotion_sha="promotion-sha",
                    artifact_path=artifact_path,
                    run_dir=run_dir,
                    manifest=manifest,
                )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))
            body_path = next(run_dir.glob("post-promotion-followup-*.md"))
            body = body_path.read_text(encoding="utf-8")

        create_command = next(
            call.args
            for call in runner.calls
            if call.args[:3] == ("gh", "issue", "create")
        )
        self.assertIn("needs-triage", create_command)
        self.assertNotIn("ready-for-agent", create_command)
        self.assertNotIn("delivery-gitflow", create_command)
        self.assertIn("## Ralph validation evidence", body)
        self.assertIn("Missing required issue section", body)
        self.assertIn("Expected exactly one category label", body)
        self.assertEqual(
            manifest_payload["post_promotion_followups"]["status"], "completed"
        )
        self.assertEqual(
            manifest_payload["post_promotion_followups"]["created"][0][
                "validation_status"
            ],
            "needs_triage",
        )
        self.assertEqual(
            manifest_payload["post_promotion_followups"]["validation_downgrades"][0][
                "labels"
            ],
            ["needs-triage"],
        )

    def test_post_promotion_followup_dedupe_skips_existing_source_marker(self) -> None:
        marker = (
            "ralph-post-promotion-followup:"
            "promotion-sha:harden-promotion-evidence-checks"
        )
        list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "all",
            "--limit",
            "1",
            "--search",
            f'"{marker}" in:body',
            "--json",
            "number,title,url",
        )
        runner = FakeRunner(
            command_outputs={
                list_command: [
                    json.dumps(
                        [
                            {
                                "number": 77,
                                "title": "Existing follow-up",
                                "url": "https://github.com/example/repo/issues/77",
                            }
                        ]
                    )
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            run_dir = tmp_path / "logs" / "promote-test"
            run_dir.mkdir(parents=True)
            artifact_path = run_dir / "post-promotion-review.md"
            artifact_path.write_text(POST_PROMOTION_REVIEW_MARKDOWN, encoding="utf-8")
            manifest = ralph.RunManifest.for_promotion(
                run_dir=run_dir,
                source_branch="dev",
                target_branch="main",
                source_path=tmp_path / "worktrees" / "source",
                promote_path=tmp_path / "worktrees" / "promote",
                config=loop.config,
            )

            with redirect_stdout(io.StringIO()):
                loop._run_post_promotion_followups(
                    source_branch="dev",
                    target_branch="main",
                    source_revision="source-sha",
                    promotion_sha="promotion-sha",
                    artifact_path=artifact_path,
                    run_dir=run_dir,
                    manifest=manifest,
                )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        commands = [call.args for call in runner.calls]
        self.assertIn(list_command, commands)
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "create") for command in commands)
        )
        self.assertEqual(
            manifest_payload["post_promotion_followups"]["status"], "completed"
        )
        self.assertEqual(
            manifest_payload["post_promotion_followups"]["duplicates"][0]["url"],
            "https://github.com/example/repo/issues/77",
        )
        self.assertEqual(manifest_payload["post_promotion_followups"]["created"], [])

    def test_deploy_repair_valid_draft_creates_ready_issue_with_redacted_prompt(
        self,
    ) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            run_dir, manifest, classification, command, error = (
                deploy_repair_test_context(tmp_path, loop)
            )

            with patch.dict(
                "os.environ",
                {
                    "AWS_SECRET_ACCESS_KEY": "operator-aws-secret",
                    "PULUMI_ACCESS_TOKEN": "operator-pulumi-secret",
                },
                clear=False,
            ):
                with redirect_stdout(io.StringIO()):
                    loop._run_deploy_repair_issues(
                        classification=classification,
                        command=command,
                        deployment_error=error,
                        deployment_log_path=error.log_path,
                        run_dir=run_dir,
                        manifest=manifest,
                    )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))
            body_path = next(run_dir.glob("deploy-repair-*.md"))
            body = body_path.read_text(encoding="utf-8")
            prompt = (run_dir / "codex-deploy-failure-analysis.prompt.md").read_text(
                encoding="utf-8"
            )

        create_command = next(
            call.args
            for call in runner.calls
            if call.args[:3] == ("gh", "issue", "create")
        )
        codex_call = next(
            call for call in runner.calls if call.args[:2] == ("codex", "exec")
        )
        self.assertIn("bug", create_command)
        self.assertIn("delivery-gitflow", create_command)
        self.assertIn("ready-for-agent", create_command)
        self.assertIn("## QA/deploy verification plan", body)
        self.assertIn("## Ralph source", body)
        self.assertIn("ralph-deploy-repair:promotion-sha", body)
        self.assertNotIn("raw-secret-value", prompt)
        self.assertNotIn("pulumi-secret-value", prompt)
        self.assertIsNotNone(codex_call.env)
        assert codex_call.env is not None
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", codex_call.env)
        self.assertNotIn("PULUMI_ACCESS_TOKEN", codex_call.env)
        self.assertEqual(
            manifest_payload["deploy_repair_issues"]["status"], "completed"
        )
        self.assertEqual(
            manifest_payload["deploy_repair_issues"]["created"][0]["validation_status"],
            "ready",
        )

    def test_deploy_repair_invalid_draft_creates_needs_triage_with_evidence(
        self,
    ) -> None:
        invalid_markdown = """# Deploy Failure Analysis

## Findings

Incomplete draft.

## Deploy Repair GitHub Issue Drafts

```json
[
  {
    "finding_id": "incomplete-deploy-repair",
    "title": "Incomplete deploy repair",
    "body": "## What to build\\nRepair it.\\n",
    "labels": ["enhancement", "delivery-gitflow"]
  }
]
```

## Evidence

- The command failed.

## Open Questions

None.
"""
        runner = FakeRunner(deploy_failure_analysis_markdown=invalid_markdown)
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            run_dir, manifest, classification, command, error = (
                deploy_repair_test_context(tmp_path, loop)
            )

            with redirect_stdout(io.StringIO()):
                loop._run_deploy_repair_issues(
                    classification=classification,
                    command=command,
                    deployment_error=error,
                    deployment_log_path=error.log_path,
                    run_dir=run_dir,
                    manifest=manifest,
                )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))
            body_path = next(run_dir.glob("deploy-repair-*.md"))
            body = body_path.read_text(encoding="utf-8")

        create_command = next(
            call.args
            for call in runner.calls
            if call.args[:3] == ("gh", "issue", "create")
        )
        self.assertIn("needs-triage", create_command)
        self.assertNotIn("ready-for-agent", create_command)
        self.assertNotIn("bug", create_command)
        self.assertIn("## Ralph validation evidence", body)
        self.assertIn("Missing required issue section", body)
        self.assertIn("Expected deploy-repair category label `bug`", body)
        self.assertIn("## QA/deploy verification plan", body)
        self.assertIn("Ralph validation placeholder", body)
        self.assertEqual(
            manifest_payload["deploy_repair_issues"]["created"][0]["validation_status"],
            "needs_triage",
        )
        self.assertEqual(
            manifest_payload["deploy_repair_issues"]["validation_downgrades"][0][
                "labels"
            ],
            ["needs-triage"],
        )

    def test_deploy_repair_dedupe_skips_existing_source_marker(self) -> None:
        marker = (
            "ralph-deploy-repair:"
            "promotion-sha:full_deployed_workflow:restore-operator-deployment"
        )
        list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "all",
            "--limit",
            "1",
            "--search",
            f'"{marker}" in:body',
            "--json",
            "number,title,url",
        )
        runner = FakeRunner(
            command_outputs={
                list_command: [
                    json.dumps(
                        [
                            {
                                "number": 88,
                                "title": "Existing deploy repair",
                                "url": "https://github.com/example/repo/issues/88",
                            }
                        ]
                    )
                ]
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            run_dir, manifest, classification, command, error = (
                deploy_repair_test_context(tmp_path, loop)
            )

            with redirect_stdout(io.StringIO()):
                loop._run_deploy_repair_issues(
                    classification=classification,
                    command=command,
                    deployment_error=error,
                    deployment_log_path=error.log_path,
                    run_dir=run_dir,
                    manifest=manifest,
                )

            manifest_payload = json.loads(manifest.path.read_text(encoding="utf-8"))

        commands = [call.args for call in runner.calls]
        self.assertIn(list_command, commands)
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "create") for command in commands)
        )
        self.assertEqual(
            manifest_payload["deploy_repair_issues"]["status"], "completed"
        )
        self.assertEqual(
            manifest_payload["deploy_repair_issues"]["duplicates"][0]["url"],
            "https://github.com/example/repo/issues/88",
        )
        self.assertEqual(manifest_payload["deploy_repair_issues"]["created"], [])

    def test_promotion_no_changes_skips_post_promotion_review_agent(self) -> None:
        runner = FakeRunner(
            diff_outputs=[""],
            rev_parse_outputs=["source-sha\n"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            output = io.StringIO()

            with redirect_stdout(output):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        self.assertFalse(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertFalse(
            any(command[:3] == ("git", "worktree", "add") for command in commands)
        )
        self.assertIn("No changes to promote from dev to main.", output.getvalue())
        self.assertIn(
            "Post-promotion review skipped: no Promotion changes.",
            output.getvalue(),
        )
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual(manifest["stage"], "no_changes_to_promote")
        self.assertEqual(
            manifest["post_promotion_review"]["status"],
            "skipped_no_changes",
        )
        self.assertEqual(
            manifest["post_promotion_followups"]["status"],
            "skipped_no_changes",
        )
        self.assertEqual(
            manifest["local_branch_fast_forwards"]["source_branch"]["status"],
            "skipped_no_promotion_changes",
        )
        self.assertEqual(
            manifest["local_branch_fast_forwards"]["integration_target"]["status"],
            "skipped_no_promotion_changes",
        )
        self.assertEqual(
            manifest["ready_issue_refresh"]["status"],
            "skipped_no_changes",
        )

    def test_post_promotion_review_failure_is_warning_only(self) -> None:
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            fail_post_promotion_review=True,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "push", "origin", "HEAD:main"), commands)
        self.assertIn(("git", "push", "origin", "HEAD:dev"), commands)
        self.assertTrue(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertIn("Post-promotion review warning:", stderr.getvalue())
        self.assertEqual(manifest["status"], "succeeded")
        self.assertIsNone(manifest["failure"])
        self.assertEqual(manifest["post_promotion_review"]["status"], "failed")
        self.assertIn("Command failed", manifest["post_promotion_review"]["error"])
        self.assertEqual(
            manifest["post_promotion_followups"]["status"],
            "skipped_review_unavailable",
        )

    def test_post_promotion_ready_issue_refresh_failure_is_warning_only(self) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_comments_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        target_ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "abc1234",
            "origin/main",
        )
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )
        comments_payload = {
            "comments": [
                {
                    "body": "\n".join(
                        [
                            "Ralph Gitflow integration completed.",
                            "",
                            "Commit: `abc1234`",
                        ]
                    )
                }
            ]
        }
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            fail_ready_issue_refresh_analysis=True,
            command_outputs={
                issue_list_command: [
                    json.dumps([issue_payload(42, ["agent-integrated"])]),
                    json.dumps([issue_payload(43, ["ready-for-agent"])]),
                ],
                issue_comments_command: [json.dumps(comments_payload)],
                promotion_log_command: [
                    "abc1234\x00Ralph Local integration for issue 42\n"
                ],
            },
            fail_commands={target_ancestor_command: 1},
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(
                tmp_path,
                runner,
                promote=True,
                skip_post_promotion_review=True,
                ready_issue_refresh_enabled=True,
            )
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        self.assertIn("Ready issue refresh warning after Promotion", stderr.getvalue())
        self.assertEqual(manifest["status"], "succeeded")
        self.assertIsNone(manifest["failure"])
        self.assertEqual(
            manifest["ready_issue_refresh"]["status"],
            "failed_warning_only",
        )
        self.assertIn(
            "Command failed",
            manifest["ready_issue_refresh"]["failure"]["message"],
        )
        self.assertIn(
            "Promotion remains succeeded",
            manifest["ready_issue_refresh"]["recovery_guidance"],
        )

    def test_post_promotion_followup_creation_failure_is_warning_only_after_push(
        self,
    ) -> None:
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            fail_issue_create=True,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")
            artifact_path = next(
                tmp_path.glob("logs/promote-*/post-promotion-review.md")
            )
            artifact = artifact_path.read_text(encoding="utf-8")

        commands = [call.args for call in runner.calls]
        push_index = commands.index(("git", "push", "origin", "HEAD:main"))
        create_command = next(
            command for command in commands if command[:3] == ("gh", "issue", "create")
        )
        create_index = commands.index(create_command)
        self.assertLess(push_index, create_index)
        self.assertIn("Post-promotion follow-up creation warning", stderr.getvalue())
        self.assertEqual(manifest["status"], "succeeded")
        self.assertIsNone(manifest["failure"])
        self.assertEqual(
            manifest["post_promotion_followups"]["status"],
            "completed_with_warnings",
        )
        self.assertIn(
            "Command failed",
            manifest["post_promotion_followups"]["failures"][0]["error"],
        )
        self.assertIn(
            "Promotion remains succeeded",
            manifest["post_promotion_followups"]["recovery_guidance"],
        )
        self.assertIn("## Follow-up Creation Recovery Guidance", artifact)
        self.assertIn("Promotion remains succeeded", artifact)

    def test_failed_promotion_push_check_runs_review_without_side_effects(self) -> None:
        qa_command = ("make", "run-prek")
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n"],
            fail_commands={qa_command},
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            output = io.StringIO()
            with self.assertRaises(ralph.CommandFailure):
                with redirect_stdout(output), redirect_stderr(io.StringIO()):
                    loop._promote()

            commands = [call.args for call in runner.calls]
            manifest = load_run_manifest(tmp_path, run_glob="promote-*")
            artifact_path = next(
                tmp_path.glob("logs/promote-*/post-promotion-review.md")
            )
            artifact = artifact_path.read_text(encoding="utf-8")

        source_path = Path(tmp) / "worktrees" / "agent-promote-source-dev-to-main"
        promote_path = Path(tmp) / "worktrees" / "agent-promote-dev-to-main"
        review_command = tuple(
            ralph.codex_exec_command(
                source_path,
                output_last_message=artifact_path,
            )
        )
        self.assertIn(
            (
                "git",
                "worktree",
                "add",
                "--detach",
                str(source_path),
                "source-sha",
            ),
            commands,
        )
        qa_index = commands.index(qa_command)
        self.assertEqual(runner.calls[qa_index].cwd, source_path / "tools/ralph-loop")
        review_index = commands.index(review_command)
        self.assertLess(qa_index, review_index)
        self.assertEqual(runner.calls[review_index].cwd, source_path)
        self.assertIn(
            "Promotion outcome: `failed`",
            runner.calls[review_index].input_text,
        )
        self.assertIn("Command failed", runner.calls[review_index].input_text)
        self.assertIn(
            "## Recovery and Consistency Guidance",
            runner.calls[review_index].input_text,
        )
        self.assertLess(
            runner.calls[review_index].input_text.index(
                "## Recovery and Consistency Guidance"
            ),
            runner.calls[review_index].input_text.index(
                "## Follow-up GitHub Issue Drafts"
            ),
        )
        self.assertNotIn(
            (
                "git",
                "worktree",
                "add",
                "--detach",
                str(promote_path),
                "origin/main",
            ),
            commands,
        )
        self.assertFalse(any(command[:2] == ("git", "merge") for command in commands))
        self.assertFalse(
            any(command[:3] == ("git", "push", "origin") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["source_tree"]["revision"], "source-sha")
        self.assertIsNone(manifest["promotion_commit"])
        self.assertEqual(manifest["pushes"], {})
        self.assertEqual(manifest["github_metadata"]["status"], "not_started")
        self.assertEqual(manifest["post_promotion_review"]["status"], "completed")
        self.assertEqual(
            manifest["post_promotion_review"]["artifact_path"],
            str(artifact_path),
        )
        self.assertEqual(artifact, POST_PROMOTION_REVIEW_MARKDOWN.rstrip() + "\n")
        self.assertIn(POST_PROMOTION_REVIEW_MARKDOWN.strip(), output.getvalue())
        failed_push_check = [
            result
            for result in manifest["qa_results"]
            if result["name"] == "Ralph loop Commit check"
        ]
        self.assertEqual(len(failed_push_check), 1)
        self.assertEqual(failed_push_check[0]["status"], "failed")

    def test_partial_promotion_metadata_failure_runs_review_preserving_failure(
        self,
    ) -> None:
        issue_list_command = (
            "gh",
            "issue",
            "list",
            "-R",
            "example/repo",
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,body,labels,createdAt,updatedAt,url,comments,author",
        )
        issue_comments_command = (
            "gh",
            "issue",
            "view",
            "42",
            "-R",
            "example/repo",
            "--comments",
            "--json",
            "comments",
        )
        target_ancestor_command = (
            "git",
            "merge-base",
            "--is-ancestor",
            "abc1234",
            "origin/main",
        )
        promotion_log_command = (
            "git",
            "log",
            "--reverse",
            "--format=%H%x00%s",
            "origin/main..source-sha",
        )
        close_command = (
            "gh",
            "issue",
            "close",
            "42",
            "-R",
            "example/repo",
            "--reason",
            "completed",
        )
        issue_payload = [
            {
                "number": 42,
                "title": "Implement thing",
                "body": IMPLEMENTATION_BODY,
                "labels": [{"name": "agent-integrated"}],
                "createdAt": "2026-04-30T00:00:00Z",
                "updatedAt": "2026-04-30T00:00:00Z",
                "url": "https://github.com/example/repo/issues/42",
                "comments": [],
                "author": {"login": "reporter"},
            }
        ]
        comments_payload = {
            "comments": [
                {
                    "body": "\n".join(
                        [
                            "Ralph Gitflow integration completed.",
                            "",
                            "Commit: `abc1234`",
                        ]
                    )
                }
            ]
        }
        runner = FakeRunner(
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
            command_outputs={
                issue_list_command: [json.dumps(issue_payload)],
                issue_comments_command: [json.dumps(comments_payload)],
                promotion_log_command: [
                    "abc1234\x00Ralph Local integration for issue 42\n"
                ],
            },
            fail_commands={
                target_ancestor_command: 1,
                close_command: 1,
            },
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            stderr = io.StringIO()

            with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
                with self.assertRaises(ralph.PostPushFailure) as error_context:
                    loop._promote()

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")
            artifact_path = next(
                tmp_path.glob("logs/promote-*/post-promotion-review.md")
            )
            artifact = artifact_path.read_text(encoding="utf-8")

        promote_path = Path(tmp) / "worktrees" / "agent-promote-dev-to-main"
        review_command = tuple(
            ralph.codex_exec_command(
                promote_path,
                output_last_message=artifact_path,
            )
        )
        commands = [call.args for call in runner.calls]
        close_index = commands.index(close_command)
        review_index = commands.index(review_command)
        self.assertLess(close_index, review_index)
        self.assertEqual(runner.calls[review_index].cwd, promote_path)
        self.assertIn(
            "Promotion outcome: `partial`",
            runner.calls[review_index].input_text,
        )
        self.assertIn("Command failed", runner.calls[review_index].input_text)
        self.assertIn(
            "## Recovery and Consistency Guidance",
            runner.calls[review_index].input_text,
        )
        self.assertLess(
            runner.calls[review_index].input_text.index(
                "## Recovery and Consistency Guidance"
            ),
            runner.calls[review_index].input_text.index(
                "## Follow-up GitHub Issue Drafts"
            ),
        )
        self.assertIn(
            "Post-push promotion metadata failed:", str(error_context.exception)
        )
        self.assertIn("Post-push promotion metadata failed:", stderr.getvalue())
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["stage"], "failed")
        self.assertIn("Command failed", manifest["failure"]["message"])
        self.assertEqual(manifest["post_promotion_review"]["status"], "completed")
        self.assertEqual(
            manifest["post_promotion_review"]["artifact_path"],
            str(artifact_path),
        )
        self.assertEqual(artifact, POST_PROMOTION_REVIEW_MARKDOWN.rstrip() + "\n")
        self.assertEqual(manifest["github_metadata"]["status"], "failed")
        self.assertEqual(
            manifest["github_metadata"]["issues"][0]["metadata_status"],
            "closing",
        )
        self.assertEqual(manifest["pushes"]["promotion_target"]["status"], "pushed")
        self.assertEqual(manifest["pushes"]["source_branch_sync"]["status"], "pushed")
        self.assertNotIn(("git", "worktree", "remove", str(promote_path)), commands)

    def test_promotion_runs_aemo_etl_e2e_gate_from_source_worktree_before_side_effects(
        self,
    ) -> None:
        changed_file = (
            "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"
        )
        runner = FakeRunner(
            diff_outputs=[f"{changed_file}\n"],
            rev_parse_outputs=["source-sha\n", "promotion-sha\n"],
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, promote=True)
            with redirect_stdout(io.StringIO()):
                loop._promote()

            commands = [call.args for call in runner.calls]
            e2e_command = (
                "scripts/aemo-etl-e2e",
                "run",
                "--rebuild",
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1800",
                "--max-concurrent-runs",
                "6",
                "--seed-root",
                str(tmp_path / "repo" / "backend-services" / ".e2e/aemo-etl"),
            )
            e2e_index = commands.index(e2e_command)
            run_prek_index = commands.index(("make", "run-prek"))
            source_path = tmp_path / "worktrees" / "agent-promote-source-dev-to-main"
            promote_path = tmp_path / "worktrees" / "agent-promote-dev-to-main"
            source_worktree_index = commands.index(
                (
                    "git",
                    "worktree",
                    "add",
                    "--detach",
                    str(source_path),
                    "source-sha",
                )
            )
            promote_worktree_index = commands.index(
                (
                    "git",
                    "worktree",
                    "add",
                    "--detach",
                    str(promote_path),
                    "origin/main",
                )
            )
            merge_index = commands.index(
                ("git", "merge", "--no-ff", "source-sha", "-m", "Promote dev to main")
            )
            push_main_index = commands.index(("git", "push", "origin", "HEAD:main"))

            self.assertLess(source_worktree_index, run_prek_index)
            self.assertLess(run_prek_index, e2e_index)
            self.assertLess(e2e_index, promote_worktree_index)
            self.assertLess(e2e_index, merge_index)
            self.assertLess(e2e_index, push_main_index)
            self.assertEqual(
                runner.calls[run_prek_index].cwd,
                source_path / "backend-services" / "dagster-user" / "aemo-etl",
            )
            self.assertEqual(
                runner.calls[e2e_index].cwd,
                source_path / "backend-services",
            )

            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        e2e_results = [
            result
            for result in manifest["qa_results"]
            if result["name"] == "aemo-etl End-to-end test"
        ]
        self.assertEqual(len(e2e_results), 1)
        self.assertEqual(
            e2e_results[0]["command"],
            [
                "scripts/aemo-etl-e2e",
                "run",
                "--rebuild",
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1800",
                "--max-concurrent-runs",
                "6",
                "--seed-root",
                str(tmp_path / "repo" / "backend-services" / ".e2e/aemo-etl"),
            ],
        )
        self.assertTrue(
            e2e_results[0]["cwd"].endswith(
                "/agent-promote-source-dev-to-main/backend-services"
            )
        )
        self.assertEqual(e2e_results[0]["status"], "passed")
        self.assertIn(
            "promotion-gate-1-aemo-etl-end-to-end-test.log",
            e2e_results[0]["log_path"],
        )
        self.assertEqual(manifest["source_tree"]["revision"], "source-sha")

    def test_promotion_e2e_gate_failure_stops_before_side_effects(self) -> None:
        changed_file = (
            "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            e2e_command = (
                "scripts/aemo-etl-e2e",
                "run",
                "--rebuild",
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1800",
                "--max-concurrent-runs",
                "6",
                "--seed-root",
                str(tmp_path / "repo" / "backend-services" / ".e2e/aemo-etl"),
            )
            runner = FakeRunner(
                diff_outputs=[f"{changed_file}\n"],
                rev_parse_outputs=["source-sha\n"],
                fail_commands={e2e_command},
            )

            loop = make_loop(tmp_path, runner, promote=True)
            with self.assertRaises(ralph.CommandFailure):
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    loop._promote()

            commands = [call.args for call in runner.calls]
            manifest = load_run_manifest(tmp_path, run_glob="promote-*")

        self.assertIn(e2e_command, commands)
        source_path = Path(tmp) / "worktrees" / "agent-promote-source-dev-to-main"
        promote_path = Path(tmp) / "worktrees" / "agent-promote-dev-to-main"
        self.assertIn(
            (
                "git",
                "worktree",
                "add",
                "--detach",
                str(source_path),
                "source-sha",
            ),
            commands,
        )
        self.assertNotIn(
            (
                "git",
                "worktree",
                "add",
                "--detach",
                str(promote_path),
                "origin/main",
            ),
            commands,
        )
        self.assertFalse(any(command[:2] == ("git", "merge") for command in commands))
        self.assertFalse(
            any(command[:3] == ("git", "push", "origin") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "comment") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "edit") for command in commands)
        )
        self.assertFalse(
            any(command[:3] == ("gh", "issue", "close") for command in commands)
        )
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["source_tree"]["revision"], "source-sha")
        self.assertIsNone(manifest["promotion_commit"])
        self.assertEqual(manifest["pushes"], {})
        self.assertEqual(manifest["github_metadata"]["status"], "not_started")
        failed_e2e_results = [
            result
            for result in manifest["qa_results"]
            if result["name"] == "aemo-etl End-to-end test"
        ]
        self.assertEqual(len(failed_e2e_results), 1)
        self.assertEqual(failed_e2e_results[0]["status"], "failed")

    def test_post_push_issue_metadata_failure_stops_without_cleanup(self) -> None:
        close_command = (
            "gh",
            "issue",
            "close",
            "42",
            "-R",
            "example/repo",
            "--reason",
            "completed",
        )
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_commands={close_command},
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(ralph.PostPushFailure):
                    loop._handle_implementation(
                        make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
                    )

        commands = [call.args for call in runner.calls]
        self.assertIn(("git", "push", "origin", "HEAD:main"), commands)
        self.assertNotIn(
            (
                "git",
                "worktree",
                "remove",
                str(Path(tmp) / "worktrees" / "agent-issue-42-implement-thing"),
            ),
            commands,
        )


if __name__ == "__main__":
    unittest.main()
