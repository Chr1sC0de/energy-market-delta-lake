"""bronze_int139a_v4_daily_zonal_heating_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_GAS_RETAIL_REPORTS_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int139a_v4_daily_zonal_heating_1",
        s3_file_glob="int139a_v4_daily_zonal_heating_1*",
        primary_keys=["gas_date", "hv_zone"],
        table_schema={
            "gas_date": String,
            "hv_zone": Int64,
            "hv_zone_desc": String,
            "heating_value": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Starting hour of gas day being reported, example: 30 Jun 2007",
            "hv_zone": "Heating value zone number as assigned by the AEMO. Values for Victoria can be in the range of 400-699",  # noqa: E501
            "hv_zone_desc": "Heating value zone name",
            "heating_value": "Daily volume flow weighted average heating value (GJ/1000 m(3)) to two decimal places",  # noqa: E501
            "current_date": "Date and time report is produced. Example: 30 Jun 2007 06:00:00",  # noqa: E501
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nA report providing the heating value for each heating value zone used to determine the energy content of gas consumed within\nVictoria. This is consistent with the Energy Calculation Procedures.\n\nSection 2.6.1 of the Retail Market Procedures (Victoria) provided details on how heating value zones for the basic meter that\nchanges during the measurement period are to be applied.\n\nThe daily zonal heating value calculation is expected to be triggered at approximately 9:30AM each day.\n\nThe reported values are the volume-weighted average HVs of each of Victoria's heating value zones.\nThe values in this report may be subject to revision by AEMO.\n\nThis report contains heating values zones for DTS connected DDS and non-DTS connected DDS (i.e. Non-DTS Bairnsdale,\nnon-DTS South Gippsland, and non-DTS Grampians regions).\n\nThis report is generated daily. Each report displays the daily volume weighted average HV for each heating value zone in\nVictoria over the previous 90 gas days (not including the current gas day).\n\nEach row in the report provides the heating values for a:\n- Heating value zone\n- Specific gas date\n\nSince the heating value (HV) is calculated based on hourly HV readings, the latest HV available is for the previous full gas day.\nTherefore, the HV is always published one day in arrears.\n\nIn the event an hourly HV wasn't available or deemed invalid, it would be substituted according to the set substitution rules.\nUnresolved substitutions are reviewed at the end of each month.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_GAS_RETAIL_REPORTS_DETAILS}",
    )
