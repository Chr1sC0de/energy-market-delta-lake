"""bronze_int199_v4_cumulative_price_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int199_v4_cumulative_price_1",
        s3_file_glob="int199_v4_cumulative_price_1*",
        primary_keys=["gas_date", "schedule_interval"],
        table_schema={
            "transmission_id": Int64,
            "gas_date": String,
            "schedule_interval": Int64,
            "cumulative_price": Float64,
            "cpt_exceeded_flag": String,
            "schedule_type_id": String,
            "transmission_doc_id": Int64,
            "approval_datetime": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "transmission_id": "Schedule Id - Unique identifier associated with each schedule",  # noqa: E501
            "gas_date": "Gas day of schedule. format dd mmm yyy e.g. 30 Jun 2008",
            "schedule_interval": "Integer identifier of schedule of the gas day: 1=schedule with start time 6:00 AM, 2=schedule with start time 10:00 AM, 3=schedule with start time 2:00 PM, 4=schedule with start time 6:00 PM, 5=schedule with start time 10:00 PM",  # noqa: E501
            "cumulative_price": "Rolling cumulative price from MCP's from previous Y-1 LAOS and next FAOS",  # noqa: E501
            "cpt_exceeded_flag": "'Y' when CP ≥ CPT, otherwise 'N'",
            "schedule_type_id": "OS (Operating Schedule Id)",
            "transmission_doc_id": "Run Id",
            "approval_datetime": "Date and time the schedule was approved 29 Jun 2007 01:23:45",  # noqa: E501
            "current_date": "Current report run date time. Format dd Mmm yyyy hh:mi:ss e.g. 15 May 2008 12:22:12",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nInterface 199 (INT199) is an Event-Triggered report published on the Market Information Bulletin Board (MIBB). This report\nmust provide by scheduling interval by gas day the cumulative price (CP) and a flag to indicate when CP is greater than or\nequal to the threshold (CPT). The report is produced on approval of a current gas day operating/pricing schedules with start\ntime equal to the commencement of each scheduling interval. Ad hoc operating reschedules during a scheduling interval are\nincluded in the determination of MCP's for previous scheduling intervals, but do not themselves trigger the report.\n\nWhilst bid information is public and this can be estimated by the public, actual scheduling information by bid is still regarded as\nconfidential by Market participants.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
