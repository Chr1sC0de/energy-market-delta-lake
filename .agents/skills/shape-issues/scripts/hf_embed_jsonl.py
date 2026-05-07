#!/usr/bin/env python3
"""Hugging Face JSONL embedding provider for shape-issues."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InputRecord:
    record_id: str
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Embed stdin JSONL records with a Sentence Transformers model.",
    )
    parser.add_argument("--model", default="Qwen/Qwen3-Embedding-8B")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument(
        "--trust-remote-code",
        action=argparse.BooleanOptionalAction,
        default=True,
    )
    return parser.parse_args()


def load_records() -> list[InputRecord]:
    records: list[InputRecord] = []
    for line_number, line in enumerate(sys.stdin, start=1):
        if line.strip() == "":
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise ValueError(f"Input line {line_number} must be a JSON object.")
        record_id = str(payload.get("id") or "")
        text = str(payload.get("text") or "")
        if record_id == "":
            raise ValueError(f"Input line {line_number} is missing id.")
        records.append(InputRecord(record_id=record_id, text=text))
    return records


def vector_payload(record: InputRecord, vector: Any) -> dict[str, Any]:
    if hasattr(vector, "tolist"):
        values = vector.tolist()
    else:
        values = list(vector)
    return {"id": record.record_id, "vector": [float(value) for value in values]}


def main() -> None:
    args = parse_args()
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        sys.stderr.write(
            "sentence-transformers is required. Run through "
            "`uv run --with sentence-transformers --with torch ...`.\n"
        )
        raise SystemExit(1) from error

    try:
        records = load_records()
        model = SentenceTransformer(args.model, trust_remote_code=args.trust_remote_code)
        texts = [record.text for record in records]
        vectors = model.encode(
            texts,
            batch_size=args.batch_size,
            normalize_embeddings=True,
        )
    except (OSError, ValueError, RuntimeError) as error:
        sys.stderr.write(f"Hugging Face embedding failed: {error}\n")
        raise SystemExit(1)

    for record, vector in zip(records, vectors):
        sys.stdout.write(json.dumps(vector_payload(record, vector)) + "\n")


if __name__ == "__main__":
    main()
