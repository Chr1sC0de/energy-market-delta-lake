"""bronze_int112_v4_dfpc_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int112_v4_dfpc_1",
        s3_file_glob="int112_v4_dfpc_1*",
        primary_keys=["dfpc_id", "ti"],
        table_schema={
            "dfpc_id": Int64,
            "injection_mirn": String,
            "withdrawal_mirn": String,
            "commencement_date": String,
            "termination_date": String,
            "daily_max_net_inj_qty_gj": Int64,
            "daily_max_net_wdl_qty_gj": Int64,
            "ti": Int64,
            "hourly_max_net_inj_qty_gj": Int64,
            "hourly_max_net_wdl_qty_gj": Int64,
            "mod_datetime": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "dfpc_id": "Id of the Constraint",
            "injection_mirn": "Injection mirn",
            "withdrawal_mirn": "Withdrawal mirn paired to injection mirn",
            "commencement_date": "Dates that mark the boundary of the application of the constraint (e.g. 27 Jun 2006)",  # noqa: E501
            "termination_date": "Dates that mark the boundary of the application of the constraint (e.g. 27 Jun 2006)",  # noqa: E501
            "daily_max_net_inj_qty_gj": "Daily maximum net injection quantity in GJ",
            "daily_max_net_wdl_qty_gj": "Daily maximum net withdrawal quantity in GJ",
            "ti": "Time interval 1-24 (hour of the gas day)",
            "hourly_max_net_inj_qty_gj": "1 value for each hour of the gas day",
            "hourly_max_net_wdl_qty_gj": "1 value for each hour of the gas day",
            "mod_datetime": "DFPC creation/modification time stamp (e.g. 07 Jun 2006 08:01:23)",  # noqa: E501
            "current_date": "Date and time the report was produced (e.g. 30 Jun 2005 1:23:56)",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report contains information on the directional flow point constraints (DFPCs) pertaining to the DTS. Directional flow points\nare those points in the DTS where both injections and withdrawals can occur, and the key item of interest is the NET\nmovement of gas.\n\nDFPCs are part of the configuration of the network that can be manually changed by the AEMO Schedulers, and form one of\nthe inputs to the schedule generation process.\n\nTraders can use this information to understand the network-based restrictions that will constrain their ability to offer gas to the\nmarket on a given day in the reporting window.\n\nA report is produced each time an operational schedule (OS) is approved by AEMO. Therefore, it is expected that each day\nthere will be at least 9 of these reports issued:\n- 5 being for the standard current gas day schedules\n- 3 being for the standard 1-day ahead schedules\n- 1 being for the standard 2 days ahead schedule\n\nEach report contains details of the DFPCs that have applied and will apply to schedules run:\n- on the previous gas day\n- for the current gas day and\n- for the next 2 gas days\n\nEach DFPC has a unique identifier and applies to a single pair of MIRNs (an injection MIRN and a withdrawal MIRN).\nEach row in the report contains details of one DFPC for one hour of the gas day, with hourly intervals commencing from the\nstart of the gas day. That is, the first row for a DFPC relates to 06:00 AM.\n\nThis report will contain 24 rows for each DFPC for each gas day reported.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
