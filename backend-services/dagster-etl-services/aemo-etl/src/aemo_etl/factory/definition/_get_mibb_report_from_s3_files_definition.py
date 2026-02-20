from logging import Logger
from typing import Any, Callable, Mapping

from dagster import (
    AssetChecksDefinition,
    AssetExecutionContext,
    AssetsDefinition,
    AutomationCondition,
    Definitions,
    define_asset_job,
)
from polars import LazyFrame, Schema
from polars._typing import PolarsDataType

from aemo_etl.factory.asset import (
    compact_and_vacuum_dataframe_asset_factory,
    get_df_from_s3_files_asset_factory,
)


class GetMibbReportFromS3FilesDefinitionBuilder:
    s3_source_bucket: str
    s3_source_prefix: str
    s3_file_glob: str
    s3_target_bucket: str
    s3_target_prefix: str

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
        process_object_hook: Callable[[Logger | None, bytes], LazyFrame] | None = None,
        preprocess_hook: Callable[[Logger | None, LazyFrame], LazyFrame] | None = None,
        table_post_process_hook: (
            Callable[[AssetExecutionContext, LazyFrame], LazyFrame] | None
        ) = None,
        retention_hours: int | None = None,
        check_factories: (
            list[Callable[[AssetsDefinition], AssetChecksDefinition]] | None
        ) = None,
        job_tags: dict[str, Any] | None = None,
        execution_timezone: str = "Australia/Melbourne",
        compact_and_vacuum_schedule: str = "@weekly",
        asset_description: str | None = None,
    ) -> None:
        self.s3_source_bucket = s3_source_bucket
        self.s3_source_prefix = s3_source_prefix
        self.s3_file_glob = s3_file_glob
        self.s3_target_bucket = s3_target_bucket
        self.s3_target_prefix = s3_target_prefix

        self.table_asset = get_df_from_s3_files_asset_factory(
            group_name=group_name,
            name=name,
            key_prefix=key_prefix,
            process_object_hook=process_object_hook,
            metadata=asset_metadata,
            io_manager_key=io_manager_key,
            s3_source_bucket=s3_source_bucket,
            s3_source_prefix=s3_source_prefix,
            s3_source_file_glob=s3_file_glob,
            post_process_hook=table_post_process_hook,
            preprocess_hook=preprocess_hook,
            table_schema=table_schema,
            description="" if asset_description is None else asset_description,
        )

        self.compact_and_vacuum_asset = compact_and_vacuum_dataframe_asset_factory(
            group_name="aemo__optimize",
            s3_target_bucket=s3_target_bucket,
            s3_target_prefix=s3_target_prefix,
            s3_target_table_name=name,
            key_prefix=["optimize"] + key_prefix,
            dependant_definitions=[self.table_asset],
            retention_hours=retention_hours,
            automation_condition=AutomationCondition.on_cron(
                compact_and_vacuum_schedule
            ),
        )

        self.asset_checks = []
        if check_factories is not None:
            for check_factory in check_factories:
                self.asset_checks.append(check_factory(self.table_asset))

        self.table_asset_job = define_asset_job(
            f"asset_{name}_job",
            selection=[self.table_asset],
            tags=job_tags,
        )

    def build(self) -> Definitions:
        return Definitions(
            assets=[self.table_asset, self.compact_and_vacuum_asset],
            jobs=[self.table_asset_job],
            asset_checks=self.asset_checks,
        )
