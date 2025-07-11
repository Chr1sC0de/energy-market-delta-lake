from polars import Float64, Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_int342_v4_ccauction_sys_capability_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int342_v4_ccauction_sys_capability_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "zone_id",
    "capacity_period",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "zone_id": Int64,
    "zone_name": String,
    "zone_type": String,
    "capacity_period": String,
    "zone_capacity_gj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "zone_id": "Identifier number of CC zone",
    "zone_name": "Name of CC zone",
    "zone_type": "Type of CC zone. Entry/Exit",
    "capacity_period": "CC product period representing date range period for the capacity",
    "zone_capacity_gj": "Zone capacity as per current model in GJ",
    "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
}

report_purpose = """
This report provides the total CC zone modelled capacities by the auction period.

This report provides the total quantity of each auction product available for allocation on the basis of capacity certificates
auction. The capacity certificates for a capacity certificates zone available for allocation will be the lower of either the
maximum pipeline capacity or maximum facility or system point/s deliverable capacity.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                register the definition                                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


definition_builder = definition_builder_factory(
    report_purpose,
    table_schema,
    schema_descriptions,
    primary_keys,
    upsert_predicate,
    s3_table_location,
    s3_prefix,
    s3_file_glob,
    table_name,
    group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
)

definitions_list.append(definition_builder.build())
