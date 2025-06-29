from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int117a_v4_est_ancillary_payments_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int117a_v4_est_ancillary_payments_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "schedule_no",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "schedule_no": Int64,
    "est_ancillary_amt_gst_ex": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Format: dd mmm yyyy hh:mm (e.g. 15 Feb 2007 06:00)",
    "schedule_no": "Schedule number associated with the scheduling horizon (i.e. 1 = 6:00 AM to 6:00 AM, 2 = 10:00 AM to 6:00 AM)",
    "est_ancillary_amt_gst_ex": "Total Estimated Ancillary Payment (can be positive or negative) for a schedule",
    "current_date": "Time Report Produced (e.g. 30 Jun 2007 01:23:45)",
}

report_purpose = """
This report is a public version of INT116a. It provides the estimated ancillary payments for the total gas market but does not
take into account Actual Gas Injected Negative Offset (AGINO) and Actual Gas Withdrawal Negative Offset (AGWNO)
quantities. That is it is it is produce at the operational schedule time and is not adjusted for actual metered values, and is
therefore likely to differ from the final settlement total.

Participants may use this report to compare their estimated ancillary payments (from INT116a) in the context of the whole gas
market.

This is a public report containing ancillary payments from the beginning of the previous month and is produced after each
schedule.

This report does not take into account AP Clawback. AP Clawback is a mechanism which recovers ancillary payments that
have already been made to participants on the basis of a scheduled injection or withdrawal when those injections or
withdrawals are de-scheduled in a later horizon.

There are a number of participant specific reports and public reports relating to ancillary payments, in particular:
- INT116 - Participant Specific Ancillary Payments Reports Day + 3
- INT116a - Participant Specific Estimated Ancillary Payments Report
- INT116b - Participant Specific Ancillary Payments
- INT117b - Public Ancillary Payments Report (Day+1)

The ancillary payment amount can be positive or negative depending on the total estimated ancillary payment for the schedule
(if it is in credit or debit).

The number of rows in this report is dependent on the time of the month when this report is produced.
Each report contains the:
- gas date
- schedule number related to the scheduling horizon (where schedule1 will refer to 6:00 AM to 6:00 AM and schedule2
  will relate to 10:00 AM to 6:00 AM, and so forth)
- total estimated ancillary payment (positive or negative) for the schedule
- date and time when the report was produced
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
