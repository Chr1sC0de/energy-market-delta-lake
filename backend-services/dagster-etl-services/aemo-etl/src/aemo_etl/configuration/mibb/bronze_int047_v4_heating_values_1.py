"""bronze_int047_v4_heating_values_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int047_v4_heating_values_1",
        s3_file_glob="int047_v4_heating_values_1*",
        primary_keys=["version_id", "event_datetime", "heating_value_zone"],
        table_schema={
            "version_id": Int64,
            "gas_date": String,
            "event_datetime": String,
            "event_interval": Int64,
            "heating_value_zone": Int64,
            "heating_value_zone_desc": String,
            "initial_heating_value": Float64,
            "current_heating_value": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "version_id": "Version of Heating Values.",
            "gas_date": "Starting hour of gas day being reported as 30 Jun 2007",
            "event_datetime": "Start of hour for which values applies (e.g. 29 Jun 2007 06:00:00)",  # noqa: E501
            "event_interval": "hour interval of the day\n    6:00 AM = 1\n    7:00 AM = 2\n    5:00 AM = 24",  # noqa: E501
            "heating_value_zone": "Heating value zone id number",
            "heating_value_zone_desc": "Heating value zone name",
            "initial_heating_value": "Heating value (GJ/1000 m(3)) rounded to 2 decimal places.",  # noqa: E501
            "current_heating_value": "Heating valiue (GJ/1000m(3)) rounded r=to 2 decimal places",  # noqa: E501
            "current_date": "Date and Time Report Produced. 30 Jun 2007 06:00:00.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the hourly calorific value of gas delivered for each heating value zone in Victoria.\n\nThis information allows AEMO and other Market participant to convert the volumetric measurements taken at interval meters\ninto units of energy for various purposes including:\n- operation of the gas system\n- settlement of the wholesale market\n- billing of interval metered retail customers.\n\nThe initial_heating_value is the first obtained, and may be superseded in the course of the gas day date and during the 7 day\nreporting window for INT047. Therefore, the current_heating_value is in most cases the more accurate data value to use. The\ncurrent_heating_value shown for yesterday is more likely to undergo revision than the current_heating_value shown for 7 days\nago.\n\nIt should be noted that even after 7 days, the HV may still be revised for settlement purposes. In these circumstances a\nHeating Value Data Correction notice for the (preceding) month will be published on the AEMO website and corrections for\nindividual meters sent to the energy values provider, DMS.\n\nThis report is generated daily. Each report displays the hourly HV for each heating value zone in Victoria over the\nprevious 7 gas days (not including the current gas day).\n\nEach row in the report provides the 'initial' and 'current' HVs:\n- for a particular hour interval\n- for a particular heating value zone\n- for a specific gas day date\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
