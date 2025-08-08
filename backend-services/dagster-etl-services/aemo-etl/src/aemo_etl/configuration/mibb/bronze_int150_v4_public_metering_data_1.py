from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int150_v4_public_metering_data_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int150_v4_public_metering_data_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "flag",
    "id",
    "ti",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "flag": String,
    "id": String,
    "ti": Int64,
    "energy_gj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas day being reported e.g. as 30 Jun 1998",
    "flag": "WTHDL - int92 withdrawals, INJ - integer 98 injections",
    "id": "Meter registration number or withdrawal zone name",
    "ti": "Trading interval (1-24), where 1= 6:00 AM to 7:00 AM, 2= 7:00 AM to 8:00 AM, until the 24th interval",
    "energy_gj": "Energy value (GJ) (not adjusted for UAFG)",
    "current_date": "Time report produced",
}

report_purpose = """
This public report contains metering data grouped by withdrawal zone and injection point for the previous 2 months. This
report provides an industry overview of what is happening across the system (for example, quantity of energy flow and
injected). This report can be used by Participants to estimate their settlement exposure to the market. Participants should
however be aware that the data is provisional and can change at settlement.

Participants should also be aware that this meter data is what is used by AEMO when prudential processing is done to assess
each Market participants exposure to the market and the likelihood of a margin call being required.

It should be noted that this data is likely to have a proportion generated from substitutions and estimates and should only be
used as a guide to the demand on that day.

A report is produced three business days after the gas date.
This report can be accessed through the MIBB and AEMO websites.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"
