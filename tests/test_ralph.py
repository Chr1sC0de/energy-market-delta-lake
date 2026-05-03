from __future__ import annotations

import importlib.util
import io
import json
import sys
import threading
import time
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


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


class FakeRunner:
    def __init__(
        self,
        *,
        status_outputs: list[str] | None = None,
        diff_outputs: list[str] | None = None,
        rev_parse_outputs: list[str] | None = None,
        command_outputs: dict[tuple[str, ...], list[str]] | None = None,
        fail_commands: set[tuple[str, ...]] | dict[tuple[str, ...], int] | None = None,
    ) -> None:
        self.dry_run = False
        self.calls: list[FakeCall] = []
        self.status_outputs = status_outputs or []
        self.diff_outputs = diff_outputs or []
        self.rev_parse_outputs = rev_parse_outputs or []
        self.command_outputs = command_outputs or {}
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
        if command[:3] == ("gh", "issue", "view") and "comments" in command:
            return ralph.CompletedCommand(stdout=json.dumps({"comments": []}), stderr="")
        return ralph.CompletedCommand(stdout="", stderr="")


def make_loop(
    tmp_path: Path,
    runner: FakeRunner,
    *,
    delivery_mode: str = ralph.TRUNK_MODE,
    target_branch: str | None = None,
    source_branch: str = ralph.DEFAULT_GITFLOW_BRANCH,
    promote: bool = False,
    issue: int | None = None,
    drain: bool = False,
    max_issues: int = ralph.DEFAULT_DRAIN_BUDGET,
    dry_run: bool = False,
    allow_dirty_worktree: bool = False,
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
        issue=issue,
        drain=drain,
        max_issues=max_issues,
        dry_run=dry_run,
        allow_dirty_worktree=allow_dirty_worktree,
        bootstrap_labels=False,
        issue_limit=100,
        log_root=log_root,
        worktree_container=worktree_container,
    )
    runner.dry_run = dry_run
    return ralph.RalphLoop(config, runner)


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

    def test_triage_prompt_uses_ralph_triage_skill(self) -> None:
        prompt = ralph.triage_prompt(make_issue({"needs-triage"}), "example/repo")

        self.assertIn("Use the $ralph-triage skill", prompt)
        self.assertNotIn("Use the $triage skill", prompt)
        self.assertIn(ralph.AI_TRIAGE_DISCLAIMER, prompt)
        self.assertIn("Do not edit repo", prompt)

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

    def test_parse_args_help_describes_default_drain_budget(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output), self.assertRaises(SystemExit):
            ralph.parse_args(["--help"])

        help_text = output.getvalue()
        self.assertIn("Defaults to 10", help_text)
        self.assertIn("Use 0 for unlimited", help_text)
        self.assertIn("--allow-dirty-worktree", help_text)

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
            rev_parse_outputs=["promotion-sha\n"],
            command_outputs={
                issue_list_command: [json.dumps(issue_payload)],
                issue_comments_command: [json.dumps(comments_payload)],
            },
            fail_commands={target_ancestor_command: 1},
        )

        with tempfile.TemporaryDirectory() as tmp:
            loop = make_loop(Path(tmp), runner, promote=True)
            with redirect_stdout(io.StringIO()):
                loop._promote()

            comment_path = next((Path(tmp) / "logs").glob("promote-*/issue-42-comment.md"))
            comment = comment_path.read_text(encoding="utf-8")
            manifest = load_run_manifest(Path(tmp), run_glob="promote-*")

        commands = [call.args for call in runner.calls]
        self.assertIn(
            ("git", "merge", "--no-ff", "origin/dev", "-m", "Promote dev to main"),
            commands,
        )
        self.assertIn(("git", "push", "origin", "HEAD:main"), commands)
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
                "agent-merged",
                "--remove-label",
                "agent-integrated",
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
        self.assertIn("Ralph promotion completed.", comment)
        self.assertIn("Promotion commit: `promotion-sha`", comment)
        self.assertIn("Integrated commit: `abc1234`", comment)
        self.assertEqual(manifest["run_kind"], "promotion")
        self.assertEqual(manifest["status"], "succeeded")
        self.assertEqual(manifest["delivery_mode"], "gitflow")
        self.assertEqual(manifest["source_branch"], "dev")
        self.assertEqual(manifest["integration_target"], "main")
        self.assertEqual(manifest["promotion_commit"]["sha"], "promotion-sha")
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
