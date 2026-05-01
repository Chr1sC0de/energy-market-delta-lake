"""CLI for replaying archived source files into bronze Delta tables."""

import argparse
import json
import os
import sys
from collections.abc import Sequence

import boto3
from types_boto3_s3 import S3Client

from aemo_etl.configs import AEMO_BUCKET, ARCHIVE_BUCKET
from aemo_etl.factories.df_from_s3_keys.source_tables import (
    load_source_table_specs,
    select_source_table_specs,
)
from aemo_etl.maintenance.archive_replay import (
    DEFAULT_MAX_BATCH_BYTES,
    DEFAULT_MAX_BATCH_FILES,
    ArchiveReplayResult,
    run_archive_replay,
)


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    """Build the archive replay CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Replay archived source-table files into bronze current-state "
            "Delta tables. Defaults to dry-run; pass --replace to write."
        )
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument(
        "--all",
        action="store_true",
        dest="include_all",
        help="target all source-table bronze assets",
    )
    target.add_argument("--domain", help="target one source-table domain")
    target.add_argument(
        "--table",
        help=(
            "target one source table by suffix, bronze table name, or "
            "domain-qualified table"
        ),
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="write rebuilt Delta tables; without this flag the command is dry-run",
    )
    parser.add_argument(
        "--batch-bytes",
        type=_positive_int,
        default=DEFAULT_MAX_BATCH_BYTES,
        help=f"maximum planned bytes per replay batch (default: {DEFAULT_MAX_BATCH_BYTES})",
    )
    parser.add_argument(
        "--batch-files",
        type=_positive_int,
        default=DEFAULT_MAX_BATCH_FILES,
        help=f"maximum files per replay batch (default: {DEFAULT_MAX_BATCH_FILES})",
    )
    parser.add_argument(
        "--archive-bucket",
        default=ARCHIVE_BUCKET,
        help=f"archive bucket name (default: {ARCHIVE_BUCKET})",
    )
    parser.add_argument(
        "--aemo-bucket",
        default=AEMO_BUCKET,
        help=f"AEMO Delta bucket name (default: {AEMO_BUCKET})",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="emit machine-readable JSON",
    )
    return parser


def make_s3_client() -> S3Client:
    """Create an S3 client using AWS_ENDPOINT_URL when configured."""
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    if endpoint_url is not None and endpoint_url != "":
        return boto3.client("s3", endpoint_url=endpoint_url)
    return boto3.client("s3")


def _format_text_result(result: ArchiveReplayResult) -> str:
    plan = result.plan
    lines = [
        f"{result.mode}: {plan.spec.table_id}",
        f"  archive: s3://{plan.archive_bucket}/{plan.spec.archive_prefix}",
        f"  glob pattern: {plan.spec.glob_pattern}",
        f"  matching archive files: {plan.matching_file_count}",
        f"  planned batches: {plan.planned_batch_count}",
        f"  total bytes: {plan.total_bytes}",
        f"  target table URI: {plan.target_table_uri}",
    ]
    if result.mode == "replace":
        lines.extend(
            [
                f"  written batches: {result.written_batches}",
                f"  written files: {result.written_files}",
                f"  skipped files: {len(result.skipped_files)}",
            ]
        )
    if result.mode == "dry-run" and plan.matching_file_count > 0:
        lines.append("  files:")
        lines.extend(f"    - {key}" for key in plan.matching_archive_files)
    return "\n".join(lines)


def _emit_results(
    results: tuple[ArchiveReplayResult, ...],
    *,
    json_output: bool,
) -> None:
    if json_output:
        sys.stdout.write(json.dumps([result.as_dict() for result in results], indent=2))
        sys.stdout.write("\n")
        return

    sys.stdout.write("\n\n".join(_format_text_result(result) for result in results))
    sys.stdout.write("\n")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the bronze archive replay CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        specs = select_source_table_specs(
            load_source_table_specs(),
            include_all=args.include_all,
            domain=args.domain,
            table=args.table,
        )
        results = run_archive_replay(
            make_s3_client(),
            specs=specs,
            replace=args.replace,
            archive_bucket=args.archive_bucket,
            aemo_bucket=args.aemo_bucket,
            max_batch_bytes=args.batch_bytes,
            max_batch_files=args.batch_files,
        )
    except ValueError as error:
        parser.exit(2, f"error: {error}\n")
    except Exception as error:
        sys.stderr.write(f"error: {error}\n")
        return 1

    _emit_results(results, json_output=args.json_output)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
