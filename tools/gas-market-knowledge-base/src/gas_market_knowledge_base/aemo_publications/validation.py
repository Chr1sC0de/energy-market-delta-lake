"""Validation reporting for the AEMO major publications corpus."""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from gas_market_knowledge_base.aemo_publications.corpus_paths import (
    AemoPublicationCorpusPaths,
    default_corpus_paths,
)
from gas_market_knowledge_base.aemo_publications.source_manifest import (
    AEMO_GSOO_CORPUS_SOURCE,
    AEMO_GSOO_URL,
    AEMO_MAJOR_PUBLICATIONS_HUB_URL,
    AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL,
    AEMO_WA_GSOO_CORPUS_SOURCE,
    AEMO_WA_GSOO_URL,
)
from gas_market_knowledge_base.corpus_core.gold_context import (
    GoldContextValidationResult,
    validate_gold_context,
)
from gas_market_knowledge_base.corpus_core.paths import source_pdf_cache_path
from gas_market_knowledge_base.corpus_core.silver_chunks import (
    SilverIndexValidationResult,
    validate_silver_index,
)
from gas_market_knowledge_base.corpus_core.silver_documents import (
    DEFAULT_MIN_TEXT_CHARS,
    SilverExtractionInputError,
)


@dataclass(frozen=True, slots=True)
class AemoPublicationCoverageSummary:
    """Coverage counts for AEMO major publications source rows."""

    manifest_row_count: int
    hub_source_family_count: int
    library_source_family_count: int
    gsoo_source_family_count: int
    wa_gsoo_source_family_count: int
    supported_media_count: int
    unsupported_media_count: int
    review_needed_count: int


@dataclass(frozen=True, slots=True)
class AemoPublicationCorpusValidationResult:
    """Result of one AEMO major publications corpus validation run."""

    paths: AemoPublicationCorpusPaths
    coverage: AemoPublicationCoverageSummary
    silver_result: SilverIndexValidationResult | None
    gold_result: GoldContextValidationResult | None
    errors: tuple[str, ...]

    @property
    def error_count(self) -> int:
        """Return the total validation error count."""
        return len(self.errors)


def validate_aemo_publications_corpus(
    *,
    paths: AemoPublicationCorpusPaths | None = None,
    min_text_chars: int = DEFAULT_MIN_TEXT_CHARS,
) -> AemoPublicationCorpusValidationResult:
    """Validate AEMO major publications coverage and corpus artifacts."""
    effective_paths = paths or default_corpus_paths()
    manifest_rows, manifest_errors = _load_manifest_rows(
        effective_paths.source_manifest_path
    )
    coverage = _coverage_summary(manifest_rows)
    errors = list(manifest_errors)
    errors.extend(_source_file_errors(manifest_rows, paths=effective_paths))

    silver_result: SilverIndexValidationResult | None = None
    gold_result: GoldContextValidationResult | None = None
    if effective_paths.source_manifest_path.exists():
        try:
            silver_result = validate_silver_index(
                manifest_path=effective_paths.source_manifest_path,
                cache_dir=effective_paths.source_cache_dir,
                document_dir=effective_paths.silver_documents_dir,
                chunk_dir=effective_paths.silver_chunks_dir,
                index_path=effective_paths.silver_index_path,
                min_text_chars=min_text_chars,
                resolve_display_path=effective_paths.layout.path_from_display,
            )
        except SilverExtractionInputError as e:
            errors.append(f"source manifest validation failed: {e}")
        else:
            errors.extend(silver_result.errors)

        gold_result = validate_gold_context(
            gold_dir=effective_paths.gold_dir,
            index_path=effective_paths.silver_index_path,
            display_path=effective_paths.layout.display_path,
            resolve_display_path=effective_paths.layout.path_from_display,
        )
        errors.extend(gold_result.errors)

    return AemoPublicationCorpusValidationResult(
        paths=effective_paths,
        coverage=coverage,
        silver_result=silver_result,
        gold_result=gold_result,
        errors=tuple(errors),
    )


