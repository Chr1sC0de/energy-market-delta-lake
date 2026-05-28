"""Fixture build for the AEMO major publications corpus."""

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from gas_market_knowledge_base.aemo_publications.corpus_paths import (
    AemoPublicationCorpusPaths,
    default_corpus_paths,
)
from gas_market_knowledge_base.corpus_core.gold_context import (
    GOLD_SCHEMA_VERSION,
    GoldContextValidationResult,
    GoldSourceCitation,
    render_gold_glossary_body,
    render_gold_markdown_page,
    validate_gold_context,
)
from gas_market_knowledge_base.corpus_core.manifest import (
    MANIFEST_SCHEMA_VERSION,
    ManifestJsonValue,
    SourceManifestRow,
    document_identity,
    dump_source_manifest_jsonl,
)
from gas_market_knowledge_base.corpus_core.paths import source_pdf_cache_path
from gas_market_knowledge_base.corpus_core.silver_chunks import (
    ExtractedHybridChunk,
    HybridChunkExtractor,
    SilverChunkBuildResult,
    SilverIndexValidationResult,
    build_silver_index,
    validate_silver_index,
)
from gas_market_knowledge_base.corpus_core.silver_documents import (
    DEFAULT_MIN_TEXT_CHARS,
    MarkdownExtractionError,
    MarkdownExtractor,
    SilverDocumentExtractionResult,
    extract_silver_documents,
)

FIXTURE_CORPUS_SOURCE = "aemo-major-publications"


class FixtureCorpusBuildError(ValueError):
    """Raised when the fixture corpus cannot be built."""


@dataclass(frozen=True, slots=True)
class FixturePublication:
    """One deterministic AEMO publication fixture."""

    filename: str
    document_family_id: str
    document_title: str
    document_kind: str
    document_version: str
    document_version_id: str
    published_date: str
    effective_date: str
    source_url: str
    source_page_url: str
    source_page_title: str
    source_link_text: str
    source_bytes: bytes
    silver_markdown: str
    chunks: tuple[ExtractedHybridChunk, ...]
    glossary_slug: str
    glossary_title: str
    glossary_definition: str


@dataclass(frozen=True, slots=True)
class FixtureManifestResult:
    """Result of writing the fixture bronze source manifest."""

    output_path: Path
    row_count: int


@dataclass(frozen=True, slots=True)
class FixtureCorpusBuildResult:
    """Result of one AEMO publications fixture corpus build."""

    paths: AemoPublicationCorpusPaths
    manifest_result: FixtureManifestResult
    silver_document_result: SilverDocumentExtractionResult
    silver_index_result: SilverChunkBuildResult
    silver_validation_result: SilverIndexValidationResult
    gold_validation_result: GoldContextValidationResult
    gold_page_count: int

    @property
    def error_count(self) -> int:
        """Return the total validation and build error count."""
        return (
            self.silver_document_result.error_count
            + self.silver_index_result.error_count
            + self.silver_validation_result.error_count
            + self.gold_validation_result.error_count
        )


class FixtureMarkdownExtractor(MarkdownExtractor):
    """Return fixture Markdown for cached fixture publication bytes."""

    def __init__(self, publications: Sequence[FixturePublication]) -> None:
        self._markdown_by_sha = {
            _source_sha256(publication.source_bytes): publication.silver_markdown
            for publication in publications
        }

    def extract_markdown(self, pdf_path: Path) -> str:
        content_sha256 = pdf_path.stem
        markdown = self._markdown_by_sha.get(content_sha256)
        if markdown is None:
            raise MarkdownExtractionError(
                f"no AEMO publication fixture Markdown for {content_sha256}"
            )
        return markdown


