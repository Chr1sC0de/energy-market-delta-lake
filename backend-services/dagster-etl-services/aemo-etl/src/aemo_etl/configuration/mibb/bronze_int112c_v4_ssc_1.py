"""bronze_int112c_v4_ssc_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int112c_v4_ssc_1",
        s3_file_glob="int112c_v4_ssc_1*",
        primary_keys=["supply_source", "gas_date", "ti"],
        table_schema={
            "supply_source": String,
            "gas_date": String,
            "ssc_id": Int64,
            "ti": Int64,
            "hourly_constraint": Int64,
            "mod_datetime": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "supply_source": "Name of the constrained supply source",
            "gas_date": "Dates that mark the boundary of the application of the constraint (e.g. 27 Jun 2011)",  # noqa: E501
            "ssc_id": "Id of the Constraint",
            "ti": "Time interval 1-24 (hour of the gas day)",
            "hourly_constraint": "1 value for each hour of the gas day, Set to 1 if hourly constraint is applied. 0 if hourly constraint has not been applied",  # noqa: E501
            "mod_datetime": "Creation/modification time stamp (e.g. 07 Jun 2011 08:01:23)",  # noqa: E501
            "current_date": "Date and time the report was produced (e.g. 30 Jun 2011 1:23:56)",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report contains information regarding any supply and demand point constraints (SDPCs) that are current in the\nscheduling processes used in the DTS. These constraints are part of the configuration of the network that can be manually set\nby the AEMO Schedulers and form one of the inputs to the schedule generation process. This report contains supply point\nconstraints, which selectively constrain injection bids at system injection points where the facility operator has registered\nmultiple supply sources.\n\nTraders can use this information to understand the network-based restrictions that will constrain their ability to offer or\nwithdraw gas in the market on a given day. Note these constraints can be applied intraday and reflect conditions from a point in\ntime.\n\nA report is produced each time an operational schedule (OS) is approved by AEMO. Therefore it is expected that each day\nthere will be at least 9 of these reports issued, with any additional ad hoc schedules also triggering this report:\n- 5 being for the standard current gas day schedules\n- 3 being for the standard 1-day ahead schedules\n- 1 being for the standard 2 days ahead schedule\n\nEach report contains details of the SSCs that have applied to schedules previously run:\n- on the previous gas day\n- for the current gas day\n- for the next 2 gas days\n\nEach SSC has a unique identifier and applies to a single injection MIRN.\nEach row in the report contains details of one SSC for one hour of the gas day, with hourly intervals commencing from the start\nof the gas day. That is, the first row for an SSC relates to 06:00 AM.\n\nThis report will contain 24 rows for each SSC for each gas day reported.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
