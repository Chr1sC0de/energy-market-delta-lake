"""bronze_int042_v4_weighted_average_daily_prices_1 - Bronze MIBB report configuration."""  # noqa: E501

from polars import Float64, String

from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int042_v4_weighted_average_daily_prices_1",
        s3_file_glob="int042_v4_weighted_average_daily_prices_1*",
        primary_keys=["gas_date"],
        table_schema={
            "gas_date": String,
            "imb_dev_wa_dly_price_gst_ex": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day for the reference prices e.g. 30 Jun 2007",
            "imb_dev_wa_dly_price_gst_ex": """
                Imbalance and deviation weighted average daily price:
                    (∑S,MP |$imb S,MP |+ ∑SI,MP |$dev SI,MP |) /
                        ( ∑S,MP |imb S,MP |+ ∑SI,MP | dev SI,MP |)
                Where:
                    $imb S,MP = $ of imbalance payments for
                        Market participant MP in Schedule S
                    $dev SI,MP = $ of deviation payments for
                        Market participant MP in Schedule Interval SI
                    imb S,MP = GJ of imbalance amount for
                        Market participant MP in Schedule S
                    dev SI,MP = GJ of deviation amount for
                        Market participant MP in Schedule Interval SI
            """,
            "current_date": "Date and Time Report Produced e.g. 29 Jun 2007 01:23:45",
            "surrogate_key": """
                Unique identifier created using sha256 over the primary keys
            """,
        },
        report_purpose="""
            This report is available to Participants for use in settlement for
            off-market hedge contracts. Potentially it is also useable as benchmark
            price of gas in contract negotiations. Traders may wish to user the report
            to get a daily perspective of the value of
            gas in a day.

            This report can be read in conjunction with INT041 which relates to the
            actual market ex ante prices and the calculated "reference prices".

            This report provides a weighted average daily price based on the total
            imbalance and deviation payments.

            The report provides another perspective of the market pricing of gas. Again
            these average prices are only for information and analysis purposes and are
            not used in the actual settlement of the gas day.

            Each report contains the:
            - gas date
            - weighted average daily price for imbalance and deviation (GST exclusive)
            - date and time when the report was produced

            The report should contain one row representing each gas day in a month.
            Therefore in a month consisting of 30 days, the user can expect to see 30
            rows of data.
        """,
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
