from polars import String, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Shippers List report                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_shippers_list"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbshippers*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "EffectiveDate",
    "FacilityId",
    "ShipperName",
    "LastUpdated",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "EffectiveDate": String,
    "FacilityId": Int64,
    "FacilityName": String,
    "FacilityType": String,
    "CompanyId": Int64,
    "OperatorName": String,
    "ShipperName": String,
    "LastUpdated": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "EffectiveDate": "Gas date that corresponding record takes effect.",
    "FacilityId": "A unique AEMO defined Facility identifier.",
    "FacilityName": "The name of the BB facility.",
    "FacilityType": "The type of facility.",
    "CompanyId": "Unique identifier for the company who operates the facility.",
    "OperatorName": "The name of the company who operates the facility.",
    "ShipperName": "The name of the shipper who holds the capacity.",
    "LastUpdated": "The date data was last submitted.",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
A list shippers who have contracted primary Storage, Compression or Pipeline capacity.

This report is updated daily.

GASBB_SHIPPERS_LIST contains current records / GASBB_SHIPPERS_FULL_LIST includes historic records.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
