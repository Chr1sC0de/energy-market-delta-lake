from unittest.mock import MagicMock, patch

import pytest
from dagster import AssetKey, DagsterRunStatus, RunRequest

from aemo_etl.factories.s3_pending_objects import (
    build_s3_pending_objects_job_run_request,
    build_s3_pending_objects_run_request,
    build_s3_keys_run_config,
    get_asset_glob_pattern,
    has_asset_failed,
    has_job_failed,
    is_asset_running,
    is_job_running,
    plan_s3_pending_objects_job_run_request,
    plan_s3_pending_objects_run_request,
    select_s3_pending_object_keys,
)
from aemo_etl.utils import S3ObjectHead

_ASSET_KEY = AssetKey(["bronze", "vicgas", "unzipper_vicgas"])
_ZIP_KEY = "bronze/vicgas/data.zip"
_JOB_NAME = "unzipper_vicgas_job"


def _make_run(
    status: DagsterRunStatus,
    asset_key: AssetKey | None = _ASSET_KEY,
    job_name: str = _JOB_NAME,
) -> MagicMock:
    run = MagicMock()
    run.asset_selection = {asset_key} if asset_key is not None else None
    run.status = status
    run.job_name = job_name
    return run


def _build_context(glob_pattern: str | None = "*.zip") -> MagicMock:
    context = MagicMock()
    mock_asset_defs = MagicMock()
    mock_asset_defs.metadata_by_key.get.return_value = (
        {"glob_pattern": glob_pattern} if glob_pattern is not None else {}
    )
    context.repository_def.assets_defs_by_key = {_ASSET_KEY: mock_asset_defs}
    return context  # type: ignore[no-any-return]


def test_is_asset_running_found() -> None:
    assert is_asset_running([_make_run(DagsterRunStatus.STARTED)], _ASSET_KEY) is True


def test_is_asset_running_ignores_other_assets_and_unselected_runs() -> None:
    other = AssetKey(["bronze", "other"])
    assert (
        is_asset_running([_make_run(DagsterRunStatus.STARTED, other)], _ASSET_KEY)
        is False
    )
    assert (
        is_asset_running([_make_run(DagsterRunStatus.STARTED, None)], _ASSET_KEY)
        is False
    )


def test_has_asset_failed_uses_most_recent_matching_completed_run() -> None:
    assert has_asset_failed([_make_run(DagsterRunStatus.FAILURE)], _ASSET_KEY) is True
    assert has_asset_failed([_make_run(DagsterRunStatus.SUCCESS)], _ASSET_KEY) is False


def test_has_asset_failed_ignores_other_assets_and_unselected_runs() -> None:
    other = AssetKey(["bronze", "other"])
    assert (
        has_asset_failed([_make_run(DagsterRunStatus.FAILURE, other)], _ASSET_KEY)
        is False
    )
    assert (
        has_asset_failed([_make_run(DagsterRunStatus.FAILURE, None)], _ASSET_KEY)
        is False
    )


def test_is_job_running_matches_job_name() -> None:
    assert is_job_running([_make_run(DagsterRunStatus.STARTED)], _JOB_NAME) is True
    assert (
        is_job_running(
            [_make_run(DagsterRunStatus.STARTED, job_name="other_job")], _JOB_NAME
        )
        is False
    )


def test_has_job_failed_matches_job_name() -> None:
    assert has_job_failed([_make_run(DagsterRunStatus.FAILURE)], _JOB_NAME) is True
    assert has_job_failed([_make_run(DagsterRunStatus.SUCCESS)], _JOB_NAME) is False
    assert (
        has_job_failed(
            [_make_run(DagsterRunStatus.FAILURE, job_name="other_job")], _JOB_NAME
        )
        is False
    )


def test_get_asset_glob_pattern_reads_asset_metadata() -> None:
    context = _build_context(glob_pattern="*.ZIP")

    assert (
        get_asset_glob_pattern(
            context,
            sensor_name="test_sensor",
            asset_key=_ASSET_KEY,
        )
        == "*.ZIP"
    )


