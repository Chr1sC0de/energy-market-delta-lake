"""Unit tests for factories/df_from_s3_keys/assets.py – all branches."""

import datetime as dt
from datetime import timezone

import polars as pl
import pytest
from dagster import AssetsDefinition
from dagster_aws.s3 import S3Resource
from polars import Datetime, String
from pytest_mock import MockerFixture
from types_boto3_s3 import S3Client

from aemo_etl.factories.df_from_s3_keys.assets import (
    DFFromS3KeysConfiguration,
    bronze_df_from_s3_keys_asset_factory,
    silver_df_from_s3_keys_asset_factory,
)
from aemo_etl.factories.df_from_s3_keys.hooks import Hook

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SCHEMA = {
    "col1": String,
    "ingested_timestamp": Datetime("us", time_zone="UTC"),
    "ingested_date": Datetime("us", time_zone="UTC"),
    "surrogate_key": String,
    "source_file": String,
}

_CSV_BYTES = b"col1\nvalue1\n"
_EMPTY_BYTES = b""

_AEST = dt.timezone(dt.timedelta(hours=10))
_UTC = timezone.utc

_BATCH_DF = pl.LazyFrame(
    {
        "col1": ["value1"],
        "ingested_timestamp": [dt.datetime(2024, 1, 1, 10, tzinfo=_AEST)],
        "ingested_date": [dt.datetime(2024, 1, 1, tzinfo=_UTC)],
        "surrogate_key": ["hash1"],
        "source_content_hash": ["content-hash1"],
        "source_file": ["s3://archive/key.csv"],
    },
    schema={
        "col1": String,
        "ingested_timestamp": Datetime("us", time_zone="UTC"),
        "ingested_date": Datetime("us", time_zone="UTC"),
        "surrogate_key": String,
        "source_content_hash": String,
        "source_file": String,
    },
)


def _make_asset(
    postprocess_object_hooks: list[Hook[bytes]] | None = None,
    postprocess_lazyframe_hooks: list[Hook[pl.LazyFrame]] | None = None,
) -> AssetsDefinition:
    return bronze_df_from_s3_keys_asset_factory(
        uri="s3://test-aemo/bronze/gbb/test_asset",
        schema=_SCHEMA,
        surrogate_key_sources=["col1"],
        postprocess_object_hooks=postprocess_object_hooks,
        postprocess_lazyframe_hooks=postprocess_lazyframe_hooks,
        name="test_asset",
        key_prefix=["bronze", "gbb"],
    )


def _call_asset(
    mocker: MockerFixture,
    asset_def: AssetsDefinition,
    s3_keys: list[str],
    bytes_by_key: dict[str, bytes | None] | None = None,
    scan_delta_side_effect: object = None,
) -> pl.LazyFrame:
    """Invoke the inner _asset function with standard mocks."""
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()

    mock_s3_client = mocker.MagicMock(spec=S3Client)
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mock_s3_client

    bytes_by_key = bytes_by_key or {}

    def _get_from_s3_side_effect(
        _client: object, _bucket: str, key: str, **_kw: object
    ) -> bytes | None:
        return bytes_by_key.get(key)

    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.assets.get_from_s3",
        side_effect=_get_from_s3_side_effect,
    )
    mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)

    if scan_delta_side_effect is None:
        mocker.patch(
            "aemo_etl.factories.df_from_s3_keys.assets.scan_delta",
            return_value=_BATCH_DF,
        )
    else:
        mocker.patch(
            "aemo_etl.factories.df_from_s3_keys.assets.scan_delta",
            side_effect=scan_delta_side_effect,
        )

    config = DFFromS3KeysConfiguration(s3_keys=s3_keys)
    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    return fn(context, s3=mock_s3, config=config)  # type: ignore[return-value, no-any-return]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_config_defaults() -> None:
    cfg = DFFromS3KeysConfiguration()
    assert cfg.s3_keys == []


def test_asset_no_keys(mocker: MockerFixture) -> None:
    """Empty s3_keys → returns an empty LazyFrame matching the schema."""
    asset_def = _make_asset()
    mocker.patch("aemo_etl.factories.df_from_s3_keys.assets.get_from_s3")
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mocker.MagicMock(spec=S3Client)
    config = DFFromS3KeysConfiguration(s3_keys=[])
    result = asset_def(context=context, s3=mock_s3, config=config)
    assert isinstance(result, pl.LazyFrame)


def test_asset_unsupported_filetype(mocker: MockerFixture) -> None:
    """Unsupported extension is skipped with a log message."""
    asset_def = _make_asset()
    result = _call_asset(
        mocker,
        asset_def,
        s3_keys=["file.xyz"],
    )
    # No data → empty schema LazyFrame
    assert isinstance(result, pl.LazyFrame)


def test_asset_key_not_found(mocker: MockerFixture) -> None:
    """get_from_s3 returns None → key skipped."""
    asset_def = _make_asset()
    result = _call_asset(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/missing.csv"],
        bytes_by_key={"bronze/gbb/missing.csv": None},
    )
    assert isinstance(result, pl.LazyFrame)


