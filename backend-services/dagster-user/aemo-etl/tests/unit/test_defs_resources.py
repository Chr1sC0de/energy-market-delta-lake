"""Unit tests for defs/resources.py IO managers."""

from typing import Any
from unittest.mock import MagicMock

import polars as pl
from dagster import Definitions
from pytest_mock import MockerFixture

from aemo_etl.configs import DAGSTER_URI
from aemo_etl.defs.resources import (
    PolarsDataFrameSinkDeltaIoManager,
    PolarsDataFrameSinkParquetIoManager,
    _parquet_dataset_glob,
    defs,
)

_URI = "s3://test-bucket/table"
_SMALL_DF = pl.LazyFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})


def _make_output_context(
    mocker: MockerFixture,
    uri: str = _URI,
    definition_metadata: dict[str, Any] | None = None,
) -> MagicMock:
    ctx: MagicMock = mocker.MagicMock()
    ctx.metadata = {DAGSTER_URI: uri}
    ctx.definition_metadata = {DAGSTER_URI: uri, **(definition_metadata or {})}
    ctx.log = mocker.MagicMock()
    return ctx


def _make_input_context(mocker: MockerFixture, uri: str = _URI) -> MagicMock:
    ctx: MagicMock = mocker.MagicMock()
    ctx.upstream_output = mocker.MagicMock()
    ctx.upstream_output.metadata = {DAGSTER_URI: uri}
    ctx.upstream_output.definition_metadata = {DAGSTER_URI: uri}
    return ctx


# ---------------------------------------------------------------------------
# handle_output
# ---------------------------------------------------------------------------


def test_handle_output_append_auto_schema(mocker: MockerFixture) -> None:
    """Append mode, no pre-defined column schema → schema is auto-generated."""
    io_mgr = PolarsDataFrameSinkDeltaIoManager(sink_delta_kwargs={"mode": "append"})
    ctx = _make_output_context(mocker, definition_metadata={})
    mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)

    io_mgr.handle_output(ctx, _SMALL_DF)
    ctx.add_output_metadata.assert_called_once()
    added = ctx.add_output_metadata.call_args[0][0]
    assert "preview" in added
    assert "dagster/column_schema" in added


def test_handle_output_with_column_schema_in_def_metadata(
    mocker: MockerFixture,
) -> None:
    """If dagster/column_schema is already in definition_metadata, skip auto-gen."""
    io_mgr = PolarsDataFrameSinkDeltaIoManager(sink_delta_kwargs={"mode": "append"})
    ctx = _make_output_context(
        mocker,
        definition_metadata={"dagster/column_schema": "pre-defined"},
    )
    mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)

    io_mgr.handle_output(ctx, _SMALL_DF)
    added = ctx.add_output_metadata.call_args[0][0]
    # dagster/column_schema should NOT be in added metadata
    assert "dagster/column_schema" not in added


def test_handle_output_with_column_description(mocker: MockerFixture) -> None:
    """column_description in definition_metadata → use it for schema generation."""
    io_mgr = PolarsDataFrameSinkDeltaIoManager(sink_delta_kwargs={"mode": "append"})
    ctx = _make_output_context(
        mocker,
        definition_metadata={"column_description": {"a": "col a desc"}},
    )
    mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)

    io_mgr.handle_output(ctx, _SMALL_DF)
    added = ctx.add_output_metadata.call_args[0][0]
    assert "dagster/column_schema" in added


def test_handle_output_builds_metadata_before_sink_delta(
    mocker: MockerFixture,
) -> None:
    """Collect output metadata before sink_delta consumes the LazyFrame plan."""
    io_mgr = PolarsDataFrameSinkDeltaIoManager(sink_delta_kwargs={"mode": "append"})
    ctx = _make_output_context(
        mocker,
        definition_metadata={"dagster/column_schema": "pre-defined"},
    )
    events: list[str] = []

    def _get_lazyframe_num_rows(_: pl.LazyFrame) -> int:
        events.append("row_count")
        return 3

    def _sink_delta(_: pl.LazyFrame, *_args: object, **_kwargs: object) -> None:
        events.append("sink_delta")

    mocker.patch(
        "aemo_etl.defs.resources.get_lazyframe_num_rows", _get_lazyframe_num_rows
    )
    mocker.patch.object(pl.LazyFrame, "sink_delta", _sink_delta)

    io_mgr.handle_output(ctx, _SMALL_DF)

    assert events == ["row_count", "sink_delta"]


def test_handle_output_merge_mode(mocker: MockerFixture) -> None:
    """Merge mode calls when_matched_update_all chain."""
    io_mgr = PolarsDataFrameSinkDeltaIoManager(sink_delta_kwargs={"mode": "merge"})
    ctx = _make_output_context(mocker)
    merge_builder = mocker.MagicMock()
    merge_builder.when_matched_update_all.return_value = merge_builder
    merge_builder.when_not_matched_insert_all.return_value = merge_builder
    mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=merge_builder)

    io_mgr.handle_output(ctx, _SMALL_DF)
    merge_builder.when_matched_update_all.assert_called_once()
    merge_builder.when_not_matched_insert_all.assert_called_once()
    merge_builder.execute.assert_called_once()


