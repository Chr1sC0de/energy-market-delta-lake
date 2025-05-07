from collections.abc import Iterable
from functools import partial
from typing import Callable
import dagster as dg
import polars as pl

from aemo_etl.util import get_lazyframe_num_rows


def get_unique_rows_from_primary_key(
    df: pl.LazyFrame, primary_key: str | Iterable[str]
) -> int:
    return get_lazyframe_num_rows(df.select(primary_key).unique())


def get_unique_rows(df: pl.LazyFrame) -> int:
    return get_lazyframe_num_rows(df.unique())


def default_check_fn(
    df: pl.LazyFrame, *, row_count_fn: Callable[[pl.LazyFrame], int]
) -> bool:
    return get_lazyframe_num_rows(df) == row_count_fn(df)


def duplicate_row_check_factory(
    assets_definition: dg.AssetsDefinition,
    check_name: str | None = None,
    primary_key: str | list[str] | None = None,
    check_fn: Callable[[pl.LazyFrame], bool] | None = None,
    description: str | None = None,
    blocking: bool = False,
    retry_policy: dg.RetryPolicy | None = None,
) -> dg.AssetChecksDefinition:
    row_count_fn: Callable[[pl.LazyFrame], int]

    if primary_key is not None:
        row_count_fn = partial(
            get_unique_rows_from_primary_key, primary_key=primary_key
        )
    else:
        row_count_fn = get_unique_rows

    if check_fn is None:
        check_fn = partial(default_check_fn, row_count_fn=row_count_fn)

    @dg.asset_check(
        asset=assets_definition,
        description=description,
        blocking=blocking,
        retry_policy=retry_policy,
        name=check_name,
    )
    def duplicate_row_check(input_df: pl.LazyFrame) -> dg.AssetCheckResult:
        return dg.AssetCheckResult(
            passed=check_fn(input_df),
            check_name=check_name,
        )

    return duplicate_row_check
