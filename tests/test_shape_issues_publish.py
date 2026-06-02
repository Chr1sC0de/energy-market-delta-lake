from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock


PUBLISHER_PATH = (
    Path(__file__).resolve().parents[1]
    / ".agents"
    / "skills"
    / "shape-issues"
    / "scripts"
    / "publish_shape_issues.py"
)
REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_SCRIPT = REPO_ROOT / ".agents" / "skills" / "shape-issues" / "scripts" / "shape_issue_gate.py"
FIXTURE_ASSESSOR = (
    REPO_ROOT
    / ".agents"
    / "skills"
    / "shape-issues"
    / "scripts"
    / "fixture_context_assessor.py"
)
SPEC = importlib.util.spec_from_file_location("publish_shape_issues", PUBLISHER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load shape-issues publisher")
publisher = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = publisher
SPEC.loader.exec_module(publisher)


READY_BODY = """## What to build
Publish one narrow tracer-bullet implementation slice.

## Acceptance criteria
- [ ] The issue is published only after confirmation.

## Blocked by
None - can start immediately.

## Current context
The shape-issues publisher consumes a passing gate report.

## Context anchors
- Path: `.agents/skills/shape-issues/SKILL.md`
- Symbol: `PUBLISHABLE_ACTIONS`
- Label: `needs-triage`
- Target: `Chr1sC0de/energy-market-delta-lake`
- QA: `python3 -m unittest tests/test_shape_issues_publish.py`
- Test lane: `root agent Unit test`

## Stiffness estimate
Low. This is one root agent workflow surface.

## QA plan
Run `python3 -m unittest tests/test_shape_issues_publish.py`.
"""


class FakeGithubClient:
    existing_by_marker: dict[str, Any] = {}
    created: list[dict[str, Any]] = []
    preflight_calls = 0
    preflight_failure: publisher.GithubCommandError | None = None
    find_failure: publisher.GithubCommandError | None = None
    create_failures_by_title: dict[str, publisher.GithubCommandError] = {}
    next_number = 40

    def __init__(self, *, repo: str, repo_root: Path, gh_binary: str) -> None:
        self.repo = repo
        self.repo_root = repo_root
        self.gh_binary = gh_binary

    @classmethod
    def reset(cls) -> None:
        cls.existing_by_marker = {}
        cls.created = []
        cls.preflight_calls = 0
        cls.preflight_failure = None
        cls.find_failure = None
        cls.create_failures_by_title = {}
        cls.next_number = 40

    def preflight(self) -> None:
        self.__class__.preflight_calls += 1
        if self.__class__.preflight_failure is not None:
            raise self.__class__.preflight_failure

    def find_issue_by_source_marker(self, marker: str) -> Any:
        if self.__class__.find_failure is not None:
            raise self.__class__.find_failure
        return self.existing_by_marker.get(marker)

    def create_issue(self, *, title: str, body_path: Path, labels: tuple[str, ...]) -> Any:
        if title in self.__class__.create_failures_by_title:
            raise self.__class__.create_failures_by_title[title]
        self.__class__.next_number += 1
        number = self.__class__.next_number
        reference = publisher.IssueReference(
            number=number,
            title=title,
            url=f"https://github.com/example/repo/issues/{number}",
        )
        self.__class__.created.append(
            {
                "title": title,
                "body_path": body_path,
                "labels": labels,
                "reference": reference,
            }
        )
        return reference


def issue_payload(
    issue_id: str,
    title: str,
    *,
    blocked_by: list[str] | None = None,
    classification: str = "afk",
) -> dict[str, Any]:
    payload = {
        "id": issue_id,
        "title": title,
        "classification": classification,
        "body": READY_BODY,
        "labels": ["enhancement", "delivery-gitflow"],
    }
    if blocked_by is not None:
        payload["blocked_by"] = blocked_by
    return payload


def write_bundle_and_report(
    tmp_path: Path,
    *,
    issues: list[dict[str, Any]],
    actions: dict[str, str],
    assessor_provider: str | None = None,
) -> tuple[Path, Path]:
    bundle_path = tmp_path / "bundle.json"
    report_path = tmp_path / "report.json"
    bundle_path.write_text(
        json.dumps(
            {
                "summary": "Publish shaped issue drafts.",
                "shared_context": [],
                "operator_overrides": {},
                "issues": issues,
            }
        ),
        encoding="utf-8",
    )
    parsed_bundle = publisher.parse_bundle(bundle_path)
    issue_by_id = {issue.issue_id: issue for issue in parsed_bundle.issues}
    report_payload: dict[str, Any] = {
        "summary": "Publish shaped issue drafts.",
        "bundle_digest": parsed_bundle.source_digest,
        "issues": [
            {
                "id": issue_id,
                "title": issue_id,
                "action": action,
                "ready": action in {"ready", "exploratory"},
                "recommended_labels": ["ready-for-agent"],
                "source_digest": issue_by_id[issue_id].source_digest,
            }
            for issue_id, action in actions.items()
        ],
    }
    if assessor_provider is not None:
        report_payload["context_assessor"] = {
            "provider": assessor_provider,
            "schema_version": "shape-issues-context-assessor-v1",
        }
    report_path.write_text(
        json.dumps(report_payload),
        encoding="utf-8",
    )
    return bundle_path, report_path


def write_bundle_only(tmp_path: Path, *, shared_context: list[str] | None = None) -> Path:
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(
        json.dumps(
            {
                "summary": "Publish shaped issue drafts.",
                "shared_context": shared_context or ["shape-issues publisher context"],
                "operator_overrides": {},
                "issues": [issue_payload("first", "First issue")],
            }
        ),
        encoding="utf-8",
    )
    return bundle_path


def run_gate(bundle_path: Path, out_dir: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(GATE_SCRIPT),
            str(bundle_path),
            "--repo-root",
            str(REPO_ROOT),
            "--out-dir",
            str(out_dir),
            "--context-assessor-command",
            f"{sys.executable} {FIXTURE_ASSESSOR}",
            "--context-assessor-name",
            "fixture",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)


def publish_config(
    tmp_path: Path,
    bundle_path: Path,
    report_path: Path,
    *,
    confirm_publish: bool = True,
    dry_run: bool = True,
    allow_fixture_publish: bool = False,
    publish_backend: str = publisher.PUBLISH_BACKEND_GH,
) -> Any:
    return publisher.PublishConfig(
        bundle_path=bundle_path,
        report_path=report_path,
        out_dir=tmp_path,
        repo_root=tmp_path,
        repo="example/repo",
        confirm_publish=confirm_publish,
        dry_run=dry_run,
        gh_binary="gh",
        publish_backend=publish_backend,
        allow_fixture_publish=allow_fixture_publish,
    )


def completed_process(
    args: list[str],
    *,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=args, returncode=0, stdout=stdout, stderr=stderr)


def command_error(
    phase: str,
    *,
    exit_code: int = 2,
    stderr: str = "command stderr",
    stdout: str = "command stdout",
) -> publisher.GithubCommandError:
    failure = publisher.GithubCommandFailure(
        phase=phase,
        exit_code=exit_code,
        stderr_summary=stderr,
        stdout_summary=stdout,
    )
    return publisher.GithubCommandError(
        failure,
        publisher.format_github_command_failure(failure, guidance="test guidance."),
    )


class ShapeIssuesPublishTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_github_client = publisher.GithubClient
        publisher.GithubClient = FakeGithubClient
        FakeGithubClient.reset()
        self.tempdir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tempdir.name)

    def tearDown(self) -> None:
        publisher.GithubClient = self.original_github_client
        self.tempdir.cleanup()

    def test_github_preflight_missing_gh_message_is_actionable(self) -> None:
        client = self.original_github_client(
            repo="example/repo",
            repo_root=self.tmp_path,
            gh_binary="missing-gh",
        )

        with mock.patch.object(
            publisher.subprocess,
            "run",
            side_effect=FileNotFoundError("missing-gh"),
        ):
            with self.assertRaisesRegex(publisher.PublishError, "Install GitHub CLI") as context:
                client.preflight()

        message = str(context.exception)
        self.assertIn("preflight-gh", message)
        self.assertIn("exit code unavailable", message)
        self.assertIn("stderr summary: <empty>", message)
        self.assertIn("stdout summary: <empty>", message)

    def test_github_preflight_auth_failure_message_is_actionable(self) -> None:
        client = self.original_github_client(
            repo="example/repo",
            repo_root=self.tmp_path,
            gh_binary="gh",
        )

        def fake_run(args: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
            if args[1] == "--version":
                return completed_process(args, stdout="gh version 2")
            raise subprocess.CalledProcessError(
                1,
                args,
                output="auth stdout",
                stderr="not logged in",
            )

        with mock.patch.object(publisher.subprocess, "run", side_effect=fake_run):
            with self.assertRaises(publisher.PublishError) as context:
                client.preflight()

        message = str(context.exception)
        self.assertIn("preflight-auth", message)
        self.assertIn("exit code 1", message)
        self.assertIn("gh auth login", message)
        self.assertIn("stderr summary: not logged in", message)
        self.assertIn("stdout summary: auth stdout", message)

    def test_github_preflight_repository_failure_message_is_actionable(self) -> None:
        client = self.original_github_client(
            repo="example/repo",
            repo_root=self.tmp_path,
            gh_binary="gh",
        )

        def fake_run(args: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
            if args[1] == "--version":
                return completed_process(args, stdout="gh version 2")
            if args[1:3] == ["auth", "status"]:
                return completed_process(args, stderr="Logged in")
            raise subprocess.CalledProcessError(
                1,
                args,
                output="repo stdout",
                stderr="could not resolve repository",
            )

        with mock.patch.object(publisher.subprocess, "run", side_effect=fake_run):
            with self.assertRaises(publisher.PublishError) as context:
                client.preflight()

        message = str(context.exception)
        self.assertIn("preflight-repository", message)
        self.assertIn("exit code 1", message)
        self.assertIn("--repo example/repo", message)
        self.assertIn("stderr summary: could not resolve repository", message)
        self.assertIn("stdout summary: repo stdout", message)

    def test_refuses_without_confirmation(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
        )

        with self.assertRaisesRegex(publisher.PublishError, "--confirm-publish"):
            publisher.publish(
                publish_config(
                    self.tmp_path,
                    bundle_path,
                    report_path,
                    confirm_publish=False,
                )
            )

    def test_refuses_non_publishable_gate_action(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "split"},
        )

        with self.assertRaisesRegex(publisher.PublishError, "gate action is split"):
            publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))

    def test_refuses_stale_report_after_bundle_changes(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
        )
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
        payload["issues"][0]["body"] = READY_BODY.replace(
            "Publish one narrow tracer-bullet implementation slice.",
            "Publish a changed implementation slice.",
        )
        bundle_path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(publisher.PublishError, "changed after gate"):
            publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))

    def test_refuses_report_missing_bundle_digest(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
        )
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        payload.pop("bundle_digest")
        report_path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(publisher.PublishError, "missing bundle_digest"):
            publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))

    def test_refuses_stale_real_gate_report_after_shared_context_changes(self) -> None:
        bundle_path = write_bundle_only(self.tmp_path)
        run_gate(bundle_path, self.tmp_path)
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
        payload["shared_context"] = ["changed context"]
        bundle_path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(publisher.PublishError, "Bundle changed after gate"):
            publisher.publish(
                publish_config(
                    self.tmp_path,
                    bundle_path,
                    self.tmp_path / "report.json",
                )
            )

    def test_refuses_stale_real_gate_report_after_operator_overrides_change(self) -> None:
        bundle_path = write_bundle_only(self.tmp_path)
        run_gate(bundle_path, self.tmp_path)
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
        payload["operator_overrides"] = {"first": "Operator override added after gate."}
        bundle_path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(publisher.PublishError, "Bundle changed after gate"):
            publisher.publish(
                publish_config(
                    self.tmp_path,
                    bundle_path,
                    self.tmp_path / "report.json",
                )
            )

    def test_real_gate_report_can_publish_dry_run(self) -> None:
        bundle_path = write_bundle_only(self.tmp_path)
        run_gate(bundle_path, self.tmp_path)

        manifest = publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                self.tmp_path / "report.json",
            )
        )

        self.assertEqual(manifest["issues"][0]["state"], "dry-run")
        self.assertEqual(manifest["context_assessor"]["provider"], "fixture")
        self.assertEqual(
            manifest["fixture_publish"],
            {"allow_fixture_publish": False, "dry_run": True},
        )
        body = Path(manifest["issues"][0]["body_path"]).read_text(encoding="utf-8")
        self.assertIn("Issue context assessor provider: `fixture`", body)
        self.assertIn("Fixture publish policy: `--dry-run` preview", body)

    def test_fixture_gate_non_dry_run_requires_explicit_override(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
            assessor_provider="fixture",
        )

        with self.assertRaisesRegex(publisher.PublishError, "--allow-fixture-publish"):
            publisher.publish(
                publish_config(
                    self.tmp_path,
                    bundle_path,
                    report_path,
                    dry_run=False,
                )
            )

        self.assertEqual(FakeGithubClient.created, [])
        self.assertFalse((self.tmp_path / "publish-manifest.json").exists())

    def test_fixture_gate_override_records_manifest_and_body_provenance(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
            assessor_provider="fixture",
        )

        manifest = publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                report_path,
                dry_run=False,
                allow_fixture_publish=True,
            )
        )

        self.assertEqual(manifest["issues"][0]["state"], "created")
        self.assertEqual(manifest["context_assessor"]["provider"], "fixture")
        self.assertEqual(
            manifest["fixture_publish"],
            {"allow_fixture_publish": True, "dry_run": False},
        )
        self.assertEqual(len(FakeGithubClient.created), 1)
        body = FakeGithubClient.created[0]["body_path"].read_text(encoding="utf-8")
        self.assertIn("Issue context assessor provider: `fixture`", body)
        self.assertIn(
            "Fixture publish policy: published with `--allow-fixture-publish`",
            body,
        )

    def test_live_assessor_non_dry_run_publish_does_not_need_fixture_override(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
            assessor_provider="codex",
        )

        manifest = publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                report_path,
                dry_run=False,
            )
        )

        self.assertEqual(manifest["issues"][0]["state"], "created")
        self.assertNotIn("context_assessor", manifest)
        self.assertNotIn("fixture_publish", manifest)
        body = FakeGithubClient.created[0]["body_path"].read_text(encoding="utf-8")
        self.assertNotIn("Issue context assessor provider:", body)
        self.assertNotIn("Fixture publish policy:", body)

    def test_preflight_failure_happens_before_body_files_or_manifest(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
        )
        FakeGithubClient.preflight_failure = command_error(
            publisher.PREFLIGHT_AUTH_PHASE,
            exit_code=1,
            stderr="not logged in",
            stdout="",
        )

        with self.assertRaisesRegex(publisher.PublishError, "preflight-auth") as context:
            publisher.publish(
                publish_config(
                    self.tmp_path,
                    bundle_path,
                    report_path,
                    dry_run=False,
                )
            )

        self.assertIn("before writing publish body files", str(context.exception))
        self.assertEqual(FakeGithubClient.preflight_calls, 1)
        self.assertFalse((self.tmp_path / "publish-bodies").exists())
        self.assertFalse((self.tmp_path / "publish-manifest.json").exists())

    def test_auto_backend_writes_connector_plan_when_gh_preflight_fails(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload("dependent", "Dependent issue", blocked_by=["blocker"]),
                issue_payload("blocker", "Blocker issue"),
            ],
            actions={"dependent": "ready", "blocker": "ready"},
            assessor_provider="codex",
        )
        FakeGithubClient.preflight_failure = command_error(
            publisher.PREFLIGHT_AUTH_PHASE,
            exit_code=1,
            stderr="not logged in",
            stdout="",
        )

        manifest = publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                report_path,
                dry_run=False,
                publish_backend=publisher.PUBLISH_BACKEND_AUTO,
            )
        )

        self.assertEqual(FakeGithubClient.preflight_calls, 1)
        self.assertEqual(FakeGithubClient.created, [])
        self.assertEqual(manifest["publish_backend"], publisher.PUBLISH_BACKEND_AUTO)
        self.assertEqual(
            [entry["state"] for entry in manifest["issues"]],
            ["connector-plan", "connector-plan"],
        )
        self.assertEqual(
            manifest["gh_failure"]["phase"],
            publisher.PREFLIGHT_AUTH_PHASE,
        )
        plan = json.loads(
            (self.tmp_path / "connector-publish-plan.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            plan["schema_version"],
            publisher.CONNECTOR_PLAN_SCHEMA_VERSION,
        )
        self.assertEqual(
            [issue["id"] for issue in plan["issues"]],
            ["blocker", "dependent"],
        )
        blocker_entry = plan["issues"][0]
        dependent_entry = plan["issues"][1]
        self.assertIn("body_path", blocker_entry)
        self.assertNotIn("body_template_path", blocker_entry)
        self.assertEqual(dependent_entry["blocked_by"], ["blocker"])
        self.assertNotIn("body_path", dependent_entry)
        self.assertIn("body_template_path", dependent_entry)
        self.assertEqual(
            dependent_entry["render_contract"]["blocked_by_draft_ids"],
            ["blocker"],
        )
        blocker_body = Path(blocker_entry["body_path"]).read_text(encoding="utf-8")
        dependent_template = Path(dependent_entry["body_template_path"]).read_text(
            encoding="utf-8"
        )
        self.assertIn("shape-issues-source", blocker_body)
        self.assertIn("{{created_issue_url:blocker}}", dependent_template)
        self.assertNotIn("None - can start immediately.", dependent_template)

    def test_connector_plan_backend_does_not_preflight_gh(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
            assessor_provider="codex",
        )

        manifest = publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                report_path,
                dry_run=False,
                publish_backend=publisher.PUBLISH_BACKEND_CONNECTOR_PLAN,
            )
        )

        self.assertEqual(FakeGithubClient.preflight_calls, 0)
        self.assertEqual(manifest["issues"][0]["state"], "connector-plan")
        self.assertTrue((self.tmp_path / "connector-publish-plan.json").exists())

    def test_connector_plan_preserves_fixture_provenance_in_body_templates(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload("dependent", "Dependent issue", blocked_by=["blocker"]),
                issue_payload("blocker", "Blocker issue"),
            ],
            actions={"dependent": "ready", "blocker": "ready"},
            assessor_provider="fixture",
        )

        publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                report_path,
                dry_run=False,
                allow_fixture_publish=True,
                publish_backend=publisher.PUBLISH_BACKEND_CONNECTOR_PLAN,
            )
        )

        plan = json.loads(
            (self.tmp_path / "connector-publish-plan.json").read_text(encoding="utf-8")
        )
        blocker_body = Path(plan["issues"][0]["body_path"]).read_text(encoding="utf-8")
        dependent_template = Path(plan["issues"][1]["body_template_path"]).read_text(
            encoding="utf-8"
        )
        for body in (blocker_body, dependent_template):
            self.assertIn("Issue context assessor provider: `fixture`", body)
            self.assertIn(
                "Fixture publish policy: published with `--allow-fixture-publish`",
                body,
            )

    def test_duplicate_search_failure_records_github_diagnostics(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
        )
        FakeGithubClient.find_failure = command_error(
            publisher.DUPLICATE_SEARCH_PHASE,
            exit_code=7,
            stderr="duplicate stderr",
            stdout="duplicate stdout",
        )

        with self.assertRaisesRegex(publisher.PublishError, "duplicate-search") as context:
            publisher.publish(
                publish_config(
                    self.tmp_path,
                    bundle_path,
                    report_path,
                    dry_run=False,
                )
            )

        message = str(context.exception)
        self.assertIn("exit code 7", message)
        self.assertIn("stderr summary: duplicate stderr", message)
        self.assertIn("stdout summary: duplicate stdout", message)
        manifest = json.loads((self.tmp_path / "publish-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["recovery"], (
            "Inspect publish-manifest.json, keep any created issues, then rerun "
            "the publisher with the same bundle. Source markers will skip duplicates."
        ))
        failed = manifest["issues"][0]
        self.assertEqual(failed["state"], "failed")
        self.assertEqual(
            failed["gh_failure"],
            {
                "exit_code": 7,
                "phase": "duplicate-search",
                "stderr_summary": "duplicate stderr",
                "stdout_summary": "duplicate stdout",
            },
        )

    def test_issue_create_failure_records_github_diagnostics(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
        )
        FakeGithubClient.create_failures_by_title["First issue"] = command_error(
            publisher.ISSUE_CREATE_PHASE,
            exit_code=8,
            stderr="create stderr",
            stdout="create stdout",
        )

        with self.assertRaisesRegex(publisher.PublishError, "issue-create") as context:
            publisher.publish(
                publish_config(
                    self.tmp_path,
                    bundle_path,
                    report_path,
                    dry_run=False,
                )
            )

        message = str(context.exception)
        self.assertIn("exit code 8", message)
        self.assertIn("stderr summary: create stderr", message)
        self.assertIn("stdout summary: create stdout", message)
        manifest = json.loads((self.tmp_path / "publish-manifest.json").read_text(encoding="utf-8"))
        failed = manifest["issues"][0]
        self.assertEqual(failed["state"], "failed")
        self.assertEqual(
            failed["gh_failure"],
            {
                "exit_code": 8,
                "phase": "issue-create",
                "stderr_summary": "create stderr",
                "stdout_summary": "create stdout",
            },
        )

    def test_refuses_duplicate_gate_report_ids(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
        )
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        payload["issues"].append(dict(payload["issues"][0]))
        report_path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(publisher.PublishError, "duplicate issue id"):
            publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))

    def test_refuses_duplicate_issue_ids(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload("same", "First issue"),
                issue_payload("same", "Second issue"),
            ],
            actions={"same": "ready"},
        )

        with self.assertRaisesRegex(publisher.PublishError, "Duplicate issue id"):
            publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))

    def test_refuses_slug_colliding_issue_ids(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload("foo/bar", "First issue"),
                issue_payload("foo bar", "Second issue"),
            ],
            actions={"foo/bar": "ready", "foo bar": "ready"},
        )

        with self.assertRaisesRegex(publisher.PublishError, "Duplicate generated"):
            publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))

    def test_refuses_human_decision_classification(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload(
                    "decision",
                    "Decision issue",
                    classification="human-decision",
                )
            ],
            actions={"decision": "ready"},
        )

        with self.assertRaisesRegex(publisher.PublishError, "non-publishable classification"):
            publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))

    def test_refuses_classification_action_mismatch(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload(
                    "explore",
                    "Exploratory issue",
                    classification="exploratory",
                )
            ],
            actions={"explore": "ready"},
        )

        with self.assertRaisesRegex(publisher.PublishError, "requires gate action exploratory"):
            publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))

    def test_dry_run_writes_manifest_and_body_without_github_mutation(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
        )

        manifest = publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))

        self.assertEqual(manifest["issues"][0]["state"], "dry-run")
        self.assertEqual(manifest["issues"][0]["labels"], ["needs-triage"])
        self.assertEqual(FakeGithubClient.created, [])
        body = Path(manifest["issues"][0]["body_path"]).read_text(encoding="utf-8")
        self.assertIn("## Shape Issues source", body)
        self.assertIn("shape-issues-source", body)
        self.assertNotIn(str(self.tmp_path), body)

    def test_duplicate_source_marker_skips_create(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[issue_payload("first", "First issue")],
            actions={"first": "ready"},
        )
        marker = publisher.source_marker(
            bundle_path,
            publisher.parse_bundle(bundle_path).issues[0],
        )
        FakeGithubClient.existing_by_marker[marker] = publisher.IssueReference(
            number=77,
            title="Existing issue",
            url="https://github.com/example/repo/issues/77",
        )

        manifest = publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                report_path,
                dry_run=False,
            )
        )

        self.assertEqual(manifest["issues"][0]["state"], "duplicate")
        self.assertEqual(manifest["issues"][0]["number"], 77)
        self.assertEqual(FakeGithubClient.created, [])

    def test_partial_publication_rerun_uses_source_marker_recovery(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload("dependent", "Dependent issue", blocked_by=["blocker"]),
                issue_payload("blocker", "Blocker issue"),
            ],
            actions={"dependent": "ready", "blocker": "ready"},
        )
        FakeGithubClient.create_failures_by_title["Dependent issue"] = command_error(
            publisher.ISSUE_CREATE_PHASE,
            exit_code=8,
            stderr="create stderr",
            stdout="create stdout",
        )

        with self.assertRaisesRegex(publisher.PublishError, "issue-create"):
            publisher.publish(
                publish_config(
                    self.tmp_path,
                    bundle_path,
                    report_path,
                    dry_run=False,
                )
            )

        failed_manifest = json.loads(
            (self.tmp_path / "publish-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            [entry["state"] for entry in failed_manifest["issues"]],
            ["created", "failed"],
        )
        created_entry = failed_manifest["issues"][0]
        FakeGithubClient.existing_by_marker[created_entry["source_marker"]] = (
            publisher.IssueReference(
                number=created_entry["number"],
                title=created_entry["title"],
                url=created_entry["url"],
            )
        )
        FakeGithubClient.create_failures_by_title = {}

        recovered_manifest = publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                report_path,
                dry_run=False,
            )
        )

        self.assertEqual(
            [entry["state"] for entry in recovered_manifest["issues"]],
            ["duplicate", "created"],
        )
        self.assertEqual(
            [call["title"] for call in FakeGithubClient.created],
            ["Blocker issue", "Dependent issue"],
        )

    def test_blockers_publish_first_and_rewrite_blocked_by_references(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload("dependent", "Dependent issue", blocked_by=["blocker"]),
                issue_payload("blocker", "Blocker issue"),
            ],
            actions={"dependent": "ready", "blocker": "ready"},
        )

        manifest = publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                report_path,
                dry_run=False,
            )
        )

        self.assertEqual([entry["id"] for entry in manifest["issues"]], ["blocker", "dependent"])
        self.assertEqual([entry["labels"] for entry in manifest["issues"]], [["needs-triage"], ["needs-triage"]])
        self.assertEqual([call["title"] for call in FakeGithubClient.created], ["Blocker issue", "Dependent issue"])
        dependent_body = FakeGithubClient.created[1]["body_path"].read_text(encoding="utf-8")
        self.assertIn("## Blocked by\n- #41", dependent_body)

    def test_external_issue_blocker_rewrites_without_bundle_draft(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload("dependent", "Dependent issue", blocked_by=["#346"]),
            ],
            actions={"dependent": "ready"},
        )

        manifest = publisher.publish(
            publish_config(
                self.tmp_path,
                bundle_path,
                report_path,
                dry_run=False,
            )
        )

        self.assertEqual([entry["id"] for entry in manifest["issues"]], ["dependent"])
        self.assertEqual([call["title"] for call in FakeGithubClient.created], ["Dependent issue"])
        dependent_body = FakeGithubClient.created[0]["body_path"].read_text(encoding="utf-8")
        self.assertIn("## Blocked by\n- #346", dependent_body)

    def test_blocked_by_cycle_is_rejected(self) -> None:
        bundle_path, report_path = write_bundle_and_report(
            self.tmp_path,
            issues=[
                issue_payload("first", "First issue", blocked_by=["second"]),
                issue_payload("second", "Second issue", blocked_by=["first"]),
            ],
            actions={"first": "ready", "second": "ready"},
        )

        with self.assertRaisesRegex(publisher.PublishError, "blocked_by cycle"):
            publisher.publish(publish_config(self.tmp_path, bundle_path, report_path))


if __name__ == "__main__":
    unittest.main()
