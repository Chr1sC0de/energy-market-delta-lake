"""bronze_gasbb_gsh_gas_trades - Bronze GASBB report configuration."""

from polars import Float64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_gsh_gas_trades",
        s3_file_glob="gasbbgshgastrades*",
        primary_keys=[
            "TRADE_DATE",
            "TYPE",
            "PRODUCT",
            "LOCATION",
            "START_DATE",
            "END_DATE",
            "MANUAL_TRADE",
        ],
        table_schema={
            "TRADE_DATE": String,
            "TYPE": String,
            "PRODUCT": String,
            "LOCATION": String,
            "TRADE_PRICE": Float64,
            "DAILY_QTY_GJ": Float64,
            "START_DATE": String,
            "END_DATE": String,
            "MANUAL_TRADE": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "TRADE_DATE": "Date of the trade",
            "TYPE": "Trade Type",
            "PRODUCT": "Trade Product",
            "LOCATION": "Location",
            "TRADE_PRICE": "Price",
            "DAILY_QTY_GJ": "Quantity",
            "START_DATE": "Start Date",
            "END_DATE": "End Date",
            "MANUAL_TRADE": "Manual Trade?",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThe file below provides a complete list of historical trades.\nThis data can be used to analyse market trends over time.\nIf you are after a more simple and straightforward representation of price trends in the GSH,\nthe benchmark price report (outlined below) may be more appropriate.\n",  # noqa: E501
    )
