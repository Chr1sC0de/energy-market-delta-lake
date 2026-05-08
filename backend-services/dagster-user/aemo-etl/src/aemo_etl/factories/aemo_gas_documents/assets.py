"""Asset factory for AEMO gas document source metadata."""

import hashlib
import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from io import BytesIO
from typing import Unpack, cast

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
from requests import Response
from types_boto3_s3 import S3Client

from aemo_etl.configs import AEMO_BUCKET, ARCHIVE_BUCKET, DAGSTER_URI, LANDING_BUCKET
from aemo_etl.defs.resources import SOURCE_TABLE_BRONZE_READ_IO_MANAGER_KEY
from aemo_etl.factories.aemo_gas_documents.models import (
    AEMOGasDocumentPendingObservation,
    AEMOGasDocumentSourcePage,
    AEMOGasDocumentSourceRecord,
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
    "resolved_url": "Final URL after the PDF GET request follows redirects",
    "normalized_source_url": "Lowercase normalized URL used as a dedupe aid",
    "source_url_query": "Retained query string from the source URL",
    "document_family_id": "Stable corpus and normalized-title document family ID",
    "document_title": "Cleaned reader-visible document title",
    "document_kind": "Inferred kind such as procedure, guide, agreement, or unknown",
    "include_decision": "include, exclude, or needs_human_review",
    "include_reason": "Audit reason for including or holding the observation",
    "exclude_reason": "Audit reason for excluding a link or scope",
    "content_type": "HTTP content type from the PDF GET response",
    "content_length": "Downloaded byte length for included PDF rows",
    "etag": "HTTP ETag from the PDF GET response",
    "last_modified": "HTTP Last-Modified value from the PDF GET response",
    "content_sha256": "SHA-256 hash of downloaded PDF bytes",
    "document_version": "Visible version token parsed from link text or URL",
    "document_version_id": "Content hash version ID for byte-level deduplication",
    "published_date": "Visible publication date parsed from link text",
    "effective_date": "Visible effective date parsed from link text",
    "media_revision": "AEMO media-library rev query parameter when present",
    "landing_storage_uri": "Landing S3 URI used before metadata table write",
    "archive_storage_uri": "Archive S3 URI used after metadata table write",
    "storage_uri": "Durable storage URI for the archived PDF bytes",
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
    """Result of scraping metadata and landing included PDF bytes."""

    records: list[AEMOGasDocumentSourceRecord]
    landed_keys: list[str]
    included_pdf_count: int
    excluded_observation_count: int
    needs_human_review_observation_count: int


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


def _pdf_key(content_sha256: str) -> str:
    """Return the canonical S3 key for a downloaded PDF byte version."""
    return f"{AEMO_GAS_DOCUMENTS_PREFIX}/{content_sha256}.pdf"


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
    """Build a metadata row for a downloaded included PDF observation."""
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


def _land_pdf_once(
    *,
    s3_client: S3Client,
    landing_bucket: str,
    key: str,
    content: bytes,
) -> bool:
    """Land PDF bytes when the content-addressed object is not already present."""
    if _object_exists(s3_client, bucket=landing_bucket, key=key):
        return False
    s3_client.upload_fileobj(
        BytesIO(content),
        landing_bucket,
        key,
        ExtraArgs={"ContentType": "application/pdf"},
    )
    return True


def scrape_and_land_aemo_gas_document_sources(
    *,
    s3_client: S3Client,
    source_pages: Iterable[AEMOGasDocumentSourcePage],
    request_getter: Callable[[str], Response] = request_get,
    landing_bucket: str = LANDING_BUCKET,
    archive_bucket: str = ARCHIVE_BUCKET,
    observed_at: datetime | None = None,
) -> AEMOGasDocumentScrapeResult:
    """Scrape metadata rows and land included PDF bytes to S3-compatible storage."""
    observations = discover_aemo_gas_document_observations(
        source_pages=source_pages,
        request_getter=request_getter,
        observed_at=observed_at,
    )

    records: list[AEMOGasDocumentSourceRecord] = []
    landed_keys: list[str] = []
    landed_hashes: set[str] = set()
    included_pdf_count = 0
    excluded_observation_count = 0
    needs_human_review_observation_count = 0

    for observation in observations:
        if observation.include_decision == "exclude":
            excluded_observation_count += 1
        if observation.include_decision == "needs_human_review":
            needs_human_review_observation_count += 1

        if not observation.should_download:
            records.append(_empty_record(observation))
            continue

        response = request_getter(observation.source_url)
        content = response.content
        content_sha256 = hashlib.sha256(content).hexdigest()
        key = _pdf_key(content_sha256)
        included_pdf_count += 1
        if content_sha256 not in landed_hashes:
            _land_pdf_once(
                s3_client=s3_client,
                landing_bucket=landing_bucket,
                key=key,
                content=content,
            )
            landed_keys.append(key)
            landed_hashes.add(content_sha256)
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
        included_pdf_count=included_pdf_count,
        excluded_observation_count=excluded_observation_count,
        needs_human_review_observation_count=needs_human_review_observation_count,
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
    """Move landed PDF bytes into archive storage after metadata write."""
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
) -> dict[str, RawMetadataValue]:
    """Return stable Dagster materialization metadata."""
    return {
        "dagster/row_count": write_result.row_count,
        "write_mode": write_result.write_mode,
        "wrote_table": write_result.wrote_table,
        "included_pdf_count": scrape_result.included_pdf_count,
        "excluded_observation_count": scrape_result.excluded_observation_count,
        "needs_human_review_observation_count": (
            scrape_result.needs_human_review_observation_count
        ),
        "landed_pdf_count": len(scrape_result.landed_keys),
        "archived_pdf_count": len(archived_keys),
        "archived_keys": MetadataValue.json(archived_keys),
    }


