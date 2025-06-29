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


table_name = "bronze_int140_v5_gas_quality_data_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int140_v5_gas_quality_data_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "mirn",
    "gas_date",
    "ti",
    "quality_type",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "mirn": String,
    "gas_date": String,
    "ti": Int64,
    "quality_type": String,
    "unit": String,
    "quantity": Float64,
    "meter_no": String,
    "site_company": String,
    "current_date": String,
}

schema_descriptions = {
    "mirn": "Meter Installation Registration Number",
    "gas_date": "Gas day being reported e.g. 30 June 2007",
    "ti": "Time interval of the gas day (1-24), where 1 = 6:00 AM to 7:00 AM, 2 = 7:00 AM to 8:00 AM, until the 24th hour",
    "quality_type": "Gas quality types including: Wobber index, Hydrogen Sulphide, Total sulphur, Temperature, Heating value, Relative Density, Odorisation; Gas Composition types including: Methane, Ethane, Propane, N-Butane, I-Butane, N-Pentane, I-Pentane, Neo-Pentane, Hexanes, Nitrogen, Carbon Dioxide, Hydrogen",
    "unit": "Unit of measurement",
    "quantity": "Measurement value (some values are averaged instantaneous values for the hour)",
    "meter_no": "CTM meter number",
    "site_company": "Company name",
    "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
}

report_purpose = """
This report provides a measure of gas quality and composition at injection points as outlined in Division 3 / Subdivision 3 Gas
Quality, of the NGR. It is important for the Distribution Network Operators as they have the right to refuse the injection of out of
specification gas into their distribution networks.

Most of the data provided are hourly average values, although some are spot (instantaneous) readings.
Not all gas quality measures are provided for each injection point. The data provided for a particular injection point differs by
the gas source for and monitoring equipment at the point.

This report is generated each hour. Each report displays gas quality and composition details for the previous 3 hours at least.
For example, the report published at 1:00 PM contains details for:
- 12:00 (ti=7)
- 11:00 (ti=6)
- 10:00 (ti=5)

Time interval which shows each hour in the gas day, where 1 = 6:00 AM to 7:00 AM, 2 = 7:00 AM to 8:00 AM, until the 24th
hour.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"
