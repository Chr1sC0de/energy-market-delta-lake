"""Tests for Dagster core deployment config contracts."""

import pytest

from dagster_core_deployment import (
    DEFAULT_DAGSTER_CORE_DEPLOYMENT,
    EC2_RUN_WORKERS_PROTOTYPE_CAPACITY_PROVIDER_NAME,
    EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT,
    run_worker_ec2_capacity_provider_name,
    validate_dagster_core_deployment_config,
)


def test_run_worker_ec2_capacity_provider_name_uses_stack_name() -> None:
    assert (
        run_worker_ec2_capacity_provider_name("test-energy-market")
        == "test-energy-market-run-worker-ec2"
    )


def test_ec2_run_workers_prototype_capacity_provider_name_is_dev_only() -> None:
    assert (
        EC2_RUN_WORKERS_PROTOTYPE_CAPACITY_PROVIDER_NAME
        == "dev-energy-market-run-worker-ec2"
    )


def test_dagster_core_deployment_config_accepts_default_pairing() -> None:
    validate_dagster_core_deployment_config(
        dagster_core_deployment=DEFAULT_DAGSTER_CORE_DEPLOYMENT,
        enable_ec2_run_worker_capacity_prototype=False,
        stack_name="test-energy-market",
    )


def test_dagster_core_deployment_config_accepts_dev_prototype_pairing() -> None:
    validate_dagster_core_deployment_config(
        dagster_core_deployment=EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT,
        enable_ec2_run_worker_capacity_prototype=True,
        stack_name="dev-energy-market",
    )


def test_dagster_core_deployment_config_rejects_unknown_target() -> None:
    with pytest.raises(ValueError, match="Unsupported Dagster core deployment"):
        validate_dagster_core_deployment_config(
            dagster_core_deployment="unknown",
            enable_ec2_run_worker_capacity_prototype=False,
            stack_name="dev-energy-market",
        )


def test_dagster_core_deployment_config_rejects_prototype_without_capacity() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "dagster_core_deployment='aws-ec2-run-workers-prototype' requires "
            "enable_ec2_run_worker_capacity_prototype=true"
        ),
    ):
        validate_dagster_core_deployment_config(
            dagster_core_deployment=EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT,
            enable_ec2_run_worker_capacity_prototype=False,
            stack_name="dev-energy-market",
        )


def test_dagster_core_deployment_config_rejects_capacity_without_prototype() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "enable_ec2_run_worker_capacity_prototype=true requires "
            "dagster_core_deployment='aws-ec2-run-workers-prototype'"
        ),
    ):
        validate_dagster_core_deployment_config(
            dagster_core_deployment=DEFAULT_DAGSTER_CORE_DEPLOYMENT,
            enable_ec2_run_worker_capacity_prototype=True,
            stack_name="dev-energy-market",
        )


def test_dagster_core_deployment_config_rejects_non_dev_prototype_stack() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "active stack name 'prod-energy-market' would create capacity "
            "provider 'prod-energy-market-run-worker-ec2'"
        ),
    ):
        validate_dagster_core_deployment_config(
            dagster_core_deployment=EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT,
            enable_ec2_run_worker_capacity_prototype=True,
            stack_name="prod-energy-market",
        )
