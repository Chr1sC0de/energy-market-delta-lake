"""AEMO gas source-page scraper and document metadata helpers."""

import re
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from html import unescape
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import bs4
from requests import Response

from aemo_etl.factories.aemo_gas_documents.models import (
    AEMOGasDocumentPendingObservation,
    AEMOGasDocumentSourcePage,
    IncludeDecision,
)

AEMO_ROOT_URL = "https://www.aemo.com.au"
PDF_SUFFIX = ".pdf"
AUTHENTICATED_HOSTS = frozenset({"portal.prod.nemnet.net.au"})
MEDIA_PATH_FRAGMENT = "/-/media/"
VERSION_PATTERN = re.compile(
    r"\b(?:v(?:ersion)?\.?\s*)?(\d+(?:\.\d+){1,3})\b",
    re.IGNORECASE,
)
LEADING_DATE_PATTERN = re.compile(
    r"^\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4}|\d{1,2}/\d{1,2}/\d{2,4}|[A-Z][a-z]+\s+\d{4})\b"
)
EFFECTIVE_DATE_PATTERN = re.compile(
    r"\beffective\s+date\s*:?\s*([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})",
    re.IGNORECASE,
)
SIZE_SUFFIX_PATTERN = re.compile(
    r"\s*\(?\s*\d+(?:\.\d+)?\s*(?:kb|mb|gb)\s*\)?\s*$", re.IGNORECASE
)
NON_WORD_PATTERN = re.compile(r"[^a-z0-9]+")


def soup_getter(html: str) -> bs4.BeautifulSoup:
    """Parse AEMO HTML into a BeautifulSoup document."""
    return bs4.BeautifulSoup(html, features="html.parser")


def normalized_text(value: str) -> str:
    """Return whitespace-normalized display text."""
    return " ".join(unescape(value).split())


def slugify(value: str) -> str:
    """Return a lowercase slug safe for identifiers and S3 path segments."""
    slug = NON_WORD_PATTERN.sub("-", value.lower()).strip("-")
    return slug or "unknown"


def normalize_source_url(source_url: str) -> tuple[str, str | None, str | None]:
    """Return normalized URL, query string, and AEMO media revision."""
    parsed = urlparse(source_url)
    query_pairs = parse_qs(parsed.query, keep_blank_values=True)
    normalized_query = urlencode(
        sorted((key, value) for key, values in query_pairs.items() for value in values)
    )
    normalized = urlunparse(
        (
            parsed.scheme.lower() or "https",
            parsed.netloc.lower(),
            parsed.path.lower(),
            "",
            normalized_query,
            "",
        )
    )
    media_revision_values = query_pairs.get("rev")
    media_revision = media_revision_values[0] if media_revision_values else None
    return normalized, normalized_query or None, media_revision


def is_pdf_url(url: str) -> bool:
    """Return whether the URL path points to a PDF file."""
    return urlparse(url).path.lower().endswith(PDF_SUFFIX)


