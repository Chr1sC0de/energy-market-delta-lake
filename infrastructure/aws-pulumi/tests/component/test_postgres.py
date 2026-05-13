"""Tests for PostgresComponentResource."""

import warnings

import pulumi

from components.postgres import PostgresComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


def _make_deps() -> tuple[VpcComponentResource, SecurityGroupsComponentResource]:
    vpc = VpcComponentResource("test-energy-market")
    sgs = SecurityGroupsComponentResource("test-energy-market", vpc)
    return vpc, sgs


class TestPostgresComponent:
    def test_instance_created(self) -> None:
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)
        assert pg.instance is not None

    @pulumi.runtime.test
    def test_instance_type_is_t4g_nano(self) -> None:
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)

        def check(instance_type: str) -> None:
            assert instance_type == "t4g.nano", (
                f"Expected t4g.nano, got {instance_type}"
            )

        return pg.instance.instance_type.apply(check)

    def test_ssm_password_param_name(self) -> None:
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)
        assert "postgres/password" in pg.ssm_param_password_name
        assert "test-energy-market" in pg.ssm_param_password_name

    def test_ssm_private_dns_param_name(self) -> None:
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)
        assert "postgres/instance_private_dns" in pg.ssm_param_private_dns_name
        assert "test-energy-market" in pg.ssm_param_private_dns_name

    def test_private_dns_output_exists(self) -> None:
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)
        assert pg.private_dns is not None

    def test_password_output_exists(self) -> None:
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)
        assert pg.password is not None

    @pulumi.runtime.test
    def test_instance_requires_imdsv2(self) -> None:
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)

        def check(metadata_options: dict) -> None:
            assert metadata_options.get("http_tokens") == "required"
            assert metadata_options.get("http_endpoint") == "enabled"

        return pg.instance.metadata_options.apply(check)

    @pulumi.runtime.test
    def test_root_volume_is_encrypted(self) -> None:
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)

        def check(root_block_device: dict) -> None:
            assert root_block_device.get("encrypted") is True

        return pg.instance.root_block_device.apply(check)

    @pulumi.runtime.test
    def test_user_data_fetches_password_from_ssm(self) -> None:
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)

        def check(user_data: str) -> None:
            assert "MockPassword123!" not in user_data
            assert "aws ssm get-parameter" in user_data
            assert pg.ssm_param_password_name in user_data
            assert "--region 'ap-southeast-2'" in user_data
            assert "0.0.0.0/0 md5" not in user_data
            assert "10.0.0.0/16 scram-sha-256" in user_data

        return pg.user_data.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        vpc, sgs = _make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            PostgresComponentResource("test-energy-market-warn", vpc, sgs)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
