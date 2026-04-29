"""Tests for ServiceDiscoveryComponentResource."""

import warnings

import pulumi

from components.service_discovery import ServiceDiscoveryComponentResource
from components.vpc import VpcComponentResource


def _make_vpc() -> VpcComponentResource:
    return VpcComponentResource("test-energy-market")


class TestServiceDiscovery:
    def test_namespace_created(self) -> None:
        vpc = _make_vpc()
        sd = ServiceDiscoveryComponentResource("test-energy-market", vpc)
        assert sd.namespace is not None

    @pulumi.runtime.test
    def test_namespace_name_is_dagster(self) -> None:
        vpc = _make_vpc()
        sd = ServiceDiscoveryComponentResource("test-energy-market", vpc)

        def check(name: str) -> None:
            assert name == "dagster", f"Expected namespace name 'dagster', got {name}"

        return sd.namespace.name.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        vpc = _make_vpc()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            ServiceDiscoveryComponentResource("test-energy-market-warn", vpc)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
