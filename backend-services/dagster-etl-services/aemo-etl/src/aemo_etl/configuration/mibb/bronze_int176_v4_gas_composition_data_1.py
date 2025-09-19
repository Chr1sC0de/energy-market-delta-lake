from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int176_v4_gas_composition_data_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int176_v4_gas_composition_data_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "hv_zone",
    "gas_date",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "hv_zone": Int64,
    "hv_zone_desc": String,
    "gas_date": String,
    "methane": Float64,
    "ethane": Float64,
    "propane": Float64,
    "butane_i": Float64,
    "butane_n": Float64,
    "pentane_i": Float64,
    "pentane_n": Float64,
    "pentane_neo": Float64,
    "hexane": Float64,
    "nitrogen": Float64,
    "carbon_dioxide": Float64,
    "hydrogen": Float64,
    "spec_gravity": Float64,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "hv_zone": "Heating value zone number as assigned by the AEMO. Values for Victoria can be in the range of 400-699",
    "hv_zone_desc": "The heating value zone",
    "gas_date": "The gas date (e.g. 30 Jun 2011)",
    "methane": "The daily average of methane",
    "ethane": "The daily average of ethane",
    "propane": "The daily average of propane",
    "butane_i": "The daily average of butane",
    "butane_n": "The daily average of butane (N)",
    "pentane_i": "The daily average of pentane",
    "pentane_n": "The daily average of pentane (N)",
    "pentane_neo": "The daily average of pentane (Neo)",
    "hexane": "The daily average of hexane",
    "nitrogen": "The daily average of nitrogen",
    "carbon_doxide": "The daily average of carbon dioxide",
    "hydrogen": "The daily average of hydrogen. If no hourly values are available for the entire day, NULL is displayed.",
    "spec_gravity": "The daily average of specific gravity",
    "current_date": "The date and time the report is produced (e.g. 29 Jun 2012 01:23:45)",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This public report provides the gas composition daily average corresponding to the heating value zone.

The gas composition daily average in the report has taken into account the total delay hours from the injection source to the
heating value zone. Therefore, the HV is always published one day in arrears.
The data in this report applies to the VIC wholesale gas market.

All gas composition values used in the daily average calculation are taken as at top of hour.
This report contains data for the past 60 gas days (such as, 60 gas days less than report date).
Only the Victorian heating value zones are included in this report.
Gas composition values are in molecule percentage units, except for Specific Gravity (which does not have a unit).
Gas composition data will be reported to 5 decimal places.

The gas composition daily average is calculated using the following formula:
- SUM(hourly gas composition values) / COUNT(hours)
- Where hours is the number of hours used to calculate the total gas composition for the day
- Where no value is available for an hour, the report skips the hour in the calculation and continues on to the
  next hour. If no hourly values are available for the entire day, a NULL is displayed.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
