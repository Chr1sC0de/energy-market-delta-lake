"""bronze_gasbb_linepack_capacity_adequacy - Bronze GASBB report configuration."""

from polars import Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_linepack_capacity_adequacy",
        s3_file_glob="gasbblinepackcapacityadequacy*",
        primary_keys=["GasDate", "FacilityId", "LastUpdated"],
        table_schema={
            "GasDate": String,
            "FacilityId": Int64,
            "FacilityName": String,
            "FacilityType": String,
            "Flag": String,
            "Description": String,
            "LastUpdated": String,
            "surrogate_key": String,
        },
        schema_descriptions={
            "GasDate": "Date of gas day. Timestamps are ignored. The gas day as defined in the pipeline contract or market rules.",  # noqa: E501
            "FacilityId": "A unique AEMO defined Facility identifier.",
            "FacilityName": "The name of the BB facility.",
            "FacilityType": "The type of facility (e.g., COMPRESSOR, PIPE).",
            "Flag": "The flags are traffic light colours (Green, Amber, Red) indicating the LCA status for each pipeline.",  # noqa: E501
            "Description": "Free text facility use is restricted to a description for reasons or comments directly related to the change in the LCA flag and the times, dates, or duration for which those changes are expected to apply.",  # noqa: E501
            "LastUpdated": "The date when the record was last updated.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",  # noqa: E501
        },
        report_purpose="\n\nThis report provides the Linepack Capacity Adequacy for each Pipeline for the current and next 2 gas days (D to D+2).\n\nThe report is produced daily and contains both historical and future data.\n\nLCA flags for BB pipelines:\n- GREEN: Pipeline is able to accommodate increased gas flows and the conditions for Amber or Red are not met.\n- AMBER: Pipeline is flowing at full capacity, but no involuntary curtailment of 'firm' load is likely or happening.\n- RED: Involuntary curtailment of 'firm' load is likely or happening, or linepack has, or is forecast to, drop below minimum operating levels.\n\nThe report can be filtered by:\n- GasDate\n- FacilityId, multiple Facility Ids, or all Facility Ids\n",  # noqa: E501
    )
