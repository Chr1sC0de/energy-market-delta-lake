"""bronze_int539_v4_daily_zonal_hv_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration import QUEENSLAND_GAS_RETAIL_REPORT_DETAILS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int539_v4_daily_zonal_hv_1",
        s3_file_glob="int539_v4_daily_zonal_hv_1*",
        primary_keys=["gas_date", "hv_zone"],
        table_schema={
            "gas_date": String,
            "hv_zone": Int64,
            "hv_zone_desc": String,
            "heating_value_mj": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Gas day being reported e.g. 30 Jun 2007",
            "hv_zone": "Heating value zone as assigned by the distributor",
            "hv_zone_desc": "Name of the heating value zone",
            "heating_value_mj": "The Heating value is in MJ per standard cubic meters",
            "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nThis report provides the daily heating value for each heating value zone.\nSection 2.6.1 of the Queensland Retail Market Procedures sect the obligation that the Distributor is to provide the HV.\n\nThis Heating Value report contains data for rolling 120 days.\nThere is no equivalent VIC MIBB report.\n\nThis report is generated daily. Each report displays the daily HV for each heating value zone in Queensland over the previous\n120 gas days.\n\nEach row in the report provides heating values:\n- for a particular heating value zone\n- for a particular gas day\n",
        group_name=f"aemo__mibb__{QUEENSLAND_GAS_RETAIL_REPORT_DETAILS}",
    )
