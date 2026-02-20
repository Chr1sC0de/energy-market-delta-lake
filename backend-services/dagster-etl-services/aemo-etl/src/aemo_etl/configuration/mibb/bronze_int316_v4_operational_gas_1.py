"""bronze_int316_v4_operational_gas_1 - Bronze MIBB report configuration."""

from polars import Float64, Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int316_v4_operational_gas_1",
        s3_file_glob="int316_v4_operational_gas_1*",
        primary_keys=["gas_date", "hv_zone"],
        table_schema={
            "gas_date": String,
            "hv_zone": Int64,
            "hv_zone_desc": String,
            "energy_gj": Float64,
            "volume_kscm": Float64,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "gas_date": "Date the record was current, e.g. 30 Jun 2007",
            "hv_zone": "Heating value zone id number",
            "hv_zone_desc": "Heating value zone name",
            "energy_gj": "Sum of Hourly energy (GJ) for gas date",
            "volume_kscm": "Sum of Hourly volume (kscm) for gas date",
            "current_date": "Date and Time Report Produced, e.g. 30 Jun 2005 1:23:56",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report is a comma separated values (csv) file that contains details of operational gas (volumes in kscm and energy in GJ)\nby heating value zone.\n\nThis report should be used in conjunction with the linepack report to determine Market participant portion of operational gas.\nParticipants are advised to check the date range of the latest final settlement run to determine if the corresponding data in this\nreport is:\n- provisional (no settlement version for the gas date)\n- preliminary (only preliminary settlement has been run for the gas date)\n- final (final settlement run for the gas date)\n- revision (revision settlement has been run for the gas date)\n\nThis report is generated weekly on a Saturday.\n\nEach report contains data for the period between and including the following:\nThe first gas date of the month that is 13 months prior to the current date and the gas date prior to the current gas date.\n",  # noqa: E501
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
