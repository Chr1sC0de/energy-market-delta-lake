"""bronze_gasbb_forecast_utilisation - Bronze GASBB report configuration."""

from polars import Float64, Int64, String

from aemo_etl.configuration.registry import gasbb_report
from aemo_etl.configuration.report_config import ReportConfig, gasbb_config_factory


@gasbb_report
def CONFIG() -> ReportConfig:
    """GASBB report configuration."""
    return gasbb_config_factory(
        table_name="bronze_gasbb_forecast_utilisation",
        s3_file_glob="gbb_forecastutilisation*",
        primary_keys=[
            "State",
            "FacilityId",
            "FacilityName",
            "FacilityType",
            "ReceiptLocationId",
            "ReceiptLocationName",
            "DeliveryLocationId",
            "DeliveryLocationName",
            "Description",
            "ForecastMethod",
            "Units",
            "ForecastDay",
            "ForecastDate",
        ],
        table_schema={
            "State": String,
            "FacilityId": Int64,
            "FacilityName": String,
            "FacilityType": String,
            "ReceiptLocationId": Int64,
            "ReceiptLocationName": String,
            "DeliveryLocationId": Int64,
            "DeliveryLocationName": String,
            "Description": String,
            "ForecastMethod": String,
            "ForecastedFrom": String,
            "ForecastDate": String,
            "ForecastDay": String,
            "Units": String,
            "ForecastValue": String,
            "Nameplate": Float64,
            "surrogate_key": String,
        },
        schema_descriptions={
            "State": "Name of the state.",
            "FacilityId": "A unique AEMO defined facility identifier.",
            "FacilityName": "The name of the BB facility.",
            "FacilityType": "Facility type associated with the facility id.",
            "ReceiptLocationId": "The Connection Point Id that best represents the receipt location associated with a pipeline's nameplate capacity flow direction.",
            "ReceiptLocationName": "The Connection Point name associated with the ReceiptLocationId.",
            "DeliveryLocationId": "The Connection Point Id that best represents the delivery location associated with a pipeline's nameplate capacity flow direction.",
            "DeliveryLocationName": "The Connection Point name associated with the DeliveryLocationId.",
            "Description": "Describes the calculation that is being performed in each row of the report.",
            "ForecastMethod": "Describes the calculation that is being performed for each BB pipeline where the Description is Forecast Flow.",
            "ForecastedFrom": "Date forecasts were created from",
            "ForecastDate": "Date forecasted for a given period",
            "ForecastDay": "Day+N description for forecast period",
            "Units": "The unit of measure for the calculated values.",
            "ForecastValue": "Value forecasted",
            "Nameplate": "Standing nameplate capacity quantity in TJ. Nameplate rating relates to maximum daily quantities under normal operating conditions.",
            "surrogate_key": "Unique identifier created using sha256 over the primary keys",
        },
        report_purpose="""

The purpose of the forecast utilisation report is to provide a summary of forecast information provided by Gas Bulletin Board (BB) facility operators. 
The report is a 7-day outlook of the supply-demand gas balance in the East Coast.

GASBB_FORECAST_UTILISATION_NEXT7 is updated daily. The report is not updated once produced.

Data in the report contains information for D+1 through to D+7.
""",
    )
