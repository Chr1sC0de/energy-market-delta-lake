"""Shared corpus artifact path planning."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CorpusArtifactLayout:
    """Artifact paths for one generated corpus."""

    root: Path
    corpus_name: str
    display_root: Path

    @property
    def corpus_dir(self) -> Path:
        """Return the root directory for this corpus."""
        return self.root / self.corpus_name

    @property
    def source_manifest_path(self) -> Path:
        """Return the bronze source manifest path."""
        return self.corpus_dir / "bronze" / "source_manifest.jsonl"

    @property
    def silver_documents_dir(self) -> Path:
        """Return the silver document Markdown directory."""
        return self.corpus_dir / "silver" / "documents"

    @property
    def silver_chunks_dir(self) -> Path:
        """Return the silver chunk Markdown directory."""
        return self.corpus_dir / "silver" / "chunks"

    @property
    def silver_index_path(self) -> Path:
        """Return the silver chunk index JSONL path."""
        return self.corpus_dir / "silver" / "index" / "chunks.jsonl"

    @property
    def gold_dir(self) -> Path:
        """Return the gold Markdown directory."""
        return self.corpus_dir / "gold"

    def generated_paths(self, document_identity: str) -> dict[str, str]:
        """Return generated artifact paths for one document identity."""
        document_identity_path = Path(*document_identity_parts(document_identity))
        return {
            "silver_document_markdown": self.display_path(
                (self.silver_documents_dir / document_identity_path).with_suffix(".md")
            ),
            "silver_chunks": self.display_path(
                self.silver_chunks_dir / document_identity_path
            ),
            "silver_chunk_index": self.display_path(self.silver_index_path),
            "gold_context": self.display_path(
                (self.gold_dir / document_identity_path).with_suffix(".md")
            ),
        }

    def display_path(self, path: Path) -> str:
        """Return a stable display path for generated metadata."""
        return display_path(path, display_root=self.display_root)

    def path_from_display(self, path_text: str) -> Path:
        """Return a filesystem path from a generated display path."""
        return path_from_display(path_text, display_root=self.display_root)


def artifact_root_from_env(
    *,
    env_var: str,
    default_root: Path,
) -> Path:
    """Return the configured corpus artifact root."""
    configured_root = os.environ.get(env_var)
    if configured_root is None or not configured_root.strip():
        return default_root
    return Path(configured_root).expanduser()


def document_identity_parts(document_identity: str) -> tuple[str, ...]:
    """Return validated relative path parts for a document identity."""
    parts = tuple(document_identity.split("/"))
    if not parts:
        raise ValueError("document_identity must be a relative path")
    for part in parts:
        if part in {"", ".", ".."}:
            raise ValueError(
                "document_identity must not contain empty, dot, or dot-dot parts"
            )
        if "\\" in part:
            raise ValueError("document_identity must use forward slashes")
    return parts


def source_pdf_cache_path(content_sha256: str, *, cache_dir: Path) -> Path:
    """Return the deterministic cached PDF path for one source hash."""
    return cache_dir / f"{content_sha256}.pdf"


def display_path(path: Path, *, display_root: Path) -> str:
    """Return a stable path string for generated metadata."""
    resolved_path = path.resolve()
    resolved_display_root = display_root.resolve()
    if resolved_path.is_relative_to(resolved_display_root):
        return resolved_path.relative_to(resolved_display_root).as_posix()
    return path.as_posix()


def path_from_display(path_text: str, *, display_root: Path) -> Path:
    """Return a filesystem path from a generated metadata path string."""
    path = Path(path_text)
    if path.is_absolute():
        return path
    return display_root / path
