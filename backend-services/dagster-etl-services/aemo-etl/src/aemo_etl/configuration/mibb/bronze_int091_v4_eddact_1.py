"""bronze_int091_v4_eddact_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_GAS_RETAIL_REPORTS_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int091_v4_eddact_1",
        s3_file_glob="int091_v4_eddact_1*",
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
            "edd_update": "Date and time value derived e.g. 27 Sep 2007 14:31:00",
            "edd_date": "Actual EDD date (event date) (e.g. 30 Jun 2007)",
            "edd_value": "EDD value",
            "edd_type": "=1 Billing EDD, used in BMP for generating consumed energy values and remains based on the 9-9 time period, even though the gas day is 6-6",  # noqa: E501
            "current_date": "Time Report Produced (e.g. 30 Jun 2007 06:00:00) Time Report Produced e.g. 29 Jun 2007 01:23:45",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the Effective Degree Day (EDD) as calculated for a gas day in AEMO's settlements processing. This\nsettlements EDD value is used in the generation of energy values used by AEMO to settle the wholesale market.\n\nGas distributors and retailers use the information in this report to derive an average EDD figure for use in their own routines to\nestimate end-use customers' consumption where no actual read is available for a basic meter. The Victorian Retail Market\nProcedures prescribes AEMO requirement to publish the EDD (see section 2.8.2), how AEMO calculates the EDD (see\nattachment 6 section 3) and the use of this EDD value when generating an estimated meter reading (see attachment 4).\n\nThe reported EDD is an actual EDD (i.e. Based on actual weather observations rather than weather forecasts) and is\ncalculated for a 9-9 time period rather than a 6-6 gas day. It should also be noted that the published EDD value is not normally\nsubject to revision.\n\nThis report is generated daily. Each report provides a historical record of actual EDD for a rolling 2 calendar month period\nending on the day before the report date.\n\nEach row in the report provides the billing EDD for the specified edd_date.\n\nSince actual EDD is calculated on actual weather observations, the latest possible EDD available is for the previous full day.\nThis means that actual EDD is always published (at least) 1 day in arrears.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}",
    )
