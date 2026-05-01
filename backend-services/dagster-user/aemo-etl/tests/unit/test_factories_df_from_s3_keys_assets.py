"""Unit tests for source-table bronze current-state helpers."""

import datetime as dt
from datetime import timezone

import polars as pl
from polars import Datetime, String

from aemo_etl.factories.df_from_s3_keys.assets import (
    SOURCE_CONTENT_HASH_COLUMN,
    add_source_content_hash,
    collapse_current_state_batch,
    source_content_hash_columns,
)

_AEST = dt.timezone(dt.timedelta(hours=10))
_UTC = timezone.utc


def test_source_content_hash_columns_exclude_ingestion_metadata() -> None:
    assert source_content_hash_columns(
        {
            "business_col": String,
            "ingested_timestamp": Datetime("us", time_zone="UTC"),
            "ingested_date": Datetime("us", time_zone="UTC"),
            "surrogate_key": String,
            "source_file": String,
            SOURCE_CONTENT_HASH_COLUMN: String,
        }
    ) == ["business_col"]


def test_source_content_hash_uses_declared_source_columns_only() -> None:
    df = pl.LazyFrame(
        {
            "business_col": ["same", "same", "changed"],
            "ingested_timestamp": [
                dt.datetime(2024, 1, 1, 10, tzinfo=_AEST),
                dt.datetime(2024, 1, 2, 10, tzinfo=_AEST),
                dt.datetime(2024, 1, 2, 10, tzinfo=_AEST),
            ],
            "ingested_date": [
                dt.datetime(2024, 1, 1, tzinfo=_UTC),
                dt.datetime(2024, 1, 2, tzinfo=_UTC),
                dt.datetime(2024, 1, 2, tzinfo=_UTC),
            ],
            "surrogate_key": ["old-key", "new-key", "new-key"],
            "source_file": [
                "s3://archive/old.csv",
                "s3://archive/new.csv",
                "s3://archive/new.csv",
            ],
        }
    )

    hashes = add_source_content_hash(df, ["business_col"]).collect()[
        SOURCE_CONTENT_HASH_COLUMN
    ]

    assert hashes[0] == hashes[1]
    assert hashes[1] != hashes[2]


def test_source_content_hash_handles_empty_source_column_selection() -> None:
    df = pl.LazyFrame({"surrogate_key": ["key-1"]})

    hashes = add_source_content_hash(df, []).collect()[SOURCE_CONTENT_HASH_COLUMN]

    assert hashes[0] is not None


def test_collapse_current_state_batch_keeps_max_source_file_per_surrogate_key() -> None:
    batch = pl.LazyFrame(
        {
            "business_col": ["older", "newer", "only"],
            "surrogate_key": ["hash1", "hash1", "hash2"],
            "source_file": [
                "s3://archive/table~20260421000000.parquet",
                "s3://archive/table~20260422000000.parquet",
                "s3://archive/table~20260420000000.parquet",
            ],
        }
    )

    result = collapse_current_state_batch(batch).sort("surrogate_key").collect()

    assert result["business_col"].to_list() == ["newer", "only"]
