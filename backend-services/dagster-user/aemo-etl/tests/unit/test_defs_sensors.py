"""Unit tests for defs/sensors.py."""

import importlib
from typing import Any

from dagster import DefaultSensorStatus, Definitions
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

    from aemo_etl.defs import sensors as sensors_module
    import aemo_etl.factories.sensors as df_from_s3_keys_sensors
    import aemo_etl.factories.unzipper.sensors as unzipper_sensors

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
        "AutomationConditionSensorDefinition",
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
