"""Unit tests for source-table bronze current-state Delta helpers."""

import polars as pl
from dagster import MetadataValue
from pytest_mock import MockerFixture

from aemo_etl.factories.df_from_s3_keys.current_state import (
    CURRENT_STATE_DELTA_MERGE_OPTIONS,
    CURRENT_STATE_MERGE_UPDATE_PREDICATE,
    SOURCE_TABLE_BRONZE_SINK_DELTA_KWARGS,
    SourceTableBronzeWriteResult,
    source_table_bronze_materialization_metadata,
    write_source_table_current_state_batch,
)

_URI = "s3://aemo/bronze/gbb/bronze_table"


def test_write_source_table_current_state_batch_appends_when_table_missing(
    mocker: MockerFixture,
) -> None:
    batch = pl.LazyFrame({"surrogate_key": ["key"], "source_file": ["archive.csv"]})
    sink_delta = mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)
    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.current_state.table_exists",
        return_value=False,
    )

    result = write_source_table_current_state_batch(batch, target_table_uri=_URI)

    sink_delta.assert_called_once_with(_URI, mode="append")
    assert result == SourceTableBronzeWriteResult(
        row_count=1,
        target_exists_before_write=False,
        wrote_table=True,
        write_mode="append",
    )


def test_write_source_table_current_state_batch_merges_existing_table(
    mocker: MockerFixture,
) -> None:
    batch = pl.LazyFrame({"surrogate_key": ["key"], "source_file": ["archive.csv"]})
    merge_builder = mocker.MagicMock()
    merge_builder.when_matched_update_all.return_value = merge_builder
    merge_builder.when_not_matched_insert_all.return_value = merge_builder
    sink_delta = mocker.patch.object(
        pl.LazyFrame,
        "sink_delta",
        return_value=merge_builder,
    )
    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.current_state.table_exists",
        return_value=True,
    )
    logger = mocker.MagicMock()

    result = write_source_table_current_state_batch(
        batch,
        target_table_uri=_URI,
        logger=logger,
    )

    sink_delta.assert_called_once_with(
        _URI,
        mode="merge",
        delta_merge_options=CURRENT_STATE_DELTA_MERGE_OPTIONS,
    )
    merge_builder.when_matched_update_all.assert_called_once_with(
        predicate=CURRENT_STATE_MERGE_UPDATE_PREDICATE
    )
    merge_builder.when_not_matched_insert_all.assert_called_once_with()
    merge_builder.execute.assert_called_once_with()
    assert logger.info.call_count == 2
    assert result.write_mode == "merge"
    assert result.row_count == 1


def test_write_source_table_current_state_batch_skips_empty_existing_table(
    mocker: MockerFixture,
) -> None:
    batch = pl.LazyFrame(schema={"surrogate_key": pl.String, "source_file": pl.String})
    sink_delta = mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)
    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.current_state.table_exists",
        return_value=True,
    )

    result = write_source_table_current_state_batch(batch, target_table_uri=_URI)

    sink_delta.assert_not_called()
    assert result == SourceTableBronzeWriteResult(
        row_count=0,
        target_exists_before_write=True,
        wrote_table=False,
        write_mode="skip",
    )


def test_write_source_table_current_state_batch_replaces_existing_table(
    mocker: MockerFixture,
) -> None:
    batch = pl.LazyFrame({"surrogate_key": ["key"], "source_file": ["archive.csv"]})
    sink_delta = mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)

    result = write_source_table_current_state_batch(
        batch,
        target_table_uri=_URI,
        replace_existing=True,
    )

    sink_delta.assert_called_once_with(
        _URI,
        mode="overwrite",
        delta_write_options={"schema_mode": "overwrite"},
    )
    assert result.write_mode == "overwrite"
    assert result.row_count == 1


def test_source_table_bronze_materialization_metadata_preserves_sink_settings() -> None:
    metadata = source_table_bronze_materialization_metadata(
        SourceTableBronzeWriteResult(
            row_count=3,
            target_exists_before_write=True,
            wrote_table=True,
            write_mode="merge",
        )
    )

    assert metadata["sink_delta_kwargs"] == MetadataValue.json(
        SOURCE_TABLE_BRONZE_SINK_DELTA_KWARGS
    )
    assert metadata["dagster/row_count"] == 3
