"""Unit tests for factories/unzipper/ – sensors, assets, file_unzipper, defs."""

import io
import zipfile
from typing import IO, Any
from unittest.mock import MagicMock

import pytest
from dagster import AssetKey, AssetSelection, DagsterRunStatus, Definitions, RunRequest
from dagster_aws.s3 import S3Resource
from pytest_mock import MockerFixture
from types_boto3_s3 import S3Client

from aemo_etl.defs.raw.sttm._manifest import get_sttm_report_manifest
from aemo_etl.factories.unzipper.assets import (
    UnzipperConfiguration,
    unzipper_asset_factory,
)
from aemo_etl.factories.unzipper.definitions import unzipper_definitions_factory
from aemo_etl.factories.unzipper.file_unzipper import S3FileUnzipper
from aemo_etl.factories.unzipper.sensors import unzipper_sensor
from aemo_etl.utils import get_s3_object_keys_from_prefix_and_name_glob

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ASSET_KEY = AssetKey(["bronze", "vicgas", "unzipper_vicgas"])
_ZIP_KEY = "bronze/vicgas/data.zip"


def _make_run(
    status: DagsterRunStatus,
    asset_key: AssetKey | None = _ASSET_KEY,
) -> MagicMock:
    run = MagicMock()
    run.asset_selection = {asset_key} if asset_key is not None else None
    run.status = status
    return run


