from typing import Sequence
from unittest.mock import MagicMock, patch

from dagster import (
    AssetKey,
    AssetsDefinition,
    AssetSelection,
    RunRequest,
    SensorDefinition,
)

from aemo_etl.factories.sensors import (
    df_from_s3_keys_sensor,
    is_running,
)

MODULE = "aemo_etl.factories.sensors"

ASSET_KEY = AssetKey(["bronze", "vicgas", "int_some_table"])
ASSET_SELECTION = AssetSelection.assets(ASSET_KEY)


def _make_run(asset_keys: list[AssetKey] | None) -> MagicMock:
    run = MagicMock()
    run.asset_selection = set(asset_keys) if asset_keys is not None else None
    return run


def _make_asset_def(
    asset_key: AssetKey, glob_pattern: str = "*.csv"
) -> AssetsDefinition:
    """Real-enough AssetsDefinition mock that satisfies sensor assertions."""
    asset_def = MagicMock(spec=AssetsDefinition)
    asset_def.key = asset_key
    asset_def.keys = {asset_key}
    asset_def.metadata_by_key = {asset_key: {"glob_pattern": glob_pattern}}
    return asset_def


def _make_context(
    asset_key: AssetKey,
    runs: Sequence[MagicMock] = (),
    glob_pattern: str = "*.csv",
) -> MagicMock:
    """Minimal SensorEvaluationContext mock for a single asset."""
    asset_def = _make_asset_def(asset_key, glob_pattern)

    # Use a real dict so .values() works naturally (AssetSelection.resolve iterates it)
    assets_defs_by_key = {asset_key: asset_def}

    repo = MagicMock()
    repo.assets_defs_by_key = assets_defs_by_key

    ctx = MagicMock()
    ctx.repository_def = repo
    ctx.instance.get_runs.return_value = list(runs)
    return ctx


def _make_s3() -> MagicMock:
    s3 = MagicMock()
    s3.get_client.return_value = MagicMock()
    return s3


def _sensor_fn(
    sensor_def: SensorDefinition, context: MagicMock, s3: MagicMock
) -> list[RunRequest]:
    result = sensor_def._raw_fn(context, s3=s3)  # type: ignore[attr-defined]
    return [r for r in result if isinstance(r, RunRequest)]  # type: ignore[union-attr]


def _make_sensor(bytes_cap: float = 200e6) -> SensorDefinition:
    return df_from_s3_keys_sensor(
        name="test_sensor",
        asset_selection=ASSET_SELECTION,
        s3_source_bucket="bucket",
        s3_source_prefix="prefix",
        bytes_cap=bytes_cap,
    )


# ---------------------------------------------------------------------------
# is_running
# ---------------------------------------------------------------------------


def test_is_running_true_when_asset_in_run() -> None:
    run = _make_run([ASSET_KEY])
    assert is_running([run], ASSET_KEY) is True


def test_is_running_false_when_asset_not_in_run() -> None:
    run = _make_run([AssetKey(["other"])])
    assert is_running([run], ASSET_KEY) is False


def test_is_running_false_when_no_asset_selection() -> None:
    run = _make_run(None)
    assert is_running([run], ASSET_KEY) is False


# ---------------------------------------------------------------------------
# factory
# ---------------------------------------------------------------------------


def test_factory_returns_sensor_definition() -> None:
    assert isinstance(_make_sensor(), SensorDefinition)


@patch(
    f"{MODULE}.get_s3_object_keys_from_prefix_and_name_glob",
    return_value=["prefix/a.csv"],
)
@patch(
    f"{MODULE}.get_object_head_from_pages", return_value={"prefix/a.csv": {"Size": 100}}
)
@patch(f"{MODULE}.get_s3_pagination")
def test_sensor_yields_run_request(
    _pages: MagicMock, _heads: MagicMock, _keys: MagicMock
) -> None:
    ctx = _make_context(ASSET_KEY)
    results = _sensor_fn(_make_sensor(), ctx, _make_s3())

    assert len(results) == 1
    run_req = results[0]
    assert isinstance(run_req, RunRequest)
    s3_keys = run_req.run_config["ops"][ASSET_KEY.to_python_identifier()]["config"][
        "s3_keys"
    ]
    assert s3_keys == ["prefix/a.csv"]


@patch(
    f"{MODULE}.get_s3_object_keys_from_prefix_and_name_glob",
    return_value=["prefix/a.csv"],
)
@patch(
    f"{MODULE}.get_object_head_from_pages", return_value={"prefix/a.csv": {"Size": 100}}
)
@patch(f"{MODULE}.get_s3_pagination")
def test_sensor_skips_when_already_running(
    _pages: MagicMock, _heads: MagicMock, _keys: MagicMock
) -> None:
    active_run = _make_run([ASSET_KEY])
    ctx = _make_context(ASSET_KEY, runs=[active_run])
    results = _sensor_fn(_make_sensor(), ctx, _make_s3())

    assert results == []


@patch(
    f"{MODULE}.get_s3_object_keys_from_prefix_and_name_glob",
    return_value=["prefix/a.csv", "prefix/b.csv"],
)
@patch(
    f"{MODULE}.get_object_head_from_pages",
    return_value={"prefix/a.csv": {"Size": 150}, "prefix/b.csv": {"Size": 150}},
)
@patch(f"{MODULE}.get_s3_pagination")
def test_sensor_respects_bytes_cap(
    _pages: MagicMock, _heads: MagicMock, _keys: MagicMock
) -> None:
    ctx = _make_context(ASSET_KEY)
    results = _sensor_fn(_make_sensor(bytes_cap=200), ctx, _make_s3())

    assert len(results) == 1
    s3_keys = results[0].run_config["ops"][ASSET_KEY.to_python_identifier()]["config"][
        "s3_keys"
    ]
    assert s3_keys == ["prefix/a.csv"]


@patch(f"{MODULE}.get_s3_object_keys_from_prefix_and_name_glob", return_value=[])
@patch(f"{MODULE}.get_object_head_from_pages", return_value={})
@patch(f"{MODULE}.get_s3_pagination")
def test_sensor_yields_nothing_when_no_keys(
    _pages: MagicMock, _heads: MagicMock, _keys: MagicMock
) -> None:
    ctx = _make_context(ASSET_KEY)
    results = _sensor_fn(_make_sensor(), ctx, _make_s3())

    assert results == []
