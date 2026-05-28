from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_SCRIPT = REPO_ROOT / ".agents" / "skills" / "shape-issues" / "scripts" / "shape_issue_gate.py"
PUBLISHER_SCRIPT = (
    REPO_ROOT
    / ".agents"
    / "skills"
    / "shape-issues"
    / "scripts"
    / "publish_shape_issues.py"
)
FIXTURE_ASSESSOR = (
    REPO_ROOT
    / ".agents"
    / "skills"
    / "shape-issues"
    / "scripts"
    / "fixture_context_assessor.py"
)


READY_BODY = """## What to build
Harden Ralph ready issue handling around ready-for-agent labels and Local integration evidence.

## Acceptance criteria
- [ ] Ready issue validation keeps required Ralph sections.
- [ ] Local integration evidence stays visible in reports.
- [ ] Root script tests cover the behavior.

## Blocked by
None - can start immediately.

## Current context
Ralph uses GitHub Issues as the queue and validates issue bodies before implementation.

## Context anchors
- Path: `scripts/ralph.py`
- Symbol: `READY_LABEL`
- Label: `ready-for-agent`
- Target: `dev`
- Doc: `docs/agents/ralph-loop.md`
- QA: `python3 -m unittest discover -s tests`
- Test lane: `root script Unit test`

## Stiffness estimate
Low. This is root script policy with existing unit-test coverage.

## QA plan
Run `python3 -m unittest discover -s tests`.
"""

APPROVAL_BODY = READY_BODY + """

## Operator approval evidence

- Purpose: run `$shape-issues` gate against this issue bundle.
- Provider: repo-local Issue context assessor.
- Corpus scope: only the files listed in `## Context anchors`.
- Output path: `.shape-issues/runs/example/`.
- Prohibited: secrets, credentials, unlisted repo files, GitHub mutation, commits, pushes.
- If the command, corpus, or sandbox settings differ, stop and ask the Operator again.
"""


STIFF_BODY = """## What to build
Change Dagster, S3, LocalStack, infrastructure, schema, Promotion, and cross-Subproject behavior.

## Acceptance criteria
- [ ] Dagster assets still materialize.
- [ ] LocalStack S3 paths still work.
- [ ] Infrastructure remains compatible.
- [ ] Schema contracts remain stable.
- [ ] Promotion evidence remains valid.
- [ ] Push check coverage remains valid.

## Blocked by
None - can start immediately.

## Current context
This touches runtime boundaries and multiple Subprojects.

## Context anchors
- Path: `scripts/ralph.py`
- Symbol: `READY_LABEL`
- Label: `ready-for-agent`
- Target: `main`
- Doc: `docs/agents/ralph-loop.md`
- QA: `python3 -m unittest discover -s tests`
- Test lane: `Integration test`

## Stiffness estimate
High. This issue crosses several runtime boundaries.

## QA plan
Run root tests and Integration tests.
"""

NEGATED_STIFF_BODY = """## What to build
Tune shape-issues stiffness scoring for repo-local agent workflow drafts.

## Acceptance criteria
- [ ] Negated boundary language is reported as ignored evidence.
- [ ] Root agent workflow anchors stay on one scoring surface.
- [ ] Unit tests cover the revised scoring behavior.

## Blocked by
None - can start immediately.

## Current context
This does not touch Ralph Local integration, Promotion, GitHub metadata mutation, S3, LocalStack, Dagster, infrastructure, schema, or cross-Subproject runtime behavior.

## Context anchors
- Path: `.agents/skills/shape-issues/scripts/shape_issue_gate.py`
- Path: `tests/test_shape_issue_gate.py`
- Symbol: `STIFFNESS_TERMS`
- Label: `ready-for-agent`
- Target: `dev`
- Doc: `OPERATOR.md`
- Doc: `docs/agents/README.md`
- QA: `python3 -m unittest tests/test_shape_issue_gate.py`
- Test lane: `root agent Unit test`

## Stiffness estimate
Low. The change is limited to the root agent workflow surface.

## QA plan
Run the unit tests without Integration tests or Push check validation.
"""