def test_get_asset_glob_pattern_requires_metadata() -> None:
    context = _build_context(glob_pattern=None)

    with pytest.raises(AssertionError, match="missing 'glob_pattern' metadata"):
        get_asset_glob_pattern(
            context,
            sensor_name="test_sensor",
            asset_key=_ASSET_KEY,
        )


def test_select_s3_pending_object_keys_matches_glob_and_byte_cap() -> None:
    object_head_mapping: dict[str, S3ObjectHead] = {
        "bronze/vicgas/a.zip": {"Size": 100},
        "bronze/vicgas/b.zip": {"Size": 100},
        "bronze/vicgas/c.txt": {"Size": 1},
    }

    assert select_s3_pending_object_keys(
        s3_source_prefix="bronze/vicgas",
        s3_file_glob="*.zip",
        object_head_mapping=object_head_mapping,
        bytes_cap=150,
        files_cap=None,
    ) == ["bronze/vicgas/a.zip"]


def test_select_s3_pending_object_keys_applies_file_cap() -> None:
    object_head_mapping: dict[str, S3ObjectHead] = {
        "bronze/vicgas/a.zip": {"Size": 100},
        "bronze/vicgas/b.zip": {"Size": 100},
        "bronze/vicgas/c.zip": {"Size": 100},
    }

    assert select_s3_pending_object_keys(
        s3_source_prefix="bronze/vicgas",
        s3_file_glob="*.zip",
        object_head_mapping=object_head_mapping,
        bytes_cap=1_000,
        files_cap=2,
    ) == ["bronze/vicgas/a.zip", "bronze/vicgas/b.zip"]


def test_build_s3_keys_run_config_targets_asset_config() -> None:
    run_config = build_s3_keys_run_config(
        asset_key=_ASSET_KEY,
        s3_keys=[_ZIP_KEY],
    )

    assert run_config == {
        "ops": {
            _ASSET_KEY.to_python_identifier(): {
                "config": {
                    "s3_keys": [_ZIP_KEY],
                },
            },
        },
    }


def test_build_s3_pending_objects_run_request_suppresses_empty_selection() -> None:
    assert (
        build_s3_pending_objects_run_request(asset_key=_ASSET_KEY, s3_keys=[]) is None
    )


def test_build_s3_pending_objects_run_request_targets_asset_selection() -> None:
    run_request = build_s3_pending_objects_run_request(
        asset_key=_ASSET_KEY,
        s3_keys=[_ZIP_KEY],
    )

    assert isinstance(run_request, RunRequest)
    assert run_request.asset_selection == [_ASSET_KEY]
    assert run_request.run_config["ops"][_ASSET_KEY.to_python_identifier()]["config"][
        "s3_keys"
    ] == [_ZIP_KEY]


def test_build_s3_pending_objects_job_run_request_targets_job_name() -> None:
    run_request = build_s3_pending_objects_job_run_request(
        asset_key=_ASSET_KEY,
        job_name=_JOB_NAME,
        s3_keys=[_ZIP_KEY],
    )

    assert isinstance(run_request, RunRequest)
    assert run_request.job_name == _JOB_NAME
    assert run_request.run_config["ops"][_ASSET_KEY.to_python_identifier()]["config"][
        "s3_keys"
    ] == [_ZIP_KEY]


def test_plan_s3_pending_objects_run_request_gates_active_asset_runs() -> None:
    context = _build_context()

    with patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob"
    ) as match_keys:
        run_request = plan_s3_pending_objects_run_request(
            context,
            sensor_name="test_sensor",
            asset_key=_ASSET_KEY,
            active_runs=[_make_run(DagsterRunStatus.STARTED)],
            completed_runs=[],
            s3_source_prefix="bronze/vicgas",
            object_head_mapping={_ZIP_KEY: {"Size": 100}},
            bytes_cap=500,
            files_cap=None,
        )

    assert run_request is None
    match_keys.assert_not_called()


