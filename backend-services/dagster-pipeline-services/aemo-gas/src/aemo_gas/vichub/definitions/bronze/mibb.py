from collections.abc import Callable
from typing import Any

import dagster as dg
from dagster_aws.s3 import S3Resource
from pydantic_core.core_schema import tagged_union_schema

from aemo_gas import utils
from aemo_gas.configurations import LANDING_BUCKET
from aemo_gas.vichub import assets
from aemo_gas.vichub.definitions.bronze import config
from configurations.parameters import DEVELOPMENT_LOCATION


def factory(
    *,
    group_name: str,
    key_prefix: list[str],
    name: str,
    schema: dict[str, type],
    search_prefix: str,
    io_manager_key: str,
    bucket: str = LANDING_BUCKET,
    description: str | None = None,
    metadata: dict[str, Any] | None = None,
    retention_hours: int = 0,
    cron_schedule: str | None = None,
    execution_timezone: str = "Australia/Melbourne",
    check_factories: list[Callable[[dg.AssetsDefinition], dg.AssetChecksDefinition]]
    | None = None,
    job_tags: dict[str, Any] | None = None,
) -> dg.Definitions:
    delta_table = assets.bronze.mibb.factory.delta_table(
        group_name=group_name,
        key_prefix=key_prefix,
        name=name,
        schema=schema,
        search_prefix=search_prefix,
        io_manager_key=io_manager_key,
        bucket=bucket,
        description=description,
        metadata=metadata,
    )
    update_metadata = assets.bronze.mibb.factory.update_metadata(
        delta_table,
        group_name=f"{group_name}__CLEANUP",
        key_prefix=key_prefix + [name],
        name=name,
        search_prefix=search_prefix,
        bucket=bucket,
    )
    cleanup_files = assets.bronze.mibb.factory.cleanup_files(
        update_metadata,
        group_name=f"{group_name}__CLEANUP",
        key_prefix=key_prefix + [name],
        name=name,
        search_prefix=search_prefix,
        bucket=bucket,
    )
    compact_and_vacuum = assets.bronze.mibb.factory.compact_and_vacuum(
        table_definition=delta_table,
        group_name=f"{group_name}__OPTIMIZATION",
        key_prefix=key_prefix + [name],
        table_name=name,
        retention_hours=retention_hours,
    )

    asset_job = dg.define_asset_job(
        name=f"{name}_etl_job",
        selection=f"key:{'/'.join(key_prefix)}/{name}",
        tags=job_tags,
    )

    compact_and_vacuum_job = dg.define_asset_job(
        name=f"{name}_compact_and_vacuum",
        selection=f"key:{'/'.join(key_prefix)}/{name}/compact_and_vacuum",
    )
    schedules = []

    if cron_schedule is not None:
        compact_and_vacuum_schedule = dg.ScheduleDefinition(
            job=compact_and_vacuum_job,
            cron_schedule=cron_schedule,
            default_status=(
                dg.DefaultScheduleStatus.STOPPED
                if DEVELOPMENT_LOCATION == "local"
                else dg.DefaultScheduleStatus.RUNNING
            ),
            execution_timezone=execution_timezone,
        )
        schedules.append(compact_and_vacuum_schedule)

    @dg.sensor(
        name=f"{name}_s3_sensor",
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
                job_name=f"{name}_etl_job", statuses=[dg.DagsterRunStatus.STARTED]
            )
        )
        if len(run_records) == 0:
            s3_object_keys = utils.get_s3_object_keys_op_from_prefix(
                s3_resource, bucket, search_prefix
            )
            if len(s3_object_keys) > 0:
                yield dg.RunRequest()
            else:
                yield dg.SkipReason("No new files found")
        else:
            yield dg.SkipReason("Run already in process")

    asset_checks = []

    if check_factories is not None:
        for factory in check_factories:
            asset_checks.append(factory(delta_table))

    return dg.Definitions(
        assets=[delta_table, update_metadata, cleanup_files, compact_and_vacuum],
        jobs=[asset_job, compact_and_vacuum_job],
        sensors=[sensor],
        asset_checks=asset_checks,
        schedules=schedules,
    )


# create all the definitions based off the factory and the config
all = [factory(**c) for c in config.all]
