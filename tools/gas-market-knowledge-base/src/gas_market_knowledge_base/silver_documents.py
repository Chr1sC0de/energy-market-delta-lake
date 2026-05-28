"""Gas corpus silver document extraction defaults."""

from collections.abc import Mapping
from pathlib import Path

from gas_market_knowledge_base.corpus_core import silver_documents as _core
from gas_market_knowledge_base.corpus_paths import (
    default_silver_documents_dir,
    default_source_manifest_path,
    display_path,
)
from gas_market_knowledge_base.pdf_cache import default_pdf_cache_dir

DEFAULT_MIN_TEXT_CHARS = _core.DEFAULT_MIN_TEXT_CHARS
MarkdownExtractionError = _core.MarkdownExtractionError
MarkdownExtractor = _core.MarkdownExtractor
SilverDocumentExtractionResult = _core.SilverDocumentExtractionResult
SilverExtractionInputError = _core.SilverExtractionInputError
SilverExtractionWriteError = _core.SilverExtractionWriteError
SourceDocumentEntry = _core.SourceDocumentEntry
SourceDocumentManifest = _core.SourceDocumentManifest


def extraction_settings(*, min_text_chars: int) -> dict[str, object]:
    """Return deterministic extraction settings for silver document Markdown."""
    return _core.extraction_settings(min_text_chars=min_text_chars)


def extraction_settings_sha256(settings: Mapping[str, object]) -> str:
    """Return the stable hash for extraction settings."""
    return _core.extraction_settings_sha256(settings)


def silver_document_path(
    document_identity: str,
    *,
    content_sha256: str,
    output_dir: Path,
) -> Path:
    """Return the deterministic silver Markdown path for one manifest row."""
    return _core.silver_document_path(
        document_identity,
        content_sha256=content_sha256,
        output_dir=output_dir,
    )


def load_source_document_manifest(
    path: Path,
    *,
    cache_dir: Path | None = None,
    output_dir: Path | None = None,
) -> SourceDocumentManifest:
    """Load extraction-ready document entries from a bronze source manifest."""
    return _core.load_source_document_manifest(
        path,
        cache_dir=cache_dir or default_pdf_cache_dir(),
        output_dir=output_dir or default_silver_documents_dir(),
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
    return _core.extract_silver_documents(
        extractor=extractor,
        manifest_path=manifest_path or default_source_manifest_path(),
        cache_dir=cache_dir or default_pdf_cache_dir(),
        output_dir=output_dir or default_silver_documents_dir(),
        min_text_chars=min_text_chars,
        display_path=display_path,
    )
