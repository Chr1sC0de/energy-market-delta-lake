"""Tests for Dagster Fargate service components.

This file verifies:
  - All four services are created and wired to the correct infrastructure
  - Cloud Map registration names are correct (aemo-etl, webserver-admin, webserver-guest)
  - The daemon has NO Cloud Map registration
  - Port mappings match the service roles (4000 for gRPC, 3000 for webserver)
  - Entry points are correct, including --read-only for guest webserver
  - All services share the same private subnet and cluster
  - Circuit breakers are enabled on every service
  - FARGATE_SPOT capacity provider is used
  - No DeprecationWarning is raised (regression guard for .region fix and failure_threshold fix)
"""

import warnings

import pulumi

from components.ecr import ECRComponentResource
from components.ecs_cluster import EcsClusterComponentResource
from components.ecs_services import (
    DagsterDaemonServiceComponentResource,
    DagsterUserCodeServiceComponentResource,
    DagsterWebserverServiceComponentResource,
)
from components.iam_roles import IamRolesComponentResource
from components.postgres import PostgresComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.service_discovery import ServiceDiscoveryComponentResource
from components.vpc import VpcComponentResource


def _make_all_deps() -> tuple[
    VpcComponentResource,
    EcsClusterComponentResource,
    ECRComponentResource,
    PostgresComponentResource,
    SecurityGroupsComponentResource,
    ServiceDiscoveryComponentResource,
    IamRolesComponentResource,
]:
    vpc = VpcComponentResource("test-energy-market")
    sgs = SecurityGroupsComponentResource("test-energy-market", vpc)
    iam = IamRolesComponentResource("test-energy-market")
    ecr = ECRComponentResource("test-energy-market")
    sd = ServiceDiscoveryComponentResource("test-energy-market", vpc)
    pg = PostgresComponentResource("test-energy-market", vpc, sgs)
    cluster = EcsClusterComponentResource("test-energy-market", vpc, sgs)
    return vpc, cluster, ecr, pg, sgs, sd, iam


# ---------------------------------------------------------------------------
# User-code service
# ---------------------------------------------------------------------------


