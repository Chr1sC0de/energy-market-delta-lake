from polars import String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_nt_lng_flow"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbntlngflow*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "Gas Date",
    "Total Receipts",
    "Total Deliveries",
]

upsert_predicate = newline_join(
    *[f"s.`{col}` = t.`{col}`" for col in primary_keys], extra="and "
)

table_schema = {
    "Gas Date": String,
    "Total Receipts": String,
    "Total Deliveries": String,
}

schema_descriptions = {
    "Gas Date": "Gas Date",
    "Total Receipts": "Total Receipts",
    "Total Deliveries": "Total Deliveries",
}

report_purpose = """
Report outlining lng total flows
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
