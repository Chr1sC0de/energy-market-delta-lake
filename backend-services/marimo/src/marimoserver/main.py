"""FastAPI wrapper for the marimo notebook server.

Serves marimo notebooks from the ``notebooks/`` directory using marimo's
built-in ASGI integration (``marimo.create_asgi_app``).  A ``/health``
endpoint is exposed for container healthchecks.

The app is designed to be served behind a reverse proxy (Caddy) under the
``/marimo`` prefix, matching the mounted notebook paths inside the container.

Notebook discovery uses ``with_app`` in a loop so each ``.py`` file in
the notebooks directory is mounted at ``/marimo/<stem>``.  A
``with_dynamic_directory`` approach would be preferable for hot-reload,
but marimo does not support ``path="/"`` for dynamic directories.
"""

from __future__ import annotations

import mimetypes
import os
from html import escape
from pathlib import Path, PurePosixPath
from typing import Any

import marimo
from fastapi import FastAPI
from starlette.responses import HTMLResponse, JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from marimoserver.dashboard_registry import (
    ROADMAP_AUDIENCES,
    DashboardAudience,
    DashboardRegistryEntry,
    DashboardStatus,
    dashboard_registry as load_dashboard_registry,
    dashboard_registry_payload,
)

NOTEBOOKS_DIR = Path(os.environ.get("MARIMO_NOTEBOOKS_DIR", "notebooks"))

# Ensure font MIME types are registered — Python's mimetypes module does not
# always include woff/woff2 depending on the host OS, causing uvicorn to fall
# back to text/plain which the browser rejects for font loading.
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/woff", ".woff")

IMMUTABLE_ASSET_CACHE_CONTROL = "public, max-age=31536000, immutable"

