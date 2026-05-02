"""Unit tests for aemo_etl.factories.sensors."""

from unittest.mock import MagicMock

import pytest
from dagster import (
    AssetKey,
    AssetSelection,
    DagsterRunStatus,
    RunRequest,
    define_asset_job,
)
from dagster_aws.s3 import S3Resource
from pytest_mock import MockerFixture
from types_boto3_s3 import S3Client

from aemo_etl.factories.sensors import (
    df_from_s3_keys_sensor,
    has_job_failed,
    is_running,
)


# ---------------------------------------------------------------------------
# Pure helper functions
# ---------------------------------------------------------------------------

_ASSET_KEY = AssetKey(["bronze", "gbb", "bronze_test_asset"])
_TARGET_JOB_NAME = "test_asset_job"


def _make_run(
    status: DagsterRunStatus,
    asset_key: AssetKey | None = _ASSET_KEY,
    job_name: str = _TARGET_JOB_NAME,
    tags: dict[str, str] | None = None,
) -> MagicMock:
    run = MagicMock()
    run.asset_selection = {asset_key} if asset_key is not None else None
    run.status = status
    run.job_name = job_name
    run.tags = tags or {}
    return run


def test_is_running_found() -> None:
    runs = [_make_run(DagsterRunStatus.STARTED)]
    assert is_running(runs, _TARGET_JOB_NAME) is True


def test_is_running_not_found() -> None:
    runs = [_make_run(DagsterRunStatus.STARTED, job_name="other_job")]
    assert is_running(runs, _TARGET_JOB_NAME) is False


def test_is_running_empty() -> None:
    assert is_running([], _TARGET_JOB_NAME) is False


def test_is_running_no_asset_selection() -> None:
    run = _make_run(DagsterRunStatus.QUEUED, asset_key=None)
    assert is_running([run], _TARGET_JOB_NAME) is True


def test_is_running_ignores_asset_selection() -> None:
    run = _make_run(DagsterRunStatus.QUEUED, job_name="other_job")
    assert is_running([run], _TARGET_JOB_NAME) is False


def test_has_job_failed_true() -> None:
    runs = [_make_run(DagsterRunStatus.FAILURE)]
    assert has_job_failed(runs, _TARGET_JOB_NAME) is True


def test_has_job_failed_false_success() -> None:
    runs = [_make_run(DagsterRunStatus.SUCCESS)]
    assert has_job_failed(runs, _TARGET_JOB_NAME) is False


def test_has_job_failed_no_match() -> None:
    runs = [_make_run(DagsterRunStatus.FAILURE, job_name="other_job")]
    assert has_job_failed(runs, _TARGET_JOB_NAME) is False


def test_has_job_failed_empty() -> None:
    assert has_job_failed([], _TARGET_JOB_NAME) is False


def test_has_job_failed_no_asset_selection() -> None:
    run = _make_run(DagsterRunStatus.FAILURE, asset_key=None)
    assert has_job_failed([run], _TARGET_JOB_NAME) is True


# ---------------------------------------------------------------------------
# Sensor factory + inner function coverage
# ---------------------------------------------------------------------------

_S3_OBJECT_KEY = "bronze/gbb/data.parquet"
_OBJECT_HEAD = {_S3_OBJECT_KEY: {"Size": 100}}


def _build_sensor_context(
    mocker: MockerFixture,
    asset_key: AssetKey = _ASSET_KEY,
    active_runs: list[MagicMock] | None = None,
    completed_runs: list[MagicMock] | None = None,
    glob_pattern: str = "*.parquet",
) -> MagicMock:
    """Return a fully-mocked SensorEvaluationContext."""
    context = mocker.MagicMock()  # type: ignore[no-any-return]
    context.log = mocker.MagicMock()

    mock_asset_defs = mocker.MagicMock()
    mock_asset_defs.metadata_by_key.get.return_value = {"glob_pattern": glob_pattern}
    context.repository_def.assets_defs_by_key = {asset_key: mock_asset_defs}
    context.instance.get_runs.side_effect = [
        active_runs or [],
        completed_runs or [],
    ]
    return context  # type: ignore[no-any-return]


