from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int236_v4_operational_meter_readings_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int236_v4_operational_meter_readings_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "direction_code_name",
    "direction",
    "commencement_datetime",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "gas_date": String,
    "direction_code_name": String,
    "direction": String,
    "commencement_datetime": String,
    "termination_datetime": String,
    "quantity": Float64,
    "time_sort_order": Int64,
    "mod_datetime": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "gas_date": "Starting hour of gas day being reported (e.g. 30 Jun 2007)",
    "direction_code_name": "Distribution zone or injection meter",
    "direction": "'Withdrawals' or 'Injections'",
    "commencement_datetime": "Start time/date value applies for",
    "termination_datetime": "End date value applies for (e.g. 30 Jun 2007 06:00:00)",
    "quantity": "Metered value. Injection: direct reading. Withdrawals: Summed by Distribution Business Zone in GJ.",
    "time_sort_order": "Internal flag",
    "mod_datetime": "Date and time data last modified (e.g. 30 Jun 2007 06:00:00)",
    "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report contains the energy by distribution network area data for the previous and the current gas day.
As this report is generated on an hourly basis, participants can use this report for adjusting their forecast of system load over
the course of the day on a geographical basis. It can be used as an input into Participants bidding decisions leading up to the
next schedule.
Distributors can use this information to monitor energy flows.
Note this is operational data and is subject to substituted data. Therefore, do not use it to validate settlement outcomes.

This report is summed by distribution network zones, net of re-injections and transmission customers.
This report does not allocate inter-distribution zone energy flows on the infrequent occasions on which they occur. To obtain
information on cross-border flows, users are referred to the specific MIRNs assigned to the cross Distribution Business
network connections.

Each report contains 24 rows for the previous gas day for:
- each injection point (for example, Culcairn, Longford, LNG, Iona, VicHub, SEAGas, Bass Gas)
- each distribution zone
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
