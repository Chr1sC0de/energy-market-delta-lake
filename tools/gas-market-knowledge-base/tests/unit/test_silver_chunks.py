import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import pytest
from click.testing import CliRunner

from gas_market_knowledge_base import cli as cli_module
from gas_market_knowledge_base.cli import main
from gas_market_knowledge_base.silver_chunks import (
    ExtractedHybridChunk,
    HybridChunkExtractor,
    build_silver_index,
    validate_silver_index,
)
from gas_market_knowledge_base.silver_documents import (
    MarkdownExtractor,
    extract_silver_documents,
)

EXTRACTED_MARKDOWN = """
# Gas Guide

This fixture extraction has enough text for the silver document validation
threshold. It represents Docling Markdown without invoking the Docling runtime
inside the Unit test lane.
"""

HYBRID_CHUNKS = (
    ExtractedHybridChunk(
        text="Gas Guide overview chunk with enough retrieval text.",
        heading_path=("Gas Guide", "Overview"),
        doc_items=(
            {
                "self_ref": "#/texts/1",
                "label": "text",
                "prov": [{"page_no": 1, "bbox": {"l": 1, "t": 2, "r": 3, "b": 4}}],
            },
        ),
    ),
    ExtractedHybridChunk(
        text="Gas Guide rules chunk with citation context.",
        heading_path=("Gas Guide", "Rules"),
        doc_items=({"self_ref": "#/texts/2", "label": "text"},),
    ),
)


class FakeMarkdownExtractor(MarkdownExtractor):
    def extract_markdown(self, pdf_path: Path) -> str:
        return EXTRACTED_MARKDOWN


class FakeHybridChunkExtractor(HybridChunkExtractor):
    def __init__(
        self, chunks: tuple[ExtractedHybridChunk, ...] = HYBRID_CHUNKS
    ) -> None:
        self._chunks = chunks
        self.requests: list[Path] = []

    def extract_chunks(self, pdf_path: Path) -> tuple[ExtractedHybridChunk, ...]:
        self.requests.append(pdf_path)
        return self._chunks


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


def _rewrite_frontmatter(path: Path, frontmatter: Mapping[str, object]) -> None:
    text = path.read_text(encoding="utf-8")
    end_index = text.find("\n---\n", len("---\n"))
    body = text[end_index + len("\n---\n") :]
    path.write_text(
        f"---\n{json.dumps(frontmatter, indent=2, sort_keys=True)}\n---\n{body}",
        encoding="utf-8",
    )


