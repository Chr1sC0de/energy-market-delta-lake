"""Gold Market context page citation validation."""

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast
from urllib.parse import unquote, urlparse

from gas_market_knowledge_base.corpus_paths import (
    default_gold_dir,
    default_silver_index_path,
    display_path,
    path_from_display,
)

GOLD_SCHEMA_VERSION = 1

_FRONTMATTER_PREFIX = "---\n"
_FRONTMATTER_SUFFIX = "\n---\n"
_CHUNK_TOKEN_PATTERN = re.compile(r"\[\[chunk:([A-Za-z0-9_.:-]+)\]\]")
_SOURCE_TOKEN_PATTERN = re.compile(r"\[\[source:sha256:([a-f0-9]{64})\]\]")
_ANY_CHUNK_TOKEN_PATTERN = re.compile(r"\[\[chunk:([^\]]*)\]\]")
_ANY_SOURCE_TOKEN_PATTERN = re.compile(r"\[\[source:([^\]]*)\]\]")
_MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
_SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")
_GLOSSARY_PAGE_TYPE = "glossary-page"
_GLOSSARY_INDEX_PATH = Path("glossary/README.md")
_CLAIM_SECTIONS = frozenset({"definition"})
_REQUIRED_FRONTMATTER_FIELDS = frozenset(
    {
        "schema_version",
        "context_type",
        "title",
        "generated_path",
    }
)
_REQUIRED_GLOSSARY_FRONTMATTER_FIELDS = _REQUIRED_FRONTMATTER_FIELDS | frozenset(
    {
        "slug",
        "source_chunk_ids",
        "source_hashes",
        "related_concepts",
    }
)


@dataclass(frozen=True, slots=True)
class GoldContextValidationResult:
    """Result of one gold Market context validation run."""

    gold_dir: Path
    index_path: Path
    page_count: int
    glossary_page_count: int
    errors: tuple[str, ...]

    @property
    def error_count(self) -> int:
        """Return the number of validation errors."""
        return len(self.errors)


@dataclass(frozen=True, slots=True)
class GoldSourceCitation:
    """Source citation entry for a gold Market context glossary page."""

    chunk_id: str
    chunk_path: str
    source_document_path: str
    source_hash: str


def render_gold_markdown_page(
    *,
    frontmatter: Mapping[str, object],
    body: str,
) -> str:
    """Render a gold Market context Markdown page with JSON frontmatter."""
    return (
        f"{_FRONTMATTER_PREFIX}"
        f"{json.dumps(frontmatter, indent=2, sort_keys=True)}"
        f"{_FRONTMATTER_SUFFIX}\n"
        f"{body.strip()}\n"
    )


def render_gold_glossary_body(
    *,
    title: str,
    definition: str,
    source_citations: Sequence[GoldSourceCitation],
    related_concepts: Sequence[tuple[str, str]] = (),
) -> str:
    """Render a gold glossary page body with flush-left Markdown blocks."""
    citation_block = "\n".join(
        render_gold_source_citation(citation) for citation in source_citations
    )
    if related_concepts:
        related_concept_block = "\n".join(
            f"- [{label.strip()}]({target.strip()})"
            for label, target in related_concepts
        )
    else:
        related_concept_block = "- None yet."
    return (
        f"# {title.strip()}\n\n"
        f"## Definition\n\n"
        f"{definition.strip()}\n\n"
        f"## Source Citations\n\n"
        f"{citation_block}\n\n"
        f"## Related Concepts\n\n"
        f"{related_concept_block}\n"
    )


def render_gold_source_citation(citation: GoldSourceCitation) -> str:
    """Render one flush-left source citation bullet."""
    return (
        f"- `{citation.chunk_id.strip()}`: "
        f"[silver chunk]({citation.chunk_path.strip()}) "
        f"from [source document]({citation.source_document_path.strip()}); "
        f"source hash `sha256:{citation.source_hash.strip()}`. "
        f"[[chunk:{citation.chunk_id.strip()}]] "
        f"[[source:sha256:{citation.source_hash.strip()}]]"
    )


def gold_dir_for_index_path(index_path: Path) -> Path:
    """Return the gold directory beside a silver chunk index path."""
    try:
        generated_root = index_path.parent.parent.parent
    except IndexError:
        return default_gold_dir()
    return generated_root / "gold"


