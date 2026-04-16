import bs4
from dagster import (
    AutomationConditionSensorDefinition,
    Definitions,
    OpExecutionContext,
    definitions,
)

from aemo_etl.factories.definitions.nemweb_public_files import (
    ASSET_KEYS,
    nemweb_public_files_definition_factory,
)


# TODO: create tests
def gbb_top_folder_filter(
    _: OpExecutionContext, tag: bs4.Tag
) -> bool:  # pragma: no cover
    tag_text: str = tag.text
    return tag_text not in ["DUPLICATE", "ForecastUtilisation", "[To Parent Directory]"]


@definitions
def defs() -> Definitions:
    return Definitions.merge(
        nemweb_public_files_definition_factory(
            key_prefix=["bronze", "vicgas"],
            table_name="bronze_nemweb_public_files_vicgas",
            nemweb_relative_href="REPORTS/CURRENT/VicGas",
            cron_schedule="*/15 * * * *",
        ),
        nemweb_public_files_definition_factory(
            key_prefix=["bronze", "gbb"],
            table_name="bronze_nemweb_public_files_gbb",
            nemweb_relative_href="REPORTS/CURRENT/GBB",
            cron_schedule="*/15 * * * *",
            folder_filter=gbb_top_folder_filter,
        ),
        nemweb_public_files_definition_factory(
            key_prefix=["bronze", "gbb"],
            table_name="bronze_nemweb_public_files_gbb_forecast_utilization",
            nemweb_relative_href="REPORTS/CURRENT/GBB/ForecastUtilisation",
            batch_size=100,
            cron_schedule="*/15 * * * *",
        ),
        nemweb_public_files_definition_factory(
            key_prefix=["bronze", "gbb"],
            table_name="bronze_nemweb_public_files_gbb_duplicate",
            nemweb_relative_href="REPORTS/CURRENT/GBB/DUPLICATE",
            batch_size=100,
            cron_schedule="*/15 * * * *",
        ),
        # as the ASSET_KEYS var is populated dynamically define the sensor last
        Definitions(
            sensors=[
                AutomationConditionSensorDefinition(
                    name="bronze_nemweb_public_files_sensor",
                    target=ASSET_KEYS,
                )
            ],
        ),
    )
