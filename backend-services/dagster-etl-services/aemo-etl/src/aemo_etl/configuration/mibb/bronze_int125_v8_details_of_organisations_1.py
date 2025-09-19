from polars import Int64, String

from aemo_etl.configuration import (
    BRONZE_BUCKET,
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_int125_v8_details_of_organisations_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int125_v8_details_of_organisations_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

# According to the documentation, this report contains a unique key rather than a primary key
# company_id and market_code together form a unique key
primary_keys = [
    "company_id",
    "market_code",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "company_id": Int64,
    "company_name": String,
    "registered_name": String,
    "acn": String,
    "abn": String,
    "organization_class_name": String,
    "organization_type_name": String,
    "organization_status_name": String,
    "line_1": String,
    "line_2": String,
    "line_3": String,
    "province_id": String,
    "city": String,
    "postal_code": String,
    "phone": String,
    "fax": String,
    "market_code": String,
    "company_code": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "company_id": "Identifying organisation's id",
    "company_name": "Participant organisation name",
    "registered_name": "Participant organisation registered name",
    "acn": "ACN details of each Market participant",
    "abn": "ABN details of each Market participant",
    "organization_class_name": "Either Non-Participant or Participant or Market-Participant",
    "organization_type_name": "Bank, Producer, Distributor, Retailer",
    "organization_status_name": "Either New Status or Applicant Status",
    "line_1": "Address details",
    "line_2": "Address details",
    "line_3": "Address details",
    "province_id": "State",
    "city": "City",
    "postal_code": "Postal code",
    "phone": "Phone number",
    "fax": "Fax number",
    "market_code": "The code representing the gas market that the Market participant operates in",
    "company_code": "The company code used by Market participants to send B2B transactions and receive MIBB/GASBB reports",
    "current_date": "Date and Time Report Produced (e.g. 30 June 2005 1:23:56)",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This report is a public listing of all the registered Market participants.

A report is produced daily at 09:00 hrs AEST.

Each report contains the:
- company id and name
- organisation class, type and status
- province id
- address and contact numbers
- the initial registration of a company in gas market systems which determines the organisation type for that company.

For market code STTM:
- Organization class name (i.e. Market Participant, Participant, and Non-Participant) should be ignored.
- Organisation type name of:
  - Producer should be interpreted as STTM Injection Facility, STTM Net Metered Facility, or STTM Aggregation Facility
  - Declared Transmission System Service Provider as STTM Pipeline Operator
  - Allocation Agent should be interpreted as a Shipper who is registered as a sub allocation agent in the STTM.

For more information about hubs and facilities in the STTM, see the Market Information System (MIS) report INT671 - Hub and
Facility Definition, which is defined in the STTM Reports Specifications and published on AEMO's website.

The market_code field represents the gas market that the Market participant operates in:
- NATGASBB – National Gas Bulletin Board
- NSWACTGAS – NSW/ACT Retail Gas Market
- QLDGAS – QLD Retail Gas Market
- SAGAS – SA Retail Gas Market
- STTM – Short Term Trading Market
- VICGAS – VIC Retail Gas Market
- VICGASW – Declared Wholesale Gas Market
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}"
