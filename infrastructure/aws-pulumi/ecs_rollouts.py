"""ECS rollout completion helpers for the deployed AWS workflow."""

import argparse
import json
import os
import sys
import time
from collections.abc import Callable, Iterable, Mapping

from code_locations import required_ecs_service_names

RolloutDiagnostics = dict[str, dict[str, object]]

_COMPLETE_PRIMARY_ROLLOUT_STATE = "COMPLETED"
_FAILED_ROLLOUT_STATE = "FAILED"
_DEPLOYMENT_DIAGNOSTIC_FIELDS = (
    "desiredCount",
    "failedTasks",
    "id",
    "pendingCount",
    "rolloutState",
    "rolloutStateReason",
    "runningCount",
    "status",
    "taskDefinition",
)


class EcsRolloutWaitError(RuntimeError):
    """Raised when required ECS service rollouts cannot be confirmed."""

    def __init__(
        self,
        message: str,
        *,
        diagnostics: RolloutDiagnostics | None = None,
    ) -> None:
        """Create an error with already-sanitized service diagnostics."""
        super().__init__(message)
        self.diagnostics = diagnostics or {}


class EcsRolloutTimeoutError(EcsRolloutWaitError):
    """Raised when required ECS service rollouts do not finish in time."""


class EcsRolloutFailedError(EcsRolloutWaitError):
    """Raised when ECS reports a failed deployment rollout."""


def describe_required_ecs_services(
    ecs_client: object,
    *,
    cluster: str,
    service_names: Iterable[str],
) -> list[dict[str, object]]:
    """Describe all required ECS services or raise with describe diagnostics."""
    requested_names = tuple(service_names)
    response = ecs_client.describe_services(  # type: ignore[attr-defined]
        cluster=cluster,
        services=list(requested_names),
    )
    failures = response.get("failures", [])
    if failures:
        raise EcsRolloutWaitError(
            f"Failed to describe required ECS services: {failures}"
        )

    services = response.get("services", [])
    service_names_seen = {
        service["serviceName"]
        for service in services
        if isinstance(service, dict) and "serviceName" in service
    }
    missing = set(requested_names) - service_names_seen
    if missing:
        raise EcsRolloutWaitError(
            f"Missing required ECS services: {sorted(missing)}",
            diagnostics=ecs_service_rollout_diagnostics(services),
        )

    return services


def ecs_service_rollout_diagnostics(
    services: Iterable[Mapping[str, object]],
) -> RolloutDiagnostics:
    """Return sanitized rollout diagnostics keyed by ECS service name."""
    diagnostics: RolloutDiagnostics = {}
    for service in services:
        service_name = service.get("serviceName")
        if not isinstance(service_name, str):
            continue

        deployments = _service_deployments(service)
        primary: Mapping[str, object] | None = next(
            (
                deployment
                for deployment in deployments
                if deployment.get("status") == "PRIMARY"
            ),
            None,
        )
        primary_state = None if primary is None else primary.get("rolloutState")
        failed = [
            _deployment_diagnostic_state(deployment)
            for deployment in deployments
            if deployment.get("rolloutState") == _FAILED_ROLLOUT_STATE
        ]
        diagnostics[service_name] = {
            "primary": primary_state if isinstance(primary_state, str) else None,
            "failed": failed,
        }
    return diagnostics


def incomplete_ecs_service_rollouts(
    services: Iterable[Mapping[str, object]],
) -> RolloutDiagnostics:
    """Return services whose primary rollout is incomplete or failed."""
    diagnostics = ecs_service_rollout_diagnostics(services)
    return {
        service_name: diagnostic
        for service_name, diagnostic in diagnostics.items()
        if diagnostic["primary"] != _COMPLETE_PRIMARY_ROLLOUT_STATE
        or diagnostic["failed"] != []
    }