def is_aemo_public_url(url: str) -> bool:
    """Return whether the URL is an unauthenticated public AEMO URL."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.netloc.lower()
    return host == "www.aemo.com.au"


def is_authenticated_url(url: str) -> bool:
    """Return whether a URL belongs to a known authenticated portal."""
    return urlparse(url).netloc.lower() in AUTHENTICATED_HOSTS


def clean_document_title(source_link_text: str, source_url: str) -> str:
    """Return a readable document title from link text or URL basename."""
    text = normalized_text(source_link_text)
    if not text:
        path_name = urlparse(source_url).path.rsplit("/", 1)[-1]
        text = path_name.rsplit(".", 1)[0].replace("-", " ").replace("_", " ")
    text = SIZE_SUFFIX_PATTERN.sub("", text)
    text = VERSION_PATTERN.sub("", text)
    text = LEADING_DATE_PATTERN.sub("", text)
    text = text.replace("PDF", "")
    return normalized_text(text).strip(" -:") or "Unknown document"


def document_family_id(corpus_source: str, title: str) -> str:
    """Return a stable document-family identifier."""
    return f"{slugify(corpus_source)}__{slugify(title)}"


def parse_document_version(source_link_text: str, source_url: str) -> str | None:
    """Parse a visible document version token when one is present."""
    match = VERSION_PATTERN.search(f"{source_link_text} {source_url}")
    if match is None:
        return None
    return match.group(1)


def parse_published_date(source_link_text: str) -> str | None:
    """Parse a leading visible publication date string when present."""
    match = LEADING_DATE_PATTERN.search(source_link_text)
    if match is None:
        return None
    return normalized_text(match.group(1))


def parse_effective_date(source_link_text: str) -> str | None:
    """Parse an effective-date string when present."""
    match = EFFECTIVE_DATE_PATTERN.search(source_link_text)
    if match is None:
        return None
    return normalized_text(match.group(1))


def infer_document_kind(source_link_text: str, source_url: str) -> str:
    """Infer the document kind from visible text and URL path."""
    haystack = f"{source_link_text} {urlparse(source_url).path}".lower()
    kind_terms = (
        ("report_specification", ("report specification", "reports specification")),
        ("technical_document", ("technical", "data model")),
        ("procedure", ("procedure", "procedures")),
        ("agreement", ("agreement", "deed")),
        ("methodology", ("methodology",)),
        ("template", ("template",)),
        ("form", ("form", "request")),
        ("guide", ("guide", "guideline", "guidelines", "protocol")),
        ("market_notice", ("market notice",)),
        ("publication", ("publication", "forecast", "planning")),
    )
    for kind, terms in kind_terms:
        if any(term in haystack for term in terms):
            return kind
    return "unknown"


def extract_page_title(soup: bs4.BeautifulSoup, fallback: str | None) -> str | None:
    """Extract a page title from a heading or the configured fallback."""
    heading = soup.find(["h1", "h2"])
    if isinstance(heading, bs4.Tag):
        title = normalized_text(heading.get_text(" "))
        if title:
            return title
    if soup.title is not None and soup.title.string is not None:
        title = normalized_text(soup.title.string)
        if title:
            return title
    return fallback


def source_page_observation(
    source_page: AEMOGasDocumentSourcePage,
    *,
    observed_at: datetime,
    source_page_title: str | None = None,
) -> AEMOGasDocumentPendingObservation:
    """Return the metadata observation for the source page itself."""
    normalized, query, media_revision = normalize_source_url(
        source_page.source_page_url
    )
    return AEMOGasDocumentPendingObservation(
        observation_type="source_page",
        corpus_source=source_page.corpus_source,
        source_page_url=source_page.source_page_url,
        source_page_title=source_page_title or source_page.source_page_title,
        source_page_section=source_page.source_page_section,
        source_page_observed_at=observed_at,
        source_link_text=None,
        source_url=source_page.source_page_url,
        resolved_url=source_page.source_page_url,
        normalized_source_url=normalized,
        source_url_query=query,
        document_family_id=None,
        document_title=None,
        document_kind="source_page",
        include_decision=source_page.include_decision,
        include_reason=source_page.include_reason,
        exclude_reason=source_page.exclude_reason,
        document_version=None,
        published_date=None,
        effective_date=None,
        media_revision=media_revision,
        should_download=False,
    )


def _nearest_section(tag: bs4.Tag) -> str | None:
    """Return the nearest preceding local section heading for a link."""
    heading = tag.find_previous(["h2", "h3", "h4"])
    if not isinstance(heading, bs4.Tag):
        return None
    text = normalized_text(heading.get_text(" "))
    return text or None


def _link_text(tag: bs4.Tag) -> str:
    """Return a link's reader-visible text."""
    return normalized_text(tag.get_text(" "))


def _link_decision(
    source_page: AEMOGasDocumentSourcePage,
    absolute_url: str,
) -> tuple[IncludeDecision, str | None, str | None, bool]:
    """Classify one observed source link."""
    if source_page.include_decision == "needs_human_review":
        return (
            "needs_human_review",
            source_page.include_reason,
            source_page.exclude_reason,
            False,
        )
    if source_page.include_decision == "exclude":
        return "exclude", source_page.include_reason, source_page.exclude_reason, False
    if is_authenticated_url(absolute_url):
        return "exclude", None, "Authenticated portal link excluded.", False
    if not is_aemo_public_url(absolute_url):
        return "exclude", None, "External or non-public AEMO link excluded.", False
    if not is_pdf_url(absolute_url):
        return "exclude", None, "Non-PDF link excluded from this corpus slice.", False
    return "include", source_page.include_reason, None, True


def link_observation(
    source_page: AEMOGasDocumentSourcePage,
    tag: bs4.Tag,
    *,
    observed_at: datetime,
    page_url: str,
    page_title: str | None,
) -> AEMOGasDocumentPendingObservation | None:
    """Build one source-link observation from an HTML anchor tag."""
    href = tag.get("href")
    if href is None:
        return None
    absolute_url = urljoin(page_url, str(href))
    text = _link_text(tag)
    include_decision, include_reason, exclude_reason, should_download = _link_decision(
        source_page, absolute_url
    )
    normalized, query, media_revision = normalize_source_url(absolute_url)
    title = clean_document_title(text, absolute_url)
    return AEMOGasDocumentPendingObservation(
        observation_type="link",
        corpus_source=source_page.corpus_source,
        source_page_url=page_url,
        source_page_title=page_title,
        source_page_section=_nearest_section(tag) or source_page.source_page_section,
        source_page_observed_at=observed_at,
        source_link_text=text,
        source_url=absolute_url,
        resolved_url=absolute_url,
        normalized_source_url=normalized,
        source_url_query=query,
        document_family_id=document_family_id(source_page.corpus_source, title),
        document_title=title,
        document_kind=infer_document_kind(text, absolute_url),
        include_decision=include_decision,
        include_reason=include_reason,
        exclude_reason=exclude_reason,
        document_version=parse_document_version(text, absolute_url),
        published_date=parse_published_date(text),
        effective_date=parse_effective_date(text),
        media_revision=media_revision,
        should_download=should_download,
    )


