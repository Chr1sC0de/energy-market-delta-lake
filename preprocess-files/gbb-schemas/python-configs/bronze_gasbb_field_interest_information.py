from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Field Interest Information report         │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_field_interest_information"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbfieldinterestinformation*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "FieldInterestId",
    "EffectiveDate",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "FieldInterestId": Int64,
    "FieldName": String,
    "CompanyID": Int64,
    "CompanyName": String,
    "Description": String,
    "EffectiveDate": String,
    "PetroleumTenements": String,
    "TenementShare": Float64,
    "ProcessingFacilities": String,
    "ResourceClassification": String,
    "ResourceSubClassification": String,
    "NatureOfGas": String,
    "AnnualReportingDate": String,
    "BasinId": Int64,
    "BasinName": String,
    "State": String,
    "OperatingState": String,
    "VersionDateTime": String,
}

schema_descriptions = {
    "FieldInterestId": "A unique AEMO defined Field Interest Identifier.",
    "FieldName": "The name of the Field in which the Field Interest is located.",
    "CompanyID": "The company ID of the responsible participant.",
    "CompanyName": "The company name of the responsible participant.",
    "Description": "Additional information relating to the field.",
    "EffectiveDate": "The date on which the record takes effect.",
    "PetroleumTenements": "The petroleum tenements which are the subject of the BB field interest.",
    "TenementShare": "The field interest share of the petroleum tenements.",
    "ProcessingFacilities": "The processing facility used to process gas from the field.",
    "ResourceClassification": "Classification of the resources in the field as conventional or unconventional.",
    "ResourceSubClassification": "Any further sub-classification of the resources.",
    "NatureOfGas": "The nature of the gas in the field using classifications in the BB Procedures.",
    "AnnualReportingDate": "Annual date when information must be updated.",
    "BasinId": "The Id of the geological basin in which the field is located.",
    "BasinName": "The name of the geological basin in which the field is located.",
    "State": "The state the field interest is in.",
    "OperatingState": "The operating state (Active or Inactive) of the field.",
    "VersionDateTime": "Time a successful submission is accepted by AEMO systems.",
}

report_purpose = """
This report displays information about Field Interests.

GASBB_FIELD_INTEREST_INFORMATION is updated daily.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
