"""Docling adapters for silver document extraction and chunking."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Protocol, cast

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
)

from gas_market_knowledge_base.silver_chunks import (
    ExtractedHybridChunk,
    HybridChunkExtractionError,
    HybridChunkExtractor,
)
from gas_market_knowledge_base.silver_documents import (
    MarkdownExtractionError,
    MarkdownExtractor,
)


class _ChunkMeta(Protocol):
    def export_json_dict(self) -> Mapping[str, object]:
        """Return Docling chunk metadata in JSON-ready form."""


class _DoclingChunk(Protocol):
    text: str
    meta: _ChunkMeta


class DoclingMarkdownExtractor(MarkdownExtractor):
    """Convert cached PDFs to Markdown with Docling and OCR disabled."""

    def __init__(self) -> None:
        self._converter = _document_converter()

    def extract_markdown(self, pdf_path: Path) -> str:
        """Return Docling Markdown for one cached PDF."""
        try:
            result = self._converter.convert(pdf_path, raises_on_error=False)
        except Exception as e:
            raise MarkdownExtractionError(str(e)) from e

        if result.status != ConversionStatus.SUCCESS:
            raise MarkdownExtractionError(
                f"Docling status {result.status.value}; "
                f"{_result_error_summary(result.errors)}"
            )

        try:
            return cast(str, result.document.export_to_markdown())
        except Exception as e:
            raise MarkdownExtractionError(
                f"failed to export Docling document to Markdown: {e}"
            ) from e


class DoclingHybridChunkExtractor(HybridChunkExtractor):
    """Convert cached PDFs to Docling Hybrid chunks with OCR disabled."""

    def __init__(self) -> None:
        self._converter = _document_converter()
        try:
            from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
        except Exception as e:
            raise HybridChunkExtractionError(
                "failed to initialise Docling HybridChunker"
            ) from e
        self._chunker = HybridChunker()

    def extract_chunks(self, pdf_path: Path) -> tuple[ExtractedHybridChunk, ...]:
        """Return Docling Hybrid chunks for one cached PDF."""
        try:
            result = self._converter.convert(pdf_path, raises_on_error=False)
        except Exception as e:
            raise HybridChunkExtractionError(str(e)) from e

        if result.status != ConversionStatus.SUCCESS:
            raise HybridChunkExtractionError(
                f"Docling status {result.status.value}; "
                f"{_result_error_summary(result.errors)}"
            )

        try:
            raw_chunks = self._chunker.chunk(result.document)
        except Exception as e:
            raise HybridChunkExtractionError(
                f"failed to run Docling HybridChunker: {e}"
            ) from e

        return tuple(
            _extracted_hybrid_chunk(cast(_DoclingChunk, chunk)) for chunk in raw_chunks
        )


def _document_converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions(
        do_ocr=False,
        do_table_structure=True,
    )
    return DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        },
    )


def _extracted_hybrid_chunk(chunk: _DoclingChunk) -> ExtractedHybridChunk:
    text = chunk.text
    meta_json = _chunk_meta_json(chunk)
    return ExtractedHybridChunk(
        text=text,
        heading_path=_string_tuple(meta_json.get("headings")),
        doc_items=_doc_item_tuple(meta_json.get("doc_items")),
    )


def _chunk_meta_json(chunk: _DoclingChunk) -> Mapping[str, object]:
    meta = chunk.meta
    return meta.export_json_dict()


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return ()
    return tuple(str(item) for item in value if str(item).strip())


def _doc_item_tuple(value: object) -> tuple[Mapping[str, object], ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return ()
    doc_items: list[Mapping[str, object]] = []
    for item in value:
        if isinstance(item, Mapping):
            doc_items.append(cast(Mapping[str, object], item))
    return tuple(doc_items)


def _result_error_summary(errors: Sequence[object]) -> str:
    if not errors:
        return "no detail returned"
    return "; ".join(str(error) for error in errors)
