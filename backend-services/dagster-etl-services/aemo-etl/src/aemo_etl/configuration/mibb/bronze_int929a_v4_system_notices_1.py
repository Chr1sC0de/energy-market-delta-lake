"""bronze_int929a_v4_system_notices_1 - Bronze MIBB report configuration."""

from polars import Int64, String

from aemo_etl.configuration import ECGS_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int929a_v4_system_notices_1",
        s3_file_glob="int929a_v4_system_notices_1*",
        primary_keys=["system_wide_notice_id"],
        table_schema={
            "system_wide_notice_id": Int64,
            "critical_notice_flag": String,
            "system_message": String,
            "system_email_message": String,
            "notice_start_date": String,
            "notice_end_date": String,
            "url_path": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "system_wide_notice_id": "Id of the ECGS Notice",
            "critical_notice_flag": "Critical notice flag",
            "system_message": "ECGS Notice SMS message",
            "system_email_message": "ECGS Notice email message",
            "notice_start_date": "e.g. 14 Feb 2023",
            "notice_end_date": "e.g. 10 May 2023",
            "url_path": "Path to any attachment included in the notice e.g. Public/ECGS_attachments/document.pdf",  # noqa: E501
            "current_date": "Date and time the report was produced e.g. 30 Jun 2023 09:33:57",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose='\n\nThis report is a comma separated values (CSV) file that contains ECGS notices published by AEMO to the public and is sent to Part 27\nRelevant Entities via email and SMS.\n\nThis report is published to the:\n1. Market Information Bulletin Board (MIBB) public folder\n2. NEMWEB folder: https://www.nemweb.com.au/REPORTS/CURRENT/ECGS/ECGS_Notices/\n\nThis report is published to the MIBB and then replicated to the NEMWeb.\n\nThe dual publication of this report allows existing Victorian DWGM and Gas Retail Market participants to access it via the MIBB. The\ngeneral public and electricity market participants can access this report directly via NEMWeb.\n\nThe "url path" field in the report reflects the MIBB folder location. Any PDF documents that are uploaded to the MIBB folder is\nreplicated to the following locations:\n1. MIBB/Public/ECGS_attachments\n2. www.nemweb.com.au - /REPORTS/CURRENT/ECGS/ECGS_Notices/Attachments/\n\nEach report contains the details of all the general ECGS notices that are in effect for Relevant Entities at the report generation time.\n',  # noqa: E501
        group_name=f"aemo__mibb__{ECGS_REPORTS}",
    )
