from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int839a_v1_daily_zonal_hv_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int839a_v1_daily_zonal_hv_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "hv_zone",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "hv_zone": Int64,
    "hv_zone_description": String,
    "heating_value_mj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas day being reported e.g. 30 Jun 2007. Covering a period of 120 gas days (as available).",
    "hv_zone": "Heating value zone as assigned by the distributor",
    "hv_zone_description": "Name of the heating value zone",
    "heating_value_mj": "The Heating value is in MJ per standard cubic meters",
    "current_date": "Report generation date and timestamp. Date format dd Mmm yyyy hh:mm:ss",
}

report_purpose = """
This report provides the daily heating value for each heating value zone for NSW/ACT networks (COUNTRY or NSWCR).

AEMO processes files sent by distributors and publishes the heating values via this public MIBB report.
This process is only applicable to Network NSWCR and COUNTRY.

The 'Published Daily Zonal heating value for the day' is a CSV report listing all of the Heating
Value zones where the distributor is the current distributor.

This report contains data for a period of 120 gas days (as available).
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS}"
