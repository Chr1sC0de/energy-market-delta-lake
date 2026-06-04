"""Data readiness overview helpers for the Marimo platform dashboard."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

import polars as pl

from marimoserver.dagster_graphql import DagsterAssetCatalogue
from marimoserver.gas_dashboard import DashboardStatusCard, render_status_cards_html
from marimoserver.gas_model_loader import bounded_row_limit
from marimoserver.table_explorer import (
    CataloguedTable,
    StorageDiscovery,
    TableAvailability,
    TableExplorerConfig,
    format_materialization_timestamp,
)


class ReadinessState(StrEnum):
    """Operator-facing readiness status for one dashboard surface."""

    READY = "Ready"
    ATTENTION = "Needs attention"
    EMPTY = "Empty"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True)
class ReadinessCard:
    """One high-signal readiness summary card."""

    area: str
    state: ReadinessState
    value: str
    detail: str
    action: str


@dataclass(frozen=True)
class DataReadinessOverview:
    """Computed data readiness overview for a Marimo dashboard render."""

    cards: tuple[ReadinessCard, ...]

    @property
    def action_items(self) -> tuple[str, ...]:
        """Return actionable follow-ups for degraded readiness surfaces."""
        return tuple(
            f"{card.area}: {card.action}"
            for card in self.cards
            if card.state is not ReadinessState.READY
        )


def build_data_readiness_overview(
    config: TableExplorerConfig,
    discovery: StorageDiscovery,
    catalogue: DagsterAssetCatalogue,
    table_catalogue: Sequence[CataloguedTable],
) -> DataReadinessOverview:
    """Build the first-stop data readiness summary from existing helper outputs."""
    return DataReadinessOverview(
        cards=(
            _s3_readiness_card(config, discovery),
            _table_catalogue_card(table_catalogue),
            _dagster_catalogue_card(catalogue),
            _bounded_read_card(config),
        )
    )


def bucket_readiness_frame(discovery: StorageDiscovery) -> pl.DataFrame:
    """Return configured bucket health rows with operator actions."""
    rows: list[dict[str, object]] = []
    for bucket in discovery.buckets:
        if bucket.error is not None:
            status = ReadinessState.UNAVAILABLE.value
            action = "Check bucket permission, endpoint reachability, and bucket name."
        elif bucket.object_count == 0:
            status = ReadinessState.EMPTY.value
            action = "Seed LocalStack or materialize data before expecting tables."
        else:
            status = ReadinessState.READY.value
            action = "No action."

        rows.append(
            {
                "bucket": bucket.name,
                "configured": bucket.is_default,
                "discovered": bucket.discovered,
                "status": status,
                "objects scanned": bucket.object_count,
                "table prefixes": bucket.table_count,
                "truncated": bucket.truncated,
                "detail": bucket.error or "",
                "action": action,
            }
        )

    if rows:
        return pl.DataFrame(rows)

    return pl.DataFrame(
        [
            {
                "bucket": "No configured buckets",
                "configured": False,
                "discovered": False,
                "status": ReadinessState.EMPTY.value,
                "objects scanned": 0,
                "table prefixes": 0,
                "truncated": False,
                "detail": discovery.bucket_listing_error or "",
                "action": (
                    "Configure MARIMO_TABLE_BUCKETS or the default bucket "
                    "environment, then refresh readiness."
                ),
            }
        ]
    )


def table_readiness_frame(
    table_catalogue: Sequence[CataloguedTable],
) -> pl.DataFrame:
    """Return table catalogue status counts with next actions."""
    counts = _table_status_counts(table_catalogue)
    rows = [
        {
            "status": status.value,
            "tables": counts[status],
            "action": _table_status_action(status),
        }
        for status in TableAvailability
        if counts[status] > 0
    ]

    if rows:
        return pl.DataFrame(rows)

    return pl.DataFrame(
        [
            {
                "status": ReadinessState.EMPTY.value,
                "tables": 0,
                "action": (
                    "No table assets or S3 table prefixes were found. "
                    "Materialize assets or seed LocalStack/AWS data, then refresh."
                ),
            }
        ]
    )


def dagster_materialization_frame(catalogue: DagsterAssetCatalogue) -> pl.DataFrame:
    """Return Dagster table asset materialization freshness rows."""
    if not catalogue.available:
        return pl.DataFrame(
            [
                {
                    "asset": "Dagster GraphQL unavailable",
                    "group": "",
                    "status": ReadinessState.UNAVAILABLE.value,
                    "latest materialization": "",
                    "uri": "",
                    "action": (
                        "Confirm DAGSTER_GRAPHQL_URL and Dagster webserver "
                        "health, then refresh readiness."
                    ),
                }
            ]
        )

    rows = [
        {
            "asset": asset.asset_id,
            "group": asset.group_name,
            "status": "Materialized"
            if asset.latest_materialization_timestamp is not None
            else "No materialization",
            "latest materialization": format_materialization_timestamp(
                asset.latest_materialization_timestamp
            ),
            "uri": asset.uri or "",
            "action": "No action."
            if asset.latest_materialization_timestamp is not None
            else "Materialize the asset before treating downstream data as ready.",
        }
        for asset in catalogue.assets
    ]

    if rows:
        return pl.DataFrame(rows)

    return pl.DataFrame(
        [
            {
                "asset": "No table assets returned",
                "group": "",
                "status": ReadinessState.EMPTY.value,
                "latest materialization": "",
                "uri": "",
                "action": (
                    "Confirm Dagster definitions expose table assets or run the "
                    "expected asset materializations."
                ),
            }
        ]
    )


def readiness_action_markdown(overview: DataReadinessOverview) -> str:
    """Return Markdown for the dashboard action callout."""
    if not overview.action_items:
        return "All readiness surfaces are reachable under the current configuration."
    return "\n".join(f"- {item}" for item in overview.action_items)


def render_readiness_cards(cards: Sequence[ReadinessCard]) -> str:
    """Render first-viewport readiness cards using repo theme tokens."""
    return render_status_cards_html(
        tuple(_readiness_status_card(card) for card in cards),
        title="Data readiness summary",
        grid_class="readiness-card-grid",
        card_class="readiness-card",
    )


def _s3_readiness_card(
    config: TableExplorerConfig,
    discovery: StorageDiscovery,
) -> ReadinessCard:
    bucket_count = len(discovery.buckets)
    reachable_count = sum(bucket.reachable for bucket in discovery.buckets)
    unreachable_count = bucket_count - reachable_count
    table_count = len(discovery.tables)
    object_count = sum(bucket.object_count for bucket in discovery.buckets)
    truncated_count = sum(bucket.truncated for bucket in discovery.buckets)

    if bucket_count == 0:
        return ReadinessCard(
            area="S3 buckets",
            state=ReadinessState.EMPTY,
            value="No buckets",
            detail="No configured buckets were checked.",
            action=(
                "Configure MARIMO_TABLE_BUCKETS or default bucket settings, "
                "then refresh readiness."
            ),
        )

    detail = (
        f"{table_count} table prefixes from {object_count} objects scanned "
        f"across {bucket_count} configured buckets."
    )
    if discovery.bucket_listing_error is not None:
        detail = f"{detail} Bucket listing detail: {discovery.bucket_listing_error}."

    if unreachable_count == bucket_count:
        return ReadinessCard(
            area="S3 buckets",
            state=ReadinessState.UNAVAILABLE,
            value=f"0/{bucket_count} reachable",
            detail=detail,
            action=(
                "Check LocalStack or AWS S3 endpoint reachability, credentials, "
                "and configured bucket names."
            ),
        )

    if table_count == 0:
        return ReadinessCard(
            area="S3 buckets",
            state=ReadinessState.EMPTY,
            value=f"{reachable_count}/{bucket_count} reachable",
            detail=detail,
            action=(
                "Seed LocalStack or materialize the expected Dagster assets "
                "before expecting table prefixes."
            ),
        )

    if unreachable_count > 0 or truncated_count > 0 or discovery.bucket_listing_error:
        return ReadinessCard(
            area="S3 buckets",
            state=ReadinessState.ATTENTION,
            value=f"{reachable_count}/{bucket_count} reachable",
            detail=detail,
            action=(
                "Review bucket-level details for denied, truncated, or partially "
                "listed buckets."
            ),
        )

    return ReadinessCard(
        area="S3 buckets",
        state=ReadinessState.READY,
        value=f"{reachable_count}/{bucket_count} reachable",
        detail=detail,
        action="No action.",
    )


def _table_catalogue_card(
    table_catalogue: Sequence[CataloguedTable],
) -> ReadinessCard:
    counts = _table_status_counts(table_catalogue)
    total_count = len(table_catalogue)
    live_count = counts[TableAvailability.LIVE]
    degraded_count = total_count - live_count
    detail = (
        f"{counts[TableAvailability.UNMATERIALIZED]} unmaterialized, "
        f"{counts[TableAvailability.MISSING]} missing, "
        f"{counts[TableAvailability.GRAPHQL_UNAVAILABLE]} storage-only while "
        "GraphQL is unavailable."
    )

    if total_count == 0:
        return ReadinessCard(
            area="Table catalogue",
            state=ReadinessState.EMPTY,
            value="No tables",
            detail="No Dagster table assets or S3 table prefixes were discovered.",
            action=(
                "Materialize assets or seed table prefixes, then refresh readiness."
            ),
        )

    if counts[TableAvailability.GRAPHQL_UNAVAILABLE] > 0:
        return ReadinessCard(
            area="Table catalogue",
            state=ReadinessState.ATTENTION,
            value=f"{live_count}/{total_count} live",
            detail=detail,
            action=(
                "Restore Dagster GraphQL to classify storage prefixes against "
                "the asset catalogue."
            ),
        )

    if live_count == 0:
        return ReadinessCard(
            area="Table catalogue",
            state=ReadinessState.ATTENTION,
            value=f"0/{total_count} live",
            detail=detail,
            action="Materialize the listed assets before treating data as ready.",
        )

    if degraded_count > 0:
        return ReadinessCard(
            area="Table catalogue",
            state=ReadinessState.ATTENTION,
            value=f"{live_count}/{total_count} live",
            detail=detail,
            action="Review missing or unmaterialized table rows before handoff.",
        )

    return ReadinessCard(
        area="Table catalogue",
        state=ReadinessState.READY,
        value=f"{live_count}/{total_count} live",
        detail=detail,
        action="No action.",
    )


def _dagster_catalogue_card(catalogue: DagsterAssetCatalogue) -> ReadinessCard:
    if not catalogue.available:
        return ReadinessCard(
            area="Dagster catalogue",
            state=ReadinessState.UNAVAILABLE,
            value="GraphQL unavailable",
            detail=catalogue.error or "Dagster GraphQL returned no detail.",
            action=(
                "Confirm DAGSTER_GRAPHQL_URL, Dagster webserver health, and "
                "reverse-proxy path."
            ),
        )

    asset_count = len(catalogue.assets)
    materialized_count = sum(
        asset.latest_materialization_timestamp is not None for asset in catalogue.assets
    )
    latest_materialization = _latest_materialization_label(catalogue)

    if asset_count == 0:
        return ReadinessCard(
            area="Dagster catalogue",
            state=ReadinessState.EMPTY,
            value="No table assets",
            detail=f"GraphQL responded at {catalogue.url}, but no table assets matched.",
            action="Confirm Dagster asset definitions expose table metadata.",
        )

    if materialized_count == 0:
        return ReadinessCard(
            area="Dagster catalogue",
            state=ReadinessState.ATTENTION,
            value=f"0/{asset_count} materialized",
            detail=latest_materialization,
            action="Run or backfill table assets before treating data as fresh.",
        )

    return ReadinessCard(
        area="Dagster catalogue",
        state=ReadinessState.READY,
        value=f"{materialized_count}/{asset_count} materialized",
        detail=latest_materialization,
        action="No action.",
    )


def _bounded_read_card(config: TableExplorerConfig) -> ReadinessCard:
    row_limit = bounded_row_limit(config)
    if row_limit is None:
        return ReadinessCard(
            area="Bounded reads",
            state=ReadinessState.READY,
            value="Full scans enabled",
            detail=(
                "Notebook table previews can compute exact row counts, text "
                "search, sorting, and column statistics."
            ),
            action="No action.",
        )

    runtime_label = "AWS" if config.aws_runtime else "local"
    return ReadinessCard(
        area="Bounded reads",
        state=ReadinessState.READY,
        value=f"{row_limit} row cap",
        detail=(
            f"{runtime_label} preview reads are capped before collection; "
            "global text search and exact row counts stay disabled for bounded scans."
        ),
        action="No action.",
    )


def _table_status_counts(
    table_catalogue: Sequence[CataloguedTable],
) -> dict[TableAvailability, int]:
    counts = {status: 0 for status in TableAvailability}
    for table in table_catalogue:
        counts[table.status] += 1
    return counts


def _table_status_action(status: TableAvailability) -> str:
    if status is TableAvailability.LIVE:
        return "No action."
    if status is TableAvailability.UNMATERIALIZED:
        return "Materialize the Dagster asset before expecting storage data."
    if status is TableAvailability.MISSING:
        return "Check the asset URI and expected S3 table prefix."
    return "Restore Dagster GraphQL to classify discovered storage prefixes."


def _latest_materialization_label(catalogue: DagsterAssetCatalogue) -> str:
    timestamps = [
        asset.latest_materialization_timestamp
        for asset in catalogue.assets
        if asset.latest_materialization_timestamp is not None
    ]
    if not timestamps:
        return "No materializations recorded."
    return (
        f"Latest materialization: {format_materialization_timestamp(max(timestamps))}"
    )


def _readiness_status_card(card: ReadinessCard) -> DashboardStatusCard:
    return DashboardStatusCard(
        label=card.area,
        state=card.state.value,
        value=card.value,
        detail=card.detail,
        action=card.action,
    )
