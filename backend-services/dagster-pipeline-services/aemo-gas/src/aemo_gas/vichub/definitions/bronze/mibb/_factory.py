from collections.abc import Callable
from typing import Any

import dagster as dg
from dagster_aws.s3 import S3Resource

from aemo_gas import utils
from aemo_gas.vichub import assets
from aemo_gas.vichub.definitions.bronze.config.schemas import (
    MibbDeltaTableDefinitionFactoryConfig,
)
from configurations.parameters import DEVELOPMENT_LOCATION


def factory(config: MibbDeltaTableDefinitionFactoryConfig) -> dg.Definitions:
    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                                 create the delta table                                 │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    delta_table_asset = assets.bronze.mibb.factory.delta_table(config)

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                     create the compact and vacuum optimization job                     │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    compact_and_vacuum_asset = assets.bronze.mibb.factory.compact_and_vacuum(
        table_definition=delta_table_asset,
        group_name=f"{config.group_name}__OPTIMIZATION",
        key_prefix=config.key_prefix + [config.target_s3_name],
        table_name=config.target_s3_name,
        retention_hours=config.retention_hours,
    )

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                 create asset jobs for bot the etl and the optimization                 │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    asset_job = dg.define_asset_job(
        name=f"aemo_gas_vichub_bronze_{config.target_s3_name}_etl_job",
        selection=[delta_table_asset],
        tags=config.job_tags,
    )
    compact_and_vacuum_job = dg.define_asset_job(
        name=f"aemo_gas_vichub_bronze_{config.target_s3_name}_compact_and_vacuum",
        selection=[compact_and_vacuum_asset],
    )

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                  create the schedules for the compact and vacuum job                   │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯
    schedules = []
    if config.compact_and_vacuum_cron_schedule is not None:
        compact_and_vacuum_schedule = dg.ScheduleDefinition(
            job=compact_and_vacuum_job,
            cron_schedule=config.compact_and_vacuum_cron_schedule,
            default_status=(
                dg.DefaultScheduleStatus.STOPPED
                if DEVELOPMENT_LOCATION == "local"
                else dg.DefaultScheduleStatus.RUNNING
            ),
            execution_timezone=config.execution_timezone,
        )
        schedules.append(compact_and_vacuum_schedule)

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │    create an s3 sensor which triggers the job whenever a relevant file is uploaded     │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    @dg.sensor(
        name=f"aemo_gas_vichub_bronze_{config.target_s3_name}_s3_sensor",
        job=asset_job,
        minimum_interval_seconds=30,
        default_status=(
            dg.DefaultSensorStatus.STOPPED
            if DEVELOPMENT_LOCATION == "local"
            else dg.DefaultSensorStatus.RUNNING
        ),  # Sensor is turned on by default
    )
    def sensor(context: dg.SensorEvaluationContext, s3_resource: S3Resource):
        # Find runs of the same job that are currently running
        run_records = context.instance.get_run_records(
            dg.RunsFilter(
                job_name=f"aemo_gas_vichub_bronze_{config.target_s3_name}_etl_job",
                statuses=[
                    dg.DagsterRunStatus.QUEUED,
                    dg.DagsterRunStatus.NOT_STARTED,
                    dg.DagsterRunStatus.STARTING,
                    dg.DagsterRunStatus.STARTED,
                ],
            )
        )
        # only run the etl job if the public files have been downloaded
        if (
            len(run_records) == 0
            and context.instance.get_latest_materialization_event(
                assets.bronze.mibb.downloaded_public_files.asset.key
            )
            is not None
        ):
            s3_object_keys = utils.get_s3_object_keys_from_prefix_and_name_glob(
                s3_resource,
                config.source_bucket,
                config.source_s3_prefix,
                config.source_s3_glob,
            )
            if len(s3_object_keys) > 0:
                yield dg.RunRequest()
            else:
                yield dg.SkipReason("No new files found")
        else:
            yield dg.SkipReason("Run already in process")

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                              compile all the asset checks                              │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    asset_checks = []
    if config.check_factories is not None:
        for factory in config.check_factories:
            asset_checks.append(factory(delta_table_asset))

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                               output the job definition                                │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    return dg.Definitions(
        assets=[delta_table_asset, compact_and_vacuum_asset],
        jobs=[asset_job, compact_and_vacuum_job],
        sensors=[sensor],
        asset_checks=asset_checks,
        schedules=schedules,
    )
