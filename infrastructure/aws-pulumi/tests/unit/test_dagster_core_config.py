"""Tests for the baked Dagster core AWS instance config."""

from pathlib import Path

from dagster_core_deployment import EC2_RUN_WORKERS_PROTOTYPE_CAPACITY_PROVIDER_NAME


def _dagster_core_config(filename: str) -> str:
    return (
        Path(__file__).resolve().parents[4]
        / "backend-services"
        / "dagster-core"
        / filename
    ).read_text(encoding="utf-8")


def _dagster_core_aws_config() -> str:
    return _dagster_core_config("dagster.aws.yaml")


def _dagster_core_ec2_run_workers_prototype_config() -> str:
    return _dagster_core_config("dagster.aws.ec2-run-workers.prototype.yaml")


def _dagster_core_dockerfile() -> str:
    return _dagster_core_config("Dockerfile")


def test_dagster_core_limits_run_concurrency_to_20() -> None:
    config = _dagster_core_aws_config()

    assert "max_concurrent_runs: 20" in config
    assert "max_concurrent_runs: 50" not in config


def test_dagster_core_uses_spot_fargate_run_workers() -> None:
    config = _dagster_core_aws_config()

    assert "capacityProviderStrategy:" in config
    assert 'capacityProvider: "FARGATE_SPOT"' in config
    assert 'capacityProvider: "FARGATE"\n' not in config
    assert "weight: 1" in config
    assert "base:" not in config


def test_dagster_core_has_ec2_run_workers_prototype_target() -> None:
    dockerfile = _dagster_core_dockerfile()

    assert "FROM base AS aws-ec2-run-workers-prototype" in dockerfile
    assert "dagster.aws.ec2-run-workers.prototype.yaml dagster.yaml" in dockerfile


def test_dagster_core_ec2_run_workers_prototype_uses_capacity_provider() -> None:
    config = _dagster_core_ec2_run_workers_prototype_config()

    assert (
        f'capacityProvider: "{EC2_RUN_WORKERS_PROTOTYPE_CAPACITY_PROVIDER_NAME}"'
        in config
    )
    assert 'capacityProvider: "FARGATE_SPOT"' not in config
    assert 'requires_compatibilities:\n        - "EC2"' in config
    assert 'type: "binpack"' in config
    assert 'field: "memory"' in config


def test_dagster_core_ec2_run_workers_prototype_sources_task_roles() -> None:
    config = _dagster_core_ec2_run_workers_prototype_config()

    assert "DAGSTER_ECS_LOG_GROUP_NAME" in config
    assert "DAGSTER_RUN_WORKER_EXECUTION_ROLE_ARN" in config
    assert "DAGSTER_RUN_WORKER_TASK_ROLE_ARN" in config
    assert "DAGSTER_POSTGRES_PASSWORD_PARAMETER_ARN" in config


def test_dagster_core_disables_default_secrets_manager_tag_lookup() -> None:
    config = _dagster_core_aws_config()

    assert "secrets_tag: null" in config


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
