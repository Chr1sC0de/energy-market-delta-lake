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
from gas_market_knowledge_base.aemo_publications.source_manifest import (
    build_aemo_publication_manifest_rows,
    write_aemo_publication_manifest,
)
from gas_market_knowledge_base.aemo_publications.validation import (
    validate_aemo_publications_corpus,
)
from gas_market_knowledge_base.corpus_core.silver_documents import (
    load_source_document_manifest,
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


def _write_frontmatter(path: Path, frontmatter: Mapping[str, object]) -> None:
    text = path.read_text(encoding="utf-8")
    end_index = text.find("\n---\n", len("---\n"))
    body = text[end_index + len("\n---\n") :]
    path.write_text(
        f"---\n{json.dumps(frontmatter, indent=2, sort_keys=True)}\n---\n{body}",
        encoding="utf-8",
    )


def _download_metadata_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "archive_storage_uri": (
            "s3://dev-energy-market-archive/bronze/aemo_major_publications/"
            f"{'a' * 64}.pdf"
        ),
        "content_length": 1234,
        "content_sha256": "a" * 64,
        "content_type": "application/pdf",
        "corpus_source": "major_publications",
        "document_family_id": "integrated-system-plan",
        "document_kind": "major-publication",
        "document_title": "Integrated System Plan",
        "document_version": "2026",
        "document_version_id": "a" * 64,
        "effective_date": "2026-01-15",
        "exclude_reason": None,
        "include_decision": "include",
        "media_revision": "rev-a",
        "published_date": "2026-01-15",
        "resolved_url": "https://www.aemo.com.au/media/isp.pdf",
        "source_content_hash": "row-a",
        "source_link_text": "2026 Integrated System Plan",
        "source_page_title": "Major publications",
        "source_page_url": (
            "https://www.aemo.com.au/energy-systems/major-publications/"
            "integrated-system-plan-isp"
        ),
        "source_url": "https://www.aemo.com.au/media/isp.pdf",
        "storage_uri": (
            "s3://dev-energy-market-archive/bronze/aemo_major_publications/"
            f"{'a' * 64}.pdf"
        ),
        "target_s3_key": f"bronze/aemo_major_publications/{'a' * 64}.pdf",
    }
    row.update(overrides)
    return row


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
    assert result.row_count == 4
    assert len(rows) == 4
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


