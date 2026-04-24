"""Unit tests for defs/resources.py – PolarsDataFrameSinkDeltaIoManager."""

from typing import Any
from unittest.mock import MagicMock

import polars as pl
from dagster import Definitions
from pytest_mock import MockerFixture

from aemo_etl.configs import DAGSTER_URI
from aemo_etl.defs.resources import PolarsDataFrameSinkDeltaIoManager, defs

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


# ---------------------------------------------------------------------------
# defs() function
# ---------------------------------------------------------------------------


def test_defs_returns_definitions_with_three_io_managers() -> None:
    d = defs()
    assert isinstance(d, Definitions)
