from polars import Float64, Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                define table and register for LNG Shipments report                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_lng_shipments"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbblngshipments*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "TransactionId",
    "FacilityId",
    "VersionDateTime",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "TransactionId": String,
    "FacilityId": Int64,
    "FacilityName": String,
    "VolumePJ": Float64,
    "ShipmentDate": String,
    "VersionDateTime": String,
}

schema_descriptions = {
    "TransactionId": "Unique shipment identifier.",
    "FacilityId": "Unique facility identifier.",
    "FacilityName": "Name of the facility.",
    "VolumePJ": "Volume of the shipment in PJ.",
    "ShipmentDate": "For LNG export facility, the departure date. For LNG import facility, the date unloading commences at the LNG import facility.",
    "VersionDateTime": "Time a successful submission is accepted by AEMO systems.",
}

report_purpose = """
This report displays a list of all LNG shipments.

GASBB_LNG_EXPO_IMPO_SHIPMENTS is updated monthly.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
