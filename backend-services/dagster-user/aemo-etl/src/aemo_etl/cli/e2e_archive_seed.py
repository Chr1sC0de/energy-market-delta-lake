"""CLI for refreshing and loading the cached AEMO ETL e2e archive seed."""

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

import boto3
from types_boto3_s3 import S3Client

from aemo_etl.configs import LANDING_BUCKET
from aemo_etl.maintenance.e2e_archive_seed import (
    DEFAULT_ARCHIVE_SEED_BUCKET,
    DEFAULT_RAW_LATEST_COUNT,
    DEFAULT_ZIP_LATEST_COUNT,
    ArchiveSeedSpec,
    SeedCoverageError,
    build_default_gas_model_archive_seed_spec,
    default_seed_root,
    load_cached_seed_to_localstack,
    refresh_archive_seed,
)


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    """Build the e2e archive seed CLI parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Refresh and load the cached archive seed for local AEMO ETL "
            "End-to-end tests."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    spec_parser = subparsers.add_parser(
        "spec",
        help="emit the JSON seed spec for the full gas_model target",
    )
    spec_parser.set_defaults(handler=_run_spec)

    refresh_parser = subparsers.add_parser(
        "refresh",
        help="copy the requested latest archive slice into the local seed cache",
    )
    _add_seed_root_argument(refresh_parser)
    _add_archive_bucket_argument(refresh_parser)
    _add_latest_count_arguments(refresh_parser)
    refresh_parser.set_defaults(handler=_run_refresh)

    load_parser = subparsers.add_parser(
        "load-localstack",
        help="validate cached seed coverage and upload it to LocalStack landing",
    )
    _add_seed_root_argument(load_parser)
    _add_archive_bucket_argument(load_parser)
    _add_latest_count_arguments(load_parser)
    load_parser.add_argument(
        "--landing-bucket",
        default=LANDING_BUCKET,
        help=f"LocalStack landing bucket name (default: {LANDING_BUCKET})",
    )
    load_parser.set_defaults(handler=_run_load_localstack)

    return parser


def make_s3_client() -> S3Client:
    """Create an S3 client using AWS_ENDPOINT_URL when configured."""
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL")
    if endpoint_url is not None and endpoint_url != "":
        return boto3.client("s3", endpoint_url=endpoint_url)
    return boto3.client("s3")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the e2e archive seed CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = args.handler

    try:
        handler(args)
    except SeedCoverageError as error:
        manifest_path = error.manifest.seed_root / "seed-run-manifest.json"
        sys.stderr.write(f"error: {error}; manifest: {manifest_path}\n")
        return 1
    except ValueError as error:
        parser.exit(2, f"error: {error}\n")
    except Exception as error:
        sys.stderr.write(f"error: {error}\n")
        return 1

    return 0


def _add_seed_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--seed-root",
        type=Path,
        default=default_seed_root(),
        help="local seed root (default: backend-services/.e2e/aemo-etl)",
    )


def _add_archive_bucket_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--archive-bucket",
        default=DEFAULT_ARCHIVE_SEED_BUCKET,
        help=f"archive bucket name (default: {DEFAULT_ARCHIVE_SEED_BUCKET})",
    )


def _add_latest_count_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--raw-latest-count",
        type=_positive_int,
        default=DEFAULT_RAW_LATEST_COUNT,
        help=(
            "source-table raw objects required per table "
            f"(default: {DEFAULT_RAW_LATEST_COUNT})"
        ),
    )
    parser.add_argument(
        "--zip-latest-count",
        type=_positive_int,
        default=DEFAULT_ZIP_LATEST_COUNT,
        help=f"zip objects required per domain (default: {DEFAULT_ZIP_LATEST_COUNT})",
    )


def _default_spec() -> ArchiveSeedSpec:
    return build_default_gas_model_archive_seed_spec()


def _run_spec(_: argparse.Namespace) -> None:
    spec = _default_spec()
    _emit_json(spec.as_dict())


def _run_refresh(args: argparse.Namespace) -> None:
    manifest = refresh_archive_seed(
        make_s3_client(),
        seed_root=args.seed_root,
        spec=_default_spec(),
        archive_bucket=args.archive_bucket,
        raw_latest_count=args.raw_latest_count,
        zip_latest_count=args.zip_latest_count,
    )
    _emit_json(manifest.as_dict())


def _run_load_localstack(args: argparse.Namespace) -> None:
    manifest = load_cached_seed_to_localstack(
        make_s3_client(),
        seed_root=args.seed_root,
        spec=_default_spec(),
        archive_bucket=args.archive_bucket,
        landing_bucket=args.landing_bucket,
        raw_latest_count=args.raw_latest_count,
        zip_latest_count=args.zip_latest_count,
    )
    _emit_json(manifest.as_dict())


def _emit_json(payload: dict[str, object]) -> None:
    sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True))
    sys.stdout.write("\n")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
