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


table_name = "bronze_int291_v4_out_of_merit_order_gas_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int291_v4_out_of_merit_order_gas_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "statement_version_id",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "statement_version_id": Int64,
    "ancillary_amt_gst_ex": Float64,
    "scheduled_out_of_merit_gj": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas day dd mmm yyy e.g.30 Jun 2008",
    "statement_version_id": "Statement version ID",
    "ancillary_amt_gst_ex": "Total estimated AP for the gas day (net position as at the last schedule of the day) ancillary_amt_gst_ex = SUM(payment_amt) FROM ap_daily_sched_mirn per gas_date for inj_wdl_flag = 'I'",
    "scheduled_out_of_merit_gj": "Net out of merit order GJs scheduled and delivered over the day scheduled_out_of merit_gj = SUM(ap_qty_gj) FROM ap_constrained_up per gas_date for inj_wdl_flag = 'I'",
    "current_date": "Current report run date time. Format dd Mmm yyyy hh:mi:ss e.g. 15 May 2008 12:22:12",
}

report_purpose = """
This is a public report generated for actual volumes of gas that contribute to APs (volumes of out of merit order gas). Report to
be on the issue of each settlement (M+7, M+18 and M+118).
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"
