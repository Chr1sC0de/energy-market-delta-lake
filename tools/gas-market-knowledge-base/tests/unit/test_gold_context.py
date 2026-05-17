import json
from pathlib import Path

from gas_market_knowledge_base.gold_context import validate_gold_context

SOURCE_HASH = "a" * 64


def _write_json_frontmatter(
    path: Path, frontmatter: dict[str, object], body: str
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\n{json.dumps(frontmatter, indent=2, sort_keys=True)}\n---\n\n{body}",
        encoding="utf-8",
    )


def _generated_path(path: Path) -> str:
    return path.as_posix()


def _write_silver_fixture(root: Path, *, chunk_id: str = "chunk-gas-day") -> Path:
    chunk_path = root / "generated" / "silver" / "chunks" / "fixture" / f"{chunk_id}.md"
    document_path = root / "generated" / "silver" / "documents" / "fixture.md"
    index_path = root / "generated" / "silver" / "index" / "chunks.jsonl"
    document_path.parent.mkdir(parents=True, exist_ok=True)
    document_path.write_text("# Fixture source document\n", encoding="utf-8")
    chunk_path.parent.mkdir(parents=True, exist_ok=True)
    chunk_path.write_text(
        "# Fixture source chunk\n\nGas day evidence.\n", encoding="utf-8"
    )
    row = {
        "chunk_id": chunk_id,
        "content_sha256": SOURCE_HASH,
        "path": chunk_path.as_posix(),
        "source_document_markdown_path": document_path.as_posix(),
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(f"{json.dumps(row, sort_keys=True)}\n", encoding="utf-8")
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
        f"[[chunk:{chunk_id}]] [[source:sha256:{SOURCE_HASH}]]\n"
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
        (
            "# Gas Day\n\n"
            "## Definition\n\n"
            f"{definition_text}\n"
            "## Source Citations\n\n"
            f"- [{chunk_id}](../../silver/chunks/fixture/{chunk_id}.md)\n"
            "- [Fixture source](../../silver/documents/fixture.md)\n"
            "\n## Related Concepts\n\n"
            "- None yet.\n"
        ),
    )
    return gold_root


def test_validate_gold_context_accepts_cited_glossary(tmp_path: Path) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path)

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert result.error_count == 0
    assert result.page_count == 3
    assert result.glossary_page_count == 1


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


def test_validate_gold_context_reports_stale_glossary_index(tmp_path: Path) -> None:
    index_path = _write_silver_fixture(tmp_path)
    gold_dir = _write_gold_fixture(tmp_path, include_index_link=False)

    result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)

    assert any("stale glossary index" in error for error in result.errors)
