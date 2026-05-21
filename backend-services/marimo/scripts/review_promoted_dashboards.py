#!/usr/bin/env python3
"""Open promoted Marimo dashboards for repeatable browser review."""

import argparse
import importlib
import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from types import TracebackType
from typing import Protocol, cast
from urllib.parse import urljoin

PROMOTED_DASHBOARD_ROUTES: tuple[str, ...] = (
    "/marimo/data_readiness_overview/",
    "/marimo/glossary_explorer/",
    "/marimo/system_notices/",
    "/marimo/gas_market_prices/",
    "/marimo/gas_bid_offer_stack/",
)

DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_ARTIFACT_DIR = Path(
    os.environ.get("MARIMO_BROWSER_REVIEW_DIR", "/tmp/marimo-dashboard-review")
)
DEFAULT_TIMEOUT_MS = 90_000


@dataclass(frozen=True)
class ViewportSpec:
    """Browser viewport used by the Marimo dashboard review helper."""

    name: str
    width: int
    height: int


@dataclass(frozen=True)
class ControlProbe:
    """One visible control interaction the helper exercises when present."""

    description: str
    text: str
    exact: bool = True
    optional: bool = False


@dataclass(frozen=True)
class DashboardReviewSpec:
    """One promoted dashboard route and its expected browser-review surface."""

    route: str
    required_texts: tuple[str, ...]
    control_probes: tuple[ControlProbe, ...]


@dataclass(frozen=True)
class DashboardReviewRun:
    """Concrete route, viewport, and optional artifact destination."""

    route: str
    url: str
    viewport: ViewportSpec
    required_texts: tuple[str, ...]
    control_probes: tuple[ControlProbe, ...]
    screenshot_path: Path | None


class BrowserPage(Protocol):
    """Small structural subset of Playwright's Page API."""

    def goto(self, url: str, *, wait_until: str, timeout: float) -> None:
        """Navigate to a URL."""

    def set_viewport_size(self, viewport_size: dict[str, int]) -> None:
        """Set the viewport size."""

    def wait_for_timeout(self, timeout: float) -> None:
        """Wait for a fixed timeout in milliseconds."""

    def wait_for_function(
        self,
        expression: str,
        arg: object = None,
        *,
        timeout: float,
    ) -> object:
        """Wait for a browser-side function to return truthy."""

    def evaluate(self, expression: str, arg: object = None) -> object:
        """Evaluate a browser-side function."""

    def screenshot(self, *, path: str, full_page: bool) -> bytes:
        """Capture a screenshot."""


class Browser(Protocol):
    """Small structural subset of Playwright's Browser API."""

    def new_page(self) -> BrowserPage:
        """Open a new browser page."""

    def close(self) -> None:
        """Close the browser."""


class BrowserType(Protocol):
    """Small structural subset of Playwright's BrowserType API."""

    def launch(self, *, headless: bool) -> Browser:
        """Launch a browser."""


class PlaywrightRuntime(Protocol):
    """Small structural subset of the Playwright runtime."""

    chromium: BrowserType


class PlaywrightContextManager(Protocol):
    """Context manager returned by ``sync_playwright``."""

    def __enter__(self) -> PlaywrightRuntime:
        """Start Playwright."""

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        """Stop Playwright."""


type SyncPlaywright = Callable[[], PlaywrightContextManager]


_VISIBLE_TEXT_PRESENT_JS = """
({ text, exact }) => {
  const normalize = (value) => value.replace(/\\s+/g, " ").trim().toLowerCase();
  const targetText = normalize(text);
  const matches = (value) => {
    const normalized = normalize(value);
    return exact ? normalized === targetText : normalized.includes(targetText);
  };
  const isVisible = (element) => {
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return (
      style.visibility !== "hidden" &&
      style.display !== "none" &&
      rect.width > 0 &&
      rect.height > 0
    );
  };
  const walkElements = function* (root) {
    for (const element of Array.from(root.querySelectorAll("*"))) {
      yield element;
      if (element.shadowRoot) {
        yield* walkElements(element.shadowRoot);
      }
    }
  };
  return Array.from(walkElements(document.body)).some((element) => (
    isVisible(element) && matches(element.innerText ?? element.textContent ?? "")
  ));
}
"""

