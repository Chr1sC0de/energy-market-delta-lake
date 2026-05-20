"""Smoke tests for curated Marimo dashboard discoverability and rendering."""

from collections.abc import Mapping

import polars as pl
import pytest

from marimoserver.dashboard_registry import DashboardStatus
from marimoserver.data_readiness import (
    ReadinessState,
    build_data_readiness_overview,
    readiness_action_markdown,
)
from marimoserver.gas_dashboard import (
    BID_STACK_TABLE_SPEC,
    CUSTOMER_TRANSFER_TABLE_SPEC,
    FACILITY_FLOW_STORAGE_TABLE_SPEC,
    GAS_QUALITY_TABLE_SPEC,
    MARKET_PRICE_TABLE_SPEC,
    SCHEDULE_RUN_TABLE_SPEC,
    SETTLEMENT_ACTIVITY_TABLE_SPEC,
    GasTableSpec,
    SYSTEM_NOTICE_TABLE_SPEC,
    bid_stack_empty_state_markdown,
    customer_transfer_empty_state_markdown,
    discover_dashboard_config,
    facility_flow_storage_empty_state_markdown,
    gas_quality_empty_state_markdown,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    load_bid_stack_table,
    load_customer_transfer_table,
    load_facility_flow_storage_table,
    load_gas_quality_table,
    load_gas_model_tables,
    load_market_price_table,
    load_schedule_run_table,
    load_settlement_activity_table,
    load_system_notice_table,
    market_price_empty_state_markdown,
    render_dashboard_context_panel,
    schedule_run_empty_state_markdown,
    settlement_activity_empty_state_markdown,
    system_notice_empty_state_markdown,
)
from marimoserver.gbb_interactive_map import (
    GbbMapTableSpec,
    load_gbb_map_tables,
    map_load_status_frame,
)
from marimoserver.glossary_explorer import (
    build_glossary_explorer,
    render_glossary_explorer_html,
)
from marimoserver import table_explorer
from marimoserver.table_explorer import (
    TableFormat,
    TablePrefix,
    TableQuery,
    BucketStatus,
    StorageDiscovery,
    discover_table_explorer_config,
    explore_table_scan,
)
from marimoserver.dagster_graphql import DagsterAssetCatalogue
from tests.component.dashboard_smoke_harness import (
    CURATED_NOTEBOOKS_DIR,
    DashboardSmokeTarget,
    assert_html_response,
    available_dashboard_entries,
    curated_notebook_names,
    dashboard_smoke_targets,
    get_fastapi_route,
)


def _target_id(target: DashboardSmokeTarget) -> str:
    return target.concept_id


DASHBOARD_SMOKE_TARGETS = dashboard_smoke_targets()


def test_available_registry_dashboards_are_discoverable_from_notebooks_dir() -> None:
    notebook_names = set(curated_notebook_names())
    missing_notebooks = [
        entry.notebook_name
        for entry in available_dashboard_entries()
        if entry.notebook_name not in notebook_names
    ]

    assert CURATED_NOTEBOOKS_DIR.is_dir()
    assert missing_notebooks == []
    assert {target.notebook_name for target in DASHBOARD_SMOKE_TARGETS} == {
        entry.notebook_name for entry in available_dashboard_entries()
    }


@pytest.mark.parametrize(
    "target",
    DASHBOARD_SMOKE_TARGETS,
    ids=_target_id,
)
def test_available_dashboard_routes_return_html(target: DashboardSmokeTarget) -> None:
    response = get_fastapi_route(target.route)

    assert target.notebook_path.is_file()
    assert_html_response(response, target.route)


@pytest.mark.parametrize(
    "target",
    DASHBOARD_SMOKE_TARGETS,
    ids=_target_id,
)
def test_available_dashboard_context_panels_render_stable_html(
    target: DashboardSmokeTarget,
) -> None:
    html = render_dashboard_context_panel(target.concept_id)

    assert 'class="dashboard-context-panel"' in html
    assert f'data-concept-id="{target.concept_id}"' in html
    assert f'data-status="{DashboardStatus.AVAILABLE.value}"' in html
    assert f'data-notebook-name="{target.notebook_name}"' in html
    assert f'data-notebook-route="{target.route}"' in html
    assert "backing assets" in html