def test_aemo_publications_downloaded_metadata_converts_supported_source_rows(
    tmp_path: Path,
) -> None:
    paths = default_corpus_paths(artifact_root=tmp_path / "corpora")
    library_hash = "b" * 64
    gsoo_hash = "c" * 64
    wa_gsoo_hash = "d" * 64

    rows, summary = build_aemo_publication_manifest_rows(
        [
            _download_metadata_row(),
            _download_metadata_row(
                content_sha256=library_hash,
                document_family_id="electricity-statement-of-opportunities",
                document_title="Electricity Statement of Opportunities",
                source_page_url="https://www.aemo.com.au/library/major-publications",
                source_url="https://www.aemo.com.au/media/esoo.pdf",
                resolved_url="https://www.aemo.com.au/media/esoo.pdf",
                archive_storage_uri=(
                    "s3://dev-energy-market-archive/bronze/"
                    f"aemo_major_publications/{library_hash}.pdf"
                ),
                storage_uri=(
                    "s3://dev-energy-market-archive/bronze/"
                    f"aemo_major_publications/{library_hash}.pdf"
                ),
                target_s3_key=f"bronze/aemo_major_publications/{library_hash}.pdf",
            ),
            _download_metadata_row(
                content_sha256=gsoo_hash,
                corpus_source="gsoo",
                document_family_id="gsoo__gas-statement-of-opportunities",
                document_title="Gas Statement of Opportunities",
                source_page_url=(
                    "https://www.aemo.com.au/energy-systems/gas/"
                    "gas-forecasting-and-planning/"
                    "gas-statement-of-opportunities-gsoo"
                ),
                source_url="https://www.aemo.com.au/media/gsoo.pdf",
                resolved_url="https://www.aemo.com.au/media/gsoo.pdf",
                archive_storage_uri=(
                    "s3://dev-energy-market-archive/bronze/"
                    f"aemo_major_publications/{gsoo_hash}.pdf"
                ),
                storage_uri=(
                    "s3://dev-energy-market-archive/bronze/"
                    f"aemo_major_publications/{gsoo_hash}.pdf"
                ),
                target_s3_key=f"bronze/aemo_major_publications/{gsoo_hash}.pdf",
            ),
            _download_metadata_row(
                content_sha256=wa_gsoo_hash,
                corpus_source="wa_gsoo",
                document_family_id="wa_gsoo__wa-gas-statement-of-opportunities",
                document_title="WA Gas Statement of Opportunities",
                source_page_url=(
                    "https://www.aemo.com.au/energy-systems/gas/"
                    "gas-forecasting-and-planning/"
                    "wa-gas-statement-of-opportunities-wa-gsoo"
                ),
                source_url="https://www.aemo.com.au/media/wa-gsoo.pdf",
                resolved_url="https://www.aemo.com.au/media/wa-gsoo.pdf",
                archive_storage_uri=(
                    "s3://dev-energy-market-archive/bronze/"
                    f"aemo_major_publications/{wa_gsoo_hash}.pdf"
                ),
                storage_uri=(
                    "s3://dev-energy-market-archive/bronze/"
                    f"aemo_major_publications/{wa_gsoo_hash}.pdf"
                ),
                target_s3_key=f"bronze/aemo_major_publications/{wa_gsoo_hash}.pdf",
            ),
        ],
        paths=paths,
    )

    assert summary.as_dict() == {
        "metadata_row_count": 4,
        "manifest_row_count": 4,
        "included_row_count": 4,
        "review_needed_row_count": 0,
        "excluded_out_of_scope_count": 0,
    }
    assert {row["document_title"] for row in rows} == {
        "Electricity Statement of Opportunities",
        "Gas Statement of Opportunities",
        "Integrated System Plan",
        "WA Gas Statement of Opportunities",
    }
    assert {row["corpus_source"] for row in rows} == {
        "gsoo",
        "major_publications",
        "wa_gsoo",
    }
    assert rows[0]["include_decision"] == "include"
    assert rows[0]["review_status"] == "ready"
    assert rows[0]["source_page_url"]
    assert rows[0]["source_url"]
    assert rows[0]["content_sha256"] in {
        "a" * 64,
        library_hash,
        gsoo_hash,
        wa_gsoo_hash,
    }
    assert rows[0]["storage_uri"] == rows[0]["archive_uri"]
    assert rows[0]["generated_paths"] == paths.generated_paths(
        cast(str, rows[0]["document_identity"])
    )


def test_aemo_publications_manifest_keeps_unsupported_and_failed_rows_for_review(
    tmp_path: Path,
) -> None:
    paths = default_corpus_paths(artifact_root=tmp_path / "corpora")
    rows, summary = build_aemo_publication_manifest_rows(
        [
            _download_metadata_row(
                content_sha256="c" * 64,
                content_type="application/vnd.ms-excel",
                source_url="https://www.aemo.com.au/media/input-workbook.xlsx",
                resolved_url="https://www.aemo.com.au/media/input-workbook.xlsx",
            ),
            _download_metadata_row(
                content_sha256=None,
                storage_uri=None,
                archive_storage_uri=None,
                exclude_reason="Download failed during materialization: timeout",
            ),
        ],
        paths=paths,
    )

    assert summary.review_needed_row_count == 2
    assert summary.included_row_count == 0
    rows_by_status = {cast(str, row["review_status"]): row for row in rows}
    assert rows_by_status["unsupported_media_type"]["include_decision"] == (
        "needs_human_review"
    )
    assert rows_by_status["unsupported_media_type"]["content_sha256"] == "c" * 64
    assert rows_by_status["unsupported_media_type"]["archive_uri"] is None
    assert rows_by_status["download_failed"]["content_sha256"] is None
    assert rows_by_status["download_failed"]["archive_uri"] is None
    assert rows_by_status["download_failed"]["review_reason"] == (
        "Download failed during materialization: timeout"
    )


