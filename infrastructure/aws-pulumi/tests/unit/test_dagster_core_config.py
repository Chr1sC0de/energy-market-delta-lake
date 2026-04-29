"""Tests for the baked Dagster core AWS instance config."""

from pathlib import Path


def _dagster_core_aws_config() -> str:
    return (
        Path(__file__).resolve().parents[4]
        / "backend-services"
        / "dagster-core"
        / "dagster.aws.yaml"
    ).read_text()


def test_dagster_core_limits_run_concurrency_to_20() -> None:
    config = _dagster_core_aws_config()

    assert "max_concurrent_runs: 20" in config
    assert "max_concurrent_runs: 50" not in config


def test_dagster_core_prefers_spot_run_workers_with_on_demand_fallback() -> None:
    config = _dagster_core_aws_config()

    assert "capacityProviderStrategy:" in config
    assert 'capacityProvider: "FARGATE_SPOT"' in config
    assert 'capacityProvider: "FARGATE"' in config
    assert "weight: 4" in config
    assert "weight: 1" in config
    assert "base:" not in config


def test_dagster_core_uses_cost_optimized_ecs_run_resources() -> None:
    config = _dagster_core_aws_config()

    assert 'cpu: "256"' in config
    assert 'memory: "2048"' in config


def test_dagster_core_detects_interrupted_workers_without_resume_attempts() -> None:
    config = _dagster_core_aws_config()

    assert "run_monitoring:" in config
    assert "enabled: true" in config
    assert "max_runtime_seconds: 1800" in config
    assert "start_timeout_seconds: 180" in config
    assert "cancel_timeout_seconds: 180" in config
    assert "max_resume_run_attempts: 0" in config
    assert "poll_interval_seconds: 120" in config