def validate_gold_context(
    *,
    gold_dir: Path | None = None,
    index_path: Path | None = None,
) -> GoldContextValidationResult:
    """Validate gold Market context pages against the silver chunk index."""
    effective_index_path = index_path or default_silver_index_path()
    effective_gold_dir = gold_dir or gold_dir_for_index_path(effective_index_path)
    page_paths = _gold_page_paths(effective_gold_dir)
    if not page_paths:
        return GoldContextValidationResult(
            gold_dir=effective_gold_dir,
            index_path=effective_index_path,
            page_count=0,
            glossary_page_count=0,
            errors=(),
        )

    chunk_rows, chunk_errors = _load_chunk_rows(effective_index_path)
    chunk_rows_by_id = {
        cast(str, row["chunk_id"]): row
        for row in chunk_rows
        if isinstance(row.get("chunk_id"), str)
    }
    indexed_source_hashes = {
        cast(str, row["content_sha256"])
        for row in chunk_rows
        if isinstance(row.get("content_sha256"), str)
    }
    errors = list(chunk_errors)
    glossary_pages: dict[str, Path] = {}
    glossary_index_path = effective_gold_dir / _GLOSSARY_INDEX_PATH

    for page_path in page_paths:
        frontmatter, body, read_errors = _read_markdown_frontmatter(page_path)
        errors.extend(read_errors)
        if frontmatter is None:
            continue

        context_type = _optional_text(frontmatter, "context_type")
        source_chunk_ids = _string_sequence(frontmatter.get("source_chunk_ids"))
        if context_type == _GLOSSARY_PAGE_TYPE:
            slug = _optional_text(frontmatter, "slug")
            if slug is not None:
                glossary_pages[slug] = page_path

        errors.extend(_markdown_rendering_errors(body, page_path=page_path))
        errors.extend(
            _frontmatter_errors(
                frontmatter,
                page_path=page_path,
                chunk_rows_by_id=chunk_rows_by_id,
                indexed_source_hashes=indexed_source_hashes,
            )
        )
        errors.extend(
            _body_citation_errors(
                body,
                page_path=page_path,
                context_type=context_type,
                chunk_rows_by_id=chunk_rows_by_id,
                indexed_source_hashes=indexed_source_hashes,
            )
        )
        if context_type == _GLOSSARY_PAGE_TYPE:
            errors.extend(
                _source_citation_section_errors(
                    body,
                    page_path=page_path,
                    source_chunk_ids=source_chunk_ids,
                    chunk_rows_by_id=chunk_rows_by_id,
                )
            )
        errors.extend(_markdown_link_errors(body, page_path=page_path))

    if glossary_pages:
        errors.extend(
            _glossary_index_errors(
                glossary_index_path=glossary_index_path,
                glossary_pages=glossary_pages,
            )
        )
        errors.extend(
            _related_concept_errors(
                page_paths=page_paths,
                glossary_pages=glossary_pages,
            )
        )

    return GoldContextValidationResult(
        gold_dir=effective_gold_dir,
        index_path=effective_index_path,
        page_count=len(page_paths),
        glossary_page_count=len(glossary_pages),
        errors=tuple(errors),
    )


def _gold_page_paths(gold_dir: Path) -> tuple[Path, ...]:
    if not gold_dir.exists():
        return ()
    return tuple(sorted(path for path in gold_dir.rglob("*.md") if path.is_file()))


def _load_chunk_rows(index_path: Path) -> tuple[list[Mapping[str, object]], list[str]]:
    if not index_path.exists():
        return [], [f"silver chunk index missing for gold validation: {index_path}"]
    rows: list[Mapping[str, object]] = []
    errors: list[str] = []
    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return [], [f"failed to read silver chunk index {index_path}: {e}"]

    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"{index_path}:{line_number} is not valid JSON: {e.msg}")
            continue
        if not isinstance(payload, Mapping):
            errors.append(f"{index_path}:{line_number} must contain a JSON object")
            continue
        rows.append(cast(Mapping[str, object], payload))
    return rows, errors


