"""bronze_int538_v4_settlement_versions_1 - Bronze MIBB report configuration."""

from polars import Int64, String

from aemo_etl.configuration import QUEENSLAND_GAS_RETAIL_REPORT_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int538_v4_settlement_versions_1",
        s3_file_glob="int538_v4_settlement_versions_1*",
        primary_keys=["network_name", "version_id"],
        table_schema={
            "network_name": String,
            "version_id": Int64,
            "extract_type": String,
            "version_from_date": String,
            "version_to_date": String,
            "issued_date": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "network_name": "Network Name",
            "version_id": "balancing statement version (invoice_id) identifier",
            "extract_type": "P - Provisional, F - Final, R - Revision",
            "version_from_date": "Effective start date. (dd mmm yyyy)",
            "version_to_date": "Effective End date. (dd mmm yyyy)",
            "issued_date": "Issue date of settlement",
            "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report is to display recently issued settlement versions when balancing statement is issued.\nParticipants may wish to use this report as a reference to link other reports together based on invoice id(balancing version).\n\nA report is produced when balancing statement is issued.\nThis report is similar to VIC MIBB report INT438.\n\nEach report contains the:\n- statement version identifier\n- settlement category type\n- effective start date\n- effective end date\n- date of issue\n- date and time when the report was produced\n",  # noqa: E501
        group_name=f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}",
    )
