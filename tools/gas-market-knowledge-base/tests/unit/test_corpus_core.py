import hashlib
import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

from gas_market_knowledge_base.corpus_core.gold_context import (
    GoldSourceCitation,
    render_gold_glossary_body,
    render_gold_markdown_page,
    validate_gold_context,
)
from gas_market_knowledge_base.corpus_core.manifest import (
    SourceManifestRow,
    document_identity,
    dump_source_manifest_jsonl,
)
from gas_market_knowledge_base.corpus_core.paths import (
    CorpusArtifactLayout,
    source_pdf_cache_path,
)
from gas_market_knowledge_base.corpus_core.silver_chunks import (
    ExtractedHybridChunk,
    HybridChunkExtractor,
    build_silver_index,
    validate_silver_index,
)
from gas_market_knowledge_base.corpus_core.silver_documents import (
    MarkdownExtractor,
    extract_silver_documents,
)


class FakeMarkdownExtractor(MarkdownExtractor):
    def extract_markdown(self, pdf_path: Path) -> str:
        return "# Publication\n\nThis shared core fixture has enough text to extract."


class FakeHybridChunkExtractor(HybridChunkExtractor):
    def extract_chunks(self, pdf_path: Path) -> tuple[ExtractedHybridChunk, ...]:
        return (
            ExtractedHybridChunk(
                text="Publication definition evidence with retrieval context.",
                heading_path=("Publication", "Definition"),
                doc_items=({"self_ref": "#/texts/1", "label": "text"},),
            ),
        )


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _index_rows(index_path: Path) -> list[Mapping[str, object]]:
    return [
        cast(Mapping[str, object], json.loads(line))
        for line in index_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _write_gold_fixture(
    layout: CorpusArtifactLayout,
    *,
    chunk_id: str,
    chunk_path: Path,
    source_document_path: Path,
    source_hash: str,
) -> None:
    glossary_index_path = layout.gold_dir / "glossary" / "README.md"
    page_path = layout.gold_dir / "glossary" / "publication.md"
    chunk_link = f"../../{chunk_path.relative_to(layout.corpus_dir).as_posix()}"
    source_document_link = (
        f"../../{source_document_path.relative_to(layout.corpus_dir).as_posix()}"
    )
    citation = GoldSourceCitation(
        chunk_id=chunk_id,
        chunk_path=chunk_link,
        source_document_path=source_document_link,
        source_hash=source_hash,
    )

    glossary_index_path.parent.mkdir(parents=True, exist_ok=True)
    glossary_index_path.write_text(
        render_gold_markdown_page(
            frontmatter={
                "schema_version": 1,
                "context_type": "glossary-index",
                "title": "Glossary",
                "generated_path": layout.display_path(glossary_index_path),
            },
            body="# Glossary\n\n- [Publication](publication.md)\n",
        ),
        encoding="utf-8",
    )
    page_path.write_text(
        render_gold_markdown_page(
            frontmatter={
                "schema_version": 1,
                "context_type": "glossary-page",
                "title": "Publication",
                "slug": "publication",
                "generated_path": layout.display_path(page_path),
                "source_chunk_ids": [chunk_id],
                "source_hashes": [source_hash],
                "related_concepts": [],
            },
            body=render_gold_glossary_body(
                title="Publication",
                definition=(
                    "A publication is backed by cited source text. "
                    f"[[chunk:{chunk_id}]] [[source:sha256:{source_hash}]]"
                ),
                source_citations=[citation],
            ),
        ),
        encoding="utf-8",
    )


def test_shared_core_builds_non_gas_corpus_flow(tmp_path: Path) -> None:
    layout = CorpusArtifactLayout(
        root=tmp_path / "corpora",
        corpus_name="aemo-publications",
        display_root=tmp_path,
    )
    cache_dir = tmp_path / ".cache" / "pdfs"
    pdf_content = b"%PDF-1.7\nshared core fixture\n"
    content_sha256 = _sha256(pdf_content)
    identity = document_identity(
        corpus_source="Major Publications",
        document_family_id="2026 ISP / Inputs",
        content_sha256=content_sha256,
    )
    manifest_row = SourceManifestRow(
        document_identity=identity,
        content_sha256=content_sha256,
        corpus_source="major-publications",
        document_family_id="2026-isp-inputs",
        document_title="2026 ISP Inputs",
        source_url="https://www.aemo.com.au/publications/isp-inputs.pdf",
        archive_uri="s3://archive/publications/isp-inputs.pdf",
        generated_paths=layout.generated_paths(identity),
        content_length=len(pdf_content),
    )
    cached_pdf_path = source_pdf_cache_path(content_sha256, cache_dir=cache_dir)
    cached_pdf_path.parent.mkdir(parents=True)
    cached_pdf_path.write_bytes(pdf_content)
    layout.source_manifest_path.parent.mkdir(parents=True)
    layout.source_manifest_path.write_text(
        dump_source_manifest_jsonl([manifest_row.as_dict()]),
        encoding="utf-8",
    )

    document_result = extract_silver_documents(
        extractor=FakeMarkdownExtractor(),
        manifest_path=layout.source_manifest_path,
        cache_dir=cache_dir,
        output_dir=layout.silver_documents_dir,
        min_text_chars=20,
        display_path=layout.display_path,
    )
    build_result = build_silver_index(
        extractor=FakeHybridChunkExtractor(),
        manifest_path=layout.source_manifest_path,
        cache_dir=cache_dir,
        document_dir=layout.silver_documents_dir,
        chunk_dir=layout.silver_chunks_dir,
        index_path=layout.silver_index_path,
        min_text_chars=20,
        display_path=layout.display_path,
    )
    validation_result = validate_silver_index(
        manifest_path=layout.source_manifest_path,
        cache_dir=cache_dir,
        document_dir=layout.silver_documents_dir,
        chunk_dir=layout.silver_chunks_dir,
        index_path=layout.silver_index_path,
        min_text_chars=20,
        resolve_display_path=layout.path_from_display,
    )

    rows = _index_rows(layout.silver_index_path)
    chunk_path = layout.path_from_display(cast(str, rows[0]["path"]))
    source_document_path = layout.path_from_display(
        cast(str, rows[0]["source_document_markdown_path"])
    )
    _write_gold_fixture(
        layout,
        chunk_id=cast(str, rows[0]["chunk_id"]),
        chunk_path=chunk_path,
        source_document_path=source_document_path,
        source_hash=content_sha256,
    )
    gold_result = validate_gold_context(
        gold_dir=layout.gold_dir,
        index_path=layout.silver_index_path,
        display_path=layout.display_path,
        resolve_display_path=layout.path_from_display,
    )

    assert identity.startswith("major-publications/2026-isp-inputs/")
    assert document_result.error_count == 0
    assert build_result.error_count == 0
    assert validation_result.error_count == 0
    assert gold_result.error_count == 0
    assert (
        "aemo-publications/silver/index/chunks.jsonl"
        in layout.generated_paths(identity)["silver_chunk_index"]
    )
