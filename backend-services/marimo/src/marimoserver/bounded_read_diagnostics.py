"""Helpers for the AWS bounded-read diagnostics Marimo dashboard."""

from collections.abc import Sequence
from dataclasses import replace
from html import escape

import polars as pl

from marimoserver.dashboard_registry import (
    DashboardRegistryEntry,
    DashboardStatus,
    dashboard_registry,
)
from marimoserver.gas_dashboard import (
    GAS_MODEL_TABLES,
    GasDashboardConfig,
    facility_table_specs,
    gas_day_table_specs,
    source_coverage_table_specs,
)
from marimoserver.gas_model_loader import (
    bounded_row_limit,
    format_row_limit,
    row_limit_message,
)
from marimoserver.gbb_interactive_map import GBB_MAP_TABLES
from marimoserver.table_explorer import (
    DEFAULT_DISCOVERY_OBJECT_LIMIT,
    TableExplorerConfig,
)

_RECENT_GAS_DASHBOARD_IDS = frozenset(
    {
        "gas-market-prices",
        "gas-schedule-runs",
        "settlement-context",
        "gas-customer-transfer-activity",
        "bid-offer-context",
        "gas-system-notices",
        "gas-quality-composition",
    }
)


def bounded_read_runtime_frame(
    gas_config: GasDashboardConfig,
    table_config: TableExplorerConfig,
) -> pl.DataFrame:
    """Return runtime bounded-read settings for dashboard display."""
    table_row_limit = bounded_row_limit(table_config)
    gas_row_limit = bounded_row_limit(gas_config)
    return pl.DataFrame(
        [
            {
                "setting": "Runtime location",
                "value": table_config.runtime_location,
                "detail": "DEVELOPMENT_LOCATION",
            },
            {
                "setting": "Endpoint mode",
                "value": endpoint_mode_label(table_config),
                "detail": endpoint_mode_detail(table_config),
            },
            {
                "setting": "AWS region",
                "value": table_config.aws_region,
                "detail": "AWS_DEFAULT_REGION",
            },
            {
                "setting": "Configured buckets",
                "value": _join_values(table_config.default_buckets),
                "detail": "MARIMO_TABLE_BUCKETS or AWS bucket fallbacks",
            },
            {
                "setting": "Gas model AEMO bucket",
                "value": gas_config.aemo_bucket,
                "detail": "AEMO_BUCKET",
            },
            {
                "setting": "Table preview row cap",
                "value": f"{table_config.max_preview_rows:,}",
                "detail": "MARIMO_MAX_PREVIEW_ROWS for table explorer reads",
            },
            {
                "setting": "Gas dashboard preview row cap",
                "value": f"{gas_config.max_preview_rows:,}",
                "detail": "MARIMO_MAX_PREVIEW_ROWS for gas_model helpers",
            },
            {
                "setting": "Full-table-scan flag",
                "value": str(table_config.full_table_scan_enabled),
                "detail": "MARIMO_FULL_TABLE_SCAN_ENABLED",
            },
            {
                "setting": "Active table explorer policy",
                "value": format_row_limit(table_row_limit),
                "detail": row_limit_message(table_row_limit),
            },
            {
                "setting": "Active gas dashboard policy",
                "value": format_row_limit(gas_row_limit),
                "detail": row_limit_message(gas_row_limit),
            },
        ]
    )


def bounded_read_state_frame(
    gas_config: GasDashboardConfig,
    table_config: TableExplorerConfig,
) -> pl.DataFrame:
    """Return operator-facing bounded-read state explanations."""
    table_row_limit = bounded_row_limit(table_config)
    source_coverage_row_limit = bounded_row_limit(
        replace(gas_config, full_table_scan_enabled=False)
    )
    return pl.DataFrame(
        [
            {
                "state": "Bounded preview",
                "active": str(table_row_limit is not None),
                "meaning": (
                    "Table row previews stop at the configured cap and may be "
                    "sampled or recent-only."
                ),
            },
            {
                "state": "Full table scan",
                "active": str(table_row_limit is None),
                "meaning": (
                    "Full table reads are allowed by the runtime flag; dashboards "
                    "that force bounded reads still keep their own cap."
                ),
            },
            {
                "state": "Forced source coverage cap",
                "active": "True",
                "meaning": (
                    "Source coverage reads stay capped at "
                    f"{format_row_limit(source_coverage_row_limit)}."
                ),
            },
            {
                "state": "Configured bucket boundary",
                "active": str(len(table_config.default_buckets) > 0),
                "meaning": (
                    "AWS mode reads only configured buckets instead of listing "
                    "the whole account."
                ),
            },
            {
                "state": "Read-only diagnostic",
                "active": "True",
                "meaning": (
                    "This dashboard renders environment and registry metadata; "
                    "it does not write data or schedule auto-refresh."
                ),
            },
        ]
    )


