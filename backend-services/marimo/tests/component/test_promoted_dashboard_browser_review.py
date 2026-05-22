"""Component coverage for the promoted dashboard browser-review helper."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

REVIEW_SCRIPT = Path(__file__).parents[2] / "scripts" / "review_promoted_dashboards.py"


class _FakeBrowserPage:
    def __init__(self) -> None:
        self.viewport_size: dict[str, int] | None = None
        self.opened_url: str | None = None
        self.wait_for_function_calls: list[tuple[str, object]] = []
        self.evaluate_calls: list[tuple[str, object]] = []

    def goto(self, url: str, *, wait_until: str, timeout: float) -> None:
        self.opened_url = url
        assert wait_until == "domcontentloaded"
        assert timeout == 1000

    def set_viewport_size(self, viewport_size: dict[str, int]) -> None:
        self.viewport_size = viewport_size

    def wait_for_timeout(self, timeout: float) -> None:
        assert timeout == 1500

    def wait_for_function(
        self,
        expression: str,
        arg: object = None,
        *,
        timeout: float,
    ) -> object:
        self.wait_for_function_calls.append((expression, arg))
        assert timeout == 1000
        return True

    def evaluate(self, expression: str, arg: object = None) -> object:
        self.evaluate_calls.append((expression, arg))
        return True

    def screenshot(self, *, path: str, full_page: bool) -> bytes:
        raise AssertionError("screenshots are off for this helper behavior test")


def _load_review_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "review_promoted_dashboards",
        REVIEW_SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_review_plan_covers_promoted_routes_and_viewports(tmp_path: Path) -> None:
    review = _load_review_script()

    runs = review.build_review_plan(
        "http://example.test:8000/base",
        tmp_path,
        screenshots=True,
    )

    assert {run.route for run in runs} == set(review.PROMOTED_DASHBOARD_ROUTES)
    assert [(run.viewport.name, run.viewport.width) for run in runs[:2]] == [
        ("desktop", 1440),
        ("narrow", 390),
    ]
    assert len(runs) == len(review.PROMOTED_DASHBOARD_ROUTES) * 2
    assert all(run.url.startswith("http://example.test:8000/") for run in runs)
    assert all(run.screenshot_path is not None for run in runs)
    assert all(str(run.screenshot_path).startswith(str(tmp_path)) for run in runs)


def test_review_plan_rejects_routes_outside_promoted_set(tmp_path: Path) -> None:
    review = _load_review_script()

    try:
        review.build_review_plan(
            "http://example.test:8000",
            tmp_path,
            routes=("/marimo/unreviewed_dashboard/",),
        )
    except ValueError as error:
        assert "unsupported promoted dashboard route" in str(error)
    else:
        raise AssertionError("expected unsupported route to fail")


def test_default_artifact_directory_is_outside_repo() -> None:
    review = _load_review_script()

    artifact_dir = review.default_artifact_dir()

    assert artifact_dir.is_absolute()
    assert not artifact_dir.is_relative_to(Path.cwd())
    assert str(artifact_dir).startswith("/tmp/")


def test_print_plan_cli_outputs_json_without_playwright_dependency() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(REVIEW_SCRIPT),
            "--base-url",
            "http://example.test:8000",
            "--print-plan",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)

    assert payload["dashboards"] == sorted(
        [
            "/marimo/aws_bounded_read_diagnostics/",
            "/marimo/concept_to_asset_explorer/",
            "/marimo/dagster_asset_catalogue_status/",
            "/marimo/data_readiness_overview/",
            "/marimo/facility_explainer/",
            "/marimo/gas_bid_offer_stack/",
            "/marimo/gas_day_explainer/",
            "/marimo/gas_market_prices/",
            "/marimo/glossary_explorer/",
            "/marimo/hub_zone_explainer/",
            "/marimo/participant_explainer/",
            "/marimo/s3_bucket_health/",
            "/marimo/source_coverage_matrix/",
            "/marimo/system_notices/",
            "/marimo/table_explorer/",
        ]
    )
    assert payload["viewports"] == [
        {"name": "desktop", "width": 1440, "height": 1100},
        {"name": "narrow", "width": 390, "height": 900},
    ]
    assert len(payload["runs"]) == 30
    assert all(run["screenshot_path"] is None for run in payload["runs"])


def test_issue_256_batch_declares_browser_review_surface(tmp_path: Path) -> None:
    review = _load_review_script()

    runs = review.build_review_plan(
        "http://example.test:8000",
        tmp_path,
        routes=review.PROMOTED_DASHBOARD_ROUTES_256,
    )
    route_payloads = {
        run["route"]: run
        for run in review.review_plan_payload(runs)["runs"]
        if run["viewport"] == "desktop"
    }

    assert set(route_payloads) == set(review.PROMOTED_DASHBOARD_ROUTES_256)
    bounded_read_payload = route_payloads["/marimo/aws_bounded_read_diagnostics/"]

    assert bounded_read_payload["control_probes"] == []
    assert "Participant Context" in bounded_read_payload["required_texts"]
    assert "Connection Point Context" in bounded_read_payload["required_texts"]
    assert "Hub / Zone Context" in bounded_read_payload["required_texts"]
    assert route_payloads["/marimo/s3_bucket_health/"]["control_probes"] == [
        {
            "description": "refresh storage health run button",
            "text": "Refresh storage health",
            "optional": False,
        },
        {"description": "bucket filter", "text": "Bucket", "optional": False},
        {
            "description": "table-format filter",
            "text": "Table format",
            "optional": False,
        },
        {
            "description": "prefix-search filter",
            "text": "Prefix search",
            "optional": False,
        },
    ]
    assert {
        probe["description"]
        for probe in route_payloads["/marimo/table_explorer/"]["control_probes"]
    } == {
        "asset-group filter",
        "layer-domain filter",
        "live-status filter",
        "asset-search filter",
        "table dropdown",
        "refresh table scan run button",
        "row-limit input",
        "columns filter",
    }


def test_review_run_checks_shadow_dom_text_and_controls() -> None:
    review = _load_review_script()
    page = _FakeBrowserPage()
    run = review.DashboardReviewRun(
        route="/marimo/data_readiness_overview/",
        url="http://example.test/marimo/data_readiness_overview/",
        viewport=review.ViewportSpec(name="desktop", width=1440, height=1100),
        required_texts=("Dashboard brief",),
        control_probes=(
            review.ControlProbe(
                description="refresh readiness button",
                text="Refresh readiness",
            ),
        ),
        screenshot_path=None,
    )

    evidence = review._review_one_run(page, run, timeout_ms=1000)

    assert page.opened_url == "http://example.test/marimo/data_readiness_overview/"
    assert page.viewport_size == {"width": 1440, "height": 1100}
    wait_expression, wait_arg = page.wait_for_function_calls[0]
    assert "shadowRoot" in wait_expression
    assert wait_arg == {"text": "Dashboard brief", "exact": False}
    assert all("shadowRoot" in call[0] for call in page.evaluate_calls)
    assert [call[1] for call in page.evaluate_calls] == [
        {"text": "Refresh readiness", "exact": True},
        {"text": "Refresh readiness", "exact": True},
    ]
    assert evidence == [
        (
            "opened /marimo/data_readiness_overview/ at desktop "
            "(http://example.test/marimo/data_readiness_overview/)"
        ),
        "verified required text: Dashboard brief",
        "exercised controls: refresh readiness button",
    ]
