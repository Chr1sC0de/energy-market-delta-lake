from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


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


def make_issue(labels: set[str], body: str = ""):
    return ralph.Issue(
        number=42,
        title="Implement thing",
        body=body,
        labels=frozenset(labels),
        created_at=datetime(2026, 4, 30, tzinfo=UTC),
        updated_at=datetime(2026, 4, 30, tzinfo=UTC),
        url="https://github.com/example/repo/issues/42",
        comments=0,
        author="reporter",
    )


@dataclass(frozen=True)
class FakeCall:
    args: tuple[str, ...]
    cwd: Path
    input_text: str | None
    log_path: Path | None
    execute_in_dry_run: bool


class FakeRunner:
    def __init__(
        self,
        *,
        status_outputs: list[str] | None = None,
        diff_outputs: list[str] | None = None,
        rev_parse_outputs: list[str] | None = None,
        fail_commands: set[tuple[str, ...]] | None = None,
    ) -> None:
        self.dry_run = False
        self.calls: list[FakeCall] = []
        self.status_outputs = status_outputs or []
        self.diff_outputs = diff_outputs or []
        self.rev_parse_outputs = rev_parse_outputs or []
        self.fail_commands = fail_commands or set()

    def run(
        self,
        args: list[str],
        *,
        cwd: Path,
        input_text: str | None = None,
        log_path: Path | None = None,
        execute_in_dry_run: bool = True,
    ):
        command = tuple(args)
        self.calls.append(
            FakeCall(
                args=command,
                cwd=cwd,
                input_text=input_text,
                log_path=log_path,
                execute_in_dry_run=execute_in_dry_run,
            )
        )
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text("fake log", encoding="utf-8")
        if command in self.fail_commands:
            raise ralph.CommandFailure(args, cwd, 1, "", "fake failure", log_path)
        if command == ("git", "status", "--porcelain"):
            return ralph.CompletedCommand(stdout=self.status_outputs.pop(0), stderr="")
        if command[:3] == ("git", "diff", "--name-only"):
            return ralph.CompletedCommand(stdout=self.diff_outputs.pop(0), stderr="")
        if command[:2] == ("git", "rev-parse"):
            return ralph.CompletedCommand(stdout=self.rev_parse_outputs.pop(0), stderr="")
        return ralph.CompletedCommand(stdout="", stderr="")


def make_loop(tmp_path: Path, runner: FakeRunner) -> ralph.RalphLoop:
    repo_root = tmp_path / "repo"
    worktree_container = tmp_path / "worktrees"
    log_root = tmp_path / "logs"
    repo_root.mkdir()
    worktree_container.mkdir()
    config = ralph.LoopConfig(
        repo_root=repo_root,
        repo="example/repo",
        base="main",
        issue=None,
        drain=False,
        max_issues=3,
        dry_run=False,
        bootstrap_labels=False,
        issue_limit=100,
        log_root=log_root,
        worktree_container=worktree_container,
    )
    return ralph.RalphLoop(config, runner)


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

    def test_basic_triage_candidate_accepts_unlabeled_and_needs_triage(self) -> None:
        self.assertTrue(ralph.is_basic_triage_candidate(make_issue(set())))
        self.assertTrue(ralph.is_basic_triage_candidate(make_issue({"needs-triage"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"ready-for-agent"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"wontfix"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"agent-merged"})))

    def test_select_qa_commands_for_aemo_etl_changes(self) -> None:
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

    def test_select_qa_commands_for_docs_and_script_changes(self) -> None:
        commands = ralph.select_qa_commands(["docs/workflow.md", "scripts/ralph.py"], Path("/repo"))
        names = [command.name for command in commands]
        self.assertEqual(names, ["root Commit check", "Ralph unit tests"])

    def test_parse_git_status_paths_includes_untracked_and_renamed_files(self) -> None:
        status = "\n".join(
            [
                " M scripts/ralph.py",
                "?? tests/test_ralph.py",
                "R  old-name.md -> docs/agent-issue-loop.md",
            ]
        )
        self.assertEqual(
            ralph.parse_git_status_paths(status),
            ["docs/agent-issue-loop.md", "scripts/ralph.py", "tests/test_ralph.py"],
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
                "--full-auto",
                "--json",
                "-",
            ],
        )

    def test_default_worktree_container_matches_sibling_worktree_layout(self) -> None:
        current = Path("/work/repo__worktrees/refactor")
        self.assertEqual(ralph.default_worktree_container(current), Path("/work/repo__worktrees"))
        main = Path("/work/repo")
        self.assertEqual(ralph.default_worktree_container(main), Path("/work/repo__worktrees"))

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
        )

        self.assertIn("Ralph local integration completed.", comment)
        self.assertIn("Commit: `abc123`", comment)
        self.assertIn("- `scripts/ralph.py`", comment)
        self.assertIn("python3 -m unittest discover -s tests", comment)
        self.assertIn("Issue #42 will be closed by the Ralph loop.", comment)


class RalphLoopLocalIntegrationTests(unittest.TestCase):
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

            comment_path = next((Path(tmp) / "logs").glob("issue-42-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            self.assertIn("Ralph local integration completed.", comment)
            self.assertIn("Commit: `merge-sha`", comment)

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
