"""Tests for ECS rollout completion helpers."""

import pytest

from ecs_rollouts import (
    EcsRolloutFailedError,
    EcsRolloutTimeoutError,
    incomplete_ecs_service_rollouts,
    wait_for_ecs_service_rollouts,
)


class FakeEcsClient:
    def __init__(self, responses: list[dict[str, object]]) -> None:
        self._responses = responses
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def describe_services(
        self,
        *,
        cluster: str,
        services: list[str],
    ) -> dict[str, object]:
        self.calls.append((cluster, tuple(services)))
        if len(self._responses) > 1:
            return self._responses.pop(0)
        return self._responses[0]


class FakeClock:
    def __init__(self) -> None:
        self.current = 0.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.current

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.current += seconds


def _service(
    service_name: str,
    primary_state: str,
    *,
    failed: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    deployments: list[dict[str, object]] = [
        {
            "id": f"ecs-svc/{service_name}/primary",
            "status": "PRIMARY",
            "rolloutState": primary_state,
            "taskDefinition": f"arn:aws:ecs:::task-definition/{service_name}:1",
            "desiredCount": 1,
            "runningCount": 1,
            "pendingCount": 0,
        }
    ]
    if failed is not None:
        deployments.extend(failed)
    return {"serviceName": service_name, "deployments": deployments}


def _response(*services: dict[str, object]) -> dict[str, object]:
    return {"services": list(services)}


def test_incomplete_ecs_service_rollouts_requires_completed_primary() -> None:
    diagnostics = incomplete_ecs_service_rollouts(
        [
            _service("complete", "COMPLETED"),
            _service("in-progress", "IN_PROGRESS"),
        ]
    )

    assert diagnostics == {"in-progress": {"primary": "IN_PROGRESS", "failed": []}}


def test_wait_for_ecs_service_rollouts_returns_after_completed_primary() -> None:
    client = FakeEcsClient([_response(_service("svc-a", "COMPLETED"))])
    clock = FakeClock()

    diagnostics = wait_for_ecs_service_rollouts(
        client,
        cluster="cluster-a",
        service_names=("svc-a",),
        timeout_seconds=60,
        poll_seconds=5,
        monotonic=clock.monotonic,
        sleep=clock.sleep,
    )

    assert diagnostics == {"svc-a": {"primary": "COMPLETED", "failed": []}}
    assert client.calls == [("cluster-a", ("svc-a",))]
    assert clock.sleeps == []


def test_wait_for_ecs_service_rollouts_polls_in_progress_until_complete() -> None:
    client = FakeEcsClient(
        [
            _response(_service("svc-a", "IN_PROGRESS")),
            _response(_service("svc-a", "COMPLETED")),
        ]
    )
    clock = FakeClock()

    wait_for_ecs_service_rollouts(
        client,
        cluster="cluster-a",
        service_names=("svc-a",),
        timeout_seconds=60,
        poll_seconds=5,
        monotonic=clock.monotonic,
        sleep=clock.sleep,
    )

    assert client.calls == [("cluster-a", ("svc-a",)), ("cluster-a", ("svc-a",))]
    assert clock.sleeps == [5]


def test_wait_for_ecs_service_rollouts_times_out_with_diagnostics() -> None:
    client = FakeEcsClient([_response(_service("svc-a", "IN_PROGRESS"))])
    clock = FakeClock()

    with pytest.raises(EcsRolloutTimeoutError) as exc_info:
        wait_for_ecs_service_rollouts(
            client,
            cluster="cluster-a",
            service_names=("svc-a",),
            timeout_seconds=0,
            poll_seconds=5,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

    assert exc_info.value.diagnostics == {
        "svc-a": {"primary": "IN_PROGRESS", "failed": []}
    }
    assert clock.sleeps == []


def test_wait_for_ecs_service_rollouts_fails_fast_on_failed_rollout() -> None:
    failed_deployment: dict[str, object] = {
        "id": "ecs-svc/svc-a/failed",
        "status": "ACTIVE",
        "rolloutState": "FAILED",
        "rolloutStateReason": "ECS deployment circuit breaker failed",
        "taskDefinition": "arn:aws:ecs:::task-definition/svc-a:2",
        "desiredCount": 1,
        "runningCount": 0,
        "pendingCount": 0,
        "environment": [{"name": "POSTGRES_PASSWORD", "value": "secret"}],
    }
    client = FakeEcsClient(
        [
            _response(
                _service("svc-a", "IN_PROGRESS", failed=[failed_deployment]),
            )
        ]
    )
    clock = FakeClock()

    with pytest.raises(EcsRolloutFailedError) as exc_info:
        wait_for_ecs_service_rollouts(
            client,
            cluster="cluster-a",
            service_names=("svc-a",),
            timeout_seconds=60,
            poll_seconds=5,
            monotonic=clock.monotonic,
            sleep=clock.sleep,
        )

    assert exc_info.value.diagnostics == {
        "svc-a": {
            "primary": "IN_PROGRESS",
            "failed": [
                {
                    "desiredCount": 1,
                    "id": "ecs-svc/svc-a/failed",
                    "pendingCount": 0,
                    "rolloutState": "FAILED",
                    "rolloutStateReason": "ECS deployment circuit breaker failed",
                    "runningCount": 0,
                    "status": "ACTIVE",
                    "taskDefinition": "arn:aws:ecs:::task-definition/svc-a:2",
                }
            ],
        }
    }
    assert clock.sleeps == []
