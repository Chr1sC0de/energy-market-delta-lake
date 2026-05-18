"""Component tests for the GBB interactive map helper surface."""

from collections.abc import Mapping
from datetime import date, datetime, timezone
from pathlib import Path
import socket

import polars as pl
import pytest

from marimoserver.gas_dashboard import discover_dashboard_config
from marimoserver import gbb_interactive_map as map_helpers
from marimoserver.gbb_interactive_map import (
    FLOW_SOURCE_ACTUAL,
    FLOW_SOURCE_FORECAST,
    GBB_MAP_TABLES,
    MAP_PIPELINES,
    MAP_POINTS,
    MAP_REGIONS,
    GbbMapModel,
    GbbMapTableLoad,
    GbbMapTableSpec,
    FacilityMapRecord,
    PipelineMapRecord,
    build_gbb_map_model,
    check_gbb_map_s3_endpoint,
    load_gbb_map_tables,
    normalize_gas_date,
    map_load_status_frame,
    pipeline_records_frame,
    render_gbb_map_html,
)


def test_gbb_map_specs_cover_required_inputs() -> None:
    table_names = {spec.table_name for spec in GBB_MAP_TABLES}

    assert "silver_gas_dim_facility" in table_names
    assert "silver_gas_dim_location" in table_names
    assert "silver_gas_dim_connection_point" in table_names
    assert "silver_gas_fact_facility_flow_storage" in table_names
    assert "silver_gas_fact_nomination_forecast" in table_names
    assert "silver_gas_fact_capacity_outlook" in table_names
    assert all(spec.route_coordinates for spec in MAP_PIPELINES)
    assert all(spec.coordinate for spec in MAP_POINTS)
    assert {"Queensland", "New South Wales", "Victoria"} <= {
        region.label for region in MAP_REGIONS
    }


def test_normalize_gas_date_handles_marimo_date_values() -> None:
    fallback = date(2024, 1, 3)

    assert normalize_gas_date(None, today=fallback) == fallback
    assert normalize_gas_date(fallback, today=date(2024, 1, 1)) == fallback
    assert normalize_gas_date("2024-01-04", today=fallback) == date(2024, 1, 4)
    assert normalize_gas_date("", today=fallback) == fallback
    assert normalize_gas_date(
        datetime(2024, 1, 5, 12, 30),
        today=fallback,
    ) == date(2024, 1, 5)


def test_load_gbb_map_tables_passes_configured_uri_and_storage() -> None:
    captured: list[tuple[str, dict[str, str], int | None]] = []
    config = discover_dashboard_config({})
    specs = [GbbMapTableSpec("silver_gas_dim_facility", "Facilities")]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        captured.append((uri, dict(storage_options), row_limit))
        return pl.DataFrame({"source_system": ["GBB"]})

    loads = load_gbb_map_tables(config, specs=specs, reader=reader)

    assert len(loads) == 1
    assert loads[0].available
    assert captured == [
        (
            "s3://dev-energy-market-aemo/silver/gas_model/silver_gas_dim_facility",
            config.storage_options(),
            None,
        )
    ]


def test_load_gbb_map_tables_returns_error_status_detail() -> None:
    config = discover_dashboard_config({})
    specs = [GbbMapTableSpec("silver_gas_dim_facility", "Facilities")]

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        raise RuntimeError("missing delta log\ntraceback")

    loads = load_gbb_map_tables(config, specs=specs, reader=reader)
    status = map_load_status_frame(loads)

    assert not loads[0].available
    assert loads[0].error == "RuntimeError: missing delta log"
    assert status.row(0, named=True)["status"] == "Empty or missing"
    assert "missing delta log" in status.row(0, named=True)["detail"]


def test_load_gbb_map_tables_can_short_circuit_unreachable_local_s3() -> None:
    config = discover_dashboard_config({})
    specs = [GbbMapTableSpec("silver_gas_dim_facility", "Facilities")]
    calls = 0

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None,
    ) -> pl.DataFrame:
        nonlocal calls
        calls += 1
        return pl.DataFrame({"source_system": ["GBB"]})

    loads = load_gbb_map_tables(
        config,
        specs=specs,
        reader=reader,
        endpoint_checker=lambda storage_options: "S3 endpoint unavailable",
    )

    assert calls == 0
    assert loads[0].error == "S3 endpoint unavailable"


