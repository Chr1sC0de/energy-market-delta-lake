"""Silver document Markdown extraction from cached source PDFs."""

import hashlib
import json
import re
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from gas_market_knowledge_base.corpus_paths import (
    default_silver_documents_dir,
    default_source_manifest_path,
    display_path,
)
from gas_market_knowledge_base.pdf_cache import (
    default_pdf_cache_dir,
    pdf_cache_path,
)

EXTRACTION_SCHEMA_VERSION = 1
EXTRACTION_TOOL = "docling"
DEFAULT_MIN_TEXT_CHARS = 80

_SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
_READ_CHUNK_SIZE = 1024 * 1024
_FRONTMATTER_PREFIX = "---\n"
_FRONTMATTER_SUFFIX = "\n---\n"
_SOURCE_FRONTMATTER_FIELDS = (
    "schema_version",
    "document_identity",
    "content_sha256",
    "corpus_source",
    "document_family_id",
    "document_title",
    "document_kind",
    "document_version",
    "document_version_id",
    "published_date",
    "effective_date",
    "media_revision",
    "source_url",
    "resolved_url",
    "source_page_url",
    "source_page_title",
    "source_link_text",
    "archive_uri",
    "storage_uri",
    "target_s3_key",
    "content_length",
)


class SilverExtractionInputError(ValueError):
    """Raised when silver extraction input cannot be loaded."""


class SilverExtractionWriteError(ValueError):
    """Raised when a silver Markdown document cannot be written."""


class MarkdownExtractionError(ValueError):
    """Raised when a PDF cannot be converted to Markdown."""


class MarkdownExtractor(ABC):
    """Converts a source PDF file into Markdown text."""

    @abstractmethod
    def extract_markdown(self, pdf_path: Path) -> str:
        """Return extracted Markdown for one cached PDF."""


@dataclass(frozen=True, slots=True)
class SourceDocumentEntry:
    """Extraction-ready source document from the bronze manifest."""

    line_number: int
    row: Mapping[str, object]
    document_identity: str
    content_sha256: str
    pdf_path: Path
    output_path: Path

    def label(self) -> str:
        """Return a human-readable row label for reports."""
        return f"manifest row {self.line_number} ({self.document_identity})"


