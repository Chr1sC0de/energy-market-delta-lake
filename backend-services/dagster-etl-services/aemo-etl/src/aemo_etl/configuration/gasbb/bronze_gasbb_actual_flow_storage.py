from polars import Float64, Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Actual Flow and Storage reports           │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_actual_flow_storage"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbactualflowstorage*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "GasDate",
    "FacilityId",
    "LocationId",
    "LastUpdated"
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "GasDate": String,
    "FacilityName": String,
    "State": String,
    "LocationId": Int64,
    "LocationName": String,
    "Demand": Float64,
    "Supply": Float64,
    "TransferIn": Float64,
    "TransferOut": Float64,
    "HeldInStorage": Float64,
    "FacilityId": Int64,
    "FacilityType": String,
    "CushionGasStorage": Float64,
    "LastUpdated": String,
}

schema_descriptions = {
    "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",
    "FacilityName": "Name of the facility.",
    "State": "Name of the state.",
    "LocationId": "Unique location identifier.",
    "LocationName": "Name of the location.",
    "Demand": "Usage type expressed in TJ. Three decimal places is not shown if the value has trailing zeros after the decimal place.",
    "Supply": "Usage type expressed in TJ. Three decimal places is not shown if the value has trailing zeros after the decimal place.",
    "TransferIn": "Usage type. Only applicable to BB pipelines. Three decimal places is not shown if the value has trailing zeros after the decimal place.",
    "TransferOut": "Usage type. Only applicable to BB pipelines. Three decimal places is not shown if the value has trailing zeros after the decimal place.",
    "HeldinStorage": "Three decimal places is not shown if the value has trailing zeros after the decimal place.",
    "FacilityId": "A unique AEMO defined Facility identifier.",
    "FacilityType": "The type of facility (e.g., BBGPG, COMPRESSOR, PIPE, PROD, STOR, LNGEXPORT, LNGIMPORT, BBLARGE).",
    "CushionGasStorage": "The quantity of gas that must be retained in the Storage or LNG Import facility in order to maintain the required pressure and deliverability rates.",
    "LastUpdated": "The date data was last submitted by a participant based on the report query.",
}

report_purpose = """
The report shows Daily Production, Flow and Storage data aggregated by Facility Id for an outlook period.

This report is updated daily and shows historic records back to Sep 2018.
There is also a GASBB_ACTUAL_FLOW_STORAGE_LAST_31 variant that is updated within 30 minutes of receiving new data and shows records from the last 31 days.

The report can be filtered by:
- State
- Facility Type
- Facilities
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
