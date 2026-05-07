from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


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
FIXTURE_PROVIDER = (
    REPO_ROOT / ".agents" / "skills" / "shape-issues" / "scripts" / "fixture_embed_jsonl.py"
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
    next_number = 40

    def __init__(self, *, repo: str, repo_root: Path, gh_binary: str) -> None:
        self.repo = repo
        self.repo_root = repo_root
        self.gh_binary = gh_binary

    @classmethod
    def reset(cls) -> None:
        cls.existing_by_marker = {}
        cls.created = []
        cls.next_number = 40

    def find_issue_by_source_marker(self, marker: str) -> Any:
        return self.existing_by_marker.get(marker)

    def create_issue(self, *, title: str, body_path: Path, labels: tuple[str, ...]) -> Any:
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
    report_path.write_text(
        json.dumps(
            {
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
        ),
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
            "--embedding-command",
            f"{sys.executable} {FIXTURE_PROVIDER}",
            "--provider-name",
            "fixture",
            "--model-id",
            "fixture-hash",
            "--corpus-path",
            ".agents/skills/shape-issues/SKILL.md",
            "--semantic-min-score",
            "0.0",
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
