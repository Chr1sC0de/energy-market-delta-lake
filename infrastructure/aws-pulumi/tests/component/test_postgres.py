"""Tests for PostgresComponentResource."""

import warnings

import pulumi
import pytest

from components.postgres import (
    ALLOW_DEV_STRING_POSTGRES_PASSWORD_PARAMETER_CONFIG_KEY,
    POSTGRES_PASSWORD_PARAMETER_TYPE_SECURE_STRING,
    POSTGRES_PASSWORD_PARAMETER_TYPE_STRING,
    POSTGRES_ROOT_VOLUME_GIB,
    PostgresComponentResource,
)
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


def _make_deps() -> tuple[VpcComponentResource, SecurityGroupsComponentResource]:
    vpc = VpcComponentResource("test-energy-market")
    sgs = SecurityGroupsComponentResource("test-energy-market", vpc)
    return vpc, sgs


def _make_named_deps(
    name: str,
) -> tuple[VpcComponentResource, SecurityGroupsComponentResource]:
    vpc = VpcComponentResource(name)
    sgs = SecurityGroupsComponentResource(name, vpc)
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

    @pulumi.runtime.test
    def test_ssm_password_param_type_defaults_to_secure_string(self):
        vpc, sgs = _make_deps()
        pg = PostgresComponentResource("test-energy-market", vpc, sgs)

        def check(parameter_type: str) -> None:
            assert pg.ssm_param_password_type == (
                POSTGRES_PASSWORD_PARAMETER_TYPE_SECURE_STRING
            )
            assert parameter_type == POSTGRES_PASSWORD_PARAMETER_TYPE_SECURE_STRING

        return pg._password_parameter.type.apply(check)

    @pulumi.runtime.test
    def test_dev_opt_in_ssm_password_param_type_is_string(
        self, set_component_config_values
    ):
        set_component_config_values(
            {
                f"aws-pulumi:{ALLOW_DEV_STRING_POSTGRES_PASSWORD_PARAMETER_CONFIG_KEY}": "true"
            }
        )
        vpc, sgs = _make_named_deps("dev-energy-market")
        pg = PostgresComponentResource("dev-energy-market", vpc, sgs)

        def check(parameter_type: str) -> None:
            assert pg.ssm_param_password_type == POSTGRES_PASSWORD_PARAMETER_TYPE_STRING
            assert parameter_type == POSTGRES_PASSWORD_PARAMETER_TYPE_STRING

        return pg._password_parameter.type.apply(check)

    def test_non_dev_opt_in_ssm_password_param_type_is_rejected(
        self, set_component_config_values
    ) -> None:
        set_component_config_values(
            {
                f"aws-pulumi:{ALLOW_DEV_STRING_POSTGRES_PASSWORD_PARAMETER_CONFIG_KEY}": "true"
            }
        )
        vpc, sgs = _make_deps()
        with pytest.raises(
            ValueError,
            match="dev-energy-market",
        ):
            PostgresComponentResource("test-energy-market", vpc, sgs)

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
            assert root_block_device.get("volume_size") == POSTGRES_ROOT_VOLUME_GIB
            assert root_block_device.get("volume_type") == "gp3"

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
