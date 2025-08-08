from polars import Float64, Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Pipeline Connection Flow report           │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_pipeline_connection_flow_history"

s3_prefix = "aemo/gasbb"

s3_file_glob = "pipelineconnectionflow_history*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "GasDate",
    "FacilityId",
    "ConnectionPointId",
    "FlowDirection",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)


table_schema = {
    "GasDate": String,
    "FacilityName": String,
    "FacilityId": Int64,
    "ConnectionPointName": String,
    "ConnectionPointId": Int64,
    "ActualQuantity": Float64,
    "FlowDirection": String,
    "State": String,
    "LocationName": String,
    "LocationId": Int64,
    "Quality": String,
}

schema_descriptions = {
    "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",
    "FacilityId": "A unique AEMO defined Facility identifier.",
    "FacilityName": "Name of the facility.",
    "ConnectionPointId": "A unique AEMO defined connection point identifier.",
    "ConnectionPointName": "Names of the connection point.",
    "FlowDirection": "A conditional value of either: RECEIPT — A flow of gas into the BB pipeline, or DELIVERY — A flow of gas out of the BB pipeline.",
    "ActualQuantity": "The actual flow quantity reported in TJ to the nearest terajoule with three decimal places.",
    "State": "Location.",
    "LocationName": "Name of the Location.",
    "LocationId": "Unique Location identifier.",
    "Quality": "Indicates whether meter data for the submission date is available. Values can be either: OK, NIL, OOR, Not Available.",
}

report_purpose = """
Provides a report for the Daily production and usage at each Connection Point.

GASBB_PIPELINE_CONNECTION_FLOW is updated daily.
GASBB_PIPELINE_CONNECTION_FLOW_LAST_31 is typically updated within 30 minutes of receiving new data.

GASBB_PIPELINE_CONNECTION_FLOW contains historical data from Sep 2018.
GASBB_PIPELINE_CONNECTION_FLOW_LAST_31 contains data from the last 31 days.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
