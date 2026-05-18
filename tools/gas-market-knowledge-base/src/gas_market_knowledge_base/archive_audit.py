"""Archive-prefix completeness audit for the bronze source manifest."""

import json
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, cast
from urllib.parse import unquote, urlparse

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from gas_market_knowledge_base.pdf_cache import (
    PdfCacheInputError,
    SourcePdfEntry,
    load_source_pdf_manifest,
)
from gas_market_knowledge_base.source_manifest import (
    AEMO_GAS_DOCUMENTS_PREFIX,
    DEFAULT_ENVIRONMENT,
    DEFAULT_NAME_PREFIX,
    default_source_manifest_path,
    environment_buckets,
)

if TYPE_CHECKING:
    from types_boto3_s3 import S3Client


class ArchiveAuditInputError(ValueError):
    """Raised when archive audit inputs cannot be loaded."""


class ArchiveListingReadError(ValueError):
    """Raised when an archive prefix listing cannot be read."""


class ArchivePrefixLister(ABC):
    """Lister for expected archive PDF object URIs."""

    @abstractmethod
    def list_pdf_uris(self, prefix_uri: str) -> tuple[str, ...]:
        """Return sorted PDF object URIs for one archive prefix."""


class DefaultArchivePrefixLister(ArchivePrefixLister):
    """List archive PDF object URIs from S3-compatible storage."""

    def __init__(self, *, s3_client: "S3Client | None" = None) -> None:
        self._s3_client = s3_client

    def list_pdf_uris(self, prefix_uri: str) -> tuple[str, ...]:
        """Return sorted PDF object URIs for one S3 archive prefix."""
        archive_prefix = _parse_archive_prefix(prefix_uri)
        try:
            paginator = self._get_s3_client().get_paginator("list_objects_v2")
            pages = paginator.paginate(
                Bucket=archive_prefix.bucket,
                Prefix=archive_prefix.key_prefix,
            )
            uris: list[str] = []
            for page in pages:
                contents = cast(
                    Iterable[Mapping[str, object]], page.get("Contents", [])
                )
                for item in contents:
                    key = item.get("Key")
                    if isinstance(key, str):
                        uris.append(archive_prefix.uri_for_key(key))
        except (BotoCoreError, ClientError, KeyError) as e:
            raise ArchiveListingReadError(
                f"failed to list archive prefix {prefix_uri}: {e}"
            ) from e
        return _unique_pdf_uris(uris)

    def _get_s3_client(self) -> "S3Client":
        if self._s3_client is None:
            self._s3_client = boto3.client("s3")
        return self._s3_client


@dataclass(frozen=True, slots=True)
class ArchivePrefix:
    """Parsed S3 archive prefix."""

    uri: str
    bucket: str
    key_prefix: str

    def uri_for_key(self, key: str) -> str:
        """Return the S3 URI for a key in this prefix's bucket."""
        normalized_key = key.lstrip("/")
        if (
            self.key_prefix
            and normalized_key != self.key_prefix
            and not normalized_key.startswith(f"{self.key_prefix}/")
        ):
            normalized_key = f"{self.key_prefix}/{normalized_key}"
        return f"s3://{self.bucket}/{normalized_key}"


@dataclass(frozen=True, slots=True)
class ExtraManifestRow:
    """Manifest row that points outside the expected archive PDF listing."""

    line_number: int
    archive_uri: str
    content_sha256: str
    document_identity: str | None


