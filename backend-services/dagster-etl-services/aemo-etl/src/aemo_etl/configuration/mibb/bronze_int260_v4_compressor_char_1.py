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


table_name = "bronze_int260_v4_compressor_char_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int260_v4_compressor_char_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "compressor_id",
    "compressor_station_id",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "compressor_id": Int64,
    "compressor_name": String,
    "pipe_segment_id": Int64,
    "min_pressure_delta": Float64,
    "most_efficient_pressure_delta": Float64,
    "max_pressure_delta": Float64,
    "max_compressor_power": Float64,
    "min_compressor_power": Float64,
    "compressor_efficiency": Float64,
    "compressor_efficiency_at_min": Float64,
    "efficiency_coefficient": Float64,
    "super_compressability_factor": Float64,
    "compressor_station_id": Int64,
    "station_name": String,
    "last_mod_date": String,
    "current_date": String,
}

schema_descriptions = {
    "compressor_id": "Compressor id e.g. 3",
    "compressor_name": "Compressor name e.g. Brooklyn Compressor No 4",
    "pipe_segment_id": "Pipe segment id e.g. 17",
    "min_pressure_delta": "Minimum pressure differential along segment e.g. 250.0",
    "most_efficient_pressure_delta": "Maximum efficiency at optimal pressure differential e.g. 960.0",
    "max_pressure_delta": "Max pressure differentials along a segment e.g. 1110.0",
    "max_compressor_power": "Max power available from each compressor e.g. 850.0",
    "min_compressor_power": "Min power available from each compressor e.g. 450.0",
    "compressor_efficiency": "Max efficiency of the compresorat its optimal pressure differential e.g. 68500000000000005",
    "compressor_efficiency_at_min": "Min efficiency at the least optimal pressure differential e.g. 330000000000000002",
    "efficiency_coefficient": "Coefficient for adjusting the efficiency of the compressor e.g. 1.5",
    "super_compressability_factor": "Super compressability of gas at compressor inlet e.g. 92000000000000004",
    "compressor_station_id": "Compressor station id e.g. 2",
    "station_name": "Station name e.g. Brooklyn Compressor Stage III",
    "last_mod_date": "Time last modified e.g. 10 Jun 2001 16:50:46",
    "current_date": "Time the report is produced e.g. 21 Jun2001 16:50:46",
}

report_purpose = """
This report contains the current compressor characteristics, and this data is used as input to the MCE.

This public report is produced each time when a change occurs.
Each report shows the minimum and maximum pressure change.

Each report contains the:
- compressor id and name
- pipe segment id
- pressure and compressor information
- station name
- last modified date

Note: From 16 December 2024, this report is decomissioned and AEMO does not produce data for it.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
