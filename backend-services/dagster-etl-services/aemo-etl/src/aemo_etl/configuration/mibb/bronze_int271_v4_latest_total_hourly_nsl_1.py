"""bronze_int271_v4_latest_total_hourly_nsl_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int271_v4_latest_total_hourly_nsl_1",
        s3_file_glob="int271_v4_latest_total_hourly_nsl_1*",
        primary_keys=["network_id", "gas_date", "ti"],
        table_schema={
            "network_id": String,
            "nsl_update": String,
            "gas_date": String,
            "ti": Int64,
            "nsl_gj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "network_id": "Network ID of NSL",
            "nsl_update": "Time profile created",
            "gas_date": "Primary key for MIBB report (e.g. 30 Jun 2007)",
            "ti": "Time Interval (1-24)",
            "nsl_gj": "Hourly nsl total for all DB",
            "current_date": "Date and Time report created (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis public report is to provide a 3-year rolling history for network system load (NSL) on an hourly basis for both DTS and non-DTS Networks. \nThis report may be used to review non-daily metered load profiles across each network and to forecast non-daily metered load shape in each distribution network area.\n\nParticipants may wish to use this data as an input into their forecasting systems to assist in predicting the daily profile of their\nnon-daily read customers' meters. It should be noted that the larger the number of non-daily read meters for which a Market\nparticipant is the FRO, the NSL will better approximate the hourly behaviour of the Market participants non-daily read load.\n\nSection 2.8.4 of the Victorian Retail Market Procedures AEMO's obligation to publish the NSL and Attachment 6 of the\nVictorian Retail Market Procedures set out how AEMO calculates the NSL.\n\nA report contains data which is grouped by network identifier which is used to distinguish non-DTS networks from the DTS\nnetwork.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
