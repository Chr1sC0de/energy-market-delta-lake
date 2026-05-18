"""Unit tests for source-table bronze current-state helpers."""

import datetime as dt
from datetime import timezone
from io import BytesIO

import polars as pl
from polars import Datetime, String
import pytest

from aemo_etl.factories.df_from_s3_keys.assets import (
    SOURCE_CONTENT_HASH_COLUMN,
    add_source_content_hash,
    source_table_bronze_frame_from_bytes,
    source_content_hash_columns,
)
from aemo_etl.factories.df_from_s3_keys.current_state import (
    collapse_current_state_batch,
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


def test_source_table_bronze_frame_from_bytes_stores_archive_source_file() -> None:
    df = source_table_bronze_frame_from_bytes(
        s3_bucket="landing",
        s3_key="bronze/gbb/table.csv",
        object_bytes=b"business_col\nvalue\n",
        schema={
            "business_col": String,
            "ingested_timestamp": Datetime("us", time_zone="UTC"),
            "ingested_date": Datetime("us", time_zone="UTC"),
            "surrogate_key": String,
            "source_file": String,
            SOURCE_CONTENT_HASH_COLUMN: String,
        },
        surrogate_key_sources=("business_col",),
        current_time=dt.datetime(2024, 1, 1, tzinfo=_AEST),
        source_file_bucket="archive",
    )

    result = df.collect()

    assert result["source_file"].to_list() == ["s3://archive/bronze/gbb/table.csv"]


def test_source_table_bronze_frame_from_bytes_parses_parquet() -> None:
    buffer = BytesIO()
    pl.DataFrame({"business_col": ["value"]}).write_parquet(buffer)

    df = source_table_bronze_frame_from_bytes(
        s3_bucket="landing",
        s3_key="bronze/gbb/table.parquet",
        object_bytes=buffer.getvalue(),
        schema={
            "business_col": String,
            "ingested_timestamp": Datetime("us", time_zone="UTC"),
            "ingested_date": Datetime("us", time_zone="UTC"),
            "surrogate_key": String,
            "source_file": String,
            SOURCE_CONTENT_HASH_COLUMN: String,
        },
        surrogate_key_sources=("business_col",),
        current_time=dt.datetime(2024, 1, 1, tzinfo=_AEST),
        source_file_bucket="archive",
    )

    result = df.collect()

    assert result["business_col"].to_list() == ["value"]
    assert result["surrogate_key"].null_count() == 0


def test_source_table_bronze_frame_from_bytes_parses_headerless_csv() -> None:
    df = source_table_bronze_frame_from_bytes(
        s3_bucket="landing",
        s3_key="bronze/sttm/int659_v1_bid_offer_rpt_1~260517013317.csv",
        object_bytes=(b"2026-05-15,68602,3121782,9\n2026-05-15,68602,3121782,10\n"),
        schema={
            "gas_date": String,
            "schedule_identifier": String,
            "bid_offer_identifier": String,
            "bid_offer_step_number": String,
            "ingested_timestamp": Datetime("us", time_zone="UTC"),
            "ingested_date": Datetime("us", time_zone="UTC"),
            "surrogate_key": String,
            "source_file": String,
            SOURCE_CONTENT_HASH_COLUMN: String,
        },
        surrogate_key_sources=(
            "gas_date",
            "schedule_identifier",
            "bid_offer_identifier",
            "bid_offer_step_number",
        ),
        current_time=dt.datetime(2024, 1, 1, tzinfo=_AEST),
        source_file_bucket="archive",
    )

    result = df.collect()

    assert result["gas_date"].to_list() == ["2026-05-15", "2026-05-15"]
    assert result["bid_offer_step_number"].to_list() == ["9", "10"]
    assert result["surrogate_key"].null_count() == 0


def test_source_table_bronze_frame_from_bytes_drops_nul_csv_lines() -> None:
    df = source_table_bronze_frame_from_bytes(
        s3_bucket="landing",
        s3_key="bronze/sttm/int659_v1_bid_offer_rpt_1~260517013317.csv",
        object_bytes=(
            b"\0partial,3121782,9\n"
            b"2026-05-15,68602,3121782,9\n"
            b"2026-05-16,68603\0,3121783,10\n"
            b"2026-05-17,68604,3121784,1\n"
        ),
        schema={
            "gas_date": String,
            "schedule_identifier": String,
            "bid_offer_identifier": String,
            "bid_offer_step_number": String,
            "ingested_timestamp": Datetime("us", time_zone="UTC"),
            "ingested_date": Datetime("us", time_zone="UTC"),
            "surrogate_key": String,
            "source_file": String,
            SOURCE_CONTENT_HASH_COLUMN: String,
        },
        surrogate_key_sources=(
            "gas_date",
            "schedule_identifier",
            "bid_offer_identifier",
            "bid_offer_step_number",
        ),
        current_time=dt.datetime(2024, 1, 1, tzinfo=_AEST),
        source_file_bucket="archive",
    )

    result = df.collect()

    assert result["gas_date"].to_list() == ["2026-05-15", "2026-05-17"]
    assert result["bid_offer_identifier"].to_list() == ["3121782", "3121784"]


def test_source_table_bronze_frame_from_bytes_tolerates_missing_surrogate_sources() -> (
    None
):
    df = source_table_bronze_frame_from_bytes(
        s3_bucket="landing",
        s3_key="bronze/sttm/int659_v1_bid_offer_rpt_1~260517013317.csv",
        object_bytes=b"\0" * 32,
        schema={
            "gas_date": String,
            "ingested_timestamp": Datetime("us", time_zone="UTC"),
            "ingested_date": Datetime("us", time_zone="UTC"),
            "surrogate_key": String,
            "source_file": String,
            SOURCE_CONTENT_HASH_COLUMN: String,
        },
        surrogate_key_sources=("gas_date",),
        current_time=dt.datetime(2024, 1, 1, tzinfo=_AEST),
        source_file_bucket="archive",
    )

    result = df.collect()

    assert result.height == 0
    assert result.columns[:6] == [
        "gas_date",
        "ingested_timestamp",
        "ingested_date",
        "surrogate_key",
        "source_file",
        SOURCE_CONTENT_HASH_COLUMN,
    ]


def test_source_table_bronze_frame_from_bytes_rejects_nonempty_missing_surrogate_source() -> (
    None
):
    with pytest.raises(ValueError, match="missing from non-empty source frame"):
        source_table_bronze_frame_from_bytes(
            s3_bucket="landing",
            s3_key="bronze/gbb/table.csv",
            object_bytes=b"other_col\nvalue\n",
            schema={
                "gas_date": String,
                "other_col": String,
                "ingested_timestamp": Datetime("us", time_zone="UTC"),
                "ingested_date": Datetime("us", time_zone="UTC"),
                "surrogate_key": String,
                "source_file": String,
                SOURCE_CONTENT_HASH_COLUMN: String,
            },
            surrogate_key_sources=("gas_date",),
            current_time=dt.datetime(2024, 1, 1, tzinfo=_AEST),
            source_file_bucket="archive",
        )


def test_source_table_bronze_frame_from_bytes_rejects_undeclared_surrogate_source() -> (
    None
):
    with pytest.raises(KeyError, match="surrogate_key_sources must be declared"):
        source_table_bronze_frame_from_bytes(
            s3_bucket="landing",
            s3_key="bronze/gbb/table.csv",
            object_bytes=b"other_col\nvalue\n",
            schema={
                "other_col": String,
                "ingested_timestamp": Datetime("us", time_zone="UTC"),
                "ingested_date": Datetime("us", time_zone="UTC"),
                "surrogate_key": String,
                "source_file": String,
                SOURCE_CONTENT_HASH_COLUMN: String,
            },
            surrogate_key_sources=("business_col",),
            current_time=dt.datetime(2024, 1, 1, tzinfo=_AEST),
            source_file_bucket="archive",
        )


def test_source_table_bronze_frame_from_bytes_rejects_unknown_filetype() -> None:
    with pytest.raises(ValueError, match="not supported"):
        source_table_bronze_frame_from_bytes(
            s3_bucket="landing",
            s3_key="bronze/gbb/table.txt",
            object_bytes=b"ignored",
            schema={},
            surrogate_key_sources=(),
            current_time=dt.datetime(2024, 1, 1, tzinfo=_AEST),
        )
