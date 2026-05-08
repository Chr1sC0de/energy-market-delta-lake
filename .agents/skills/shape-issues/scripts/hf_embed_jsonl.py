#!/usr/bin/env python3
"""Hugging Face JSONL embedding provider for shape-issues."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from typing import Any


DEFAULT_MODEL_ID = "Qwen/Qwen3-Embedding-0.6B"
DEFAULT_BATCH_SIZE = 2
DEFAULT_DEVICE = "auto"
DEFAULT_MIN_FREE_VRAM_GB = 6.0
BYTES_PER_GIB = 1024**3
METADATA_PREFIX = "shape-issues-provider-metadata:"


@dataclass(frozen=True)
class InputRecord:
    record_id: str
    text: str


@dataclass(frozen=True)
class RuntimeSelection:
    device: str
    requested_device: str
    batch_size: int
    min_free_vram_gb: float
    cuda_available: bool
    free_vram_gb: float | None
    total_vram_gb: float | None
    fallback_reason: str | None


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be an integer") from error
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def non_negative_float(value: str) -> float:
    try:
        parsed = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a number") from error
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be at least 0")
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Embed stdin JSONL records with a Sentence Transformers model.",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL_ID)
    parser.add_argument("--batch-size", type=positive_int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default=DEFAULT_DEVICE,
        help=(
            "Runtime device. auto uses CUDA only when enough free VRAM is "
            "available, otherwise CPU."
        ),
    )
    parser.add_argument(
        "--min-free-vram-gb",
        type=non_negative_float,
        default=DEFAULT_MIN_FREE_VRAM_GB,
        help="Minimum free CUDA VRAM required before auto selects GPU.",
    )
    parser.add_argument(
        "--trust-remote-code",
        action=argparse.BooleanOptionalAction,
        default=False,
    )
    return parser.parse_args()


def cuda_memory_info(torch_module: Any) -> tuple[float | None, float | None]:
    try:
        free_bytes, total_bytes = torch_module.cuda.mem_get_info()
    except TypeError:
        try:
            free_bytes, total_bytes = torch_module.cuda.mem_get_info(0)
        except (AttributeError, RuntimeError, ValueError):
            return None, None
    except (AttributeError, RuntimeError, ValueError):
        return None, None
    return free_bytes / BYTES_PER_GIB, total_bytes / BYTES_PER_GIB


def cuda_device_name(torch_module: Any) -> str:
    try:
        return f"cuda:{torch_module.cuda.current_device()}"
    except (AttributeError, RuntimeError, ValueError):
        return "cuda"


def select_runtime(args: argparse.Namespace, torch_module: Any) -> RuntimeSelection:
    cuda_available = bool(torch_module.cuda.is_available())
    free_vram_gb: float | None = None
    total_vram_gb: float | None = None
    if cuda_available:
        free_vram_gb, total_vram_gb = cuda_memory_info(torch_module)

    if args.device == "cpu":
        return RuntimeSelection(
            device="cpu",
            requested_device=args.device,
            batch_size=args.batch_size,
            min_free_vram_gb=args.min_free_vram_gb,
            cuda_available=cuda_available,
            free_vram_gb=free_vram_gb,
            total_vram_gb=total_vram_gb,
            fallback_reason="CPU requested",
        )

    if args.device == "cuda":
        if not cuda_available:
            raise ValueError("--device cuda requested but CUDA is unavailable.")
        return RuntimeSelection(
            device=cuda_device_name(torch_module),
            requested_device=args.device,
            batch_size=args.batch_size,
            min_free_vram_gb=args.min_free_vram_gb,
            cuda_available=cuda_available,
            free_vram_gb=free_vram_gb,
            total_vram_gb=total_vram_gb,
            fallback_reason=None,
        )

    if not cuda_available:
        fallback_reason = "CUDA unavailable"
    elif free_vram_gb is None:
        fallback_reason = "CUDA free VRAM could not be measured"
    elif free_vram_gb < args.min_free_vram_gb:
        fallback_reason = (
            f"CUDA free VRAM {free_vram_gb:.2f} GiB is below the "
            f"{args.min_free_vram_gb:.2f} GiB minimum"
        )
    else:
        return RuntimeSelection(
            device=cuda_device_name(torch_module),
            requested_device=args.device,
            batch_size=args.batch_size,
            min_free_vram_gb=args.min_free_vram_gb,
            cuda_available=cuda_available,
            free_vram_gb=free_vram_gb,
            total_vram_gb=total_vram_gb,
            fallback_reason=None,
        )

    return RuntimeSelection(
        device="cpu",
        requested_device=args.device,
        batch_size=args.batch_size,
        min_free_vram_gb=args.min_free_vram_gb,
        cuda_available=cuda_available,
        free_vram_gb=free_vram_gb,
        total_vram_gb=total_vram_gb,
        fallback_reason=fallback_reason,
    )


def runtime_metadata(
    args: argparse.Namespace,
    runtime: RuntimeSelection,
) -> dict[str, Any]:
    return {
        "batch_size": runtime.batch_size,
        "cuda_available": runtime.cuda_available,
        "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"),
        "fallback_reason": runtime.fallback_reason,
        "free_vram_gb": runtime.free_vram_gb,
        "min_free_vram_gb": runtime.min_free_vram_gb,
        "model": args.model,
        "requested_device": runtime.requested_device,
        "runtime_device": runtime.device,
        "total_vram_gb": runtime.total_vram_gb,
        "trust_remote_code": bool(args.trust_remote_code),
    }


def write_runtime_metadata(args: argparse.Namespace, runtime: RuntimeSelection) -> None:
    payload = json.dumps(runtime_metadata(args, runtime), sort_keys=True)
    sys.stderr.write(f"{METADATA_PREFIX} {payload}\n")


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
        import torch
        from sentence_transformers import SentenceTransformer
    except ImportError as error:
        sys.stderr.write(
            "sentence-transformers and torch are required. Run through "
            "`uv run --with sentence-transformers --with torch ...`.\n"
        )
        raise SystemExit(1) from error

    try:
        records = load_records()
        runtime = select_runtime(args, torch)
        model = SentenceTransformer(
            args.model,
            trust_remote_code=args.trust_remote_code,
            device=runtime.device,
        )
        write_runtime_metadata(args, runtime)
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
