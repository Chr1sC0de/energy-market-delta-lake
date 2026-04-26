"""Unit tests for defs/sensors.py."""

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


def test_defs_sensors_returns_definitions() -> None:
    from aemo_etl.defs.sensors import defs

    d = defs()
    assert isinstance(d, Definitions)


def test_default_status_aws_branch(monkeypatch: object) -> None:
    """Cover the DefaultSensorStatus.RUNNING branch when DEVELOPMENT_LOCATION=aws."""

    monkeypatch.setenv("DEVELOPMENT_LOCATION", "aws")  # type: ignore[attr-defined]

    import aemo_etl.configs as _cfg
    import aemo_etl.defs.sensors as _sensors

    importlib.reload(_cfg)
    importlib.reload(_sensors)

    assert _cfg.DEFAULT_SENSOR_STATUS == DefaultSensorStatus.RUNNING

    # Restore
    monkeypatch.delenv("DEVELOPMENT_LOCATION", raising=False)  # type: ignore[attr-defined]
    importlib.reload(_cfg)
    importlib.reload(_sensors)


def test_event_driven_raw_sensor_byte_caps(mocker: MockerFixture) -> None:
    calls: list[dict[str, object]] = []

    def _df_from_s3_keys_sensor(**kwargs: object) -> object:
        calls.append(kwargs)
        return mocker.MagicMock()

    import aemo_etl.factories.sensors as df_from_s3_keys_sensors
    import aemo_etl.factories.unzipper.sensors as unzipper_sensors
    from aemo_etl.defs import sensors as sensors_module

    mocker.patch.object(
        df_from_s3_keys_sensors,
        "df_from_s3_keys_sensor",
        side_effect=_df_from_s3_keys_sensor,
    )
    mocker.patch.object(
        unzipper_sensors,
        "unzipper_sensor",
        return_value=mocker.MagicMock(),
    )
    mocker.patch.object(
        sensors_module,
        "Definitions",
        return_value=mocker.MagicMock(),
    )

    defs_load_fn: Any = getattr(sensors_module.defs, "load_fn")
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
    assert raw_sensor_calls["vicgas_event_driven_assets_sensor"]["bytes_cap"] == 250e6
    assert raw_sensor_calls["gbb_event_driven_assets_sensor"]["bytes_cap"] == 250e6


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

        assert len(sensors) == 1, module_name

        sensor = sensors[0]
        assert isinstance(sensor, AutomationConditionSensorDefinition), module_name
        assert sensor.name == f"{module_name}_sensor"
        asset_selection: Any = sensor.asset_selection
        assert asset_selection.__class__.__name__ == "KeysAssetSelection"
        assert asset_selection.selected_keys == [
            AssetKey(["silver", "gas_model", module_name])
        ]
