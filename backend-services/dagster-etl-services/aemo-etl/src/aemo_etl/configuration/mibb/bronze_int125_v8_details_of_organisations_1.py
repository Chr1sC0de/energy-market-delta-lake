"""bronze_int125_v8_details_of_organisations_1 - Bronze MIBB report configuration."""

from polars import Int64, String
from aemo_etl.configuration import (
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int125_v8_details_of_organisations_1",
        s3_file_glob="int125_v8_details_of_organisations_1*",
        primary_keys=["company_id", "market_code"],
        table_schema={
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
        },
        schema_descriptions={
            "company_id": "Identifying organisation's id",
            "company_name": "Participant organisation name",
            "registered_name": "Participant organisation registered name",
            "acn": "ACN details of each Market participant",
            "abn": "ABN details of each Market participant",
            "organization_class_name": "Either Non-Participant or Participant or Market-Participant",  # noqa: E501
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
            "market_code": "The code representing the gas market that the Market participant operates in",  # noqa: E501
            "company_code": "The company code used by Market participants to send B2B transactions and receive MIBB/GASBB reports",  # noqa: E501
            "current_date": "Date and Time Report Produced (e.g. 30 June 2005 1:23:56)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report is a public listing of all the registered Market participants.\n\nA report is produced daily at 09:00 hrs AEST.\n\nEach report contains the:\n- company id and name\n- organisation class, type and status\n- province id\n- address and contact numbers\n- the initial registration of a company in gas market systems which determines the organisation type for that company.\n\nFor market code STTM:\n- Organization class name (i.e. Market Participant, Participant, and Non-Participant) should be ignored.\n- Organisation type name of:\n  - Producer should be interpreted as STTM Injection Facility, STTM Net Metered Facility, or STTM Aggregation Facility\n  - Declared Transmission System Service Provider as STTM Pipeline Operator\n  - Allocation Agent should be interpreted as a Shipper who is registered as a sub allocation agent in the STTM.\n\nFor more information about hubs and facilities in the STTM, see the Market Information System (MIS) report INT671 - Hub and\nFacility Definition, which is defined in the STTM Reports Specifications and published on AEMO's website.\n\nThe market_code field represents the gas market that the Market participant operates in:\n- NATGASBB – National Gas Bulletin Board\n- NSWACTGAS – NSW/ACT Retail Gas Market\n- QLDGAS – QLD Retail Gas Market\n- SAGAS – SA Retail Gas Market\n- STTM – Short Term Trading Market\n- VICGAS – VIC Retail Gas Market\n- VICGASW – Declared Wholesale Gas Market\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
