"""Tests for EcsClusterComponentResource."""

import warnings

import pulumi

from components.ecs_cluster import EcsClusterComponentResource
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
