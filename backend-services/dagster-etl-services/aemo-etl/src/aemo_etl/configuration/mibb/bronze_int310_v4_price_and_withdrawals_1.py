"""bronze_int310_v4_price_and_withdrawals_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int310_v4_price_and_withdrawals_1",
        s3_file_glob="int310_v4_price_and_withdrawals_1*",
        primary_keys=["gas_date", "schedule_interval"],
        table_schema={
            "gas_date": String,
            "schedule_interval": Int64,
            "transmission_id": Int64,
            "sched_inj_gj": Float64,
            "sched_wdl_gj": Float64,
            "price_value": Float64,
            "administered_price": Float64,
            "actual_wdl_gj": Float64,
            "actual_inj_gj": Float64,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "dd mmm yyyy",
            "schedule_interval": "(1,2,3,4 or 5)",
            "transmission_id": "Schedule ID",
            "sched_inj_gj": "Last approved scheduled injections",
            "sched_wdl_gj": "Last approved scheduled withdrawals including controllable withdrawals",  # noqa: E501
            "price_value": "Price value",
            "administered_price": "Administered Price",
            "actual_wdl_gj": "Actual metered withdrawals",
            "actual_inj_gj": "Actual metered injections",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report is to show the overall statistics for gas days for the last 12 months. Participants may wish to use this report as a\nmarket analysis tool for forecasting purposes, and general information for management within their respective organisations.\n\nA report is produced daily covering the previous rolling 12-month period.\nThe report provides information about scheduled gas injections and withdrawals and actual system performance for the\nprevious 12 months.\n\nEach report contains the:\n- gas date\n- schedule interval (indicating 1 to 5 when the deviation occurred, where 1 refers to 6:00 AM to 10:00 AM, 2 will relate to\n10:00 AM to 2:00 PM, and so forth)\n- transmission identifier for the schedule\n- scheduled injections in gigajoules\n- scheduled withdrawals in gigajoules\n- price for the scheduling horizons\n- Administered Price (the value in the admin price field is null when no admin prices applies and when there has been an\nadmin price, it will be displayed and the price_value will show the last approved schedule price)\n- Actual metered withdrawals in gigajoules\n- Actual metered injections in gigajoules\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
