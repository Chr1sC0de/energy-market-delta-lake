from typing import Any, Callable, Mapping

from dagster import (
    AssetChecksDefinition,
    AssetExecutionContext,
    AssetsDefinition,
    DagsterInstance,
    DagsterRunStatus,
    DefaultScheduleStatus,
    DefaultSensorStatus,
    Definitions,
    RunRequest,
    RunsFilter,
    ScheduleDefinition,
    SensorEvaluationContext,
    SkipReason,
    define_asset_job,
    sensor,
)
from dagster_aws.s3 import S3Resource
from polars import LazyFrame, Schema
from polars._typing import PolarsDataType

from aemo_etl.factory.asset import (
    compact_and_vacuum_dataframe_asset_factory,
    get_mibb_report_from_s3_files_asset_factory,
)
from aemo_etl.util import get_s3_object_keys_from_prefix_and_name_glob
from configurations.parameters import DEVELOPMENT_LOCATION


class GetMibbReportFromS3FilesDefinitionBuilder:
    s3_source_bucket: str
    s3_source_prefix: str
    s3_file_glob: str

    def __init__(
        self,
        io_manager_key: str,
        asset_metadata: dict[str, Any],
        group_name: str,
        key_prefix: list[str],
        name: str,
        s3_source_bucket: str,
        s3_source_prefix: str,
        s3_file_glob: str,
        s3_target_bucket: str,
        s3_target_prefix: str,
        table_schema: Mapping[str, PolarsDataType] | Schema,
        table_post_process_hook: (
            Callable[[AssetExecutionContext, LazyFrame], LazyFrame] | None
        ) = None,
        retention_hours: int = 0,
        check_factories: (
            list[Callable[[AssetsDefinition], AssetChecksDefinition]] | None
        ) = None,
        job_tags: dict[str, Any] | None = None,
        compact_and_vacuum_cron_schedule="45 23 * * *",
        execution_timezone="Australia/Melbourne",
    ):
        self.s3_source_bucket = s3_source_bucket
        self.s3_source_prefix = s3_source_prefix
        self.s3_file_glob = s3_file_glob

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                   create the assets                                    │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.table_asset = get_mibb_report_from_s3_files_asset_factory(
            group_name=group_name,
            name=name,
            key_prefix=key_prefix,
            metadata=asset_metadata,
            io_manager_key=io_manager_key,
            s3_source_bucket=s3_source_bucket,
            s3_source_prefix=s3_source_prefix,
            s3_source_file_glob=s3_file_glob,
            post_process_hook=table_post_process_hook,
        )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                          create the compact and vacuum asset                           │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.compact_and_vacuum_asset = compact_and_vacuum_dataframe_asset_factory(
            group_name=f"{group_name}__optimize",
            s3_target_bucket=s3_target_bucket,
            s3_target_prefix=s3_target_prefix,
            s3_target_table_name=name,
            key_prefix=key_prefix + ["optimize"],
            dependant_definitions=[self.table_asset],
            retention_hours=retention_hours,
        )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                create the asset checks                                 │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.asset_checks = []
        if check_factories is not None:
            for check_factory in check_factories:
                self.asset_checks.append(check_factory(self.table_asset))

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                      create jobs                                       │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.table_asset_job = define_asset_job(
            f"{name}_job",
            selection=[self.table_asset],
            tags=job_tags,
        )

        self.table_asset_compact_and_vacuum_job = define_asset_job(
            name=f"{name}_compact_and_vacuum_job",
            selection=[self.compact_and_vacuum_asset],
        )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                  create the schedules for the compact and vacuum job                   │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.schedules = []
        if compact_and_vacuum_cron_schedule is not None:
            self.compact_and_vacuum_schedule = ScheduleDefinition(
                job=self.table_asset_compact_and_vacuum_job,
                cron_schedule=compact_and_vacuum_cron_schedule,
                default_status=(
                    DefaultScheduleStatus.STOPPED
                    if DEVELOPMENT_LOCATION == "local"
                    else DefaultScheduleStatus.RUNNING
                ),
                execution_timezone=execution_timezone,
            )
            self.schedules.append(self.compact_and_vacuum_schedule)

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                create the asset sensor                                 │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        def has_job_failed(instance: DagsterInstance, job_name: str) -> bool:
            runs = instance.get_runs(limit=1, filters=RunsFilter(job_name=job_name))
            if runs:
                return runs[0].status.value == "FAILURE"
            return False

        @sensor(
            name=f"{name}_s3_sensor",
            job=self.table_asset_job,
            minimum_interval_seconds=30,
            default_status=(
                DefaultSensorStatus.STOPPED
                if DEVELOPMENT_LOCATION == "local"
                else DefaultSensorStatus.RUNNING
            ),  # Sensor is turned on by default
        )
        def asset_sensor(context: SensorEvaluationContext, s3_resource: S3Resource):
            # Find runs of the same job that are currently running
            run_records = context.instance.get_run_records(
                RunsFilter(
                    job_name=f"{name}_job",
                    statuses=[
                        DagsterRunStatus.QUEUED,
                        DagsterRunStatus.NOT_STARTED,
                        DagsterRunStatus.STARTING,
                        DagsterRunStatus.STARTED,
                    ],
                )
            )

            # kill the sensor if the job has failed
            if has_job_failed(context.instance, self.table_asset_job.name):
                return SkipReason("Job previously failed. Sensor paused logic.")

            if len(run_records) == 0:
                # only run the etl job if the public files have been downloaded
                s3_object_keys = get_s3_object_keys_from_prefix_and_name_glob(
                    s3_client=s3_resource.get_client(),
                    s3_bucket=s3_source_bucket,
                    s3_prefix=s3_source_prefix,
                    s3_file_glob=s3_file_glob,
                    case_insensitive=True,
                )
                if len(s3_object_keys) > 0:
                    yield RunRequest()
                else:
                    yield SkipReason("No new files found")
            else:
                yield SkipReason("Run already in process")

        self.asset_sensor = asset_sensor

    def build(self) -> Definitions:
        return Definitions(
            assets=[self.table_asset, self.compact_and_vacuum_asset],
            jobs=[self.table_asset_job, self.table_asset_compact_and_vacuum_job],
            sensors=[self.asset_sensor],
            asset_checks=self.asset_checks,
            schedules=self.schedules,
        )
