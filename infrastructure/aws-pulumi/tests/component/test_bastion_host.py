"""Tests for BastionHostComponentResource."""

import warnings

import pulumi

from components.bastion_host import BastionHostComponentResource
from components.iam_roles import IamRolesComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


def _make_deps() -> tuple[
    VpcComponentResource, SecurityGroupsComponentResource, IamRolesComponentResource
]:
    vpc = VpcComponentResource("test-energy-market")
    sgs = SecurityGroupsComponentResource("test-energy-market", vpc)
    iam = IamRolesComponentResource("test-energy-market")
    return vpc, sgs, iam


class TestBastionHostComponent:
    def test_instance_created(self) -> None:
        vpc, sgs, iam = _make_deps()
        bastion = BastionHostComponentResource("test-energy-market", vpc, sgs, iam)
        assert bastion.instance is not None

    @pulumi.runtime.test
    def test_instance_type_is_t3_nano(self) -> None:
        vpc, sgs, iam = _make_deps()
        bastion = BastionHostComponentResource("test-energy-market", vpc, sgs, iam)

        def check(instance_type: str) -> None:
            assert instance_type == "t3.nano", f"Expected t3.nano, got {instance_type}"

        return bastion.instance.instance_type.apply(check)

    def test_key_pair_created(self) -> None:
        vpc, sgs, iam = _make_deps()
        bastion = BastionHostComponentResource("test-energy-market", vpc, sgs, iam)
        assert bastion.key_pair is not None

    def test_eip_created(self) -> None:
        vpc, sgs, iam = _make_deps()
        bastion = BastionHostComponentResource("test-energy-market", vpc, sgs, iam)
        assert bastion.eip is not None

    def test_private_key_created(self) -> None:
        vpc, sgs, iam = _make_deps()
        bastion = BastionHostComponentResource("test-energy-market", vpc, sgs, iam)
        assert bastion.private_key is not None

    @pulumi.runtime.test
    def test_private_key_algorithm_is_ed25519(self) -> None:
        vpc, sgs, iam = _make_deps()
        bastion = BastionHostComponentResource("test-energy-market", vpc, sgs, iam)

        def check(algorithm: str) -> None:
            assert algorithm.upper() == "ED25519", f"Expected ED25519, got {algorithm}"

        return bastion.private_key.algorithm.apply(check)

    @pulumi.runtime.test
    def test_instance_in_public_subnet(self) -> None:
        """Bastion host must be placed in the public subnet (needs direct SSH access)."""
        vpc, sgs, iam = _make_deps()
        bastion = BastionHostComponentResource("test-energy-market", vpc, sgs, iam)
        public_subnet_id = vpc.public_subnet.id
        private_subnet_id = vpc.private_subnet.id

        def check(values: list) -> None:
            instance_subnet, public_id, private_id = values
            assert instance_subnet == public_id, (
                f"Bastion must be in public subnet ({public_id}), "
                f"got {instance_subnet} (private={private_id})"
            )

        return pulumi.Output.all(
            bastion.instance.subnet_id,
            public_subnet_id,
            private_subnet_id,
        ).apply(check)

    def test_no_deprecation_warnings(self) -> None:
        vpc, sgs, iam = _make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            BastionHostComponentResource("test-energy-market-warn", vpc, sgs, iam)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
