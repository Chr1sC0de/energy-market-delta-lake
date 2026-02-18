"""bronze_int188_v4_ctm_to_hv_zone_mapping_1 - Bronze MIBB report configuration."""

from polars import Int64, String
from aemo_etl.configuration import VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS
from aemo_etl.configuration.registry import mibb_report
from aemo_etl.configuration.report_config import ReportConfig, mibb_config_factory


@mibb_report
def CONFIG() -> ReportConfig:
    """MIBB report configuration."""
    return mibb_config_factory(
        table_name="bronze_int188_v4_ctm_to_hv_zone_mapping_1",
        s3_file_glob="int188_v4_ctm_to_hv_zone_mapping_1*",
        primary_keys=["mirn"],
        table_schema={
            "mirn": String,
            "site_company": String,
            "hv_zone": Int64,
            "hv_zone_desc": String,
            "effective_from": String,
            "current_date": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "mirn": "Meter Installation Registration Number",
            "site_company": "Company name",
            "hv_zone": "Heating value zone number as assigned by the AEMO. Values for Victoria can be in the range of 400-699",
            "hv_zone_desc": "Heating value zone name",
            "effective_from": "Date when the HV zone became effective for the mirn, Example: 01 Aug 2023",
            "current_date": "Date and time report produced, Example: 30 Jun 2007 06:00:00)",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="\n\nA report containing the DWGM's Custody Transfer Meter (CTM) to Heating Value Zone mapping.\n\nThe report provides the mapping of active DTS CTMs to the Heating Value Zones. The mapping of non-DTS CTM to heating\nvalue zone mapping for South Gippsland, Bairnsdale and Gippsland regions are also provided.\n",
        group_name=f"aemo__mibb__{VICTORIAN_WHOLESALE_SETTLEMENTS_AND_METERING_REPORTS}",
    )
