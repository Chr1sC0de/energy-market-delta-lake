"""Unit tests for defs/testing.py."""

from typing import Any

import pytest
from dagster import AssetKey, Definitions
from pytest_mock import MockerFixture

from aemo_etl.defs.testing import (
    FAILED_RUN_ALERT_PROBE_ERROR,
    defs,
    failed_run_alert_probe,
)


def test_defs_testing_returns_definitions() -> None:
    d = defs()

    assert isinstance(d, Definitions)


def test_failed_run_alert_probe_registered() -> None:
    d = defs()
    assets: Any = d.assets or []
    asset_keys = {key for asset_definition in assets for key in asset_definition.keys}

    assert AssetKey(["ops", "testing", "failed_run_alert_probe"]) in asset_keys


def test_failed_run_alert_probe_fails_intentionally(
    mocker: MockerFixture,
) -> None:
    compute_fn: Any = failed_run_alert_probe.op.compute_fn
    fn: Any = compute_fn.decorated_fn
    context = mocker.MagicMock()

    with pytest.raises(RuntimeError, match=FAILED_RUN_ALERT_PROBE_ERROR):
        fn(context)

    context.log.warning.assert_called_once_with(FAILED_RUN_ALERT_PROBE_ERROR)
