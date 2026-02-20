"""bronze_int089_v4_linepack_balance_1 - Bronze MIBB report configuration."""

from polars import Float64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int089_v4_linepack_balance_1",
        s3_file_glob="int089_v4_linepack_balance_1*",
        primary_keys=["gas_date"],
        table_schema={
            "gas_date": String,
            "total_imb_pmt": Float64,
            "total_dev_pmt": Float64,
            "linepack_acct_pmt_gst_ex": Float64,
            "linepack_acct_bal_gst_ex": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day being reported e.g. 30 Jun 2007 06:00:00",
            "total_imb_pmt": "Sum of imbalance payments for the gas day (across all scheduling intervals) credit or debit amount ($)",  # noqa: E501
            "total_dev_pmt": "Sum of deviation payments for the gas day (across all scheduling intervals credit or debit amount ($)",  # noqa: E501
            "linepack_acct_pmt_gst_ex": "Credit or debit amount ($) to AEMO's linepack account = total_imbal_pmts + total_dev_pmts",  # noqa: E501
            "linepack_acct_bal_gst_ex": "Sum (linepack_acct_pmts for month) progressive total, accumulating from beginning of month to the end of the month",  # noqa: E501
            "current_date": "Date and Time Report Produced e.g. 29 Jun 2007 01:23:45",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis month-to-date report is to provide an ongoing perspective of the total markets liability to linepack account payments or\nreceipts. The amount reported is accumulated during the month and then paid out (in credit or debit) based on the participant\nconsumption during the month.\n\nThis amount effectively cashes out inter day movements in system linepack and smears the impact of unallocated gas in the\nmarket (due to things like measurement error).\n\nThis account balance is based on provisional meter data and is subject to change at settlement time.\n\nA report is produced daily after 3 business days of the actual gas date.\n\nThe report is used as part of the pre-processing step for settlements whereby participants may wish to use this report as an\nindication against liability of their linepack account.\n\nEach report contains a row for each gas day which shows the:\n- total imbalance payment\n- total deviation payment\n- linepack account payment\n- linepack account balance\n- date and time when the report was produced\n\nThe amounts showed will then be taken into account each month and used as part of settlements where based on\nconsumption, the participant will then receive a statement in debit or credit.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
