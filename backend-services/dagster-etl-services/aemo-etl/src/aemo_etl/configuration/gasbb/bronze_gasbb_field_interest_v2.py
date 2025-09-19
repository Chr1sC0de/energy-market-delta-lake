from polars import Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Field Interests report                    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_field_interest_v2"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbgasfieldinterest*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["FieldInterestId", "CompanyId", "EffectiveDate"]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "FieldName": String,
    "FieldInterestId": Int64,
    "CompanyId": Int64,
    "CompanyName": String,
    "GroupMembers": String,
    "PercentageShare": String,
    "EffectiveDate": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "FieldName": "The name of the Field in which the Field Interest is located.",
    "FieldInterestId": "A unique AEMO defined Field Interest Identifier.",
    "CompanyId": "The company ID of the responsible participant.",
    "CompanyName": "The company name of the responsible participant.",
    "GroupMembers": "The name of the group member.",
    "PercentageShare": "The BB field interest (as a percentage) of each member of the field owner group.",
    "EffectiveDate": "The date on which the record takes effect.",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report displays information about Field Interests.

GASBB_FIELD_INTEREST is updated daily.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
