import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import pytest

from gas_market_knowledge_base.docling_adapter import DoclingMarkdownExtractor
from gas_market_knowledge_base.silver_documents import extract_silver_documents

pytestmark = pytest.mark.docling_adapter

DOCLING_PDF_LINES = (
    "Docling durable fixture gas market extraction.",
    "Silver path should extract this known PDF text.",
    "Known marker DOC01386 durable adapter coverage.",
)
DOCLING_MARKER_TEXT = "Known marker DOC01386 durable adapter coverage."


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _generated_pdf(text_lines: tuple[str, ...]) -> bytes:
    stream = (
        "BT\n/F1 12 Tf\n14 TL\n72 720 Td\n"
        + "\n".join(f"({_pdf_literal_text(line)}) Tj\nT*" for line in text_lines)
        + "\nET\n"
    ).encode("ascii")
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n",
        b"5 0 obj\n<< /Length "
        + str(len(stream)).encode("ascii")
        + b" >>\nstream\n"
        + stream
        + b"endstream\nendobj\n",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for item in objects:
        offsets.append(len(pdf))
        pdf.extend(item)

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(pdf)


def _pdf_literal_text(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _manifest_row(pdf_content: bytes, **overrides: object) -> dict[str, object]:
    content_sha256 = _sha256(pdf_content)
    row: dict[str, object] = {
        "schema_version": 1,
        "document_identity": f"gbb/gas-guide/sha256-{content_sha256}",
        "content_sha256": content_sha256,
        "corpus_source": "gbb",
        "document_family_id": "gas-guide",
        "document_title": "Gas Guide",
        "document_kind": "guide",
        "document_version": "v1",
        "document_version_id": "a" * 64,
        "published_date": "2026-01-02",
        "effective_date": "2026-01-01",
        "media_revision": "rev-a",
        "source_url": "https://www.aemo.com.au/media/gas-guide.pdf",
        "resolved_url": "https://www.aemo.com.au/media/gas-guide.pdf",
        "source_page_url": "https://www.aemo.com.au/gas/gbb",
        "source_page_title": "GBB procedures and guides",
        "source_link_text": "Gas Guide v1",
        "archive_uri": "s3://dev-energy-market-archive/bronze/aemo_gas_documents/base.pdf",
        "storage_uri": "s3://dev-energy-market-archive/bronze/aemo_gas_documents/base.pdf",
        "target_s3_key": "bronze/aemo_gas_documents/base.pdf",
        "content_length": len(pdf_content),
    }
    row.update(overrides)
    return row


def _write_manifest(path: Path, rows: list[Mapping[str, object]]) -> None:
    path.write_text(
        "".join(f"{json.dumps(row, sort_keys=True)}\n" for row in rows),
        encoding="utf-8",
    )


def _write_cached_pdf(cache_dir: Path, pdf_content: bytes) -> None:
    content_sha256 = _sha256(pdf_content)
    pdf_path = cache_dir / f"{content_sha256}.pdf"
    pdf_path.parent.mkdir(parents=True)
    pdf_path.write_bytes(pdf_content)


def _frontmatter(path: Path) -> Mapping[str, object]:
    text = path.read_text(encoding="utf-8")
    end_index = text.find("\n---\n", len("---\n"))
    return cast(Mapping[str, object], json.loads(text[len("---\n") : end_index]))


def test_extract_silver_uses_docling_adapter_with_generated_pdf(
    tmp_path: Path,
) -> None:
    pdf_content = _generated_pdf(DOCLING_PDF_LINES)
    content_sha256 = _sha256(pdf_content)
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    output_dir = tmp_path / "generated" / "silver" / "documents"
    _write_cached_pdf(cache_dir, pdf_content)
    _write_manifest(manifest_path, [_manifest_row(pdf_content)])

    result = extract_silver_documents(
        extractor=DoclingMarkdownExtractor(),
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        output_dir=output_dir,
        min_text_chars=20,
    )

    output_path = output_dir / "gbb" / "gas-guide" / f"sha256-{content_sha256}.md"
    rendered_markdown = output_path.read_text(encoding="utf-8")
    body = rendered_markdown.split("\n---\n\n", maxsplit=1)[1]
    frontmatter = _frontmatter(output_path)
    assert result.extracted_count == 1
    assert result.skipped_count == 0
    assert result.error_count == 0
    assert "Docling durable fixture gas market extraction." in body
    assert DOCLING_MARKER_TEXT in body
    assert frontmatter["content_sha256"] == content_sha256
    assert frontmatter["document_identity"] == f"gbb/gas-guide/sha256-{content_sha256}"
    assert frontmatter["extraction_tool"] == "docling"
    settings = frontmatter["extraction_settings"]
    assert isinstance(settings, dict)
    assert settings["tool"] == "docling"
    assert settings["ocr_enabled"] is False
    assert settings["table_structure_enabled"] is True
    assert settings["min_text_chars"] == 20
    source = frontmatter["source"]
    assert isinstance(source, dict)
    assert source["document_title"] == "Gas Guide"
