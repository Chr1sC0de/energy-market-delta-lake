"""bronze_int381_v4_tie_breaking_event_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int381_v4_tie_breaking_event_1",
        s3_file_glob="int381_v4_tie_breaking_event_1*",
        primary_keys=["gas_date", "schedule_interval", "transmission_id", "mirn"],
        table_schema={
            "gas_date": String,
            "schedule_interval": Int64,
            "transmission_id": Int64,
            "mirn": String,
            "tie_breaking_event": Int64,
            "cc_bids": Int64,
            "non_cc_bids": Int64,
            "part_cc_bids": Int64,
            "gas_not_scheduled": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "The date of gas day being reported (for example, 30 Jun 2012)",
            "schedule_interval": "(1,2,3,4 or 5)",
            "transmission_id": "Schedule ID from which results were drawn",
            "mirn": "Meter Registration Identification Number of the system point",
            "tie_breaking_event": "Total tie-breaking event",
            "cc_bids": "If the tie-breaking bids have CC allocated to them, list number of bids with CC allocated to them",
            "non_cc_bids": "If the tie-breaking bids do not have CC allocated to them, list number of bids with no CC allocated to them",
            "part_cc_bids": "If the tie-breaking bids have part CC allocated to them, list number of bids with part CC allocated to them",
            "gas_not_scheduled": "Aggregate tie breaking bids - aggregate tie breaking bids scheduled",
            "current_date": "Date and time report produced (for example, 30 Jun 2012 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report provides information about tie-breaking events that occurred on each gas D on the following gas day D+1.\n\nThis report details the tie-breaking events from the previous gas day for the 5 intraday scheduling intervals.\nThis report does not take into account MPs submitting bids that are inconsistent with their accreditations constraint. In an\nevent MPs bids exceed their accreditation, a tie breaking event may be incorrectly reported.\n\nEach row in the report provides details for each mirn the tie-breaking events for the previous gas days 5 intraday schedules.\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
