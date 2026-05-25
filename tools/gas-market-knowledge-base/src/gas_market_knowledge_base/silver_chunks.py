"""Silver Docling Hybrid chunks and retrieval index generation."""

import hashlib
import json
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from gas_market_knowledge_base.pdf_cache import default_pdf_cache_dir
from gas_market_knowledge_base.silver_documents import (
    DEFAULT_MIN_TEXT_CHARS,
    SourceDocumentEntry,
    default_silver_documents_dir,
    extraction_settings,
    extraction_settings_sha256,
    load_source_document_manifest,
)
from gas_market_knowledge_base.source_manifest import (
    default_source_manifest_path,
    subproject_root,
)

SILVER_CHUNKS_RELATIVE_PATH = Path("generated/silver/chunks")
SILVER_INDEX_RELATIVE_PATH = Path("generated/silver/index/chunks.jsonl")
CHUNK_SCHEMA_VERSION = 1
CHUNKING_TOOL = "docling-hybrid"

_FRONTMATTER_PREFIX = "---\n"
_FRONTMATTER_SUFFIX = "\n---\n"
_READ_CHUNK_SIZE = 1024 * 1024
_REQUIRED_INDEX_FIELDS = frozenset(
    {
        "schema_version",
        "chunk_id",
        "chunk_ordinal",
        "path",
        "document_identity",
        "content_sha256",
        "document_title",
        "corpus",
        "document_family_id",
        "source_document_markdown_path",
        "heading_path",
        "chunk_text_sha256",
        "extraction_settings_sha256",
        "chunking_settings_sha256",
        "citations",
    }
)
_REQUIRED_CHUNK_FRONTMATTER_FIELDS = _REQUIRED_INDEX_FIELDS | {
    "generated_path",
    "document_family",
    "chunking_tool",
    "chunking_settings",
}
_REQUIRED_CITATION_FIELDS = frozenset(
    {
        "source_document_markdown_path",
        "source_manifest_path",
        "source_manifest_line_number",
        "source_url",
        "doc_items",
    }
)


class SilverChunkInputError(ValueError):
    """Raised when chunk or index input cannot be loaded."""


class SilverChunkWriteError(ValueError):
    """Raised when generated chunk or index files cannot be written."""


class HybridChunkExtractionError(ValueError):
    """Raised when Docling Hybrid chunks cannot be extracted."""


class HybridChunkExtractor(ABC):
    """Extract Docling Hybrid chunks from one cached PDF."""

    @abstractmethod
    def extract_chunks(self, pdf_path: Path) -> tuple["ExtractedHybridChunk", ...]:
        """Return chunk text and structural metadata for one cached PDF."""


@dataclass(frozen=True, slots=True)
class ExtractedHybridChunk:
    """One chunk returned by Docling Hybrid chunking."""

    text: str
    heading_path: tuple[str, ...] = ()
    doc_items: tuple[Mapping[str, object], ...] = ()


@dataclass(frozen=True, slots=True)
class SilverChunkBuildResult:
    """Result of one silver chunk/index build."""

    manifest_path: Path
    document_dir: Path
    chunk_dir: Path
    index_path: Path
    manifest_row_count: int
    source_document_count: int
    chunk_count: int
    errors: tuple[str, ...]

    @property
    def error_count(self) -> int:
        """Return the number of build errors."""
        return len(self.errors)


@dataclass(frozen=True, slots=True)
class SilverIndexValidationResult:
    """Result of one silver chunk/index validation."""

    manifest_path: Path
    document_dir: Path
    chunk_dir: Path
    index_path: Path
    manifest_row_count: int
    index_row_count: int
    chunk_file_count: int
    errors: tuple[str, ...]

    @property
    def error_count(self) -> int:
        """Return the number of validation errors."""
        return len(self.errors)


@dataclass(frozen=True, slots=True)
class _SourceChunkMetadata:
    document_title: str
    corpus: str
    document_family_id: str
    source_url: str
    source_page_url: str | None


@dataclass(frozen=True, slots=True)
class _RenderedChunk:
    chunk_id: str
    path: Path
    markdown: str
    index_row: dict[str, object]