@dataclass(frozen=True, slots=True)
class DuplicateManifestValue:
    """Duplicate archive URI or content hash observed in manifest rows."""

    value: str
    line_numbers: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ArchiveAuditResult:
    """Result of comparing archive prefix PDFs with the source manifest."""

    manifest_path: Path
    archive_prefix_uri: str
    prefix_pdf_object_count: int
    manifest_row_count: int
    manifest_object_count: int
    manifest_hash_count: int
    missing_archive_uris: tuple[str, ...]
    extra_manifest_rows: tuple[ExtraManifestRow, ...]
    duplicate_archive_uris: tuple[DuplicateManifestValue, ...]
    duplicate_content_hashes: tuple[DuplicateManifestValue, ...]
    manifest_errors: tuple[str, ...]

    @property
    def problem_count(self) -> int:
        """Return the number of reportable audit problems."""
        return (
            len(self.manifest_errors)
            + len(self.missing_archive_uris)
            + len(self.extra_manifest_rows)
            + len(self.duplicate_archive_uris)
            + len(self.duplicate_content_hashes)
        )

    def summary_text(self) -> str:
        """Return a deterministic single-line summary."""
        return (
            f"summary: prefix_pdf_objects={self.prefix_pdf_object_count} "
            f"manifest_rows={self.manifest_row_count} "
            f"manifest_objects={self.manifest_object_count} "
            f"manifest_hashes={self.manifest_hash_count} "
            f"missing_archive_pdfs={len(self.missing_archive_uris)} "
            f"extra_manifest_rows={len(self.extra_manifest_rows)} "
            f"duplicate_archive_uris={len(self.duplicate_archive_uris)} "
            f"duplicate_content_hashes={len(self.duplicate_content_hashes)} "
            f"manifest_errors={len(self.manifest_errors)}"
        )

    def problem_lines(self) -> tuple[str, ...]:
        """Return deterministic problem lines for CLI reporting."""
        lines: list[str] = []
        lines.extend(f"manifest error: {error}" for error in self.manifest_errors)
        lines.extend(f"missing archive PDF: {uri}" for uri in self.missing_archive_uris)
        lines.extend(
            (
                f"extra manifest row {row.line_number}: {row.archive_uri} "
                f"(content_sha256={row.content_sha256})"
            )
            for row in self.extra_manifest_rows
        )
        lines.extend(
            (
                f"duplicate archive_uri: {group.value} "
                f"(manifest rows {_line_numbers_text(group.line_numbers)})"
            )
            for group in self.duplicate_archive_uris
        )
        lines.extend(
            (
                f"duplicate content_sha256: {group.value} "
                f"(manifest rows {_line_numbers_text(group.line_numbers)})"
            )
            for group in self.duplicate_content_hashes
        )
        return tuple(lines)


def default_archive_prefix_uri(
    environment: str = DEFAULT_ENVIRONMENT,
    *,
    name_prefix: str = DEFAULT_NAME_PREFIX,
) -> str:
    """Return the default AEMO gas document archive prefix URI."""
    buckets = environment_buckets(environment, name_prefix=name_prefix)
    return f"s3://{buckets.archive_bucket}/{AEMO_GAS_DOCUMENTS_PREFIX}/"


def load_archive_listing_from_json(
    path: Path,
    *,
    archive_prefix_uri: str,
) -> tuple[str, ...]:
    """Load expected archive object URIs from a fixture JSON or JSONL listing."""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return ()
    if path.suffix == ".jsonl":
        payload = [json.loads(line) for line in text.splitlines() if line.strip()]
    else:
        payload = json.loads(text)
        if isinstance(payload, Mapping):
            if "objects" in payload:
                payload = payload["objects"]
            elif "rows" in payload:
                payload = payload["rows"]
    if not isinstance(payload, Sequence) or isinstance(payload, str | bytes):
        raise ArchiveAuditInputError(
            f"{path} must contain a JSON array, JSONL rows, or an object with objects"
        )

    archive_prefix = _parse_archive_prefix(archive_prefix_uri)
    uris = [
        _archive_listing_item_uri(item, index=index, path=path, prefix=archive_prefix)
        for index, item in enumerate(payload)
    ]
    return _unique_pdf_uris(uris)