def _index_rows(index_path: Path) -> list[Mapping[str, object]]:
    return [
        cast(Mapping[str, object], json.loads(line))
        for line in index_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _build_fixture(
    tmp_path: Path,
    *,
    extractor: FakeHybridChunkExtractor | None = None,
) -> tuple[Path, Path, Path, Path, FakeHybridChunkExtractor]:
    pdf_content = b"%PDF-1.7\nfixture pdf bytes\n"
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    document_dir = tmp_path / "generated" / "silver" / "documents"
    chunk_dir = tmp_path / "generated" / "silver" / "chunks"
    index_path = tmp_path / "generated" / "silver" / "index" / "chunks.jsonl"
    _write_cached_pdf(cache_dir, pdf_content)
    _write_manifest(manifest_path, [_manifest_row(pdf_content)])
    extract_result = extract_silver_documents(
        extractor=FakeMarkdownExtractor(),
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        output_dir=document_dir,
        min_text_chars=20,
    )
    assert extract_result.error_count == 0
    chunk_extractor = extractor or FakeHybridChunkExtractor()

    build_result = build_silver_index(
        extractor=chunk_extractor,
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        document_dir=document_dir,
        chunk_dir=chunk_dir,
        index_path=index_path,
        min_text_chars=20,
    )

    assert build_result.error_count == 0
    return manifest_path, document_dir, chunk_dir, index_path, chunk_extractor


def test_build_index_writes_stable_chunk_markdown_and_jsonl_index(
    tmp_path: Path,
) -> None:
    manifest_path, document_dir, chunk_dir, index_path, extractor = _build_fixture(
        tmp_path
    )
    first_index_text = index_path.read_text(encoding="utf-8")
    first_rows = _index_rows(index_path)
    first_chunk_path = Path(cast(str, first_rows[0]["path"]))
    first_frontmatter = _frontmatter(first_chunk_path)

    second_result = build_silver_index(
        extractor=extractor,
        manifest_path=manifest_path,
        cache_dir=tmp_path / ".cache" / "pdfs",
        document_dir=document_dir,
        chunk_dir=chunk_dir,
        index_path=index_path,
        min_text_chars=20,
    )

    assert second_result.error_count == 0
    assert second_result.chunk_count == 2
    assert index_path.read_text(encoding="utf-8") == first_index_text
    assert len(extractor.requests) == 2
    assert first_frontmatter["chunk_id"] == first_rows[0]["chunk_id"]
    assert first_frontmatter["content_sha256"] == first_rows[0]["content_sha256"]
    assert first_frontmatter["document_title"] == "Gas Guide"
    assert first_frontmatter["corpus"] == "gbb"
    assert first_frontmatter["document_family"] == "gas-guide"
    assert first_frontmatter["heading_path"] == ["Gas Guide", "Overview"]
    assert first_frontmatter["source_document_markdown_path"] == cast(
        str, first_rows[0]["source_document_markdown_path"]
    )
    citations = first_frontmatter["citations"]
    assert isinstance(citations, dict)
    assert citations["source_url"] == "https://www.aemo.com.au/media/gas-guide.pdf"
    assert (
        citations["source_document_markdown_path"]
        == first_frontmatter["source_document_markdown_path"]
    )
    assert first_chunk_path.read_text(encoding="utf-8").endswith(
        "Gas Guide overview chunk with enough retrieval text.\n"
    )


def test_validate_silver_index_accepts_current_build(tmp_path: Path) -> None:
    manifest_path, document_dir, chunk_dir, index_path, _ = _build_fixture(tmp_path)

    result = validate_silver_index(
        manifest_path=manifest_path,
        document_dir=document_dir,
        chunk_dir=chunk_dir,
        index_path=index_path,
        min_text_chars=20,
    )

    assert result.error_count == 0
    assert result.index_row_count == 2
    assert result.chunk_file_count == 2


def test_validate_reports_missing_chunk_target(tmp_path: Path) -> None:
    manifest_path, document_dir, chunk_dir, index_path, _ = _build_fixture(tmp_path)
    first_chunk_path = Path(cast(str, _index_rows(index_path)[0]["path"]))
    first_chunk_path.unlink()

    result = validate_silver_index(
        manifest_path=manifest_path,
        document_dir=document_dir,
        chunk_dir=chunk_dir,
        index_path=index_path,
        min_text_chars=20,
    )

    assert result.error_count >= 1
    assert any("missing document target" in error for error in result.errors)


def test_validate_reports_duplicate_chunk_ids(tmp_path: Path) -> None:
    manifest_path, document_dir, chunk_dir, index_path, _ = _build_fixture(tmp_path)
    first_line = index_path.read_text(encoding="utf-8").splitlines()[0]
    with index_path.open("a", encoding="utf-8") as file:
        file.write(f"{first_line}\n")

    result = validate_silver_index(
        manifest_path=manifest_path,
        document_dir=document_dir,
        chunk_dir=chunk_dir,
        index_path=index_path,
        min_text_chars=20,
    )

    assert any("duplicate chunk_id" in error for error in result.errors)


def test_validate_reports_missing_citations_metadata(tmp_path: Path) -> None:
    manifest_path, document_dir, chunk_dir, index_path, _ = _build_fixture(tmp_path)
    first_chunk_path = Path(cast(str, _index_rows(index_path)[0]["path"]))
    frontmatter = dict(_frontmatter(first_chunk_path))
    del frontmatter["citations"]
    _rewrite_frontmatter(first_chunk_path, frontmatter)

    result = validate_silver_index(
        manifest_path=manifest_path,
        document_dir=document_dir,
        chunk_dir=chunk_dir,
        index_path=index_path,
        min_text_chars=20,
    )

    assert any("missing citations metadata" in error for error in result.errors)


def test_validate_reports_stale_index_rows(tmp_path: Path) -> None:
    manifest_path, document_dir, chunk_dir, index_path, _ = _build_fixture(tmp_path)
    rows = [dict(row) for row in _index_rows(index_path)]
    rows[0]["document_title"] = "Outdated title"
    index_path.write_text(
        "".join(
            f"{json.dumps(row, sort_keys=True, separators=(',', ':'))}\n"
            for row in rows
        ),
        encoding="utf-8",
    )

    result = validate_silver_index(
        manifest_path=manifest_path,
        document_dir=document_dir,
        chunk_dir=chunk_dir,
        index_path=index_path,
        min_text_chars=20,
    )

    assert any("stale" in error for error in result.errors)


def test_build_index_and_validate_commands_use_fixture_chunker(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pdf_content = b"%PDF-1.7\nfixture pdf bytes\n"
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    document_dir = tmp_path / "generated" / "silver" / "documents"
    chunk_dir = tmp_path / "generated" / "silver" / "chunks"
    index_path = tmp_path / "generated" / "silver" / "index" / "chunks.jsonl"
    _write_cached_pdf(cache_dir, pdf_content)
    _write_manifest(manifest_path, [_manifest_row(pdf_content)])
    extract_result = extract_silver_documents(
        extractor=FakeMarkdownExtractor(),
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        output_dir=document_dir,
        min_text_chars=20,
    )
    assert extract_result.error_count == 0
    monkeypatch.setattr(
        cli_module,
        "_default_hybrid_chunk_extractor",
        lambda: FakeHybridChunkExtractor(),
    )

    build_result = CliRunner().invoke(
        main,
        [
            "build-index",
            "--manifest-path",
            str(manifest_path),
            "--cache-dir",
            str(cache_dir),
            "--document-dir",
            str(document_dir),
            "--chunk-dir",
            str(chunk_dir),
            "--index-path",
            str(index_path),
            "--min-text-chars",
            "20",
        ],
    )
    validate_result = CliRunner().invoke(
        main,
        [
            "validate",
            "--manifest-path",
            str(manifest_path),
            "--document-dir",
            str(document_dir),
            "--chunk-dir",
            str(chunk_dir),
            "--index-path",
            str(index_path),
            "--min-text-chars",
            "20",
        ],
    )

    assert build_result.exit_code == 0, build_result.output
    assert "wrote silver chunk index" in build_result.output
    assert "chunks=2" in build_result.output
    assert validate_result.exit_code == 0, validate_result.output
    assert "validated silver chunk index" in validate_result.output
