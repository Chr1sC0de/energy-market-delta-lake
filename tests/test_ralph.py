from __future__ import annotations

import importlib.util
import sys
import unittest
from datetime import UTC, datetime
from pathlib import Path


RALPH_PATH = Path(__file__).resolve().parents[1] / "scripts" / "ralph.py"
SPEC = importlib.util.spec_from_file_location("ralph", RALPH_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load scripts/ralph.py")
ralph = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ralph
SPEC.loader.exec_module(ralph)


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

    def test_basic_triage_candidate_accepts_unlabeled_and_needs_triage(self) -> None:
        self.assertTrue(ralph.is_basic_triage_candidate(make_issue(set())))
        self.assertTrue(ralph.is_basic_triage_candidate(make_issue({"needs-triage"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"ready-for-agent"})))
        self.assertFalse(ralph.is_basic_triage_candidate(make_issue({"wontfix"})))

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

    def test_default_worktree_container_matches_sibling_worktree_layout(self) -> None:
        current = Path("/work/repo__worktrees/refactor")
        self.assertEqual(ralph.default_worktree_container(current), Path("/work/repo__worktrees"))
        main = Path("/work/repo")
        self.assertEqual(ralph.default_worktree_container(main), Path("/work/repo__worktrees"))


if __name__ == "__main__":
    unittest.main()
