"""bronze_int471_v4_latest_nsl_non_pts_rpt_1 - Bronze MIBB report configuration."""

from polars import Float64, String

from aemo_etl.configuration import VICTORIAN_GAS_RETAIL_REPORTS_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int471_v4_latest_nsl_non_pts_rpt_1",
        s3_file_glob="int471_v4_latest_nsl_non_pts_rpt_1*",
        primary_keys=["nsl_update", "network_name", "gas_date", "distributor_name"],
        table_schema={
            "nsl_update": String,
            "network_name": String,
            "gas_date": String,
            "distributor_name": String,
            "nsl_gj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "nsl_update": "Date and Time profile created",
            "network_name": "Primary Key for MIBB report",
            "gas_date": "Primary Key for MIBB report (e.g. 30 Jun 2007)",
            "distributor_name": "Primary Key for MIBB report",
            "nsl_gj": "Daily nsl energy for a DB",
            "current_date": "Date and Time report created",
            "surrogate_key": """
                Unique identifier created using sha256 over the primary keys
            """,
        },
        report_purpose="""
            This report provides the daily net system load (NSL) for each distribution
            area for a non-DTS (declared transmission system) network for the past 3
            years. This report may be used as a reference for settlement information.

            Section 2.8.4 of the Victorian Retail Market Procedures AEMO's obligation to
            publish the NSL and Attachment 6 of the Victorian Retail Market Procedures
            set out how AEMO calculates the NSL.

            This public report is produced upon generation of NSL. It is similar to
            INT171 but for the non-DTS network and has an additional column for network
            name.

            Each report contains the: - date and time when the NSL was created/updated -
            network name - gas date - distributor name - daily NSL energy for a
            distribution business - date and time when the report was created
        """,
        group_name=f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}",
    )