def test_read_gbb_map_table_delegates_to_parquet_reader(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[tuple[str, dict[str, str], int | None]] = []

    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None = None,
    ) -> pl.DataFrame:
        captured.append((uri, dict(storage_options), row_limit))
        return pl.DataFrame({"source_system": ["GBB"]})

    monkeypatch.setattr(map_helpers, "read_parquet_table", reader)

    frame = map_helpers.read_gbb_map_table(
        "s3://bucket/silver/gas_model/table",
        {"AWS_REGION": "ap-southeast-2"},
        row_limit=7,
    )

    assert frame.to_dict(as_series=False) == {"source_system": ["GBB"]}
    assert captured == [
        (
            "s3://bucket/silver/gas_model/table",
            {"AWS_REGION": "ap-southeast-2"},
            7,
        )
    ]


def test_read_gbb_map_table_reads_local_parquet_prefix(
    tmp_path: Path,
) -> None:
    table_dir = tmp_path / "silver_gas_dim_facility"
    table_dir.mkdir()
    pl.DataFrame({"source_facility_id": ["10"]}).write_parquet(
        table_dir / "part-00000.parquet"
    )

    frame = map_helpers.read_gbb_map_table(str(table_dir), {})

    assert frame.to_dict(as_series=False) == {"source_facility_id": ["10"]}


def test_read_gbb_map_table_reports_parquet_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def reader(
        uri: str,
        storage_options: Mapping[str, str],
        row_limit: int | None = None,
    ) -> pl.DataFrame:
        raise FileNotFoundError("no parquet files found")

    monkeypatch.setattr(map_helpers, "read_parquet_table", reader)

    with pytest.raises(FileNotFoundError) as exc_info:
        map_helpers.read_gbb_map_table("s3://bucket/silver/gas_model/missing", {})

    assert "no parquet files found" in str(exc_info.value)


def test_check_gbb_map_s3_endpoint_handles_local_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeSocket:
        def __enter__(self) -> object:
            return self

        def __exit__(
            self,
            exc_type: object,
            exc: object,
            traceback: object,
        ) -> None:
            return None

    captured: list[tuple[tuple[str, int], float | None]] = []

    def connect(address: tuple[str, int], timeout: float | None = None) -> FakeSocket:
        captured.append((address, timeout))
        return FakeSocket()

    monkeypatch.setattr(socket, "create_connection", connect)

    error = check_gbb_map_s3_endpoint({"AWS_ENDPOINT_URL": "http://localhost:4566"})

    assert error is None
    assert captured == [(("localhost", 4566), 0.35)]

    captured.clear()
    assert check_gbb_map_s3_endpoint({"AWS_ENDPOINT_URL": "http://localhost"}) is None
    assert captured == [(("localhost", 80), 0.35)]


def test_check_gbb_map_s3_endpoint_reports_unreachable_local_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def connect(address: tuple[str, int], timeout: float | None = None) -> None:
        raise OSError("refused")

    monkeypatch.setattr(socket, "create_connection", connect)

    error = check_gbb_map_s3_endpoint({"AWS_ENDPOINT_URL": "http://localstack:4566"})

    assert error == (
        "S3 endpoint unavailable: http://localstack:4566; start LocalStack or set "
        "AWS_ENDPOINT_URL to a reachable endpoint"
    )


def test_check_gbb_map_s3_endpoint_skips_non_local_endpoint() -> None:
    assert check_gbb_map_s3_endpoint({"AWS_ENDPOINT_URL": ""}) is None
    assert (
        check_gbb_map_s3_endpoint({"AWS_ENDPOINT_URL": "https://s3.amazonaws.com"})
        is None
    )


def test_build_gbb_map_model_uses_actuals_for_past_gas_day() -> None:
    loads = _loads(
        actual_flow=pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1)],
                "source_facility_id": ["10"],
                "source_location_id": ["20"],
                "demand_tj": [2.0],
                "supply_tj": [9.0],
                "transfer_in_tj": [1.0],
                "transfer_out_tj": [3.0],
                "held_in_storage_tj": [0.0],
                "source_last_updated_timestamp": [_timestamp()],
                "ingested_timestamp": [_timestamp()],
            }
        ),
        capacity=pl.DataFrame(
            {
                "source_facility_id": ["10"],
                "facility_name": ["Carpentaria Gas Pipeline"],
                "capacity_quantity_tj": [14.0],
                "flow_direction": ["north"],
                "from_gas_date": [date(2024, 1, 1)],
                "to_gas_date": [None],
                "capacity_description": ["CGP north capacity"],
            }
        ),
    )

    model = build_gbb_map_model(
        loads,
        gas_date=date(2024, 1, 1),
        today=date(2024, 1, 2),
    )
    cgp = _pipeline(model, "CGP")

    assert model.data_source == FLOW_SOURCE_ACTUAL
    assert cgp.flow_tj == 5.0
    assert cgp.capacity_tj == 14.0
    assert cgp.utilisation_pct == 35.7
    assert cgp.direction == "north"
    assert cgp.status == "Flow and capacity"


