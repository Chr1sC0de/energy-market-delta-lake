"""bronze_int131_v4_bids_at_bid_cutoff_times_prev_2_1 - Bronze MIBB report configuration."""  # noqa: E501

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
        table_name="bronze_int131_v4_bids_at_bid_cutoff_times_prev_2_1",
        s3_file_glob="int131_v4_bids_at_bid_cutoff_times_prev_2_1*",
        primary_keys=[
            "gas_date",
            "type_1",
            "type_2",
            "participant_id",
            "code",
            "offer_type",
            "bid_id",
            "schedule_type",
        ],
        table_schema={
            "gas_date": String,
            "type_1": String,
            "type_2": String,
            "participant_id": Int64,
            "participant_name": String,
            "code": String,
            "name": String,
            "offer_type": String,
            "step1": String,
            "step2": String,
            "step3": String,
            "step4": String,
            "step5": String,
            "step6": String,
            "step7": String,
            "step8": String,
            "step9": String,
            "step10": String,
            "min_daily_qty": Int64,
            "bid_id": Int64,
            "bid_cutoff_time": String,
            "schedule_type": String,
            "schedule_time": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Starting hour of gas day being reported e.g. 30 Jun 2007 06:00:00",  # noqa: E501
            "type_1": "'a' injections, 'b' controlled withdrawals. Used for grouping and ordering",  # noqa: E501
            "type_2": "'a' indicates price record, 'c' indicates cumulative quantity record. Used for grouping and ordering",  # noqa: E501
            "participant_id": "Participant id number",
            "participant_name": "Participant name",
            "code": "MIRN number for injection or withdrawal point",
            "name": "MIRN number as above",
            "offer_type": "Injection ('INJEC') or withdrawal ('CTLW')",
            "step1": "Price ($) or quantity for step 1",
            "step2": "Price ($) or quantity for step 2",
            "step3": "Price ($) or quantity for step 3",
            "step4": "Price ($) or quantity for step 4",
            "step5": "Price ($) or quantity for step 5",
            "step6": "Price ($) or quantity for step 6",
            "step7": "Price ($) or quantity for step 7",
            "step8": "Price ($) or quantity for step 8",
            "step9": "Price ($) or quantity for step 9",
            "step10": "Price ($) or quantity for step 10",
            "min_daily_qty": "Minimum daily quantity in GJ",
            "bid_id": "Bid identifier",
            "bid_cutoff_time": "Bid cutoff time",
            "schedule_type": "In this context: D+1 means the schedule was run 1 day ago, D+2 means the schedule was run 2 days ago",  # noqa: E501
            "schedule_time": "Time of schedule (e.g. 6:00:00, 10:00:00 etc.)",
            "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis public report lists the detail of all injection and controllable withdrawal bids provided by all Participants that were used as\ninputs into the scheduling processes run on the previous 2 gas days.\n\nThis report meets AEMO's statutory reporting requirement as specified in clause 209(11) of the NGR.\n\nInformation published in this report is historical. It is no longer commercially sensitive, and is intended to assist in the provision\nof transparency in the determination of market prices.\n\nInformation is available to each Market participant to confirm the receipt of each of their own submissions; therefore this report\nis not designed for confirmation purposes. Participants may use this report to analyse the bidding strategies of other\nParticipants that may be apparent in the bid data provided.\n\nEach report contains the details of all the bids that were used as input to approved schedules run for the previous 2 days (not\nincluding the current gas day).\n\nAll bids used at the time of scheduling are listed, regardless of whether they were submitted on the date of the schedule, or on\na prior day (for example, standing bids).\n\nEach row in the report contains either price or quantity details for a bid, along with the characteristics (schedule_time and bid_\ncutoff_time) for the schedule to which the bid was an input.\n\nThis report contains 2 rows for each bid listed:\n- The first row (type_2 = a) will contain the price steps for the bid.\n- The second row (type_2 = c) will contain the cumulative quantity for each bid step.\n\nContents in the type_1 field should correspond to contents in the offer_type field.\nContents in the gas_date field and the current_date field for a row should correspond to contents in the schedule_type field.\n\nFor example:\n- gas_date = 5 Feb 2007\n- current_date = 7 Feb 2007\nTherefore, schedule_type = D+2.\n\nThe bid_cutoff_time and schedule_time fields can be used to differentiate between intraday bids. It should be noted that a\nsingle bid_id may be repeated for multiple bid_cutoff_times.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
