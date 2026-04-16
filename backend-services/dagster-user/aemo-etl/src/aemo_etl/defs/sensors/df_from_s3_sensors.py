from dagster import (
    AssetSelection,
    Definitions,
    definitions,
)

import aemo_etl.factories.sensors.df_from_s3_keys_sensor
from aemo_etl.configs import LANDING_BUCKET


@definitions
def defs() -> Definitions:
    return Definitions(
        sensors=[
            aemo_etl.factories.sensors.df_from_s3_keys_sensor.factory(
                name="vicgas_sensor",
                asset_selection=(
                    AssetSelection.key_prefixes(["bronze", "vicgas"])
                    & AssetSelection.key_substring("int")
                ),
                s3_source_bucket=LANDING_BUCKET,
                s3_source_prefix="bronze/vicgas",
                # 200mb for a 1024 ram ecs instance
                bytes_cap=200e6,
            ),
            aemo_etl.factories.sensors.df_from_s3_keys_sensor.factory(
                name="gbb_sensor",
                asset_selection=(
                    AssetSelection.key_prefixes(["bronze", "gbb"])
                    & AssetSelection.key_substring("gasbb")
                ),
                s3_source_bucket=LANDING_BUCKET,
                s3_source_prefix="bronze/gbb",
                # 200mb for a 1024 ram ecs instance
                bytes_cap=200e6,
            ),
        ]
    )
