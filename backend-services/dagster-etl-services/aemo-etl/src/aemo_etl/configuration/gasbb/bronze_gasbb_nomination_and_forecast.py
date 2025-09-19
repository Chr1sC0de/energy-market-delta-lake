from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Nominations And Forecasts report          │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_nomination_and_forecast"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbnominationandforecast*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "Gasdate",
    "FacilityId",
    "LocationId",
    "LastUpdated",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "Gasdate": String,
    "FacilityName": String,
    "FacilityType": String,
    "State": String,
    "LocationName": String,
    "Demand": Float64,
    "Supply": Float64,
    "TransferIn": Float64,
    "TransferOut": Float64,
    "FacilityId": Int64,
    "LocationId": Int64,
    "LastUpdated": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "GasDate": "Date of gas day.",
    "FacilityName": "The name of the BB facility.",
    "FacilityType": "Facility type associated with the Facility Id.",
    "State": "Name of the state.",
    "LocationName": "Name of the location.",
    "Demand": "Usage type expressed in TJ. Three decimal places is not shown if the value has trailing zeros after the decimal place.",
    "Supply": "Usage type expressed in TJ. Three decimal places is not shown if the value has trailing zeros after the decimal place.",
    "TransferIn": "Usage type expressed in TJ. Only applicable to BB pipelines. Three decimal places is not shown if the value has trailing zeros after the decimal place.",
    "TransferOut": "Usage type expressed in TJ. Only applicable to BB pipelines. Three decimal places is not shown if the value has trailing zeros after the decimal place.",
    "FacilityId": "A unique AEMO defined Facility identifier.",
    "LocationId": "Unique location identifier.",
    "LastUpdated": "Date file was last updated.",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
The report shall return Nomination and Forecast data submitted to the market.
Nomination and Forecasts data shall be aggregated by BB facility.

GASBB_NOMINATION_AND_FORECAST is updated daily.
GASBB_NOMINATION_AND_FORECAST_NEXT_7 is typically updated within 30 minutes of receiving new data.

GASBB_NOMINATION_AND_FORECAST report contain historical data as well as nominations for D+0, D+1, D+2, D+3, D+4, D+5, and D+6. 
GASBB_NOMINATION_AND_FORECAST_NEXT_7 report covers the outlook period of D+0, D+1, D+2, D+3, D+4, D+5, and D+6.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
