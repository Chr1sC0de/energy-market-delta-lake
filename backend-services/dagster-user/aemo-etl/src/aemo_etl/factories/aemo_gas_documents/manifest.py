"""Checked-in manifest loader for AEMO gas document media links."""

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.resources import files
from typing import Any, cast

from aemo_etl.factories.aemo_gas_documents.models import (
    AEMOGasDocumentPendingObservation,
    AEMOGasDocumentSourcePage,
    IncludeDecision,
)
from aemo_etl.factories.aemo_gas_documents.scraper import (
    clean_document_title,
    document_family_id,
    infer_document_kind,
    is_downloadable_media_url,
    normalize_source_url,
    parse_document_version,
    parse_effective_date,
    parse_published_date,
    source_page_observation,
)

MANIFEST_SCHEMA_VERSION = 1
DISCOVERY_REPORT_SCHEMA_VERSION = 1
MANIFEST_FILENAME = "aemo_gas_document_media_manifest.json"
DISCOVERY_REPORT_FILENAME = "aemo_gas_document_media_discovery_report.json"


def load_default_aemo_gas_document_observations(
    *,
    observed_at: datetime | None = None,
) -> list[AEMOGasDocumentPendingObservation]:
    """Load packaged manifest observations for the daily asset path."""
    return observations_from_manifest_payload(
        load_default_manifest_payload(),
        observed_at=observed_at,
    )


def load_default_manifest_payload() -> dict[str, Any]:
    """Load the checked-in AEMO gas document media manifest JSON."""
    resource = files(__package__).joinpath(MANIFEST_FILENAME)
    return cast(dict[str, Any], json.loads(resource.read_text(encoding="utf-8")))


def load_default_discovery_report_payload() -> dict[str, Any]:
    """Load the checked-in AEMO gas document media discovery report JSON."""
    resource = files(__package__).joinpath(DISCOVERY_REPORT_FILENAME)
    return cast(dict[str, Any], json.loads(resource.read_text(encoding="utf-8")))


def observations_from_manifest_payload(
    payload: Mapping[str, Any],
    *,
    observed_at: datetime | None = None,
) -> list[AEMOGasDocumentPendingObservation]:
    """Convert a manifest payload into source-page and link observations."""
    _validate_schema_version(payload, key="schema_version")
    fallback_observed_at = observed_at or _generated_at(payload)
    observations: list[AEMOGasDocumentPendingObservation] = []

    for entry in _sequence(payload, "source_pages"):
        source_page = source_page_from_manifest_entry(entry)
        page_observed_at = _entry_observed_at(entry, fallback_observed_at)
        observations.append(
            source_page_observation(
                source_page,
                observed_at=page_observed_at,
                source_page_title=_optional_str(entry, "source_page_title"),
            )
        )

    for entry in _sequence(payload, "media_links"):
        observations.append(
            media_link_observation_from_manifest_entry(
                entry,
                observed_at=fallback_observed_at,
            )
        )

    return observations


def source_page_from_manifest_entry(
    entry: Mapping[str, Any],
) -> AEMOGasDocumentSourcePage:
    """Build a configured source page from one manifest source-page entry."""
    include_decision = _include_decision(entry, "include_decision")
    return AEMOGasDocumentSourcePage(
        corpus_source=_required_str(entry, "corpus_source"),
        source_page_url=_required_str(entry, "source_page_url"),
        include_decision=include_decision,
        include_reason=_optional_str(entry, "include_reason"),
        exclude_reason=_optional_str(entry, "exclude_reason"),
        source_page_title=_optional_str(entry, "source_page_title"),
        source_page_section=_optional_str(entry, "source_page_section"),
        fetch_links=_optional_bool(entry, "fetch_links", default=True),
        discover_child_pages=_optional_bool(
            entry,
            "discover_child_pages",
            default=False,
        ),
    )


