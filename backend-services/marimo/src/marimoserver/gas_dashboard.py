"""Helpers for the gas market overview marimo dashboard."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from html import escape
import os

import polars as pl

from marimoserver.dashboard_registry import (
    DashboardRegistryEntry,
    DashboardRegistryError,
    dashboard_registry,
    registry_entry_by_concept_id,
)
from marimoserver.gas_model_loader import (
    SILVER_GAS_MODEL_PREFIX as SILVER_GAS_MODEL_PREFIX,
    GasModelReadRequest,
    GasModelTableView,
    TableReader,
    load_gas_model_read_requests,
    read_parquet_table as read_parquet_table,
)

DEFAULT_NAME_PREFIX = "energy-market"
DEFAULT_DEVELOPMENT_ENVIRONMENT = "dev"
DEFAULT_AWS_ENDPOINT_URL = "http://localstack:4566"
DEFAULT_AWS_REGION = "ap-southeast-4"
DEFAULT_AWS_ACCESS_KEY_ID = "test"
DEFAULT_AWS_SECRET_ACCESS_KEY = "test"
DEFAULT_AWS_ALLOW_HTTP = "true"
DEFAULT_AWS_PREVIEW_ROWS = 100
AWS_DEVELOPMENT_LOCATION = "aws"
DEFAULT_RELATED_CONTEXT_LIMIT = 6


@dataclass(frozen=True)
class GasDashboardConfig:
    """Environment-derived settings used to read gas model Parquet tables."""

    runtime_location: str
    development_environment: str
    name_prefix: str
    aemo_bucket: str
    aws_endpoint_url: str | None
    aws_region: str
    aws_access_key_id: str | None
    aws_secret_access_key: str | None
    aws_allow_http: str
    max_preview_rows: int
    full_table_scan_enabled: bool

    @property
    def aws_runtime(self) -> bool:
        """Return whether the dashboard is running in AWS deployment mode."""
        return self.runtime_location == AWS_DEVELOPMENT_LOCATION

    def table_uri(self, table_name: str) -> str:
        """Return the Parquet dataset URI for a silver gas_model table."""
        return f"s3://{self.aemo_bucket}/{SILVER_GAS_MODEL_PREFIX}/{table_name}"

    def storage_options(self) -> dict[str, str]:
        """Return Polars S3 storage options for the configured endpoint."""
        options = {
            "AWS_REGION": self.aws_region,
            "AWS_ALLOW_HTTP": self.aws_allow_http,
            "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
        }
        if self.aws_endpoint_url is not None:
            options["AWS_ENDPOINT_URL"] = self.aws_endpoint_url
        if self.aws_access_key_id is not None:
            options["AWS_ACCESS_KEY_ID"] = self.aws_access_key_id
        if self.aws_secret_access_key is not None:
            options["AWS_SECRET_ACCESS_KEY"] = self.aws_secret_access_key
        return options


@dataclass(frozen=True)
class GasTableSpec:
    """A gas_model output table included in the dashboard."""

    section: str
    label: str
    table_name: str
    date_columns: tuple[str, ...] = ()
    preview_columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class GasTableLoad:
    """Loaded DataFrame or professional unavailable-state detail for one table."""

    spec: GasTableSpec
    uri: str
    dataframe: pl.DataFrame | None
    error: str | None
    row_limit: int | None

    @property
    def available(self) -> bool:
        """Return whether the table loaded and contains at least one row."""
        return self.dataframe is not None and not self.dataframe.is_empty()

    @property
    def is_limited(self) -> bool:
        """Return whether the runtime applied a bounded preview row limit."""
        return self.row_limit is not None


GAS_MODEL_TABLES: tuple[GasTableSpec, ...] = (
    GasTableSpec(
        section="Prices",
        label="Market prices",
        table_name="silver_gas_fact_market_price",
        date_columns=("gas_date",),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_table",
            "price_type",
            "schedule_type_id",
            "source_location_id",
            "price_value_gst_ex",
            "weighted_average_price_gst_ex",
            "cumulative_price",
            "administered_price",
        ),
    ),
    GasTableSpec(
        section="Schedules",
        label="Schedule runs",
        table_name="silver_gas_fact_schedule_run",
        date_columns=("gas_date", "creation_timestamp", "approval_timestamp"),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_table",
            "schedule_type_id",
            "transmission_id",
            "forecast_demand_version",
            "approval_timestamp",
        ),
    ),
    GasTableSpec(
        section="Schedules",
        label="Scheduled quantities",
        table_name="silver_gas_fact_scheduled_quantity",
        date_columns=("gas_date",),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_table",
            "quantity_type",
            "schedule_type_id",
            "source_point_id",
            "quantity_gj",
            "amount_gst_ex",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Connection point flow",
        table_name="silver_gas_fact_connection_point_flow",
        date_columns=("gas_date",),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_facility_id",
            "source_connection_point_id",
            "flow_direction",
            "actual_quantity_tj",
            "quality",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Facility flow and storage",
        table_name="silver_gas_fact_facility_flow_storage",
        date_columns=("gas_date",),
        preview_columns=(
            "gas_date",
            "source_system",
            "source_facility_id",
            "source_location_id",
            "demand_tj",
            "supply_tj",
            "held_in_storage_tj",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Linepack",
        table_name="silver_gas_fact_linepack",
        date_columns=("gas_date", "observation_timestamp"),
        preview_columns=(
            "gas_date",
            "observation_timestamp",
            "source_system",
            "source_table",
            "source_facility_id",
            "actual_linepack_gj",
            "adequacy_flag",
            "adequacy_description",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Capacity outlook",
        table_name="silver_gas_fact_capacity_outlook",
        date_columns=("from_gas_date", "to_gas_date"),
        preview_columns=(
            "from_gas_date",
            "to_gas_date",
            "source_system",
            "source_table",
            "source_facility_id",
            "facility_name",
            "capacity_type",
            "flow_direction",
            "capacity_quantity_tj",
        ),
    ),
    GasTableSpec(
        section="Flow and capacity",
        label="Capacity auction",
        table_name="silver_gas_fact_capacity_auction",
        date_columns=("auction_date", "start_date", "end_date"),
        preview_columns=(
            "auction_date",
            "source_system",
            "source_table",
            "auction_id",
            "zone_name",
            "auction_metric",
            "quantity_gj",
            "price",
        ),
    ),
)


def discover_dashboard_config(
    environ: Mapping[str, str] | None = None,
) -> GasDashboardConfig:
    """Discover dashboard settings from the Marimo service environment."""
    settings = os.environ if environ is None else environ
    runtime_location = _setting(settings, "DEVELOPMENT_LOCATION", "local").lower()
    aws_runtime = runtime_location == AWS_DEVELOPMENT_LOCATION
    name_prefix = _setting(settings, "NAME_PREFIX", DEFAULT_NAME_PREFIX)
    development_environment = _setting(
        settings,
        "DEVELOPMENT_ENVIRONMENT",
        DEFAULT_DEVELOPMENT_ENVIRONMENT,
    ).lower()
    aemo_bucket = _setting(
        settings,
        "AEMO_BUCKET",
        f"{development_environment}-{name_prefix}-aemo",
    )

    return GasDashboardConfig(
        runtime_location=runtime_location,
        development_environment=development_environment,
        name_prefix=name_prefix,
        aemo_bucket=aemo_bucket,
        aws_endpoint_url=_optional_setting(
            settings,
            "AWS_ENDPOINT_URL",
            None if aws_runtime else DEFAULT_AWS_ENDPOINT_URL,
        ),
        aws_region=_setting(settings, "AWS_DEFAULT_REGION", DEFAULT_AWS_REGION),
        aws_access_key_id=_optional_setting(
            settings,
            "AWS_ACCESS_KEY_ID",
            None if aws_runtime else DEFAULT_AWS_ACCESS_KEY_ID,
        ),
        aws_secret_access_key=_optional_setting(
            settings,
            "AWS_SECRET_ACCESS_KEY",
            None if aws_runtime else DEFAULT_AWS_SECRET_ACCESS_KEY,
        ),
        aws_allow_http=_setting(
            settings,
            "AWS_ALLOW_HTTP",
            "false" if aws_runtime else DEFAULT_AWS_ALLOW_HTTP,
        ),
        max_preview_rows=_positive_int_setting(
            settings,
            "MARIMO_MAX_PREVIEW_ROWS",
            DEFAULT_AWS_PREVIEW_ROWS,
        ),
        full_table_scan_enabled=_bool_setting(
            settings,
            "MARIMO_FULL_TABLE_SCAN_ENABLED",
            not aws_runtime,
        ),
    )


def load_gas_model_tables(
    config: GasDashboardConfig,
    specs: Sequence[GasTableSpec] = GAS_MODEL_TABLES,
    reader: TableReader = read_parquet_table,
    view: GasModelTableView = GasModelTableView.SAMPLE,
) -> list[GasTableLoad]:
    """Load configured gas_model tables, returning unavailable entries on errors."""
    requests = tuple(
        GasModelReadRequest(
            table_name=spec.table_name,
            view=view,
            date_columns=spec.date_columns,
        )
        for spec in specs
    )
    shared_loads = load_gas_model_read_requests(config, requests, reader=reader)

    return [
        GasTableLoad(
            spec=spec,
            uri=shared_load.uri,
            dataframe=shared_load.dataframe,
            error=shared_load.error,
            row_limit=shared_load.row_limit,
        )
        for spec, shared_load in zip(specs, shared_loads, strict=True)
    ]


def table_load_by_name(
    loads: Sequence[GasTableLoad],
    table_name: str,
) -> GasTableLoad | None:
    """Return a loaded table entry by gas_model table name."""
    for load in loads:
        if load.spec.table_name == table_name:
            return load
    return None


def render_dashboard_context_panel(
    concept_id: str,
    entries: Sequence[DashboardRegistryEntry] | None = None,
    related_limit: int = DEFAULT_RELATED_CONTEXT_LIMIT,
) -> str:
    """Render a cited Market context panel from the Marimo dashboard registry."""
    candidate_entries = dashboard_registry() if entries is None else entries
    entry = registry_entry_by_concept_id(concept_id, candidate_entries)
    if entry is None:
        raise DashboardRegistryError(
            f"dashboard context panel concept not found: {concept_id}"
        )

    related_entries = _related_context_entries(
        entry,
        candidate_entries,
        related_limit,
    )
    notebook_name = entry.notebook_name or ""
    notebook_route = entry.notebook_route or ""

    return f"""\