def _load_manifest_rows(path: Path) -> tuple[list[Mapping[str, object]], list[str]]:
    if not path.exists():
        return [], [f"downloaded metadata missing: source manifest not found at {path}"]

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return [], [f"downloaded metadata unreadable: failed to read {path}: {e}"]

    rows: list[Mapping[str, object]] = []
    errors: list[str] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(
                f"downloaded metadata malformed: {path}:{line_number}: {e.msg}"
            )
            continue
        if not isinstance(payload, Mapping):
            errors.append(
                f"downloaded metadata malformed: {path}:{line_number} "
                "must contain a JSON object"
            )
            continue
        rows.append(cast(Mapping[str, object], payload))

    if not rows and not errors:
        errors.append(
            f"downloaded metadata missing: source manifest has no rows at {path}"
        )
    return rows, errors


def _coverage_summary(
    rows: list[Mapping[str, object]],
) -> AemoPublicationCoverageSummary:
    hub_families: set[str] = set()
    library_families: set[str] = set()
    gsoo_families: set[str] = set()
    wa_gsoo_families: set[str] = set()
    supported_media_count = 0
    unsupported_media_count = 0
    review_needed_count = 0

    for row in rows:
        corpus_source = _optional_text(row, "corpus_source")
        family_id = _optional_text(row, "document_family_id")
        source_page_url = _optional_text(row, "source_page_url")
        if family_id is not None and source_page_url is not None:
            source_family = _source_family(source_page_url, corpus_source=corpus_source)
            if source_family == "hub":
                hub_families.add(family_id)
            elif source_family == "library":
                library_families.add(family_id)
            elif source_family == "gsoo":
                gsoo_families.add(family_id)
            elif source_family == "wa_gsoo":
                wa_gsoo_families.add(family_id)

        review_status = _optional_text(row, "review_status")
        include_decision = _optional_text(row, "include_decision")
        if include_decision == "include" and review_status == "ready":
            supported_media_count += 1
        elif review_status == "unsupported_media_type":
            unsupported_media_count += 1

        if include_decision == "needs_human_review" or (
            review_status is not None and review_status != "ready"
        ):
            review_needed_count += 1

    return AemoPublicationCoverageSummary(
        manifest_row_count=len(rows),
        hub_source_family_count=len(hub_families),
        library_source_family_count=len(library_families),
        gsoo_source_family_count=len(gsoo_families),
        wa_gsoo_source_family_count=len(wa_gsoo_families),
        supported_media_count=supported_media_count,
        unsupported_media_count=unsupported_media_count,
        review_needed_count=review_needed_count,
    )


def _source_file_errors(
    rows: list[Mapping[str, object]],
    *,
    paths: AemoPublicationCorpusPaths,
) -> list[str]:
    errors: list[str] = []
    for row_number, row in enumerate(rows, 1):
        if _optional_text(row, "include_decision") != "include":
            continue
        if _optional_text(row, "review_status") != "ready":
            continue
        content_sha256 = _optional_text(row, "content_sha256")
        if content_sha256 is None:
            errors.append(
                "missing source file metadata: "
                f"manifest row {row_number} has no content_sha256"
            )
            continue
        source_path = source_pdf_cache_path(
            content_sha256,
            cache_dir=paths.source_cache_dir,
        )
        if not source_path.exists():
            errors.append(
                f"missing source file: manifest row {row_number} expected cached PDF "
                f"at {source_path}"
            )
    return errors


def _source_family(source_page_url: str, *, corpus_source: str | None) -> str | None:
    normalized = source_page_url.rstrip("/") + "/"
    if normalized.startswith(AEMO_GSOO_URL.rstrip("/") + "/"):
        return "gsoo"
    if normalized.startswith(AEMO_WA_GSOO_URL.rstrip("/") + "/"):
        return "wa_gsoo"
    if normalized.startswith(AEMO_MAJOR_PUBLICATIONS_HUB_URL):
        return "hub"
    if normalized.startswith(AEMO_MAJOR_PUBLICATIONS_LIBRARY_URL.rstrip("/") + "/"):
        return "library"
    if corpus_source is None or corpus_source == "major_publications":
        return None
    if corpus_source == AEMO_GSOO_CORPUS_SOURCE:
        return "gsoo"
    if corpus_source == AEMO_WA_GSOO_CORPUS_SOURCE:
        return "wa_gsoo"
    return None


def _optional_text(row: Mapping[str, object], key: str) -> str | None:
    value = row.get(key)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    return normalized or None
