from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_GAS_RETAIL_REPORTS_DETAILS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int438_v4_bmp_version_non_pts_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int438_v4_bmp_version_non_pts_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_name",
    "version_id",
    "version_from_date",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "network_name": String,
    "version_id": Int64,
    "extract_type": String,
    "version_from_date": String,
    "version_to_date": String,
    "issued_date": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "network_name": "Network name",
    "version_id": "Set to BMP run id",
    "extract_type": "Type (e.g. F for Final, P for Preliminary, R = Revision)",
    "version_from_date": "Effective start date",
    "version_to_date": "Effective end date e.g. 30 Jun 2007",
    "issued_date": "Transfer to MIBB date. (dd mm yyyy hh:mm:ss)",
    "current_date": "Time Report Produced e.g. 29 Jun 2007 01:23:45",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report provides the run version of the basic meter profiles system (BMP) used by AEMO when producing the preliminary,
final and revised settlement versions. Market participants may wish to use this report as a reference for settlement
reconciliation processing.

This public report is produced daily on BMP run.
Each report shows the unique name for each network and only reports the non-DTS (Declared transmission system) networks.

Each report contains the:
- network name
- version id
- extract type
- version dates
- issued date
- date and time when the report was produced
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}"