_INDEX_CSS = """
        :root {
            color-scheme: light;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            color: var(--emdl-ink, #1b2324);
            background: var(--emdl-paper, #f6f8f3);
            font-family: ui-sans-serif, system-ui, -apple-system,
                BlinkMacSystemFont, "Segoe UI", sans-serif;
            line-height: 1.5;
        }

        main {
            width: min(1180px, calc(100% - 32px));
            margin: 0 auto;
            padding: 48px 0 64px;
        }

        .hero {
            display: grid;
            gap: 18px;
            margin-bottom: 28px;
        }

        .eyebrow {
            margin: 0;
            color: var(--emdl-green, #3e7a54);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
        }

        h1 {
            max-width: 760px;
            margin: 0;
            color: var(--emdl-slate, #354348);
            font-size: 3.4rem;
            line-height: 1.02;
            letter-spacing: 0;
        }

        .hero-copy {
            max-width: 780px;
            margin: 0;
            color: var(--emdl-muted, #566365);
            font-size: 1.05rem;
        }

        .summary {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            padding: 0;
            margin: 4px 0 0;
            list-style: none;
        }

        .summary li {
            min-width: 150px;
            padding: 10px 14px;
            border: 1px solid var(--emdl-line, #cfdbd6);
            border-radius: 8px;
            background: var(--emdl-panel, #ffffff);
            box-shadow: var(--emdl-soft-shadow, 0 8px 28px rgb(27 35 36 / 0.08));
        }

        .summary-value {
            display: block;
            font-size: 1.45rem;
            font-weight: 760;
            line-height: 1.1;
        }

        .summary-label {
            display: block;
            color: var(--emdl-muted, #566365);
            font-size: 0.82rem;
        }

        .overview-strip {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-top: 8px;
        }

        .overview-card,
        .spotlight,
        .search-box {
            border: 1px solid var(--emdl-line, #cfdbd6);
            border-radius: 8px;
            background: var(--emdl-panel, #ffffff);
            box-shadow: var(--emdl-soft-shadow, 0 8px 28px rgb(27 35 36 / 0.08));
        }

        .overview-card {
            padding: 12px;
        }

        .overview-card strong {
            display: block;
            color: var(--emdl-slate, #354348);
        }

        .overview-card span {
            color: var(--emdl-muted, #566365);
            font-size: 0.82rem;
        }

        .filter-controls label {
            display: inline-flex;
            align-items: center;
            min-height: 36px;
            padding: 7px 12px;
            border: 1px solid var(--emdl-line, #cfdbd6);
            border-radius: 999px;
            color: var(--emdl-slate, #354348);
            background: rgb(var(--emdl-panel-rgb, 255 255 255) / 0.86);
            font-size: 0.9rem;
            font-weight: 650;
            text-decoration: none;
        }

        .filter-controls label:hover {
            border-color: var(--emdl-blue, #166791);
            color: var(--emdl-blue, #166791);
        }

        .gallery-shell {
            position: relative;
        }

        .gallery-tools {
            position: sticky;
            top: 0;
            z-index: 3;
            display: grid;
            gap: 12px;
            margin: 22px 0;
            padding: 14px;
            border: 1px solid var(--emdl-line, #cfdbd6);
            border-radius: 8px;
            background: rgb(var(--emdl-paper-rgb, 246 248 243) / 0.94);
            backdrop-filter: blur(12px);
        }

        .search-box {
            display: grid;
            grid-template-columns: auto minmax(0, 1fr);
            gap: 10px;
            align-items: center;
            padding: 10px 12px;
        }

        .search-box svg {
            color: var(--emdl-blue, #166791);
        }

        .search-box input {
            min-width: 0;
            border: 0;
            outline: 0;
            color: var(--emdl-ink, #1b2324);
            background: transparent;
            font: inherit;
        }

        .filter-heading {
            margin: 0 0 6px;
            color: var(--emdl-muted, #566365);
            font-size: 0.74rem;
            font-weight: 800;
            text-transform: uppercase;
        }

        .audience-filter {
            position: absolute;
            inline-size: 1px;
            block-size: 1px;
            opacity: 0;
            pointer-events: none;
        }

        .filter-controls {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 18px;
        }

        .filter-block .filter-controls {
            margin-bottom: 0;
        }

        #audience-all:checked ~ .gallery-tools label[for="audience-all"],
        #audience-platform-operations:checked ~ .gallery-tools label[for="audience-platform-operations"],
        #audience-operator:checked ~ .gallery-tools label[for="audience-operator"],
        #audience-analyst:checked ~ .gallery-tools label[for="audience-analyst"],
        #audience-stakeholder:checked ~ .gallery-tools label[for="audience-stakeholder"],
        #audience-data-engineer:checked ~ .gallery-tools label[for="audience-data-engineer"] {
            border-color: var(--emdl-blue, #166791);
            color: var(--emdl-panel, #ffffff);
            background: var(--emdl-blue, #166791);
        }

        #audience-platform-operations:checked ~ .dashboard-grid .dashboard-card:not(.audience-platform-operations),
        #audience-operator:checked ~ .dashboard-grid .dashboard-card:not(.audience-operator),
        #audience-analyst:checked ~ .dashboard-grid .dashboard-card:not(.audience-analyst),
        #audience-stakeholder:checked ~ .dashboard-grid .dashboard-card:not(.audience-stakeholder),
        #audience-data-engineer:checked ~ .dashboard-grid .dashboard-card:not(.audience-data-engineer) {
            display: none;
        }

        .dashboard-card[hidden] {
            display: none !important;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr));
            gap: 16px;
        }

        .dashboard-card {
            display: grid;
            gap: 14px;
            min-width: 0;
            min-height: 340px;
            padding: 20px;
            border: 1px solid var(--emdl-line, #cfdbd6);
            border-radius: 8px;
            color: inherit;
            background: var(--emdl-panel, #ffffff);
            box-shadow: var(--emdl-soft-shadow, 0 8px 28px rgb(27 35 36 / 0.08));
            text-decoration: none;
        }

        .dashboard-card > * {
            min-width: 0;
        }

        .dashboard-card:focus-visible {
            outline: 3px solid rgb(var(--emdl-blue-rgb, 22 103 145) / 0.42);
            outline-offset: 4px;
        }

        .dashboard-card--available:hover {
            border-color: var(--emdl-blue, #166791);
            box-shadow: var(--emdl-shadow, 0 18px 46px rgb(27 35 36 / 0.1));
            transform: translateY(-1px);
        }

        .dashboard-card h2 {
            margin: 0;
            color: var(--emdl-slate, #354348);
            font-size: 1.28rem;
            line-height: 1.2;
            letter-spacing: 0;
        }

        .dashboard-card p {
            margin: 0;
            color: var(--emdl-muted, #566365);
        }

        .card-topline,
        .audience-tags,
        .asset-list {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            min-width: 0;
        }

        .status-pill,
        .audience-tag,
        .asset-pill {
            display: inline-flex;
            align-items: center;
            max-width: 100%;
            min-width: 0;
            min-height: 28px;
            padding: 4px 8px;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            line-height: 1.2;
            overflow-wrap: anywhere;
            text-align: left;
            white-space: normal;
            word-break: break-word;
        }

        .status-pill--available {
            color: var(--emdl-green, #3e7a54);
            background: rgb(var(--emdl-green-rgb, 62 122 84) / 0.13);
        }

        .status-pill--planned {
            color: var(--emdl-amber, #b2682a);
            background: rgb(var(--emdl-amber-rgb, 178 104 42) / 0.14);
        }

        .status-pill--unmounted {
            color: var(--emdl-red, #9e4839);
            background: rgb(var(--emdl-red-rgb, 158 72 57) / 0.12);
        }

        .story-pill {
            color: var(--emdl-blue, #166791);
            background: rgb(var(--emdl-blue-rgb, 22 103 145) / 0.11);
        }

        .audience-tag {
            color: var(--emdl-slate, #354348);
            background: var(--emdl-service-band, #eef4f1);
        }

        .asset-list {
            padding: 0;
            margin: 0;
            list-style: none;
        }

        .asset-pill {
            color: var(--emdl-muted, #566365);
            background: rgb(var(--emdl-line-rgb, 207 219 214) / 0.34);
        }

        .dashboard-action {
            align-self: end;
            color: var(--emdl-blue, #166791);
            font-weight: 760;
        }

        .dashboard-action--planned,
        .dashboard-action--unmounted {
            color: var(--emdl-muted, #566365);
        }

        .spotlight {
            display: grid;
            gap: 8px;
            margin: 18px 0;
            padding: 16px;
        }

        .spotlight h2 {
            margin: 0;
        }

        .spotlight p {
            margin: 0;
            color: var(--emdl-muted, #566365);
        }

        .spotlight-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        @media (max-width: 640px) {
            main {
                width: min(100% - 24px, 1180px);
                padding-top: 32px;
            }

            .dashboard-card {
                min-height: auto;
            }

            h1 {
                font-size: 2.25rem;
            }

            .overview-strip {
                grid-template-columns: 1fr;
            }

            .gallery-tools {
                position: static;
            }
        }

        @media (prefers-color-scheme: dark) {
            :root {
                color-scheme: dark;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                transition-duration: 0.001ms !important;
                animation-duration: 0.001ms !important;
                animation-iteration-count: 1 !important;
                scroll-behavior: auto !important;
            }
        }
"""


