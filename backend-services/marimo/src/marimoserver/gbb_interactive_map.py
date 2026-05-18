"""Helpers for a local Marimo replica of the AEMO GBB interactive map."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime
from html import escape
import socket
from typing import Literal
from urllib.parse import urlparse

from plotly.graph_objs._figure import Figure
from plotly.graph_objs._scattergeo import Scattergeo
import plotly.io as pio
import polars as pl

from marimoserver.gas_model_loader import (
    GasModelReadConfig,
    bounded_row_limit,
    read_parquet_table,
)

AEMO_GBB_INTERACTIVE_MAP_URL = (
    "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/"
    "data-gbb/interactive-map-gbb"
)
AEMO_GBB_MAP_HELP_URL = (
    "https://www.aemo.com.au/energy-systems/gas/gas-bulletin-board-gbb/"
    "procedures-policies-and-guides/map-help"
)

FLOW_SOURCE_ACTUAL = "Actual Flow and Storage"
FLOW_SOURCE_FORECAST = "Nomination and Forecast"

MapView = Literal["Summary", "Pipeline", "Production", "Storage"]
FlowFormula = Literal["net", "demand"]
EndpointChecker = Callable[[Mapping[str, str]], str | None]
TableReader = Callable[[str, Mapping[str, str], int | None], pl.DataFrame]
GeoCoordinate = tuple[float, float]

LOCAL_S3_ENDPOINT_HOSTS = frozenset(("localhost", "127.0.0.1", "localstack"))
LOCAL_S3_ENDPOINT_TIMEOUT_SECONDS = 0.35
GBB_MAP_BOUNDS: tuple[GeoCoordinate, GeoCoordinate] = ((-43.8, 136.4), (-10.2, 154.5))


@dataclass(frozen=True)
class GbbMapTableSpec:
    """A gas_model table used by the GBB map notebook."""

    table_name: str
    label: str


@dataclass(frozen=True)
class GbbMapTableLoad:
    """Loaded GBB map input table or unavailable-state detail."""

    spec: GbbMapTableSpec
    uri: str
    dataframe: pl.DataFrame | None
    error: str | None

    @property
    def available(self) -> bool:
        """Return whether the table loaded and contains at least one row."""
        return self.dataframe is not None and not self.dataframe.is_empty()


@dataclass(frozen=True)
class MapPathSpec:
    """Static display metadata for one pipeline shown on the AEMO GBB map."""

    code: str
    name: str
    operator: str
    route_coordinates: tuple[GeoCoordinate, ...]
    facility_terms: tuple[str, ...]
    location_terms: tuple[str, ...]
    flow_formula: FlowFormula
    positive_direction: str
    negative_direction: str | None = None


@dataclass(frozen=True)
class MapPointSpec:
    """Static display metadata for one map node."""

    label: str
    kind: MapView
    coordinate: GeoCoordinate
    match_terms: tuple[str, ...]
    measure: str


@dataclass(frozen=True)
class MapRegionSpec:
    """Local basemap polygon used by the Plotly GBB map."""

    label: str
    coordinates: tuple[GeoCoordinate, ...]
    label_coordinate: GeoCoordinate


@dataclass(frozen=True)
class PipelineMapRecord:
    """Computed display record for one GBB map pipeline."""

    code: str
    name: str
    operator: str
    flow_tj: float | None
    capacity_tj: float | None
    utilisation_pct: float | None
    direction: str | None
    data_source: str
    status: str


@dataclass(frozen=True)
class FacilityMapRecord:
    """Computed display record for a production or storage map node."""

    label: str
    kind: MapView
    quantity_tj: float | None
    measure: str
    status: str


@dataclass(frozen=True)
class GbbMapModel:
    """Computed map state for one gas day."""

    gas_date: date
    data_source: str
    pipelines: tuple[PipelineMapRecord, ...]
    facilities: tuple[FacilityMapRecord, ...]
    load_errors: tuple[str, ...]


GBB_MAP_TABLES: tuple[GbbMapTableSpec, ...] = (
    GbbMapTableSpec("silver_gas_dim_facility", "Facility standing data"),
    GbbMapTableSpec("silver_gas_dim_location", "Location standing data"),
    GbbMapTableSpec("silver_gas_dim_connection_point", "Connection points"),
    GbbMapTableSpec("silver_gas_fact_facility_flow_storage", "Actual flows"),
    GbbMapTableSpec("silver_gas_fact_nomination_forecast", "Nominations"),
    GbbMapTableSpec("silver_gas_fact_capacity_outlook", "Capacity outlook"),
)

MAP_PIPELINES: tuple[MapPathSpec, ...] = (
    MapPathSpec(
        code="APLNG",
        name="Australia Pacific LNG Gladstone Pipeline",
        operator="APLNG",
        route_coordinates=((-26.58, 149.19), (-25.55, 150.10), (-23.78, 151.30)),
        facility_terms=("aplng", "australia pacific lng"),
        location_terms=("curtis",),
        flow_formula="demand",
        positive_direction="north",
    ),
    MapPathSpec(
        code="CGP",
        name="Carpentaria Gas Pipeline",
        operator="APA Group",
        route_coordinates=((-27.40, 141.82), (-24.50, 140.80), (-20.73, 139.49)),
        facility_terms=("cgp", "carpentaria"),
        location_terms=("ballera",),
        flow_formula="net",
        positive_direction="north",
        negative_direction="south",
    ),
    MapPathSpec(
        code="EGP",
        name="Eastern Gas Pipeline",
        operator="Jemena",
        route_coordinates=(
            (-38.17, 147.08),
            (-36.65, 149.60),
            (-34.75, 150.75),
            (-33.87, 151.21),
        ),
        facility_terms=("egp", "eastern gas"),
        location_terms=("longford",),
        flow_formula="net",
        positive_direction="north",
    ),
    MapPathSpec(
        code="GLNG",
        name="GLNG Pipeline",
        operator="GLNG",
        route_coordinates=((-26.58, 149.19), (-25.10, 150.25), (-23.78, 151.30)),
        facility_terms=("glng",),
        location_terms=("curtis",),
        flow_formula="demand",
        positive_direction="north",
    ),
    MapPathSpec(
        code="LMP",
        name="Longford - Melbourne Pipeline",
        operator="APA Group",
        route_coordinates=((-38.17, 147.08), (-38.00, 146.00), (-37.81, 144.96)),
        facility_terms=("victorian transmission", "lmp", "longford"),
        location_terms=("longford",),
        flow_formula="net",
        positive_direction="west",
    ),
    MapPathSpec(
        code="MAPS",
        name="Moomba to Adelaide Pipeline System",
        operator="Epic Energy",
        route_coordinates=((-28.10, 140.20), (-31.00, 139.15), (-34.93, 138.60)),
        facility_terms=("maps", "moomba to adelaide"),
        location_terms=("moomba",),
        flow_formula="net",
        positive_direction="south",
    ),
    MapPathSpec(
        code="MSP",
        name="Moomba to Sydney Pipeline",
        operator="APA Group",
        route_coordinates=(
            (-28.10, 140.20),
            (-30.60, 143.45),
            (-32.40, 147.50),
            (-33.87, 151.21),
        ),
        facility_terms=("msp", "moomba to sydney"),
        location_terms=("moomba",),
        flow_formula="net",
        positive_direction="south",
        negative_direction="north",
    ),
    MapPathSpec(
        code="PCA",
        name="Port Campbell to Adelaide Pipeline",
        operator="South East Australia Gas Pty Ltd",
        route_coordinates=((-38.42, 142.73), (-36.90, 140.70), (-34.93, 138.60)),
        facility_terms=("pca", "port campbell", "seagas", "sea gas"),
        location_terms=("iona",),
        flow_formula="net",
        positive_direction="west",
    ),
    MapPathSpec(
        code="QGP",
        name="Queensland Gas Pipeline",
        operator="Jemena",
        route_coordinates=((-26.58, 149.19), (-24.80, 150.10), (-23.85, 151.10)),
        facility_terms=("qgp", "queensland gas"),
        location_terms=(),
        flow_formula="demand",
        positive_direction="north",
    ),
    MapPathSpec(
        code="RBP",
        name="Roma - Brisbane Pipeline",
        operator="APA Group",
        route_coordinates=((-26.58, 149.19), (-27.00, 151.00), (-27.47, 153.02)),
        facility_terms=("rbp", "roma", "brisbane"),
        location_terms=("brisbane",),
        flow_formula="demand",
        positive_direction="east",
    ),
    MapPathSpec(
        code="SWP",
        name="South West Pipeline",
        operator="Australian Energy Market Operator Ltd",
        route_coordinates=((-38.42, 142.73), (-38.10, 144.10), (-37.81, 144.96)),
        facility_terms=("victorian transmission", "swp", "south west"),
        location_terms=("iona",),
        flow_formula="net",
        positive_direction="east",
        negative_direction="west",
    ),
    MapPathSpec(
        code="SWQP-WAL",
        name="South West Queensland Pipeline - Wallumbilla leg",
        operator="APA Group",
        route_coordinates=((-26.58, 149.19), (-26.95, 145.20), (-27.40, 141.82)),
        facility_terms=("swqp", "south west queensland"),
        location_terms=("wallumbilla",),
        flow_formula="net",
        positive_direction="west",
        negative_direction="east",
    ),
    MapPathSpec(
        code="SWQP-MOO",
        name="South West Queensland Pipeline - Moomba leg",
        operator="APA Group",
        route_coordinates=((-28.10, 140.20), (-27.70, 141.00), (-27.40, 141.82)),
        facility_terms=("swqp", "south west queensland"),
        location_terms=("moomba",),
        flow_formula="net",
        positive_direction="east",
        negative_direction="west",
    ),
    MapPathSpec(
        code="TGP",
        name="Tasmanian Gas Pipeline",
        operator="Tasmanian Gas Pipeline Pty Ltd",
        route_coordinates=(
            (-38.17, 147.08),
            (-39.45, 147.65),
            (-40.72, 147.25),
            (-41.12, 146.90),
        ),
        facility_terms=("tgp", "tasmanian"),
        location_terms=("longford",),
        flow_formula="net",
        positive_direction="south",
    ),
    MapPathSpec(
        code="VNI",
        name="Victoria Northern Interconnect",
        operator="Australian Energy Market Operator Ltd",
        route_coordinates=((-37.81, 144.96), (-36.55, 146.05), (-35.67, 147.04)),
        facility_terms=("victorian transmission", "vni", "northern interconnect"),
        location_terms=("culcairn",),
        flow_formula="net",
        positive_direction="south",
        negative_direction="north",
    ),
    MapPathSpec(
        code="WGP",
        name="Wallumbilla - Gladstone Pipeline",
        operator="APA Group",
        route_coordinates=((-26.58, 149.19), (-25.20, 150.40), (-23.85, 151.25)),
        facility_terms=("wgp", "wallumbilla", "gladstone"),
        location_terms=("curtis",),
        flow_formula="demand",
        positive_direction="north",
    ),
)

MAP_POINTS: tuple[MapPointSpec, ...] = (
    MapPointSpec(
        "Curtis Island", "Production", (-23.78, 151.30), ("curtis",), "supply"
    ),
    MapPointSpec(
        "Wallumbilla", "Production", (-26.58, 149.19), ("wallumbilla",), "supply"
    ),
    MapPointSpec("Moomba", "Production", (-28.10, 140.20), ("moomba",), "supply"),
    MapPointSpec("Longford", "Production", (-38.17, 147.08), ("longford",), "supply"),
    MapPointSpec("Ballera", "Production", (-27.40, 141.82), ("ballera",), "supply"),
    MapPointSpec("Iona", "Storage", (-38.42, 142.73), ("iona",), "held storage"),
    MapPointSpec(
        "Dandenong LNG",
        "Storage",
        (-38.02, 145.20),
        ("dandenong",),
        "held storage",
    ),
    MapPointSpec(
        "Moomba Storage", "Storage", (-28.10, 140.20), ("moomba",), "held storage"
    ),
)

MAP_REGIONS: tuple[MapRegionSpec, ...] = (
    MapRegionSpec(
        label="Queensland",
        coordinates=(
            (-29.2, 138.0),
            (-10.2, 138.0),
            (-10.6, 142.8),
            (-14.2, 145.2),
            (-19.8, 148.8),
            (-23.8, 151.3),
            (-28.5, 153.7),
            (-29.2, 138.0),
        ),
        label_coordinate=(-22.6, 145.2),
    ),
    MapRegionSpec(
        label="New South Wales",
        coordinates=(
            (-37.5, 141.0),
            (-29.2, 141.0),
            (-28.5, 153.7),
            (-33.9, 151.5),
            (-37.5, 149.9),
            (-37.5, 141.0),
        ),
        label_coordinate=(-33.0, 146.7),
    ),
    MapRegionSpec(
        label="Victoria",
        coordinates=(
            (-39.2, 141.0),
            (-37.5, 141.0),
            (-37.5, 149.9),
            (-38.6, 146.9),
            (-38.4, 144.0),
            (-39.2, 141.0),
        ),
        label_coordinate=(-37.9, 145.3),
    ),
    MapRegionSpec(
        label="South Australia",
        coordinates=(
            (-38.2, 129.0),
            (-25.8, 129.0),
            (-25.8, 138.0),
            (-29.2, 138.0),
            (-29.2, 141.0),
            (-37.5, 141.0),
            (-38.2, 129.0),
        ),
        label_coordinate=(-32.7, 136.5),
    ),
    MapRegionSpec(
        label="Tasmania",
        coordinates=(
            (-43.8, 144.5),
            (-40.4, 144.5),
            (-40.7, 148.5),
            (-43.1, 148.3),
            (-43.8, 144.5),
        ),
        label_coordinate=(-42.1, 146.8),
    ),
)


def normalize_gas_date(value: object | None, today: date | None = None) -> date:
    """Normalize a Marimo date widget value into a date."""
    fallback = date.today() if today is None else today
    if value is None:
        return fallback
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip() != "":
        return date.fromisoformat(value.strip())
    return fallback


def check_gbb_map_s3_endpoint(storage_options: Mapping[str, str]) -> str | None:
    """Return a readable local S3 endpoint error before expensive S3 table reads."""
    endpoint = storage_options.get("AWS_ENDPOINT_URL", "").strip()
    if endpoint == "":
        return None

    parsed_endpoint = urlparse(endpoint)
    host = parsed_endpoint.hostname
    if host not in LOCAL_S3_ENDPOINT_HOSTS:
        return None

    port = parsed_endpoint.port
    if port is None:
        port = 443 if parsed_endpoint.scheme == "https" else 80

    try:
        with socket.create_connection(
            (host, port),
            timeout=LOCAL_S3_ENDPOINT_TIMEOUT_SECONDS,
        ):
            return None
    except OSError:
        return (
            f"S3 endpoint unavailable: {endpoint}; start LocalStack or set "
            "AWS_ENDPOINT_URL to a reachable endpoint"
        )


def load_gbb_map_tables(
    config: GasModelReadConfig,
    specs: Sequence[GbbMapTableSpec] = GBB_MAP_TABLES,
    reader: TableReader | None = None,
    endpoint_checker: EndpointChecker | None = None,
    gas_date: date | None = None,
) -> list[GbbMapTableLoad]:
    """Load configured map input tables, returning unavailable entries on errors."""
    storage_options = config.storage_options()
    endpoint_error = None
    if endpoint_checker is not None:
        endpoint_error = endpoint_checker(storage_options)
    if endpoint_error is not None:
        return [
            GbbMapTableLoad(
                spec=spec,
                uri=config.table_uri(spec.table_name),
                dataframe=None,
                error=endpoint_error,
            )
            for spec in specs
        ]

    row_limit = bounded_row_limit(config)
    loads: list[GbbMapTableLoad] = []

    for spec in specs:
        uri = config.table_uri(spec.table_name)
        try:
            if reader is None:
                dataframe = read_gbb_map_table(
                    uri,
                    storage_options,
                    row_limit,
                    table_name=spec.table_name,
                    gas_date=gas_date,
                )
            else:
                dataframe = reader(uri, storage_options, row_limit)
        except Exception as error:
            loads.append(
                GbbMapTableLoad(
                    spec=spec,
                    uri=uri,
                    dataframe=None,
                    error=_compact_error(error),
                )
            )
            continue

        loads.append(
            GbbMapTableLoad(
                spec=spec,
                uri=uri,
                dataframe=dataframe,
                error=None,
            )
        )

    return loads


def read_gbb_map_table(
    uri: str,
    storage_options: Mapping[str, str],
    row_limit: int | None = None,
    *,
    table_name: str | None = None,
    gas_date: date | None = None,
) -> pl.DataFrame:
    """Read a GBB map table stored as a gas_model parquet prefix."""
    filter_expression = _gas_day_filter_expression(table_name, gas_date)
    if filter_expression is None:
        return read_parquet_table(uri, storage_options, row_limit=row_limit)
    return read_parquet_table(
        uri,
        storage_options,
        row_limit=row_limit,
        filter_expression=filter_expression,
    )


def _gas_day_filter_expression(
    table_name: str | None,
    gas_date: date | None,
) -> pl.Expr | None:
    if gas_date is None:
        return None
    if table_name == "silver_gas_fact_facility_flow_storage":
        return pl.col("gas_date") == gas_date
    if table_name == "silver_gas_fact_nomination_forecast":
        return (pl.col("source_system") == "GBB") & (pl.col("gas_date") == gas_date)
    if table_name == "silver_gas_fact_capacity_outlook":
        return (
            pl.col("from_gas_date").is_null() | (pl.col("from_gas_date") <= gas_date)
        ) & (pl.col("to_gas_date").is_null() | (pl.col("to_gas_date") >= gas_date))
    return None


def build_gbb_map_model(
    loads: Sequence[GbbMapTableLoad],
    gas_date: date,
    today: date | None = None,
) -> GbbMapModel:
    """Build pipeline and facility display records for one GBB gas day."""
    source_cutover = date.today() if today is None else today
    data_source = (
        FLOW_SOURCE_ACTUAL if gas_date < source_cutover else FLOW_SOURCE_FORECAST
    )
    flow_rows = _flow_rows(loads, gas_date, data_source)
    capacity_rows = _capacity_rows(loads, gas_date)

    pipelines = tuple(
        _pipeline_record(spec, flow_rows, capacity_rows, data_source)
        for spec in MAP_PIPELINES
    )
    facilities = tuple(_facility_record(spec, flow_rows) for spec in MAP_POINTS)
    load_errors = tuple(
        f"{load.spec.table_name}: {load.error}"
        for load in loads
        if load.error is not None
    )

    return GbbMapModel(
        gas_date=gas_date,
        data_source=data_source,
        pipelines=pipelines,
        facilities=facilities,
        load_errors=load_errors,
    )


def pipeline_records_frame(records: Sequence[PipelineMapRecord]) -> pl.DataFrame:
    """Return pipeline records as a Marimo table-friendly frame."""
    return pl.DataFrame(
        [
            {
                "pipeline": record.code,
                "name": record.name,
                "operator": record.operator,
                "flow TJ/d": record.flow_tj,
                "capacity TJ/d": record.capacity_tj,
                "utilisation %": record.utilisation_pct,
                "direction": record.direction or "",
                "status": record.status,
            }
            for record in records
        ]
    )


def facility_records_frame(records: Sequence[FacilityMapRecord]) -> pl.DataFrame:
    """Return facility records as a Marimo table-friendly frame."""
    return pl.DataFrame(
        [
            {
                "facility": record.label,
                "kind": record.kind,
                "measure": record.measure,
                "quantity TJ/d": record.quantity_tj,
                "status": record.status,
            }
            for record in records
        ]
    )


def map_load_status_frame(loads: Sequence[GbbMapTableLoad]) -> pl.DataFrame:
    """Return map input load status as a table."""
    return pl.DataFrame(
        [
            {
                "table": load.spec.table_name,
                "label": load.spec.label,
                "status": "Available" if load.available else "Empty or missing",
                "rows": 0 if load.dataframe is None else load.dataframe.height,
                "detail": load.error or "",
                "uri": load.uri,
            }
            for load in loads
        ]
    )


def render_gbb_map_html(model: GbbMapModel, active_view: MapView) -> str:
    """Render the Plotly GBB map and side summary."""
    map_markup = _plotly_map_markup(model, active_view)
    side_markup = _side_summary(model, active_view)
    stats_markup = _map_stats_markup(model)
    notice_markup = _load_errors_markup(model.load_errors)

    return f"""
