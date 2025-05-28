from polars import Date, Datetime, Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.utils import definition_builder_factory
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_vicgas_int029a_system_wide_notices"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int029a*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "system_wide_notice_id",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "system_wide_notice_id": Int64,
    "critical_notice_flag": String,
    "system_message": String,
    "system_email_message": String,
    "notice_start_date": Date,
    "notice_end_date": Date,
    "url_path": String,
    "current_date": Datetime(time_unit="ms", time_zone="UTC"),
}

schema_descriptions = {
    "system_wide_notice_id": "Id of the Notice",
    "critical_notice_flag": "",
    "system_message": "SWN SMS message",
    "system_email_message": "SWN email message",
    "notice_start_date": " e.g. 14 Feb 2007 11:48:55. Sorted descending.",
    "notice_end_date": "e.g. 23 Jul 2007 16:30:35",
    "url_path": "Path to any attachment included in the notice e.g. Public/Master_MIBB_report_list.zip",
    "current_date": "Date and time the report was produced e.g. Jul 23 2007 16:30:35",
}

report_purpose = """
This report is a CSV file (INT029a) published by AEMO containing public system-wide notices shared on the MIBB.
It provides consistent and timely market operation updates and mirrors the content of the HTML version (INT105).
These reports are for public viewing, unlike similar reports (INT029b and INT106) sent to specific participants.

Key points:

Purpose: Public communication of market notices.

Format: CSV (INT029a) and HTML (INT105), both containing the same information.

Timing: Issued simultaneously when AEMO publishes a system-wide notice.

Content: Includes the issue date/time, urgency level, effective period, and source for further details.

Notices are listed from most recent to oldest.
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
)

definitions_list.append(definition_builder.build())