class StaticAssetHeadersMiddleware:
    """Set stable response headers for Marimo packaged static assets.

    uvicorn's StaticFiles falls back to ``text/plain`` for ``.woff`` and
    ``.woff2`` on systems where the OS MIME database does not include these
    types.  Browsers refuse to apply fonts served with the wrong MIME type,
    causing the notebook UI to render with fallback fonts.

    Marimo emits content-hashed JavaScript, CSS, image, and font asset paths
    under each notebook route.  Those package assets can be cached immutably
    while notebook HTML, registry JSON, manifests, and favicons stay outside
    this cache rule.
    """

    _CONTENT_TYPE_OVERRIDES: dict[str, str] = {
        ".woff2": "font/woff2",
        ".woff": "font/woff",
    }

    def __init__(self, app: ASGIApp) -> None:
        """Store the wrapped ASGI app."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Patch font response MIME types before sending HTTP responses."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope.get("path", "")
        suffix = PurePosixPath(path).suffix.lower()
        content_type_override = self._CONTENT_TYPE_OVERRIDES.get(suffix)
        cache_control = _cache_control_for_path(path)

        if content_type_override is None and cache_control is None:
            await self.app(scope, receive, send)
            return

        async def send_with_static_asset_headers(message: Any) -> None:  # noqa: ANN401
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                if content_type_override is not None and message.get("status") == 200:
                    headers = [
                        (k, v) for k, v in headers if k.lower() != b"content-type"
                    ]
                    headers.append((b"content-type", content_type_override.encode()))
                if cache_control is not None and message.get("status") == 200:
                    headers = [
                        (k, v) for k, v in headers if k.lower() != b"cache-control"
                    ]
                    headers.append((b"cache-control", cache_control.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_static_asset_headers)


def _cache_control_for_path(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    if len(parts) >= 4 and parts[1] == "marimo" and parts[3] == "assets":
        return IMMUTABLE_ASSET_CACHE_CONTROL
    return None


app = FastAPI(title="Marimo Notebook Server")
app.add_middleware(StaticAssetHeadersMiddleware)  # type: ignore[arg-type]


@app.get("/health")
@app.get("/marimo/health")
async def health() -> JSONResponse:
    """Liveness / readiness probe for container orchestrators."""
    return JSONResponse(content={"status": "ok"})


@app.get("/marimo/dashboard-registry.json")
async def dashboard_registry_endpoint() -> JSONResponse:
    """Return the code-local dashboard roadmap registry."""
    return JSONResponse(content=dashboard_registry_payload())


# ---------------------------------------------------------------------------
# Discover notebooks and mount each one as a marimo sub-app.
# ---------------------------------------------------------------------------
server = marimo.create_asgi_app()
app_names: list[str] = []

if NOTEBOOKS_DIR.is_dir():
    for notebook in sorted(NOTEBOOKS_DIR.iterdir()):
        if notebook.suffix == ".py":
            name = notebook.stem
            server = server.with_app(path=f"/{name}", root=str(notebook))
            app_names.append(name)


@app.get("/marimo")
async def index() -> HTMLResponse:
    """Render the dashboard concept gallery hub."""
    html = _render_index_html(mounted_notebook_names=set(app_names))
    return HTMLResponse(content=html)


def _render_index_html(mounted_notebook_names: set[str]) -> str:
    entries = load_dashboard_registry()
    available_count = sum(
        1 for entry in entries if _notebook_href(entry, mounted_notebook_names)
    )
    planned_count = sum(
        1 for entry in entries if entry.status is DashboardStatus.PLANNED
    )
    audience_inputs = "\n".join(
        _render_audience_input(audience) for audience in ROADMAP_AUDIENCES
    )
    audience_labels = "\n".join(
        _render_audience_label(audience) for audience in ROADMAP_AUDIENCES
    )
    overview_cards = "\n".join(
        _render_overview_card(story, entries)
        for story in ("market", "operations", "trust", "concepts")
    )
    cards = "\n".join(
        _render_dashboard_card(entry, mounted_notebook_names) for entry in entries
    )
    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marimo Concept Gallery</title>
    <link rel="stylesheet" href="/theme.css">
    <style>
{_INDEX_CSS}
    </style>
</head>
<body>
    <main>
        <section class="hero" aria-labelledby="gallery-title">
            <p class="eyebrow">Generated Market context roadmap</p>
            <h1 id="gallery-title">Marimo concept gallery</h1>
            <p class="hero-copy">
                Curated and planned gas-market dashboards aligned to generated
                Market context concepts, audience tags, and backing
                silver.gas_model assets.
            </p>
            <ul class="summary" aria-label="Dashboard roadmap summary">
                <li>
                    <span class="summary-value">{available_count}</span>
                    <span class="summary-label">available notebooks</span>
                </li>
                <li>
                    <span class="summary-value">{planned_count}</span>
                    <span class="summary-label">planned concepts</span>
                </li>
                <li>
                    <span class="summary-value">{len(entries)}</span>
                    <span class="summary-label">registry concepts</span>
                </li>
            </ul>
            <div class="overview-strip" aria-label="Market story overview">
{overview_cards}
            </div>
        </section>

        <section class="gallery-shell" aria-label="Dashboard cards">
            <input
                class="audience-filter"
                type="radio"
                id="audience-all"
                name="audience-filter"
                checked
            >
{audience_inputs}
            <div class="gallery-tools">
                <label class="search-box" for="dashboard-search">
                    {_inline_icon("search")}
                    <input
                        id="dashboard-search"
                        type="search"
                        placeholder="Search dashboards, assets, audience, status"
                        autocomplete="off"
                    >
                </label>
                <div class="filter-block">
                    <p class="filter-heading">Audience filters</p>
                    <div class="filter-controls" aria-label="Audience filters">
                        <label for="audience-all">All audiences</label>
{audience_labels}
                    </div>
                </div>
            </div>
            <div class="spotlight" id="route-spotlight" tabindex="-1">
                <p class="eyebrow">Route spotlight</p>
                <h2>Source to dashboard route</h2>
                <p>
                    Select or focus a dashboard card to inspect its story group,
                    status, audience, and backing assets.
                </p>
                <div class="spotlight-meta" aria-label="Spotlight details">
                    <span class="asset-pill">Static fallback ready</span>
                    <span class="asset-pill">No auto-refresh timers</span>
                </div>
            </div>
            <div class="dashboard-grid">
{cards}
            </div>
        </section>
        <script>
{_INDEX_JS}
        </script>
    </main>
</body>
</html>"""
    return html


