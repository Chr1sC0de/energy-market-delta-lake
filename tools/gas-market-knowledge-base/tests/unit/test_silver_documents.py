import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import pytest
from click.testing import CliRunner

from gas_market_knowledge_base import cli as cli_module
from gas_market_knowledge_base.cli import main
from gas_market_knowledge_base.corpus_paths import (
    CORPUS_ROOT_ENV_VAR,
    default_silver_documents_dir,
    default_source_manifest_path,
)
from gas_market_knowledge_base.silver_documents import (
    MarkdownExtractionError,
    MarkdownExtractor,
    extract_silver_documents,
    silver_document_path,
)

EXTRACTED_MARKDOWN = """
# Gas Guide

This fixture extraction has enough text for the silver document validation
threshold. It represents Docling Markdown without invoking the Docling runtime
inside the Unit test lane.
"""


class FakeMarkdownExtractor(MarkdownExtractor):
    def __init__(
        self,
        markdown: str = EXTRACTED_MARKDOWN,
        *,
        failures: set[Path] | None = None,
    ) -> None:
        self._markdown = markdown
        self._failures = failures or set()
        self.requests: list[Path] = []

    def extract_markdown(self, pdf_path: Path) -> str:
        self.requests.append(pdf_path)
        if pdf_path in self._failures:
            raise MarkdownExtractionError("fixture conversion failed")
        return self._markdown


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


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


def _write_cached_pdf(cache_dir: Path, pdf_content: bytes) -> Path:
    content_sha256 = _sha256(pdf_content)
    pdf_path = cache_dir / f"{content_sha256}.pdf"
    pdf_path.parent.mkdir(parents=True)
    pdf_path.write_bytes(pdf_content)
    return pdf_path


def _frontmatter(path: Path) -> Mapping[str, object]:
    text = path.read_text(encoding="utf-8")
    end_index = text.find("\n---\n", len("---\n"))
    return cast(Mapping[str, object], json.loads(text[len("---\n") : end_index]))


def test_silver_document_path_uses_identity_and_content_hash(tmp_path: Path) -> None:
    content_sha256 = "a" * 64

    assert (
        silver_document_path(
            "gbb/gas-guide",
            content_sha256=content_sha256,
            output_dir=tmp_path,
        )
        == tmp_path / "gbb" / "gas-guide" / f"sha256-{content_sha256}.md"
    )


def test_extract_silver_writes_markdown_with_stable_frontmatter(
    tmp_path: Path,
) -> None:
    pdf_content = b"%PDF-1.7\nfixture pdf bytes\n"
    content_sha256 = _sha256(pdf_content)
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    output_dir = tmp_path / "generated" / "silver" / "documents"
    pdf_path = _write_cached_pdf(cache_dir, pdf_content)
    _write_manifest(manifest_path, [_manifest_row(pdf_content)])
    extractor = FakeMarkdownExtractor()

    result = extract_silver_documents(
        extractor=extractor,
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        output_dir=output_dir,
        min_text_chars=20,
    )

    output_path = output_dir / "gbb" / "gas-guide" / f"sha256-{content_sha256}.md"
    frontmatter = _frontmatter(output_path)
    assert result.extracted_count == 1
    assert result.skipped_count == 0
    assert result.error_count == 0
    assert extractor.requests == [pdf_path]
    assert output_path.read_text(encoding="utf-8").endswith(
        "inside the Unit test lane.\n"
    )
    assert frontmatter["content_sha256"] == content_sha256
    assert frontmatter["document_identity"] == f"gbb/gas-guide/sha256-{content_sha256}"
    assert frontmatter["extraction_tool"] == "docling"
    settings = frontmatter["extraction_settings"]
    assert isinstance(settings, dict)
    assert settings["ocr_enabled"] is False
    assert settings["min_text_chars"] == 20
    source = frontmatter["source"]
    assert isinstance(source, dict)
    assert source["document_title"] == "Gas Guide"
    assert source["source_url"] == "https://www.aemo.com.au/media/gas-guide.pdf"
    source_manifest = frontmatter["source_manifest"]
    assert isinstance(source_manifest, dict)
    assert source_manifest["line_number"] == 1


def test_extract_silver_default_output_uses_corpus_root_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus_root = tmp_path / "corpora"
    pdf_content = b"%PDF-1.7\nfixture pdf bytes\n"
    content_sha256 = _sha256(pdf_content)
    monkeypatch.setenv(CORPUS_ROOT_ENV_VAR, str(corpus_root))
    manifest_path = default_source_manifest_path()
    manifest_path.parent.mkdir(parents=True)
    cache_dir = tmp_path / ".cache" / "pdfs"
    _write_cached_pdf(cache_dir, pdf_content)
    _write_manifest(manifest_path, [_manifest_row(pdf_content)])

    result = extract_silver_documents(
        extractor=FakeMarkdownExtractor(),
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        min_text_chars=20,
    )

    output_path = (
        default_silver_documents_dir()
        / "gbb"
        / "gas-guide"
        / f"sha256-{content_sha256}.md"
    )
    frontmatter = _frontmatter(output_path)
    source_manifest = frontmatter["source_manifest"]
    assert result.output_dir == default_silver_documents_dir()
    assert frontmatter["generated_path"] == output_path.as_posix()
    assert isinstance(source_manifest, dict)
    assert source_manifest["path"] == manifest_path.as_posix()


