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


table_name = "bronze_int381_v4_tie_breaking_event_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int381_v4_tie_breaking_event_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "schedule_interval",
    "transmission_id",
    "mirn",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "schedule_interval": Int64,
    "transmission_id": Int64,
    "mirn": String,
    "tie_breaking_event": Int64,
    "cc_bids": Int64,
    "non_cc_bids": Int64,
    "part_cc_bids": Int64,
    "gas_not_scheduled": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "The date of gas day being reported (for example, 30 Jun 2012)",
    "schedule_interval": "(1,2,3,4 or 5)",
    "transmission_id": "Schedule ID from which results were drawn",
    "mirn": "Meter Registration Identification Number of the system point",
    "tie_breaking_event": "Total tie-breaking event",
    "cc_bids": "If the tie-breaking bids have CC allocated to them, list number of bids with CC allocated to them",
    "non_cc_bids": "If the tie-breaking bids do not have CC allocated to them, list number of bids with no CC allocated to them",
    "part_cc_bids": "If the tie-breaking bids have part CC allocated to them, list number of bids with part CC allocated to them",
    "gas_not_scheduled": "Aggregate tie breaking bids - aggregate tie breaking bids scheduled",
    "current_date": "Date and time report produced (for example, 30 Jun 2012 06:00:00)",
}

report_purpose = """
This report provides information about tie-breaking events that occurred on each gas D on the following gas day D+1.

This report details the tie-breaking events from the previous gas day for the 5 intraday scheduling intervals.
This report does not take into account MPs submitting bids that are inconsistent with their accreditations constraint. In an
event MPs bids exceed their accreditation, a tie breaking event may be incorrectly reported.

Each row in the report provides details for each mirn the tie-breaking events for the previous gas days 5 intraday schedules.
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