_CLICK_VISIBLE_TEXT_JS = """
({ text, exact }) => {
  const normalize = (value) => value.replace(/\\s+/g, " ").trim().toLowerCase();
  const targetText = normalize(text);
  const matches = (value) => {
    const normalized = normalize(value);
    return exact ? normalized === targetText : normalized.includes(targetText);
  };
  const isVisible = (element) => {
    const style = window.getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return (
      style.visibility !== "hidden" &&
      style.display !== "none" &&
      rect.width > 0 &&
      rect.height > 0
    );
  };
  const walkElements = function* (root) {
    for (const element of Array.from(root.querySelectorAll("*"))) {
      yield element;
      if (element.shadowRoot) {
        yield* walkElements(element.shadowRoot);
      }
    }
  };
  const selector = [
    "button",
    "label",
    "[role='button']",
    "[role='radio']",
    "[role='combobox']",
    "[aria-label]"
  ].join(",");
  const candidates = Array.from(walkElements(document.body)).filter(
    (element) => isVisible(element) &&
      matches(element.innerText ?? element.textContent ?? "")
  );
  for (const candidate of candidates) {
    const target = candidate.closest(selector) ?? candidate;
    if (isVisible(target)) {
      target.click();
      return true;
    }
  }
  return false;
}
"""


VIEWPORTS: tuple[ViewportSpec, ...] = (
    ViewportSpec(name="desktop", width=1440, height=1100),
    ViewportSpec(name="narrow", width=390, height=900),
)

REVIEW_SPECS: tuple[DashboardReviewSpec, ...] = (
    DashboardReviewSpec(
        route="/marimo/data_readiness_overview/",
        required_texts=(
            "Data Readiness Overview",
            "Dashboard brief",
            "Dashboard intent",
            "Runtime Configuration",
            "S3 Bucket Readiness",
        ),
        control_probes=(
            ControlProbe(
                description="refresh readiness run button",
                text="Refresh readiness",
            ),
        ),
    ),
    DashboardReviewSpec(
        route="/marimo/glossary_explorer/",
        required_texts=(
            "Glossary Explorer",
            "Dashboard brief",
            "Dashboard intent",
            "Marimo dashboard registry",
            "Concepts",
        ),
        control_probes=(),
    ),
    DashboardReviewSpec(
        route="/marimo/system_notices/",
        required_texts=(
            "Gas System Notices",
            "Dashboard brief",
            "Dashboard intent",
            "System notice read diagnostics",
            "Notice Summary",
        ),
        control_probes=(
            ControlProbe(description="refresh data run button", text="Refresh data"),
            ControlProbe(description="critical-only radio", text="Critical only"),
            ControlProbe(description="all-notices radio", text="All notices"),
            ControlProbe(description="active-now radio", text="Active now"),
            ControlProbe(
                description="all-loaded-notices radio",
                text="All loaded notices",
            ),
        ),
    ),
    DashboardReviewSpec(
        route="/marimo/gas_market_prices/",
        required_texts=(
            "Gas Market Prices",
            "Dashboard brief",
            "Dashboard intent",
            "Market price read diagnostics",
            "Bounded Price Trend Diagnostics",
            "Bounded Price Exception Candidates",
        ),
        control_probes=(
            ControlProbe(description="refresh data run button", text="Refresh data"),
            ControlProbe(description="gas-date dropdown", text="All gas dates"),
            ControlProbe(description="price-type dropdown", text="All price types"),
            ControlProbe(
                description="source-system dropdown",
                text="All source systems",
            ),
            ControlProbe(description="source-table dropdown", text="All source tables"),
        ),
    ),
    DashboardReviewSpec(
        route="/marimo/gas_bid_offer_stack/",
        required_texts=(
            "Gas Bid / Offer Stack",
            "Dashboard brief",
            "Dashboard intent",
            "Bid / Offer stack read diagnostics",
            "Bid / Offer Stack Summary",
            "Source Identifier Coverage",
        ),
        control_probes=(
            ControlProbe(description="refresh data run button", text="Refresh data"),
            ControlProbe(description="participant dropdown", text="All participants"),
            ControlProbe(description="facility dropdown", text="All facilities"),
            ControlProbe(description="zone/hub dropdown", text="All zones"),
            ControlProbe(
                description="source-system dropdown",
                text="All source systems",
            ),
        ),
    ),
)