@dataclass(frozen=True, slots=True)
class SourceDocumentManifest:
    """Parsed document manifest rows plus row-level validation errors."""

    path: Path
    row_count: int
    entries: tuple[SourceDocumentEntry, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SilverDocumentExtractionResult:
    """Result of one silver document extraction run."""

    manifest_path: Path
    cache_dir: Path
    output_dir: Path
    manifest_row_count: int
    extractable_row_count: int
    extracted_count: int
    skipped_count: int
    errors: tuple[str, ...]

    @property
    def error_count(self) -> int:
        """Return the number of row-level extraction or validation errors."""
        return len(self.errors)


def extraction_settings(*, min_text_chars: int) -> dict[str, object]:
    """Return deterministic extraction settings for silver document Markdown."""
    if min_text_chars < 1:
        raise SilverExtractionInputError("min_text_chars must be at least 1")
    return {
        "schema_version": EXTRACTION_SCHEMA_VERSION,
        "tool": EXTRACTION_TOOL,
        "input_format": "pdf",
        "output_format": "markdown",
        "ocr_enabled": False,
        "table_structure_enabled": True,
        "min_text_chars": min_text_chars,
    }


def extraction_settings_sha256(settings: Mapping[str, object]) -> str:
    """Return the stable hash for extraction settings."""
    payload = json.dumps(settings, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def silver_document_path(
    document_identity: str,
    *,
    content_sha256: str,
    output_dir: Path,
) -> Path:
    """Return the deterministic silver Markdown path for one manifest row."""
    identity_parts = _document_identity_parts(document_identity)
    hash_part = f"sha256-{content_sha256}"
    if hash_part in identity_parts and identity_parts[-1] != hash_part:
        raise ValueError("document_identity hash component must be the final path part")
    if identity_parts[-1] != hash_part:
        identity_parts = (*identity_parts, hash_part)
    return output_dir.joinpath(*identity_parts).with_suffix(".md")


def load_source_document_manifest(
    path: Path,
    *,
    cache_dir: Path | None = None,
    output_dir: Path | None = None,
) -> SourceDocumentManifest:
    """Load extraction-ready document entries from a bronze source manifest."""
    effective_cache_dir = cache_dir or default_pdf_cache_dir()
    effective_output_dir = output_dir or default_silver_documents_dir()
    if not path.exists():
        raise SilverExtractionInputError(f"source manifest not found: {path}")

    rows: list[SourceDocumentEntry] = []
    seen_document_identities: set[str] = set()
    errors: list[str] = []
    row_count = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        raise SilverExtractionInputError(
            f"failed to read source manifest {path}: {e}"
        ) from e

    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        row_count += 1
        payload = _json_manifest_row(line, path=path, line_number=line_number)
        entry, row_errors = _source_document_entry(
            payload,
            line_number=line_number,
            cache_dir=effective_cache_dir,
            output_dir=effective_output_dir,
        )
        if entry is not None:
            if entry.document_identity in seen_document_identities:
                errors.extend(row_errors)
                continue
            seen_document_identities.add(entry.document_identity)
            rows.append(entry)
        errors.extend(row_errors)

    return SourceDocumentManifest(
        path=path,
        row_count=row_count,
        entries=tuple(rows),
        errors=tuple(errors),
    )


def extract_silver_documents(
    *,
    extractor: MarkdownExtractor,
    manifest_path: Path | None = None,
    cache_dir: Path | None = None,
    output_dir: Path | None = None,
    min_text_chars: int = DEFAULT_MIN_TEXT_CHARS,
) -> SilverDocumentExtractionResult:
    """Convert cached PDFs from the bronze manifest into silver Markdown."""
    effective_manifest_path = manifest_path or default_source_manifest_path()
    effective_cache_dir = cache_dir or default_pdf_cache_dir()
    effective_output_dir = output_dir or default_silver_documents_dir()
    settings = extraction_settings(min_text_chars=min_text_chars)
    settings_sha256 = extraction_settings_sha256(settings)
    manifest = load_source_document_manifest(
        effective_manifest_path,
        cache_dir=effective_cache_dir,
        output_dir=effective_output_dir,
    )

    errors = list(manifest.errors)
    extracted_count = 0
    skipped_count = 0
    for entry in manifest.entries:
        if _output_is_current(
            entry.output_path,
            content_sha256=entry.content_sha256,
            settings_sha256=settings_sha256,
        ):
            skipped_count += 1
            continue

        cache_error = _cache_validation_error(entry)
        if cache_error is not None:
            errors.append(cache_error)
            continue

        try:
            markdown = extractor.extract_markdown(entry.pdf_path)
        except MarkdownExtractionError as e:
            errors.append(
                f"{entry.label()} extraction failed for {entry.pdf_path}: {e}"
            )
            continue

        text_chars = _text_char_count(markdown)
        if text_chars < min_text_chars:
            errors.append(
                f"{entry.label()} extracted text below minimum from {entry.pdf_path}: "
                f"got {text_chars} text chars, expected at least {min_text_chars}; "
                "OCR fallback is out of scope for v1"
            )
            continue

        rendered_markdown = _render_document_markdown(
            entry,
            manifest_path=manifest.path,
            markdown=markdown,
            settings=settings,
            settings_sha256=settings_sha256,
        )
        try:
            _write_silver_document(entry.output_path, rendered_markdown)
        except SilverExtractionWriteError as e:
            errors.append(f"{entry.label()} write failed for {entry.output_path}: {e}")
            continue
        extracted_count += 1

    return SilverDocumentExtractionResult(
        manifest_path=manifest.path,
        cache_dir=effective_cache_dir,
        output_dir=effective_output_dir,
        manifest_row_count=manifest.row_count,
        extractable_row_count=len(manifest.entries),
        extracted_count=extracted_count,
        skipped_count=skipped_count,
        errors=tuple(errors),
    )


def _json_manifest_row(
    line: str, *, path: Path, line_number: int
) -> Mapping[str, object]:
    try:
        payload = json.loads(line)
    except json.JSONDecodeError as e:
        raise SilverExtractionInputError(
            f"{path}:{line_number} is not valid JSON: {e.msg}"
        ) from e
    if not isinstance(payload, Mapping):
        raise SilverExtractionInputError(
            f"{path}:{line_number} must contain a JSON object"
        )
    return cast(Mapping[str, object], payload)


def _source_document_entry(
    row: Mapping[str, object],
    *,
    line_number: int,
    cache_dir: Path,
    output_dir: Path,
) -> tuple[SourceDocumentEntry | None, tuple[str, ...]]:
    errors: list[str] = []
    content_sha256 = _required_manifest_text(
        row, "content_sha256", line_number=line_number
    )
    document_identity = _required_manifest_text(
        row, "document_identity", line_number=line_number
    )

    if content_sha256 is None:
        errors.append(f"manifest row {line_number} missing content_sha256")
    elif not _SHA256_PATTERN.fullmatch(content_sha256):
        errors.append(
            f"manifest row {line_number} content_sha256 must be a lowercase "
            "SHA-256 hex digest"
        )

    if document_identity is None:
        errors.append(f"manifest row {line_number} missing document_identity")

    if errors:
        return None, tuple(errors)

    checked_content_sha256 = cast(str, content_sha256)
    checked_document_identity = cast(str, document_identity)
    try:
        output_path = silver_document_path(
            checked_document_identity,
            content_sha256=checked_content_sha256,
            output_dir=output_dir,
        )
    except ValueError as e:
        return None, (f"manifest row {line_number} invalid document_identity: {e}",)

    return (
        SourceDocumentEntry(
            line_number=line_number,
            row=row,
            document_identity=checked_document_identity,
            content_sha256=checked_content_sha256,
            pdf_path=pdf_cache_path(checked_content_sha256, cache_dir=cache_dir),
            output_path=output_path,
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


def _document_identity_parts(document_identity: str) -> tuple[str, ...]:
    parts = tuple(document_identity.split("/"))
    if not parts:
        raise ValueError("document_identity must be a relative path")
    for part in parts:
        if part in {"", ".", ".."}:
            raise ValueError(
                "document_identity must not contain empty, dot, or dot-dot parts"
            )
        if "\\" in part:
            raise ValueError("document_identity must use forward slashes")
    return parts


def _cache_validation_error(entry: SourceDocumentEntry) -> str | None:
    if not entry.pdf_path.exists():
        return f"{entry.label()} cached PDF missing: {entry.pdf_path}"
    try:
        cache_hash = _file_sha256(entry.pdf_path)
    except OSError as e:
        return f"{entry.label()} failed to hash cached PDF {entry.pdf_path}: {e}"
    if cache_hash != entry.content_sha256:
        return (
            f"{entry.label()} cached PDF hash mismatch for {entry.pdf_path}: "
            f"expected {entry.content_sha256}, got {cache_hash}"
        )
    return None


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(_READ_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _text_char_count(markdown: str) -> int:
    return len(re.sub(r"\s+", "", markdown))


def _output_is_current(
    path: Path,
    *,
    content_sha256: str,
    settings_sha256: str,
) -> bool:
    frontmatter = _read_frontmatter(path)
    if frontmatter is None:
        return False
    return (
        frontmatter.get("content_sha256") == content_sha256
        and frontmatter.get("extraction_settings_sha256") == settings_sha256
    )


def _read_frontmatter(path: Path) -> Mapping[str, object] | None:
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not text.startswith(_FRONTMATTER_PREFIX):
        return None
    end_index = text.find(_FRONTMATTER_SUFFIX, len(_FRONTMATTER_PREFIX))
    if end_index == -1:
        return None
    payload_text = text[len(_FRONTMATTER_PREFIX) : end_index].strip()
    if not payload_text:
        return None
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, Mapping):
        return None
    return cast(Mapping[str, object], payload)


def _render_document_markdown(
    entry: SourceDocumentEntry,
    *,
    manifest_path: Path,
    markdown: str,
    settings: Mapping[str, object],
    settings_sha256: str,
) -> str:
    frontmatter = _frontmatter_payload(
        entry,
        manifest_path=manifest_path,
        settings=settings,
        settings_sha256=settings_sha256,
    )
    frontmatter_text = json.dumps(frontmatter, indent=2, sort_keys=True)
    body = markdown.strip()
    return f"---\n{frontmatter_text}\n---\n\n{body}\n"


def _frontmatter_payload(
    entry: SourceDocumentEntry,
    *,
    manifest_path: Path,
    settings: Mapping[str, object],
    settings_sha256: str,
) -> dict[str, object]:
    source_fields = {
        field: _frontmatter_value(entry.row.get(field))
        for field in _SOURCE_FRONTMATTER_FIELDS
        if field in entry.row
    }
    return {
        "schema_version": EXTRACTION_SCHEMA_VERSION,
        "document_identity": entry.document_identity,
        "content_sha256": entry.content_sha256,
        "generated_path": _display_path(entry.output_path),
        "extraction_tool": EXTRACTION_TOOL,
        "extraction_settings": dict(settings),
        "extraction_settings_sha256": settings_sha256,
        "source_manifest": {
            "path": _display_path(manifest_path),
            "line_number": entry.line_number,
        },
        "source": source_fields,
    }


def _frontmatter_value(value: object) -> object:
    if value is None or isinstance(value, str | int | bool | float):
        return value
    if isinstance(value, Mapping):
        return {
            str(key): _frontmatter_value(nested_value)
            for key, nested_value in value.items()
        }
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return [_frontmatter_value(item) for item in value]
    return str(value)


def _display_path(path: Path) -> str:
    return display_path(path)


def _write_silver_document(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f"{path.name}.tmp")
    try:
        temporary_path.write_text(content, encoding="utf-8")
        temporary_path.replace(path)
    except OSError as e:
        raise SilverExtractionWriteError(str(e)) from e
    finally:
        temporary_path.unlink(missing_ok=True)
