#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import boto3
import bs4
import requests
from botocore.exceptions import ClientError
from types_boto3_s3.client import S3Client

ROOT_URL = "https://nemweb.com.au/REPORTS/CURRENT/VicGas/"
PUBLIC_REPORT_PATTERN = re.compile(r"^PublicRpts\d{2}\.zip$", re.IGNORECASE)


@dataclass(frozen=True)
class ReportLink:
    filename: str
    url: str


def select_zip_links(
    html: str,
    *,
    include_current_day: bool = False,
    report_names: set[str] | None = None,
) -> list[ReportLink]:
    soup = bs4.BeautifulSoup(html, "html.parser")
    selected: list[ReportLink] = []
    normalized_report_names = (
        {name.lower() for name in report_names} if report_names is not None else None
    )

    for link in soup.find_all("a"):
        if not isinstance(link, bs4.Tag):
            continue
        filename = link.text.strip()
        href = link.get("href")
        if not isinstance(href, str):
            continue

        filename_lower = filename.lower()
        is_public_report = PUBLIC_REPORT_PATTERN.match(filename) is not None
        is_current_day = filename_lower == "currentday.zip"
        if normalized_report_names is not None:
            should_select = filename_lower in normalized_report_names
        else:
            should_select = is_public_report or (include_current_day and is_current_day)

        if should_select:
            selected.append(ReportLink(filename=filename, url=urljoin(ROOT_URL, href)))

    return selected


def object_exists_with_size(
    s3_client: S3Client, bucket: str, key: str, size: int
) -> bool:
    try:
        response = s3_client.head_object(Bucket=bucket, Key=key)
    except ClientError as error:
        if error.response.get("Error", {}).get("Code") in {"404", "NoSuchKey"}:
            return False
        raise
    return response.get("ContentLength") == size


def download_to_tempfile(url: str, directory: Path) -> tuple[Path, int]:
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    total_bytes = 0
    with tempfile.NamedTemporaryFile(dir=directory, delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                total_bytes += len(chunk)
                temp_file.write(chunk)
    return temp_path, total_bytes


def upload_report(
    *,
    s3_client: S3Client,
    report: ReportLink,
    bucket: str,
    prefix: str,
    dry_run: bool,
    temp_dir: Path,
) -> str:
    key = f"{prefix.rstrip('/')}/{report.filename}"
    temp_path, size = download_to_tempfile(report.url, temp_dir)
    try:
        if object_exists_with_size(s3_client, bucket, key, size):
            return f"skip existing: s3://{bucket}/{key}"

        if dry_run:
            return f"would upload: {report.url} -> s3://{bucket}/{key} ({size} bytes)"

        with temp_path.open("rb") as file_obj:
            s3_client.upload_fileobj(file_obj, bucket, key)
        return f"uploaded: {report.url} -> s3://{bucket}/{key} ({size} bytes)"
    finally:
        temp_path.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Upload VicGas public report zip bundles to the landing bucket."
    )
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", default="bronze/vicgas")
    parser.add_argument("--include-current-day", action="store_true")
    parser.add_argument(
        "--report",
        action="append",
        dest="reports",
        help="Specific report filename to upload, e.g. PublicRpts24.zip.",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    response = requests.get(ROOT_URL, timeout=30)
    response.raise_for_status()

    reports = select_zip_links(
        response.text,
        include_current_day=args.include_current_day,
        report_names=set(args.reports) if args.reports else None,
    )
    s3_client = boto3.client("s3")

    with tempfile.TemporaryDirectory() as temp_dir:
        for report in reports:
            print(
                upload_report(
                    s3_client=s3_client,
                    report=report,
                    bucket=args.bucket,
                    prefix=args.prefix,
                    dry_run=args.dry_run,
                    temp_dir=Path(temp_dir),
                )
            )


if __name__ == "__main__":
    main()
