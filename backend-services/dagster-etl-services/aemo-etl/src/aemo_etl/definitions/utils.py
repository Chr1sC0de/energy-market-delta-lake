from typing import Iterable, Mapping
from dagster import (
    AssetCheckResult,
    AssetExecutionContext,
    AssetsDefinition,
    asset_check,
)
from polars import DataType, Date, Datetime, LazyFrame, Time, col

from aemo_etl.util import get_lazyframe_num_rows


def post_process_hook(
    _: AssetExecutionContext,
    df: LazyFrame,
    *,
    primary_keys: Iterable[str],
    table_schema: Mapping[str, DataType],
) -> LazyFrame:
    df = df.filter(
        (
            col("current_date").str.strptime(Datetime, "%d %b %Y %H:%M:%S")
            == col("current_date").str.strptime(Datetime, "%d %b %Y %H:%M:%S").max()
        ).over(*primary_keys)
    )
    for name, type_ in table_schema.items():
        if type_ == Date:
            df = df.with_columns(col(name).str.to_date("%d %b %Y").cast(type_))
        if type_ == Datetime:
            df = df.with_columns(
                col(name).str.to_datetime("%d %b %Y %H:%M:%S").cast(type_)
            )
        if type_ == Time:
            df = df.with_columns(col(name).str.to_time("%H:%M:%S").cast(type_))
        else:
            df = df.with_columns(col(name).cast(type_))
    return df


def asset_check_factory(
    asset_definition: AssetsDefinition, *, primary_keys: Iterable[str]
):
    @asset_check(
        asset=asset_definition,
        name="check_unique_system_wide_notice_ids",
    )
    def check_unique_system_wide_notice_ids(input_df: LazyFrame):
        return AssetCheckResult(
            passed=bool(
                get_lazyframe_num_rows(input_df)
                == get_lazyframe_num_rows(input_df.select(*primary_keys).unique())
            )
        )

    return check_unique_system_wide_notice_ids