ROOT_AGENT_BODY = """## What to build
Adjust shape-issues docs and tests for the root agent workflow.

## Acceptance criteria
- [ ] Skill instructions describe the new report fields.
- [ ] Gate contract describes section-aware scoring.
- [ ] Root tests cover the workflow policy.

## Blocked by
None - can start immediately.

## Current context
The shape-issues skill, OPERATOR guidance, and root tests are one agent workflow surface.

## Context anchors
- Path: `.agents/skills/shape-issues/SKILL.md`
- Path: `tests/test_shape_issue_gate.py`
- Symbol: `StiffnessResult`
- Label: `ready-for-agent`
- Target: `dev`
- Doc: `OPERATOR.md`
- Doc: `docs/agents/README.md`
- QA: `python3 -m unittest tests/test_shape_issue_gate.py`
- Test lane: `root agent Unit test`

## Stiffness estimate
Low. This is one workflow surface with local root tests.

## QA plan
Run `python3 -m unittest tests/test_shape_issue_gate.py`.
"""

MEDIUM_RATIO_BODY = """## What to build
Add visible ratio fields to the shape-issues report contract.

## Acceptance criteria
- [ ] Report JSON includes Step size.
- [ ] Report JSON includes safe feedback step.
- [ ] Report JSON includes hidden-coupling pressure.
- [ ] Report JSON includes Stiffness ratio.
- [ ] Report JSON includes ratio level.

## Blocked by
None - can start immediately.

## Current context
This keeps the root agent workflow output contract explicit for future drafts.

## Context anchors
- Path: `.agents/skills/shape-issues/scripts/shape_issue_gate.py`
- Doc: `.agents/skills/shape-issues/references/gate-contract.md`
- Symbol: `StiffnessResult`
- Label: `ready-for-agent`
- Target: `dev`
- QA: `prek run -a`
- Test lane: `root Commit check`

## Stiffness estimate
Medium. The output shape changes for every draft but stays inside the gate.

## QA plan
Run the root Commit check.
"""

HIGH_RATIO_BODY = """## What to build
Adjust Dagster schema integration reporting for one gate output path.

## Acceptance criteria
- [ ] Ratio data stays visible in JSON.
- [ ] Ratio data stays visible in Markdown.
- [ ] Dagster references stay anchored.
- [ ] Schema references stay anchored.
- [ ] Unit tests cover the routing evidence.

## Blocked by
None - can start immediately.

## Current context
This crosses the root agent workflow and one ETL Subproject boundary.

## Context anchors
- Path: `.agents/skills/shape-issues/scripts/shape_issue_gate.py`
- Path: `backend-services/dagster-user/aemo-etl/pyproject.toml`
- Doc: `docs/agents/ralph-loop.md`
- Symbol: `StiffnessResult`
- Label: `ready-for-agent`
- Target: `dev`
- QA: `uv run pytest tests/component`
- Test lane: `Component test`

## Stiffness estimate
High. The slice names Dagster, schema, and integration pressure.

## QA plan
Run Component tests for the changed behavior.
"""

MISSING_FEEDBACK_BODY = """## What to build
Add an intentionally incomplete ratio example.

## Acceptance criteria
- [ ] Missing feedback data does not divide by zero.

## Blocked by
None - can start immediately.

## Current context
This draft omits QA anchors to exercise fallback ratio handling.

## Context anchors
- Path: `.agents/skills/shape-issues/scripts/shape_issue_gate.py`
- Symbol: `StiffnessResult`
- Label: `ready-for-agent`
- Target: `dev`

## Stiffness estimate
Medium. The test is about a missing denominator.

## QA plan
To be added by the shaper.
"""


def write_bundle(tmp_path: Path, body: str, *, overrides: dict[str, str] | None = None) -> Path:
    bundle = {
        "summary": "Shape Ralph issue work.",
        "shared_context": ["Ralph issue drafts need durable context anchors."],
        "operator_overrides": overrides or {},
        "issues": [
            {
                "id": "harden-ready-issue",
                "title": "Harden Ralph ready issue handling",
                "body": body,
                "labels": ["enhancement", "delivery-gitflow"],
            }
        ],
    }
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path


