"""Ad hoc jobs for downloading NEMWeb public report zip files."""

import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath, PureWindowsPath
from textwrap import dedent
from urllib.parse import unquote, urljoin, urlparse

import bs4
import requests
from dagster import Config, OpExecutionContext, job, op
from dagster_aws.s3 import S3Resource
from types_boto3_s3 import S3Client

from aemo_etl.configs import LANDING_BUCKET
from aemo_etl.utils import get_response_factory

ROOT_URL = "https://www.nemweb.com.au"
REPORT_URL = f"{ROOT_URL}/REPORTS/CURRENT/VicGas"
STTM_REPORT_URL = f"{ROOT_URL}/REPORTS/CURRENT/STTM"
PUBLIC_REPORT_PATTERN = re.compile(r"^PublicRpts\d{2}\.zip$", re.IGNORECASE)
STTM_DAY_ZIP_PATTERN = re.compile(
    r"^DAY(?:0[1-9]|[12]\d|3[01])\.ZIP$",
    re.IGNORECASE,
)
S3_PREFIX = "bronze/vicgas"
STTM_S3_PREFIX = "bronze/sttm"
VICGAS_DESCRIPTION = dedent(f"""
    Download the VICGAS public report zip files from {REPORT_URL} and upload to {LANDING_BUCKET}/{S3_PREFIX}/<filename>
""").strip("\n")
STTM_DESCRIPTION = dedent(f"""
    Download the STTM DAYNN.ZIP files from {STTM_REPORT_URL} and upload to {LANDING_BUCKET}/{STTM_S3_PREFIX}/<filename>
""").strip("\n")


@dataclass(frozen=True, slots=True)
class ZipDownloadSpec:
    """Configuration for one NEMWeb zip bootstrap listing."""

    domain: str
    report_url: str
    filename_pattern: re.Pattern[str]
    s3_prefix: str
    pattern_description: str


@dataclass(frozen=True, slots=True)
class ZipCandidate:
    """Selected listing entry for one zip file."""

    filename: str
    url: str


class PublicReportZipDownloadConfig(Config):
    """Runtime config for targeted zip bootstrap/backfill downloads."""

    target_files: list[str] = []


VICGAS_ZIP_DOWNLOAD_SPEC = ZipDownloadSpec(
    domain="vicgas",
    report_url=REPORT_URL,
    filename_pattern=PUBLIC_REPORT_PATTERN,
    s3_prefix=S3_PREFIX,
    pattern_description="PublicRptsNN.zip",
)
STTM_DAY_ZIP_DOWNLOAD_SPEC = ZipDownloadSpec(
    domain="sttm",
    report_url=STTM_REPORT_URL,
    filename_pattern=STTM_DAY_ZIP_PATTERN,
    s3_prefix=STTM_S3_PREFIX,
    pattern_description="DAY01.ZIP through DAY31.ZIP",
)


def _listing_url(report_url: str) -> str:
    """Return a listing URL suitable for urljoin base behavior."""
    return f"{report_url.rstrip('/')}/"


def _href_basename(href: str) -> str:
    """Return the decoded basename from a listing href."""
    return unquote(PurePosixPath(urlparse(href).path).name)


def _is_basename(value: str) -> bool:
    """Return whether a target file string is basename-only."""
    if value == "":
        return False
    if PurePosixPath(value).name != value:
        return False
    return PureWindowsPath(value).name == value


def _normalized_target_files(
    target_files: list[str],
    *,
    spec: ZipDownloadSpec,
) -> set[str]:
    """Validate target files and return their case-insensitive basenames."""
    invalid_targets = [
        target
        for target in target_files
        if not _is_basename(target) or spec.filename_pattern.fullmatch(target) is None
    ]
    if invalid_targets:
        raise ValueError(
            f"{spec.domain} target_files must be basename-only "
            f"{spec.pattern_description} values: {', '.join(invalid_targets)}"
        )

    return {target.casefold() for target in target_files}


def _candidate_from_link(
    link: object,
    *,
    spec: ZipDownloadSpec,
) -> ZipCandidate | None:
    """Build a candidate from an anchor when its basename matches the spec."""
    if not isinstance(link, bs4.Tag):
        return None

    href = link.get("href")
    if not isinstance(href, str):
        return None

    filename = _href_basename(href)
    if spec.filename_pattern.fullmatch(filename) is None:
        return None

    return ZipCandidate(
        filename=filename,
        url=urljoin(_listing_url(spec.report_url), href),
    )


def _zip_candidates_from_listing(
    soup: bs4.BeautifulSoup,
    *,
    spec: ZipDownloadSpec,
) -> list[ZipCandidate]:
    """Return deterministic, basename-de-duplicated zip candidates."""
    candidates_by_filename: dict[str, ZipCandidate] = {}

    for link in soup.find_all("a"):
        candidate = _candidate_from_link(link, spec=spec)
        if candidate is None:
            continue

        normalized_filename = candidate.filename.casefold()
        existing_candidate = candidates_by_filename.get(normalized_filename)
        if existing_candidate is None or candidate.url < existing_candidate.url:
            candidates_by_filename[normalized_filename] = candidate

    return [
        candidates_by_filename[normalized_filename]
        for normalized_filename in sorted(candidates_by_filename)
    ]


