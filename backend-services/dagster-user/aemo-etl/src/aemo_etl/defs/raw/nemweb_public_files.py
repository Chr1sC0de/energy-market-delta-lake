import bs4
from dagster import (
    Definitions,
    OpExecutionContext,
    definitions,
)

from aemo_etl.factories.nemweb_public_files.definitions import (
    nemweb_public_files_definitions_factory,
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
        nemweb_public_files_definitions_factory(
            domain="vicgas",
            table_name="bronze_nemweb_public_files_vicgas",
            nemweb_relative_href="REPORTS/CURRENT/VicGas",
            cron_schedule="*/15 * * * *",
        ),
        nemweb_public_files_definitions_factory(
            domain="gbb",
            table_name="bronze_nemweb_public_files_gbb",
            nemweb_relative_href="REPORTS/CURRENT/GBB",
            cron_schedule="*/15 * * * *",
            folder_filter=gbb_top_folder_filter,
        ),
        nemweb_public_files_definitions_factory(
            domain="gbb",
            table_name="bronze_nemweb_public_files_gbb_forecast_utilization",
            nemweb_relative_href="REPORTS/CURRENT/GBB/ForecastUtilisation",
            batch_size=100,
            cron_schedule="*/15 * * * *",
        ),
        nemweb_public_files_definitions_factory(
            domain="gbb",
            table_name="bronze_nemweb_public_files_gbb_duplicate",
            nemweb_relative_href="REPORTS/CURRENT/GBB/DUPLICATE",
            batch_size=100,
            cron_schedule="*/15 * * * *",
        ),
    )
