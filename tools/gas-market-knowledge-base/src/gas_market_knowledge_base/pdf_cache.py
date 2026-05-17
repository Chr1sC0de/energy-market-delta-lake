"""Local PDF cache fetcher for bronze source manifest rows."""

import hashlib
import json
import re
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast
from urllib.parse import ParseResult, unquote, urlparse

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from types_boto3_s3 import S3Client

from gas_market_knowledge_base.source_manifest import (
    default_source_manifest_path,
    subproject_root,
)

PDF_CACHE_RELATIVE_PATH = Path(".cache/pdfs")
_SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
_READ_CHUNK_SIZE = 1024 * 1024


class PdfCacheInputError(ValueError):
    """Raised when source manifest input cannot be loaded."""


class ArchiveObjectReadError(ValueError):
    """Raised when an archive object cannot be read."""


class PdfCacheWriteError(ValueError):
    """Raised when a validated PDF cannot be written to the cache."""


class ArchiveObjectReader(ABC):
    """Reader for archived PDF object bytes."""

    @abstractmethod
    def read_bytes(self, uri: str) -> bytes:
        """Return bytes for one archive URI."""


class DefaultArchiveObjectReader(ArchiveObjectReader):
    """Read archive bytes from S3 or local fixture paths."""

    def __init__(self, *, s3_client: S3Client | None = None) -> None:
        self._s3_client = s3_client

    def read_bytes(self, uri: str) -> bytes:
        """Return bytes for one supported archive URI."""
        parsed = urlparse(uri)
        if parsed.scheme == "s3":
            return self._read_s3_uri(uri, parsed=parsed)
        if parsed.scheme == "file":
            return self._read_file_uri(uri, parsed=parsed)
        if parsed.scheme == "":
            return self._read_local_path(uri)
        raise ArchiveObjectReadError(
            f"unsupported archive URI scheme {parsed.scheme!r}"
        )

    def _read_s3_uri(self, uri: str, *, parsed: ParseResult) -> bytes:
        bucket = parsed.netloc.strip()
        key = unquote(parsed.path).lstrip("/")
        if not bucket or not key:
            raise ArchiveObjectReadError(f"invalid S3 archive URI {uri!r}")

        try:
            response = self._get_s3_client().get_object(Bucket=bucket, Key=key)
            body = response["Body"]
            return body.read()
        except (BotoCoreError, ClientError, KeyError) as e:
            raise ArchiveObjectReadError(str(e)) from e

    def _get_s3_client(self) -> S3Client:
        if self._s3_client is None:
            self._s3_client = boto3.client("s3")
        return self._s3_client

    def _read_file_uri(self, uri: str, *, parsed: ParseResult) -> bytes:
        if parsed.netloc not in {"", "localhost"}:
            raise ArchiveObjectReadError(f"unsupported file URI host {parsed.netloc!r}")
        return self._read_path(Path(unquote(parsed.path)), uri=uri)

    def _read_local_path(self, uri: str) -> bytes:
        return self._read_path(Path(uri), uri=uri)

    def _read_path(self, path: Path, *, uri: str) -> bytes:
        try:
            return path.read_bytes()
        except OSError as e:
            raise ArchiveObjectReadError(str(e)) from e


@dataclass(frozen=True, slots=True)
class SourcePdfEntry:
    """Fetch-ready source PDF entry from the bronze manifest."""

    line_number: int
    content_sha256: str
    archive_uri: str
    document_identity: str | None

    def label(self) -> str:
        """Return a human-readable row label for reports."""
        if self.document_identity is None:
            return f"manifest row {self.line_number}"
        return f"manifest row {self.line_number} ({self.document_identity})"


