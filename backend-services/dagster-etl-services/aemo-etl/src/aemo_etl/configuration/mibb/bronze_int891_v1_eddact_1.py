"""bronze_int891_v1_eddact_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration import SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int891_v1_eddact_1",
        s3_file_glob="int891_v1_eddact_1*",
        primary_keys=["edd_update", "edd_date"],
        table_schema={
            "edd_update": String,
            "edd_date": String,
            "edd_value": Float64,
            "edd_type": Int64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "edd_update": "Date and time value derived e.g. 27 Sep 2007 14:33:00",
            "edd_date": "Actual EDD date (event date) (e.g. 30 Jun 2007)",
            "edd_value": "EDD value",
            "edd_type": "=3 for NSW/ACT EDD",
            "current_date": "Time Report Produced (e.g. 30 Apr 2015 18:00:03)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the separate Effective Degree Day (EDD) values for NSW and ACT as\ncalculated for a gas day.\n\nGas distributors and retailers use the information in this report to derive an average EDD\nfigure for use in their own routines to estimate end-use customers' consumption where no\nactual read is available for a basic meter. The NSW/ACT Retail Market Procedures prescribes\nAEMO requirement to publish the EDD, how AEMO calculates the EDD (refer Attachment 2)\nand the use of this EDD value when generating an estimated meter reading (see Attachment 2\nand 3).\n\nThe reported EDD is an actual EDD (i.e. Based on actual weather observations rather than\nweather forecasts) and is calculated for a time period as specified under Attachment 2 of the\nNSW/ACT RMP. It should also be noted that the published EDD value is not normally subject\nto revision.\n\nThis report is generated daily. Each report provides a historical record of actual EDD for a\nrolling 60 day period ending on the day before the report date.\n\nEach row in the report provides the EDD for the specified edd_date.\n\nSince actual EDD is calculated on actual weather observations, the latest possible EDD\navailable is for the previous full day. This means that actual EDD is always published (at least)\n1 day in arrears.\n",  # noqa: E501
        group_name=f"aemo__mibb__{SOUTH_AUSTRALIAN_GAS_RETAIL_REPORTS}",
    )
