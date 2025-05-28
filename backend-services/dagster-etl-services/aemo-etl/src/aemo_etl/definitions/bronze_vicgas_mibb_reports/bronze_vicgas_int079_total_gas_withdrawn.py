from functools import partial

from polars import Date, Datetime, Float64, String

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


table_name = "bronze_vicgas_int079_total_gas_withdrawn"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int079*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["gas_date"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and"
)

table_schema = {
    "gas_date": Date,
    "unit_id": String,
    "qty": Float64,
    "qty_reinj": Float64,
    "current_date": Datetime(time_unit="ms", time_zone="Australia/Melbourne"),
}

schema_descriptions = {
    "gas_date": "Gas day being reported e.g. 30 Jun 2007",
    "unit_id": "Unit of measurement (GJ)",
    "qty": "Total Gas withdrawn Daily",
    "qty_reinj": "Total Net Gas withdrawn Daily (Withdrawals less re-injections)",
    "current_date": "Date and time report produced e.g. 30 Jun 2007 01:23:45",
}

report_purpose = """
This report provides a view of the total quantity of gas that is flowing in the DTS on a given day. Retailers may use this
information as an input to their demand forecasts or to estimate their market share. Participants must be aware that the data is
of operational quality and not settlement quality, and is therefore subject to revision. The data revisions can be significant and
is dependent on a number of factors, including, but not limited to, the availability of telemetered data and system availability.

The report contains metering data for the prior gas day. The data is of operational quality and is subject to substitution and
replacement.

In the context of this report, re-injections represent the flow to the transmission pipeline system (TPS) from the distribution
pipeline system (DPS) at times of low pressure and low demand. The first quantity reported, "qty", includes re-injections.

It should be noted that for a single day, multiple entries can exist. Initial uploads of data for a given date can be incomplete
when it is first reported and updates arriving later into AEMO's system will cause multiple entries to exist, Participants should
combine the reports to provide a daily total.

Each report contains details of the withdrawals that occurred on the previous seven gas days. That is, the INT079 report for
the gas date of 11-August will contain withdrawal quantities for the dates 4 to 10 August inclusive.

The data in this report can have a significant number of substituted values and it is possible for the data to change from day to
day as they are updated through the 7-day reporting window.
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
        "description": report_purpose,
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
