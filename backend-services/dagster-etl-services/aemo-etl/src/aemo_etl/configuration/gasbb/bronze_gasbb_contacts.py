"""bronze_gasbb_contacts - Bronze GASBB report configuration."""

from polars import Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_contacts",
        s3_file_glob="gasbbcontacts*",
        primary_keys=["PersonId", "LastUpdated"],
        table_schema={
            "PersonId": Int64,
            "PersonName": String,
            "CompanyName": String,
            "CompanyId": Int64,
            "Position": String,
            "Email": String,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "PersonId": "Person unique identifier.",
            "PersonName": "Name of the person.",
            "CompanyName": "Company name associated with the person.",
            "CompanyId": "Company ID associated with the person.",
            "Position": "Job title of person.",
            "Email": "Email address of person.",
            "LastUpdated": "Date and time the record was last modified.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nProvides a report of registered contact details for each participant.\n\nThis report is updated daily and shows current records.\n",
    )
