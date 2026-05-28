"""AEMO major publications source manifest conversion from AEMO ETL metadata."""

import hashlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import cast
from urllib.parse import urlparse

from gas_market_knowledge_base.aemo_publications.corpus_paths import (
    AemoPublicationCorpusPaths,
    default_corpus_paths,
)
from gas_market_knowledge_base.corpus_core.manifest import (
    MANIFEST_SCHEMA_VERSION,
    ManifestJsonValue,
    SourceManifestRow,
    document_identity,
    dump_source_manifest_jsonl,
)

AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE = "major_publications"
AEMO_MAJOR_PUBLICATIONS_HUB_URL = (
    "https://www.aemo.com.au/energy-systems/major-publications/"
)
AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL = (
    "https://www.aemo.com.au/library/major-publications"
)
SUPPORTED_CONTENT_TYPES = frozenset({"application/pdf"})
SUPPORTED_EXTENSIONS = frozenset({".pdf"})
REQUIRED_DOWNLOAD_METADATA_FIELDS = frozenset(
    {
        "archive_storage_uri",
        "content_length",
        "content_sha256",
        "content_type",
        "corpus_source",
        "document_family_id",
        "document_kind",
        "document_title",
        "document_version",
        "document_version_id",
        "effective_date",
        "exclude_reason",
        "include_decision",
        "media_revision",
        "published_date",
        "resolved_url",
        "source_link_text",
        "source_page_title",
        "source_page_url",
        "source_url",
        "storage_uri",
        "target_s3_key",
    }
)

type DownloadMetadataRow = Mapping[str, object]


class AemoPublicationManifestValidationError(ValueError):
    """Raised when downloaded publication metadata rows are malformed."""


@dataclass(frozen=True, slots=True)
class AemoPublicationManifestSummary:
    """Summary counts for AEMO publications manifest conversion."""

    metadata_row_count: int
    manifest_row_count: int
    included_row_count: int
    review_needed_row_count: int
    excluded_out_of_scope_count: int

    def as_dict(self) -> dict[str, int]:
        """Return a JSON-ready summary mapping."""
        return {
            "metadata_row_count": self.metadata_row_count,
            "manifest_row_count": self.manifest_row_count,
            "included_row_count": self.included_row_count,
            "review_needed_row_count": self.review_needed_row_count,
            "excluded_out_of_scope_count": self.excluded_out_of_scope_count,
        }


@dataclass(frozen=True, slots=True)
class AemoPublicationManifestResult:
    """Result of writing an AEMO publications source manifest."""

    output_path: Path
    summary: AemoPublicationManifestSummary


def write_aemo_publication_manifest(
    metadata_rows: Iterable[DownloadMetadataRow],
    *,
    paths: AemoPublicationCorpusPaths | None = None,
) -> AemoPublicationManifestResult:
    """Write the AEMO publications bronze source manifest from metadata rows."""
    effective_paths = paths or default_corpus_paths()
    manifest_rows, summary = build_aemo_publication_manifest_rows(
        metadata_rows,
        paths=effective_paths,
    )
    effective_paths.source_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    effective_paths.source_manifest_path.write_text(
        dump_source_manifest_jsonl(manifest_rows),
        encoding="utf-8",
    )
    return AemoPublicationManifestResult(
        output_path=effective_paths.source_manifest_path,
        summary=summary,
    )