def test_extract_silver_skips_current_output_without_cached_pdf(
    tmp_path: Path,
) -> None:
    pdf_content = b"%PDF-1.7\nfixture pdf bytes\n"
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    output_dir = tmp_path / "generated" / "silver" / "documents"
    pdf_path = _write_cached_pdf(cache_dir, pdf_content)
    _write_manifest(manifest_path, [_manifest_row(pdf_content)])

    first_result = extract_silver_documents(
        extractor=FakeMarkdownExtractor(),
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        output_dir=output_dir,
        min_text_chars=20,
    )
    pdf_path.unlink()
    second_extractor = FakeMarkdownExtractor(markdown="this should not be used")

    second_result = extract_silver_documents(
        extractor=second_extractor,
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        output_dir=output_dir,
        min_text_chars=20,
    )

    assert first_result.extracted_count == 1
    assert second_result.extracted_count == 0
    assert second_result.skipped_count == 1
    assert second_result.error_count == 0
    assert second_extractor.requests == []


def test_extract_silver_coalesces_duplicate_document_identity_rows(
    tmp_path: Path,
) -> None:
    pdf_content = b"%PDF-1.7\nfixture pdf bytes\n"
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    output_dir = tmp_path / "generated" / "silver" / "documents"
    pdf_path = _write_cached_pdf(cache_dir, pdf_content)
    _write_manifest(
        manifest_path,
        [
            _manifest_row(pdf_content),
            _manifest_row(pdf_content),
        ],
    )
    extractor = FakeMarkdownExtractor()

    result = extract_silver_documents(
        extractor=extractor,
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        output_dir=output_dir,
        min_text_chars=20,
    )

    assert result.manifest_row_count == 2
    assert result.extractable_row_count == 1
    assert result.extracted_count == 1
    assert result.error_count == 0
    assert extractor.requests == [pdf_path]


def test_extract_silver_reports_low_text_without_writing_empty_page(
    tmp_path: Path,
) -> None:
    pdf_content = b"%PDF-1.7\nimage only fixture\n"
    content_sha256 = _sha256(pdf_content)
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    output_dir = tmp_path / "generated" / "silver" / "documents"
    _write_cached_pdf(cache_dir, pdf_content)
    _write_manifest(manifest_path, [_manifest_row(pdf_content)])

    result = extract_silver_documents(
        extractor=FakeMarkdownExtractor(markdown="tiny"),
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        output_dir=output_dir,
        min_text_chars=20,
    )

    output_path = output_dir / "gbb" / "gas-guide" / f"sha256-{content_sha256}.md"
    assert result.extracted_count == 0
    assert result.error_count == 1
    assert "extracted text below minimum" in result.errors[0]
    assert "OCR fallback is out of scope for v1" in result.errors[0]
    assert not output_path.exists()


def test_extract_silver_reports_cached_pdf_hash_mismatch(tmp_path: Path) -> None:
    expected_pdf_content = b"%PDF-1.7\nexpected fixture\n"
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    output_dir = tmp_path / "generated" / "silver" / "documents"
    content_sha256 = _sha256(expected_pdf_content)
    cache_dir.mkdir(parents=True)
    (cache_dir / f"{content_sha256}.pdf").write_bytes(b"%PDF-1.7\nwrong fixture\n")
    _write_manifest(manifest_path, [_manifest_row(expected_pdf_content)])
    extractor = FakeMarkdownExtractor()

    result = extract_silver_documents(
        extractor=extractor,
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        output_dir=output_dir,
        min_text_chars=20,
    )

    assert result.extracted_count == 0
    assert result.error_count == 1
    assert "cached PDF hash mismatch" in result.errors[0]
    assert extractor.requests == []


def test_extract_silver_command_uses_cached_pdf_fixture(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_content = b"%PDF-1.7\nfixture pdf bytes\n"
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    output_dir = tmp_path / "generated" / "silver" / "documents"
    _write_cached_pdf(cache_dir, pdf_content)
    _write_manifest(manifest_path, [_manifest_row(pdf_content)])
    extractor = FakeMarkdownExtractor()
    monkeypatch.setattr(
        cli_module,
        "_default_markdown_extractor",
        lambda: extractor,
    )

    result = CliRunner().invoke(
        main,
        [
            "extract-silver",
            "--manifest-path",
            str(manifest_path),
            "--cache-dir",
            str(cache_dir),
            "--output-dir",
            str(output_dir),
            "--min-text-chars",
            "20",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "wrote silver documents to" in result.output
    assert "extracted=1" in result.output
    assert "skipped=0" in result.output
    assert len(extractor.requests) == 1
