"""bronze_int438_v4_bmp_version_non_pts_1 - Bronze MIBB report configuration."""

from polars import Int64, String

from aemo_etl.configuration import VICTORIAN_GAS_RETAIL_REPORTS_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int438_v4_bmp_version_non_pts_1",
        s3_file_glob="int438_v4_bmp_version_non_pts_1*",
        primary_keys=["network_name", "version_id", "version_from_date"],
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
            "network_name": "Network name",
            "version_id": "Set to BMP run id",
            "extract_type": "Type (e.g. F for Final, P for Preliminary, R = Revision)",
            "version_from_date": "Effective start date",
            "version_to_date": "Effective end date e.g. 30 Jun 2007",
            "issued_date": "Transfer to MIBB date. (dd mm yyyy hh:mm:ss)",
            "current_date": "Time Report Produced e.g. 29 Jun 2007 01:23:45",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the run version of the basic meter profiles system (BMP) used by AEMO when producing the preliminary,\nfinal and revised settlement versions. Market participants may wish to use this report as a reference for settlement\nreconciliation processing.\n\nThis public report is produced daily on BMP run.\nEach report shows the unique name for each network and only reports the non-DTS (Declared transmission system) networks.\n\nEach report contains the:\n- network name\n- version id\n- extract type\n- version dates\n- issued date\n- date and time when the report was produced\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}",
    )
