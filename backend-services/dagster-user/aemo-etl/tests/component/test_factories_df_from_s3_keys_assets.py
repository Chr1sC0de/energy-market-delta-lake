"""Unit tests for factories/df_from_s3_keys/assets.py – all branches."""

import datetime as dt
from collections.abc import Mapping
from datetime import timezone
from unittest.mock import MagicMock, call

import polars as pl
import pytest
from dagster import (
    AssetCheckResult,
    AssetCheckSeverity,
    AssetKey,
    AssetsDefinition,
    MaterializeResult,
)
from dagster._core.definitions.metadata import RawMetadataValue
from dagster_aws.s3 import S3Resource
from polars import Datetime, String
from pytest_mock import MockerFixture
from types_boto3_s3 import S3Client

from aemo_etl.factories.df_from_s3_keys.current_state import (
    SourceTableBronzeWriteResult,
)
from aemo_etl.factories.df_from_s3_keys.assets import (
    DFFromS3KeysConfiguration,
    SKIPPED_S3_KEYS_CHECK_NAME,
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

_DEFAULT_WRITE_RESULT = SourceTableBronzeWriteResult(
    row_count=1,
    target_exists_before_write=True,
    wrote_table=True,
    write_mode="merge",
)
_SKIPPED_WRITE_RESULT = SourceTableBronzeWriteResult(
    row_count=0,
    target_exists_before_write=True,
    wrote_table=False,
    write_mode="skip",
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
    patch_writer: bool = True,
    writer_result: SourceTableBronzeWriteResult = _DEFAULT_WRITE_RESULT,
) -> MaterializeResult[None]:
    """Invoke the inner _asset function with standard mocks."""
    result, _s3_client = _call_asset_with_s3_client(
        mocker,
        asset_def,
        s3_keys=s3_keys,
        bytes_by_key=bytes_by_key,
        scan_delta_side_effect=scan_delta_side_effect,
        patch_writer=patch_writer,
        writer_result=writer_result,
    )
    return result


def _call_asset_with_s3_client(
    mocker: MockerFixture,
    asset_def: AssetsDefinition,
    *,
    s3_keys: list[str],
    bytes_by_key: dict[str, bytes | None] | None = None,
    scan_delta_side_effect: object = None,
    patch_writer: bool = True,
    writer_result: SourceTableBronzeWriteResult = _DEFAULT_WRITE_RESULT,
) -> tuple[MaterializeResult[None], MagicMock]:
    """Invoke the inner _asset function and return the mocked S3 client."""
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
    if patch_writer:
        mocker.patch(
            "aemo_etl.factories.df_from_s3_keys.assets.write_source_table_current_state_batch",
            return_value=writer_result,
        )

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
    result = fn(context, s3=mock_s3, config=config)
    return result, mock_s3_client


def _skipped_s3_keys_check(
    result: MaterializeResult[None],
) -> AssetCheckResult:
    return result.check_result_named(SKIPPED_S3_KEYS_CHECK_NAME)


def _metadata_int(metadata_value: object) -> int:
    value = getattr(metadata_value, "value", metadata_value)
    assert isinstance(value, int)
    return value


def _result_metadata(
    result: MaterializeResult[None],
) -> Mapping[str, RawMetadataValue]:
    assert result.metadata is not None
    return result.metadata


def _skipped_check_asset_key(asset_def: AssetsDefinition) -> AssetKey:
    for check_spec in asset_def.check_specs:
        if check_spec.name == SKIPPED_S3_KEYS_CHECK_NAME:
            return check_spec.asset_key
    raise AssertionError(f"{SKIPPED_S3_KEYS_CHECK_NAME} not found")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_config_defaults() -> None:
    cfg = DFFromS3KeysConfiguration()
    assert cfg.s3_keys == []


def test_asset_check_spec_uses_explicit_key() -> None:
    asset_def = bronze_df_from_s3_keys_asset_factory(
        uri="s3://test-aemo/bronze/gbb/test_asset",
        schema=_SCHEMA,
        surrogate_key_sources=["col1"],
        key=["bronze", "gbb", "explicit_asset"],
    )

    assert _skipped_check_asset_key(asset_def) == AssetKey(
        ["bronze", "gbb", "explicit_asset"]
    )


def test_asset_check_spec_uses_name_without_key_prefix() -> None:
    asset_def = bronze_df_from_s3_keys_asset_factory(
        uri="s3://test-aemo/bronze/gbb/test_asset",
        schema=_SCHEMA,
        surrogate_key_sources=["col1"],
        name="unprefixed_asset",
    )

    assert _skipped_check_asset_key(asset_def) == AssetKey(["unprefixed_asset"])


def test_asset_check_spec_uses_string_key_prefix() -> None:
    asset_def = bronze_df_from_s3_keys_asset_factory(
        uri="s3://test-aemo/bronze/gbb/test_asset",
        schema=_SCHEMA,
        surrogate_key_sources=["col1"],
        name="string_prefixed_asset",
        key_prefix="bronze",
    )

    assert _skipped_check_asset_key(asset_def) == AssetKey(
        ["bronze", "string_prefixed_asset"]
    )


def test_asset_no_keys(mocker: MockerFixture) -> None:
    """Empty s3_keys materializes an empty current-state batch."""
    asset_def = _make_asset()
    mocker.patch("aemo_etl.factories.df_from_s3_keys.assets.get_from_s3")
    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.assets.write_source_table_current_state_batch",
        return_value=SourceTableBronzeWriteResult(
            row_count=0,
            target_exists_before_write=True,
            wrote_table=False,
            write_mode="skip",
        ),
    )
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mocker.MagicMock(spec=S3Client)
    config = DFFromS3KeysConfiguration(s3_keys=[])
    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = fn(context, s3=mock_s3, config=config)
    assert isinstance(result, MaterializeResult)
    check_result = _skipped_s3_keys_check(result)
    assert check_result.passed is True
    metadata = _result_metadata(result)
    assert metadata["processed_file_count"] == 0
    assert metadata["archived_file_count"] == 0


