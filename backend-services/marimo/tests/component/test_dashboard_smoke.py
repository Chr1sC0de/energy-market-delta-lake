"""Smoke tests for curated Marimo dashboard discoverability and rendering."""

from collections.abc import Mapping

import polars as pl
import pytest

from marimoserver.dashboard_registry import DashboardStatus
from marimoserver.gas_dashboard import (
    GasTableSpec,
    discover_dashboard_config,
    gas_table_load_status_frame,
    gas_table_load_status_message,
    load_gas_model_tables,
    render_dashboard_context_panel,
)
from marimoserver.gbb_interactive_map import (
    GbbMapTableSpec,
    load_gbb_map_tables,
    map_load_status_frame,
)
from marimoserver import table_explorer
from marimoserver.table_explorer import (
    TableFormat,
    TablePrefix,
    TableQuery,
    discover_table_explorer_config,
    explore_table_scan,
)
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
