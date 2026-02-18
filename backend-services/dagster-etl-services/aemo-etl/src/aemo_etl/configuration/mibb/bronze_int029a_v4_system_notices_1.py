"""bronze_int029a_v4_system_notices_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int029a_v4_system_notices_1",
        s3_file_glob="int029a_v4_system_notices_1*",
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
            "system_wide_notice_id": "Id of the Notice",
            "critical_notice_flag": "",
            "system_message": "SWN SMS message",
            "system_email_message": "SWN email message",
            "notice_start_date": " e.g. 14 Feb 2007 11:48:55. Sorted descending.",
            "notice_end_date": "e.g. 23 Jul 2007 16:30:35",
            "url_path": "Path to any attachment included in the notice e.g. Public/Master_MIBB_report_list.zip",
            "current_date": "Date and time the report was produced e.g. Jul 23 2007 16:30:35",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report is a CSV file (INT029a) published by AEMO containing public system-wide notices shared on the MIBB.\nIt provides consistent and timely market operation updates and mirrors the content of the HTML version (INT105).\nThese reports are for public viewing, unlike similar reports (INT029b and INT106) sent to specific participants.\n\nKey points:\n\nPurpose: Public communication of market notices.\n\nFormat: CSV (INT029a) and HTML (INT105), both containing the same information.\n\nTiming: Issued simultaneously when AEMO publishes a system-wide notice.\n\nContent: Includes the issue date/time, urgency level, effective period, and source for further details.\n\nNotices are listed from most recent to oldest.\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
