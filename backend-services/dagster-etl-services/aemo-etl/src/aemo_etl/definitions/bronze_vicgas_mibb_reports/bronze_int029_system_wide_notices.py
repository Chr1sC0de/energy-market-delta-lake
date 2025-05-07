from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    AssetsDefinition,
    asset_check,
)
from polars import Datetime, Int64, LazyFrame, String, col

from aemo_etl.configuration import BRONZE_BUCKET, LANDING_BUCKET
from aemo_etl.factory.asset import (
    MetadataBuilder,
)
from aemo_etl.factory.definition import (
    GetMibbReportFromS3FilesDefinitionBuilder,
)
from aemo_etl.register import definitions_list
from aemo_etl.util import get_lazyframe_num_rows, newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                 define the user hooks                                  │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


def post_process_hook(_: AssetExecutionContext, df: LazyFrame) -> LazyFrame:
    return (
        df.filter(
            (
                col("current_date").str.strptime(Datetime, "%d %b %Y %H:%M:%S")
                == col("current_date").str.strptime(Datetime, "%d %b %Y %H:%M:%S").max()
            ).over("system_wide_notice_id")
        )
        .collect()
        .lazy()
    )


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                define the asset checks                                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


def asset_check_factory(asset_definition: AssetsDefinition):
    @asset_check(
        asset=asset_definition,
        name="check_unique_system_wide_notice_ids",
    )
    def check_unique_system_wide_notice_ids(input_df: LazyFrame):
        return AssetCheckResult(
            passed=bool(
                get_lazyframe_num_rows(input_df)
                == get_lazyframe_num_rows(
                    input_df.select("system_wide_notice_id").unique()
                )
            )
        )

    return check_unique_system_wide_notice_ids


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                register the definition                                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

definition_builder = GetMibbReportFromS3FilesDefinitionBuilder(
    key_prefix=["bronze", "aemo", "vicgas"],
    io_manager_key="bronze_delta_polars_io_manager",
    asset_metadata={
        "merge_predicate": newline_join(
            "s.system_wide_notice_id = t.system_wide_notice_id",
        ),
        "schema": "aemo_vicgas",
    },
    group_name="aemo",
    name="bronze_int029a_system_wide_notices",
    s3_source_bucket=LANDING_BUCKET,
    s3_source_prefix="aemo_vicgas",
    s3_file_glob="int029a*",
    s3_target_bucket=BRONZE_BUCKET,
    s3_target_schema="aemo_vicgas",
    df_schema={
        "system_wide_notice_id": Int64,
        "critical_notice_flag": String,
        "system_message": String,
        "system_email_message": String,
        "notice_start_date": String,
        "notice_end_date": String,
        "url_path": String,
        "current_date": String,
    },
    check_factories=[asset_check_factory],
    table_post_process_hook=post_process_hook,
    table_context_metadata_builder=MetadataBuilder(
        table_uri=f"s3://{BRONZE_BUCKET}/{'aemo_vicgas'}/{'bronze_delta_polars_io_manager'}"
    ),
)

definitions_list.append(definition_builder.build())