class FixtureHybridChunkExtractor(HybridChunkExtractor):
    """Return fixture Hybrid chunks for cached fixture publication bytes."""

    def __init__(self, publications: Sequence[FixturePublication]) -> None:
        self._chunks_by_sha = {
            _source_sha256(publication.source_bytes): publication.chunks
            for publication in publications
        }

    def extract_chunks(self, pdf_path: Path) -> tuple[ExtractedHybridChunk, ...]:
        content_sha256 = pdf_path.stem
        chunks = self._chunks_by_sha.get(content_sha256)
        if chunks is None:
            raise FixtureCorpusBuildError(
                f"no AEMO publication fixture chunks for {content_sha256}"
            )
        return chunks


def fixture_publications() -> tuple[FixturePublication, ...]:
    """Return the deterministic publication fixtures used by build-fixture."""
    return (
        FixturePublication(
            filename="2026-integrated-system-plan-fixture.pdf",
            document_family_id="integrated-system-plan",
            document_title="2026 Integrated System Plan Fixture",
            document_kind="major-publication",
            document_version="2026 fixture",
            document_version_id="fixture-2026-isp",
            published_date="2026-01-15",
            effective_date="2026-01-15",
            source_url=(
                "https://aemo.com.au/energy-systems/major-publications/"
                "integrated-system-plan-isp"
            ),
            source_page_url=(
                "https://aemo.com.au/energy-systems/major-publications/"
                "integrated-system-plan-isp"
            ),
            source_page_title="Integrated System Plan",
            source_link_text="2026 Integrated System Plan fixture",
            source_bytes=(
                b"%PDF-1.7\n"
                b"AEMO 2026 Integrated System Plan fixture publication bytes.\n"
            ),
            silver_markdown=(
                "# 2026 Integrated System Plan Fixture\n\n"
                "The Integrated System Plan fixture describes a planning publication "
                "used to exercise the AEMO major publications corpus without live "
                "metadata. It includes enough source text for deterministic silver "
                "document extraction and citation validation.\n"
            ),
            chunks=(
                ExtractedHybridChunk(
                    text=(
                        "The Integrated System Plan fixture is an AEMO major "
                        "publication used for deterministic corpus validation."
                    ),
                    heading_path=("Integrated System Plan", "Fixture Scope"),
                    doc_items=({"self_ref": "#/texts/1", "label": "text"},),
                ),
            ),
            glossary_slug="integrated-system-plan",
            glossary_title="Integrated System Plan",
            glossary_definition=(
                "The Integrated System Plan fixture represents an AEMO major "
                "publication in the generated corpus."
            ),
        ),
        FixturePublication(
            filename="2025-electricity-statement-of-opportunities-fixture.pdf",
            document_family_id="electricity-statement-of-opportunities",
            document_title="2025 Electricity Statement of Opportunities Fixture",
            document_kind="major-publication",
            document_version="2025 fixture",
            document_version_id="fixture-2025-esoo",
            published_date="2025-08-28",
            effective_date="2025-08-28",
            source_url=(
                "https://aemo.com.au/energy-systems/major-publications/"
                "electricity-statement-of-opportunities"
            ),
            source_page_url=(
                "https://aemo.com.au/energy-systems/major-publications/"
                "electricity-statement-of-opportunities"
            ),
            source_page_title="Electricity Statement of Opportunities",
            source_link_text="2025 Electricity Statement of Opportunities fixture",
            source_bytes=(
                b"%PDF-1.7\n"
                b"AEMO 2025 Electricity Statement of Opportunities fixture bytes.\n"
            ),
            silver_markdown=(
                "# 2025 Electricity Statement of Opportunities Fixture\n\n"
                "The Electricity Statement of Opportunities fixture describes a "
                "reliability and supply outlook publication. It keeps the AEMO "
                "major publications corpus build local, repeatable, and independent "
                "of live AEMO ETL metadata.\n"
            ),
            chunks=(
                ExtractedHybridChunk(
                    text=(
                        "The Electricity Statement of Opportunities fixture is an "
                        "AEMO major publication used for repeatable corpus checks."
                    ),
                    heading_path=(
                        "Electricity Statement of Opportunities",
                        "Fixture Scope",
                    ),
                    doc_items=({"self_ref": "#/texts/1", "label": "text"},),
                ),
            ),
            glossary_slug="electricity-statement-of-opportunities",
            glossary_title="Electricity Statement of Opportunities",
            glossary_definition=(
                "The Electricity Statement of Opportunities fixture represents an "
                "AEMO major publication in the generated corpus."
            ),
        ),
    )