def test_glossary_explorer_smoke_renders_planned_dashboard_states() -> None:
    html = render_glossary_explorer_html(build_glossary_explorer())

    assert 'data-concept-count="13"' in html
    assert 'data-dashboard-status="planned"' in html
    assert "Planned dashboard" in html
    assert "No source chunk IDs recorded in the Marimo registry." not in html


def test_gas_market_dashboard_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "3",
        }
    )
    specs = (
        GasTableSpec(
            section="Prices",
            label="Market prices",
            table_name="silver_gas_fact_market_price",
        ),
    )
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    loads = load_gas_model_tables(config, specs=specs, reader=reader)
    message = gas_table_load_status_message(loads)
    status = gas_table_load_status_frame(loads)

    assert captured_row_limits == [3]
    assert "Bounded preview reads are capped at `3` rows per table" in message
    assert status.row(0, named=True)["status"] == "Empty"
    assert status.row(0, named=True)["row limit"] == "Bounded preview: 3 rows max"


def test_market_prices_dashboard_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "7",
        }
    )
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    load = load_market_price_table(config, reader=reader)
    empty_markdown = market_price_empty_state_markdown(load)

    assert captured_row_limits == [7]
    assert load.spec == MARKET_PRICE_TABLE_SPEC
    assert not load.available
    assert "No market price data is available" in empty_markdown
    assert "Bounded preview reads are capped at `7` rows per table" in empty_markdown


def test_schedule_runs_dashboard_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "8",
        }
    )
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    load = load_schedule_run_table(config, reader=reader)
    empty_markdown = schedule_run_empty_state_markdown(load)

    assert captured_row_limits == [8]
    assert load.spec == SCHEDULE_RUN_TABLE_SPEC
    assert not load.available
    assert "No schedule run data is available" in empty_markdown
    assert "Bounded preview reads are capped at `8` rows per table" in empty_markdown


def test_settlement_activity_dashboard_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "10",
        }
    )
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    load = load_settlement_activity_table(config, reader=reader)
    empty_markdown = settlement_activity_empty_state_markdown(load)

    assert captured_row_limits == [10]
    assert load.spec == SETTLEMENT_ACTIVITY_TABLE_SPEC
    assert not load.available
    assert "No settlement activity data is available" in empty_markdown
    assert "Bounded preview reads are capped at `10` rows per table" in empty_markdown


def test_customer_transfer_dashboard_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "12",
        }
    )
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    load = load_customer_transfer_table(config, reader=reader)
    empty_markdown = customer_transfer_empty_state_markdown(load)

    assert captured_row_limits == [12]
    assert load.spec == CUSTOMER_TRANSFER_TABLE_SPEC
    assert not load.available
    assert "No customer transfer data is available" in empty_markdown
    assert "Bounded preview reads are capped at `12` rows per table" in empty_markdown


def test_facility_flow_storage_dashboard_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "12",
        }
    )
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    load = load_facility_flow_storage_table(config, reader=reader)
    empty_markdown = facility_flow_storage_empty_state_markdown(load)

    assert captured_row_limits == [12]
    assert load.spec == FACILITY_FLOW_STORAGE_TABLE_SPEC
    assert not load.available
    assert "No facility flow or storage data is available" in empty_markdown
    assert "Bounded preview reads are capped at `12` rows per table" in empty_markdown


def test_bid_stack_dashboard_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "9",
        }
    )
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    load = load_bid_stack_table(config, reader=reader)
    empty_markdown = bid_stack_empty_state_markdown(load)

    assert captured_row_limits == [9]
    assert load.spec == BID_STACK_TABLE_SPEC
    assert not load.available
    assert "No Bid / Offer stack data is available" in empty_markdown
    assert "Bounded preview reads are capped at `9` rows per table" in empty_markdown


