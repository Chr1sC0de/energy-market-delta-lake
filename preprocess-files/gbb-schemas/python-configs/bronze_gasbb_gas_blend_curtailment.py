from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Gas Blend and Curtailment report          │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "python-configs.bronze_gasbb_gas_blend_curtailment"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbblendandblendcurtail*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "Year",
    "Month",
    "FacilityId",
    "ConnectionPointId",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "Year": Int64,
    "Month": Int64,
    "State": String,
    "FacilityId": Int64,
    "FacilityName": String,
    "FacilityType": String,
    "ConnectionPointId": Int64,
    "ConnectionPointName": String,
    "FlowDirection": String,
    "LocationName": String,
    "LocationId": Int64,
    "GasType": String,
    "GasBlendCurtailEvent": Int64,
    "GasBlendCurtailQty": Float64,
    "GasBlendLimit": Float64,
    "GasBlendHigh": Float64,
    "MaxGasDate": String,
    "GasBlendLow": Float64,
    "MinGasDate": String,
    "GasBlendAvg": Float64,
    "LastUpdated": String,
}

schema_descriptions = {
    "Year": "Year that the information applies to.",
    "Month": "Month that the information applies to.",
    "State": "Name of the state.",
    "FacilityId": "A unique AEMO defined facility identifier.",
    "FacilityName": "The name of the BB facility.",
    "FacilityType": "Facility type associated with the facility id.",
    "ConnectionPointId": "A unique AEMO defined connection point identifier.",
    "ConnectionPointName": "Name of connection point.",
    "FlowDirection": "Gas flow direction. Values can be either: Receipt or Delivery.",
    "LocationName": "Name of location.",
    "LocationId": "A unique AEMO defined location identifier.",
    "GasType": "Primary gas added to the gas blend.",
    "GasBlendCurtailEvent": "The number of times gas blend curtailment has occurred during the month in relation to the BB facility, or part of a BB facility (as applicable).",
    "GasBlendCurtailQty": "The aggregate curtailed quantity resulting from a gas blend curtailment event.",
    "GasBlendLimit": "Blend level limit, as a percentage (%vol), applied for the gas day.",
    "GasBlendHigh": "Highest blend level, as a percentage (%vol), achieved on any gas day in the month.",
    "MaxGasDate": "The gas date in the month where the highest blend level was achieved.",
    "GasBlendLow": "Lowest blend level, as a percentage (%vol), achieved on any gas day in the month.",
    "MinGasDate": "The gas date in the month where the lowest blend level was achieved.",
    "GasBlendAvg": "Average blend level, as a percentage (%vol), across all gas days in the month.",
    "LastUpdated": "Date the record was last modified.",
}

report_purpose = """
The purpose of the gas blend and gas blend curtailment information report is to provide a summary of gas blend and gas blend curtailment event information 
to the Gas Bulletin Board (GBB) for a BB blended gas distribution system or BB pipeline that transports a gas blend.

GASBB_BLEND_AND_BLEND_CURTAIL is updated monthly on the 5th day of the calendar month. The report is not updated once produced.

Data in the report contains information for the previous calendar month.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
