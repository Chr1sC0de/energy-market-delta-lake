"""Asset factory for AEMO gas document source metadata."""

import hashlib
import json
import mimetypes
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from io import BytesIO
from pathlib import PurePosixPath
from typing import Unpack, cast
from urllib.parse import urlparse

import requests
from botocore.exceptions import ClientError
from dagster import (
    AssetExecutionContext,
    AssetsDefinition,
    MaterializeResult,
    MetadataValue,
    asset,
)
from dagster._core.definitions.metadata import RawMetadataValue
from dagster_aws.s3 import S3Resource
from polars import Datetime, Int64, LazyFrame, Schema, String
from requests import RequestException, Response
from types_boto3_s3 import S3Client

from aemo_etl.asset_organization import (
    GAS_AEMO_GAS_DOCUMENTS_GROUP,
    GAS_AEMO_MAJOR_PUBLICATIONS_GROUP,
)
from aemo_etl.configs import AEMO_BUCKET, ARCHIVE_BUCKET, DAGSTER_URI, LANDING_BUCKET
from aemo_etl.defs.resources import SOURCE_TABLE_BRONZE_READ_IO_MANAGER_KEY
from aemo_etl.factories.aemo_gas_documents.models import (
    AEMO_GSOO_CORPUS_SOURCE,
    AEMO_GSOO_URL,
    AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
    AEMO_MAJOR_PUBLICATIONS_HUB_URL,
    AEMO_WA_GSOO_CORPUS_SOURCE,
    AEMO_WA_GSOO_URL,
    AEMOGasDocumentPendingObservation,
    AEMOGasDocumentSourcePage,
    AEMOGasDocumentSourceRecord,
    DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES,
)
from aemo_etl.factories.aemo_gas_documents.manifest import (
    load_default_aemo_gas_document_observations,
)
from aemo_etl.factories.aemo_gas_documents.scraper import (
    discover_aemo_gas_document_observations,
)
from aemo_etl.models._graph_asset_kwargs import AssetDefinitonParamSpec
from aemo_etl.utils import (
    get_lazyframe_num_rows,
    get_metadata_schema,
    request_get,
    table_exists,
)

AEMO_GAS_DOCUMENTS_DOMAIN = "aemo_gas_documents"
BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME = "bronze_aemo_gas_document_sources"
AEMO_GAS_DOCUMENTS_PREFIX = f"bronze/{AEMO_GAS_DOCUMENTS_DOMAIN}"
AEMO_MAJOR_PUBLICATIONS_DOMAIN = "aemo_major_publications"
BRONZE_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOADS_TABLE_NAME = (
    "bronze_aemo_major_publications_hub_downloads"
)
AEMO_MAJOR_PUBLICATIONS_PREFIX = f"bronze/{AEMO_MAJOR_PUBLICATIONS_DOMAIN}"
DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES = (
    AEMOGasDocumentSourcePage(
        corpus_source=AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
        source_page_url=AEMO_MAJOR_PUBLICATIONS_HUB_URL,
        include_decision="include",
        include_reason=(
            "Approved major-publications hub corpus source. Public AEMO media "
            "links are downloaded, landed, and archived for downstream corpus "
            "generation."
        ),
        source_page_title="Major publications",
        source_page_section="Energy systems major publications",
        discover_child_pages=True,
    ),
    AEMOGasDocumentSourcePage(
        corpus_source=AEMO_GSOO_CORPUS_SOURCE,
        source_page_url=AEMO_GSOO_URL,
        include_decision="include",
        include_reason=(
            "Approved Gas Statement of Opportunities publication bundle. "
            "Public AEMO media links are downloaded, landed, and archived for "
            "downstream corpus generation."
        ),
        source_page_title="Gas Statement of Opportunities",
        source_page_section="Gas forecasting and planning",
        discover_child_pages=True,
    ),
    AEMOGasDocumentSourcePage(
        corpus_source=AEMO_WA_GSOO_CORPUS_SOURCE,
        source_page_url=AEMO_WA_GSOO_URL,
        include_decision="include",
        include_reason=(
            "Approved WA Gas Statement of Opportunities publication bundle. "
            "Public AEMO media links are downloaded, landed, and archived for "
            "downstream corpus generation."
        ),
        source_page_title="WA Gas Statement of Opportunities",
        source_page_section="Gas forecasting and planning",
        discover_child_pages=True,
    ),
)
SURROGATE_KEY_COLUMNS = [
    "observation_type",
    "source_page_url",
    "source_url",
    "include_decision",
    "content_sha256",
]
DELTA_MERGE_OPTIONS = {
    "predicate": "source.surrogate_key = target.surrogate_key",
    "source_alias": "source",
    "target_alias": "target",
}
AEMO_GAS_DOCUMENT_REQUEST_HEADERS: Mapping[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/pdf,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-AU,en;q=0.9",
}
AEMO_GAS_DOCUMENT_REQUEST_TIMEOUT_SECONDS = 60
SAFE_MEDIA_EXTENSION_PATTERN = re.compile(r"^\.[a-z0-9][a-z0-9]{0,15}$")
DEFAULT_MEDIA_EXTENSION = ".bin"
CONTENT_TYPE_EXTENSION_OVERRIDES: Mapping[str, str] = {
    "application/gzip": ".gz",
    "application/msword": ".doc",
    "application/octet-stream": DEFAULT_MEDIA_EXTENSION,
    "application/pdf": ".pdf",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/x-zip-compressed": ".zip",
    "application/zip": ".zip",
    "text/csv": ".csv",
}

