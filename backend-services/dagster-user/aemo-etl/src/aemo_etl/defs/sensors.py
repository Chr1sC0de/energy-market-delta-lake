from dagster import (
    AssetSelection,
    AutomationConditionSensorDefinition,
    DefaultSensorStatus,
    Definitions,
    definitions,
)

import aemo_etl.factories.sensors
import aemo_etl.factories.unzipper.sensors
from aemo_etl.configs import DEVELOPMENT_LOCATION, LANDING_BUCKET

DEFAULT_STATUS = (
    DefaultSensorStatus.RUNNING
    if DEVELOPMENT_LOCATION == "aws"
    else DefaultSensorStatus.STOPPED
)

VICGAS_ASSET_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "vicgas"]
) & AssetSelection.key_substring("int")

GBB_ASSET_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "gbb"]
) & AssetSelection.key_substring("gasbb")

VICGAS_UNZIPPER_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "vicgas"]
) & AssetSelection.key_substring("unzipper")

GBB_UNZIPPER_SELECTION = AssetSelection.key_prefixes(
    ["bronze", "gbb"]
) & AssetSelection.key_substring("unzipper")

EVENT_DRIVEN_ASSETS_SELECTION = (
    VICGAS_ASSET_SELECTION
    | GBB_ASSET_SELECTION
    | VICGAS_UNZIPPER_SELECTION
    | GBB_UNZIPPER_SELECTION
)


@definitions
def defs() -> Definitions:
    return Definitions(
        sensors=[
            aemo_etl.factories.sensors.df_from_s3_keys_sensor(
                name="vicgas_event_driven_assets_sensor",
                asset_selection=VICGAS_ASSET_SELECTION,
                s3_source_bucket=LANDING_BUCKET,
                s3_source_prefix="bronze/vicgas",
                bytes_cap=100e6,
                files_cap=None,
                default_status=DEFAULT_STATUS,
            ),
            aemo_etl.factories.sensors.df_from_s3_keys_sensor(
                name="gbb_event_driven_assets_sensor",
                asset_selection=GBB_ASSET_SELECTION,
                s3_source_bucket=LANDING_BUCKET,
                s3_source_prefix="bronze/gbb",
                bytes_cap=100e6,
                files_cap=None,
                default_status=DEFAULT_STATUS,
            ),
            aemo_etl.factories.unzipper.sensors.unzipper_sensor(
                name="vicgas_unzipper_sensor",
                asset_selection=VICGAS_UNZIPPER_SELECTION,
                s3_source_bucket=LANDING_BUCKET,
                s3_source_prefix="bronze/vicgas",
                default_status=DEFAULT_STATUS,
            ),
            aemo_etl.factories.unzipper.sensors.unzipper_sensor(
                name="gbb_unzipper_sensor",
                asset_selection=GBB_UNZIPPER_SELECTION,
                s3_source_bucket=LANDING_BUCKET,
                s3_source_prefix="bronze/gbb",
                default_status=DEFAULT_STATUS,
            ),
            AutomationConditionSensorDefinition(
                name="default_automation_condition_sensor",
                target=AssetSelection.all() - EVENT_DRIVEN_ASSETS_SELECTION,
                default_status=DEFAULT_STATUS,
            ),
        ]
    )
