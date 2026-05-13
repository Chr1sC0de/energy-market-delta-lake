#!/usr/bin/env python3
"""Deterministic JSON context assessor for shape-issues tests."""

from __future__ import annotations

import json
import sys
from typing import Any


def main() -> None:
    request = json.loads(sys.stdin.read())
    if not isinstance(request, dict):
        sys.stderr.write("fixture assessor request must be a JSON object\n")
        raise SystemExit(1)

    assessments: list[dict[str, Any]] = []
    force_stale_digest = False
    for issue in request.get("issues", []):
        if not isinstance(issue, dict):
            continue
        issue_id = str(issue.get("id") or "")
        text = f"{issue.get('title') or ''}\n{issue.get('body') or ''}".lower()
        corpus = issue.get("context_corpus")
        evidence = []
        if isinstance(corpus, dict) and isinstance(corpus.get("evidence"), list):
            evidence = [item for item in corpus["evidence"] if isinstance(item, dict)]

        if "fixture context verdict: weak" in text:
            verdict = "weak"
            confidence = 0.55
            reasons = ["fixture marked the supplied context as weak"]
        elif "fixture context verdict: fail" in text:
            verdict = "fail"
            confidence = 0.2
            reasons = ["fixture marked the supplied context as insufficient"]
        else:
            verdict = "pass"
            confidence = 0.92
            reasons = ["fixture found enough supplied evidence for independent work"]

        cited_paths = [
            str(item.get("path"))
            for item in evidence[:2]
            if str(item.get("path") or "").strip() != ""
        ]
        if "fixture invalid cited path" in text:
            cited_paths = ["missing-from-supplied-evidence.md"]
        if "fixture stale corpus digest" in text:
            force_stale_digest = True

        assessments.append(
            {
                "id": issue_id,
                "verdict": verdict,
                "confidence": confidence,
                "cited_paths": cited_paths,
                "reasons": reasons,
            }
        )

    corpus_digest = str(request.get("corpus_digest") or "")
    if force_stale_digest:
        corpus_digest = "0" * 64
    response = {
        "schema_version": request.get("schema_version"),
        "bundle_digest": request.get("bundle_digest"),
        "corpus_digest": corpus_digest,
        "assessments": assessments,
    }
    sys.stdout.write(json.dumps(response, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