@dataclass(frozen=True, slots=True)
class SourcePdfManifest:
    """Parsed source manifest rows plus row-level validation errors."""

    path: Path
    row_count: int
    entries: tuple[SourcePdfEntry, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PdfCacheResult:
    """Result of one PDF cache fetch run."""

    manifest_path: Path
    cache_dir: Path
    manifest_row_count: int
    fetchable_row_count: int
    reused_count: int
    downloaded_count: int
    refreshed_count: int
    invalid_cache_entry_count: int
    errors: tuple[str, ...]

    @property
    def error_count(self) -> int:
        """Return the number of row-level fetch or validation errors."""
        return len(self.errors)


def default_pdf_cache_dir() -> Path:
    """Return the default ignored PDF cache directory."""
    return subproject_root() / PDF_CACHE_RELATIVE_PATH


def pdf_cache_path(content_sha256: str, *, cache_dir: Path) -> Path:
    """Return the deterministic cache path for one content hash."""
    return cache_dir / f"{content_sha256}.pdf"


def load_source_pdf_manifest(path: Path) -> SourcePdfManifest:
    """Load fetchable PDF entries from a bronze source manifest JSONL file."""
    if not path.exists():
        raise PdfCacheInputError(f"source manifest not found: {path}")

    rows: list[SourcePdfEntry] = []
    errors: list[str] = []
    row_count = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        raise PdfCacheInputError(f"failed to read source manifest {path}: {e}") from e

    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        row_count += 1
        payload = _json_manifest_row(line, path=path, line_number=line_number)
        entry, row_errors = _source_pdf_entry(payload, line_number=line_number)
        if entry is not None:
            rows.append(entry)
        errors.extend(row_errors)

    return SourcePdfManifest(
        path=path,
        row_count=row_count,
        entries=tuple(rows),
        errors=tuple(errors),
    )


def fetch_pdf_cache(
    *,
    manifest_path: Path = default_source_manifest_path(),
    cache_dir: Path = default_pdf_cache_dir(),
    archive_reader: ArchiveObjectReader | None = None,
) -> PdfCacheResult:
    """Populate the local PDF cache from source manifest archive objects."""
    manifest = load_source_pdf_manifest(manifest_path)
    cache_dir.mkdir(parents=True, exist_ok=True)

    reader = archive_reader or DefaultArchiveObjectReader()
    errors = list(manifest.errors)
    reused_count = 0
    downloaded_count = 0
    refreshed_count = 0
    invalid_cache_entry_count = 0

    for entry in manifest.entries:
        target_path = pdf_cache_path(entry.content_sha256, cache_dir=cache_dir)
        has_invalid_cache_entry = False
        if target_path.exists():
            try:
                cache_hash = _file_sha256(target_path)
            except OSError as e:
                errors.append(
                    f"{entry.label()} failed to validate existing cache entry "
                    f"{target_path}: {e}"
                )
                continue
            if cache_hash == entry.content_sha256:
                reused_count += 1
                continue
            has_invalid_cache_entry = True
            invalid_cache_entry_count += 1

        try:
            content = reader.read_bytes(entry.archive_uri)
        except ArchiveObjectReadError as e:
            errors.append(f"{entry.label()} fetch failed for {entry.archive_uri}: {e}")
            continue

        content_sha256 = hashlib.sha256(content).hexdigest()
        if content_sha256 != entry.content_sha256:
            errors.append(
                f"{entry.label()} hash mismatch for {entry.archive_uri}: "
                f"expected {entry.content_sha256}, got {content_sha256}"
            )
            continue

        try:
            _write_pdf_cache(target_path, content)
        except PdfCacheWriteError as e:
            errors.append(f"{entry.label()} cache write failed for {target_path}: {e}")
            continue

        if has_invalid_cache_entry:
            refreshed_count += 1
        else:
            downloaded_count += 1

    return PdfCacheResult(
        manifest_path=manifest.path,
        cache_dir=cache_dir,
        manifest_row_count=manifest.row_count,
        fetchable_row_count=len(manifest.entries),
        reused_count=reused_count,
        downloaded_count=downloaded_count,
        refreshed_count=refreshed_count,
        invalid_cache_entry_count=invalid_cache_entry_count,
        errors=tuple(errors),
    )


def _json_manifest_row(
    line: str, *, path: Path, line_number: int
) -> Mapping[str, object]:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError as e:
        raise PdfCacheInputError(
            f"{path}:{line_number} is not valid JSON: {e.msg}"
        ) from e
    if not isinstance(payload, Mapping):
        raise PdfCacheInputError(f"{path}:{line_number} must contain a JSON object")
    return cast(Mapping[str, object], payload)


def _source_pdf_entry(
    row: Mapping[str, object],
    *,
    line_number: int,
) -> tuple[SourcePdfEntry | None, tuple[str, ...]]:
    errors: list[str] = []
    content_sha256 = _required_manifest_text(
        row, "content_sha256", line_number=line_number
    )
    archive_uri = _required_manifest_text(row, "archive_uri", line_number=line_number)
    document_identity = _optional_manifest_text(row, "document_identity")

    if content_sha256 is None:
        errors.append(f"manifest row {line_number} missing content_sha256")
    elif not _SHA256_PATTERN.fullmatch(content_sha256):
        errors.append(
            f"manifest row {line_number} content_sha256 must be a lowercase "
            "SHA-256 hex digest"
        )

    if archive_uri is None:
        errors.append(f"manifest row {line_number} missing archive_uri")

    if errors:
        return None, tuple(errors)
    return (
        SourcePdfEntry(
            line_number=line_number,
            content_sha256=cast(str, content_sha256),
            archive_uri=cast(str, archive_uri),
            document_identity=document_identity,
        ),
        (),
    )


def _required_manifest_text(
    row: Mapping[str, object],
    key: str,
    *,
    line_number: int,
) -> str | None:
    value = row.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def _optional_manifest_text(row: Mapping[str, object], key: str) -> str | None:
    value = row.get(key)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(_READ_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _write_pdf_cache(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f"{path.name}.tmp")
    try:
        temporary_path.write_bytes(content)
        temporary_path.replace(path)
    except OSError as e:
        raise PdfCacheWriteError(str(e)) from e
    finally:
        temporary_path.unlink(missing_ok=True)
