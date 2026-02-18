"""bronze_int263_v4_lng_monitor_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int263_v4_lng_monitor_1",
        s3_file_glob="int263_v4_lng_monitor_1*",
        primary_keys=["gas_date"],
        table_schema={
            "gas_date": String,
            "allocated_market_stock": Int64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas Date data generated e.g. 02 Feb 2001",
            "allocated_market_stock": "Sum of Allocated Market LNG Stock Holding (tonnes) Sum of participant and AEMO Allocated stock holding excluding participant ID 14 GasNet.",
            "current_date": "Date and Time report produced e.g. 29 Jun 2007 01:23:45",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report is one of a number of reports produced to provide market information about the daily total LNG reserves held by\nAEMO and all Market participants.\n\nThis public report displays the sum of LNG reserves (in tonnes) held for each day for the past 60 days.\n\nEach report contains daily data for the last 60 days.\nThe LNG stock reported excludes the status of BOC operations on AEMO's stock holding.\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