type AEMOGasDocumentObservationLoader = Callable[
    [datetime],
    Iterable[AEMOGasDocumentPendingObservation],
]

SCHEMA = Schema(
    {
        "observation_type": String,
        "corpus_source": String,
        "source_page_url": String,
        "source_page_title": String,
        "source_page_section": String,
        "source_page_observed_at": Datetime("us", time_zone="UTC"),
        "source_link_text": String,
        "source_url": String,
        "resolved_url": String,
        "normalized_source_url": String,
        "source_url_query": String,
        "document_family_id": String,
        "document_title": String,
        "document_kind": String,
        "include_decision": String,
        "include_reason": String,
        "exclude_reason": String,
        "content_type": String,
        "content_length": Int64,
        "etag": String,
        "last_modified": String,
        "content_sha256": String,
        "document_version": String,
        "document_version_id": String,
        "published_date": String,
        "effective_date": String,
        "media_revision": String,
        "landing_storage_uri": String,
        "archive_storage_uri": String,
        "storage_uri": String,
        "target_s3_key": String,
        "surrogate_key": String,
        "source_content_hash": String,
        "ingested_timestamp": Datetime("us", time_zone="UTC"),
    }
)

DESCRIPTIONS = {
    "observation_type": "Source-page inventory row or source-link observation row",
    "corpus_source": "AEMO gas corpus source such as gbb, sttm, dwgm, or retail_gas",
    "source_page_url": "Exact source page or explicit scope where the link was observed",
    "source_page_title": "Source page title observed or configured for audit",
    "source_page_section": "Nearest local section heading when available",
    "source_page_observed_at": "UTC timestamp when the source page was observed",
    "source_link_text": "Visible source-link text from the AEMO page",
    "source_url": "Exact source href after absolutizing relative links",
    "resolved_url": "Final URL after the media GET request follows redirects",
    "normalized_source_url": "Lowercase normalized URL used as a dedupe aid",
    "source_url_query": "Retained query string from the source URL",
    "document_family_id": "Stable corpus and normalized-title document family ID",
    "document_title": "Cleaned reader-visible document title",
    "document_kind": "Inferred kind such as procedure, guide, agreement, or unknown",
    "include_decision": "include, exclude, or needs_human_review",
    "include_reason": "Audit reason for including or holding the observation",
    "exclude_reason": "Audit reason for excluding a link or scope",
    "content_type": "HTTP content type from the media GET response",
    "content_length": "Downloaded byte length for included media rows",
    "etag": "HTTP ETag from the media GET response",
    "last_modified": "HTTP Last-Modified value from the media GET response",
    "content_sha256": "SHA-256 hash of downloaded media bytes",
    "document_version": "Visible version token parsed from link text or URL",
    "document_version_id": "Content hash version ID for byte-level deduplication",
    "published_date": "Visible publication date parsed from link text",
    "effective_date": "Visible effective date parsed from link text",
    "media_revision": "AEMO media-library rev query parameter when present",
    "landing_storage_uri": "Landing S3 URI used before metadata table write",
    "archive_storage_uri": "Archive S3 URI used after metadata table write",
    "storage_uri": "Durable storage URI for the archived media bytes",
    "target_s3_key": "S3 object key under bronze/aemo_gas_documents",
    "surrogate_key": f"SHA-256 key from {SURROGATE_KEY_COLUMNS}",
    "source_content_hash": "SHA-256 hash of the metadata row content",
    "ingested_timestamp": "UTC timestamp when the metadata batch was ingested",
}