def build_fixture_manifest_rows(
    paths: AemoPublicationCorpusPaths,
    *,
    publications: Sequence[FixturePublication] | None = None,
) -> list[dict[str, ManifestJsonValue]]:
    """Return deterministic bronze manifest rows for fixture publications."""
    rows = [
        _manifest_row(publication, paths=paths)
        for publication in (publications or fixture_publications())
    ]
    rows.sort(
        key=lambda row: (
            cast(str, row["document_identity"]),
            cast(str, row["source_url"]),
        )
    )
    return rows


def write_fixture_manifest(
    paths: AemoPublicationCorpusPaths,
    *,
    publications: Sequence[FixturePublication] | None = None,
) -> FixtureManifestResult:
    """Write the fixture bronze source manifest."""
    manifest_rows = build_fixture_manifest_rows(
        paths,
        publications=publications,
    )
    paths.source_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    paths.source_manifest_path.write_text(
        dump_source_manifest_jsonl(manifest_rows),
        encoding="utf-8",
    )
    return FixtureManifestResult(
        output_path=paths.source_manifest_path,
        row_count=len(manifest_rows),
    )


def write_fixture_source_cache(
    paths: AemoPublicationCorpusPaths,
    *,
    publications: Sequence[FixturePublication] | None = None,
) -> tuple[Path, ...]:
    """Write deterministic fixture source bytes to the bronze source cache."""
    cache_paths: list[Path] = []
    for publication in publications or fixture_publications():
        content_sha256 = _source_sha256(publication.source_bytes)
        cache_path = source_pdf_cache_path(
            content_sha256,
            cache_dir=paths.source_cache_dir,
        )
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_bytes(publication.source_bytes)
        cache_paths.append(cache_path)
    return tuple(cache_paths)


def build_fixture_corpus(
    *,
    artifact_root: Path | None = None,
    source_manifest_path: Path | None = None,
    source_cache_dir: Path | None = None,
    silver_documents_dir: Path | None = None,
    silver_chunks_dir: Path | None = None,
    silver_index_path: Path | None = None,
    gold_dir: Path | None = None,
    min_text_chars: int = DEFAULT_MIN_TEXT_CHARS,
    publications: Sequence[FixturePublication] | None = None,
) -> FixtureCorpusBuildResult:
    """Build the fixture AEMO major publications bronze/silver/gold corpus."""
    effective_publications = publications or fixture_publications()
    paths = default_corpus_paths(
        artifact_root=artifact_root,
        source_manifest_path=source_manifest_path,
        source_cache_dir=source_cache_dir,
        silver_documents_dir=silver_documents_dir,
        silver_chunks_dir=silver_chunks_dir,
        silver_index_path=silver_index_path,
        gold_dir=gold_dir,
    )
    manifest_result = write_fixture_manifest(
        paths,
        publications=effective_publications,
    )
    write_fixture_source_cache(paths, publications=effective_publications)
    silver_document_result = extract_silver_documents(
        extractor=FixtureMarkdownExtractor(effective_publications),
        manifest_path=paths.source_manifest_path,
        cache_dir=paths.source_cache_dir,
        output_dir=paths.silver_documents_dir,
        min_text_chars=min_text_chars,
        display_path=paths.layout.display_path,
    )
    silver_index_result = build_silver_index(
        extractor=FixtureHybridChunkExtractor(effective_publications),
        manifest_path=paths.source_manifest_path,
        cache_dir=paths.source_cache_dir,
        document_dir=paths.silver_documents_dir,
        chunk_dir=paths.silver_chunks_dir,
        index_path=paths.silver_index_path,
        min_text_chars=min_text_chars,
        display_path=paths.layout.display_path,
    )
    if silver_document_result.errors or silver_index_result.errors:
        raise FixtureCorpusBuildError(
            "fixture silver build failed; inspect silver document and index errors"
        )

    gold_page_count = write_fixture_gold_pages(
        paths,
        publications=effective_publications,
    )
    silver_validation_result = validate_silver_index(
        manifest_path=paths.source_manifest_path,
        cache_dir=paths.source_cache_dir,
        document_dir=paths.silver_documents_dir,
        chunk_dir=paths.silver_chunks_dir,
        index_path=paths.silver_index_path,
        min_text_chars=min_text_chars,
        resolve_display_path=paths.layout.path_from_display,
    )
    gold_validation_result = validate_gold_context(
        gold_dir=paths.gold_dir,
        index_path=paths.silver_index_path,
        display_path=paths.layout.display_path,
        resolve_display_path=paths.layout.path_from_display,
    )
    return FixtureCorpusBuildResult(
        paths=paths,
        manifest_result=manifest_result,
        silver_document_result=silver_document_result,
        silver_index_result=silver_index_result,
        silver_validation_result=silver_validation_result,
        gold_validation_result=gold_validation_result,
        gold_page_count=gold_page_count,
    )


