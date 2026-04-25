"""Unit tests for defs/sensors.py."""

import importlib

from dagster import DefaultSensorStatus, Definitions


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