def test_build_gbb_map_model_uses_forecasts_for_today_and_future() -> None:
    loads = _loads(
        forecast=pl.DataFrame(
            {
                "source_system": ["GBB"],
                "gas_date": [date(2024, 1, 2)],
                "source_facility_id": ["30"],
                "source_location_id": ["40"],
                "demand_forecast_gj": [88_000.0],
                "supply_forecast_gj": [0.0],
                "transfer_in_forecast_gj": [0.0],
                "transfer_out_forecast_gj": [0.0],
                "source_last_updated_timestamp": [_timestamp()],
                "ingested_timestamp": [_timestamp()],
            }
        )
    )

    model = build_gbb_map_model(
        loads,
        gas_date=date(2024, 1, 2),
        today=date(2024, 1, 2),
    )
    rbp = _pipeline(model, "RBP")

    assert model.data_source == FLOW_SOURCE_FORECAST
    assert rbp.flow_tj == 88.0
    assert rbp.direction == "east"
    assert rbp.status == "Flow only"


def test_build_gbb_map_model_handles_empty_forecast_source() -> None:
    model = build_gbb_map_model(
        _loads(),
        gas_date=date(2024, 1, 2),
        today=date(2024, 1, 2),
    )

    assert model.data_source == FLOW_SOURCE_FORECAST
    assert all(record.status == "No local data" for record in model.pipelines)


def test_build_gbb_map_model_handles_negative_and_capacity_only_flows() -> None:
    loads = _loads(
        actual_flow=pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 1)],
                "source_facility_id": ["10", "50"],
                "source_location_id": ["20", "70"],
                "demand_tj": [9.0, 15.0],
                "supply_tj": [1.0, 0.0],
                "transfer_in_tj": [0.0, 0.0],
                "transfer_out_tj": [0.0, 0.0],
                "held_in_storage_tj": [0.0, 0.0],
                "source_last_updated_timestamp": [_timestamp(), _timestamp()],
                "ingested_timestamp": [_timestamp(), _timestamp()],
            }
        ),
        capacity=pl.DataFrame(
            {
                "source_facility_id": ["60", "30", "10"],
                "facility_name": [
                    "Wallumbilla - Gladstone Pipeline",
                    "Roma - Brisbane Pipeline",
                    "Carpentaria Gas Pipeline",
                ],
                "capacity_quantity_tj": [99.0, 40.0, 14.0],
                "flow_direction": ["north", "east", "south"],
                "from_gas_date": [
                    date(2024, 1, 1),
                    date(2024, 2, 1),
                    date(2023, 1, 1),
                ],
                "to_gas_date": [None, None, date(2023, 12, 31)],
                "capacity_description": [
                    "WGP north capacity",
                    "future RBP capacity",
                    "expired CGP capacity",
                ],
            }
        ),
    )

    model = build_gbb_map_model(
        loads,
        gas_date=date(2024, 1, 1),
        today=date(2024, 1, 2),
    )
    cgp = _pipeline(model, "CGP")
    qgp = _pipeline(model, "QGP")
    wgp = _pipeline(model, "WGP")

    assert cgp.flow_tj == 8.0
    assert cgp.direction == "south"
    assert cgp.capacity_tj is None
    assert qgp.flow_tj == 15.0
    assert wgp.capacity_tj == 99.0
    assert wgp.status == "Capacity only"


def test_pipeline_records_frame_and_html_render_selected_view() -> None:
    model = build_gbb_map_model(
        _loads(),
        gas_date=date(2024, 1, 1),
        today=date(2024, 1, 2),
    )

    frame = pipeline_records_frame(model.pipelines)
    html = render_gbb_map_html(model, "Pipeline")

    assert frame.height >= 15
    assert "GBB interactive map" in html
    assert "Pipeline flow and capacity" in html
    assert "APLNG" in html
    assert "gbb-plotly-iframe" in html
    assert "Plotly.newPlot" in html
    assert "scattergeo" in html
    assert "mercator" in html
    assert "gbb-map-svg" not in html
    assert "tileLayer" not in html
    assert "leaflet" not in html.lower()


