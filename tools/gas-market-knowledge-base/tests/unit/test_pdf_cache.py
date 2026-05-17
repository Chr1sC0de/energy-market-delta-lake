import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from click.testing import CliRunner

from gas_market_knowledge_base.cli import main
from gas_market_knowledge_base.pdf_cache import (
    ArchiveObjectReader,
    ArchiveObjectReadError,
    fetch_pdf_cache,
    pdf_cache_path,
)


class FakeArchiveReader(ArchiveObjectReader):
    def __init__(
        self,
        objects: Mapping[str, bytes],
        *,
        failures: set[str] | None = None,
    ) -> None:
        self._objects = objects
        self._failures = failures or set()
        self.requests: list[str] = []

    def read_bytes(self, uri: str) -> bytes:
        self.requests.append(uri)
        if uri in self._failures:
            raise ArchiveObjectReadError("object is missing")
        if uri not in self._objects:
            raise ArchiveObjectReadError("object not found")
        return self._objects[uri]


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _manifest_row(
    content: bytes, *, archive_uri: str = "fake://archive/doc.pdf"
) -> dict[str, object]:
    content_sha256 = _sha256(content)
    return {
        "schema_version": 1,
        "document_identity": f"gbb/guide/sha256-{content_sha256}",
        "content_sha256": content_sha256,
        "archive_uri": archive_uri,
    }


def _write_manifest(path: Path, rows: list[Mapping[str, object]]) -> None:
    path.write_text(
        "".join(f"{json.dumps(row, sort_keys=True)}\n" for row in rows),
        encoding="utf-8",
    )


def test_fetch_pdfs_reuses_valid_cache_entry(tmp_path: Path) -> None:
    content = b"%PDF-1.7\nvalid cache\n"
    content_sha256 = _sha256(content)
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    target_path = pdf_cache_path(content_sha256, cache_dir=cache_dir)
    target_path.parent.mkdir(parents=True)
    target_path.write_bytes(content)
    _write_manifest(manifest_path, [_manifest_row(content)])
    reader = FakeArchiveReader({"fake://archive/doc.pdf": b"unused"})

    result = fetch_pdf_cache(
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        archive_reader=reader,
    )

    assert result.reused_count == 1
    assert result.downloaded_count == 0
    assert result.error_count == 0
    assert reader.requests == []
    assert target_path.read_bytes() == content


def test_fetch_pdfs_downloads_missing_cache_entry(tmp_path: Path) -> None:
    content = b"%PDF-1.7\nfresh download\n"
    content_sha256 = _sha256(content)
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    _write_manifest(manifest_path, [_manifest_row(content)])
    reader = FakeArchiveReader({"fake://archive/doc.pdf": content})

    result = fetch_pdf_cache(
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        archive_reader=reader,
    )

    target_path = cache_dir / f"{content_sha256}.pdf"
    assert result.downloaded_count == 1
    assert result.reused_count == 0
    assert result.error_count == 0
    assert reader.requests == ["fake://archive/doc.pdf"]
    assert target_path.read_bytes() == content


def test_fetch_pdfs_repairs_invalid_cache_entry_after_valid_download(
    tmp_path: Path,
) -> None:
    content = b"%PDF-1.7\nreplacement\n"
    content_sha256 = _sha256(content)
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    target_path = pdf_cache_path(content_sha256, cache_dir=cache_dir)
    target_path.parent.mkdir(parents=True)
    target_path.write_bytes(b"stale bytes")
    _write_manifest(manifest_path, [_manifest_row(content)])
    reader = FakeArchiveReader({"fake://archive/doc.pdf": content})

    result = fetch_pdf_cache(
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        archive_reader=reader,
    )

    assert result.invalid_cache_entry_count == 1
    assert result.refreshed_count == 1
    assert result.downloaded_count == 0
    assert result.error_count == 0
    assert target_path.read_bytes() == content


def test_fetch_pdfs_reports_hash_mismatch_without_writing_cache(
    tmp_path: Path,
) -> None:
    expected_content = b"%PDF-1.7\nexpected\n"
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    _write_manifest(manifest_path, [_manifest_row(expected_content)])
    reader = FakeArchiveReader({"fake://archive/doc.pdf": b"%PDF-1.7\nwrong\n"})

    result = fetch_pdf_cache(
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        archive_reader=reader,
    )

    target_path = pdf_cache_path(_sha256(expected_content), cache_dir=cache_dir)
    assert result.error_count == 1
    assert "hash mismatch" in result.errors[0]
    assert not target_path.exists()


def test_fetch_pdfs_reports_missing_archive_uri(tmp_path: Path) -> None:
    content = b"%PDF-1.7\nmissing archive uri\n"
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    row = _manifest_row(content)
    del row["archive_uri"]
    _write_manifest(manifest_path, [row])
    reader = FakeArchiveReader({})

    result = fetch_pdf_cache(
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        archive_reader=reader,
    )

    assert result.fetchable_row_count == 0
    assert result.error_count == 1
    assert result.errors == ("manifest row 1 missing archive_uri",)
    assert reader.requests == []


def test_fetch_pdfs_reports_fetch_failure(tmp_path: Path) -> None:
    content = b"%PDF-1.7\nfetch failure\n"
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    _write_manifest(manifest_path, [_manifest_row(content)])
    reader = FakeArchiveReader({}, failures={"fake://archive/doc.pdf"})

    result = fetch_pdf_cache(
        manifest_path=manifest_path,
        cache_dir=cache_dir,
        archive_reader=reader,
    )

    assert result.error_count == 1
    assert "fetch failed" in result.errors[0]
    assert "object is missing" in result.errors[0]


def test_fetch_pdfs_command_can_use_file_archive_fixture(tmp_path: Path) -> None:
    content = b"%PDF-1.7\nfile archive fixture\n"
    content_sha256 = _sha256(content)
    source_pdf = tmp_path / "archive.pdf"
    source_pdf.write_bytes(content)
    manifest_path = tmp_path / "source_manifest.jsonl"
    cache_dir = tmp_path / ".cache" / "pdfs"
    _write_manifest(
        manifest_path,
        [_manifest_row(content, archive_uri=source_pdf.as_uri())],
    )

    result = CliRunner().invoke(
        main,
        [
            "fetch-pdfs",
            "--manifest-path",
            str(manifest_path),
            "--cache-dir",
            str(cache_dir),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "cached PDFs in" in result.output
    assert "downloaded=1" in result.output
    assert (cache_dir / f"{content_sha256}.pdf").read_bytes() == content
