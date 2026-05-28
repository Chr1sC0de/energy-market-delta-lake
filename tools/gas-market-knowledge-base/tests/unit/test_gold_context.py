import json
from pathlib import Path

from gas_market_knowledge_base.gold_context import (
    GoldSourceCitation,
    render_gold_glossary_body,
    render_gold_markdown_page,
    validate_gold_context,
)

SOURCE_HASH = "a" * 64


def _write_json_frontmatter(
    path: Path, frontmatter: dict[str, object], body: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        render_gold_markdown_page(frontmatter=frontmatter, body=body),
        encoding="utf-8",
    )


def _generated_path(path: Path) -> str:
    return path.as_posix()


def _write_silver_fixture(
    root: Path,
    *,
    chunk_id: str = "chunk-gas-day",
    extra_chunk_ids: tuple[str, ...] = (),
) -> Path:
    document_path = root / "generated" / "silver" / "documents" / "fixture.md"
    index_path = root / "generated" / "silver" / "index" / "chunks.jsonl"
    document_path.parent.mkdir(parents=True, exist_ok=True)
    document_path.write_text("# Fixture source document\n", encoding="utf-8")
    rows = []
    for current_chunk_id in (chunk_id, *extra_chunk_ids):
        chunk_path = (
            root
            / "generated"
            / "silver"
            / "chunks"
            / "fixture"
            / f"{current_chunk_id}.md"
        )
        chunk_path.parent.mkdir(parents=True, exist_ok=True)
        chunk_path.write_text(
            f"# Fixture source chunk\n\n{current_chunk_id} evidence.\n",
            encoding="utf-8",
        )
        rows.append(
            {
                "chunk_id": current_chunk_id,
                "content_sha256": SOURCE_HASH,
                "path": chunk_path.as_posix(),
                "source_document_markdown_path": document_path.as_posix(),
            }
        )
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(
        "".join(f"{json.dumps(row, sort_keys=True)}\n" for row in rows),
        encoding="utf-8",
    )
    return index_path


def _write_gold_fixture(
    root: Path,
    *,
    chunk_id: str = "chunk-gas-day",
    source_hashes: list[str] | None = None,
    definition: str | None = None,
    include_index_link: bool = True,
) -> Path:
    gold_root = root / "generated" / "gold"
    readme_path = gold_root / "README.md"
    glossary_index_path = gold_root / "glossary" / "README.md"
    page_path = gold_root / "glossary" / "gas-day.md"
    source_hash_list = [SOURCE_HASH] if source_hashes is None else source_hashes
    definition_text = definition or (
        f"A gas day is represented by the cited fixture source. "
        f"[[chunk:{chunk_id}]] [[source:sha256:{SOURCE_HASH}]]"
    )
    source_citation = GoldSourceCitation(
        chunk_id=chunk_id,
        chunk_path=f"../../silver/chunks/fixture/{chunk_id}.md",
        source_document_path="../../silver/documents/fixture.md",
        source_hash=SOURCE_HASH,
    )

    _write_json_frontmatter(
        readme_path,
        {
            "schema_version": 1,
            "context_type": "navigation",
            "title": "Gold Market Context",
            "generated_path": _generated_path(readme_path),
        },
        "# Gold Market Context\n\nUse the glossary index to find seed concepts.\n",
    )
    index_body = "# Glossary\n\n"
    if include_index_link:
        index_body += "- [Gas Day](gas-day.md)\n"
    _write_json_frontmatter(
        glossary_index_path,
        {
            "schema_version": 1,
            "context_type": "glossary-index",
            "title": "Glossary",
            "generated_path": _generated_path(glossary_index_path),
        },
        index_body,
    )
    _write_json_frontmatter(
        page_path,
        {
            "schema_version": 1,
            "context_type": "glossary-page",
            "title": "Gas Day",
            "slug": "gas-day",
            "generated_path": _generated_path(page_path),
            "source_chunk_ids": [chunk_id],
            "source_hashes": source_hash_list,
            "related_concepts": [],
        },
        render_gold_glossary_body(
            title="Gas Day",
            definition=definition_text,
            source_citations=[source_citation],
        ),
    )
    return gold_root


def _gold_fixture_page(gold_dir: Path) -> Path:
    return gold_dir / "glossary" / "gas-day.md"