def test_aemo_publications_manifest_keeps_duplicate_hash_and_missing_storage_auditable(
    tmp_path: Path,
) -> None:
    paths = default_corpus_paths(artifact_root=tmp_path / "corpora")
    rows, summary = build_aemo_publication_manifest_rows(
        [
            _download_metadata_row(),
            _download_metadata_row(source_url="https://www.aemo.com.au/media/copy.pdf"),
            _download_metadata_row(
                content_sha256="d" * 64,
                storage_uri=None,
                archive_storage_uri=None,
                source_url="https://www.aemo.com.au/media/no-storage.pdf",
                resolved_url="https://www.aemo.com.au/media/no-storage.pdf",
            ),
        ],
        paths=paths,
    )

    assert summary.included_row_count == 1
    assert summary.review_needed_row_count == 2
    rows_by_status = {cast(str, row["review_status"]): row for row in rows}
    assert rows_by_status["ready"]["include_decision"] == "include"
    assert rows_by_status["duplicate_content_hash"]["content_sha256"] == "a" * 64
    assert rows_by_status["duplicate_content_hash"]["archive_uri"] is None
    assert rows_by_status["missing_storage_uri"]["content_sha256"] == "d" * 64
    assert rows_by_status["missing_storage_uri"]["archive_uri"] is None


def test_aemo_publications_manifest_excludes_unknown_publication_rows(
    tmp_path: Path,
) -> None:
    rows, summary = build_aemo_publication_manifest_rows(
        [
            _download_metadata_row(
                corpus_source="not_a_publication",
                source_page_url=(
                    "https://www.aemo.com.au/energy-systems/gas/"
                    "gas-forecasting-and-planning/"
                    "gas-statement-of-opportunities-gsoo"
                ),
            )
        ],
        paths=default_corpus_paths(artifact_root=tmp_path / "corpora"),
    )

    assert rows == []
    assert summary.excluded_out_of_scope_count == 1


def test_aemo_publications_review_rows_stay_visible_but_not_extractable(
    tmp_path: Path,
) -> None:
    paths = default_corpus_paths(artifact_root=tmp_path / "corpora")
    result = write_aemo_publication_manifest(
        [
            _download_metadata_row(),
            _download_metadata_row(
                content_sha256=None,
                storage_uri=None,
                archive_storage_uri=None,
                exclude_reason="Download failed during materialization: timeout",
            ),
        ],
        paths=paths,
    )

    manifest = load_source_document_manifest(
        paths.source_manifest_path,
        cache_dir=paths.source_cache_dir,
        output_dir=paths.silver_documents_dir,
    )

    assert result.summary.manifest_row_count == 2
    assert manifest.row_count == 2
    assert len(manifest.entries) == 1
    assert manifest.errors == ()


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
    assert result.silver_document_result.extracted_count == 4
    assert result.manifest_result.row_count == 4
    assert result.silver_index_result.chunk_count == 4
    assert result.silver_validation_result.error_count == 0
    assert result.gold_validation_result.error_count == 0
    assert len(index_rows) == 4
    assert source_frontmatter["content_sha256"] == index_rows[0]["content_sha256"]
    assert gold_frontmatter["context_type"] == "glossary-page"
    assert gold_frontmatter["source_chunk_ids"] == [index_rows[0]["chunk_id"]]
    assert "\n## Source Citations\n\n- `chunk-" in gold_text
    assert "[[source:sha256:" in gold_text