def default_silver_chunks_dir() -> Path:
    """Return the default silver chunk Markdown output directory."""
    return subproject_root() / SILVER_CHUNKS_RELATIVE_PATH


def default_silver_index_path() -> Path:
    """Return the default silver chunk index JSONL path."""
    return subproject_root() / SILVER_INDEX_RELATIVE_PATH


def chunking_settings() -> dict[str, object]:
    """Return deterministic Docling Hybrid chunk settings."""
    return {
        "schema_version": CHUNK_SCHEMA_VERSION,
        "tool": CHUNKING_TOOL,
        "chunker": "HybridChunker",
        "merge_peers": True,
        "repeat_table_header": True,
        "omit_header_on_overflow": False,
    }


def chunking_settings_sha256(settings: Mapping[str, object]) -> str:
    """Return the stable hash for chunking settings."""
    payload = json.dumps(settings, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_silver_index(
    *,
    extractor: HybridChunkExtractor,
    manifest_path: Path = default_source_manifest_path(),
    cache_dir: Path = default_pdf_cache_dir(),
    document_dir: Path = default_silver_documents_dir(),
    chunk_dir: Path = default_silver_chunks_dir(),
    index_path: Path = default_silver_index_path(),
    min_text_chars: int = DEFAULT_MIN_TEXT_CHARS,
) -> SilverChunkBuildResult:
    """Build silver chunk Markdown and the global chunk index."""
    extraction_config = extraction_settings(min_text_chars=min_text_chars)
    extraction_config_sha256 = extraction_settings_sha256(extraction_config)
    chunking_config = chunking_settings()
    chunking_config_sha256 = chunking_settings_sha256(chunking_config)
    manifest = load_source_document_manifest(
        manifest_path,
        cache_dir=cache_dir,
        output_dir=document_dir,
    )

    errors = list(manifest.errors)
    rendered_chunks: list[_RenderedChunk] = []
    if not errors:
        for entry in manifest.entries:
            errors.extend(
                _source_document_errors(
                    entry,
                    extraction_settings_sha=extraction_config_sha256,
                )
            )
            errors.extend(_cached_pdf_errors(entry))
            source_metadata, source_errors = _source_chunk_metadata(entry)
            errors.extend(source_errors)
            if source_metadata is None:
                continue
            if errors:
                continue

            try:
                extracted_chunks = extractor.extract_chunks(entry.pdf_path)
            except HybridChunkExtractionError as e:
                errors.append(
                    f"{entry.label()} Hybrid chunk extraction failed for "
                    f"{entry.pdf_path}: {e}"
                )
                continue
            if not extracted_chunks:
                errors.append(f"{entry.label()} produced no Hybrid chunks")
                continue

            document_chunks = _render_chunks(
                entry,
                extracted_chunks,
                source_metadata=source_metadata,
                manifest_path=manifest.path,
                chunk_dir=chunk_dir,
                extraction_settings_sha=extraction_config_sha256,
                chunking_config=chunking_config,
                chunking_settings_sha=chunking_config_sha256,
            )
            if not document_chunks:
                errors.append(f"{entry.label()} produced no non-empty Hybrid chunks")
                continue
            rendered_chunks.extend(document_chunks)

    if errors:
        return SilverChunkBuildResult(
            manifest_path=manifest.path,
            document_dir=document_dir,
            chunk_dir=chunk_dir,
            index_path=index_path,
            manifest_row_count=manifest.row_count,
            source_document_count=len(manifest.entries),
            chunk_count=0,
            errors=tuple(errors),
        )

    try:
        _write_chunks_and_index(
            rendered_chunks,
            chunk_dir=chunk_dir,
            index_path=index_path,
        )
    except SilverChunkWriteError as e:
        errors.append(str(e))

    return SilverChunkBuildResult(
        manifest_path=manifest.path,
        document_dir=document_dir,
        chunk_dir=chunk_dir,
        index_path=index_path,
        manifest_row_count=manifest.row_count,
        source_document_count=len(manifest.entries),
        chunk_count=len(rendered_chunks),
        errors=tuple(errors),
    )


def validate_silver_index(
    *,
    manifest_path: Path = default_source_manifest_path(),
    document_dir: Path = default_silver_documents_dir(),
    chunk_dir: Path = default_silver_chunks_dir(),
    index_path: Path = default_silver_index_path(),
    min_text_chars: int = DEFAULT_MIN_TEXT_CHARS,
) -> SilverIndexValidationResult:
    """Validate silver chunk Markdown and chunk index consistency."""
    extraction_config = extraction_settings(min_text_chars=min_text_chars)
    extraction_config_sha256 = extraction_settings_sha256(extraction_config)
    manifest = load_source_document_manifest(
        manifest_path,
        output_dir=document_dir,
    )

    errors = list(manifest.errors)
    expected_document_identities: set[str] = set()
    for entry in manifest.entries:
        expected_document_identities.add(entry.document_identity)
        errors.extend(
            _source_document_errors(
                entry,
                extraction_settings_sha=extraction_config_sha256,
            )
        )

    index_rows, index_errors = _load_index_rows(index_path)
    errors.extend(index_errors)
    chunk_file_paths = _chunk_file_paths(chunk_dir)
    referenced_chunk_paths: set[Path] = set()
    discovered_index_rows: list[dict[str, object]] = []
    chunk_ids: dict[str, Path] = {}
    indexed_document_identities: set[str] = set()

    for row_number, row in enumerate(index_rows, 1):
        row_errors = _index_row_errors(row, row_number=row_number)
        errors.extend(row_errors)

        chunk_id = _optional_text(row, "chunk_id")
        if chunk_id is not None:
            if chunk_id in chunk_ids:
                errors.append(
                    f"{index_path}:{row_number} duplicate chunk_id {chunk_id!r}; "
                    f"first seen at {chunk_ids[chunk_id]}"
                )
            else:
                row_path = _path_from_display(_optional_text(row, "path") or "")
                chunk_ids[chunk_id] = row_path

        document_identity = _optional_text(row, "document_identity")
        if document_identity is not None:
            indexed_document_identities.add(document_identity)

        path_text = _optional_text(row, "path")
        if path_text is None:
            continue
        chunk_path = _path_from_display(path_text)
        referenced_chunk_paths.add(chunk_path.resolve())
        frontmatter, body, read_errors = _read_markdown_frontmatter(chunk_path)
        errors.extend(read_errors)
        if frontmatter is None:
            continue

        errors.extend(_chunk_frontmatter_errors(frontmatter, path=chunk_path))
        errors.extend(_chunk_body_errors(frontmatter, body=body, path=chunk_path))
        if chunk_id is not None and frontmatter.get("chunk_id") != chunk_id:
            errors.append(
                f"{chunk_path} chunk_id {frontmatter.get('chunk_id')!r} does "
                f"not match index row {chunk_id!r}"
            )
        if _REQUIRED_INDEX_FIELDS.issubset(frontmatter):
            expected_row = _index_row_from_frontmatter(frontmatter)
            if expected_row != row:
                errors.append(f"{index_path}:{row_number} is stale for {chunk_path}")
            discovered_index_rows.append(expected_row)

    for chunk_path in chunk_file_paths:
        if chunk_path.resolve() not in referenced_chunk_paths:
            errors.append(f"stale chunk file not referenced by index: {chunk_path}")

    missing_document_identities = (
        expected_document_identities - indexed_document_identities
    )
    for document_identity in sorted(missing_document_identities):
        errors.append(f"missing index rows for source document {document_identity}")

    duplicate_frontmatter_errors = _duplicate_chunk_frontmatter_errors(chunk_file_paths)
    errors.extend(duplicate_frontmatter_errors)

    if index_path.exists() and discovered_index_rows:
        expected_index_text = _dump_jsonl(
            sorted(
                discovered_index_rows,
                key=lambda row: (
                    str(row["document_identity"]),
                    int(row["chunk_ordinal"]),
                    str(row["chunk_id"]),
                ),
            )
        )
        actual_index_text = index_path.read_text(encoding="utf-8")
        if actual_index_text != expected_index_text:
            errors.append(f"{index_path} is stale; run gas-market-kb build-index")

    return SilverIndexValidationResult(
        manifest_path=manifest.path,
        document_dir=document_dir,
        chunk_dir=chunk_dir,
        index_path=index_path,
        manifest_row_count=manifest.row_count,
        index_row_count=len(index_rows),
        chunk_file_count=len(chunk_file_paths),
        errors=tuple(errors),
    )


def _source_document_errors(
    entry: SourceDocumentEntry,
    *,
    extraction_settings_sha: str,
) -> list[str]:
    frontmatter, _, read_errors = _read_markdown_frontmatter(entry.output_path)
    if read_errors:
        if not entry.output_path.exists():
            return [f"{entry.label()} source document missing: {entry.output_path}"]
        return [f"{entry.label()} source document {error}" for error in read_errors]
    if frontmatter is None:
        return [f"{entry.label()} source document missing frontmatter"]

    errors: list[str] = []
    if frontmatter.get("content_sha256") != entry.content_sha256:
        errors.append(
            f"{entry.label()} source document stale content_sha256 in "
            f"{entry.output_path}"
        )
    if frontmatter.get("document_identity") != entry.document_identity:
        errors.append(
            f"{entry.label()} source document has mismatched document_identity "
            f"in {entry.output_path}"
        )
    if frontmatter.get("extraction_settings_sha256") != extraction_settings_sha:
        errors.append(
            f"{entry.label()} source document stale extraction settings in "
            f"{entry.output_path}"
        )
    return errors


def _cached_pdf_errors(entry: SourceDocumentEntry) -> list[str]:
    if not entry.pdf_path.exists():
        return [f"{entry.label()} cached PDF missing: {entry.pdf_path}"]
    try:
        cache_hash = _file_sha256(entry.pdf_path)
    except OSError as e:
        return [f"{entry.label()} failed to hash cached PDF {entry.pdf_path}: {e}"]
    if cache_hash != entry.content_sha256:
        return [
            f"{entry.label()} cached PDF hash mismatch for {entry.pdf_path}: "
            f"expected {entry.content_sha256}, got {cache_hash}"
        ]
    return []


def _source_chunk_metadata(
    entry: SourceDocumentEntry,
) -> tuple[_SourceChunkMetadata | None, list[str]]:
    errors: list[str] = []
    document_title = _required_text(entry.row, "document_title")
    corpus = _required_text(entry.row, "corpus_source")
    document_family_id = _required_text(entry.row, "document_family_id")
    source_url = _required_text(entry.row, "source_url")
    source_page_url = _optional_text(entry.row, "source_page_url")
    if document_title is None:
        errors.append(f"{entry.label()} missing document_title")
    if corpus is None:
        errors.append(f"{entry.label()} missing corpus_source")
    if document_family_id is None:
        errors.append(f"{entry.label()} missing document_family_id")
    if source_url is None:
        errors.append(f"{entry.label()} missing source_url")
    if errors:
        return None, errors
    return (
        _SourceChunkMetadata(
            document_title=cast(str, document_title),
            corpus=cast(str, corpus),
            document_family_id=cast(str, document_family_id),
            source_url=cast(str, source_url),
            source_page_url=source_page_url,
        ),
        [],
    )


def _render_chunks(
    entry: SourceDocumentEntry,
    chunks: Sequence[ExtractedHybridChunk],
    *,
    source_metadata: _SourceChunkMetadata,
    manifest_path: Path,
    chunk_dir: Path,
    extraction_settings_sha: str,
    chunking_config: Mapping[str, object],
    chunking_settings_sha: str,
) -> list[_RenderedChunk]:
    rendered_chunks: list[_RenderedChunk] = []
    chunk_id_counts: dict[str, int] = {}
    for chunk_ordinal, chunk in enumerate(chunks):
        text = _normalize_chunk_text(chunk.text)
        if not text:
            continue
        chunk_id_base = _chunk_id_base(
            entry,
            text=text,
            extraction_settings_sha=extraction_settings_sha,
        )
        occurrence = chunk_id_counts.get(chunk_id_base, 0) + 1
        chunk_id_counts[chunk_id_base] = occurrence
        chunk_id = chunk_id_base if occurrence == 1 else f"{chunk_id_base}-{occurrence}"
        chunk_path = _chunk_markdown_path(
            entry.document_identity,
            chunk_id=chunk_id,
            chunk_dir=chunk_dir,
        )
        frontmatter = _chunk_frontmatter(
            entry,
            chunk,
            chunk_id=chunk_id,
            chunk_ordinal=chunk_ordinal,
            chunk_path=chunk_path,
            text=text,
            source_metadata=source_metadata,
            manifest_path=manifest_path,
            extraction_settings_sha=extraction_settings_sha,
            chunking_config=chunking_config,
            chunking_settings_sha=chunking_settings_sha,
        )
        markdown = _render_markdown(frontmatter, text)
        rendered_chunks.append(
            _RenderedChunk(
                chunk_id=chunk_id,
                path=chunk_path,
                markdown=markdown,
                index_row=_index_row_from_frontmatter(frontmatter),
            )
        )
    return rendered_chunks


def _chunk_id_base(
    entry: SourceDocumentEntry,
    *,
    text: str,
    extraction_settings_sha: str,
) -> str:
    payload = {
        "content_sha256": entry.content_sha256,
        "document_identity": entry.document_identity,
        "extraction_settings_sha256": extraction_settings_sha,
        "chunk_text_sha256": _text_sha256(text),
        "chunk_content": text,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return f"chunk-{digest[:24]}"


def _chunk_frontmatter(
    entry: SourceDocumentEntry,
    chunk: ExtractedHybridChunk,
    *,
    chunk_id: str,
    chunk_ordinal: int,
    chunk_path: Path,
    text: str,
    source_metadata: _SourceChunkMetadata,
    manifest_path: Path,
    extraction_settings_sha: str,
    chunking_config: Mapping[str, object],
    chunking_settings_sha: str,
) -> dict[str, object]:
    source_document_path = _display_path(entry.output_path)
    doc_items = [_jsonable_mapping(item) for item in chunk.doc_items]
    citations = {
        "source_document_markdown_path": source_document_path,
        "source_manifest_path": _display_path(manifest_path),
        "source_manifest_line_number": entry.line_number,
        "source_url": source_metadata.source_url,
        "source_page_url": source_metadata.source_page_url,
        "doc_items": doc_items,
    }
    return {
        "schema_version": CHUNK_SCHEMA_VERSION,
        "chunk_id": chunk_id,
        "chunk_ordinal": chunk_ordinal,
        "generated_path": _display_path(chunk_path),
        "path": _display_path(chunk_path),
        "document_identity": entry.document_identity,
        "content_sha256": entry.content_sha256,
        "document_title": source_metadata.document_title,
        "corpus": source_metadata.corpus,
        "document_family": source_metadata.document_family_id,
        "document_family_id": source_metadata.document_family_id,
        "source_document_markdown_path": source_document_path,
        "heading_path": list(chunk.heading_path),
        "chunk_text_sha256": _text_sha256(text),
        "chunking_tool": CHUNKING_TOOL,
        "chunking_settings": dict(chunking_config),
        "chunking_settings_sha256": chunking_settings_sha,
        "extraction_settings_sha256": extraction_settings_sha,
        "citations": citations,
    }


def _index_row_from_frontmatter(frontmatter: Mapping[str, object]) -> dict[str, object]:
    return {
        "schema_version": frontmatter["schema_version"],
        "chunk_id": frontmatter["chunk_id"],
        "chunk_ordinal": frontmatter["chunk_ordinal"],
        "path": frontmatter["path"],
        "document_identity": frontmatter["document_identity"],
        "content_sha256": frontmatter["content_sha256"],
        "document_title": frontmatter["document_title"],
        "corpus": frontmatter["corpus"],
        "document_family_id": frontmatter["document_family_id"],
        "source_document_markdown_path": frontmatter["source_document_markdown_path"],
        "heading_path": frontmatter["heading_path"],
        "chunk_text_sha256": frontmatter["chunk_text_sha256"],
        "extraction_settings_sha256": frontmatter["extraction_settings_sha256"],
        "chunking_settings_sha256": frontmatter["chunking_settings_sha256"],
        "citations": frontmatter["citations"],
    }


def _write_chunks_and_index(
    rendered_chunks: Sequence[_RenderedChunk],
    *,
    chunk_dir: Path,
    index_path: Path,
) -> None:
    expected_paths = {chunk.path.resolve() for chunk in rendered_chunks}
    if chunk_dir.exists():
        for path in sorted(chunk_dir.rglob("*.md")):
            if path.resolve() not in expected_paths:
                try:
                    path.unlink()
                except OSError as e:
                    raise SilverChunkWriteError(
                        f"failed to remove stale chunk file {path}: {e}"
                    ) from e

    for chunk in rendered_chunks:
        _write_text_atomic(chunk.path, chunk.markdown)

    index_rows = sorted(
        (chunk.index_row for chunk in rendered_chunks),
        key=lambda row: (
            str(row["document_identity"]),
            int(row["chunk_ordinal"]),
            str(row["chunk_id"]),
        ),
    )
    _write_text_atomic(index_path, _dump_jsonl(index_rows))


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_name(f"{path.name}.tmp")
    try:
        temporary_path.write_text(content, encoding="utf-8")
        temporary_path.replace(path)
    except OSError as e:
        raise SilverChunkWriteError(f"failed to write {path}: {e}") from e
    finally:
        temporary_path.unlink(missing_ok=True)


def _load_index_rows(path: Path) -> tuple[list[Mapping[str, object]], list[str]]:
    if not path.exists():
        return [], [f"chunk index missing: {path}"]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        raise SilverChunkInputError(f"failed to read chunk index {path}: {e}") from e

    rows: list[Mapping[str, object]] = []
    errors: list[str] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"{path}:{line_number} is not valid JSON: {e.msg}")
            continue
        if not isinstance(payload, Mapping):
            errors.append(f"{path}:{line_number} must contain a JSON object")
            continue
        rows.append(cast(Mapping[str, object], payload))
    return rows, errors


def _index_row_errors(row: Mapping[str, object], *, row_number: int) -> list[str]:
    errors: list[str] = []
    missing_fields = sorted(
        field for field in _REQUIRED_INDEX_FIELDS if field not in row
    )
    if missing_fields:
        errors.append(
            f"index row {row_number} missing required fields: "
            f"{', '.join(missing_fields)}"
        )
    if _optional_text(row, "chunk_id") is None:
        errors.append(f"index row {row_number} missing chunk_id")
    if _optional_text(row, "path") is None:
        errors.append(f"index row {row_number} missing path")
    citations = row.get("citations")
    if not isinstance(citations, Mapping):
        errors.append(f"index row {row_number} missing citations metadata")
    return errors


def _chunk_frontmatter_errors(
    frontmatter: Mapping[str, object],
    *,
    path: Path,
) -> list[str]:
    errors: list[str] = []
    missing_fields = sorted(
        field
        for field in _REQUIRED_CHUNK_FRONTMATTER_FIELDS
        if field not in frontmatter
    )
    if missing_fields:
        errors.append(
            f"{path} malformed frontmatter missing required fields: "
            f"{', '.join(missing_fields)}"
        )
    citations = frontmatter.get("citations")
    if not isinstance(citations, Mapping):
        errors.append(f"{path} missing citations metadata")
        return errors
    missing_citation_fields = sorted(
        field for field in _REQUIRED_CITATION_FIELDS if field not in citations
    )
    if missing_citation_fields:
        errors.append(
            f"{path} citations metadata missing required fields: "
            f"{', '.join(missing_citation_fields)}"
        )
    source_doc = _optional_text(citations, "source_document_markdown_path")
    if source_doc is None:
        errors.append(f"{path} citations metadata missing source document target")
    else:
        source_doc_path = _path_from_display(source_doc)
        if not source_doc_path.exists():
            errors.append(f"{path} source document target missing: {source_doc_path}")
    if not isinstance(citations.get("doc_items"), Sequence):
        errors.append(f"{path} citations metadata missing doc_items")
    return errors


def _chunk_body_errors(
    frontmatter: Mapping[str, object],
    *,
    body: str,
    path: Path,
) -> list[str]:
    expected_hash = _optional_text(frontmatter, "chunk_text_sha256")
    if expected_hash is None:
        return []
    actual_hash = _text_sha256(body.strip())
    if actual_hash != expected_hash:
        return [
            f"{path} body hash mismatch: expected {expected_hash}, got {actual_hash}"
        ]
    return []


def _duplicate_chunk_frontmatter_errors(chunk_file_paths: Sequence[Path]) -> list[str]:
    errors: list[str] = []
    chunk_ids: dict[str, Path] = {}
    for path in chunk_file_paths:
        frontmatter, _, read_errors = _read_markdown_frontmatter(path)
        if read_errors or frontmatter is None:
            continue
        chunk_id = _optional_text(frontmatter, "chunk_id")
        if chunk_id is None:
            continue
        if chunk_id in chunk_ids:
            errors.append(
                f"duplicate chunk_id {chunk_id!r} in {path}; "
                f"first seen at {chunk_ids[chunk_id]}"
            )
        else:
            chunk_ids[chunk_id] = path
    return errors


def _read_markdown_frontmatter(
    path: Path,
) -> tuple[Mapping[str, object] | None, str, list[str]]:
    if not path.exists():
        return None, "", [f"missing document target: {path}"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise SilverChunkInputError(f"failed to read {path}: {e}") from e
    if not text.startswith(_FRONTMATTER_PREFIX):
        return None, "", [f"malformed frontmatter in {path}: missing opening marker"]
    end_index = text.find(_FRONTMATTER_SUFFIX, len(_FRONTMATTER_PREFIX))
    if end_index == -1:
        return None, "", [f"malformed frontmatter in {path}: missing closing marker"]
    payload_text = text[len(_FRONTMATTER_PREFIX) : end_index].strip()
    if not payload_text:
        return None, "", [f"malformed frontmatter in {path}: empty payload"]
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as e:
        return None, "", [f"malformed frontmatter in {path}: {e.msg}"]
    if not isinstance(payload, Mapping):
        return None, "", [f"malformed frontmatter in {path}: expected JSON object"]
    body = text[end_index + len(_FRONTMATTER_SUFFIX) :]
    return cast(Mapping[str, object], payload), body, []


def _chunk_file_paths(chunk_dir: Path) -> list[Path]:
    if not chunk_dir.exists():
        return []
    return sorted(path for path in chunk_dir.rglob("*.md") if path.is_file())


def _chunk_markdown_path(
    document_identity: str,
    *,
    chunk_id: str,
    chunk_dir: Path,
) -> Path:
    return chunk_dir.joinpath(
        *_document_identity_parts(document_identity),
        chunk_id,
    ).with_suffix(".md")


def _document_identity_parts(document_identity: str) -> tuple[str, ...]:
    parts = tuple(document_identity.split("/"))
    if not parts:
        raise SilverChunkInputError("document_identity must be a relative path")
    for part in parts:
        if part in {"", ".", ".."}:
            raise SilverChunkInputError(
                "document_identity must not contain empty, dot, or dot-dot parts"
            )
        if "\\" in part:
            raise SilverChunkInputError("document_identity must use forward slashes")
    return parts


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(_READ_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _normalize_chunk_text(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""
    return "\n".join(line.rstrip() for line in stripped.splitlines())


def _render_markdown(frontmatter: Mapping[str, object], body: str) -> str:
    frontmatter_text = json.dumps(frontmatter, indent=2, sort_keys=True)
    return f"---\n{frontmatter_text}\n---\n\n{body.strip()}\n"


def _dump_jsonl(rows: Sequence[Mapping[str, object]]) -> str:
    if not rows:
        return ""
    lines = [json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows]
    return f"{'\n'.join(lines)}\n"


def _required_text(row: Mapping[str, object], key: str) -> str | None:
    value = row.get(key)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def _optional_text(row: Mapping[str, object], key: str) -> str | None:
    return _required_text(row, key)


def _jsonable_mapping(row: Mapping[str, object]) -> dict[str, object]:
    return {str(key): _jsonable_value(value) for key, value in row.items()}


def _jsonable_value(value: object) -> object:
    if value is None or isinstance(value, str | int | bool | float):
        return value
    if isinstance(value, Mapping):
        return {str(key): _jsonable_value(nested) for key, nested in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return [_jsonable_value(item) for item in value]
    return str(value)


def _display_path(path: Path) -> str:
    resolved_path = path.resolve()
    root = subproject_root().resolve()
    if resolved_path.is_relative_to(root):
        return resolved_path.relative_to(root).as_posix()
    return path.as_posix()


def _path_from_display(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return subproject_root() / path