def _create_zip(members: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in members.items():
            zf.writestr(name, content)
    return buf.getvalue()


_CSV_CONTENT = b"col1,col2\nval1,val2\n"
_CSV_ZIP = _create_zip({"data.csv": _CSV_CONTENT})
_NON_CSV_ZIP = _create_zip({"data.txt": b"hello"})
_DIR_ZIP = _create_zip({"subdir/": b""})


class _NoSuchKey(Exception):
    """Stand-in for s3_client.exceptions.NoSuchKey."""


# ===========================================================================
# sensors: factory + inner function
# ===========================================================================


def test_unzipper_sensor_factory_creates_sensor() -> None:
    sensor_def = unzipper_sensor(
        name="test_unzipper_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/vicgas",
    )
    assert sensor_def.name == "test_unzipper_sensor"


def _build_sensor_context(
    mocker: MockerFixture,
    active_runs: list[MagicMock] | None = None,
    completed_runs: list[MagicMock] | None = None,
    glob_pattern: str = "*.zip",
) -> MagicMock:
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mock_asset_defs = mocker.MagicMock()
    mock_asset_defs.metadata_by_key.get.return_value = {"glob_pattern": glob_pattern}
    context.repository_def.assets_defs_by_key = {_ASSET_KEY: mock_asset_defs}
    context.instance.get_runs.side_effect = [active_runs or [], completed_runs or []]
    return context  # type: ignore[no-any-return]


@pytest.mark.parametrize(
    "active_runs,completed_runs,has_requests",
    [
        ([], [], True),
        ([_make_run(DagsterRunStatus.STARTED)], [], False),
        ([], [_make_run(DagsterRunStatus.FAILURE)], False),
    ],
)
def test_unzipper_sensor_inner(
    mocker: MockerFixture,
    active_runs: list[MagicMock],
    completed_runs: list[MagicMock],
    has_requests: bool,
) -> None:
    mocker.patch(
        "aemo_etl.factories.unzipper.sensors.get_s3_pagination",
        return_value=[{}],
    )
    mocker.patch(
        "aemo_etl.factories.unzipper.sensors.get_object_head_from_pages",
        return_value={_ZIP_KEY: {"Size": 100}},
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=[_ZIP_KEY] if has_requests or not active_runs else [],
    )
    mocker.patch.object(AssetSelection, "resolve", return_value=frozenset([_ASSET_KEY]))

    sensor_def = unzipper_sensor(
        name="test_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/vicgas",
    )
    context = _build_sensor_context(mocker, active_runs, completed_runs)
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mocker.MagicMock(spec=S3Client)

    results: list[RunRequest] = list(sensor_def._raw_fn(context, s3=mock_s3))  # type: ignore[call-overload, arg-type]
    if has_requests:
        assert len(results) == 1
    else:
        assert len(results) == 0


def test_unzipper_sensor_bytes_cap(mocker: MockerFixture) -> None:
    many_keys = [f"bronze/vicgas/zip{i}.zip" for i in range(3)]
    big_heads = {k: {"Size": 300_000_000} for k in many_keys}

    mocker.patch(
        "aemo_etl.factories.unzipper.sensors.get_s3_pagination", return_value=[{}]
    )
    mocker.patch(
        "aemo_etl.factories.unzipper.sensors.get_object_head_from_pages",
        return_value=big_heads,
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=many_keys,
    )
    mocker.patch.object(AssetSelection, "resolve", return_value=frozenset([_ASSET_KEY]))

    sensor_def = unzipper_sensor(
        name="bytes_cap_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/vicgas",
        bytes_cap=500_000_000,  # only 1 zip at 300MB fits
    )
    context = _build_sensor_context(mocker)
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mocker.MagicMock(spec=S3Client)

    results: list[RunRequest] = list(sensor_def._raw_fn(context, s3=mock_s3))  # type: ignore[call-overload, arg-type]
    assert len(results) == 1
    assert (
        len(
            results[0].run_config["ops"][_ASSET_KEY.to_python_identifier()]["config"][
                "s3_keys"
            ]
        )
        == 1
    )


def test_unzipper_sensor_files_cap(mocker: MockerFixture) -> None:
    many_keys = [f"bronze/vicgas/zip{i}.zip" for i in range(3)]
    small_heads = {k: {"Size": 100} for k in many_keys}

    mocker.patch(
        "aemo_etl.factories.unzipper.sensors.get_s3_pagination", return_value=[{}]
    )
    mocker.patch(
        "aemo_etl.factories.unzipper.sensors.get_object_head_from_pages",
        return_value=small_heads,
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=many_keys,
    )
    mocker.patch.object(AssetSelection, "resolve", return_value=frozenset([_ASSET_KEY]))

    sensor_def = unzipper_sensor(
        name="files_cap_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/vicgas",
        files_cap=2,
    )
    context = _build_sensor_context(mocker)
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mocker.MagicMock(spec=S3Client)

    results: list[RunRequest] = list(sensor_def._raw_fn(context, s3=mock_s3))  # type: ignore[call-overload, arg-type]
    assert len(results) == 1
    assert (
        len(
            results[0].run_config["ops"][_ASSET_KEY.to_python_identifier()]["config"][
                "s3_keys"
            ]
        )
        == 2
    )


def test_unzipper_sensor_no_keys(mocker: MockerFixture) -> None:
    mocker.patch(
        "aemo_etl.factories.unzipper.sensors.get_s3_pagination", return_value=[{}]
    )
    mocker.patch(
        "aemo_etl.factories.unzipper.sensors.get_object_head_from_pages",
        return_value={},
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=[],
    )
    mocker.patch.object(AssetSelection, "resolve", return_value=frozenset([_ASSET_KEY]))

    sensor_def = unzipper_sensor(
        name="no_keys_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/vicgas",
    )
    context = _build_sensor_context(mocker)
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mocker.MagicMock(spec=S3Client)

    results: list[RunRequest] = list(sensor_def._raw_fn(context, s3=mock_s3))  # type: ignore[call-overload, arg-type]
    assert results == []


# ===========================================================================
# assets: UnzipperConfiguration + inner _asset function
# ===========================================================================


def test_unzipper_configuration_defaults() -> None:
    cfg = UnzipperConfiguration()
    assert cfg.s3_keys == []


def test_unzipper_asset_factory_creates_asset() -> None:
    asset_def = unzipper_asset_factory(
        s3_landing_bucket="landing-bucket",
        s3_landing_prefix="bronze/vicgas",
        s3_archive_bucket="archive-bucket",
        name="unzipper_test",
        key_prefix=["bronze", "vicgas"],
    )
    assert asset_def is not None


def test_unzipper_asset_empty_keys(mocker: MockerFixture) -> None:
    mock_unzipper = MagicMock(spec=S3FileUnzipper)
    asset_def = unzipper_asset_factory(
        s3_landing_bucket="landing",
        s3_landing_prefix="bronze/vicgas",
        s3_archive_bucket="archive",
        file_unzipper=mock_unzipper,
        name="unzipper_vicgas",
    )
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    config = UnzipperConfiguration(s3_keys=[])
    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    fn(context, s3=mock_s3, config=config)
    mock_unzipper.unzip.assert_not_called()


def test_unzipper_asset_with_keys(mocker: MockerFixture) -> None:
    mock_unzipper = MagicMock(spec=S3FileUnzipper)
    mock_unzipper.unzip.return_value = []
    asset_def = unzipper_asset_factory(
        s3_landing_bucket="landing",
        s3_landing_prefix="bronze/vicgas",
        s3_archive_bucket="archive",
        file_unzipper=mock_unzipper,
        name="unzipper_vicgas",
    )
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    config = UnzipperConfiguration(s3_keys=[_ZIP_KEY])
    fn = asset_def.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    fn(context, s3=mock_s3, config=config)
    mock_unzipper.unzip.assert_called_once()


# ===========================================================================
# file_unzipper: S3FileUnzipper.unzip + _convert_csv_to_parquet
# ===========================================================================


def _build_unzip_args(
    mocker: MockerFixture,
    zip_bytes: bytes,
    s3_source_keys: list[str] | None = None,
) -> tuple[MagicMock, MagicMock, MagicMock, dict[str, Any]]:
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()

    mock_s3_client = mocker.MagicMock(spec=S3Client)
    mock_s3_client.exceptions.NoSuchKey = _NoSuchKey
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mock_s3_client

    def _download(bucket: str, key: str, fileobj: IO[bytes]) -> None:
        fileobj.write(zip_bytes)

    mock_s3_client.download_fileobj.side_effect = _download

    kwargs = {
        "context": context,
        "s3": mock_s3,
        "s3_source_keys": s3_source_keys or [_ZIP_KEY],
        "s3_landing_bucket": "landing",
        "s3_landing_prefix": "bronze/vicgas",
        "s3_archive_bucket": "archive",
    }
    return context, mock_s3, mock_s3_client, kwargs


def test_unzipper_csv_member_success(mocker: MockerFixture) -> None:
    """CSV member is converted to parquet and source zip is deleted."""
    mocker.patch(
        "aemo_etl.factories.unzipper.file_unzipper.scan_csv",
        return_value=mocker.MagicMock(),
    )
    context, mock_s3, mock_s3_client, kwargs = _build_unzip_args(mocker, _CSV_ZIP)
    unzipper = S3FileUnzipper()
    result = unzipper.unzip(**kwargs)
    assert result == []
    # Source zip should be copied to archive then deleted
    mock_s3_client.copy_object.assert_called_once()
    mock_s3_client.delete_object.assert_called_once()


def test_sttm_day_zip_member_matches_raw_source_table_glob(
    mocker: MockerFixture,
) -> None:
    """Representative STTM DAYNN.ZIP extraction matches the INT651 raw glob."""
    mocker.patch(
        "aemo_etl.factories.unzipper.file_unzipper.scan_csv",
        return_value=mocker.MagicMock(),
    )
    sttm_zip = _create_zip(
        {
            "INT651_V1_EX_ANTE_MARKET_PRICE_RPT_1.CSV": (
                b"gas_date,hub_identifier\n2024-01-01,SYD\n"
            )
        }
    )
    _, _, mock_s3_client, kwargs = _build_unzip_args(
        mocker,
        sttm_zip,
        s3_source_keys=["bronze/sttm/DAY01.ZIP"],
    )
    kwargs["s3_landing_prefix"] = "bronze/sttm"

    unzipper = S3FileUnzipper()
    unzipper.unzip(**kwargs)

    uploaded_key = mock_s3_client.upload_fileobj.call_args.args[2]
    report = get_sttm_report_manifest("INT651")
    assert get_s3_object_keys_from_prefix_and_name_glob(
        s3_prefix="bronze/sttm",
        s3_file_glob=report["glob_pattern"],
        original_keys=[uploaded_key],
    ) == [uploaded_key]


def test_unzipper_non_csv_member(mocker: MockerFixture) -> None:
    """Non-CSV member is uploaded raw; source zip is deleted."""
    context, mock_s3, mock_s3_client, kwargs = _build_unzip_args(mocker, _NON_CSV_ZIP)
    unzipper = S3FileUnzipper()
    result = unzipper.unzip(**kwargs)
    assert result == []
    mock_s3_client.upload_fileobj.assert_called_once()
    mock_s3_client.copy_object.assert_called_once()
    mock_s3_client.delete_object.assert_called_once()


def test_unzipper_dir_member_skipped(mocker: MockerFixture) -> None:
    """Directory-only zip should not upload anything."""
    dir_zip = _create_zip({"subdir/": b""})
    context, mock_s3, mock_s3_client, kwargs = _build_unzip_args(mocker, dir_zip)
    unzipper = S3FileUnzipper()

    # Dir member inside zipfile needs special handling
    # Actually create a zip with a directory entry properly
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.mkdir("subdir")  # type: ignore[attr-defined]
    dir_only_zip = buf.getvalue()

    _, _, mock_s3_client2, kwargs2 = _build_unzip_args(mocker, dir_only_zip)
    unzipper.unzip(**kwargs2)
    mock_s3_client2.upload_fileobj.assert_not_called()


def test_unzipper_member_failure_no_delete(mocker: MockerFixture) -> None:
    """Member processing exception prevents source zip deletion."""
    mock_s3_client = mocker.MagicMock(spec=S3Client)
    mock_s3_client.exceptions.NoSuchKey = _NoSuchKey
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mock_s3_client

    def _download(bucket: str, key: str, fileobj: IO[bytes]) -> None:
        fileobj.write(_CSV_ZIP)

    mock_s3_client.download_fileobj.side_effect = _download
    # Make upload_fileobj fail for all calls
    mock_s3_client.upload_fileobj.side_effect = RuntimeError("upload failed")
    # Also make scan_csv raise so _convert_csv_to_parquet fails
    mocker.patch(
        "aemo_etl.factories.unzipper.file_unzipper.scan_csv",
        side_effect=RuntimeError("csv parse failed"),
    )

    context = mocker.MagicMock()
    context.log = mocker.MagicMock()

    unzipper = S3FileUnzipper()
    result = unzipper.unzip(
        context=context,
        s3=mock_s3,
        s3_source_keys=[_ZIP_KEY],
        s3_landing_bucket="landing",
        s3_landing_prefix="bronze/vicgas",
        s3_archive_bucket="archive",
    )
    assert result == []
    # Source zip should NOT be deleted because member failed
    mock_s3_client.copy_object.assert_not_called()
    mock_s3_client.delete_object.assert_not_called()


def test_unzipper_no_such_key(mocker: MockerFixture) -> None:
    """NoSuchKey exception from S3 is handled gracefully."""

    class _NoSuchKey(Exception):
        pass

    mock_s3_client = mocker.MagicMock(spec=S3Client)
    mock_s3_client.exceptions.NoSuchKey = _NoSuchKey
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mock_s3_client
    mock_s3_client.download_fileobj.side_effect = _NoSuchKey("no such key")
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    unzipper = S3FileUnzipper()
    result = unzipper.unzip(
        context=context,
        s3=mock_s3,
        s3_source_keys=[_ZIP_KEY],
        s3_landing_bucket="landing",
        s3_landing_prefix="bronze/vicgas",
        s3_archive_bucket="archive",
    )
    assert result == []


def test_unzipper_generic_exception_reraises(mocker: MockerFixture) -> None:
    """Generic exception from S3 is re-raised."""
    mock_s3_client = mocker.MagicMock(spec=S3Client)
    mock_s3_client.exceptions.NoSuchKey = _NoSuchKey
    mock_s3 = mocker.MagicMock(spec=S3Resource)
    mock_s3.get_client.return_value = mock_s3_client
    mock_s3_client.download_fileobj.side_effect = ValueError("unexpected")
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    unzipper = S3FileUnzipper()
    with pytest.raises(ValueError, match="unexpected"):
        unzipper.unzip(
            context=context,
            s3=mock_s3,
            s3_source_keys=[_ZIP_KEY],
            s3_landing_bucket="landing",
            s3_landing_prefix="bronze/vicgas",
            s3_archive_bucket="archive",
        )


def test_convert_csv_to_parquet_success(mocker: MockerFixture) -> None:
    """_convert_csv_to_parquet converts a CSV file to parquet on S3."""
    mock_s3_client = mocker.MagicMock(spec=S3Client)
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mock_lf = mocker.MagicMock()
    mocker.patch(
        "aemo_etl.factories.unzipper.file_unzipper.scan_csv",
        return_value=mock_lf,
    )
    zipped_file = io.BytesIO(_CSV_CONTENT)
    unzipper = S3FileUnzipper()
    write_key = unzipper._convert_csv_to_parquet(
        context=context,
        s3_client=mock_s3_client,
        zipped_file=zipped_file,
        original_filename="data.csv",
        base_dir="",
        base_name="data.csv",
        s3_target_bucket="landing",
        s3_target_prefix="bronze/vicgas",
    )
    assert write_key.endswith(".parquet")
    mock_s3_client.upload_fileobj.assert_called_once()


def test_convert_csv_to_parquet_fallback(mocker: MockerFixture) -> None:
    """When parquet conversion fails, raw CSV is uploaded as fallback."""
    mock_s3_client = mocker.MagicMock(spec=S3Client)
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mocker.patch(
        "aemo_etl.factories.unzipper.file_unzipper.scan_csv",
        side_effect=RuntimeError("parse error"),
    )
    zipped_file = io.BytesIO(_CSV_CONTENT)
    unzipper = S3FileUnzipper()
    write_key = unzipper._convert_csv_to_parquet(
        context=context,
        s3_client=mock_s3_client,
        zipped_file=zipped_file,
        original_filename="data.csv",
        base_dir="",
        base_name="data.csv",
        s3_target_bucket="landing",
        s3_target_prefix="bronze/vicgas",
    )
    assert write_key.endswith(".csv")
    mock_s3_client.upload_fileobj.assert_called_once()


def test_convert_csv_to_parquet_fallback_no_tmp_file(mocker: MockerFixture) -> None:
    """RuntimeError when fallback tmp CSV is also unavailable."""
    mock_s3_client = mocker.MagicMock(spec=S3Client)
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mocker.patch(
        "aemo_etl.factories.unzipper.file_unzipper.scan_csv",
        side_effect=RuntimeError("parse error"),
    )
    # Make os.path.exists return False so fallback hits RuntimeError
    mocker.patch(
        "aemo_etl.factories.unzipper.file_unzipper.os.path.exists",
        return_value=False,
    )
    zipped_file = io.BytesIO(_CSV_CONTENT)
    unzipper = S3FileUnzipper()
    with pytest.raises(RuntimeError, match="CSV fallback failed"):
        unzipper._convert_csv_to_parquet(
            context=context,
            s3_client=mock_s3_client,
            zipped_file=zipped_file,
            original_filename="data.csv",
            base_dir="",
            base_name="data.csv",
            s3_target_bucket="landing",
            s3_target_prefix="bronze/vicgas",
        )


# ===========================================================================
# definitions factory
# ===========================================================================


def test_unzipper_definitions_factory_default_prefix() -> None:
    defs = unzipper_definitions_factory(domain="vicgas", name="unzipper_vicgas")
    assert isinstance(defs, Definitions)


def test_unzipper_definitions_factory_explicit_prefix() -> None:
    defs = unzipper_definitions_factory(
        domain="gbb",
        name="unzipper_gbb",
        s3_landing_prefix="bronze/gbb/custom",
    )
    assert isinstance(defs, Definitions)
