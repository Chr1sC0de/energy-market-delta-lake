"""bronze_int153_v4_demand_forecast_rpt_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int153_v4_demand_forecast_rpt_1",
        s3_file_glob="int153_v4_demand_forecast_rpt_1*",
        primary_keys=["forecast_date", "version_id", "ti"],
        table_schema={
            "forecast_date": String,
            "version_id": Int64,
            "ti": Int64,
            "forecast_demand_gj": Int64,
            "vc_override_gj": Int64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "forecast_date": "Gas date of forecast e.g. 30 Jun 2007",
            "version_id": "Forecast version used to identify which forecast was used in the schedule (reference INT108)",
            "ti": "Time interval (1-24)",
            "forecast_demand_gj": "Forecast total hourly demand (in GJ/hour) potentially used as input in the MCE",
            "vc_override_gj": "Quantity (in GJ) of any AEMO override (can be either positive or negative)",
            "current_date": "Date and time report produced",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report is created each time AEMO generates and saves a demand forecast. Note this may occur many times prior to the\nrunning of a schedule as AEMO tests the feasibility of the different variables used in a schedule. The report provides:\n- the total uncontrollable withdrawal quantity that may be used as input in the production of a schedule\n- the quantity (positive or negative) by which AEMO deems it necessary to adjust Market participant submissions in\n  order to maintain system security.\n\nParticipants may use this report to gauge AEMO's schedulers view of the current day situation and whether the aggregate of\nall Participants demand forecasts sum to an adequate demand value and/or profile given AEMO's perspective of the system\ndemands of the gas day.\n\nAs not every saved forecast demand generated is used in the scheduling process, Market participants need to reference\nINT108 Schedule Run Log to determine which Demand Forecast was actually used in scheduling.\n\nThe INT108 forecast_demand_version will specify which INT053 rows will provide information that was used by AEMO in its\nscheduling processes.\n\nThis report is generated each time AEMO generates and saves a demand forecast. Each report provides details of all the\ndemand forecasts created up to the report generation time on the current gas day.\n\nA given report may contain demand forecasts that are for:\n- the current day\n- 1 day ahead\n- 2 days ahead\n- 3 days ahead\n\nBy comparing the forecast_date with the current_date, users will be able to determine the type of forecast for a particular\nforecast (version_id) (i.e. whether it is for the current day or a day ahead schedule)\n\nEach row in a report provides the forecast demand and the AEMO override (in GJ) for the specified hour of the gas day of the\nspecified demand forecast. Therefore, there will be 24 rows in the report for each demand forecast.\n",
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