def build_review_plan(
    base_url: str,
    artifact_dir: Path,
    *,
    screenshots: bool = False,
    routes: tuple[str, ...] = PROMOTED_DASHBOARD_ROUTES,
) -> tuple[DashboardReviewRun, ...]:
    """Return the concrete browser review runs for promoted dashboards."""
    spec_by_route = {spec.route: spec for spec in REVIEW_SPECS}
    runs: list[DashboardReviewRun] = []
    for route in routes:
        if route not in spec_by_route:
            raise ValueError(f"unsupported promoted dashboard route: {route}")
        spec = spec_by_route[route]
        for viewport in VIEWPORTS:
            screenshot_path = (
                artifact_dir / _screenshot_name(route, viewport)
                if screenshots
                else None
            )
            runs.append(
                DashboardReviewRun(
                    route=route,
                    url=dashboard_url(base_url, route),
                    viewport=viewport,
                    required_texts=spec.required_texts,
                    control_probes=spec.control_probes,
                    screenshot_path=screenshot_path,
                )
            )
    return tuple(runs)


def dashboard_url(base_url: str, route: str) -> str:
    """Return an absolute dashboard URL from a base URL and mounted route."""
    return urljoin(base_url.rstrip("/") + "/", route.lstrip("/"))


def default_artifact_dir() -> Path:
    """Return the default temp artifact directory for optional screenshots."""
    return DEFAULT_ARTIFACT_DIR


def review_plan_payload(runs: tuple[DashboardReviewRun, ...]) -> dict[str, object]:
    """Return a stable JSON-serializable review plan."""
    return {
        "dashboards": sorted({run.route for run in runs}),
        "viewports": [
            {"name": viewport.name, "width": viewport.width, "height": viewport.height}
            for viewport in VIEWPORTS
        ],
        "runs": [
            {
                "route": run.route,
                "url": run.url,
                "viewport": run.viewport.name,
                "required_texts": list(run.required_texts),
                "control_probes": [
                    {
                        "description": probe.description,
                        "text": probe.text,
                        "optional": probe.optional,
                    }
                    for probe in run.control_probes
                ],
                "screenshot_path": (
                    None if run.screenshot_path is None else str(run.screenshot_path)
                ),
            }
            for run in runs
        ],
    }


def run_browser_review(
    runs: tuple[DashboardReviewRun, ...],
    *,
    headless: bool = True,
    timeout_ms: int = DEFAULT_TIMEOUT_MS,
) -> list[str]:
    """Open review runs in Playwright and return evidence lines."""
    sync_playwright = _load_sync_playwright()

    evidence: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        page = browser.new_page()
        for run in runs:
            evidence.extend(_review_one_run(page, run, timeout_ms=timeout_ms))
        browser.close()
    return evidence


def _load_sync_playwright() -> SyncPlaywright:
    try:
        module = importlib.import_module("playwright.sync_api")
    except ImportError as import_error:
        raise RuntimeError(
            "Playwright is not installed. Run with "
            "`uv run --with playwright python scripts/review_promoted_dashboards.py`."
        ) from import_error

    return cast(SyncPlaywright, getattr(module, "sync_playwright"))


