from collections import defaultdict

import dagster as dg
import polars as pl
import pymupdf
import requests

from aemo_gas.configurations import BRONZE_BUCKET
from aemo_gas.utils import get_lazyframe_num_rows, get_metadata_schema
from aemo_gas.vichub.assets.bronze.table_locations import (
    register as table_locations_register,
)

guide_to_mibb_reports_link = "https://aemo.com.au/-/media/files/stakeholder_consultation/consultations/gas_consultations/2024/april-2024-amendment-to-user-guide-to-mibb-reports/user-guide-to-mibb-reports.pdf?la=en"

table_name = "bronze_mibb_report_list"
table_s3_location = f"s3://{BRONZE_BUCKET}/aemo/gas/vichub/{table_name}"
table_locations_register[table_name] = {
    "s3_path": table_s3_location,
    "storage_type": "parquet",
}


schema = {
    "Report Name": pl.String,
    "Trigger (Event and/or Time (AEST))": pl.String,
    "Participant": pl.String,
    "Market": pl.String,
    "Consultative Forum": pl.String,
}


def process_extracted_table(table_contents: list[list[str]]) -> pl.LazyFrame:
    headers = [header.replace("\n", " ") for header in table_contents[0]]
    df_dict = defaultdict(list)
    for content in table_contents[1:]:
        for header, item in zip(headers, content):
            df_dict[header].append(item.replace("\n", " ").strip(""))
    return pl.LazyFrame(df_dict)


@dg.asset(
    group_name="AEMO__GAS__VICHUB",
    key_prefix=["aemo", "gas", "vichub"],
    name=table_name,
    description="Grab the mibb report list from the following User Guide to MIBB Reports Document found here: https://aemo.com.au/energy-systems/gas/declared-wholesale-gas-market-dwgm/procedures-policies-and-guides",
    kinds={"source", "bronze", "parquet"},
    io_manager_key="bronze_aemo_gas_simple_polars_parquet_io_manager",
    automation_condition=dg.AutomationCondition.missing()
    & ~dg.AutomationCondition.in_progress(),
    metadata={"dagster/column_schema": get_metadata_schema(schema)},
)
def asset() -> pl.LazyFrame:
    response = requests.get(
        guide_to_mibb_reports_link,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
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
    output = pl.concat(all_dfs)
    return output


@dg.asset_check(asset=asset, name="has_not_duplicate_reports")
def asset_check(
    mibb_report_list: pl.LazyFrame,
):
    return dg.AssetCheckResult(
        passed=bool(
            get_lazyframe_num_rows(mibb_report_list)
            == get_lazyframe_num_rows(
                mibb_report_list.select(pl.col("Report Name")).unique()
            )
        ),
    )