def media_link_observation_from_manifest_entry(
    entry: Mapping[str, Any],
    *,
    observed_at: datetime,
) -> AEMOGasDocumentPendingObservation:
    """Build one pending media-link observation from a manifest entry."""
    source_url = _required_str(entry, "source_url")
    resolved_url = _optional_str(entry, "resolved_url") or source_url
    normalized_source_url, source_url_query, media_revision = normalize_source_url(
        source_url
    )
    source_link_text = _optional_str(entry, "source_link_text")
    document_title = _optional_str(entry, "document_title") or clean_document_title(
        source_link_text or "",
        source_url,
    )
    corpus_source = _required_str(entry, "corpus_source")
    include_decision = _include_decision(entry, "include_decision")
    return AEMOGasDocumentPendingObservation(
        observation_type="link",
        corpus_source=corpus_source,
        source_page_url=_required_str(entry, "source_page_url"),
        source_page_title=_optional_str(entry, "source_page_title"),
        source_page_section=_optional_str(entry, "source_page_section"),
        source_page_observed_at=_entry_observed_at(entry, observed_at),
        source_link_text=source_link_text,
        source_url=source_url,
        resolved_url=resolved_url,
        normalized_source_url=(
            _optional_str(entry, "normalized_source_url") or normalized_source_url
        ),
        source_url_query=_optional_str(entry, "source_url_query") or source_url_query,
        document_family_id=(
            _optional_str(entry, "document_family_id")
            or document_family_id(corpus_source, document_title)
        ),
        document_title=document_title,
        document_kind=(
            _optional_str(entry, "document_kind")
            or infer_document_kind(source_link_text or "", source_url)
        ),
        include_decision=include_decision,
        include_reason=_optional_str(entry, "include_reason"),
        exclude_reason=_optional_str(entry, "exclude_reason"),
        document_version=(
            _optional_str(entry, "document_version")
            or parse_document_version(source_link_text or "", source_url)
        ),
        published_date=(
            _optional_str(entry, "published_date")
            or parse_published_date(source_link_text or "")
        ),
        effective_date=(
            _optional_str(entry, "effective_date")
            or parse_effective_date(source_link_text or "")
        ),
        media_revision=_optional_str(entry, "media_revision") or media_revision,
        should_download=_should_download(entry, include_decision, source_url),
    )


def source_page_manifest_entry(
    source_page: AEMOGasDocumentSourcePage,
    *,
    observed_at: datetime,
    source_page_title: str | None = None,
    status: str = "configured",
    error: str | None = None,
) -> dict[str, Any]:
    """Return a JSON-ready manifest entry for one source page."""
    return _drop_none(
        {
            **asdict(source_page),
            "source_page_title": source_page_title or source_page.source_page_title,
            "observed_at": _format_datetime(observed_at),
            "status": status,
            "error": error,
        }
    )


def media_link_manifest_entry(
    observation: AEMOGasDocumentPendingObservation,
) -> dict[str, Any]:
    """Return a JSON-ready manifest entry for one media-link observation."""
    return _drop_none(
        {
            "corpus_source": observation.corpus_source,
            "source_page_url": observation.source_page_url,
            "source_page_title": observation.source_page_title,
            "source_page_section": observation.source_page_section,
            "observed_at": _format_datetime(observation.source_page_observed_at),
            "source_link_text": observation.source_link_text,
            "source_url": observation.source_url,
            "resolved_url": observation.resolved_url,
            "normalized_source_url": observation.normalized_source_url,
            "source_url_query": observation.source_url_query,
            "document_family_id": observation.document_family_id,
            "document_title": observation.document_title,
            "document_kind": observation.document_kind,
            "include_decision": observation.include_decision,
            "include_reason": observation.include_reason,
            "exclude_reason": observation.exclude_reason,
            "document_version": observation.document_version,
            "published_date": observation.published_date,
            "effective_date": observation.effective_date,
            "media_revision": observation.media_revision,
            "should_download": observation.should_download,
        }
    )


