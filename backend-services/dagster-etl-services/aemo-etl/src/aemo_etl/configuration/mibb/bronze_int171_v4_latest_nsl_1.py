"""bronze_int171_v4_latest_nsl_1 - Bronze MIBB report configuration."""

from polars import Float64, String
from aemo_etl.configuration import VICTORIAN_GAS_RETAIL_REPORTS_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int171_v4_latest_nsl_1",
        s3_file_glob="int171_v4_latest_nsl_1*",
        primary_keys=["nsl_update", "gas_date", "distributor_name"],
        table_schema={
            "nsl_update": String,
            "gas_date": String,
            "distributor_name": String,
            "nsl_gj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "nsl_update": "Time profile created",
            "gas_date": "Primary key for MIBB report (e.g. 30 Jun 2007)",
            "distributor_name": "Primary Key for MIBB report",
            "nsl_gj": "Daily nsl energy for a DB",
            "current_date": "Time report created (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report is to list the Net System Load (NSL) for each distribution area for a rolling 3 year period. This report may be used to\nvalidate consumed energy produced in INT169. Section 2.8.4 of the Victorian Retail Market Procedures AEMO's obligation to\npublish the NSL and Attachment 6 of the Victorian Retail Market Procedures set out how AEMO calculates the NSL.\n\nThis public report is updated daily and reflects data which is one business day after the gas date (Day + 1).\nThis report only applies to the DTS network.\n\nThe NSL is defined as the total injection into a distribution business network minus the daily metered load (i.e. all the interval\nmetered sites). It therefore represents the consumption profile of all the non-daily read meters (basic meters).\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}",
    )
