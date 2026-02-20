"""bronze_int235_v4_sched_system_total_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int235_v4_sched_system_total_1",
        s3_file_glob="int235_v4_sched_system_total_1*",
        primary_keys=[
            "transmission_id",
            "gas_date",
            "day_in_advance",
            "data_type",
            "detail",
            "id",
        ],
        table_schema={
            "transmission_id": Int64,
            "gas_date": String,
            "flag": String,
            "day_in_advance": String,
            "data_type": String,
            "detail": String,
            "transmission_doc_id": Int64,
            "id": String,
            "value": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "transmission_id": "Schedule Id, (0 for Administered price) - Unique identifier associated with each schedule",  # noqa: E501
            "gas_date": "Gas day of schedule (e.g. 30 Jun 2007)",
            "flag": "Schedule_Type – OS, MS, (Administered Pricing)",
            "day_in_advance": "D-2, D-1, D-0",
            "data_type": "CTLD WDLS (Scheduled quantities), UNCTLD WDLS (Scheduled quantities), LINEPACK, INJECTIONS (Scheduled quantities), COMP FUEL USAGE, MKT PRICE HORIZON 1 GST EX, MKT PRICE HORIZON 2 GST EX, MKT PRICE HORIZON 3 GST EX, MKT PRICE HORIZON 4 GST EX, MKT PRICE HORIZON 5 GST EX",  # noqa: E501
            "detail": "DAILY, EOD, MCE BOD, 10% EXCEEDANCE, NORMAL, 90% EXCEEDANCE, ADMINISTERED, ACTUAL PRICE",  # noqa: E501
            "transmission_doc_id": "Run Id, (0 for Administered price)",
            "id": "MIRN (e.g. 30000001PC), Withdrawal Zone (e.g. Ballarat), ALL COMPRESSORS, SYSTEM",  # noqa: E501
            "value": "Quantity or Price",
            "current_date": "Date/Time report produced (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides transparency into the operation of the wholesale gas market as required in clause 320 of the NGR. It is\nintended to provide users with a public summary 'snapshot' of the market and of all schedules and prices.\n\nINT235 brings together many varied pieces of information.\nUsers should refer to INT108 (Schedule Run Log) to determine the specific characteristics of each schedule (for example, the\nschedule start date and time, publish time and so on) associated with a specific transmission id or transmission document id\n(which is also known as schedule id).\nWhere prices have been administered, no schedule id will exist in these cases. Therefore 0 is used as transmission id.\n\nAn INT235 report is triggered each time a schedule is approved. It contains details for both operational and market schedules.\nThe reporting window for INT235 includes:\n- the gas day date on which the report is being run (the 'current date')\n- 2 days prior to the current date\n- 2 days after the current date.\n\nFor each day in its reporting window, wherever possible INT235 will provide details of the:\n- last approved 2-day ahead operational schedule for the specified gas date\n- last approved 2-day ahead pricing schedule for the specified gas date\n- last approved 1-day ahead operational schedule for the specified gas date\n- last approved 1-day ahead pricing schedule for the specified gas date\n- first approved current gas day operational schedule for the specified gas date\n- first approved current gas day pricing schedule for the specified gas date.\n- last approved current gas day operational schedule for the specified gas date\n- last approved current gas day pricing schedule for the specified gas date.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
