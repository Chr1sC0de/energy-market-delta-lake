from polars import Int64, String

from aemo_etl.configuration import BRONZE_BUCKET, ECGS_REPORTS
from aemo_etl.register import table_locations

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

table_name = "bronze_int934_v4_ecgs_contacts_1"

s3_prefix = "aemo/vicgas"

s3_file_glob = "int934_v4_ecgs_contacts_1*"

s3_table_location = f"s3://{BRONZE_BUCKET}/{s3_prefix}/{table_name}"

primary_keys = [
    "company_id",
    "first_name",
    "last_name",
]

upsert_predicate = "s.surrogate_key = t.surrogate_key"

table_schema = {
    "company_name": String,
    "abn": String,
    "company_id": Int64,
    "first_name": String,
    "last_name": String,
    "contact_email": String,
    "current_date": String,
    "surrogate_key": String,
}

schema_descriptions = {
    "company_name": "Relevant entity organisation name",
    "abn": "ABN details of each relevant entity",
    "company_id": "Company identifier",
    "first_name": "First name of the ECGS Responsible Person",
    "last_name": "Last name of the ECGS Responsible Person (sorted by Company_Name then Last_Name)",
    "contact_email": "Email address of the ECGS Responsible Person",
    "current_date": "Date and time the report was produced e.g. 30 Jun 2023 09:33:57",
    "surrogate_key": "Unique identifier created using sha256 over the primary keys",
}

report_purpose = """
This is the Part 27 Register for the purposes of rule 713(1)(b) of the NGR. AEMO only publishes a portion of the Part 27 Register
information required by section 6.1 of the ECGS Procedures.

This report is a comma separated values (CSV) file that contains each Part 27 relevant entity's active ECGS Responsible Person
contacts. The ECGS Responsible Person contact receives ECGS notices from AEMO. This report is published to the:
1. Market Information Bulletin Board (MIBB) public folder
2. NEMWEB folder: https://www.nemweb.com.au/REPORTS/CURRENT/ECGS/

This report is published to the MIBB and then replicated to the NEMWeb.

Each report contains the ECGS Responsible Person contacts of each relevant entity.
"""

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "delta",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


group_name = f"aemo__mibb__{ECGS_REPORTS}"
