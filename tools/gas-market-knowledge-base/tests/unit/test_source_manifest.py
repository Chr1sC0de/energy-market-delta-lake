import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from gas_market_knowledge_base.cli import main
from gas_market_knowledge_base.source_manifest import (
    ManifestValidationError,
    build_source_manifest_rows,
    default_metadata_table_uri,
    load_metadata_rows_from_json,
    sync_source_manifest,
)


def _metadata_row(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "archive_storage_uri": (
            "s3://dev-energy-market-archive/bronze/aemo_gas_documents/base.pdf"
        ),
        "content_length": 1234,
        "content_sha256": "a" * 64,
        "corpus_source": "gbb",
        "document_family_id": "gbb__gas-guide",
        "document_kind": "guide",
        "document_title": "Gas Guide",
        "document_version": "v1",
        "document_version_id": "a" * 64,
        "effective_date": "2026-01-01",
        "include_decision": "include",
        "media_revision": "rev-a",
        "published_date": "2026-01-02",
        "resolved_url": "https://www.aemo.com.au/media/gas-guide.pdf",
        "source_link_text": "Gas Guide v1",
        "source_page_title": "GBB procedures and guides",
        "source_page_url": "https://www.aemo.com.au/gas/gbb",
        "source_url": "https://www.aemo.com.au/media/gas-guide.pdf",
        "storage_uri": (
            "s3://dev-energy-market-archive/bronze/aemo_gas_documents/base.pdf"
        ),
        "target_s3_key": "bronze/aemo_gas_documents/base.pdf",
    }
    row.update(overrides)
    return row


def _jsonl_rows(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_default_metadata_table_uri_uses_dev_energy_market_buckets() -> None:
    assert default_metadata_table_uri() == (
        "s3://dev-energy-market-aemo/bronze/aemo_gas_documents/"
        "bronze_aemo_gas_document_sources"
    )


def test_source_manifest_filters_counts_and_sorts_fixture_rows(tmp_path: Path) -> None:
    output_path = tmp_path / "source_manifest.jsonl"
    rows = [
        _metadata_row(
            content_sha256="b" * 64,
            document_family_id="sttm__zeta-procedure",
            document_title="Zeta Procedure",
            corpus_source="sttm",
            source_url="https://www.aemo.com.au/media/zeta.pdf",
            archive_storage_uri=(
                "s3://dev-energy-market-archive/bronze/aemo_gas_documents/zeta.pdf"
            ),
            storage_uri=(
                "s3://dev-energy-market-archive/bronze/aemo_gas_documents/zeta.pdf"
            ),
            target_s3_key="bronze/aemo_gas_documents/zeta.pdf",
        ),
        _metadata_row(
            content_sha256="a" * 64,
            document_family_id="gbb__alpha-guide",
            document_title="Alpha Guide",
            source_url="https://www.aemo.com.au/media/alpha.pdf",
            archive_storage_uri=(
                "s3://dev-energy-market-archive/bronze/aemo_gas_documents/alpha.pdf"
            ),
            storage_uri=(
                "s3://dev-energy-market-archive/bronze/aemo_gas_documents/alpha.pdf"
            ),
            target_s3_key="bronze/aemo_gas_documents/alpha.pdf",
        ),
        _metadata_row(include_decision="exclude"),
        _metadata_row(include_decision="needs_human_review"),
        _metadata_row(content_sha256=None),
        _metadata_row(
            archive_storage_uri=(
                "s3://dev-energy-market-landing/bronze/aemo_gas_documents/base.pdf"
            ),
            storage_uri=(
                "s3://dev-energy-market-landing/bronze/aemo_gas_documents/base.pdf"
            ),
        ),
    ]

    result = sync_source_manifest(rows, output_path=output_path)

    manifest_rows = _jsonl_rows(output_path)
    assert [row["content_sha256"] for row in manifest_rows] == ["a" * 64, "b" * 64]
    assert manifest_rows[0]["document_identity"] == (
        f"gbb/gbb-alpha-guide/sha256-{'a' * 64}"
    )
    assert manifest_rows[0]["document_title"] == "Alpha Guide"
    archive_uri = manifest_rows[0]["archive_uri"]
    assert isinstance(archive_uri, str)
    assert archive_uri.startswith("s3://dev-energy-market-archive/")
    assert manifest_rows[0]["content_length"] == 1234
    assert manifest_rows[0]["generated_paths"] == {
        "silver_document_markdown": (
            f"generated/silver/documents/gbb/gbb-alpha-guide/sha256-{'a' * 64}.md"
        ),
        "silver_chunks": (
            f"generated/silver/chunks/gbb/gbb-alpha-guide/sha256-{'a' * 64}"
        ),
        "silver_chunk_index": "generated/silver/index/chunks.jsonl",
        "gold_context": (f"generated/gold/gbb/gbb-alpha-guide/sha256-{'a' * 64}.md"),
    }
    assert result.summary.as_dict() == {
        "environment": "dev",
        "metadata_row_count": 6,
        "manifest_row_count": 2,
        "excluded_by_decision_count": 2,
        "excluded_without_content_sha256_count": 1,
        "excluded_without_archive_storage_count": 1,
    }


def test_source_manifest_requires_metadata_contract_fields() -> None:
    row = _metadata_row()
    del row["source_url"]

    with pytest.raises(
        ManifestValidationError,
        match="metadata row 0 missing required metadata fields: source_url",
    ):
        build_source_manifest_rows([row])


def test_source_manifest_requires_selected_lineage_fields() -> None:
    row = _metadata_row(document_title=None)

    with pytest.raises(
        ManifestValidationError,
        match="metadata row 0 field document_title must be a non-empty string",
    ):
        build_source_manifest_rows([row])


def test_load_metadata_rows_from_json_accepts_rows_object(tmp_path: Path) -> None:
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(json.dumps({"rows": [_metadata_row()]}), encoding="utf-8")

    assert load_metadata_rows_from_json(metadata_path) == [_metadata_row()]


def test_sync_manifest_command_writes_fixture_manifest(tmp_path: Path) -> None:
    metadata_path = tmp_path / "metadata.jsonl"
    metadata_path.write_text(
        "\n".join(
            [
                json.dumps(_metadata_row()),
                json.dumps(_metadata_row(content_sha256=None)),
            ]
        ),
        encoding="utf-8",
    )
    output_path = tmp_path / "generated" / "bronze" / "source_manifest.jsonl"

    result = CliRunner().invoke(
        main,
        [
            "sync-manifest",
            "--environment",
            "dev",
            "--metadata-path",
            str(metadata_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "wrote 1 manifest rows" in result.output
    assert "excluded_without_content_sha256=1" in result.output
    assert len(_jsonl_rows(output_path)) == 1


def test_sync_manifest_command_reports_validation_errors(tmp_path: Path) -> None:
    row = _metadata_row()
    del row["content_sha256"]
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(json.dumps([row]), encoding="utf-8")

    result = CliRunner().invoke(
        main,
        [
            "sync-manifest",
            "--metadata-path",
            str(metadata_path),
            "--output-path",
            str(tmp_path / "source_manifest.jsonl"),
        ],
    )

    assert result.exit_code == 1
    assert "Error: metadata row 0 missing required metadata fields: content_sha256" in (
        result.output
    )
