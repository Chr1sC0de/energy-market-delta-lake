"""Delta table maintenance definitions for aemo-etl assets."""

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Final

from dagster import (
    AssetsDefinition,
    DefaultScheduleStatus,
    Definitions,
    MetadataValue,
    OpExecutionContext,
    ScheduleDefinition,
    job,
    op,
)
from deltalake import DeltaTable
from deltalake.exceptions import TableNotFoundError

from aemo_etl.configs import DAGSTER_URI


DELTA_TABLE_VACUUM_JOB_NAME: Final = "delta_table_vacuum_job"
DELTA_TABLE_VACUUM_SCHEDULE_NAME: Final = "delta_table_vacuum_schedule"
DELTA_TABLE_VACUUM_CRON_SCHEDULE: Final = "0 2 * * *"
DELTA_TABLE_VACUUM_TIMEZONE: Final = "Australia/Melbourne"
FULL_VACUUM_RETENTION_HOURS: Final = 0
FULL_VACUUM_ENFORCE_RETENTION_DURATION: Final = False
FULL_VACUUM_DRY_RUN: Final = False
DELTA_MAINTENANCE_ENABLED: Final = "delta_maintenance/enabled"
DELTA_MAINTENANCE_COMPACT: Final = "delta_maintenance/compact"
DELTA_MAINTENANCE_VACUUM: Final = "delta_maintenance/vacuum"
DELTA_MAINTENANCE_RETENTION_HOURS: Final = "delta_maintenance/retention_hours"
DELTA_MAINTENANCE_ENFORCE_RETENTION_DURATION: Final = (
    "delta_maintenance/enforce_retention_duration"
)
DELTA_MAINTENANCE_DRY_RUN: Final = "delta_maintenance/dry_run"

DELTA_IO_MANAGER_KEYS: Final = frozenset(
    {
        "aemo_deltalake_append_io_manager",
        "aemo_deltalake_overwrite_io_manager",
        "aemo_deltalake_ingest_partitioned_append_io_manager",
    }
)


@dataclass(frozen=True, slots=True)
class DeltaTableMaintenanceConfig:
    """Per-asset Delta maintenance settings."""

    enabled: bool
    compact: bool
    vacuum: bool
    retention_hours: int
    enforce_retention_duration: bool
    dry_run: bool


@dataclass(frozen=True, slots=True)
class DeltaTableMaintenanceTarget:
    """Delta table selected for scheduled maintenance."""

    asset_key: str
    table_uri: str
    config: DeltaTableMaintenanceConfig


def _metadata_bool(
    metadata: Mapping[str, object],
    *,
    asset_key: str,
    key: str,
    default: bool,
) -> bool:
    value = metadata.get(key, default)
    if type(value) is not bool:
        raise ValueError(
            f"{asset_key} metadata {key} must be bool, got {type(value).__name__}"
        )
    return value


def _metadata_retention_hours(
    metadata: Mapping[str, object],
    *,
    asset_key: str,
) -> int:
    value = metadata.get(DELTA_MAINTENANCE_RETENTION_HOURS, FULL_VACUUM_RETENTION_HOURS)
    if type(value) is not int:
        raise ValueError(
            f"{asset_key} metadata {DELTA_MAINTENANCE_RETENTION_HOURS} must be int, "
            f"got {type(value).__name__}"
        )
    if value < 0:
        raise ValueError(
            f"{asset_key} metadata {DELTA_MAINTENANCE_RETENTION_HOURS} must be "
            "greater than or equal to 0"
        )
    return value


def _maintenance_config_from_metadata(
    metadata: Mapping[str, object],
    *,
    asset_key: str,
) -> DeltaTableMaintenanceConfig:
    return DeltaTableMaintenanceConfig(
        enabled=_metadata_bool(
            metadata,
            asset_key=asset_key,
            key=DELTA_MAINTENANCE_ENABLED,
            default=True,
        ),
        compact=_metadata_bool(
            metadata,
            asset_key=asset_key,
            key=DELTA_MAINTENANCE_COMPACT,
            default=True,
        ),
        vacuum=_metadata_bool(
            metadata,
            asset_key=asset_key,
            key=DELTA_MAINTENANCE_VACUUM,
            default=True,
        ),
        retention_hours=_metadata_retention_hours(metadata, asset_key=asset_key),
        enforce_retention_duration=_metadata_bool(
            metadata,
            asset_key=asset_key,
            key=DELTA_MAINTENANCE_ENFORCE_RETENTION_DURATION,
            default=FULL_VACUUM_ENFORCE_RETENTION_DURATION,
        ),
        dry_run=_metadata_bool(
            metadata,
            asset_key=asset_key,
            key=DELTA_MAINTENANCE_DRY_RUN,
            default=FULL_VACUUM_DRY_RUN,
        ),
    )


