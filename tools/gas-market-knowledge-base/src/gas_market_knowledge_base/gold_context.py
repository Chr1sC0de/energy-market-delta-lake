"""Gas corpus gold Market context defaults."""

from collections.abc import Mapping, Sequence
from pathlib import Path

from gas_market_knowledge_base.corpus_core import gold_context as _core
from gas_market_knowledge_base.corpus_paths import (
    default_silver_index_path,
    display_path,
    path_from_display,
)

GOLD_SCHEMA_VERSION = _core.GOLD_SCHEMA_VERSION
GoldContextValidationResult = _core.GoldContextValidationResult
GoldSourceCitation = _core.GoldSourceCitation


def render_gold_markdown_page(
    *,
    frontmatter: Mapping[str, object],
    body: str,
) -> str:
    """Render a gold Market context Markdown page with JSON frontmatter."""
    return _core.render_gold_markdown_page(frontmatter=frontmatter, body=body)


def render_gold_glossary_body(
    *,
    title: str,
    definition: str,
    source_citations: Sequence[GoldSourceCitation],
    related_concepts: Sequence[tuple[str, str]] = (),
) -> str:
    """Render a gold glossary page body with flush-left Markdown blocks."""
    return _core.render_gold_glossary_body(
        title=title,
        definition=definition,
        source_citations=source_citations,
        related_concepts=related_concepts,
    )


def render_gold_source_citation(citation: GoldSourceCitation) -> str:
    """Render one flush-left source citation bullet."""
    return _core.render_gold_source_citation(citation)


def gold_dir_for_index_path(index_path: Path) -> Path:
    """Return the gold directory beside a silver chunk index path."""
    return _core.gold_dir_for_index_path(index_path)


def validate_gold_context(
    *,
    gold_dir: Path | None = None,
    index_path: Path | None = None,
) -> GoldContextValidationResult:
    """Validate gold Market context pages against the silver chunk index."""
    effective_index_path = index_path or default_silver_index_path()
    return _core.validate_gold_context(
        gold_dir=gold_dir or gold_dir_for_index_path(effective_index_path),
        index_path=effective_index_path,
        display_path=display_path,
        resolve_display_path=path_from_display,
    )
