import bs4
from dagster import (
    Definitions,
    OpExecutionContext,
    definitions,
)

from aemo_etl.configs import DEFAULT_SCHEDULE_STATUS
from aemo_etl.factories.nemweb_public_files.definitions import (
    nemweb_public_files_definitions_factory,
)


def gbb_folder_filter(_: OpExecutionContext, tag: bs4.Tag) -> bool:
    tag_text: str = tag.text
    return tag_text not in ["[To Parent Directory]", "DUPLICATE"]


@definitions
def defs() -> Definitions:
    return Definitions.merge(
        nemweb_public_files_definitions_factory(
            domain="vicgas",
            table_name="bronze_nemweb_public_files_vicgas",
            nemweb_relative_href="REPORTS/CURRENT/VicGas",
            cron_schedule="*/15 * * * *",
            n_executors=10,
            group_name="integration",
            default_status=DEFAULT_SCHEDULE_STATUS,
        ),
        nemweb_public_files_definitions_factory(
            domain="gbb",
            table_name="bronze_nemweb_public_files_gbb",
            nemweb_relative_href="REPORTS/CURRENT/GBB",
            cron_schedule="*/15 * * * *",
            n_executors=10,
            folder_filter=gbb_folder_filter,
            group_name="integration",
            default_status=DEFAULT_SCHEDULE_STATUS,
        ),
    )
