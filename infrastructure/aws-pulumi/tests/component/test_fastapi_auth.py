"""Tests for FastAPIAuthComponentResource."""

import warnings

import pulumi

from components.ecr import ECRComponentResource
from components.fastapi_auth import FastAPIAuthComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


def _make_deps() -> tuple[
    VpcComponentResource, ECRComponentResource, SecurityGroupsComponentResource
]:
    vpc = VpcComponentResource("test-energy-market")
    sgs = SecurityGroupsComponentResource("test-energy-market", vpc)
    ecr = ECRComponentResource("test-energy-market")
    return vpc, ecr, sgs


class TestFastAPIAuthComponent:
    def test_instance_created(self) -> None:
        vpc, ecr, sgs = _make_deps()
        auth = FastAPIAuthComponentResource("test-energy-market", vpc, ecr, sgs)
        assert auth.instance is not None

    @pulumi.runtime.test
    def test_instance_type_is_t3_nano(self) -> None:
        vpc, ecr, sgs = _make_deps()
        auth = FastAPIAuthComponentResource("test-energy-market", vpc, ecr, sgs)

        def check(instance_type: str) -> None:
            assert instance_type == "t3.nano", f"Expected t3.nano, got {instance_type}"

        return auth.instance.instance_type.apply(check)

    @pulumi.runtime.test
    def test_instance_in_private_subnet(self) -> None:
        """FastAPI auth server must be placed in the private subnet (not public)."""
        vpc, ecr, sgs = _make_deps()
        auth = FastAPIAuthComponentResource("test-energy-market", vpc, ecr, sgs)
        private_subnet_id = vpc.private_subnet.id
        public_subnet_id = vpc.public_subnet.id

        def check(values: list) -> None:
            instance_subnet, private_id, public_id = values
            assert instance_subnet == private_id, (
                f"FastAPI auth must be in private subnet ({private_id}), "
                f"got {instance_subnet} (public={public_id})"
            )

        return pulumi.Output.all(
            auth.instance.subnet_id,
            private_subnet_id,
            public_subnet_id,
        ).apply(check)

    @pulumi.runtime.test
    def test_instance_requires_imdsv2(self) -> None:
        vpc, ecr, sgs = _make_deps()
        auth = FastAPIAuthComponentResource("test-energy-market", vpc, ecr, sgs)

        def check(metadata_options: dict) -> None:
            assert metadata_options.get("http_tokens") == "required"
            assert metadata_options.get("http_endpoint") == "enabled"

        return auth.instance.metadata_options.apply(check)

    @pulumi.runtime.test
    def test_root_volume_is_encrypted(self) -> None:
        vpc, ecr, sgs = _make_deps()
        auth = FastAPIAuthComponentResource("test-energy-market", vpc, ecr, sgs)

        def check(root_block_device: dict) -> None:
            assert root_block_device.get("encrypted") is True

        return auth.instance.root_block_device.apply(check)

    @pulumi.runtime.test
    def test_user_data_fetches_cognito_values_from_ssm(self) -> None:
        vpc, ecr, sgs = _make_deps()
        auth = FastAPIAuthComponentResource("test-energy-market", vpc, ecr, sgs)

        def check(user_data: str) -> None:
            assert "test-cognito-client-id" not in user_data
            assert "test-cognito-client-secret" not in user_data
            assert (
                "https://cognito.test.example.com/.well-known/jwks.json"
                not in user_data
            )
            assert "AWS_DEFAULT_REGION=ap-southeast-2" in user_data
            assert "aws ssm get-parameter" in user_data
            assert set(auth.cognito_parameter_names) == {
                "client_id",
                "token_signing_key_url",
                "client_secret",
            }
            for parameter_name in auth.cognito_parameter_names.values():
                assert parameter_name in user_data
            assert "cognito_server_metadata_url" not in user_data
            assert "COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL" not in user_data

        return auth.user_data.apply(check)

    @pulumi.runtime.test
    def test_user_data_uses_digest_pinned_auth_image(self) -> None:
        vpc, ecr, sgs = _make_deps()
        auth = FastAPIAuthComponentResource("test-energy-market", vpc, ecr, sgs)

        def check(user_data: str) -> None:
            assert "@sha256:" in user_data
            assert "authentication:latest" not in user_data
            assert 'docker pull "$IMAGE_URI"' in user_data

        return auth.user_data.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        """Regression guard: region.region must be used, not region.name."""
        vpc, ecr, sgs = _make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            FastAPIAuthComponentResource("test-energy-market-warn", vpc, ecr, sgs)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
