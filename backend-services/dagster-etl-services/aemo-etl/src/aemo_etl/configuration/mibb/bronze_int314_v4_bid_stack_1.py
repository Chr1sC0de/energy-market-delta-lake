"""bronze_int314_v4_bid_stack_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int314_v4_bid_stack_1",
        s3_file_glob="int314_v4_bid_stack_1*",
        primary_keys=["bid_id", "gas_date", "mirn", "bid_step"],
        table_schema={
            "bid_id": Int64,
            "gas_date": String,
            "market_participant_id": Int64,
            "company_name": String,
            "mirn": String,
            "bid_step": Int64,
            "bid_price": Float64,
            "bid_qty_gj": Float64,
            "step_qty_gj": Float64,
            "inject_withdraw": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "bid_id": "Bid Id.",
            "gas_date": "Gas date. Dd mmm yyyy",
            "market_participant_id": "Company Id of Bid owner",
            "company_name": "Company Name of Bid owner.",
            "mirn": "Phy_mirn (commissioned ='Y', bidding ='Y')",
            "bid_step": "Step (0 – 10)",
            "bid_price": "Dollar price per GJ for bid.",
            "bid_qty_gj": "MDQ for step.",
            "step_qty_gj": "Incremental MDQ for step",
            "inject_withdraw": "I or W Flag",
            "current_date": "Report generation date. dd mmm yyyy hh:mm:ss",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report is a public report that is published on both the MIBB and AEMO Website. It provides the bid stack data used in the\nscheduling process for the last scheduling horizon of each gas day in the past year.\n\nIt provides Participants with historical trend information that combined with other public information enables Participants to\ngain an insight to the scheduling outcomes for that horizon in the AEMO scheduling process.\n\nThis report provides historical bid stack data for each gas day in the previous one year (rolling), commencing with the previous\ngas day.\n\nThis report contains bid stack details, which are constructed by AEMO based on:\n- Bid step quantities (up to 10)\n- Minimum daily quantity (MDQ) submitted as part of the bid\n- Hourly quantity constraints requested by Market participants and accredited by AEMO\n\nAs a result of the application of the confidential accreditation values stored by AEMO the bid stack details\nmay not exactly match bids submitted by Market participants.\n\nbid_step details are constructed by AEMO based on MDQ details entered as part of the bid and the structure of bid steps\nthemselves.\n\nbid_step 0 is associated with:\n- a $0-price step for an injection bid\n- a VOLL-price step for a withdrawal bid\n\nIn general bid_step 0 will reflect the MDQ entered.\nbid_qty_gj reflects the cumulative quantities as submitted by the Market participant.\nstep_qty_gj is a calculated value that is the difference between 2 consecutive bid_qty_gj values. For example, if bid step 2 is\nfor 2,500GJ and bid step 3 is for 3,000GJ, then the step_qty_gj associated with bid_step = 3 is 500GJ.\n",
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
