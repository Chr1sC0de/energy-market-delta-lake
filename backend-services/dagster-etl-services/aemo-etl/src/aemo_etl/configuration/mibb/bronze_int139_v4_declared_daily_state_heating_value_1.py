"""bronze_int139_v4_declared_daily_state_heating_value_1 - Bronze MIBB report configuration."""  # noqa: E501

from polars import Float64, String
from aemo_etl.configuration import VICTORIAN_GAS_RETAIL_REPORTS_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int139_v4_declared_daily_state_heating_value_1",
        s3_file_glob="int139_v4_declared_daily_state_heating_value_1*",
        primary_keys=["gas_date"],
        table_schema={
            "gas_date": String,
            "declared_heating_value": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day being reported (e.g. 30 Jun 2007)",
            "declared_heating_value": "Declared daily state heating value\n    Sum(h,z [HV(z,h) *(CF(z,h)) ])/Sum(h,z (CF(h,z))\n    h= hour index\n    z=zone index\n    CF Corrected flow\n    HV Heating Value",  # noqa: E501
            "current_date": "Date and time report produced (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the declared daily state heating value (HV) which is used by gas retailers and distribution businesses in\ntheir billing processes, to convert the difference in (actual or estimated) index readings from basic meters to energy\nconsumption figures. The use of this state wide declared heating value is prescribed in the Victorian Distribution system code\nissued by the Essential Services Commission of Victoria. Section 2.6.1 (b) of the Victorian Retail Market Procedures describes\nAEMO obligation to publish the daily state heating value and the obligation that the Distributor must use this value to calculate\nthe average heating value for a reading period.\n\nThe reported values are the volume-weighted average HVs of all Victoria's heating value zones.\nNote the values in this report are not normally subject to revision.\n\nThis report is generated daily. Each report displays the daily state HV for the previous 90 days (not including the current gas\nday).\n\nEach row in the report provides the daily state HV for the specified gas_date.\n\nSince daily state HV is calculated on the basis of hourly HV readings, the latest possible daily state HV available is for the\nprevious full gas day. This means that daily state HV is always published 1 day in arrears.\n\nNote: This report is decommissioned from December 2024.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}",
    )
