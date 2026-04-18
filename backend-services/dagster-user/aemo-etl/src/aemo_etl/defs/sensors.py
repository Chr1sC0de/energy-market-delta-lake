from dagster import (
    AssetSelection,
    AutomationConditionSensorDefinition,
    DefaultSensorStatus,
    Definitions,
    definitions,
)

import aemo_etl.factories.sensors
from aemo_etl.configs import DEVELOPMENT_LOCATION, LANDING_BUCKET

DEFAULT_STATUS = (
    DefaultSensorStatus.RUNNING
    if DEVELOPMENT_LOCATION == "aws"
    else DefaultSensorStatus.STOPPED
)

EVENT_DRIVEN_ASSETS_SELECTION = (
    AssetSelection.key_prefixes(["bronze", "vicgas"])
    & AssetSelection.key_substring("int")
) | (
    AssetSelection.key_prefixes(["bronze", "gbb"])
    & AssetSelection.key_substring("gasbb")
)


@definitions
def defs() -> Definitions:
    return Definitions(
        sensors=[
            aemo_etl.factories.sensors.df_from_s3_keys_sensor(
                name="event_driven_assets_sensor",
                asset_selection=EVENT_DRIVEN_ASSETS_SELECTION,
                s3_source_bucket=LANDING_BUCKET,
                s3_source_prefix="bronze/vicgas",
                # 200mb for a 1024 ram ecs instance
                bytes_cap=200e6,
                default_status=DEFAULT_STATUS,
            ),
            AutomationConditionSensorDefinition(
                name="default_automation_condition_sensor",
                target=AssetSelection.all() - EVENT_DRIVEN_ASSETS_SELECTION,
                default_status=DEFAULT_STATUS,
            ),
        ]
    )