def test_asset_unsupported_filetype(mocker: MockerFixture) -> None:
    """Unsupported extension is skipped with a log message."""
    asset_def = _make_asset()
    result, mock_s3_client = _call_asset_with_s3_client(
        mocker,
        asset_def,
        s3_keys=["file.xyz"],
    )
    assert isinstance(result, MaterializeResult)
    check_result = _skipped_s3_keys_check(result)
    assert check_result.passed is False
    assert check_result.severity == AssetCheckSeverity.WARN
    assert _metadata_int(check_result.metadata["unsupported_key_count"]) == 1
    assert _result_metadata(result)["unsupported_key_count"] == 1
    mock_s3_client.copy_object.assert_not_called()
    mock_s3_client.delete_object.assert_not_called()


def test_asset_key_not_found(mocker: MockerFixture) -> None:
    """get_from_s3 returns None → key skipped."""
    asset_def = _make_asset()
    result, mock_s3_client = _call_asset_with_s3_client(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/missing.csv"],
        bytes_by_key={"bronze/gbb/missing.csv": None},
    )
    assert isinstance(result, MaterializeResult)
    check_result = _skipped_s3_keys_check(result)
    assert check_result.passed is False
    assert check_result.severity == AssetCheckSeverity.WARN
    assert _metadata_int(check_result.metadata["missing_key_count"]) == 1
    assert _result_metadata(result)["missing_key_count"] == 1
    mock_s3_client.copy_object.assert_not_called()
    mock_s3_client.delete_object.assert_not_called()


def test_asset_empty_bytes(mocker: MockerFixture) -> None:
    """Zero-byte file → skipped."""
    asset_def = _make_asset()
    result, mock_s3_client = _call_asset_with_s3_client(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/empty.csv"],
        bytes_by_key={"bronze/gbb/empty.csv": _EMPTY_BYTES},
        writer_result=_SKIPPED_WRITE_RESULT,
    )
    assert isinstance(result, MaterializeResult)
    check_result = _skipped_s3_keys_check(result)
    assert check_result.passed is True
    metadata = _result_metadata(result)
    assert metadata["zero_byte_file_count"] == 1
    assert metadata["deleted_zero_byte_file_count"] == 1
    mock_s3_client.copy_object.assert_not_called()
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket="dev-energy-market-landing",
        Key="bronze/gbb/empty.csv",
    )


def test_asset_first_run(mocker: MockerFixture) -> None:
    """Valid CSV bytes, table does not exist yet → first-run path."""
    asset_def = _make_asset()
    result, mock_s3_client = _call_asset_with_s3_client(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/data.csv"],
        bytes_by_key={"bronze/gbb/data.csv": _CSV_BYTES},
    )
    assert isinstance(result, MaterializeResult)
    assert _skipped_s3_keys_check(result).passed is True
    metadata = _result_metadata(result)
    assert metadata["processed_file_count"] == 1
    assert metadata["archived_file_count"] == 1
    mock_s3_client.copy_object.assert_called_once_with(
        CopySource={
            "Bucket": "dev-energy-market-landing",
            "Key": "bronze/gbb/data.csv",
        },
        Bucket="dev-energy-market-archive",
        Key="bronze/gbb/data.csv",
    )
    mock_s3_client.delete_object.assert_called_once_with(
        Bucket="dev-energy-market-landing",
        Key="bronze/gbb/data.csv",
    )