assert len(SCHEMA) == len(DESCRIPTIONS)


@dataclass(frozen=True, slots=True)
class AEMOGasDocumentSourceWriteResult:
    """Result metadata for one AEMO gas document-source metadata write."""

    row_count: int
    target_exists_before_write: bool
    wrote_table: bool
    write_mode: str


@dataclass(frozen=True, slots=True)
class AEMOGasDocumentScrapeResult:
    """Result of scraping metadata and landing included media bytes."""

    records: list[AEMOGasDocumentSourceRecord]
    landed_keys: list[str]
    included_media_count: int
    excluded_observation_count: int
    needs_human_review_observation_count: int
    failed_download_count: int


def _stable_hash(parts: Iterable[object]) -> str:
    """Return a stable SHA-256 hash from scalar values."""
    payload = json.dumps([_json_safe_part(part) for part in parts], sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _json_safe_part(value: object) -> object:
    """Return a JSON-safe scalar representation."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _headers_get(headers: Mapping[str, str], name: str) -> str | None:
    """Return a response header value by case-insensitive name."""
    lower_name = name.lower()
    for key, value in headers.items():
        if key.lower() == lower_name:
            return value
    return None


def _response_url(response: Response, fallback: str) -> str:
    """Return a response URL with a safe fallback for test doubles."""
    url = getattr(response, "url", fallback)
    if isinstance(url, str) and url:
        return url
    return fallback


def _content_length(headers: Mapping[str, str], content: bytes) -> int:
    """Return HTTP content length when valid, otherwise the downloaded byte count."""
    content_length = _headers_get(headers, "Content-Length")
    if content_length is None:
        return len(content)
    try:
        return int(content_length)
    except ValueError:
        return len(content)


def request_get_aemo_gas_document(path: str) -> Response:
    """Run an AEMO gas document GET with browser-compatible request headers."""
    return request_get(path, getter=_aemo_gas_document_get)


def _aemo_gas_document_get(path: str) -> Response:
    response: Response = requests.get(
        path,
        headers=AEMO_GAS_DOCUMENT_REQUEST_HEADERS,
        timeout=AEMO_GAS_DOCUMENT_REQUEST_TIMEOUT_SECONDS,
    )
    return response


def _record_surrogate_key(
    observation: AEMOGasDocumentPendingObservation,
    *,
    content_sha256: str | None,
) -> str:
    """Return the metadata row surrogate key."""
    return _stable_hash(
        [
            observation.observation_type,
            observation.source_page_url,
            observation.source_url,
            observation.include_decision,
            content_sha256,
        ]
    )


def _record_source_content_hash(record: AEMOGasDocumentSourceRecord) -> str:
    """Return a content hash for the mutable metadata row fields."""
    return _stable_hash(
        [
            record.observation_type,
            record.corpus_source,
            record.source_page_url,
            record.source_page_title,
            record.source_page_section,
            record.source_link_text,
            record.source_url,
            record.resolved_url,
            record.normalized_source_url,
            record.source_url_query,
            record.document_family_id,
            record.document_title,
            record.document_kind,
            record.include_decision,
            record.include_reason,
            record.exclude_reason,
            record.content_type,
            record.content_length,
            record.etag,
            record.last_modified,
            record.content_sha256,
            record.document_version,
            record.document_version_id,
            record.published_date,
            record.effective_date,
            record.media_revision,
            record.storage_uri,
            record.target_s3_key,
        ]
    )


def _object_exists(
    s3_client: S3Client,
    *,
    bucket: str,
    key: str,
) -> bool:
    """Return whether an S3 object exists."""
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise
    return True


def _content_type_base(content_type: str | None) -> str | None:
    """Return a normalized media type without parameters."""
    if content_type is None:
        return None
    base = content_type.split(";", 1)[0].strip().lower()
    return base or None


def _safe_media_extension(extension: str | None) -> str | None:
    """Return a normalized safe file extension when one is usable."""
    if extension is None:
        return None
    normalized = extension.lower()
    if SAFE_MEDIA_EXTENSION_PATTERN.fullmatch(normalized) is None:
        return None
    return normalized


def _url_media_extension(source_url: str) -> str | None:
    """Return a safe extension from a URL path when available."""
    suffix = PurePosixPath(urlparse(source_url).path).suffix
    return _safe_media_extension(suffix)


def _content_type_media_extension(content_type: str | None) -> str | None:
    """Return a safe extension inferred from an HTTP content type."""
    base = _content_type_base(content_type)
    if base is None:
        return None
    extension = CONTENT_TYPE_EXTENSION_OVERRIDES.get(base)
    if extension is None:
        extension = mimetypes.guess_extension(base)
    return _safe_media_extension(extension)


def _media_extension(*, source_url: str, content_type: str | None) -> str:
    """Return the storage suffix for downloaded media bytes."""
    return (
        _url_media_extension(source_url)
        or _content_type_media_extension(content_type)
        or DEFAULT_MEDIA_EXTENSION
    )


def _media_key(
    *,
    content_sha256: str,
    source_url: str,
    content_type: str | None,
    storage_prefix: str = AEMO_GAS_DOCUMENTS_PREFIX,
) -> str:
    """Return the canonical S3 key for a downloaded media byte version."""
    extension = _media_extension(source_url=source_url, content_type=content_type)
    return f"{storage_prefix}/{content_sha256}{extension}"


def _empty_record(
    observation: AEMOGasDocumentPendingObservation,
) -> AEMOGasDocumentSourceRecord:
    """Build a metadata row for a source-page, excluded, or review observation."""
    surrogate_key = _record_surrogate_key(observation, content_sha256=None)
    record = AEMOGasDocumentSourceRecord(
        observation_type=observation.observation_type,
        corpus_source=observation.corpus_source,
        source_page_url=observation.source_page_url,
        source_page_title=observation.source_page_title,
        source_page_section=observation.source_page_section,
        source_page_observed_at=observation.source_page_observed_at,
        source_link_text=observation.source_link_text,
        source_url=observation.source_url,
        resolved_url=observation.resolved_url,
        normalized_source_url=observation.normalized_source_url,
        source_url_query=observation.source_url_query,
        document_family_id=observation.document_family_id,
        document_title=observation.document_title,
        document_kind=observation.document_kind,
        include_decision=observation.include_decision,
        include_reason=observation.include_reason,
        exclude_reason=observation.exclude_reason,
        content_type=None,
        content_length=None,
        etag=None,
        last_modified=None,
        content_sha256=None,
        document_version=observation.document_version,
        document_version_id=None,
        published_date=observation.published_date,
        effective_date=observation.effective_date,
        media_revision=observation.media_revision,
        landing_storage_uri=None,
        archive_storage_uri=None,
        storage_uri=None,
        target_s3_key=None,
        surrogate_key=surrogate_key,
        source_content_hash="",
    )
    return _with_source_content_hash(record)


def _with_source_content_hash(
    record: AEMOGasDocumentSourceRecord,
) -> AEMOGasDocumentSourceRecord:
    """Return a record with its source_content_hash populated."""
    return replace(record, source_content_hash=_record_source_content_hash(record))


def _download_failed_record(
    observation: AEMOGasDocumentPendingObservation,
    *,
    error: RequestException,
) -> AEMOGasDocumentSourceRecord:
    """Build a metadata-only row for included media that failed to download."""
    return _empty_record(
        replace(
            observation,
            should_download=False,
            exclude_reason=f"Download failed during materialization: {error}",
        )
    )


def _downloaded_record(
    observation: AEMOGasDocumentPendingObservation,
    *,
    response: Response,
    content: bytes,
    content_sha256: str,
    landing_bucket: str,
    archive_bucket: str,
    key: str,
) -> AEMOGasDocumentSourceRecord:
    """Build a metadata row for a downloaded included media observation."""
    headers = cast(Mapping[str, str], response.headers)
    landing_uri = f"s3://{landing_bucket}/{key}"
    archive_uri = f"s3://{archive_bucket}/{key}"
    surrogate_key = _record_surrogate_key(
        observation,
        content_sha256=content_sha256,
    )
    record = AEMOGasDocumentSourceRecord(
        observation_type=observation.observation_type,
        corpus_source=observation.corpus_source,
        source_page_url=observation.source_page_url,
        source_page_title=observation.source_page_title,
        source_page_section=observation.source_page_section,
        source_page_observed_at=observation.source_page_observed_at,
        source_link_text=observation.source_link_text,
        source_url=observation.source_url,
        resolved_url=_response_url(response, observation.source_url),
        normalized_source_url=observation.normalized_source_url,
        source_url_query=observation.source_url_query,
        document_family_id=observation.document_family_id,
        document_title=observation.document_title,
        document_kind=observation.document_kind,
        include_decision=observation.include_decision,
        include_reason=observation.include_reason,
        exclude_reason=observation.exclude_reason,
        content_type=_headers_get(headers, "Content-Type"),
        content_length=_content_length(headers, content),
        etag=_headers_get(headers, "ETag"),
        last_modified=_headers_get(headers, "Last-Modified"),
        content_sha256=content_sha256,
        document_version=observation.document_version,
        document_version_id=content_sha256,
        published_date=observation.published_date,
        effective_date=observation.effective_date,
        media_revision=observation.media_revision,
        landing_storage_uri=landing_uri,
        archive_storage_uri=archive_uri,
        storage_uri=archive_uri,
        target_s3_key=key,
        surrogate_key=surrogate_key,
        source_content_hash="",
    )
    return _with_source_content_hash(record)


def _land_media_once(
    *,
    s3_client: S3Client,
    landing_bucket: str,
    key: str,
    content: bytes,
    content_type: str | None,
) -> bool:
    """Land media bytes when the content-addressed object is not already present."""
    if _object_exists(s3_client, bucket=landing_bucket, key=key):
        return False
    extra_args = {}
    if content_type is not None:
        extra_args["ContentType"] = content_type
    s3_client.upload_fileobj(
        BytesIO(content),
        landing_bucket,
        key,
        ExtraArgs=extra_args,
    )
    return True


def scrape_and_land_aemo_gas_document_sources(
    *,
    s3_client: S3Client,
    source_pages: Iterable[AEMOGasDocumentSourcePage],
    request_getter: Callable[[str], Response] = request_get_aemo_gas_document,
    landing_bucket: str = LANDING_BUCKET,
    archive_bucket: str = ARCHIVE_BUCKET,
    storage_prefix: str = AEMO_GAS_DOCUMENTS_PREFIX,
    observed_at: datetime | None = None,
) -> AEMOGasDocumentScrapeResult:
    """Scrape metadata rows and land included media bytes to S3-compatible storage."""
    observations = discover_aemo_gas_document_observations(
        source_pages=source_pages,
        request_getter=request_getter,
        observed_at=observed_at,
    )
    return land_aemo_gas_document_observations(
        s3_client=s3_client,
        observations=observations,
        request_getter=request_getter,
        landing_bucket=landing_bucket,
        archive_bucket=archive_bucket,
        storage_prefix=storage_prefix,
    )


def land_aemo_gas_document_observations(
    *,
    s3_client: S3Client,
    observations: Iterable[AEMOGasDocumentPendingObservation],
    request_getter: Callable[[str], Response] = request_get_aemo_gas_document,
    landing_bucket: str = LANDING_BUCKET,
    archive_bucket: str = ARCHIVE_BUCKET,
    storage_prefix: str = AEMO_GAS_DOCUMENTS_PREFIX,
    logger: object | None = None,
) -> AEMOGasDocumentScrapeResult:
    """Land included media bytes and return metadata for pending observations."""
    records: list[AEMOGasDocumentSourceRecord] = []
    landed_keys: list[str] = []
    landed_keys_by_hash: dict[str, str] = {}
    included_media_count = 0
    excluded_observation_count = 0
    needs_human_review_observation_count = 0
    failed_download_count = 0

    for observation in observations:
        if observation.include_decision == "exclude":
            excluded_observation_count += 1
        if observation.include_decision == "needs_human_review":
            needs_human_review_observation_count += 1

        if not observation.should_download:
            records.append(_empty_record(observation))
            continue

        try:
            response = request_getter(observation.source_url)
        except RequestException as e:
            failed_download_count += 1
            if logger is not None and hasattr(logger, "warning"):
                logger.warning(
                    "recording AEMO gas document download failure for %s: %s",
                    observation.source_url,
                    e,
                )
            records.append(_download_failed_record(observation, error=e))
            continue

        content = response.content
        content_sha256 = hashlib.sha256(content).hexdigest()
        headers = cast(Mapping[str, str], response.headers)
        content_type = _headers_get(headers, "Content-Type")
        resolved_url = _response_url(response, observation.source_url)
        key = landed_keys_by_hash.get(content_sha256)
        if key is None:
            key = _media_key(
                content_sha256=content_sha256,
                source_url=resolved_url,
                content_type=content_type,
                storage_prefix=storage_prefix,
            )
        included_media_count += 1
        if content_sha256 not in landed_keys_by_hash:
            _land_media_once(
                s3_client=s3_client,
                landing_bucket=landing_bucket,
                key=key,
                content=content,
                content_type=content_type,
            )
            landed_keys.append(key)
            landed_keys_by_hash[content_sha256] = key
        records.append(
            _downloaded_record(
                observation,
                response=response,
                content=content,
                content_sha256=content_sha256,
                landing_bucket=landing_bucket,
                archive_bucket=archive_bucket,
                key=key,
            )
        )

    return AEMOGasDocumentScrapeResult(
        records=records,
        landed_keys=landed_keys,
        included_media_count=included_media_count,
        excluded_observation_count=excluded_observation_count,
        needs_human_review_observation_count=needs_human_review_observation_count,
        failed_download_count=failed_download_count,
    )


def records_to_lazyframe(
    records: list[AEMOGasDocumentSourceRecord],
    *,
    ingested_timestamp: datetime,
) -> LazyFrame:
    """Convert source records into a typed metadata LazyFrame."""
    if not records:
        return LazyFrame(schema=SCHEMA)

    return LazyFrame(
        {
            **{
                column: [getattr(record, column) for record in records]
                for column in SCHEMA
                if column != "ingested_timestamp"
            },
            "ingested_timestamp": [ingested_timestamp] * len(records),
        },
        schema=SCHEMA,
    )


def write_aemo_gas_document_sources_batch(
    batch: LazyFrame,
    *,
    target_table_uri: str,
    logger: object | None = None,
) -> AEMOGasDocumentSourceWriteResult:
    """Write AEMO gas document source metadata to a bounded Delta table."""
    row_count = get_lazyframe_num_rows(batch)
    target_exists = table_exists(target_table_uri)

    if row_count == 0 and target_exists:
        return AEMOGasDocumentSourceWriteResult(
            row_count=row_count,
            target_exists_before_write=target_exists,
            wrote_table=False,
            write_mode="skip",
        )

    if not target_exists:
        batch.sink_delta(target_table_uri, mode="append")
        return AEMOGasDocumentSourceWriteResult(
            row_count=row_count,
            target_exists_before_write=target_exists,
            wrote_table=True,
            write_mode="append",
        )

    merge_builder = batch.sink_delta(
        target_table_uri,
        mode="merge",
        delta_merge_options=DELTA_MERGE_OPTIONS,
    )
    assert merge_builder is not None, "mode was set to merge but result is None"
    if logger is not None and hasattr(logger, "info"):
        logger.info(f"merging AEMO gas document metadata with {DELTA_MERGE_OPTIONS}")
    merge_results = (
        merge_builder.when_matched_update_all(
            predicate=(
                "target.source_content_hash IS NULL OR "
                "source.source_content_hash != target.source_content_hash"
            )
        )
        .when_not_matched_insert_all()
        .execute()
    )
    if logger is not None and hasattr(logger, "info"):
        logger.info(f"merged AEMO gas document metadata with results {merge_results}")
    return AEMOGasDocumentSourceWriteResult(
        row_count=row_count,
        target_exists_before_write=target_exists,
        wrote_table=True,
        write_mode="merge",
    )


def _archive_landed_keys(
    *,
    s3_client: S3Client,
    landing_bucket: str,
    archive_bucket: str,
    landed_keys: Iterable[str],
) -> list[str]:
    """Move landed media bytes into archive storage after metadata write."""
    archived_keys: list[str] = []
    for key in landed_keys:
        s3_client.copy_object(
            CopySource={"Bucket": landing_bucket, "Key": key},
            Bucket=archive_bucket,
            Key=key,
        )
        s3_client.delete_object(Bucket=landing_bucket, Key=key)
        archived_keys.append(key)
    return archived_keys


def _asset_metadata(
    *,
    scrape_result: AEMOGasDocumentScrapeResult,
    write_result: AEMOGasDocumentSourceWriteResult,
    archived_keys: list[str],
    target_table_uri: str,
    landing_root: str,
    archive_root: str,
) -> dict[str, RawMetadataValue]:
    """Return stable Dagster materialization metadata."""
    source_page_count = sum(
        record.observation_type == "source_page" for record in scrape_result.records
    )
    return {
        "dagster/row_count": write_result.row_count,
        "target_table_uri": target_table_uri,
        "storage_uri": target_table_uri,
        "s3_landing_root": landing_root,
        "s3_archive_root": archive_root,
        "source_page_count": source_page_count,
        "write_mode": write_result.write_mode,
        "wrote_table": write_result.wrote_table,
        "included_download_count": scrape_result.included_media_count,
        "failed_count": scrape_result.failed_download_count,
        "review_needed_count": scrape_result.needs_human_review_observation_count,
        "included_media_count": scrape_result.included_media_count,
        "excluded_observation_count": scrape_result.excluded_observation_count,
        "needs_human_review_observation_count": (
            scrape_result.needs_human_review_observation_count
        ),
        "failed_download_count": scrape_result.failed_download_count,
        "landed_media_count": len(scrape_result.landed_keys),
        "archived_media_count": len(archived_keys),
        "archived_keys": MetadataValue.json(archived_keys),
    }


def aemo_gas_document_sources_asset_factory(
    *,
    source_pages: Iterable[AEMOGasDocumentSourcePage],
    request_getter: Callable[[str], Response] = request_get,
    observation_loader: AEMOGasDocumentObservationLoader | None = None,
    landing_bucket: str = LANDING_BUCKET,
    archive_bucket: str = ARCHIVE_BUCKET,
    aemo_bucket: str = AEMO_BUCKET,
    table_name: str = BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME,
    asset_domain: str = AEMO_GAS_DOCUMENTS_DOMAIN,
    storage_prefix: str | None = None,
    **asset_kwargs: Unpack[AssetDefinitonParamSpec],
) -> AssetsDefinition:
    """Create the AEMO gas document-source metadata bronze asset."""
    source_pages_tuple = tuple(source_pages)
    resolved_storage_prefix = storage_prefix or f"bronze/{asset_domain}"
    if observation_loader is None:
        observation_loader = _default_observation_loader(
            source_pages=source_pages_tuple,
            request_getter=request_getter,
        )

    target_table_uri = f"s3://{aemo_bucket}/{resolved_storage_prefix}/{table_name}"
    landing_root = f"s3://{landing_bucket}/{resolved_storage_prefix}"
    archive_root = f"s3://{archive_bucket}/{resolved_storage_prefix}"
    asset_kwargs.setdefault("key_prefix", ["bronze", asset_domain])
    asset_kwargs.setdefault("name", table_name)
    asset_kwargs.setdefault("group_name", GAS_AEMO_GAS_DOCUMENTS_GROUP)
    asset_kwargs.setdefault("io_manager_key", SOURCE_TABLE_BRONZE_READ_IO_MANAGER_KEY)
    asset_kwargs.setdefault("kinds", {"source", "table", "deltalake"})
    asset_kwargs.setdefault(
        "description",
        (
            "Bronze metadata table for public AEMO gas media source-page and "
            "source-link observations. Included media bytes are landed to S3 and "
            "archived only after the metadata Delta write succeeds."
        ),
    )
    caller_metadata = asset_kwargs.get("metadata") or {}
    asset_kwargs["metadata"] = {
        DAGSTER_URI: target_table_uri,
        "dagster/table_name": f"aemo.{asset_domain}.{table_name}",
        "dagster/column_schema": get_metadata_schema(SCHEMA, DESCRIPTIONS),
        "target_table_uri": target_table_uri,
        "configured_source_page_count": len(source_pages_tuple),
        "surrogate_key_sources": MetadataValue.json(SURROGATE_KEY_COLUMNS),
        "s3_landing_root": landing_root,
        "s3_archive_root": archive_root,
        **caller_metadata,
    }

    @asset(**asset_kwargs)
    def _asset(
        context: AssetExecutionContext,
        s3: S3Resource,
    ) -> MaterializeResult[None]:
        s3_client = s3.get_client()
        ingested_timestamp = datetime.now(UTC)
        scrape_result = land_aemo_gas_document_observations(
            s3_client=s3_client,
            observations=observation_loader(ingested_timestamp),
            request_getter=request_getter,
            landing_bucket=landing_bucket,
            archive_bucket=archive_bucket,
            storage_prefix=resolved_storage_prefix,
            logger=context.log,
        )
        batch = records_to_lazyframe(
            scrape_result.records,
            ingested_timestamp=ingested_timestamp,
        )
        write_result = write_aemo_gas_document_sources_batch(
            batch,
            target_table_uri=target_table_uri,
            logger=context.log,
        )
        archived_keys = []
        if write_result.wrote_table:
            archived_keys = _archive_landed_keys(
                s3_client=s3_client,
                landing_bucket=landing_bucket,
                archive_bucket=archive_bucket,
                landed_keys=scrape_result.landed_keys,
            )
        return MaterializeResult(
            metadata=_asset_metadata(
                scrape_result=scrape_result,
                write_result=write_result,
                archived_keys=archived_keys,
                target_table_uri=target_table_uri,
                landing_root=landing_root,
                archive_root=archive_root,
            )
        )

    return _asset


def aemo_major_publications_hub_downloads_asset_factory(
    *,
    source_pages: Iterable[AEMOGasDocumentSourcePage] = (
        DEFAULT_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOAD_SOURCE_PAGES
    ),
    request_getter: Callable[[str], Response] = request_get_aemo_gas_document,
    observation_loader: AEMOGasDocumentObservationLoader | None = None,
    landing_bucket: str = LANDING_BUCKET,
    archive_bucket: str = ARCHIVE_BUCKET,
    aemo_bucket: str = AEMO_BUCKET,
    **asset_kwargs: Unpack[AssetDefinitonParamSpec],
) -> AssetsDefinition:
    """Create the major-publications source-family download metadata bronze asset."""
    source_pages_tuple = tuple(source_pages)
    caller_metadata = asset_kwargs.pop("metadata", {}) or {}
    asset_kwargs.setdefault("group_name", GAS_AEMO_MAJOR_PUBLICATIONS_GROUP)
    asset_kwargs.setdefault(
        "description",
        (
            "Bronze metadata table for AEMO energy-systems major-publications "
            "hub, GSOO, and WA GSOO source pages and public media downloads. "
            "Media bytes are landed to S3 and archived only after the metadata "
            "Delta write succeeds."
        ),
    )
    asset_kwargs["metadata"] = {
        "source_family": AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
        "source_page_root": AEMO_MAJOR_PUBLICATIONS_HUB_URL,
        "source_page_roots": MetadataValue.json(
            [source_page.source_page_url for source_page in source_pages_tuple]
        ),
        **caller_metadata,
    }
    return aemo_gas_document_sources_asset_factory(
        source_pages=source_pages_tuple,
        request_getter=request_getter,
        observation_loader=observation_loader,
        landing_bucket=landing_bucket,
        archive_bucket=archive_bucket,
        aemo_bucket=aemo_bucket,
        table_name=BRONZE_AEMO_MAJOR_PUBLICATIONS_HUB_DOWNLOADS_TABLE_NAME,
        asset_domain=AEMO_MAJOR_PUBLICATIONS_DOMAIN,
        storage_prefix=AEMO_MAJOR_PUBLICATIONS_PREFIX,
        **asset_kwargs,
    )


def _default_observation_loader(
    *,
    source_pages: tuple[AEMOGasDocumentSourcePage, ...],
    request_getter: Callable[[str], Response],
) -> AEMOGasDocumentObservationLoader:
    """Return manifest-backed defaults while preserving custom scrape fixtures."""
    if source_pages == DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES:

        def _load_manifest(
            observed_at: datetime,
        ) -> Iterable[AEMOGasDocumentPendingObservation]:
            return load_default_aemo_gas_document_observations(observed_at=observed_at)

        return _load_manifest

    def _scrape_source_pages(
        observed_at: datetime,
    ) -> Iterable[AEMOGasDocumentPendingObservation]:
        return discover_aemo_gas_document_observations(
            source_pages=source_pages,
            request_getter=request_getter,
            observed_at=observed_at,
        )

    return _scrape_source_pages