def test_facility_records_and_map_views_render() -> None:
    loads = _loads(
        actual_flow=pl.DataFrame(
            {
                "gas_date": [date(2024, 1, 1), date(2024, 1, 1)],
                "source_facility_id": ["10", "10"],
                "source_location_id": ["20", "80"],
                "demand_tj": [0.0, 0.0],
                "supply_tj": [22.0, 0.0],
                "transfer_in_tj": [0.0, 0.0],
                "transfer_out_tj": [0.0, 0.0],
                "held_in_storage_tj": [0.0, 44.0],
                "source_last_updated_timestamp": [_timestamp(), _timestamp()],
                "ingested_timestamp": [_timestamp(), _timestamp()],
            }
        )
    )
    model = build_gbb_map_model(
        loads,
        gas_date=date(2024, 1, 1),
        today=date(2024, 1, 2),
    )
    production_html = render_gbb_map_html(model, "Production")
    summary_html = render_gbb_map_html(model, "Summary")
    storage_html = render_gbb_map_html(model, "Storage")
    frame = map_helpers.facility_records_frame(model.facilities)

    assert "gbb-plotly-iframe" in summary_html
    assert "Production" in production_html
    assert "Storage" in storage_html
    assert "Ballera" in production_html
    assert "Iona" in storage_html
    assert "Pipeline flow and capacity" not in production_html
    assert "Pipeline flow and capacity" not in storage_html
    assert frame.height == len(model.facilities)


def test_render_includes_load_errors() -> None:
    model = GbbMapModel(
        gas_date=date(2024, 1, 1),
        data_source=FLOW_SOURCE_ACTUAL,
        pipelines=(),
        facilities=(),
        load_errors=("silver_gas_dim_facility: unavailable",),
    )

    html = render_gbb_map_html(model, "Summary")

    assert "Local map inputs unavailable" in html
    assert "silver_gas_dim_facility" in html


def test_private_helper_edges() -> None:
    empty_lookup_loads = _loads(empty_dimensions=True)
    record = PipelineMapRecord(
        code="CGP",
        name="Carpentaria Gas Pipeline",
        operator="APA Group",
        flow_tj=None,
        capacity_tj=None,
        utilisation_pct=None,
        direction=None,
        data_source=FLOW_SOURCE_ACTUAL,
        status="No local data",
    )
    point = FacilityMapRecord(
        label="Iona",
        kind="Storage",
        quantity_tj=None,
        measure="held storage",
        status="No local data",
    )

    assert map_helpers._sum_measure([{"demand_tj": None}], "demand_tj") is None
    assert map_helpers._measure_column("held storage") == "held_in_storage_tj"
    assert map_helpers._measure_column("demand") == "demand_tj"
    assert map_helpers._number(None) is None
    assert map_helpers._number("3.5") == 3.5
    assert map_helpers._number("") is None
    assert map_helpers._table([], "missing").is_empty()
    assert map_helpers._latest_rows_by(pl.DataFrame({"value": [1]}), []).height == 1
    assert map_helpers._enrich_flow_rows(empty_lookup_loads, pl.DataFrame()).is_empty()
    assert map_helpers._facility_lookup(empty_lookup_loads).is_empty()
    assert map_helpers._location_lookup(empty_lookup_loads).is_empty()
    spec = map_helpers._path_spec_by_code("CGP")

    assert map_helpers._pipeline_coordinates(record, spec) == spec.route_coordinates
    south_record = PipelineMapRecord(
        code="CGP",
        name="Carpentaria Gas Pipeline",
        operator="APA Group",
        flow_tj=8.0,
        capacity_tj=None,
        utilisation_pct=None,
        direction="south",
        data_source=FLOW_SOURCE_ACTUAL,
        status="Flow only",
    )
    assert map_helpers._pipeline_coordinates(south_record, spec) == tuple(
        reversed(spec.route_coordinates)
    )
    assert map_helpers._pipeline_weight(record) == 3.0
    assert map_helpers._pipeline_weight(south_record) > 3.0
    assert map_helpers._facility_radius(None) == 6.5
    assert map_helpers._facility_radius(900.0) == 16.0
    assert map_helpers._facility_color("Storage") == "#7553a4"
    assert map_helpers._facility_color("Production") == "#24775d"
    assert map_helpers._route_label_coordinate(((1.0, 2.0), (3.0, 4.0))) == (
        2.0,
        3.0,
    )
    assert map_helpers._label_coordinate((1.0, 2.0)) == (1.26, 2.26)
    assert "Carpentaria Gas Pipeline" in map_helpers._pipeline_tooltip(record)
    assert "Iona" in map_helpers._facility_tooltip(point)
    assert "Carpentaria Gas Pipeline" in map_helpers._pipeline_hover_template(record)
    assert "Iona" in map_helpers._facility_hover_template(point)
    assert "gbb-map-legend" in map_helpers._plotly_legend_markup()
    assert map_helpers._record_color(None, 1.0) == "blue"
    assert map_helpers._record_color(95.0, 1.0) == "red"
    assert map_helpers._record_color(75.0, 1.0) == "amber"
    assert map_helpers._record_color(10.0, 1.0) == "green"
    assert map_helpers._map_color("muted") == "#8b9699"
    assert map_helpers._status_class("Flow only") == "gbb-status-partial"
    assert map_helpers._format_number(3.0) == "3"
    assert map_helpers._format_number(3.25) == "3.2"

    class EmptyMessageError(Exception):
        def __str__(self) -> str:
            return ""

    assert map_helpers._compact_error(EmptyMessageError()) == "EmptyMessageError"
    assert map_helpers._compact_error(OSError("Kernel error -> Generic S3 error")) == (
        "OSError: S3 read failed; LocalStack may be unreachable or the table prefix "
        "is missing"
    )
    with pytest.raises(ValueError, match="unknown pipeline code"):
        map_helpers._path_spec_by_code("missing")
    with pytest.raises(ValueError, match="unknown point label"):
        map_helpers._point_spec_by_label("missing")