<style>
{_dashboard_context_panel_css()}
</style>
<section
    class="dashboard-context-panel"
    aria-labelledby="dashboard-context-title-{escape(entry.concept_id, quote=True)}"
    data-concept-id="{escape(entry.concept_id, quote=True)}"
    data-status="{escape(entry.status.value, quote=True)}"
    data-notebook-name="{escape(notebook_name, quote=True)}"
    data-notebook-route="{escape(notebook_route, quote=True)}"
>
    <div class="context-panel__header">
        <p class="context-panel__eyebrow">Market context</p>
        <h2 id="dashboard-context-title-{escape(entry.concept_id, quote=True)}">
            {escape(entry.title)}
        </h2>
        <p>{escape(entry.description)}</p>
    </div>
    <dl class="context-panel__metadata" aria-label="Dashboard usage metadata">
        {_definition_item("Concept ID", entry.concept_id)}
        {_definition_item("Status", entry.status.value)}
        {_definition_item("Audiences", ", ".join(audience.value for audience in entry.audiences))}
        {_definition_item("Notebook", notebook_name or "No notebook recorded")}
        {_definition_item("Route", notebook_route or "No notebook route recorded")}
    </dl>
    <div class="context-panel__grid">
        {_render_context_list("generated-gold paths", entry.generated_gold_paths)}
        {_render_context_list("source chunk IDs", entry.source_chunk_ids)}
        {_render_context_list("backing assets", entry.backing_assets)}
        {_render_related_context_list(related_entries)}
    </div>
