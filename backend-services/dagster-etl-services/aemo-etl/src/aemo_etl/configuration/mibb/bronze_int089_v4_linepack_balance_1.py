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
            "total_imb_pmt": """
                Sum of imbalance payments for the gas day (across all scheduling
                intervals) credit or debit amount ($)
            """,
            "total_dev_pmt": """
                Sum of deviation payments for the gas day (across all scheduling
                intervals credit or debit amount ($)
            """,
            "linepack_acct_pmt_gst_ex": """
                Credit or debit amount ($) to AEMO's linepack account = total_imbal_pmts
                + total_dev_pmts
            """,
            "linepack_acct_bal_gst_ex": """
                Sum (linepack_acct_pmts for month) progressive total, accumulating from
                beginning of month to the end of the month
            """,
            "current_date": "Date and Time Report Produced e.g. 29 Jun 2007 01:23:45",
            "surrogate_key": """
                Unique identifier created using sha256 over the primary keys
            """,
        },
        report_purpose="""
            This month-to-date report is to provide an ongoing perspective of the total
            markets liability to linepack account payments or receipts. The amount
            reported is accumulated during the month and then paid out (in credit or
            debit) based on the participant consumption during the month.

            This amount effectively cashes out inter day movements in system linepack
            and smears the impact of unallocated gas in the market (due to things like
            measurement error).

            This account balance is based on provisional meter data and is subject to
            change at settlement time.

            A report is produced daily after 3 business days of the actual gas date.

            The report is used as part of the pre-processing step for settlements
            whereby participants may wish to use this report as an indication against
            liability of their linepack account.

            Each report contains a row for each gas day which shows the: - total
            imbalance payment - total deviation payment - linepack account payment -
            linepack account balance - date and time when the report was produced

            The amounts showed will then be taken into account each month and used as
            part of settlements where based on consumption, the participant will then
            receive a statement in debit or credit.
        """,
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
