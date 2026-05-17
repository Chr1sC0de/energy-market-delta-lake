"""Gold Market context page citation validation."""

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import cast
from urllib.parse import unquote, urlparse

from gas_market_knowledge_base.silver_chunks import default_silver_index_path
from gas_market_knowledge_base.source_manifest import subproject_root

GOLD_RELATIVE_PATH = Path("generated/gold")
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


def default_gold_dir() -> Path:
    """Return the default gold Market context directory."""
    return subproject_root() / GOLD_RELATIVE_PATH


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
    index_path: Path = default_silver_index_path(),
) -> GoldContextValidationResult:
    """Validate gold Market context pages against the silver chunk index."""
    effective_gold_dir = gold_dir or gold_dir_for_index_path(index_path)
    page_paths = _gold_page_paths(effective_gold_dir)
    if not page_paths:
        return GoldContextValidationResult(
            gold_dir=effective_gold_dir,
            index_path=index_path,
            page_count=0,
            glossary_page_count=0,
            errors=(),
        )

    chunk_rows, chunk_errors = _load_chunk_rows(index_path)
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
        if context_type == _GLOSSARY_PAGE_TYPE:
            slug = _optional_text(frontmatter, "slug")
            if slug is not None:
                glossary_pages[slug] = page_path

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
        index_path=index_path,
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
    resolved_path = path.resolve()
    root = subproject_root().resolve()
    if resolved_path.is_relative_to(root):
        return resolved_path.relative_to(root).as_posix()
    return path.as_posix()


def _path_from_display(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path
    return subproject_root() / path
