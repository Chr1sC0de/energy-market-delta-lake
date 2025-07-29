from polars import Boolean, String, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Nodes And Connection Points report        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_nodes_connection_points"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbnodesandconnectionpoints*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "FacilityId",
    "ConnectionPointId",
    "EffectiveDate",
    "LastUpdated",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "FacilityName": String,
    "FacilityId": Int64,
    "FacilityType": String,
    "ConnectionPointId": Int64,
    "ConnectionPointName": String,
    "FlowDirection": String,
    "Exempt": Boolean,
    "ExemptionDescription": String,
    "NodeId": Int64,
    "StateId": Int64,
    "StateName": String,
    "LocationName": String,
    "LocationId": Int64,
    "EffectiveDate": String,
    "LastUpdated": String,
}

schema_descriptions = {
    "FacilityName": "Name of the facility.",
    "FacilityId": "A unique AEMO defined facility identifier.",
    "FacilityType": "Facility type associated with the Facility Id.",
    "ConnectionPointId": "A unique AEMO defined connection point identifier.",
    "ConnectionPointName": "Name of connection point.",
    "FlowDirection": "Gas flow direction. Values can be either: Receipt, Delivery, Processed, or DeliveryLngStor.",
    "Exempt": "Flag indicating whether the connection point has a data exemption.",
    "ExemptionDescription": "Description of exemption.",
    "NodeId": "A unique AEMO defined node identifier.",
    "StateId": "A unique AEMO defined state identifier.",
    "StateName": "Name of the state.",
    "LocationName": "Name of location.",
    "LocationId": "A unique AEMO defined location identifier.",
    "EffectiveDate": "Date record is effective from",
    "LastUpdated": "Date the record was last modified.",
}

report_purpose = """
Displays detailed information on all facilities and their associated nodes and Connection Points.

Both GASBB_NODES_AND_CONNECTIONPOINTS_LIST and GASBB_NODES_CONNECTIONPOINTS_FULL_LIST are updated daily.

Contains all current facilities and their nodes and connection points.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
