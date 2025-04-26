from collections import defaultdict

import dagster as dg
import polars as pl
import pymupdf
import requests

from aemo_gas.configurations import BRONZE_BUCKET
from aemo_gas.utils import get_metadata_schema
from aemo_gas.vichub.assets.bronze.table_locations import (
    register as table_locations_register,
)

schema = {
    "table_name": pl.String,
    "s3_path": pl.String,
    "storage_type": pl.String,
}

table_name = "s3_table_locations"
table_s3_location = f"s3://{BRONZE_BUCKET}/aemo/gas/vichub/{table_name}"
table_locations_register[table_name] = {
    "s3_path": table_s3_location,
    "storage_type": "parquet",
}


@dg.asset(
    group_name="BRONZE__AEMO__GAS__VICHUB",
    key_prefix=["bronze", "aemo", "gas", "vichub"],
    name=table_name,
    description="this table maps tables back to their locations on s3",
    kinds={"bronze", "parquet"},
    io_manager_key="bronze_aemo_gas_simple_polars_parquet_io_manager",
    automation_condition=dg.AutomationCondition.missing()
    & ~dg.AutomationCondition.in_progress(),
    metadata={"dagster/column_schema": get_metadata_schema(schema)},
)
def asset() -> pl.LazyFrame:
    table_names = []
    s3_paths = []
    storage_types = []
    for key, items in table_locations_register.items():
        table_names.append(key)
        s3_paths.append(items["s3_path"])
        storage_types.append(items["storage_type"])

    return pl.LazyFrame(
        {"table_name": table_names, "s3_path": s3_paths, "storage_type": storage_types},
        schema=schema,
    )
