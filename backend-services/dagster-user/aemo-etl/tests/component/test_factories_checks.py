from functools import partial

import polars as pl
import pytest
from dagster import AssetsDefinition, asset
from dagster import RetryPolicy

from aemo_etl.factories.checks import (
    default_check_fn,
    duplicate_row_check_factory,
    get_unique_rows,
    get_unique_rows_from_primary_key,
    schema_drift_check_factory,
    schema_matches_check_factor,
)
from aemo_etl.models._asset_check_kwargs import AssetChecksKwargs


_DF_NO_DUPS = pl.LazyFrame({"surrogate_key": ["a", "b", "c"]})
_DF_WITH_DUPS = pl.LazyFrame({"surrogate_key": ["a", "a", "b"]})


def test_get_unique_rows_from_primary_key_no_dups() -> None:
    assert get_unique_rows_from_primary_key(_DF_NO_DUPS, "surrogate_key") == 3


def test_get_unique_rows_from_primary_key_with_dups() -> None:
    assert get_unique_rows_from_primary_key(_DF_WITH_DUPS, "surrogate_key") == 2


def test_get_unique_rows_no_dups() -> None:
    assert get_unique_rows(_DF_NO_DUPS) == 3


def test_get_unique_rows_with_dups() -> None:
    assert get_unique_rows(_DF_WITH_DUPS) == 2


def test_default_check_fn_passing() -> None:
    row_count_fn = partial(
        get_unique_rows_from_primary_key, primary_key="surrogate_key"
    )
    assert default_check_fn(_DF_NO_DUPS, row_count_fn=row_count_fn) is True


def test_default_check_fn_failing() -> None:
    row_count_fn = partial(
        get_unique_rows_from_primary_key, primary_key="surrogate_key"
    )
    assert default_check_fn(_DF_WITH_DUPS, row_count_fn=row_count_fn) is False


@pytest.fixture()
def _minimal_asset() -> AssetsDefinition:
    """A minimal stand-in for AssetsDefinition."""

    @asset(name="test_check_asset")
    def _a() -> None:
        pass

    return _a  # type: ignore[return-value]


def test_duplicate_row_check_factory_with_primary_key(
    _minimal_asset: AssetsDefinition,
) -> None:
    check = duplicate_row_check_factory(
        assets_definition=_minimal_asset,
        check_name="dup_check",
        primary_key="surrogate_key",
        description="test",
    )
    assert check is not None
    result = check.op.compute_fn.decorated_fn(_DF_NO_DUPS)  # type: ignore[union-attr]
    assert result.passed is True


def test_duplicate_row_check_factory_with_primary_key_failure_metadata(
    _minimal_asset: AssetsDefinition,
) -> None:
    check = duplicate_row_check_factory(
        assets_definition=_minimal_asset,
        check_name="dup_check_pk_failure",
        primary_key="surrogate_key",
        description="test",
    )

    result = check.op.compute_fn.decorated_fn(_DF_WITH_DUPS)  # type: ignore[union-attr]

    assert result.passed is False
    assert result.metadata is not None


def test_duplicate_row_check_factory_no_primary_key(
    _minimal_asset: AssetsDefinition,
) -> None:
    check = duplicate_row_check_factory(
        assets_definition=_minimal_asset,
        check_name="dup_check_no_pk",
    )
    assert check is not None
    result = check.op.compute_fn.decorated_fn(_DF_WITH_DUPS)  # type: ignore[union-attr]
    assert result.passed is False


def test_duplicate_row_check_factory_custom_check_fn(
    _minimal_asset: AssetsDefinition,
) -> None:
    def always_true(df: pl.LazyFrame) -> bool:
        return True

    check = duplicate_row_check_factory(
        assets_definition=_minimal_asset,
        check_name="custom_check",
        check_fn=always_true,
    )
    assert check is not None
    result = check.op.compute_fn.decorated_fn(_DF_WITH_DUPS)  # type: ignore[union-attr]
    assert result.passed is True


def test_duplicate_row_check_factory_with_primary_key_list(
    _minimal_asset: AssetsDefinition,
) -> None:
    check = duplicate_row_check_factory(
        assets_definition=_minimal_asset,
        check_name="dup_check_pk_list",
        primary_key=["surrogate_key", "value"],
    )

    result = check.op.compute_fn.decorated_fn(  # type: ignore[union-attr]
        pl.LazyFrame(
            {
                "surrogate_key": ["a", "a", "a"],
                "value": [1, 1, 2],
            }
        )
    )

    assert result.passed is False
    assert result.metadata is not None


def test_schema_matches_check_factor_ignores_unexpected_columns(
    _minimal_asset: AssetsDefinition,
) -> None:
    check = schema_matches_check_factor(
        assets_definition=_minimal_asset,
        check_name="schema_matches",
        schema={"surrogate_key": pl.String},
    )

    result = check.op.compute_fn.decorated_fn(  # type: ignore[union-attr]
        pl.LazyFrame({"surrogate_key": ["a"], "extra_column": ["x"]})
    )

    assert result.passed is True


def test_schema_matches_check_factor_fails_for_missing_declared_columns(
    _minimal_asset: AssetsDefinition,
) -> None:
    check = schema_matches_check_factor(
        assets_definition=_minimal_asset,
        check_name="schema_matches_fail",
        schema={"surrogate_key": pl.String, "required_column": pl.Int64},
    )

    result = check.op.compute_fn.decorated_fn(  # type: ignore[union-attr]
        pl.LazyFrame({"surrogate_key": ["a"]})
    )

    assert result.passed is False
    assert result.metadata is not None


def test_schema_drift_check_factory_reports_unexpected_columns(
    _minimal_asset: AssetsDefinition,
) -> None:
    check = schema_drift_check_factory(
        assets_definition=_minimal_asset,
        check_name="schema_drift",
        schema={"surrogate_key": pl.String},
    )

    result = check.op.compute_fn.decorated_fn(  # type: ignore[union-attr]
        pl.LazyFrame({"surrogate_key": ["a"], "extra_column": ["x"]})
    )

    assert result.passed is False
    assert result.metadata is not None


def test_schema_drift_check_factory_passes_without_unexpected_columns(
    _minimal_asset: AssetsDefinition,
) -> None:
    check = schema_drift_check_factory(
        assets_definition=_minimal_asset,
        check_name="schema_drift_pass",
        schema={"surrogate_key": pl.String},
    )

    result = check.op.compute_fn.decorated_fn(  # type: ignore[union-attr]
        pl.LazyFrame({"surrogate_key": ["a"]})
    )

    assert result.passed is True


def test_asset_checks_kwargs_typed_dict_instantiation() -> None:
    kwargs: AssetChecksKwargs = {
        "name": "check_name",
        "description": "description",
        "blocking": False,
        "retry_policy": RetryPolicy(max_retries=1),
        "metadata": {"key": "value"},
        "required_resource_keys": {"resource_a"},
    }

    assert kwargs["name"] == "check_name"
