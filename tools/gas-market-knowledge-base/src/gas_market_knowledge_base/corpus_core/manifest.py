"""Shared source manifest row shape and document identity planning."""

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

MANIFEST_SCHEMA_VERSION = 1
MAX_DOCUMENT_IDENTITY_PART_CHARS = 96
DOCUMENT_IDENTITY_HASH_CHARS = 12

type ManifestJsonValue = str | int | None | dict[str, str]


@dataclass(frozen=True, slots=True)
class SourceManifestRow:
    """Portable source manifest row used by corpus silver and gold pipelines."""

    document_identity: str
    content_sha256: str
    corpus_source: str
    document_family_id: str
    document_title: str
    source_url: str
    archive_uri: str
    generated_paths: Mapping[str, str]
    schema_version: int = MANIFEST_SCHEMA_VERSION
    document_kind: str | None = None
    document_version: str | None = None
    document_version_id: str | None = None
    published_date: str | None = None
    effective_date: str | None = None
    media_revision: str | None = None
    resolved_url: str | None = None
    source_page_url: str | None = None
    source_page_title: str | None = None
    source_link_text: str | None = None
    storage_uri: str | None = None
    target_s3_key: str | None = None
    content_length: int | None = None

    def as_dict(self) -> dict[str, ManifestJsonValue]:
        """Return this row as deterministic JSON-ready manifest fields."""
        return {
            "schema_version": self.schema_version,
            "document_identity": self.document_identity,
            "content_sha256": self.content_sha256,
            "corpus_source": self.corpus_source,
            "document_family_id": self.document_family_id,
            "document_title": self.document_title,
            "document_kind": self.document_kind,
            "document_version": self.document_version,
            "document_version_id": self.document_version_id,
            "published_date": self.published_date,
            "effective_date": self.effective_date,
            "media_revision": self.media_revision,
            "source_url": self.source_url,
            "resolved_url": self.resolved_url,
            "source_page_url": self.source_page_url,
            "source_page_title": self.source_page_title,
            "source_link_text": self.source_link_text,
            "archive_uri": self.archive_uri,
            "storage_uri": self.storage_uri,
            "target_s3_key": self.target_s3_key,
            "content_length": self.content_length,
            "generated_paths": dict(self.generated_paths),
        }


def document_identity(
    *,
    corpus_source: str,
    document_family_id: str,
    content_sha256: str,
) -> str:
    """Return the portable source document identity path."""
    return (
        f"{document_identity_path_part(corpus_source)}/"
        f"{document_identity_path_part(document_family_id)}/"
        f"sha256-{content_sha256}"
    )


def document_identity_path_part(value: str) -> str:
    """Return one bounded filesystem-safe document identity part."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        return "unknown"
    if len(slug) <= MAX_DOCUMENT_IDENTITY_PART_CHARS:
        return slug
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    prefix_length = MAX_DOCUMENT_IDENTITY_PART_CHARS - DOCUMENT_IDENTITY_HASH_CHARS - 1
    prefix = slug[:prefix_length].rstrip("-")
    return f"{prefix}-{digest[:DOCUMENT_IDENTITY_HASH_CHARS]}"


def dump_source_manifest_jsonl(rows: Sequence[Mapping[str, object]]) -> str:
    """Serialize manifest rows as deterministic JSONL."""
    if not rows:
        return ""
    lines = [json.dumps(row, sort_keys=True, separators=(",", ":")) for row in rows]
    return f"{'\n'.join(lines)}\n"