def collect_delta_table_maintenance_targets(
    definitions: Definitions,
) -> tuple[DeltaTableMaintenanceTarget, ...]:
    """Collect Delta-backed asset targets from loaded Dagster definitions."""
    targets: dict[str, DeltaTableMaintenanceTarget] = {}

    for asset in definitions.assets or []:
        if not isinstance(asset, AssetsDefinition):
            continue

        for asset_key in asset.keys:
            io_manager_key = asset.get_io_manager_key_for_asset_key(asset_key)
            if io_manager_key not in DELTA_IO_MANAGER_KEYS:
                continue

            metadata = asset.metadata_by_key.get(asset_key, {})
            table_uri = metadata.get(DAGSTER_URI)
            if not isinstance(table_uri, str):
                continue

            asset_key_string = "/".join(asset_key.path)
            target = DeltaTableMaintenanceTarget(
                asset_key=asset_key_string,
                table_uri=table_uri,
                config=_maintenance_config_from_metadata(
                    metadata,
                    asset_key=asset_key_string,
                ),
            )
            targets[target.asset_key] = target

    return tuple(sorted(targets.values(), key=lambda target: target.asset_key))


def run_delta_table_maintenance(
    context: OpExecutionContext,
    *,
    targets: tuple[DeltaTableMaintenanceTarget, ...],
) -> None:
    """Compact and vacuum selected Delta tables and record metadata."""
    results: list[dict[str, object]] = []
    skipped_count = 0

    for target in targets:
        if not target.config.enabled:
            skipped_count += 1
            context.log.info(
                f"delta maintenance disabled for {target.table_uri}; skipping"
            )
            results.append(
                {
                    "asset_key": target.asset_key,
                    "table_uri": target.table_uri,
                    "status": "skipped",
                    "reason": "maintenance_disabled",
                    "maintenance_config": asdict(target.config),
                }
            )
            continue

        if not target.config.compact and not target.config.vacuum:
            skipped_count += 1
            context.log.info(
                f"no delta maintenance operations enabled for {target.table_uri}; "
                "skipping"
            )
            results.append(
                {
                    "asset_key": target.asset_key,
                    "table_uri": target.table_uri,
                    "status": "skipped",
                    "reason": "no_operations_enabled",
                    "maintenance_config": asdict(target.config),
                }
            )
            continue

        context.log.info(f"running delta maintenance for {target.table_uri}")

        try:
            delta_table = DeltaTable(target.table_uri)
        except TableNotFoundError:
            skipped_count += 1
            context.log.info(f"table not found {target.table_uri}; skipping")
            results.append(
                {
                    "asset_key": target.asset_key,
                    "table_uri": target.table_uri,
                    "status": "skipped",
                    "reason": "table_not_found",
                    "maintenance_config": asdict(target.config),
                }
            )
            continue

        compact_response: object | None = None
        vacuumed_files: object | None = None

        if target.config.compact:
            compact_response = delta_table.optimize.compact()

        if target.config.vacuum:
            vacuumed_files = delta_table.vacuum(
                retention_hours=target.config.retention_hours,
                enforce_retention_duration=target.config.enforce_retention_duration,
                dry_run=target.config.dry_run,
            )

        results.append(
            {
                "asset_key": target.asset_key,
                "table_uri": target.table_uri,
                "status": "processed",
                "maintenance_config": asdict(target.config),
                "compact": compact_response,
                "vacuumed_files": vacuumed_files,
            }
        )

    context.add_output_metadata(
        {
            "target_count": len(targets),
            "processed_count": len(targets) - skipped_count,
            "skipped_count": skipped_count,
            "tables": MetadataValue.json(results),
        }
    )


def delta_table_maintenance_definitions_factory(
    source_definitions: Definitions,
    *,
    default_status: DefaultScheduleStatus,
) -> Definitions:
    """Create the scheduled Delta table maintenance job definitions."""
    targets = collect_delta_table_maintenance_targets(source_definitions)

    @op(name="compact_and_full_vacuum_delta_tables")
    def compact_and_full_vacuum_delta_tables(context: OpExecutionContext) -> None:
        run_delta_table_maintenance(context, targets=targets)

    @job(name=DELTA_TABLE_VACUUM_JOB_NAME)
    def delta_table_vacuum_job() -> None:
        compact_and_full_vacuum_delta_tables()

    schedule = ScheduleDefinition(
        name=DELTA_TABLE_VACUUM_SCHEDULE_NAME,
        job=delta_table_vacuum_job,
        cron_schedule=DELTA_TABLE_VACUUM_CRON_SCHEDULE,
        execution_timezone=DELTA_TABLE_VACUUM_TIMEZONE,
        default_status=default_status,
        description=(
            "Daily compaction and full vacuum for Delta tables discovered from "
            "Dagster asset metadata."
        ),
    )

    return Definitions(
        jobs=[delta_table_vacuum_job],
        schedules=[schedule],
    )