def dashboard_read_behavior_frame(
    gas_config: GasDashboardConfig,
    table_config: TableExplorerConfig,
    entries: Sequence[DashboardRegistryEntry] | None = None,
) -> pl.DataFrame:
    """Return per-dashboard bounded-read behavior for available dashboards."""
    candidate_entries = dashboard_registry() if entries is None else entries
    rows = [
        _dashboard_read_behavior_row(entry, gas_config, table_config)
        for entry in candidate_entries
        if entry.status is DashboardStatus.AVAILABLE
    ]
    return pl.DataFrame(rows)


def render_bounded_read_summary_cards(
    gas_config: GasDashboardConfig,
    table_config: TableExplorerConfig,
) -> str:
    """Render first-viewport bounded-read diagnostic cards."""
    table_row_limit = bounded_row_limit(table_config)
    cards = (
        (
            "Runtime",
            table_config.runtime_location,
            "AWS mode applies the deployed bounded-read policy."
            if table_config.aws_runtime
            else "Local mode keeps full scans enabled unless overridden.",
        ),
        (
            "Endpoint mode",
            endpoint_mode_label(table_config),
            endpoint_mode_detail(table_config),
        ),
        (
            "Table preview",
            format_row_limit(table_row_limit),
            row_limit_message(table_row_limit),
        ),
        (
            "Buckets",
            str(len(table_config.default_buckets)),
            _join_values(table_config.default_buckets),
        ),
        (
            "Gas bucket",
            gas_config.aemo_bucket,
            "silver.gas_model table helpers read this configured AEMO bucket.",
        ),
    )
    items = "\n".join(
        f"""
        <article class="bounded-read-card">
            <span class="bounded-read-card__label">{escape(label)}</span>
            <strong>{escape(value)}</strong>
            <span>{escape(detail)}</span>
        </article>
        """
        for label, value, detail in cards
    )
    return f"""
{_bounded_read_summary_css()}
<section class="bounded-read-card-grid" aria-label="Bounded-read runtime summary">
    {items}
</section>
"""


def endpoint_mode_label(config: TableExplorerConfig) -> str:
    """Return the configured S3 endpoint mode label."""
    if config.aws_endpoint_url is None:
        return "AWS service endpoints"
    return "S3-compatible endpoint override"


def endpoint_mode_detail(config: TableExplorerConfig) -> str:
    """Return endpoint detail suitable for diagnostics display."""
    if config.aws_endpoint_url is None:
        return "Using AWS SDK default service endpoints and runtime credentials."
    return f"Using configured endpoint {config.aws_endpoint_url}."