def test_asset_writes_current_state_batch(mocker: MockerFixture) -> None:
    """Bronze writes one max-source_file row per surrogate_key."""
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
    written_batches: list[pl.LazyFrame] = []

    def _write_source_table_current_state_batch(
        batch: pl.LazyFrame,
        **_kwargs: object,
    ) -> SourceTableBronzeWriteResult:
        written_batches.append(batch)
        return SourceTableBronzeWriteResult(
            row_count=2,
            target_exists_before_write=True,
            wrote_table=True,
            write_mode="merge",
        )

    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.assets.write_source_table_current_state_batch",
        side_effect=_write_source_table_current_state_batch,
    )
    result = _call_asset(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/data.csv"],
        bytes_by_key={"bronze/gbb/data.csv": _CSV_BYTES},
        scan_delta_side_effect=lambda *_args, **_kwargs: staged_batch,
        patch_writer=False,
    )

    assert isinstance(result, MaterializeResult)
    collected = written_batches[0].sort("surrogate_key").collect()
    assert collected["col1"].to_list() == ["newer", "only"]


def test_asset_defers_archive_when_current_state_write_skips(
    mocker: MockerFixture,
) -> None:
    asset_def = _make_asset()

    result, mock_s3_client = _call_asset_with_s3_client(
        mocker,
        asset_def,
        s3_keys=["bronze/gbb/data.csv"],
        bytes_by_key={"bronze/gbb/data.csv": _CSV_BYTES},
        writer_result=_SKIPPED_WRITE_RESULT,
    )

    assert isinstance(result, MaterializeResult)
    check_result = _skipped_s3_keys_check(result)
    assert check_result.passed is False
    assert check_result.severity == AssetCheckSeverity.WARN
    assert _metadata_int(check_result.metadata["deferred_processed_key_count"]) == 1
    metadata = _result_metadata(result)
    assert metadata["processed_file_count"] == 1
    assert metadata["archived_file_count"] == 0
    assert metadata["deferred_processed_file_count"] == 1
    mock_s3_client.copy_object.assert_not_called()
    mock_s3_client.delete_object.assert_not_called()


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


def test_asset_does_not_cleanup_when_current_state_write_fails(
    mocker: MockerFixture,
) -> None:
    asset_def = _make_asset()
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mock_s3_client = mocker.MagicMock(spec=S3Client)
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mock_s3_client

    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.assets.get_from_s3",
        side_effect=lambda _client, _bucket, key, **_kw: {
            "bronze/gbb/data.csv": _CSV_BYTES,
            "bronze/gbb/empty.csv": _EMPTY_BYTES,
        }.get(key),
    )
    mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)
    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.assets.scan_delta",
        return_value=_BATCH_DF,
    )
    mocker.patch(
        "aemo_etl.factories.df_from_s3_keys.assets.write_source_table_current_state_batch",
        side_effect=RuntimeError("write failed"),
    )

    config = DFFromS3KeysConfiguration(
        s3_keys=["bronze/gbb/data.csv", "bronze/gbb/empty.csv"]
    )
    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    with pytest.raises(RuntimeError, match="write failed"):
        fn(context, s3=mock_s3, config=config)

    mock_s3_client.copy_object.assert_not_called()
    mock_s3_client.delete_object.assert_not_called()


def test_asset_deletes_zero_byte_and_reports_skipped_keys(
    mocker: MockerFixture,
) -> None:
    asset_def = _make_asset()

    result, mock_s3_client = _call_asset_with_s3_client(
        mocker,
        asset_def,
        s3_keys=[
            "bronze/gbb/data.csv",
            "bronze/gbb/empty.csv",
            "bronze/gbb/missing.csv",
            "bronze/gbb/unsupported.txt",
        ],
        bytes_by_key={
            "bronze/gbb/data.csv": _CSV_BYTES,
            "bronze/gbb/empty.csv": _EMPTY_BYTES,
            "bronze/gbb/missing.csv": None,
        },
    )

    assert isinstance(result, MaterializeResult)
    check_result = _skipped_s3_keys_check(result)
    assert check_result.passed is False
    assert check_result.severity == AssetCheckSeverity.WARN
    assert _metadata_int(check_result.metadata["missing_key_count"]) == 1
    assert _metadata_int(check_result.metadata["unsupported_key_count"]) == 1
    metadata = _result_metadata(result)
    assert metadata["processed_file_count"] == 1
    assert metadata["archived_file_count"] == 1
    assert metadata["zero_byte_file_count"] == 1
    assert metadata["deleted_zero_byte_file_count"] == 1
    mock_s3_client.copy_object.assert_called_once_with(
        CopySource={
            "Bucket": "dev-energy-market-landing",
            "Key": "bronze/gbb/data.csv",
        },
        Bucket="dev-energy-market-archive",
        Key="bronze/gbb/data.csv",
    )
    mock_s3_client.delete_object.assert_has_calls(
        [
            call(Bucket="dev-energy-market-landing", Key="bronze/gbb/data.csv"),
            call(Bucket="dev-energy-market-landing", Key="bronze/gbb/empty.csv"),
        ]
    )


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
    assert isinstance(result, MaterializeResult)
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
    assert isinstance(result, MaterializeResult)
