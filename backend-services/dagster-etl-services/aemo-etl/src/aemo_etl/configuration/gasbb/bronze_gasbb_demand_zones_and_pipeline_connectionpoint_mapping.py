from polars import String, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join


key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_demand_zones_pipeline_connectionpoint_mapping"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbdemandzonespipelineconnectionpointmapping*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["FacilityId", "NodeId", "ConnectionPointId", "FlowDirection"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)


table_schema = {
    "FacilityName": String,
    "FacilityType": String,
    "FacilityId": Int64,
    "NodeId": Int64,
    "ConnectionPointId": Int64,
    "FlowDirection": String,
    "ConnectionPointName": String,
    "State": String,
    "DemandZone": String,
}

schema_descriptions = {
    "FacilityName": "Name of the facility.",
    "FacilityType": "The facility development type.",
    "FacilityId": "The gas storage facility ID for the facility by means of which the service is provided.",
    "NodeId": "A unique AEMO defined node identifier.",
    "ConnectionPointId": "A unique AEMO defined connection point identifier.",
    "FlowDirection": "Gas flow direction. Values can be: RECEIPT, DELIVERY, PROCESSED, DELIVERYLNGSTOR.",
    "ConnectionPointName": "Names of the connection point.",
    "State": "The state where the transaction occurred.",
    "DemandZone": "",
}

report_purpose = """
Provides mapping between pipelines, connectionpoints and  demand zones:w
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
