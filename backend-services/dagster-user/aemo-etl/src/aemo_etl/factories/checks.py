"""Reusable Dagster asset check factories."""

import tempfile
from collections.abc import Iterable
from functools import partial
from pathlib import Path
from typing import Callable, Mapping

import polars as pl
from dagster import (
    AssetCheckResult,
    AssetChecksDefinition,
    AssetCheckSeverity,
    AssetsDefinition,
    MetadataValue,
    RetryPolicy,
    asset_check,
)
from polars import LazyFrame, scan_delta
from polars._typing import PolarsDataType
from polars.testing import assert_schema_equal

from aemo_etl.utils import get_lazyframe_num_rows


def get_unique_rows_from_primary_key(
    df: pl.LazyFrame, primary_key: str | Iterable[str]
) -> int:
    """Return the number of unique rows for the selected primary key columns."""
    return get_lazyframe_num_rows(df.select(primary_key).unique())


def get_unique_rows(df: pl.LazyFrame) -> int:
    """Return the number of unique rows across all columns."""
    return get_lazyframe_num_rows(df.unique())


def default_check_fn(
    df: pl.LazyFrame, *, row_count_fn: Callable[[pl.LazyFrame], int]
) -> bool:
    """Return whether total row count matches the supplied unique row count."""
    return get_lazyframe_num_rows(df) == row_count_fn(df)


def duplicate_row_check_factory(
    assets_definition: AssetsDefinition,
    check_name: str | None = None,
    primary_key: str | list[str] | None = None,
    check_fn: Callable[[pl.LazyFrame], bool] | None = None,
    description: str | None = None,
    blocking: bool = False,
    retry_policy: RetryPolicy | None = None,
) -> AssetChecksDefinition:
    """Create an asset check that fails when duplicate rows are present."""
    if primary_key is not None:
        row_count_fn = partial(
            get_unique_rows_from_primary_key, primary_key=primary_key
        )
    else:
        row_count_fn = get_unique_rows

    if check_fn is None:
        check_fn = partial(default_check_fn, row_count_fn=row_count_fn)

    @asset_check(
        asset=assets_definition,
        description=description,
        blocking=blocking,
        retry_policy=retry_policy,
        name=check_name,
    )
    def duplicate_row_check(input_df: LazyFrame) -> AssetCheckResult:
        passed = check_fn(input_df)

        if not passed:
            if primary_key is None:
                duplicate_partition_columns = input_df.collect_schema().names()
            elif isinstance(primary_key, str):
                duplicate_partition_columns = [primary_key]
            else:
                duplicate_partition_columns = list(primary_key)

            sink_path = Path(tempfile.mkdtemp()) / "duplicate_data"
            input_df.filter(pl.len().over(duplicate_partition_columns) > 1).sink_delta(
                sink_path
            )

            duplicates = scan_delta(sink_path).filter(
                pl.len().over(duplicate_partition_columns) > 1
            )
            duplicate_count = duplicates.select(pl.len()).collect().item()

            metadata = {
                "duplicate_preview": MetadataValue.md(
                    duplicates.head(10).collect().to_pandas().to_markdown()
                ),
                "count": duplicate_count,
            }
        else:
            metadata = None

        return AssetCheckResult(passed=passed, check_name=check_name, metadata=metadata)

    return duplicate_row_check


def schema_matches_check_factor(
    schema: Mapping[str, PolarsDataType],
    assets_definition: AssetsDefinition,
    check_name: str | None = None,
    description: str | None = None,
    retry_policy: RetryPolicy | None = None,
) -> AssetChecksDefinition:
    """Create an asset check that compares observed columns against a schema."""
    # NOTE: checks that there is a part of the observed schema which matches the target schema

    @asset_check(
        asset=assets_definition,
        description=description,
        name=check_name,
        retry_policy=retry_policy,
    )
    def schema_matches_check(input_df: LazyFrame) -> AssetCheckResult:
        observed_schema = input_df.collect_schema()

        # find the columns in the required schema which are not found in the observed schema
        missing_declared_columns = [
            column for column in schema if column not in observed_schema
        ]
        # extract the portion of the target schema which have been observed
        declared_observed_schema = {
            column: observed_schema[column]
            for column in schema
            if column in observed_schema
        }

        try:
            assert_schema_equal(declared_observed_schema, schema)
            passed = True
            message = "passed"
        except AssertionError as e:
            message = str(e)
            passed = False

        return AssetCheckResult(
            passed=passed,
            check_name=check_name,
            severity=AssetCheckSeverity.WARN,
            metadata={
                "message": message,
                "missing_declared_columns": MetadataValue.json(
                    missing_declared_columns
                ),
            },
        )

    return schema_matches_check


def schema_drift_check_factory(
    schema: Mapping[str, PolarsDataType],
    assets_definition: AssetsDefinition,
    check_name: str | None = None,
    description: str | None = None,
    retry_policy: RetryPolicy | None = None,
) -> AssetChecksDefinition:
    """Create an asset check that warns about unexpected observed columns."""

    @asset_check(
        asset=assets_definition,
        description=description,
        name=check_name,
        retry_policy=retry_policy,
    )
    def schema_drift_check(input_df: LazyFrame) -> AssetCheckResult:
        observed_schema = input_df.collect_schema()
        unexpected_columns = [
            column for column in observed_schema if column not in schema
        ]

        passed = len(unexpected_columns) == 0

        if passed:
            message = "passed"
        else:
            message = (
                f"Unexpected columns found in observed schema: {unexpected_columns}"
            )

        return AssetCheckResult(
            passed=passed,
            check_name=check_name,
            severity=AssetCheckSeverity.WARN,
            metadata={
                "message": message,
                "unexpected_columns": MetadataValue.json(unexpected_columns),
                "declared_schema": MetadataValue.json(
                    {column: str(dtype) for column, dtype in schema.items()}
                ),
                "observed_schema": MetadataValue.json(
                    {column: str(dtype) for column, dtype in observed_schema.items()}
                ),
            },
        )

    return schema_drift_check
