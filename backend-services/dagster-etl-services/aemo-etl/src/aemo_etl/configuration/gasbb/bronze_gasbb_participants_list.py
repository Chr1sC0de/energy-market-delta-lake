"""bronze_gasbb_participants_list - Bronze GASBB report configuration."""

from polars import String, Int64

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_participants_list",
        s3_file_glob="gasbbparticipants*",
        primary_keys=["CompanyId"],
        table_schema={
            "CompanyName": String,
            "CompanyId": Int64,
            "OrganisationTypeName": String,
            "ABN": String,
            "CompanyPhone": String,
            "Locale": String,
            "LastUpdated": String,
            "AddressType": String,
            "Address": String,
            "State": String,
            "Postcode": String,
            "CompanyFax": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "CompanyName": "Company name associated with the person.",
            "CompanyId": "Company ID associated with the person.",
            "OrganisationTypeName": "The type of organisation.",
            "ABN": "Australian Business Number for the participant.",
            "CompanyPhone": "Company phone details.",
            "Locale": "Location for the participant.",
            "LastUpdated": "Last changed details.",
            "AddressType": "Type of address.",
            "Address": "Mailing address for the company.",
            "State": "State where the company is located.",
            "Postcode": "Postcode details.",
            "CompanyFax": "Company fax details.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides a list of registered participants in the Gas Bulletin Board system.\n\nThis report is updated daily and shows current records.\n",  # noqa: E501
    )
