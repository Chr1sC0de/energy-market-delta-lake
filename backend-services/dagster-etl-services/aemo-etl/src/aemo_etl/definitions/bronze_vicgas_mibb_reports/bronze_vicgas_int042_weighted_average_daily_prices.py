from polars import Datetime, Float64, String

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.definitions.utils import definition_builder_factory
from aemo_etl.register import definitions_list, table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_vicgas_int042_weighted_average_daily_prices"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int042*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["gas_date"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "imb_dev_wa_dly_price_gst_ex": Float64,
    "current_date": Datetime(time_unit="ms", time_zone="UTC"),
}

schema_descriptions = {
    "gas_date": "Gas day for the reference prices e.g. 30 Jun 2007",
    "imb_dev_wa_dly_price_gst_ex": """Imbalance and deviation weighted average daily price:
( ∑S,MP |$imb S,MP |+ ∑SI,MP |$dev SI,MP |) / ( ∑S,MP |imb S,MP |+ ∑SI,MP | dev SI,MP |)
Where:
$imb S,MP = $ of imbalance payments for Market participant MP in Schedule S
$dev SI,MP = $ of deviation payments for Market participant MP in Schedule Interval SI
imb S,MP = GJ of imbalance amount for Market participant MP in Schedule S
dev SI,MP = GJ of deviation amount for Market participant MP in Schedule Interval SI""",
    "current_date": "Date and Time Report Produced e.g. 29 Jun 2007 01:23:45",
}

report_purpose = """
This report is available to Participants for use in settlement for off-market hedge contracts. Potentially it is also useable as
benchmark price of gas in contract negotiations. Traders may wish to user the report to get a daily perspective of the value of
gas in a day.

This report can be read in conjunction with INT041 which relates to the actual market ex ante prices and the calculated
"reference prices".

This report provides a weighted average daily price based on the total imbalance and deviation payments.

The report provides another perspective of the market pricing of gas. Again these average prices are only for information and
analysis purposes and are not used in the actual settlement of the gas day.

Each report contains the:
- gas date
- weighted average daily price for imbalance and deviation (GST exclusive)
- date and time when the report was produced

The report should contain one row representing each gas day in a month. Therefore in a month consisting of 30 days, the user
can expect to see 30 rows of data.
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
)

definitions_list.append(definition_builder.build())