def _skipped_listing_filenames(
    soup: bs4.BeautifulSoup,
    *,
    candidates: list[ZipCandidate],
) -> list[str]:
    """Return listing basenames that did not become zip candidates."""
    candidate_filenames = {candidate.filename.casefold() for candidate in candidates}
    skipped_filenames_by_normalized_name: dict[str, str] = {}

    for link in soup.find_all("a"):
        href = link.get("href")
        if not isinstance(href, str):
            continue

        filename = _href_basename(href)
        normalized_filename = filename.casefold()
        if filename != "" and normalized_filename not in candidate_filenames:
            skipped_filenames_by_normalized_name.setdefault(
                normalized_filename,
                filename,
            )

    return [
        skipped_filenames_by_normalized_name[normalized_filename]
        for normalized_filename in sorted(skipped_filenames_by_normalized_name)
    ]


def _select_zip_candidates(
    context: OpExecutionContext,
    *,
    candidates: list[ZipCandidate],
    listing_skipped_filenames: list[str],
    target_files: list[str],
    spec: ZipDownloadSpec,
) -> list[ZipCandidate]:
    """Apply target file config to listing candidates."""
    normalized_targets = _normalized_target_files(target_files, spec=spec)
    candidates_by_filename = {
        candidate.filename.casefold(): candidate for candidate in candidates
    }

    missing_targets = sorted(normalized_targets - set(candidates_by_filename))
    if missing_targets:
        raise ValueError(
            f"{spec.domain} target_files are not present in {spec.report_url}: "
            f"{', '.join(missing_targets)}"
        )

    if not normalized_targets:
        selected_candidates = candidates
    else:
        selected_candidates = [
            candidates_by_filename[normalized_filename]
            for normalized_filename in sorted(normalized_targets)
        ]

    skipped_candidates = [
        candidate.filename
        for candidate in candidates
        if candidate.filename.casefold()
        not in {selected.filename.casefold() for selected in selected_candidates}
    ]
    skipped_filenames = [*skipped_candidates, *listing_skipped_filenames]
    context.log.info(
        f"{spec.domain} zip selected files: "
        f"{', '.join(candidate.filename for candidate in selected_candidates) or '<none>'}"
    )
    context.log.info(
        f"{spec.domain} zip skipped files: {', '.join(skipped_filenames) or '<none>'}"
    )
    return selected_candidates


def _download_public_report_zip_files(
    context: OpExecutionContext,
    s3: S3Resource,
    *,
    config: PublicReportZipDownloadConfig,
    spec: ZipDownloadSpec,
) -> None:
    """Download matching NEMWeb report zips into landing storage."""
    response = requests.get(spec.report_url, timeout=30)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, features="html.parser")
    candidates = _zip_candidates_from_listing(soup, spec=spec)
    selected_candidates = _select_zip_candidates(
        context,
        candidates=candidates,
        listing_skipped_filenames=_skipped_listing_filenames(
            soup,
            candidates=candidates,
        ),
        target_files=config.target_files,
        spec=spec,
    )

    response_getter = get_response_factory()
    s3_client: S3Client = s3.get_client()

    for candidate in selected_candidates:
        s3_key = f"{spec.s3_prefix}/{candidate.filename}"
        context.log.info(f"uploading {candidate.url} to s3://{LANDING_BUCKET}/{s3_key}")
        contents = response_getter(candidate.url)
        s3_client.upload_fileobj(BytesIO(contents), LANDING_BUCKET, s3_key)


@op(description=f"Operation: {VICGAS_DESCRIPTION}".replace("\n\n", "\n"))
def download_vicgas_public_report_zip_files_op(
    context: OpExecutionContext,
    s3: S3Resource,
    config: PublicReportZipDownloadConfig,
) -> None:
    """Download current VICGAS public report zips into landing storage."""
    _download_public_report_zip_files(
        context,
        s3,
        config=config,
        spec=VICGAS_ZIP_DOWNLOAD_SPEC,
    )


@op(description=f"Operation: {STTM_DESCRIPTION}".replace("\n\n", "\n"))
def download_sttm_day_zip_files_op(
    context: OpExecutionContext,
    s3: S3Resource,
    config: PublicReportZipDownloadConfig,
) -> None:
    """Download current STTM DAYNN.ZIP bundles into landing storage."""
    _download_public_report_zip_files(
        context,
        s3,
        config=config,
        spec=STTM_DAY_ZIP_DOWNLOAD_SPEC,
    )


@job(
    description=f"Job: {VICGAS_DESCRIPTION}. To be run ad-hoc e.g. during initialization or sync missing data".replace(
        "\n\n", "\n"
    )
)
def download_vicgas_public_report_zip_files_job() -> None:
    """Run the VICGAS public report zip download operation."""
    download_vicgas_public_report_zip_files_op()


@job(
    description=f"Job: {STTM_DESCRIPTION}. To be run ad-hoc e.g. during initialization or sync missing data".replace(
        "\n\n", "\n"
    )
)
def download_sttm_day_zip_files_job() -> None:
    """Run the STTM DAYNN.ZIP download operation."""
    download_sttm_day_zip_files_op()
