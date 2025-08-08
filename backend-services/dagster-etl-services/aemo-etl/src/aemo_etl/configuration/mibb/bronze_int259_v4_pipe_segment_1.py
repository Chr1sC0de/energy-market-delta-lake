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


table_name = "bronze_int259_v4_pipe_segment_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int259_v4_pipe_segment_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "pipe_segment_id",
    "commencement_date",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "pipe_segment_id": Int64,
    "pipe_segment_name": String,
    "linepack_zone_id": Int64,
    "commencement_date": String,
    "termination_date": String,
    "node_destination_id": Int64,
    "node_origin_id": Int64,
    "diameter": Float64,
    "diameter_paired": Float64,
    "length": Float64,
    "max_pressure": Float64,
    "min_pressure": Float64,
    "max_pressure_delta": Float64,
    "pressure_at_regulator_outlet": Float64,
    "regulator_at_origin": String,
    "reverse_flow": String,
    "compressor": String,
    "mean_pipe_altitude": Int64,
    "last_mod_date": String,
    "current_date": String,
}

schema_descriptions = {
    "pipe_segment_id": "Pipe segment id e.g. 1",
    "pipe_segment_name": "Pipe segment name e.g. Pre-Longford to Longford",
    "linepack_zone_id": "Linepack zone id e.g. 6",
    "commencement_date": "Commencement date e.g. 21 Jun 2001",
    "termination_date": "Termination date e.g. 21 Jun 2001",
    "node_destination_id": "Node destination id e.g. 3",
    "node_origin_id": "Last of the location node at the beginning of the segment e.g. 3",
    "diameter": "Last of diameter of pipe segment e.g. 74139999999999995",
    "diameter_paired": "Last of diameter of a parallel pipeline e.g. 741399999999995",
    "length": "Last of the length of pipe segment e.g. 64.79789999999998",
    "max_pressure": "Last of Max of available operating pressure e.g. 6850.0",
    "min_pressure": "Last of the operational minimum pressure e.g. 3500.0",
    "max_pressure_delta": "Last of max pressure differentials along a segment e.g. 1350.0",
    "pressure_at_regulator_outlet": "Pressure at regulator outlet e.g. 2760.0",
    "regulator_at_origin": "Yes denotes that a regulator exists e.g. N",
    "reverse_flow": "Yes denotes that the reverse flow os allowed e.g. Y",
    "compressor": "Yes denotes that the pipe segment has a compressor station on it e.g. N",
    "mean_pipe_altitude": "Mean pipe altitude e.g. 56",
    "last_mod_date": "Time last modified e.g. 20 Jun 2001 16:44:46",
    "current_date": "Time the report is produced e.g. 21 Jun 2001 16:44:46",
}

report_purpose = """
This report contains the current pipe segment definitions.

This public report is produced each time a change occurs.
The report is similar to INT258 and shows minimum and maximum volumes for pipelines and the pressure of gas.

Each report contains the:
- pipe segment id and name
- linepack zone id
- commencement and termination dates
- node destination and origin id
- pipe segment measurements
- details of pressure
- if a regulator, reverse flow and compressor exists
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