def _pipeline(model: GbbMapModel, code: str) -> PipelineMapRecord:
    for record in model.pipelines:
        if record.code == code:
            return record
    raise AssertionError(f"missing pipeline record: {code}")


def _loads(
    actual_flow: pl.DataFrame | None = None,
    forecast: pl.DataFrame | None = None,
    capacity: pl.DataFrame | None = None,
    empty_dimensions: bool = False,
) -> list[GbbMapTableLoad]:
    facilities = (
        pl.DataFrame()
        if empty_dimensions
        else pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "GBB", "GBB"],
                "source_facility_id": ["10", "30", "50", "60"],
                "facility_name": [
                    "Carpentaria Gas Pipeline",
                    "Roma - Brisbane Pipeline",
                    "Queensland Gas Pipeline",
                    "Wallumbilla - Gladstone Pipeline",
                ],
                "facility_short_name": ["CGP", "RBP", "QGP", "WGP"],
                "facility_type": ["PIPE", "PIPE", "PIPE", "PIPE"],
                "facility_type_description": [
                    "Pipeline",
                    "Pipeline",
                    "Pipeline",
                    "Pipeline",
                ],
            }
        )
    )
    locations = (
        pl.DataFrame()
        if empty_dimensions
        else pl.DataFrame(
            {
                "source_system": ["GBB", "GBB", "GBB", "GBB"],
                "source_location_id": ["20", "40", "70", "80"],
                "location_name": ["Ballera", "Brisbane", "Wallumbilla", "Iona"],
                "state": ["QLD", "QLD", "QLD", "VIC"],
            }
        )
    )

    dataframes = {
        "silver_gas_dim_facility": facilities,
        "silver_gas_dim_location": locations,
        "silver_gas_dim_connection_point": pl.DataFrame(),
        "silver_gas_fact_facility_flow_storage": actual_flow
        if actual_flow is not None
        else pl.DataFrame(),
        "silver_gas_fact_nomination_forecast": forecast
        if forecast is not None
        else pl.DataFrame(),
        "silver_gas_fact_capacity_outlook": capacity
        if capacity is not None
        else pl.DataFrame(),
    }

    return [
        GbbMapTableLoad(
            spec=spec,
            uri=f"s3://bucket/silver/gas_model/{spec.table_name}",
            dataframe=dataframes[spec.table_name],
            error=None,
        )
        for spec in GBB_MAP_TABLES
    ]


def _timestamp() -> datetime:
    return datetime(2024, 1, 1, 12, tzinfo=timezone.utc)
