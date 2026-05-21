import re

import bs4
from dagster import (
    Definitions,
    OpExecutionContext,
    definitions,
)

from aemo_etl.asset_organization import GAS_INGESTION_DISCOVERY_GROUP
from aemo_etl.configs import AEMO_BUCKET, DEFAULT_SCHEDULE_STATUS, LANDING_BUCKET
from aemo_etl.factories.nemweb_public_files.definitions import (
    NEMWebPublicFilesSpec,
    build_nemweb_public_files_definitions,
)
from aemo_etl.factories.nemweb_public_files.ops.nemweb_link_fetcher import (
    default_file_filter,
    default_folder_filter,
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
        build_nemweb_public_files_definitions(
            NEMWebPublicFilesSpec(
                domain="vicgas",
                table_name="bronze_nemweb_public_files_vicgas",
                nemweb_relative_href="REPORTS/CURRENT/VicGas",
                cron_schedule="*/30 * * * *",
                default_status=DEFAULT_SCHEDULE_STATUS,
                n_executors=10,
                folder_filter=default_folder_filter,
                file_filter=vicgas_file_filter,
                group_name=GAS_INGESTION_DISCOVERY_GROUP,
                tags={"ecs/cpu": "512", "ecs/memory": "4096"},
                process_retry=3,
                initial=10,
                exp_base=3,
                max_retry_time=100,
                table_bucket=AEMO_BUCKET,
                landing_bucket=LANDING_BUCKET,
                io_manager_key="aemo_deltalake_append_io_manager",
                cached_link_ttl_seconds=900,
            )
        ),
        build_nemweb_public_files_definitions(
            NEMWebPublicFilesSpec(
                domain="gbb",
                table_name="bronze_nemweb_public_files_gbb",
                nemweb_relative_href="REPORTS/CURRENT/GBB",
                cron_schedule="*/30 * * * *",
                default_status=DEFAULT_SCHEDULE_STATUS,
                n_executors=10,
                folder_filter=gbb_folder_filter,
                file_filter=default_file_filter,
                group_name=GAS_INGESTION_DISCOVERY_GROUP,
                tags={"ecs/cpu": "512", "ecs/memory": "4096"},
                process_retry=3,
                initial=10,
                exp_base=3,
                max_retry_time=100,
                table_bucket=AEMO_BUCKET,
                landing_bucket=LANDING_BUCKET,
                io_manager_key="aemo_deltalake_append_io_manager",
                cached_link_ttl_seconds=900,
            )
        ),
        build_nemweb_public_files_definitions(
            NEMWebPublicFilesSpec(
                domain="sttm",
                table_name="bronze_nemweb_public_files_sttm",
                nemweb_relative_href="REPORTS/CURRENT/STTM",
                cron_schedule="*/30 * * * *",
                default_status=DEFAULT_SCHEDULE_STATUS,
                n_executors=10,
                folder_filter=sttm_folder_filter,
                file_filter=sttm_file_filter,
                group_name=GAS_INGESTION_DISCOVERY_GROUP,
                tags={"ecs/cpu": "512", "ecs/memory": "4096"},
                process_retry=3,
                initial=10,
                exp_base=3,
                max_retry_time=100,
                table_bucket=AEMO_BUCKET,
                landing_bucket=LANDING_BUCKET,
                io_manager_key="aemo_deltalake_append_io_manager",
                cached_link_ttl_seconds=900,
            )
        ),
    )
