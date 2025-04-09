import dagster as dg
from aemo_gas.vichub.jobs import vichub_downloaded_files_metadata_job


all = [
    dg.ScheduleDefinition(
        job=vichub_downloaded_files_metadata_job,
        # run every hour
        cron_schedule="0 * * * *",
    )
]
