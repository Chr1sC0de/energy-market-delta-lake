"""bronze_int079_v4_total_gas_withdrawn_1 - Bronze MIBB report configuration."""

from polars import Float64, String
from aemo_etl.configuration import (
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int079_v4_total_gas_withdrawn_1",
        s3_file_glob="int079_v4_total_gas_withdrawn_1*",
        primary_keys=["gas_date"],
        table_schema={
            "gas_date": String,
            "unit_id": String,
            "qty": Float64,
            "qty_reinj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day being reported e.g. 30 Jun 2007",
            "unit_id": "Unit of measurement (GJ)",
            "qty": "Total Gas withdrawn Daily",
            "qty_reinj": "Total Net Gas withdrawn Daily (Withdrawals less re-injections)",  # noqa: E501
            "current_date": "Date and time report produced e.g. 30 Jun 2007 01:23:45",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose='\n\nThis report provides a view of the total quantity of gas that is flowing in the DTS on a given day. Retailers may use this\ninformation as an input to their demand forecasts or to estimate their market share. Participants must be aware that the data is\nof operational quality and not settlement quality, and is therefore subject to revision. The data revisions can be significant and\nis dependent on a number of factors, including, but not limited to, the availability of telemetered data and system availability.\n\nThe report contains metering data for the prior gas day. The data is of operational quality and is subject to substitution and\nreplacement.\n\nIn the context of this report, re-injections represent the flow to the transmission pipeline system (TPS) from the distribution\npipeline system (DPS) at times of low pressure and low demand. The first quantity reported, "qty", includes re-injections.\n\nIt should be noted that for a single day, multiple entries can exist. Initial uploads of data for a given date can be incomplete\nwhen it is first reported and updates arriving later into AEMO\'s system will cause multiple entries to exist, Participants should\ncombine the reports to provide a daily total.\n\nEach report contains details of the withdrawals that occurred on the previous seven gas days. That is, the INT079 report for\nthe gas date of 11-August will contain withdrawal quantities for the dates 4 to 10 August inclusive.\n\nThe data in this report can have a significant number of substituted values and it is possible for the data to change from day to\nday as they are updated through the 7-day reporting window.\n',  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
