"""Data models and default source-page scope for AEMO gas documents."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

type IncludeDecision = Literal["include", "exclude", "needs_human_review"]
type ObservationType = Literal["source_page", "link"]


@dataclass(frozen=True, slots=True)
class AEMOGasDocumentSourcePage:
    """Configured AEMO source page or scope observation."""

    corpus_source: str
    source_page_url: str
    include_decision: IncludeDecision
    include_reason: str | None = None
    exclude_reason: str | None = None
    source_page_title: str | None = None
    source_page_section: str | None = None
    fetch_links: bool = True
    discover_child_pages: bool = False


@dataclass(frozen=True, slots=True)
class AEMOGasDocumentPendingObservation:
    """Source-page or link observation before optional PDF byte download."""

    observation_type: ObservationType
    corpus_source: str
    source_page_url: str
    source_page_title: str | None
    source_page_section: str | None
    source_page_observed_at: datetime
    source_link_text: str | None
    source_url: str
    resolved_url: str
    normalized_source_url: str
    source_url_query: str | None
    document_family_id: str | None
    document_title: str | None
    document_kind: str
    include_decision: IncludeDecision
    include_reason: str | None
    exclude_reason: str | None
    document_version: str | None
    published_date: str | None
    effective_date: str | None
    media_revision: str | None
    should_download: bool


@dataclass(frozen=True, slots=True)
class AEMOGasDocumentSourceRecord:
    """Bronze metadata row for one source-page or source-link observation."""

    observation_type: ObservationType
    corpus_source: str
    source_page_url: str
    source_page_title: str | None
    source_page_section: str | None
    source_page_observed_at: datetime
    source_link_text: str | None
    source_url: str
    resolved_url: str
    normalized_source_url: str
    source_url_query: str | None
    document_family_id: str | None
    document_title: str | None
    document_kind: str
    include_decision: IncludeDecision
    include_reason: str | None
    exclude_reason: str | None
    content_type: str | None
    content_length: int | None
    etag: str | None
    last_modified: str | None
    content_sha256: str | None
    document_version: str | None
    document_version_id: str | None
    published_date: str | None
    effective_date: str | None
    media_revision: str | None
    landing_storage_uri: str | None
    archive_storage_uri: str | None
    storage_uri: str | None
    target_s3_key: str | None
    surrogate_key: str
    source_content_hash: str


DEFAULT_AEMO_GAS_DOCUMENT_SOURCE_PAGES: tuple[AEMOGasDocumentSourcePage, ...] = (
    AEMOGasDocumentSourcePage(
        corpus_source="gas_root",
        source_page_url="https://www.aemo.com.au/energy-systems/gas",
        include_decision="include",
        include_reason="Seed page for public AEMO gas section discovery.",
        source_page_title="Gas",
        source_page_section="Seed page",
        fetch_links=False,
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="gas_approved_process",
        source_page_url="https://www.aemo.com.au/energy-systems/gas/gas-approved-process",
        include_decision="include",
        include_reason="Cross-gas procedure-change process documents and templates.",
        source_page_title="Gas approved process",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="gbb",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "gas-bulletin-board-gbb/procedures-policies-and-guides/"
            "procedures-and-guides"
        ),
        include_decision="include",
        include_reason="GBB procedures, guides, methodologies, and business rules.",
        source_page_title="GBB procedures and guides",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="gbb",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "gas-bulletin-board-gbb/procedures-policies-and-guides/faq"
        ),
        include_decision="needs_human_review",
        include_reason="FAQ documents need operator confirmation before ingestion.",
        source_page_title="GBB FAQ",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="ecgs",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/east-coast-gas-system/"
            "procedures-and-guidelines"
        ),
        include_decision="include",
        include_reason="East Coast Gas System procedures and compensation guides.",
        source_page_title="East Coast Gas System procedures and guidelines",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="sttm",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "short-term-trading-market-sttm/about-the-short-term-trading-market-sttm"
        ),
        include_decision="include",
        include_reason="STTM technical and contact-type guide documents.",
        source_page_title="About the Short Term Trading Market",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="sttm",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "short-term-trading-market-sttm/procedures-policies-and-guides"
        ),
        include_decision="include",
        include_reason="Current and previous STTM procedure documents.",
        source_page_title="STTM procedures, policies and guides",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="dwgm",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "declared-wholesale-gas-market-dwgm/procedures-policies-and-guides"
        ),
        include_decision="include",
        include_reason="DWGM procedures, technical documents, and applicable guides.",
        source_page_title="DWGM procedures, policies and guides",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="gsh",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "gas-supply-hub-gsh/exchange-agreement-and-guides"
        ),
        include_decision="include",
        include_reason="GSH exchange agreement, membership, methodology, and guides.",
        source_page_title="GSH exchange agreement and guides",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="pct",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "pipeline-capacity-trading-pct/procedures-policies-and-guides"
        ),
        include_decision="include",
        include_reason="PCT procedures, transfer, auction, protocol, and guide documents.",
        source_page_title="PCT procedures, policies and guides",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="retail_gas",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "gas-retail-markets/procedures-policies-and-guides"
        ),
        include_decision="include",
        include_reason="Retail gas procedure, protocol, FRC, and user-guide PDFs.",
        source_page_title="Gas retail procedures, policies and guides",
        discover_child_pages=True,
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="wa_gbb",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/gas/"
            "wa-gas-bulletin-board-wa-gbb/procedures-policies-and-guides"
        ),
        include_decision="include",
        include_reason="WA GBB GSI procedures, operation guides, and forms.",
        source_page_title="WA GBB procedures, policies and guides",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="gas_systems_guides",
        source_page_url=(
            "https://www.aemo.com.au/energy-systems/market-it-systems/"
            "gas-systems-guides"
        ),
        include_decision="needs_human_review",
        include_reason="Mixed forms, online help, and guides need review before ingestion.",
        source_page_title="Gas systems guides",
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="gas_forecasting_planning",
        source_page_url="scope://aemo-gas/gas-forecasting-and-planning-publications",
        include_decision="needs_human_review",
        include_reason=(
            "Planning publications are gas-relevant but outside the first "
            "operational-procedure corpus without operator review."
        ),
        source_page_title="Gas forecasting and planning publications",
        fetch_links=False,
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="gas_emergency_management",
        source_page_url="scope://aemo-gas/gas-emergency-management-publications",
        include_decision="needs_human_review",
        include_reason=(
            "Emergency-management publications are gas-relevant but outside the "
            "first operational-procedure corpus without operator review."
        ),
        source_page_title="Gas emergency management publications",
        fetch_links=False,
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="manual_seed",
        source_page_url="scope://aemo-gas/consultation-and-historical-manual-seeds",
        include_decision="needs_human_review",
        include_reason=(
            "Consultation and historical stakeholder PDFs require explicit manual "
            "seeds before crawling."
        ),
        source_page_title="Consultation and historical manual seeds",
        fetch_links=False,
    ),
    AEMOGasDocumentSourcePage(
        corpus_source="excluded_external_or_non_pdf",
        source_page_url="scope://aemo-gas/external-authenticated-nemweb-and-non-pdf-assets",
        include_decision="exclude",
        exclude_reason=(
            "External bodies, authenticated portals, NEMWeb data, APIs, software "
            "bundles, and non-PDF downloads are link metadata only for this slice."
        ),
        source_page_title="External, authenticated, NEMWeb, and non-PDF assets",
        fetch_links=False,
    ),
)
