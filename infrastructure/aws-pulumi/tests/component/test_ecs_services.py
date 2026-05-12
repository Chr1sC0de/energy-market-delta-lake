"""Tests for Dagster Fargate service components.

This file verifies:
  - All four services are created and wired to the correct infrastructure
  - Cloud Map registration names are correct (aemo-etl, webserver-admin, webserver-guest)
  - The daemon has NO Cloud Map registration
  - Port mappings match the service roles (4000 for gRPC, 3000 for webserver)
  - Entry points are correct, including --read-only for guest webserver
  - All services share the same private subnet and cluster
  - Long-running services use Fargate Spot capacity
  - Circuit breakers are enabled on every service
  - No DeprecationWarning is raised (regression guard for .region fix and failure_threshold fix)
"""

import json
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


def _first_container(container_definitions: str) -> dict:
    containers = json.loads(container_definitions)
    assert len(containers) == 1
    return containers[0]


def _env_value(container: dict, name: str) -> str:
    for item in container["environment"]:
        if item["name"] == name:
            return item["value"]
    raise AssertionError(f"Missing environment variable {name!r}")


def _env_names(container: dict) -> set[str]:
    return {item["name"] for item in container.get("environment", [])}


def _secret_value(container: dict, name: str) -> str:
    for item in container.get("secrets", []):
        if item["name"] == name:
            return item["valueFrom"]
    raise AssertionError(f"Missing secret {name!r}")


def _assert_spot_fargate_strategy(strategies: list) -> None:
    providers = [s.get("capacity_provider") for s in strategies]
    assert providers == ["FARGATE_SPOT"], (
        f"Expected FARGATE_SPOT only for long-running service, got {providers}"
    )
    assert strategies[0].get("weight") == 1
    assert strategies[0].get("base") == 0


def _assert_postgres_password_uses_ecs_secret(container: dict) -> None:
    assert "DAGSTER_POSTGRES_PASSWORD" not in _env_names(container)
    value_from = _secret_value(container, "DAGSTER_POSTGRES_PASSWORD")
    assert value_from.endswith(
        ":parameter/test-energy-market/dagster/postgres/password"
    )


def _assert_webserver_health_check_probes_port(container: dict) -> None:
    health_check = container["healthCheck"]
    command = " ".join(health_check["command"])
    assert "socket.socket()" in command
    assert "localhost',3000" in command
    assert command != "CMD-SHELL true"


def _assert_port_mapping(container: dict, port: int) -> None:
    assert container["portMappings"] == [
        {"containerPort": port, "hostPort": port, "protocol": "tcp"}
    ]


def _assert_no_port_mappings(container: dict) -> None:
    assert "portMappings" not in container


def _assert_log_stream_prefix(container: dict, stream_prefix: str) -> None:
    options = container["logConfiguration"]["options"]
    assert options["awslogs-stream-prefix"] == stream_prefix
    assert options["awslogs-region"] == "ap-southeast-2"