def write_fixture_gold_pages(
    paths: AemoPublicationCorpusPaths,
    *,
    publications: Sequence[FixturePublication] | None = None,
) -> int:
    """Write cited fixture gold glossary pages from the silver index."""
    index_rows = _index_rows(paths.silver_index_path)
    rows_by_family = _first_index_row_by_family(index_rows)
    effective_publications = publications or fixture_publications()

    readme_path = paths.gold_dir / "README.md"
    glossary_index_path = paths.gold_dir / "glossary" / "README.md"
    page_paths: list[Path] = []
    for publication in effective_publications:
        row = rows_by_family.get(publication.document_family_id)
        if row is None:
            raise FixtureCorpusBuildError(
                f"silver index missing fixture row for {publication.document_family_id}"
            )
        page_path = paths.gold_dir / "glossary" / f"{publication.glossary_slug}.md"
        _write_gold_glossary_page(
            page_path,
            row,
            publication=publication,
            paths=paths,
        )
        page_paths.append(page_path)

    _write_gold_navigation(readme_path, paths=paths)
    _write_gold_glossary_index(
        glossary_index_path,
        page_paths=tuple(page_paths),
        paths=paths,
    )
    return len(page_paths) + 2


def _manifest_row(
    publication: FixturePublication,
    *,
    paths: AemoPublicationCorpusPaths,
) -> dict[str, ManifestJsonValue]:
    content_sha256 = _source_sha256(publication.source_bytes)
    identity = document_identity(
        corpus_source=FIXTURE_CORPUS_SOURCE,
        document_family_id=publication.document_family_id,
        content_sha256=content_sha256,
    )
    fixture_uri = f"fixture://{FIXTURE_CORPUS_SOURCE}/{publication.filename}"
    return SourceManifestRow(
        schema_version=MANIFEST_SCHEMA_VERSION,
        document_identity=identity,
        content_sha256=content_sha256,
        corpus_source=FIXTURE_CORPUS_SOURCE,
        document_family_id=publication.document_family_id,
        document_title=publication.document_title,
        document_kind=publication.document_kind,
        document_version=publication.document_version,
        document_version_id=publication.document_version_id,
        published_date=publication.published_date,
        effective_date=publication.effective_date,
        media_revision="fixture-v1",
        source_url=publication.source_url,
        resolved_url=publication.source_url,
        source_page_url=publication.source_page_url,
        source_page_title=publication.source_page_title,
        source_link_text=publication.source_link_text,
        archive_uri=fixture_uri,
        storage_uri=fixture_uri,
        target_s3_key=f"fixtures/{FIXTURE_CORPUS_SOURCE}/{publication.filename}",
        content_length=len(publication.source_bytes),
        generated_paths=paths.generated_paths(identity),
    ).as_dict()


