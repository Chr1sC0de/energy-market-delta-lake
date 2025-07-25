from dagster import OpExecutionContext
from deltalake.exceptions import TableNotFoundError
from polars import col, lit, read_delta

from aemo_etl.configuration import BRONZE_BUCKET, LANDING_BUCKET
from aemo_etl.configuration._configuration import Link
from aemo_etl.factory.definition import (
    download_nemweb_public_files_to_s3_definition_factory,
)
from aemo_etl.register import definitions_list, table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

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

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                update the link filter to exclude the duplicates folder                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


def ignore_duplicate_folder_filter(_: OpExecutionContext, link: Link) -> bool:
    try:
        if "DUPLICATE" in link.source_absolute_href:
            return False
        df = read_delta(s3_table_location)
        search_df = df.filter(
            col("source_absolute_href") == lit(link.source_absolute_href),
            col("source_upload_datetime")
            == lit(link.source_upload_datetime).cast(
                df["source_upload_datetime"].dtype
            ),
        )
        if len(search_df) > 0:
            return False
        return True
    except TableNotFoundError:
        return True


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                register the definition                                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

definitions_list.append(
    download_nemweb_public_files_to_s3_definition_factory(
        group_name="aemo__metadata",
        key_prefix=key_prefix,
        name=table_name,
        root_relative_href="REPORTS/CURRENT/GBB",
        s3_landing_bucket=LANDING_BUCKET,
        s3_landing_prefix=s3_prefix,
        s3_target_prefix=s3_prefix,
        link_filter=ignore_duplicate_folder_filter,
        get_buffer_from_link_hook=None,
        override_get_links_fn=None,
        vacuum_retention_hours=0,
        job_tags={
            "ecs/cpu": "512",
            "ecs/memory": "2048",
        },
        job_schedule_cron="5 * * * *",  # run every day 5 minutes past the hour
        compact_and_vacuum_schdule_cron="00 23 * * *",  # run at every 11 pm
    )
)