<style>
  .gbb-map-shell {{
    --gbb-ink: #182226;
    --gbb-muted: #59666c;
    --gbb-border: #d9e0dd;
    --gbb-paper: #f8f8f4;
    --gbb-panel: #ffffff;
    --gbb-sea: #e5f0f4;
    --gbb-land: #edf2e8;
    --gbb-blue: #156d93;
    --gbb-green: #24775d;
    --gbb-amber: #b37a24;
    --gbb-red: #b44a36;
    --gbb-purple: #7553a4;
    color: var(--gbb-ink);
    display: grid;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    grid-template-columns: minmax(420px, 1fr) minmax(300px, 380px);
    gap: 16px;
    width: 100%;
  }}
  .gbb-map-panel,
  .gbb-summary-panel {{
    background: var(--gbb-panel);
    border: 1px solid var(--gbb-border);
    border-radius: 8px;
    box-shadow: 0 14px 38px rgba(29, 39, 43, 0.08);
    overflow: hidden;
  }}
  .gbb-map-header {{
    align-items: center;
    background: #ffffff;
    display: grid;
    gap: 14px;
    grid-template-columns: minmax(0, 1fr) auto;
    padding: 16px 18px 14px;
  }}
  .gbb-map-kicker {{
    color: var(--gbb-muted);
    font-size: 12px;
    font-weight: 700;
    margin: 0 0 4px;
  }}
  .gbb-map-title {{
    font-size: 22px;
    font-weight: 750;
    line-height: 1.15;
    margin: 0;
  }}
  .gbb-map-subtitle {{
    color: var(--gbb-muted);
    font-size: 13px;
    margin: 5px 0 0;
  }}
  .gbb-map-badge {{
    background: #eaf2f4;
    border: 1px solid #c5d8df;
    border-radius: 999px;
    color: var(--gbb-blue);
    font-size: 12px;
    font-weight: 700;
    padding: 6px 11px;
    white-space: nowrap;
  }}
  .gbb-stat-grid {{
    background: #fbfbf8;
    border-bottom: 1px solid var(--gbb-border);
    border-top: 1px solid var(--gbb-border);
    display: grid;
    gap: 0;
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }}
  .gbb-stat {{
    min-width: 0;
    padding: 12px 16px;
  }}
  .gbb-stat + .gbb-stat {{
    border-left: 1px solid var(--gbb-border);
  }}
  .gbb-stat-label {{
    color: var(--gbb-muted);
    font-size: 11px;
    font-weight: 700;
    margin-bottom: 4px;
  }}
  .gbb-stat-value {{
    color: var(--gbb-ink);
    font-size: 19px;
    font-weight: 750;
    line-height: 1.1;
  }}
  .gbb-data-notice {{
    background: #fff8ec;
    border-bottom: 1px solid #ead7b8;
    color: #6f4314;
    font-size: 13px;
    line-height: 1.4;
    padding: 11px 18px;
  }}
  .gbb-data-notice summary {{
    cursor: pointer;
    font-weight: 700;
  }}
  .gbb-data-notice ul {{
    margin: 8px 0 0 18px;
    padding: 0;
  }}
  .gbb-map-stage {{
    background: var(--gbb-sea);
    padding: 10px;
    position: relative;
  }}
  .gbb-plotly-iframe {{
    background: var(--gbb-sea);
    border: 0;
    border-radius: 6px;
    display: block;
    height: 560px;
    width: 100%;
  }}
  .gbb-map-legend {{
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(199, 211, 206, 0.95);
    border-radius: 8px;
    bottom: 28px;
    box-shadow: 0 10px 28px rgba(29, 39, 43, 0.14);
    color: var(--gbb-ink);
    font-size: 12px;
    left: 28px;
    line-height: 1.25;
    padding: 10px 12px;
    position: absolute;
    z-index: 2;
  }}
  .gbb-map-legend strong {{
    display: block;
    font-size: 12px;
    margin-bottom: 7px;
  }}
  .gbb-map-legend-item {{
    align-items: center;
    display: grid;
    gap: 8px;
    grid-template-columns: 22px max-content;
    margin-top: 5px;
  }}
  .gbb-map-legend-line {{
    border-radius: 999px;
    display: inline-block;
    height: 4px;
    width: 22px;
  }}
  .gbb-map-legend-dot {{
    border-radius: 999px;
    display: inline-block;
    height: 10px;
    width: 10px;
  }}
  .gbb-summary-panel {{
    max-height: 730px;
    overflow: auto;
    padding: 14px 16px;
  }}
  .gbb-summary-panel h3 {{
    font-size: 17px;
    line-height: 1.2;
    margin: 0 0 12px;
  }}
  .gbb-summary-item {{
    border-top: 1px solid var(--gbb-border);
    padding: 11px 0;
  }}
  .gbb-summary-item:first-of-type {{
    border-top: 0;
  }}
  .gbb-summary-name {{
    font-size: 13px;
    font-weight: 750;
    line-height: 1.25;
  }}
  .gbb-summary-meta {{
    color: var(--gbb-muted);
    font-size: 12px;
    line-height: 1.35;
    margin-top: 3px;
  }}
  .gbb-status-pill {{
    border-radius: 999px;
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    margin-top: 7px;
    padding: 3px 8px;
  }}
  .gbb-status-good {{
    background: #e6f1eb;
    color: var(--gbb-green);
  }}
  .gbb-status-partial {{
    background: #eaf2f4;
    color: var(--gbb-blue);
  }}
  .gbb-status-empty {{
    background: #eef0ee;
    color: #69757a;
  }}
  .gbb-meter {{
    background: #e7ece8;
    border-radius: 999px;
    height: 6px;
    margin-top: 9px;
    overflow: hidden;
  }}
  .gbb-meter-fill {{
    background: var(--gbb-green);
    border-radius: inherit;
    height: 100%;
    min-width: 2px;
  }}
  @media (max-width: 900px) {{
    .gbb-map-shell {{
      grid-template-columns: 1fr;
    }}
    .gbb-stat-grid {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }}
    .gbb-stat:nth-child(3) {{
      border-left: 0;
      border-top: 1px solid var(--gbb-border);
    }}
    .gbb-stat:nth-child(4) {{
      border-top: 1px solid var(--gbb-border);
    }}
    .gbb-map-stage {{
      padding: 8px;
    }}
    .gbb-plotly-iframe {{
      height: 430px;
    }}
    .gbb-map-legend {{
      bottom: 18px;
      left: 18px;
    }}
  }}