def _build_mock_s3(mocker: MockerFixture) -> MagicMock:
    s3 = mocker.MagicMock(spec=S3Resource)
    client = mocker.MagicMock(spec=S3Client)
    s3.get_client.return_value = client
    return s3  # type: ignore[no-any-return]


def test_df_from_s3_keys_sensor_factory_creates_sensor() -> None:
    sensor_def = df_from_s3_keys_sensor(
        name="test_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="prefix",
    )
    assert sensor_def.name == "test_sensor"


@pytest.mark.parametrize(
    "active_runs,completed_runs,expected_requests",
    [
        # Normal – no runs → yields RunRequest
        ([], [], 1),
        # Target job is actively running → skip
        ([_make_run(DagsterRunStatus.STARTED)], [], 0),
        # Target job is queued without asset selection → skip
        ([_make_run(DagsterRunStatus.QUEUED, asset_key=None)], [], 0),
        # Another job is active, even for the same asset → do not skip
        ([_make_run(DagsterRunStatus.STARTED, job_name="other_job")], [], 1),
        # Target job previously failed → skip
        ([], [_make_run(DagsterRunStatus.FAILURE)], 0),
        # Another job previously failed, even for the same asset → do not skip
        ([], [_make_run(DagsterRunStatus.FAILURE, job_name="other_job")], 1),
    ],
)
def test_sensor_inner_function_run_requests(
    mocker: MockerFixture,
    active_runs: list[MagicMock],
    completed_runs: list[MagicMock],
    expected_requests: int,
) -> None:
    mocker.patch(
        "aemo_etl.factories.sensors.get_s3_pagination",
        return_value=[{"Contents": []}],
    )
    mocker.patch(
        "aemo_etl.factories.sensors.get_object_head_from_pages",
        return_value=_OBJECT_HEAD,
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=[_S3_OBJECT_KEY] if expected_requests else [],
    )
    mocker.patch.object(
        AssetSelection,
        "resolve",
        return_value=frozenset([_ASSET_KEY]),
    )

    sensor_def = df_from_s3_keys_sensor(
        name="test_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/gbb",
    )
    context = _build_sensor_context(
        mocker,
        active_runs=active_runs,
        completed_runs=completed_runs,
    )
    mock_s3 = _build_mock_s3(mocker)

    results: list[RunRequest] = list(sensor_def._raw_fn(context, s3=mock_s3))  # type: ignore[call-overload, arg-type]
    assert len(results) == expected_requests
    if expected_requests:
        assert results[0].job_name == _TARGET_JOB_NAME
        assert results[0].run_config["ops"][_ASSET_KEY.to_python_identifier()][
            "config"
        ]["s3_keys"] == [_S3_OBJECT_KEY]


def test_sensor_inner_retries_failed_job_when_current_job_tags_changed(
    mocker: MockerFixture,
) -> None:
    mocker.patch(
        "aemo_etl.factories.sensors.get_s3_pagination",
        return_value=[{"Contents": []}],
    )
    mocker.patch(
        "aemo_etl.factories.sensors.get_object_head_from_pages",
        return_value=_OBJECT_HEAD,
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=[_S3_OBJECT_KEY],
    )
    mocker.patch.object(
        AssetSelection,
        "resolve",
        return_value=frozenset([_ASSET_KEY]),
    )

    sensor_def = df_from_s3_keys_sensor(
        name="test_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/gbb",
        jobs=[
            define_asset_job(
                _TARGET_JOB_NAME,
                tags={"ecs/cpu": "1024", "ecs/memory": "8192"},
            )
        ],
    )
    context = _build_sensor_context(
        mocker,
        completed_runs=[
            _make_run(
                DagsterRunStatus.FAILURE,
                tags={"ecs/cpu": "512", "ecs/memory": "4096"},
            )
        ],
    )
    mock_s3 = _build_mock_s3(mocker)

    results: list[RunRequest] = list(sensor_def._raw_fn(context, s3=mock_s3))  # type: ignore[call-overload, arg-type]

    assert len(results) == 1
    assert results[0].job_name == _TARGET_JOB_NAME


