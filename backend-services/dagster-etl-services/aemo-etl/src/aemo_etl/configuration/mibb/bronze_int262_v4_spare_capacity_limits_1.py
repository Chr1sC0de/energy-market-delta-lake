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


table_name = "bronze_int262_v4_spare_capacity_limits_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int262_v4_spare_capacity_limits_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "node_id",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "node_id": Int64,
    "node_name": String,
    "current_system_capacity": Float64,
    "current_lateral_capacity": Float64,
    "max_system_capacity": Float64,
    "min_system_capacity": Float64,
    "max_lateral_capacity": Float64,
    "min_lateral_capacity": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas Date data generated e.g. 02 Feb 2001",
    "node_id": "AMDQ node ID",
    "node_name": "AMDQ node name",
    "current_system_capacity": "Current system spare capacity available for Gas Date (refer to Content notes)",
    "current_lateral_capacity": "Current lateral spare capacity available for Gas Date (refer to Content notes)",
    "max_system_capacity": "Maximum future system spare capacity available for Gas Date (refer to Content notes)",
    "min_system_capacity": "Minimum future system spare capacity available (refer to Content notes)",
    "max_lateral_capacity": "Maximum future lateral spare capacity available (refer to Content notes)",
    "min_lateral_capacity": "Minimum future lateral spare capacity available (refer to Content notes)",
    "current_date": "Date and Time report produced e.g. 21 May 2007 01:32:00",
}

report_purpose = """
This report displays the current and future maximum and minimum 'lateral' and 'system' spare capacity available for each
AMDQ node.

This report is generated daily for the current gas day.

Null capacity values indicate the spare capacity is not calculated for this node as the spare capacity is considered very large.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"
