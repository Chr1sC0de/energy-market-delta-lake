from polars import String, Float64, Int64

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.bronze_vicgas_mibb_reports.utils import (
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
    definition_builder_factory,
)
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_int322b_v4_uplift_breakdown_prud_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int322b_v4_uplift_breakdown_prud_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "sched_no",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "sched_no": Int64,
    "total_uplift_amt": Float64,
    "tuq_qty": Float64,
    "dts_uplift_amt": Float64,
    "final_qds_gj": Float64,
    "event_cap_rate": Float64,
    "event_liability_amt": Float64,
    "event_liability_qty": Float64,
    "annual_cap_limit": Float64,
    "annual_liability_amt": Float64,
    "annual_liability_qty": Float64,
    "net_dts_uplift_amt": Float64,
    "modified_surprise_uplift_amt": Float64,
    "modified_surprise_uplift_qty": Float64,
    "common_uplift_amt": Float64,
    "common_uplift_qty": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas date in format dd mmm yyyy",
    "sched_no": "Schedule number",
    "total_uplift_amt": "Total uplift amount",
    "tuq_qty": "TUQ quantity",
    "dts_uplift_amt": "DTS uplift amount",
    "final_qds_gj": "Final QDS in GJ",
    "event_cap_rate": "Event cap rate",
    "event_liability_amt": "Event liability amount",
    "event_liability_qty": "Event liability quantity",
    "annual_cap_limit": "Annual cap limit",
    "annual_liability_amt": "Annual liability amount",
    "annual_liability_qty": "Annual liability quantity",
    "net_dts_uplift_amt": "Net DTS uplift amount",
    "modified_surprise_uplift_amt": "Modified surprise uplift amount",
    "modified_surprise_uplift_qty": "Modified surprise uplift quantity",
    "common_uplift_amt": "Common uplift amount",
    "common_uplift_qty": "Common uplift quantity",
    "current_date": "Date and Time Report Produced, e.g. 29 Jun 2007 01:23:45",
}

report_purpose = """
This is a public Report, to show the breakdown of prudential run Uplift payments for gas days from 1 January 2023 onwards.
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
