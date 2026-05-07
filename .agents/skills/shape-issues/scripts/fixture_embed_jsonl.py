#!/usr/bin/env python3
"""Deterministic JSONL embedding provider for shape-issues tests."""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from typing import Any


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_./-]+")
DIMENSIONS = 64


def tokens(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def embed(text: str) -> list[float]:
    vector = [0.0] * DIMENSIONS
    for token in tokens(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % DIMENSIONS
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def record_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    record_id = str(payload.get("id") or "")
    text = str(payload.get("text") or "")
    return {"id": record_id, "vector": embed(text)}


def main() -> None:
    for line in sys.stdin:
        if line.strip() == "":
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise SystemExit("fixture provider input line must be a JSON object")
        sys.stdout.write(json.dumps(record_from_payload(payload)) + "\n")


if __name__ == "__main__":
    main()
