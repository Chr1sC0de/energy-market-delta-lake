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


table_name = "bronze_int199_v4_cumulative_price_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int199_v4_cumulative_price_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "schedule_interval",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "transmission_id": Int64,
    "gas_date": String,
    "schedule_interval": Int64,
    "cumulative_price": Float64,
    "cpt_exceeded_flag": String,
    "schedule_type_id": String,
    "transmission_doc_id": Int64,
    "approval_datetime": String,
    "current_date": String,
}

schema_descriptions = {
    "transmission_id": "Schedule Id - Unique identifier associated with each schedule",
    "gas_date": "Gas day of schedule. format dd mmm yyy e.g. 30 Jun 2008",
    "schedule_interval": "Integer identifier of schedule of the gas day: 1=schedule with start time 6:00 AM, 2=schedule with start time 10:00 AM, 3=schedule with start time 2:00 PM, 4=schedule with start time 6:00 PM, 5=schedule with start time 10:00 PM",
    "cumulative_price": "Rolling cumulative price from MCP's from previous Y-1 LAOS and next FAOS",
    "cpt_exceeded_flag": "'Y' when CP ≥ CPT, otherwise 'N'",
    "schedule_type_id": "OS (Operating Schedule Id)",
    "transmission_doc_id": "Run Id",
    "approval_datetime": "Date and time the schedule was approved 29 Jun 2007 01:23:45",
    "current_date": "Current report run date time. Format dd Mmm yyyy hh:mi:ss e.g. 15 May 2008 12:22:12",
}

report_purpose = """
Interface 199 (INT199) is an Event-Triggered report published on the Market Information Bulletin Board (MIBB). This report
must provide by scheduling interval by gas day the cumulative price (CP) and a flag to indicate when CP is greater than or
equal to the threshold (CPT). The report is produced on approval of a current gas day operating/pricing schedules with start
time equal to the commencement of each scheduling interval. Ad hoc operating reschedules during a scheduling interval are
included in the determination of MCP's for previous scheduling intervals, but do not themselves trigger the report.

Whilst bid information is public and this can be estimated by the public, actual scheduling information by bid is still regarded as
confidential by Market participants.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
