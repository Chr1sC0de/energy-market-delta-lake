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


table_name = "bronze_int152_v4_sched_min_qty_linepack_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int152_v4_sched_min_qty_linepack_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "type",
    "linepack_id",
    "commencement_datetime",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "type": String,
    "linepack_id": Int64,
    "linepack_zone_id": Int64,
    "commencement_datetime": String,
    "ti": Int64,
    "termination_datetime": String,
    "unit_id": String,
    "linepack_zone_name": String,
    "transmission_document_id": Int64,
    "quantity": Int64,
    "current_date": String,
    "approval_date": String,
}

schema_descriptions = {
    "gas_date": "Gas day (e.g. 30 Jun 2007)",
    "type": "LPMIN for INT046, LPSCHED for INT115",
    "linepack_id": "Linepack identifier",
    "linepack_zone_id": "Linepack zone identifier (Null for LPSCHED)",
    "commencement_datetime": "Format: dd mon yyy hh:mm:ss",
    "ti": "Applicable to LPSCHED only, null for LPMIN. 0-24. 0 means linepack at start of schedule. Ie 5:59am 1-24 represents the time interval of the day.",
    "termination_datetime": "Format: dd mon yyyy hh:mm:ss",
    "unit_id": "GJ",
    "linepack_zone_name": "Name of linepack zone",
    "transmission_document_id": "Null for LPMIN",
    "quantity": "Quantity value",
    "current_date": "Date and time the report was produced: Format dd mon yyyy hh:mm:ss",
    "approval_date": "Date of approval (e.g. 30 Jun 2007)",
}

report_purpose = """
This report provides transparency into the system operation of the gas market, as required under clause 320 of the NGR.

This report combines two different types of content:
- the end-of-day linepack minimum target (in GJ) set by AEMO as part of system operations.
- the hourly linepack quantities scheduled for the gas day

In examining hourly linepack quantities associated with a schedule (row where type = 'LPSCHED'), users may find it useful to
re-order rows using the commencement time column.

Users should refer to INT108 (Schedule Run Log) to determine the characteristics of each schedule (for example, the
schedule start date and time, publish time, schedule type and so on) associated with a specific transmission_document_id
(which is also known as schedule_id).

As a report is generated each time an operational schedule is approved there will be at least 9 issues of INT152 each day (with
an additional report generated for each ad hoc schedule required).

Each report shows the scheduled and minimum linepack quantities (in GJ) for the:
- previous 7 gas day
- current gas day
- next 2 gas days

Some reports provide information only for the next gas day (not 2 days into the future).

The number of gas days and/or schedules covered by a report will depend on the time at which the particular report version is
produced. In general, reports produced by the approval of standard schedules at 06:00 AM and 10:00 AM will contain
information only for the past 7, current and next gas day as at that point in time no schedules for 2 days in the future will have
been run.

For the section of the report providing information on linepack minima (rows where type = 'LPMIN'), there is one row for the
system linepack minimum for each gas day within the reporting window.

For the section of the report providing information on hourly scheduled linepack quantities (rows where type = 'LPSCHED'),
there are:
- 25 rows for each schedule (operational or pricing) where the schedule start time is 06:00 AM:
  - One row is tagged '05:59' in the commencement time column and provides the initial linepack condition at the start of
    the gas day.
  - Other rows are tagged with hourly intervals commencing from '06:00' and provide the scheduled linepack quantities for
    each hour of the gas day.
- 26 rows for each schedule (operational or pricing) where the schedule start time is other than 06:00 AM:
  - One row is tagged '05:59' in the commencement time column and provide the initial linepack condition at the
    start of the gas day.
  - One row is tagged as one minute prior to the schedule start time (for example, 09:59 PM) and provide the initial
    linepack condition at the start of the scheduling interval.
  - Other rows are tagged with hourly intervals commencing from '06:00' and provide the scheduled linepack
    quantities for each hour of the gas day.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