def _write_capacity_gold_page(gold_dir: Path) -> None:
    chunk_id = "chunk-capacity"
    glossary_index_path = gold_dir / "glossary" / "README.md"
    page_path = gold_dir / "glossary" / "capacity.md"
    _replace_gold_page_text(
        glossary_index_path,
        "- [Gas Day](gas-day.md)\n",
        "- [Gas Day](gas-day.md)\n- [Capacity](capacity.md)\n",
    )
    source_citation = GoldSourceCitation(
        chunk_id=chunk_id,
        chunk_path=f"../../silver/chunks/fixture/{chunk_id}.md",
        source_document_path="../../silver/documents/fixture.md",
        source_hash=SOURCE_HASH,
    )
    _write_json_frontmatter(
        page_path,
        {
            "schema_version": 1,
            "context_type": "glossary-page",
            "title": "Capacity",
            "slug": "capacity",
            "generated_path": _generated_path(page_path),
            "source_chunk_ids": [chunk_id],
            "source_hashes": [SOURCE_HASH],
            "related_concepts": [],
        },
        render_gold_glossary_body(
            title="Capacity",
            definition=(
                f"Capacity is represented by the cited fixture source. "
                f"[[chunk:{chunk_id}]] [[source:sha256:{SOURCE_HASH}]]"
            ),
            source_citations=[source_citation],
        ),
    )


def _replace_gold_page_text(page_path: Path, old: str, new: str) -> None:
    text = page_path.read_text(encoding="utf-8")
    assert old in text
    page_path.write_text(
        text.replace(old, new, 1),
        encoding="utf-8",
    )


def test_validate_gold_context_accepts_cited_glossary(tmp_path: Path) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path)

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert result.error_count == 0
    assert result.page_count == 3
    assert result.glossary_page_count == 1


def test_validate_gold_context_accepts_multiple_fixture_glossary_pages(
    tmp_path: Path,
) -> None:
    index_path = _write_silver_fixture(tmp_path, extra_chunk_ids=("chunk-capacity",))
    gold_dir = _write_gold_fixture(tmp_path)
    _write_capacity_gold_page(gold_dir)

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert result.error_count == 0


def test_validate_gold_context_reports_uncited_factual_claim(tmp_path: Path) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(
        tmp_path,
        definition="A gas day is represented by the fixture source.\n",
    )

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("uncited factual claim" in error for error in result.errors)


def test_validate_gold_context_reports_broken_chunk_link(tmp_path: Path) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path, chunk_id="missing-chunk")

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("unknown silver chunk" in error for error in result.errors)


def test_validate_gold_context_reports_missing_source_hash(tmp_path: Path) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path, source_hashes=[])

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("missing source" in error for error in result.errors)


def test_validate_gold_context_reports_indented_atx_heading(tmp_path: Path) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path)
    _replace_gold_page_text(
        _gold_fixture_page(gold_dir),
        "## Definition",
        "    ## Definition",
    )

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("indented ATX heading" in error for error in result.errors)


def test_validate_gold_context_reports_tab_indented_heading(tmp_path: Path) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path)
    _replace_gold_page_text(
        _gold_fixture_page(gold_dir),
        "## Definition",
        "\t## Definition",
    )

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("tab-indented ATX heading" in error for error in result.errors)


def test_validate_gold_context_reports_indented_definition_paragraph(
    tmp_path: Path,
) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path)
    _replace_gold_page_text(
        _gold_fixture_page(gold_dir),
        "A gas day is represented",
        "    A gas day is represented",
    )

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("normal paragraphs must start" in error for error in result.errors)


def test_validate_gold_context_reports_malformed_citation_list(
    tmp_path: Path,
) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path)
    _replace_gold_page_text(
        _gold_fixture_page(gold_dir),
        "- `chunk-gas-day`:",
        "`chunk-gas-day`:",
    )

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("malformed source citation list" in error for error in result.errors)


def test_validate_gold_context_reports_citation_chunk_not_in_frontmatter(
    tmp_path: Path,
) -> None:
    index_path = _write_silver_fixture(tmp_path, chunk_id="chunk-capacity")
    gold_dir = _write_gold_fixture(tmp_path, chunk_id="chunk-capacity")
    _replace_gold_page_text(
        _gold_fixture_page(gold_dir),
        f"[[chunk:chunk-capacity]] [[source:sha256:{SOURCE_HASH}]]\n\n"
        "## Related Concepts",
        f"[[chunk:chunk-gas-day]] [[source:sha256:{SOURCE_HASH}]]\n\n"
        "## Related Concepts",
    )

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any(
        "source citation bullet references chunk" in error for error in result.errors
    )


def test_validate_gold_context_reports_broken_source_document_reference(
    tmp_path: Path,
) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path)
    (tmp_path / "generated" / "silver" / "documents" / "fixture.md").unlink()

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("source document target missing" in error for error in result.errors)


def test_validate_gold_context_reports_stale_glossary_index(tmp_path: Path) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path, include_index_link=False)

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("stale glossary index" in error for error in result.errors)
