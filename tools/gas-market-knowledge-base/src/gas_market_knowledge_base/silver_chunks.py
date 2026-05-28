"""Gas corpus silver chunk and retrieval index defaults."""

from collections.abc import Mapping
from pathlib import Path

from gas_market_knowledge_base.corpus_core import silver_chunks as _core
from gas_market_knowledge_base.corpus_paths import (
    default_silver_chunks_dir,
    default_silver_documents_dir,
    default_silver_index_path,
    default_source_manifest_path,
    display_path,
    path_from_display,
)
from gas_market_knowledge_base.pdf_cache import default_pdf_cache_dir
from gas_market_knowledge_base.silver_documents import DEFAULT_MIN_TEXT_CHARS

ExtractedHybridChunk = _core.ExtractedHybridChunk
HybridChunkExtractionError = _core.HybridChunkExtractionError
HybridChunkExtractor = _core.HybridChunkExtractor
SilverChunkBuildResult = _core.SilverChunkBuildResult
SilverChunkInputError = _core.SilverChunkInputError
SilverChunkWriteError = _core.SilverChunkWriteError
SilverIndexValidationResult = _core.SilverIndexValidationResult


def chunking_settings() -> dict[str, object]:
    """Return deterministic Docling Hybrid chunk settings."""
    return _core.chunking_settings()


def chunking_settings_sha256(settings: Mapping[str, object]) -> str:
    """Return the stable hash for chunking settings."""
    return _core.chunking_settings_sha256(settings)


def build_silver_index(
    *,
    extractor: HybridChunkExtractor,
    manifest_path: Path | None = None,
    cache_dir: Path | None = None,
    document_dir: Path | None = None,
    chunk_dir: Path | None = None,
    index_path: Path | None = None,
    min_text_chars: int = DEFAULT_MIN_TEXT_CHARS,
) -> SilverChunkBuildResult:
    """Build silver chunk Markdown and the global chunk index."""
    return _core.build_silver_index(
        extractor=extractor,
        manifest_path=manifest_path or default_source_manifest_path(),
        cache_dir=cache_dir or default_pdf_cache_dir(),
        document_dir=document_dir or default_silver_documents_dir(),
        chunk_dir=chunk_dir or default_silver_chunks_dir(),
        index_path=index_path or default_silver_index_path(),
        min_text_chars=min_text_chars,
        display_path=display_path,
    )


def validate_silver_index(
    *,
    manifest_path: Path | None = None,
    document_dir: Path | None = None,
    chunk_dir: Path | None = None,
    index_path: Path | None = None,
    min_text_chars: int = DEFAULT_MIN_TEXT_CHARS,
) -> SilverIndexValidationResult:
    """Validate silver chunk Markdown and chunk index consistency."""
    return _core.validate_silver_index(
        manifest_path=manifest_path or default_source_manifest_path(),
        cache_dir=default_pdf_cache_dir(),
        document_dir=document_dir or default_silver_documents_dir(),
        chunk_dir=chunk_dir or default_silver_chunks_dir(),
        index_path=index_path or default_silver_index_path(),
        min_text_chars=min_text_chars,
        resolve_display_path=path_from_display,
    )
