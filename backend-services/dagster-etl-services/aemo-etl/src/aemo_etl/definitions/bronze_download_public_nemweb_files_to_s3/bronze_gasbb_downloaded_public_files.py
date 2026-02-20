import polars as pl
from dagster import OpExecutionContext, ScheduleEvaluationContext

from aemo_etl.configuration import BRONZE_BUCKET, LANDING_BUCKET
from aemo_etl.configuration._configuration import Link
from aemo_etl.factory.definition import (
    download_nemweb_public_files_to_s3_definition_factory,
)
from aemo_etl.factory.definition._downloaded_nemweb_public_files_to_s3_definition_factory import (  # noqa: E501
    InMemoryCachedLinkFilter,
)
from aemo_etl.register import definitions_list, table_locations

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_downloaded_public_files"

s3_prefix = "aemo/gasbb"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


class InMemoryCachedLinkFilterIgnoreDuplicates(InMemoryCachedLinkFilter):
    def __call__(self, _: OpExecutionContext, link: Link) -> bool:
        if "DUPLICATE" in link.source_absolute_href:
            return False
        return super().__call__(_, link)


def table_exists() -> bool:
    try:
        pl.scan_delta(s3_table_location)
        return True
    except Exception:
        return False


def schedule_tags_fn(_: ScheduleEvaluationContext) -> dict[str, str]:
    return {
        "ecs/cpu": "512" if table_exists() else "8192",
        "ecs/memory": "2048" if table_exists() else "16384",
    }


definitions_list.append(
    download_nemweb_public_files_to_s3_definition_factory(
        group_name="aemo__metadata",
        key_prefix=key_prefix,
        name=table_name,
        root_relative_href="REPORTS/CURRENT/GBB",
        s3_landing_bucket=LANDING_BUCKET,
        s3_landing_prefix=s3_prefix,
        s3_target_prefix=s3_prefix,
        link_filter=InMemoryCachedLinkFilterIgnoreDuplicates(s3_table_location, 900),
        get_buffer_from_link_hook=None,
        override_get_links_fn=None,
        vacuum_retention_hours=0,
        job_tags=None,
        schedule_tags_fn=schedule_tags_fn,
        job_schedule_cron="5 * * * *",  # run every day 5 minutes past the hour
        compact_and_vacuum_schdule_cron="00 23 * * *",  # run at every 11 pm
    )
)