def _review_one_run(
    page: BrowserPage,
    run: DashboardReviewRun,
    *,
    timeout_ms: int,
) -> list[str]:
    page.set_viewport_size({"width": run.viewport.width, "height": run.viewport.height})
    page.goto(run.url, wait_until="domcontentloaded", timeout=float(timeout_ms))
    page.wait_for_timeout(1_500)
    evidence = [f"opened {run.route} at {run.viewport.name} ({run.url})"]

    for required_text in run.required_texts:
        _require_visible_text(page, required_text, timeout_ms=timeout_ms)
    evidence.append(f"verified required text: {', '.join(run.required_texts)}")

    exercised_controls = _exercise_control_probes(
        page,
        run.control_probes,
        timeout_ms=timeout_ms,
    )
    if exercised_controls:
        evidence.append(f"exercised controls: {', '.join(exercised_controls)}")
    else:
        evidence.append("exercised controls: none declared")

    if run.screenshot_path is not None:
        run.screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(run.screenshot_path), full_page=True)
        evidence.append(f"screenshot: {run.screenshot_path}")

    return evidence


def _require_visible_text(
    page: BrowserPage,
    text: str,
    *,
    timeout_ms: int,
) -> None:
    try:
        page.wait_for_function(
            _VISIBLE_TEXT_PRESENT_JS,
            arg={"text": text, "exact": False},
            timeout=float(timeout_ms),
        )
    except Exception as visibility_error:
        raise RuntimeError(
            f"required dashboard text was not visible: {text}"
        ) from visibility_error


def _exercise_control_probes(
    page: BrowserPage,
    probes: tuple[ControlProbe, ...],
    *,
    timeout_ms: int,
) -> list[str]:
    exercised_controls: list[str] = []
    for probe in probes:
        if not _visible_text_present(page, probe.text, exact=probe.exact):
            if probe.optional:
                continue
            raise RuntimeError(f"control was not visible: {probe.description}")
        try:
            clicked = page.evaluate(
                _CLICK_VISIBLE_TEXT_JS,
                {"text": probe.text, "exact": probe.exact},
            )
        except Exception as click_error:
            raise RuntimeError(
                f"control could not be exercised: {probe.description}"
            ) from click_error
        if clicked is not True:
            raise RuntimeError(f"control was not clickable: {probe.description}")
        exercised_controls.append(probe.description)
    return exercised_controls


def _visible_text_present(page: BrowserPage, text: str, *, exact: bool) -> bool:
    present = page.evaluate(
        _VISIBLE_TEXT_PRESENT_JS,
        {"text": text, "exact": exact},
    )
    return present is True


def _screenshot_name(route: str, viewport: ViewportSpec) -> str:
    route_slug = route.strip("/").replace("/", "__")
    return f"{route_slug}__{viewport.name}.png"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Open promoted Marimo dashboards at desktop and narrow viewports "
            "for repeatable Playwright review."
        )
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help="Base URL for the running Marimo FastAPI or Caddy route.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=default_artifact_dir(),
        help="Directory for optional screenshots; defaults outside the repo.",
    )
    parser.add_argument(
        "--route",
        action="append",
        choices=PROMOTED_DASHBOARD_ROUTES,
        help="Limit review to one promoted dashboard route; may be repeated.",
    )
    parser.add_argument(
        "--screenshots",
        action="store_true",
        help="Capture full-page screenshots into --artifact-dir.",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run Chromium headed instead of headless.",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=DEFAULT_TIMEOUT_MS,
        help="Per-action timeout in milliseconds.",
    )
    parser.add_argument(
        "--print-plan",
        action="store_true",
        help="Print the dashboard, viewport, and control plan without opening a browser.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the promoted-dashboard browser review helper."""
    parsed_args = _parse_args(sys.argv[1:] if argv is None else argv)
    routes = (
        PROMOTED_DASHBOARD_ROUTES
        if parsed_args.route is None
        else tuple(parsed_args.route)
    )
    runs = build_review_plan(
        parsed_args.base_url,
        parsed_args.artifact_dir,
        screenshots=parsed_args.screenshots,
        routes=routes,
    )

    if parsed_args.print_plan:
        json.dump(review_plan_payload(runs), sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0

    try:
        evidence = run_browser_review(
            runs,
            headless=not parsed_args.headed,
            timeout_ms=parsed_args.timeout_ms,
        )
    except RuntimeError as review_error:
        sys.stderr.write(f"ERROR: {review_error}\n")
        return 1

    for line in evidence:
        sys.stdout.write(f"{line}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
