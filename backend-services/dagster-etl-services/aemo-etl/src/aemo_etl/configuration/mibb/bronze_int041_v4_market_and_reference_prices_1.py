from polars import Float64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS,
)
from aemo_etl.register import table_locations
from aemo_etl.util import newline_join

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int041_v4_market_and_reference_prices_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int041_v4_market_and_reference_prices_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = ["gas_date"]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "price_bod_gst_ex": Float64,
    "price_10am_gst_ex": Float64,
    "price_2pm_gst_ex": Float64,
    "price_6pm_gst_ex": Float64,
    "price_10pm_gst_ex": Float64,
    "imb_wtd_ave_price_gst_ex": Float64,
    "imb_inj_wtd_ave_price_gst_ex": Float64,
    "imb_wdr_wtd_ave_price_gst_ex": Float64,
    "current_date": String,
}

schema_descriptions = {
    "gas_date": "Gas day for the reference prices e.g. 30 Jun 2007",
    "price_bod_gst_ex": "Beginning of day (BoD) ex ante price.",
    "price_10am_gst_ex": "10:00 AM schedule ex ante price",
    "price_2pm_gst_ex": "2:00 PM schedule ex ante price",
    "price_6pm_gst_ex": "6:00 PM schedule ex ante price",
    "price_10pm_gst_ex": "10:00 PM schedule ex ante price",
    "imb_wtd_ave_price_gst_ex": """Imbalance weighted average daily price:
∑S,MP |$imb S,MP |/ ∑S,MP | imb S,MP |
Where:
$imb S,MP = $ of imbalance payments for Market participant MP in Schedule S
imb S,MP = GJ of imbalance amount for Market participant MP in Schedule S""",
    "imb_inj_wtd_ave_price_gst_ex": """Injection Imbalance weighted average daily price:
∑S,MP |$inj imb S,MP | / ∑S,MP | inj imb S,MP |
Where:
$ inj imb S,MP = $ of imbalance payments for injections only for Market participant MP in Schedule S
inj imb S,MP = GJ of imbalance amount for injections only for Market participant MP in Schedule S""",
    "imb_wdr_wtd_ave_price_gst_ex": """Withdrawal Imbalance weighted average daily price:
∑S,MP |$wdr imb S,MP | / ∑S,MP | wdr imb S,MP |
Where:
$ wdr imb S,MP = $ of imbalance payments for withdrawals only for Market participant MP in Schedule S
wdr imb S,MP = GJ of imbalance amount for withdrawals only for Market participant MP in Schedule S""",
    "current_date": "Date and Time Report Produced e.g. 29 Jun 2007 01:23:45",
}

report_purpose = """
This report is to provide a clear picture of the actual market ex ante prices and calculated reference prices across a gas day
used for settling the Declared Wholesale Gas Market. Therefore the market prices reported will use any administered price in
place of the market price in this report. Effectively average daily prices are also inclusive of any administered prices. To view
the market price determined by AEMO's market schedule please see INT037b, INT235 or INT310.

Participants may wish to use this report to track an average daily price of gas over time. It may also be possible to use these
prices as strike prices in off market hedge contracts that may develop over time.

Note the average prices are not used for settling the market, only the prices set for each scheduling horizon are used in the
settlement of a gas day.

This report is produced after each last approved pricing schedule for the day and shows the data over a 14-day rolling period.
Each report will contain a price for each of the 5 pricing schedules for the day and also include 3 forms of average daily pricing:
- imbalance weighted average daily price
- injection imbalance weighted average daily price
- withdrawal imbalance weighted average daily price
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"
