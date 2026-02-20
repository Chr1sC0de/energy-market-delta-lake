"""bronze_int310_v1_price_and_withdrawals_rpt_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int310_v1_price_and_withdrawals_rpt_1",
        s3_file_glob="int310_v1_price_and_withdrawals_rpt_1*",
        primary_keys=["gas_date", "gas_hour"],
        table_schema={
            "gas_date": String,
            "gas_hour": Int64,
            "transmission_id": Int64,
            "ctm_d1_inj": Float64,
            "ctm_d1_wdl": Float64,
            "price_value": Float64,
            "administered_price": Float64,
            "total_gas_withdrawals": Float64,
            "total_gas_injections": Float64,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day being reported e.g. 30 Jun 2007",
            "gas_hour": "Schedule interval (1-5) where 1 refers to 6:00 AM to 10:00 AM, 2 relates to 10:00 AM to 2:00 PM, etc.",  # noqa: E501
            "transmission_id": "Schedule ID",
            "ctm_d1_inj": "Last approved scheduled injections in gigajoules",
            "ctm_d1_wdl": "Last approved scheduled withdrawals including controllable withdrawals in gigajoules",  # noqa: E501
            "price_value": "Price value",
            "administered_price": "Administered Price (null when no admin prices applies, otherwise shows the admin price while price_value shows the last approved schedule price)",  # noqa: E501
            "total_gas_withdrawals": "Actual metered withdrawals in gigajoules",
            "total_gas_injections": "Actual metered injections in gigajoules",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report is to show the overall statistics for gas days for the last 12 months. Participants may wish to use this report as a market\nanalysis tool for forecasting purposes, and general information for management within their respective organisations.\n\nA report is produced daily covering the previous rolling 12-month period.\n\nThe report provides information about scheduled gas injections and withdrawals and actual system performance for the previous 12\nmonths.\n\nEach report contains:\n- the gas date\n- schedule interval (indicating 1 to 5 when the deviation occurred, where 1 refers to 6:00 AM to 10:00 AM, 2 will relate to 10:00\nAM to 2:00 PM, and so forth)\n- transmission identifier for the schedule\n- scheduled injections in gigajoules\n- scheduled withdrawals in gigajoules\n- price for the scheduling horizons\n- Administered Price (the value in the admin price field is null when no admin prices applies and when there has been an\nadmin price, it will be displayed and the price_value will show the last approved schedule price.)\n- Actual metered withdrawals in gigajoules\n- Actual metered injections in gigajoules\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
