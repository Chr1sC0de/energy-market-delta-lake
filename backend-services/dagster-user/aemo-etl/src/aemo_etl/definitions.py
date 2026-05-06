"""Root Dagster definitions for the aemo-etl project."""

from pathlib import Path
from typing import Final

from dagster import (
    AssetSelection,
    Definitions,
    RunFailureSensorContext,
    definitions,
    load_from_defs_folder,
    run_failure_sensor,
)

import aemo_etl.factories.sensors
import aemo_etl.factories.unzipper.sensors
from aemo_etl.alerts import send_failed_run_alert
from aemo_etl.configs import (
    DEFAULT_SCHEDULE_STATUS,
    DEFAULT_SENSOR_STATUS,
    LANDING_BUCKET,
)
from aemo_etl.maintenance.delta_tables import (
    delta_table_maintenance_definitions_factory,
)

VICGAS_ASSET_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "vicgas"]
) & AssetSelection.key_substring("int")

GBB_ASSET_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "gbb"]
) & AssetSelection.key_substring("gasbb")

STTM_ASSET_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "sttm"]
) & AssetSelection.key_substring("int")

VICGAS_UNZIPPER_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "vicgas"]
) & AssetSelection.key_substring("unzipper")

GBB_UNZIPPER_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "gbb"]
) & AssetSelection.key_substring("unzipper")

STTM_UNZIPPER_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "sttm"]
) & AssetSelection.key_substring("unzipper")

EVENT_DRIVEN_ASSETS_SELECTION = (
    VICGAS_ASSET_SELECTION
    | GBB_ASSET_SELECTION
    | STTM_ASSET_SELECTION
    | VICGAS_UNZIPPER_SELECTION
    | GBB_UNZIPPER_SELECTION
    | STTM_UNZIPPER_SELECTION
)

SOURCE_TABLE_SENSOR_BYTES_CAP: Final = 128_000_000
SOURCE_TABLE_SENSOR_FILES_CAP: Final = 25


@run_failure_sensor(
    name="aemo_etl_failed_run_alert_sensor",
    default_status=DEFAULT_SENSOR_STATUS,
)
def aemo_etl_failed_run_alert_sensor(context: RunFailureSensorContext) -> None:
    """Forward failed Dagster runs to the configured alert channel."""
    send_failed_run_alert(context)


@definitions
def defs() -> Definitions:
    """Load and merge all project Dagster definitions."""
    loaded_definitions = load_from_defs_folder(
        path_within_project=Path(__file__).parent
    )

    jobs = tuple(loaded_definitions.jobs or ())

    return Definitions.merge(
        loaded_definitions,
        delta_table_maintenance_definitions_factory(
            loaded_definitions,
            default_status=DEFAULT_SCHEDULE_STATUS,
        ),
        Definitions(
            sensors=[
                aemo_etl_failed_run_alert_sensor,
                aemo_etl.factories.sensors.df_from_s3_keys_sensor(
                    name="vicgas_event_driven_assets_sensor",
                    asset_selection=VICGAS_ASSET_SELECTION,
                    s3_source_bucket=LANDING_BUCKET,
                    s3_source_prefix="bronze/vicgas",
                    bytes_cap=SOURCE_TABLE_SENSOR_BYTES_CAP,
                    files_cap=SOURCE_TABLE_SENSOR_FILES_CAP,
                    default_status=DEFAULT_SENSOR_STATUS,
                    jobs=jobs,
                ),
                aemo_etl.factories.sensors.df_from_s3_keys_sensor(
                    name="gbb_event_driven_assets_sensor",
                    asset_selection=GBB_ASSET_SELECTION,
                    s3_source_bucket=LANDING_BUCKET,
                    s3_source_prefix="bronze/gbb",
                    bytes_cap=SOURCE_TABLE_SENSOR_BYTES_CAP,
                    files_cap=SOURCE_TABLE_SENSOR_FILES_CAP,
                    default_status=DEFAULT_SENSOR_STATUS,
                    jobs=jobs,
                ),
                aemo_etl.factories.sensors.df_from_s3_keys_sensor(
                    name="sttm_event_driven_assets_sensor",
                    asset_selection=STTM_ASSET_SELECTION,
                    s3_source_bucket=LANDING_BUCKET,
                    s3_source_prefix="bronze/sttm",
                    bytes_cap=SOURCE_TABLE_SENSOR_BYTES_CAP,
                    files_cap=SOURCE_TABLE_SENSOR_FILES_CAP,
                    default_status=DEFAULT_SENSOR_STATUS,
                    jobs=jobs,
                ),
                aemo_etl.factories.unzipper.sensors.unzipper_sensor(
                    name="vicgas_unzipper_sensor",
                    asset_selection=VICGAS_UNZIPPER_SELECTION,
                    s3_source_bucket=LANDING_BUCKET,
                    s3_source_prefix="bronze/vicgas",
                    default_status=DEFAULT_SENSOR_STATUS,
                ),
                aemo_etl.factories.unzipper.sensors.unzipper_sensor(
                    name="gbb_unzipper_sensor",
                    asset_selection=GBB_UNZIPPER_SELECTION,
                    s3_source_bucket=LANDING_BUCKET,
                    s3_source_prefix="bronze/gbb",
                    default_status=DEFAULT_SENSOR_STATUS,
                ),
                aemo_etl.factories.unzipper.sensors.unzipper_sensor(
                    name="sttm_unzipper_sensor",
                    asset_selection=STTM_UNZIPPER_SELECTION,
                    s3_source_bucket=LANDING_BUCKET,
                    s3_source_prefix="bronze/sttm",
                    default_status=DEFAULT_SENSOR_STATUS,
                ),
            ],
        ),
    )
