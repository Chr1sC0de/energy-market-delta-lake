from polars import Float64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_GAS_RETAIL_REPORTS_DETAILS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_int139_v4_declared_daily_state_heating_value_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int139_v4_declared_daily_state_heating_value_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["gas_date"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "declared_heating_value": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas day being reported (e.g. 30 Jun 2007)",
    "declared_heating_value": """Declared daily state heating value
Sum(h,z [HV(z,h) *(CF(z,h)) ])/Sum(h,z (CF(h,z))
h= hour index
z=zone index
CF Corrected flow
HV Heating Value""",
    "current_date": "Date and time report produced (e.g. 30 Jun 2007 06:00:00)",
}

report_purpose = """
This report provides the declared daily state heating value (HV) which is used by gas retailers and distribution businesses in
their billing processes, to convert the difference in (actual or estimated) index readings from basic meters to energy
consumption figures. The use of this state wide declared heating value is prescribed in the Victorian Distribution system code
issued by the Essential Services Commission of Victoria. Section 2.6.1 (b) of the Victorian Retail Market Procedures describes
AEMO obligation to publish the daily state heating value and the obligation that the Distributor must use this value to calculate
the average heating value for a reading period.

The reported values are the volume-weighted average HVs of all Victoria's heating value zones.
Note the values in this report are not normally subject to revision.

This report is generated daily. Each report displays the daily state HV for the previous 90 days (not including the current gas
day).

Each row in the report provides the daily state HV for the specified gas_date.

Since daily state HV is calculated on the basis of hourly HV readings, the latest possible daily state HV available is for the
previous full gas day. This means that daily state HV is always published 1 day in arrears.

Note: This report is decommissioned from December 2024.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}"