</section>"""


def _related_context_entries(
    entry: DashboardRegistryEntry,
    entries: Sequence[DashboardRegistryEntry],
    limit: int,
) -> tuple[DashboardRegistryEntry, ...]:
    if limit <= 0:
        return ()

    scored_entries: list[tuple[int, str, DashboardRegistryEntry]] = []
    entry_gold_paths = set(entry.generated_gold_paths)
    entry_source_chunks = set(entry.source_chunk_ids)
    entry_assets = set(entry.backing_assets)

    for candidate in entries:
        if candidate.concept_id == entry.concept_id:
            continue

        score = (
            len(entry_gold_paths & set(candidate.generated_gold_paths)) * 3
            + len(entry_assets & set(candidate.backing_assets)) * 2
            + len(entry_source_chunks & set(candidate.source_chunk_ids))
        )
        if score == 0:
            continue
        scored_entries.append((score, candidate.title, candidate))

    return tuple(
        candidate
        for _, _, candidate in sorted(
            scored_entries,
            key=lambda scored_entry: (-scored_entry[0], scored_entry[1]),
        )[:limit]
    )


def _definition_item(label: str, value: str) -> str:
    return f"""\
        <div>
            <dt>{escape(label)}</dt>
            <dd>{escape(value)}</dd>
        </div>"""


def _render_context_list(title: str, values: Sequence[str]) -> str:
    if len(values) == 0:
        body = (
            '<p class="context-panel__empty">'
            f"No {escape(title)} recorded in the Marimo registry."
            "</p>"
        )
    else:
        body = "\n".join(
            f"                <li><code>{escape(value)}</code></li>" for value in values
        )
        body = f"<ul>\n{body}\n            </ul>"

    return f"""\
        <section class="context-panel__section">
            <h3>{escape(title)}</h3>
            {body}
        </section>"""


def _render_related_context_list(
    related_entries: Sequence[DashboardRegistryEntry],
) -> str:
    if len(related_entries) == 0:
        body = (
            '<p class="context-panel__empty">'
            "No related concepts share generated-gold paths, source chunk IDs, "
            "or backing assets in the Marimo registry."
            "</p>"
        )
    else:
        rows = "\n".join(
            f"""\
                <li>
                    <span>{escape(entry.title)}</span>
                    <code>{escape(entry.concept_id)}</code>
                </li>"""
            for entry in related_entries
        )
        body = f"<ul>\n{rows}\n            </ul>"

    return f"""\
        <section class="context-panel__section">
            <h3>related concepts</h3>
            {body}
        </section>"""


def _dashboard_context_panel_css() -> str:
    return """\
