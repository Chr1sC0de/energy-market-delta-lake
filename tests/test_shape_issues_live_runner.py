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


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = (
    REPO_ROOT
    / ".agents"
    / "skills"
    / "shape-issues"
    / "scripts"
    / "run_live_shape_issue_gate.py"
)


def load_runner() -> Any:
    spec = importlib.util.spec_from_file_location(
        "shape_issues_live_runner_under_test",
        RUNNER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load live runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ShapeIssuesLiveRunnerTests(unittest.TestCase):
    def test_validate_run_paths_refuses_outside_bundle(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            outside_bundle = repo_root / "bundle.json"

            with self.assertRaisesRegex(
                runner.LiveGateRunnerError,
                r"\.shape-issues/runs",
            ):
                runner.validate_run_paths(
                    repo_root=repo_root,
                    bundle_path=outside_bundle,
                    out_dir=outside_bundle.parent,
                    runtime_dir=outside_bundle.parent / "runtime",
                )

    def test_gate_command_hardcodes_live_assessor_command(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            run_dir = repo_root / ".shape-issues" / "runs" / "demo"
            bundle_path = run_dir / "bundle.json"
            run_dir.mkdir(parents=True)
            bundle_path.write_text("{}", encoding="utf-8")
            config = runner.LiveGateConfig(
                bundle_path=bundle_path,
                repo_root=repo_root,
                out_dir=run_dir,
                runtime_dir=run_dir / "codex-runtime",
                codex_binary="codex",
                model=None,
                timeout=600,
            )

            command = runner.gate_command_args(config)

        command_text = " ".join(command)
        self.assertIn("shape_issue_gate.py", command_text)
        self.assertIn("codex_context_assessor.py", command_text)
        self.assertIn("--context-assessor-name codex", command_text)
        self.assertNotIn("fixture_context_assessor.py", command_text)

    def test_run_live_gate_preflights_runs_gate_and_annotates_report(self) -> None:
        runner = load_runner()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            run_dir = repo_root / ".shape-issues" / "runs" / "demo"
            bundle_path = run_dir / "bundle.json"
            run_dir.mkdir(parents=True)
            bundle_path.write_text("{}", encoding="utf-8")
            config = runner.LiveGateConfig(
                bundle_path=bundle_path,
                repo_root=repo_root,
                out_dir=run_dir,
                runtime_dir=run_dir / "codex-runtime",
                codex_binary="codex",
                model=None,
                timeout=600,
            )
            calls: list[tuple[str, ...]] = []

            def fake_run(args: list[str], **_kwargs: Any) -> subprocess.CompletedProcess[str]:
                calls.append(tuple(args))
                if "shape_issue_gate.py" in args[1]:
                    (run_dir / "report.json").write_text(
                        json.dumps({"context_assessor": {"provider": "codex"}}),
                        encoding="utf-8",
                    )
                    (run_dir / "report.md").write_text(
                        "# Shape Issues Gate Report\n",
                        encoding="utf-8",
                    )
                return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

            with mock.patch.object(runner.subprocess, "run", side_effect=fake_run):
                runner.run_live_gate(config)

            self.assertEqual(len(calls), 2)
            self.assertIn("--preflight", calls[0])
            self.assertIn("shape_issue_gate.py", calls[1][1])
            report = json.loads((run_dir / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(
                report["live_assessor_runner"]["schema_version"],
                runner.RUNNER_SCHEMA_VERSION,
            )
            markdown = (run_dir / "report.md").read_text(encoding="utf-8")
            self.assertIn("## Live Assessor Runner", markdown)


if __name__ == "__main__":
    unittest.main()
