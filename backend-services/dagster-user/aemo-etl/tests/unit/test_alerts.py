"""Unit tests for failed-run alerts."""

from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from aemo_etl.alerts import (
    FAILED_RUN_ALERT_SUBJECT,
    MAX_FAILED_RUN_ALERT_MESSAGE_LENGTH,
    build_failed_run_alert_message,
    send_failed_run_alert,
)
from aemo_etl.configs import (
    DAGSTER_FAILURE_ALERT_BASE_URL_ENV_VAR,
    DAGSTER_FAILURE_ALERT_TOPIC_ARN_ENV_VAR,
)


def _build_context(mocker: MockerFixture) -> MagicMock:
    context = mocker.MagicMock()
    context.dagster_run.job_name = "daily_refresh"
    context.dagster_run.run_id = "run-123"
    context.failure_event.message = "Asset failed with ValueError"
    return context  # type: ignore[no-any-return]


def test_build_failed_run_alert_message_includes_failure_details(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    monkeypatch.setenv(
        DAGSTER_FAILURE_ALERT_BASE_URL_ENV_VAR,
        "https://example.test/dagster-webserver/admin/",
    )
    context = _build_context(mocker)

    message = build_failed_run_alert_message(context)

    assert "Dagster run failed" in message
    assert "Job: daily_refresh" in message
    assert "Run ID: run-123" in message
    assert "Error: Asset failed with ValueError" in message
    assert "Run: https://example.test/dagster-webserver/admin/runs/run-123" in message


def test_build_failed_run_alert_message_trims_long_messages(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    monkeypatch.delenv(DAGSTER_FAILURE_ALERT_BASE_URL_ENV_VAR, raising=False)
    context = _build_context(mocker)
    context.failure_event.message = "x" * 2_000

    message = build_failed_run_alert_message(context)

    assert len(message) == MAX_FAILED_RUN_ALERT_MESSAGE_LENGTH
    assert message.endswith("...")


def test_send_failed_run_alert_skips_when_topic_arn_missing(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    monkeypatch.delenv(DAGSTER_FAILURE_ALERT_TOPIC_ARN_ENV_VAR, raising=False)
    context = _build_context(mocker)
    sns_client = mocker.MagicMock()

    send_failed_run_alert(context, sns_client=sns_client)

    sns_client.publish.assert_not_called()
    context.log.warning.assert_called_once()


def test_send_failed_run_alert_publishes_to_sns(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    monkeypatch.setenv(
        DAGSTER_FAILURE_ALERT_TOPIC_ARN_ENV_VAR,
        "arn:aws:sns:ap-southeast-2:123456789012:dagster-failed-run-alerts",
    )
    context = _build_context(mocker)
    sns_client = mocker.MagicMock()

    send_failed_run_alert(context, sns_client=sns_client)

    sns_client.publish.assert_called_once()
    _, kwargs = sns_client.publish.call_args
    assert (
        kwargs["TopicArn"]
        == "arn:aws:sns:ap-southeast-2:123456789012:dagster-failed-run-alerts"
    )
    assert kwargs["Subject"] == FAILED_RUN_ALERT_SUBJECT
    assert "Job: daily_refresh" in kwargs["Message"]
    assert "Run ID: run-123" in kwargs["Message"]
    assert "Asset failed with ValueError" in kwargs["Message"]


def test_send_failed_run_alert_logs_and_raises_sns_errors(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    monkeypatch.setenv(
        DAGSTER_FAILURE_ALERT_TOPIC_ARN_ENV_VAR,
        "arn:aws:sns:ap-southeast-2:123456789012:dagster-failed-run-alerts",
    )
    context = _build_context(mocker)
    sns_client = mocker.MagicMock()
    sns_client.publish.side_effect = RuntimeError("sns unavailable")

    with pytest.raises(RuntimeError, match="sns unavailable"):
        send_failed_run_alert(context, sns_client=sns_client)

    context.log.exception.assert_called_once()
