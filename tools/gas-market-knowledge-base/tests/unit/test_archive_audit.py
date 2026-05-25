import json
from collections.abc import Mapping
from pathlib import Path

from click.testing import CliRunner

from gas_market_knowledge_base.archive_audit import (
    audit_archive_prefix,
    default_archive_prefix_uri,
)
from gas_market_knowledge_base.cli import main

ARCHIVE_PREFIX = "s3://dev-energy-market-archive/bronze/aemo_gas_documents/"
ARCHIVE_A = f"{ARCHIVE_PREFIX}a.pdf"
ARCHIVE_B = f"{ARCHIVE_PREFIX}nested/b.pdf"
ARCHIVE_C = f"{ARCHIVE_PREFIX}c.pdf"


def _manifest_row(
    *,
    archive_uri: str,
    content_sha256: str,
    document_identity: str = "gbb/guide/sha256-source",
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "document_identity": document_identity,
        "content_sha256": content_sha256,
        "archive_uri": archive_uri,
    }


def _write_manifest(path: Path, rows: list[Mapping[str, object]]) -> None:
    path.write_text(
        "".join(f"{json.dumps(row, sort_keys=True)}\n" for row in rows),
        encoding="utf-8",
    )


def _write_listing(path: Path, rows: list[object]) -> None:
    path.write_text(json.dumps({"objects": rows}, sort_keys=True), encoding="utf-8")


def test_default_archive_prefix_uri_uses_dev_energy_market_archive_bucket() -> None:
    assert default_archive_prefix_uri() == ARCHIVE_PREFIX


