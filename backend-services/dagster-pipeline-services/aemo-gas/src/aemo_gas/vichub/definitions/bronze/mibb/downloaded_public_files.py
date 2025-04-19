import dagster as dg
import polars as pl

from configurations.parameters import (
    DEVELOPMENT_LOCATION,
)
from aemo_gas.vichub import assets


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                           create a compact and vacuum asset                            │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

compact_and_vacuum_asset = assets.bronze.mibb.factory.compact_and_vacuum(
    table_definition=assets.bronze.mibb.downloaded_public_files.asset,
    group_name="BRONZE__AEMO__GAS__VICHUB__OPTIMIZATION",
    key_prefix=["bronze", "aemo", "gas", "vichub", "downloaded_public_files"],
    table_name="downloaded_public_files",
    retention_hours=0,
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                            create check for the core asset                             │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@dg.asset_check(asset=assets.bronze.mibb.downloaded_public_files.asset)
def has_no_duplicate_source_and_target_entries(
    downloaded_public_files: pl.LazyFrame,
):
    return dg.AssetCheckResult(
        passed=bool(
            downloaded_public_files.select(pl.len()).collect().item()
            == downloaded_public_files.select("source_file", "target_file")
            .unique()
            .select(pl.len())
            .collect()
            .item()
        ),
    )


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                      create jobs                                       │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

downloaded_public_files_job = dg.define_asset_job(
    "aemo_gas_vichub_bronze_downloaded_public_files_job",
    selection=[assets.bronze.mibb.downloaded_public_files.asset],
    tags={
        "ecs/cpu": "512",
        "ecs/memory": "2048",
    },
)

downloaded_public_files_compact_and_vacuum_job = dg.define_asset_job(
    name="aemo_gas_vichub_bronze_downloaded_public_files_compact_and_vacuum",
    selection=[compact_and_vacuum_asset],
)


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                 create a schedule for the downloaded_public_files_job                  │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

downloaded_public_files_schedule = dg.ScheduleDefinition(
    job=downloaded_public_files_job,
    cron_schedule="5 * * * *",  # run every 5 minutes past the hour
    default_status=(
        dg.DefaultScheduleStatus.STOPPED
        if DEVELOPMENT_LOCATION == "local"
        else dg.DefaultScheduleStatus.RUNNING
    ),
)

downloaded_public_files_compact_and_vacuum_schedule = dg.ScheduleDefinition(
    job=downloaded_public_files_compact_and_vacuum_job,
    cron_schedule="00 23 * * *",  # run every day at 11 pm
    execution_timezone="Australia/Melbourne",
    default_status=(
        dg.DefaultScheduleStatus.STOPPED
        if DEVELOPMENT_LOCATION == "local"
        else dg.DefaultScheduleStatus.RUNNING
    ),
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                           generate the required definitions                            │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


definition = dg.Definitions(
    assets=[assets.bronze.mibb.downloaded_public_files.asset, compact_and_vacuum_asset],
    jobs=[
        downloaded_public_files_job,
        downloaded_public_files_compact_and_vacuum_job,
    ],
    schedules=[
        downloaded_public_files_schedule,
        downloaded_public_files_compact_and_vacuum_schedule,
    ],
)
