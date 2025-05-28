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


table_name = "bronze_vicgas_int047_heating_values"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int047*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "version_id",
    "event_datetime",
    "heating_value_zone",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and"
)

table_schema = {
    "version_id": Int64,
    "gas_date": Date,
    "event_datetime": Datetime(time_unit="ms", time_zone="Australia/Melbourne"),
    "event_interval": Int64,
    "heating_value_zone": Int64,
    "heating_value_zone_desc": String,
    "initial_heating_value": Float64,
    "current_heating_value": Float64,
    "current_date": Datetime(time_unit="ms", time_zone="Australia/Melbourne"),
}

schema_descriptions = {
    "version_id": "Version of Heating Values.",
    "gas_date": "Starting hour of gas day being reported as 30 Jun 2007",
    "event_datetime": "Start of hour for which values applies (e.g. 29 Jun 2007 06:00:00)",
    "event_interval": """hour interval of the day
6:00 AM = 1
7:00 AM = 2
5:00 AM = 24""",
    "heating_value_zone": "Heating value zone id number",
    "heating_value_zone_desc": "Heating value zone name",
    "initial_heating_value": "Heating value (GJ/1000 m(3)) rounded to 2 decimal places.",
    "current_heating_value": "Heating valiue (GJ/1000m(3)) rounded r=to 2 decimal places",
    "current_date": "Date and Time Report Produced. 30 Jun 2007 06:00:00.",
}

report_purpose = """
This report provides the hourly calorific value of gas delivered for each heating value zone in Victoria.

This information allows AEMO and other Market participant to convert the volumetric measurements taken at interval meters
into units of energy for various purposes including:
- operation of the gas system
- settlement of the wholesale market
- billing of interval metered retail customers.

The initial_heating_value is the first obtained, and may be superseded in the course of the gas day date and during the 7 day
reporting window for INT047. Therefore, the current_heating_value is in most cases the more accurate data value to use. The
current_heating_value shown for yesterday is more likely to undergo revision than the current_heating_value shown for 7 days
ago.

It should be noted that even after 7 days, the HV may still be revised for settlement purposes. In these circumstances a
Heating Value Data Correction notice for the (preceding) month will be published on the AEMO website and corrections for
individual meters sent to the energy values provider, DMS.

This report is generated daily. Each report displays the hourly HV for each heating value zone in Victoria over the
previous 7 gas days (not including the current gas day).

Each row in the report provides the 'initial' and 'current' HVs:
- for a particular hour interval
- for a particular heating value zone
- for a specific gas day date
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
