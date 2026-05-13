"""Tests for EcsClusterComponentResource."""

import base64
import warnings

import pulumi

from components.ecs_cluster import (
    RUN_WORKER_EC2_ASG_MAX_SIZE,
    RUN_WORKER_EC2_CAPACITY_PROVIDER_SUFFIX,
    RUN_WORKER_EC2_INSTANCE_TYPE,
    RUN_WORKER_EC2_ROOT_VOLUME_GB,
    EcsClusterComponentResource,
)
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


def _make_deps() -> tuple[VpcComponentResource, SecurityGroupsComponentResource]:
    vpc = VpcComponentResource("test-energy-market")
    sgs = SecurityGroupsComponentResource("test-energy-market", vpc)
    return vpc, sgs


class TestEcsClusterComponent:
    def test_cluster_created(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource("test-energy-market", vpc, sgs)
        assert cluster.cluster is not None

    @pulumi.runtime.test
    def test_cluster_registers_fargate_and_spot_capacity_providers(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource("test-energy-market", vpc, sgs)

        def check(providers: list[str]) -> None:
            assert providers == ["FARGATE", "FARGATE_SPOT"]

        return cluster.capacity_providers.capacity_providers.apply(check)

    @pulumi.runtime.test
    def test_ec2_run_worker_prototype_adds_capacity_provider(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource(
            "test-energy-market",
            vpc,
            sgs,
            enable_ec2_run_worker_capacity_prototype=True,
            run_worker_instance_profile_arn="arn:aws:iam::123456789012:instance-profile/test-energy-market-ecs-instance-profile",
        )

        def check(providers: list[str]) -> None:
            assert providers == [
                "FARGATE",
                "FARGATE_SPOT",
                f"test-energy-market-{RUN_WORKER_EC2_CAPACITY_PROVIDER_SUFFIX}",
            ]

        return cluster.capacity_providers.capacity_providers.apply(check)

    @pulumi.runtime.test
    def test_cluster_default_capacity_provider_uses_spot(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource("test-energy-market", vpc, sgs)

        def check(strategies: list) -> None:
            assert len(strategies) == 1
            assert strategies[0].get("capacity_provider") == "FARGATE_SPOT"
            assert strategies[0].get("weight") == 1

        return cluster.capacity_providers.default_capacity_provider_strategies.apply(
            check
        )

    @pulumi.runtime.test
    def test_ec2_run_worker_prototype_preserves_spot_default_strategy(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource(
            "test-energy-market",
            vpc,
            sgs,
            enable_ec2_run_worker_capacity_prototype=True,
            run_worker_instance_profile_arn="arn:aws:iam::123456789012:instance-profile/test-energy-market-ecs-instance-profile",
        )

        def check(strategies: list) -> None:
            assert len(strategies) == 1
            assert strategies[0].get("capacity_provider") == "FARGATE_SPOT"
            assert strategies[0].get("weight") == 1

        return cluster.capacity_providers.default_capacity_provider_strategies.apply(
            check
        )

    @pulumi.runtime.test
    def test_ec2_run_worker_prototype_uses_empty_managed_asg(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource(
            "test-energy-market",
            vpc,
            sgs,
            enable_ec2_run_worker_capacity_prototype=True,
            run_worker_instance_profile_arn="arn:aws:iam::123456789012:instance-profile/test-energy-market-ecs-instance-profile",
        )

        assert cluster.run_worker_auto_scaling_group is not None

        def check(values: list[object]) -> None:
            min_size, desired_capacity, max_size, tags = values
            assert min_size == 0
            assert desired_capacity == 0
            assert max_size == RUN_WORKER_EC2_ASG_MAX_SIZE
            assert {
                "key": "AmazonECSManaged",
                "value": "true",
                "propagate_at_launch": True,
            } in tags

        return pulumi.Output.all(
            cluster.run_worker_auto_scaling_group.min_size,
            cluster.run_worker_auto_scaling_group.desired_capacity,
            cluster.run_worker_auto_scaling_group.max_size,
            cluster.run_worker_auto_scaling_group.tags,
        ).apply(check)

    @pulumi.runtime.test
    def test_ec2_run_worker_prototype_launch_template_registers_cluster(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource(
            "test-energy-market",
            vpc,
            sgs,
            enable_ec2_run_worker_capacity_prototype=True,
            run_worker_instance_profile_arn="arn:aws:iam::123456789012:instance-profile/test-energy-market-ecs-instance-profile",
        )

        assert cluster.run_worker_launch_template is not None

        def check(user_data: str) -> None:
            decoded = base64.b64decode(user_data).decode("utf-8")
            assert "ECS_CLUSTER=test-energy-market-dagster-cluster" in decoded
            assert "ECS_ENABLE_TASK_IAM_ROLE=true" in decoded
            assert "ECS_AVAILABLE_LOGGING_DRIVERS" in decoded

        return cluster.run_worker_launch_template.user_data.apply(check)

    @pulumi.runtime.test
    def test_ec2_run_worker_prototype_launch_template_shape(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource(
            "test-energy-market",
            vpc,
            sgs,
            enable_ec2_run_worker_capacity_prototype=True,
            run_worker_instance_profile_arn="arn:aws:iam::123456789012:instance-profile/test-energy-market-ecs-instance-profile",
        )

        assert cluster.run_worker_launch_template is not None

        def check(values: list[object]) -> None:
            image_id, instance_type, metadata_options, block_device_mappings = values
            assert "ecs/optimized-ami/amazon-linux-2023" in image_id
            assert instance_type == RUN_WORKER_EC2_INSTANCE_TYPE
            assert metadata_options.get("http_tokens") == "required"
            assert isinstance(block_device_mappings, list)
            block_device_mapping = block_device_mappings[0]
            assert isinstance(block_device_mapping, dict)
            ebs = block_device_mapping["ebs"]
            assert isinstance(ebs, dict)
            assert ebs.get("encrypted") == "true"
            assert ebs.get("volume_size") == RUN_WORKER_EC2_ROOT_VOLUME_GB
            assert ebs.get("volume_type") == "gp3"

        return pulumi.Output.all(
            cluster.run_worker_launch_template.image_id,
            cluster.run_worker_launch_template.instance_type,
            cluster.run_worker_launch_template.metadata_options,
            cluster.run_worker_launch_template.block_device_mappings,
        ).apply(check)

    @pulumi.runtime.test
    def test_ec2_run_worker_prototype_uses_managed_scaling(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource(
            "test-energy-market",
            vpc,
            sgs,
            enable_ec2_run_worker_capacity_prototype=True,
            run_worker_instance_profile_arn="arn:aws:iam::123456789012:instance-profile/test-energy-market-ecs-instance-profile",
        )

        assert cluster.run_worker_capacity_provider is not None

        def check(provider: dict) -> None:
            assert provider.get("managed_draining") == "ENABLED"
            assert provider.get("managed_termination_protection") == "DISABLED"
            managed_scaling = provider["managed_scaling"]
            assert managed_scaling.get("status") == "ENABLED"
            assert managed_scaling.get("target_capacity") == 100

        return cluster.run_worker_capacity_provider.auto_scaling_group_provider.apply(
            check
        )

    def test_log_group_created(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource("test-energy-market", vpc, sgs)
        assert cluster.log_group is not None

    @pulumi.runtime.test
    def test_log_group_retention_is_one_day(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource("test-energy-market", vpc, sgs)

        def check(retention: int) -> None:
            assert retention == 1, f"Expected retention 1 day, got {retention}"

        return cluster.log_group.retention_in_days.apply(check)

    @pulumi.runtime.test
    def test_cluster_name_contains_dagster(self) -> None:
        vpc, sgs = _make_deps()
        cluster = EcsClusterComponentResource("test-energy-market", vpc, sgs)

        def check(name: str) -> None:
            assert "dagster" in name.lower(), (
                f"Expected 'dagster' in cluster name, got {name}"
            )

        return cluster.cluster.name.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        vpc, sgs = _make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            EcsClusterComponentResource("test-energy-market-warn", vpc, sgs)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