def _render_audience_input(audience: DashboardAudience) -> str:
    audience_value = escape(audience.value, quote=True)
    return f"""\
            <input
                class="audience-filter"
                type="radio"
                id="audience-{audience_value}"
                name="audience-filter"
            >"""


def _render_audience_label(audience: DashboardAudience) -> str:
    audience_value = escape(audience.value, quote=True)
    audience_label = escape(_label_from_slug(audience.value))
    return f'                <label for="audience-{audience_value}">{audience_label}</label>'


def _render_overview_card(
    story: str,
    entries: tuple[DashboardRegistryEntry, ...],
) -> str:
    count = sum(1 for entry in entries if _story_group(entry) == story)
    return f"""\
                <article class="overview-card">
                    <strong>{escape(_label_from_slug(story))}</strong>
                    <span>{count} dashboard concepts</span>
                </article>"""


def _render_dashboard_card(
    entry: DashboardRegistryEntry,
    mounted_notebook_names: set[str],
) -> str:
    href = _notebook_href(entry, mounted_notebook_names)
    story_group = _story_group(entry)
    audience_classes = " ".join(
        f"audience-{escape(audience.value, quote=True)}" for audience in entry.audiences
    )
    status_kind = _status_kind(entry, href)
    card_class = (
        f"dashboard-card dashboard-card--{status_kind} story-{story_group} "
        f"{audience_classes}"
    )
    search_text = " ".join(
        (
            entry.title,
            entry.description,
            entry.status.value,
            story_group,
            " ".join(audience.value for audience in entry.audiences),
            " ".join(entry.backing_assets),
        )
    )
    attributes = (
        f'class="{card_class}" '
        f'id="concept-{escape(entry.concept_id, quote=True)}" '
        f'data-concept-id="{escape(entry.concept_id, quote=True)}" '
        f'data-status="{escape(entry.status.value, quote=True)}" '
        f'data-availability="{escape(status_kind, quote=True)}" '
        f'data-story="{escape(story_group, quote=True)}" '
        f'data-search="{escape(search_text.lower(), quote=True)}"'
    )
    body = _render_dashboard_card_body(entry, status_kind, story_group)

    if href is not None:
        return f'                <a {attributes} href="{escape(href, quote=True)}">\n{body}\n                </a>'

    return f"                <article {attributes}>\n{body}\n                </article>"


