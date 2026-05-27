"""Generated Gas market corpus artifact path defaults."""

import os
from pathlib import Path

CORPUS_ROOT_ENV_VAR = "ENERGY_MARKET_CORPUS_ROOT"
DEFAULT_CORPUS_ROOT_RELATIVE_PATH = Path("energy-market-delta-lake-artifacts/corpora")
GAS_MARKET_CORPUS_RELATIVE_PATH = Path("gas-market")
SOURCE_MANIFEST_RELATIVE_PATH = GAS_MARKET_CORPUS_RELATIVE_PATH / (
    "bronze/source_manifest.jsonl"
)
SILVER_DOCUMENTS_RELATIVE_PATH = GAS_MARKET_CORPUS_RELATIVE_PATH / "silver/documents"
SILVER_CHUNKS_RELATIVE_PATH = GAS_MARKET_CORPUS_RELATIVE_PATH / "silver/chunks"
SILVER_INDEX_RELATIVE_PATH = GAS_MARKET_CORPUS_RELATIVE_PATH / (
    "silver/index/chunks.jsonl"
)
GOLD_RELATIVE_PATH = GAS_MARKET_CORPUS_RELATIVE_PATH / "gold"


def subproject_root() -> Path:
    """Return the Gas market knowledge base Subproject root."""
    return Path(__file__).resolve().parents[2]


def default_corpus_root() -> Path:
    """Return the fallback corpus artifact root under the user's home directory."""
    return Path.home() / DEFAULT_CORPUS_ROOT_RELATIVE_PATH


def corpus_root() -> Path:
    """Return the configured corpus artifact root."""
    configured_root = os.environ.get(CORPUS_ROOT_ENV_VAR)
    if configured_root is None or not configured_root.strip():
        return default_corpus_root()
    return Path(configured_root).expanduser()


def default_source_manifest_path() -> Path:
    """Return the default bronze source manifest path."""
    return corpus_root() / SOURCE_MANIFEST_RELATIVE_PATH


def default_silver_documents_dir() -> Path:
    """Return the default silver document Markdown output directory."""
    return corpus_root() / SILVER_DOCUMENTS_RELATIVE_PATH


def default_silver_chunks_dir() -> Path:
    """Return the default silver chunk Markdown output directory."""
    return corpus_root() / SILVER_CHUNKS_RELATIVE_PATH


def default_silver_index_path() -> Path:
    """Return the default silver chunk index JSONL path."""
    return corpus_root() / SILVER_INDEX_RELATIVE_PATH


def default_gold_dir() -> Path:
    """Return the default gold Market context directory."""
    return corpus_root() / GOLD_RELATIVE_PATH


def default_generated_paths(document_identity: str) -> dict[str, str]:
    """Return generated artifact paths for one manifest document identity."""
    document_identity_path = Path(*document_identity.split("/"))
    return {
        "silver_document_markdown": display_path(
            (default_silver_documents_dir() / document_identity_path).with_suffix(".md")
        ),
        "silver_chunks": display_path(
            default_silver_chunks_dir() / document_identity_path
        ),
        "silver_chunk_index": display_path(default_silver_index_path()),
        "gold_context": display_path(
            (default_gold_dir() / document_identity_path).with_suffix(".md")
        ),
    }


def display_path(path: Path) -> str:
    """Return a stable path string for generated metadata."""
    resolved_path = path.resolve()
    root = subproject_root().resolve()
    if resolved_path.is_relative_to(root):
        return resolved_path.relative_to(root).as_posix()
    return path.as_posix()


def path_from_display(path_text: str) -> Path:
    """Return a filesystem path from a generated metadata path string."""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return subproject_root() / path
