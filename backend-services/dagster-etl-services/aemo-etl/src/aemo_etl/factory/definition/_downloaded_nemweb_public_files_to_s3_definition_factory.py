from io import BytesIO
from time import time
from typing import Callable, Self

from dagster import (
    DefaultScheduleStatus,
    Definitions,
    OpExecutionContext,
    ScheduleDefinition,
    define_asset_job,
)
from deltalake.exceptions import TableNotFoundError
from polars import LazyFrame, col, lit, read_delta
from polars import len as len_

from aemo_etl.configuration import BRONZE_BUCKET, Link
from aemo_etl.factory.asset import (
    compact_and_vacuum_dataframe_asset_factory,
)
from aemo_etl.factory.asset._download_nemweb_public_files_to_s3_asset_factory import (
    download_nemweb_public_files_to_s3_asset_factory,
)
from aemo_etl.factory.check import duplicate_row_check_factory
from aemo_etl.parameter_specification import (
    PolarsDataFrameReadScanDeltaParamSpec,
    PolarsDataFrameWriteDeltaParamSpec,
    PolarsDeltaLakeMergeParamSpec,
)
from aemo_etl.util import newline_join
from aemo_etl.configuration import DEVELOPMENT_LOCATION

# pyright: reportUnknownMemberType=false, reportMissingTypeStubs=false


class InMemoryCachedLinkFilter:
    table_path: str
    _cache: LazyFrame | None

    def __init__(self, table_path: str, ttl_seconds: int):
        self.table_path = table_path
        self.ttl_seconds = ttl_seconds
        self._cache = None

    def set(self) -> Self:
        self._cache = read_delta(self.table_path).lazy()
        self.cache_time = time()
        return self

    def get(self) -> LazyFrame:
        if self._cache is None:
            self.set()
        else:
            if time() - self.cache_time > self.ttl_seconds:
                self.set()

        assert self._cache is not None, f"cache for {self.table_path} has not beeen set"

        return self._cache

    def __call__(self, _: OpExecutionContext, link: Link) -> bool:
        try:
            df = self.get()
            search_df = df.filter(
                col("source_absolute_href") == lit(link.source_absolute_href),
                col("source_upload_datetime")
                == lit(link.source_upload_datetime).cast(
                    df.collect_schema()["source_upload_datetime"]
                ),
            )
            if search_df.select(len_()).collect().item() > 0:
                return False
            return True
        except TableNotFoundError:
            return True


