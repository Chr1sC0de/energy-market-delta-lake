from polars import Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Contact Details report                    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_contacts"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbcontacts*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "PersonId",
    "LastUpdated",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "PersonId": Int64,
    "PersonName": String,
    "CompanyName": String,
    "CompanyId": Int64,
    "Position": String,
    "Email": String,
    "LastUpdated": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "PersonId": "Person unique identifier.",
    "PersonName": "Name of the person.",
    "CompanyName": "Company name associated with the person.",
    "CompanyId": "Company ID associated with the person.",
    "Position": "Job title of person.",
    "Email": "Email address of person.",
    "LastUpdated": "Date and time the record was last modified.",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
Provides a report of registered contact details for each participant.

This report is updated daily and shows current records.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
