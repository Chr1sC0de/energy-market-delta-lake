"""bronze_int140_v5_gas_quality_data_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int140_v5_gas_quality_data_1",
        s3_file_glob="int140_v5_gas_quality_data_1*",
        primary_keys=["mirn", "gas_date", "ti", "quality_type"],
        table_schema={
            "mirn": String,
            "gas_date": String,
            "ti": Int64,
            "quality_type": String,
            "unit": String,
            "quantity": Float64,
            "meter_no": String,
            "site_company": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "mirn": "Meter Installation Registration Number",
            "gas_date": "Gas day being reported e.g. 30 June 2007",
            "ti": "Time interval of the gas day (1-24), where 1 = 6:00 AM to 7:00 AM, 2 = 7:00 AM to 8:00 AM, until the 24th hour",  # noqa: E501
            "quality_type": "Gas quality types including: Wobber index, Hydrogen Sulphide, Total sulphur, Temperature, Heating value, Relative Density, Odorisation; Gas Composition types including: Methane, Ethane, Propane, N-Butane, I-Butane, N-Pentane, I-Pentane, Neo-Pentane, Hexanes, Nitrogen, Carbon Dioxide, Hydrogen",  # noqa: E501
            "unit": "Unit of measurement",
            "quantity": "Measurement value (some values are averaged instantaneous values for the hour)",  # noqa: E501
            "meter_no": "CTM meter number",
            "site_company": "Company name",
            "current_date": "Date and Time Report Produced (e.g. 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides a measure of gas quality and composition at injection points as outlined in Division 3 / Subdivision 3 Gas\nQuality, of the NGR. It is important for the Distribution Network Operators as they have the right to refuse the injection of out of\nspecification gas into their distribution networks.\n\nMost of the data provided are hourly average values, although some are spot (instantaneous) readings.\nNot all gas quality measures are provided for each injection point. The data provided for a particular injection point differs by\nthe gas source for and monitoring equipment at the point.\n\nThis report is generated each hour. Each report displays gas quality and composition details for the previous 3 hours at least.\nFor example, the report published at 1:00 PM contains details for:\n- 12:00 (ti=7)\n- 11:00 (ti=6)\n- 10:00 (ti=5)\n\nTime interval which shows each hour in the gas day, where 1 = 6:00 AM to 7:00 AM, 2 = 7:00 AM to 8:00 AM, until the 24th\nhour.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
