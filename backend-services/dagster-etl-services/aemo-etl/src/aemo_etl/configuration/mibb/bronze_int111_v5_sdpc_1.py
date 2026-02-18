"""bronze_int111_v5_sdpc_1 - Bronze MIBB report configuration."""

from polars import Int64, String
from aemo_etl.configuration import (
    VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS,
)
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int111_v5_sdpc_1",
        s3_file_glob="int111_v5_sdpc_1*",
        primary_keys=[
            "gas_date",
            "ti",
            "mirn",
            "schedule_response_time",
            "expiration_time",
            "sdpc_id",
            "current_date",
        ],
        table_schema={
            "gas_date": String,
            "ti": Int64,
            "mirn": String,
            "ps_hourly_max_qty": Int64,
            "ps_hourly_min_qty": Int64,
            "os_hourly_max_qty": Int64,
            "os_hourly_min_qty": Int64,
            "ramp_up_constraint": Int64,
            "ramp_down_constraint": Int64,
            "schedule_response_time": String,
            "ps_daily_min_qty": Int64,
            "ps_daily_max_qty": Int64,
            "os_daily_min_qty": Int64,
            "os_daily_max_qty": Int64,
            "expiration_time": String,
            "sdpc_id": Int64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas date (e.g. 24 Nov 2007)",
            "ti": "Trading interval (1-24)",
            "mirn": "Meter Installation Registration Number",
            "ps_hourly_max_qty": "Pricing schedule hourly maximum quantity",
            "ps_hourly_min_qty": "Pricing schedule hourly minimum quantity",
            "os_hourly_max_qty": "Operating schedule hourly maximum quantity",
            "os_hourly_min_qty": "Operating schedule hourly minimum quantity",
            "ramp_up_constraint": "Ramp up constraint",
            "ramp_down_constraint": "Ramp down constraint",
            "schedule_response_time": "Schedule response time (e.g. 30 Jun 2007 06:00:00)",
            "ps_daily_min_qty": "Pricing schedule daily minimum quantity",
            "ps_daily_max_qty": "Pricing schedule daily maximum quantity",
            "os_daily_min_qty": "Operating schedule daily minimum quantity",
            "os_daily_max_qty": "Operating schedule daily maximum quantity",
            "expiration_time": "Expiration time (e.g. 06:00:00)",
            "sdpc_id": "ID of the Constraint",
            "current_date": "Date and Time Report Produced (e.g. 30 June 2005 1:23:56)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report contains information regarding any supply and demand point constraints (SDPCs) that are current in the\nscheduling processes used in the DTS. These constraints are part of the configuration of the network that can be manually set\nby the AEMO Schedulers and form one of the inputs to the schedule generation process.\n\nTraders can use this information to understand the network-based restrictions that will constrain their ability to offer or\nwithdraw gas in the market on a given day. Note these constraints can be applied intraday and reflect conditions from a point in\ntime.\n\nA report is produced each time an operational schedule (OS) or pricing schedule (PS) is approved by AEMO. Therefore, it is\nexpected that each day there will be at least 9 of these reports issued, with any additional ad hoc schedules also triggering this\nreport:\n- 5 being for the standard current gas day schedules\n- 3 being for the standard 1-day ahead schedules\n- 1 being for the standard 2 days ahead schedule\n\nEach report contains details of the SDPCs that have applied to schedules previously run:\n- on the previous gas day\n- for the current gas day and\n- for the next 2 gas days\n\nEach SDPC has a unique identifier and applies to a single MIRN (both injection and withdrawal points).\nEach row in the report contains details of one SDPC for one hour of the gas day, with hourly intervals commencing from the\nstart of the gas day. That is, the first row for an SDPC relates to 06:00 AM.\n\nThis report will contain 24 rows for each SDPC for each gas day reported.\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