</style>
<div class="gbb-map-shell">
  <section class="gbb-map-panel" aria-label="GBB interactive map replica">
    <div class="gbb-map-header">
      <div>
        <p class="gbb-map-kicker">Gas Bulletin Board</p>
        <p class="gbb-map-title">Interactive map</p>
        <p class="gbb-map-subtitle">Gas day {escape(model.gas_date.isoformat())} - {escape(model.data_source)}</p>
      </div>
      <div class="gbb-map-badge">{escape(active_view)}</div>
    </div>
    {stats_markup}
    {notice_markup}
    <div class="gbb-map-stage">
      {map_markup}
    </div>
  </section>
  <aside class="gbb-summary-panel" aria-label="GBB map summary">
    {side_markup}
  </aside>
</div>
"""


def _flow_rows(
    loads: Sequence[GbbMapTableLoad],
    gas_date: date,
    data_source: str,
) -> list[dict[str, object]]:
    if data_source == FLOW_SOURCE_ACTUAL:
        source = _table(loads, "silver_gas_fact_facility_flow_storage")
        if source.is_empty():
            return []
        flow = (
            source.filter(pl.col("gas_date") == gas_date)
            .with_columns(
                demand_tj=pl.col("demand_tj").cast(pl.Float64),
                supply_tj=pl.col("supply_tj").cast(pl.Float64),
                transfer_in_tj=pl.col("transfer_in_tj").cast(pl.Float64),
                transfer_out_tj=pl.col("transfer_out_tj").cast(pl.Float64),
                held_in_storage_tj=pl.col("held_in_storage_tj").cast(pl.Float64),
            )
            .pipe(_latest_rows_by, ["source_facility_id", "source_location_id"])
        )
    else:
        source = _table(loads, "silver_gas_fact_nomination_forecast")
        if source.is_empty():
            return []
        flow = (
            source.filter(
                (pl.col("source_system") == "GBB") & (pl.col("gas_date") == gas_date)
            )
            .with_columns(
                demand_tj=pl.col("demand_forecast_gj").cast(pl.Float64) / 1000,
                supply_tj=pl.col("supply_forecast_gj").cast(pl.Float64) / 1000,
                transfer_in_tj=pl.col("transfer_in_forecast_gj").cast(pl.Float64)
                / 1000,
                transfer_out_tj=pl.col("transfer_out_forecast_gj").cast(pl.Float64)
                / 1000,
                held_in_storage_tj=pl.lit(None).cast(pl.Float64),
            )
            .pipe(_latest_rows_by, ["source_facility_id", "source_location_id"])
        )

    return _enrich_flow_rows(loads, flow).to_dicts()


def _capacity_rows(
    loads: Sequence[GbbMapTableLoad],
    gas_date: date,
) -> list[dict[str, object]]:
    source = _table(loads, "silver_gas_fact_capacity_outlook")
    if source.is_empty():
        return []
    rows = []
    for row in source.to_dicts():
        from_gas_date = row.get("from_gas_date")
        to_gas_date = row.get("to_gas_date")
        if isinstance(from_gas_date, date) and from_gas_date > gas_date:
            continue
        if isinstance(to_gas_date, date) and to_gas_date < gas_date:
            continue
        rows.append(row)
    return rows


def _pipeline_record(
    spec: MapPathSpec,
    flow_rows: Sequence[Mapping[str, object]],
    capacity_rows: Sequence[Mapping[str, object]],
    data_source: str,
) -> PipelineMapRecord:
    matching_flows = [row for row in flow_rows if _matches_pipeline(row, spec)]
    raw_flow = _pipeline_flow_value(spec, matching_flows)
    direction = _pipeline_direction(spec, raw_flow)
    flow_tj = None if raw_flow is None else round(abs(raw_flow), 2)
    capacity_tj = _pipeline_capacity(spec, capacity_rows, direction)
    utilisation_pct = _utilisation(flow_tj, capacity_tj)
    status = _pipeline_status(flow_tj, capacity_tj)

    return PipelineMapRecord(
        code=spec.code,
        name=spec.name,
        operator=spec.operator,
        flow_tj=flow_tj,
        capacity_tj=capacity_tj,
        utilisation_pct=utilisation_pct,
        direction=direction,
        data_source=data_source,
        status=status,
    )


def _facility_record(
    spec: MapPointSpec,
    flow_rows: Sequence[Mapping[str, object]],
) -> FacilityMapRecord:
    matching_rows = [
        row for row in flow_rows if _contains_any(_row_text(row), spec.match_terms)
    ]
    values = [_number(row.get(_measure_column(spec.measure))) for row in matching_rows]
    valid_values = [value for value in values if value is not None]
    quantity = None if not valid_values else round(sum(valid_values), 2)
    status = "Available" if quantity is not None else "No local data"
    return FacilityMapRecord(
        label=spec.label,
        kind=spec.kind,
        quantity_tj=quantity,
        measure=spec.measure,
        status=status,
    )


def _pipeline_flow_value(
    spec: MapPathSpec,
    rows: Sequence[Mapping[str, object]],
) -> float | None:
    if not rows:
        return None

    if spec.flow_formula == "demand":
        return _sum_measure(rows, "demand_tj")

    supply = _sum_measure(rows, "supply_tj") or 0.0
    transfer_in = _sum_measure(rows, "transfer_in_tj") or 0.0
    demand = _sum_measure(rows, "demand_tj") or 0.0
    transfer_out = _sum_measure(rows, "transfer_out_tj") or 0.0
    return supply + transfer_in - demand - transfer_out


def _pipeline_direction(spec: MapPathSpec, raw_flow: float | None) -> str | None:
    if raw_flow is None:
        return None
    if spec.negative_direction is None:
        return spec.positive_direction
    if raw_flow >= 0:
        return spec.positive_direction
    return spec.negative_direction


def _pipeline_capacity(
    spec: MapPathSpec,
    rows: Sequence[Mapping[str, object]],
    direction: str | None,
) -> float | None:
    matching = [row for row in rows if _matches_capacity(row, spec)]
    if direction is not None:
        directional = [
            row
            for row in matching
            if _contains_any(str(row.get("flow_direction", "")), (direction,))
        ]
        if directional:
            matching = directional

    values = [_number(row.get("capacity_quantity_tj")) for row in matching]
    valid_values = [value for value in values if value is not None and value >= 0]
    if not valid_values:
        return None
    return round(max(valid_values), 2)


def _utilisation(flow_tj: float | None, capacity_tj: float | None) -> float | None:
    if flow_tj is None or capacity_tj is None or capacity_tj <= 0:
        return None
    return round((flow_tj / capacity_tj) * 100, 1)


def _pipeline_status(flow_tj: float | None, capacity_tj: float | None) -> str:
    if flow_tj is not None and capacity_tj is not None:
        return "Flow and capacity"
    if flow_tj is not None:
        return "Flow only"
    if capacity_tj is not None:
        return "Capacity only"
    return "No local data"


def _sum_measure(rows: Sequence[Mapping[str, object]], column: str) -> float | None:
    values = [_number(row.get(column)) for row in rows]
    valid_values = [value for value in values if value is not None]
    if not valid_values:
        return None
    return sum(valid_values)


def _matches_pipeline(row: Mapping[str, object], spec: MapPathSpec) -> bool:
    text = _row_text(row)
    facility_match = _contains_any(text, spec.facility_terms)
    if not facility_match:
        return False
    if not spec.location_terms:
        return True
    return _contains_any(text, spec.location_terms)


def _matches_capacity(row: Mapping[str, object], spec: MapPathSpec) -> bool:
    return _contains_any(_row_text(row), spec.facility_terms)


def _contains_any(value: str, terms: Sequence[str]) -> bool:
    normalized = value.casefold()
    return any(term.casefold() in normalized for term in terms)


def _row_text(row: Mapping[str, object]) -> str:
    columns = (
        "facility_name",
        "facility_short_name",
        "source_facility_id",
        "location_name",
        "source_location_id",
        "capacity_description",
    )
    return " ".join(str(row.get(column, "") or "") for column in columns)


def _measure_column(measure: str) -> str:
    if measure == "supply":
        return "supply_tj"
    if measure == "held storage":
        return "held_in_storage_tj"
    return "demand_tj"


def _number(value: object | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str) and value.strip() != "":
        return float(value)
    return None


def _table(loads: Sequence[GbbMapTableLoad], table_name: str) -> pl.DataFrame:
    for load in loads:
        if load.spec.table_name == table_name and load.dataframe is not None:
            return load.dataframe
    return pl.DataFrame()


def _latest_rows_by(dataframe: pl.DataFrame, subset: Sequence[str]) -> pl.DataFrame:
    sort_columns = [
        column
        for column in (*subset, "source_last_updated_timestamp", "ingested_timestamp")
        if column in dataframe.columns
    ]
    descending = [
        column in ("source_last_updated_timestamp", "ingested_timestamp")
        for column in sort_columns
    ]
    if not sort_columns:
        return dataframe
    return dataframe.sort(
        sort_columns,
        descending=descending,
        nulls_last=True,
    ).unique(subset=list(subset), keep="first", maintain_order=True)


def _enrich_flow_rows(
    loads: Sequence[GbbMapTableLoad],
    flow: pl.DataFrame,
) -> pl.DataFrame:
    if flow.is_empty():
        return flow

    return flow.join(
        _facility_lookup(loads),
        on="source_facility_id",
        how="left",
    ).join(
        _location_lookup(loads),
        on="source_location_id",
        how="left",
    )


def _facility_lookup(loads: Sequence[GbbMapTableLoad]) -> pl.DataFrame:
    source = _table(loads, "silver_gas_dim_facility")
    schema = {
        "source_facility_id": pl.String,
        "facility_name": pl.String,
        "facility_short_name": pl.String,
        "facility_type": pl.String,
        "facility_type_description": pl.String,
    }
    if source.is_empty():
        return pl.DataFrame(schema=schema)
    return (
        source.filter(pl.col("source_system") == "GBB")
        .select(
            source_facility_id=pl.col("source_facility_id").cast(pl.String),
            facility_name=pl.col("facility_name").cast(pl.String),
            facility_short_name=pl.col("facility_short_name").cast(pl.String),
            facility_type=pl.col("facility_type").cast(pl.String),
            facility_type_description=pl.col("facility_type_description").cast(
                pl.String
            ),
        )
        .unique(subset=["source_facility_id"], keep="first", maintain_order=True)
    )


def _location_lookup(loads: Sequence[GbbMapTableLoad]) -> pl.DataFrame:
    source = _table(loads, "silver_gas_dim_location")
    schema = {
        "source_location_id": pl.String,
        "location_name": pl.String,
        "state": pl.String,
    }
    if source.is_empty():
        return pl.DataFrame(schema=schema)
    return (
        source.filter(pl.col("source_system") == "GBB")
        .select(
            source_location_id=pl.col("source_location_id").cast(pl.String),
            location_name=pl.col("location_name").cast(pl.String),
            state=pl.col("state").cast(pl.String),
        )
        .unique(subset=["source_location_id"], keep="first", maintain_order=True)
    )


def _path_spec_by_code(code: str) -> MapPathSpec:
    for spec in MAP_PIPELINES:
        if spec.code == code:
            return spec
    raise ValueError(f"unknown pipeline code: {code}")


def _point_spec_by_label(label: str) -> MapPointSpec:
    for spec in MAP_POINTS:
        if spec.label == label:
            return spec
    raise ValueError(f"unknown point label: {label}")


def _plotly_map_markup(model: GbbMapModel, active_view: MapView) -> str:
    figure = _plotly_map_figure(model, active_view)
    plotly_div = pio.to_html(  # type: ignore[no-untyped-call]
        figure,
        config={
            "displayModeBar": False,
            "displaylogo": False,
            "responsive": True,
            "scrollZoom": True,
        },
        default_height="100%",
        default_width="100%",
        div_id=f"gbb-plotly-map-{active_view.casefold()}",
        full_html=False,
        include_plotlyjs=True,
    )
    plotly_html = (
        '<!doctype html><html><head><meta charset="utf-8">'
        "<style>html,body{height:100%;margin:0;overflow:hidden;}</style>"
        f"</head><body>{plotly_div}</body></html>"
    )
    return (
        '<iframe class="gbb-plotly-iframe" '
        'title="East coast gas pipeline map" '
        f'srcdoc="{escape(plotly_html, quote=True)}"></iframe>'
        f"{_plotly_legend_markup()}"
    )


def _plotly_map_figure(model: GbbMapModel, active_view: MapView) -> Figure:
    figure = Figure()
    _add_plotly_region_labels(figure)

    if active_view in ("Summary", "Pipeline"):
        for record in model.pipelines:
            _add_plotly_pipeline(
                figure,
                record,
                _path_spec_by_code(record.code),
                show_label=active_view == "Pipeline",
            )

    if active_view in ("Summary", "Production", "Storage"):
        for record in model.facilities:
            spec = _point_spec_by_label(record.label)
            if active_view in ("Summary", spec.kind):
                _add_plotly_facility(
                    figure,
                    record,
                    spec,
                    show_label=active_view != "Summary",
                )

    figure.update_layout(
        autosize=True,
        dragmode="pan",
        font={
            "family": (
                "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "
                "Segoe UI, sans-serif"
            ),
            "color": "#182226",
        },
        height=560,
        geo={
            "bgcolor": "#e5f0f4",
            "coastlinecolor": "#9cafb6",
            "coastlinewidth": 1.2,
            "countrycolor": "#b9c5c0",
            "fitbounds": False,
            "lakecolor": "#d7e8ee",
            "landcolor": "#edf2e8",
            "lataxis": {"range": [GBB_MAP_BOUNDS[0][0], -19.2]},
            "lonaxis": {"range": [137.0, GBB_MAP_BOUNDS[1][1]]},
            "oceancolor": "#e5f0f4",
            "projection": {"type": "mercator"},
            "resolution": 50,
            "rivercolor": "#c2dce4",
            "showcoastlines": True,
            "showcountries": False,
            "showframe": False,
            "showland": True,
            "showlakes": True,
            "showocean": True,
            "showrivers": True,
        },
        margin={"b": 0, "l": 0, "r": 0, "t": 0},
        paper_bgcolor="#e5f0f4",
        plot_bgcolor="#e5f0f4",
        showlegend=False,
    )
    return figure


def _add_plotly_region_labels(figure: Figure) -> None:
    figure.add_trace(
        Scattergeo(
            hoverinfo="skip",
            lat=[region.label_coordinate[0] for region in MAP_REGIONS],
            lon=[region.label_coordinate[1] for region in MAP_REGIONS],
            mode="text",
            showlegend=False,
            text=[region.label.upper() for region in MAP_REGIONS],
            textfont={"color": "#53646a", "size": 11},
            textposition="middle center",
        )
    )


def _add_plotly_pipeline(
    figure: Figure,
    record: PipelineMapRecord,
    spec: MapPathSpec,
    *,
    show_label: bool,
) -> None:
    coordinates = _pipeline_coordinates(record, spec)
    lats, lons = _coordinate_lists(coordinates)
    color = _record_color(record.utilisation_pct, record.flow_tj)
    stroke = _map_color(color)
    weight = _pipeline_weight(record)

    figure.add_trace(
        Scattergeo(
            hoverinfo="skip",
            lat=lats,
            line={"color": "rgba(25, 41, 46, 0.18)", "width": weight + 5},
            lon=lons,
            mode="lines",
            showlegend=False,
        )
    )
    figure.add_trace(
        Scattergeo(
            hovertemplate=_pipeline_hover_template(record),
            lat=lats,
            line={
                "color": stroke,
                "width": weight,
            },
            lon=lons,
            mode="lines",
            opacity=0.9 if record.status != "No local data" else 0.58,
            showlegend=False,
        )
    )

    if not show_label:
        return

    label_coordinate = _route_label_coordinate(coordinates)
    figure.add_trace(
        Scattergeo(
            hoverinfo="skip",
            lat=[label_coordinate[0]],
            lon=[label_coordinate[1]],
            mode="text",
            showlegend=False,
            text=[record.code],
            textfont={"color": stroke, "size": 11},
            textposition="middle center",
        )
    )


def _add_plotly_facility(
    figure: Figure,
    record: FacilityMapRecord,
    spec: MapPointSpec,
    *,
    show_label: bool,
) -> None:
    color = _facility_color(spec.kind)
    radius = _facility_radius(record.quantity_tj)
    text = record.label if show_label else None

    figure.add_trace(
        Scattergeo(
            hoverinfo="skip",
            lat=[spec.coordinate[0]],
            lon=[spec.coordinate[1]],
            marker={
                "color": "#ffffff",
                "opacity": 0.72,
                "size": radius * 2.05,
            },
            mode="markers",
            showlegend=False,
        )
    )
    figure.add_trace(
        Scattergeo(
            hovertemplate=_facility_hover_template(record),
            lat=[spec.coordinate[0]],
            lon=[spec.coordinate[1]],
            marker={
                "color": color,
                "opacity": 0.92 if record.quantity_tj is not None else 0.42,
                "size": radius * 1.6,
            },
            mode="markers+text" if show_label else "markers",
            showlegend=False,
            text=[text] if text is not None else None,
            textfont={"color": "#17242a", "size": 12},
            textposition="middle right",
        )
    )


def _coordinate_lists(
    coordinates: Sequence[GeoCoordinate],
) -> tuple[list[float], list[float]]:
    return (
        [coordinate[0] for coordinate in coordinates],
        [coordinate[1] for coordinate in coordinates],
    )


def _pipeline_coordinates(
    record: PipelineMapRecord,
    spec: MapPathSpec,
) -> tuple[GeoCoordinate, ...]:
    if record.direction == spec.negative_direction:
        return tuple(reversed(spec.route_coordinates))
    return spec.route_coordinates


def _pipeline_weight(record: PipelineMapRecord) -> float:
    if record.flow_tj is None:
        return 3.0
    return min(7.0, 3.4 + (record.flow_tj / 180))


def _facility_radius(quantity_tj: float | None) -> float:
    if quantity_tj is None:
        return 6.5
    return min(16.0, 7.0 + (quantity_tj / 75))


def _facility_color(kind: MapView) -> str:
    if kind == "Storage":
        return "#7553a4"
    return "#24775d"


def _route_label_coordinate(coordinates: Sequence[GeoCoordinate]) -> GeoCoordinate:
    middle = len(coordinates) // 2
    if len(coordinates) % 2 == 1:
        return coordinates[middle]
    previous = coordinates[middle - 1]
    current = coordinates[middle]
    return ((previous[0] + current[0]) / 2, (previous[1] + current[1]) / 2)


def _label_coordinate(coordinate: GeoCoordinate) -> GeoCoordinate:
    return (coordinate[0] + 0.26, coordinate[1] + 0.26)


def _pipeline_tooltip(record: PipelineMapRecord) -> str:
    return (
        f"{record.code} - {record.name}: "
        f"flow {_format_number(record.flow_tj)} TJ/d, "
        f"capacity {_format_number(record.capacity_tj)} TJ/d"
    )


def _facility_tooltip(record: FacilityMapRecord) -> str:
    return f"{record.label}: {record.measure} {_format_number(record.quantity_tj)} TJ/d"


def _pipeline_hover_template(record: PipelineMapRecord) -> str:
    direction = record.direction or "unknown"
    return (
        f"<b>{escape(record.code)} - {escape(record.name)}</b><br>"
        f"Operator: {escape(record.operator)}<br>"
        f"Flow: {_format_number(record.flow_tj)} TJ/d<br>"
        f"Capacity: {_format_number(record.capacity_tj)} TJ/d<br>"
        f"Utilisation: {_format_number(record.utilisation_pct)}%<br>"
        f"Direction: {escape(direction)}<br>"
        f"Status: {escape(record.status)}"
        "<extra></extra>"
    )


def _facility_hover_template(record: FacilityMapRecord) -> str:
    return (
        f"<b>{escape(record.label)}</b><br>"
        f"Type: {escape(record.kind)}<br>"
        f"Measure: {escape(record.measure)}<br>"
        f"Quantity: {_format_number(record.quantity_tj)} TJ/d<br>"
        f"Status: {escape(record.status)}"
        "<extra></extra>"
    )


def _plotly_legend_markup() -> str:
    return """
    <div class="gbb-map-legend" aria-label="Map legend">
      <strong>GBB map</strong>
      <div class="gbb-map-legend-item">
        <span class="gbb-map-legend-line" style="background: #24775d;"></span>
        <span>flow under 70%</span>
      </div>
      <div class="gbb-map-legend-item">
        <span class="gbb-map-legend-line" style="background: #b37a24;"></span>
        <span>flow 70-90%</span>
      </div>
      <div class="gbb-map-legend-item">
        <span class="gbb-map-legend-line" style="background: #b44a36;"></span>
        <span>flow over 90%</span>
      </div>
      <div class="gbb-map-legend-item">
        <span class="gbb-map-legend-line" style="background: #8b9699;"></span>
        <span>no local data</span>
      </div>
      <div class="gbb-map-legend-item">
        <span class="gbb-map-legend-dot" style="background: #24775d;"></span>
        <span>production</span>
      </div>
      <div class="gbb-map-legend-item">
        <span class="gbb-map-legend-dot" style="background: #7553a4;"></span>
        <span>storage</span>
      </div>
    </div>
    """


def _map_stats_markup(model: GbbMapModel) -> str:
    pipeline_count = len(model.pipelines)
    flow_count = sum(record.flow_tj is not None for record in model.pipelines)
    capacity_count = sum(record.capacity_tj is not None for record in model.pipelines)
    facility_count = sum(record.quantity_tj is not None for record in model.facilities)
    error_count = len(model.load_errors)
    facility_value = (
        f"{facility_count}/{len(model.facilities)}"
        if error_count == 0
        else f"{error_count} input errors"
    )
    return f"""
    <div class="gbb-stat-grid" aria-label="Map data summary">
      {_stat_markup("Pipelines", str(pipeline_count))}
      {_stat_markup("Live flow", f"{flow_count}/{pipeline_count}")}
      {_stat_markup("Capacity", f"{capacity_count}/{pipeline_count}")}
      {_stat_markup("Facilities", facility_value)}
    </div>
    """


def _stat_markup(label: str, value: str) -> str:
    return f"""
      <div class="gbb-stat">
        <div class="gbb-stat-label">{escape(label)}</div>
        <div class="gbb-stat-value">{escape(value)}</div>
      </div>
    """


def _side_summary(model: GbbMapModel, active_view: MapView) -> str:
    if active_view == "Production":
        records = [record for record in model.facilities if record.kind == "Production"]
        items = "".join(_facility_summary_item(record) for record in records)
        return f"<h3>Production</h3>{items}"
    if active_view == "Storage":
        records = [record for record in model.facilities if record.kind == "Storage"]
        items = "".join(_facility_summary_item(record) for record in records)
        return f"<h3>Storage</h3>{items}"

    records = sorted(
        model.pipelines,
        key=lambda record: (record.flow_tj is None, -(record.flow_tj or 0.0)),
    )
    items = "".join(_pipeline_summary_item(record) for record in records)
    return f"<h3>Pipeline flow and capacity</h3>{items}"


def _pipeline_summary_item(record: PipelineMapRecord) -> str:
    flow = _format_number(record.flow_tj)
    capacity = _format_number(record.capacity_tj)
    utilisation = _format_number(record.utilisation_pct)
    direction = record.direction or "unknown"
    meter_width = (
        "0" if record.utilisation_pct is None else str(min(record.utilisation_pct, 100))
    )
    status_class = _status_class(record.status)
    return f"""
      <div class="gbb-summary-item">
        <div class="gbb-summary-name">{escape(record.code)} - {escape(record.name)}</div>
        <div class="gbb-summary-meta">
          {escape(record.operator)}<br>
          flow {flow} TJ/d; capacity {capacity} TJ/d; utilisation {utilisation}%;
          direction {escape(direction)}.
        </div>
        <div class="gbb-meter" aria-label="Utilisation">
          <div class="gbb-meter-fill" style="width: {escape(meter_width)}%;"></div>
        </div>
        <span class="gbb-status-pill {status_class}">{escape(record.status)}</span>
      </div>
    """


def _facility_summary_item(record: FacilityMapRecord) -> str:
    quantity = _format_number(record.quantity_tj)
    status_class = _status_class(record.status)
    return f"""
      <div class="gbb-summary-item">
        <div class="gbb-summary-name">{escape(record.label)}</div>
        <div class="gbb-summary-meta">
          {escape(record.measure)} {quantity} TJ/d.
        </div>
        <span class="gbb-status-pill {status_class}">{escape(record.status)}</span>
      </div>
    """


def _load_errors_markup(errors: Sequence[str]) -> str:
    if not errors:
        return ""
    items = "".join(f"<li>{escape(error)}</li>" for error in errors)
    count = len(errors)
    return f"""
    <div class="gbb-data-notice">
      <details>
        <summary>Local map inputs unavailable ({count}); showing static topology.</summary>
        <ul>{items}</ul>
      </details>
    </div>
    """


def _status_class(status: str) -> str:
    if status == "Flow and capacity" or status == "Available":
        return "gbb-status-good"
    if status == "No local data":
        return "gbb-status-empty"
    return "gbb-status-partial"


def _record_color(utilisation_pct: float | None, flow_tj: float | None) -> str:
    if flow_tj is None:
        return "muted"
    if utilisation_pct is None:
        return "blue"
    if utilisation_pct >= 90:
        return "red"
    if utilisation_pct >= 70:
        return "amber"
    return "green"


def _map_color(color: str) -> str:
    colors = {
        "blue": "#156d93",
        "green": "#24775d",
        "amber": "#b37a24",
        "red": "#b44a36",
        "muted": "#8b9699",
    }
    return colors[color]


def _format_number(value: float | None) -> str:
    if value is None:
        return "-"
    if value == round(value):
        return str(int(value))
    return f"{value:.1f}"


def _compact_error(error: Exception) -> str:
    message = str(error).strip().splitlines()
    if not message:
        return error.__class__.__name__
    if "Generic S3 error" in message[0]:
        return (
            f"{error.__class__.__name__}: S3 read failed; LocalStack may be "
            "unreachable or the table prefix is missing"
        )
    return f"{error.__class__.__name__}: {message[0]}"
