"""bronze_int117b_v4_ancillary_payments_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int117b_v4_ancillary_payments_1",
        s3_file_glob="int117b_v4_ancillary_payments_1*",
        primary_keys=["ap_run_id", "gas_date", "schedule_no"],
        table_schema={
            "ap_run_id": Int64,
            "gas_date": String,
            "schedule_no": Int64,
            "ancillary_amt_gst_ex": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "ap_run_id": "Number identifying ancillary run",
            "gas_date": "Format: dd mmm yyyy hh:mm (e.g. 15 Feb 2007 06:00)",
            "schedule_no": "Schedule number",
            "ancillary_amt_gst_ex": "Total Ancillary Payment (can be positive or negative) for a schedule",  # noqa: E501
            "current_date": "Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report is a public version of INT116b. It shows the actual ancillary payments for the gas market by taking into account the\nActual Gas Injected Negative Offset (AGINO) and Actual Gas Withdrawal Negative Offset (AGWNO) quantities, as well as the\nproportion of injections used to support an uplift hedge.\n\nParticipants may wish to use this report to gauge their actual ancillary payments (from INT116b) in the context of the whole\ngas market.\n\nParticipants should note that although the AGINO and AGWNO are included in the calculations for this report, the meter data\nused for this purpose is provisional data that may change at settlement.\n\nThis a public report containing ancillary payments from the beginning of the previous month and is produced no later than the\nthird business day after the gas day (D+3).\n\nThere are a number of participant specific reports and public reports relating to ancillary payments, in particular:\n- INT116 - Participant Specific Ancillary Payments Reports Day + 3\n- INT116a - Participant Specific Estimated Ancillary Payments Report\n- INT116b - Participant Specific Ancillary Payments\n- INT117a - Public Estimated Ancillary Payments\n\nThe ancillary payment amount can be positive or negative depending on the total ancillary payment for the schedule (if it is in\ncredit or debit).\n\nThe number of rows in this report is dependent on the time of the month when this report is produced.\nEach report contains the:\n- ancillary run identifier\n- gas date\n- schedule number related to the scheduling horizon (where schedule1 will refer to 6:00 AM to 6:00 AM and schedule2\n  will relate to 10:00 AM to 6:00 AM, and so forth)\n- total ancillary payment for the schedule\n- date and time when the report was produced\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
