from polars import String, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Contact Details report                    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_contacts_list"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbcontactslist*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "PersonId",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "PersonId": Int64,
    "PersonName": String,
    "CompanyName": String,
    "CompanyId": Int64,
    "Position": String,
    "Email": String,
    "LastUpdated": String,
}

schema_descriptions = {
    "PersonId": "Person unique identifier.",
    "PersonName": "Name of the person.",
    "CompanyName": "Company name associated with the person.",
    "CompanyId": "Company ID associated with the person.",
    "Position": "Job title of person.",
    "Email": "Email address of person.",
    "LastUpdated": "Date and time the record was last modified.",
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
