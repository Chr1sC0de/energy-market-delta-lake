from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int284_v4_tuos_zone_postcode_map_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int284_v4_tuos_zone_postcode_map_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "postcode",
    "tuos_zone",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "last_update_datetime": String,
    "postcode": String,
    "tuos_zone": Int64,
    "tuos_zone_desc": String,
    "current_date": String,
}

schema_descriptions = {
    "last_update_datetime": "date time the mapping was last updated in AEMO database (e.g. 30 Jun 2007)",
    "postcode": "Post Code",
    "tuos_zone": "TUOS Zone mapped to post code",
    "tuos_zone_desc": "TUoS Zone description",
    "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 01:23:45)",
}

report_purpose = """
This public report defines the postcodes to TUoS zone mappings used to assign new MIRNs to a TUoS zone for TUoS billing
purposes. It is this mapping that is provided to the Transmission System Service Provider for billing purposes. Retail
businesses can use this report to verify the MIRNs that are being billed in each TUoS zone, and also to confirm the DB
Network to which it is connected and the heating Zone used if it is an interval meter.

A report is produced monthly showing the current transmission tariff zone to postcode mapping.
The report only covers the DTS (declared transmission system) network.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"
