"""bronze_int176_v4_gas_composition_data_1 - Bronze MIBB report configuration."""

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
        table_name="bronze_int176_v4_gas_composition_data_1",
        s3_file_glob="int176_v4_gas_composition_data_1*",
        primary_keys=["hv_zone", "gas_date"],
        table_schema={
            "hv_zone": Int64,
            "hv_zone_desc": String,
            "gas_date": String,
            "methane": Float64,
            "ethane": Float64,
            "propane": Float64,
            "butane_i": Float64,
            "butane_n": Float64,
            "pentane_i": Float64,
            "pentane_n": Float64,
            "pentane_neo": Float64,
            "hexane": Float64,
            "nitrogen": Float64,
            "carbon_dioxide": Float64,
            "hydrogen": Float64,
            "spec_gravity": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "hv_zone": "Heating value zone number as assigned by the AEMO. Values for Victoria can be in the range of 400-699",  # noqa: E501
            "hv_zone_desc": "The heating value zone",
            "gas_date": "The gas date (e.g. 30 Jun 2011)",
            "methane": "The daily average of methane",
            "ethane": "The daily average of ethane",
            "propane": "The daily average of propane",
            "butane_i": "The daily average of butane",
            "butane_n": "The daily average of butane (N)",
            "pentane_i": "The daily average of pentane",
            "pentane_n": "The daily average of pentane (N)",
            "pentane_neo": "The daily average of pentane (Neo)",
            "hexane": "The daily average of hexane",
            "nitrogen": "The daily average of nitrogen",
            "carbon_doxide": "The daily average of carbon dioxide",
            "hydrogen": "The daily average of hydrogen. If no hourly values are available for the entire day, NULL is displayed.",  # noqa: E501
            "spec_gravity": "The daily average of specific gravity",
            "current_date": "The date and time the report is produced (e.g. 29 Jun 2012 01:23:45)",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis public report provides the gas composition daily average corresponding to the heating value zone.\n\nThe gas composition daily average in the report has taken into account the total delay hours from the injection source to the\nheating value zone. Therefore, the HV is always published one day in arrears.\nThe data in this report applies to the VIC wholesale gas market.\n\nAll gas composition values used in the daily average calculation are taken as at top of hour.\nThis report contains data for the past 60 gas days (such as, 60 gas days less than report date).\nOnly the Victorian heating value zones are included in this report.\nGas composition values are in molecule percentage units, except for Specific Gravity (which does not have a unit).\nGas composition data will be reported to 5 decimal places.\n\nThe gas composition daily average is calculated using the following formula:\n- SUM(hourly gas composition values) / COUNT(hours)\n- Where hours is the number of hours used to calculate the total gas composition for the day\n- Where no value is available for an hour, the report skips the hour in the calculation and continues on to the\n  next hour. If no hourly values are available for the entire day, a NULL is displayed.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_DECLARED_WHOLESALE_MARKET_SCHEDULING_REPORTS}",
    )