def audit_archive_prefix(
    *,
    manifest_path: Path = default_source_manifest_path(),
    archive_prefix_uri: str = default_archive_prefix_uri(),
    listing_path: Path | None = None,
    prefix_lister: ArchivePrefixLister | None = None,
) -> ArchiveAuditResult:
    """Audit archive-prefix PDF completeness against the source manifest."""
    try:
        manifest = load_source_pdf_manifest(manifest_path)
    except PdfCacheInputError as e:
        raise ArchiveAuditInputError(str(e)) from e

    if listing_path is None:
        lister = prefix_lister or DefaultArchivePrefixLister()
        expected_uris = lister.list_pdf_uris(archive_prefix_uri)
    else:
        expected_uris = load_archive_listing_from_json(
            listing_path,
            archive_prefix_uri=archive_prefix_uri,
        )

    expected_uri_set = set(expected_uris)
    manifest_uri_set = {entry.archive_uri for entry in manifest.entries}
    manifest_hash_set = {entry.content_sha256 for entry in manifest.entries}
    missing_archive_uris = tuple(
        uri for uri in expected_uris if uri not in manifest_uri_set
    )
    extra_manifest_rows = tuple(
        ExtraManifestRow(
            line_number=entry.line_number,
            archive_uri=entry.archive_uri,
            content_sha256=entry.content_sha256,
            document_identity=entry.document_identity,
        )
        for entry in sorted(manifest.entries, key=_entry_sort_key)
        if entry.archive_uri not in expected_uri_set
    )

    return ArchiveAuditResult(
        manifest_path=manifest.path,
        archive_prefix_uri=archive_prefix_uri,
        prefix_pdf_object_count=len(expected_uris),
        manifest_row_count=manifest.row_count,
        manifest_object_count=len(manifest_uri_set),
        manifest_hash_count=len(manifest_hash_set),
        missing_archive_uris=missing_archive_uris,
        extra_manifest_rows=extra_manifest_rows,
        duplicate_archive_uris=_duplicate_groups(
            (entry.archive_uri, entry.line_number) for entry in manifest.entries
        ),
        duplicate_content_hashes=_duplicate_groups(
            (entry.content_sha256, entry.line_number) for entry in manifest.entries
        ),
        manifest_errors=manifest.errors,
    )


def _parse_archive_prefix(prefix_uri: str) -> ArchivePrefix:
    parsed = urlparse(prefix_uri)
    if parsed.scheme != "s3":
        raise ArchiveAuditInputError(
            f"archive prefix must be an S3 URI, got {prefix_uri!r}"
        )
    bucket = parsed.netloc.strip()
    key_prefix = unquote(parsed.path).lstrip("/").rstrip("/")
    if not bucket:
        raise ArchiveAuditInputError(f"archive prefix missing bucket: {prefix_uri!r}")
    if not key_prefix:
        raise ArchiveAuditInputError(f"archive prefix missing key: {prefix_uri!r}")
    return ArchivePrefix(uri=prefix_uri, bucket=bucket, key_prefix=key_prefix)


def _archive_listing_item_uri(
    item: object,
    *,
    index: int,
    path: Path,
    prefix: ArchivePrefix,
) -> str:
    if isinstance(item, str):
        return _archive_listing_text_uri(item, index=index, path=path, prefix=prefix)
    if not isinstance(item, Mapping):
        raise ArchiveAuditInputError(f"{path} listing row {index} must be an object")

    uri = _listing_text_field(item, "uri")
    if uri is None:
        uri = _listing_text_field(item, "archive_uri")
    if uri is None:
        uri = _listing_text_field(item, "storage_uri")
    if uri is not None:
        return uri

    key = _listing_text_field(item, "key")
    if key is not None:
        return prefix.uri_for_key(key)

    raise ArchiveAuditInputError(
        f"{path} listing row {index} must include uri, archive_uri, storage_uri, or key"
    )


def _archive_listing_text_uri(
    value: str,
    *,
    index: int,
    path: Path,
    prefix: ArchivePrefix,
) -> str:
    normalized = value.strip()
    if not normalized:
        raise ArchiveAuditInputError(f"{path} listing row {index} must be non-empty")
    parsed = urlparse(normalized)
    if parsed.scheme:
        return normalized
    return prefix.uri_for_key(normalized)


def _listing_text_field(row: Mapping[object, object], key: str) -> str | None:
    value = row.get(key)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def _unique_pdf_uris(uris: Iterable[str]) -> tuple[str, ...]:
    return tuple(sorted({uri for uri in uris if _is_pdf_uri(uri)}))


def _is_pdf_uri(uri: str) -> bool:
    parsed = urlparse(uri)
    return unquote(parsed.path).lower().endswith(".pdf")


def _duplicate_groups(
    values: Iterable[tuple[str, int]],
) -> tuple[DuplicateManifestValue, ...]:
    line_numbers_by_value: defaultdict[str, list[int]] = defaultdict(list)
    for value, line_number in values:
        line_numbers_by_value[value].append(line_number)
    return tuple(
        DuplicateManifestValue(value=value, line_numbers=tuple(sorted(line_numbers)))
        for value, line_numbers in sorted(line_numbers_by_value.items())
        if len(line_numbers) > 1
    )


def _entry_sort_key(entry: SourcePdfEntry) -> tuple[str, int]:
    return (entry.archive_uri, entry.line_number)


def _line_numbers_text(line_numbers: Sequence[int]) -> str:
    return ", ".join(str(line_number) for line_number in line_numbers)
