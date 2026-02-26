"""bronze_int439_v4_published_daily_heating_value_non_pts_1 - Bronze MIBB report configuration."""  # noqa: E501

from polars import Float64, String

from aemo_etl.configuration import VICTORIAN_GAS_RETAIL_REPORTS_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int439_v4_published_daily_heating_value_non_pts_1",
        s3_file_glob="int439_v4_published_daily_heating_value_non_pts_1*",
        primary_keys=["network_name", "gas_day"],
        table_schema={
            "network_name": String,
            "gas_day": String,
            "heating_value": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "network_name": "Network name",
            "gas_day": "Gas day being reported e.g. 30 Jun 2007",
            "heating_value": "Heating Value",
            "current_date": "Time Report Produced e.g. 29 Jun 2007 01:23:45",
            "surrogate_key": """
                Unique identifier created using sha256 over the primary keys
            """,
        },
        report_purpose="""
            This report provides the publish heating values.

            This public report is produced daily. Only reports the non-DTS (Declared
            transmission) networks.

            Note: This report is decommissioned from December 2024.
        """,
        group_name=f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}",
    )
