#!/usr/bin/env python3
"""Run the shape-issues gate with the live Codex-backed assessor."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


RUNNER_SCHEMA_VERSION = "shape-issues-live-gate-runner-v1"


class LiveGateRunnerError(Exception):
    """Raised when the live shape-issues gate runner cannot continue."""


@dataclass(frozen=True)
class LiveGateConfig:
    bundle_path: Path
    repo_root: Path
    out_dir: Path
    runtime_dir: Path
    codex_binary: str
    model: str | None
    timeout: int


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run shape_issue_gate.py with the repo-local live Codex-backed "
            "Issue context assessor."
        ),
    )
    parser.add_argument("bundle", type=Path, help="Path to bundle.json.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--runtime-dir", type=Path, default=None)
    parser.add_argument("--codex-binary", default="codex")
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout", type=int, default=600)
    return parser.parse_args(argv)


def resolve_config(args: argparse.Namespace) -> LiveGateConfig:
    repo_root = args.repo_root.resolve()
    bundle_path = args.bundle.resolve()
    out_dir = (args.out_dir or bundle_path.parent).resolve()
    runtime_dir = (args.runtime_dir or out_dir / "codex-runtime").resolve()
    validate_run_paths(
        repo_root=repo_root,
        bundle_path=bundle_path,
        out_dir=out_dir,
        runtime_dir=runtime_dir,
    )
    if args.timeout < 1:
        raise LiveGateRunnerError("--timeout must be positive.")
    return LiveGateConfig(
        bundle_path=bundle_path,
        repo_root=repo_root,
        out_dir=out_dir,
        runtime_dir=runtime_dir,
        codex_binary=args.codex_binary,
        model=args.model,
        timeout=args.timeout,
    )


def validate_run_paths(
    *,
    repo_root: Path,
    bundle_path: Path,
    out_dir: Path,
    runtime_dir: Path,
) -> None:
    runs_root = (repo_root / ".shape-issues" / "runs").resolve()
    if bundle_path.name != "bundle.json":
        raise LiveGateRunnerError("Live gate runner requires a bundle.json input.")
    if not bundle_path.is_relative_to(runs_root):
        raise LiveGateRunnerError("Bundle path must be under .shape-issues/runs/.")
    if out_dir != bundle_path.parent:
        raise LiveGateRunnerError("Output directory must match the bundle run directory.")
    if not runtime_dir.is_relative_to(out_dir):
        raise LiveGateRunnerError("Runtime directory must be under the bundle run directory.")


def script_path(name: str) -> Path:
    return Path(__file__).resolve().parent / name


def assessor_command_args(config: LiveGateConfig, *, preflight: bool = False) -> list[str]:
    args = [
        sys.executable,
        str(script_path("codex_context_assessor.py")),
        "--repo-root",
        str(config.repo_root),
        "--runtime-dir",
        str(config.runtime_dir),
        "--codex-binary",
        config.codex_binary,
        "--timeout",
        str(config.timeout),
    ]
    if config.model is not None and config.model.strip() != "":
        args.extend(["--model", config.model])
    if preflight:
        args.append("--preflight")
    return args


def command_string(args: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in args)


def gate_command_args(config: LiveGateConfig) -> list[str]:
    return [
        sys.executable,
        str(script_path("shape_issue_gate.py")),
        str(config.bundle_path),
        "--repo-root",
        str(config.repo_root),
        "--context-assessor-command",
        command_string(assessor_command_args(config)),
        "--context-assessor-name",
        "codex",
        "--out-dir",
        str(config.out_dir),
    ]


def run_command(args: list[str], *, cwd: Path) -> CommandResult:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        stderr = (error.stderr or "").strip()
        stdout = (error.stdout or "").strip()
        detail = stderr or stdout or f"exit code {error.returncode}"
        raise LiveGateRunnerError(
            f"Command failed: {command_string(args)}\n{detail}"
        ) from error
    return CommandResult(stdout=result.stdout, stderr=result.stderr)


def relative_to_repo(path: Path, repo_root: Path) -> str:
    resolved = path.resolve()
    if resolved.is_relative_to(repo_root):
        return str(resolved.relative_to(repo_root))
    return str(resolved)


def annotate_report(config: LiveGateConfig, *, preflight_stdout: str) -> None:
    report_path = config.out_dir / "report.json"
    if not report_path.exists():
        raise LiveGateRunnerError(f"Gate did not write expected report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(report, dict):
        raise LiveGateRunnerError("Gate report must be a JSON object.")
    report["live_assessor_runner"] = {
        "schema_version": RUNNER_SCHEMA_VERSION,
        "provider": "codex",
        "runner": relative_to_repo(Path(__file__), config.repo_root),
        "runtime_dir": relative_to_repo(config.runtime_dir, config.repo_root),
        "codex_binary": config.codex_binary,
        "model": config.model,
        "timeout": config.timeout,
        "preflight": "passed",
        "preflight_stdout_empty": preflight_stdout.strip() == "",
        "permission_boundary": "operator-approved live shape-issues runner",
        "ran_at": datetime.now(UTC).isoformat(),
    }
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    annotate_markdown(config)


def annotate_markdown(config: LiveGateConfig) -> None:
    report_path = config.out_dir / "report.md"
    if not report_path.exists():
        return
    text = report_path.read_text(encoding="utf-8")
    section = "\n".join(
        [
            "## Live Assessor Runner",
            "",
            f"- Schema: `{RUNNER_SCHEMA_VERSION}`",
            "- Provider: `codex`",
            f"- Runner: `{relative_to_repo(Path(__file__), config.repo_root)}`",
            f"- Runtime dir: `{relative_to_repo(config.runtime_dir, config.repo_root)}`",
            "- Permission boundary: `operator-approved live shape-issues runner`",
            "",
        ]
    )
    report_path.write_text(replace_or_append_section(text, section), encoding="utf-8")


def replace_or_append_section(text: str, section: str) -> str:
    heading = "## Live Assessor Runner"
    start = text.find(heading)
    if start < 0:
        return text.rstrip() + "\n\n" + section
    next_heading = text.find("\n## ", start + len(heading))
    if next_heading < 0:
        return text[:start].rstrip() + "\n\n" + section
    return text[:start].rstrip() + "\n\n" + section + text[next_heading:]


def run_live_gate(config: LiveGateConfig) -> None:
    config.runtime_dir.mkdir(parents=True, exist_ok=True)
    preflight = run_command(assessor_command_args(config, preflight=True), cwd=config.repo_root)
    run_command(gate_command_args(config), cwd=config.repo_root)
    annotate_report(config, preflight_stdout=preflight.stdout)


def main(argv: list[str] | None = None) -> int:
    try:
        config = resolve_config(parse_args(argv))
        run_live_gate(config)
    except (LiveGateRunnerError, OSError, json.JSONDecodeError) as error:
        sys.stderr.write(f"live shape-issues gate failed: {error}\n")
        return 1
    sys.stdout.write(str(config.out_dir / "report.json") + "\n")
    sys.stdout.write(str(config.out_dir / "report.md") + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
