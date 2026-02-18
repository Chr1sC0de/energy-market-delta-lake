"""bronze_int117a_v4_est_ancillary_payments_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int117a_v4_est_ancillary_payments_1",
        s3_file_glob="int117a_v4_est_ancillary_payments_1*",
        primary_keys=["gas_date", "schedule_no"],
        table_schema={
            "gas_date": String,
            "schedule_no": Int64,
            "est_ancillary_amt_gst_ex": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Format: dd mmm yyyy hh:mm (e.g. 15 Feb 2007 06:00)",
            "schedule_no": "Schedule number associated with the scheduling horizon (i.e. 1 = 6:00 AM to 6:00 AM, 2 = 10:00 AM to 6:00 AM)",
            "est_ancillary_amt_gst_ex": "Total Estimated Ancillary Payment (can be positive or negative) for a schedule",
            "current_date": "Time Report Produced (e.g. 30 Jun 2007 01:23:45)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report is a public version of INT116a. It provides the estimated ancillary payments for the total gas market but does not\ntake into account Actual Gas Injected Negative Offset (AGINO) and Actual Gas Withdrawal Negative Offset (AGWNO)\nquantities. That is it is it is produce at the operational schedule time and is not adjusted for actual metered values, and is\ntherefore likely to differ from the final settlement total.\n\nParticipants may use this report to compare their estimated ancillary payments (from INT116a) in the context of the whole gas\nmarket.\n\nThis is a public report containing ancillary payments from the beginning of the previous month and is produced after each\nschedule.\n\nThis report does not take into account AP Clawback. AP Clawback is a mechanism which recovers ancillary payments that\nhave already been made to participants on the basis of a scheduled injection or withdrawal when those injections or\nwithdrawals are de-scheduled in a later horizon.\n\nThere are a number of participant specific reports and public reports relating to ancillary payments, in particular:\n- INT116 - Participant Specific Ancillary Payments Reports Day + 3\n- INT116a - Participant Specific Estimated Ancillary Payments Report\n- INT116b - Participant Specific Ancillary Payments\n- INT117b - Public Ancillary Payments Report (Day+1)\n\nThe ancillary payment amount can be positive or negative depending on the total estimated ancillary payment for the schedule\n(if it is in credit or debit).\n\nThe number of rows in this report is dependent on the time of the month when this report is produced.\nEach report contains the:\n- gas date\n- schedule number related to the scheduling horizon (where schedule1 will refer to 6:00 AM to 6:00 AM and schedule2\n  will relate to 10:00 AM to 6:00 AM, and so forth)\n- total estimated ancillary payment (positive or negative) for the schedule\n- date and time when the report was produced\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
