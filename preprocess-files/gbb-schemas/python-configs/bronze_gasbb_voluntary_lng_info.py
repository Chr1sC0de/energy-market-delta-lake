from polars import String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │        define table and register for Voluntary information from LNG producers          │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_voluntary_lng_info"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbvoluntarylnginfo*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "DocumentId",
    "PublishDate",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "DocumentId": String,
    "Title": String,
    "Description": String,
    "PublishDate": String,
    "DocumentURL": String,
    "ProducerName": String,
    "LastUpdated": String,
}

schema_descriptions = {
    "DocumentId": "Unique identifier for the document.",
    "Title": "Title of the published document.",
    "Description": "Description of the document content.",
    "PublishDate": "Date when the document was published.",
    "DocumentURL": "URL to access the document.",
    "ProducerName": "Name of the LNG producer that provided the document.",
    "LastUpdated": "Date and time when the record was last updated.",
}

report_purpose = """
A list of published documents provided by LNG producers that detail scheduled maintenance events.

This report is updated as required and produced on request.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
