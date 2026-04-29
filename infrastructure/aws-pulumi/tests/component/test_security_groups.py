"""Tests for SecurityGroupsComponentResource."""

import warnings

import pulumi

from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


def _make_vpc() -> VpcComponentResource:
    return VpcComponentResource("test-energy-market")


class TestSecurityGroupsCreation:
    def test_register_has_all_security_groups(self) -> None:
        vpc = _make_vpc()
        sgs = SecurityGroupsComponentResource("test-energy-market", vpc)
        reg = sgs.register
        assert reg.bastion_host is not None
        assert reg.dagster_webserver is not None
        assert reg.dagster_user_code is not None
        assert reg.dagster_daemon is not None
        assert reg.dagster_postgres is not None
        assert reg.caddy_instance is not None
        assert reg.fastapi_auth is not None

    @pulumi.runtime.test
    def test_bastion_sg_name_contains_bastion(self) -> None:
        vpc = _make_vpc()
        sgs = SecurityGroupsComponentResource("test-energy-market", vpc)

        # Mock returns args.name as the `name` output — the resource logical name
        def check(name: str) -> None:
            assert "bastion" in name.lower(), (
                f"Expected 'bastion' in SG resource name, got {name}"
            )

        return sgs.register.bastion_host.name.apply(check)

    @pulumi.runtime.test
    def test_dagster_webserver_sg_name(self) -> None:
        vpc = _make_vpc()
        sgs = SecurityGroupsComponentResource("test-energy-market", vpc)

        def check(name: str) -> None:
            assert "webserver" in name.lower() or "dagster" in name.lower(), (
                f"Expected 'webserver' or 'dagster' in SG resource name, got {name}"
            )

        return sgs.register.dagster_webserver.name.apply(check)

    @pulumi.runtime.test
    def test_dagster_user_code_sg_name(self) -> None:
        vpc = _make_vpc()
        sgs = SecurityGroupsComponentResource("test-energy-market", vpc)

        def check(name: str) -> None:
            assert (
                "user" in name.lower()
                or "code" in name.lower()
                or "dagster" in name.lower()
            ), f"Unexpected SG resource name: {name}"

        return sgs.register.dagster_user_code.name.apply(check)

    @pulumi.runtime.test
    def test_dagster_postgres_sg_name(self) -> None:
        vpc = _make_vpc()
        sgs = SecurityGroupsComponentResource("test-energy-market", vpc)

        def check(name: str) -> None:
            assert "postgres" in name.lower() or "dagster" in name.lower(), (
                f"Expected 'postgres' in SG resource name, got {name}"
            )

        return sgs.register.dagster_postgres.name.apply(check)

    @pulumi.runtime.test
    def test_caddy_sg_name(self) -> None:
        vpc = _make_vpc()
        sgs = SecurityGroupsComponentResource("test-energy-market", vpc)

        def check(name: str) -> None:
            assert "caddy" in name.lower(), (
                f"Expected 'caddy' in SG resource name, got {name}"
            )

        return sgs.register.caddy_instance.name.apply(check)

    @pulumi.runtime.test
    def test_fastapi_auth_sg_name(self) -> None:
        vpc = _make_vpc()
        sgs = SecurityGroupsComponentResource("test-energy-market", vpc)

        def check(name: str) -> None:
            assert "fastapi" in name.lower() or "auth" in name.lower(), (
                f"Expected 'fastapi' or 'auth' in SG resource name, got {name}"
            )

        return sgs.register.fastapi_auth.name.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        vpc = _make_vpc()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            SecurityGroupsComponentResource("test-energy-market-warn", vpc)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