def test_system_notices_dashboard_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "5",
        }
    )
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    load = load_system_notice_table(config, reader=reader)
    empty_markdown = system_notice_empty_state_markdown(load)

    assert captured_row_limits == [5]
    assert load.spec == SYSTEM_NOTICE_TABLE_SPEC
    assert not load.available
    assert "No system notice data is available for this view" in empty_markdown
    assert "Bounded preview reads are capped at `5` rows per table" in empty_markdown


def test_gas_quality_dashboard_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "6",
        }
    )
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    load = load_gas_quality_table(config, reader=reader)
    empty_markdown = gas_quality_empty_state_markdown(load)

    assert captured_row_limits == [6]
    assert load.spec == GAS_QUALITY_TABLE_SPEC
    assert not load.available
    assert "No gas quality or composition data is available" in empty_markdown
    assert "Bounded preview reads are capped at `6` rows per table" in empty_markdown


def test_gbb_map_bounded_loader_renders_empty_state() -> None:
    config = discover_dashboard_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "AEMO_BUCKET": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "2",
        }
    )
    specs = (GbbMapTableSpec("silver_gas_dim_facility", "Facilities"),)
    captured_row_limits: list[int | None] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    loads = load_gbb_map_tables(config, specs=specs, reader=reader)
    status = map_load_status_frame(loads)

    assert captured_row_limits == [2]
    assert not loads[0].available
    assert status.row(0, named=True)["status"] == "Empty or missing"


def test_table_explorer_bounded_loader_renders_empty_scan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = discover_table_explorer_config(
        {
            "DEVELOPMENT_LOCATION": "aws",
            "MARIMO_TABLE_BUCKETS": "prod-energy-market-aemo",
            "MARIMO_MAX_PREVIEW_ROWS": "4",
        }
    )
    table = TablePrefix(
        bucket="prod-energy-market-aemo",
        prefix="silver/gas_model/silver_gas_fact_market_price",
        table_format=TableFormat.DELTA,
        parquet_files=(),
    )
    captured_row_limits: list[int | None] = []

    def fake_read_delta_table(
        table_arg: TablePrefix,
        config_arg: table_explorer.TableExplorerConfig,
        row_limit: int | None = None,
    ) -> pl.DataFrame:
        assert table_arg == table
        assert config_arg == config
        captured_row_limits.append(row_limit)
        return pl.DataFrame()

    monkeypatch.setattr(table_explorer, "read_delta_table", fake_read_delta_table)

    scan = table_explorer.load_table_dataframe(table, config)
    exploration = explore_table_scan(scan, TableQuery())

    assert captured_row_limits == [4]
    assert scan.available
    assert scan.is_limited
    assert scan.row_limit == 4
    assert exploration.available
    assert exploration.preview.is_empty()
    assert exploration.row_count == 0


def test_data_readiness_dashboard_renders_actionable_empty_states() -> None:
    config = discover_table_explorer_config({})
    discovery = StorageDiscovery(
        buckets=(
            BucketStatus(
                name="dev-energy-market-aemo",
                is_default=True,
                discovered=False,
                reachable=True,
                object_count=0,
                table_count=0,
                truncated=False,
                error=None,
            ),
        ),
        tables=(),
        bucket_listing_error=None,
    )
    catalogue = DagsterAssetCatalogue(
        url="http://dagster/graphql",
        assets=(),
        error="connection refused",
    )

    overview = build_data_readiness_overview(config, discovery, catalogue, ())
    action_markdown = readiness_action_markdown(overview)

    assert overview.cards[0].state is ReadinessState.EMPTY
    assert overview.cards[1].state is ReadinessState.EMPTY
    assert overview.cards[2].state is ReadinessState.UNAVAILABLE
    assert "Seed LocalStack or materialize" in action_markdown
    assert "DAGSTER_GRAPHQL_URL" in action_markdown