def download_nemweb_public_files_to_s3_definition_factory(
    group_name: str,
    key_prefix: list[str],
    name: str,
    root_relative_href: str,
    s3_landing_bucket: str,
    s3_landing_prefix: str,
    s3_target_prefix: str,
    link_filter: Callable[[OpExecutionContext, Link], bool] | None = None,
    get_buffer_from_link_hook: Callable[[Link], BytesIO] | None = None,
    override_get_links_fn: Callable[[OpExecutionContext], list[Link]] | None = None,
    vacuum_retention_hours: int = 0,
    job_tags: dict[str, str] = {
        "ecs/cpu": "512",
        "ecs/memory": "2048",
    },
    job_schedule_cron: str = "5 * * * *",  # run every day 5 minutes past the hour,
    compact_and_vacuum_schdule_cron: str = "00 23 * * *",  # run at every 11 pm
) -> Definitions:
    table_path = f"s3://{BRONZE_BUCKET}/{s3_target_prefix}/{name}"

    default_link_filter = InMemoryCachedLinkFilter(table_path, 900)

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                                   define the assets                                    │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    if link_filter is None:
        link_filter = default_link_filter
    else:
        link_filter = link_filter

    download_nemweb_public_files_to_s3_asset = download_nemweb_public_files_to_s3_asset_factory(
        group_name=group_name,
        key_prefix=key_prefix,
        name=name,
        io_manager_key="s3_polars_deltalake_io_manager",
        nemweb_relative_href=root_relative_href,
        s3_source_bucket=s3_landing_bucket,
        s3_source_prefix=s3_landing_prefix,
        link_filter=link_filter,
        get_buffer_from_link_hook=get_buffer_from_link_hook,
        override_get_links_fn=override_get_links_fn,
        out_metadata={
            "s3_polars_deltalake_io_manager_options": {
                "write_delta_options": PolarsDataFrameWriteDeltaParamSpec(
                    target=table_path,
                    mode="merge",
                    delta_merge_options=PolarsDeltaLakeMergeParamSpec(
                        predicate=newline_join(
                            "s.source_absolute_href = t.source_absolute_href",
                            "and s.source_upload_datetime = t.source_upload_datetime",
                        ),
                        source_alias="s",
                        target_alias="t",
                    ),
                ),
                "scan_delta_options": PolarsDataFrameReadScanDeltaParamSpec(
                    source=table_path
                ),
            }
        },
    )

    compact_and_vacuum_asset = compact_and_vacuum_dataframe_asset_factory(
        group_name="aemo__optimize",
        s3_target_bucket=BRONZE_BUCKET,
        s3_target_prefix=s3_target_prefix,
        s3_target_table_name=name,
        key_prefix=["optimize"] + key_prefix,
        retention_hours=vacuum_retention_hours,
        dependant_definitions=[download_nemweb_public_files_to_s3_asset],
    )

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                                create the asset checks                                 │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    download_nemweb_public_files_to_s3_asset_check = duplicate_row_check_factory(
        assets_definition=download_nemweb_public_files_to_s3_asset,
        check_name="check_for_duplicate_rows",
        primary_key=[
            "source_absolute_href",
            "source_upload_datetime",
            "target_s3_name",
            "target_ingested_datetime",
        ],
        description="""
            Check that row group:

                ["source_absolute_href","source_upload_datetime","target_s3_name","target_ingested_datetime"] 

            is unique
            """,
    )

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                                      create jobs                                       │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    asset_job_name = f"asset_{name}_job"
    compact_and_vacuum_job_name = f"compact_and_vacuum_{name}_job"

    download_nemweb_public_files_to_s3_job = define_asset_job(
        asset_job_name,
        selection=[download_nemweb_public_files_to_s3_asset],
        tags=job_tags,
    )

    download_nemweb_public_files_to_s3_compact_and_vacuum_job = define_asset_job(
        name=compact_and_vacuum_job_name,
        selection=[compact_and_vacuum_asset],
    )

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                 create a schedule for the downloaded_public_files_job                  │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    download_nemweb_public_files_to_s3_schedule = ScheduleDefinition(
        name=f"job_schedule_{name}",
        job=download_nemweb_public_files_to_s3_job,
        cron_schedule=job_schedule_cron,  # run every 5 minutes past the hour
        default_status=(
            DefaultScheduleStatus.STOPPED
            if DEVELOPMENT_LOCATION == "local"
            else DefaultScheduleStatus.RUNNING
        ),
    )

    download_nemweb_public_files_to_s3_compact_and_vacuum_schedule = ScheduleDefinition(
        name=f"job_schedule_compact_and_vacuum_{name}",
        job=download_nemweb_public_files_to_s3_compact_and_vacuum_job,
        cron_schedule=compact_and_vacuum_schdule_cron,
        execution_timezone="Australia/Melbourne",
        default_status=(
            DefaultScheduleStatus.STOPPED
            if DEVELOPMENT_LOCATION == "local"
            else DefaultScheduleStatus.RUNNING
        ),
    )

    #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
    #     │                           generate the required definitions                            │
    #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

    definition = Definitions(
        assets=[download_nemweb_public_files_to_s3_asset, compact_and_vacuum_asset],
        asset_checks=[download_nemweb_public_files_to_s3_asset_check],
        jobs=[
            download_nemweb_public_files_to_s3_job,
            download_nemweb_public_files_to_s3_compact_and_vacuum_job,
        ],
        schedules=[
            download_nemweb_public_files_to_s3_schedule,
            download_nemweb_public_files_to_s3_compact_and_vacuum_schedule,
        ],
    )
    return definition
