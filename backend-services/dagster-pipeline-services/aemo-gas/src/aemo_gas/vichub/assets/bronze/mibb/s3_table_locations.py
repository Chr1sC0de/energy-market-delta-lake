from collections.abc import Iterable
import dagster as dg
import polars as pl

from aemo_gas.configurations import BRONZE_BUCKET
from aemo_gas.utils import get_metadata_schema, get_lazyframe_num_rows
from aemo_gas.vichub.assets.bronze.table_locations import (
    register as table_locations_register,
)

schema = {
    "table_name": pl.String,
    "s3_path": pl.String,
    "storage_type": pl.String,
}

table_name = "bronze_s3_table_locations"
table_s3_location = f"s3://{BRONZE_BUCKET}/aemo/gas/vichub/{table_name}"
table_locations_register[table_name] = {
    "s3_path": table_s3_location,
    "storage_type": "parquet",
}


@dg.asset(
    group_name="AEMO__GAS__VICHUB",
    key_prefix=["aemo", "gas", "vichub"],
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


@dg.multi_asset_check(
    # Map checks to targeted assets
    specs=[
        dg.AssetCheckSpec(
            name="unique_table_names",
            asset=asset,
            description="check that the table names are all unique",
        ),
        dg.AssetCheckSpec(
            name="s3_path_correctly_formatted",
            asset=asset,
            description="ensure that the table paths start with 's3://'",
        ),
        dg.AssetCheckSpec(
            name="storage_type_are_correct",
            asset=asset,
            description="ensure that the storage type is within ('parquet','deltalake')",
        ),
    ],
    ins={"table": dg.AssetIn(asset.key)},
)
def asset_check(table: pl.LazyFrame) -> Iterable[dg.AssetCheckResult]:
    table_length = get_lazyframe_num_rows(table)
    yield dg.AssetCheckResult(
        check_name="unique_table_names",
        passed=bool(
            table_length == get_lazyframe_num_rows(table.select("table_name").unique())
        ),
        asset_key=asset.key,
    )

    yield dg.AssetCheckResult(
        check_name="s3_path_correctly_formatted",
        passed=bool(
            table_length
            == get_lazyframe_num_rows(
                table.filter(
                    pl.col("s3_path").str.starts_with(f"s3://{BRONZE_BUCKET}/")
                )
            )
        ),
        asset_key=asset.key,
    )

    yield dg.AssetCheckResult(
        check_name="storage_type_are_correct",
        passed=bool(
            table_length
            == get_lazyframe_num_rows(
                table.filter(pl.col("storage_type").is_in(["deltalake", "parquet"]))
            )
        ),
        asset_key=asset.key,
    )
