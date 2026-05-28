import json
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import pytest
from click.testing import CliRunner

from gas_market_knowledge_base.aemo_publications.cli import main
from gas_market_knowledge_base.aemo_publications.corpus_paths import (
    CORPUS_ROOT_ENV_VAR,
    default_corpus_paths,
)
from gas_market_knowledge_base.aemo_publications.fixture_corpus import (
    FIXTURE_CORPUS_SOURCE,
    build_fixture_corpus,
    build_fixture_manifest_rows,
    write_fixture_manifest,
)


def _jsonl_rows(path: Path) -> list[Mapping[str, object]]:
    return [
        cast(Mapping[str, object], json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _frontmatter(path: Path) -> Mapping[str, object]:
    text = path.read_text(encoding="utf-8")
    end_index = text.find("\n---\n", len("---\n"))
    return cast(Mapping[str, object], json.loads(text[len("---\n") : end_index]))


def test_aemo_publications_defaults_use_configured_corpus_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus_root = tmp_path / "corpora"
    monkeypatch.setenv(CORPUS_ROOT_ENV_VAR, str(corpus_root))

    paths = default_corpus_paths()

    assert paths.source_manifest_path == (
        corpus_root / "aemo-major-publications" / "bronze" / "source_manifest.jsonl"
    )
    assert paths.source_cache_dir == (
        corpus_root / "aemo-major-publications" / "bronze" / "fixture-pdfs"
    )
    assert paths.silver_documents_dir == (
        corpus_root / "aemo-major-publications" / "silver" / "documents"
    )
    assert paths.silver_chunks_dir == (
        corpus_root / "aemo-major-publications" / "silver" / "chunks"
    )
    assert paths.silver_index_path == (
        corpus_root / "aemo-major-publications" / "silver" / "index" / "chunks.jsonl"
    )
    assert paths.gold_dir == corpus_root / "aemo-major-publications" / "gold"


def test_aemo_publications_explicit_path_overrides_drive_generated_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(CORPUS_ROOT_ENV_VAR, str(tmp_path / "ignored-corpora"))
    paths = default_corpus_paths(
        artifact_root=tmp_path / "explicit-root",
        source_manifest_path=tmp_path / "bronze" / "manifest.jsonl",
        source_cache_dir=tmp_path / "bronze" / "source-cache",
        silver_documents_dir=tmp_path / "silver-documents",
        silver_chunks_dir=tmp_path / "silver-chunks",
        silver_index_path=tmp_path / "silver-index" / "chunks.jsonl",
        gold_dir=tmp_path / "gold-pages",
    )

    rows = build_fixture_manifest_rows(paths)
    generated_paths = rows[0]["generated_paths"]

    assert paths.source_manifest_path == tmp_path / "bronze" / "manifest.jsonl"
    assert isinstance(generated_paths, dict)
    assert str(generated_paths["silver_document_markdown"]).startswith(
        (tmp_path / "silver-documents").as_posix()
    )
    assert (
        generated_paths["silver_chunk_index"]
        == (tmp_path / "silver-index" / "chunks.jsonl").as_posix()
    )
    assert str(generated_paths["gold_context"]).startswith(
        (tmp_path / "gold-pages").as_posix()
    )


def test_fixture_manifest_conversion_uses_shared_manifest_shape(
    tmp_path: Path,
) -> None:
    paths = default_corpus_paths(artifact_root=tmp_path / "corpora")

    result = write_fixture_manifest(paths)

    rows = _jsonl_rows(paths.source_manifest_path)
    assert result.row_count == 2
    assert len(rows) == 2
    assert rows[0]["schema_version"] == 1
    assert rows[0]["corpus_source"] == FIXTURE_CORPUS_SOURCE
    assert str(rows[0]["document_identity"]).startswith(
        "aemo-major-publications/electricity-statement-of-opportunities/sha256-"
    )
    assert rows[0]["archive_uri"] == (
        "fixture://aemo-major-publications/"
        "2025-electricity-statement-of-opportunities-fixture.pdf"
    )
    assert rows[0]["generated_paths"] == paths.generated_paths(
        cast(str, rows[0]["document_identity"])
    )


def test_build_fixture_corpus_writes_silver_index_and_gold(
    tmp_path: Path,
) -> None:
    result = build_fixture_corpus(
        artifact_root=tmp_path / "corpora",
        min_text_chars=20,
    )

    index_rows = _jsonl_rows(result.paths.silver_index_path)
    first_source_doc_path = result.paths.layout.path_from_display(
        cast(str, index_rows[0]["source_document_markdown_path"])
    )
    first_gold_page = (
        result.paths.gold_dir / "glossary" / "electricity-statement-of-opportunities.md"
    )
    source_frontmatter = _frontmatter(first_source_doc_path)
    gold_frontmatter = _frontmatter(first_gold_page)
    gold_text = first_gold_page.read_text(encoding="utf-8")

    assert result.error_count == 0
    assert result.manifest_result.row_count == 2
    assert result.silver_document_result.extracted_count == 2
    assert result.silver_index_result.chunk_count == 2
    assert result.silver_validation_result.error_count == 0
    assert result.gold_validation_result.error_count == 0
    assert len(index_rows) == 2
    assert source_frontmatter["content_sha256"] == index_rows[0]["content_sha256"]
    assert gold_frontmatter["context_type"] == "glossary-page"
    assert gold_frontmatter["source_chunk_ids"] == [index_rows[0]["chunk_id"]]
    assert "\n## Source Citations\n\n- `chunk-" in gold_text
    assert "[[source:sha256:" in gold_text


def test_build_fixture_command_accepts_artifact_root_override(
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / "corpora"

    result = CliRunner().invoke(
        main,
        [
            "build-fixture",
            "--artifact-root",
            str(artifact_root),
            "--min-text-chars",
            "20",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "wrote fixture manifest" in result.output
    assert "summary: manifest_rows=2 silver_documents=2 chunks=2" in result.output
    assert (
        artifact_root / "aemo-major-publications" / "silver" / "index" / "chunks.jsonl"
    ).exists()


def test_aemo_publications_cli_help_mentions_artifact_root() -> None:
    result = CliRunner().invoke(main, ["build-fixture", "--help"])
    compact_output = result.output.replace("\n", "").replace(" ", "")

    assert result.exit_code == 0
    assert "ENERGY_MARKET_CORPUS_ROOT" in result.output
    assert "aemo-major-publications/bronze/source_manifest.jsonl" in compact_output
    assert "aemo-major-publications/silver/index/chunks.jsonl" in compact_output
    assert "aemo-major-publications/gold" in compact_output
