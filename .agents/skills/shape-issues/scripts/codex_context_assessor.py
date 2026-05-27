#!/usr/bin/env python3
"""Codex-backed context assessor provider for shape-issues."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ASSESSOR_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "bundle_digest", "corpus_digest", "assessments"],
    "properties": {
        "schema_version": {"type": "string"},
        "bundle_digest": {"type": "string"},
        "corpus_digest": {"type": "string"},
        "assessments": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "verdict", "confidence", "cited_paths", "reasons"],
                "properties": {
                    "id": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["pass", "weak", "fail"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "cited_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "reasons": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
        },
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Codex as a bounded shape-issues context assessor.",
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--codex-binary", default="codex")
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout", type=int, default=600)
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=None,
        help=(
            "Writable runtime directory for nested Codex temporary files and "
            "cache state. Authentication still uses the caller's CODEX_HOME."
        ),
    )
    parser.add_argument(
        "--preflight",
        action="store_true",
        help="Run a minimal live assessor request to validate nested Codex startup.",
    )
    return parser.parse_args()


def build_prompt(request_text: str) -> str:
    return "\n".join(
        [
            "You are the shape-issues Issue context assessor.",
            "",
            "Assess only the JSON evidence supplied below. Do not inspect the repository, "
            "run commands, browse, or infer from files not present in the JSON.",
            "",
            "For each issue, decide whether the supplied Context anchors and evidence "
            "snippets are enough for an implementation agent to work independently.",
            "",
            "Verdicts:",
            "- pass: evidence is specific enough to start implementation independently.",
            "- weak: evidence is relevant but likely missing important implementation context.",
            "- fail: evidence is missing, stale, unrelated, or too vague to support the work.",
            "",
            "Cite only paths present in the issue's context_corpus.evidence array. "
            "Return JSON only, matching the provided output schema. Echo the request "
            "schema_version, bundle_digest, and corpus_digest exactly.",
            "",
            "Request JSON:",
            request_text,
        ]
    )


def run_codex(
    *,
    codex_binary: str,
    model: str | None,
    repo_root: Path,
    prompt: str,
    timeout: int,
    env: dict[str, str] | None,
) -> str:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        schema_path = temp_path / "schema.json"
        output_path = temp_path / "last-message.json"
        schema_path.write_text(
            json.dumps(ASSESSOR_SCHEMA, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        args = [
            codex_binary,
            "exec",
            "--sandbox",
            "read-only",
            "-c",
            'approval_policy="never"',
            "--ephemeral",
            "--cd",
            str(repo_root),
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
        ]
        if model is not None and model.strip() != "":
            args.extend(["--model", model])
        args.append("-")

        result = subprocess.run(
            args,
            input=prompt,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(f"codex context assessor failed: {detail}")
        if output_path.exists():
            output = output_path.read_text(encoding="utf-8").strip()
            if output != "":
                return output
        return result.stdout.strip()


def parse_json_response(text: str) -> dict[str, Any]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match is None:
            raise
        payload = json.loads(match.group(0))
    if not isinstance(payload, dict):
        raise RuntimeError("codex context assessor returned non-object JSON")
    return payload


def runtime_environment(runtime_dir: Path | None) -> dict[str, str] | None:
    if runtime_dir is None:
        return None

    runtime_path = runtime_dir.resolve()
    tmp_dir = runtime_path / "tmp"
    xdg_cache_dir = runtime_path / "xdg-cache"
    for path in (runtime_path, tmp_dir, xdg_cache_dir):
        path.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["TMPDIR"] = str(tmp_dir)
    env["TMP"] = str(tmp_dir)
    env["TEMP"] = str(tmp_dir)
    env["XDG_CACHE_HOME"] = str(xdg_cache_dir)
    env["CODEX_SHAPE_ISSUES_RUNTIME_DIR"] = str(runtime_path)
    return env


def preflight_request() -> dict[str, Any]:
    return {
        "schema_version": "shape-issues-context-assessor-v1",
        "bundle_digest": "preflight",
        "corpus_digest": "preflight",
        "shared_context": [],
        "issues": [],
    }


def main() -> None:
    args = parse_args()
    request_text = json.dumps(preflight_request()) if args.preflight else sys.stdin.read()
    try:
        request = json.loads(request_text)
        if not isinstance(request, dict):
            raise RuntimeError("request must be a JSON object")
        env = runtime_environment(args.runtime_dir)
        response_text = run_codex(
            codex_binary=args.codex_binary,
            model=args.model,
            repo_root=args.repo_root.resolve(),
            prompt=build_prompt(json.dumps(request, indent=2, sort_keys=True)),
            timeout=args.timeout,
            env=env,
        )
        response = parse_json_response(response_text)
    except (OSError, RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as error:
        sys.stderr.write(f"codex context assessor failed: {error}\n")
        raise SystemExit(1)
    sys.stdout.write(json.dumps(response, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