def test_aemo_publications_validation_reports_coverage_and_artifact_counts(
    tmp_path: Path,
) -> None:
    artifact_root = tmp_path / "corpora"
    build_fixture_corpus(
        artifact_root=artifact_root,
        min_text_chars=20,
    )

    result = CliRunner().invoke(
        main,
        [
            "validate",
            "--artifact-root",
            str(artifact_root),
            "--min-text-chars",
            "20",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "hub_source_families=1" in result.output
    assert "library_source_families=1" in result.output
    assert "gsoo_source_families=1" in result.output
    assert "wa_gsoo_source_families=1" in result.output
    assert "supported_media=4" in result.output
    assert "unsupported_media=0" in result.output
    assert "silver_index_rows=4" in result.output
    assert "silver_chunk_files=4" in result.output
    assert "gold_pages=6" in result.output


def test_aemo_publications_validation_counts_unsupported_metadata_rows(
    tmp_path: Path,
) -> None:
    paths = default_corpus_paths(artifact_root=tmp_path / "corpora")
    library_hash = "b" * 64
    write_aemo_publication_manifest(
        [
            _download_metadata_row(),
            _download_metadata_row(
                content_sha256=library_hash,
                document_family_id="electricity-statement-of-opportunities",
                document_title="Electricity Statement of Opportunities",
                source_page_url="https://www.aemo.com.au/library/major-publications",
                source_url="https://www.aemo.com.au/media/esoo.pdf",
                resolved_url="https://www.aemo.com.au/media/esoo.pdf",
                archive_storage_uri=(
                    "s3://dev-energy-market-archive/bronze/"
                    f"aemo_major_publications/{library_hash}.pdf"
                ),
                storage_uri=(
                    "s3://dev-energy-market-archive/bronze/"
                    f"aemo_major_publications/{library_hash}.pdf"
                ),
                target_s3_key=f"bronze/aemo_major_publications/{library_hash}.pdf",
            ),
            _download_metadata_row(
                content_sha256="c" * 64,
                content_type="application/vnd.ms-excel",
                source_url="https://www.aemo.com.au/media/input-workbook.xlsx",
                resolved_url="https://www.aemo.com.au/media/input-workbook.xlsx",
            ),
        ],
        paths=paths,
    )

    result = validate_aemo_publications_corpus(paths=paths, min_text_chars=20)

    assert result.coverage.hub_source_family_count == 1
    assert result.coverage.library_source_family_count == 1
    assert result.coverage.gsoo_source_family_count == 0
    assert result.coverage.wa_gsoo_source_family_count == 0
    assert result.coverage.supported_media_count == 2
    assert result.coverage.unsupported_media_count == 1
    assert result.coverage.review_needed_count == 1


def test_aemo_publications_validation_reports_missing_downloaded_metadata(
    tmp_path: Path,
) -> None:
    paths = default_corpus_paths(artifact_root=tmp_path / "corpora")

    result = validate_aemo_publications_corpus(paths=paths)

    assert result.error_count == 1
    assert result.errors == (
        f"downloaded metadata missing: source manifest not found at "
        f"{paths.source_manifest_path}",
    )


def test_aemo_publications_validation_reports_missing_source_files(
    tmp_path: Path,
) -> None:
    paths = default_corpus_paths(artifact_root=tmp_path / "corpora")
    write_aemo_publication_manifest([_download_metadata_row()], paths=paths)

    result = validate_aemo_publications_corpus(paths=paths, min_text_chars=20)

    assert any(
        "missing source file: manifest row 1" in error for error in result.errors
    )


def test_aemo_publications_validation_reports_stale_index_rows(
    tmp_path: Path,
) -> None:
    result = build_fixture_corpus(
        artifact_root=tmp_path / "corpora",
        min_text_chars=20,
    )
    index_rows = _jsonl_rows(result.paths.silver_index_path)
    stale_row = dict(index_rows[0])
    stale_row["document_title"] = "Stale title"
    result.paths.silver_index_path.write_text(
        "\n".join(
            json.dumps(row, sort_keys=True) for row in (stale_row, *index_rows[1:])
        )
        + "\n",
        encoding="utf-8",
    )

    validation_result = validate_aemo_publications_corpus(
        paths=result.paths,
        min_text_chars=20,
    )

    assert any("is stale" in error for error in validation_result.errors)


def test_aemo_publications_validation_reports_broken_gold_citations(
    tmp_path: Path,
) -> None:
    result = build_fixture_corpus(
        artifact_root=tmp_path / "corpora",
        min_text_chars=20,
    )
    gold_page = (
        result.paths.gold_dir / "glossary" / "electricity-statement-of-opportunities.md"
    )
    frontmatter = dict(_frontmatter(gold_page))
    frontmatter["source_chunk_ids"] = ["chunk-missing"]
    _write_frontmatter(gold_page, frontmatter)

    validation_result = validate_aemo_publications_corpus(
        paths=result.paths,
        min_text_chars=20,
    )

    assert any("chunk-missing" in error for error in validation_result.errors)


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
    assert "summary: manifest_rows=4 silver_documents=4 chunks=4" in result.output
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