def write_blocked_bundle(tmp_path: Path) -> Path:
    bundle = {
        "summary": "Shape Ralph issue work.",
        "shared_context": ["Ralph issue drafts need durable context anchors."],
        "operator_overrides": {},
        "issues": [
            {
                "id": "dependent",
                "title": "Dependent issue",
                "classification": "afk",
                "blocked_by": ["blocker"],
                "body": READY_BODY.replace(
                    "Harden Ralph ready issue handling",
                    "Harden dependent Ralph issue handling",
                ),
                "labels": ["enhancement", "delivery-gitflow"],
            },
            {
                "id": "blocker",
                "title": "Blocker issue",
                "classification": "afk",
                "body": READY_BODY.replace(
                    "Harden Ralph ready issue handling",
                    "Harden blocker Ralph issue handling",
                ),
                "labels": ["enhancement", "delivery-gitflow"],
            },
        ],
    }
    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text(json.dumps(bundle), encoding="utf-8")
    return bundle_path


def run_gate(bundle_path: Path, out_dir: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    command = [
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
        *extra_args,
    ]
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def load_script_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load script module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def stiffness_for_body(
    gate: ModuleType,
    body: str,
    *,
    context_paths: tuple[str, ...] = (),
) -> object:
    issue = gate.IssueDraft(
        issue_id="ratio-example",
        title="Ratio example",
        body=body,
        labels=("delivery-gitflow", "enhancement"),
        classification=None,
        blocked_by=(),
        source_digest="digest",
    )
    anchors = gate.parse_anchors(body, REPO_ROOT)
    return gate.stiffness_score(issue, anchors, context_paths, gate.Thresholds())


class ShapeIssueGateTests(unittest.TestCase):
    def test_gate_defaults_use_codex_context_assessor_command(self) -> None:
        gate = load_script_module("shape_issue_gate_under_test", GATE_SCRIPT)

        with (
            mock.patch.dict("os.environ", {}, clear=True),
            mock.patch.object(sys, "argv", ["shape_issue_gate.py", "bundle.json"]),
        ):
            args = gate.parse_args()
            command = gate.default_context_assessor_command()

        self.assertEqual(args.context_assessor_name, "codex")
        self.assertIn("codex_context_assessor.py", command)
        self.assertIn("--repo-root .", command)
        self.assertFalse(hasattr(args, "embedding_command"))
        self.assertFalse(hasattr(args, "semantic_min_score"))

    def test_caddyfile_is_readable_context_evidence(self) -> None:
        gate = load_script_module("shape_issue_gate_caddyfile_under_test", GATE_SCRIPT)

        with tempfile.TemporaryDirectory() as tmp:
            caddyfile = Path(tmp) / "Caddyfile"
            caddyfile.write_text(
                "handle @protectedMarimo {\n"
                "    forward_auth {$DAGSTER_AUTHSERVER}\n"
                "}\n",
                encoding="utf-8",
            )

            self.assertTrue(gate.is_candidate_text_file(caddyfile))

    def test_evidence_snippets_prioritize_symbol_anchors(self) -> None:
        gate = load_script_module("shape_issue_gate_snippets_under_test", GATE_SCRIPT)
        text = "\n".join(
            [
                '"""Evaluate shape-issues bundles for context evidence and stiffness."""',
                "stiffness appears in generic prose before the symbol definitions.",
                "",
                "class Thresholds:",
                "    pass",
                "",
                "class StiffnessResult:",
                "    pass",
                "",
                "def stiffness_score(issue):",
                "    return 0",
            ]
        )

        snippets = gate.evidence_snippets(
            text,
            ("Thresholds", "StiffnessResult", "stiffness_score", "stiffness"),
        )
        snippet_text = "\n".join(snippet.text for snippet in snippets)

        self.assertIn("class Thresholds:", snippet_text)
        self.assertIn("class StiffnessResult:", snippet_text)
        self.assertIn("def stiffness_score", snippet_text)

    def test_evidence_document_can_find_deep_symbols(self) -> None:
        gate = load_script_module("shape_issue_gate_deep_symbol_under_test", GATE_SCRIPT)

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            source = repo_root / "large_source.py"
            source.write_text(
                ("# filler\n" * 12_000)
                + "\n\n"
                + "def deep_symbol_anchor():\n"
                + "    return True\n",
                encoding="utf-8",
            )

            document = gate.read_evidence_document(
                repo_root,
                "large_source.py",
                source="anchor",
                search_terms=("def deep_symbol_anchor",),
            )

        self.assertIsNotNone(document)
        snippet_text = "\n".join(snippet.text for snippet in document.snippets)
        self.assertIn("def deep_symbol_anchor", snippet_text)

    def test_ready_issue_passes_with_context_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, READY_BODY), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
            markdown = (tmp_path / "report.md").read_text(encoding="utf-8")

        self.assertRegex(report["bundle_digest"], r"^[0-9a-f]{64}$")
        self.assertNotIn("embedding", report)
        self.assertNotIn("semantic_min_score", report["thresholds"])
        self.assertEqual(report["context_assessor"]["provider"], "fixture")
        self.assertRegex(report["context_assessor"]["corpus_digest"], r"^[0-9a-f]{64}$")
        self.assertIn("## Issue Context Assessor", markdown)
        self.assertIn("- Provider: `fixture`", markdown)
        issue = report["issues"][0]
        self.assertEqual(issue["action"], "ready")
        self.assertTrue(issue["ready"])
        self.assertEqual(issue["recommended_state_label"], "ready-for-agent")
        self.assertRegex(issue["source_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(issue["validation_reasons"], [])
        self.assertEqual(issue["context_assessment"]["verdict"], "pass")
        self.assertTrue(issue["context_assessment"]["passed"])
        self.assertTrue(issue["context_assessment"]["cited_paths"])
        self.assertNotIn("semantic", issue)
        self.assertLessEqual(len(issue["context_corpus"]["rg_candidate_paths"]), 8)
        stiffness = issue["stiffness"]
        for field in (
            "step_size",
            "safe_feedback_step",
            "hidden_coupling_pressure",
            "ratio",
            "ratio_level",
            "recommended_action",
        ):
            self.assertIn(field, stiffness)
        self.assertEqual(stiffness["ratio_level"], "low")
        self.assertGreater(stiffness["safe_feedback_step"], 0)
        self.assertTrue(math.isfinite(stiffness["ratio"]))
        self.assertIn(
            "safe feedback step raised by local Unit test or Fast check evidence",
            stiffness["reasons"],
        )

    def test_stiffness_ratio_levels_cover_expected_bands(self) -> None:
        gate = load_script_module("shape_issue_gate_ratio_bands_under_test", GATE_SCRIPT)

        examples = (
            (READY_BODY, "low"),
            (MEDIUM_RATIO_BODY, "medium"),
            (HIGH_RATIO_BODY, "high"),
            (STIFF_BODY, "extreme"),
        )
        for body, expected_level in examples:
            with self.subTest(expected_level=expected_level):
                stiffness = stiffness_for_body(gate, body)
                self.assertEqual(stiffness.ratio_level, expected_level)
                self.assertGreater(stiffness.hidden_coupling_pressure, 0)
                self.assertGreater(stiffness.safe_feedback_step, 0)
                self.assertTrue(math.isfinite(stiffness.ratio))
                self.assertIn("hidden-coupling pressure", "\n".join(stiffness.reasons))

    def test_missing_and_zero_safe_feedback_do_not_divide_by_zero(self) -> None:
        gate = load_script_module("shape_issue_gate_ratio_zero_under_test", GATE_SCRIPT)

        missing_feedback = stiffness_for_body(gate, MISSING_FEEDBACK_BODY)

        self.assertEqual(missing_feedback.safe_feedback_step, 0.25)
        self.assertGreater(missing_feedback.ratio, 0)
        self.assertTrue(math.isfinite(missing_feedback.ratio))
        self.assertEqual(gate.safe_ratio(2.0, 0.0), 8.0)

    def test_gate_writes_issue_draft_review_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = write_bundle(tmp_path, READY_BODY)
            result = run_gate(bundle_path, tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            combined_path = tmp_path / "issue-drafts.md"
            draft_path = tmp_path / "issue-drafts" / "harden-ready-issue.md"
            combined = combined_path.read_text(encoding="utf-8")
            draft = draft_path.read_text(encoding="utf-8")

        self.assertIn("# Shape Issues Draft Review", combined)
        self.assertIn(
            "### harden-ready-issue: Harden Ralph ready issue handling",
            combined,
        )
        self.assertIn("- Labels: `delivery-gitflow`, `enhancement`", combined)
        self.assertIn("- Blocked by draft ids: None", combined)
        self.assertIn("- Gate action: `ready`", combined)
        self.assertIn("- Stiffness summary:", combined)
        self.assertIn("- Issue context assessor: `pass`", combined)
        self.assertIn("## What to build", combined)
        self.assertIn("# Harden Ralph ready issue handling", draft)
        self.assertIn("## Shape Issues source", draft)
        self.assertIn("shape-issues-source", draft)
        self.assertIn("- Source digest:", draft)
        self.assertIn("## Draft body", draft)
        self.assertIn(READY_BODY.strip(), draft)

    def test_issue_draft_markdown_uses_publication_order_and_draft_blockers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_blocked_bundle(tmp_path), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            combined = (tmp_path / "issue-drafts.md").read_text(encoding="utf-8")
            blocker = (tmp_path / "issue-drafts" / "blocker.md").read_text(
                encoding="utf-8"
            )
            dependent = (tmp_path / "issue-drafts" / "dependent.md").read_text(
                encoding="utf-8"
            )

        self.assertLess(
            combined.index("### blocker: Blocker issue"),
            combined.index("### dependent: Dependent issue"),
        )
        self.assertIn("- Blocked by draft ids: `blocker`", combined)
        self.assertIn("- Publication order: `1`", blocker)
        self.assertIn("- Publication order: `2`", dependent)
        self.assertIn("## What to build", blocker)
        self.assertIn("## What to build", dependent)

    def test_issue_draft_source_lines_match_publisher_source_lines(self) -> None:
        gate = load_script_module("shape_issue_gate_rendering_under_test", GATE_SCRIPT)
        publisher = load_script_module(
            "shape_issues_publisher_rendering_under_test",
            PUBLISHER_SCRIPT,
        )

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = write_bundle(tmp_path, READY_BODY)
            result = run_gate(bundle_path, tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            gate_issue = gate.parse_bundle(bundle_path).issues[0]
            publisher_issue = publisher.parse_bundle(bundle_path).issues[0]
            marker = publisher.source_marker(bundle_path, publisher_issue)
            final_body = publisher.final_issue_body(
                publisher_issue,
                references={},
                marker=marker,
                bundle_path=bundle_path,
                context_assessor_provider="codex",
                dry_run=True,
                allow_fixture_publish=False,
            )
            draft = (
                tmp_path / "issue-drafts" / "harden-ready-issue.md"
            ).read_text(encoding="utf-8")

        self.assertEqual(gate.source_marker(bundle_path, gate_issue), marker)
        for line in (
            f"- Source marker: `{marker}`",
            f"- Bundle: `{publisher.bundle_reference(bundle_path)}`",
        ):
            self.assertIn(line, draft)
            self.assertIn(line, final_body)

    def test_operator_approval_evidence_is_reported_not_permission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, APPROVAL_BODY), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
            markdown = (tmp_path / "report.md").read_text(encoding="utf-8")

        evidence = report["issues"][0]["operator_approval_evidence"]
        self.assertTrue(evidence["present"])
        self.assertIn("Issue context assessor", evidence["body"])
        self.assertIn(
            "Approval evidence is context only; it does not grant tool permission.",
            evidence["warnings"],
        )
        self.assertIn("Operator approval evidence: present", markdown)

    def test_weak_context_assessment_needs_context(self) -> None:
        body = READY_BODY + "\n\n<!-- fixture context verdict: weak -->\n"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, body), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        issue = report["issues"][0]
        self.assertEqual(issue["context_assessment"]["verdict"], "weak")
        self.assertEqual(issue["action"], "needs-context")
        self.assertIn(
            "Issue context assessor verdict weak: fixture marked the supplied context as weak",
            issue["validation_reasons"],
        )

    def test_fail_context_assessment_needs_context(self) -> None:
        body = READY_BODY + "\n\n<!-- fixture context verdict: fail -->\n"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, body), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        issue = report["issues"][0]
        self.assertEqual(issue["context_assessment"]["verdict"], "fail")
        self.assertEqual(issue["action"], "needs-context")

    def test_invalid_assessor_cited_path_needs_context(self) -> None:
        body = READY_BODY + "\n\n<!-- fixture invalid cited path -->\n"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, body), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        issue = report["issues"][0]
        self.assertEqual(issue["action"], "needs-context")
        self.assertFalse(issue["context_assessment"]["valid"])
        self.assertIn(
            "Issue context assessor evidence invalid: assessor cited paths outside supplied evidence: missing-from-supplied-evidence.md",
            issue["validation_reasons"],
        )

    def test_stale_assessor_corpus_digest_needs_context(self) -> None:
        body = READY_BODY + "\n\n<!-- fixture stale corpus digest -->\n"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, body), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        issue = report["issues"][0]
        self.assertEqual(issue["action"], "needs-context")
        self.assertFalse(issue["context_assessment"]["valid"])
        self.assertIn(
            "Issue context assessor evidence invalid: assessor corpus digest mismatch",
            issue["validation_reasons"],
        )

    def test_missing_anchor_categories_need_context(self) -> None:
        incomplete_body = READY_BODY.replace("- Symbol: `READY_LABEL`\n", "")
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, incomplete_body), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        issue = report["issues"][0]
        self.assertEqual(issue["action"], "needs-context")
        self.assertFalse(issue["ready"])
        self.assertIn("missing anchor category: symbol", issue["validation_reasons"])

    def test_high_stiffness_recommends_split(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, STIFF_BODY), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        issue = report["issues"][0]
        self.assertEqual(issue["action"], "split")
        self.assertFalse(issue["ready"])
        self.assertGreaterEqual(issue["stiffness"]["score"], 70)
        self.assertIn(
            "mentions stiff boundary terms: cross-subproject, dagster, infrastructure, localstack, promotion, push check, s3, schema",
            issue["stiffness"]["reasons"],
        )

    def test_negated_boundary_terms_are_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(
                write_bundle(tmp_path, NEGATED_STIFF_BODY),
                tmp_path,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        issue = report["issues"][0]
        self.assertEqual(issue["action"], "ready")
        self.assertLess(issue["stiffness"]["score"], 30)
        self.assertTrue(issue["stiffness"]["ignored_terms"])
        self.assertNotIn(
            "mentions stiff boundary terms",
            "\n".join(issue["stiffness"]["reasons"]),
        )

    def test_root_agent_workflow_paths_share_one_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(
                write_bundle(tmp_path, ROOT_AGENT_BODY),
                tmp_path,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        issue = report["issues"][0]
        self.assertEqual(issue["action"], "ready")
        self.assertEqual(issue["stiffness"]["surface_areas"], ["root-agent-workflow"])
        self.assertLess(issue["stiffness"]["score"], 30)

    def test_declared_low_stiffness_mismatch_is_reported(self) -> None:
        body = STIFF_BODY.replace(
            "## Stiffness estimate\nHigh. This issue crosses several runtime boundaries.",
            "## Stiffness estimate\nLow. This is expected to be narrow.",
        )
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, body), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        stiffness = report["issues"][0]["stiffness"]
        self.assertEqual(stiffness["declared_level"], "low")
        self.assertTrue(stiffness["declared_mismatch"])

    def test_operator_override_can_accept_high_stiffness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(
                write_bundle(
                    tmp_path,
                    STIFF_BODY,
                    overrides={"harden-ready-issue": "Operator accepts this scope."},
                ),
                tmp_path,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))

        issue = report["issues"][0]
        self.assertEqual(issue["action"], "ready")
        self.assertTrue(issue["ready"])
        self.assertEqual(issue["operator_override"], "Operator accepts this scope.")

    def test_provider_failure_stops_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = write_bundle(tmp_path, READY_BODY)
            command = [
                sys.executable,
                str(GATE_SCRIPT),
                str(bundle_path),
                "--repo-root",
                str(REPO_ROOT),
                "--out-dir",
                str(tmp_path),
                "--context-assessor-command",
                f"{sys.executable} does-not-exist.py",
            ]
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Context assessor provider failed", result.stderr)

    def test_duplicate_issue_ids_stop_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            bundle_path = write_bundle(tmp_path, READY_BODY)
            payload = json.loads(bundle_path.read_text(encoding="utf-8"))
            payload["issues"].append(dict(payload["issues"][0]))
            bundle_path.write_text(json.dumps(payload), encoding="utf-8")
            result = run_gate(bundle_path, tmp_path)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Duplicate issue id", result.stderr)


if __name__ == "__main__":
    unittest.main()
