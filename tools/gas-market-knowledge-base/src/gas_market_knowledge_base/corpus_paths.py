"""Generated Gas market corpus artifact path defaults."""

from pathlib import Path

from gas_market_knowledge_base.corpus_core.paths import (
    CorpusArtifactLayout,
    artifact_root_from_env,
)

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
    return artifact_root_from_env(
        env_var=CORPUS_ROOT_ENV_VAR,
        default_root=default_corpus_root(),
    )


def corpus_layout() -> CorpusArtifactLayout:
    """Return the Gas market corpus artifact layout."""
    return CorpusArtifactLayout(
        root=corpus_root(),
        corpus_name=GAS_MARKET_CORPUS_RELATIVE_PATH.as_posix(),
        display_root=subproject_root(),
    )


def default_source_manifest_path() -> Path:
    """Return the default bronze source manifest path."""
    return corpus_layout().source_manifest_path


def default_silver_documents_dir() -> Path:
    """Return the default silver document Markdown output directory."""
    return corpus_layout().silver_documents_dir


def default_silver_chunks_dir() -> Path:
    """Return the default silver chunk Markdown output directory."""
    return corpus_layout().silver_chunks_dir


def default_silver_index_path() -> Path:
    """Return the default silver chunk index JSONL path."""
    return corpus_layout().silver_index_path


def default_gold_dir() -> Path:
    """Return the default gold Market context directory."""
    return corpus_layout().gold_dir


def default_generated_paths(document_identity: str) -> dict[str, str]:
    """Return generated artifact paths for one manifest document identity."""
    return corpus_layout().generated_paths(document_identity)


def display_path(path: Path) -> str:
    """Return a stable path string for generated metadata."""
    return corpus_layout().display_path(path)


def path_from_display(path_text: str) -> Path:
    """Return a filesystem path from a generated metadata path string."""
    return corpus_layout().path_from_display(path_text)
