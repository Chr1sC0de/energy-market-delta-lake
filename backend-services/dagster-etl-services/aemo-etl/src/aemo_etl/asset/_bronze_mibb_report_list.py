from collections import defaultdict

import dagster as dg
import polars as pl
import pymupdf
import requests

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.parameter_specification import (
    PolarsLazyFrameScanParquetParamSpec,
    PolarsLazyFrameSinkParquetParamSpec,
)
from aemo_etl.register import table_locations
from aemo_etl.util import get_lazyframe_num_rows, get_metadata_schema


table_name = "bronze_mibb_report_list"
s3_table_location = f"s3://{BRONZE_BUCKET}/aemo/{table_name}"
table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "parquet",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


def process_extracted_table(table_contents: list[list[str]]) -> pl.LazyFrame:
    headers = [header.replace("\n", " ") for header in table_contents[0]]
    df_dict = defaultdict(list)
    for content in table_contents[1:]:
        for header, item in zip(headers, content):
            df_dict[header].append(item.replace("\n", " ").strip(""))
    return pl.LazyFrame(df_dict)


@dg.asset(
    group_name="aemo__metadata",
    key_prefix=["bronze", "aemo"],
    name=table_name,
    description="Grab the mibb report list from the following User Guide to MIBB Reports Document found here: https://aemo.com.au/energy-systems/gas/declared-wholesale-gas-market-dwgm/procedures-policies-and-guides",  # noqa: E501
    kinds={"source", "table", "parquet"},
    io_manager_key="s3_polars_parquet_io_manager",
    automation_condition=dg.AutomationCondition.missing()
    & ~dg.AutomationCondition.in_progress(),
    metadata={
        "dagster/column_schema": get_metadata_schema(
            {
                "report_name": pl.String,
                "trigger_event_and_or_time_aest": pl.String,
                "participant": pl.String,
                "market": pl.String,
                "consultative_forum": pl.String,
            },
            {
                "report_name": "Name of the report",
                "trigger_event_and_or_time_aest": "Trigger (event or time (shown as HH:MM AEST in table below))",  # noqa: E501
                "participant": "Participant receiving report (Public, private, Market participant, etc)",  # noqa: E501
                "market": "Market (DWGM – VIC, Retail – VIC, Retail – QLD etc)",
                "consultative_forum": "Consultative forum owner (GWCF or GRCF)",
            },
        ),
        "s3_polars_parquet_io_manager_options": {
            "sink_parquet_options": PolarsLazyFrameSinkParquetParamSpec(
                path=f"{s3_table_location}/result.parquet"
            ),
            "scan_parquet_options": PolarsLazyFrameScanParquetParamSpec(
                source=f"{s3_table_location}/"
            ),
        },
    },
)
def bronze_vicgas_mibb_report_list_asset() -> pl.LazyFrame:
    response = requests.get(
        "https://aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/april-2024-amendment-to-user-guide-to-mibb-reports/user-guide-to-mibb-reports.pdf?la=en",
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",  # noqa: E501
            "Accept": "application/pdf",
        },
    )
    assert response.status_code == 200, (
        f"request failed with status code: {response.status_code}"
    )
    doc: pymupdf.Document = pymupdf.open(stream=response.content)
    all_dfs = []
    all_dfs.append(process_extracted_table(doc[16].find_tables()[-1].extract()))  # pyright: ignore[reportAttributeAccessIssue]
    for i in range(17, 27):
        try:
            all_dfs.append(process_extracted_table(doc[i].find_tables()[-1].extract()))  # pyright: ignore[reportAttributeAccessIssue]
        except:
            raise
    output = pl.concat(all_dfs).rename(
        {
            "Report Name": "report_name",
            "Trigger (Event and/or Time (AEST))": "trigger_event_and_or_time_aest",
            "Participant": "participant",
            "Market": "market",
            "Consultative Forum": "consultative_forum",
        }
    )
    return output


@dg.asset_check(asset=bronze_vicgas_mibb_report_list_asset, name="no_duplicate_reports")
def bronze_vicgas_mibb_report_list_asset_check(
    bronze_mibb_report_list: pl.LazyFrame,
) -> dg.AssetCheckResult:
    return dg.AssetCheckResult(
        passed=bool(
            get_lazyframe_num_rows(bronze_mibb_report_list)
            == get_lazyframe_num_rows(
                bronze_mibb_report_list.select(pl.col("report_name")).unique()
            )
        ),
    )
