"""Unit tests for defs/raw/table_metadata.py."""

import json

import polars as pl
from dagster import AssetKey, Definitions, TableColumn, TableSchema
from pytest_mock import MockerFixture

from aemo_etl.defs.raw.table_metadata import (
    _safe_json,
    _silver_extract,
    _silver_extract_column_schema_field,
    bronze_table_metadata,
    defs,
    silver_table_metadata,
)


# ---------------------------------------------------------------------------
# _safe_json
# ---------------------------------------------------------------------------


def test_safe_json_empty_dict() -> None:
    assert _safe_json({}) is None


def test_safe_json_table_schema() -> None:
    schema = TableSchema(columns=[TableColumn("col1", "String", description="a col")])
    result = _safe_json({"dagster/column_schema": schema})
    assert result is not None
    parsed = json.loads(result)
    assert "dagster/column_schema" in parsed
    assert "col1" in parsed["dagster/column_schema"]
    assert parsed["dagster/column_schema"]["col1"]["type"] == "String"


def test_safe_json_serializable_value() -> None:
    result = _safe_json({"key": "value", "num": 42})
    assert result is not None
    parsed = json.loads(result)
    assert parsed["key"] == "value"
    assert parsed["num"] == 42


def test_safe_json_non_serializable_value() -> None:
    class _Unserializable:
        def __repr__(self) -> str:
            return "unserializable_obj"

    result = _safe_json({"key": _Unserializable()})
    assert result is not None
    parsed = json.loads(result)
    assert "key" in parsed  # stored as str fallback


# ---------------------------------------------------------------------------
# bronze_table_metadata
# ---------------------------------------------------------------------------


def test_bronze_table_metadata(mocker: MockerFixture) -> None:
    """Call bronze_table_metadata with a mocked repository context."""
    mock_key1 = AssetKey(["bronze", "gbb", "test_asset"])
    mock_key2 = AssetKey(["silver", "meta", "test"])

    # mock_def1 has all optional attributes
    mock_def1 = mocker.MagicMock()
    mock_def1.metadata_by_key.get.return_value = {"glob_pattern": "*.csv"}
    mock_def1.descriptions_by_key.get.return_value = "A test asset"
    mock_def1.asset_deps = {mock_key1: None}

    # mock_def2 has no optional attributes (tests the hasattr branches)
    mock_def2 = object()

    asset_key_dict = {mock_key1: mock_def1, mock_key2: mock_def2}

    ctx = mocker.MagicMock()
    ctx.log = mocker.MagicMock()
    ctx.repository_def.assets_defs_by_key = asset_key_dict

    fn = bronze_table_metadata.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = fn(ctx)
    assert isinstance(result, pl.LazyFrame)
    collected = result.collect()
    assert len(collected) == 2
    assert "asset_key_path" in collected.columns
    assert "surrogate_key" in collected.columns


# ---------------------------------------------------------------------------
# silver_table_metadata
# ---------------------------------------------------------------------------


def _make_bronze_df() -> pl.LazyFrame:
    """Build a minimal bronze LazyFrame for silver_table_metadata input."""
    schema_dict = {
        "dagster/column_schema": {"col1": {"type": "String", "description": "desc"}},
        "dagster/table_name": "test.table",
        "dagster/uri": "s3://bucket/table",
        "surrogate_key_sources": ["col1"],
        "cron_schedule": "0 * * * *",
        "cron_description": "Every hour",
    }
    return pl.LazyFrame(
        {
            "asset_key_path": [["bronze", "gbb", "test"]],
            "metadata": [json.dumps(schema_dict)],
            "description": ["test description"],
            "dependencies": [[["dep1"]]],
            "surrogate_key": ["hash1"],
        }
    )


def test_silver_table_metadata() -> None:
    df = _make_bronze_df()
    fn = silver_table_metadata.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = fn(df)
    assert isinstance(result, pl.LazyFrame)
    collected = result.collect()
    assert "column_schema" in collected.columns
    assert "column_description" in collected.columns
    assert "dagster_table_name" in collected.columns


def test_silver_table_metadata_none_metadata() -> None:
    """Handles rows where metadata is None."""
    df = pl.LazyFrame(
        {
            "asset_key_path": [["bronze", "test"]],
            "metadata": [None],
            "description": ["desc"],
            "dependencies": [[]],
            "surrogate_key": ["hash1"],
        }
    )
    fn = silver_table_metadata.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = fn(df)
    assert isinstance(result, pl.LazyFrame)


def test_silver_table_metadata_missing_keys() -> None:
    """Metadata exists but missing expected sub-keys."""
    metadata_no_keys = json.dumps({"other_key": "other_val"})
    metadata_empty_schema = json.dumps({"dagster/column_schema": None})
    df = pl.LazyFrame(
        {
            "asset_key_path": [["bronze", "test1"], ["bronze", "test2"]],
            "metadata": [metadata_no_keys, metadata_empty_schema],
            "description": ["desc1", "desc2"],
            "dependencies": [[], []],
            "surrogate_key": ["hash1", "hash2"],
        }
    )
    fn = silver_table_metadata.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = fn(df)
    assert isinstance(result, pl.LazyFrame)
    collected = result.collect()
    assert len(collected) == 2


def test_silver_table_metadata_waits_for_upstream_dependency() -> None:
    condition = silver_table_metadata.automation_conditions_by_key[
        silver_table_metadata.key
    ]
    assert "any_deps_missing" in repr(condition)


# ---------------------------------------------------------------------------
# _silver_extract (module-level, directly testable)
# ---------------------------------------------------------------------------


def test_silver_extract_none_raw() -> None:
    assert _silver_extract(None, "key") is None


def test_silver_extract_key_missing() -> None:
    raw = json.dumps({"other": "val"})
    assert _silver_extract(raw, "missing_key") is None


def test_silver_extract_str_value() -> None:
    raw = json.dumps({"key": "string_val"})
    assert _silver_extract(raw, "key") == "string_val"


def test_silver_extract_non_str_value() -> None:
    raw = json.dumps({"key": ["a", "b"]})
    result = _silver_extract(raw, "key")
    assert result is not None
    assert json.loads(result) == ["a", "b"]


# ---------------------------------------------------------------------------
# _silver_extract_column_schema_field (module-level, directly testable)
# ---------------------------------------------------------------------------


def test_silver_extract_column_schema_field_none_raw() -> None:
    assert _silver_extract_column_schema_field(None, "type") is None


def test_silver_extract_column_schema_field_no_schema() -> None:
    raw = json.dumps({"no_schema": True})
    assert _silver_extract_column_schema_field(raw, "type") is None


def test_silver_extract_column_schema_field_empty_schema() -> None:
    raw = json.dumps({"dagster/column_schema": None})
    assert _silver_extract_column_schema_field(raw, "type") is None


def test_silver_extract_column_schema_field_with_schema() -> None:
    raw = json.dumps(
        {"dagster/column_schema": {"col1": {"type": "String", "description": "d1"}}}
    )
    result = _silver_extract_column_schema_field(raw, "type")
    assert result is not None
    parsed = json.loads(result)
    assert parsed["col1"] == "String"


# ---------------------------------------------------------------------------
# defs()
# ---------------------------------------------------------------------------


def test_defs_returns_definitions() -> None:
    d = defs()
    assert isinstance(d, Definitions)
