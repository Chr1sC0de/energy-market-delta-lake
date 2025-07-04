from polars import Float64, Int64, String

from aemo_etl.configuration import BRONZE_BUCKET

from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int117b_v4_ancillary_payments_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int117b_v4_ancillary_payments_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "ap_run_id",
    "gas_date",
    "schedule_no",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "ap_run_id": Int64,
    "gas_date": String,
    "schedule_no": Int64,
    "ancillary_amt_gst_ex": Float64,
    "current_date": String,
}

schema_descriptions = {
    "ap_run_id": "Number identifying ancillary run",
    "gas_date": "Format: dd mmm yyyy hh:mm (e.g. 15 Feb 2007 06:00)",
    "schedule_no": "Schedule number",
    "ancillary_amt_gst_ex": "Total Ancillary Payment (can be positive or negative) for a schedule",
    "current_date": "Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
}

report_purpose = """
This report is a public version of INT116b. It shows the actual ancillary payments for the gas market by taking into account the
Actual Gas Injected Negative Offset (AGINO) and Actual Gas Withdrawal Negative Offset (AGWNO) quantities, as well as the
proportion of injections used to support an uplift hedge.

Participants may wish to use this report to gauge their actual ancillary payments (from INT116b) in the context of the whole
gas market.

Participants should note that although the AGINO and AGWNO are included in the calculations for this report, the meter data
used for this purpose is provisional data that may change at settlement.

This a public report containing ancillary payments from the beginning of the previous month and is produced no later than the
third business day after the gas day (D+3).

There are a number of participant specific reports and public reports relating to ancillary payments, in particular:
- INT116 - Participant Specific Ancillary Payments Reports Day + 3
- INT116a - Participant Specific Estimated Ancillary Payments Report
- INT116b - Participant Specific Ancillary Payments
- INT117a - Public Estimated Ancillary Payments

The ancillary payment amount can be positive or negative depending on the total ancillary payment for the schedule (if it is in
credit or debit).

The number of rows in this report is dependent on the time of the month when this report is produced.
Each report contains the:
- ancillary run identifier
- gas date
- schedule number related to the scheduling horizon (where schedule1 will refer to 6:00 AM to 6:00 AM and schedule2
  will relate to 10:00 AM to 6:00 AM, and so forth)
- total ancillary payment for the schedule
- date and time when the report was produced
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
    group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
)

definitions_list.append(definition_builder.build())
