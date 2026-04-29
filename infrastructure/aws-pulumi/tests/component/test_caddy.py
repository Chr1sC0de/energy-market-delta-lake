"""Tests for CaddyServerComponentResource."""

import warnings

import pulumi

from components.caddy import CaddyServerComponentResource
from components.ecr import ECRComponentResource
from components.fastapi_auth import FastAPIAuthComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


def _make_deps() -> tuple[
    VpcComponentResource,
    ECRComponentResource,
    FastAPIAuthComponentResource,
    SecurityGroupsComponentResource,
]:
    vpc = VpcComponentResource("test-energy-market")
    sgs = SecurityGroupsComponentResource("test-energy-market", vpc)
    ecr = ECRComponentResource("test-energy-market")
    fastapi_auth = FastAPIAuthComponentResource("test-energy-market", vpc, ecr, sgs)
    return vpc, ecr, fastapi_auth, sgs


class TestCaddyServerComponent:
    def test_instance_created(self) -> None:
        vpc, ecr, auth, sgs = _make_deps()
        caddy = CaddyServerComponentResource("test-energy-market", vpc, ecr, auth, sgs)
        assert caddy.instance is not None

    @pulumi.runtime.test
    def test_instance_type_is_t3_nano(self) -> None:
        vpc, ecr, auth, sgs = _make_deps()
        caddy = CaddyServerComponentResource("test-energy-market", vpc, ecr, auth, sgs)

        def check(instance_type: str) -> None:
            assert instance_type == "t3.nano", f"Expected t3.nano, got {instance_type}"

        return caddy.instance.instance_type.apply(check)

    def test_eip_created(self) -> None:
        vpc, ecr, auth, sgs = _make_deps()
        caddy = CaddyServerComponentResource("test-energy-market", vpc, ecr, auth, sgs)
        assert caddy.eip is not None

    def test_ebs_volume_created(self) -> None:
        """Caddy must create an EBS volume for SSL certificate persistence."""
        vpc, ecr, auth, sgs = _make_deps()
        caddy = CaddyServerComponentResource("test-energy-market", vpc, ecr, auth, sgs)
        # _ebs_volume is private but must exist — certs stored across restarts
        assert caddy._ebs_volume is not None, (  # type: ignore[attr-defined]
            "Caddy must create an EBS volume for certificate persistence"
        )

    def test_no_deprecation_warnings(self) -> None:
        """Regression guard: region.region must be used, not region.name."""
        vpc, ecr, auth, sgs = _make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            CaddyServerComponentResource("test-energy-market-warn", vpc, ecr, auth, sgs)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