def build_aemo_publication_manifest_rows(
    metadata_rows: Iterable[DownloadMetadataRow],
    *,
    paths: AemoPublicationCorpusPaths | None = None,
) -> tuple[list[dict[str, ManifestJsonValue]], AemoPublicationManifestSummary]:
    """Convert downloaded AEMO major-publications metadata to manifest rows."""
    effective_paths = paths or default_corpus_paths()
    manifest_rows: list[dict[str, ManifestJsonValue]] = []
    seen_included_content_hashes: set[str] = set()
    metadata_row_count = 0
    included_row_count = 0
    review_needed_row_count = 0
    excluded_out_of_scope_count = 0

    for index, row in enumerate(metadata_rows):
        metadata_row_count += 1
        _validate_contract_fields(row, index=index)
        if not _is_major_publications_hub_or_library_row(row, index=index):
            excluded_out_of_scope_count += 1
            continue

        review_status = _review_status(row, index=index)
        content_sha256 = _optional_text(row, "content_sha256", index=index)
        if (
            review_status == "ready"
            and content_sha256 is not None
            and content_sha256 in seen_included_content_hashes
        ):
            review_status = "duplicate_content_hash"

        if review_status == "ready":
            included_row_count += 1
            seen_included_content_hashes.add(cast(str, content_sha256))
        else:
            review_needed_row_count += 1

        manifest_rows.append(
            _manifest_row(
                row,
                paths=effective_paths,
                index=index,
                review_status=review_status,
            )
        )

    manifest_rows.sort(
        key=lambda row: (
            cast(str, row["document_identity"]),
            cast(str, row["source_url"]),
            cast(str | None, row["archive_uri"]) or "",
            cast(str, row["review_status"]),
        )
    )
    return manifest_rows, AemoPublicationManifestSummary(
        metadata_row_count=metadata_row_count,
        manifest_row_count=len(manifest_rows),
        included_row_count=included_row_count,
        review_needed_row_count=review_needed_row_count,
        excluded_out_of_scope_count=excluded_out_of_scope_count,
    )


def _manifest_row(
    row: DownloadMetadataRow,
    *,
    paths: AemoPublicationCorpusPaths,
    index: int,
    review_status: str,
) -> dict[str, ManifestJsonValue]:
    content_sha256 = _optional_text(row, "content_sha256", index=index)
    manifest_hash = content_sha256 or _fallback_row_hash(row, index=index)
    document_family_id = _required_text(row, "document_family_id", index=index)
    identity = document_identity(
        corpus_source=AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
        document_family_id=document_family_id,
        content_sha256=manifest_hash,
    )
    include_decision = "include" if review_status == "ready" else "needs_human_review"
    archive_uri = _storage_uri(row, index=index) if review_status == "ready" else None
    storage_uri = _optional_text(row, "storage_uri", index=index)
    if storage_uri is None:
        storage_uri = _optional_text(row, "archive_storage_uri", index=index)
    target_s3_key = _optional_text(row, "target_s3_key", index=index)
    if target_s3_key is None and archive_uri is not None:
        target_s3_key = _target_s3_key_from_storage_uri(archive_uri)

    manifest_row = SourceManifestRow(
        schema_version=MANIFEST_SCHEMA_VERSION,
        document_identity=identity,
        content_sha256=manifest_hash,
        corpus_source=AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE,
        document_family_id=document_family_id,
        document_title=_required_text(row, "document_title", index=index),
        document_kind=_optional_text(row, "document_kind", index=index),
        document_version=_optional_text(row, "document_version", index=index),
        document_version_id=_optional_text(row, "document_version_id", index=index),
        published_date=_optional_text(row, "published_date", index=index),
        effective_date=_optional_text(row, "effective_date", index=index),
        media_revision=_optional_text(row, "media_revision", index=index),
        source_url=_required_text(row, "source_url", index=index),
        resolved_url=_optional_text(row, "resolved_url", index=index),
        source_page_url=_optional_text(row, "source_page_url", index=index),
        source_page_title=_optional_text(row, "source_page_title", index=index),
        source_link_text=_optional_text(row, "source_link_text", index=index),
        archive_uri=archive_uri or "",
        storage_uri=storage_uri,
        target_s3_key=target_s3_key,
        content_length=_optional_int(row, "content_length", index=index),
        include_decision=include_decision,
        review_status=review_status,
        review_reason=_review_reason(row, review_status=review_status, index=index),
        generated_paths=paths.generated_paths(identity),
    ).as_dict()
    if review_status != "ready":
        manifest_row["archive_uri"] = None
        if content_sha256 is None:
            manifest_row["content_sha256"] = None
    return manifest_row


