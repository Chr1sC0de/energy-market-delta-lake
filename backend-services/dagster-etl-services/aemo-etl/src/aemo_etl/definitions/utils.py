from functools import partial
from typing import Iterable, Mapping

from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    AssetsDefinition,
    MetadataValue,
    asset_check,
)
from polars import (
    DataType,
    Datetime,
    LazyFrame,
    Schema,
    col,
    int_range,
)
from polars import (
    len as len_,
)

from aemo_etl.configuration import BRONZE_BUCKET, LANDING_BUCKET
from aemo_etl.factory.definition import (
    GetMibbReportFromS3FilesDefinitionBuilder,
)
from aemo_etl.parameter_specification import (
    PolarsDataFrameReadScanDeltaParamSpec,
    PolarsDataFrameWriteDeltaParamSpec,
    PolarsDeltaLakeMergeParamSpec,
)
from aemo_etl.util import get_lazyframe_num_rows, get_metadata_schema

"""
Abbreviation Key:
- vic, qld, sa = state abbreviations
- dwm = Declared Wholesale Market
- sched = scheduling
- ws = wholesale
- settle = settlements
- meter = metering
- ret = retail
- rpt / rpts = report(s)
- dets = details
"""

VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS = "vic_dwm_sched_rpts"
VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS = "vic_ws_settle_meter_rpts"

VICTORIAN_GAS_RETAIL_REPORTS_DETAILS = "vic_gas_ret_rpt_dets"
QUEENSLAND_GAS_RETAIL_REPORT_DETAILS = "qld_gas_ret_rpt_dets"
SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS = "sa_gas_ret_rpts"

ECGS_REPORTS = "ecgs_rpts"


def post_process_hook(
    _: AssetExecutionContext,
    df: LazyFrame,
    *,
    primary_keys: list[str],
) -> LazyFrame:
    schema = df.collect_schema()
    if len(schema) > 0:
        datetime_column_name = None
        if "current_date" in schema:
            datetime_column_name = "current_date"
        elif "current_datetime" in schema:
            datetime_column_name = "current_datetime"

        if datetime_column_name is not None:
            df = df.with_columns(
                int_range(len_())
                .over(
                    *primary_keys,
                    order_by=col(datetime_column_name).str.strptime(
                        Datetime, "%d %b %Y %H:%M:%S"
                    ),
                    descending=True,
                )
                .alias("row_num")
            )
        else:
            df = df.with_columns(
                int_range(len_())
                .over(
                    *primary_keys,
                    descending=True,
                )
                .alias("row_num")
            )

        df = df.filter(col("row_num") == 0).drop("row_num")

    return df


def asset_check_factory(
    asset_definition: AssetsDefinition, *, primary_keys: Iterable[str]
):
    @asset_check(
        asset=asset_definition,
        name="check_primary_keys_are_unique",
    )
    def check_primary_keys_are_unique(input_df: LazyFrame):
        return AssetCheckResult(
            passed=bool(
                get_lazyframe_num_rows(input_df)
                == get_lazyframe_num_rows(input_df.select(*primary_keys).unique())
            )
        )

    return check_primary_keys_are_unique


def definition_builder_factory(
    report_purpose: str,
    table_schema: Mapping[str, type[DataType]] | Schema,
    schema_descriptions: Mapping[str, str],
    primary_keys: list[str],
    upsert_predicate: str,
    s3_table_location: str,
    s3_prefix: str,
    s3_file_glob: str,
    table_name: str,
    group_name: str = "aemo",
    cpu: str = "512",
    memory: str = "2048",
) -> GetMibbReportFromS3FilesDefinitionBuilder:
    return GetMibbReportFromS3FilesDefinitionBuilder(
        job_tags={
            "ecs/cpu": cpu,
            "ecs/memory": memory,
        },
        key_prefix=["bronze", "aemo", "vicgas"],
        io_manager_key="s3_polars_deltalake_io_manager",
        asset_metadata={
            "dagster/column_schema": get_metadata_schema(
                table_schema, schema_descriptions
            ),
            "dagster/primary_keys": MetadataValue.json(primary_keys),
            "s3_polars_deltalake_io_manager_options": {
                "write_delta_options": PolarsDataFrameWriteDeltaParamSpec(
                    target=s3_table_location,
                    mode="merge",
                    delta_merge_options=PolarsDeltaLakeMergeParamSpec(
                        predicate=upsert_predicate,
                        source_alias="s",
                        target_alias="t",
                    ),
                ),
                "scan_delta_options": PolarsDataFrameReadScanDeltaParamSpec(
                    source=s3_table_location
                ),
            },
        },
        group_name=group_name,
        name=table_name,
        asset_description=report_purpose,
        s3_source_bucket=LANDING_BUCKET,
        s3_source_prefix=s3_prefix,
        s3_file_glob=s3_file_glob,
        s3_target_bucket=BRONZE_BUCKET,
        s3_target_prefix=s3_prefix,
        table_schema=table_schema,
        check_factories=[partial(asset_check_factory, primary_keys=primary_keys)],
        table_post_process_hook=partial(
            post_process_hook,
            primary_keys=primary_keys,
        ),
    )
