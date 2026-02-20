"""bronze_int571_v4_latest_nsl_1 - Bronze MIBB report configuration."""

from polars import Float64, String

from aemo_etl.configuration import QUEENSLAND_GAS_RETAIL_REPORT_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int571_v4_latest_nsl_1",
        s3_file_glob="int571_v4_latest_nsl_1*",
        primary_keys=["network_name", "gas_date", "distributor_name"],
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
            "network_name": "Network name",
            "gas_date": "Gas date being reported",
            "distributor_name": "Distribution region",
            "nsl_gj": "Daily nsl energy for a DB",
            "current_date": "Date and Time report created (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report is to list the Net System Load (NSL) for each distribution area for a rolling 3 year period. This report may be used to\nvalidate consumed energy produced in INT569.\n\nAttachment 4 of the Queensland Retail Market Procedures describes the NSL in further detail.\n\nThis public report is updated daily and reflects data which is one business day after the gas date (Day + 1).\nThe NSL is defined as the total injection into a distribution business network minus the daily metered load (ie all the interval\nmetered sites). It therefore represents the total consumption profile of all the non-daily read meters (basic meters).\n\nThis report is similar to VIC MIBB report INT471.\n\nEach report contains the:\n- date and time when the NSL profile was updated\n- network name\n- gas date\n- distributor name\n- daily NSL energy in gigajoules for a distribution business\n- date and time the report was produced\n",  # noqa: E501
        group_name=f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}",
    )
