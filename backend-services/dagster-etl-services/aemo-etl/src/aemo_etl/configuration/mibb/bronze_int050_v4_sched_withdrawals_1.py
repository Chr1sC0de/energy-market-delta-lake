from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int050_v4_sched_withdrawals_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int050_v4_sched_withdrawals_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "withdrawal_zone_name",
    "transmission_id",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "gas_date": String,
    "withdrawal_zone_name": String,
    "scheduled_qty": Float64,
    "transmission_id": Int64,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "gas_date": "Starting hour of gas day being reported e.g. 30 Jun 1998 09:00:00",
    "withdrawal_zone_name": "Withdrawal zone name",
    "scheduled_qty": "Scheduled withdrawal (GJ) for withdrawal zone.",
    "transmission_id": "Schedule ID from which results were drawn",
    "current_date": "Date and time report produced e.g. 29 Jun 2007 01:23:45",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report provides information required under 320(2)(i) and 320(3)(a) of the NGR.
It provides a view of the amount of gas that is flowing in each of the withdrawal zones, and in the network overall, on a given
day. It therefore contributes to data on mid- to long-term trends for planning and load forecasting purposes.

A report is produced each time an operational schedule (OS) is approved by AEMO. Therefore it is expected that at least 9 of
these reports will be issued each day:
- 5 being for the standard current gas day schedules (published at 6:00 AM, 10:00 AM, 2:00 PM, 6:00 PM and 10:00 PM)
- 3 being for the standard 1-day ahead schedules (published at 8:00 AM, 4:00 PM and midnight)
- 1 being for the standard 2 day ahead schedule (published at midday)

Each report will provide information on at most 3 gas days, and only report the details associated with the latest approved
schedule for each of the three specified gas days. If the user wishes to view information for each schedule run and approved
for a gas day, it will be necessary to retrieve and analyse data in multiple reports.

Each report contains details of the energy quantities scheduled:
- in the latest approved schedule for the current gas day and
- in the last approved 1-day ahead schedule and
- in the last approved 2-day ahead schedule, if one exists.

The energy quantities reported are scheduled withdrawal quantities for a withdrawal zone:
Scheduled withdrawals = Controllable withdrawals + forecast uncontrollable demand

Each row in the report contains details of the scheduled withdrawals for the specified withdrawal zone for the specified
schedule. If there are 5 withdrawal zones defined for the Victorian gas network for example, then each schedule (identified by
a unique transmission_id) will be represented by 5 rows in this report.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
