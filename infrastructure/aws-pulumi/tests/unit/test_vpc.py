"""Tests for VpcComponentResource."""

import warnings

import pulumi

from components.vpc import VpcComponentResource


class TestVpcResourceCreation:
    @pulumi.runtime.test
    def test_vpc_cidr_block(self) -> None:
        vpc = VpcComponentResource("test-energy-market")

        def check(cidr: str) -> None:
            assert cidr == "10.0.0.0/16", f"Expected 10.0.0.0/16, got {cidr}"

        return vpc.vpc.cidr_block.apply(check)

    @pulumi.runtime.test
    def test_vpc_dns_hostnames_enabled(self) -> None:
        vpc = VpcComponentResource("test-energy-market")

        def check(enabled: bool) -> None:
            assert enabled is True, "DNS hostnames must be enabled"

        return vpc.vpc.enable_dns_hostnames.apply(check)

    @pulumi.runtime.test
    def test_vpc_dns_support_enabled(self) -> None:
        vpc = VpcComponentResource("test-energy-market")

        def check(enabled: bool) -> None:
            assert enabled is True, "DNS support must be enabled"

        return vpc.vpc.enable_dns_support.apply(check)

    @pulumi.runtime.test
    def test_public_subnet_cidr(self) -> None:
        vpc = VpcComponentResource("test-energy-market")

        def check(cidr: str) -> None:
            assert cidr == "10.0.0.0/24", f"Expected 10.0.0.0/24, got {cidr}"

        return vpc.public_subnet.cidr_block.apply(check)

    @pulumi.runtime.test
    def test_private_subnet_cidr(self) -> None:
        vpc = VpcComponentResource("test-energy-market")

        def check(cidr: str) -> None:
            assert cidr == "10.0.1.0/24", f"Expected 10.0.1.0/24, got {cidr}"

        return vpc.private_subnet.cidr_block.apply(check)

    @pulumi.runtime.test
    def test_nat_instance_type(self) -> None:
        vpc = VpcComponentResource("test-energy-market")

        def check(instance_type: str) -> None:
            assert instance_type == "t4g.nano", (
                f"Expected t4g.nano, got {instance_type}"
            )

        return vpc.fk_nat_instance.instance_type.apply(check)

    def test_internet_gateway_created(self) -> None:
        vpc = VpcComponentResource("test-energy-market")
        assert vpc.internet_gateway is not None

    def test_nat_key_pair_created(self) -> None:
        vpc = VpcComponentResource("test-energy-market")
        assert vpc.fk_nat_key_pair is not None

    def test_nat_eip_created(self) -> None:
        vpc = VpcComponentResource("test-energy-market")
        assert vpc.fk_nat_eip is not None

    def test_nat_security_group_created(self) -> None:
        vpc = VpcComponentResource("test-energy-market")
        assert vpc.fk_nat_security_group is not None

    def test_route_tables_created(self) -> None:
        vpc = VpcComponentResource("test-energy-market")
        assert vpc.public_route_table is not None
        assert vpc.private_route_table is not None

    def test_private_key_created(self) -> None:
        vpc = VpcComponentResource("test-energy-market")
        assert vpc.fk_nat_private_key is not None

    def test_no_deprecation_warnings(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            VpcComponentResource("test-energy-market-warn")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