def test_sensor_inner_bytes_cap(mocker: MockerFixture) -> None:
    """bytes_cap stops adding keys once exceeded."""
    many_keys = [f"bronze/gbb/file{i}.parquet" for i in range(5)]
    big_heads = {k: {"Size": 150_000_000} for k in many_keys}

    mocker.patch("aemo_etl.factories.sensors.get_s3_pagination", return_value=[{}])
    mocker.patch(
        "aemo_etl.factories.sensors.get_object_head_from_pages",
        return_value=big_heads,
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=many_keys,
    )
    mocker.patch.object(AssetSelection, "resolve", return_value=frozenset([_ASSET_KEY]))

    sensor_def = df_from_s3_keys_sensor(
        name="bytes_cap_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/gbb",
        bytes_cap=200_000_000,  # only room for 1 file at 150MB each
    )
    context = _build_sensor_context(mocker)
    mock_s3 = _build_mock_s3(mocker)

    results: list[RunRequest] = list(sensor_def._raw_fn(context, s3=mock_s3))  # type: ignore[call-overload, arg-type]
    assert len(results) == 1
    # Only 1 key fits under 200MB
    assert (
        len(
            results[0].run_config["ops"][_ASSET_KEY.to_python_identifier()]["config"][
                "s3_keys"
            ]
        )
        == 1
    )


def test_sensor_inner_files_cap(mocker: MockerFixture) -> None:
    """files_cap stops adding keys once file count exceeded."""
    many_keys = [f"bronze/gbb/file{i}.parquet" for i in range(5)]
    small_heads = {k: {"Size": 100} for k in many_keys}

    mocker.patch("aemo_etl.factories.sensors.get_s3_pagination", return_value=[{}])
    mocker.patch(
        "aemo_etl.factories.sensors.get_object_head_from_pages",
        return_value=small_heads,
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=many_keys,
    )
    mocker.patch.object(AssetSelection, "resolve", return_value=frozenset([_ASSET_KEY]))

    sensor_def = df_from_s3_keys_sensor(
        name="files_cap_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/gbb",
        files_cap=2,
    )
    context = _build_sensor_context(mocker)
    mock_s3 = _build_mock_s3(mocker)

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


def test_sensor_inner_suppresses_cap_selected_empty_keys(
    mocker: MockerFixture,
) -> None:
    """Matching S3 keys that caps exclude do not launch a no-op run."""
    mocker.patch("aemo_etl.factories.sensors.get_s3_pagination", return_value=[{}])
    mocker.patch(
        "aemo_etl.factories.sensors.get_object_head_from_pages",
        return_value={_S3_OBJECT_KEY: {"Size": 100}},
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=[_S3_OBJECT_KEY],
    )
    mocker.patch.object(AssetSelection, "resolve", return_value=frozenset([_ASSET_KEY]))

    sensor_def = df_from_s3_keys_sensor(
        name="cap_zero_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/gbb",
        bytes_cap=0,
    )
    context = _build_sensor_context(mocker)
    mock_s3 = _build_mock_s3(mocker)

    results: list[RunRequest] = list(sensor_def._raw_fn(context, s3=mock_s3))  # type: ignore[call-overload, arg-type]
    assert results == []


def test_sensor_inner_no_keys(mocker: MockerFixture) -> None:
    """No S3 keys → no RunRequest emitted."""
    mocker.patch("aemo_etl.factories.sensors.get_s3_pagination", return_value=[{}])
    mocker.patch(
        "aemo_etl.factories.sensors.get_object_head_from_pages",
        return_value={},
    )
    mocker.patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob",
        return_value=[],
    )
    mocker.patch.object(AssetSelection, "resolve", return_value=frozenset([_ASSET_KEY]))

    sensor_def = df_from_s3_keys_sensor(
        name="no_keys_sensor",
        asset_selection=AssetSelection.all(),
        s3_source_bucket="bucket",
        s3_source_prefix="bronze/gbb",
    )
    context = _build_sensor_context(mocker)
    mock_s3 = _build_mock_s3(mocker)
    results: list[RunRequest] = list(sensor_def._raw_fn(context, s3=mock_s3))  # type: ignore[call-overload, arg-type]
    assert results == []
