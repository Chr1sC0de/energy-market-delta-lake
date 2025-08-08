from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Nameplate Rating report                   │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_nameplate_rating"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbnameplaterating*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "FacilityId",
    "CapacityType",
    "FlowDirection",
    "EffectiveDate",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "FacilityName": String,
    "FacilityId": Int64,
    "FacilityType": String,
    "CapacityType": String,
    "CapacityQuantity": Float64,
    "FlowDirection": String,
    "CapacityDescription": String,
    "ReceiptLocation": Int64,
    "ReceiptLocationName": String,
    "DeliveryLocation": Int64,
    "DeliveryLocationName": String,
    "EffectiveDate": String,
    "Description": String,
    "LastUpdated": String,
}

schema_descriptions = {
    "FacilityName": "Facility name associated with the Facility Id.",
    "FacilityId": "A unique AEMO defined Facility identifier.",
    "FacilityType": "Facility type associated with the Facility Id.",
    "CapacityType": "Capacity type can be either: Storage: Holding capacity in storage, or MDQ: Daily maximum firm capacity (name plate) under the expected operating conditions.",
    "CapacityQuantity": "Standing capacity quantity in TJ to three decimal places. Three decimal places is not required if the value has trailing zeros after the decimal place.",
    "FlowDirection": "Gas flow direction. Values can be either: Receipt, Delivery, Processed, DeliveryLngStor, or NONE.",
    "CapacityDescription": "Free text to describe the meaning of the capacity number provided, including relevant assumptions made in the calculation of the capacity number and any other relevant information.",
    "ReceiptLocation": "The Connection Point Id that best represents the receipt location. The Receipt Location in conjunction with the Delivery Location indicates the capacity direction and location.",
    "ReceiptLocationName": "The name of the receipt location.",
    "DeliveryLocation": "The Connection Point Id that best represents the delivery location. This location in conjunction with the Receipt Location indicates the capacity direction and location.",
    "DeliveryLocationName": "The name of the delivery location.",
    "EffectiveDate": "Gas day date that corresponding record takes effect. Any time component supplied will be ignored.",
    "Description": "Free text facility use is restricted to a description for reasons or comments directly related to the quantity or the change in quantity provided in relation to a BB facility.",
    "LastUpdated": "Date and time record was last updated.",
}

report_purpose = """
This report displays the standing nameplate capacity of all BB facilities and BB compression facility. Nameplate rating relates to maximum daily quantities in TJ under normal operating conditions.

GASBB_NAMEPLATE_RATING_FULL_LIST is updated annually / GASBB_NAMEPLATE_RATING_CURRENT is updated within 30 minutes of receiving new data.

GASBB_NAMEPLATE_RATING_FULL_LIST contains historical records / GASBB_NAMEPLATE_RATING_CURRENT contains the current nameplate.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
