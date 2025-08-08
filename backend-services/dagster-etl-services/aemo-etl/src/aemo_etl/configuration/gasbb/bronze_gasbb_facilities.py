from polars import String, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Facilities List report                    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_facilities"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbfacilities*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["FacilityId", "LastUpdated"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "FacilityName": String,
    "FacilityShortName": String,
    "FacilityId": Int64,
    "FacilityType": String,
    "FacilityTypeDescription": String,
    "OperatingState": String,
    "OperatingStateDate": String,
    "OperatorName": String,
    "OperatorId": Int64,
    "OperatorChangeDate": String,
    "LastUpdated": String,
}

schema_descriptions = {
    "FacilityName": "Name of the facility.",
    "FacilityShortName": "Abbreviated version of the facility name.",
    "FacilityId": "A unique AEMO defined facility identifier.",
    "FacilityType": "Facility type associated with the facility id.",
    "FacilityTypeDescription": "Free text description of the facility type.",
    "OperatingState": "The operating state (Active or Inactive) of the facility.",
    "OperatingStateDate": "Date the current operating state was set.",
    "OperatorName": "Name of the operator for the facility.",
    "OperatorId": "The facility operator's ID.",
    "OperatorChangeDate": "Date the current operator for the facility was set.",
    "LastUpdated": "Date and time the record was last modified.",
}

report_purpose = """
Displays a list of all currently registered BB facilities and identifies the organisation responsible for the operation of the respective facility.

Both GASBB_FACILITIES_LIST and GASBB_FACILITIES_FULL_LIST are updated daily.

Current records.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