def _render_dashboard_card_body(
    entry: DashboardRegistryEntry,
    status_kind: str,
    story_group: str,
) -> str:
    audience_tags = "\n".join(
        f'                    <span class="audience-tag">{escape(_label_from_slug(audience.value))}</span>'
        for audience in entry.audiences
    )
    assets = "\n".join(
        f'                    <li class="asset-pill">{escape(asset)}</li>'
        for asset in entry.backing_assets[:3]
    )
    if len(entry.backing_assets) == 0:
        assets = (
            '                    <li class="asset-pill">'
            "Registry or configuration metadata only</li>"
        )
    if len(entry.backing_assets) > 3:
        assets = (
            f"{assets}\n"
            f'                    <li class="asset-pill">+{len(entry.backing_assets) - 3} more</li>'
        )

    return f"""\
                    <div class="card-topline">
                        <span class="status-pill status-pill--{escape(status_kind, quote=True)}">
                            {escape(_status_label(status_kind))}
                        </span>
                        <span class="status-pill story-pill">
                            {escape(_label_from_slug(story_group))}
                        </span>
                    </div>
                    <div>
                        <h2>{escape(entry.title)}</h2>
                        <p>{escape(entry.description)}</p>
                    </div>
                    <div class="audience-tags" aria-label="Audience tags">
{audience_tags}
                    </div>
                    <ul class="asset-list" aria-label="Backing assets">
{assets}
                    </ul>
                    <span class="dashboard-action dashboard-action--{escape(status_kind, quote=True)}">
                        {escape(_action_label(status_kind))}
                    </span>"""