def test_asset_empty_bytes(mocker: MockerFixture) -> None:
    """Zero-byte file → skipped."""
    asset_def = _make_asset()
    result = _call_asset(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/empty.csv"],
        bytes_by_key={"bronze/gbb/empty.csv": _EMPTY_BYTES},
    )
    assert isinstance(result, pl.LazyFrame)


def test_asset_first_run(mocker: MockerFixture) -> None:
    """Valid CSV bytes, table does not exist yet → first-run path."""
    asset_def = _make_asset()
    result = _call_asset(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/data.csv"],
        bytes_by_key={"bronze/gbb/data.csv": _CSV_BYTES},
    )
    assert isinstance(result, pl.LazyFrame)


def test_asset_returns_current_state_batch(mocker: MockerFixture) -> None:
    """Bronze emits one max-source_file row per surrogate_key."""
    staged_batch = pl.LazyFrame(
        {
            "col1": ["older", "newer", "only"],
            "ingested_timestamp": [
                dt.datetime(2024, 1, 1, 10, tzinfo=_AEST),
                dt.datetime(2024, 1, 1, 10, tzinfo=_AEST),
                dt.datetime(2024, 1, 1, 10, tzinfo=_AEST),
            ],
            "ingested_date": [
                dt.datetime(2024, 1, 1, tzinfo=_UTC),
                dt.datetime(2024, 1, 1, tzinfo=_UTC),
                dt.datetime(2024, 1, 1, tzinfo=_UTC),
            ],
            "surrogate_key": ["hash1", "hash1", "hash2"],
            "source_content_hash": ["old-content", "new-content", "only-content"],
            "source_file": [
                "s3://archive/table~20260421000000.parquet",
                "s3://archive/table~20260422000000.parquet",
                "s3://archive/table~20260420000000.parquet",
            ],
        }
    )
    asset_def = _make_asset()
    result = _call_asset(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/data.csv"],
        bytes_by_key={"bronze/gbb/data.csv": _CSV_BYTES},
        scan_delta_side_effect=lambda *_args, **_kwargs: staged_batch,
    )
    collected = result.sort("surrogate_key").collect()
    assert collected["col1"].to_list() == ["newer", "only"]


def test_asset_does_not_archive_when_staging_fails(mocker: MockerFixture) -> None:
    asset_def = _make_asset()
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mock_s3_client = mocker.MagicMock(spec=S3Client)
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mock_s3_client
    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.assets.get_from_s3",
        return_value=_CSV_BYTES,
    )
    mocker.patch.object(
        pl.LazyFrame, "sink_delta", side_effect=RuntimeError("stage failed")
    )
    config = DFFromS3KeysConfiguration(s3_keys=["bronze/gbb/data.csv"])
    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    with pytest.raises(RuntimeError, match="stage failed"):
        fn(context, s3=mock_s3, config=config)

    mock_s3_client.copy_object.assert_not_called()
    mock_s3_client.delete_object.assert_not_called()


def test_silver_asset_keeps_latest_source_file_per_surrogate_key(
    mocker: MockerFixture,
) -> None:
    sink_parquet_spy = mocker.spy(pl.LazyFrame, "sink_parquet")
    asset_def = silver_df_from_s3_keys_asset_factory(
        name="silver_test_asset",
        key_prefix=["silver", "gbb"],
    )
    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    input_df = pl.LazyFrame(
        {
            "col1": ["older", "newer", "only"],
            "surrogate_key": ["hash1", "hash1", "hash2"],
            "source_file": [
                "s3://archive/table~20260421000000.parquet",
                "s3://archive/table~20260422000000.parquet",
                "s3://archive/table~20260420000000.parquet",
            ],
        }
    )

    result = fn(input_df).sort("surrogate_key").collect()

    assert result["col1"].to_list() == ["newer", "only"]
    assert sink_parquet_spy.call_count == 2
    assert sink_parquet_spy.call_args_list[0].args[1].endswith("/silver_input.parquet")
    assert (
        sink_parquet_spy.call_args_list[1].args[1].endswith("/silver_current.parquet")
    )


def test_asset_with_object_hook(mocker: MockerFixture) -> None:
    """postprocess_object_hooks are called on the raw bytes."""
    mock_hook = mocker.MagicMock(spec=Hook)  # type: ignore[type-arg]
    mock_hook.process.return_value = _CSV_BYTES

    asset_def = _make_asset(postprocess_object_hooks=[mock_hook])
    result = _call_asset(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/data.csv"],
        bytes_by_key={"bronze/gbb/data.csv": _CSV_BYTES},
    )
    assert isinstance(result, pl.LazyFrame)
    mock_hook.process.assert_called_once()


def test_asset_with_lazyframe_hook(mocker: MockerFixture) -> None:
    """postprocess_lazyframe_hooks are called on the parsed LazyFrame."""

    class _PassthroughHook(Hook[pl.LazyFrame]):
        def process(
            self, s3_bucket: str, s3_key: str, object_: pl.LazyFrame
        ) -> pl.LazyFrame:
            return object_

    asset_def = _make_asset(postprocess_lazyframe_hooks=[_PassthroughHook()])
    result = _call_asset(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/data.csv"],
        bytes_by_key={"bronze/gbb/data.csv": _CSV_BYTES},
    )
    assert isinstance(result, pl.LazyFrame)
