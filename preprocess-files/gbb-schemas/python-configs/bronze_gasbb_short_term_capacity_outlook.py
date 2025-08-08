from polars import String, Int64, Float64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for Short Term Capacity Outlook report        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_short_term_capacity_outlook"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbshorttermcapacityoutlook*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "GasDate",
    "FacilityId",
    "CapacityType",
    "FlowDirection",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "GasDate": String,
    "FacilityId": Int64,
    "FacilityName": String,
    "CapacityType": String,
    "CapacityTypeDescription": String,
    "OutlookQuantity": Float64,
    "FlowDirection": String,
    "CapacityDescription": String,
    "ReceiptLocation": Int64,
    "DeliveryLocation": Int64,
    "ReceiptLocationName": String,
    "DeliveryLocationName": String,
    "Description": String,
    "LastUpdated": String,
}

schema_descriptions = {
    "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",
    "FacilityId": "A unique AEMO defined Facility identifier.",
    "FacilityName": "The name of the BB facility.",
    "CapacityType": "Capacity type values can be: STORAGE — Holding capacity in storage; or MDQ — Daily maximum firm capacity under the expected operating conditions.",
    "CapacityTypeDescription": "Description of the Capacity Type.",
    "OutlookQuantity": "Capacity outlook quantity to three decimal places. Three decimal places is not required if the value has trailing zeros after the decimal place.",
    "FlowDirection": "Gas flow direction. Only valid for BB storage, LNG export, or LNG import facilities.",
    "CapacityDescription": "Free text to describe the meaning of the capacity number provided, including a description of material factors that impact the capacity number and any other relevant information.",
    "ReceiptLocation": "The Connection Point Id that best represents the receipt location. The Receipt Location in conjunction with the Delivery Location indicates the capacity direction and location.",
    "DeliveryLocation": "The Connection Point Id that best represents the delivery location. This location in conjunction with the Receipt Location indicates the capacity direction and location.",
    "ReceiptLocationName": "A description of the Receipt Location. Only valid for BB pipelines.",
    "DeliveryLocationName": "A description of the Delivery Location. Only valid for BB pipelines.",
    "Description": "Comments about the quantity or change in Flow Direction relating to the Facility Id, and the times, dates, or duration which those quantities or changes in quantities.",
    "LastUpdated": "Date the record was last modified.",
}

report_purpose = """
This report displays the expected daily capacity of a BB facility for the next seven days.

GASBB_SHORT_TERM_CAPACITY_OUTLOOK is updated daily.
GASBB_SHORT_TERM_CAPACITY_OUTLOOK_FUTURE is typically updated within 30 minutes of receiving new data.

GASBB_SHORT_TERM_CAPACITY_OUTLOOK contains historic outlooks.
GASBB_SHORT_TERM_CAPACITY_OUTLOOK_FUTURE contains data in the seven day outlook window.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