def _dashboard_read_behavior_row(
    entry: DashboardRegistryEntry,
    gas_config: GasDashboardConfig,
    table_config: TableExplorerConfig,
) -> dict[str, str]:
    concept_id = entry.concept_id
    route = entry.notebook_route or ""

    if concept_id == "aws-bounded-read-diagnostics":
        return _row(
            entry,
            route,
            "Configuration and registry metadata only",
            "No table rows read",
            "No table-row reads",
            "Environment settings and registry entries",
        )
    if concept_id in {
        "citation-chain-explorer",
        "concept-to-asset-explorer",
        "glossary-explorer",
    }:
        return _row(
            entry,
            route,
            "Registry metadata browser",
            "No table rows read",
            "No table-row reads",
            "Marimo dashboard registry metadata",
        )
    if concept_id == "s3-bucket-health":
        return _row(
            entry,
            route,
            "Configured bucket object discovery",
            "Object listing",
            f"{DEFAULT_DISCOVERY_OBJECT_LIMIT:,} objects per bucket",
            "Configured S3-compatible buckets",
        )
    if concept_id in {"data-readiness-overview", "dagster-asset-catalogue-status"}:
        return _row(
            entry,
            route,
            "Storage and Dagster metadata diagnostics",
            "No table rows previewed",
            "No table-row reads",
            "Configured buckets and Dagster GraphQL metadata",
        )
    if concept_id == "gas-model-table-explorer":
        return _row(
            entry,
            route,
            "Operator-selected live table preview",
            "Selected table sample",
            format_row_limit(bounded_row_limit(table_config)),
            "Configured table buckets",
        )
    if concept_id in {
        "source-coverage-matrix",
        "source-table-lineage-explorer",
        "gas-day-context",
        "facility-context",
    }:
        return _forced_bounded_registry_row(entry, route, gas_config)
    if concept_id == "gas-market-overview":
        return _row(
            entry,
            route,
            "Gas market overview table previews",
            "Bounded sample",
            format_row_limit(bounded_row_limit(gas_config)),
            f"{len(GAS_MODEL_TABLES)} gas_model overview tables",
        )
    if concept_id == "gbb-interactive-map":
        return _row(
            entry,
            route,
            "Map input table previews",
            "Bounded sample",
            format_row_limit(bounded_row_limit(gas_config)),
            f"{len(GBB_MAP_TABLES)} gas_model map input tables",
        )
    if concept_id in _RECENT_GAS_DASHBOARD_IDS:
        return _row(
            entry,
            route,
            "Focused gas_model dashboard table read",
            "Recent-only bounded view",
            format_row_limit(bounded_row_limit(gas_config)),
            _join_values(entry.backing_assets),
        )

    return _row(
        entry,
        route,
        "Dashboard-specific read behavior",
        "See dashboard",
        format_row_limit(bounded_row_limit(gas_config)),
        _join_values(entry.backing_assets),
    )


def _forced_bounded_registry_row(
    entry: DashboardRegistryEntry,
    route: str,
    gas_config: GasDashboardConfig,
) -> dict[str, str]:
    if entry.concept_id == "gas-day-context":
        read_behavior = "Registry-backed Gas Day date-field inspection"
        scope = f"{len(gas_day_table_specs())} registry-backed gas_model tables"
    elif entry.concept_id == "facility-context":
        read_behavior = "Registry-backed Facility relationship inspection"
        scope = f"{len(facility_table_specs())} facility-oriented gas_model tables"
    else:
        read_behavior = "Registry-backed source metadata inspection"
        scope = f"{len(source_coverage_table_specs())} registry-backed gas_model tables"

    return _row(
        entry,
        route,
        read_behavior,
        "Forced bounded sample",
        format_row_limit(
            bounded_row_limit(replace(gas_config, full_table_scan_enabled=False))
        ),
        scope,
    )


def _row(
    entry: DashboardRegistryEntry,
    route: str,
    read_behavior: str,
    view: str,
    row_policy: str,
    scope: str,
) -> dict[str, str]:
    return {
        "dashboard": entry.title,
        "route": route,
        "audience": ", ".join(audience.value for audience in entry.audiences),
        "read behavior": read_behavior,
        "view": view,
        "row policy": row_policy,
        "scope": scope,
        "side effects": "Read-only",
    }


def _join_values(values: Sequence[str]) -> str:
    if len(values) == 0:
        return "(none configured)"
    return ", ".join(values)


def _bounded_read_summary_css() -> str:
    return """
<style>
.bounded-read-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 210px), 1fr));
    gap: 12px;
    margin: 0 0 18px;
}

.bounded-read-card {
    display: grid;
    gap: 6px;
    min-height: 132px;
    padding: 14px;
    border: 1px solid var(--emdl-line, #cfdbd6);
    border-radius: 8px;
    background: var(--emdl-panel, #ffffff);
    box-shadow: var(--emdl-soft-shadow, 0 8px 28px rgb(27 35 36 / 0.08));
}

.bounded-read-card__label {
    color: var(--emdl-green, #3e7a54);
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
}

.bounded-read-card strong {
    color: var(--emdl-slate, #354348);
    font-size: 1.05rem;
    line-height: 1.2;
}

.bounded-read-card span:last-child {
    color: var(--emdl-muted, #566365);
    font-size: 0.9rem;
}
</style>
"""
