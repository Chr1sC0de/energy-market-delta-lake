from __future__ import annotations

import importlib.util
import io
import json
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


RALPH_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ralph.py"
SPEC = importlib.util.spec_from_file_location("ralph", RALPH_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load scripts/ralph.py")
ralph = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ralph
SPEC.loader.exec_module(ralph)


IMPLEMENTATION_BODY = """## What to build
Build it.

## Acceptance criteria
- [ ] It works.

## Blocked by
None
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


def implementation_body_with_blockers(*blockers: int) -> str:
    blocked_by = "\n".join(f"- #{blocker}" for blocker in blockers) if blockers else "None"
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

READY_ISSUE_REFRESH_ANALYSIS_MARKDOWN = """# Ready Issue Refresh Analysis

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


def make_issue(
    labels: set[str],
    body: str = "",
    *,
    number: int = 42,
    title: str = "Implement thing",
):
    return ralph.Issue(
        number=number,
        title=title,
        body=body,
        labels=frozenset(labels),
        created_at=datetime(2026, 4, 30, tzinfo=UTC),
        updated_at=datetime(2026, 4, 30, tzinfo=UTC),
        url=f"https://github.com/example/repo/issues/{number}",
        comments=0,
        author="reporter",
    )


def load_run_manifest(tmp_path: Path, run_glob: str = "issue-42-*") -> dict[str, Any]:
    manifest_path = next((tmp_path / "logs").glob(f"{run_glob}/ralph-run.json"))
    return json.loads(manifest_path.read_text(encoding="utf-8"))


@dataclass(frozen=True)
class FakeCall:
    args: tuple[str, ...]
    cwd: Path
    input_text: str | None
    log_path: Path | None
    phase: str | None
    execute_in_dry_run: bool
    env: dict[str, str] | None


class FakeRunner:
    def __init__(
        self,
        *,
        status_outputs: list[str] | None = None,
        diff_outputs: list[str] | None = None,
        rev_parse_outputs: list[str] | None = None,
        command_outputs: dict[tuple[str, ...], list[str]] | None = None,
        fail_commands: set[tuple[str, ...]] | dict[tuple[str, ...], int] | None = None,
        fail_post_promotion_review: bool = False,
        fail_ready_issue_refresh_analysis: bool = False,
        fail_issue_create: bool = False,
    ) -> None:
        self.dry_run = False
        self.calls: list[FakeCall] = []
        self.status_outputs = status_outputs or []
        self.diff_outputs = diff_outputs or []
        self.rev_parse_outputs = rev_parse_outputs or []
        self.command_outputs = command_outputs or {}
        self.fail_post_promotion_review = fail_post_promotion_review
        self.fail_ready_issue_refresh_analysis = fail_ready_issue_refresh_analysis
        self.fail_issue_create = fail_issue_create
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
            )
        )
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("fake log", encoding="utf-8")
        if command in self.fail_commands:
            raise ralph.CommandFailure(
                args,
                cwd,
                self.fail_commands[command],
                "",
                "fake failure",
                log_path,
            )
        if command in self.command_outputs:
            return ralph.CompletedCommand(
                stdout=self.command_outputs[command].pop(0),
                stderr="",
            )
        if command == ("git", "status", "--porcelain"):
            stdout = self.status_outputs.pop(0) if self.status_outputs else ""
            return ralph.CompletedCommand(stdout=stdout, stderr="")
        if command[:3] == ("git", "diff", "--name-only"):
            return ralph.CompletedCommand(stdout=self.diff_outputs.pop(0), stderr="")
        if command[:2] == ("git", "rev-parse"):
            return ralph.CompletedCommand(stdout=self.rev_parse_outputs.pop(0), stderr="")
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
            return ralph.CompletedCommand(stdout=json.dumps({"comments": []}), stderr="")
        if command == ("gh", "auth", "token"):
            return ralph.CompletedCommand(stdout="fake-gh-token\n", stderr="")
        if command[:2] == ("codex", "exec") and input_text is not None:
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
                    stdout=READY_ISSUE_REFRESH_ANALYSIS_MARKDOWN,
                    stderr="",
                )
        return ralph.CompletedCommand(stdout="", stderr="")


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
    issue: int | None = None,
    drain: bool = False,
    max_issues: int = ralph.DEFAULT_DRAIN_BUDGET,
    dry_run: bool = False,
    allow_dirty_worktree: bool = False,
    issue_limit: int = 100,
) -> ralph.RalphLoop:
    repo_root = tmp_path / "repo"
    worktree_container = tmp_path / "worktrees"
    log_root = tmp_path / "logs"
    repo_root.mkdir()
    worktree_container.mkdir()
    config = ralph.LoopConfig(
        repo_root=repo_root,
        repo="example/repo",
        delivery_mode=delivery_mode,
        target_branch=target_branch,
        source_branch=source_branch,
        promote=promote,
        skip_post_promotion_review=skip_post_promotion_review,
        skip_post_promotion_followups=skip_post_promotion_followups,
        issue=issue,
        drain=drain,
        max_issues=max_issues,
        dry_run=dry_run,
        allow_dirty_worktree=allow_dirty_worktree,
        bootstrap_labels=False,
        issue_limit=issue_limit,
        log_root=log_root,
        worktree_container=worktree_container,
    )
    runner.dry_run = dry_run
    return ralph.RalphLoop(config, runner)


