from typing import Iterable

from dagster import (
    AssetCheckResult,
    AssetChecksDefinition,
    AssetsDefinition,
    asset_check,
)
from polars import LazyFrame

from aemo_etl.util import get_lazyframe_num_rows


def check_primary_keys_are_unique_factory(
    asset_definition: AssetsDefinition, *, primary_keys: Iterable[str]
) -> AssetChecksDefinition:
    @asset_check(
        asset=asset_definition,
        name="check_primary_keys_are_unique",
    )
    def check_primary_keys_are_unique(input_df: LazyFrame) -> AssetCheckResult:
        return AssetCheckResult(
            passed=bool(
                get_lazyframe_num_rows(input_df)
                == get_lazyframe_num_rows(input_df.select(*primary_keys).unique())
            )
        )

    return check_primary_keys_are_unique
