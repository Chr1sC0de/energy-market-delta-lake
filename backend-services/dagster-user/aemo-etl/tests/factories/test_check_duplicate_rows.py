from unittest.mock import Mock

import dagster as dg
import polars as pl

from aemo_etl.factories.checks.check_duplicate_rows import (
    default_check_fn,
    duplicate_row_check_factory,
    get_unique_rows,
    get_unique_rows_from_primary_key,
)


def test_get_unique_rows_from_primary_key_single_column() -> None:
    df = pl.LazyFrame({"id": [1, 2, 2, 3], "value": [10, 20, 30, 40]})

    result = get_unique_rows_from_primary_key(df, "id")

    assert result == 3


def test_get_unique_rows_from_primary_key_multiple_columns() -> None:
    df = pl.LazyFrame(
        {"id": [1, 2, 2, 3], "name": ["a", "b", "b", "c"], "value": [10, 20, 30, 40]}
    )

    result = get_unique_rows_from_primary_key(df, ["id", "name"])

    assert result == 3


def test_get_unique_rows() -> None:
    df = pl.LazyFrame({"id": [1, 2, 2, 3], "value": [10, 20, 20, 40]})

    result = get_unique_rows(df)

    assert result == 3


def test_default_check_fn_no_duplicates() -> None:
    df = pl.LazyFrame({"id": [1, 2, 3], "value": [10, 20, 30]})

    result = default_check_fn(df, row_count_fn=get_unique_rows)

    assert result is True


def test_default_check_fn_with_duplicates() -> None:
    df = pl.LazyFrame({"id": [1, 2, 2], "value": [10, 20, 20]})

    result = default_check_fn(df, row_count_fn=get_unique_rows)

    assert result is False


def test_duplicate_row_check_factory_with_primary_key() -> None:
    mock_asset = Mock(spec=dg.AssetsDefinition)
    mock_asset.key = dg.AssetKey("test_asset")

    check_def = duplicate_row_check_factory(
        assets_definition=mock_asset,
        check_name="test_check",
        primary_key="id",
    )

    assert isinstance(check_def, dg.AssetChecksDefinition)


def test_duplicate_row_check_factory_without_primary_key() -> None:
    mock_asset = Mock(spec=dg.AssetsDefinition)
    mock_asset.key = dg.AssetKey("test_asset")

    check_def = duplicate_row_check_factory(
        assets_definition=mock_asset,
        check_name="test_check",
        primary_key=None,
    )

    assert isinstance(check_def, dg.AssetChecksDefinition)


def test_duplicate_row_check_factory_with_custom_check_fn() -> None:
    mock_asset = Mock(spec=dg.AssetsDefinition)
    mock_asset.key = dg.AssetKey("test_asset")

    custom_check = Mock(return_value=True)

    check_def = duplicate_row_check_factory(
        assets_definition=mock_asset,
        check_name="custom_check",
        check_fn=custom_check,
    )

    assert isinstance(check_def, dg.AssetChecksDefinition)


def test_duplicate_row_check_execution_passed() -> None:
    mock_asset = Mock(spec=dg.AssetsDefinition)
    mock_asset.key = dg.AssetKey("test_asset")

    check_def = duplicate_row_check_factory(
        assets_definition=mock_asset,
        check_name="test_check",
        primary_key="id",
    )

    df = pl.LazyFrame({"id": [1, 2, 3], "value": [10, 20, 30]})

    result = check_def.node_def.compute_fn.decorated_fn(input_df=df)  # type: ignore[attr-defined]

    assert isinstance(result, dg.AssetCheckResult)
    assert result.passed is True
    assert result.check_name == "test_check"


def test_duplicate_row_check_execution_failed() -> None:
    mock_asset = Mock(spec=dg.AssetsDefinition)
    mock_asset.key = dg.AssetKey("test_asset")

    check_def = duplicate_row_check_factory(
        assets_definition=mock_asset,
        check_name="test_check",
        primary_key="id",
    )

    df = pl.LazyFrame({"id": [1, 2, 2, 3], "value": [10, 20, 30, 40]})

    result = check_def.node_def.compute_fn.decorated_fn(input_df=df)  # type: ignore[attr-defined]

    assert isinstance(result, dg.AssetCheckResult)
    assert result.passed is False
    assert result.check_name == "test_check"
