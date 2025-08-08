from polars import Int64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │           define table and register for Linepack Capacity Adequacy reports             │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_linepack_capacity_adequacy"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbblinepackcapacityadequacy*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "GasDate",
    "FacilityId",
    "LastUpdated"
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "GasDate": String,
    "FacilityId": Int64,
    "FacilityName": String,
    "FacilityType": String,
    "Flag": String,
    "Description": String,
    "LastUpdated": String,
}

schema_descriptions = {
    "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",
    "FacilityId": "A unique AEMO defined Facility identifier.",
    "FacilityName": "The name of the BB facility.",
    "FacilityType": "The type of facility (e.g., COMPRESSOR, PIPE).",
    "Flag": "The flags are traffic light colours (Green, Amber, Red) indicating the LCA status for each pipeline.",
    "Description": "Free text facility use is restricted to a description for reasons or comments directly related to the change in the LCA flag and the times, dates, or duration for which those changes are expected to apply.",
    "LastUpdated": "The date when the record was last updated.",
}

report_purpose = """
This report provides the Linepack Capacity Adequacy for each Pipeline for the current and next 2 gas days (D to D+2).

The report is produced daily and contains both historical and future data.

LCA flags for BB pipelines:
- GREEN: Pipeline is able to accommodate increased gas flows and the conditions for Amber or Red are not met.
- AMBER: Pipeline is flowing at full capacity, but no involuntary curtailment of 'firm' load is likely or happening.
- RED: Involuntary curtailment of 'firm' load is likely or happening, or linepack has, or is forecast to, drop below minimum operating levels.

The report can be filtered by:
- GasDate
- FacilityId, multiple Facility Ids, or all Facility Ids
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