.dashboard-context-panel {
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    padding: 1rem;
    background: var(--emdl-panel, #ffffff);
    color: var(--emdl-ink, #1b2324);
}

.context-panel__header {
    display: grid;
    gap: 0.35rem;
    margin-bottom: 0.9rem;
}

.context-panel__eyebrow {
    margin: 0;
    color: var(--emdl-green, #3e7a54);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0;
    text-transform: uppercase;
}

.context-panel__header h2,
.context-panel__section h3 {
    margin: 0;
    color: var(--emdl-slate, #354348);
}

.context-panel__header h2 {
    font-size: 1.25rem;
}

.context-panel__header p,
.context-panel__empty {
    margin: 0;
    color: var(--emdl-muted, #566365);
}

.context-panel__metadata {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(10rem, 1fr));
    gap: 0.7rem;
    margin-bottom: 1rem;
}

.context-panel__metadata div {
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 6px;
    padding: 0.55rem 0.65rem;
    background: var(--emdl-service-band, #eef4f1);
}

.context-panel__metadata dt {
    color: var(--emdl-muted, #566365);
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
}

.context-panel__metadata dd {
    margin: 0.2rem 0 0;
    overflow-wrap: anywhere;
}

.context-panel__grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
    gap: 0.85rem;
}

.context-panel__section {
    min-width: 0;
}

.context-panel__section h3 {
    margin-bottom: 0.4rem;
    font-size: 0.95rem;
    text-transform: capitalize;
}

.context-panel__section ul {
    display: grid;
    gap: 0.35rem;
    margin: 0;
    padding: 0;
    list-style: none;
}

.context-panel__section li {
    display: grid;
    gap: 0.2rem;
    min-width: 0;
    border-left: 3px solid var(--emdl-blue, #166791);
    padding: 0.35rem 0 0.35rem 0.55rem;
    background: rgb(var(--emdl-line-rgb, 207 219 214) / 0.24);
}

.context-panel__section code {
    white-space: normal;
    overflow-wrap: anywhere;
}"""


def _setting(environ: Mapping[str, str], name: str, default: str) -> str:
    value = environ.get(name, default).strip()
    if value == "":
        return default
    return value


def _optional_setting(
    environ: Mapping[str, str],
    name: str,
    default: str | None,
) -> str | None:
    value = environ.get(name)
    if value is None:
        return default
    stripped = value.strip()
    if stripped == "":
        return default
    return stripped


def _positive_int_setting(
    environ: Mapping[str, str],
    name: str,
    default: int,
) -> int:
    value = environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(1, parsed)


def _bool_setting(environ: Mapping[str, str], name: str, default: bool) -> bool:
    value = environ.get(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
