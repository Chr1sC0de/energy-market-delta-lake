"""Component tests for source-table current-state Delta merge behavior."""

from pathlib import Path

import polars as pl
import pytest

from aemo_etl.factories.df_from_s3_keys.current_state import (
    collapse_current_state_batch,
    write_source_table_current_state_batch,
)


@pytest.mark.component
def test_multi_file_current_state_batch_merges_into_existing_delta_target(
    tmp_path: Path,
) -> None:
    target_uri = str(tmp_path / "bronze_current_state")
    pl.LazyFrame(
        {
            "surrogate_key": ["key-a"],
            "source_file": ["s3://archive/table~20260520000000.parquet"],
            "source_content_hash": ["old-hash"],
            "business_value": ["old"],
        }
    ).sink_delta(target_uri, mode="append")
    staged = pl.LazyFrame(
        {
            "surrogate_key": ["key-a", "key-a", "key-b"],
            "source_file": [
                "s3://archive/table~20260520000000.parquet",
                "s3://archive/table~20260521000000.parquet",
                "s3://archive/table~20260521000000.parquet",
            ],
            "source_content_hash": ["old-hash", "new-hash", "insert-hash"],
            "business_value": ["old", "new", "insert"],
        }
    )

    batch = collapse_current_state_batch(staged)
    result = write_source_table_current_state_batch(
        batch,
        target_table_uri=target_uri,
    )

    merged = pl.scan_delta(target_uri).sort("surrogate_key").collect()
    assert result.write_mode == "merge"
    assert result.row_count == 2
    assert merged["surrogate_key"].to_list() == ["key-a", "key-b"]
    assert merged["business_value"].to_list() == ["new", "insert"]
