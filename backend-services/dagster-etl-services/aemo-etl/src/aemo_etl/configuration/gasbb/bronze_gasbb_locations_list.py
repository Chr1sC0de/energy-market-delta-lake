from polars import Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Locations List report                     │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_locations_list"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbblocationslist*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "LocationId",
    "LastUpdated",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "LocationName": String,
    "LocationId": Int64,
    "State": String,
    "LocationType": String,
    "Description": String,
    "LastUpdated": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "LocationName": "Name of the Location.",
    "LocationId": "Unique Location identifier.",
    "State": "Location state.",
    "LocationType": "Type of location.",
    "Description": "Free text description of the Location including boundaries and the basis of measurement.",
    "LastUpdated": "Date the list of locations was last updated.",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report lists all production and demand locations within the Bulletin Board system.

This report is updated daily and shows current records.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