def _review_status(row: DownloadMetadataRow, *, index: int) -> str:
    include_decision = _required_text(row, "include_decision", index=index)
    if include_decision != "include":
        return include_decision
    if _optional_text(row, "content_sha256", index=index) is None:
        exclude_reason = _optional_text(row, "exclude_reason", index=index)
        if exclude_reason is not None and "download failed" in exclude_reason.lower():
            return "download_failed"
        return "missing_content_sha256"
    if _storage_uri(row, index=index) is None:
        return "missing_storage_uri"
    if not _is_supported_media(row, index=index):
        return "unsupported_media_type"
    return "ready"


def _review_reason(
    row: DownloadMetadataRow,
    *,
    review_status: str,
    index: int,
) -> str | None:
    if review_status == "ready":
        return None
    exclude_reason = _optional_text(row, "exclude_reason", index=index)
    if exclude_reason is not None:
        return exclude_reason
    return review_status.replace("_", " ")


def _is_supported_media(row: DownloadMetadataRow, *, index: int) -> bool:
    content_type = _content_type_base(_optional_text(row, "content_type", index=index))
    if content_type in SUPPORTED_CONTENT_TYPES:
        return True
    source_url = _optional_text(row, "resolved_url", index=index) or _required_text(
        row, "source_url", index=index
    )
    extension = PurePosixPath(urlparse(source_url).path).suffix.lower()
    return extension in SUPPORTED_EXTENSIONS


def _is_major_publications_hub_or_library_row(
    row: DownloadMetadataRow,
    *,
    index: int,
) -> bool:
    if (
        _required_text(row, "corpus_source", index=index)
        != AEMO_MAJOR_PUBLICATIONS_CORPUS_SOURCE
    ):
        return False
    source_page_url = _required_text(row, "source_page_url", index=index)
    normalized = source_page_url.rstrip("/") + "/"
    return normalized.startswith(
        AEMO_MAJOR_PUBLICATIONS_HUB_URL
    ) or normalized.startswith(AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL.rstrip("/") + "/")


def _storage_uri(row: DownloadMetadataRow, *, index: int) -> str | None:
    return _optional_text(row, "storage_uri", index=index) or _optional_text(
        row, "archive_storage_uri", index=index
    )


def _target_s3_key_from_storage_uri(storage_uri: str) -> str:
    parsed = storage_uri.removeprefix("s3://")
    if "/" not in parsed:
        return ""
    return parsed.split("/", maxsplit=1)[1]


def _content_type_base(content_type: str | None) -> str | None:
    if content_type is None:
        return None
    base = content_type.split(";", 1)[0].strip().lower()
    return base or None


def _fallback_row_hash(row: DownloadMetadataRow, *, index: int) -> str:
    source_content_hash = _optional_text(row, "source_content_hash", index=index)
    if source_content_hash is not None:
        return hashlib.sha256(source_content_hash.encode("utf-8")).hexdigest()
    source_url = _required_text(row, "source_url", index=index)
    return hashlib.sha256(source_url.encode("utf-8")).hexdigest()


def _validate_contract_fields(row: DownloadMetadataRow, *, index: int) -> None:
    missing = sorted(REQUIRED_DOWNLOAD_METADATA_FIELDS.difference(row.keys()))
    if missing:
        joined = ", ".join(missing)
        raise AemoPublicationManifestValidationError(
            f"metadata row {index} missing required metadata fields: {joined}"
        )


def _required_text(row: DownloadMetadataRow, key: str, *, index: int) -> str:
    value = _optional_text(row, key, index=index)
    if value is None:
        raise AemoPublicationManifestValidationError(
            f"metadata row {index} field {key} must be a non-empty string"
        )
    return value


def _optional_text(row: DownloadMetadataRow, key: str, *, index: int) -> str | None:
    value = row[key]
    if value is None:
        return None
    if not isinstance(value, str):
        raise AemoPublicationManifestValidationError(
            f"metadata row {index} field {key} must be a string or null"
        )
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def _optional_int(row: DownloadMetadataRow, key: str, *, index: int) -> int | None:
    value = row[key]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise AemoPublicationManifestValidationError(
            f"metadata row {index} field {key} must be an integer or null"
        )
    return value
