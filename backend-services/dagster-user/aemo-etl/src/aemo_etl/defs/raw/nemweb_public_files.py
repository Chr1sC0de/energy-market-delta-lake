import re

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


def vicgas_file_filter(_: OpExecutionContext, tag: bs4.Tag) -> bool:
    filename: str = tag.text.strip().lower()
    return filename != "currentday.zip" and not (
        filename.startswith("publicrpts") and filename.endswith(".zip")
    )


STTM_DAY_ZIP_PATTERN = re.compile(r"^day\d{2}\.zip$", re.IGNORECASE)


def sttm_folder_filter(_: OpExecutionContext, __: bs4.Tag) -> bool:
    return False


def sttm_file_filter(_: OpExecutionContext, tag: bs4.Tag) -> bool:
    filename: str = tag.text.strip().lower()
    if filename.startswith("currentday."):
        return False
    if STTM_DAY_ZIP_PATTERN.fullmatch(filename):
        return False
    return filename.endswith(".csv")


@definitions
def defs() -> Definitions:
    return Definitions.merge(
        nemweb_public_files_definitions_factory(
            domain="vicgas",
            table_name="bronze_nemweb_public_files_vicgas",
            nemweb_relative_href="REPORTS/CURRENT/VicGas",
            cron_schedule="*/30 * * * *",
            n_executors=10,
            file_filter=vicgas_file_filter,
            group_name="integration",
            default_status=DEFAULT_SCHEDULE_STATUS,
            tags={"ecs/cpu": "512", "ecs/memory": "4096"},
        ),
        nemweb_public_files_definitions_factory(
            domain="gbb",
            table_name="bronze_nemweb_public_files_gbb",
            nemweb_relative_href="REPORTS/CURRENT/GBB",
            cron_schedule="*/30 * * * *",
            n_executors=10,
            folder_filter=gbb_folder_filter,
            group_name="integration",
            default_status=DEFAULT_SCHEDULE_STATUS,
            tags={"ecs/cpu": "512", "ecs/memory": "4096"},
        ),
        nemweb_public_files_definitions_factory(
            domain="sttm",
            table_name="bronze_nemweb_public_files_sttm",
            nemweb_relative_href="REPORTS/CURRENT/STTM",
            cron_schedule="*/30 * * * *",
            n_executors=10,
            folder_filter=sttm_folder_filter,
            file_filter=sttm_file_filter,
            group_name="integration",
            default_status=DEFAULT_SCHEDULE_STATUS,
            tags={"ecs/cpu": "512", "ecs/memory": "4096"},
        ),
    )