def write_recovery_manifest(
    tmp_path: Path,
    *,
    delivery_mode: str = ralph.TRUNK_MODE,
    target_branch: str = ralph.DEFAULT_TRUNK_BRANCH,
    metadata_status: str = "failed",
    push_status: str = "pushed",
    commit_sha: str = "abc1234",
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
                "name": "Ralph unit tests",
                "command": ["python3", "-m", "unittest", "discover", "-s", "tests"],
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
) -> dict[str, Any]:
    return {
        "number": number,
        "title": f"Issue {number}",
        "body": body,
        "labels": [{"name": label} for label in labels],
        "createdAt": "2026-04-30T00:00:00Z",
        "updatedAt": "2026-04-30T00:00:00Z",
        "url": f"https://github.com/example/repo/issues/{number}",
        "comments": [],
        "author": {"login": "reporter"},
    }


class CountingRalphLoop(ralph.RalphLoop):
    def __init__(self, config: ralph.LoopConfig, runner: FakeRunner, ready_count: int) -> None:
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
        return make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)

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

    def _next_triage_issue(self) -> ralph.Issue | None:
        return None


class RalphHelperTests(unittest.TestCase):
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

    def test_ready_issue_refresh_notes_filter_limit_and_order_by_created_at(self) -> None:
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

    def test_ready_issue_refresh_notes_preserve_input_order_without_timestamps(self) -> None:
        comments = [
            {"body": ready_issue_refresh_body(f"refresh {index}")} for index in range(1, 7)
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
        self.assertIn("Treat the issue body above as the primary implementation contract.", prompt)

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
            any("Missing required issue section" in reason for reason in invalid_result.reasons)
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

    def test_parse_blockers_reads_issue_references_from_blocked_by_section(self) -> None:
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
            make_issue({"ready-for-agent", stop_label}, IMPLEMENTATION_BODY, number=number)
            for number, stop_label in enumerate(stop_labels, start=43)
        ]

        candidates = ralph.select_ready_issue_refresh_candidates(
            issues,
            just_integrated_issue_number=42,
            blocker_state=lambda _number: "CLOSED",
        )

        self.assertEqual(candidates, [])

    def test_ready_issue_refresh_candidates_respect_issue_limit_scan_bound(self) -> None:
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
                ("python3", "-m", "unittest", "discover", "-s", "tests"),
                Path("/repo"),
                "Ralph unit tests",
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
        )

        self.assertIn("Use the repo-local $ralph-issue-refresh skill", prompt)
        self.assertIn("Do not comment, edit labels, edit issue bodies, close issues", prompt)
        self.assertIn("Do not run `gh issue comment`, `gh issue edit`, `gh issue close`", prompt)
        self.assertIn("commit, push, pull, fetch, merge, rebase, reset", prompt)
        self.assertIn("Delivery mode: `trunk`", prompt)
        self.assertIn("Integration target: `main`", prompt)
        self.assertIn("Local integration commit: `merge-sha`", prompt)
        self.assertIn("- `scripts/ralph.py`", prompt)
        self.assertIn("`python3 -m unittest discover -s tests` from `/repo`", prompt)
        self.assertIn("Run logs: `/logs/issue-42-test`", prompt)
        self.assertIn("## What to build", prompt)
        self.assertIn("### Candidate issue #43: Refresh candidate", prompt)
        self.assertIn("- #42", prompt)
        self.assertIn("# Ready Issue Refresh Analysis", prompt)
        self.assertIn("## Candidate Issue Update Plan", prompt)

    def test_basic_triage_candidate_accepts_unlabeled_and_needs_triage(self) -> None:
        self.assertTrue(ralph.is_basic_triage_candidate(make_issue(set())))
        self.assertTrue(ralph.is_basic_triage_candidate(make_issue({"needs-triage"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"ready-for-agent"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"wontfix"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"agent-merged"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"agent-reviewing"})))

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
        self.assertEqual(plan.target_branch, "agent/exploratory/issue-42-implement-thing")
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
                "aemo-etl Unit test",
                "aemo-etl Component test",
                "aemo-etl Integration test",
                "aemo-etl Commit check",
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

    def test_select_qa_commands_for_mixed_aemo_etl_docs_and_runtime_changes(self) -> None:
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
                "aemo-etl Unit test",
                "aemo-etl Component test",
                "aemo-etl Integration test",
                "aemo-etl Commit check",
                "root Commit check",
            ],
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
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1200",
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
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1200",
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
        self.assertEqual(names, ["root Commit check", "Ralph unit tests"])

    def test_select_promotion_gate_commands_skips_non_aemo_changes(self) -> None:
        commands = ralph.select_promotion_gate_commands(["scripts/ralph.py"], Path("/repo"))

        self.assertEqual(commands, [])

    def test_parse_git_status_paths_includes_untracked_and_renamed_files(self) -> None:
        status = "\n".join(
            [
                " M scripts/ralph.py",
                "?? tests/test_ralph.py",
                "R  old-name.md -> docs/agents/ralph-loop.md",
            ]
        )
        self.assertEqual(
            ralph.parse_git_status_paths(status),
            ["docs/agents/ralph-loop.md", "scripts/ralph.py", "tests/test_ralph.py"],
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
                "--full-auto",
                "--json",
                "-",
            ],
        )

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

    def test_post_promotion_review_markdown_reads_codex_json_final_message(self) -> None:
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

    def test_run_codex_injects_sandbox_issue_access_without_recording_token(self) -> None:
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
                manifest_payload["qa_runtime_env"]["variables"]["DAGSTER_HOME"]["source"],
                "ralph_default",
            )
            self.assertEqual(
                manifest_payload["qa_runtime_env"]["variables"]["UV_CACHE_DIR"]["value"],
                str(runtime_root / "uv-cache"),
            )

    def test_default_worktree_container_matches_sibling_worktree_layout(self) -> None:
        current = Path("/work/repo__worktrees/refactor")
        self.assertEqual(
            ralph.default_worktree_container(current),
            Path("/work/repo__worktrees"),
        )
        main = Path("/work/repo")
        self.assertEqual(ralph.default_worktree_container(main), Path("/work/repo__worktrees"))

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

    def test_parse_args_help_describes_default_drain_budget(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output), self.assertRaises(SystemExit):
            ralph.parse_args(["--help"])

        help_text = output.getvalue()
        self.assertIn("Defaults to 10", help_text)
        self.assertIn("Use 0 for unlimited", help_text)
        self.assertIn("--allow-dirty-worktree", help_text)
        self.assertIn("--skip-post-promotion-review", help_text)
        self.assertIn("--skip-post-promotion-followups", help_text)
        self.assertIn("exploratory", help_text)

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
            " M scripts/ralph.py\n?? tests/test_ralph.py\n",
        )

        self.assertIn("Root worktree has uncommitted changes: /repo", message)
        self.assertIn("--allow-dirty-worktree", message)
        self.assertIn("- scripts/ralph.py", message)
        self.assertIn("- tests/test_ralph.py", message)

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
                max_issues=ralph.parse_args(["--drain", "--max-issues", "0"]).max_issues,
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

    def test_dirty_root_blocks_live_issue_drain_and_promote_before_side_effects(self) -> None:
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

                self.assertIn("Root worktree has uncommitted changes", str(caught.exception))
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
                    any(command[:3] == ("git", "worktree", "add") for command in commands)
                )
                self.assertFalse(
                    any(command[:3] == ("git", "push", "origin") for command in commands)
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
        self.assertIn("DRY RUN: would implement #42: Implement thing", output.getvalue())
        commands = [call.args for call in runner.calls]
        self.assertNotIn(("git", "status", "--porcelain"), commands)

    def test_dry_run_reports_ready_issue_refresh_candidate_selection(self) -> None:
        runner = FakeRunner()
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner, drain=True, dry_run=True)
            probe = PreflightProbeLoop(loop.config, runner)
            output = io.StringIO()

            with redirect_stdout(output):
                probe.run()

        text = output.getvalue()
        self.assertIn("DRY RUN: would implement #42: Implement thing", text)
        self.assertIn(
            "DRY RUN: after Local integration of #42, would select Ready issue "
            "refresh candidates within --issue-limit 100.",
            text,
        )
        commands = [call.args for call in runner.calls]
        self.assertFalse(any(command[:2] == ("codex", "exec") for command in commands))
        self.assertFalse(any(command[:3] == ("gh", "issue", "edit") for command in commands))
        self.assertFalse(any(command[:3] == ("gh", "issue", "comment") for command in commands))
        self.assertFalse(any(command[:3] == ("gh", "issue", "close") for command in commands))

    def test_completion_comment_records_local_integration_evidence(self) -> None:
        issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
        qa_results = [
            ralph.QAResult(
                command=ralph.QACommand(
                    ("python3", "-m", "unittest", "discover", "-s", "tests"),
                    Path("/repo"),
                    "Ralph unit tests",
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
        self.assertIn("python3 -m unittest discover -s tests", comment)
        self.assertIn("Issue #42 will be closed by the Ralph loop.", comment)

    def test_exploratory_completion_comment_records_review_branch(self) -> None:
        issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
        qa_results = [
            ralph.QAResult(
                command=ralph.QACommand(
                    ("python3", "-m", "unittest", "discover", "-s", "tests"),
                    Path("/repo"),
                    "Ralph unit tests",
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
        self.assertIn("Target branch: `agent/exploratory/issue-42-implement-thing`", comment)
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
        self.assertIn("--recover-run", text)

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

        self.assertIn("not reachable from expected Integration target", str(caught.exception))
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
        self.assertFalse(any(command[:3] == ("gh", "issue", "edit") for command in commands))
        self.assertFalse(any(command[:3] == ("gh", "issue", "close") for command in commands))

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
                issue_view_command: [issue_view_output(labels=[ralph.AGENT_RUNNING_LABEL])],
                issue_state_command: [json.dumps({"state": "OPEN"})],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            run_dir = write_recovery_manifest(tmp_path)
            loop = make_loop(tmp_path, runner)
            output = io.StringIO()

            with redirect_stdout(output):
                ralph.RalphRunRecovery(loop.config, runner).recover(run_dir)

            comment_path = run_dir / "issue-42-comment.md"
            comment = comment_path.read_text(encoding="utf-8")
            manifest = json.loads((run_dir / "ralph-run.json").read_text(encoding="utf-8"))

        commands = [call.args for call in runner.calls]
        self.assertIn("Ralph trunk integration completed.", comment)
        self.assertIn("Commit: `abc1234`", comment)
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
        self.assertIn("Recovered issue #42 trunk metadata for abc1234.", output.getvalue())

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
                issue_view_command: [issue_view_output(labels=[ralph.AGENT_RUNNING_LABEL])],
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

            manifest = json.loads((run_dir / "ralph-run.json").read_text(encoding="utf-8"))

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
        self.assertFalse(any(command[:3] == ("gh", "issue", "close") for command in commands))
        self.assertEqual(manifest["github_metadata"]["status"], "marked_integrated")
        self.assertIn("Recovered issue #42 Gitflow metadata for abc1234.", output.getvalue())


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
            self.assertIn("Ralph heartbeat: phase=streaming test phase; log=", output.getvalue())

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

            comment_path = next((Path(tmp) / "logs").glob("issue-42-*/issue-42-comment.md"))
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
        self.assertFalse(any(command[:3] == ("git", "worktree", "add") for command in commands))
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
        self.assertFalse(any(command[:3] == ("git", "worktree", "add") for command in commands))
        self.assertFalse(any(command[:3] == ("git", "push", "origin") for command in commands))
        self.assertIn("Missing required issue section(s): Review focus", comment)
        self.assertEqual(manifest["status"], "failed")
        self.assertEqual(manifest["delivery_mode"], "exploratory")
        self.assertEqual(
            manifest["integration_target"],
            "agent/exploratory/issue-42-implement-thing",
        )
        self.assertEqual(manifest["github_metadata"]["status"], "failure_commented")
        self.assertIn("Review focus", manifest["failure"]["message"])

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
                call
                for call in runner.calls
                if call.args == ("python3", "-m", "unittest", "discover", "-s", "tests")
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

    def test_successful_implementation_squash_merges_pushes_comments_and_closes(self) -> None:
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
            self.assertFalse(any(command[:3] == ("gh", "pr", "create") for command in commands))
            progress = output.getvalue()
            self.assertIn("#42: claiming issue with agent-running", progress)
            self.assertIn("#42: running QA Ralph unit tests", progress)
            self.assertIn("#42: pushing merge-sha to main", progress)
            self.assertIn("Issue #42 merged to main: merge-sha", progress)
            self.assertIn("#42: Codex implementation attempt 1", phases)
            self.assertIn("#42: QA Ralph unit tests", phases)

            comment_path = next((Path(tmp) / "logs").glob("issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(Path(tmp))
            self.assertIn("Ralph trunk integration completed.", comment)
            self.assertIn("Commit: `merge-sha`", comment)
            self.assertEqual(manifest["status"], "succeeded")
            self.assertEqual(manifest["issue"]["number"], 42)
            self.assertEqual(manifest["delivery_mode"], "trunk")
            self.assertEqual(manifest["integration_target"], "main")
            self.assertEqual(manifest["branches"]["issue"], "agent/issue-42-implement-thing")
            self.assertEqual(manifest["integration_commit"]["sha"], "merge-sha")
            self.assertEqual(manifest["pushes"]["integration_target"]["status"], "pushed")
            self.assertEqual(manifest["github_metadata"]["status"], "closed")
            self.assertEqual(manifest["qa_results"][0]["status"], "passed")

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
        included_note = ready_issue_refresh_body("Issue body blockers changed after #68.")
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
        codex_call = next(call for call in runner.calls if call.args[:2] == ("codex", "exec"))
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
                issue_list_command: [json.dumps([issue_payload(43, ["ready-for-agent"])])]
            },
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            loop = make_loop(tmp_path, runner, drain=True)
            output = io.StringIO()

            with redirect_stdout(output):
                loop._handle_implementation(make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY))

            manifest = load_run_manifest(tmp_path)
            artifact_path = next(tmp_path.glob("logs/issue-42-*/ready-issue-refresh-analysis.md"))
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
        self.assertLess(commands.index(close_command), commands.index(issue_list_command))
        self.assertLess(commands.index(issue_list_command), analysis_index)
        self.assertIn(
            "Ready issue refresh candidate selection found 1 candidate(s) after "
            "Local integration of #42.",
            output.getvalue(),
        )
        self.assertIn("- #43: Issue 43", output.getvalue())
        self.assertIn("Running read-only Ready issue refresh analysis for #42.", output.getvalue())
        self.assertEqual(artifact, READY_ISSUE_REFRESH_ANALYSIS_MARKDOWN.rstrip() + "\n")
        self.assertEqual(manifest["ready_issue_refresh"]["status"], "completed")
        self.assertEqual(manifest["ready_issue_refresh"]["candidate_issue_numbers"], [43])
        self.assertEqual(
            manifest["ready_issue_refresh"]["artifact_path"],
            str(artifact_path),
        )
        self.assertIsNone(manifest["ready_issue_refresh"]["failure"])
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
        after_analysis_commands = [call.args for call in runner.calls[analysis_index + 1 :]]
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

    def test_gitflow_implementation_creates_dev_integrates_and_leaves_issue_open(self) -> None:
        ls_remote = ("git", "ls-remote", "--exit-code", "--heads", "origin", "dev")
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
            diff_outputs=["scripts/ralph.py\n"],
            rev_parse_outputs=["base-sha\n", "base-sha\n", "merge-sha\n"],
            fail_commands={ls_remote: 2},
        )
        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner, delivery_mode=ralph.GITFLOW_MODE)
            issue = make_issue({"ready-for-agent"}, IMPLEMENTATION_BODY)
            output = io.StringIO()

            with redirect_stdout(output):
                loop._handle_implementation(issue)

            commands = [call.args for call in runner.calls]
            self.assertIn(("git", "push", "origin", "origin/main:refs/heads/dev"), commands)
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
            self.assertFalse(any(command[:3] == ("gh", "issue", "close") for command in commands))
            self.assertIn("Issue #42 integrated to dev: merge-sha", output.getvalue())

            comment_path = next((Path(tmp) / "logs").glob("issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            self.assertIn("Ralph Gitflow integration completed.", comment)
            self.assertIn("Target branch: `dev`", comment)
            self.assertIn("will stay open until Ralph promotes `dev`", comment)

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
            self.assertFalse(any(command[:3] == ("gh", "issue", "close") for command in commands))
            self.assertIn(
                f"Issue #42 ready for review on {handoff_branch}: merge-sha",
                output.getvalue(),
            )

            comment_path = next((Path(tmp) / "logs").glob("issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(Path(tmp))
            self.assertIn("Ralph exploratory handoff completed.", comment)
            self.assertIn(f"Target branch: `{handoff_branch}`", comment)
            self.assertEqual(manifest["delivery_mode"], "exploratory")
            self.assertEqual(manifest["integration_target"], handoff_branch)
            self.assertEqual(manifest["branches"]["issue"], handoff_branch)
            self.assertEqual(manifest["github_metadata"]["status"], "marked_reviewing")

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
        self.assertFalse(any(command[:3] == ("git", "worktree", "add") for command in commands))
        self.assertFalse(any(command[:3] == ("git", "push", "origin") for command in commands))
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
                issue_list_command: [json.dumps([issue_payload(43, ["ready-for-agent"])])]
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
        self.assertLess(commands.index(reviewing_command), commands.index(issue_list_command))
        self.assertIn(
            "Ready issue refresh candidate selection found 1 candidate(s) after "
            "Exploratory handoff of #42.",
            output.getvalue(),
        )

    def test_gitflow_implementation_syncs_dev_with_main_before_issue_branch(self) -> None:
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
            command
            for command in commands
            if command == ("python3", "-m", "unittest", "discover", "-s", "tests")
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
        qa_command = ("python3", "-m", "unittest", "discover", "-s", "tests")
        runner = FakeRunner(
            status_outputs=[" M scripts/ralph.py\n", " M scripts/ralph.py\n"],
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
            if result["name"] == "Ralph unit tests" and result["status"] == "failed"
        ]
        self.assertGreaterEqual(len(failed_qa), 1)
        self.assertTrue(
            any(event["stage"] == "qa_failed" for event in manifest["events"])
        )

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

            comment_path = next((Path(tmp) / "logs").glob("promote-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            artifact_path = next((Path(tmp) / "logs").glob("promote-*/post-promotion-review.md"))
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
        qa_command = ("python3", "-m", "unittest", "discover", "-s", "tests")
        source_worktree_index = commands.index(source_worktree)
        qa_index = commands.index(qa_command)
        promote_worktree_index = commands.index(promote_worktree)
        self.assertLess(source_worktree_index, qa_index)
        self.assertLess(qa_index, promote_worktree_index)
        self.assertEqual(runner.calls[qa_index].cwd, source_path)
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
        self.assertIn("Run a Post-promotion review", runner.calls[review_index].input_text)
        self.assertIn("## Learnings", runner.calls[review_index].input_text)
        self.assertIn(
            "## Recovery and Consistency Guidance",
            runner.calls[review_index].input_text,
        )
        self.assertIn("## Follow-up GitHub Issue Drafts", runner.calls[review_index].input_text)
        self.assertIn("Do not create the follow-up issues yourself.", runner.calls[review_index].input_text)
        self.assertIn("Automatic validated follow-up issue creation is enabled.", runner.calls[review_index].input_text)
        self.assertLess(
            runner.calls[review_index].input_text.index("## Recovery and Consistency Guidance"),
            runner.calls[review_index].input_text.index("## Follow-up GitHub Issue Drafts"),
        )
        self.assertIn(
            "Promotion outcome: `succeeded`",
            runner.calls[review_index].input_text,
        )
        self.assertIn("Promotion error: `None`", runner.calls[review_index].input_text)
        self.assertIn(
            "`abc1234` Ralph Local integration for issue 42 - "
            "verified Local integration commit for #42 Implement thing",
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
        self.assertEqual(manifest["post_promotion_followups"]["validation_downgrades"], [])
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

    def test_promotion_skip_post_promotion_review_flag_disables_review_agent(self) -> None:
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
        self.assertFalse(any(command[:3] == ("gh", "issue", "create") for command in commands))
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
            artifact_path = next(tmp_path.glob("logs/promote-*/post-promotion-review.md"))

        commands = [call.args for call in runner.calls]
        promote_path = Path(tmp) / "worktrees" / "agent-promote-dev-to-main"
        review_command = tuple(
            ralph.codex_exec_command(
                promote_path,
                output_last_message=artifact_path,
            )
        )
        self.assertIn(review_command, commands)
        self.assertFalse(any(command[:3] == ("gh", "issue", "create") for command in commands))
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
            call.args for call in runner.calls if call.args[:3] == ("gh", "issue", "create")
        )
        self.assertIn("needs-triage", create_command)
        self.assertNotIn("ready-for-agent", create_command)
        self.assertNotIn("delivery-gitflow", create_command)
        self.assertIn("## Ralph validation evidence", body)
        self.assertIn("Missing required issue section", body)
        self.assertIn("Expected exactly one category label", body)
        self.assertEqual(manifest_payload["post_promotion_followups"]["status"], "completed")
        self.assertEqual(
            manifest_payload["post_promotion_followups"]["created"][0]["validation_status"],
            "needs_triage",
        )
        self.assertEqual(
            manifest_payload["post_promotion_followups"]["validation_downgrades"][0]["labels"],
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
        self.assertFalse(any(command[:3] == ("gh", "issue", "create") for command in commands))
        self.assertEqual(manifest_payload["post_promotion_followups"]["status"], "completed")
        self.assertEqual(
            manifest_payload["post_promotion_followups"]["duplicates"][0]["url"],
            "https://github.com/example/repo/issues/77",
        )
        self.assertEqual(manifest_payload["post_promotion_followups"]["created"], [])

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
        self.assertFalse(any(command[:3] == ("git", "worktree", "add") for command in commands))
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
            artifact_path = next(tmp_path.glob("logs/promote-*/post-promotion-review.md"))
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
        qa_command = ("python3", "-m", "unittest", "discover", "-s", "tests")
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
            artifact_path = next(tmp_path.glob("logs/promote-*/post-promotion-review.md"))
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
        self.assertEqual(runner.calls[qa_index].cwd, source_path)
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
            runner.calls[review_index].input_text.index("## Recovery and Consistency Guidance"),
            runner.calls[review_index].input_text.index("## Follow-up GitHub Issue Drafts"),
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
            if result["name"] == "Ralph unit tests"
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
                promotion_log_command: ["abc1234\x00Ralph Local integration for issue 42\n"],
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
            artifact_path = next(tmp_path.glob("logs/promote-*/post-promotion-review.md"))
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
            runner.calls[review_index].input_text.index("## Recovery and Consistency Guidance"),
            runner.calls[review_index].input_text.index("## Follow-up GitHub Issue Drafts"),
        )
        self.assertIn("Post-push promotion metadata failed:", str(error_context.exception))
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
        changed_file = "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"
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
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1200",
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
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1200",
                "--max-concurrent-runs",
                "6",
                "--seed-root",
                str(tmp_path / "repo" / "backend-services" / ".e2e/aemo-etl"),
            ],
        )
        self.assertTrue(e2e_results[0]["cwd"].endswith("/agent-promote-source-dev-to-main/backend-services"))
        self.assertEqual(e2e_results[0]["status"], "passed")
        self.assertIn(
            "promotion-gate-1-aemo-etl-end-to-end-test.log",
            e2e_results[0]["log_path"],
        )
        self.assertEqual(manifest["source_tree"]["revision"], "source-sha")

    def test_promotion_e2e_gate_failure_stops_before_side_effects(self) -> None:
        changed_file = "backend-services/dagster-user/aemo-etl/src/aemo_etl/definitions.py"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            e2e_command = (
                "scripts/aemo-etl-e2e",
                "run",
                "--scenario",
                "promotion-gas-model",
                "--timeout-seconds",
                "1200",
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
