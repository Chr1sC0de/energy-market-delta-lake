from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Connection Point Nameplate Rating report  │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_connection_point_nameplate"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbconnectionpointnameplate*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "ConnectionPointId",
    "EffectiveDate",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "ConnectionPointName": String,
    "ConnectionPointId": Int64,
    "FacilityName": String,
    "FacilityId": Int64,
    "FacilityType": String,
    "OwnerName": String,
    "OwnerId": Int64,
    "OperatorName": String,
    "OperatorId": Int64,
    "CapacityQuantity": Float64,
    "EffectiveDate": String,
    "Description": String,
    "LastUpdated": String,
}

schema_descriptions = {
    "ConnectionPointName": "Connection Point name where the connection point is associated to a BB Pipeline or BB compression facility.",
    "ConnectionPointId": "A unique AEMO defined connection point identifier.",
    "FacilityName": "The facility reported.",
    "FacilityId": "Unique facility identifier.",
    "FacilityType": "The type of facility.",
    "OwnerName": "The reporting facility owner.",
    "OwnerId": "The reporting facility owner ID.",
    "OperatorName": "Name of the operator for the facility.",
    "OperatorId": "The facility operator's ID.",
    "CapacityQuantity": "Standing capacity quantity in TJ to three decimal places. Three decimal places is not required if the value has trailing zeros after the decimal place.",
    "EffectiveDate": "Gas day date that corresponding record takes effect. Any time component supplied will be ignored.",
    "Description": "Reasons or comments directly related to the capacity quantity or the change in quantity provided in relation to a BB facility and the times, dates, or duration for which those quantities or changes in quantities are expected to apply.",
    "LastUpdated": "The date data was last submitted by a participant based on the report query.",
}

report_purpose = """
This report displays the nameplate rating for each connection point id connected to a BB pipeline or BB compression facility.

This report will be a combination of all submissions for Gate Station Nameplate Rating and Connection Point Nameplate Rating.

This report is updated daily and shows future records.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
