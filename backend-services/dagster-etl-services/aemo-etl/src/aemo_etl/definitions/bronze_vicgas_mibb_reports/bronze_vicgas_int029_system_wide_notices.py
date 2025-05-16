from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    AssetsDefinition,
    asset_check,
)
from polars import Datetime, Int64, LazyFrame, String, col

from aemo_etl.configuration import BRONZE_BUCKET, LANDING_BUCKET
from aemo_etl.factory.definition import (
    GetMibbReportFromS3FilesDefinitionBuilder,
)
from aemo_etl.parameter_specification import (
    PolarsDataFrameReadScanDeltaParamSpec,
    PolarsDataFrameWriteDeltaParamSpec,
    PolarsDeltaLakeMergeParamSpec,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import get_lazyframe_num_rows, get_metadata_schema


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_vicgas_int029a_system_wide_notices"

s3_prefix = "aemo/vicgas"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

table_schema = {
    "system_wide_notice_id": Int64,
    "critical_notice_flag": String,
    "system_message": String,
    "system_email_message": String,
    "notice_start_date": String,
    "notice_end_date": String,
    "url_path": String,
    "current_date": String,
}

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


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
    io_manager_key="s3_polars_deltalake_io_manager",
    asset_metadata={
        "dagster/column_schema": get_metadata_schema(table_schema),
        "s3_polars_deltalake_io_manager_options": {
            "write_delta_options": PolarsDataFrameWriteDeltaParamSpec(
                target=s3_table_location,
                mode="merge",
                delta_merge_options=PolarsDeltaLakeMergeParamSpec(
                    predicate="s.system_wide_notice_id = t.system_wide_notice_id",
                    source_alias="s",
                    target_alias="t",
                ),
            ),
            "scan_delta_options": PolarsDataFrameReadScanDeltaParamSpec(
                source=s3_table_location
            ),
        },
    },
    group_name="aemo",
    name=table_name,
    s3_source_bucket=LANDING_BUCKET,
    s3_source_prefix=s3_prefix,
    s3_file_glob="int029a*",
    s3_target_bucket=BRONZE_BUCKET,
    s3_target_prefix=s3_prefix,
    table_schema=table_schema,
    check_factories=[asset_check_factory],
    table_post_process_hook=post_process_hook,
)

definitions_list.append(definition_builder.build())