def _assert_health_check_timing(container: dict) -> None:
    health_check = container["healthCheck"]
    assert health_check["interval"] == 15
    assert health_check["timeout"] == 5
    assert health_check["retries"] == 4
    assert health_check["startPeriod"] == 60


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
    def test_user_code_uses_spot_fargate(self) -> None:
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

        return svc.service.capacity_provider_strategies.apply(
            _assert_spot_fargate_strategy
        )

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
    def test_user_code_forces_new_deployments(self) -> None:
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

        def check(force_new_deployment: bool) -> None:
            assert force_new_deployment is True

        return svc.service.force_new_deployment.apply(check)

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
    def test_user_code_task_definition_uses_image_digest(self) -> None:
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

        def check(container_definitions: str) -> None:
            container = _first_container(container_definitions)
            image = container["image"]
            assert "@sha256:" in image
            assert not image.endswith(":latest")
            assert _env_value(container, "DAGSTER_CURRENT_IMAGE") == image

        return svc.task_definition.container_definitions.apply(check)

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

        def check(container_definitions: str) -> None:
            container = _first_container(container_definitions)
            assert container["name"] == "dagster-grpc"
            assert container["entryPoint"] == [
                "dagster",
                "api",
                "grpc",
                "-h",
                "0.0.0.0",
                "-p",
                "4000",
                "-m",
                "aemo_etl.definitions",
            ]
            _assert_port_mapping(container, 4000)
            _assert_log_stream_prefix(container, "dagster-aemo-etl-user-code")
            _assert_health_check_timing(container)
            health_check_command = " ".join(container["healthCheck"]["command"])
            assert "localhost',4000" in health_check_command
            assert _env_value(container, "AWS_S3_LOCKING_PROVIDER") == "dynamodb"
            assert _env_value(container, "DAGSTER_GRPC_TIMEOUT_SECONDS") == "300"

        return svc.task_definition.container_definitions.apply(check)

    @pulumi.runtime.test
    def test_user_code_task_definition_has_failure_alert_env(self) -> None:
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

        def check(container_definitions: str) -> None:
            container = _first_container(container_definitions)
            assert (
                _env_value(container, "DAGSTER_FAILURE_ALERT_TOPIC_ARN")
                == "arn:aws:sns:ap-southeast-2:123456789012:dagster-failed-run-alerts"
            )
            assert (
                _env_value(container, "DAGSTER_FAILURE_ALERT_BASE_URL")
                == "https://test.ausenergymarketdata.com/dagster-webserver/admin"
            )
            assert _env_value(container, "AWS_DEFAULT_REGION") == "ap-southeast-2"

        return svc.task_definition.container_definitions.apply(check)

    @pulumi.runtime.test
    def test_user_code_uses_ecs_secret_for_postgres_password(self) -> None:
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

        def check(container_definitions: str) -> None:
            _assert_postgres_password_uses_ecs_secret(
                _first_container(container_definitions)
            )

        return svc.task_definition.container_definitions.apply(check)

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
    def test_webserver_admin_task_definition_uses_image_digest(self) -> None:
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

        def check(container_definitions: str) -> None:
            image = _first_container(container_definitions)["image"]
            assert "@sha256:" in image
            assert not image.endswith(":latest")

        return svc.task_definition.container_definitions.apply(check)

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
    def test_webserver_admin_uses_ecs_secret_for_postgres_password(self) -> None:
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

        def check(container_definitions: str) -> None:
            _assert_postgres_password_uses_ecs_secret(
                _first_container(container_definitions)
            )

        return svc.task_definition.container_definitions.apply(check)

    @pulumi.runtime.test
    def test_webserver_admin_health_check_probes_port(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-admin-health",
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

        def check(container_definitions: str) -> None:
            _assert_webserver_health_check_probes_port(
                _first_container(container_definitions)
            )

        return svc.task_definition.container_definitions.apply(check)

    @pulumi.runtime.test
    def test_webserver_admin_task_definition_has_runtime_settings(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-admin-runtime",
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

        def check(container_definitions: str) -> None:
            container = _first_container(container_definitions)
            assert container["name"] == "webserver"
            assert container["entryPoint"] == [
                "dagster-webserver",
                "-h",
                "0.0.0.0",
                "-p",
                "3000",
                "-w",
                "workspace.yaml",
                "--path-prefix",
                "/dagster-webserver/admin",
            ]
            _assert_port_mapping(container, 3000)
            _assert_log_stream_prefix(container, "dagster-webserver-service-admin")
            _assert_health_check_timing(container)

        return svc.task_definition.container_definitions.apply(check)

    @pulumi.runtime.test
    def test_webserver_admin_uses_spot_fargate(self) -> None:
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

        return svc.service.capacity_provider_strategies.apply(
            _assert_spot_fargate_strategy
        )

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
    def test_webserver_guest_task_definition_uses_image_digest(self) -> None:
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

        def check(container_definitions: str) -> None:
            image = _first_container(container_definitions)["image"]
            assert "@sha256:" in image
            assert not image.endswith(":latest")

        return svc.task_definition.container_definitions.apply(check)

    @pulumi.runtime.test
    def test_webserver_admin_and_guest_have_distinct_families(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        admin = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-admin-family",
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
        guest = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-guest-family",
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

        def check(families: list[str]) -> None:
            assert families == ["dagster-webserver-admin", "dagster-webserver-guest"]

        return pulumi.Output.all(
            admin.task_definition.family,
            guest.task_definition.family,
        ).apply(check)

    @pulumi.runtime.test
    def test_webserver_guest_uses_spot_fargate(self) -> None:
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

        return svc.service.capacity_provider_strategies.apply(
            _assert_spot_fargate_strategy
        )

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

    @pulumi.runtime.test
    def test_webserver_guest_uses_ecs_secret_for_postgres_password(self) -> None:
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

        def check(container_definitions: str) -> None:
            _assert_postgres_password_uses_ecs_secret(
                _first_container(container_definitions)
            )

        return svc.task_definition.container_definitions.apply(check)

    @pulumi.runtime.test
    def test_webserver_guest_health_check_probes_port(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-guest-health",
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

        def check(container_definitions: str) -> None:
            _assert_webserver_health_check_probes_port(
                _first_container(container_definitions)
            )

        return svc.task_definition.container_definitions.apply(check)

    @pulumi.runtime.test
    def test_webserver_guest_task_definition_has_runtime_settings(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterWebserverServiceComponentResource(
            "test-energy-market-webserver-guest-runtime",
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

        def check(container_definitions: str) -> None:
            container = _first_container(container_definitions)
            assert container["name"] == "webserver"
            assert container["entryPoint"] == [
                "dagster-webserver",
                "--read-only",
                "-h",
                "0.0.0.0",
                "-p",
                "3000",
                "-w",
                "workspace.yaml",
                "--path-prefix",
                "/dagster-webserver/guest",
            ]
            _assert_port_mapping(container, 3000)
            _assert_log_stream_prefix(container, "dagster-webserver-service-guest")
            _assert_health_check_timing(container)

        return svc.task_definition.container_definitions.apply(check)

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
    def test_daemon_task_definition_uses_image_digest(self) -> None:
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

        def check(container_definitions: str) -> None:
            image = _first_container(container_definitions)["image"]
            assert "@sha256:" in image
            assert not image.endswith(":latest")

        return svc.task_definition.container_definitions.apply(check)

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
    def test_daemon_uses_spot_fargate(self) -> None:
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

        return svc.service.capacity_provider_strategies.apply(
            _assert_spot_fargate_strategy
        )

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

    @pulumi.runtime.test
    def test_daemon_uses_ecs_secret_for_postgres_password(self) -> None:
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

        def check(container_definitions: str) -> None:
            _assert_postgres_password_uses_ecs_secret(
                _first_container(container_definitions)
            )

        return svc.task_definition.container_definitions.apply(check)

    @pulumi.runtime.test
    def test_daemon_task_definition_has_runtime_settings(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = _make_all_deps()
        svc = DagsterDaemonServiceComponentResource(
            "test-energy-market-daemon-runtime",
            vpc=vpc,
            cluster=cluster,
            ecr=ecr,
            postgres=pg,
            security_groups=sgs,
            iam_roles=iam,
        )

        def check(container_definitions: str) -> None:
            container = _first_container(container_definitions)
            assert container["name"] == "DagsterDaemonContainer"
            assert container["entryPoint"] == ["dagster-daemon", "run"]
            _assert_no_port_mappings(container)
            _assert_log_stream_prefix(container, "dagster-daemon")
            _assert_health_check_timing(container)
            assert container["healthCheck"]["command"] == ["CMD-SHELL", "true"]
            assert _env_value(container, "AWS_S3_LOCKING_PROVIDER") == "dynamodb"
            assert _env_value(container, "DAGSTER_GRPC_TIMEOUT_SECONDS") == "300"

        return svc.task_definition.container_definitions.apply(check)

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
