from polars import String, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Missing Nomination And Forecast report    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_missing_nomination_forecast"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbmissingnominationandforecast*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "GasDate",
    "FacilityId",
    "ConnectionPointId",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "GasDate": String,
    "FacilityName": String,
    "FacilityId": Int64,
    "ConnectionPointId": Int64,
    "surrogate_key": String,
}

schema_descriptions = {
    "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",
    "FacilityName": "Name of the facility.",
    "FacilityId": "A unique AEMO defined Facility identifier.",
    "ConnectionPointId": "A unique AEMO defined connection point identifier.",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
Returns any missing nomination/forecast flow data.

GASBB_MISSING_NOMINATION_AND_FORECAST is updated daily.

The report covers the last 31 days.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
