from polars import Float64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int128_v4_actual_linepack_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int128_v4_actual_linepack_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "commencement_datetime",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "commencement_datetime": String,
    "actual_linepack": Float64,
    "current_date": String,
}

schema_descriptions = {
    "commencement_datetime": "Commencement date and time (e.g. 25 Apr 2007 1:00:00)",
    "actual_linepack": "Energy value representing the physical linepack",
    "current_date": "Date and time report produced (e.g. 30 Jun 2007 01:23:56)",
}

report_purpose = """
This report provides information on changes in physical linepack over a 3-day period, and can be used by Participants as an
input into their forecasting and trading activities.

Note the information in this report is derived from real-time gas pressure data and does not relate to the scheduled linepack
values, as the scheduled linepack is a relative value.

It is also important to recognise that this report contains details about the system's physical linepack and is not the settlement
linepack, which is a financial balancing concept not related in any way to the physical linepack in the system on each day.

Participants may use this report to make assumptions about the physical capabilities of the system when correlated with
weather, type of day and other variables that impact on demand.

Each report provides hourly linepack quantities for the current and previous 2 gas days.

Reports are produced as operational schedules are approved, with information about the linepack movements for the current
gas day becoming progressively more complete in the course of the day. It follows, therefore, that the number of rows in an
INT128 report will increase over the course of the day.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"