def _source_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _index_rows(index_path: Path) -> tuple[Mapping[str, object], ...]:
    if not index_path.exists():
        raise FixtureCorpusBuildError(f"silver index not found: {index_path}")
    rows: list[Mapping[str, object]] = []
    for line_number, line in enumerate(
        index_path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip():
            continue
        payload = json.loads(line)
        if not isinstance(payload, Mapping):
            raise FixtureCorpusBuildError(
                f"{index_path}:{line_number} must contain a JSON object"
            )
        rows.append(cast(Mapping[str, object], payload))
    return tuple(rows)


def _first_index_row_by_family(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, Mapping[str, object]]:
    rows_by_family: dict[str, Mapping[str, object]] = {}
    for row in rows:
        family = _required_text(row, "document_family_id")
        rows_by_family.setdefault(family, row)
    return rows_by_family


def _write_gold_navigation(
    readme_path: Path,
    *,
    paths: AemoPublicationCorpusPaths,
) -> None:
    _write_text(
        readme_path,
        render_gold_markdown_page(
            frontmatter={
                "schema_version": GOLD_SCHEMA_VERSION,
                "context_type": "navigation",
                "title": "AEMO Major Publications Corpus",
                "generated_path": paths.layout.display_path(readme_path),
            },
            body=(
                "# AEMO Major Publications Corpus\n\n"
                "Use the glossary index to inspect fixture publication context.\n"
            ),
        ),
    )


def _write_gold_glossary_index(
    glossary_index_path: Path,
    *,
    page_paths: Sequence[Path],
    paths: AemoPublicationCorpusPaths,
) -> None:
    links = [
        f"- [{_title_from_slug(page_path.stem)}]({page_path.name})"
        for page_path in sorted(page_paths)
    ]
    _write_text(
        glossary_index_path,
        render_gold_markdown_page(
            frontmatter={
                "schema_version": GOLD_SCHEMA_VERSION,
                "context_type": "glossary-index",
                "title": "Glossary",
                "generated_path": paths.layout.display_path(glossary_index_path),
            },
            body=f"# Glossary\n\n{'\n'.join(links)}\n",
        ),
    )


def _write_gold_glossary_page(
    page_path: Path,
    row: Mapping[str, object],
    *,
    publication: FixturePublication,
    paths: AemoPublicationCorpusPaths,
) -> None:
    chunk_id = _required_text(row, "chunk_id")
    source_hash = _required_text(row, "content_sha256")
    chunk_path = paths.layout.path_from_display(_required_text(row, "path"))
    source_document_path = paths.layout.path_from_display(
        _required_text(row, "source_document_markdown_path")
    )
    citation = GoldSourceCitation(
        chunk_id=chunk_id,
        chunk_path=_markdown_link_target(chunk_path, page_path=page_path),
        source_document_path=_markdown_link_target(
            source_document_path,
            page_path=page_path,
        ),
        source_hash=source_hash,
    )
    _write_text(
        page_path,
        render_gold_markdown_page(
            frontmatter={
                "schema_version": GOLD_SCHEMA_VERSION,
                "context_type": "glossary-page",
                "title": publication.glossary_title,
                "slug": publication.glossary_slug,
                "generated_path": paths.layout.display_path(page_path),
                "source_chunk_ids": [chunk_id],
                "source_hashes": [source_hash],
                "related_concepts": [],
            },
            body=render_gold_glossary_body(
                title=publication.glossary_title,
                definition=(
                    f"{publication.glossary_definition} "
                    f"[[chunk:{chunk_id}]] [[source:sha256:{source_hash}]]"
                ),
                source_citations=[citation],
            ),
        ),
    )


def _markdown_link_target(target_path: Path, *, page_path: Path) -> str:
    try:
        return (
            target_path.resolve()
            .relative_to(
                page_path.parent.resolve(),
                walk_up=True,
            )
            .as_posix()
        )
    except ValueError:
        return target_path.resolve().as_posix()


def _required_text(row: Mapping[str, object], key: str) -> str:
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise FixtureCorpusBuildError(f"index row missing non-empty {key}")
    return value


def _title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