def wait_for_ecs_service_rollouts(
    ecs_client: object,
    *,
    cluster: str,
    service_names: Iterable[str],
    timeout_seconds: int,
    poll_seconds: int,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
) -> RolloutDiagnostics:
    """Wait until required ECS service primary deployments are completed."""
    if timeout_seconds < 0:
        raise ValueError("timeout_seconds must be greater than or equal to 0")
    if poll_seconds <= 0:
        raise ValueError("poll_seconds must be greater than 0")

    requested_names = tuple(service_names)
    deadline = monotonic() + timeout_seconds
    while True:
        services = describe_required_ecs_services(
            ecs_client,
            cluster=cluster,
            service_names=requested_names,
        )
        diagnostics = ecs_service_rollout_diagnostics(services)
        incomplete = incomplete_ecs_service_rollouts(services)
        failed = {
            service_name: diagnostic
            for service_name, diagnostic in incomplete.items()
            if diagnostic["failed"] != []
        }
        if not incomplete:
            return diagnostics
        if failed:
            raise EcsRolloutFailedError(
                "ECS service rollout failed.",
                diagnostics=diagnostics,
            )

        remaining_seconds = deadline - monotonic()
        if remaining_seconds <= 0:
            raise EcsRolloutTimeoutError(
                f"ECS service rollout completion timed out after {timeout_seconds}s.",
                diagnostics=diagnostics,
            )
        sleep(min(float(poll_seconds), remaining_seconds))


def format_rollout_diagnostics(diagnostics: Mapping[str, object]) -> str:
    """Format sanitized ECS rollout diagnostics for command output."""
    lines = ["ECS rollout diagnostics:"]
    for service_name in sorted(diagnostics):
        diagnostic = diagnostics[service_name]
        if not isinstance(diagnostic, dict):
            continue
        primary = diagnostic.get("primary")
        primary_label = "<missing>" if primary is None else str(primary)
        failed = diagnostic.get("failed", [])
        failed_json = json.dumps(failed, default=str, sort_keys=True)
        lines.append(
            f"  - {service_name}: primary={primary_label}; failed={failed_json}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Run the ECS rollout completion waiter CLI."""
    parser = argparse.ArgumentParser(
        description="Wait for required ECS service primary rollouts to complete.",
    )
    parser.add_argument("--cluster", required=True)
    parser.add_argument("--resource-name")
    parser.add_argument("--services", nargs="+")
    parser.add_argument(
        "--timeout-seconds",
        type=_non_negative_int,
        default=900,
    )
    parser.add_argument(
        "--poll-seconds",
        type=_positive_int,
        default=15,
    )
    args = parser.parse_args(argv)

    service_names = tuple(args.services or ())
    if not service_names:
        if args.resource_name is None:
            parser.error("--services or --resource-name is required")
        service_names = required_ecs_service_names(args.resource_name)

    import boto3

    ecs_client = boto3.client(
        "ecs",
        region_name=os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-2"),
    )
    try:
        diagnostics = wait_for_ecs_service_rollouts(
            ecs_client,
            cluster=args.cluster,
            service_names=service_names,
            timeout_seconds=args.timeout_seconds,
            poll_seconds=args.poll_seconds,
        )
    except EcsRolloutWaitError as exc:
        print(str(exc), file=sys.stderr)
        print(format_rollout_diagnostics(exc.diagnostics), file=sys.stderr)
        return 1

    print("ECS rollout completion confirmed:")
    print(format_rollout_diagnostics(diagnostics))
    return 0


def _service_deployments(
    service: Mapping[str, object],
) -> list[Mapping[str, object]]:
    deployments = service.get("deployments", [])
    if not isinstance(deployments, list):
        return []
    return [deployment for deployment in deployments if isinstance(deployment, Mapping)]


def _deployment_diagnostic_state(
    deployment: Mapping[str, object],
) -> dict[str, object]:
    return {
        field: deployment[field]
        for field in _DEPLOYMENT_DIAGNOSTIC_FIELDS
        if field in deployment
    }


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be greater than or equal to 0")
    return parsed


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than 0")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
