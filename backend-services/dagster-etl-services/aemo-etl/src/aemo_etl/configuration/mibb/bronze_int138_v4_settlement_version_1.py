"""bronze_int138_v4_settlement_version_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int138_v4_settlement_version_1",
        s3_file_glob="int138_v4_settlement_version_1*",
        primary_keys=["statement_version_id", "version_from_date"],
        table_schema={
            "statement_version_id": Int64,
            "settlement_cat_type": String,
            "version_from_date": String,
            "version_to_date": String,
            "interest_rate": Float64,
            "issued_date": String,
            "version_desc": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "statement_version_id": "Statement version identifier",
            "settlement_cat_type": "Type (e.g. FNL for Final, PLM for Preliminary)",
            "version_from_date": "Effective start date (e.g. 30 Jun 2007)",
            "version_to_date": "Effective end date (e.g. 30 Jun 2007)",
            "interest_rate": "Interest rate applied to the settlement",
            "issued_date": "Date issued (e.g. 30 Jun 2007)",
            "version_desc": "Description of the version",
            "current_date": "Date and time report produced (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report is to display recently issued settlement versions.\n\nParticipants may wish to use this report as a reference to link other reports together based on settlement version.\n\nA report is produced publicly when settlement statement is issued.\n\nEach report contains the:\n- statement version identifier\n- settlement category type\n- effective state date\n- effective end date\n- interest rate\n- date of issue\n- description of the version\n- date and time when the report was produced\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
