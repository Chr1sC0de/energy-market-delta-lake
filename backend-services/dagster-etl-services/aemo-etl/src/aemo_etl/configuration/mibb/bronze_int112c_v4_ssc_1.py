from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int112c_v4_ssc_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int112c_v4_ssc_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "supply_source",
    "gas_date",
    "ti",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "supply_source": String,
    "gas_date": String,
    "ssc_id": Int64,
    "ti": Int64,
    "hourly_constraint": Int64,
    "mod_datetime": String,
    "current_date": String,
}

schema_descriptions = {
    "supply_source": "Name of the constrained supply source",
    "gas_date": "Dates that mark the boundary of the application of the constraint (e.g. 27 Jun 2011)",
    "ssc_id": "Id of the Constraint",
    "ti": "Time interval 1-24 (hour of the gas day)",
    "hourly_constraint": "1 value for each hour of the gas day, Set to 1 if hourly constraint is applied. 0 if hourly constraint has not been applied",
    "mod_datetime": "Creation/modification time stamp (e.g. 07 Jun 2011 08:01:23)",
    "current_date": "Date and time the report was produced (e.g. 30 Jun 2011 1:23:56)",
}

report_purpose = """
This report contains information regarding any supply and demand point constraints (SDPCs) that are current in the
scheduling processes used in the DTS. These constraints are part of the configuration of the network that can be manually set
by the AEMO Schedulers and form one of the inputs to the schedule generation process. This report contains supply point
constraints, which selectively constrain injection bids at system injection points where the facility operator has registered
multiple supply sources.

Traders can use this information to understand the network-based restrictions that will constrain their ability to offer or
withdraw gas in the market on a given day. Note these constraints can be applied intraday and reflect conditions from a point in
time.

A report is produced each time an operational schedule (OS) is approved by AEMO. Therefore it is expected that each day
there will be at least 9 of these reports issued, with any additional ad hoc schedules also triggering this report:
- 5 being for the standard current gas day schedules
- 3 being for the standard 1-day ahead schedules
- 1 being for the standard 2 days ahead schedule

Each report contains details of the SSCs that have applied to schedules previously run:
- on the previous gas day
- for the current gas day
- for the next 2 gas days

Each SSC has a unique identifier and applies to a single injection MIRN.
Each row in the report contains details of one SSC for one hour of the gas day, with hourly intervals commencing from the start
of the gas day. That is, the first row for an SSC relates to 06:00 AM.

This report will contain 24 rows for each SSC for each gas day reported.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
