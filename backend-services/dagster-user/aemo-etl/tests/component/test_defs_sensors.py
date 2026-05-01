"""Unit tests for top-level sensor definitions."""

import importlib
from pathlib import Path
from typing import Any

from dagster import (
    AssetKey,
    AutomationConditionSensorDefinition,
    DefaultSensorStatus,
    Definitions,
)
from pytest_mock import MockerFixture


def test_definitions_returns_definitions() -> None:
    from aemo_etl.definitions import defs

    d = defs()
    assert isinstance(d, Definitions)


def test_failed_run_alert_sensor_registered() -> None:
    from aemo_etl.configs import DEFAULT_SENSOR_STATUS
    from aemo_etl.definitions import defs

    d = defs()
    sensors = {sensor.name: sensor for sensor in d.sensors or []}

    assert "aemo_etl_failed_run_alert_sensor" in sensors
    assert (
        sensors["aemo_etl_failed_run_alert_sensor"].default_status
        == DEFAULT_SENSOR_STATUS
    )


def test_failed_run_alert_sensor_invokes_alert_sender(mocker: MockerFixture) -> None:
    import aemo_etl.definitions as definitions_module

    context = mocker.MagicMock()
    send_alert = mocker.patch.object(definitions_module, "send_failed_run_alert")

    definitions_module.aemo_etl_failed_run_alert_sensor._run_status_sensor_fn(context)  # type: ignore[attr-defined]

    send_alert.assert_called_once_with(context)


def test_default_status_aws_branch(monkeypatch: object) -> None:
    """Cover the DefaultSensorStatus.RUNNING branch when DEVELOPMENT_LOCATION=aws."""

    monkeypatch.setenv("DEVELOPMENT_LOCATION", "aws")  # type: ignore[attr-defined]

    import aemo_etl.configs as _cfg
    import aemo_etl.definitions as _definitions

    importlib.reload(_cfg)
    importlib.reload(_definitions)

    assert _cfg.DEFAULT_SENSOR_STATUS == DefaultSensorStatus.RUNNING
    assert (
        _definitions.aemo_etl_failed_run_alert_sensor.default_status
        == DefaultSensorStatus.RUNNING
    )

    # Restore
    monkeypatch.delenv("DEVELOPMENT_LOCATION", raising=False)  # type: ignore[attr-defined]
    importlib.reload(_cfg)
    importlib.reload(_definitions)


def test_event_driven_raw_sensor_batch_caps(mocker: MockerFixture) -> None:
    calls: list[dict[str, object]] = []
    unzipper_calls: list[dict[str, object]] = []

    def _df_from_s3_keys_sensor(**kwargs: object) -> object:
        calls.append(kwargs)
        return mocker.MagicMock()

    def _unzipper_sensor(**kwargs: object) -> object:
        unzipper_calls.append(kwargs)
        return mocker.MagicMock()

    import aemo_etl.factories.sensors as df_from_s3_keys_sensors
    import aemo_etl.factories.unzipper.sensors as unzipper_sensors
    import aemo_etl.definitions as definitions_module

    jobs = [mocker.MagicMock()]
    loaded_definitions = mocker.MagicMock()
    loaded_definitions.jobs = jobs

    mocker.patch.object(
        df_from_s3_keys_sensors,
        "df_from_s3_keys_sensor",
        side_effect=_df_from_s3_keys_sensor,
    )
    mocker.patch.object(
        unzipper_sensors,
        "unzipper_sensor",
        side_effect=_unzipper_sensor,
    )
    mocker.patch.object(
        definitions_module,
        "load_from_defs_folder",
        return_value=loaded_definitions,
    )
    mocker.patch.object(
        definitions_module,
        "delta_table_maintenance_definitions_factory",
        return_value=mocker.MagicMock(),
    )
    mocker.patch.object(
        definitions_module,
        "Definitions",
        return_value=mocker.MagicMock(),
    )

    defs_load_fn: Any = getattr(definitions_module.defs, "load_fn")
    defs_load_fn()

    raw_sensor_calls = {
        str(call["name"]): call
        for call in calls
        if call["name"]
        in {
            "vicgas_event_driven_assets_sensor",
            "gbb_event_driven_assets_sensor",
        }
    }
    assert (
        raw_sensor_calls["vicgas_event_driven_assets_sensor"]["bytes_cap"]
        == 128_000_000
    )
    assert raw_sensor_calls["vicgas_event_driven_assets_sensor"]["files_cap"] == 25
    assert (
        raw_sensor_calls["gbb_event_driven_assets_sensor"]["bytes_cap"] == 128_000_000
    )
    assert raw_sensor_calls["gbb_event_driven_assets_sensor"]["files_cap"] == 25
    assert raw_sensor_calls["vicgas_event_driven_assets_sensor"]["jobs"] == tuple(jobs)
    assert raw_sensor_calls["gbb_event_driven_assets_sensor"]["jobs"] == tuple(jobs)
    assert unzipper_calls
    for call in unzipper_calls:
        assert "bytes_cap" not in call
        assert "files_cap" not in call


def test_gas_model_silver_modules_define_asset_targeted_automation_sensors() -> None:
    gas_model_dir = (
        Path(__file__).resolve().parents[2] / "src" / "aemo_etl" / "defs" / "gas_model"
    )
    module_names = sorted(path.stem for path in gas_model_dir.glob("silver_*.py"))

    assert module_names

    for module_name in module_names:
        module = importlib.import_module(f"aemo_etl.defs.gas_model.{module_name}")
        definitions = module.defs()
        sensors = list(definitions.sensors or [])

        if module_name == "silver_gas_dim_date":
            schedules = list(definitions.schedules or [])

            assert sensors == []
            assert len(schedules) == 1
            assert schedules[0].name == "silver_gas_dim_date_schedule"
            continue

        assert len(sensors) == 1, module_name

        sensor = sensors[0]
        assert isinstance(sensor, AutomationConditionSensorDefinition), module_name
        assert sensor.name == f"{module_name}_sensor"
        asset_selection: Any = sensor.asset_selection
        assert asset_selection.__class__.__name__ == "KeysAssetSelection"
        assert asset_selection.selected_keys == [
            AssetKey(["silver", "gas_model", module_name])
        ]
