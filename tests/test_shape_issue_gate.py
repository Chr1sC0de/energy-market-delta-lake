from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_SCRIPT = REPO_ROOT / ".agents" / "skills" / "shape-issues" / "scripts" / "shape_issue_gate.py"
HF_PROVIDER_SCRIPT = (
    REPO_ROOT / ".agents" / "skills" / "shape-issues" / "scripts" / "hf_embed_jsonl.py"
)
FIXTURE_PROVIDER = (
    REPO_ROOT / ".agents" / "skills" / "shape-issues" / "scripts" / "fixture_embed_jsonl.py"
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
- Model: `Qwen/Qwen3-Embedding-0.6B`.
- Remote model code: prohibited; use `--no-trust-remote-code`.
- Downloads: PyPI packages and Hugging Face model files are acceptable.
- Corpus scope: only the files listed in `## Context anchors`.
- Output path: `.shape-issues/runs/example/`.
- Prohibited: secrets, credentials, unlisted repo files, GitHub mutation, commits, pushes.
- If the command, model, corpus, or trust settings differ, stop and ask the Operator again.
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


def run_gate(bundle_path: Path, out_dir: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    command = [
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
        "scripts/ralph.py",
        "--corpus-path",
        "docs/agents/ralph-loop.md",
        "--semantic-min-score",
        "0.05",
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


class ShapeIssueGateTests(unittest.TestCase):
    def test_gate_defaults_use_06b_safe_embedding_command(self) -> None:
        gate = load_script_module("shape_issue_gate_under_test", GATE_SCRIPT)

        with (
            mock.patch.dict("os.environ", {}, clear=True),
            mock.patch.object(sys, "argv", ["shape_issue_gate.py", "bundle.json"]),
        ):
            args = gate.parse_args()
            command = gate.default_embedding_command()

        self.assertEqual(args.model_id, "Qwen/Qwen3-Embedding-0.6B")
        self.assertIn("--model Qwen/Qwen3-Embedding-0.6B", command)
        self.assertIn("--no-trust-remote-code", command)
        self.assertIn("--batch-size 2", command)
        self.assertIn("--device auto", command)
        self.assertIn("--min-free-vram-gb 6", command)
        self.assertNotIn("Qwen/Qwen3-Embedding-8B", command)

    def test_hf_provider_defaults_use_06b_without_remote_code(self) -> None:
        provider = load_script_module("hf_embed_jsonl_under_test", HF_PROVIDER_SCRIPT)

        with mock.patch.object(sys, "argv", ["hf_embed_jsonl.py"]):
            args = provider.parse_args()

        self.assertEqual(args.model, "Qwen/Qwen3-Embedding-0.6B")
        self.assertEqual(args.batch_size, 2)
        self.assertEqual(args.device, "auto")
        self.assertEqual(args.min_free_vram_gb, 6.0)
        self.assertFalse(args.trust_remote_code)

        with mock.patch.object(
            sys,
            "argv",
            ["hf_embed_jsonl.py", "--trust-remote-code"],
        ):
            opted_in = provider.parse_args()
        self.assertTrue(opted_in.trust_remote_code)

    def test_hf_provider_auto_device_requires_enough_free_vram(self) -> None:
        provider = load_script_module(
            "hf_embed_jsonl_runtime_under_test",
            HF_PROVIDER_SCRIPT,
        )

        class FakeCuda:
            def __init__(
                self,
                *,
                available: bool,
                free_gb: float,
                total_gb: float,
            ) -> None:
                self._available = available
                self._free_bytes = int(free_gb * provider.BYTES_PER_GIB)
                self._total_bytes = int(total_gb * provider.BYTES_PER_GIB)

            def is_available(self) -> bool:
                return self._available

            def mem_get_info(self) -> tuple[int, int]:
                return self._free_bytes, self._total_bytes

            def current_device(self) -> int:
                return 0

        class FakeTorch:
            def __init__(self, cuda: FakeCuda) -> None:
                self.cuda = cuda

        with mock.patch.object(sys, "argv", ["hf_embed_jsonl.py"]):
            args = provider.parse_args()

        high_vram = provider.select_runtime(
            args,
            FakeTorch(FakeCuda(available=True, free_gb=8.0, total_gb=12.0)),
        )
        low_vram = provider.select_runtime(
            args,
            FakeTorch(FakeCuda(available=True, free_gb=2.0, total_gb=12.0)),
        )
        no_cuda = provider.select_runtime(
            args,
            FakeTorch(FakeCuda(available=False, free_gb=0.0, total_gb=0.0)),
        )

        self.assertEqual(high_vram.device, "cuda:0")
        self.assertIsNone(high_vram.fallback_reason)
        self.assertEqual(low_vram.device, "cpu")
        self.assertIn("below", low_vram.fallback_reason or "")
        self.assertEqual(no_cuda.device, "cpu")
        self.assertEqual(no_cuda.fallback_reason, "CUDA unavailable")

    def test_ready_issue_passes_with_context_anchors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, READY_BODY), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
            markdown = (tmp_path / "report.md").read_text(encoding="utf-8")

        self.assertRegex(report["bundle_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(report["embedding"]["runtime_device"], "fixture")
        self.assertEqual(report["embedding"]["batch_size"], 1)
        self.assertFalse(report["embedding"]["provider_metadata"]["trust_remote_code"])
        self.assertIn("- Runtime device: `fixture`", markdown)
        self.assertIn("- Batch size: `1`", markdown)
        issue = report["issues"][0]
        self.assertEqual(issue["action"], "ready")
        self.assertTrue(issue["ready"])
        self.assertEqual(issue["recommended_state_label"], "ready-for-agent")
        self.assertRegex(issue["source_digest"], r"^[0-9a-f]{64}$")
        self.assertEqual(issue["validation_reasons"], [])
        self.assertGreaterEqual(issue["semantic"]["top_score"], 0.05)

    def test_operator_approval_evidence_is_reported_not_permission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_gate(write_bundle(tmp_path, APPROVAL_BODY), tmp_path)
            self.assertEqual(result.returncode, 0, result.stderr)

            report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
            markdown = (tmp_path / "report.md").read_text(encoding="utf-8")

        evidence = report["issues"][0]["operator_approval_evidence"]
        self.assertTrue(evidence["present"])
        self.assertIn("Qwen/Qwen3-Embedding-0.6B", evidence["body"])
        self.assertIn(
            "Approval evidence is context only; it does not grant tool permission.",
            evidence["warnings"],
        )
        self.assertIn("Operator approval evidence: present", markdown)

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
                "--semantic-min-score",
                "0.0",
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
                "--semantic-min-score",
                "0.0",
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
                "--embedding-command",
                f"{sys.executable} does-not-exist.py",
                "--corpus-path",
                "scripts/ralph.py",
            ]
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Embedding provider failed", result.stderr)

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
