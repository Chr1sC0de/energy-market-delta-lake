"""bronze_int037b_v4_indicative_mkt_price_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration import (
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int037b_v4_indicative_mkt_price_1",
        s3_file_glob="int037b_v4_indicative_mkt_price_1*",
        primary_keys=["demand_type_name", "transmission_id"],
        table_schema={
            "demand_type_name": String,
            "price_value_gst_ex": Float64,
            "transmission_group_id": Int64,
            "schedule_type_id": String,
            "transmission_id": Int64,
            "gas_date": String,
            "approval_datetime": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "demand_type_name": (
                "Normal Uses Demand forecast used by operational schedule. "
                "10% exceedence means the estimated market price is based on "
                "10% exceedance of the forecast demand level. "
                "90% exceedence means the estimated market price if the demand "
                "is 90% of the forecast demand."
            ),
            "price_value_gst_ex": "Forecast market price ($) for BoD Scheduling horizon of the gas day in question",  # noqa: E501
            "transmission_group_id": "Link to the related day(s) ahead operational schedule",  # noqa: E501
            "schedule_type_id": "MS (Market Schedule Id)",
            "transmission_id": "Schedule number these prices are related to",
            "gas_date": "e.g. 30 Jun 2007",
            "approval_datetime": "Date and time the schedule was approved 29 Jun 2007 01:23:45",  # noqa: E501
            "current_date": "Date and time Report Produced e.g. 29 Jun 2007 01:23:45",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="""

This report indicates prices for the day and predictions for the next two days.

Market participants may use this to estimate pricing for the following two days.
""",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
