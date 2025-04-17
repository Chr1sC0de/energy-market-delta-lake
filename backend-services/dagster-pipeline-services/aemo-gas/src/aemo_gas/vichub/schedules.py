import dagster as dg
from aemo_gas.vichub.jobs import vichub_downloaded_files_metadata_job
from configurations.parameters import DEVELOPMENT_LOCATION


all = [
    dg.ScheduleDefinition(
        job=vichub_downloaded_files_metadata_job,
        # run every hour
        cron_schedule="*/30 * * * *",
        default_status=(
            dg.DefaultScheduleStatus.STOPPED
            if DEVELOPMENT_LOCATION == "local"
            else dg.DefaultScheduleStatus.RUNNING
        ),
    )
]
