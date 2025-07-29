from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Forecast Utilisation report               │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_forecast_utilisation"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbforecastutilisationnext7*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "FacilityId",
    "ReceiptLocationId",
    "DeliveryLocationId",
    "Description",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "State": String,
    "FacilityId": Int64,
    "FacilityName": String,
    "FacilityType": String,
    "ReceiptLocationId": Int64,
    "ReceiptLocationName": String,
    "DeliveryLocationId": Int64,
    "DeliveryLocationName": String,
    "Description": String,
    "ForecastMethod": String,
    "Units": String,
    "Nameplate": Float64,
    "DayPlus1": Float64,
    "DayPlus2": Float64,
    "DayPlus3": Float64,
    "DayPlus4": Float64,
    "DayPlus5": Float64,
    "DayPlus6": Float64,
    "DayPlus7": Float64,
}

schema_descriptions = {
    "State": "Name of the state.",
    "FacilityId": "A unique AEMO defined facility identifier.",
    "FacilityName": "The name of the BB facility.",
    "FacilityType": "Facility type associated with the facility id.",
    "ReceiptLocationId": "The Connection Point Id that best represents the receipt location associated with a pipeline's nameplate capacity flow direction.",
    "ReceiptLocationName": "The Connection Point name associated with the ReceiptLocationId.",
    "DeliveryLocationId": "The Connection Point Id that best represents the delivery location associated with a pipeline's nameplate capacity flow direction.",
    "DeliveryLocationName": "The Connection Point name associated with the DeliveryLocationId.",
    "Description": "Describes the calculation that is being performed in each row of the report.",
    "ForecastMethod": "Describes the calculation that is being performed for each BB pipeline where the Description is Forecast Flow.",
    "Units": "The unit of measure for the calculated values.",
    "Nameplate": "Standing nameplate capacity quantity in TJ. Nameplate rating relates to maximum daily quantities under normal operating conditions.",
    "DayPlus1": "Forecast values and calculations relating to each Description for the first day of the forecast period.",
    "DayPlus2": "Forecast values and calculations relating to each Description for the second day of the forecast period.",
    "DayPlus3": "Forecast values and calculations relating to each Description for the third day of the forecast period.",
    "DayPlus4": "Forecast values and calculations relating to each Description for the fourth day of the forecast period.",
    "DayPlus5": "Forecast values and calculations relating to each Description for the fifth day of the forecast period.",
    "DayPlus6": "Forecast values and calculations relating to each Description for the sixth day of the forecast period.",
    "DayPlus7": "Forecast values and calculations relating to each Description for the seventh day of the forecast period.",
}

report_purpose = """
The purpose of the forecast utilisation report is to provide a summary of forecast information provided by Gas Bulletin Board (BB) facility operators. 
The report is a 7-day outlook of the supply-demand gas balance in the East Coast.

GASBB_FORECAST_UTILISATION_NEXT7 is updated daily. The report is not updated once produced.

Data in the report contains information for D+1 through to D+7.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
