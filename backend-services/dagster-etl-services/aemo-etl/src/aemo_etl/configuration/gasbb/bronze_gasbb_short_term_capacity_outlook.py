from polars import Float64, Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │           define table and register for Short Term Capacity Outlook reports            │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_short_term_capacity_outlook"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbshorttermcapacityoutlook*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "GasDate",
    "FacilityId",
    "FlowDirection",
    "ReceiptLocation",
    "DeliveryLocation",
    "LastUpdated"
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
    "FacilityId": "A unique AEMO defined Facility Identifier.",
    "FacilityName": "The name of the BB facility.",
    "CapacityType": "STORAGE — Holding capacity; MDQ — Daily max firm capacity under expected conditions.",
    "CapacityTypeDescription": "Description of the capacity type (e.g. daily max firm capacity under expected conditions).",
    "OutlookQuantity": "Capacity outlook quantity to 3 decimal places.",
    "FlowDirection": "Direction of gas flow: RECEIPT, DELIVERY, PROCESSED, DELIVERYLNGSTOR.",
    "CapacityDescription": "Free text describing meaning of capacity number and material factors (for pipelines/compressors).",
    "ReceiptLocation": "Connection Point ID representing the receipt location. -1 for non-pipeline facilities.",
    "DeliveryLocation": "Connection Point ID representing the delivery location. -1 for non-pipeline facilities.",
    "ReceiptLocationName": "Description of the Receipt Location (BB pipelines only).",
    "DeliveryLocationName": "Description of the Delivery Location (BB pipelines only).",
    "Description": "Comments about quantity or changes, timing, dates or durations relating to the record.",
    "LastUpdated": "Timestamp of last modification.",
}

report_purpose = """
This report displays the expected daily capacity of a BB facility for the next seven days. It helps traders and market 
participants to understand projected network capabilities and restrictions.

Two report types exist:
- GASBB_SHORT_TERM_CAPACITY_OUTLOOK: Historical outlooks updated daily.
- GASBB_SHORT_TERM_CAPACITY_OUTLOOK_FUTURE: Forecast data updated within 30 minutes of new input.

Each record represents the outlook for one facility, on one gas day, for one type of capacity, and a given flow direction.

The report supports understanding short-term constraints or capacities on gas facilities such as pipelines, storage, and LNG.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