def _read_markdown_frontmatter(
    path: Path,
) -> tuple[Mapping[str, object] | None, str, list[str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        return None, "", [f"failed to read gold page {path}: {e}"]
    if not text.startswith(_FRONTMATTER_PREFIX):
        return None, text, [f"{path} missing frontmatter"]
    end_index = text.find(_FRONTMATTER_SUFFIX, len(_FRONTMATTER_PREFIX))
    if end_index == -1:
        return None, text, [f"{path} missing frontmatter terminator"]
    payload_text = text[len(_FRONTMATTER_PREFIX) : end_index].strip()
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as e:
        return None, text, [f"{path} frontmatter is not valid JSON: {e.msg}"]
    if not isinstance(payload, Mapping):
        return None, text, [f"{path} frontmatter must contain a JSON object"]
    body = text[end_index + len(_FRONTMATTER_SUFFIX) :]
    return cast(Mapping[str, object], payload), body, []


def _frontmatter_errors(
    frontmatter: Mapping[str, object],
    *,
    page_path: Path,
    chunk_rows_by_id: Mapping[str, Mapping[str, object]],
    indexed_source_hashes: set[str],
) -> list[str]:
    errors: list[str] = []
    context_type = _optional_text(frontmatter, "context_type")
    required_fields = (
        _REQUIRED_GLOSSARY_FRONTMATTER_FIELDS
        if context_type == _GLOSSARY_PAGE_TYPE
        else _REQUIRED_FRONTMATTER_FIELDS
    )
    missing_fields = sorted(
        field for field in required_fields if field not in frontmatter
    )
    if missing_fields:
        errors.append(
            f"{page_path} frontmatter missing required fields: "
            f"{', '.join(missing_fields)}"
        )
    if frontmatter.get("schema_version") != GOLD_SCHEMA_VERSION:
        errors.append(
            f"{page_path} frontmatter schema_version must be {GOLD_SCHEMA_VERSION}"
        )

    generated_path = _optional_text(frontmatter, "generated_path")
    if generated_path is not None and generated_path != _display_path(page_path):
        errors.append(
            f"{page_path} generated_path {generated_path!r} does not match page path"
        )

    source_chunk_ids = _string_sequence(frontmatter.get("source_chunk_ids"))
    source_hashes = _string_sequence(frontmatter.get("source_hashes"))
    if context_type == _GLOSSARY_PAGE_TYPE:
        if not source_chunk_ids:
            errors.append(f"{page_path} frontmatter missing source_chunk_ids")
        if not source_hashes:
            errors.append(f"{page_path} frontmatter missing source_hashes")

    expected_source_hashes: set[str] = set()
    for chunk_id in source_chunk_ids:
        chunk_row = chunk_rows_by_id.get(chunk_id)
        if chunk_row is None:
            errors.append(f"{page_path} references unknown silver chunk {chunk_id!r}")
            continue
        source_hash = _optional_text(chunk_row, "content_sha256")
        if source_hash is not None:
            expected_source_hashes.add(source_hash)
        chunk_path = _optional_text(chunk_row, "path")
        if chunk_path is None:
            errors.append(f"{page_path} chunk {chunk_id!r} missing path in index")
        elif not _path_from_display(chunk_path).exists():
            errors.append(
                f"{page_path} chunk {chunk_id!r} target missing: "
                f"{_path_from_display(chunk_path)}"
            )
        source_document_path = _optional_text(
            chunk_row, "source_document_markdown_path"
        )
        if source_document_path is None:
            errors.append(
                f"{page_path} chunk {chunk_id!r} missing "
                "source_document_markdown_path in index"
            )
        elif not _path_from_display(source_document_path).exists():
            errors.append(
                f"{page_path} chunk {chunk_id!r} source document target missing: "
                f"{_path_from_display(source_document_path)}"
            )

    for source_hash in source_hashes:
        if not _SHA256_PATTERN.fullmatch(source_hash):
            errors.append(f"{page_path} source hash {source_hash!r} is not SHA-256")
        elif source_hash not in indexed_source_hashes:
            errors.append(f"{page_path} source hash {source_hash!r} is not indexed")

    missing_source_hashes = sorted(expected_source_hashes.difference(source_hashes))
    if missing_source_hashes:
        errors.append(
            f"{page_path} missing source hashes for cited chunks: "
            f"{', '.join(missing_source_hashes)}"
        )
    return errors


def _body_citation_errors(
    body: str,
    *,
    page_path: Path,
    context_type: str | None,
    chunk_rows_by_id: Mapping[str, Mapping[str, object]],
    indexed_source_hashes: set[str],
) -> list[str]:
    errors: list[str] = []
    chunk_tokens = _CHUNK_TOKEN_PATTERN.findall(body)
    source_tokens = _SOURCE_TOKEN_PATTERN.findall(body)

    for raw_chunk_token in _ANY_CHUNK_TOKEN_PATTERN.findall(body):
        if raw_chunk_token not in chunk_tokens:
            errors.append(
                f"{page_path} has malformed chunk citation {raw_chunk_token!r}"
            )
    for raw_source_token in _ANY_SOURCE_TOKEN_PATTERN.findall(body):
        if raw_source_token.removeprefix("sha256:") not in source_tokens:
            errors.append(
                f"{page_path} has malformed source citation {raw_source_token!r}"
            )

    for chunk_id in sorted(set(chunk_tokens)):
        chunk_row = chunk_rows_by_id.get(chunk_id)
        if chunk_row is None:
            errors.append(
                f"{page_path} body references unknown silver chunk {chunk_id!r}"
            )
            continue
        chunk_path = _optional_text(chunk_row, "path")
        if chunk_path is None:
            errors.append(f"{page_path} chunk {chunk_id!r} missing path in index")
        elif not _path_from_display(chunk_path).exists():
            errors.append(
                f"{page_path} chunk {chunk_id!r} target missing: "
                f"{_path_from_display(chunk_path)}"
            )

    for source_hash in sorted(set(source_tokens)):
        if source_hash not in indexed_source_hashes:
            errors.append(
                f"{page_path} body source hash {source_hash!r} is not indexed"
            )

    if context_type == _GLOSSARY_PAGE_TYPE:
        errors.extend(_uncited_claim_errors(body, page_path=page_path))
    return errors


def _markdown_rendering_errors(body: str, *, page_path: Path) -> list[str]:
    errors: list[str] = []
    for line_number, line in enumerate(body.splitlines(), 1):
        if not line:
            continue
        stripped = line.lstrip(" \t")
        if _is_atx_heading(stripped) and line != stripped:
            if line.startswith("\t"):
                errors.append(
                    f"{page_path}:{line_number} has tab-indented ATX heading; "
                    "headings must start at column 1"
                )
            else:
                errors.append(
                    f"{page_path}:{line_number} has indented ATX heading; "
                    "headings must start at column 1"
                )
            continue
        if line.startswith("\t"):
            errors.append(
                f"{page_path}:{line_number} has tab-indented gold Markdown body "
                "line; normal content must start at column 1"
            )
            continue
        if line.startswith("    "):
            if stripped.startswith("- "):
                errors.append(
                    f"{page_path}:{line_number} has indented Markdown list "
                    "bullet; bullets must start at column 1"
                )
            else:
                errors.append(
                    f"{page_path}:{line_number} has indented gold Markdown body "
                    "line; normal paragraphs must start at column 1"
                )
    return errors


def _source_citation_section_errors(
    body: str,
    *,
    page_path: Path,
    source_chunk_ids: Sequence[str],
    chunk_rows_by_id: Mapping[str, Mapping[str, object]],
) -> list[str]:
    found_section, section_lines = _markdown_section_lines(
        body,
        section_slug="source-citations",
    )
    if not found_section:
        return [f"{page_path} missing Source Citations section"]

    errors: list[str] = []
    citation_lines = [
        (line_number, line) for line_number, line in section_lines if line.strip()
    ]
    if not citation_lines:
        return [f"{page_path} Source Citations section has no citation bullets"]

    expected_chunk_ids = set(source_chunk_ids)
    cited_chunk_ids: set[str] = set()
    for line_number, line in citation_lines:
        stripped = line.strip()
        if line != stripped:
            errors.append(
                f"{page_path}:{line_number} has indented source citation bullet; "
                "citation bullets must start at column 1"
            )
        if not stripped.startswith("- "):
            errors.append(
                f"{page_path}:{line_number} has malformed source citation list "
                "entry; expected a '- ' bullet"
            )
            continue

        bullet_chunk_ids = _CHUNK_TOKEN_PATTERN.findall(stripped)
        bullet_source_hashes = _SOURCE_TOKEN_PATTERN.findall(stripped)
        if len(bullet_chunk_ids) != 1:
            errors.append(
                f"{page_path}:{line_number} source citation bullet must include "
                "exactly one chunk citation token"
            )
            continue
        if len(bullet_source_hashes) != 1:
            errors.append(
                f"{page_path}:{line_number} source citation bullet must include "
                "exactly one source hash token"
            )

        chunk_id = bullet_chunk_ids[0]
        if chunk_id in cited_chunk_ids:
            errors.append(
                f"{page_path}:{line_number} source citation bullet duplicates "
                f"chunk {chunk_id!r}"
            )
        cited_chunk_ids.add(chunk_id)
        if chunk_id not in expected_chunk_ids:
            errors.append(
                f"{page_path}:{line_number} source citation bullet references "
                f"chunk {chunk_id!r} not listed in source_chunk_ids"
            )

        chunk_row = chunk_rows_by_id.get(chunk_id)
        if chunk_row is None:
            continue
        errors.extend(
            _source_citation_target_errors(
                stripped,
                page_path=page_path,
                line_number=line_number,
                chunk_id=chunk_id,
                chunk_row=chunk_row,
                source_hashes=bullet_source_hashes,
            )
        )

    missing_citation_chunks = sorted(expected_chunk_ids.difference(cited_chunk_ids))
    if missing_citation_chunks:
        errors.append(
            f"{page_path} Source Citations section missing bullets for "
            f"source_chunk_ids: {', '.join(missing_citation_chunks)}"
        )
    return errors


def _source_citation_target_errors(
    line: str,
    *,
    page_path: Path,
    line_number: int,
    chunk_id: str,
    chunk_row: Mapping[str, object],
    source_hashes: Sequence[str],
) -> list[str]:
    errors: list[str] = []
    expected_source_hash = _optional_text(chunk_row, "content_sha256")
    if expected_source_hash is not None and source_hashes:
        source_hash = source_hashes[0]
        if source_hash != expected_source_hash:
            errors.append(
                f"{page_path}:{line_number} source citation bullet for "
                f"{chunk_id!r} uses source hash {source_hash!r}, expected "
                f"{expected_source_hash!r}"
            )

    linked_paths = {
        _resolve_markdown_link(target, page_path=page_path).resolve()
        for target in _MARKDOWN_LINK_PATTERN.findall(line)
        if not _is_external_or_anchor_link(target)
    }
    chunk_path = _optional_text(chunk_row, "path")
    if chunk_path is not None:
        expected_chunk_path = _path_from_display(chunk_path).resolve()
        if expected_chunk_path not in linked_paths:
            errors.append(
                f"{page_path}:{line_number} source citation bullet for "
                f"{chunk_id!r} missing link to indexed silver chunk"
            )

    source_document_path = _optional_text(chunk_row, "source_document_markdown_path")
    if source_document_path is None:
        errors.append(
            f"{page_path}:{line_number} source citation bullet for {chunk_id!r} "
            "has no indexed source document reference"
        )
    else:
        expected_source_document_path = _path_from_display(source_document_path)
        if not expected_source_document_path.exists():
            errors.append(
                f"{page_path}:{line_number} source citation bullet for "
                f"{chunk_id!r} has missing source document target: "
                f"{expected_source_document_path}"
            )
        elif expected_source_document_path.resolve() not in linked_paths:
            errors.append(
                f"{page_path}:{line_number} source citation bullet for "
                f"{chunk_id!r} missing link to indexed source document"
            )
    return errors


def _uncited_claim_errors(body: str, *, page_path: Path) -> list[str]:
    errors: list[str] = []
    current_section = ""
    for line_number, line in enumerate(body.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            current_section = _heading_slug(stripped)
            continue
        if current_section not in _CLAIM_SECTIONS:
            continue
        if _is_non_claim_line(stripped):
            continue
        has_chunk = bool(_CHUNK_TOKEN_PATTERN.search(stripped))
        has_source = bool(_SOURCE_TOKEN_PATTERN.search(stripped))
        if not has_chunk or not has_source:
            errors.append(
                f"{page_path}:{line_number} uncited factual claim; "
                "definition lines must cite a silver chunk and source hash"
            )
    return errors


def _markdown_link_errors(body: str, *, page_path: Path) -> list[str]:
    errors: list[str] = []
    for raw_target in _MARKDOWN_LINK_PATTERN.findall(body):
        target = raw_target.strip()
        if _is_external_or_anchor_link(target):
            continue
        target_path = _resolve_markdown_link(target, page_path=page_path)
        if not target_path.exists():
            errors.append(f"{page_path} has broken link target: {target}")
    return errors


def _glossary_index_errors(
    *,
    glossary_index_path: Path,
    glossary_pages: Mapping[str, Path],
) -> list[str]:
    frontmatter, body, read_errors = _read_markdown_frontmatter(glossary_index_path)
    if read_errors:
        return [f"glossary index error: {error}" for error in read_errors]
    if frontmatter is None:
        return [f"glossary index missing or malformed: {glossary_index_path}"]

    index_links = {
        _resolve_markdown_link(target, page_path=glossary_index_path).resolve()
        for target in _MARKDOWN_LINK_PATTERN.findall(body)
        if _is_glossary_markdown_target(target)
    }
    errors: list[str] = []
    for slug, page_path in sorted(glossary_pages.items()):
        if page_path.name == "README.md":
            continue
        if page_path.resolve() not in index_links:
            errors.append(
                f"{glossary_index_path} has stale glossary index; "
                f"missing link to {slug!r} at {page_path}"
            )
    return errors


def _related_concept_errors(
    *,
    page_paths: Sequence[Path],
    glossary_pages: Mapping[str, Path],
) -> list[str]:
    errors: list[str] = []
    for page_path in page_paths:
        frontmatter, _, read_errors = _read_markdown_frontmatter(page_path)
        if read_errors or frontmatter is None:
            continue
        if _optional_text(frontmatter, "context_type") != _GLOSSARY_PAGE_TYPE:
            continue
        for related_slug in _string_sequence(frontmatter.get("related_concepts")):
            if related_slug not in glossary_pages:
                errors.append(
                    f"{page_path} related concept {related_slug!r} has no glossary page"
                )
    return errors


def _is_non_claim_line(line: str) -> bool:
    return (
        line.startswith("|")
        or line.startswith("---")
        or line.startswith("[")
        or line.startswith("<!--")
    )


def _is_atx_heading(line: str) -> bool:
    return bool(re.match(r"^#{1,6}(?:\s|$)", line))


def _markdown_section_lines(
    body: str,
    *,
    section_slug: str,
) -> tuple[bool, tuple[tuple[int, str], ...]]:
    current_section = ""
    found_section = False
    section_lines: list[tuple[int, str]] = []
    for line_number, line in enumerate(body.splitlines(), 1):
        if _is_atx_heading(line):
            current_section = _heading_slug(line)
            if current_section == section_slug:
                found_section = True
            continue
        if current_section == section_slug:
            section_lines.append((line_number, line))
    return found_section, tuple(section_lines)


def _heading_slug(line: str) -> str:
    heading_text = line.lstrip("#").strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", heading_text).strip("-")


def _is_external_or_anchor_link(target: str) -> bool:
    parsed = urlparse(target)
    return bool(parsed.scheme) or target.startswith("#")


def _is_glossary_markdown_target(target: str) -> bool:
    if _is_external_or_anchor_link(target):
        return False
    path_text = target.split("#", maxsplit=1)[0].strip()
    return path_text.endswith(".md") and Path(path_text).name != "README.md"


def _resolve_markdown_link(target: str, *, page_path: Path) -> Path:
    path_text = unquote(target.split("#", maxsplit=1)[0].strip())
    return (page_path.parent / path_text).resolve()


def _optional_text(row: Mapping[str, object], key: str) -> str | None:
    value = row.get(key)
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized


def _string_sequence(value: object) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        return ()
    strings: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            strings.append(item.strip())
    return tuple(strings)


def _display_path(path: Path) -> str:
    return display_path(path)


def _path_from_display(path_text: str) -> Path:
    return path_from_display(path_text)