def _is_child_page_link(parent_url: str, candidate_url: str) -> bool:
    """Return whether candidate_url is a crawlable child page."""
    parent = urlparse(parent_url)
    candidate = urlparse(candidate_url)
    if candidate.netloc.lower() != parent.netloc.lower():
        return False
    if MEDIA_PATH_FRAGMENT in candidate.path.lower():
        return False
    if is_pdf_url(candidate_url):
        return False
    parent_path = parent.path.rstrip("/")
    candidate_path = candidate.path.rstrip("/")
    return candidate_path.startswith(f"{parent_path}/")


def child_source_pages(
    source_page: AEMOGasDocumentSourcePage,
    soup: bs4.BeautifulSoup,
) -> list[AEMOGasDocumentSourcePage]:
    """Discover same-scope child pages from a configured source page."""
    children: list[AEMOGasDocumentSourcePage] = []
    seen: set[str] = set()
    for element in soup.find_all("a"):
        if not isinstance(element, bs4.Tag):
            continue
        href = element.get("href")
        if href is None:
            continue
        absolute_url = urljoin(source_page.source_page_url, str(href))
        if absolute_url in seen or not _is_child_page_link(
            source_page.source_page_url, absolute_url
        ):
            continue
        seen.add(absolute_url)
        children.append(
            AEMOGasDocumentSourcePage(
                corpus_source=source_page.corpus_source,
                source_page_url=absolute_url,
                include_decision=source_page.include_decision,
                include_reason=source_page.include_reason,
                exclude_reason=source_page.exclude_reason,
                source_page_title=_link_text(element) or source_page.source_page_title,
                source_page_section=_nearest_section(element),
            )
        )
    return children


def _page_link_observations(
    source_page: AEMOGasDocumentSourcePage,
    soup: bs4.BeautifulSoup,
    *,
    observed_at: datetime,
    page_url: str,
    page_title: str | None,
) -> list[AEMOGasDocumentPendingObservation]:
    """Return all link observations from a source page soup."""
    observations: list[AEMOGasDocumentPendingObservation] = []
    seen: set[tuple[str, str]] = set()
    for element in soup.find_all("a"):
        if not isinstance(element, bs4.Tag):
            continue
        observation = link_observation(
            source_page,
            element,
            observed_at=observed_at,
            page_url=page_url,
            page_title=page_title,
        )
        if observation is None:
            continue
        dedupe_key = (observation.source_url, observation.source_link_text or "")
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        observations.append(observation)
    return observations


def discover_aemo_gas_document_observations(
    *,
    source_pages: Iterable[AEMOGasDocumentSourcePage],
    request_getter: Callable[[str], Response],
    observed_at: datetime | None = None,
    parse_soup: Callable[[str], bs4.BeautifulSoup] = soup_getter,
) -> list[AEMOGasDocumentPendingObservation]:
    """Discover source-page and source-link observations for AEMO gas documents."""
    if observed_at is None:
        observed_at = datetime.now(UTC)

    observations: list[AEMOGasDocumentPendingObservation] = []
    queued_pages = list(source_pages)
    seen_pages: set[str] = set()

    while queued_pages:
        source_page = queued_pages.pop(0)
        if source_page.source_page_url in seen_pages:
            continue
        seen_pages.add(source_page.source_page_url)

        page_title = source_page.source_page_title
        soup: bs4.BeautifulSoup | None = None
        if source_page.fetch_links:
            response = request_getter(source_page.source_page_url)
            soup = parse_soup(response.text)
            page_title = extract_page_title(soup, source_page.source_page_title)

        observations.append(
            source_page_observation(
                source_page,
                observed_at=observed_at,
                source_page_title=page_title,
            )
        )

        if soup is None:
            continue

        observations.extend(
            _page_link_observations(
                source_page,
                soup,
                observed_at=observed_at,
                page_url=source_page.source_page_url,
                page_title=page_title,
            )
        )
        if source_page.discover_child_pages:
            queued_pages.extend(child_source_pages(source_page, soup))

    return observations
