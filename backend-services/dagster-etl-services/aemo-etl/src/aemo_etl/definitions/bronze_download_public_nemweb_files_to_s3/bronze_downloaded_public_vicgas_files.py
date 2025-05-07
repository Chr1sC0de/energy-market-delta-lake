from aemo_etl.configuration import BRONZE_BUCKET, LANDING_BUCKET
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.factory.definition import (
    download_nemweb_public_files_to_s3_definition_factory,
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                    define variables                                    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

schema = "aemo_vicgas"


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                register the definition                                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

definitions_list.append(
    download_nemweb_public_files_to_s3_definition_factory(
        group_name="aemo",
        key_prefix=["bronze", "aemo", "vicgas"],
        name="bronze_downloaded_public_vicgas_files",
        root_relative_href="REPORTS/CURRENT/VicGas",
        s3_landing_bucket=LANDING_BUCKET,
        s3_landing_prefix=schema,
        s3_schema=schema,
        link_filter=None,
        get_buffer_from_link_hook=None,
        post_process_hook=None,
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
