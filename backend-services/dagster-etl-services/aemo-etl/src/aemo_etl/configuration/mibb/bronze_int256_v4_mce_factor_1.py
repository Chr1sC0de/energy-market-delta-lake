from polars import Float64, Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int256_v4_mce_factor_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int256_v4_mce_factor_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "general_information_id",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "general_information_id": Int64,
    "r_factor": Float64,
    "super_compressability_factor": Float64,
    "t_factor": Float64,
    "viscosity": Float64,
    "voll_price": Float64,
    "number_of_steps": Int64,
    "eod_linepack_min": Float64,
    "eod_linepack_max": Float64,
    "commencement_date": String,
    "termination_date": String,
    "last_mod_date": String,
    "current_date": String,
}

schema_descriptions = {
    "general_information_id": "General Information Identifier e.g. 5",
    "r_factor": "Ideal gas constant e.g. 47264",
    "super_compressability_factor": "Super Compressability Factor e.g. 859999999999999999",
    "t_factor": "Temperature of pipelines e.g. 288.0",
    "viscosity": "Viscosity e.g. 1.15e-005",
    "voll_price": "VOLL_Price ($/GJ) e.g. 800.0",
    "number_of_steps": "MCE Iterator e.g. 4",
    "eod_linepack_min": "End of Day Line Pack Minimum e.g. 0.0",
    "eod_linepack_max": "End of Day Line Pack Maximum e.g. 10000000000000001",
    "commencement_date": "e.g. 18 Jun 2001 16:34:57",
    "termination_date": "e.g. 19 Jun 2001 16:34:57",
    "last_mod_date": "Time last modified e.g. 20 Jun 2001 16:34:57",
    "current_date": "Date and Time the report is produced e.g. 21 Jun 2001 16:34:57",
}

report_purpose = """
This report lists what the standard parameters are that are used as input data for Market Clearing Engine (MCE) in generating
schedules for the market.

This public report shows the current MCE factors and is produced when a change occurs to the factors.

Each report contains the general information identifier.

Note: From 16 December 2024, this report is decomissioned and AEMO does not produce data for it.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
