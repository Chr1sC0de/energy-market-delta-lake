"""AEMO major publications corpus artifact path defaults."""

from dataclasses import dataclass
from pathlib import Path

from gas_market_knowledge_base.corpus_core.paths import (
    CorpusArtifactLayout,
    artifact_root_from_env,
    document_identity_parts,
)

CORPUS_ROOT_ENV_VAR = "ENERGY_MARKET_CORPUS_ROOT"
DEFAULT_CORPUS_ROOT_RELATIVE_PATH = Path("energy-market-delta-lake-artifacts/corpora")
AEMO_MAJOR_PUBLICATIONS_CORPUS_NAME = "aemo-major-publications"


@dataclass(frozen=True, slots=True)
class AemoPublicationCorpusPaths:
    """Resolved artifact paths for one AEMO publications fixture build."""

    layout: CorpusArtifactLayout
    source_manifest_path: Path
    source_cache_dir: Path
    silver_documents_dir: Path
    silver_chunks_dir: Path
    silver_index_path: Path
    gold_dir: Path

    def generated_paths(self, document_identity: str) -> dict[str, str]:
        """Return generated artifact paths for one document identity."""
        document_identity_path = Path(*document_identity_parts(document_identity))
        return {
            "silver_document_markdown": self.layout.display_path(
                (self.silver_documents_dir / document_identity_path).with_suffix(".md")
            ),
            "silver_chunks": self.layout.display_path(
                self.silver_chunks_dir / document_identity_path
            ),
            "silver_chunk_index": self.layout.display_path(self.silver_index_path),
            "gold_context": self.layout.display_path(
                (self.gold_dir / document_identity_path).with_suffix(".md")
            ),
        }


def subproject_root() -> Path:
    """Return the owning corpus Subproject root."""
    return Path(__file__).resolve().parents[3]


def default_corpus_root() -> Path:
    """Return the fallback corpus artifact root under the user's home directory."""
    return Path.home() / DEFAULT_CORPUS_ROOT_RELATIVE_PATH


def corpus_root() -> Path:
    """Return the configured corpus artifact root."""
    return artifact_root_from_env(
        env_var=CORPUS_ROOT_ENV_VAR,
        default_root=default_corpus_root(),
    )


def corpus_layout(*, artifact_root: Path | None = None) -> CorpusArtifactLayout:
    """Return the AEMO major publications corpus artifact layout."""
    return CorpusArtifactLayout(
        root=artifact_root or corpus_root(),
        corpus_name=AEMO_MAJOR_PUBLICATIONS_CORPUS_NAME,
        display_root=subproject_root(),
    )


def default_source_cache_dir(*, artifact_root: Path | None = None) -> Path:
    """Return the default bronze fixture source byte cache directory."""
    return (
        corpus_layout(artifact_root=artifact_root).corpus_dir
        / "bronze"
        / "fixture-pdfs"
    )


def default_corpus_paths(
    *,
    artifact_root: Path | None = None,
    source_manifest_path: Path | None = None,
    source_cache_dir: Path | None = None,
    silver_documents_dir: Path | None = None,
    silver_chunks_dir: Path | None = None,
    silver_index_path: Path | None = None,
    gold_dir: Path | None = None,
) -> AemoPublicationCorpusPaths:
    """Return default corpus paths with optional explicit path overrides."""
    layout = corpus_layout(artifact_root=artifact_root)
    return AemoPublicationCorpusPaths(
        layout=layout,
        source_manifest_path=source_manifest_path or layout.source_manifest_path,
        source_cache_dir=source_cache_dir
        or default_source_cache_dir(artifact_root=artifact_root),
        silver_documents_dir=silver_documents_dir or layout.silver_documents_dir,
        silver_chunks_dir=silver_chunks_dir or layout.silver_chunks_dir,
        silver_index_path=silver_index_path or layout.silver_index_path,
        gold_dir=gold_dir or layout.gold_dir,
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
    """Return the default gold Markdown directory."""
    return corpus_layout().gold_dir
