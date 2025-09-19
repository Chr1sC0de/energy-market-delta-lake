from polars import Float64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.register import table_locations

key_prefix = ["bronze", "aemo", "gasbb"]

table_name = "bronze_gasbb_gsh_gas_trades"

s3_prefix = "aemo/gasbb"

s3_file_glob = "gasbbgshgastrades*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "TRADE_DATE",
    "TYPE",
    "PRODUCT",
    "LOCATION",
    "START_DATE",
    "END_DATE",
    "MANUAL_TRADE",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"


table_schema = {
    "TRADE_DATE": String,
    "TYPE": String,
    "PRODUCT": String,
    "LOCATION": String,
    "TRADE_PRICE": Float64,
    "DAILY_QTY_GJ": Float64,
    "START_DATE": String,
    "END_DATE": String,
    "MANUAL_TRADE": String,
    "surrogate_key": String,
}


schema_descriptions = {
    "TRADE_DATE": "Date of the trade",
    "TYPE": "Trade Type",
    "PRODUCT": "Trade Product",
    "LOCATION": "Location",
    "TRADE_PRICE": "Price",
    "DAILY_QTY_GJ": "Quantity",
    "START_DATE": "Start Date",
    "END_DATE": "End Date",
    "MANUAL_TRADE": "Manual Trade?",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
The file below provides a complete list of historical trades.
This data can be used to analyse market trends over time.
If you are after a more simple and straightforward representation of price trends in the GSH,
the benchmark price report (outlined below) may be more appropriate.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}

group_name = "aemo__gasbb"
