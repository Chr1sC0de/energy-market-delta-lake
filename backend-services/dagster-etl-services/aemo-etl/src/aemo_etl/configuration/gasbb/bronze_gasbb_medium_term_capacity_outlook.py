from polars import Float64, Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │           define table and register for Medium Term Capacity Outlook reports           │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_medium_term_capacity_outlook"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbmediumtermcapacityoutlook*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "FromGasDate",
    "ToGasDate",
    "FacilityId",
    "CapacityType",
    "FlowDirection",
    "ReceiptLocation",
    "DeliveryLocation",
    "LastUpdated",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "FacilityId": Int64,
    "FacilityName": String,
    "FromGasDate": String,
    "ToGasDate": String,
    "CapacityType": String,
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
    "FacilityId": "Unique plant identifier.",
    "FacilityName": "Name of the plant.",
    "FromGasDate": "Date of gas day. Any time component supplied is ignored. The gas day is applicable under the pipeline contract or market rules.",
    "ToGasDate": "Date of gas day. Any time component supplied is ignored. The gas day is that applicable under the pipeline contract or market rules.",
    "CapacityType": "Capacity type values can be: STORAGE — Holding capacity in storage; or MDQ — Daily maximum firm capacity under the expected operating conditions.",
    "OutlookQuantity": "Capacity outlook quantity in TJ to three decimal places. Three decimal places is not required if the value has trailing zeros after the decimal place.",
    "FlowDirection": "Gas flow direction. Values can be: RECEIPT, DELIVERY, PROCESSED, DELIVERYLNGSTOR.",
    "CapacityDescription": "Free text to describe the meaning of the capacity number provided, including a description of material factors that impact the capacity number and any other relevant information. Will only be shown for Pipelines, Compression facilities and may be shown for LNGImport facilities.",
    "ReceiptLocation": "The Connection Point Id that best represents the receipt location. The Receipt Location in conjunction with the Delivery Location indicates the capacity direction and location. Note: Applicable to BB pipelines only. For other BB facilities, this field is populated with -1.",
    "DeliveryLocation": "The Connection Point Id that best represents the delivery location. This location in conjunction with the Receipt Location indicates the capacity direction and location. Note: Applicable to BB pipelines only. For other BB facilities, this field is populated with -1.",
    "ReceiptLocationName": "The name of the receipt location.",
    "DeliveryLocationName": "The name of the delivery location.",
    "Description": "Comments about the quantity or change in Outlook Quantity relating to the Facility Id, and the times, dates, or duration which those quantities or changes in quantities.",
    "LastUpdated": "Date and time record was last modified.",
}

report_purpose = """
Provides a report of the Capacity Outlook for the medium term to identify possible impact to future supply.

Two report types exist:
- GASBB_MEDIUM_TERM_OUTLOOK_FULL_LIST: Contains historic and future outlooks, updated daily.
- GASBB_MEDIUM_TERM_OUTLOOK_FUTURE: Contains the current and future outlooks, updated within 30 minutes of receiving new data.

Each record represents the outlook for one facility, for a range of gas days (FromGasDate to ToGasDate), for one type of capacity, and a given flow direction.

The report supports understanding medium-term constraints or capacities on gas facilities such as pipelines, storage, and LNG.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
