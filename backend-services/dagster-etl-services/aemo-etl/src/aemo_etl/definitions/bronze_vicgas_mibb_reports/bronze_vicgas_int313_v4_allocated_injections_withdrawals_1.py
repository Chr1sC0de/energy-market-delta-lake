from polars import Date, Float64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.utils import (
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_vicgas_int313_v4_allocated_injections_withdrawals_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int313_v4_allocated_injections_withdrawals_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "gas_hour",
    "phy_mirn",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": Date,
    "gas_hour": String,
    "site_company": String,
    "phy_mirn": String,
    "inject_withdraw": String,
    "energy_flow_gj": Float64,
}

schema_descriptions = {
    "gas_date": "dd mmm yyyy",
    "gas_hour": "The start time of the gas day 9:00:00 pre GMP and 6:00:00 post GMP start",
    "site_company": "Site Company Name",
    "phy_mirn": "Phy_mirn (commissioned = 'Y', biddin = 'Y')",
    "inject_withdraw": "Sum of Actual Injections",
    "energy_flow_gj": "Actual GJ",
}

report_purpose = """
This is a public report that provides historical injection and controllable withdrawal information in a form that has been
structured to facilitate graphing and trend analysis of the energy flows in the gas network:
- out of the network at transmission withdrawal points
- into the network at transmission injection points.

This report does not contain a current date column to assist in graphing data directly from presented figures.
The energy withdrawals reported in INT313 are controllable withdrawals.

Each report contains daily data for the last 12 months.
For each gas day date reported, a separate row will list the energy flow (in GJ) associated with each transmission pipeline
injection or withdrawal MIRN.
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
    group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
)

definitions_list.append(definition_builder.build())
