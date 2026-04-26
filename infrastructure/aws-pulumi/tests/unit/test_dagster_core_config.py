"""Tests for the baked Dagster core AWS instance config."""

from pathlib import Path


def _dagster_core_aws_config() -> str:
    return (
        Path(__file__).resolve().parents[4]
        / "backend-services"
        / "dagster-core"
        / "dagster.aws.yaml"
    ).read_text()


def test_dagster_core_limits_run_concurrency_to_50() -> None:
    config = _dagster_core_aws_config()

    assert "max_concurrent_runs: 50" in config


def test_dagster_core_uses_cost_optimized_ecs_run_resources() -> None:
    config = _dagster_core_aws_config()

    assert 'cpu: "256"' in config
    assert 'memory: "2048"' in config
