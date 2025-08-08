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


table_name = "bronze_int135_v4_uplift_cap_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int135_v4_uplift_cap_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "gas_date",
    "schedule_no",
]

upsert_predicate = newline_join(
    *[f"s.{col} = t.{col}" for col in primary_keys], extra="and "
)

table_schema = {
    "gas_date": String,
    "schedule_no": Int64,
    "positive_ave_ancillary_rate": Float64,
    "negative_ave_ancillary_rate": Float64,
    "positive_uplift_rate": Float64,
    "negative_uplift_rate": Float64,
    "current_datetime": String,
}

schema_descriptions = {
    "gas_date": "Gas day Format: dd mm yyyy e.g. 23 Jul 2008",
    "schedule_no": "Pricing schedule horizon that the uplift payment applies to",
    "positive_ave_ancillary_rate": "Positive average ancillary rate over all injection and withdrawal points and all MP's. PAVAPR variable from the ancillary payment calculations.",
    "negative_ave_ancillary_rate": "Negative average ancillary rate over all injection and withdrawal points and all MP's. NAVAPR variable from the ancillary payment calculations.",
    "positive_uplift_rate": "Positive uplift rate. UPR(P) variable from the uplift payment calculation.",
    "negative_uplift_rate": "Negative uplift rate. UPR(N) variable from the uplift payment calculation.",
    "current_datetime": "When report produced. The format is dd mm yyyy hh:mm:ss e.g. 23 Jul 2008 16:30:35",
}

report_purpose = """
To provide aggregated information used in Ancillary and Uplift payments calculations.

This public report is produced whenever ancillary and uplift payments are required.

The variables PAVAPR and NAVAPR are the average rate of ancillary payment as described in the Ancillary Payment
Procedures.

The variables UPR(P) and UPR(N) are part of the uplift rate cap as described in the Uplift Payment Procedures.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}"
