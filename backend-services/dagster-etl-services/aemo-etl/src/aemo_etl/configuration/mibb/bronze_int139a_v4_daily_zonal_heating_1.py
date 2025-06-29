from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_GAS_RETAIL_REPORTS_DETAILS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int139a_v4_daily_zonal_heating_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int139a_v4_daily_zonal_heating_1*"

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
    "hv_zone_desc": String,
    "heating_value": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Starting hour of gas day being reported, example: 30 Jun 2007",
    "hv_zone": "Heating value zone number as assigned by the AEMO. Values for Victoria can be in the range of 400-699",
    "hv_zone_desc": "Heating value zone name",
    "heating_value": "Daily volume flow weighted average heating value (GJ/1000 m(3)) to two decimal places",
    "current_date": "Date and time report is produced. Example: 30 Jun 2007 06:00:00",
}

report_purpose = """
A report providing the heating value for each heating value zone used to determine the energy content of gas consumed within
Victoria. This is consistent with the Energy Calculation Procedures.

Section 2.6.1 of the Retail Market Procedures (Victoria) provided details on how heating value zones for the basic meter that
changes during the measurement period are to be applied.

The daily zonal heating value calculation is expected to be triggered at approximately 9:30AM each day.

The reported values are the volume-weighted average HVs of each of Victoria's heating value zones.
The values in this report may be subject to revision by AEMO.

This report contains heating values zones for DTS connected DDS and non-DTS connected DDS (i.e. Non-DTS Bairnsdale,
non-DTS South Gippsland, and non-DTS Grampians regions).

This report is generated daily. Each report displays the daily volume weighted average HV for each heating value zone in
Victoria over the previous 90 gas days (not including the current gas day).

Each row in the report provides the heating values for a:
- Heating value zone
- Specific gas date

Since the heating value (HV) is calculated based on hourly HV readings, the latest HV available is for the previous full gas day.
Therefore, the HV is always published one day in arrears.

In the event an hourly HV wasn't available or deemed invalid, it would be substituted according to the set substitution rules.
Unresolved substitutions are reviewed at the end of each month.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}"