def test_archive_prefix_audit_accepts_complete_fixture_listing(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source_manifest.jsonl"
    listing_path = tmp_path / "archive-listing.json"
    _write_manifest(
        manifest_path,
        [
            _manifest_row(archive_uri=ARCHIVE_A, content_sha256="a" * 64),
            _manifest_row(archive_uri=ARCHIVE_B, content_sha256="b" * 64),
        ],
    )
    _write_listing(
        listing_path,
        [
            {"key": "bronze/aemo_gas_documents/a.pdf"},
            {"uri": ARCHIVE_B},
            {"key": "bronze/aemo_gas_documents/not-a-pdf.txt"},
        ],
    )

    result = audit_archive_prefix(
        manifest_path=manifest_path,
        archive_prefix_uri=ARCHIVE_PREFIX,
        listing_path=listing_path,
    )

    assert result.problem_count == 0
    assert result.prefix_pdf_object_count == 2
    assert result.manifest_row_count == 2
    assert result.manifest_object_count == 2
    assert result.manifest_hash_count == 2
    assert result.summary_text() == (
        "summary: prefix_pdf_objects=2 manifest_rows=2 manifest_objects=2 "
        "manifest_hashes=2 missing_archive_pdfs=0 extra_manifest_rows=0 "
        "duplicate_archive_uris=0 duplicate_content_hashes=0 manifest_errors=0"
    )


def test_archive_prefix_audit_reports_missing_archive_pdfs(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source_manifest.jsonl"
    listing_path = tmp_path / "archive-listing.json"
    _write_manifest(
        manifest_path,
        [_manifest_row(archive_uri=ARCHIVE_A, content_sha256="a" * 64)],
    )
    _write_listing(listing_path, [ARCHIVE_A, ARCHIVE_B])

    result = audit_archive_prefix(
        manifest_path=manifest_path,
        archive_prefix_uri=ARCHIVE_PREFIX,
        listing_path=listing_path,
    )

    assert result.problem_count == 1
    assert result.missing_archive_uris == (ARCHIVE_B,)
    assert result.problem_lines() == (f"missing archive PDF: {ARCHIVE_B}",)


def test_archive_prefix_audit_reports_extra_manifest_rows(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source_manifest.jsonl"
    listing_path = tmp_path / "archive-listing.json"
    _write_manifest(
        manifest_path,
        [
            _manifest_row(archive_uri=ARCHIVE_A, content_sha256="a" * 64),
            _manifest_row(archive_uri=ARCHIVE_C, content_sha256="c" * 64),
        ],
    )
    _write_listing(listing_path, [ARCHIVE_A])

    result = audit_archive_prefix(
        manifest_path=manifest_path,
        archive_prefix_uri=ARCHIVE_PREFIX,
        listing_path=listing_path,
    )

    assert result.problem_count == 1
    assert len(result.extra_manifest_rows) == 1
    assert result.extra_manifest_rows[0].line_number == 2
    assert result.problem_lines() == (
        f"extra manifest row 2: {ARCHIVE_C} (content_sha256={'c' * 64})",
    )


def test_archive_prefix_audit_tracks_duplicate_objects_and_hashes_as_warnings(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source_manifest.jsonl"
    listing_path = tmp_path / "archive-listing.json"
    duplicate_hash = "d" * 64
    _write_manifest(
        manifest_path,
        [
            _manifest_row(archive_uri=ARCHIVE_A, content_sha256=duplicate_hash),
            _manifest_row(archive_uri=ARCHIVE_A, content_sha256=duplicate_hash),
            _manifest_row(archive_uri=ARCHIVE_B, content_sha256=duplicate_hash),
        ],
    )
    _write_listing(listing_path, [ARCHIVE_A, ARCHIVE_B])

    result = audit_archive_prefix(
        manifest_path=manifest_path,
        archive_prefix_uri=ARCHIVE_PREFIX,
        listing_path=listing_path,
    )

    assert result.missing_archive_uris == ()
    assert result.extra_manifest_rows == ()
    assert result.problem_count == 0
    assert result.problem_lines() == ()
    assert result.warning_count == 2
    assert result.manifest_row_count == 3
    assert result.manifest_object_count == 2
    assert result.manifest_hash_count == 1
    assert result.duplicate_archive_uris[0].value == ARCHIVE_A
    assert result.duplicate_archive_uris[0].line_numbers == (1, 2)
    assert result.duplicate_content_hashes[0].value == duplicate_hash
    assert result.duplicate_content_hashes[0].line_numbers == (1, 2, 3)
    assert result.warning_lines() == (
        f"duplicate archive_uri: {ARCHIVE_A} (manifest rows 1, 2)",
        f"duplicate content_sha256: {duplicate_hash} (manifest rows 1, 2, 3)",
    )


def test_audit_archive_prefix_command_warns_for_duplicate_manifest_rows(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "source_manifest.jsonl"
    listing_path = tmp_path / "archive-listing.jsonl"
    duplicate_hash = "d" * 64
    _write_manifest(
        manifest_path,
        [
            _manifest_row(archive_uri=ARCHIVE_A, content_sha256=duplicate_hash),
            _manifest_row(archive_uri=ARCHIVE_A, content_sha256=duplicate_hash),
        ],
    )
    listing_path.write_text(f"{json.dumps(ARCHIVE_A)}\n", encoding="utf-8")

    result = CliRunner().invoke(
        main,
        [
            "audit-archive-prefix",
            "--archive-prefix",
            ARCHIVE_PREFIX,
            "--listing-path",
            str(listing_path),
            "--manifest-path",
            str(manifest_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert f"Warning: duplicate archive_uri: {ARCHIVE_A}" in result.output
    assert f"Warning: duplicate content_sha256: {duplicate_hash}" in result.output
    assert "duplicate_archive_uris=1 duplicate_content_hashes=1" in result.output


def test_audit_archive_prefix_command_uses_fixture_listing(tmp_path: Path) -> None:
    manifest_path = tmp_path / "source_manifest.jsonl"
    listing_path = tmp_path / "archive-listing.jsonl"
    _write_manifest(
        manifest_path,
        [
            _manifest_row(archive_uri=ARCHIVE_A, content_sha256="a" * 64),
            _manifest_row(archive_uri=ARCHIVE_C, content_sha256="c" * 64),
        ],
    )
    listing_path.write_text(f"{json.dumps(ARCHIVE_A)}\n", encoding="utf-8")

    result = CliRunner().invoke(
        main,
        [
            "audit-archive-prefix",
            "--archive-prefix",
            ARCHIVE_PREFIX,
            "--listing-path",
            str(listing_path),
            "--manifest-path",
            str(manifest_path),
        ],
    )

    assert result.exit_code == 1
    assert "Error: audit-archive-prefix found 1 problem(s)" in result.output
    assert f"extra manifest row 2: {ARCHIVE_C}" in result.output
    assert "summary: prefix_pdf_objects=1 manifest_rows=2 manifest_objects=2" in (
        result.output
    )