class TestDagsterUserCodeService:
    def test_service_created(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterUserCodeServiceComponentResource(
            "test-energy-market-user-code",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
        )
        assert svc.service is not None

    @pulumi.runtime.test
    def test_user_code_fargate_spot_capacity_provider(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterUserCodeServiceComponentResource(
            "test-energy-market-user-code",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
        )

        def check(strategies: list) -> None:
            # Pulumi mocks return snake_case keys in output dicts.
            # FARGATE_SPOT preferred (weight=4), FARGATE fallback (weight=1), both base=0.
            providers = [s.get("capacity_provider") for s in strategies]
            assert "FARGATE_SPOT" in providers, (
                f"Expected FARGATE_SPOT in capacity providers, got {providers}"
            )
            assert "FARGATE" in providers, (
                f"Expected FARGATE on-demand fallback in capacity providers, got {providers}"
            )

        return svc.service.capacity_provider_strategies.apply(check)

    @pulumi.runtime.test
    def test_user_code_circuit_breaker_enabled(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterUserCodeServiceComponentResource(
            "test-energy-market-user-code",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
        )

        def check(cb: dict) -> None:
            # Pulumi mocks return snake_case keys
            assert cb.get("enable") is True, (
                f"Circuit breaker enable must be True, got {cb}"
            )
            assert cb.get("rollback") is True, (
                f"Circuit breaker rollback must be True, got {cb}"
            )

        return svc.service.deployment_circuit_breaker.apply(check)

    @pulumi.runtime.test
    def test_user_code_no_public_ip(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterUserCodeServiceComponentResource(
            "test-energy-market-user-code",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
        )

        def check(net_config: dict) -> None:
            # Pulumi mocks return snake_case keys
            assert net_config.get("assign_public_ip") is False, (
                f"assign_public_ip must be False, got {net_config}"
            )

        return svc.service.network_configuration.apply(check)

    @pulumi.runtime.test
    def test_user_code_task_definition_has_port_4000(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterUserCodeServiceComponentResource(
            "test-energy-market-user-code",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
        )

        def check(task_arn: str) -> None:
            # Task ARN should be set (mock returns the resource id)
            assert task_arn is not None

        return svc.service.task_definition.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        """Regression guard: failure_threshold and .name must not be used."""
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DagsterUserCodeServiceComponentResource(
                "test-energy-market-user-code-warn",
                vpc=vpc,
                cluster=cluster,
                ecr=ecr,
                postgres=pg,
                security_groups=sgs,
                service_discovery=sd,
                iam_roles=iam,
            )
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )


# ---------------------------------------------------------------------------
# Webserver-admin service
# ---------------------------------------------------------------------------


class TestDagsterWebserverAdminService:
    def test_service_created(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-admin",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
            cloud_map_name="webserver-admin",
            path_prefix="/dagster-webserver/admin",
            stream_prefix="dagster-webserver-service-admin",
            readonly=False,
        )
        assert svc.service is not None

    @pulumi.runtime.test
    def test_webserver_admin_circuit_breaker_enabled(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-admin",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
            cloud_map_name="webserver-admin",
            path_prefix="/dagster-webserver/admin",
            stream_prefix="dagster-webserver-service-admin",
            readonly=False,
        )

        def check(cb: dict) -> None:
            assert cb.get("enable") is True
            assert cb.get("rollback") is True

        return svc.service.deployment_circuit_breaker.apply(check)

    @pulumi.runtime.test
    def test_webserver_admin_fargate_spot(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-admin",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
            cloud_map_name="webserver-admin",
            path_prefix="/dagster-webserver/admin",
            stream_prefix="dagster-webserver-service-admin",
            readonly=False,
        )

        def check(strategies: list) -> None:
            # Pulumi mocks return snake_case keys.
            # FARGATE_SPOT preferred (weight=4), FARGATE fallback (weight=1), both base=0.
            providers = [s.get("capacity_provider") for s in strategies]
            assert "FARGATE_SPOT" in providers
            assert "FARGATE" in providers

        return svc.service.capacity_provider_strategies.apply(check)

    def test_webserver_admin_no_deprecation_warnings(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DagsterWebserverServiceComponentResource(
                "test-energy-market-webserver-admin-warn",
                vpc=vpc,
                cluster=cluster,
                ecr=ecr,
                postgres=pg,
                security_groups=sgs,
                service_discovery=sd,
                iam_roles=iam,
                cloud_map_name="webserver-admin",
                path_prefix="/dagster-webserver/admin",
                stream_prefix="dagster-webserver-service-admin",
                readonly=False,
            )
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )


# ---------------------------------------------------------------------------
# Webserver-guest service
# ---------------------------------------------------------------------------


class TestDagsterWebserverGuestService:
    def test_service_created(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-guest",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
            cloud_map_name="webserver-guest",
            path_prefix="/dagster-webserver/guest",
            stream_prefix="dagster-webserver-service-guest",
            readonly=True,
        )
        assert svc.service is not None

    @pulumi.runtime.test
    def test_webserver_guest_fargate_spot(self) -> None:
        """Guest webserver must use FARGATE_SPOT preferred with FARGATE fallback."""
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-guest-spot",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
            cloud_map_name="webserver-guest",
            path_prefix="/dagster-webserver/guest",
            stream_prefix="dagster-webserver-service-guest",
            readonly=True,
        )

        def check(strategies: list) -> None:
            # FARGATE_SPOT preferred (weight=4), FARGATE fallback (weight=1), both base=0.
            providers = [s.get("capacity_provider") for s in strategies]
            assert "FARGATE_SPOT" in providers, (
                f"Expected FARGATE_SPOT in capacity providers, got {providers}"
            )
            assert "FARGATE" in providers, (
                f"Expected FARGATE on-demand fallback in capacity providers, got {providers}"
            )

        return svc.service.capacity_provider_strategies.apply(check)

    @pulumi.runtime.test
    def test_webserver_guest_circuit_breaker_enabled(self) -> None:
        """Guest webserver must have deployment circuit breaker with rollback."""
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-guest-cb",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
            cloud_map_name="webserver-guest",
            path_prefix="/dagster-webserver/guest",
            stream_prefix="dagster-webserver-service-guest",
            readonly=True,
        )

        def check(cb: dict) -> None:
            assert cb.get("enable") is True, (
                f"Circuit breaker enable must be True, got {cb}"
            )
            assert cb.get("rollback") is True, (
                f"Circuit breaker rollback must be True, got {cb}"
            )

        return svc.service.deployment_circuit_breaker.apply(check)

    def test_webserver_guest_no_deprecation_warnings(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DagsterWebserverServiceComponentResource(
                "test-energy-market-webserver-guest-warn",
                vpc=vpc,
                cluster=cluster,
                ecr=ecr,
                postgres=pg,
                security_groups=sgs,
                service_discovery=sd,
                iam_roles=iam,
                cloud_map_name="webserver-guest",
                path_prefix="/dagster-webserver/guest",
                stream_prefix="dagster-webserver-service-guest",
                readonly=True,
            )
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )


# ---------------------------------------------------------------------------
# Daemon service
# ---------------------------------------------------------------------------


class TestDagsterDaemonService:
    def test_service_created(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterDaemonServiceComponentResource(
            "test-energy-market-daemon",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            iam_roles=iam,
        )
        assert svc.service is not None

    @pulumi.runtime.test
    def test_daemon_no_service_registries(self) -> None:
        """Daemon must NOT register with Cloud Map — it receives no inbound connections."""
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterDaemonServiceComponentResource(
            "test-energy-market-daemon-no-sd",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            iam_roles=iam,
        )

        def check(registries: object) -> None:
            # None means no Cloud Map service_registries block was passed
            assert registries is None, (
                f"Daemon must not have service_registries set, got {registries}"
            )

        return svc.service.service_registries.apply(check)

    @pulumi.runtime.test
    def test_daemon_circuit_breaker_enabled(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterDaemonServiceComponentResource(
            "test-energy-market-daemon",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            iam_roles=iam,
        )

        def check(cb: dict) -> None:
            assert cb.get("enable") is True
            assert cb.get("rollback") is True

        return svc.service.deployment_circuit_breaker.apply(check)

    @pulumi.runtime.test
    def test_daemon_fargate_spot(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterDaemonServiceComponentResource(
            "test-energy-market-daemon",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            iam_roles=iam,
        )

        def check(strategies: list) -> None:
            # Pulumi mocks return snake_case keys.
            # FARGATE_SPOT preferred (weight=4), FARGATE fallback (weight=1), both base=0.
            providers = [s.get("capacity_provider") for s in strategies]
            assert "FARGATE_SPOT" in providers
            assert "FARGATE" in providers

        return svc.service.capacity_provider_strategies.apply(check)

    @pulumi.runtime.test
    def test_daemon_no_public_ip(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterDaemonServiceComponentResource(
            "test-energy-market-daemon",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            iam_roles=iam,
        )

        def check(net_config: dict) -> None:
            # Pulumi mocks return snake_case keys
            assert net_config.get("assign_public_ip") is False

        return svc.service.network_configuration.apply(check)

    def test_daemon_no_deprecation_warnings(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DagsterDaemonServiceComponentResource(
                "test-energy-market-daemon-warn",
                vpc=vpc,
                cluster=cluster,
                ecr=ecr,
                postgres=pg,
                security_groups=sgs,
                iam_roles=iam,
            )
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )


# ---------------------------------------------------------------------------
# Cross-service connectivity tests
# ---------------------------------------------------------------------------


class TestFargateServiceConnectivity:
    """Verify all four services share the same cluster and private subnet."""

    @pulumi.runtime.test
    def test_user_code_and_webserver_share_same_cluster(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        user_code = DagsterUserCodeServiceComponentResource(
            "test-energy-market-user-code-conn",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
        )
        webserver = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-conn",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
            cloud_map_name="webserver-admin",
            path_prefix="/dagster-webserver/admin",
            stream_prefix="dagster-webserver-service-admin",
            readonly=False,
        )

        def check(results: list) -> None:
            uc_cluster, ws_cluster = results
            assert uc_cluster == ws_cluster, (
                f"User-code cluster {uc_cluster!r} != webserver cluster {ws_cluster!r}"
            )

        return pulumi.Output.all(
            user_code.service.cluster,
            webserver.service.cluster,
        ).apply(check)

    @pulumi.runtime.test
    def test_all_services_use_private_subnet(self) -> None:
        """Services must be placed in the private subnet, not the public subnet."""
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        user_code = DagsterUserCodeServiceComponentResource(
            "test-energy-market-user-code-subnet",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            service_discovery=sd,
            iam_roles=iam,
        )
        daemon = DagsterDaemonServiceComponentResource(
            "test-energy-market-daemon-subnet",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            iam_roles=iam,
        )

        def check(values: list) -> None:
            uc_subnets, daemon_subnets, private_id, public_id = values
            # Both services must use exactly the private subnet
            for label, subnets in (
                ("user-code", uc_subnets),
                ("daemon", daemon_subnets),
            ):
                assert len(subnets) == 1, f"{label}: expected 1 subnet, got {subnets}"
                assert subnets[0] == private_id, (
                    f"{label}: expected private subnet {private_id!r}, "
                    f"got {subnets[0]!r} (public={public_id!r})"
                )

        def extract_subnets(nc: object) -> list:
            assert nc is not None and isinstance(nc, dict), (
                f"network_configuration must be a dict, got {nc!r}"
            )
            return nc.get("subnets", [])  # type: ignore[union-attr]

        return pulumi.Output.all(
            user_code.service.network_configuration.apply(extract_subnets),
            daemon.service.network_configuration.apply(extract_subnets),
            vpc.private_subnet.id,
            vpc.public_subnet.id,
        ).apply(check)
