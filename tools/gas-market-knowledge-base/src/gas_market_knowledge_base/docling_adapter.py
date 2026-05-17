"""Docling adapter for silver document Markdown extraction."""

from collections.abc import Sequence
from pathlib import Path
from typing import cast

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import (
    DocumentConverter,
    PdfFormatOption,
)

from gas_market_knowledge_base.silver_documents import (
    MarkdownExtractionError,
    MarkdownExtractor,
)


class DoclingMarkdownExtractor(MarkdownExtractor):
    """Convert cached PDFs to Markdown with Docling and OCR disabled."""

    def __init__(self) -> None:
        pipeline_options = PdfPipelineOptions(
            do_ocr=False,
            do_table_structure=True,
        )
        self._converter = DocumentConverter(
            allowed_formats=[InputFormat.PDF],
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            },
        )

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


def _result_error_summary(errors: Sequence[object]) -> str:
    if not errors:
        return "no detail returned"
    return "; ".join(str(error) for error in errors)