# ---------------------------------------------------------------------------
# load_input
# ---------------------------------------------------------------------------


def test_load_input(mocker: MockerFixture) -> None:
    io_mgr = PolarsDataFrameSinkDeltaIoManager()
    ctx = _make_input_context(mocker)
    mock_lf = pl.LazyFrame({"a": [1]})
    mocker.patch(
        "aemo_etl.defs.resources.scan_delta",
        return_value=mock_lf,
    )
    result = io_mgr.load_input(ctx)
    assert isinstance(result, pl.LazyFrame)


def test_parquet_dataset_glob() -> None:
    assert (
        _parquet_dataset_glob("s3://test-bucket/table")
        == "s3://test-bucket/table/*.parquet"
    )
    assert _parquet_dataset_glob("/tmp/test-table/") == "/tmp/test-table/*.parquet"


def test_handle_output_parquet_builds_metadata_before_write(
    mocker: MockerFixture,
) -> None:
    io_mgr = PolarsDataFrameSinkParquetIoManager()
    ctx = _make_output_context(
        mocker,
        definition_metadata={"dagster/column_schema": "pre-defined"},
    )
    events: list[str] = []

    def _get_lazyframe_num_rows(_: pl.LazyFrame) -> int:
        events.append("row_count")
        return 3

    def _sink_parquet(_: pl.LazyFrame, *_args: object, **_kwargs: object) -> None:
        events.append("sink_parquet")

    mocker.patch(
        "aemo_etl.defs.resources.get_lazyframe_num_rows", _get_lazyframe_num_rows
    )
    mocker.patch.object(pl.LazyFrame, "sink_parquet", _sink_parquet)

    io_mgr.handle_output(ctx, _SMALL_DF)

    assert events == ["row_count", "sink_parquet"]


def test_handle_output_parquet_auto_schema(mocker: MockerFixture) -> None:
    io_mgr = PolarsDataFrameSinkParquetIoManager()
    ctx = _make_output_context(mocker, definition_metadata={})
    sink_parquet = mocker.patch.object(pl.LazyFrame, "sink_parquet", return_value=None)

    io_mgr.handle_output(ctx, _SMALL_DF)

    sink_parquet.assert_called_once_with(
        "s3://test-bucket/table/part-00000.parquet", mkdir=True
    )
    added = ctx.add_output_metadata.call_args[0][0]
    assert "preview" in added
    assert "dagster/column_schema" in added
    assert "dagster/row_count" in added


def test_handle_output_parquet_with_column_description(
    mocker: MockerFixture,
) -> None:
    io_mgr = PolarsDataFrameSinkParquetIoManager()
    ctx = _make_output_context(
        mocker,
        definition_metadata={"column_description": {"a": "col a desc"}},
    )
    mocker.patch.object(pl.LazyFrame, "sink_parquet", return_value=None)

    io_mgr.handle_output(ctx, _SMALL_DF)

    added = ctx.add_output_metadata.call_args[0][0]
    assert "dagster/column_schema" in added


def test_handle_output_parquet_skips_schema_when_defined(
    mocker: MockerFixture,
) -> None:
    io_mgr = PolarsDataFrameSinkParquetIoManager()
    ctx = _make_output_context(
        mocker,
        definition_metadata={"dagster/column_schema": "pre-defined"},
    )
    mocker.patch.object(pl.LazyFrame, "sink_parquet", return_value=None)

    io_mgr.handle_output(ctx, _SMALL_DF)

    added = ctx.add_output_metadata.call_args[0][0]
    assert "dagster/column_schema" not in added


def test_handle_output_parquet_uses_local_writer_for_local_paths(
    mocker: MockerFixture,
) -> None:
    io_mgr = PolarsDataFrameSinkParquetIoManager()
    ctx = _make_output_context(mocker, uri="/tmp/test-table")
    sink_parquet = mocker.patch.object(pl.LazyFrame, "sink_parquet", return_value=None)

    io_mgr.handle_output(ctx, _SMALL_DF)

    sink_parquet.assert_called_once_with(
        "/tmp/test-table/part-00000.parquet", mkdir=True
    )


def test_load_input_parquet(mocker: MockerFixture) -> None:
    io_mgr = PolarsDataFrameSinkParquetIoManager()
    ctx = _make_input_context(mocker)
    mock_lf = pl.LazyFrame({"a": [1]})
    scan_parquet = mocker.patch(
        "aemo_etl.defs.resources.scan_parquet",
        return_value=mock_lf,
    )

    result = io_mgr.load_input(ctx)

    assert isinstance(result, pl.LazyFrame)
    scan_parquet.assert_called_once_with("s3://test-bucket/table/*.parquet")


# ---------------------------------------------------------------------------
# defs() function
# ---------------------------------------------------------------------------


def test_defs_returns_definitions_with_four_io_managers() -> None:
    d = defs()
    assert isinstance(d, Definitions)
    assert d.resources is not None
    assert set(d.resources) == {
        "aemo_deltalake_append_io_manager",
        "aemo_deltalake_overwrite_io_manager",
        "aemo_deltalake_ingest_partitioned_append_io_manager",
        "aemo_parquet_overwrite_io_manager",
    }