def _notebook_href(
    entry: DashboardRegistryEntry,
    mounted_notebook_names: set[str],
) -> str | None:
    if entry.status is not DashboardStatus.AVAILABLE:
        return None
    if entry.notebook_name not in mounted_notebook_names:
        return None
    return entry.notebook_route


def _status_kind(entry: DashboardRegistryEntry, href: str | None) -> str:
    if href is not None:
        return "available"
    if entry.status is DashboardStatus.PLANNED:
        return "planned"
    return "unmounted"


def _status_label(status_kind: str) -> str:
    if status_kind == "available":
        return "Available"
    if status_kind == "planned":
        return "Planned"
    return "Not mounted"


def _action_label(status_kind: str) -> str:
    if status_kind == "available":
        return "Open notebook"
    if status_kind == "planned":
        return "Planned dashboard"
    return "Notebook not present in this image"


def _story_group(entry: DashboardRegistryEntry) -> str:
    concept_text = " ".join(
        (
            entry.concept_id,
            entry.title,
            entry.description,
        )
    ).lower()
    searchable = " ".join((concept_text, " ".join(entry.backing_assets))).lower()
    if any(
        token in concept_text
        for token in (
            "price",
            "schedule",
            "settlement",
            "bid",
            "offer",
            "allocation",
            "market",
            "mos",
        )
    ):
        return "market"
    if any(
        token in searchable
        for token in (
            "readiness",
            "health",
            "lineage",
            "coverage",
            "freshness",
            "diagnostic",
            "dictionary",
            "citation",
            "asset catalogue",
        )
    ):
        return "trust"
    if any(
        token in searchable
        for token in (
            "flow",
            "storage",
            "capacity",
            "linepack",
            "notice",
            "forecast",
            "operation",
        )
    ):
        return "operations"
    if any(
        token in searchable
        for token in (
            "concept",
            "glossary",
            "explainer",
            "participant",
            "facility",
            "connection",
            "hub",
            "gas day",
        )
    ):
        return "concepts"
    return "market"


def _label_from_slug(value: str) -> str:
    return value.replace("-", " ").title()


def _inline_icon(name: str) -> str:
    if name == "search":
        return """\
                    <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none">
                        <path d="m21 21-4.3-4.3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                        <circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/>
                    </svg>"""
    return ""


_INDEX_JS = """
(() => {
    const search = document.querySelector("#dashboard-search");
    const cards = Array.from(document.querySelectorAll(".dashboard-card"));
    const spotlight = document.querySelector("#route-spotlight");

    const updateSearch = () => {
        const query = search.value.trim().toLowerCase();
        for (const card of cards) {
            const haystack = card.getAttribute("data-search") || "";
            card.hidden = query.length > 0 && !haystack.includes(query);
        }
    };

    const updateSpotlight = (card) => {
        if (!spotlight || !card) {
            return;
        }
        const title = card.querySelector("h2")?.textContent || "Dashboard route";
        const description = card.querySelector("p")?.textContent || "";
        const story = card.getAttribute("data-story") || "market";
        const status = card.getAttribute("data-availability") || card.getAttribute("data-status") || "available";
        const assets = Array.from(card.querySelectorAll(".asset-pill"))
            .slice(0, 4)
            .map((node) => `<span class="asset-pill">${node.textContent}</span>`)
            .join("");
        spotlight.innerHTML = `
            <p class="eyebrow">Route spotlight</p>
            <h2>${title}</h2>
            <p>${description}</p>
            <div class="spotlight-meta" aria-label="Spotlight details">
                <span class="asset-pill">${story}</span>
                <span class="asset-pill">${status}</span>
                ${assets}
            </div>
        `;
    };

    if (search) {
        search.addEventListener("input", updateSearch);
    }

    for (const card of cards) {
        card.addEventListener("mouseenter", () => updateSpotlight(card));
        card.addEventListener("focus", () => updateSpotlight(card));
    }

    if (cards.length > 0) {
        updateSpotlight(cards[0]);
    }
})();
"""


app.mount("/marimo", server.build())
