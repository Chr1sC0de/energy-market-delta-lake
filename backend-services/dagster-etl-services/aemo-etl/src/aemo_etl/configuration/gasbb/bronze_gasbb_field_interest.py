from polars import String, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Field Interests report                    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_field_interest"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbfieldinterest*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["FieldInterestId", "CompanyId", "EffectiveDate", "VersionDateTime"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "FieldName": String,
    "FieldInterestId": Int64,
    "CompanyId": Int64,
    "CompanyName": String,
    "GroupMembers": String,
    "PercentageShare": String,
    "EffectiveDate": String,
    "VersionDateTime": String,
}

schema_descriptions = {
    "FieldName": "The name of the Field in which the Field Interest is located.",
    "FieldInterestId": "A unique AEMO defined Field Interest Identifier.",
    "CompanyId": "The company ID of the responsible participant.",
    "CompanyName": "The company name of the responsible participant.",
    "GroupMembers": "The name of the group member.",
    "PercentageShare": "The BB field interest (as a percentage) of each member of the field owner group.",
    "EffectiveDate": "The date on which the record takes effect.",
    "VersionDateTime": "VersionDatetime",
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