def aemo_gas_document_sources_asset_factory(
    *,
    source_pages: Iterable[AEMOGasDocumentSourcePage],
    request_getter: Callable[[str], Response] = request_get,
    landing_bucket: str = LANDING_BUCKET,
    archive_bucket: str = ARCHIVE_BUCKET,
    aemo_bucket: str = AEMO_BUCKET,
    **asset_kwargs: Unpack[AssetDefinitonParamSpec],
) -> AssetsDefinition:
    """Create the AEMO gas document-source metadata bronze asset."""
    target_table_uri = (
        f"s3://{aemo_bucket}/{AEMO_GAS_DOCUMENTS_PREFIX}/"
        f"{BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME}"
    )
    asset_kwargs.setdefault("key_prefix", ["bronze", AEMO_GAS_DOCUMENTS_DOMAIN])
    asset_kwargs.setdefault("name", BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME)
    asset_kwargs.setdefault("group_name", "gas_raw")
    asset_kwargs.setdefault("io_manager_key", SOURCE_TABLE_BRONZE_READ_IO_MANAGER_KEY)
    asset_kwargs.setdefault("kinds", {"source", "table", "deltalake"})
    asset_kwargs.setdefault(
        "description",
        (
            "Bronze metadata table for public AEMO gas PDF source-page and "
            "source-link observations. Included PDF bytes are landed to S3 and "
            "archived only after the metadata Delta write succeeds."
        ),
    )
    caller_metadata = asset_kwargs.get("metadata") or {}
    asset_kwargs["metadata"] = {
        DAGSTER_URI: target_table_uri,
        "dagster/table_name": (
            f"aemo.{AEMO_GAS_DOCUMENTS_DOMAIN}."
            f"{BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME}"
        ),
        "dagster/column_schema": get_metadata_schema(SCHEMA, DESCRIPTIONS),
        "surrogate_key_sources": MetadataValue.json(SURROGATE_KEY_COLUMNS),
        "s3_landing_root": f"s3://{landing_bucket}/{AEMO_GAS_DOCUMENTS_PREFIX}",
        "s3_archive_root": f"s3://{archive_bucket}/{AEMO_GAS_DOCUMENTS_PREFIX}",
        **caller_metadata,
    }

    @asset(**asset_kwargs)
    def _asset(
        context: AssetExecutionContext,
        s3: S3Resource,
    ) -> MaterializeResult[None]:
        s3_client = s3.get_client()
        ingested_timestamp = datetime.now(UTC)
        scrape_result = scrape_and_land_aemo_gas_document_sources(
            s3_client=s3_client,
            source_pages=source_pages,
            request_getter=request_getter,
            landing_bucket=landing_bucket,
            archive_bucket=archive_bucket,
            observed_at=ingested_timestamp,
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
            )
        )

    return _asset