def manifest_payload(
    *,
    generated_at: datetime,
    source_pages: Sequence[Mapping[str, Any]],
    media_links: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build the top-level checked-in manifest payload."""
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generated_at": _format_datetime(generated_at),
        "generator": "aemo-refresh-gas-document-media-manifest",
        "source_page_count": len(source_pages),
        "media_link_count": len(media_links),
        "source_pages": list(source_pages),
        "media_links": list(media_links),
    }


def discovery_report_payload(
    *,
    generated_at: datetime,
    source_pages: Sequence[Mapping[str, Any]],
    media_validations: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build the top-level checked-in discovery report payload."""
    return {
        "schema_version": DISCOVERY_REPORT_SCHEMA_VERSION,
        "generated_at": _format_datetime(generated_at),
        "generator": "aemo-refresh-gas-document-media-manifest",
        "source_page_count": len(source_pages),
        "media_validation_count": len(media_validations),
        "source_pages": list(source_pages),
        "media_validations": list(media_validations),
    }


def dump_manifest_json(payload: Mapping[str, Any]) -> str:
    """Serialize a manifest or discovery report payload consistently."""
    return f"{json.dumps(payload, indent=2, sort_keys=True)}\n"


def existing_manifest_entries(
    payload: Mapping[str, Any],
) -> tuple[dict[str, Mapping[str, Any]], dict[str, list[Mapping[str, Any]]]]:
    """Return existing source-page and media-link entries keyed by source page."""
    source_pages = {
        _required_str(entry, "source_page_url"): entry
        for entry in _sequence(payload, "source_pages")
    }
    media_links: dict[str, list[Mapping[str, Any]]] = {}
    for entry in _sequence(payload, "media_links"):
        media_links.setdefault(_required_str(entry, "source_page_url"), []).append(
            entry
        )
    return source_pages, media_links


def _generated_at(payload: Mapping[str, Any]) -> datetime:
    generated_at = _optional_str(payload, "generated_at")
    if generated_at is None:
        return datetime.now(UTC)
    return _parse_datetime(generated_at)


def _entry_observed_at(entry: Mapping[str, Any], fallback: datetime) -> datetime:
    observed_at = _optional_str(entry, "observed_at")
    if observed_at is None:
        return fallback
    return _parse_datetime(observed_at)


def _parse_datetime(value: str) -> datetime:
    normalized = value.removesuffix("Z")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _format_datetime(value: datetime) -> str:
    return (
        value.astimezone(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace(
            "+00:00",
            "Z",
        )
    )


def _validate_schema_version(payload: Mapping[str, Any], *, key: str) -> None:
    version = payload.get(key)
    if version != MANIFEST_SCHEMA_VERSION:
        raise ValueError(
            f"unsupported AEMO gas document manifest schema version: {version!r}"
        )


def _sequence(payload: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    value = payload.get(key)
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"manifest field {key!r} must be a list")
    result: list[Mapping[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError(f"manifest field {key!r} must contain objects")
        result.append(cast(Mapping[str, Any], item))
    return result


def _required_str(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or value == "":
        raise ValueError(f"manifest field {key!r} must be a non-empty string")
    return value


def _optional_str(payload: Mapping[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"manifest field {key!r} must be a string when present")
    return value


def _optional_bool(payload: Mapping[str, Any], key: str, *, default: bool) -> bool:
    value = payload.get(key)
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError(f"manifest field {key!r} must be a boolean when present")
    return value


def _include_decision(payload: Mapping[str, Any], key: str) -> IncludeDecision:
    value = _required_str(payload, key)
    if value not in {"include", "exclude", "needs_human_review"}:
        raise ValueError(f"manifest field {key!r} has invalid decision {value!r}")
    return cast(IncludeDecision, value)


def _should_download(
    entry: Mapping[str, Any],
    include_decision: IncludeDecision,
    source_url: str,
) -> bool:
    value = entry.get("should_download")
    if value is None:
        return include_decision == "include" and is_downloadable_media_url(source_url)
    if not isinstance(value, bool):
        raise ValueError("manifest field 'should_download' must be a boolean")
    return value


def _drop_none(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None}
