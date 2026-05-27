from pathlib import Path

import pytest

from gas_market_knowledge_base.corpus_paths import (
    CORPUS_ROOT_ENV_VAR,
    default_corpus_root,
    default_generated_paths,
    default_gold_dir,
    default_silver_chunks_dir,
    default_silver_documents_dir,
    default_silver_index_path,
    default_source_manifest_path,
)


def test_generated_defaults_use_configured_corpus_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus_root = tmp_path / "corpora"
    monkeypatch.setenv(CORPUS_ROOT_ENV_VAR, str(corpus_root))

    assert default_source_manifest_path() == (
        corpus_root / "gas-market" / "bronze" / "source_manifest.jsonl"
    )
    assert default_silver_documents_dir() == (
        corpus_root / "gas-market" / "silver" / "documents"
    )
    assert default_silver_chunks_dir() == (
        corpus_root / "gas-market" / "silver" / "chunks"
    )
    assert default_silver_index_path() == (
        corpus_root / "gas-market" / "silver" / "index" / "chunks.jsonl"
    )
    assert default_gold_dir() == corpus_root / "gas-market" / "gold"


def test_generated_defaults_use_home_corpus_root_when_env_is_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(CORPUS_ROOT_ENV_VAR, raising=False)

    assert default_corpus_root() == (
        Path.home() / "energy-market-delta-lake-artifacts" / "corpora"
    )
    assert default_source_manifest_path() == (
        Path.home()
        / "energy-market-delta-lake-artifacts"
        / "corpora"
        / "gas-market"
        / "bronze"
        / "source_manifest.jsonl"
    )


def test_empty_corpus_root_env_uses_non_dot_home_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(CORPUS_ROOT_ENV_VAR, "")

    assert default_source_manifest_path().is_absolute()
    assert default_source_manifest_path() != Path(
        "gas-market/bronze/source_manifest.jsonl"
    )


def test_default_generated_manifest_paths_use_external_corpus_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    corpus_root = tmp_path / "corpora"
    document_identity = "gbb/gas-guide/sha256-" + ("a" * 64)
    monkeypatch.setenv(CORPUS_ROOT_ENV_VAR, str(corpus_root))

    assert default_generated_paths(document_identity) == {
        "silver_document_markdown": (
            corpus_root
            / "gas-market"
            / "silver"
            / "documents"
            / "gbb"
            / "gas-guide"
            / f"sha256-{'a' * 64}.md"
        ).as_posix(),
        "silver_chunks": (
            corpus_root
            / "gas-market"
            / "silver"
            / "chunks"
            / "gbb"
            / "gas-guide"
            / f"sha256-{'a' * 64}"
        ).as_posix(),
        "silver_chunk_index": (
            corpus_root / "gas-market" / "silver" / "index" / "chunks.jsonl"
        ).as_posix(),
        "gold_context": (
            corpus_root
            / "gas-market"
            / "gold"
            / "gbb"
            / "gas-guide"
            / f"sha256-{'a' * 64}.md"
        ).as_posix(),
    }
