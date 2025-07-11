from polars import Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    QUEENSLAND_GAS_RETAIL_REPORT_DETAILS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int583_v4_monthly_cumulative_imb_pos_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int583_v4_monthly_cumulative_imb_pos_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "network_name",
    "version_id",
    "fro_name",
    "distributor_name",
    "withdrawal_zone",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "network_name": String,
    "version_id": Int64,
    "fro_name": String,
    "distributor_name": String,
    "withdrawal_zone": String,
    "curr_cum_date": String,
    "curr_cum_imb_position": String,
    "current_date": String,
}

schema_descriptions = {
    "network_name": "Network Name",
    "version_id": "Settlement statement version identifier",
    "fro_name": "Name of Financially Responsible Organisation",
    "distributor_name": "Distribution business name",
    "withdrawal_zone": "Withdrawal zone",
    "curr_cum_date": "Current cumulative imbalance issue date",
    "curr_cum_imb_position": "Surplus or Deficit or Balance",
    "current_date": "Date and Time report produced 15 Aug 2007 10:06:54",
}

report_purpose = """
This report shows the cumulative imbalance position of Retailers. Retailers may wish to use this report to track their status of
the imbalance to do the necessary adjustments.

This public report is updated at each issue of settlement to show the status of each retailer's imbalance position.
There is no equivalent VIC MIBB report.

Each report contains the:
- network name
- statement version id
- financially Responsible Organisation
- distributor Name
- withdrawal zone
- current cumulative imbalance issue date
- current cumulative imbalance position (Surplus, Deficit or Balanced)
- date and time report produced
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
    group_name=f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}",
)

definitions_list.append(definition_builder.build())
