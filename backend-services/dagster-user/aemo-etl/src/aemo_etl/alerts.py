"""Failed-run alert helpers for Dagster sensors."""

import os
from typing import Protocol

import boto3
from dagster import RunFailureSensorContext

from aemo_etl.configs import (
    DAGSTER_FAILURE_ALERT_BASE_URL_ENV_VAR,
    DAGSTER_FAILURE_ALERT_TOPIC_ARN_ENV_VAR,
)

MAX_FAILED_RUN_ALERT_MESSAGE_LENGTH = 1600
FAILED_RUN_ALERT_SUBJECT = "Dagster run failed"


class SnsClient(Protocol):
    """Protocol for the SNS client subset used by failed-run alerts."""

    def publish(self, *, TopicArn: str, Message: str, Subject: str) -> object:
        """Publish an SNS message."""
        ...


def _trim_failed_run_alert_message(message: str) -> str:
    if len(message) <= MAX_FAILED_RUN_ALERT_MESSAGE_LENGTH:
        return message
    return f"{message[: MAX_FAILED_RUN_ALERT_MESSAGE_LENGTH - 3]}..."


def _run_url(run_id: str) -> str | None:
    base_url = os.environ.get(DAGSTER_FAILURE_ALERT_BASE_URL_ENV_VAR, "").strip()
    if base_url == "":
        return None
    return f"{base_url.rstrip('/')}/runs/{run_id}"


def build_failed_run_alert_message(context: RunFailureSensorContext) -> str:
    """Build the alert body for a failed Dagster run."""
    dagster_run = context.dagster_run
    failure_message = context.failure_event.message or "No failure message available."
    message_lines = [
        "Dagster run failed",
        f"Job: {dagster_run.job_name}",
        f"Run ID: {dagster_run.run_id}",
        f"Error: {failure_message}",
    ]

    run_url = _run_url(dagster_run.run_id)
    if run_url is not None:
        message_lines.append(f"Run: {run_url}")

    return _trim_failed_run_alert_message("\n".join(message_lines))


def send_failed_run_alert(
    context: RunFailureSensorContext,
    sns_client: SnsClient | None = None,
) -> None:
    """Send a failed-run alert to SNS when alert configuration is present."""
    topic_arn = os.environ.get(DAGSTER_FAILURE_ALERT_TOPIC_ARN_ENV_VAR, "").strip()
    if topic_arn == "":
        context.log.warning(
            f"{DAGSTER_FAILURE_ALERT_TOPIC_ARN_ENV_VAR} is not set; skipping "
            f"failed-run alert for run {context.dagster_run.run_id}."
        )
        return

    client = sns_client if sns_client is not None else boto3.client("sns")
    message = build_failed_run_alert_message(context)

    try:
        client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=FAILED_RUN_ALERT_SUBJECT,
        )
    except Exception:
        context.log.exception(
            f"Failed to send failed-run alert for run {context.dagster_run.run_id}."
        )
        raise
