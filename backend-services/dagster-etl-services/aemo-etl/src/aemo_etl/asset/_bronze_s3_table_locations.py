from collections import defaultdict
from collections.abc import Iterable

from dagster import (
    AssetCheckResult,
    AssetCheckSpec,
    AssetIn,
    AutomationCondition,
    asset,
    multi_asset_check,
)
from polars import LazyFrame, String, col

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.parameter_specification import (
    PolarsLazyFrameScanParquetParamSpec,
    PolarsLazyFrameSinkParquetParamSpec,
)
from aemo_etl.register import table_locations
from aemo_etl.util import get_lazyframe_num_rows, get_metadata_schema

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      define table and register to table locations                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


table_name = "bronze_s3_table_locations"

s3_table_location = f"s3://{BRONZE_BUCKET}/aemo/{table_name}"

schema = {
    "table_name": String,
    "table_type": String,
    "glue_schema": String,
    "s3_table_location": String,
}

descriptions = {
    "table_name": "name of the target table",
    "table_type": "target type of the table Literal['parquet', 'delta']",
    "glue_schema": "schema used by glue",
    "s3_table_location": "s3 location of table",
}

table_locations[table_name] = {
    "table_name": table_name,
    "table_type": "parquet",
    "glue_schema": "aemo",
    "s3_table_location": s3_table_location,
}


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                create asset definition                                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@asset(
    group_name="aemo__metadata",
    key_prefix=["bronze", "aemo"],
    name=table_name,
    description="This table maps tables back to their locations on s3",
    kinds={"table", "parquet"},
    io_manager_key="s3_polars_parquet_io_manager",
    automation_condition=AutomationCondition.missing()
    & ~AutomationCondition.in_progress(),
    metadata={
        "dagster/column_schema": get_metadata_schema(schema, descriptions),
        "s3_polars_parquet_io_manager_options": {
            "sink_parquet_options": PolarsLazyFrameSinkParquetParamSpec(
                path=f"{s3_table_location}/result.parquet"
            ),
            "scan_parquet_options": PolarsLazyFrameScanParquetParamSpec(
                source=f"{s3_table_location}/"
            ),
            "preview_row_count": 10000,
        },
    },
)
def bronze_s3_table_locations_asset() -> LazyFrame:
    df_dict = defaultdict[str, list[object]](list)
    for dict_ in table_locations.values():
        for key, value in dict_.items():
            df_dict[key].append(value)

    return LazyFrame(
        df_dict,
        schema=schema,
    )


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                  create asset checks                                   │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@multi_asset_check(
    # Map checks to targeted assets
    specs=[
        AssetCheckSpec(
            name="unique_table_names",
            asset=bronze_s3_table_locations_asset,
            description="check that the table names are all unique",
        ),
        AssetCheckSpec(
            name="s3_table_location_correctly_formatted",
            asset=bronze_s3_table_locations_asset,
            description="ensure that the table paths start with 's3://'",
        ),
        AssetCheckSpec(
            name="storage_type_are_correct",
            asset=bronze_s3_table_locations_asset,
            description="ensure that the storage type is within ('parquet','deltalake')",
        ),
    ],
    ins={"table": AssetIn(bronze_s3_table_locations_asset.key)},
)
def bronze_s3_table_locations_asset_check(
    table: LazyFrame,
) -> Iterable[AssetCheckResult]:
    table_length = get_lazyframe_num_rows(table)
    yield AssetCheckResult(
        check_name="unique_table_names",
        passed=bool(
            table_length == get_lazyframe_num_rows(table.select("table_name").unique())
        ),
        asset_key=bronze_s3_table_locations_asset.key,
    )

    yield AssetCheckResult(
        check_name="s3_table_location_correctly_formatted",
        passed=bool(
            table_length
            == get_lazyframe_num_rows(
                table.filter(
                    col("s3_table_location").str.starts_with(f"s3://{BRONZE_BUCKET}/")
                )
            )
        ),
        asset_key=bronze_s3_table_locations_asset.key,
    )

    yield AssetCheckResult(
        check_name="storage_type_are_correct",
        passed=bool(
            table_length
            == get_lazyframe_num_rows(
                table.filter(col("table_type").is_in(["delta", "parquet"]))
            )
        ),
        asset_key=bronze_s3_table_locations_asset.key,
    )
