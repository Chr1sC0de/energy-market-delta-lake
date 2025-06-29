from polars import Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int263_v4_lng_monitor_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int263_v4_lng_monitor_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "allocated_market_stock": Int64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas Date data generated e.g. 02 Feb 2001",
    "allocated_market_stock": "Sum of Allocated Market LNG Stock Holding (tonnes) Sum of participant and AEMO Allocated stock holding excluding participant ID 14 GasNet.",
    "current_date": "Date and Time report produced e.g. 29 Jun 2007 01:23:45",
}

report_purpose = """
This report is one of a number of reports produced to provide market information about the daily total LNG reserves held by
AEMO and all Market participants.

This public report displays the sum of LNG reserves (in tonnes) held for each day for the past 60 days.

Each report contains daily data for the last 60 days.
The LNG stock reported excludes the status of BOC operations on AEMO's stock holding.
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


definition_builder = definition_builder_factory(
    report_purpose,
    table_schema,
    schema_descriptions,
    primary_keys,
    upsert_predicate,
    s3_table_location,
    s3_prefix,
    s3_file_glob,
    table_name,
    group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
)

definitions_list.append(definition_builder.build())
