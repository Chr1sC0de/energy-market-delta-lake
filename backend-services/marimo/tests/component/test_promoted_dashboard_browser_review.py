"""Component coverage for the promoted dashboard browser-review helper."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

REVIEW_SCRIPT = Path(__file__).parents[2] / "scripts" / "review_promoted_dashboards.py"

SAMPLE_ENERGY_MARKET_REQUIRED_TEXTS = (
    "Local Gas Market Overview",
    "Dashboard brief",
    "Dashboard intent",
    "Gas Model Outputs",
    "Prices",
    "Source Coverage",
)


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
        if (
            isinstance(arg, dict)
            and arg.get("text") == "Traceback (most recent call last)"
        ):
            return False
        return True

    def screenshot(self, *, path: str, full_page: bool) -> bytes:
        raise AssertionError("screenshots are off for this helper behavior test")


class _VisibleTextPage:
    def __init__(self, text: str) -> None:
        self.text = text

    def evaluate(self, expression: str, arg: object = None) -> object:
        assert "shadowRoot" in expression
        assert isinstance(arg, dict)
        target = str(arg["text"]).lower()
        return target in self.text.lower()


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
    assert all(run.video_path is None for run in runs)


def test_review_plan_can_plan_webm_videos_for_registry_route(tmp_path: Path) -> None:
    review = _load_review_script()

    runs = review.build_review_plan(
        "http://example.test:8000",
        tmp_path,
        videos=True,
        routes=("/marimo/sample_energy_market/",),
    )

    assert [(run.viewport.name, run.required_texts) for run in runs] == [
        ("desktop", SAMPLE_ENERGY_MARKET_REQUIRED_TEXTS),
        ("narrow", SAMPLE_ENERGY_MARKET_REQUIRED_TEXTS),
    ]
    assert [run.video_path for run in runs] == [
        tmp_path / "marimo__sample_energy_market__desktop.webm",
        tmp_path / "marimo__sample_energy_market__narrow.webm",
    ]


def test_review_plan_rejects_routes_outside_promoted_set(tmp_path: Path) -> None:
    review = _load_review_script()

    try:
        review.build_review_plan(
            "http://example.test:8000",
            tmp_path,
            routes=("/marimo/unreviewed_dashboard/",),
        )
    except ValueError as error:
        assert "unsupported configured or registry-backed dashboard route" in str(error)
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
            "/marimo/capacity_outlook/",
            "/marimo/capacity_auction/",
            "/marimo/capacity_transactions/",
            "/marimo/citation_chain_explorer/",
            "/marimo/concept_to_asset_explorer/",
            "/marimo/connection_point_explainer/",
            "/marimo/dagster_asset_catalogue_status/",
            "/marimo/data_readiness_overview/",
            "/marimo/facility_flow_storage/",
            "/marimo/facility_explainer/",
            "/marimo/forecast_vs_actual/",
            "/marimo/flow_operations/",
            "/marimo/gas_bid_offer_stack/",
            "/marimo/gas_day_explainer/",
            "/marimo/gas_market_prices/",
            "/marimo/gas_scheduled_quantities/",
            "/marimo/gas_sttm_capacity_settlement/",
            "/marimo/gas_sttm_contingency_gas/",
            "/marimo/gas_sttm_market_settlement/",
            "/marimo/gas_sttm_mos_allocation/",
            "/marimo/glossary_explorer/",
            "/marimo/heating_value_pressure/",
            "/marimo/hub_zone_explainer/",
            "/marimo/linepack_adequacy/",
            "/marimo/materialization_freshness/",
            "/marimo/nomination_demand_forecast/",
            "/marimo/operational_meter_flow/",
            "/marimo/participant_explainer/",
            "/marimo/pipeline_connection_operations/",
            "/marimo/s3_bucket_health/",
            "/marimo/schema_data_dictionary_explorer/",
            "/marimo/source_coverage_matrix/",
            "/marimo/source_table_lineage_explorer/",
            "/marimo/system_notices/",
            "/marimo/table_explorer/",
        ]
    )
    assert payload["viewports"] == [
        {"name": "desktop", "width": 1440, "height": 1100},
        {"name": "narrow", "width": 390, "height": 900},
    ]
    assert len(payload["runs"]) == 72
    assert all(run["screenshot_path"] is None for run in payload["runs"])
    assert all(run["video_path"] is None for run in payload["runs"])


def test_issue_341_routes_declare_browser_review_surface(tmp_path: Path) -> None:
    review = _load_review_script()

    runs = review.build_review_plan(
        "http://example.test:8000",
        tmp_path,
        routes=(
            "/marimo/source_coverage_matrix/",
            "/marimo/source_table_lineage_explorer/",
            "/marimo/sample_energy_market/",
        ),
    )
    route_payloads = {
        run["route"]: run
        for run in review.review_plan_payload(runs)["runs"]
        if run["viewport"] == "desktop"
    }

    assert (
        "Coverage Health"
        in route_payloads["/marimo/source_coverage_matrix/"]["required_texts"]
    )
    assert (
        "Lineage Health"
        in route_payloads["/marimo/source_table_lineage_explorer/"]["required_texts"]
    )
    sample_payload = route_payloads["/marimo/sample_energy_market/"]
    assert sample_payload["required_texts"] == list(SAMPLE_ENERGY_MARKET_REQUIRED_TEXTS)
    assert sample_payload["control_probes"] == []


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


def test_issue_258_batch_declares_browser_review_surface(tmp_path: Path) -> None:
    review = _load_review_script()

    runs = review.build_review_plan(
        "http://example.test:8000",
        tmp_path,
        routes=review.PROMOTED_DASHBOARD_ROUTES_258,
    )
    route_payloads = {
        run["route"]: run
        for run in review.review_plan_payload(runs)["runs"]
        if run["viewport"] == "desktop"
    }

    assert set(route_payloads) == set(review.PROMOTED_DASHBOARD_ROUTES_258)
    materialization_payload = route_payloads["/marimo/materialization_freshness/"]
    assert "Asset Freshness Detail" in materialization_payload["required_texts"]
    assert {
        probe["description"] for probe in materialization_payload["control_probes"]
    } == {
        "refresh freshness run button",
        "asset-group filter",
        "layer/domain filter",
        "freshness-state filter",
        "minimum-gap-hours slider",
        "asset-search filter",
    }

    citation_payload = route_payloads["/marimo/citation_chain_explorer/"]
    assert citation_payload["control_probes"] == []
    assert "Source hashes" in citation_payload["required_texts"]

    assert {
        probe["description"]
        for probe in route_payloads["/marimo/capacity_outlook/"]["control_probes"]
    } == {
        "refresh data run button",
        "capacity-source-coverage dropdown",
        "date-range dropdown",
        "capacity-type dropdown",
        "direction dropdown",
        "source-facility dropdown",
        "source-system dropdown",
    }

    assert {
        probe["description"]
        for probe in route_payloads["/marimo/source_table_lineage_explorer/"][
            "control_probes"
        ]
    } == {
        "refresh data run button",
        "curated-asset filter",
        "source-system filter",
        "lineage-state filter",
        "lineage-search filter",
    }
    assert (
        "Data Health"
        in route_payloads["/marimo/source_table_lineage_explorer/"]["required_texts"]
    )


def test_c47c461_batch_declares_browser_review_surface(tmp_path: Path) -> None:
    review = _load_review_script()

    runs = review.build_review_plan(
        "http://example.test:8000",
        tmp_path,
        routes=review.PROMOTED_DASHBOARD_ROUTES_C47C461,
    )
    route_payloads = {
        run["route"]: run
        for run in review.review_plan_payload(runs)["runs"]
        if run["viewport"] == "desktop"
    }

    assert set(route_payloads) == set(review.PROMOTED_DASHBOARD_ROUTES_C47C461)

    forecast_payload = route_payloads["/marimo/forecast_vs_actual/"]
    assert "Data Health" in forecast_payload["required_texts"]
    assert "Forecast-vs-actual read diagnostics" in forecast_payload["required_texts"]
    assert {probe["description"] for probe in forecast_payload["control_probes"]} == {
        "refresh data run button",
        "gas-day dropdown",
        "source-facility dropdown",
        "source-system dropdown",
    }

    pipeline_payload = route_payloads["/marimo/pipeline_connection_operations/"]
    assert pipeline_payload["control_probes"] == [
        {
            "description": "refresh data run button",
            "text": "Refresh data",
            "optional": False,
        }
    ]
    assert "Relationship Gaps" in pipeline_payload["required_texts"]

    heating_payload = route_payloads["/marimo/heating_value_pressure/"]
    assert (
        "Heating value and pressure read diagnostics"
        in heating_payload["required_texts"]
    )
    assert {probe["description"] for probe in heating_payload["control_probes"]} == {
        "refresh data run button",
        "source-system dropdown",
        "source-table dropdown",
        "source-qualified-identifier dropdown",
    }

    operational_payload = route_payloads["/marimo/operational_meter_flow/"]
    assert "Data Health" in operational_payload["required_texts"]
    assert "Relationship Coverage Gaps" in operational_payload["required_texts"]

    capacity_auction_payload = route_payloads["/marimo/capacity_auction/"]
    assert {
        probe["description"] for probe in capacity_auction_payload["control_probes"]
    } == {
        "refresh data run button",
        "auction-date dropdown",
        "zone dropdown",
        "capacity-period dropdown",
        "auction-metric dropdown",
        "source-system dropdown",
    }

    scheduled_quantity_payload = route_payloads["/marimo/gas_scheduled_quantities/"]
    assert (
        "Scheduled quantity read diagnostics"
        in scheduled_quantity_payload["required_texts"]
    )
    assert {
        probe["description"] for probe in scheduled_quantity_payload["control_probes"]
    } == {
        "refresh data run button",
        "gas-day dropdown",
        "source-system dropdown",
        "schedule-type dropdown",
    }

    contingency_payload = route_payloads["/marimo/gas_sttm_contingency_gas/"]
    assert "Source Identifier Coverage" in contingency_payload["required_texts"]
    assert {
        probe["description"] for probe in contingency_payload["control_probes"]
    } == {
        "refresh data run button",
        "contingency-grain dropdown",
        "quantity-type dropdown",
        "hub dropdown",
        "source-system dropdown",
    }

    market_settlement_payload = route_payloads["/marimo/gas_sttm_market_settlement/"]
    assert {
        probe["description"] for probe in market_settlement_payload["control_probes"]
    } == {
        "refresh data run button",
        "gas-day dropdown",
        "settlement-period dropdown",
        "settlement-stage dropdown",
        "settlement-component dropdown",
    }

    capacity_settlement_payload = route_payloads[
        "/marimo/gas_sttm_capacity_settlement/"
    ]
    assert {
        probe["description"] for probe in capacity_settlement_payload["control_probes"]
    } == {
        "refresh data run button",
        "gas-day dropdown",
        "settlement-stage dropdown",
        "capacity-settlement-component dropdown",
        "hub dropdown",
        "facility dropdown",
    }


def test_promotion_2ddac3f_batch_declares_browser_review_surface(
    tmp_path: Path,
) -> None:
    review = _load_review_script()

    runs = review.build_review_plan(
        "http://example.test:8000",
        tmp_path,
        routes=review.PROMOTED_DASHBOARD_ROUTES_2DDAC3F,
    )
    route_payloads = {
        run["route"]: run
        for run in review.review_plan_payload(runs)["runs"]
        if run["viewport"] == "desktop"
    }

    assert set(route_payloads) == set(review.PROMOTED_DASHBOARD_ROUTES_2DDAC3F)
    capacity_transactions_payload = route_payloads["/marimo/capacity_transactions/"]

    assert (
        "Capacity transaction read diagnostics"
        in (capacity_transactions_payload["required_texts"])
    )
    assert (
        "Recent Loaded Capacity Transaction Preview"
        in (capacity_transactions_payload["required_texts"])
    )
    assert {
        probe["description"]
        for probe in capacity_transactions_payload["control_probes"]
    } == {
        "refresh data run button",
        "transaction-type dropdown",
        "transaction-date dropdown",
        "source-location dropdown",
        "source-facility dropdown",
        "source-system dropdown",
    }


def test_promotion_9d437f_batch_declares_browser_review_surface(
    tmp_path: Path,
) -> None:
    review = _load_review_script()

    runs = review.build_review_plan(
        "http://example.test:8000",
        tmp_path,
        routes=review.PROMOTED_DASHBOARD_ROUTES_9D437F,
    )
    route_payloads = {
        run["route"]: run
        for run in review.review_plan_payload(runs)["runs"]
        if run["viewport"] == "desktop"
    }

    assert set(route_payloads) == set(review.PROMOTED_DASHBOARD_ROUTES_9D437F)
    sttm_mos_allocation_payload = route_payloads["/marimo/gas_sttm_mos_allocation/"]

    assert (
        "STTM MOS/allocation read diagnostics"
        in sttm_mos_allocation_payload["required_texts"]
    )
    assert (
        "STTM MOS And Allocation Summary"
        in sttm_mos_allocation_payload["required_texts"]
    )
    assert "Source Coverage" in sttm_mos_allocation_payload["required_texts"]
    assert {
        probe["description"] for probe in sttm_mos_allocation_payload["control_probes"]
    } == {
        "refresh data run button",
        "gas-day dropdown",
        "source-system dropdown",
        "hub/zone dropdown",
        "facility dropdown",
    }


def test_existing_promoted_dashboard_coverage_is_preserved() -> None:
    review = _load_review_script()

    assert "/marimo/gas_market_prices/" in review.PROMOTED_DASHBOARD_ROUTES
    assert "/marimo/gas_bid_offer_stack/" in review.PROMOTED_DASHBOARD_ROUTES
    assert "/marimo/capacity_transactions/" in review.PROMOTED_DASHBOARD_ROUTES
    assert "/marimo/gas_sttm_mos_allocation/" in review.PROMOTED_DASHBOARD_ROUTES


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
        {"text": "Traceback (most recent call last)", "exact": False},
        {"text": "Refresh readiness", "exact": True},
        {"text": "Refresh readiness", "exact": True},
    ]
    assert evidence == [
        (
            "opened /marimo/data_readiness_overview/ at desktop "
            "(http://example.test/marimo/data_readiness_overview/)"
        ),
        "verified required text: Dashboard brief",
        "verified absent text: Traceback header",
        "exercised controls: refresh readiness button",
    ]


def test_absent_traceback_check_allows_normal_tracebacks_copy() -> None:
    review = _load_review_script()
    page = _VisibleTextPage(
        "This dashboard renders empty states instead of tracebacks."
    )

    review._require_absent_visible_text(page, "Traceback (most recent call last)")


def test_absent_traceback_check_fails_python_traceback_header() -> None:
    review = _load_review_script()
    page = _VisibleTextPage("Traceback (most recent call last):")

    try:
        review._require_absent_visible_text(page, "Traceback (most recent call last)")
    except RuntimeError as error:
        assert "unexpected dashboard text was visible" in str(error)
    else:
        raise AssertionError("expected traceback header to fail browser review")
