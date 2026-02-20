"""bronze_int236_v4_operational_meter_readings_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int236_v4_operational_meter_readings_1",
        s3_file_glob="int236_v4_operational_meter_readings_1*",
        primary_keys=[
            "gas_date",
            "direction_code_name",
            "direction",
            "commencement_datetime",
        ],
        table_schema={
            "gas_date": String,
            "direction_code_name": String,
            "direction": String,
            "commencement_datetime": String,
            "termination_datetime": String,
            "quantity": Float64,
            "time_sort_order": Int64,
            "mod_datetime": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Starting hour of gas day being reported (e.g. 30 Jun 2007)",
            "direction_code_name": "Distribution zone or injection meter",
            "direction": "'Withdrawals' or 'Injections'",
            "commencement_datetime": "Start time/date value applies for",
            "termination_datetime": "End date value applies for (e.g. 30 Jun 2007 06:00:00)",  # noqa: E501
            "quantity": "Metered value. Injection: direct reading. Withdrawals: Summed by Distribution Business Zone in GJ.",  # noqa: E501
            "time_sort_order": "Internal flag",
            "mod_datetime": "Date and time data last modified (e.g. 30 Jun 2007 06:00:00)",  # noqa: E501
            "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report contains the energy by distribution network area data for the previous and the current gas day.\nAs this report is generated on an hourly basis, participants can use this report for adjusting their forecast of system load over\nthe course of the day on a geographical basis. It can be used as an input into Participants bidding decisions leading up to the\nnext schedule.\nDistributors can use this information to monitor energy flows.\nNote this is operational data and is subject to substituted data. Therefore, do not use it to validate settlement outcomes.\n\nThis report is summed by distribution network zones, net of re-injections and transmission customers.\nThis report does not allocate inter-distribution zone energy flows on the infrequent occasions on which they occur. To obtain\ninformation on cross-border flows, users are referred to the specific MIRNs assigned to the cross Distribution Business\nnetwork connections.\n\nEach report contains 24 rows for the previous gas day for:\n- each injection point (for example, Culcairn, Longford, LNG, Iona, VicHub, SEAGas, Bass Gas)\n- each distribution zone\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
