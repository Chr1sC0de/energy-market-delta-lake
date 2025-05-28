from functools import partial

from polars import Date, Datetime, Float64, Int64, String

from aemo_etl.configuration import BRONZE_BUCKET, LANDING_BUCKET
from aemo_etl.definitions.utils import asset_check_factory, post_process_hook
from aemo_etl.factory.definition import (
    GetMibbReportFromS3FilesDefinitionBuilder,
)
from aemo_etl.parameter_specification import (
    PolarsDataFrameReadScanDeltaParamSpec,
    PolarsDataFrameWriteDeltaParamSpec,
    PolarsDeltaLakeMergeParamSpec,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import get_metadata_schema, newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_vicgas_int037b_indicative_market_price"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int037b*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["demand_type_name", "transmission_id"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and"
)

table_schema = {
    "demand_type_name": String,
    "price_value_gst_ex": Float64,
    "transmission_group_id": Int64,
    "schedule_type_id": String,
    "transmission_id": Int64,
    "gas_date": Date,
    "approval_datetime": Datetime(time_unit="ms", time_zone="Australia/Melbourne"),
    "current_date": Datetime(time_unit="ms", time_zone="Australia/Melbourne"),
}

schema_descriptions = {
    "demand_type_name": """Normal Uses Demand forecast used by operational schedule
10% exceedence means the estimated market price is based on
10 % exceedance of the forecast demand level.
90% exceedence means the estimated market price if the demand
is 90 % of the the forecast demand.""",
    "price_value_gst_ex": "Forecast market price ($) for BoD Scheduling horizon of the gas day in question",
    "transmission_group_id": "Link to the related day(s) ahead operational schedule",
    "schedule_type_id": "MS (Market Schedule Id)",
    "transmission_id": "Schedule number these prices are related to",
    "gas_date": "e.g. 30 Jun 2007",
    "approval_datetime": "Date and time the schedule was approved 29 Jun 2007 01:23:45",
    "current_date": "Date and time Report Produced e.g. 29 Jun 2007 01:23:45",
}

report_purpose = """
This report is to indicate what the prices are for the day and what they are predicted to be for the next two days.

Market participants may wish to use this information to estimate pricing for the following two days.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                register the definition                                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


definition_builder = GetMibbReportFromS3FilesDefinitionBuilder(
    key_prefix=["bronze", "aemo", "vicgas"],
    io_manager_key="s3_polars_deltalake_io_manager",
    asset_metadata={
        "destription": report_purpose,
        "dagster/column_schema": get_metadata_schema(table_schema, schema_descriptions),
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
    group_name="aemo",
    name=table_name,
    s3_source_bucket=LANDING_BUCKET,
    s3_source_prefix=s3_prefix,
    s3_file_glob=s3_file_glob,
    s3_target_bucket=BRONZE_BUCKET,
    s3_target_prefix=s3_prefix,
    table_schema=table_schema,
    check_factories=[partial(asset_check_factory, primary_keys=primary_keys)],
    table_post_process_hook=partial(
        post_process_hook, primary_keys=primary_keys, table_schema=table_schema
    ),
)

definitions_list.append(definition_builder.build())
