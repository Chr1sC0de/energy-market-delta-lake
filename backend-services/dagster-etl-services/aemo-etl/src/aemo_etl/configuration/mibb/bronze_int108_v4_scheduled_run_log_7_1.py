"""bronze_int108_v4_scheduled_run_log_7_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int108_v4_scheduled_run_log_7_1",
        s3_file_glob="int108_v4_scheduled_run_log_7_1*",
        primary_keys=["transmission_document_id"],
        table_schema={
            "transmission_id": Int64,
            "transmission_document_id": Int64,
            "transmission_group_id": Int64,
            "gas_start_datetime": String,
            "bid_cutoff_datetime": String,
            "schedule_type_id": String,
            "creation_datetime": String,
            "forecast_demand_version": String,
            "dfs_interface_audit_id": Int64,
            "last_os_for_gas_day_tdoc_id": Int64,
            "os_prior_gas_day_tdoc_id": Int64,
            "approval_datetime": String,
            "demand_type_id": Int64,
            "objective_function_value": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "transmission_id": "Transmission ID",
            "transmission_document_id": "Unique identity for each schedule",
            "transmission_group_id": "To link the Operational Schedule to the Market Schedule of an ante schedule",
            "gas_start_datetime": "Similar to Schedule_Start_date but not absolute (Trading between midnight and 6:00 AM is considered to be belonged to the previous day)",
            "bid_cutoff_datetime": "If the submission datetime is after the datetime specified by this Bid_Cutoff_Date then the nomination (or bids) is used",
            "schedule_type_id": "'MS' Market Schedule, 'OS' Operational Schedule",
            "creation_datetime": "When schedule is created",
            "forecast_demand_version": "Version as listed in the TMM database",
            "dfs_interface_audit_id": "Version as stored in the DFS database",
            "last_os_for_gas_day_tdoc_id": "Last Operating schedule for the day either a 1 PM or an ad hoc",
            "os_prior_gas_day_tdoc_id": "Last Operating schedule for the previous day either a 1 PM or an ad hoc",
            "approval_datetime": "Date and time of approval",
            "demand_type_id": "Type of demand: '0' = Normal, '1' = Plus 10 percent, '2' = Minus 10 percent",
            "objective_function_value": "Objective_Function_Value for each run. This value is returned from the MCE",
            "current_date": "Date and Time Report Produced",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose='\n\nThis report lists all the schedules that have been run for the previous 7 gas days. It provides transparency of AEMO demand\nforecasting and scheduling activities on the basis of inputs from Market participants and weather forecasts.\n\nFor instance, Participants may wish to rely on the information provided in this report for reconciliation of the scheduling\nprocess delivered by AEMO. The quantities and prices for each of the standard schedules in the reporting window are\nidentified by the unique schedule identifiers (transmission_id and transmission_document_id) to assist with tracking the\nprocess across the day.\n\nThis report contains details for each of the schedules run for the previous 7 gas days. It includes both:\n- standard schedules (such as the schedules published at fixed times specified in the NGR); and\n- any ad hoc schedules\n\nInformation in the report can be linked to Participants demand forecasting activities. For example, see "INT126 - DFS Data"\nand "INT153 - Demand Forecast" for quantities and prices.\n\nEach report identifies each of the schedules run for the previous 7 gas days. For each day in the reporting window, \nthere will be at least 18 rows of data:\n- 5 being for the standard current gas day operational schedules\n- 5 being for the standard current gas day pricing schedules\n- 3 being for the standard 1-day ahead operational schedules\n- 3 being for the standard 1-day ahead pricing schedules\n- 1 being for the standard 2 days ahead operational schedule\n- 1 being for the standard 2 days ahead pricing schedule\n\nEach schedule run in the previous 7 gas days is identified in a separate row of the report.\n',
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