def test_plan_s3_pending_objects_run_request_gates_failed_asset_runs() -> None:
    context = _build_context()

    run_request = plan_s3_pending_objects_run_request(
        context,
        sensor_name="test_sensor",
        asset_key=_ASSET_KEY,
        active_runs=[],
        completed_runs=[_make_run(DagsterRunStatus.FAILURE)],
        s3_source_prefix="bronze/vicgas",
        object_head_mapping={_ZIP_KEY: {"Size": 100}},
        bytes_cap=500,
        files_cap=None,
    )

    assert run_request is None


def test_plan_s3_pending_objects_run_request_suppresses_cap_selected_empty_keys() -> (
    None
):
    context = _build_context()

    run_request = plan_s3_pending_objects_run_request(
        context,
        sensor_name="test_sensor",
        asset_key=_ASSET_KEY,
        active_runs=[],
        completed_runs=[],
        s3_source_prefix="bronze/vicgas",
        object_head_mapping={_ZIP_KEY: {"Size": 100}},
        bytes_cap=0,
        files_cap=None,
    )

    assert run_request is None


def test_plan_s3_pending_objects_run_request_builds_request_for_pending_keys() -> None:
    context = _build_context()

    run_request = plan_s3_pending_objects_run_request(
        context,
        sensor_name="test_sensor",
        asset_key=_ASSET_KEY,
        active_runs=[],
        completed_runs=[],
        s3_source_prefix="bronze/vicgas",
        object_head_mapping={_ZIP_KEY: {"Size": 100}},
        bytes_cap=500,
        files_cap=None,
    )

    assert isinstance(run_request, RunRequest)
    assert run_request.asset_selection == [_ASSET_KEY]
    assert run_request.run_config["ops"][_ASSET_KEY.to_python_identifier()]["config"][
        "s3_keys"
    ] == [_ZIP_KEY]


def test_plan_s3_pending_objects_job_run_request_gates_active_job_runs() -> None:
    context = _build_context()

    with patch(
        "aemo_etl.factories.s3_pending_objects.get_s3_object_keys_from_prefix_and_name_glob"
    ) as match_keys:
        run_request = plan_s3_pending_objects_job_run_request(
            context,
            sensor_name="test_sensor",
            asset_key=_ASSET_KEY,
            job_name=_JOB_NAME,
            active_runs=[_make_run(DagsterRunStatus.STARTED)],
            completed_runs=[],
            s3_source_prefix="bronze/vicgas",
            object_head_mapping={_ZIP_KEY: {"Size": 100}},
            bytes_cap=500,
            files_cap=None,
        )

    assert run_request is None
    match_keys.assert_not_called()


def test_plan_s3_pending_objects_job_run_request_suppresses_cap_selected_empty_keys() -> (
    None
):
    context = _build_context()

    run_request = plan_s3_pending_objects_job_run_request(
        context,
        sensor_name="test_sensor",
        asset_key=_ASSET_KEY,
        job_name=_JOB_NAME,
        active_runs=[],
        completed_runs=[],
        s3_source_prefix="bronze/vicgas",
        object_head_mapping={_ZIP_KEY: {"Size": 100}},
        bytes_cap=0,
        files_cap=None,
    )

    assert run_request is None


def test_plan_s3_pending_objects_job_run_request_builds_job_request() -> None:
    context = _build_context()

    run_request = plan_s3_pending_objects_job_run_request(
        context,
        sensor_name="test_sensor",
        asset_key=_ASSET_KEY,
        job_name=_JOB_NAME,
        active_runs=[],
        completed_runs=[],
        s3_source_prefix="bronze/vicgas",
        object_head_mapping={_ZIP_KEY: {"Size": 100}},
        bytes_cap=500,
        files_cap=None,
    )

    assert isinstance(run_request, RunRequest)
    assert run_request.job_name == _JOB_NAME
    assert run_request.run_config["ops"][_ASSET_KEY.to_python_identifier()]["config"][
        "s3_keys"
    ] == [_ZIP_KEY]
