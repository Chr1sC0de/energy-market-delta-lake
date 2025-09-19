from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    QUEENSLAND_GAS_RETAIL_REPORT_DETAILS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int538_v4_settlement_versions_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int538_v4_settlement_versions_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_name",
    "version_id",
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
    "network_name": "Network Name",
    "version_id": "balancing statement version (invoice_id) identifier",
    "extract_type": "P - Provisional, F - Final, R - Revision",
    "version_from_date": "Effective start date. (dd mmm yyyy)",
    "version_to_date": "Effective End date. (dd mmm yyyy)",
    "issued_date": "Issue date of settlement",
    "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report is to display recently issued settlement versions when balancing statement is issued.
Participants may wish to use this report as a reference to link other reports together based on invoice id(balancing version).

A report is produced when balancing statement is issued.
This report is similar to VIC MIBB report INT438.

Each report contains the:
- statement version identifier
- settlement category type
- effective start date
- effective end date
- date of issue
- date and time when the report was produced
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}"
