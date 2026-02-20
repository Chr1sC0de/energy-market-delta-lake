"""bronze_int128_v4_actual_linepack_1 - Bronze MIBB report configuration."""

from polars import Float64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int128_v4_actual_linepack_1",
        s3_file_glob="int128_v4_actual_linepack_1*",
        primary_keys=["commencement_datetime"],
        table_schema={
            "commencement_datetime": String,
            "actual_linepack": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "commencement_datetime": "Commencement date and time (e.g. 25 Apr 2007 1:00:00)",  # noqa: E501
            "actual_linepack": "Energy value representing the physical linepack",
            "current_date": "Date and time report produced (e.g. 30 Jun 2007 01:23:56)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides information on changes in physical linepack over a 3-day period, and can be used by Participants as an\ninput into their forecasting and trading activities.\n\nNote the information in this report is derived from real-time gas pressure data and does not relate to the scheduled linepack\nvalues, as the scheduled linepack is a relative value.\n\nIt is also important to recognise that this report contains details about the system's physical linepack and is not the settlement\nlinepack, which is a financial balancing concept not related in any way to the physical linepack in the system on each day.\n\nParticipants may use this report to make assumptions about the physical capabilities of the system when correlated with\nweather, type of day and other variables that impact on demand.\n\nEach report provides hourly linepack quantities for the current and previous 2 gas days.\n\nReports are produced as operational schedules are approved, with information about the linepack movements for the current\ngas day becoming progressively more complete in the course of the day. It follows, therefore, that the number of rows in an\nINT128 report will increase over the course of the day.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
