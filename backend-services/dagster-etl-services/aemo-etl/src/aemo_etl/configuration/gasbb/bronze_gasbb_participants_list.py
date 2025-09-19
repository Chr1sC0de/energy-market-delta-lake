from polars import String, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Participants List report                  │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_participants_list"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbparticipants*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "CompanyId",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "CompanyName": String,
    "CompanyId": Int64,
    "OrganisationTypeName": String,
    "ABN": String,
    "CompanyPhone": String,
    "Locale": String,
    "LastUpdated": String,
    "AddressType": String,
    "Address": String,
    "State": String,
    "Postcode": String,
    "CompanyFax": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "CompanyName": "Company name associated with the person.",
    "CompanyId": "Company ID associated with the person.",
    "OrganisationTypeName": "The type of organisation.",
    "ABN": "Australian Business Number for the participant.",
    "CompanyPhone": "Company phone details.",
    "Locale": "Location for the participant.",
    "LastUpdated": "Last changed details.",
    "AddressType": "Type of address.",
    "Address": "Mailing address for the company.",
    "State": "State where the company is located.",
    "Postcode": "Postcode details.",
    "CompanyFax": "Company fax details.",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report provides a list of registered participants in the Gas Bulletin Board system.

This report is updated daily and shows current records.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
