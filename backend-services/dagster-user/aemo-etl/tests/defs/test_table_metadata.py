import json
from typing import cast

import polars as pl
import pytest
from dagster import TableColumn, TableSchema
from polars import LazyFrame

from aemo_etl.defs.table_metadata import (
    METADATA_KEYS,
    _safe_json,
    silver_table_metadata,
)

_SCHEMA = TableSchema(
    columns=[
        TableColumn(name="col_a", type="String", description="Column A"),
        TableColumn(name="col_b", type="Int64", description="Column B"),
    ]
)


# ---------------------------------------------------------------------------
# _safe_json
# ---------------------------------------------------------------------------


class TestSafeJson:
    def test_none_returns_none(self) -> None:
        assert _safe_json({}) is None

    def test_serialisable_values_are_preserved(self) -> None:
        d = {"key": "value", "num": 42, "lst": ["a", "b"]}
        result = json.loads(_safe_json(d))  # type: ignore[arg-type]
        assert result == d

    def test_non_serialisable_value_falls_back_to_str(self) -> None:
        class Unserializable:
            def __iter__(self) -> None:
                raise Exception("iteration banned")

            def __str__(self) -> str:
                return "sentinel"

        result = json.loads(_safe_json({"k": Unserializable()}))  # type: ignore[arg-type]
        assert result == {"k": "sentinel"}

    def test_mixed_serialisable_and_not(self) -> None:
        class Bad:
            def __str__(self) -> str:
                return "bad"

        result = json.loads(_safe_json({"good": "ok", "bad": Bad()}))  # type: ignore[arg-type]
        assert result == {"good": "ok", "bad": "bad"}

    def test_table_schema_serialised_to_structured_dict(self) -> None:
        result = json.loads(_safe_json({"dagster/column_schema": _SCHEMA}))  # type: ignore[arg-type]
        assert result == {
            "dagster/column_schema": {
                "col_a": {"type": "String", "description": "Column A"},
                "col_b": {"type": "Int64", "description": "Column B"},
            }
        }


# ---------------------------------------------------------------------------
# silver_table_metadata transformation
# ---------------------------------------------------------------------------


@pytest.fixture
def bronze_df() -> LazyFrame:
    """Minimal bronze-shaped LazyFrame with two assets."""
    metadata_with_all_keys = {
        "dagster/table_name": "aemo.gbb.bronze_foo",
        "dagster/uri": "s3://bucket/bronze/gbb/bronze_foo",
        "dagster/column_schema": _SCHEMA,
        "surrogate_key_sources": ["col_a", "col_b"],
        "cron_schedule": "*/15 * * * *",
        "cron_description": "Every 15 minutes",
    }
    metadata_partial = {
        "dagster/table_name": "aemo.gbb.silver_foo",
        "dagster/uri": "s3://bucket/silver/gbb/silver_foo",
    }
    return LazyFrame(
        {
            "asset_key_path": [
                ["bronze", "gbb", "bronze_foo"],
                ["silver", "gbb", "silver_foo"],
            ],
            "metadata": [
                _safe_json(metadata_with_all_keys),
                _safe_json(metadata_partial),
            ],
            "description": ["Bronze foo asset", "Silver foo asset"],
            "dependencies": [[["bronze", "gbb", "bronze_foo"]], []],
            "surrogate_key": ["sk1", "sk2"],
        },
        strict=False,
    )


class TestSilverTableMetadataTransformation:
    def _run(self, bronze_df: LazyFrame) -> pl.DataFrame:
        return cast(LazyFrame, silver_table_metadata(df=bronze_df)).collect()

    def test_metadata_column_is_dropped(self, bronze_df: LazyFrame) -> None:
        assert "metadata" not in self._run(bronze_df).columns

    def test_expected_columns_present(self, bronze_df: LazyFrame) -> None:
        result = self._run(bronze_df)
        for col_name in METADATA_KEYS.values():
            assert col_name in result.columns, f"missing column: {col_name}"
        assert "column_schema" in result.columns
        assert "column_description" in result.columns

    def test_string_values_extracted_correctly(self, bronze_df: LazyFrame) -> None:
        result = self._run(bronze_df)
        row = result.filter(
            pl.col("asset_key_path").list.join("__") == "bronze__gbb__bronze_foo"
        )
        assert row["dagster_table_name"][0] == "aemo.gbb.bronze_foo"
        assert row["dagster_uri"][0] == "s3://bucket/bronze/gbb/bronze_foo"
        assert row["cron_schedule"][0] == "*/15 * * * *"
        assert row["cron_description"][0] == "Every 15 minutes"

    def test_column_schema_extracted_as_type_dict(self, bronze_df: LazyFrame) -> None:
        result = self._run(bronze_df)
        row = result.filter(
            pl.col("asset_key_path").list.join("__") == "bronze__gbb__bronze_foo"
        )
        schema = json.loads(row["column_schema"][0])
        assert schema == {"col_a": "String", "col_b": "Int64"}

    def test_column_description_extracted_as_description_dict(
        self, bronze_df: LazyFrame
    ) -> None:
        result = self._run(bronze_df)
        row = result.filter(
            pl.col("asset_key_path").list.join("__") == "bronze__gbb__bronze_foo"
        )
        descriptions = json.loads(row["column_description"][0])
        assert descriptions == {"col_a": "Column A", "col_b": "Column B"}

    def test_list_values_serialised_to_json_string(self, bronze_df: LazyFrame) -> None:
        result = self._run(bronze_df)
        row = result.filter(
            pl.col("asset_key_path").list.join("__") == "bronze__gbb__bronze_foo"
        )
        sources = json.loads(row["surrogate_key_sources"][0])
        assert sources == ["col_a", "col_b"]

    def test_missing_keys_are_null(self, bronze_df: LazyFrame) -> None:
        result = self._run(bronze_df)
        row = result.filter(
            pl.col("asset_key_path").list.join("__") == "silver__gbb__silver_foo"
        )
        assert row["cron_schedule"][0] is None
        assert row["cron_description"][0] is None
        assert row["surrogate_key_sources"][0] is None
        assert row["column_schema"][0] is None
        assert row["column_description"][0] is None

    def test_non_metadata_columns_are_preserved(self, bronze_df: LazyFrame) -> None:
        result = self._run(bronze_df)
        for col in ("asset_key_path", "description", "dependencies", "surrogate_key"):
            assert col in result.columns

    def test_row_count_unchanged(self, bronze_df: LazyFrame) -> None:
        assert len(self._run(bronze_df)) == 2
