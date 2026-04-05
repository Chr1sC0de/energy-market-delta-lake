"""Zero-warning regression guard.

This file is the definitive protection against re-introducing deprecated API usage.
Every component that was affected by the two warning categories is instantiated
inside warnings.catch_warnings(record=True) and the test asserts that zero
DeprecationWarning instances are emitted.

Warning categories guarded:
  1. `name is deprecated. Use region instead.`
     Triggered by accessing .name on GetRegionResult from aws.get_region().
     Fixed by using .region instead across ecs_services.py, iam_roles.py,
     fastapi_auth.py, caddy.py, and removing dead call in ecr.py.

  2. `failure_threshold is deprecated`
     Triggered by passing failure_threshold to ServiceHealthCheckCustomConfigArgs.
     Fixed by passing ServiceHealthCheckCustomConfigArgs() with no arguments —
     health_check_custom_config is retained (needed for ECS-managed health) but
     failure_threshold is omitted since AWS ignores it and always uses 1.
"""

import warnings

from components.caddy import CaddyServerComponentResource
from components.ecr import ECRComponentResource
from components.ecs_cluster import EcsClusterComponentResource
from components.ecs_services import (
    DagsterDaemonServiceComponentResource,
    DagsterUserCodeServiceComponentResource,
    DagsterWebserverServiceComponentResource,
)
from components.fastapi_auth import FastAPIAuthComponentResource
from components.iam_roles import IamRolesComponentResource
from components.postgres import PostgresComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.service_discovery import ServiceDiscoveryComponentResource
from components.vpc import VpcComponentResource


def _assert_no_deprecation_warnings(caught: list) -> None:
    """Fail with a clear message if any DeprecationWarning was recorded."""
    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    if deprecations:
        messages = [str(w.message) for w in deprecations]
        raise AssertionError(
            f"Expected zero DeprecationWarnings but got {len(deprecations)}:\n"
            + "\n".join(f"  - {m}" for m in messages)
        )


class TestNoDeprecationWarningsIamRoles:
    def test_iam_roles_no_deprecation(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            IamRolesComponentResource("test-dw-iam")
        _assert_no_deprecation_warnings(caught)


class TestNoDeprecationWarningsEcr:
    def test_ecr_no_deprecation(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            ECRComponentResource("test-dw-ecr")
        _assert_no_deprecation_warnings(caught)


class TestNoDeprecationWarningsEcsServices:
    def _make_deps(self) -> tuple:
        vpc = VpcComponentResource("test-dw-vpc")
        sgs = SecurityGroupsComponentResource("test-dw-vpc", vpc)
        iam = IamRolesComponentResource("test-dw-vpc")
        ecr = ECRComponentResource("test-dw-vpc")
        sd = ServiceDiscoveryComponentResource("test-dw-vpc", vpc)
        pg = PostgresComponentResource("test-dw-vpc", vpc, sgs)
        cluster = EcsClusterComponentResource("test-dw-vpc", vpc, sgs)
        return vpc, cluster, ecr, pg, sgs, sd, iam

    def test_user_code_service_no_deprecation(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = self._make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DagsterUserCodeServiceComponentResource(
                "test-dw-user-code",
                vpc=vpc,
                cluster=cluster,
                ecr=ecr,
                postgres=pg,
                security_groups=sgs,
                service_discovery=sd,
                iam_roles=iam,
            )
        _assert_no_deprecation_warnings(caught)

    def test_webserver_admin_service_no_deprecation(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = self._make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DagsterWebserverServiceComponentResource(
                "test-dw-webserver-admin",
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
        _assert_no_deprecation_warnings(caught)

    def test_webserver_guest_service_no_deprecation(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = self._make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DagsterWebserverServiceComponentResource(
                "test-dw-webserver-guest",
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
        _assert_no_deprecation_warnings(caught)

    def test_daemon_service_no_deprecation(self) -> None:
        vpc, cluster, ecr, pg, sgs, sd, iam = self._make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DagsterDaemonServiceComponentResource(
                "test-dw-daemon",
                vpc=vpc,
                cluster=cluster,
                ecr=ecr,
                postgres=pg,
                security_groups=sgs,
                iam_roles=iam,
            )
        _assert_no_deprecation_warnings(caught)


class TestNoDeprecationWarningsFastAPIAuth:
    def test_fastapi_auth_no_deprecation(self) -> None:
        vpc = VpcComponentResource("test-dw-fastapi-vpc")
        sgs = SecurityGroupsComponentResource("test-dw-fastapi-vpc", vpc)
        ecr = ECRComponentResource("test-dw-fastapi-vpc")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            FastAPIAuthComponentResource("test-dw-fastapi", vpc, ecr, sgs)
        _assert_no_deprecation_warnings(caught)


class TestNoDeprecationWarningsCaddy:
    def test_caddy_no_deprecation(self) -> None:
        vpc = VpcComponentResource("test-dw-caddy-vpc")
        sgs = SecurityGroupsComponentResource("test-dw-caddy-vpc", vpc)
        ecr = ECRComponentResource("test-dw-caddy-vpc")
        auth = FastAPIAuthComponentResource("test-dw-caddy-vpc", vpc, ecr, sgs)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            CaddyServerComponentResource("test-dw-caddy", vpc, ecr, auth, sgs)
        _assert_no_deprecation_warnings(caught)
