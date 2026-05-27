"""Bronze source manifest builder for AEMO gas document metadata rows."""

import hashlib
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import polars as pl

from gas_market_knowledge_base.corpus_paths import (
    SOURCE_MANIFEST_RELATIVE_PATH as SOURCE_MANIFEST_RELATIVE_PATH,
)
from gas_market_knowledge_base.corpus_paths import (
    default_generated_paths,
    default_source_manifest_path,
)
from gas_market_knowledge_base.corpus_paths import (
    subproject_root as subproject_root,
)

AEMO_GAS_DOCUMENTS_PREFIX = "bronze/aemo_gas_documents"
BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME = "bronze_aemo_gas_document_sources"
DEFAULT_ENVIRONMENT = "dev"
DEFAULT_NAME_PREFIX = "energy-market"
MANIFEST_SCHEMA_VERSION = 1
MAX_DOCUMENT_IDENTITY_PART_CHARS = 96
DOCUMENT_IDENTITY_HASH_CHARS = 12

REQUIRED_METADATA_FIELDS = frozenset(
    {
        "archive_storage_uri",
        "content_length",
        "content_sha256",
        "corpus_source",
        "document_family_id",
        "document_kind",
        "document_title",
        "document_version",
        "document_version_id",
        "effective_date",
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

SELECTED_REQUIRED_STRING_FIELDS = (
    "content_sha256",
    "corpus_source",
    "document_family_id",
    "document_title",
    "source_url",
)

type MetadataRow = Mapping[str, object]
type ManifestJsonValue = str | int | None | dict[str, str]


class ManifestInputError(ValueError):
    """Raised when metadata row input cannot be loaded."""


class ManifestValidationError(ValueError):
    """Raised when metadata rows do not match the bronze contract."""


@dataclass(frozen=True, slots=True)
class EnvironmentBuckets:
    """Bucket names for one AEMO deployment environment."""

    environment: str
    name_prefix: str
    aemo_bucket: str
    archive_bucket: str


@dataclass(frozen=True, slots=True)
class SourceManifestSummary:
    """Summary counts for one source manifest sync."""

    environment: str
    metadata_row_count: int
    manifest_row_count: int
    excluded_by_decision_count: int
    excluded_without_content_sha256_count: int
    excluded_without_archive_storage_count: int

    def as_dict(self) -> dict[str, str | int]:
        """Return a JSON-ready summary mapping."""
        return {
            "environment": self.environment,
            "metadata_row_count": self.metadata_row_count,
            "manifest_row_count": self.manifest_row_count,
            "excluded_by_decision_count": self.excluded_by_decision_count,
            "excluded_without_content_sha256_count": (
                self.excluded_without_content_sha256_count
            ),
            "excluded_without_archive_storage_count": (
                self.excluded_without_archive_storage_count
            ),
        }


@dataclass(frozen=True, slots=True)
class SourceManifestResult:
    """Result of writing a bronze source manifest."""

    output_path: Path
    summary: SourceManifestSummary


def environment_buckets(
    environment: str = DEFAULT_ENVIRONMENT,
    *,
    name_prefix: str = DEFAULT_NAME_PREFIX,
) -> EnvironmentBuckets:
    """Return bucket names matching the AEMO ETL environment convention."""
    normalized_environment = _normalized_environment(environment)
    return EnvironmentBuckets(
        environment=normalized_environment,
        name_prefix=name_prefix,
        aemo_bucket=f"{normalized_environment}-{name_prefix}-aemo",
        archive_bucket=f"{normalized_environment}-{name_prefix}-archive",
    )


def default_metadata_table_uri(
    environment: str = DEFAULT_ENVIRONMENT,
    *,
    name_prefix: str = DEFAULT_NAME_PREFIX,
) -> str:
    """Return the default AEMO gas document source metadata Delta table URI."""
    buckets = environment_buckets(environment, name_prefix=name_prefix)
    return (
        f"s3://{buckets.aemo_bucket}/{AEMO_GAS_DOCUMENTS_PREFIX}/"
        f"{BRONZE_AEMO_GAS_DOCUMENT_SOURCES_TABLE_NAME}"
    )


def load_metadata_rows_from_delta(table_uri: str) -> list[dict[str, object]]:
    """Load metadata rows from an AEMO gas document source Delta table."""
    try:
        rows = pl.scan_delta(table_uri).collect().to_dicts()
    except Exception as e:
        raise ManifestInputError(
            f"failed to read source metadata Delta table {table_uri}: {e}"
        ) from e
    return cast(list[dict[str, object]], rows)


def load_metadata_rows_from_json(path: Path) -> list[dict[str, object]]:
    """Load fixture metadata rows from JSON or JSONL."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if path.suffix == ".jsonl":
        payload = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        payload = json.loads(text)
        if isinstance(payload, Mapping) and "rows" in payload:
            payload = payload["rows"]
    if not isinstance(payload, Sequence) or isinstance(payload, str | bytes):
        raise ManifestInputError(
            f"{path} must contain a JSON array, JSONL rows, or an object with rows"
        )
    return [
        _as_metadata_row(item, index=index, path=path)
        for index, item in enumerate(payload)
    ]


def sync_source_manifest(
    metadata_rows: Iterable[MetadataRow],
    *,
    output_path: Path | None = None,
    environment: str = DEFAULT_ENVIRONMENT,
    name_prefix: str = DEFAULT_NAME_PREFIX,
) -> SourceManifestResult:
    """Build and write the bronze source manifest JSONL file."""
    effective_output_path = output_path or default_source_manifest_path()
    manifest_rows, summary = build_source_manifest_rows(
        metadata_rows,
        environment=environment,
        name_prefix=name_prefix,
    )
    effective_output_path.parent.mkdir(parents=True, exist_ok=True)
    effective_output_path.write_text(
        dump_source_manifest_jsonl(manifest_rows),
        encoding="utf-8",
    )
    return SourceManifestResult(output_path=effective_output_path, summary=summary)


def build_source_manifest_rows(
    metadata_rows: Iterable[MetadataRow],
    *,
    environment: str = DEFAULT_ENVIRONMENT,
    name_prefix: str = DEFAULT_NAME_PREFIX,
) -> tuple[list[dict[str, ManifestJsonValue]], SourceManifestSummary]:
    """Build deterministic source manifest rows and explain exclusion counts."""
    buckets = environment_buckets(environment, name_prefix=name_prefix)
    manifest_rows: list[dict[str, ManifestJsonValue]] = []
    metadata_row_count = 0
    excluded_by_decision_count = 0
    excluded_without_content_sha256_count = 0
    excluded_without_archive_storage_count = 0

    for index, row in enumerate(metadata_rows):
        metadata_row_count += 1
        _validate_contract_fields(row, index=index)

        include_decision = _required_text(row, "include_decision", index=index)
        if include_decision != "include":
            excluded_by_decision_count += 1
            continue

        content_sha256 = _optional_text(row, "content_sha256", index=index)
        if content_sha256 is None:
            excluded_without_content_sha256_count += 1
            continue

        archive_uri = _archive_uri(
            row, archive_bucket=buckets.archive_bucket, index=index
        )
        if archive_uri is None:
            excluded_without_archive_storage_count += 1
            continue

        manifest_rows.append(
            _manifest_row(
                row,
                content_sha256=content_sha256,
                archive_uri=archive_uri,
                index=index,
            )
        )

    manifest_rows.sort(
        key=lambda row: (
            cast(str, row["document_identity"]),
            cast(str, row["source_url"]),
            cast(str, row["archive_uri"]),
        )
    )
    return manifest_rows, SourceManifestSummary(
        environment=buckets.environment,
        metadata_row_count=metadata_row_count,
        manifest_row_count=len(manifest_rows),
        excluded_by_decision_count=excluded_by_decision_count,
        excluded_without_content_sha256_count=excluded_without_content_sha256_count,
        excluded_without_archive_storage_count=excluded_without_archive_storage_count,
    )


def dump_source_manifest_jsonl(rows: Sequence[Mapping[str, object]]) -> str:
    """Serialize manifest rows as deterministic JSONL."""
    if not rows:
        return ""
    lines = [json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows]
    return f"{'\n'.join(lines)}\n"


def _manifest_row(
    row: MetadataRow,
    *,
    content_sha256: str,
    archive_uri: str,
    index: int,
) -> dict[str, ManifestJsonValue]:
    for field in SELECTED_REQUIRED_STRING_FIELDS:
        _required_text(row, field, index=index)

    corpus_source = _required_text(row, "corpus_source", index=index)
    document_family_id = _required_text(row, "document_family_id", index=index)
    document_identity = _document_identity(
        corpus_source=corpus_source,
        document_family_id=document_family_id,
        content_sha256=content_sha256,
    )
    target_s3_key = _optional_text(row, "target_s3_key", index=index)
    if target_s3_key is None:
        target_s3_key = _target_s3_key_from_archive_uri(archive_uri)

    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "document_identity": document_identity,
        "content_sha256": content_sha256,
        "corpus_source": corpus_source,
        "document_family_id": document_family_id,
        "document_title": _required_text(row, "document_title", index=index),
        "document_kind": _optional_text(row, "document_kind", index=index),
        "document_version": _optional_text(row, "document_version", index=index),
        "document_version_id": _optional_text(row, "document_version_id", index=index),
        "published_date": _optional_text(row, "published_date", index=index),
        "effective_date": _optional_text(row, "effective_date", index=index),
        "media_revision": _optional_text(row, "media_revision", index=index),
        "source_url": _required_text(row, "source_url", index=index),
        "resolved_url": _optional_text(row, "resolved_url", index=index),
        "source_page_url": _optional_text(row, "source_page_url", index=index),
        "source_page_title": _optional_text(row, "source_page_title", index=index),
        "source_link_text": _optional_text(row, "source_link_text", index=index),
        "archive_uri": archive_uri,
        "storage_uri": _optional_text(row, "storage_uri", index=index),
        "target_s3_key": target_s3_key,
        "content_length": _optional_int(row, "content_length", index=index),
        "generated_paths": _generated_paths(document_identity),
    }


def _generated_paths(document_identity: str) -> dict[str, str]:
    return default_generated_paths(document_identity)


def _document_identity(
    *,
    corpus_source: str,
    document_family_id: str,
    content_sha256: str,
) -> str:
    return (
        f"{_path_part(corpus_source)}/"
        f"{_path_part(document_family_id)}/"
        f"sha256-{content_sha256}"
    )


def _path_part(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        return "unknown"
    if len(slug) <= MAX_DOCUMENT_IDENTITY_PART_CHARS:
        return slug
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    prefix_length = MAX_DOCUMENT_IDENTITY_PART_CHARS - DOCUMENT_IDENTITY_HASH_CHARS - 1
    prefix = slug[:prefix_length].rstrip("-")
    return f"{prefix}-{digest[:DOCUMENT_IDENTITY_HASH_CHARS]}"


def _archive_uri(
    row: MetadataRow,
    *,
    archive_bucket: str,
    index: int,
) -> str | None:
    archive_uri = _optional_text(row, "archive_storage_uri", index=index)
    storage_uri = _optional_text(row, "storage_uri", index=index)
    if archive_uri is None and _is_archive_uri(
        storage_uri, archive_bucket=archive_bucket
    ):
        archive_uri = storage_uri
    if not _is_archive_uri(archive_uri, archive_bucket=archive_bucket):
        return None
    return archive_uri


def _is_archive_uri(value: str | None, *, archive_bucket: str) -> bool:
    if value is None:
        return False
    return value.startswith(f"s3://{archive_bucket}/")


def _target_s3_key_from_archive_uri(archive_uri: str) -> str:
    parsed = archive_uri.removeprefix("s3://")
    if "/" not in parsed:
        return ""
    return parsed.split("/", maxsplit=1)[1]


def _validate_contract_fields(row: MetadataRow, *, index: int) -> None:
    missing = sorted(REQUIRED_METADATA_FIELDS.difference(row.keys()))
    if missing:
        joined = ", ".join(missing)
        raise ManifestValidationError(
            f"metadata row {index} missing required metadata fields: {joined}"
        )


def _required_text(row: MetadataRow, key: str, *, index: int) -> str:
    value = _optional_text(row, key, index=index)
    if value is None:
        raise ManifestValidationError(
            f"metadata row {index} field {key} must be a non-empty string"
        )
    return value


def _optional_text(row: MetadataRow, key: str, *, index: int) -> str | None:
    value = row[key]
    if value is None:
        return None
    if not isinstance(value, str):
        raise ManifestValidationError(
            f"metadata row {index} field {key} must be a string or null"
        )
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def _optional_int(row: MetadataRow, key: str, *, index: int) -> int | None:
    value = row[key]
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ManifestValidationError(
            f"metadata row {index} field {key} must be an integer or null"
        )
    return value


def _normalized_environment(environment: str) -> str:
    normalized_environment = environment.strip().lower()
    if not normalized_environment:
        raise ManifestValidationError("environment must be a non-empty string")
    if re.search(r"[^a-z0-9-]", normalized_environment):
        raise ManifestValidationError(
            "environment may only contain lowercase letters, numbers, and hyphens"
        )
    return normalized_environment


def _as_metadata_row(item: object, *, index: int, path: Path) -> dict[str, object]:
    if not isinstance(item, Mapping):
        raise ManifestInputError(f"{path} row {index} must be a JSON object")
    return cast(dict[str, object], item)
