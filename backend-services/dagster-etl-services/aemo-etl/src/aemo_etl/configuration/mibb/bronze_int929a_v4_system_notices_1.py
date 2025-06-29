from polars import Int64, String

from aemo_etl.configuration import BRONZE_BUCKET, ECGS_REPORTS
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_int929a_v4_system_notices_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int929a_v4_system_notices_1*"

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
    "notice_start_date": String,
    "notice_end_date": String,
    "url_path": String,
    "current_date": String,
}

schema_descriptions = {
    "system_wide_notice_id": "Id of the ECGS Notice",
    "critical_notice_flag": "Critical notice flag",
    "system_message": "ECGS Notice SMS message",
    "system_email_message": "ECGS Notice email message",
    "notice_start_date": "e.g. 14 Feb 2023",
    "notice_end_date": "e.g. 10 May 2023",
    "url_path": "Path to any attachment included in the notice e.g. Public/ECGS_attachments/document.pdf",
    "current_date": "Date and time the report was produced e.g. 30 Jun 2023 09:33:57",
}

report_purpose = """
This report is a comma separated values (CSV) file that contains ECGS notices published by AEMO to the public and is sent to Part 27
Relevant Entities via email and SMS.

This report is published to the:
1. Market Information Bulletin Board (MIBB) public folder
2. NEMWEB folder: https://www.nemweb.com.au/REPORTS/CURRENT/ECGS/ECGS_Notices/

This report is published to the MIBB and then replicated to the NEMWeb.

The dual publication of this report allows existing Victorian DWGM and Gas Retail Market participants to access it via the MIBB. The
general public and electricity market participants can access this report directly via NEMWeb.

The "url path" field in the report reflects the MIBB folder location. Any PDF documents that are uploaded to the MIBB folder is
replicated to the following locations:
1. MIBB/Public/ECGS_attachments
2. www.nemweb.com.au - /REPORTS/CURRENT/ECGS/ECGS_Notices/Attachments/

Each report contains the details of all the general ECGS notices that are in effect for Relevant Entities at the report generation time.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{ECGS_REPORTS}"
